#!/usr/bin/env python3
"""Extract auditable IMAGE energy-layer series for the workshop slides."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "image_energy_layers.csv"
YEARS = [str(year) for year in range(2020, 2101, 10)]
FILES = {
    "SSP1-L": "IMAGE 3.4_SSP1_L.xlsx",
    "SSP2-VLHO": "IMAGE 3.4_SSP2_VLHO.xlsx",
    "SSP2-M": "IMAGE 3.4_SSP2_M_CP.xlsx",
    "SSP3-H": "IMAGE 3.4_SSP3_H.xlsx",
}
REGION_GROUPS = {
    "World": ["World"],
    "Europe (WEU + CEU)": ["WEU", "CEU"],
}

# Each group contains non-overlapping IMAGE totals or explicitly enumerated leaves.
SERIES = {
    "Primary energy": {
        "Coal": ["Primary Energy|Coal"],
        "Oil": ["Primary Energy|Oil"],
        "Gas": ["Primary Energy|Gas"],
        "Biomass": ["Primary Energy|Biomass"],
        "Nuclear": ["Primary Energy|Nuclear"],
        "Non-biomass renewables": ["Primary Energy|Non-Biomass Renewables"],
    },
    "Secondary electricity": {
        "Coal": ["Secondary Energy|Electricity|Coal"],
        "Gas": ["Secondary Energy|Electricity|Gas"],
        "Oil": ["Secondary Energy|Electricity|Oil"],
        "Biomass": ["Secondary Energy|Electricity|Biomass"],
        "Nuclear": ["Secondary Energy|Electricity|Nuclear"],
        "Hydro": ["Secondary Energy|Electricity|Hydro"],
        "Solar": [
            "Secondary Energy|Electricity|Solar|CSP",
            "Secondary Energy|Electricity|Solar|PV|1",
            "Secondary Energy|Electricity|Solar|PV|2",
        ],
        "Wind": [
            "Secondary Energy|Electricity|Wind|1",
            "Secondary Energy|Electricity|Wind|2",
        ],
        "Other": [
            "Secondary Energy|Electricity|Geothermal",
            "Secondary Energy|Electricity|Hydrogen",
            "Secondary Energy|Electricity|Other",
            "Secondary Energy|Electricity|Storage",
            "Secondary Energy|Electricity|Wave",
        ],
    },
    "Final energy": {
        "Passenger transport": ["Final Energy|Transportation|Passenger"],
        "Freight transport": ["Final Energy|Transportation|Freight"],
        "Iron & steel": ["Final Energy|Industry|Iron and Steel"],
        "Space heating": [
            "Final Energy|Residential|Space Heating",
            "Final Energy|Commercial|Space Heating",
        ],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract World and European energy layers from four IMAGE workbooks."
    )
    parser.add_argument(
        "input_dir", type=Path, help="Directory containing IMAGE xlsx files"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records: list[dict[str, object]] = []

    for scenario, filename in FILES.items():
        path = args.input_dir / filename
        frame = pd.read_excel(path)

        required = {
            variable
            for groups in SERIES.values()
            for variables in groups.values()
            for variable in variables
        }
        for region, source_regions in REGION_GROUPS.items():
            regional = frame.loc[frame["Region"].isin(source_regions)].set_index(
                ["Region", "Variable"]
            )
            for source_region in source_regions:
                available = set(regional.loc[source_region].index)
                missing = required - available
                if missing:
                    raise SystemExit(
                        f"{filename}/{source_region}: missing required variables: "
                        f"{sorted(missing)}"
                    )

            for layer, groups in SERIES.items():
                for group, variables in groups.items():
                    for year in YEARS:
                        value = sum(
                            float(regional.loc[(source_region, variable), year])
                            for source_region in source_regions
                            for variable in variables
                        )
                        units = {
                            str(regional.loc[(source_region, variable), "Unit"])
                            for source_region in source_regions
                            for variable in variables
                        }
                        if units != {"EJ/yr"}:
                            raise SystemExit(
                                f"{filename}: unexpected units for "
                                f"{region}/{layer}/{group}: {units}"
                            )
                        records.append(
                            {
                                "model": "IMAGE",
                                "model_version": "3.4",
                                "scenario": scenario,
                                "region": region,
                                "layer": layer,
                                "group": group,
                                "year": int(year),
                                "value": value,
                                "unit": "EJ/yr",
                                "source_regions": "; ".join(source_regions),
                                "source_variables": "; ".join(variables),
                                "source_file_id": filename,
                            }
                        )

    output = pd.DataFrame.from_records(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False, float_format="%.6f")
    print(f"Wrote {len(output)} rows to {args.output}")


if __name__ == "__main__":
    main()
