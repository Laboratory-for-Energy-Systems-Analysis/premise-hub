from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from apps.scenario_explorer.app import (
    DATASETS,
    DEFAULT_DATASET,
    MAX_COMPARISONS,
    TOP_VARIABLES,
    UNITS,
    app,
    available_pairs,
    build_figure,
    build_layout,
    build_single_series_figure,
    chart_kind,
    common_regions,
    dataset_path,
    export_displayed,
    export_selected,
    get_all_variables,
    get_dataset,
    humanize_variable,
    is_single_series_comparison,
    normalize_pairs,
    parse_view_query,
    sector_supports_relative,
    sectors_for_topic,
    serialize_view_state,
    summarize_for_chart,
    validate_view_state,
)
from apps.scenario_explorer.dev.generate_data import (
    normalize_dataset,
    validate_historical_pathway_scale,
)


def component_ids(component) -> set[str]:
    ids: set[str] = set()
    component_id = getattr(component, "id", None)
    if isinstance(component_id, str):
        ids.add(component_id)
    children = getattr(component, "children", None)
    if children is None:
        return ids
    if not isinstance(children, (list, tuple)):
        children = [children]
    for child in children:
        if hasattr(child, "to_plotly_json"):
            ids.update(component_ids(child))
    return ids


def test_dataset_manifest_preserves_live_versions() -> None:
    assert DEFAULT_DATASET == "2.4.9"
    assert list(DATASETS) == [
        "2.4.9",
        "2.4.8",
        "2.4.4",
        "2.3.7",
        "2.3.2",
        "2.3.1",
        "2.3.0",
        "2.2.0",
    ]
    assert all(dataset_path(dataset_id).is_file() for dataset_id in DATASETS)
    with pytest.raises(ValueError):
        dataset_path("../../etc/passwd")


def test_loader_adds_provenance_to_historical_data() -> None:
    current = get_dataset(DEFAULT_DATASET)
    historical = get_dataset("2.4.8")
    required = {"model", "scenario", "sector", "region", "variables", "year", "val"}
    assert required <= set(current.columns)
    assert required <= set(historical.columns)
    assert set(historical["region_source"].astype(str).unique()) == {"reported"}
    assert {
        "Heat - Buildings",
        "Heat - Industry",
        "Heat - District heating",
    } <= set(current["sector"].astype(str).unique())


def test_current_dataset_integrity_and_derived_world_equality() -> None:
    frame = get_dataset(DEFAULT_DATASET)
    keys = ["region", "year", "variables", "sector", "model", "scenario"]
    assert np.isfinite(frame["val"]).all()
    assert frame["val"].ne(0).all()
    assert not frame.duplicated(keys).any()

    district_heat = frame.loc[
        frame["model"].astype(str).eq("image")
        & frame["sector"].astype(str).eq("Heat - District heating")
    ]
    assert district_heat["scenario"].astype(str).nunique() == 8
    assert (
        district_heat.loc[district_heat["region"].astype(str).eq("World"), "scenario"]
        .astype(str)
        .nunique()
        == 8
    )

    group_keys = ["model", "scenario", "sector", "variables", "year"]
    image = frame.loc[frame["model"].astype(str).eq("image")]
    derived = image.loc[
        image["region"].astype(str).eq("World")
        & image["region_source"].astype(str).eq("derived")
    ]
    regional_sums = (
        image.loc[image["region"].astype(str).ne("World")]
        .groupby(group_keys, observed=True, as_index=False)["val"]
        .sum()
        .rename(columns={"val": "regional_sum"})
    )
    checked = derived.merge(regional_sums, on=group_keys, how="left")
    assert len(checked) == len(derived) == 600
    assert np.allclose(checked["val"], checked["regional_sum"], rtol=1e-12, atol=1e-12)
    validate_historical_pathway_scale(frame)

    all_sectors: set[str] = set()
    for dataset_id in DATASETS:
        all_sectors.update(
            pd.read_csv(dataset_path(dataset_id), usecols=["sector"])["sector"]
            .dropna()
            .astype(str)
            .unique()
        )
    assert not all_sectors - set(UNITS)


def test_current_release_has_no_systematic_scale_shift_from_248() -> None:
    current = get_dataset(DEFAULT_DATASET)
    previous = get_dataset("2.4.8")
    keys = ["model", "scenario", "sector", "variables", "region", "year"]
    common = previous.merge(current, on=keys, suffixes=("_previous", "_current"))
    common = common.loc[common["val_previous"].ne(0) & common["val_current"].ne(0)]
    common["ratio"] = common["val_current"].abs() / common["val_previous"].abs()
    summary = common.groupby(["model", "scenario", "sector"], observed=True)[
        "ratio"
    ].agg(["count", "median"])
    systematic = summary.loc[
        summary["count"].ge(20)
        & (summary["median"].gt(100) | summary["median"].lt(0.01))
    ]
    assert systematic.empty
    assert not common["ratio"].between(900, 1100).any()


