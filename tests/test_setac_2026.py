from __future__ import annotations

import hashlib
import json

import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from apps.setac_2026 import results
from apps.setac_2026.app import (
    pdf_deck,
    update_context,
    update_mixes,
    update_pulse,
    update_temporal,
)
from apps.setac_2026.deck import ALL_SLIDES, CORE_COUNT, SLIDES
from apps.setac_2026.figures import (
    CASES,
    MIX_SECTORS,
    MIX_YEARS,
    PATHWAYS,
    SNAPSHOT_YEARS,
    forcing_figure,
    mix_figure,
    prospective_figure,
    pulse_figure,
    pulse_value,
    removal_requirements,
    scenario_context_figure,
    scenario_context_rows,
    sector_mix,
    sector_mix_rows,
    static_figure,
    static_score,
    temporal_figure,
    temporal_years,
)
from portal.wsgi import application


def test_regenerated_dataset_is_isolated_and_uses_consistent_inputs():
    from apps.lca_time.workshop import results as original

    manifest = json.loads((results.ROOT / "data/regeneration.json").read_text())
    new_hash = manifest["new_package"]["archive_sha256"]
    foreground_hash = manifest["foreground_sha256"]
    assert results.STATIC_RESULTS != original.STATIC_RESULTS
    assert results.cohort_temporal_score_rows is not original.cohort_temporal_score_rows
    for name, digest in manifest["output_sha256"].items():
        path = results.ROOT / "data/processed" / name
        with path.open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == digest
    for row in results.static_rows():
        assert row["foreground_sha256"] == foreground_hash
        expected = (
            new_hash
            if row["pathway"] == "SSP2-PkBudg1000"
            else manifest["comparison_package"]["sha256"]
        )
        assert row["package_sha256"] == expected
    for row in (
        *results.cohort_temporal_score_rows(),
        *results.cohort_fair_response_rows(),
    ):
        assert row["package_sha256"] == new_hash
        assert row["foreground_sha256"] == foreground_hash
    grid = json.loads(results.cohort_pulse_equivalence_grid()["metadata_json"])
    assert grid["package_sha256"] == new_hash
    assert grid["foreground_sha256"] == foreground_hash
    summary = manifest["forcing_summary"]
    assert summary["scenario"] == grid["scenario"]
    assert (
        summary["csv_sha256"] == manifest["output_sha256"]["cohort_fair_responses.csv"]
    )
    assert {r["contribution_view"] for r in results.cohort_fair_response_rows()} == {
        "total"
    }


@pytest.mark.parametrize("case", CASES)
def test_default_pulse_matches_independent_trails_calculation(case):
    validation = json.loads(
        (
            results.ROOT / "data/processed/cohort_pulse_equivalence_validation.json"
        ).read_text()
    )
    expected = validation["cases"][case]["radiative forcing"][
        "trails_config_first_kg_co2_per_net_tonne"
    ]["median"]
    assert pulse_value(case) == pytest.approx(expected, abs=0.02)
    integration = json.loads(
        (results.ROOT / "data/processed/pulse_integration_audit.json").read_text()
    )["cases"][case]["values_kg_co2_per_net_tonne"]
    for end in (2100, 2140, 2300):
        assert pulse_value(case, end) == pytest.approx(
            integration["1.0"][str(end)], abs=0.02
        )
        assert abs(integration["1.0"][str(end)] - integration["0.1"][str(end)]) < 0.1


@pytest.mark.parametrize(
    "path",
    (
        "/",
        "/presenter",
        "/health",
        "/_dash-layout",
        "/_dash-dependencies",
        "/assets/styles.css",
        "/shared/case-pathways.svg",
        "/system-flows.svg",
    ),
)
def test_setac_routes_are_public(path):
    client = Client(application, Response)
    response = client.get("/setac-2026" + path)
    assert response.status_code == 200
    assert 'type="password"' not in response.text
    assert "Set-Cookie" not in response.headers


