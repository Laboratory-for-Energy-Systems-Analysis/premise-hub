#!/usr/bin/env python3
"""Build a versioned Scenario Explorer dataset from premise IAM data.

The script intentionally uses :class:`premise.data_collection.IAMDataCollection`
instead of constructing a ``NewDatabase``. The explorer only needs the IAM
variables selected by premise's mappings; extracting an ecoinvent database is
therefore unnecessary.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

from premise import __version__
from premise.data_collection import IAMDataCollection

DEV_DIR = Path(__file__).resolve().parent
DATA_DIR = DEV_DIR.parent / "data"

SCENARIOS = [
    {"model": "remind", "pathway": "SSP1-NPi", "year": 2025},
    {"model": "remind", "pathway": "SSP1-PkBudg650", "year": 2025},
    {"model": "remind", "pathway": "SSP1-PkBudg1000", "year": 2025},
    {"model": "remind", "pathway": "SSP2-NDC", "year": 2025},
    {"model": "remind", "pathway": "SSP2-NPi", "year": 2025},
    {"model": "remind", "pathway": "SSP2-PkBudg650", "year": 2025},
    {"model": "remind", "pathway": "SSP3-rollBack", "year": 2025},
    {"model": "remind", "pathway": "SSP2-PkBudg1000", "year": 2025},
    {"model": "remind-eu", "pathway": "SSP2-NDC", "year": 2025},
    {"model": "remind-eu", "pathway": "SSP2-NPi", "year": 2025},
    {"model": "remind-eu", "pathway": "SSP2-PkBudg650", "year": 2025},
    {"model": "remind-eu", "pathway": "SSP2-PkBudg1000", "year": 2025},
    {"model": "image", "pathway": "SSP1-L", "year": 2025},
    {"model": "image", "pathway": "SSP1-M", "year": 2025},
    {"model": "image", "pathway": "SSP1-VLLO", "year": 2025},
    {"model": "image", "pathway": "SSP2-L", "year": 2025},
    {"model": "image", "pathway": "SSP2-M", "year": 2025},
    {"model": "image", "pathway": "SSP2-VLHO", "year": 2025},
    {"model": "image", "pathway": "SSP3-H", "year": 2025},
    {"model": "image", "pathway": "SSP5-H", "year": 2025},
    {"model": "tiam-ucl", "pathway": "SSP2-Base", "year": 2025},
    {"model": "tiam-ucl", "pathway": "SSP2-RCP19", "year": 2025},
    {"model": "tiam-ucl", "pathway": "SSP2-RCP26", "year": 2025},
    {"model": "tiam-ucl", "pathway": "SSP2-RCP45", "year": 2025},
    {"model": "message", "pathway": "SSP1-L", "year": 2050},
    {"model": "message", "pathway": "SSP1-VL", "year": 2050},
    {"model": "message", "pathway": "SSP2-L", "year": 2050},
    {"model": "message", "pathway": "SSP2-LO", "year": 2050},
    {"model": "message", "pathway": "SSP2-M", "year": 2050},
    {"model": "message", "pathway": "SSP2-ML", "year": 2050},
    {"model": "message", "pathway": "SSP2-VL", "year": 2050},
    {"model": "message", "pathway": "SSP3-H", "year": 2050},
    {"model": "message", "pathway": "SSP4-LO", "year": 2050},
    {"model": "message", "pathway": "SSP5-H", "year": 2050},
    {"model": "message", "pathway": "SSP5-LO", "year": 2050},
]

OTHER_VARIABLES = {"CO2", "gdp", "population", "GMST"}


def version_string() -> str:
    if isinstance(__version__, tuple):
        return ".".join(map(str, __version__))
    return str(__version__)


def parse_args() -> argparse.Namespace:
    version = version_string()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iam-dir",
        type=Path,
        required=True,
        help="Directory containing encrypted premise IAM scenario files",
    )
    parser.add_argument(
        "--mapping-overview",
        type=Path,
        default=DEV_DIR / "mapping_overview.xlsx",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DATA_DIR / f"structured_data ({version.replace('.', ', ')}).csv",
    )
    parser.add_argument(
        "--expected-version",
        default=version,
        help="Fail if the imported premise version differs from this value",
    )
    return parser.parse_args()


def load_production_mapping(path: Path) -> pd.DataFrame:
    sheets = pd.read_excel(path, sheet_name=None)
    mapping = pd.concat(
        [frame.assign(Sheet=sheet) for sheet, frame in sheets.items()],
        ignore_index=True,
    )
    return mapping.loc[
        mapping["Variable Type"].eq("Production volume"),
        ["Sheet", "Key", "IAM Model"],
    ].drop_duplicates()


def scenario_frame(
    scenario: dict[str, object], mapping: pd.DataFrame, iam_dir: Path, key: bytes
) -> pd.DataFrame:
    model = str(scenario["model"])
    pathway = str(scenario["pathway"])
    print(f"[{model} / {pathway}] loading IAM data", flush=True)
    iam_data = IAMDataCollection(
        model=model,
        pathway=pathway,
        year=int(scenario["year"]),
        filepath_iam_files=iam_dir,
        key=key,
    )

    production_variables = set(
        iam_data.production_volumes.coords["variables"].values.tolist()
    )
    mapped_variables = mapping.loc[mapping["IAM Model"].eq(model)]
    frames: list[pd.DataFrame] = []

    for (sector, variable), _ in mapped_variables.groupby(["Sheet", "Key"], sort=True):
        if variable in OTHER_VARIABLES:
            array = iam_data.other_vars.sel(variables=variable)
        elif variable in production_variables:
            array = iam_data.production_volumes.sel(variables=variable)
        else:
            continue

        frame = array.to_dataframe("val").reset_index()
        frame["sector"] = sector
        frame["model"] = model
        frame["scenario"] = pathway
        frames.append(frame.loc[frame["year"].le(2100)])

    if not frames:
        raise RuntimeError(f"No mapped variables found for {model} / {pathway}")
    return pd.concat(frames, ignore_index=True)


def normalize_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    cdr = frame["sector"].eq("Carbon Dioxide Removal") & frame["val"].lt(0)
    frame.loc[cdr, "val"] *= -1

    sector_overrides = {
        "population": "Population",
        "CO2": "Carbon Dioxide emissions",
        "gdp": "Gross Domestic Product",
        "GMST": "GMST increase",
    }
    for variable, sector in sector_overrides.items():
        frame.loc[frame["variables"].eq(variable), "sector"] = sector

    variables = frame["variables"].astype("string")
    non_road_diesel = variables.str.contains(
        "diesel", na=False
    ) & ~variables.str.contains("truck|train|bus|car|ship", regex=True, na=False)
    frame.loc[non_road_diesel, "sector"] = "Diesel"
    frame.loc[variables.str.contains("ethanol", na=False), "sector"] = "Gasoline"
    non_road_gasoline = variables.str.contains(
        "gasoline", na=False
    ) & ~variables.str.contains("truck|train|bus|car|two-wheeler", regex=True, na=False)
    frame.loc[non_road_gasoline, "sector"] = "Gasoline"
    frame.loc[variables.str.contains("liquefied", na=False), "sector"] = "LPG"
    frame.loc[variables.str.contains("kerosene", na=False), "sector"] = "Kerosene"
    frame.loc[variables.str.contains("hydrogen", na=False), "sector"] = "Hydrogen"
    frame.loc[variables.eq("natural gas") | variables.eq("biomethane"), "sector"] = (
        "Gas"
    )
    frame.loc[variables.eq("heavy fuel oil"), "sector"] = "Oil"

    replacements = (
        (r"truck, |train, |bus, |passenger car, |two-wheeler, ", ""),
        (r", (mini|medium SUV|large SUV|medium|van|large|small)$", ""),
        (r", (3\.5t|7\.5t|18t|26t|40t)$", ""),
        (r", energy allocation$", ""),
        (r"^kerosene, |^hydrogen, ", ""),
        (r"liquefied petroleum gas, ", "LPG"),
        (r"^steel - ", ""),
    )
    for pattern, replacement in replacements:
        frame["variables"] = frame["variables"].replace(
            pattern, replacement, regex=True
        )

    frame = frame.groupby(
        ["region", "year", "variables", "sector", "model", "scenario"],
        observed=True,
        as_index=False,
    )["val"].sum()

    image_remind_co2 = frame["model"].isin(
        ["image", "remind", "remind-eu", "gcam"]
    ) & frame["variables"].eq("CO2")
    frame.loc[image_remind_co2, "val"] *= 1_000_000
    tiam_co2 = frame["model"].eq("tiam-ucl") & frame["variables"].eq("CO2")
    frame.loc[tiam_co2, "val"] *= 1_000
    tiam_gdp = frame["model"].eq("tiam-ucl") & frame["variables"].eq("gdp")
    frame.loc[tiam_gdp, "val"] *= 10_000

    biomass_variables = {
        "biomass crops - purpose grown",
        "biomass wood - purpose grown",
        "biomass - residual",
    }
    tiam_biomass = frame["model"].eq("tiam-ucl") & frame["variables"].isin(
        biomass_variables
    )
    frame.loc[tiam_biomass, "val"] /= 1_000
    remind_biomass = frame["model"].eq("remind") & frame["variables"].isin(
        biomass_variables
    )
    frame.loc[remind_biomass, "val"] *= 10
    tiam_cdr = frame["model"].eq("tiam-ucl") & frame["sector"].eq(
        "Carbon Dioxide Removal"
    )
    frame.loc[tiam_cdr, "val"] /= 1_000

    heat_layers = {
        "heat, buildings,": "Heat - Buildings",
        "heat, industrial,": "Heat - Industry",
        "heat, secondary,": "Heat - District heating",
    }
    is_heat_sector = frame["sector"].eq("Heat")
    is_layered_heat = frame["variables"].str.startswith(tuple(heat_layers), na=False)
    frame = frame.loc[~is_heat_sector | is_layered_heat].copy()
    for prefix, sector in heat_layers.items():
        frame.loc[frame["variables"].str.startswith(prefix, na=False), "sector"] = (
            sector
        )

    frame = frame.loc[frame["val"].ne(0) & frame["val"].abs().gt(0.1)].copy()
    frame["year"] = frame["year"].astype("int32")
    frame["val"] = frame["val"].astype("float32")
    return frame.sort_values(
        ["model", "scenario", "sector", "variables", "region", "year"]
    ).reset_index(drop=True)


def main() -> None:
    args = parse_args()
    actual_version = version_string()
    if actual_version != args.expected_version:
        raise SystemExit(
            f"Expected premise {args.expected_version}, imported {actual_version}"
        )

    key_text = os.environ.get("PREMISE_KEY") or os.environ.get("IAM_FILES_KEY")
    if not key_text:
        raise SystemExit("Set PREMISE_KEY (or IAM_FILES_KEY) for encrypted IAM data")

    mapping = load_production_mapping(args.mapping_overview)
    frames = [
        scenario_frame(scenario, mapping, args.iam_dir, key_text.encode("utf-8"))
        for scenario in SCENARIOS
    ]
    dataset = normalize_dataset(pd.concat(frames, ignore_index=True))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(args.output, index=False)
    heat_variables = dataset.loc[
        dataset["sector"].isin(
            ["Heat - Buildings", "Heat - Industry", "Heat - District heating"]
        ),
        "variables",
    ].nunique()
    print(
        f"Wrote {len(dataset):,} rows and {heat_variables} heat variables to {args.output}",
        flush=True,
    )


if __name__ == "__main__":
    main()
