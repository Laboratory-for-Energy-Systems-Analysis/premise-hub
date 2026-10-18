"""Explain BECCS pulse equivalence using the carbon balance and fresh FaIR runs.

The shifted-regrowth case is a diagnostic only; it does not replace the deck's
standing-forest reference or its post-harvest regrowth inventory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    sys.path.insert(0, str(workspace))
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
    from scripts.calculate_cohort_temporal_scores import sha256

    path = workspace / "data/processed"
    cache = path / "fair-species-BECCS.csv"
    metadata = json.loads(cache.with_suffix(".json").read_text())
    assert sha256(cache) == metadata["csv_sha256"]
    delta = pd.read_csv(cache, index_col=0)
    scores = pd.read_csv(path / "cohort_temporal_scores.csv")
    forest_rows = scores[
        (scores.case == "BECCS") & (scores.contributor == "Forest regrowth")
    ]
    denominator = metadata["denominator_net_stored_tonnes"]
    forest_series = forest_rows.groupby(
        "impact_year"
    ).score_per_net_tonne_kg_co2eq.sum()
    forest = delta * 0.0
    forest.loc[forest_series.index, "CO2 AFOLU"] = forest_series * denominator
    config = json.loads((workspace / "data/inventories/parameters.json").read_text())
    transport = config["co2_transport"]
    loss = (
        transport["pipeline_loss_kg_per_tonne_km"]
        * transport["pipeline_distance_km"]
        / 1000
    )
    capture_rate = config["beccs"]["capture_rate"]
    captured_per_tonne = 1000 / (1 - loss)
    stack_per_tonne = captured_per_tonne * (1 - capture_rate) / capture_rate
    loss_per_tonne = captured_per_tonne - 1000
    direct = delta * 0.0
    direct.loc[2030:2049, "CO2 AFOLU"] = (
        (stack_per_tonne + loss_per_tonne) / 20 * denominator
    )
    co2 = delta * 0.0
    co2[["CO2 FFI", "CO2 AFOLU"]] = delta[["CO2 FFI", "CO2 AFOLU"]]
    advanced_forest = delta * 0.0
    advanced_forest.loc[2030:2049, "CO2 AFOLU"] = forest_series.sum() / 20 * denominator
    variants = {
        "full_inventory": delta,
        "forest_regrowth": forest,
        "residual_stack_and_transport_co2": direct,
        "other_supply_chain_co2": co2 - forest - direct,
        "non_co2_species": delta - co2,
        "all_co2_only": co2,
        "diagnostic_regrowth_during_operation": delta - forest + advanced_forest,
    }
    scenario = "REMIND|SSP2-PkBudg1000"
    names = _all_config_names_from_csv(DEFAULT_CONFIGS_CSV, None, None)
    settings = dict(
        config_csv=DEFAULT_CONFIGS_CSV,
        config_names=names,
        ghg_method="myhre1998",
        temperature_prescribed=False,
        debug=False,
        progress=False,
    )
    baseline = _ensure_response_species_rows(
        load_emissions_csv(),
        scenario=scenario,
        drivers=list(delta.columns),
        debug=False,
    )
    baseline_run = _run_fair_emissions(baseline, scenario, **settings)
    base = _total_response_by_config(
        baseline_run.forcing, scenario=scenario, sum_species=True
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
        _total_response_by_config(
            ref_run.forcing, scenario=scenario, sum_species=True
        ).values
        - base.values
    )
    _, common_scale = perturbed_emissions(baseline, delta, scenario=scenario)
    world = baseline[
        (baseline.scenario == scenario) & (baseline.region.str.lower() == "world")
    ]
    results = {}
    scores_by_config = {}
    for name, gases in variants.items():
        print(f"FaIR carbon-balance audit: {name}", flush=True)
        frame, auto_scale = perturbed_emissions(baseline, gases, scenario=scenario)
        columns = [c for c in frame.columns if str(c).replace(".", "", 1).isdigit()]
        frame.loc[:, columns] = world.loc[
            frame.index, columns
        ] + common_scale / auto_scale * (
            frame.loc[:, columns] - world.loc[frame.index, columns]
        )
        run = _run_fair_emissions(frame, scenario, **settings)
        forcing = (
            _total_response_by_config(
                run.forcing, scenario=scenario, sum_species=True
            ).values
            - base.values
        ) / common_scale
        results[name] = {}
        for end in (2100, 2140, 2300):
            keep = (years >= 2020) & (years <= end)
            ratio = (
                1e9
                / denominator
                * np.trapezoid(forcing[:, keep], years[keep], axis=1)
                / np.trapezoid(reference[:, keep], years[keep], axis=1)
            )
            scores_by_config[name, end] = ratio
            results[name][str(end)] = float(np.median(ratio))
    # A common representative configuration makes the contribution sum legible;
    # medians of separate component ensembles would not be additive.
    middle = int(np.argsort(scores_by_config["full_inventory", 2100])[len(names) // 2])
    components = (
        "forest_regrowth",
        "residual_stack_and_transport_co2",
        "other_supply_chain_co2",
        "non_co2_species",
    )
    representative = {
        name: float(scores_by_config[name, 2100][middle]) for name in components
    }
    total = float(scores_by_config["full_inventory", 2100][middle])
    result = {
        "provenance": metadata,
        "window_start": 2020,
        "reference_year": 2030,
        "denominator_net_stored_tonnes": denominator,
        "physical_balance_kg_per_net_tonne": {
            "forest_regrowth_co2": float(forest_series.sum()),
            "captured_co2": captured_per_tonne,
            "residual_stack_co2": stack_per_tonne,
            "transport_loss_co2": loss_per_tonne,
            "direct_net_atmospheric_co2": float(forest_series.sum())
            + stack_per_tonne
            + loss_per_tonne,
            "all_inventory_net_co2": float(co2.sum().sum() / denominator),
        },
        "forest_timing": {
            "first_year": int(forest_series.index.min()),
            "last_year": int(forest_series.index.max()),
            "uptake_weighted_year": float(
                (forest_series * forest_series.index).sum() / forest_series.sum()
            ),
            "fraction_by_2100": float(
                forest_series.loc[:2100].sum() / forest_series.sum()
            ),
        },
        "ensemble_median_pulse_equivalents": results,
        "representative_config": {
            "name": str(base.coords["config"].values[middle]),
            "contributions": representative,
            "full_result": total,
            "nonadditivity_residual": total - sum(representative.values()),
        },
        "diagnostic_note": "Advancing regrowth to operation changes the physical timing assumption; it is not a correction or an alternative baseline result.",
    }
    (path / "beccs_carbon_balance_audit.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