def test_setac_callback_works_without_login():
    client = Client(application, Response)
    response = client.post(
        "/setac-2026/_dash-update-component",
        json={
            "output": "forcing-chart.figure",
            "outputs": {"id": "forcing-chart", "property": "figure"},
            "inputs": [{"id": "forcing-horizon", "property": "value", "value": 2300}],
            "state": [],
            "changedPropIds": ["forcing-horizon.value"],
        },
    )
    assert response.status_code == 200
    assert response.json["response"]["forcing-chart"]["figure"]["data"]
    assert client.get("/setac-2026/health").json["core_slides"] == CORE_COUNT
    assert client.get("/").status_code == 200
    assert client.get("/lca-time/").status_code == 200


def test_standalone_password_gate_redirects_to_local_root():
    from portal.auth import PresentationPasswordGate
    from werkzeug.security import generate_password_hash

    gate = PresentationPasswordGate(
        Response("private slides"),
        presentation_id="test",
        title="Test deck",
        password_hash=generate_password_hash("test-password"),
        mount_path="/",
    )
    client = Client(gate, Response)
    assert client.get("/").status_code == 401
    response = client.post("/", data={"password": "test-password"})
    assert response.headers["Location"] == "/"
    assert client.get("/presenter").text == "private slides"
    # Public password hashes cannot be used as bearer cookies.
    client.set_cookie("premise_presentation_test", gate.password_hash)
    assert client.get("/").status_code == 401


def test_mounted_app_and_presenter():
    client = Client(application, Response)
    for path in (
        "/",
        "/presenter",
        "/health",
        "/_dash-layout",
        "/_dash-dependencies",
        "/assets/styles.css",
        "/assets/presentation.js",
        "/shared/styles.css",
        "/shared/psi-mark.svg",
        "/shared/cover-iam-trajectories.svg",
        "/shared/case-pathways.svg",
        "/shared/pik-logo.png",
        "/shared/premise-logo.png",
        "/shared/trails-logo.png",
        "/assets/trails-annual-matrices.svg",
        "/assets/trails-temporal-routing.svg",
        "/system-flows.svg",
    ):
        assert client.get("/setac-2026" + path).status_code == 200
    assert "/setac-2026/_dash-component-suites/" in client.get("/setac-2026/").text
    assert (
        client.get("/setac-2026/shared/styles.css").data
        == client.get("/lca-time/assets/styles.css").data
    )
    assert client.get("/setac-2026/shared/../app.py").status_code == 404


def test_default_pdf_is_complete_main_talk_without_sensitive_backup_topic():
    assert CORE_COUNT == 12
    assert sum(slide["seconds"] for slide in SLIDES) == 625  # 1:35 buffer in 12 min.
    deck = pdf_deck()
    assert len(deck) == 12
    assert len(pdf_deck(True)) == len(ALL_SLIDES) == 14
    content = repr(deck)
    assert "BECCS sensitivity to additional forest-carbon losses" not in content
    assert "Data sources and model versions" in repr(deck[-1])
    for slide in (deck[-2], deck[-1]):
        assert "Horizon Europe" in repr(slide)
        assert "UPTAKE" in repr(slide)
        assert "101081521" in repr(slide)
    assert "pulse-window" not in content  # Static results need no control interaction.
    assert "context-indicator" not in content
    assert "context-region" not in content
    assert "mix-pathway" not in content
    assert "mix-material-sector" not in content
    assert "temporal-view" not in content
    assert "2100" in content and "2300" in content
    assert "−" in content


