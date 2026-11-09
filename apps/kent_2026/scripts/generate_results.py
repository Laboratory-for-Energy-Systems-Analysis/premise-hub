#!/usr/bin/env python3
"""Generate auditable, presentation-sized carculator results.

Run from the repository root with the local carculator checkouts on PYTHONPATH.
The output deliberately contains only whole-vehicle annual profiles and derived
decision maps; the web app performs no LCA calculations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import xarray as xr

from carculator import CarInputParameters, CarModel, InventoryCar, fill_xarray_from_input_parameters

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "runtime"
SUPPORTED = [2020, 2025, 2030, 2040, 2050]
YEARS = list(range(2020, 2061))
ANCHOR_YEARS = [2020, 2025, 2030, 2035, 2040, 2050, 2060]
MILEAGES = [5_000, 12_000, 20_000]
LIFETIMES = [150_000, 200_000, 250_000]
CORE_CATEGORIES = ["climate change", "particulate matter formation"]
SCENARIOS = {
    "baseline": ("SSP2-NPi", "geco-2025-reference"),
    "transition": ("SSP2-PkBudg1000", "geco-2025-ndc-lts"),
    "rapid": ("SSP2-PkBudg650", "geco-2025-1.5c"),
    "electricity_ndc": ("SSP2-NPi", "geco-2025-ndc-lts"),
    "electricity_15c": ("SSP2-NPi", "geco-2025-1.5c"),
    "fuel_e20": ("SSP2-NPi", "geco-2025-reference"),
    "fuel_e50": ("SSP2-NPi", "geco-2025-reference"),
    "fuel_e85": ("SSP2-NPi", "geco-2025-reference"),
    "fuel_synthetic": ("SSP2-NPi", "geco-2025-reference"),
    "fuel_hydrogen": ("SSP2-NPi", "geco-2025-reference"),
}


class HeldEndpointInventoryCar(InventoryCar):
    """Allow post-2050 cohorts while holding endpoint-only fuel data at 2050."""

    def get_sulfur_content(self, location, fuel):
        years = np.asarray(self.scope["year"])
        endpoint = int(self.bs.sulfur.year.max())
        selected = self.bs.sulfur.sel(
            country=location if location in self.bs.sulfur.country.values else "RER",
            year=np.minimum(years, endpoint),
            fuel=fuel,
            drop=True,
        ).copy(deep=True)
        return selected.assign_coords(year=years)


def git_state(path: Path) -> dict:
    def run(*args: str) -> str:
        return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()
    return {
        "path": str(path),
        "commit": run("rev-parse", "HEAD"),
        "dirty": bool(run("status", "--porcelain")),
    }


def model_array(years: list[int], sizes: list[str], powertrains: list[str], variants: list[dict]) -> xr.DataArray:
    params = CarInputParameters()
    params.static()
    _, base = fill_xarray_from_input_parameters(
        params,
        scope={"size": sizes, "powertrain": powertrains, "year": SUPPORTED},
    )
    core_years = [year for year in years if year <= 2050]
    parts = [base.interp(year=core_years)] if core_years else []
    future = [year for year in years if year > 2050]
    if future:
        held = xr.concat(
            [base.sel(year=2050, drop=True)] * len(future),
            dim=xr.IndexVariable("year", future),
        )
        parts.append(held)
    array = xr.concat(parts, dim="year").transpose(*base.dims)
    array = xr.concat(
        [array.isel(value=0, drop=True)] * len(variants),
        dim=xr.IndexVariable("value", [item["label"] for item in variants]),
    ).transpose(*base.dims)
    for item in variants:
        array.loc[dict(value=item["label"], parameter="kilometers per year")] = item["annual_km"]
        array.loc[dict(value=item["label"], parameter="lifetime kilometers")] = item["lifetime_km"]
    return array


def fuel_blend(kind: str) -> dict | None:
    if kind in {"e20", "e50", "e85"}:
        ethanol_volume_share = {"e20": 0.20, "e50": 0.50, "e85": 0.85}[kind]
        petrol_mass = (1 - ethanol_volume_share) * 0.75
        ethanol_mass = ethanol_volume_share * 0.785
        share = petrol_mass / (petrol_mass + ethanol_mass)
        return {"petrol": {
            "primary": {"type": "petrol", "share": share},
            "secondary": {"type": "petrol - bioethanol - maize starch", "share": 1 - share},
        }}
    if kind == "synthetic":
        return {"petrol": {
            "primary": {"type": "petrol - synthetic - methanol - cement - energy allocation", "share": 1.0},
            "secondary": {"type": "petrol", "share": 0.0},
        }}
    if kind == "hydrogen-smr":
        return {"hydrogen": {
            "primary": {"type": "hydrogen - smr - natural gas", "share": 1.0},
            "secondary": {"type": "hydrogen - electrolysis - PEM", "share": 0.0},
        }}
    return None


def calculate_batch(
    profiles: dict,
    *,
    case: str,
    years: list[int],
    sizes: list[str],
    powertrains: list[str],
    variants: list[dict],
    fuel: str = "default",
) -> tuple[dict, dict]:
    scenario, electricity = SCENARIOS[case]
    array = model_array(years, sizes, powertrains, variants)
    model = CarModel(array, country="US", cycle="WLTC", fuel_blend=fuel_blend(fuel))
    model.set_all()
    model.array.loc[dict(parameter="battery lifetime replacements")] = 0
    inventory = HeldEndpointInventoryCar(
        model,
        scenario=scenario,
        method="ef",
        indicator="midpoint",
        functional_unit="vkm",
        background_configuration={"electricity scenario": electricity},
    )
    categories = {
        name: {key: value for key, value in metadata.items()}
        for name, metadata in inventory.impact_categories.items()
    }
    # The aggregate EF calculation covers all 25 midpoint categories.  The
    # much larger annual tensor is retained only for the two categories used
    # in the presentation; slicing before temporal characterization keeps the
    # generator's memory and runtime proportional to the published result.
    aggregate = inventory.calculate_impacts().sum("impact")
    inventory.B = inventory.B.sel(category=CORE_CATEGORIES)
    inventory.impact_categories = {
        name: inventory.impact_categories[name] for name in CORE_CATEGORIES
    }
    temporal = inventory.calculate_temporal_impacts().sum("impact")
    for cohort in years:
        for size in sizes:
            for powertrain in powertrains:
                for variant in variants:
                    label = variant["label"]
                    cell = temporal.sel(size=size, powertrain=powertrain, year=cohort, value=label)
                    annual = {}
                    for category in CORE_CATEGORIES:
                        selected = cell.sel(impact_category=category)
                        years_out = {}
                        for event_year in selected.calendar_year.values.tolist():
                            stages = {}
                            row = selected.sel(calendar_year=event_year)
                            for stage in row.lifecycle_stage.values.tolist():
                                value = float(row.sel(lifecycle_stage=stage).item())
                                if abs(value) > 1e-15:
                                    stages[str(stage)] = value
                            if stages:
                                years_out[str(int(event_year))] = stages
                        annual[category] = years_out
                    key = f"{case}|{cohort}|{size}|{powertrain}|{variant['annual_km']}|{variant['lifetime_km']}"
                    profiles[key] = {
                        "cohort": cohort,
                        "size": size,
                        "powertrain": powertrain,
                        "annual_km": variant["annual_km"],
                        "lifetime_km": variant["lifetime_km"],
                        "scenario": scenario,
                        "electricity": electricity,
                        "fuel": fuel,
                        "ef_midpoints_per_vkm": {
                            category: float(
                                aggregate.sel(
                                    impact_category=category,
                                    size=size,
                                    powertrain=powertrain,
                                    year=cohort,
                                    value=label,
                                ).item()
                            )
                            for category in categories
                        },
                        "annual": annual,
                    }
    return categories, inventory.temporal_coverage()


def calculate_batched(profiles: dict, *, chunk_size: int = 6, **kwargs):
    """Calculate the same case in bounded cohort chunks to cap peak memory."""
    years = list(kwargs.pop("years"))
    categories = coverage = None
    for start in range(0, len(years), chunk_size):
        categories, coverage = calculate_batch(
            profiles, years=years[start : start + chunk_size], **kwargs
        )
    return categories, coverage


def interpolate_profiles(profiles, *, case, sizes, powertrains, variants):
    """Fill annual cohort profiles between directly calculated anchors.

    Interpolation is by event age (calendar year minus cohort), independently
    for every lifecycle stage and impact category.  This preserves the event
    schedule while interpolating the calendar-year characterized magnitude.
    """
    for target in YEARS:
        if target in ANCHOR_YEARS:
            continue
        lower = max(year for year in ANCHOR_YEARS if year < target)
        upper = min(year for year in ANCHOR_YEARS if year > target)
        weight = (target - lower) / (upper - lower)
        for size in sizes:
            for powertrain in powertrains:
                for variant in variants:
                    annual = variant["annual_km"]
                    lifetime = variant["lifetime_km"]
                    low = profiles[_profile_key(case, lower, size, powertrain, annual, lifetime)]
                    high = profiles[_profile_key(case, upper, size, powertrain, annual, lifetime)]
                    interpolated = {}
                    for category in CORE_CATEGORIES:
                        low_ages = {int(year) - lower: stages for year, stages in low["annual"][category].items()}
                        high_ages = {int(year) - upper: stages for year, stages in high["annual"][category].items()}
                        years_out = {}
                        for age in sorted(set(low_ages) | set(high_ages)):
                            stages = {}
                            low_row, high_row = low_ages.get(age, {}), high_ages.get(age, {})
                            for stage in set(low_row) | set(high_row):
                                value = (1 - weight) * low_row.get(stage, 0.0) + weight * high_row.get(stage, 0.0)
                                if abs(value) > 1e-15:
                                    stages[stage] = value
                            if stages:
                                years_out[str(target + age)] = stages
                        interpolated[category] = years_out
                    key = _profile_key(case, target, size, powertrain, annual, lifetime)
                    profiles[key] = {
                        **{k: v for k, v in low.items() if k not in {"cohort", "annual", "ef_midpoints_per_vkm"}},
                        "cohort": target,
                        "interpolated_from": [lower, upper],
                        "ef_midpoints_per_vkm": {
                            category: (1 - weight) * low["ef_midpoints_per_vkm"][category] + weight * high["ef_midpoints_per_vkm"][category]
                            for category in low["ef_midpoints_per_vkm"]
                        },
                        "annual": interpolated,
                    }


def _profile_key(case, cohort, size, powertrain, annual, lifetime):
    return f"{case}|{cohort}|{size}|{powertrain}|{annual}|{lifetime}"


def build_maps(profiles: dict) -> dict:
    del profiles
    from apps.kent_2026 import results as runtime_results

    runtime_results.bundle.cache_clear()
    states = {
        "baseline": dict(case="baseline", size="Medium", lifetime=200_000),
        "small_bev": dict(case="baseline", size="Small", lifetime=200_000),
        "large_bev": dict(case="baseline", size="Large SUV", lifetime=200_000),
        "short_life": dict(case="baseline", size="Medium", lifetime=150_000),
        "long_life": dict(case="baseline", size="Medium", lifetime=250_000),
        "transition": dict(case="transition", size="Medium", lifetime=200_000),
        "rapid": dict(case="rapid", size="Medium", lifetime=200_000),
    }
    maps = {}
    for name, config in states.items():
        values = {category: [] for category in CORE_CATEGORIES}
        valid = []
        for annual in MILEAGES:
            row_valid = []
            rows = {category: [] for category in CORE_CATEGORIES}
            for decision in range(2020, 2036):
                result = runtime_results.ownership_case(
                    decision_year=decision,
                    annual_km=annual,
                    lifetime_km=config["lifetime"],
                    size=config["size"],
                    case=config["case"],
                )
                row_valid.append(result["valid"])
                for category in CORE_CATEGORIES:
                    rows[category].append(
                        None if not result["valid"] else runtime_results.delta(result, category)
                    )
            valid.append(row_valid)
            for category in CORE_CATEGORIES: values[category].append(rows[category])
        maps[name] = {
            "decision_years": list(range(2020, 2036)),
            "annual_km": MILEAGES,
            "valid": valid,
            "values": values,
            **config,
        }
    return maps


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Generate only the baseline bundle for development.")
    parser.add_argument("--compose-only", action="store_true", help="Rebuild decision maps from the checked-in vehicle profiles.")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.compose_only:
        result_path = OUTPUT / "results.json"
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        payload["decision_maps"] = build_maps(payload["profiles"])
        result_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
        manifest_path = OUTPUT / "manifest.json"
        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_payload["results_sha256"] = sha256(result_path)
        manifest_path.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")
        print(f"Recomposed {len(payload['decision_maps'])} decision maps · {manifest_payload['results_sha256']}")
        return
    profiles = {}
    variants = [dict(label=f"m{m}", annual_km=m, lifetime_km=200_000) for m in MILEAGES]
    categories, coverage = calculate_batched(
        profiles, case="baseline", years=ANCHOR_YEARS, sizes=["Medium"],
        powertrains=["ICEV-p", "BEV"], variants=variants,
    )
    interpolate_profiles(profiles, case="baseline", sizes=["Medium"], powertrains=["ICEV-p", "BEV"], variants=variants)
    calculate_batched(
        profiles, case="baseline", years=ANCHOR_YEARS, sizes=["Small", "Large SUV"],
        powertrains=["BEV"], variants=variants,
    )
    interpolate_profiles(profiles, case="baseline", sizes=["Small", "Large SUV"], powertrains=["BEV"], variants=variants)
    for lifetime in (150_000, 250_000):
        lifetime_variants = [dict(label=f"m{m}", annual_km=m, lifetime_km=lifetime) for m in MILEAGES]
        calculate_batched(
            profiles, case="baseline", years=ANCHOR_YEARS, sizes=["Medium"],
            powertrains=["ICEV-p", "BEV"],
            variants=lifetime_variants,
        )
        interpolate_profiles(profiles, case="baseline", sizes=["Medium"], powertrains=["ICEV-p", "BEV"], variants=lifetime_variants)
    if not args.quick:
        for case in ("transition", "rapid"):
            calculate_batched(
                profiles, case=case, years=ANCHOR_YEARS, sizes=["Medium"], powertrains=["ICEV-p", "BEV"], variants=variants,
            )
            interpolate_profiles(profiles, case=case, sizes=["Medium"], powertrains=["ICEV-p", "BEV"], variants=variants)
        sensitivity_variant = [dict(label="m12000", annual_km=12_000, lifetime_km=200_000)]
        for case in ("electricity_ndc", "electricity_15c"):
            calculate_batched(
                profiles, case=case, years=ANCHOR_YEARS, sizes=["Medium"],
                powertrains=["ICEV-p", "BEV"], variants=sensitivity_variant,
            )
            interpolate_profiles(
                profiles, case=case, sizes=["Medium"],
                powertrains=["ICEV-p", "BEV"], variants=sensitivity_variant,
            )
        for case, fuel, powertrain in (
            ("fuel_e85", "e85", "ICEV-p"),
            ("fuel_synthetic", "synthetic", "ICEV-p"),
            ("fuel_hydrogen", "hydrogen-smr", "FCEV"),
        ):
            calculate_batched(
                profiles, case=case, years=ANCHOR_YEARS, sizes=["Medium"],
                powertrains=[powertrain], variants=sensitivity_variant, fuel=fuel,
            )
            interpolate_profiles(
                profiles, case=case, sizes=["Medium"],
                powertrains=[powertrain], variants=sensitivity_variant,
            )
    comparison_profiles = {}
    for fuel, powertrains in (("default", ["ICEV-p", "BEV"]), ("e85", ["ICEV-p"]), ("synthetic", ["ICEV-p"]), ("hydrogen-smr", ["FCEV"])):
        local = {}
        calculate_batch(
            local, case="baseline", years=[2026], sizes=["Small", "Medium", "Large SUV"],
            powertrains=powertrains,
            variants=[dict(label="comparison", annual_km=12_000, lifetime_km=200_000)], fuel=fuel,
        )
        for key, value in local.items():
            totals = {category: sum(sum(stages.values()) for stages in years.values()) for category, years in value["annual"].items()}
            comparison_profiles[f"{fuel}|{value['size']}|{value['powertrain']}"] = totals
    generated_at = datetime.now(UTC).isoformat()
    payload = {
        "schema_version": 1,
        "profiles": profiles,
        "decision_maps": {},
        "option_comparison": comparison_profiles,
        "ef_categories": list(categories.values()),
    }
    result_path = OUTPUT / "results.json"
    result_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    decision_maps = build_maps(profiles) if not args.quick else {}
    payload["decision_maps"] = decision_maps
    result_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    manifest_payload = {
        "schema_version": 1,
        "generated_at": generated_at,
        "carculator": git_state(Path.home() / "github" / "carculator"),
        "carculator_utils": git_state(Path.home() / "github" / "carculator_utils"),
        "configuration": {
            "country": "US", "cycle": "WLTC", "method": "EF v3.1 midpoint", "functional_unit": "vehicle-km",
            "years": [2020, 2060], "native_model_years": SUPPORTED, "post_2050": "2050 vehicle specifications held constant",
            "direct_cohort_anchors": ANCHOR_YEARS, "between_anchor_profiles": "linear interpolation by lifecycle-event age and stage",
            "backgrounds": SCENARIOS,
            "fuel_routes": {
                "default_petrol": "carculator US default petrol blend",
                "e85": "85% corn-starch ethanol by volume; balance petrol",
                "synthetic_petrol": "methanol route; electrolytic hydrogen; cement-plant CO2; energy allocation",
                "hydrogen": "natural-gas steam methane reforming",
            },
            "omitted_as_unsupported": ["DAC synthetic petrol", "dedicated solar-PV charging"],
            "battery_replacements": 0,
        },
        "temporal_coverage_example": coverage,
        "results_sha256": sha256(result_path),
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest_payload, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {len(profiles):,} profiles and {len(decision_maps)} decision maps to {result_path}")


if __name__ == "__main__":
    main()
