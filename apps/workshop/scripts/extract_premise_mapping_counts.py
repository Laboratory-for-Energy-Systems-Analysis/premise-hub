#!/usr/bin/env python3
"""Count distinct IAM variables referenced by premise mapping YAML files."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "premise_mapping_counts.csv"
MODELS = ["image", "message", "remind", "remind-eu", "tiam-ucl", "gcam"]
SECTOR_FILES = {
    "Electricity": "electricity.yaml",
    "Final energy": "final_energy.yaml",
    "Fuels": "fuels.yaml",
    "Cement": "cement.yaml",
    "Steel": "steel.yaml",
    "Passenger cars": "transport_passenger_cars.yaml",
    "Road freight": "transport_road_freight.yaml",
    "Heat": "heat.yaml",
    "Carbon removal": "carbon_dioxide_removal.yaml",
    "Biomass": "biomass.yaml",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count model-specific IAM aliases in premise mapping YAML files."
    )
    parser.add_argument(
        "mapping_dir",
        type=Path,
        help="Path to premise/iam_variables_mapping",
    )
    parser.add_argument("--premise-version", default="2.4.6")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for value_item in value for item in strings(value_item)}
    return set()


def collect_model_variables(value: object, variables: dict[str, set[str]]) -> None:
    if isinstance(value, dict):
        if set(value).intersection(MODELS):
            for model in MODELS:
                if model in value:
                    variables[model].update(strings(value[model]))
        for child in value.values():
            collect_model_variables(child, variables)
    elif isinstance(value, list):
        for child in value:
            collect_model_variables(child, variables)


def main() -> None:
    args = parse_args()
    records: list[dict[str, object]] = []
    for sector, filename in SECTOR_FILES.items():
        path = args.mapping_dir / filename
        if not path.is_file():
            raise SystemExit(f"Missing premise mapping file: {path}")
        with path.open(encoding="utf-8") as stream:
            mapping = yaml.safe_load(stream)
        variables = {model: set() for model in MODELS}
        collect_model_variables(mapping, variables)
        for model in MODELS:
            records.append(
                {
                    "premise_version": args.premise_version,
                    "sector": sector,
                    "model": model,
                    "mapped_variable_count": len(variables[model]),
                    "source_file": filename,
                    "counting_rule": (
                        "Distinct strings under model-specific alias dictionaries; "
                        "includes IAM activity, efficiency and energy-use aliases."
                    ),
                }
            )

    output = pd.DataFrame.from_records(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    print(f"Wrote {len(output)} rows to {args.output}")


if __name__ == "__main__":
    main()
