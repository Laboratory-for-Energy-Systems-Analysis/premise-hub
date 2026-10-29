"""Recalculate the ERW example as twenty equal annual batches, 2030–2049.

Use the TRAILS environment. Licensed matrices stay in ignored build/. The
reviewed batch workbook/results are preserved; only the campaign is new.
"""

from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

import bw2data as bd
from datapackage import Package
import numpy as np
import openpyxl
import trails
from trails import Trails, search_activity
from trails.fair_rf import run_fair_delta_rf

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from apps.seoul_2026.erw import CAMPAIGN_START, CAMPAIGN_YEARS, campaign_profile
from apps.seoul_2026.scripts.calculate_erw_comparison import ARCHIVE, METHOD

DATA = REPO / "apps/seoul_2026/data"
WORK = REPO / "build/seoul-erw-campaign"
SOURCE = DATA / "coastal_erw_ei312.xlsx"
FOREGROUND = DATA / "coastal_erw_campaign.xlsx"
DATED = "coastal olivine weathering deployment, 20-year campaign, dated reference"
STATIC = "coastal olivine weathering deployment, 20-year campaign, static reference"
PRODUCT = "coastal weathering campaign, 1.25 kg rock total"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def build_foreground():
    """Keep exchange amounts; convolve each existing profile with annual demand."""
    wb = openpyxl.load_workbook(SOURCE)
    weights = np.full(CAMPAIGN_YEARS, 1 / CAMPAIGN_YEARS)
    for sheet in wb:
        columns = None
        for row in sheet:
            name = row[0].value
            if name == "Activity":
                row[1].value = str(row[1].value).replace("deployment, ", "deployment, 20-year campaign, ")
                columns = None
            elif name == "reference product":
                row[1].value = PRODUCT
            elif name == "comment" and columns is None:
                row[1].value = (str(row[1].value or "") + " Twenty equal annual batches in 2030–2049; fixed total 1.25 kg rock/unit. Equipment construction/dismantling quantities are not added.")
            elif name == "name" and row[1].value == "amount":
                columns = {cell.value: i for i, cell in enumerate(row) if cell.value}
            elif columns and name and row[columns["type"]].value == "production":
                row[0].value = str(name).replace("deployment, ", "deployment, 20-year campaign, ")
                row[columns["reference product"]].value = PRODUCT
            elif columns and name and row[columns["type"]].value in ("technosphere", "biosphere"):
                offsets_cell = row[columns["temporal_offsets"]]
                weights_cell = row[columns["temporal_weights"]]
                if row[columns["temporal_distribution"]].value == 6:
                    offsets = json.loads(offsets_cell.value)
                    old = json.loads(weights_cell.value)
                    dense = np.zeros(max(offsets) + 1)
                    for age, value in zip(offsets, old):
                        dense[age] += value
                    profile = np.convolve(dense, weights)
                else:
                    assert row[columns["temporal_loc"]].value == 0
                    profile = weights
                offsets_cell.value = json.dumps(list(range(len(profile))))
                weights_cell.value = json.dumps(profile.tolist())
                row[columns["temporal_distribution"]].value = 6
                row[columns["temporal_loc"]].value = None
                row[columns["temporal_amount_source"]].value = "port"
                assert abs(sum(profile) - 1) < 1e-12
    wb.save(FOREGROUND)


def prepare_package():
    target = WORK / "package"
    target.mkdir(parents=True, exist_ok=True)
    with ZipFile(ARCHIVE) as source:
        descriptor = json.loads(source.read("datapackage.json"))
        descriptor["resources"] = [r for r in descriptor["resources"]
            if any(f"/{year}/" in r["path"] for year in (2030, 2035, 2040, 2045, 2050))]
        assert len(descriptor["resources"]) == 20
        for resource in descriptor["resources"]:
            rel = Path(resource["path"])
            assert not rel.is_absolute() and ".." not in rel.parts
            path = target / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_bytes(source.read(str(rel)))
    path = target / "datapackage.json"
    path.write_text(json.dumps(descriptor))
    return path


def dense(array):
    return array.data.todense() if hasattr(array.data, "todense") else np.asarray(array.data)