def test_temporal_presentation_preserves_full_inventory_totals():
    from apps.setac_2026.figures import BECCS_TEMPORAL_GROUPS, DACCS_TEMPORAL_PRODUCTS

    figure = temporal_figure()
    for case in CASES:
        traces = [
            trace
            for trace in figure.data
            if trace.meta["case"] == case and trace.stackgroup
        ]
        assert sum(sum(trace.y) for trace in traces) == pytest.approx(
            results.cohort_temporal_total(case, "per_tonne")
        )
        # Category stacking preserves both signs in every year, including
        # upstream contributions outside the requested 2000-onward view.
        raw = results.cohort_temporal_score_series(case, "per_tonne")
        energy = [row for row in results.energy_flow_rows() if row["case"] == case]
        for sign in (-1, 1):
            expected = {}
            plotted = {}
            for label, series in raw:
                category = (
                    BECCS_TEMPORAL_GROUPS[label]
                    if case == "BECCS"
                    else DACCS_TEMPORAL_PRODUCTS[label.split(" | ")[1]]
                )
                if category == "Energy":
                    continue
                for year, value in series:
                    if value * sign > 0:
                        expected[year] = expected.get(year, 0.0) + value
            for row in energy:
                if int(row["sign"]) == sign:
                    year = int(row["impact_year"])
                    expected[year] = expected.get(year, 0.0) + float(
                        row["score_per_net_tonne_kg_co2eq"]
                    )
            for trace in traces:
                if trace.meta["sign"] != sign:
                    continue
                for year, value in zip(trace.x, trace.y, strict=True):
                    assert value * sign >= 0
                    plotted[year] = plotted.get(year, 0.0) + value
            for year in set(plotted) | set(expected):
                assert plotted.get(year, 0) == pytest.approx(expected.get(year, 0))
            # Both positive and negative stack extrema must remain visible.
            lower, upper = figure.layout.yaxis.range
            assert all(lower <= value <= upper for value in plotted.values())
        uptake = sum(sum(t.y) for t in traces if t.name == "Uptake")
        expected_uptake = sum(
            value
            for label, series in raw
            if label == "Forest regrowth" or " | carbon dioxide, captured | " in label
            for _, value in series
        )
        assert uptake == pytest.approx(expected_uptake)
    assert figure.layout.xaxis.range == (2000, temporal_years()[-1])
    assert figure.layout.xaxis2.range == figure.layout.xaxis.range
    raw_years = [
        int(row["impact_year"]) for row in results.cohort_temporal_score_rows()
    ]
    assert min(figure.data[0].x) <= min(raw_years)
    assert max(figure.data[0].x) >= max(raw_years)


@pytest.mark.parametrize("case", CASES)
def test_energy_flow_signs_close_to_published_annual_root_scores(case):
    grouped = {}
    for row in results.energy_flow_rows():
        if row["case"] != case:
            continue
        value = float(row["score_per_net_tonne_kg_co2eq"])
        assert value * int(row["sign"]) > 0
        key = row["root_activity_index"], row["impact_year"]
        grouped[key] = grouped.get(key, 0.0) + value
    root_ids = {root for root, year in grouped}
    expected = {}
    for row in results.cohort_temporal_score_rows():
        if row["case"] == case and row["root_activity_index"] in root_ids:
            key = row["root_activity_index"], row["impact_year"]
            expected[key] = expected.get(key, 0.0) + float(
                row["score_per_net_tonne_kg_co2eq"]
            )
    assert root_ids
    for key in grouped.keys() | expected.keys():
        assert grouped.get(key, 0) == pytest.approx(expected.get(key, 0), abs=2e-6)
    figure = temporal_figure()
    assert {"Energy (+)", "Energy (−)"} <= {t.name for t in figure.data if t.showlegend}


def test_temporal_cumulative_gwp_closes_and_includes_earlier_inventory():
    figure = temporal_figure()
    cumulative = [t for t in figure.data if t.meta["category"] == "cumulative"]
    assert len(cumulative) == 2
    for trace, case, axis in zip(cumulative, CASES, ("y2", "y4"), strict=True):
        assert trace.meta["case"] == case
        assert trace.yaxis == axis
        assert not trace.stackgroup
        raw = results.cohort_temporal_score_series(case, "per_tonne")
        annual = {}
        for _, series in raw:
            for year, value in series:
                annual[year] = annual.get(year, 0) + value
        previous = 0
        for year, total in zip(trace.x, trace.y, strict=True):
            assert total - previous == pytest.approx(annual.get(year, 0))
            previous = total
        assert trace.y[-1] == pytest.approx(
            results.cohort_temporal_total(case, "per_tonne")
        )
        assert dict(zip(trace.x, trace.y))[2000] == pytest.approx(
            sum(value for year, value in annual.items() if year <= 2000)
        )
    assert figure.layout.yaxis2.range == figure.layout.yaxis4.range
    annual_range = figure.layout.yaxis.range
    cumulative_range = figure.layout.yaxis2.range
    assert annual_range[0] / annual_range[1] == pytest.approx(
        cumulative_range[0] / cumulative_range[1]
    )


