#!/usr/bin/env python3
"""Audit the checked-in Kent runtime bundle without importing Dash."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from apps.kent_2026 import results


def main() -> None:
    results.bundle.cache_clear()
    results.manifest.cache_clear()
    payload = results.bundle()
    manifest = results.manifest()
    path = results.DATA_DIR / "results.json"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == manifest["results_sha256"]
    assert len(payload["profiles"]) == 1_763
    assert len(payload["decision_maps"]) == 7
    assert len(payload["ef_categories"]) == 25
    assert all(len(profile["ef_midpoints_per_vkm"]) == 25 for profile in payload["profiles"].values())

    baseline = results.ownership_case()
    assert baseline["valid"]
    for category in ("climate change", "particulate matter formation"):
        keep = results.annual_totals(baseline["keep"], category)
        replace = results.annual_totals(baseline["replace"], category)
        assert keep[2019] == replace[2019]
        assert keep[2020] == replace[2020]
    for path in ("keep", "replace"):
        assert baseline[path]["cohorts"][-1]["last_use"] == 2060
        assert all(abs(distance - 12_000) < 1e-9 for distance in baseline[path]["service"].values())
        assert abs(sum(baseline[path]["service"].values()) - 12_000 * 41) < 1e-9

    conflict = baseline
    assert results.delta(conflict, "climate change") < 0
    assert results.delta(conflict, "particulate matter formation") > 0

    fuel_cases = (
        ("BEV", "baseline"),
        ("ICEV-p", "baseline"),
        ("ICEV-p", "fuel_e85"),
        ("ICEV-p", "fuel_synthetic"),
        ("FCEV", "fuel_hydrogen"),
    )
    fuel_deltas = []
    for powertrain, successor_case in fuel_cases:
        case = results.ownership_case(successor=powertrain, successor_case=successor_case)
        assert case["keep"]["cohorts"][-1]["last_use"] == 2060
        assert case["replace"]["cohorts"][-1]["last_use"] == 2060
        fuel_deltas.append(results.delta(case, "climate change"))
    assert len({round(value, 6) for value in fuel_deltas}) == len(fuel_deltas)

    electricity_deltas = [
        results.delta(results.ownership_case(case=case), "climate change")
        for case in ("baseline", "electricity_ndc", "electricity_15c")
    ]
    assert len({round(value, 6) for value in electricity_deltas}) == 3

    for state, decision_map in payload["decision_maps"].items():
        assert decision_map["annual_km"] == [5_000, 12_000, 20_000], state
        assert decision_map["decision_years"] == list(range(2020, 2036)), state
        for category in ("climate change", "particulate matter formation"):
            assert len(decision_map["values"][category]) == 3, state
        for annual_km in decision_map["annual_km"]:
            for decision_year in decision_map["decision_years"]:
                case = results.ownership_case(
                    decision_year=decision_year,
                    annual_km=annual_km,
                    lifetime_km=decision_map["lifetime"],
                    size=decision_map["size"],
                    case=decision_map["case"],
                )
                if not case["valid"]:
                    continue
                for path in ("keep", "replace"):
                    assert all(
                        abs(distance - annual_km) < 1e-9
                        for distance in case[path]["service"].values()
                    ), (state, annual_km, decision_year, path)

    print(f"Kent result audit passed · {len(payload['profiles']):,} profiles · SHA-256 {digest}")


if __name__ == "__main__":
    main()
