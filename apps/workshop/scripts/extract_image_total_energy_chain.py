#!/usr/bin/env python3
"""Extract an auditable World primary-carrier-final IMAGE energy chain."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "image_total_energy_chain.csv"
SOURCE_FILE = "IMAGE 3.4_SSP2_VLHO.xlsx"
SOURCE_REGION = "World"
YEARS = [str(year) for year in range(2020, 2101, 10)]

PRIMARY_SERIES = {
    "Fossil": [
        "Primary Energy|Coal",
        "Primary Energy|Gas",
        "Primary Energy|Oil",
    ],
    "Biomass": ["Primary Energy|Biomass"],
    "Nuclear + other": ["Primary Energy|Nuclear", "Primary Energy|Other"],
    "Non-biomass renewables": ["Primary Energy|Non-Biomass Renewables"],
}

ELECTRICITY_VARIABLES = [
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
]

HYDROGEN_VARIABLES = [
    "Secondary Energy|Hydrogen|Biomass",
    "Secondary Energy|Hydrogen|Coal",
    "Secondary Energy|Hydrogen|Electricity",
    "Secondary Energy|Hydrogen|Gas",
    "Secondary Energy|Hydrogen|Oil",
]

INDUSTRY_SUBSECTORS = [
    "Chemicals",
    "Fertilizer production",
    "Food Processing",
    "Iron and Steel",
    "Non-Metallic Minerals",
    "Other Sector",
    "Pulp and Paper",
]
INDUSTRY_CARRIERS = ["Electricity", "Gases", "Heat", "Hydrogen", "Liquids", "Solids"]
COMMERCIAL_SERVICES = [
    "Appliances",
    "Cooking",
    "Cooling",
    "Lighting",
    "Space Heating",
    "Water Heating",
]
RESIDENTIAL_SERVICES = ["Cooking", "Space Heating", "Water Heating"]
RESIDENTIAL_APPLIANCES = [
    "Final Energy|Residential|Cleaning Appliances|Electricity",
    "Final Energy|Residential|Cooling Appliance|Electricity",
    "Final Energy|Residential|Refrigeration|Electricity",
    "Final Energy|Residential|Small Appliances|Electricity",
]
FINAL_CARRIERS = [
    "Electricity",
    "Liquids",
    "Gases",
    "Solids + biomass",
    "Heat",
    "Hydrogen",
]
FINAL_SECTORS = ["Industry", "Transport", "Buildings", "Other + carbon management"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract IMAGE SSP2-VLHO World energy accounting data."
    )
    parser.add_argument(
        "input_dir", type=Path, help="Directory containing IMAGE xlsx files"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def carrier_group(variable: str) -> str:
    token = variable.rsplit("|", 1)[-1]
    if token == "Electricity":
        return "Electricity"
    if token in {"Liquids", "Liquid (fossil)", "Oil"}:
        return "Liquids"
    if token in {"Gases", "Gas", "Natural Gas"}:
        return "Gases"
    if token in {
        "Solids",
        "Coal",
        "Biomass",
        "Modern Biomass",
        "Traditional Biomass",
        "Modern",
        "Traditional",
        "Fossil",
    }:
        return "Solids + biomass"
    if token in {"Heat", "Secondary Heat", "Secondary heat"}:
        return "Heat"
    if token in {"Hydrogen", "H2"}:
        return "Hydrogen"
    raise ValueError(f"No final-energy carrier mapping for {variable}")


def direct_children(variables: set[str], prefix: str, depth: int) -> list[str]:
    return sorted(
        variable
        for variable in variables
        if variable.startswith(f"{prefix}|") and variable.count("|") == depth
    )


def final_flow_variables(variables: set[str]) -> dict[tuple[str, str], list[str]]:
    flows: dict[tuple[str, str], list[str]] = defaultdict(list)
    for subsector in INDUSTRY_SUBSECTORS:
        for carrier in INDUSTRY_CARRIERS:
            variable = f"Final Energy|Industry|{subsector}|{carrier}"
            flows[("Industry", carrier_group(variable))].append(variable)

    for service in COMMERCIAL_SERVICES:
        prefix = f"Final Energy|Commercial|{service}"
        for variable in direct_children(variables, prefix, 3):
            flows[("Buildings", carrier_group(variable))].append(variable)
    for variable in sorted(
        variable
        for variable in variables
        if variable.startswith("Final Energy|Commercial|Space Heating|Solids|")
        and not any(
            other.startswith(f"{variable}|") for other in variables if other != variable
        )
    ):
        flows[("Buildings", "Solids + biomass")].append(variable)

    for service in RESIDENTIAL_SERVICES:
        prefix = f"Final Energy|Residential|{service}"
        for variable in direct_children(variables, prefix, 3):
            flows[("Buildings", carrier_group(variable))].append(variable)
    for variable in RESIDENTIAL_APPLIANCES:
        flows[("Buildings", "Electricity")].append(variable)

    flows[("Other + carbon management", "Solids + biomass")].append(
        "Final Energy|Other Sector|Solids|Biomass"
    )
    flows[("Other + carbon management", "Gases")].append(
        "Final Energy|Carbon Management|Direct Air Capture|Gases"
    )
    return flows


def transport_flow_variables(variables: set[str], service: str) -> dict[str, list[str]]:
    prefix = f"Final Energy|Transportation|{service}"
    leaves = direct_children(variables, prefix, 4)
    if service == "Passenger":
        leaves = [
            variable
            for variable in leaves
            if "|International Aviation|" not in variable
        ]
    grouped: dict[str, list[str]] = defaultdict(list)
    for variable in leaves:
        grouped[carrier_group(variable)].append(variable)
    return grouped


def main() -> None:
    args = parse_args()
    path = args.input_dir / SOURCE_FILE
    frame = pd.read_excel(path)
    world = frame.loc[frame["Region"].eq(SOURCE_REGION)].set_index("Variable")
    variables = set(world.index)

    biomass_liquids = sorted(
        variable
        for variable in variables
        if variable.startswith("Secondary Energy|Consumption|Liquids|Biomass|")
        and variable.count("|") == 6
    )
    if len(biomass_liquids) != 18:
        raise SystemExit(
            f"Expected 18 biomass-liquid technology rows, found {len(biomass_liquids)}"
        )
    secondary_series = {
        "Electricity output": ELECTRICITY_VARIABLES,
        "Liquid-fuel consumption": [
            "Secondary Energy|Consumption|Liquids|Fossil",
            *biomass_liquids,
        ],
        "Hydrogen output": HYDROGEN_VARIABLES,
    }
    final_variables = final_flow_variables(variables)
    transport_variables = {
        service: transport_flow_variables(variables, service)
        for service in ["Passenger", "Freight"]
    }
    required = {
        variable
        for groups in [PRIMARY_SERIES, secondary_series]
        for group_variables in groups.values()
        for variable in group_variables
    }
    required.update(
        variable
        for group_variables in final_variables.values()
        for variable in group_variables
    )
    required.update(
        variable
        for service_groups in transport_variables.values()
        for group_variables in service_groups.values()
        for variable in group_variables
    )
    required.update(
        f"Final Energy|Transportation|{service}" for service in transport_variables
    )
    missing = required - variables
    if missing:
        raise SystemExit(f"{SOURCE_FILE}/{SOURCE_REGION}: missing {sorted(missing)}")
    units = {str(world.loc[variable, "Unit"]) for variable in required}
    if units != {"EJ/yr"}:
        raise SystemExit(f"Unexpected units: {units}")

    records: list[dict[str, object]] = []

    def append_record(
        *,
        year: str,
        stage: str,
        group: str,
        value: float,
        source_variables: list[str],
        destination: str = "",
        allocation_method: str = "Direct sum of reported IMAGE variables",
    ) -> None:
        records.append(
            {
                "model": "IMAGE",
                "model_version": "3.4",
                "scenario": "SSP2-VLHO",
                "region": SOURCE_REGION,
                "year": int(year),
                "stage": stage,
                "group": group,
                "destination": destination,
                "value": value,
                "unit": "EJ/yr",
                "source_regions": SOURCE_REGION,
                "source_variables": "; ".join(source_variables),
                "allocation_method": allocation_method,
                "source_file_id": SOURCE_FILE,
            }
        )

    for year in YEARS:
        for group, group_variables in PRIMARY_SERIES.items():
            append_record(
                year=year,
                stage="Primary energy supply",
                group=group,
                value=sum(
                    float(world.loc[variable, year]) for variable in group_variables
                ),
                source_variables=group_variables,
            )
        for group, group_variables in secondary_series.items():
            append_record(
                year=year,
                stage="Secondary carrier indicator",
                group=group,
                value=sum(
                    float(world.loc[variable, year]) for variable in group_variables
                ),
                source_variables=group_variables,
            )
        for (destination, group), group_variables in final_variables.items():
            append_record(
                year=year,
                stage="Final energy flow",
                group=group,
                destination=destination,
                value=sum(
                    float(world.loc[variable, year]) for variable in group_variables
                ),
                source_variables=group_variables,
            )
        for service, carrier_variables in transport_variables.items():
            target_variable = f"Final Energy|Transportation|{service}"
            target = float(world.loc[target_variable, year])
            raw_total = sum(
                float(world.loc[variable, year])
                for group_variables in carrier_variables.values()
                for variable in group_variables
            )
            factor = target / raw_total if raw_total else 0.0
            for group in FINAL_CARRIERS:
                group_variables = carrier_variables.get(group, [])
                raw_value = sum(
                    float(world.loc[variable, year]) for variable in group_variables
                )
                append_record(
                    year=year,
                    stage="Final energy flow",
                    group=group,
                    destination="Transport",
                    value=raw_value * factor,
                    source_variables=[target_variable, *group_variables],
                    allocation_method=(
                        f"{service} modal carrier shares scaled by {factor:.8f} "
                        "to the reported service total; international passenger aviation excluded"
                    ),
                )

    output = pd.DataFrame.from_records(records)
    output = (
        output.groupby(
            [
                "model",
                "model_version",
                "scenario",
                "region",
                "year",
                "stage",
                "group",
                "destination",
                "unit",
                "source_regions",
                "source_file_id",
            ],
            as_index=False,
            dropna=False,
        )
        .agg(
            value=("value", "sum"),
            source_variables=("source_variables", "; ".join),
            allocation_method=("allocation_method", "; ".join),
        )
        .sort_values(["year", "stage", "group", "destination"])
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False, float_format="%.6f")
    print(f"Wrote {len(output)} rows to {args.output}")


if __name__ == "__main__":
    main()