def test_temporal_view_switch_preserves_all_values_and_scales():
    stacked = update_temporal("stacked")
    unstacked = update_temporal("unstacked")
    assert unstacked.layout.meta["view"] == "unstacked"
    assert update_temporal(None).layout.meta["view"] == "stacked"
    for first, second in zip(stacked.data, unstacked.data, strict=True):
        assert tuple(first.x) == tuple(second.x)
        assert tuple(first.y) == tuple(second.y)
        assert first.yaxis == second.yaxis
        assert not second.stackgroup
        if first.meta["category"] != "cumulative":
            assert first.stackgroup
            assert second.fill == "none"
    for axis in ("xaxis", "xaxis2", "yaxis", "yaxis2", "yaxis3", "yaxis4"):
        assert stacked.layout[axis].range == unstacked.layout[axis].range


@pytest.mark.parametrize("case", CASES)
def test_required_removal_reaches_negative_one_tonne_in_each_metric(case):
    amounts = removal_requirements(case)
    assert all(amount > 0 for amount in amounts.values())
    assert amounts["current_static"] * static_score(
        case, "SSP2-NPi", 2025
    ) == pytest.approx(-1000)
    assert amounts["prospective_static"] * static_score(
        case, "SSP2-PkBudg1000", 2030
    ) == pytest.approx(-1000)
    assert amounts["pulse"] * results.cohort_co2_pulse_equivalent(
        case, "radiative forcing", 2020, 2100, reference_year=2030
    ) == pytest.approx(-1000)


def test_prospective_stacks_preserve_each_snapshot_and_sign():
    figure = prospective_figure()
    plotted = {}
    nets = {}
    for trace in figure.data:
        for key, value in zip(trace.customdata, trace.y, strict=True):
            key = tuple(key)
            if trace.type == "bar":
                positive, negative = plotted.setdefault(key, [0, 0])
                plotted[key] = [positive + max(0, value), negative + min(0, value)]
            else:
                assert trace.mode == "markers"
                nets[key] = value
    assert len(plotted) == len(nets) == 12
    for (case, pathway, year), (positive, negative) in plotted.items():
        treatment = (
            "not applicable"
            if case == "DACCS"
            else "new CHP+CCS vs standing forest and Northern European energy"
        )
        raw = results.static_activity_contributions_per_net_tonne(
            case, pathway, year, treatment
        )
        assert positive == pytest.approx(sum(max(0, value) for _, value in raw))
        assert negative == pytest.approx(sum(min(0, value) for _, value in raw))
        assert positive + negative == pytest.approx(static_score(case, pathway, year))
        assert nets[case, pathway, year] == static_score(case, pathway, year)
    bars = [trace for trace in figure.data if trace.type == "bar"]
    assert figure.layout.barmode == "relative"
    assert {trace.marker.pattern.shape for trace in bars} == {"", "/"}


@pytest.mark.parametrize("sector", MIX_SECTORS)
@pytest.mark.parametrize("pathway", PATHWAYS)
def test_mix_charts_preserve_regional_market_shares(sector, pathway):
    figure = mix_figure(sector, pathway)
    assert MIX_YEARS == (2025, 2030, 2035, 2040, 2045, 2050)
    for trace in figure.data:
        assert trace.x == tuple(str(year) for year in MIX_YEARS)
    for i, year in enumerate(MIX_YEARS):
        expected = sector_mix(sector, pathway, year)
        if year in SNAPSHOT_YEARS:
            assert expected == dict(results.scenario_sector_mix(sector, pathway, year))
        assert sum(trace.y[i] for trace in figure.data) == pytest.approx(1)
        major = set()
        for trace in figure.data:
            assert trace.y[i] >= 0
            if trace.name != "Other":
                major.add(trace.name)
                assert trace.y[i] == expected[trace.name]
        remainder = next(
            (trace.y[i] for trace in figure.data if trace.name == "Other"), 0
        )
        assert remainder == pytest.approx(
            sum(v for k, v in expected.items() if k not in major)
        )
    assert {r["location"] for r in sector_mix_rows()} == {"ENC"}


