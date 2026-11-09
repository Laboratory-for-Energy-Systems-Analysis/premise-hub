"""Lossless runtime loading without retaining duplicate raw result tables."""

import csv
import gzip
import importlib.util
import json
import math
from pathlib import Path

import pytest

from apps.ccus_webinar.webinar.release import (
    APP,
    _read_public_json,
    load_release_bundle,
)
from apps.ccus_webinar.webinar.tables import ColumnTable


@pytest.mark.parametrize(
    "rows",
    [
        [],
        [{}, {}],
        [{"a": 1}, {"b": None}],
        [
            {
                "label": "first",
                "year": 2030,
                "value": -0.0,
                "flag": True,
                "missing": None,
            },
            {
                "label": "second",
                "year": 2050,
                "value": 1.23456789012345,
                "flag": False,
                "missing": None,
            },
        ],
        [{"number": 2**100}, {"number": 1}],
        [{"value": 1}, {"value": 1.0}],
    ],
)
def test_column_table_preserves_rows_types_slices_and_independent_reads(rows):
    table = ColumnTable(rows)
    assert len(table) == len(rows)
    assert list(table) == rows
    assert table[:] == tuple(rows)
    assert table[::-1] == tuple(reversed(rows))
    for index, expected in enumerate(rows):
        assert table[index] == expected
        assert {key: type(value) for key, value in table[index].items()} == {
            key: type(value) for key, value in expected.items()
        }
        modified = table[index]
        modified["new"] = "changed"
        assert table[index] == expected
    if rows:
        assert table[-1] == rows[-1]
    with pytest.raises(IndexError):
        table[len(rows)]
    with pytest.raises(IndexError):
        table[-len(rows) - 1]


def test_column_table_preserves_nonfinite_values_and_signed_zero():
    table = ColumnTable(
        [{"value": float("nan")}, {"value": float("inf")}, {"value": -0.0}]
    )
    assert math.isnan(table[0]["value"])
    assert table[1]["value"] == float("inf")
    assert math.copysign(1, table[2]["value"]) == -1


@pytest.mark.parametrize(
    "key",
    [
        "main",
        "2035-SSP2-NPi",
        "2035-SSP2-PkBudg1000",
        "2050-SSP2-NPi",
        "2050-SSP2-PkBudg1000",
    ],
)
def test_compact_release_matches_every_source_row_and_payload(key):
    bundle = load_release_bundle(key)
    assert bundle.approved
    path = APP / bundle.manifest["bundles"][key]["path"]
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        source = json.load(stream)
    assert bundle.tables.keys() == source["tables"].keys()
    for name, expected in source["tables"].items():
        actual = bundle.tables[name]
        assert len(actual) == len(expected)
        assert all(row == original for row, original in zip(actual, expected)), name
    assert bundle.payloads == source["payloads"]
    assert bundle.arrays == source.get("arrays", {})


@pytest.mark.parametrize("compressed", [False, True])
def test_public_json_shares_labels_without_changing_values(tmp_path, compressed):
    label = "Repeated scenario and provenance label"
    expected = {
        "tables": {
            "example": [
                {
                    "label": label,
                    "score": 1.23456789012345,
                    "year": 2030,
                    "valid": True,
                },
                {
                    "label": label,
                    "score": None,
                    "nested": {"label": label, "unicode": "CO₂"},
                },
            ]
        },
        "arrays": [],
        "payloads": {},
    }
    path = tmp_path / ("example.json.gz" if compressed else "example.json")
    opener = gzip.open if compressed else open
    with opener(path, "wt", encoding="utf-8") as stream:
        json.dump(expected, stream)
    actual = _read_public_json(path)
    assert actual == expected
    rows = actual["tables"]["example"]
    assert rows[0]["label"] is rows[1]["label"] is rows[1]["nested"]["label"]


@pytest.fixture
def reader():
    path = Path(__file__).resolve().parents[1] / "apps/lca_time/workshop/results.py"
    spec = importlib.util.spec_from_file_location("isolated_memory_reader", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_rows(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_fair_index_streams_rows_and_preserves_accumulation(reader, tmp_path):
    path = tmp_path / "fair.csv"
    base = dict(
        case="DACCS",
        metric="radiative forcing",
        contribution_view="process",
        quantile="50",
        contributor="electricity",
        response_year="2030",
    )
    write_rows(
        path,
        [
            {**base, "value_per_net_tonne": "1.25"},
            {**base, "value_per_net_tonne": "-0.5"},
            {**base, "response_year": "2031", "value_per_net_tonne": "2"},
        ],
    )
    reader.COHORT_FAIR_RESPONSES = path
    assert reader.cohort_fair_response_series(
        "DACCS", "radiative forcing", "process"
    ) == (("electricity", ((2030, 0.75), (2031, 2.0))),)
    assert reader.cohort_fair_response_rows.cache_info().currsize == 0


def test_reference_index_preserves_selection_sorting_and_duplicate_years(
    reader, tmp_path
):
    path = tmp_path / "reference.csv"
    base = dict(metric="radiative forcing", quantile="50", pulse_year="2030")
    write_rows(
        path,
        [
            {**base, "response_year": "2031", "value_per_kg_co2_pulse": "2"},
            {**base, "response_year": "2030", "value_per_kg_co2_pulse": "1"},
            {**base, "response_year": "2030", "value_per_kg_co2_pulse": "3"},
            {
                **base,
                "quantile": "2.5",
                "response_year": "2030",
                "value_per_kg_co2_pulse": "0.5",
            },
        ],
    )
    reader.CO2_REFERENCE_PULSE = path
    assert reader.co2_reference_pulse_series("radiative forcing") == (
        (2030, 3.0),
        (2031, 2.0),
    )
    assert reader.co2_reference_pulse_series("radiative forcing", 2.5) == ((2030, 0.5),)
    assert reader.co2_reference_pulse_rows.cache_info().currsize == 0
    with pytest.raises(LookupError):
        reader.co2_reference_pulse_series("temperature")


def test_workshop_categories_preserve_complete_source_table():
    import pandas as pd
    from apps.workshop.workshop.data import PATHWAY_FILE, pathways

    original = pd.read_csv(PATHWAY_FILE)
    compact = pathways()
    labels = {column: "object" for column in compact.select_dtypes(include="category")}
    pd.testing.assert_frame_equal(compact.astype(labels), original)
    assert (
        compact.memory_usage(deep=True).sum()
        < original.memory_usage(deep=True).sum() / 5
    )
