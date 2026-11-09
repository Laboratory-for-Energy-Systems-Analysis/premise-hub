#!/usr/bin/env python3
"""Precompute the slide-10 3D keep/replace decision landscape."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from apps.kent_2026 import results


LIFETIMES = [150_000, 200_000, 250_000, 300_000]
MILEAGES = [5_000, 8_000, 12_000, 20_000]
DECISION_YEARS = list(range(2020, 2036))
HORIZONS = [2035, 2040, 2050, 2060]
INTENSITIES = [50, 150, 300, 450, 650]
REFERENCE_INTENSITY = 449.29186810850484
THRESHOLD_T = 2.0


def bev_use_impact(path: dict, annual_km: int, lifetime_km: int, stop: int) -> float:
    """Return climate impact from BEV operating electricity through ``stop``."""
    total = 0.0
    for cohort in path["cohorts"]:
        if cohort["powertrain"] != "BEV":
            continue
        start = int(cohort["cohort"])
        source = results.profile(
            cohort=start,
            powertrain="BEV",
            size=cohort["size"],
            annual_km=annual_km,
            lifetime_km=lifetime_km,
            case="baseline",
        )
        remaining = float(cohort["service_km"])
        year = start
        while remaining > 1e-9:
            capacity = float(cohort["first_year_km"] if year == start else annual_km)
            distance = min(capacity, remaining)
            if year <= stop:
                total += results._stage_rate(source, "climate change", "use", year) * distance
            remaining -= distance
            year += 1
    return total


def main() -> None:
    states = {}
    for lifetime in LIFETIMES:
        cases = {}
        for annual in MILEAGES:
            for decision in DECISION_YEARS:
                case = results.ownership_case(
                    decision_year=decision,
                    annual_km=annual,
                    lifetime_km=lifetime,
                )
                if case["valid"]:
                    cases[(annual, decision)] = case
        for horizon in HORIZONS:
            points = []
            ties = 0
            for annual in MILEAGES:
                for decision in DECISION_YEARS:
                    case = cases.get((annual, decision))
                    if case is None:
                        continue
                    baseline_delta = (
                        results.total(case["replace"], "climate change", stop=horizon)
                        - results.total(case["keep"], "climate change", stop=horizon)
                    ) / 1000
                    electricity_delta = (
                        bev_use_impact(case["replace"], annual, lifetime, horizon)
                        - bev_use_impact(case["keep"], annual, lifetime, horizon)
                    ) / 1000
                    for intensity in INTENSITIES:
                        delta = baseline_delta + (intensity / REFERENCE_INTENSITY - 1) * electricity_delta
                        outcome = "tie" if abs(delta) < THRESHOLD_T else ("keep" if delta > 0 else "replace")
                        if outcome == "tie":
                            ties += 1
                        points.append({
                            "decision_year": decision,
                            "annual_km": annual,
                            "intensity": intensity,
                            "delta_t": round(delta, 6),
                            "outcome": outcome,
                        })
            valid_cells = len(cases) * len(INTENSITIES)
            states[f"{lifetime}|{horizon}"] = {
                "points": points,
                "counts": {
                    "keep": sum(point["outcome"] == "keep" for point in points),
                    "replace": sum(point["outcome"] == "replace" for point in points),
                    "ties_hidden": ties,
                    "invalid": len(MILEAGES) * len(DECISION_YEARS) * len(INTENSITIES) - valid_cells,
                },
            }

    payload = {
        "schema_version": 2,
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": {
            "country": "US",
            "current_vehicle": "2020 medium gasoline car",
            "successor": "medium BEV",
            "background": "REMIND SSP2-NPi + GECO reference",
            "indicator": "EF 3.1 climate change",
            "gasoline": "carculator reference blend",
        },
        "method": {
            "threshold_t": THRESHOLD_T,
            "reference_intensity": REFERENCE_INTENSITY,
            "description": (
                "BEV use-stage climate impacts from the annual GECO reference profile are "
                "scaled to the carbon-intensity axis; all non-use impacts remain unchanged."
            ),
        },
        "dimensions": {
            "lifetime_km": LIFETIMES,
            "annual_km": MILEAGES,
            "decision_year": DECISION_YEARS,
            "horizon": HORIZONS,
            "intensity_g_per_kwh": INTENSITIES,
        },
        "states": states,
    }
    target = results.DATA_DIR / "slide10_landscape.json"
    target.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    manifest_path = results.DATA_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["slide10_landscape_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {len(states)} landscape states and {sum(len(v['points']) for v in states.values()):,} valid outcomes")


if __name__ == "__main__":
    main()