def test_mix_controls_change_scenario_and_material_together():
    for pathway in PATHWAYS:
        for material in ("Steel", "Cement clinker", "Truck transport"):
            figures = update_mixes(pathway, material)
            assert [fig.layout.meta["sector"] for fig in figures] == [
                "Electricity",
                "District heat",
                material,
            ]
            assert all(fig.layout.meta["pathway"] == pathway for fig in figures)


def test_static_stacks_close_to_reviewed_totals_and_preserve_attribution():
    figure = static_figure()
    bars = [trace for trace in figure.data if trace.type == "bar"]
    totals = next(trace for trace in figure.data if trace.type == "scatter")
    assert figure.layout.barmode == "relative"
    for i, case in enumerate(CASES):
        assert sum(trace.y[i] for trace in bars) == pytest.approx(static_score(case))
        assert totals.y[i] == static_score(case)
        assert any(trace.y[i] > 0 for trace in bars)
        assert any(trace.y[i] < 0 for trace in bars)

    # Distinguish direct DAC removal from its upstream biogenic credit, and
    # preserve the explicit BECCS regrowth/stack attribution.
    by_name = {trace.name: trace.y for trace in bars}
    beccs = results.process_step_attribution()["BECCS"][
        "process_groups_kg_co2eq_per_net_tonne"
    ]
    assert by_name["Forest regrowth"][0] == beccs["Forest regrowth"]
    assert (
        by_name["Residual stack emissions"][0]
        == beccs["Residual biogenic stack emissions"]
    )
    assert by_name["Direct air capture"][1] == pytest.approx(-1028.8065671920776)
    assert by_name["Upstream biogenic uptake"][1] == pytest.approx(-420.8362769932267)


def test_forcing_preserves_stored_response_and_units():
    figure = forcing_figure()
    curves = [trace for trace in figure.data if trace.name in CASES]
    for case, trace in zip(CASES, curves, strict=True):
        plotted = dict(zip(trace.x, trace.y, strict=True))
        expected = results.cohort_fair_total_series(case, "radiative forcing", "total")
        for year, value in expected:
            assert plotted[year] == pytest.approx(value * 1e12)
        assert trace.x[0] == 1940.5 and trace.x[-1] == 2299.5
        assert trace.y[-1] < 0  # Never append an artificial zero at the horizon.
        assert min(trace.y) >= figure.layout.yaxis.range[0]
        assert max(trace.y) <= figure.layout.yaxis.range[1]


@pytest.mark.parametrize("metric", ["radiative forcing", "temperature anomaly"])
def test_total_response_quantiles_share_exact_times_and_are_ordered(metric):
    for case in CASES:
        series = [
            results.cohort_fair_total_series(case, metric, "total", q)
            for q in (2.5, 50, 97.5)
        ]
        assert all(len(s) == 360 for s in series)
        for low, median, high in zip(*series, strict=True):
            assert low[0] == median[0] == high[0]
            assert low[1] <= median[1] <= high[1]


@pytest.mark.parametrize("end", [2050, 2100, 2140, 2300])
def test_pulse_values_use_configuration_first_grid(end):
    figure, cards, *_ = update_pulse([2020, 2030, end])
    assert len(cards) == 2
    for i, case in enumerate(CASES):
        expected = results.cohort_co2_pulse_equivalent(
            case,
            "radiative forcing",
            2020,
            end,
            reference_year=2030,
        )
        assert pulse_value(case, end) == expected
        assert figure.data[2 * i + 1].y[0] == expected
    # Corrected signed uptake removes the former ranking reversal at 2300.
    assert pulse_value("BECCS", 2100) > pulse_value("DACCS", 2100)
    assert pulse_value("BECCS", 2300) > pulse_value("DACCS", 2300)
    assert pulse_value("BECCS", 2300) - pulse_value("DACCS", 2300) < (
        pulse_value("BECCS", 2100) - pulse_value("DACCS", 2100)
    )


