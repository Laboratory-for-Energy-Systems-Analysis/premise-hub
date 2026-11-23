"""Build MCV slide aggregates from the checked branch and species inventories."""

import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from apps.setac_2026.scripts.audit_energy_and_pulse import pulse
from apps.setac_2026.scripts.regenerate_results import sha256

CASES = ("BECCS", "DACCS")


def combine(output, prefix, name):
    rows = []
    for case in CASES:
        with (output / f"{prefix}-{case}.csv").open(newline="") as stream:
            rows.extend(csv.DictReader(stream))
    with (output / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return rows


def validate_branches(output, expected):
    from apps.setac_2026.figures import BECCS_TEMPORAL_GROUPS, DACCS_TEMPORAL_PRODUCTS

    temporal = combine(output, "temporal", "cohort_temporal_scores.csv")
    energy = combine(output, "energy", "energy_flow_signs.csv")
    totals = defaultdict(float)
    energy_expected = defaultdict(float)
    energy_actual = defaultdict(float)
    for row in temporal:
        case = row["case"]
        score = float(row["score_per_net_tonne_kg_co2eq"])
        totals[case] += score
        group = (BECCS_TEMPORAL_GROUPS[row["contributor"]] if case == "BECCS"
                 else DACCS_TEMPORAL_PRODUCTS[row["reference_product"]])
        if group == "Energy":
            energy_expected[case, row["root_activity_index"], row["impact_year"]] += score
    for row in energy:
        value = float(row["score_per_net_tonne_kg_co2eq"])
        assert int(row["sign"]) * value > 0
        energy_actual[row["case"], row["root_activity_index"], row["impact_year"]] += value
    for key in energy_expected.keys() | energy_actual.keys():
        assert math.isclose(energy_expected[key], energy_actual[key], abs_tol=2e-6), key
    for case, score in totals.items():
        assert math.isclose(score, expected["cases"][case]["gwp100_kg_per_net_tonne"], abs_tol=0.03), (case, score)
    return totals


def run(workspace, package, source_project, control, destination):
    sys.path.insert(0, str(workspace))
    output = workspace / "data/processed"
    expected = json.loads(control.read_text())
    totals = validate_branches(output, expected)
    digest = sha256(package)
    assert expected["package_sha256"] == digest
    templates = {}
    for case in CASES:
        meta = json.loads((output / f"fair-species-{case}.json").read_text())
        assert meta["package_sha256"] == digest
        for metric, unit in (("radiative forcing", "W/m2"), ("temperature anomaly", "K")):
            templates[case, metric] = dict(
                case=case, system="new CHP+CCS vs standing forest and Northern European energy"
                if case == "BECCS" else "not applicable",
                pathway="SSP2-PkBudg1000", commissioning_year=2030,
                metric=metric, unit=unit,
                **{key: meta[key] for key in ("package_sha256", "foreground_sha256",
                   "cohort_foreground_sha256", "denominator_net_stored_tonnes")},
            )
    with ThreadPoolExecutor(max_workers=2) as pool:
        audit = pool.submit(pulse, workspace, package, templates)
        grid_job = pool.submit(subprocess.run, [
            sys.executable, str(ROOT / "apps/setac_2026/scripts/regenerate_results.py"),
            "--source-project", str(source_project), "--workspace", str(workspace),
            "--package", str(package), "--steps", "pulse",
        ], check=True)
        audit.result()
        grid_job.result()

    import numpy as np

    validation = json.loads((output / "pulse_integration_audit.json").read_text())
    with np.load(output / "cohort_pulse_equivalence_grid.npz") as grid:
        assert tuple(grid["cases"]) == CASES
        years = list(grid["years"])
        i, j, k = (years.index(year) for year in (2020, 2030, 2100))
        for index, case in enumerate(CASES):
            observed = float(grid["median_kg_co2_per_net_tonne"][index, 0, i, j, k])
            direct = validation["cases"][case]["values_kg_co2_per_net_tonne"]["1.0"]["2100"]
            assert math.isclose(observed, direct, abs_tol=0.02), (case, observed, direct)
            target = expected["cases"][case]["pulse_kg_per_net_tonne"]["median"]
            assert math.isclose(observed, target, abs_tol=0.05), (case, observed, target)

    processed = destination / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    for name in (
        "static_lcia.csv", "static_contributions.csv", "process_step_attribution_2025.json",
        "system_inventory_2025.json", "cohort_temporal_scores.csv", "energy_flow_signs.csv",
        "co2_reference_pulse.csv", "cohort_pulse_equivalence_grid.npz",
        "pulse_integration_audit.json",
    ):
        shutil.copyfile(output / name, processed / name)
    shutil.copyfile(output / "cohort_fair_total_responses.csv", processed / "cohort_fair_responses.csv")
    shutil.copyfile(output / "scenario_sector_mixes.csv", destination / "sector_mixes.csv")
    for path in [*processed.glob("*.csv"), destination / "sector_mixes.csv"]:
        path.write_text(path.read_text(), newline="\n")
    shutil.copyfile(ROOT / "apps/setac_2026/data/forest_pool_sensitivity.json",
                    destination / "forest_pool_sensitivity.json")
    raw = json.loads((workspace / "regeneration.json").read_text())
    provenance = dict(
        background_packages={item["pathway"]: item["sha256"] for item in
            json.loads((workspace / "data/trails_packages_manifest.json").read_text())["packages"]},
        source_commit=raw["source_commit"], routes_max_depth=4, vintage_calendar_start=1880,
        dated_gwp100_per_net_tonne=dict(totals), config_count=validation["config_count"],
        inventory_reference={key: expected[key] for key in (
            "package_sha256", "foreground_sha256", "cohort_foreground_sha256", "trails_routing_source_sha256"
        )}, files={str(p.relative_to(destination)): sha256(p)
                    for p in sorted(processed.iterdir()) if p.is_file()},
    )
    (destination / "regeneration.json").write_text(json.dumps(provenance, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("workspace", "package", "source-project", "control", "destination"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    run(*(getattr(args, name).resolve() for name in
          ("workspace", "package", "source_project", "control", "destination")))


if __name__ == "__main__":
    main()