def test_catalog_initializes_without_loading_every_dataset() -> None:
    variables = get_all_variables()
    assert variables == sorted(variables)
    assert len(variables) > 100


def test_normalization_preserves_small_values_and_derives_image_world() -> None:
    frame = pd.DataFrame(
        [
            [
                "A",
                2030,
                "heat, secondary, natural gas",
                "Heat",
                "image",
                "SSP1-L",
                0.02,
            ],
            [
                "B",
                2030,
                "heat, secondary, natural gas",
                "Heat",
                "image",
                "SSP1-L",
                0.03,
            ],
            ["A", 2030, "heat, secondary, biomass", "Heat", "image", "SSP1-L", 0.01],
            [
                "World",
                2030,
                "heat, secondary, biomass",
                "Heat",
                "image",
                "SSP1-L",
                0.25,
            ],
            ["A", 2030, "heat, secondary, oil", "Heat", "remind", "SSP2-NPi", 0.04],
            ["B", 2030, "heat, secondary, coal", "Heat", "image", "SSP1-L", np.nan],
            ["B", 2030, "heat, secondary, coal", "Heat", "image", "SSP1-L", 0.0],
        ],
        columns=["region", "year", "variables", "sector", "model", "scenario", "val"],
    )
    normalized = normalize_dataset(frame)

    natural_gas = normalized.loc[
        normalized["variables"].eq("heat, secondary, natural gas")
    ]
    assert set(natural_gas["region"]) == {"A", "B", "World"}
    derived = natural_gas.loc[natural_gas["region"].eq("World")].iloc[0]
    assert derived["val"] == pytest.approx(0.05)
    assert derived["region_source"] == "derived"

    biomass_world = normalized.loc[
        normalized["variables"].eq("heat, secondary, biomass")
        & normalized["region"].eq("World")
    ]
    assert len(biomass_world) == 1
    assert biomass_world.iloc[0]["val"] == pytest.approx(0.25)
    assert biomass_world.iloc[0]["region_source"] == "reported"
    assert normalized["val"].abs().min() == pytest.approx(0.01)
    assert np.isfinite(normalized["val"]).all()
    assert not (
        normalized["model"].eq("remind") & normalized["region"].eq("World")
    ).any()


def test_historical_scale_validation_rejects_mixed_units_in_any_sector() -> None:
    frame = pd.DataFrame(
        {
            "model": ["image", "image"],
            "scenario": ["SSP1-L", "SSP1-M"],
            "sector": ["Any mapped sector"] * 2,
            "region": ["World"] * 2,
            "year": [2020] * 2,
            "val": [77_000_000.0, 77_000.0],
        }
    )
    with pytest.raises(ValueError, match="historical scale"):
        validate_historical_pathway_scale(frame)


def test_pair_region_and_topic_contracts() -> None:
    frame = get_dataset(DEFAULT_DATASET)
    district_pairs = available_pairs(frame, "Heat - District heating")
    assert len(district_pairs) > 1
    assert "Heat - District heating" in sectors_for_topic(frame, "heat")
    assert common_regions(frame, "GMST increase", district_pairs[:2])[0] == "World"
    assert normalize_pairs(district_pairs * 2) == district_pairs[:MAX_COMPARISONS]


def test_url_state_round_trip_and_invalid_fallback() -> None:
    state = {
        "version": "2.4.9",
        "sector": "Heat - District heating",
        "pairs": [
            {"model": "image", "scenario": "SSP1-L"},
            {"model": "remind", "scenario": "SSP2-NPi"},
        ],
        "regions": ["World", "WEU"],
        "mode": "relative",
    }
    assert parse_view_query("?" + serialize_view_state(state)) == state

    validated, notes = validate_view_state(
        {
            "version": "unknown",
            "sector": "not-a-sector",
            "pairs": [{"model": "bad", "scenario": "bad"}],
            "regions": ["Atlantis"],
            "mode": "relative",
        }
    )
    assert validated["version"] == DEFAULT_DATASET
    assert validated["sector"] == "GMST increase"
    assert validated["pairs"] == [{"model": "image", "scenario": "SSP1-L"}]
    assert validated["regions"] == ["World"]
    assert validated["mode"] == "absolute"
    assert notes


def test_top_eight_other_is_display_only() -> None:
    rows = []
    for index in range(10):
        rows.append(
            {
                "year": 2050,
                "region": "World",
                "region_source": "reported",
                "variables": f"technology {index}",
                "val": float(index + 1),
            }
        )
    source = pd.DataFrame(rows)
    plotted = summarize_for_chart(source)
    assert TOP_VARIABLES == 8
    assert plotted["display_variable"].nunique() == 9
    assert plotted.loc[plotted["display_variable"].eq("Other"), "val"].iloc[0] == 3
    assert source["variables"].nunique() == 10
    assert source["val"].sum() == plotted["val"].sum()


