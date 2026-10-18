"""Rebuild SETAC derivatives in an isolated copy of the reviewed calculation project.

Run with the TRAILS environment, --source-project FSLCI_workshop_2026 and the
new --package. Licensed matrices and foreground workbooks stay in --workspace;
only reviewed aggregate outputs are subsequently copied into the app.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

APP = Path(__file__).resolve().parents[1]
STEPS = (
    "prepare",
    "foreground",
    "static",
    "attribution",
    "cohort",
    "energy_audit",
    "reference",
    "validation",
    "pulse",
    "pulse_audit",
    "balance_audit",
    "mixes",
    "system",
    "publish",
)


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def replace_once(path, before, after):
    source = path.read_text()
    if source.count(before) != 1:
        raise ValueError(f"Calculation source changed: {path.name}: {before[:70]}")
    path.write_text(source.replace(before, after, 1))


def prepare(source, package, workspace):
    build = json.loads(package.with_name("build_manifest.json").read_text())
    digest = sha256(package)
    if digest != build["archive_sha256"]:
        raise ValueError("Package checksum differs from its build manifest")
    if build["scenario"] != {"model": "remind-eu", "pathway": "SSP2-PkBudg1000"}:
        raise ValueError("This reproduction requires REMIND-EU SSP2-PkBudg1000")
    with zipfile.ZipFile(package) as archive:
        if archive.testzip() is not None:
            raise ValueError("Invalid ZIP archive")
    workspace.mkdir(parents=True, exist_ok=True)
    for directory in ("scripts", "workshop", "dev"):
        shutil.copytree(
            source / directory,
            workspace / directory,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
    inventory_dir = workspace / "data/inventories"
    (inventory_dir / "generated").mkdir(parents=True, exist_ok=True)
    (workspace / "data/processed").mkdir(parents=True, exist_ok=True)
    config = json.loads((source / "data/inventories/parameters.json").read_text())
    for workbook in config["source_workbooks"].values():
        workbook["path"] = str(
            (source / "data/inventories" / workbook["path"]).resolve()
        )
    forest_package = config["source_packages"]["spruce_inventory"]
    forest_package.update(
        path=str(package),
        sha256=digest,
        note="Regenerated REMIND-EU package with post-harvest uptake.",
    )
    # The activity identity, rather than its old integer position, selects the forest.
    config["beccs"]["forest_feedstock"].pop("source_activity_index", None)
    config["beccs"]["forest_feedstock"]["temporal_stage_assumptions"][
        "carbon_uptake"
    ] = (
        "Native post-harvest empirical offsets and weights retained; no second shift. "
        "Uptake amount retains the reviewed CHP biogenic-carbon balance."
    )
    (inventory_dir / "parameters.json").write_text(json.dumps(config, indent=2) + "\n")
    manifest = json.loads((source / "data/trails_packages_manifest.json").read_text())
    for record in manifest["packages"]:
        record["path"] = str((source / record["path"]).resolve())
        record["premise_version"] = manifest["generation"]["premise_version"]
        if record["pathway"] == "SSP2-PkBudg1000":
            record.update(
                path=str(package),
                sha256=digest,
                size_bytes=package.stat().st_size,
                premise_version=".".join(map(str, build["premise_version"])),
            )
        if sha256(record["path"]) != record["sha256"]:
            raise ValueError(f"Package checksum mismatch: {record['pathway']}")
    (workspace / "data/trails_packages_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )

    foreground = workspace / "scripts/prepare_foreground_inventories.py"
    replace_once(
        foreground,
        "    shifted = [int(offset) + int(rotation_years) for offset in offsets]\n"
        "    if min(shifted) < 1 or max(shifted) != int(rotation_years):",
        "    shifted = [float(offset) for offset in offsets]\n"
        "    if min(shifted) < 0 or max(shifted) > int(rotation_years):",
    )
    replace_once(
        foreground,
        '"Greenfield differential stage: empirical Norway-spruce regrowth "\n'
        '            f"during years +1 through +{rotation_years}; historical uptake "',
        '"Greenfield differential stage: native post-harvest Norway-spruce regrowth "\n'
        '            f"at offsets {min(shifted)} through {max(shifted)}; historical uptake "',
    )
    # The selected forest source year is an anchor; annual interpolation is unnecessary here.
    replace_once(
        foreground,
        "        interpolate_annual=True,\n        cache_interpolation=True,\n"
        "        interpolation_start_year_offset=1940 - 2005,",
        "        interpolate_annual=False,\n        cache_interpolation=True,\n"
        "        interpolation_start_year_offset=0,",
    )
    replace_once(
        workspace / "scripts/calculate_static_results.py",
        '"premise_version": manifest["generation"]["premise_version"],',
        '"premise_version": package_record["premise_version"],',
    )
    provenance = {
        "source_project": str(source),
        "source_commit": subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip(),
        "new_package": build,
        "comparison_package": manifest["packages"][0],
        "source_script_hashes": {
            str(p.relative_to(source)): sha256(p)
            for p in sorted((source / "scripts").glob("*.py"))
        },
        "notes": [
            "Static NPi comparison retains its original background package and uses the regenerated foreground.",
            "Forest uptake offsets are already post-harvest and are copied without a second rotation shift.",
            "Reviewed functional units, transport, standing-forest reference and cohort routing schedule are retained.",
            "Original calculation project and long lca_time presentation are not modified.",
        ],
    }
    (workspace / "regeneration.json").write_text(
        json.dumps(provenance, indent=2) + "\n"
    )
    print(f"Prepared {workspace}; package {digest}", flush=True)


def extract_mixes(workspace):
    sys.path.insert(0, str(workspace))
    from scripts.extract_scenario_sector_mixes import extract_year

    rows = []
    manifest = json.loads(
        (workspace / "data/trails_packages_manifest.json").read_text()
    )
    for record in manifest["packages"]:
        with zipfile.ZipFile(record["path"]) as package:
            for year in (2025, 2030, 2035, 2040, 2045, 2050):
                rows.extend(extract_year(package, record["pathway"], year))
    output = workspace / "data/processed/scenario_sector_mixes.csv"
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} market-share records", flush=True)


def publish(workspace):
    """Validate the calculation outputs, then publish aggregate data locally."""
    import numpy as np
    import trails

    source = workspace / "data/processed"
    destination = APP / "data/processed"
    run = json.loads((workspace / "regeneration.json").read_text())
    expected_package = run["new_package"]["archive_sha256"]
    foreground = sha256(
        workspace / "data/inventories/generated/lcss2026-foreground.xlsx"
    )

    def read(name):
        with (source / name).open(newline="") as stream:
            return list(csv.DictReader(stream))

    static = read("static_lcia.csv")
    assert len(static) == 12
    assert all(r["foreground_sha256"] == foreground for r in static)
    assert all(
        r["package_sha256"] == expected_package
        for r in static
        if r["pathway"] == "SSP2-PkBudg1000"
    )
    contributions = defaultdict(float)
    for row in read("static_contributions.csv"):
        contributions[row["provenance_id"], row["contributor_type"]] += float(
            row["score"]
        )
    for row in static:
        for view in ("activity", "biosphere flow"):
            assert math.isclose(
                contributions[row["provenance_id"], view],
                float(row["score"]),
                abs_tol=1e-5,
            )
    temporal = read("cohort_temporal_scores.csv")
    forcing = read("cohort_fair_responses.csv")
    for rows in (temporal, forcing):
        assert {r["case"] for r in rows} == {"BECCS", "DACCS"}
        assert {r["package_sha256"] for r in rows} == {expected_package}
        assert {r["foreground_sha256"] for r in rows} == {foreground}
    with np.load(source / "cohort_pulse_equivalence_grid.npz") as grid:
        metadata = json.loads(str(grid["metadata_json"].item()))
        assert metadata["package_sha256"] == expected_package
        assert metadata["foreground_sha256"] == foreground
        assert metadata["config_count"] == 841
        assert tuple(grid["cases"]) == ("BECCS", "DACCS")
        grid_years = list(grid["years"])
        default_values = grid["median_kg_co2_per_net_tonne"][
            :, 0, grid_years.index(2020), grid_years.index(2030), grid_years.index(2100)
        ]
        assert np.all(np.isfinite(default_values))
    validation = json.loads(
        (source / "cohort_pulse_equivalence_validation.json").read_text()
    )
    assert validation["package_sha256"] == expected_package
    assert validation["foreground_sha256"] == foreground
    assert (
        validation["window_start"],
        validation["reference_year"],
        validation["window_end"],
    ) == (2020, 2030, 2100)
    for case, value in zip(("BECCS", "DACCS"), default_values):
        expected = validation["cases"][case]["radiative forcing"][
            "trails_config_first_kg_co2_per_net_tonne"
        ]["median"]
        assert math.isclose(float(value), expected, abs_tol=0.02), (
            case,
            value,
            expected,
        )

    energy_metadata = json.loads((source / "energy_flow_signs.json").read_text())
    assert energy_metadata["package_sha256"] == expected_package
    assert energy_metadata["foreground_sha256"] == foreground
    assert energy_metadata["csv_sha256"] == sha256(source / "energy_flow_signs.csv")
    energy_totals = defaultdict(float)
    for row in read("energy_flow_signs.csv"):
        value = float(row["score_per_net_tonne_kg_co2eq"])
        assert value * int(row["sign"]) > 0
        key = (row["case"], row["root_activity_index"], row["impact_year"])
        energy_totals[key] += value
    energy_roots = {(case, root) for case, root, year in energy_totals}
    assert {case for case, root in energy_roots} == {"BECCS", "DACCS"}
    expected_energy = defaultdict(float)
    for row in temporal:
        if (row["case"], row["root_activity_index"]) in energy_roots:
            key = (row["case"], row["root_activity_index"], row["impact_year"])
            expected_energy[key] += float(row["score_per_net_tonne_kg_co2eq"])
    for key in energy_totals.keys() | expected_energy.keys():
        assert math.isclose(energy_totals[key], expected_energy[key], abs_tol=2e-6), key

    audit = json.loads((source / "pulse_integration_audit.json").read_text())
    assert audit["package_sha256"] == expected_package
    assert audit["total_response"]["csv_sha256"] == sha256(
        source / "cohort_fair_total_responses.csv"
    )
    assert audit["config_count"] == metadata["config_count"]
    assert audit["total_response"]["scenario"] == metadata["scenario"]
    total_forcing = read("cohort_fair_total_responses.csv")
    assert {r["contribution_view"] for r in total_forcing} == {"total"}
    assert {r["package_sha256"] for r in total_forcing} == {expected_package}
    assert {r["foreground_sha256"] for r in total_forcing} == {foreground}
    assert len(total_forcing) == 2 * 2 * 3 * (2300 - 1940)
    assert {float(r["response_year"]) for r in total_forcing} == set(
        np.arange(1940.5, 2300, 1)
    )
    for case, expected in zip(("BECCS", "DACCS"), default_values):
        checks = audit["cases"][case]["values_kg_co2_per_net_tonne"]
        assert math.isclose(checks["1.0"]["2100"], float(expected), abs_tol=0.02)
        assert abs(checks["1.0"]["2100"] - checks["0.1"]["2100"]) < 0.1

    destination.mkdir(parents=True, exist_ok=True)
    for name in (
        "static_lcia.csv",
        "static_contributions.csv",
        "process_step_attribution_2025.json",
        "system_inventory_2025.json",
        "cohort_temporal_scores.csv",
        "cohort_pulse_equivalence_grid.npz",
        "cohort_pulse_equivalence_validation.json",
        "co2_reference_pulse.csv",
        "energy_flow_signs.csv",
        "energy_flow_signs.json",
        "pulse_integration_audit.json",
        "beccs_carbon_balance_audit.json",
    ):
        shutil.copyfile(source / name, destination / name)
    # Display the total ensemble response used by pulse equivalence. Summing
    # process-level quantiles is not the quantile of the complete response.
    shutil.copyfile(
        source / "cohort_fair_total_responses.csv",
        destination / "cohort_fair_responses.csv",
    )
    # Verify the retained IAM context and steel audit against the old extract.
    mix_keys = ("pathway", "year", "sector", "category")
    with (APP / "data/sector_mixes.csv").open(newline="") as stream:
        old_mix = {
            tuple(row[key] for key in mix_keys): float(row["share"])
            for row in csv.DictReader(stream)
        }
    new_mix = {
        tuple(row[key] for key in mix_keys): float(row["share"])
        for row in read("scenario_sector_mixes.csv")
    }
    assert old_mix.keys() == new_mix.keys()
    assert all(
        math.isclose(new_mix[key], old_mix[key], abs_tol=1e-9) for key in old_mix
    )
    shutil.copyfile(source / "scenario_sector_mixes.csv", APP / "data/sector_mixes.csv")
    # Hash canonical LF files so Git's newline normalization cannot invalidate
    # the published manifest when this deck is checked out on another system.
    for path in [*destination.glob("*.csv"), APP / "data/sector_mixes.csv"]:
        path.write_text(path.read_text(), newline="\n")
    packages = json.loads(
        (workspace / "data/trails_packages_manifest.json").read_text()
    )["packages"]
    (APP / "data/sector_mixes.json").write_text(
        json.dumps(
            {
                "model": "remind-eu",
                "location": "ENC",
                "years": [2025, 2030, 2035, 2040, 2045, 2050],
                "packages": [
                    {
                        "pathway": p["pathway"],
                        "file": Path(p["path"]).name,
                        "sha256": p["sha256"],
                        "premise_version": p["premise_version"],
                    }
                    for p in packages
                ],
                "extractor_sha256": sha256(
                    workspace / "scripts/extract_scenario_sector_mixes.py"
                ),
                "notes": [
                    "Shares extracted from each anchor-year market; no interpolation.",
                    "PkBudg1000 regenerated from the 14 October 2026 package; original NPi background retained.",
                ],
            },
            indent=2,
        )
        + "\n"
    )
    steel_path = APP / "data/steel_mix_audit.json"
    steel_audit = json.loads(steel_path.read_text())
    iam_hash = run["new_package"]["encrypted_iam_sha256"]
    assert {
        r["iam_encrypted_sha256"]
        for r in steel_audit["rows"]
        if r["pathway"] == "SSP2-PkBudg1000"
    } == {iam_hash}
    steel_audit["regenerated_package_sha256"] = expected_package
    steel_audit["regenerated_package_check"] = (
        "14 October 2026: all sector mix shares reproduce the existing extract; underlying IAM input hash unchanged."
    )
    steel_path.write_text(json.dumps(steel_audit, indent=2) + "\n")
    context_path = APP / "data/scenario_context.json"
    context = json.loads(context_path.read_text())
    context["regeneration_check"] = {
        "package_sha256": expected_package,
        "iam_encrypted_sha256": iam_hash,
        "note": "New inventory package uses the unchanged IAM input; the scenario context extract is retained.",
    }
    context_path.write_text(json.dumps(context, indent=2) + "\n")
    shutil.copyfile(
        APP.parent / "lca_time/data/forest_pool_sensitivity.json",
        APP / "data/forest_pool_sensitivity.json",
    )
    run["trails_version"] = trails.__version__
    run["trails_source"] = str(Path(trails.__file__).resolve())
    run["trails_commit"] = subprocess.check_output(
        [
            "git",
            "-C",
            str(Path(trails.__file__).resolve().parents[1]),
            "rev-parse",
            "HEAD",
        ],
        text=True,
    ).strip()
    run["published_at"] = datetime.now(timezone.utc).isoformat()
    run["workflow_script_hashes"] = {
        path.name: sha256(path)
        for path in (
            Path(__file__),
            APP / "scripts/calculate_cohort_outputs.py",
            APP / "scripts/diagnose_fair_sign_change.py",
            APP / "scripts/audit_energy_and_pulse.py",
            APP / "scripts/audit_beccs_pulse_balance.py",
        )
    }
    run["foreground_sha256"] = foreground
    run["cohort_foreground_sha256"] = sha256(
        workspace / "data/inventories/generated/lcss2026-routing-cohorts.xlsx"
    )
    diagnostic_path = source / "diagnostic_legacy_uptake_sign.json"
    if diagnostic_path.exists():
        diagnostic = json.loads(diagnostic_path.read_text())
        assert diagnostic["diagnostic_only"] is True
        assert diagnostic["package_sha256"] == expected_package
        assert diagnostic["foreground_sha256"] == foreground
        run["fair_sign_diagnostic"] = {
            "trails_fix_commit": "de32b19d2552892e98b246149409fa40c0f3e0c2",
            "description": diagnostic["mapping_override"],
            "script": "apps/setac_2026/scripts/diagnose_fair_sign_change.py",
            "window": [2020, 2030, 2100],
            "cases": {
                case: {
                    "legacy_mapping_only_kg_co2_per_net_tonne": values[
                        "radiative forcing"
                    ]["trails_config_first_kg_co2_per_net_tonne"]["median"],
                    "corrected_kg_co2_per_net_tonne": values[
                        "corrected_rf_kg_co2_per_net_tonne"
                    ],
                }
                for case, values in diagnostic["cases"].items()
            },
        }
    run["output_sha256"] = {
        p.name: sha256(p) for p in sorted(destination.iterdir()) if p.is_file()
    }
    run["default_pulse_kg_co2eq"] = dict(
        zip(("BECCS", "DACCS"), map(float, default_values))
    )
    run["temporal_totals_kg_co2eq"] = {
        case: sum(
            float(r["score_per_net_tonne_kg_co2eq"])
            for r in temporal
            if r["case"] == case
        )
        for case in ("BECCS", "DACCS")
    }
    run["forcing_summary"] = audit["total_response"]
    (APP / "data/regeneration.json").write_text(json.dumps(run, indent=2) + "\n")
    print(
        json.dumps(
            {k: run[k] for k in ("default_pulse_kg_co2eq", "temporal_totals_kg_co2eq")},
            indent=2,
        ),
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-project", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--steps", nargs="+", choices=STEPS, default=list(STEPS))
    args = parser.parse_args()
    source, package, workspace = (
        p.resolve() for p in (args.source_project, args.package, args.workspace)
    )
    for step in args.steps:
        print(f"=== {step} ===", flush=True)
        if step == "prepare":
            prepare(source, package, workspace)
            continue
        if step == "mixes":
            extract_mixes(workspace)
            continue
        if step == "publish":
            publish(workspace)
            continue
        if step == "cohort":
            subprocess.run(
                [
                    sys.executable,
                    str(APP / "scripts/calculate_cohort_outputs.py"),
                    "--workspace",
                    str(workspace),
                    "--package",
                    str(package),
                ],
                check=True,
            )
            continue
        if step in ("energy_audit", "pulse_audit"):
            subprocess.run(
                [
                    sys.executable,
                    str(APP / "scripts/audit_energy_and_pulse.py"),
                    "--workspace",
                    str(workspace),
                    "--package",
                    str(package),
                    "--step",
                    step.removesuffix("_audit"),
                ],
                check=True,
            )
            continue
        if step == "balance_audit":
            subprocess.run(
                [
                    sys.executable,
                    str(APP / "scripts/audit_beccs_pulse_balance.py"),
                    "--workspace",
                    str(workspace),
                ],
                check=True,
            )
            continue
        if step == "pulse":
            # Use the exact species inventory already solved for GWP and forcing.
            # Validate every input and cache hash before replacing the costly LCI step.
            path = workspace / "scripts/calculate_cohort_pulse_equivalence_grid.py"
            marker = '    """Return the routed cohort inventory grouped by mapped FaIR species."""\n'
            replacement = marker + """
    import pandas as pd
    cached = ROOT / "data/processed" / f"fair-species-{case}.csv"
    metadata = json.loads(cached.with_suffix(".json").read_text())
    for field, path in (
        ("package_sha256", package), ("foreground_sha256", foreground),
        ("cohort_foreground_sha256", cohort_foreground),
        ("config_sha256", ROOT / "data/inventories/parameters.json"),
        ("csv_sha256", cached),
    ):
        if sha256(path) != metadata[field]:
            raise ValueError(f"Stale inventory cache: {case}, {field}")
    return pd.read_csv(cached, index_col=0)
"""
            if "Stale inventory cache" not in path.read_text():
                replace_once(path, marker, replacement)
        commands = {
            "foreground": [
                ("scripts/prepare_foreground_inventories.py",),
                ("scripts/prepare_routing_cohorts.py",),
            ],
            "static": [("scripts/calculate_static_results.py",)],
            "attribution": [("dev/diagnose_beccs_heat_contribution.py",)],
            "pulse": [
                (
                    "scripts/calculate_cohort_pulse_equivalence_grid.py",
                    "--package",
                    str(package),
                    "--show-progress",
                )
            ],
            "validation": [
                (
                    "scripts/validate_cohort_pulse_equivalence.py",
                    "--package",
                    str(package),
                    "--window-start",
                    "2020",
                    "--window-end",
                    "2100",
                    "--reference-year",
                    "2030",
                )
            ],
            "reference": [
                ("scripts/calculate_co2_reference_pulse.py", "--pulse-year", "2030")
            ],
            "system": [("scripts/build_system_inventory.py",)],
        }
        for command in commands[step]:
            subprocess.run([sys.executable, *command], cwd=workspace, check=True)


if __name__ == "__main__":
    main()
