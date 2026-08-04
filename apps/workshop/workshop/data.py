from __future__ import annotations

import json
from functools import lru_cache

import pandas as pd

from .config import (
    IMAGE_REGION_MAPPING_FILE,
    IAM_REGION_TOPOLOGIES_FILE,
    REMIND_EU_REGION_MAPPING_FILE,
    IMAGE_END_USE_TRANSFORMATIONS_FILE,
    IMAGE_ELECTRICITY_CHAIN_FILE,
    IMAGE_ENERGY_LAYERS_FILE,
    IMAGE_TOTAL_ENERGY_CHAIN_FILE,
    LCIA_FILE,
    LCIA_CONTRIBUTIONS_FILE,
    MECHANICS_FILE,
    PATHWAY_FILE,
    PREMISE_MAPPING_COUNTS_FILE,
)


@lru_cache(maxsize=1)
def pathways() -> pd.DataFrame:
    frame = pd.read_csv(PATHWAY_FILE)
    frame["year"] = frame["year"].astype(int)
    frame["display_value"] = frame["display_value"].astype(float)
    return frame


@lru_cache(maxsize=1)
def lcia_results() -> pd.DataFrame:
    frame = pd.read_csv(LCIA_FILE)
    return frame


@lru_cache(maxsize=1)
def lcia_contributions() -> pd.DataFrame:
    return pd.read_csv(LCIA_CONTRIBUTIONS_FILE)


@lru_cache(maxsize=1)
def image_region_mapping() -> dict:
    with IMAGE_REGION_MAPPING_FILE.open(encoding="utf-8") as stream:
        return json.load(stream)


@lru_cache(maxsize=1)
def remind_eu_region_mapping() -> dict:
    with REMIND_EU_REGION_MAPPING_FILE.open(encoding="utf-8") as stream:
        return json.load(stream)


@lru_cache(maxsize=1)
def iam_region_topologies() -> dict:
    with IAM_REGION_TOPOLOGIES_FILE.open(encoding="utf-8") as stream:
        return json.load(stream)


@lru_cache(maxsize=1)
def mechanics_series() -> pd.DataFrame:
    frame = pd.read_csv(MECHANICS_FILE)
    frame["year"] = frame["year"].astype(int)
    frame["value"] = frame["value"].astype(float)
    return frame


@lru_cache(maxsize=1)
def image_energy_layers() -> pd.DataFrame:
    frame = pd.read_csv(IMAGE_ENERGY_LAYERS_FILE)
    frame["year"] = frame["year"].astype(int)
    frame["value"] = frame["value"].astype(float)
    return frame


@lru_cache(maxsize=1)
def image_electricity_chain() -> pd.DataFrame:
    frame = pd.read_csv(IMAGE_ELECTRICITY_CHAIN_FILE)
    frame["year"] = frame["year"].astype(int)
    frame["value"] = frame["value"].astype(float)
    return frame


@lru_cache(maxsize=1)
def image_total_energy_chain() -> pd.DataFrame:
    frame = pd.read_csv(IMAGE_TOTAL_ENERGY_CHAIN_FILE)
    frame["year"] = frame["year"].astype(int)
    frame["value"] = frame["value"].astype(float)
    return frame


@lru_cache(maxsize=1)
def image_end_use_transformations() -> pd.DataFrame:
    frame = pd.read_csv(IMAGE_END_USE_TRANSFORMATIONS_FILE)
    frame["year"] = frame["year"].astype(int)
    frame["value"] = frame["value"].astype(float)
    return frame


@lru_cache(maxsize=1)
def premise_mapping_counts() -> pd.DataFrame:
    frame = pd.read_csv(PREMISE_MAPPING_COUNTS_FILE)
    frame["mapped_variable_count"] = frame["mapped_variable_count"].astype(int)
    return frame


def context_series(
    sector: str,
    scenarios: list[str],
    model: str = "image",
    region: str = "World",
) -> pd.DataFrame:
    frame = pathways()
    subset = frame[
        (frame["model"] == model)
        & (frame["scenario"].isin(scenarios))
        & (frame["sector"] == sector)
        & (frame["region"] == region)
    ].copy()
    if subset.empty:
        return subset
    return (
        subset.groupby(
            ["model", "model_version", "scenario", "year", "display_unit"],
            as_index=False,
            observed=True,
        )["display_value"]
        .sum()
        .sort_values(["scenario", "year"])
    )


