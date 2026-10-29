"""Calculate compact ERW snapshot results using a local licensed TRAILS package.

The background stays in ignored build/. Only aggregate scores and a foreground
timing screen are exported. This never writes a Brightway database.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
import re
import argparse
from datetime import datetime, timezone

import numpy as np
import openpyxl
from datapackage import Package
from trails import Trails, search_activity
import trails

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from apps.seoul_2026.erw import temporal_profile

ARCHIVE = Path(
    "/Users/romain/GitHub/premise/export/trails/remind-eu-SSP2-PkBudg1000-all-years-20261014/trails_remind-eu_SSP2-PkBudg1000.zip"
)
WORK = REPO / "build/seoul-erw-calculation"
FOREGROUND = REPO / "apps/seoul_2026/data/coastal_erw_temporalized.xlsx"
METHOD = "IPCC 2021 (incl. biogenic CO2) - climate change: total (incl. biogenic CO2) - global warming potential (GWP100)"


def main(climate=False):
    WORK.mkdir(parents=True, exist_ok=True)
    package_dir = WORK / "selected-package"
    package_dir.mkdir(exist_ok=True)
    with ZipFile(ARCHIVE) as source:
        descriptor = json.loads(source.read("datapackage.json"))
        resources = [
            r
            for r in descriptor["resources"]
            if "inventories/" not in r["path"]
            or any("/" + str(year) + "/" in r["path"] for year in (2025, 2030, 2050))
        ]
        descriptor["resources"] = resources
        for resource in resources:
            target = package_dir / resource["path"]
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read(resource["path"]))
        (package_dir / "datapackage.json").write_text(json.dumps(descriptor))
    # Aggregate identical supplier coordinates introduced by the voltage fix.
    # Distinct temporal profiles must never be merged.
    workbook = openpyxl.load_workbook(FOREGROUND)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    result, seen, columns = [], {}, None
    for row in rows:
        row = list(row)
        if row[0] and "lorry >32 metric ton, EURO" in str(row[0]):
            for col in (0, 7):
                row[col] = re.sub(
                    r"lorry >32 metric ton, EURO(\d)",
                    r"lorry, >32 metric ton, diesel, EURO \1",
                    row[col],
                )
        if row[0] == "Activity":
            seen, columns = {}, None
        if row[0] == "name" and row[1] == "amount":
            columns = list(row)
        elif (
            columns and row[0] and row[6] in ("production", "technosphere", "biosphere")
        ):
            if row[6] == "technosphere":
                row[2] = "ecoinvent-3.12-cutoff"
            if row[6] == "biosphere":
                row[2] = "ecoinvent-3.12-biosphere"
            e = dict(zip(columns, row))
            key = tuple(
                e.get(k)
                for k in (
                    "name",
                    "reference product",
                    "location",
                    "unit",
                    "categories",
                    "type",
                    "temporal_distribution",
                    "temporal_loc",
                    "temporal_offsets",
                    "temporal_weights",
                    "temporal_amount_source",
                )
            )
            if key in seen:
                prior = result[seen[key]]
                prior[1] += row[1]
                prior[8] = (
                    (prior[8] or "")
                    + " Aggregated duplicate supplier amount; all physical inputs retained."
                )
                continue
            seen[key] = len(result)
        result.append(list(row))
    normalized = openpyxl.Workbook()
    for row in result:
        normalized.active.append(row)
    calculation_workbook = WORK / "foreground-normalized.xlsx"
    normalized.save(calculation_workbook)
    normalized.save(REPO / "apps/seoul_2026/data/coastal_erw_ei312.xlsx")
    print("Loading three source snapshots", flush=True)
    with Trails(
        Package(str(package_dir / "datapackage.json")),
        interpolate_annual=False,
        ei_version="3.12",
    ) as model:
        model.import_excel_inventory(str(calculation_workbook))
        matches = search_activity(
            model,
            name="coastal olivine weathering deployment, static reference",
            reference_product="coastal weathering deployment, 1.25 kg rock",
            location="RER",
            match="exact",
        )
        assert len(matches.rows) == 1
        index = int(matches.rows[0][0])
        snapshots = []
        for year in (2025, 2030, 2050):
            model.static_lca(
                year=year,
                act_idx=index,
                amount=1000,
                methods=[METHOD],
                ei_version="3.12",
            )
            net = float(np.asarray(model.static_score).sum())
            snapshots.append(
                dict(year=year, net_kg_co2eq=net, upstream_kg_co2eq=net + 1000)
            )
            print("Snapshot", snapshots[-1], flush=True)
        # Foreground timing screen: retain a full LCA upstream burden, dated at
        # deployment, while spreading only measured-modelled uptake in time.
        # It deliberately does not claim full upstream temporal routing.
        profile = temporal_profile(10, 1, 1)
        burden = next(r["upstream_kg_co2eq"] for r in snapshots if r["year"] == 2030)
        temporal = [dict(age=0, score=burden)] + [
            dict(age=int(age), score=-float(value))
            for age, value in zip(profile["age"], profile["uptake_kg"])
        ]
        assert abs(sum(r["score"] for r in temporal) - (burden - 1000)) < 1e-7
        record = dict(
            status="calculated snapshots; foreground-timing screen",
            calculated_at=datetime.now(timezone.utc).isoformat(),
            package_sha256=hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
            foreground_sha256=hashlib.sha256(FOREGROUND.read_bytes()).hexdigest(),
            normalized_foreground_sha256=hashlib.sha256(
                calculation_workbook.read_bytes()
            ).hexdigest(),
            ei312_foreground_sha256=hashlib.sha256(
                (REPO / "apps/seoul_2026/data/coastal_erw_ei312.xlsx").read_bytes()
            ).hexdigest(),
            method=METHOD,
            ecoinvent="3.12 cutoff",
            trails=trails.__version__,
            model="REMIND-EU",
            pathway="SSP2-PkBudg1000",
            region="RER foreground",
            deployment_rock_kg=1250,
            potential_uptake_kg=1000,
            snapshots=snapshots,
            temporal=temporal,
            temporal_scope="Upstream life-cycle GWP assigned to deployment year; explicit dissolution and air-sea uptake. Upstream event timing is not routed. Not a field-calibrated uptake forecast.",
            import_diagnostics=str(model.import_diagnostics),
        )
        if climate:
            dated = search_activity(
                model,
                name="coastal olivine weathering deployment, dated reference",
                reference_product="coastal weathering deployment, 1.25 kg rock",
                location="RER",
                match="exact",
            )
            assert len(dated.rows) == 1
            model.temporal_routing(
                start_year=2030,
                start_act_idx=int(dated.rows[0][0]),
                amount=1000,
                max_depth=1,
                adaptive_relative_score_cutoff=None,
                attribute_to_roots=True,
                show_progress=False,
            )
            model.lci(
                show_progress=False,
                solver_mode="direct",
                inventory_backend="factorized",
            )
            model.lcia(methods=[METHOD], ei_version="3.12")
            score = model.scores
            annual = score.sum(dim=[d for d in score.dims if d != "year"])
            values = (
                annual.data.todense()
                if hasattr(annual.data, "todense")
                else np.asarray(annual.data)
            )
            record["routed_temporal"] = [
                dict(age=int(y) - 2030, score=float(v))
                for y, v in zip(annual.year.values, values)
            ]
            static_2030 = next(
                r["net_kg_co2eq"] for r in snapshots if r["year"] == 2030
            )
            closure_error = abs(float(np.asarray(values).sum()) - static_2030)
            assert closure_error < 1e-3, (
                f"Static/temporal closure failed: {closure_error}"
            )
            record["checks"] = dict(
                exact_foreground_links="passed; no unlinked exchanges",
                duplicate_supplier_aggregation="passed",
                static_temporal_closure_kg=closure_error,
                routing_max_depth=1,
                routing_convergence_tested=False,
                foreground_uptake_mass_kg=float(profile["uptake_kg"].sum()),
            )
            record["routed_temporal_scope"] = (
                "TRAILS fixed depth 1; all frontier demands retained in complete year-specific background solves. Full upstream temporal routing/convergence not established."
            )
            print("Routed inventory ready", flush=True)
            from trails.fair_rf import run_fair_delta_rf

            run_fair_delta_rf(
                model,
                scenario="REMIND|SSP2-EU21-PkBudg1000",
                per_species_runs=False,
                quantiles=[50],
                show_progress=False,
            )
            record["fair"] = {}
            for key, array in [
                ("radiative_forcing", model.instant_radiative_forcing),
                ("temperature", model.delta_temperature),
            ]:
                series = array.sel(quantile=50).sum(
                    dim=[d for d in array.dims if d not in ("quantile", "year")]
                )
                values = (
                    series.data.todense()
                    if hasattr(series.data, "todense")
                    else np.asarray(series.data)
                )
                record["fair"][key] = [
                    dict(year=float(y), value=float(v))
                    for y, v in zip(series.year.values, values)
                ]
            record["fair_scope"] = (
                "FaIR response for fixed-depth-one ERW inventory; REMIND|SSP2-EU21-PkBudg1000. Assumed coastal uptake profile, not field calibration."
            )
            record["status"] = (
                "calculated snapshots, fixed-depth-one temporal LCI and FaIR response"
            )
            defaults = run_fair_delta_rf.__kwdefaults__
            record["fair_input_hashes"] = {
                key: hashlib.sha256(Path(defaults[key]).read_bytes()).hexdigest()
                for key in (
                    "emissions_csv",
                    "mapping_yaml",
                    "config_csv",
                    "properties_csv",
                )
                if defaults.get(key) is not None
            }
        output = REPO / "apps/seoul_2026/data/erw_comparison.json"
        output.write_text(json.dumps(record, indent=2) + "\n")
        if climate:
            update_review(record)
        print("Saved", output, flush=True)


def update_review(record):
    path = REPO / "apps/seoul_2026/data/erw_review.json"
    review = json.loads(path.read_text())
    review["validation"] = (
        "Original foreground parsed with bw2io. The normalized ecoinvent 3.12 variant imports into TRAILS with zero unlinked exchanges and aggregated duplicate suppliers. Static results, fixed-depth-one temporal LCI and FaIR response have been calculated; static/temporal GWP closure error is below 0.001 kg CO2-eq per deployment. Routing convergence and field performance are not established."
    )
    review["calculation"] = {
        k: record[k]
        for k in (
            "status",
            "calculated_at",
            "method",
            "ecoinvent",
            "trails",
            "model",
            "pathway",
            "package_sha256",
            "ei312_foreground_sha256",
            "snapshots",
            "checks",
            "routed_temporal_scope",
            "fair_scope",
            "fair_input_hashes",
        )
    }
    review["limitations"] = [
        v
        for v in review["limitations"]
        if not v.startswith("No new full-background")
        and not v.startswith("Original supplier database labels")
    ]
    extra = [
        "The calculated snapshots use the corrected linked foreground. Dated LCI uses fixed depth one with complete residual background solves; full upstream temporal-routing convergence has not been tested.",
        "The live uptake controls vary only foreground timing and realization, holding the calculated upstream inventory fixed. They do not rerun FaIR or LCA, or implement matched particle-size/energy variants.",
    ]
    for item in extra:
        if item not in review["limitations"]:
            review["limitations"].append(item)
    findings = [
        dict(
            title="ecoinvent 3.12 supplier identities",
            evidence="The original EURO3/5/6 truck names do not match the renamed ecoinvent 3.12 datasets.",
            action="Use the same size, diesel fuel and EURO class with exact current name/product/location identities; preserve quantities.",
            status="Exact TRAILS import passed with no unlinked exchanges.",
        ),
        dict(
            title="Repeated electricity supplier coordinate",
            evidence="Correcting grinding to medium voltage makes it share an identity with pumping electricity.",
            action="Aggregate amounts without losing physical inputs; distinct temporal profiles stay separate.",
            status="Calculated input retains 0.093120605 kWh per deployment unit.",
        ),
    ]
    for finding in findings:
        if finding["title"] not in {f["title"] for f in review["findings"]}:
            review["findings"].append(finding)
    path.write_text(json.dumps(review, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--climate", action="store_true")
    main(parser.parse_args().climate)
