import numpy as np
import pandas as pd

from apps.scenario_explorer import app as explorer
from apps.scenario_explorer.dev.generate_data import normalize_dataset

PAIRS = [
    {"model": "remind-eu", "scenario": "SSP2-NPi"},
    {"model": "remind-eu", "scenario": "SSP2-PkBudg1000"},
]


def test_gas_supplier_names_are_classified_without_heat_demand():
    variables = [
        "natural gas",
        "biomethane",
        "methane, from biomass",
        "methane, synthetic",
        "methane, from coal",
        "methane, fossil",
        "heat, industrial, from biomethane boiler",
    ]
    frame = pd.DataFrame(
        {
            "variables": variables,
            "val": np.arange(1, len(variables) + 1, dtype=float),
            "sector": ["Fuels"] * 6 + ["Heat"],
            "region": "ENC",
            "year": 2050,
            **PAIRS[0],
        }
    )
    normalized = normalize_dataset(frame).set_index("variables")
    assert normalized.loc[variables[:6], "sector"].eq("Gas").all()
    assert normalized.loc[variables[-1], "sector"] == "Heat - Industry"
    np.testing.assert_array_equal(normalized.loc[variables, "val"], frame.val)


def test_remind_eu_enc_has_biomethane_and_separate_pathway_charts():
    frame = explorer.filter_frame(explorer.get_dataset("2.4.9"), "Gas", PAIRS, ["ENC"])
    for pair in PAIRS:
        subset = frame.loc[frame.scenario.eq(pair["scenario"])]
        assert {"natural gas", "methane, from biomass", "methane, synthetic"} <= set(
            subset.variables
        )
        assert (
            subset.loc[subset.variables.eq("methane, from biomass"), "val"].gt(0).all()
        )

    children, status = explorer.update_graphs(
        PAIRS, "Gas", ["ENC"], "relative", "2.4.9"
    )
    cards = children[1].children
    assert len(cards) == 2
    assert status == "Rendered 2 comparison charts."
    for card, pair in zip(cards, PAIRS):
        assert card.children[0].children[0].children[1].children == pair["scenario"]
        figure = card.children[1].figure
        assert {trace.name for trace in figure.data} == {
            "Natural gas",
            "Methane, from biomass",
            "Methane, synthetic",
        }
        assert all(trace.groupnorm == "percent" for trace in figure.data)


def test_single_supplier_pathways_stay_separate(monkeypatch):
    frame = pd.DataFrame(
        [
            dict(
                pair,
                region="ENC",
                year=year,
                variables="natural gas",
                val=value,
                sector="Gas",
                region_source="reported",
            )
            for pair in PAIRS
            for year, value in [(2030, 1.0), (2040, 2.0), (2050, 3.0)]
        ]
    )
    monkeypatch.setattr(explorer, "get_dataset", lambda _: frame)
    for mode in ["absolute", "relative"]:
        children, _ = explorer.update_graphs(PAIRS, "Gas", ["ENC"], mode, "2.4.9")
        assert len(children[1].children) == 2