def available_scenarios(model: str) -> list[str]:
    frame = pathways()
    return sorted(frame.loc[frame["model"] == model, "scenario"].unique())


def available_regions(model: str, scenarios: list[str] | None = None) -> list[str]:
    frame = pathways()
    subset = frame[frame["model"] == model]
    if scenarios:
        subset = subset[subset["scenario"].isin(scenarios)]
    regions = sorted(subset["region"].dropna().unique())
    return (["World"] if "World" in regions else []) + [
        r for r in regions if r != "World"
    ]


def technology_group(variable: str) -> str:
    name = variable.lower()
    rules = [
        ("solar", "Solar"),
        ("wind", "Wind"),
        ("hydro", "Hydro"),
        ("nuclear", "Nuclear"),
        ("geothermal", "Geothermal"),
        ("biomass", "Biomass"),
        ("biogas", "Biomass"),
        ("coal", "Coal"),
        ("gas", "Gas"),
        ("oil", "Oil"),
        ("storage", "Storage"),
        ("wave", "Other renewables"),
    ]
    for token, group in rules:
        if token in name:
            return group
    return "Other"


def sector_mix(
    sector: str,
    scenarios: list[str],
    year: int,
    model: str = "image",
    region: str = "World",
) -> pd.DataFrame:
    frame = pathways()
    subset = frame[
        (frame["model"] == model)
        & (frame["scenario"].isin(scenarios))
        & (frame["sector"] == sector)
        & (frame["year"] == year)
        & (frame["region"] == region)
    ].copy()
    if sector == "Electricity":
        subset["technology"] = subset["variable"].map(technology_group)
    elif sector == "Transport Passenger Cars":
        subset["technology"] = subset["variable"].map(transport_group)
    elif sector == "Transport Road Freight":
        subset["technology"] = subset["variable"].map(transport_group)
    elif sector == "Steel":
        subset["technology"] = subset["variable"].map(steel_group)
    elif sector == "Cement":
        subset["technology"] = subset["variable"].map(cement_group)
    elif sector == "Carbon Dioxide Removal":
        subset["technology"] = subset["variable"].map(cdr_group)
    else:
        subset["technology"] = subset["variable"]
    grouped = subset.groupby(["scenario", "technology"], as_index=False, observed=True)[
        "display_value"
    ].sum()
    totals = grouped.groupby("scenario")["display_value"].transform("sum")
    grouped["share"] = grouped["display_value"] / totals.where(totals != 0)
    return grouped


def electricity_mix(scenarios: list[str], year: int) -> pd.DataFrame:
    return sector_mix("Electricity", scenarios, year)


def transport_group(variable: str) -> str:
    name = variable.lower()
    if "battery electric" in name:
        return "Battery electric"
    if "fuel cell" in name:
        return "Fuel cell"
    if "plugin" in name:
        return "Plug-in hybrid"
    if "hybrid" in name:
        return "Hybrid"
    if "gasoline" in name:
        return "Gasoline"
    if "diesel" in name:
        return "Diesel"
    if "gas" in name:
        return "Gaseous fuel"
    return "Other"


def steel_group(variable: str) -> str:
    name = variable.lower()
    if "secondary" in name:
        return "Secondary"
    if "h-dri" in name or "hydrogen" in name:
        return "Hydrogen-based primary"
    if "ccs" in name:
        return "Primary with CCS"
    return "Other primary"


def cement_group(variable: str) -> str:
    name = variable.lower()
    if "mea ccs" in name:
        return "MEA CCS"
    if "on-site ccs" in name:
        return "On-site CCS"
    if "oxyfuel ccs" in name:
        return "Oxyfuel CCS"
    if "efficient" in name:
        return "Efficient kiln"
    return "Conventional kiln"


def cdr_group(variable: str) -> str:
    name = variable.lower()
    if "direct air" in name or "dac" in name:
        return "Direct air capture"
    if "biofuel" in name:
        return "Biofuels with CCS"
    if "biomass" in name or "beccs" in name:
        return "BECCS"
    if "synthetic" in name:
        return "Synthetic fuels with CCS"
    return "Other removal"


def steel_mix(scenarios: list[str], year: int) -> pd.DataFrame:
    grouped = sector_mix("Steel", scenarios, year)
    grouped = grouped.rename(columns={"technology": "route"})
    return grouped
