"""Reproduce the reviewed DACCS cohort and resolve electricity's signed effects.

Only compact characterized aggregates leave ignored build/. The original
SETAC scripts, inventories, result tables and shared TRAILS caches are unchanged.
"""

from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

REPO = Path(__file__).resolve().parents[3]
SOURCE = REPO / "build/setac-regeneration-20261014"
sys.path.insert(0,str(REPO))
sys.path.insert(0,str(SOURCE))

from scripts import generate_routing_graphs as routing
from scripts.calculate_cohort_temporal_scores import reattribute_graph_to_physical_branches
from workshop.lifetime import cohort_cases
from workshop.temporal import enable_signed_technosphere_routing

import bw2data as bd
from datapackage import Package
import numpy as np
import trails
from trails import Trails
from trails.characterization import get_cf_vector
from trails.lca import _CHAR_CACHE

from apps.setac_2026 import results

ARCHIVE = Path("/Users/romain/GitHub/premise/export/trails/remind-eu-SSP2-PkBudg1000-all-years-20261014/trails_remind-eu_SSP2-PkBudg1000.zip")
WORK = REPO / "build/seoul-daccs-energy-signs"
DATA = REPO / "apps/seoul_2026/data"
FOREGROUND = SOURCE / "data/inventories/generated/lcss2026-foreground.xlsx"
COHORT = SOURCE / "data/inventories/generated/lcss2026-routing-cohorts.xlsx"
CONFIG = SOURCE / "data/inventories/parameters.json"
METHOD = "IPCC 2021 (incl. biogenic CO2) no LT - climate change: total (incl. biogenic CO2) no LT - global warming potential (GWP100) no LT"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def package_path():
    target=WORK/"package"
    target.mkdir(parents=True,exist_ok=True)
    with ZipFile(ARCHIVE) as archive:
        descriptor=json.loads(archive.read("datapackage.json"))
        for resource in descriptor["resources"]:
            member=Path(resource["path"])
            assert not member.is_absolute() and ".." not in member.parts
            path=target/member
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists(): path.write_bytes(archive.read(str(member)))
    path=target/"datapackage.json"
    path.write_text(json.dumps(descriptor))
    return path


