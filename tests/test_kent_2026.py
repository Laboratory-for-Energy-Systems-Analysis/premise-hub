from __future__ import annotations

import hashlib
import pytest

from apps.kent_2026 import results
from apps.kent_2026.app import ALL_SLIDES, CORE_COUNT, graph_count, pdf_deck, server
from apps.kent_2026.deck import SLIDES, render_slide
from apps.kent_2026.figures import annual_stage_figure, decision_matrix_figure


def test_deck_contract():
    assert CORE_COUNT == 12
    assert len(ALL_SLIDES) == 12
    assert sum(slide["seconds"] for slide in SLIDES) <= 35 * 60
    assert all(slide["cue"] and slide["notes"] for slide in ALL_SLIDES)


def test_health_and_presenter_routes():
    client = server.test_client()
    assert client.get("/health").get_json() == {"status": "ok", "core_slides": 12, "backup_slides": 0}
    response = client.get("/presenter")
    assert response.status_code == 200
    assert b"21:45" in response.data


def test_runtime_artifact_hash_and_categories():
    manifest = results.manifest()
    path = results.DATA_DIR / "results.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest["results_sha256"]
    landscape = results.DATA_DIR / "slide10_landscape.json"
    assert hashlib.sha256(landscape.read_bytes()).hexdigest() == manifest["slide10_landscape_sha256"]
    categories = results.ef_categories()
    assert len(categories) == 25
    assert {item["category"] for item in categories} >= {"climate change", "particulate matter formation"}


def test_bev_profile_uses_calendar_year_electricity():
    profile = results.profile(cohort=2025, powertrain="BEV")
    climate = profile["annual"]["climate change"]
    assert profile["electricity"] == "geco-2025-reference"
    assert climate["2025"]["use"] > climate["2030"]["use"] > climate["2040"]["use"]
    assert "use" not in climate["2023"]
    assert "use" not in climate["2024"]


def test_slide6_mobility_comparison_has_common_scope_and_real_scores():
    comparison = results.mobility_comparison()
    assert comparison["scope"]["year"] == 2025
    assert comparison["scope"]["country"] == "US"
    assert [family["key"] for family in comparison["families"]] == [
        "two-wheelers", "cars", "buses", "trucks"
    ]
    assert all(
        option["value"] > 0
        for family in comparison["families"]
        for option in family["options"]
        if option["value"] is not None
    )
    assert all(len(family["candidates"]) >= 5 for family in comparison["families"])
    for family in comparison["families"]:
        assert all(candidate["total"] > 0 for candidate in family["candidates"])
        assert all(
            sum(candidate["contributions"].values()) == pytest.approx(candidate["total"], abs=.01)
            for candidate in family["candidates"]
        )
    bus = next(family for family in comparison["families"] if family["key"] == "buses")
    assert {candidate["label"] for candidate in bus["candidates"]} >= {"Depot", "Opp.", "Trolley"}
    sensitivity = comparison["electricity_sensitivity"]
    assert sensitivity["low_intensity"] < sensitivity["reference_intensity"] < sensitivity["high_intensity"]
    synthetic = next(item for item in sensitivity["series"] if item["powertrain"] == "SYNTHETIC")
    assert synthetic["high_score"] > 10 * synthetic["low_score"]


def test_owner_paths_share_history_and_service():
    case = results.ownership_case()
    assert case["valid"]
    for category in ("climate change", "particulate matter formation"):
        keep = results.annual_totals(case["keep"], category)
        replace = results.annual_totals(case["replace"], category)
        assert keep[2019] == pytest.approx(replace[2019])
        assert keep[2020] == pytest.approx(replace[2020])
    assert case["replace"]["cohorts"][0]["transferred"] is True
    assert case["keep"]["cohorts"][-1]["last_use"] == 2060
    assert case["replace"]["cohorts"][-1]["last_use"] == 2060
    for path in ("keep", "replace"):
        assert set(case[path]["service"].values()) == {12_000.0}
        assert sum(case[path]["service"].values()) == 12_000 * 41


def test_baseline_vehicle_changes_follow_mileage_and_calendar_convention():
    case = results.ownership_case(
        decision_year=2026,
        annual_km=12_000,
        lifetime_km=200_000,
        end_year=2060,
    )
    keep = case["keep"]["cohorts"]
    replace = case["replace"]["cohorts"]

    assert [(item["cohort"], item["last_use"], item["service_km"]) for item in keep] == [
        (2020, 2036, 200_000.0),
        (2036, 2053, 200_000.0),
        (2053, 2060, 92_000.0),
    ]
    assert [(item["cohort"], item["last_use"], item["service_km"]) for item in replace] == [
        (2020, 2026, 84_000.0),
        (2027, 2043, 200_000.0),
        (2043, 2060, 200_000.0),
        (2060, 2060, 8_000.0),
    ]


