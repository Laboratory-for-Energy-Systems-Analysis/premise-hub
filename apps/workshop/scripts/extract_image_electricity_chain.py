#!/usr/bin/env python3
"""Extract an auditable IMAGE electricity-chain example for the workshop."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "image_electricity_chain_example.csv"
SOURCE_FILE = "IMAGE 3.4_SSP2_VLHO.xlsx"
SOURCE_REGIONS = ["WEU", "CEU"]
YEARS = [str(year) for year in range(2020, 2101, 10)]

SERIES = {
    ("Primary input to electricity", "Fossil"): [
        "Primary Energy|Coal|Electricity",
        "Primary Energy|Gas|Electricity",
        "Primary Energy|Oil|Electricity",
    ],
    ("Primary input to electricity", "Biomass"): ["Primary Energy|Biomass|Electricity"],
    ("Primary input to electricity", "Nuclear + hydro"): [
        "Primary Energy|Nuclear",
        "Primary Energy|Hydro",
    ],
    ("Primary input to electricity", "Wind + solar"): [
        "Primary Energy|Wind",
        "Primary Energy|Solar",
    ],
    ("Secondary electricity", "Electricity output"): [
        "Secondary Energy|Electricity|Biomass",
        "Secondary Energy|Electricity|Coal",
        "Secondary Energy|Electricity|Gas",
        "Secondary Energy|Electricity|Geothermal",
        "Secondary Energy|Electricity|Hydro",
        "Secondary Energy|Electricity|Hydrogen",
        "Secondary Energy|Electricity|Nuclear",
        "Secondary Energy|Electricity|Oil",
        "Secondary Energy|Electricity|Other",
        "Secondary Energy|Electricity|Solar|CSP",
        "Secondary Energy|Electricity|Solar|PV|1",
        "Secondary Energy|Electricity|Solar|PV|2",
        "Secondary Energy|Electricity|Storage",
        "Secondary Energy|Electricity|Wave",
        "Secondary Energy|Electricity|Wind|1",
        "Secondary Energy|Electricity|Wind|2",
    ],
    ("Final electricity", "Passenger transport"): [
        "Final Energy|Transportation|Passenger|Bus|Electricity",
        "Final Energy|Transportation|Passenger|Domestic Aviation|Electricity",
        "Final Energy|Transportation|Passenger|International Aviation|Electricity",
        "Final Energy|Transportation|Passenger|Light Duty Vehicle|Electricity",
        "Final Energy|Transportation|Passenger|Rail (high speed)|Electricity",
        "Final Energy|Transportation|Passenger|Rail (low speed)|Electricity",
    ],
    ("Final electricity", "Space heating"): [
        "Final Energy|Residential|Space Heating|Electricity",
        "Final Energy|Commercial|Space Heating|Electricity",
    ],
    ("Energy service", "Passenger mobility"): [
        "Energy Service|Transportation|Passenger"
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract the IMAGE SSP2-VLHO European electricity-chain example."
    )
    parser.add_argument(
        "input_dir", type=Path, help="Directory containing IMAGE xlsx files"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = args.input_dir / SOURCE_FILE
    frame = pd.read_excel(path)
    regional = frame.loc[frame["Region"].isin(SOURCE_REGIONS)].set_index(
        ["Region", "Variable"]
    )
    required = {variable for variables in SERIES.values() for variable in variables}
    for region in SOURCE_REGIONS:
        missing = required - set(regional.loc[region].index)
        if missing:
            raise SystemExit(
                f"{SOURCE_FILE}/{region}: missing variables: {sorted(missing)}"
            )

    records: list[dict[str, object]] = []
    for (stage, group), variables in SERIES.items():
        expected_unit = "billion pkm/yr" if stage == "Energy service" else "EJ/yr"
        units = {
            str(regional.loc[(region, variable), "Unit"])
            for region in SOURCE_REGIONS
            for variable in variables
        }
        if units != {expected_unit}:
            raise SystemExit(f"Unexpected units for {stage}/{group}: {units}")
        for year in YEARS:
            value = sum(
                float(regional.loc[(region, variable), year])
                for region in SOURCE_REGIONS
                for variable in variables
            )
            records.append(
                {
                    "model": "IMAGE",
                    "model_version": "3.4",
                    "scenario": "SSP2-VLHO",
                    "region": "Europe (WEU + CEU)",
                    "year": int(year),
                    "stage": stage,
                    "group": group,
                    "value": value,
                    "unit": expected_unit,
                    "source_regions": "; ".join(SOURCE_REGIONS),
                    "source_variables": "; ".join(variables),
                    "source_file_id": SOURCE_FILE,
                }
            )

    output = pd.DataFrame.from_records(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False, float_format="%.6f")
    print(f"Wrote {len(output)} rows to {args.output}")


if __name__ == "__main__":
    main()