def main():
    bd.projects.set_current("ecoinvent-3.12-cutoff")
    source_rows=[r for r in results.cohort_temporal_score_rows() if r["case"]=="DACCS"]
    sample=source_rows[0]
    assert digest(ARCHIVE)==sample["package_sha256"]
    assert digest(FOREGROUND)==sample["foreground_sha256"]
    assert digest(COHORT)==sample["cohort_foreground_sha256"]
    denominator=float(sample["denominator_net_stored_tonnes"])
    config=json.loads(CONFIG.read_text())
    assert abs(cohort_cases(config,commissioning_year=2030)["DACCS"].lifetime_net_stored_kg/1000-denominator)<1e-6
    expected=defaultdict(float)
    for row in source_rows:
        if row["contributor"]=="market group for electricity, medium voltage" and row["location"]=="ENC":
            expected[int(row["impact_year"])]+=float(row["score_per_net_tonne_kg_co2eq"])
    assert expected
    WORK.mkdir(parents=True,exist_ok=True)
    record=dict(schema_version=1,calculated_at=datetime.now(timezone.utc).isoformat(),
        method=METHOD,ecoinvent="3.12 cutoff",trails=trails.__version__,
        trails_source=str(Path(trails.__file__).resolve()),brightway_project=bd.projects.current,
        normalization_stored_tonnes=1,cohort_storage_tonnes=denominator,
        package_sha256=digest(ARCHIVE),foreground_sha256=digest(FOREGROUND),
        cohort_foreground_sha256=digest(COHORT),config_sha256=digest(CONFIG),
        source_scores_sha256=digest(REPO/"apps/setac_2026/data/processed/cohort_temporal_scores.csv"),
        script_sha256=digest(Path(__file__)),
        source_helper_sha256={str(p.relative_to(SOURCE)):digest(p) for p in
            (SOURCE/"scripts/generate_routing_graphs.py",SOURCE/"scripts/calculate_cohort_temporal_scores.py")},
        scope="Signed characterized elementary-flow totals within the complete ENC electricity supplier root, aggregated by year before sign separation. Original annual net scores retained after bounded numerical reconciliation. Not a new inventory or climate response.")
    print("Load source annual background and the two reviewed foreground workbooks",flush=True)
    with Trails(Package(str(package_path())),interpolate_annual=True,cache_interpolation=False,
                interpolation_start_year_offset=0,interpolation_end_year_offset=0,ei_version="3.12") as model:
        model.import_excel_inventory([str(FOREGROUND),str(COHORT)])
        diagnostics=model.import_diagnostics
        assert not diagnostics.get("unlinked") and not diagnostics.get("new_flows")
        routing.apply_daccs_cohort_timing(model,2030,config)
        enable_signed_technosphere_routing(model)
        root=routing.find_activity(model,2030,routing.ROOTS["DACCS"])
        model.temporal_routing(start_year=2030,start_act_idx=root,amount=1,
            max_depth=4,adaptive_relative_score_cutoff=None,min_amount=1e-15,
            attribute_to_roots=True,show_progress=False)
        reattribute_graph_to_physical_branches(model,"DACCS")
        electric=routing.find_activity(model,2030,dict(name="market group for electricity, medium voltage",
            **{"reference product":"electricity, medium voltage"},location="ENC"))
        demand=defaultdict(float)
        for node,meta in model.graph.nodes(data=True):
            if int(meta.get("act_idx",-1))==electric and int(meta.get("depth",-1))==3:
                demand[int(meta["year"])]+=float(meta.get("amount",0))/denominator
        record["electricity_demand"]=[dict(year=y,kwh_per_t_stored=v) for y,v in sorted(demand.items())]
        print("Electricity demand, normalized",record["electricity_demand"],flush=True)
        print("Solve original fixed-depth-four cohort with retained factorized inventory",flush=True)
        model.lci(show_progress=False,solver_mode="iterative",iterative_rtol=1e-5,
            iterative_maxiter=500,inventory_backend="factorized")
        model.lcia(methods=[METHOD],ei_version="3.12",show_progress=False)
        cf=np.asarray(get_cf_vector(model,[METHOD],_CHAR_CACHE,ei_version="3.12"),dtype=float)
        selected=np.flatnonzero(cf)
        years=np.asarray(model.inventory.coords["year"].values,dtype=int)
        scores=np.zeros((len(years),len(cf)),dtype=float)
        count=0
        print("Stream characterized electricity-root flows; cancel timing corrections before splitting signs",flush=True)
        for _,activities,flows,year_positions,roots,values in model._inventory_builder.iter_entries_for_flows(selected,show_progress=False):
            mask=np.asarray(roots)==electric
            if not np.any(mask):continue
            f=np.asarray(flows[mask],dtype=int);y=np.asarray(year_positions[mask],dtype=int)
            v=np.asarray(values[mask],dtype=float)*cf[f]/denominator
            np.add.at(scores,(y,f),v)
            count+=int(mask.sum())
        reconstructed=scores.sum(axis=1)
        discrepancy=max(abs(float(value)-expected.get(int(year),0)) for year,value in zip(years,reconstructed))
        missing=max((abs(v) for y,v in expected.items() if y not in set(years)),default=0)
        print("Max annual source-net discrepancy",discrepancy,"missing",missing,flush=True)
        assert discrepancy<1e-3 and missing<1e-10,(discrepancy,missing)
        positive=np.maximum(scores,0).sum(axis=1);negative=np.minimum(scores,0).sum(axis=1)
        record["annual"]=[]
        flow_meta=model.biosphere_indices[str(model._map_year_to_template_year(2030))]
        record["flow_totals"]=[dict(flow=flow_meta[int(i)]["name"],
            compartment=flow_meta[int(i)].get("compartment"),
            total=float(scores[:,i].sum()),positive=float(np.maximum(scores[:,i],0).sum()),
            negative=float(np.minimum(scores[:,i],0).sum())) for i in selected if np.any(scores[:,i])]
        for year,p,n,actual in zip(years,positive,negative,reconstructed):
            original=expected.get(int(year),0)
            delta=original-float(actual)
            p=float(p)+max(delta,0);n=float(n)+min(delta,0)
            if p or n or original:
                record["annual"].append(dict(year=int(year),positive=p,negative=n,net=original,
                    reproduced_net=float(actual),reconciliation=delta))
        record["checks"]=dict(max_annual_source_difference=discrepancy,
            missing_source_year_max=missing,streamed_entries=count,
            source_net_total=sum(expected.values()),reproduced_net_total=float(reconstructed.sum()),
            signed_annual_closure=max(abs(r["positive"]+r["negative"]-r["net"]) for r in record["annual"]))
        record["status"]="source net reproduced; signed electricity contributions checked"
    output=DATA/"daccs_energy_signed.json"
    temp=output.with_suffix(".json.tmp");temp.write_text(json.dumps(record,indent=2)+"\n");temp.replace(output)
    print("Saved",output,record["checks"],flush=True)


if __name__=="__main__":
    main()
