from __future__ import annotations

import pytest

from apps.scenario_explorer.app import (
    DATASETS,
    DEFAULT_DATASET,
    dataset_path,
    get_all_variables,
    get_dataset,
    update_dropdowns,
    update_graphs,
    update_region_options,
)


def test_dataset_manifest_preserves_live_versions() -> None:
    assert DEFAULT_DATASET == "2.4.4"
    assert list(DATASETS) == ["2.4.4", "2.3.7", "2.3.2", "2.3.1", "2.3.0", "2.2.0"]
    assert all(dataset_path(dataset_id).is_file() for dataset_id in DATASETS)
    with pytest.raises(ValueError):
        dataset_path("../../etc/passwd")


def test_catalog_initializes_without_loading_every_dataset() -> None:
    variables = get_all_variables()
    assert variables == sorted(variables)
    assert len(variables) > 100


def test_default_explorer_callbacks_render() -> None:
    frame = get_dataset(DEFAULT_DATASET)
    assert not frame.empty
    assert {"model", "scenario", "sector", "region", "variables", "year", "val"} <= set(frame.columns)

    model_options, selected_models, sector_options, selected_sector = update_dropdowns(DEFAULT_DATASET)
    assert model_options
    assert selected_models == [model_options[0]["value"]]
    assert sector_options

    region_options, regions = update_region_options(
        selected_sector,
        selected_models,
        DEFAULT_DATASET,
        ["World"],
    )
    assert region_options
    assert regions

    rendered = update_graphs(
        selected_models,
        selected_sector,
        regions,
        [],
        DEFAULT_DATASET,
    )
    assert rendered

