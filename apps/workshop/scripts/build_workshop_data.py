#!/usr/bin/env python3
"""Build the public teaching extract from the ignored consolidated IAM CSV.

The extract keeps the four IMAGE teaching pathways at all native IMAGE regions,
plus World-level comparison rows for every model and scenario. Source values are
never filled or interpolated. The consolidated source lacks units, so every
sector admitted here has an explicit display rule and any model-specific scale
correction is visible below.
"""

from __future__ import annotations

import csv
import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "structured_data (2, 4, 4) + GCAM 2026.csv"
OUTPUT = ROOT / "data" / "processed" / "workshop_pathways.csv.gz"

CORE_IMAGE_SCENARIOS = {"SSP1-L", "SSP2-M", "SSP3-H", "SSP2-VLHO"}
SECTORS = {
    "Population",
    "Gross Domestic Product",
    "Carbon Dioxide emissions",
    "GMST increase",
    "Final Energy",
    "Electricity",
    "Transport Passenger Cars",
    "Transport Road Freight",
    "Steel",
    "Cement",
    "Hydrogen",
    "Biomass",
    "Carbon Dioxide Removal",
}

DISPLAY_RULES = {
    "Population": (1 / 1_000, "billion people"),
    "Gross Domestic Product": (1 / 1_000, "trillion US$ (PPP)"),
    "Carbon Dioxide emissions": (1 / 1_000_000_000, "Gt CO₂/yr"),
    "GMST increase": (1, "°C above 1850–1900"),
    "Final Energy": (1, "EJ/yr"),
    "Electricity": (1, "EJ/yr"),
    "Transport Passenger Cars": (1, "model activity unit"),
    "Transport Road Freight": (1, "model activity unit"),
    "Steel": (1, "Mt/yr"),
    "Cement": (1, "Mt/yr"),
    "Hydrogen": (1, "EJ/yr"),
    "Biomass": (1, "EJ/yr"),
    "Carbon Dioxide Removal": (1, "Mt CO₂/yr"),
}

MODEL_SECTOR_SCALE_OVERRIDES = {
    ("message", "Carbon Dioxide emissions"): 1 / 1_000,
}

MODEL_VERSIONS = {
    "image": "IMAGE 3.4",
    "message": "MESSAGEix-GLOBIOM-GAINS 2.1-M-R12",
    "remind": "REMIND",
    "remind-eu": "REMIND-EU",
    "tiam-ucl": "TIAM-UCL",
    "gcam": "GCAM 2026",
}

FIELDNAMES = [
    "model",
    "model_version",
    "scenario",
    "region",
    "year",
    "sector",
    "variable",
    "source_value",
    "display_value",
    "display_unit",
    "source_file_id",
]


def keep(row: dict[str, str]) -> bool:
    if row["sector"] not in SECTORS:
        return False
    if row["model"] == "image" and row["scenario"] in CORE_IMAGE_SCENARIOS:
        return True
    return row["region"] == "World"


def transform(row: dict[str, str]) -> dict[str, str | int | float]:
    source_value = float(row["val"])
    default_scale, unit = DISPLAY_RULES[row["sector"]]
    scale = MODEL_SECTOR_SCALE_OVERRIDES.get(
        (row["model"], row["sector"]), default_scale
    )
    return {
        "model": row["model"],
        "model_version": MODEL_VERSIONS.get(row["model"], row["model"]),
        "scenario": row["scenario"],
        "region": row["region"],
        "year": int(float(row["year"])),
        "sector": row["sector"],
        "variable": row["variables"],
        "source_value": source_value,
        "display_value": source_value * scale,
        "display_unit": unit,
        "source_file_id": SOURCE.name,
    }


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source dataset: {SOURCE}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows_written = 0
    with SOURCE.open(newline="", encoding="utf-8-sig") as source, gzip.open(
        OUTPUT, "wt", newline="", encoding="utf-8"
    ) as target:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(target, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in reader:
            if keep(row):
                writer.writerow(transform(row))
                rows_written += 1

    if rows_written == 0:
        raise SystemExit("No rows matched the workshop selection")
    print(f"Wrote {rows_written:,} rows to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
