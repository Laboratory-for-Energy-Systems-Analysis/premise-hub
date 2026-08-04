#!/usr/bin/env python3
"""Validate the compact workshop dataset without needing dashboard packages."""

from __future__ import annotations

import csv
import gzip
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "workshop_pathways.csv.gz"
CORE_SCENARIOS = {"SSP1-L", "SSP2-M", "SSP3-H", "SSP2-VLHO"}
CONTEXT_SECTORS = {
    "Population",
    "Gross Domestic Product",
    "Carbon Dioxide emissions",
    "GMST increase",
    "Electricity",
    "Steel",
}
EXPANDED_SECTORS = {
    "Final Energy",
    "Transport Passenger Cars",
    "Transport Road Freight",
    "Cement",
    "Hydrogen",
    "Biomass",
}
TARGET_YEARS = {2020, 2040, 2060}


def main() -> None:
    with gzip.open(DATA, "rt", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows, "processed dataset is empty"
    image_scenarios = {row["scenario"] for row in rows if row["model"] == "image"}
    assert CORE_SCENARIOS <= image_scenarios, image_scenarios
    models = {row["model"] for row in rows}
    assert models == {
        "image",
        "message",
        "remind",
        "remind-eu",
        "tiam-ucl",
        "gcam",
    }, models
    sectors = {row["sector"] for row in rows}
    assert EXPANDED_SECTORS <= sectors, sectors

    coverage: dict[tuple[str, str], set[int]] = defaultdict(set)
    for row in rows:
        if row["model"] == "image":
            coverage[(row["scenario"], row["sector"])].add(int(row["year"]))
    for scenario in CORE_SCENARIOS:
        for sector in CONTEXT_SECTORS:
            assert TARGET_YEARS <= coverage[(scenario, sector)], (
                scenario,
                sector,
                coverage[(scenario, sector)],
            )

    co2_2020 = {
        row["model"]: float(row["display_value"])
        for row in rows
        if row["scenario"] == "SSP2-M"
        and row["sector"] == "Carbon Dioxide emissions"
        and int(row["year"]) == 2020
    }
    assert math.isclose(co2_2020["image"], 36.8343808627, rel_tol=1e-9)
    assert math.isclose(co2_2020["message"], 44.5627702620, rel_tol=1e-9)

    cdr_scenarios = {
        row["scenario"]
        for row in rows
        if row["model"] == "image" and row["sector"] == "Carbon Dioxide Removal"
    }
    assert "SSP3-H" not in cdr_scenarios, "missing CDR was filled unexpectedly"
    print(
        f"Validated {len(rows):,} rows, {len(models)} models and {len(CORE_SCENARIOS)} core scenarios"
    )


if __name__ == "__main__":
    main()
