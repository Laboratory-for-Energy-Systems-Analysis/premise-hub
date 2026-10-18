"""Audit energy signs before flow netting and independently integrate FaIR runs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def energy(workspace, package):
    import numpy as np
    from datapackage import Package
    from trails import Trails
    from trails.characterization import _build_cf_matrix_flowid_space
    from trails.fair_rf import _inventory_flow_year_root
    from scripts import calculate_cohort_temporal_scores as temporal
    from scripts import generate_routing_graphs as routing
    from workshop.lifetime import cohort_cases
    from workshop.temporal import enable_signed_technosphere_routing

    config_path = workspace / "data/inventories/parameters.json"
    config = json.loads(config_path.read_text())
    foreground = workspace / "data/inventories/generated/lcss2026-foreground.xlsx"
    cohort = foreground.with_name("lcss2026-routing-cohorts.xlsx")
    cohorts = cohort_cases(config, commissioning_year=2030)
    rows = []
    for case in ("BECCS", "DACCS"):
        print(f"Auditing signed energy flows for {case}", flush=True)
        with Trails(
            Package(str(package)),
            interpolate_annual=True,
            cache_interpolation=True,
            interpolation_start_year_offset=0,
            interpolation_end_year_offset=routing.TECHNOSPHERE_END_YEAR_OFFSETS[case],
            ei_version="3.12",
        ) as model:
            model.import_excel_inventory([foreground, cohort])
            assert not model.import_diagnostics.get("unlinked")
            if case == "BECCS":
                forest = config["beccs"]["forest_feedstock"]
                routing.reset_background_temporal_exchanges(
                    model,
                    preserve_activity_names={forest["name"], forest["regrowth_name"]},
                )
                routing.apply_beccs_cohort_timing(model, 2030, config)
            else:
                routing.apply_daccs_cohort_timing(model, 2030, config)
            enable_signed_technosphere_routing(model)
            model.temporal_routing(
                start_year=2030,
                start_act_idx=routing.find_activity(model, 2030, routing.ROOTS[case]),
                amount=routing.cohort_root_amount(case, config, 2030),
                max_depth=routing.ROUTING_DEPTH,
                adaptive_relative_score_cutoff=None,
                min_amount=routing.ROUTING_MIN_AMOUNT,
                attribute_to_roots=True,
                show_progress=False,
            )
            temporal.reattribute_graph_to_physical_branches(model, case)
            model.lci(
                show_progress=False,
                attribute_to_roots=True,
                solver_mode="iterative",
                iterative_rtol=1e-5,
                iterative_maxiter=500,
                inventory_backend="factorized" if case == "BECCS" else "auto",
            )
            # Reduce only the activity axis using TRAILS' guarded sparse path.
            # Characterize each (flow, year, root) before separating its sign.
            cf = _build_cf_matrix_flowid_space(model, [temporal.METHOD], "3.12", {})[0]
            data = _inventory_flow_year_root(
                model.inventory,
                flow_positions=np.flatnonzero(cf).tolist(),
                builder=getattr(model, "_inventory_builder", None),
                show_progress=False,
            ).asformat("coo")
            roots = model.inventory.coords["root activity"].values
            years = model.inventory.coords["year"].values
            flows = model.inventory.coords["flow"].values
            root_metadata = temporal.activity_metadata(model, 2030)
            biosphere = model.biosphere_indices[
                str(model._map_year_to_template_year(2030))
            ]
            denominator = cohorts[case].lifetime_net_stored_kg / 1000
            for f, y, r, value in zip(*data.coords, data.data, strict=True):
                root = root_metadata[int(roots[r])]
                label = (
                    temporal.beccs_temporal_category(root)
                    if case == "BECCS"
                    else root["reference product"]
                )
                energy_roots = (
                    {
                        "Harvesting and biomass supply",
                        "Compression and recompression",
                        "Avoided Northern European electricity",
                        "Avoided Northern European heat",
                    }
                    if case == "BECCS"
                    else {
                        "electricity, medium voltage",
                        "diesel, burned in diesel-electric generating set, 10MW",
                    }
                )
                if label not in energy_roots:
                    continue
                score = float(value * cf[f] / denominator)
                if abs(score) < 1e-12:
                    continue
                flow = biosphere[int(flows[f])]
                rows.append(
                    dict(
                        case=case,
                        impact_year=int(years[y]),
                        root_activity_index=int(roots[r]),
                        root=label,
                        flow=flow["name"],
                        compartment=flow["compartment"],
                        subcompartment=flow["subcompartment"],
                        sign=1 if score > 0 else -1,
                        score_per_net_tonne_kg_co2eq=score,
                    )
                )
    output = workspace / "data/processed/energy_flow_signs.csv"
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    output.with_suffix(".json").write_text(
        json.dumps(
            dict(
                package_sha256=digest(package),
                foreground_sha256=digest(foreground),
                cohort_foreground_sha256=digest(cohort),
                config_sha256=digest(config_path),
                csv_sha256=digest(output),
                script_sha256=digest(__file__),
                convention="Characterize activity-reduced flow/year/root inventory, then separate positive and negative scores; not gross activity-level emissions.",
            ),
            indent=2,
        )
        + "\n"
    )
    print(f"Wrote {len(rows)} energy flow contributions", flush=True)


def pulse(workspace, package):
    import numpy as np
    import pandas as pd
    from trails.fair_io import DEFAULT_CONFIGS_CSV, load_emissions_csv
    from trails.fair_rf import (
        _all_config_names_from_csv,
        _ensure_response_species_rows,
        _run_fair_emissions,
        _total_response_by_config,
        make_reference_co2_pulse_emissions,
    )
    from scripts.calculate_cohort_pulse_equivalence_grid import perturbed_emissions

    output = workspace / "data/processed"
    scenario = "REMIND|SSP2-PkBudg1000"
    settings = dict(
        config_csv=DEFAULT_CONFIGS_CSV,
        config_names=_all_config_names_from_csv(DEFAULT_CONFIGS_CSV, None, None),
        ghg_method="myhre1998",
        temperature_prescribed=False,
        debug=False,
        progress=False,
    )
    results = {
        "package_sha256": digest(package),
        "reference_year": 2030,
        "window_start": 2020,
        "config_count": len(settings["config_names"]),
        "cases": {},
    }
    templates = {}
    with (output / "cohort_fair_responses.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            templates.setdefault((row["case"], row["metric"]), row)
    total_rows = []
    ensembles = {}
    timestamp = datetime.now(timezone.utc).isoformat()
    for case in ("BECCS", "DACCS"):
        metadata = json.loads((output / f"fair-species-{case}.json").read_text())
        for field, path in (
            ("csv_sha256", output / f"fair-species-{case}.csv"),
            ("package_sha256", package),
            (
                "foreground_sha256",
                workspace / "data/inventories/generated/lcss2026-foreground.xlsx",
            ),
            (
                "cohort_foreground_sha256",
                workspace / "data/inventories/generated/lcss2026-routing-cohorts.xlsx",
            ),
            ("config_sha256", workspace / "data/inventories/parameters.json"),
        ):
            assert metadata[field] == digest(path), (case, field)
        delta = pd.read_csv(output / f"fair-species-{case}.csv", index_col=0)
        baseline = _ensure_response_species_rows(
            load_emissions_csv(),
            scenario=scenario,
            drivers=list(delta.columns),
            debug=False,
        )
        perturbed, scale = perturbed_emissions(baseline, delta, scenario=scenario)
        base_run = _run_fair_emissions(baseline, scenario, **settings)
        base = _total_response_by_config(
            base_run.forcing, scenario=scenario, sum_species=True
        )
        years = np.asarray(base.coords["timebounds"].values)
        ref_run = _run_fair_emissions(
            make_reference_co2_pulse_emissions(
                baseline, scenario=scenario, pulse_year=2030, pulse_mass_kg=1e9
            ),
            scenario,
            **settings,
        )
        reference = (
            np.asarray(
                _total_response_by_config(
                    ref_run.forcing, scenario=scenario, sum_species=True
                ).values
            )
            - base.values
        )
        denominator = metadata["denominator_net_stored_tonnes"]
        values = {}
        for factor in (1.0, 0.1):
            print(
                f"Direct FaIR integration {case}, perturbation factor {factor}",
                flush=True,
            )
            # Rescale the perturbation only; leave baseline and reference fixed.
            frame = perturbed.copy()
            world = baseline[
                (baseline.scenario == scenario)
                & (baseline.region.str.lower() == "world")
            ]
            columns = [c for c in frame.columns if str(c).replace(".", "", 1).isdigit()]
            frame.loc[:, columns] = world.loc[frame.index, columns] + factor * (
                perturbed.loc[:, columns] - world.loc[frame.index, columns]
            )
            run = _run_fair_emissions(frame, scenario, **settings)
            system = (
                np.asarray(
                    _total_response_by_config(
                        run.forcing, scenario=scenario, sum_species=True
                    ).values
                )
                - base.values
            ) / (scale * factor)
            if factor == 1.0:
                # Summarize the total perturbation AFTER combining all gases
                # within each configuration, as in the pulse-equivalence run.
                # Retain ensembles locally for independent reduction checks.
                keep_response = (years >= 1940) & (years <= 2300)
                ensembles["years"] = years[keep_response]
                ensembles[f"{case}_reference_rf_per_kg"] = (
                    reference[:, keep_response] / 1e9
                )
                temperature = (
                    _total_response_by_config(
                        run.temperature, scenario=scenario, sum_species=False
                    ).values
                    - _total_response_by_config(
                        base_run.temperature, scenario=scenario, sum_species=False
                    ).values
                ) / scale
                for metric, response in (
                    ("radiative forcing", system),
                    ("temperature anomaly", temperature),
                ):
                    per_tonne = response[:, keep_response] / denominator
                    ensembles[f"{case}_{metric}"] = per_tonne
                    quantiles = np.percentile(per_tonne, [2.5, 50.0, 97.5], axis=0)
                    for quantile, values_by_year in zip(
                        (2.5, 50.0, 97.5), quantiles, strict=True
                    ):
                        for year, value in zip(
                            years[keep_response], values_by_year, strict=True
                        ):
                            total_rows.append(
                                dict(
                                    templates[case, metric],
                                    response_year=float(year),
                                    quantile=quantile,
                                    contribution_view="total",
                                    contributor="All emissions and removals",
                                    value_per_net_tonne=float(value),
                                    calculation_timestamp=timestamp,
                                )
                            )
            values[str(factor)] = {}
            for end in (2100, 2140, 2300):
                keep = (years >= 2020) & (years <= end)
                # Independent trapezoidal integration, with no TRAILS metric/grid helper.
                ratio = (
                    1e9
                    * np.trapezoid(system[:, keep], years[keep], axis=1)
                    / np.trapezoid(reference[:, keep], years[keep], axis=1)
                    / denominator
                )
                values[str(factor)][str(end)] = float(np.median(ratio))
        results["cases"][case] = dict(
            auto_scale=scale, values_kg_co2_per_net_tonne=values
        )
    total_path = output / "cohort_fair_total_responses.csv"
    with total_path.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=list(total_rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(total_rows)
    np.savez_compressed(output / "cohort_fair_total_ensembles.npz", **ensembles)
    results["total_response"] = {
        "csv_sha256": digest(total_path),
        "summary_convention": "Total all-gas scenario perturbation per configuration, then pointwise ensemble quantiles.",
        "scenario": scenario,
        "display_window": [1940, 2300],
        "timebounds_years": [
            float(ensembles["years"][0]),
            float(ensembles["years"][-1]),
        ],
        "config_csv_sha256": digest(DEFAULT_CONFIGS_CSV),
    }
    (output / "pulse_integration_audit.json").write_text(
        json.dumps(results, indent=2) + "\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--step", choices=("energy", "pulse"), required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    sys.path.insert(0, str(workspace))
    {"energy": energy, "pulse": pulse}[args.step](workspace, args.package.resolve())


if __name__ == "__main__":
    main()