def test_replacement_vehicle_specs_show_cohort_development():
    specs = results.replacement_vehicle_specs()
    vehicles = specs["vehicles"]
    assert [item["year"] for item in vehicles] == [2020, 2027, 2036, 2043, "2053+"]
    future = vehicles[1:]
    assert future[-1]["battery_kwh"] > future[0]["battery_kwh"]
    assert future[-1]["energy_value"] < future[0]["energy_value"]
    assert future[-1]["mass_kg"] < future[0]["mass_kg"]


def test_annual_stage_figure_splits_keep_and_replace_on_shared_timeline():
    figure = annual_stage_figure()
    assert len(figure.data) == 10
    assert sum(trace.showlegend is True for trace in figure.data) == 5
    assert {trace.x[0] for trace in figure.data} == {2018}
    assert figure.layout.xaxis.matches == "x2"
    assert figure.layout.yaxis.range == figure.layout.yaxis2.range


def test_cumulative_summary_includes_full_history_and_baseline_crossing():
    case = results.ownership_case()
    summary = results.cumulative_summary(case)
    assert summary["break_even_year"] == 2034
    assert summary["keep_2060"] / 1000 == pytest.approx(109.799, abs=.001)
    assert summary["replace_2060"] / 1000 == pytest.approx(103.084, abs=.001)
    assert summary["delta_2060"] / 1000 == pytest.approx(-6.715, abs=.001)


def test_slide9_sensitivity_cube_is_complete_and_baseline_matches():
    cube = results.slide9_sensitivity()
    assert len(cube["configurations"]) == 256
    baseline = results.cumulative_sensitivity()
    assert baseline["break_even_year"] == 2034
    assert baseline["delta_2060_t"] == pytest.approx(-6.715, abs=.001)
    assert len(baseline["years"]) == len(baseline["keep_t"]) == len(baseline["replace_t"]) == 43
    particulate = results.cumulative_sensitivity(indicator="particulate matter formation")
    assert particulate["break_even_year"] is None
    assert particulate["delta_2060_t"] == pytest.approx(.5949, abs=.0001)
    assert particulate["display_unit"] == "10⁻³ disease incidences"


def test_decision_maps_are_precomputed_and_signed():
    for state in ("baseline", "small_bev", "large_bev", "short_life", "long_life", "transition", "rapid"):
        data = results.decision_map(state)
        assert len(data["decision_years"]) == 16
        assert data["annual_km"] == [5_000, 12_000, 20_000]
        assert len(data["values"]["climate change"]) == 3
    baseline = results.decision_map("baseline")["values"]["climate change"]
    finite = [value for row in baseline for value in row if value is not None]
    assert finite
    assert min(finite) < max(finite)


def test_slide10_landscape_retains_signed_values_and_decision_matrix():
    data = results.slide10_landscape()
    assert data["dimensions"]["intensity_g_per_kwh"] == [50, 150, 300, 450, 650]
    state = results.landscape_state()
    assert state["counts"] == {"keep": 53, "replace": 180, "ties_hidden": 57, "invalid": 30}
    assert {point["outcome"] for point in state["points"]} == {"keep", "replace", "tie"}
    assert any(abs(point["delta_t"]) < 2 for point in state["points"])
    figure = decision_matrix_figure()
    assert len(figure.data) == 1
    assert figure.data[0].type == "heatmap"
    assert len(figure.data[0].z) == 4
    assert len(figure.data[0].z[0]) == 5


def test_fuel_and_electricity_sensitivities_are_owner_level_cases():
    fuel_cases = (
        ("BEV", "baseline"),
        ("ICEV-p", "baseline"),
        ("ICEV-p", "fuel_e85"),
        ("ICEV-p", "fuel_synthetic"),
        ("FCEV", "fuel_hydrogen"),
    )
    deltas = []
    for successor, successor_case in fuel_cases:
        case = results.ownership_case(
            successor=successor,
            successor_case=successor_case,
        )
        assert case["valid"]
        assert case["keep"]["cohorts"][-1]["last_use"] == 2060
        assert case["replace"]["cohorts"][-1]["last_use"] == 2060
        deltas.append(results.delta(case, "climate change"))
    assert len({round(value, 6) for value in deltas}) == len(deltas)

    electricity = [
        results.delta(results.ownership_case(case=case), "climate change")
        for case in ("baseline", "electricity_ndc", "electricity_15c")
    ]
    assert len({round(value, 6) for value in electricity}) == 3


def test_all_slides_render():
    for index in range(len(ALL_SLIDES)):
        component = render_slide(index, print_mode=True)
        assert component.id == f"slide-{index}"


def test_pdf_deck_has_no_live_control_ids_and_stable_graph_count():
    slides = pdf_deck()
    assert len(slides) == CORE_COUNT
    rendered = repr(slides)
    assert "map-state" not in rendered
    assert "interactive-map" not in rendered
    assert sum(graph_count(slide) for slide in slides) == 5

