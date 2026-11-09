#!/usr/bin/env python3
"""Precompute the four-control cumulative sensitivity used on slide 9."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime

from apps.kent_2026 import results as runtime_results
from apps.kent_2026.scripts.generate_results import (
    ANCHOR_YEARS,
    OUTPUT,
    calculate_batch,
    calculate_batched,
    interpolate_profiles,
)

LIFETIMES = [150_000, 200_000, 250_000, 300_000]
MILEAGES = [5_000, 8_000, 12_000, 20_000]

ELECTRICITY = {
    "reference": {"case": "baseline", "label": "SSP2-NPi + Reference"},
    "mid": {"case": None, "label": "Mid-transition · interpolated"},
    "transition": {"case": "transition", "label": "SSP2-PkBudg1000 + NDC/LTS"},
    "rapid": {"case": "rapid", "label": "SSP2-PkBudg650 + 1.5°C"},
}
FUELS = {
    "petrol": {"case": "baseline", "label": "Petrol blend"},
    "e20": {"case": "fuel_e20", "label": "E20 · corn"},
    "e50": {"case": "fuel_e50", "label": "E50 · corn"},
    "e85": {"case": "fuel_e85", "label": "E85 · corn"},
}


def key(lifetime: int, annual: int, electricity: str, fuel: str) -> str:
    return f"{lifetime}|{annual}|{electricity}|{fuel}"


def main() -> None:
    result_path = OUTPUT / "results.json"
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    profiles = payload["profiles"]
    variants = [
        {
            "label": f"m{annual}_l{lifetime}",
            "annual_km": annual,
            "lifetime_km": lifetime,
        }
        for lifetime in LIFETIMES
        for annual in MILEAGES
    ]

    if "--compose-only" not in sys.argv:
        for scenario, powertrains in (
            ("baseline", ["ICEV-p", "BEV"]),
            ("transition", ["BEV"]),
            ("rapid", ["BEV"]),
        ):
            calculate_batched(
                profiles,
                case=scenario,
                years=ANCHOR_YEARS,
                sizes=["Medium"],
                powertrains=powertrains,
                variants=variants,
            )
            interpolate_profiles(
                profiles,
                case=scenario,
                sizes=["Medium"],
                powertrains=powertrains,
                variants=variants,
            )

        for scenario, blend in (
            ("fuel_e20", "e20"),
            ("fuel_e50", "e50"),
            ("fuel_e85", "e85"),
        ):
            calculate_batch(
                profiles,
                case=scenario,
                years=[2020],
                sizes=["Medium"],
                powertrains=["ICEV-p"],
                variants=variants,
                fuel=blend,
            )

        result_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    runtime_results.bundle.cache_clear()

    configurations = {}
    years = list(range(2018, 2061))
    for lifetime in LIFETIMES:
        for annual in MILEAGES:
            for electricity, electricity_data in ELECTRICITY.items():
                for fuel, fuel_data in FUELS.items():
                    electricity_cases = (
                        ("baseline", "transition")
                        if electricity == "mid"
                        else (electricity_data["case"],)
                    )
                    case_results = [
                        runtime_results.ownership_case(
                            decision_year=2026,
                            annual_km=annual,
                            lifetime_km=lifetime,
                            case=fuel_data["case"],
                            successor_case=electricity_case,
                        )
                        for electricity_case in electricity_cases
                    ]
                    cumulative_pairs = [
                        (
                            [value / 1000 for value in runtime_results.cumulative(item["keep"], "climate change", start=2018)],
                            [value / 1000 for value in runtime_results.cumulative(item["replace"], "climate change", start=2018)],
                        )
                        for item in case_results
                    ]
                    keep_t = [sum(values) / len(values) for values in zip(*(item[0] for item in cumulative_pairs))]
                    replace_t = [sum(values) / len(values) for values in zip(*(item[1] for item in cumulative_pairs))]
                    pm_pairs = [
                        (
                            [value * 1000 for value in runtime_results.cumulative(item["keep"], "particulate matter formation", start=2018)],
                            [value * 1000 for value in runtime_results.cumulative(item["replace"], "particulate matter formation", start=2018)],
                        )
                        for item in case_results
                    ]
                    keep_pm = [sum(values) / len(values) for values in zip(*(item[0] for item in pm_pairs))]
                    replace_pm = [sum(values) / len(values) for values in zip(*(item[1] for item in pm_pairs))]
                    case_result = case_results[0]
                    persistent_crossing = next(
                        (
                            year
                            for position, year in enumerate(years)
                            if year > 2026
                            and all(
                                replace <= keep
                                for keep, replace in zip(keep_t[position:], replace_t[position:])
                            )
                        ),
                        None,
                    )
                    pm_persistent_crossing = next(
                        (
                            year
                            for position, year in enumerate(years)
                            if year > 2026
                            and all(
                                replace <= keep
                                for keep, replace in zip(keep_pm[position:], replace_pm[position:])
                            )
                        ),
                        None,
                    )
                    configurations[key(lifetime, annual, electricity, fuel)] = {
                        "years": years,
                        "keep_t": keep_t,
                        "replace_t": replace_t,
                        "break_even_year": persistent_crossing,
                        "delta_2060_t": replace_t[-1] - keep_t[-1],
                        "keep_pm_milli": keep_pm,
                        "replace_pm_milli": replace_pm,
                        "pm_break_even_year": pm_persistent_crossing,
                        "pm_delta_2060_milli": replace_pm[-1] - keep_pm[-1],
                        "keep_cohorts": case_result["keep"]["cohorts"],
                        "replace_cohorts": case_result["replace"]["cohorts"],
                    }

    sensitivity = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": {
            "country": "US",
            "decision_after": 2026,
            "end_year": 2060,
            "current_vehicle": "2020 medium gasoline car",
            "successor": "medium BEV",
            "background": "REMIND SSP2-NPi",
            "indicators": ["EF 3.1 climate change", "EF 3.1 particulate matter formation"],
        },
        "dimensions": {
            "lifetime_km": LIFETIMES,
            "annual_km": MILEAGES,
            "electricity": ELECTRICITY,
            "fuel": FUELS,
        },
        "configurations": configurations,
    }
    (OUTPUT / "slide9_sensitivity.json").write_text(
        json.dumps(sensitivity, separators=(",", ":")), encoding="utf-8"
    )

    manifest_path = OUTPUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["configuration"]["backgrounds"]["fuel_e20"] = [
        "SSP2-NPi", "geco-2025-reference"
    ]
    manifest["configuration"]["backgrounds"]["fuel_e50"] = [
        "SSP2-NPi", "geco-2025-reference"
    ]
    manifest["configuration"]["fuel_routes"]["e20"] = (
        "20% corn-starch ethanol by volume; balance petrol"
    )
    manifest["configuration"]["fuel_routes"]["e50"] = (
        "50% corn-starch ethanol by volume; balance petrol"
    )
    manifest["results_sha256"] = hashlib.sha256(result_path.read_bytes()).hexdigest()
    manifest["slide9_sensitivity_sha256"] = hashlib.sha256(
        (OUTPUT / "slide9_sensitivity.json").read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(
        f"Wrote {len(configurations)} slide-9 configurations and "
        f"{len(profiles):,} source profiles"
    )


if __name__ == "__main__":
    main()
