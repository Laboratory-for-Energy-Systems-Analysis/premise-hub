#!/usr/bin/env python3
"""Extract auditable IMAGE end-use transformation series for the workshop."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATHWAYS = ROOT / "data" / "processed" / "workshop_pathways.csv.gz"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "image_end_use_transformations.csv"
SOURCE_FILE = "IMAGE 3.4_SSP2_VLHO.xlsx"
SOURCE_REGION = "World"
SCENARIO = "SSP2-VLHO"
YEARS = [2020, 2025, 2030, 2035, 2040, 2045, 2050, 2060, 2070, 2080, 2090, 2100]

TRANSPORT_GROUPS = {
    "battery electric": "Battery electric",
    "fuel cell electric": "Fuel cell",
    "compressed gas": "Combustion",
    "gasoline": "Combustion",
}
CEMENT_GROUPS = {
    "cement, dry feed rotary kiln": "Conventional kiln",
    "cement, dry feed rotary kiln, efficient": "Efficient kiln",
    "cement, dry feed rotary kiln, efficient, with MEA CCS": "MEA CCS",
    "cement, dry feed rotary kiln, efficient, with on-site CCS": "On-site CCS",
    "cement, dry feed rotary kiln, efficient, with oxyfuel CCS": "Oxyfuel CCS",
}
STEEL_GROUPS = {
    "primary - BF/BOF": "Conventional BF/BOF",
    "primary - DRI": "Advanced fossil primary",
    "primary - TGR BF/BOF": "Advanced fossil primary",
    "primary - BF/BOF CCS": "Primary with CCS",
    "primary - DRI CCS": "Primary with CCS",
    "primary - TGR BF/BOF CCS": "Primary with CCS",
    "primary - H-DRI": "Hydrogen + electrowinning",
    "primary - Electrowinning": "Hydrogen + electrowinning",
    "secondary": "Secondary steel",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract IMAGE SSP2-VLHO World end-use transformation series."
    )
    parser.add_argument(
        "input_dir", type=Path, help="Directory containing the IMAGE 3.4 workbook"
    )
    parser.add_argument("--pathways", type=Path, default=DEFAULT_PATHWAYS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = args.input_dir / SOURCE_FILE
    workbook = pd.read_excel(source_path)
    world = workbook.loc[workbook["Region"].eq(SOURCE_REGION)].set_index("Variable")
    pathways = pd.read_csv(args.pathways)
    pathways = pathways.loc[
        pathways["model"].eq("image")
        & pathways["scenario"].eq(SCENARIO)
        & pathways["region"].eq(SOURCE_REGION)
    ].copy()

    records: list[dict[str, object]] = []

    def add_record(
        *,
        domain: str,
        metric: str,
        group: str,
        year: int,
        value: float,
        unit: str,
        source_dataset: str,
        source_variables: str,
        derivation: str,
    ) -> None:
        records.append(
            {
                "model": "IMAGE",
                "model_version": "3.4",
                "scenario": SCENARIO,
                "region": SOURCE_REGION,
                "domain": domain,
                "metric": metric,
                "group": group,
                "year": year,
                "value": value,
                "unit": unit,
                "source_dataset": source_dataset,
                "source_variables": source_variables,
                "derivation": derivation,
            }
        )

    def add_pathway_mix(
        domain: str, sector: str, group_mapping: dict[str, str], unit: str
    ) -> None:
        subset = pathways.loc[
            pathways["sector"].eq(sector) & pathways["year"].isin(YEARS)
        ].copy()
        unknown = set(subset["variable"]) - set(group_mapping)
        if unknown:
            raise SystemExit(f"Unmapped {sector} variables: {sorted(unknown)}")
        reported_units = set(subset["display_unit"])
        if reported_units != {unit}:
            raise SystemExit(
                f"Unexpected {sector} display units: {sorted(reported_units)}"
            )
        subset["group"] = subset["variable"].map(group_mapping)
        grouped = subset.groupby(["year", "group"], as_index=False, observed=True)[
            "display_value"
        ].sum()
        variables = {
            group: "; ".join(sorted(rows["variable"].unique()))
            for group, rows in subset.groupby("group", observed=True)
        }
        for row in grouped.itertuples(index=False):
            add_record(
                domain=domain,
                metric="technology mix",
                group=row.group,
                year=int(row.year),
                value=float(row.display_value),
                unit=unit,
                source_dataset=str(subset["source_file_id"].iloc[0]),
                source_variables=variables[row.group],
                derivation="Sum mapped pathway rows; chart normalizes the annual total to 100%.",
            )

    add_pathway_mix(
        "Passenger cars",
        "Transport Passenger Cars",
        TRANSPORT_GROUPS,
        "model activity unit",
    )
    add_pathway_mix("Cement", "Cement", CEMENT_GROUPS, "Mt/yr")
    add_pathway_mix("Steel", "Steel", STEEL_GROUPS, "Mt/yr")

    heat_variables = {
        "Electric heating": [
            "Final Energy|Residential|Space Heating|Electricity",
            "Final Energy|Commercial|Space Heating|Electricity",
        ],
        "District heat": [
            "Final Energy|Residential|Space Heating|Heat",
            "Final Energy|Commercial|Space Heating|Heat",
        ],
        "Fossil boilers": [
            "Final Energy|Residential|Space Heating|Coal",
            "Final Energy|Residential|Space Heating|Liquid (fossil)",
            "Final Energy|Residential|Space Heating|Natural Gas",
            "Final Energy|Commercial|Space Heating|Gases",
            "Final Energy|Commercial|Space Heating|Liquids",
        ],
        "Bioenergy": [
            "Final Energy|Residential|Space Heating|Modern Biomass",
            "Final Energy|Residential|Space Heating|Traditional Biomass",
        ],
        "Hydrogen": [
            "Final Energy|Residential|Space Heating|Hydrogen",
            "Final Energy|Commercial|Space Heating|Hydrogen",
        ],
    }
    required_workbook_variables = {
        variable for variables in heat_variables.values() for variable in variables
    }
    required_workbook_variables.update(
        {
            "Final Energy|Transportation|Passenger|Light Duty Vehicle",
            "Energy Service|Transportation|Passenger|Road|Light-Duty Vehicle",
            "Final Energy|Industry|Non-Metallic Minerals",
            "Final Energy|Industry|Iron and Steel",
            "Production|Industry|Iron and Steel|Crude Steel",
            "Final Energy|Residential|Space Heating",
            "Final Energy|Commercial|Space Heating",
            "Population",
        }
    )
    missing = required_workbook_variables - set(world.index)
    if missing:
        raise SystemExit(f"{SOURCE_FILE}/{SOURCE_REGION}: missing {sorted(missing)}")
    expected_units = {
        "Final Energy|Transportation|Passenger|Light Duty Vehicle": "EJ/yr",
        "Energy Service|Transportation|Passenger|Road|Light-Duty Vehicle": "billion pkm/yr",
        "Final Energy|Industry|Non-Metallic Minerals": "EJ/yr",
        "Final Energy|Industry|Iron and Steel": "EJ/yr",
        "Production|Industry|Iron and Steel|Crude Steel": "Mtonne/yr",
        "Final Energy|Residential|Space Heating": "EJ/yr",
        "Final Energy|Commercial|Space Heating": "EJ/yr",
        "Population": "million",
    }
    expected_units.update(
        {
            variable: "EJ/yr"
            for variable in required_workbook_variables
            if variable not in expected_units
        }
    )
    unexpected_units = {
        variable: str(world.loc[variable, "Unit"])
        for variable, expected in expected_units.items()
        if str(world.loc[variable, "Unit"]) != expected
    }
    if unexpected_units:
        raise SystemExit(f"Unexpected workbook units: {unexpected_units}")

    for year in YEARS:
        year_column = str(year)
        for group, variables in heat_variables.items():
            add_record(
                domain="Space heating",
                metric="technology mix",
                group=group,
                year=year,
                value=sum(
                    float(world.loc[variable, year_column]) for variable in variables
                ),
                unit="EJ/yr",
                source_dataset=SOURCE_FILE,
                source_variables="; ".join(variables),
                derivation=(
                    "Sum residential and commercial delivered-energy carriers; electricity is "
                    "a technology proxy that includes heat pumps and resistance heating."
                ),
            )

        ldv_energy = float(
            world.loc[
                "Final Energy|Transportation|Passenger|Light Duty Vehicle", year_column
            ]
        )
        ldv_service = float(
            world.loc[
                "Energy Service|Transportation|Passenger|Road|Light-Duty Vehicle",
                year_column,
            ]
        )
        cement_output = float(
            pathways.loc[
                pathways["sector"].eq("Cement") & pathways["year"].eq(year),
                "display_value",
            ].sum()
        )
        nonmetal_energy = float(
            world.loc["Final Energy|Industry|Non-Metallic Minerals", year_column]
        )
        steel_energy = float(
            world.loc["Final Energy|Industry|Iron and Steel", year_column]
        )
        steel_output = float(
            world.loc["Production|Industry|Iron and Steel|Crude Steel", year_column]
        )
        heating_energy = sum(
            float(world.loc[variable, year_column])
            for variable in [
                "Final Energy|Residential|Space Heating",
                "Final Energy|Commercial|Space Heating",
            ]
        )
        population = float(world.loc["Population", year_column])

        intensity_rows = [
            (
                "Passenger cars",
                ldv_energy / ldv_service * 1_000,
                "MJ/pkm",
                "Final Energy|Transportation|Passenger|Light Duty Vehicle / "
                "Energy Service|Transportation|Passenger|Road|Light-Duty Vehicle",
                "EJ/yr divided by billion pkm/yr, converted to MJ/pkm.",
            ),
            (
                "Cement",
                nonmetal_energy / cement_output * 1_000,
                "GJ/t cement (sector proxy)",
                "Final Energy|Industry|Non-Metallic Minerals / summed Cement pathway output",
                "EJ/yr divided by Mt cement/yr, converted to GJ/t; numerator covers the wider non-metallic-minerals sector.",
            ),
            (
                "Steel",
                steel_energy / steel_output * 1_000,
                "GJ/t crude steel",
                "Final Energy|Industry|Iron and Steel / Production|Industry|Iron and Steel|Crude Steel",
                "EJ/yr divided by Mt crude steel/yr, converted to GJ/t.",
            ),
            (
                "Space heating",
                heating_energy / population * 1_000,
                "GJ/person",
                "(Final Energy|Residential|Space Heating + Final Energy|Commercial|Space Heating) / Population",
                "EJ/yr divided by million people, converted to GJ/person; floor area and useful heat are not reported.",
            ),
        ]
        for domain, value, unit, variables, derivation in intensity_rows:
            add_record(
                domain=domain,
                metric="specific energy",
                group="Specific energy use",
                year=year,
                value=value,
                unit=unit,
                source_dataset=SOURCE_FILE,
                source_variables=variables,
                derivation=derivation,
            )

        context_rows = [
            (
                "Passenger cars",
                ldv_service,
                "billion pkm/yr",
                "Passenger-kilometres",
                "Energy Service|Transportation|Passenger|Road|Light-Duty Vehicle",
            ),
            (
                "Cement",
                cement_output,
                "Mt/yr",
                "Cement output",
                "Summed Cement pathway output",
            ),
            (
                "Steel",
                steel_output,
                "Mt/yr",
                "Crude-steel output",
                "Production|Industry|Iron and Steel|Crude Steel",
            ),
            (
                "Space heating",
                heating_energy,
                "EJ/yr",
                "Delivered space-heating energy",
                "Final Energy|Residential|Space Heating + Final Energy|Commercial|Space Heating",
            ),
        ]
        for domain, value, unit, group, variables in context_rows:
            add_record(
                domain=domain,
                metric="context total",
                group=group,
                year=year,
                value=value,
                unit=unit,
                source_dataset=SOURCE_FILE,
                source_variables=variables,
                derivation="Direct IMAGE value or explicitly stated sum.",
            )

    output = pd.DataFrame.from_records(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False, float_format="%.8f")
    print(f"Wrote {len(output)} rows to {args.output}")


if __name__ == "__main__":
    main()