def main():
    bd.projects.set_current("ecoinvent-3.12-cutoff")
    source = json.loads((DATA / "erw_comparison.json").read_text())
    assert digest(SOURCE) == source["ei312_foreground_sha256"]
    assert digest(ARCHIVE) == source["package_sha256"]
    WORK.mkdir(parents=True, exist_ok=True)
    build_foreground()
    package = prepare_package()
    record = dict(schema_version=1, calculated_at=datetime.now(timezone.utc).isoformat(),
        script_sha256=digest(Path(__file__)), trails=trails.__version__,
        trails_source=str(Path(trails.__file__).resolve()), brightway_project=bd.projects.current,
        package_sha256=source["package_sha256"], source_foreground_sha256=digest(SOURCE),
        foreground_sha256=digest(FOREGROUND), method=METHOD, ecoinvent="3.12 cut-off",
        model="REMIND-EU", pathway="SSP2-PkBudg1000", region="RER foreground",
        campaign=dict(start=CAMPAIGN_START, end=CAMPAIGN_START+CAMPAIGN_YEARS-1,
                      years=CAMPAIGN_YEARS, annual_fraction=1/CAMPAIGN_YEARS,
                      total_rock_kg=1250, annual_rock_kg=1250/CAMPAIGN_YEARS,
                      eventual_gross_uptake_kg=1000),
        scope="Twenty annual foreground batches; annual interpolated suppliers; fixed depth one with complete residual background solves. Same total rock and uptake potential. No invented plant construction or dismantling inventory.")
    print("Load five source anchors and interpolate annual suppliers", flush=True)
    with Trails(Package(str(package)), interpolate_annual=True, cache_interpolation=False,
                interpolation_start_year_offset=0, interpolation_end_year_offset=0,
                ei_version="3.12") as model:
        model.import_excel_inventory(str(FOREGROUND))
        def find(name):
            found = search_activity(model, name=name, reference_product=PRODUCT, location="RER", match="exact")
            assert len(found.rows) == 1
            return int(found.rows[0][0])
        dated, static = find(DATED), find(STATIC)
        metadata = {int(i): m for mapping in model.activity_indices.values() for i,m in mapping.items()}
        annual = []
        for year in range(CAMPAIGN_START, CAMPAIGN_START+CAMPAIGN_YEARS):
            model.static_lca(year, static, [METHOD], amount=1000/CAMPAIGN_YEARS, ei_version="3.12")
            total = float(np.asarray(model.static_score).sum())
            annual.append(dict(year=year, total=total))
            print("Independent static annual batch", year, total, flush=True)
        record["annual_static_checks"] = annual
        print("Route campaign and solve dated LCI", flush=True)
        model.temporal_routing(start_year=CAMPAIGN_START, start_act_idx=dated, amount=1000,
            max_depth=1, adaptive_relative_score_cutoff=None,
            attribute_to_roots=True, show_progress=False)
        model.lci(show_progress=False, solver_mode="direct", inventory_backend="factorized")
        model.lcia(methods=[METHOD], ei_version="3.12")
        score = model.scores
        total = score.sum(dim=[d for d in score.dims if d != "year"])
        record["temporal"] = [dict(age=int(y)-CAMPAIGN_START, score=float(v))
            for y,v in zip(total.year.values, dense(total)) if v != 0]
        roots = score.sum(dim=[d for d in score.dims if d not in ("year","root activity")]).transpose("root activity","year")
        record["temporal_roots"] = []
        for root, vals in zip(roots["root activity"].values, dense(roots)):
            if not np.any(vals): continue
            meta = metadata[int(root)]
            record["temporal_roots"].append(dict(activity=meta["name"],
                reference_product=meta.get("reference product"),
                series=[dict(age=int(y)-CAMPAIGN_START,score=float(v)) for y,v in zip(roots.year.values,vals) if v != 0]))
        aggregate = defaultdict(float)
        for root in record["temporal_roots"]:
            for point in root["series"]: aggregate[point["age"]] += point["score"]
        error = max(abs(aggregate[r["age"]]-r["score"]) for r in record["temporal"])
        closure = sum(r["score"] for r in record["temporal"]) - sum(r["total"] for r in annual)
        assert error < 1e-8, error
        assert abs(closure) < 1e-3, closure
        profile = campaign_profile()
        uptake = sum(profile["uptake_kg"])
        assert abs(uptake-1000) < 1e-8
        record["checks"] = dict(root_annual_closure_kg=error, independent_annual_static_closure_kg=closure,
            uptake_kg=float(uptake), rock_kg=1250, routing_max_depth=1,
            routing_convergence_tested=False)
        print("Campaign LCI checked", record["checks"], flush=True)
        (WORK / "campaign-before-fair.json").write_text(json.dumps(record,indent=2)+"\n")
        run_fair_delta_rf(model, scenario="REMIND|SSP2-EU21-PkBudg1000",
                          per_species_runs=False, quantiles=[50], show_progress=False)
        record["fair"] = {}
        for key,array in (("radiative_forcing",model.instant_radiative_forcing),
                          ("temperature",model.delta_temperature)):
            series=array.sel(quantile=50).sum(dim=[d for d in array.dims if d not in ("quantile","year")])
            record["fair"][key]=[dict(year=float(y),value=float(v)) for y,v in zip(series.year.values,dense(series))]
        record["fair_input_hashes"] = {key:digest(Path(run_fair_delta_rf.__kwdefaults__[key]))
            for key in ("emissions_csv","mapping_yaml","config_csv","properties_csv")
            if run_fair_delta_rf.__kwdefaults__.get(key) is not None}
        record["status"] = "calculated 20-year campaign; annual static/root closure and FaIR completed"
    output=DATA/"erw_campaign.json"
    temporary=output.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(record,indent=2)+"\n"); temporary.replace(output)
    print("Saved",output,flush=True)


if __name__ == "__main__":
    main()
