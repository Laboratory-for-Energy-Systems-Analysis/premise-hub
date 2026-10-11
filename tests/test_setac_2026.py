from __future__ import annotations

import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from apps.lca_time.workshop import results
from apps.setac_2026.app import pdf_deck, update_context, update_mixes, update_pulse
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
)
from portal.wsgi import application


@pytest.mark.parametrize(
    "path",
    (
        "/",
        "/presenter",
        "/health",
        "/_dash-layout",
        "/_dash-dependencies",
        "/_dash-update-component",
        "/assets/styles.css",
        "/shared/case-pathways.svg",
        "/system-flows.svg",
    ),
)
def test_setac_routes_require_password(path):
    client = Client(application, Response)
    response = client.get("/setac-2026" + path)
    assert response.status_code == 401
    assert 'type="password"' in response.text
    assert "test-setac-password" not in response.text
    assert response.headers["Cache-Control"] == "no-store"
    if path == "/_dash-update-component":
        assert client.post("/setac-2026" + path, json={}).status_code == 401


def test_setac_password_login_and_cookie_scope():
    client = Client(application, Response)
    assert client.post("/setac-2026/", data={"password": "wrong"}).status_code == 401
    assert client.post("/setac-2026/", data={"password": "错误"}).status_code == 401
    response = client.post(
        "/setac-2026/",
        data={"password": "test-setac-password"},
        headers={"X-Forwarded-Proto": "https"},
    )
    assert response.status_code == 303
    assert response.headers["Location"] == "/setac-2026/"
    cookie = response.headers["Set-Cookie"]
    for attribute in ("HttpOnly", "Secure", "SameSite=Lax", "Path=/setac-2026"):
        assert attribute in cookie
    assert client.get("/setac-2026/health").json["core_slides"] == CORE_COUNT
    client.set_cookie(
        "premise_presentation_setac_time_explicit_lca_2026_10_19",
        "forged",
        path="/setac-2026",
    )
    assert client.get("/setac-2026/").status_code == 401
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
    assert (
        client.post(
            "/setac-2026/", data={"password": "test-setac-password"}
        ).status_code
        == 303
    )
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
    assert sum(slide["seconds"] for slide in SLIDES) == 600
    deck = pdf_deck()
    assert len(deck) == 12
    assert len(pdf_deck(True)) == len(ALL_SLIDES) == 14
    content = repr(deck)
    assert "BECCS sensitivity to additional forest-carbon losses" not in content
    assert "Data sources and model versions" in repr(deck[-1])
    assert "pulse-window" not in content  # Static results need no control interaction.
    assert "context-indicator" not in content
    assert "context-region" not in content
    assert "mix-pathway" not in content
    assert "mix-material-sector" not in content
    assert "2100" in content and "2300" in content
    assert "−" in content


def test_temporal_presentation_preserves_full_inventory_totals():
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
        for sign in (-1, 1):
            expected = {}
            plotted = {}
            for _, series in raw:
                for year, value in series:
                    if value * sign > 0:
                        expected[year] = expected.get(year, 0.0) + value
            for trace in traces:
                if trace.meta["sign"] != sign:
                    continue
                for year, value in zip(trace.x, trace.y, strict=True):
                    assert value * sign >= 0
                    plotted[year] = plotted.get(year, 0.0) + value
            for year in set(plotted) | set(expected):
                assert plotted.get(year, 0) == pytest.approx(expected.get(year, 0))
        uptake = sum(sum(t.y) for t in traces if t.name == "Uptake")
        expected_uptake = sum(
            value
            for label, series in raw
            if label == "Forest regrowth" or " | carbon dioxide, captured | " in label
            for _, value in series
        )
        assert uptake == pytest.approx(expected_uptake)
    assert figure.layout.xaxis.range == (2000, 2140)
    assert figure.layout.xaxis2.range == (2000, 2140)
    assert min(figure.data[0].x) <= 1882


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


@pytest.mark.parametrize("case", CASES)
def test_required_removal_reaches_negative_one_tonne_in_each_metric(case):
    amounts = removal_requirements(case)
    assert amounts["gwp100"] > 0
    assert amounts["pulse"] > 0
    assert amounts["gwp100"] * results.cohort_temporal_total(
        case, "per_tonne"
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
    for case, trace in zip(CASES, figure.data, strict=True):
        plotted = dict(zip(trace.x, trace.y, strict=True))
        expected = results.cohort_fair_total_series(
            case, "radiative forcing", "process"
        )
        for year, value in expected:
            assert plotted[year] == pytest.approx(value * 1e12)


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
    # The slide's two fixed endpoint rows illustrate a change in comparison.
    assert pulse_value("BECCS", 2100) > pulse_value("DACCS", 2100)
    assert pulse_value("BECCS", 2300) < pulse_value("DACCS", 2300)


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
    assert str(start) in repr(config) and str(reference) in repr(labels)
    assert ("—" in repr(comparison)) == (reference >= 2100)


@pytest.mark.parametrize("window", [None, [], [2300, 2000, 2000], [1990, 2000, 2000]])
def test_pulse_selection_keeps_reference_strictly_inside_window(window):
    *_, actual = update_pulse(window)
    start, reference, end = actual
    assert 2000 <= start < reference < end <= 2300
    assert all(year % 5 == 0 for year in actual)
