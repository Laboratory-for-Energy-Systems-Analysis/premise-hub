"""Solve each cohort once for GWP, FaIR forcing and reusable species inventories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--cases", nargs="+", default=["BECCS", "DACCS"])
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    sys.path.insert(0, str(workspace))
    from datapackage import Package
    from trails import Trails
    from trails.fair_io import load_species_mapping
    from trails.fair_rf import (
        _inventory_delta_by_fair_species_for_trails,
        run_fair_delta_rf,
    )
    from scripts import calculate_cohort_temporal_scores as temporal
    from scripts import calculate_cohort_fair_responses as forcing
    from scripts import generate_routing_graphs as routing
    from workshop.lifetime import cohort_cases
    from workshop.temporal import enable_signed_technosphere_routing

    package = args.package.resolve()
    config_path = workspace / "data/inventories/parameters.json"
    config = json.loads(config_path.read_text())
    foreground = workspace / "data/inventories/generated/lcss2026-foreground.xlsx"
    cohort_foreground = foreground.with_name("lcss2026-routing-cohorts.xlsx")
    output = workspace / "data/processed"
    cohorts = cohort_cases(config, commissioning_year=temporal.START_YEAR)
    provenance = {
        "package_sha256": temporal.sha256(package),
        "foreground_sha256": temporal.sha256(foreground),
        "cohort_foreground_sha256": temporal.sha256(cohort_foreground),
    }
    for case in args.cases:
        print(
            f"Solving {case}: temporal GWP and FaIR from the same inventory", flush=True
        )
        with Trails(
            Package(str(package)),
            interpolate_annual=True,
            cache_interpolation=True,
            interpolation_start_year_offset=0,
            interpolation_end_year_offset=routing.TECHNOSPHERE_END_YEAR_OFFSETS[case],
            ei_version="3.12",
        ) as model:
            model.import_excel_inventory([foreground, cohort_foreground])
            if model.import_diagnostics.get("unlinked") or model.import_diagnostics.get(
                "new_flows"
            ):
                raise AssertionError(model.import_diagnostics)
            if case == "BECCS":
                forest = config["beccs"]["forest_feedstock"]
                routing.reset_background_temporal_exchanges(
                    model,
                    preserve_activity_names={forest["name"], forest["regrowth_name"]},
                )
                routing.apply_beccs_cohort_timing(model, temporal.START_YEAR, config)
            else:
                routing.apply_daccs_cohort_timing(model, temporal.START_YEAR, config)
            enable_signed_technosphere_routing(model)
            model.temporal_routing(
                start_year=temporal.START_YEAR,
                start_act_idx=routing.find_activity(
                    model, temporal.START_YEAR, routing.ROOTS[case]
                ),
                amount=routing.cohort_root_amount(case, config, temporal.START_YEAR),
                max_depth=routing.ROUTING_DEPTH,
                adaptive_relative_score_cutoff=None,
                min_amount=routing.ROUTING_MIN_AMOUNT,
                attribute_to_roots=True,
                show_progress=True,
            )
            attribution = temporal.reattribute_graph_to_physical_branches(model, case)
            model.lci(
                show_progress=True,
                attribute_to_roots=True,
                solver_mode="iterative",
                iterative_rtol=1e-5,
                iterative_maxiter=500,
                inventory_backend="factorized" if case == "BECCS" else "auto",
            )
            model.lcia(methods=[temporal.METHOD], ei_version="3.12")
            denominator = cohorts[case].lifetime_net_stored_kg / 1000
            scores = temporal.root_score_rows(
                model,
                case=case,
                denominator_tonnes=denominator,
                provenance=provenance,
                root_depths=attribution["root_depths"],
                config=config,
            )
            temporal.write_csv(output / f"temporal-{case}.csv", scores)
            print(
                f"{case}: {sum(float(r['score_per_net_tonne_kg_co2eq']) for r in scores):.6f} kg CO2-eq/net tonne",
                flush=True,
            )
            mapping, signs = load_species_mapping()
            delta, _years = _inventory_delta_by_fair_species_for_trails(
                model,
                mapping,
                signs,
                show_progress=True,
            )
            delta_path = output / f"fair-species-{case}.csv"
            delta.to_csv(delta_path)
            delta_path.with_suffix(".json").write_text(
                json.dumps(
                    {
                        **provenance,
                        "config_sha256": temporal.sha256(config_path),
                        "csv_sha256": temporal.sha256(delta_path),
                        "denominator_net_stored_tonnes": denominator,
                        "lci_diagnostics": str(model.lci_diagnostics),
                    },
                    indent=2,
                )
                + "\n"
            )
            run_fair_delta_rf(
                model,
                scenario=forcing.FAIR_SCENARIO,
                quantiles=list(forcing.QUANTILES),
                per_species_runs=True,
                per_species_workers=None,
                show_progress=True,
            )
            rows = forcing.response_rows(
                model,
                case=case,
                denominator_tonnes=denominator,
                provenance=provenance,
            )
            forcing.write_csv(output / f"forcing-{case}.csv", rows)
    # Per-case checkpoints allow a failed climate run to be resumed independently.
    for stem, destination in (
        ("temporal", "cohort_temporal_scores.csv"),
        ("forcing", "cohort_fair_responses.csv"),
    ):
        paths = [output / f"{stem}-{case}.csv" for case in ("BECCS", "DACCS")]
        if all(p.exists() for p in paths):
            with (output / destination).open("w") as target:
                for index, path in enumerate(paths):
                    with path.open() as source:
                        header = next(source)
                        if index == 0:
                            target.write(header)
                        for line in source:
                            target.write(line)


if __name__ == "__main__":
    main()
