#!/usr/bin/env python3
"""Extract the REMIND electrolysis example used on the IAM mechanics slide."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "remind_hydrogen_mechanics.csv"
YEARS = [str(year) for year in range(2020, 2061, 5)]
METRICS = {
    "Energy Investments|Hydrogen|+|Electrolysis": "annual_investment",
    "SE|Hydrogen|+|Electricity": "hydrogen_output",
    "Tech|Hydrogen|Electricity|Efficiency": "conversion_efficiency",
}
FIELDNAMES = [
    "model",
    "model_version",
    "scenario",
    "region",
    "metric",
    "variable",
    "year",
    "value",
    "unit",
    "source_file_id",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract World-level REMIND electrolysis mechanics series."
    )
    parser.add_argument("input", type=Path, help="REMIND SSP2-PkBudg650 MIF file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model-version", default="REMIND 3.5")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected: dict[str, dict[str, str]] = {}
    with args.input.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream, delimiter=";"):
            variable = row["Variable"]
            if row["Region"] == "World" and variable in METRICS:
                selected[variable] = row

    missing = set(METRICS) - set(selected)
    if missing:
        raise SystemExit(f"Missing required REMIND variables: {sorted(missing)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for variable, metric in METRICS.items():
            row = selected[variable]
            for year in YEARS:
                writer.writerow(
                    {
                        "model": row["Model"],
                        "model_version": args.model_version,
                        "scenario": row["Scenario"],
                        "region": row["Region"],
                        "metric": metric,
                        "variable": variable,
                        "year": year,
                        "value": f"{float(row[year]):.6f}",
                        "unit": row["Unit"],
                        "source_file_id": args.input.name,
                    }
                )

    print(f"Wrote {len(METRICS) * len(YEARS)} rows to {args.output}")


if __name__ == "__main__":
    main()