def test_chart_rules_labels_and_relative_eligibility() -> None:
    base = pd.DataFrame(
        {
            "year": [2030, 2040, 2050],
            "region": ["World"] * 3,
            "region_source": ["reported"] * 3,
            "variables": ["heat, secondary, natural gas"] * 3,
            "val": [1.0, 1.5, 2.0],
        }
    )
    assert humanize_variable("heat, secondary, natural gas") == "Natural gas"
    assert chart_kind("Heat - District heating", base) == "area"
    assert chart_kind("Heat - District heating", base.iloc[:2]) == "bar"
    assert chart_kind("Carbon Dioxide Removal", base) == "area"
    assert chart_kind("GMST increase", base) == "line"
    assert sector_supports_relative("Heat - District heating", base)
    assert not sector_supports_relative("GMST increase", base)
    assert not sector_supports_relative(
        "Heat - District heating", base.assign(val=[1.0, -0.5, 2.0])
    )
    figure = build_figure(base, "Heat - District heating", "relative")
    assert figure.layout.yaxis.range == (0, 100)
    assert figure.layout.showlegend is True

    removal = pd.concat(
        [
            base.assign(variables="geological storage"),
            base.assign(variables="enhanced weathering", val=base["val"] * 0.5),
        ],
        ignore_index=True,
    )
    removal_figure = build_figure(removal, "Carbon Dioxide Removal", "absolute")
    assert len(removal_figure.data) == 2
    assert all(trace.stackgroup == "1" for trace in removal_figure.data)


def test_comparable_single_series_are_overlaid_by_model_scenario() -> None:
    rows = []
    for model, scenario, values in [
        ("image", "SSP1-L", [1.0, 1.5, 2.0]),
        ("remind", "SSP2-NPi", [1.2, 1.7, 2.3]),
    ]:
        for year, value in zip([2030, 2040, 2050], values, strict=True):
            rows.append(
                {
                    "model": model,
                    "scenario": scenario,
                    "year": year,
                    "region": "World",
                    "region_source": "reported",
                    "variables": "temperature",
                    "val": value,
                }
            )
    frame = pd.DataFrame(rows)
    pairs = [
        {"model": "image", "scenario": "SSP1-L"},
        {"model": "remind", "scenario": "SSP2-NPi"},
    ]

    assert is_single_series_comparison(frame)
    figure = build_single_series_figure(frame, "GMST increase", "absolute", pairs)
    assert [trace.name for trace in figure.data] == [
        "IMAGE · SSP1-L",
        "REMIND · SSP2-NPi",
    ]
    assert all(trace.mode == "lines+markers" for trace in figure.data)
    assert figure.layout.legend.title.text == "Model · scenario"

    second_region = frame.assign(region="WEU", val=frame["val"] * 0.2)
    regional = pd.concat([frame, second_region], ignore_index=True)
    assert is_single_series_comparison(regional)
    regional_figure = build_single_series_figure(
        regional, "GMST increase", "absolute", pairs
    )
    assert len(regional_figure.data) == 4
    assert {annotation.text for annotation in regional_figure.layout.annotations} == {
        "World",
        "WEU",
    }

    multi_component = pd.concat(
        [frame, frame.iloc[[0]].assign(variables="another indicator")],
        ignore_index=True,
    )
    assert not is_single_series_comparison(multi_component)


def test_exports_are_unsummarized_and_include_provenance() -> None:
    pairs = [{"model": "image", "scenario": "SSP1-L"}]
    current = export_displayed(
        1, pairs, "Heat - District heating", ["World"], DEFAULT_DATASET
    )
    selected = export_selected(1, pairs, DEFAULT_DATASET)
    assert current["filename"] == "premise-2.4.9-heat-district-heating-current-view.csv"
    assert selected["filename"] == "premise-2.4.9-selected-scenarios.csv"
    assert current["content"].splitlines()[0].endswith("region_source")
    assert selected["content"].splitlines()[0].endswith("region_source")
    assert ",derived" in current["content"]
    assert "Other" not in current["content"]


def test_layout_exposes_accessible_workflow_and_psi_theme() -> None:
    ids = component_ids(build_layout())
    assert {
        "dataset-version-dropdown",
        "topic-dropdown",
        "sector-dropdown",
        "model-dropdown",
        "scenario-dropdown",
        "add-comparison-btn",
        "comparison-store",
        "region-dropdown",
        "view-mode-radio",
        "share-link-copy",
        "graphs-loading",
    } <= ids
    assert app.title == "Premise IAM Scenario Explorer"

    explorer_css = (Path("apps/scenario_explorer/assets/explorer.css")).read_text()
    workshop_css = (Path("apps/workshop/assets/styles.css")).read_text()
    for token in [
        "--ink: #17232c",
        "--muted: #5b6a74",
        "--psi-blue: #006b8f",
        "--psi-deep: #0b3b52",
        "--teal: #008a82",
        "--amber: #d99614",
    ]:
        assert token in explorer_css
        assert token in workshop_css