def test_context_extract_retains_source_values_and_gaps():
    from apps.setac_2026.scripts.extract_scenario_context import extract_rows

    assert scenario_context_rows() == tuple(extract_rows())
    assert not any(
        row["indicator"] == "GMST" and row["region"] == "ENC"
        for row in scenario_context_rows()
    )
    figure = scenario_context_figure("CO2", "ENC")
    assert max(figure.data[0].x) == 2090  # Missing source value is not filled.
    assert figure.data[1].y[-1] == pytest.approx(-84.0969479)  # t -> Mt
    world = scenario_context_figure("CO2", "World")
    assert world.data[0].y[-1] == pytest.approx(27.9458915866)  # t -> Gt


@pytest.mark.parametrize(
    "indicator,region,scale",
    [
        ("GMST", "World", 1),
        ("CO2", "World", 1e-9),
        ("CO2", "ENC", 1e-6),
        ("Population", "World", 1e-3),
        ("Population", "ENC", 1),
    ],
)
def test_context_controls_preserve_units_and_scenarios(indicator, region, scale):
    figure, options, selected, _ = update_context(indicator, region, PATHWAYS[0])
    assert selected == region
    for trace, pathway in zip(figure.data, PATHWAYS, strict=True):
        expected = {
            int(row["year"]): float(row["value"]) * scale
            for row in scenario_context_rows()
            if (row["indicator"], row["region"], row["pathway"])
            == (indicator, region, pathway)
        }
        assert dict(zip(trace.x, trace.y)) == pytest.approx(expected)
    assert figure.layout.meta["pathway"] == PATHWAYS[0]
    assert options[1]["disabled"] == (indicator == "GMST")


def test_gmst_cannot_be_mislabelled_as_regional_temperature():
    figure, options, region, note = update_context("GMST", "ENC", PATHWAYS[1])
    assert region == figure.layout.meta["region"] == "World"
    assert options[1]["disabled"] and "global" in note
    with pytest.raises(ValueError, match="global"):
        scenario_context_figure("GMST", "ENC")


@pytest.mark.parametrize(
    "window",
    [
        [2020, 2030, 2050],
        [2020, 2030, 2100],
        [2000, 2010, 2100],
        [2020, 2040, 2140],
        [2050, 2060, 2300],
        [2285, 2295, 2300],
    ],
)
def test_all_pulse_handles_use_the_configuration_first_grid(window):
    figure, cards, config, labels, comparison, takeaway, actual = update_pulse(window)
    assert actual == window
    start, reference, end = actual
    for i, case in enumerate(CASES):
        for year, value in zip(figure.data[2 * i].x, figure.data[2 * i].y):
            assert value == results.cohort_co2_pulse_equivalent(
                case, "radiative forcing", start, year, reference_year=reference
            )
        assert figure.data[2 * i + 1].y[0] == pulse_value(
            case, end, start=start, reference=reference
        )
        score = figure.data[2 * i + 1].y[0]
        sentence = repr(takeaway[i])
        assert case in sentence
        assert f"{start}–{end}" in sentence and f"in {reference}" in sentence
        assert f"{abs(score) / 1000:.3g} tonnes of CO₂" in sentence
        assert ("cooling effect" in sentence) == (score < 0)
        assert ("one-off removal" in sentence) == (score < 0)
        assert ("warming effect" in sentence) == (score > 0)
        assert ("one-off emission" in sentence) == (score > 0)
    assert str(start) in repr(config) and str(reference) in repr(labels)
    assert ("—" in repr(comparison)) == (reference >= 2100)


@pytest.mark.parametrize("window", [None, [], [2300, 2000, 2000], [1990, 2000, 2000]])
def test_pulse_selection_keeps_reference_strictly_inside_window(window):
    *_, actual = update_pulse(window)
    start, reference, end = actual
    assert 2000 <= start < reference < end <= 2300
    assert all(year % 5 == 0 for year in actual)
