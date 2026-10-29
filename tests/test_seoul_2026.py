from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from apps.seoul_2026.app import (
    pdf_deck,
    update_erw,
    update_response,
    update_pulse,
)
from apps.seoul_2026.comparison import (
    static_panels,
    time_panels,
    forcing_panels,
    snapshot,
    cement_scores,
    annual_scores,
    erw_results,
)
from apps.seoul_2026.visuals import CASES
from apps.seoul_2026.deck import (
    ALL_SLIDES,
    CORE_COUNT,
    SLIDES,
    SLIDE_INDEX,
    render_slide,
)
from apps.seoul_2026.erw import NICKEL_KG, dissolution_cdf, temporal_profile
from portal.wsgi import application


def walk(component):
    yield component
    children = getattr(component, "children", None)
    for child in children if isinstance(children, (list, tuple)) else [children]:
        if child is not None:
            yield from walk(child)


@pytest.mark.parametrize("slug", ("daccs", "beccs", "erw", "cement"))
def test_initial_routing_response_omits_level_four(slug):
    from apps.seoul_2026.routing import shallow_route_json, verified_route_path

    full = json.loads(verified_route_path(slug, "json").read_text())
    shallow = json.loads(shallow_route_json(slug))
    assert shallow["loaded_max_depth"] == 3
    assert shallow["metadata"] == full["metadata"]
    assert shallow["nodes"] == [n for n in full["nodes"] if n["depth"] <= 3]
    ids = {n["id"] for n in shallow["nodes"]}
    assert shallow["edges"] == [e for e in full["edges"] if e["source"] in ids and e["target"] in ids]
    assert len(shallow["nodes"]) < len(full["nodes"]) / 3


@pytest.mark.parametrize("slug", ("daccs", "beccs", "erw", "cement"))
def test_routing_exports_preserve_actual_four_level_demand_graphs(slug):
    import hashlib

    folder = Path(__file__).resolve().parents[1] / "apps/seoul_2026/data/routing"
    manifest = json.loads((folder / "manifest.json").read_text())
    raw = (folder / f"{slug}.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == manifest["cases"][slug]["graph_sha256"]
    graph = json.loads(raw)
    meta = graph["metadata"]
    assert meta["routing"]["max_depth"] == 4
    assert meta["routing"]["adaptive_relative_score_cutoff"] is None
    assert meta["nodes"] == len(graph["nodes"])
    assert meta["edges"] == len(graph["edges"])
    nodes = {n["id"]: n for n in graph["nodes"]}
    roots = [n for n in nodes.values() if n["depth"] == 0]
    assert len(roots) == 1
    assert {n["depth"] for n in nodes.values()} == set(range(5))
    assert all("amount" not in n for n in nodes.values())
    adjacency = {}
    for e in graph["edges"]:
        assert e["source"] in nodes and e["target"] in nodes
        assert nodes[e["target"]]["depth"] == nodes[e["source"]]["depth"] + 1
        assert "amount" not in e and "value" not in e
        adjacency.setdefault(e["source"], []).append(e["target"])
    reached, queue = {roots[0]["id"]}, [roots[0]["id"]]
    while queue:
        for child in adjacency.get(queue.pop(), []):
            if child not in reached:
                reached.add(child)
                queue.append(child)
    assert reached == set(nodes)
    assert (folder / f"{slug}.png").read_bytes().startswith(b"\x89PNG")
    if slug == "beccs":
        assert meta["interpolation_end_year_offset"] == 83
        assert meta["years"][1] > 2100
        assert roots[0]["name"].startswith("carbon dioxide, captured and stored")
        assert not any(n["name"] == roots[0]["name"] for n in nodes.values() if n["depth"] > 0)
        heat = [n for n in nodes.values() if n["depth"] == 1 and n["name"] == "market for heat, district or industrial"]
        assert sorted(n["year"] for n in heat) == list(range(2030,2050))
        assert all(any(e["source"] == roots[0]["id"] and e["target"] == n["id"] and e["negative"] for e in graph["edges"]) for n in heat)
    if slug == "cement":
        assert meta["root_amount"] == 1000
        assert "CCS minus" in meta["comparison"]
        assert "October" in meta["background_vintage_note"]
        assert any(e["negative"] for e in graph["edges"])
        assert not any("clinker cohort" in n["name"] for n in nodes.values() if n["depth"] > 0)
        assert meta["structure_review"]["instantaneous_emission_carriers_folded"] > 0
    if slug != "erw":
        review = meta["structure_review"]
        assert review["dated_supplier_demands_equivalent"]
        assert review["max_absolute_numerical_difference"] < 1e-8
        assert review["annual_root_coefficients_checked"]
        assert review["direct_biosphere_profiles_preserved"]
        assert review["emission_carrier_biosphere_equivalent"]


def test_teaching_and_discussion_are_separate_and_fully_timed():
    assert CORE_COUNT == 23
    assert [s["key"] for s in SLIDES[:3]] == ["cover", "about", "why-time"]
    assert not {"coast", "erw-sensitivity", "lenses", "discussion"} & SLIDE_INDEX.keys()
    assert "mechanisms" not in SLIDE_INDEX
    assert sum(s["seconds"] for s in SLIDES if s.get("timing_phase") != "discussion") == 70 * 60
    assert SLIDES[SLIDE_INDEX["thanks"]]["seconds"] == 20 * 60
    assert SLIDES[-1]["key"] == "thanks"
    assert [s["key"] for s in SLIDES if "Discussion pause" in s["phase"]] == [
        "pause-current",
        "pause-future",
        "pause-gwp",
    ]
    assert all(s["notes"] and s["cue"] for s in ALL_SLIDES)


@pytest.mark.parametrize("index", range(len(ALL_SLIDES)))
def test_each_slide_renders_and_print_has_no_callback_identifiers(index):
    assert render_slide(index)
    printed = render_slide(index, print_mode=True)
    assert all(not getattr(c, "id", None) for c in walk(printed))


def test_pdf_defaults_and_backup_pages():
    assert len(pdf_deck()) == CORE_COUNT + 4
    assert len(pdf_deck(True)) == len(ALL_SLIDES) + 4
    pages=[p for p in pdf_deck() if getattr(p,"data-slide-key")=="pulse-equivalence"]
    assert [getattr(p,"data-pulse-view") for p in pages] == ["method","cases"]
    assert "case-equivalence-method" in repr(pages[0])
    assert "case-pulse-equivalence" in repr(pages[1])


def test_process_carousel_and_pdf_preserve_each_technology():
    slide = render_slide(SLIDE_INDEX["supply-chain"])
    panels = [c for c in walk(slide) if getattr(c, "className", "") == "process-panel"]
    assert len(panels) == 4
    assert [p.hidden for p in panels] == [False, True, True, True]
    pages = [p for p in pdf_deck() if getattr(p, "data-slide-key") == "supply-chain"]
    assert len(pages) == 4
    visible = [
        [
            c
            for c in walk(p)
            if getattr(c, "className", "") == "process-panel" and not c.hidden
        ]
        for p in pages
    ]
    assert all(len(p) == 1 for p in visible)
    assert [p[0].children[1].alt for p in visible] == [
        p.children[1].alt for p in panels
    ]
    assert all(not getattr(c, "id", None) for p in pages for c in walk(p))


@pytest.mark.parametrize("duration", [10, 30, 100])
@pytest.mark.parametrize("lag", [0, 1, 5])
@pytest.mark.parametrize("efficiency", [0.5, 0.8, 1])
def test_erw_mass_balance_and_time_direction(duration, lag, efficiency):
    profile = temporal_profile(duration, lag, efficiency)
    assert np.all(profile["uptake_kg"] >= 0)
    assert profile["age"][0] == 1  # No immediate full uptake at deployment.
    assert profile["dissolved"].sum() == pytest.approx(1)
    assert profile["uptake_kg"].sum() == pytest.approx(1000 * efficiency)
    assert profile["nickel_upper_bound_kg"].sum() == pytest.approx(NICKEL_KG)
    no_delay = temporal_profile(duration, 0, efficiency)
    assert np.all(
        np.cumsum(profile["uptake_kg"]) <= np.cumsum(no_delay["uptake_kg"]) + 1e-9
    )
    assert np.abs(profile["tail_kg"]) < 1e-9


def test_erw_horizon_tail_is_retained_and_not_renormalized():
    short = temporal_profile(100, 5, 0.8, years=20)
    long = temporal_profile(100, 5, 0.8, years=500)
    assert short["uptake_kg"].sum() < 800
    assert short["uptake_kg"].sum() + short["tail_kg"] == pytest.approx(800)
    assert short["uptake_kg"] == pytest.approx(long["uptake_kg"][:20])
    assert dissolution_cdf([0, 10], 10) == pytest.approx([0, 1])


def test_erw_controls_change_the_stated_screening_assumptions():
    figures = update_erw(100, 5, 0.5)
    baseline = update_erw(10, 1, 1)
    figure = figures[2]
    assert figure.layout.meta["duration"] == 100
    assert figure.layout.meta["efficiency"] == 0.5
    for i in (0, 1, 3):
        assert figures[i].data[0].y == baseline[i].data[0].y


@pytest.mark.parametrize(
    "render",
    [lambda: static_panels(), lambda: static_panels(True), time_panels, forcing_panels],
)
def test_same_four_cases_in_same_order_across_all_views(render):
    panels = render()
    assert [p.to_plotly_json()["props"]["data-case"] for p in panels.children] == list(
        CASES
    )


def test_cement_uses_its_clinker_reference_at_both_snapshots():
    for year in (2025, 2050):
        ccs, bau = cement_scores(year)
        assert snapshot("Cement + CCS", year) == pytest.approx(ccs - bau)


@pytest.mark.parametrize("pathway", ["SSP2-NPi", "SSP2-PkBudg1000"])
@pytest.mark.parametrize("case", CASES)
def test_three_year_future_bars_close_and_keep_both_scenario_diamonds(case, pathway):
    from apps.seoul_2026.contributions import static_figure

    years = (2025, 2035, 2050)
    fig = static_figure(case, years, co2_terms=True, default_view="activities",
                        pathway=pathway, show_scenarios=True)
    bars = [t for t in fig.data if t.type == "bar"]
    totals = np.sum([np.asarray(t.y, dtype=float) for t in bars], axis=0)
    assert totals == pytest.approx([snapshot(case, y, pathway) for y in years], abs=1e-6)
    assert list(fig.layout.xaxis.ticktext) == ["2025", "2035", "2050"]
    assert fig.layout.meta["bars_pathway"] == pathway
    diamonds = {t.name: t for t in fig.data if t.type == "scatter"}
    for p, name, symbol in (("SSP2-NPi", "NPi net", "diamond-open"),
                             ("SSP2-PkBudg1000", "PkBudg1000 net", "diamond")):
        trace = diamonds[name]
        assert trace.marker.symbol == symbol
        assert list(trace.y) == pytest.approx([snapshot(case, y, p) for y in years[1:]])
        assert [r[0] for r in trace.customdata] == [2035, 2050]
    assert list(diamonds["NPi net"].x) != list(diamonds["PkBudg1000 net"].x)
    assert diamonds["2025 reference net"].y[0] == pytest.approx(snapshot(case, 2025))


def test_new_static_snapshots_reproduce_forward_scores_and_existing_2050_release():
    from apps.seoul_2026.static_scenarios import scenario_results
    from apps.setac_2026.figures import static_score

    for record in scenario_results()["records"]:
        for case, data in record["cases"].items():
            total = sum(r["score"] for r in data["foreground"] + data["suppliers"])
            assert total == pytest.approx(data["forward_static_total"], abs=1e-6)
            if record["year"] == 2050 and case in ("DACCS", "BECCS"):
                assert total == pytest.approx(static_score(case, record["pathway"], 2050), abs=1e-6)
            if case == "ERW":
                assert sum(r["score"] for r in data["foreground"]) == pytest.approx(-1000, abs=1e-6)


def test_future_selector_defaults_and_updates_scores_without_changing_reference():
    from apps.seoul_2026.app import update_future_pathway
    from apps.seoul_2026.contributions import future_comparison

    selector = next(c for c in walk(future_comparison()) if getattr(c, "id", None) == "future-pathway")
    assert selector.value == "SSP2-PkBudg1000"
    for pathway in ("SSP2-NPi", "SSP2-PkBudg1000"):
        updated = update_future_pathway(pathway)
        assert len(updated) == 8
        for fig, case, score in zip(updated[:4], CASES, updated[4:]):
            assert fig.layout.meta["bars_pathway"] == pathway
            assert score.startswith("2050: ")
            assert fig.layout.meta["net_scores"][0] == pytest.approx(snapshot(case, 2025))
    assert all(not getattr(c, "id", None) for c in walk(future_comparison(print_mode=True)))


def test_cement_stored_tonne_basis_reaches_snapshots_inventory_and_climate():
    from apps.ccus_webinar.webinar.release import load_release_bundle
    from apps.seoul_2026.cement_basis import cement_scale
    from apps.seoul_2026.comparison import forcing_series

    # Two snapshots and the full production campaign have different storage
    # yields. Using a snapshot denominator for the entire cohort is incorrect.
    factors = [cement_scale(2025), cement_scale(2050), cement_scale()]
    assert len(set(factors)) == 3
    for year, key in ((2025, "main"), (2050, "2050-SSP2-PkBudg1000")):
        raw = load_release_bundle(key)
        totals = {r["system"]: r["score"] for r in raw.tables["static_totals"]}
        expected = (totals["CCS"] - totals["BAU"]) * cement_scale(year)
        assert snapshot("Cement + CCS", year) == pytest.approx(expected)

    raw = load_release_bundle()
    original = sum(
        r["score"] * (1 if r["system"] == "CCS" else -1)
        for r in raw.tables["temporal_totals"] if r["system"] in ("CCS", "BAU")
    )
    assert sum(v for _, v in annual_scores("Cement + CCS")) == pytest.approx(original * cement_scale())
    climate = {
        (r["system"], float(r["year"])): r["value"]
        for r in raw.tables["fair_responses"]
        if r["metric"] == "radiative_forcing"
        and r["statistic"] in ("q50", "median", "p50")
    }
    for age, value in forcing_series("Cement + CCS"):
        difference = climate["CCS", age + 2035] - climate["BAU", age + 2035]
        assert value == pytest.approx(difference * 1e12 * cement_scale())


def test_formal_equations_are_in_backup_and_iam_visuals_are_reused():
    for i in range(CORE_COUNT):
        assert not any(
            "equation" in (getattr(c, "className", "") or "").split()
            for c in walk(render_slide(i))
        )
    assert "data-reused-from" in repr(render_slide(SLIDE_INDEX["iam"]))
    assert "/workshop/" in repr(render_slide(SLIDE_INDEX["scenario"]))
    assert "equation" in repr(render_slide(CORE_COUNT))


def test_cumulative_views_include_inventory_before_display_window():
    from apps.seoul_2026.contributions import temporal_figure

    annual_ranges,cumulative_ranges=set(),set()
    for case in CASES:
        fig = temporal_figure(case)
        annual_ranges.add(tuple(fig.layout.yaxis.range))
        cumulative_ranges.add(tuple(fig.layout.yaxis2.range))
        line = next(t for t in fig.data if t.name == "Cumulative GWP100")
        assert line.y[-1] == pytest.approx(sum(v for y, v in annual_scores(case)))
        first = next(i for i,age in enumerate(line.x) if age >= -5)
        assert line.y[first] == pytest.approx(sum(v for y,v in annual_scores(case) if y <= line.x[first]))
        assert line.yaxis == "y2"
        low,high=fig.layout.yaxis.range
        low2,high2=fig.layout.yaxis2.range
        assert low2 == -1000
        assert -low/(high-low) == pytest.approx(-low2/(high2-low2))
        start=2035 if case == "Cement + CCS" else 2030
        assert fig.layout.xaxis.ticktext[0] == str(start)
        assert fig.layout.xaxis.ticktext[-1] == str(start+100)
        assert not any(t.name == "Annual net GWP100" for t in fig.data)
        assert fig.layout.meta["case"] == case
        for sign in ("positive","negative"):
            traces=[t for t in fig.data if t.stackgroup==sign]
            stack=np.sum([np.asarray(t.y) for t in traces],axis=0)
            visible=(np.asarray(traces[0].x)>=-5)&(np.asarray(traces[0].x)<=100)
            assert stack[visible].min()>=low
            assert stack[visible].max()<=high
            assert all(t.line.shape=="linear" for t in traces)
        visible=(np.asarray(line.x)>=-5)&(np.asarray(line.x)<=100)
        assert np.asarray(line.y)[visible].min()>=low2
        assert np.asarray(line.y)[visible].max()<=high2
    assert len(annual_ranges)==len(cumulative_ranges)==1


def test_inventory_has_no_view_selector_and_missing_erw_controls_do_not_replace_it():
    from dash.exceptions import PreventUpdate
    assert "inventory-view" not in repr(render_slide(SLIDE_INDEX["inventory"]))
    with pytest.raises(PreventUpdate):
        update_erw(None,None,None)


def test_temporal_cement_carbon_split_retains_roots_and_heat_credit_scope():
    from apps.seoul_2026.contributions import temporal_contributions,TEMPORAL_TYPES
    from apps.seoul_2026.cement_temporal_foreground import kiln_co2_differences

    groups,labels=temporal_contributions("Cement + CCS")
    assert "Direct / avoided emissions" not in labels
    assert "Direct / avoided emissions" not in TEMPORAL_TYPES
    assert "capture" in labels["Capture operation + heat credit"]
    assert "capture" not in labels["Materials + equipment"]
    assert "kiln_fuels" in labels["Fuel + biomass supply"]
    assert sum(sum(v.values()) for (typ,_),v in groups.items() if typ=="Capture operation + heat credit")<0
    assert sum(sum(v.values()) for (typ,_),v in groups.items() if typ=="Materials + equipment")>0
    direct=kiln_co2_differences()
    assert set(direct)==set(range(2035,2065))
    for typ in ("Avoided fossil CO₂","Avoided biogenic CO₂"):
        assert sum(groups[typ,-1].values())<0
        for year,parts in direct.items():
            assert groups[typ,-1][year-2035] == pytest.approx(parts[typ],abs=1e-8)
    bio,_=temporal_contributions("BECCS")
    assert sum(bio["Biogenic uptake",-1].values())<0


def test_daccs_energy_positives_and_negatives_are_visible_without_netting():
    from apps.seoul_2026.contributions import temporal_figure,temporal_contributions
    figure=temporal_figure("DACCS")
    groups,_=temporal_contributions("DACCS")
    traces={t.name:t for t in figure.data}
    positive=traces["Electricity + heat (+)"]
    negative=traces["Electricity + heat (−)"]
    assert positive.stackgroup=="positive" and negative.stackgroup=="negative"
    assert all(v>=0 for v in positive.y) and any(v>0 for v in positive.y)
    assert all(v<=0 for v in negative.y) and any(v<0 for v in negative.y)
    assert sum(positive.y)==pytest.approx(sum(groups["Electricity + heat",1].values()))
    assert sum(negative.y)==pytest.approx(sum(groups["Electricity + heat",-1].values()))
    assert negative.fillpattern.shape=="/"
    from apps.seoul_2026.daccs_energy import signed_energy
    record=signed_energy()
    annual={p["year"]:p for p in record["annual"]}
    # A near-zero annual net must not hide the two opposing contributions.
    assert annual[2042]["positive"]>10
    assert annual[2042]["negative"] < -10
    assert abs(annual[2042]["net"])<.2
    assert record["checks"]["max_annual_source_difference"]<1e-9
    demand=[p["kwh_per_t_stored"] for p in record["electricity_demand"]]
    assert len(demand)==20
    assert max(demand)==pytest.approx(min(demand))


def test_erw_timing_envelope_brackets_reference_without_changing_total_service():
    from apps.seoul_2026.contributions import temporal_figure
    figure=temporal_figure("ERW")
    traces={t.name:t for t in figure.data}
    lower=np.asarray(traces["ERW timing minimum"].y)
    upper=np.asarray(traces["ERW timing maximum"].y)
    reference=np.asarray(traces["Cumulative GWP100"].y)
    assert np.all(lower<=reference+1e-9) and np.all(reference<=upper+1e-9)
    assert (upper-lower).max()>100
    assert lower[-1]==pytest.approx(upper[-1],abs=1e-6)
    assert upper[-1]==pytest.approx(reference[-1],abs=1e-6)
    before=np.asarray(traces["Cumulative GWP100"].x)<0
    assert lower[before]==pytest.approx(upper[before])
    assert traces["ERW timing maximum"].fill=="tonexty"
    assert traces["ERW timing maximum"].yaxis=="y2"
    assert "not a confidence interval" in figure.layout.meta["timing_envelope"]["interpretation"]
    assert figure.layout.meta["timing_envelope"]["upstream"]=="held fixed"


def test_plant_activity_is_scaled_by_whole_lifetime_physical_storage():
    from apps.setac_2026 import results
    from apps.seoul_2026.erw_campaign import campaign_results
    from apps.seoul_2026.contributions import temporal_figure

    for case in ("DACCS","BECCS"):
        rows=[r for r in results.cohort_temporal_score_rows() if r["case"]==case]
        denominators={float(r["denominator_net_stored_tonnes"]) for r in rows}
        assert len(denominators)==1
        denominator=denominators.pop()
        assert denominator>1000
        assert all(float(r["score_total_kg_co2eq"])/denominator ==
                   pytest.approx(float(r["score_per_net_tonne_kg_co2eq"]),abs=1e-10) for r in rows)
        assert sum(float(r["score_total_kg_co2eq"]) for r in rows)/denominator == pytest.approx(
            sum(v for _,v in annual_scores(case)),abs=1e-7)
    campaign=campaign_results()["campaign"]
    assert campaign["annual_rock_kg"]*campaign["years"]==1250
    assert campaign["eventual_gross_uptake_kg"]==1000
    for case in CASES:
        figure=temporal_figure(case)
        assert figure.layout.meta["normalization_tonnes"]==1
        assert figure.layout.meta["normalization_scope"]=="whole operating lifetime"


def test_response_horizon_preserves_case_scales_and_pulse_delay_changes_response():
    near = update_response([2030, 2050])
    far = update_response([2030, 2200])
    default = update_response(None)
    for i, case in enumerate(CASES):
        assert near[i].layout.yaxis.range == far[i].layout.yaxis.range
        assert near[i].layout.meta["case"] == case
        assert near[i].layout.xaxis.range == (2030, 2050)
        assert default[i].layout.xaxis.range == (2030, 2050)
        assert far[i].layout.xaxis.range == (2030, 2200)
        assert near[i].data[0].x == far[i].data[0].x
        assert near[i].data[0].y == far[i].data[0].y
        assert near[i].layout.meta["integrated_forcing"] != far[i].layout.meta["integrated_forcing"]
        assert near[i].layout.meta["project_start"] == (2035 if case == "Cement + CCS" else 2030)
    assert near[-1] == "2030–2050"
    assert max(abs(v) for v in update_pulse(0).data[0].y) == 0
    assert max(update_pulse(50).data[0].y) > 0


def test_integrated_forcing_interpolates_boundaries_and_retains_sign():
    from apps.seoul_2026.comparison import integrated_forcing

    # Known linear functions exercise fractional boundaries between stored years.
    assert integrated_forcing([(0, -1), (1, 1), (2, 3)], .25, 1.75) == pytest.approx(1.5)
    assert integrated_forcing([(0, -3), (1, -1), (2, 1)], .25, 1.75) == pytest.approx(-1.5)
    assert integrated_forcing([(0, -1), (1, 1)], 0, 1) == pytest.approx(0)
    with pytest.raises(ValueError, match="does not cover"):
        integrated_forcing([(0, 1), (1, 2)], 0, 2)


def test_new_erw_calculation_preserves_mass_and_closes_to_static():
    data = erw_results()
    target = next(r["net_kg_co2eq"] for r in data["snapshots"] if r["year"] == 2030)
    assert sum(r["score"] for r in data["routed_temporal"]) == pytest.approx(
        target, abs=1e-3
    )
    assert sum(r["score"] for r in data["temporal"]) == pytest.approx(target, abs=1e-7)
    assert set(data["fair"]) == {"radiative_forcing", "temperature"}
    assert all(
        np.isfinite(r["value"]) for series in data["fair"].values() for r in series
    )


def test_erw_campaign_repeats_physical_batches_without_multiplying_the_service():
    from apps.seoul_2026.erw import campaign_profile

    batch = temporal_profile()
    campaign = campaign_profile()
    assert campaign["uptake_kg"].sum() == pytest.approx(1000)
    assert campaign["dissolved"].sum() == pytest.approx(1)
    assert campaign["nickel_upper_bound_kg"].sum() == pytest.approx(NICKEL_KG)
    # Twenty equally weighted annual batches delay the mean by 9.5 years.
    mean_batch = np.dot(batch["age"],batch["uptake_kg"])/1000
    mean_campaign = np.dot(campaign["age"],campaign["uptake_kg"])/1000
    assert mean_campaign-mean_batch == pytest.approx(9.5)
    assert campaign["uptake_kg"][20:].sum()>0
    short = campaign_profile(duration=100,lag=5,efficiency=.8,years=20)
    assert short["uptake_kg"].sum()+short["tail_kg"] == pytest.approx(800)
    assert campaign_profile(campaign_years=1)["uptake_kg"] == pytest.approx(batch["uptake_kg"])


def test_erw_campaign_calculation_matches_independent_annual_static_lcas():
    from apps.seoul_2026.erw_campaign import campaign_results
    from apps.seoul_2026.erw import campaign_profile
    from apps.seoul_2026.comparison import forcing_series

    data=campaign_results()
    assert data["campaign"]["start"] == 2030
    assert data["campaign"]["end"] == 2049
    assert data["campaign"]["total_rock_kg"] == 1250
    assert data["campaign"]["annual_rock_kg"]*20 == 1250
    assert [r["year"] for r in data["annual_static_checks"]] == list(range(2030,2050))
    assert sum(v for _,v in annual_scores("ERW")) == pytest.approx(
        sum(r["total"] for r in data["annual_static_checks"]),abs=1e-3)
    electricity=next(r for r in data["temporal_roots"] if "electricity" in r["activity"])
    # Complete supplier effects can precede or outlast the operating demands.
    electricity_by_age={p["age"]:p["score"] for p in electricity["series"]}
    assert set(range(20)) <= electricity_by_age.keys()
    assert electricity_by_age[0] != pytest.approx(electricity_by_age[19])
    uptake=next(r for r in data["temporal_roots"] if "20-year campaign" in r["activity"])
    physical=dict(zip(campaign_profile()["age"],campaign_profile()["uptake_kg"]))
    for point in uptake["series"]:
        assert point["score"] == pytest.approx(-physical.get(point["age"],0),abs=1e-5)
    assert data["fair_input_hashes"] == erw_results()["fair_input_hashes"]
    assert forcing_series("ERW") == [(r["year"]-2030,r["value"]*1e12)
        for r in data["fair"]["radiative_forcing"]]
    assert data["fair"]["radiative_forcing"] != erw_results()["fair"]["radiative_forcing"]


def test_erw_campaign_sensitivity_preserves_the_calculated_supplier_inventory():
    baseline=dict(annual_scores("ERW"))
    half=dict(annual_scores("ERW",realization=.5))
    assert sum(half.values())-sum(baseline.values()) == pytest.approx(500)
    assert half[0] == baseline[0]


def test_review_exposes_corrections_and_discloses_calculation_limits():
    root = Path(__file__).resolve().parents[1] / "apps/seoul_2026/data"
    review = json.loads((root / "erw_review.json").read_text())
    assert len(review["source_sha256"]) == 64
    assert "TRAILS" in review["validation"]
    assert len(review["temporal_checks"]) == 3
    assert "low-voltage" in repr(review)
    assert "groundwater" in repr(review)


def test_mounted_routes_assets_and_presenter_are_self_contained():
    client = Client(application, Response)
    for path in (
        "",
        "_dash-layout",
        "_dash-dependencies",
        "health",
        "presenter",
        "erw-review",
        "erw-inventory.xlsx",
        "assets/styles.css",
        "shared/styles.css",
        "shared/setac.css",
        "assets/edges-logo.png",
        "assets/romain-sacchi-portrait.png",
    ):
        response = client.get("/seoul-2026/" + path)
        assert response.status_code == 200, path
    page = client.get("/seoul-2026/").text
    assert "/seoul-2026/_dash-component-suites/" in page
    presenter = client.get("/seoul-2026/presenter").text
    assert "70:00" in presenter and "20 min" in presenter
    assert "snu-2026-slide" in presenter
    assert client.get("/seoul-2026/shared/not-allowed.txt").status_code == 404


def test_pulse_equivalence_illustrates_why_zero_aggregate_gwp_can_hide_warming():
    same = update_pulse(0).layout.meta
    short = update_pulse(20).layout.meta
    late = update_pulse(50).layout.meta
    assert same["equivalent_kg"] == 0
    assert 0 < short["equivalent_kg"] < late["equivalent_kg"] < 1000
    assert (late["window_start"], late["window_end"], late["reference_year"]) == (
        2020,
        2100,
        2030,
    )
    assert "median response areas" in late["equivalent_basis"]
    # Independently integrate the stored unit responses for this teaching example.
    from apps.lca_time.workshop import results as source

    first = dict(source.co2_reference_pulse_series("radiative forcing", 50, 2030))
    second = dict(source.co2_reference_pulse_series("radiative forcing", 50, 2080))
    area_first = sum((first[y] + first[y + 1]) / 2 for y in range(2020, 2100))
    area_second = sum((second[y] + second[y + 1]) / 2 for y in range(2020, 2100))
    assert late["equivalent_kg"] == pytest.approx(
        1000 * (area_first - area_second) / area_first
    )


@pytest.mark.parametrize("window", [(2020, 2030, 2050), (2020, 2030, 2100), (2020, 2050, 2300), (2090, 2100, 2200)])
def test_interactive_equivalence_matches_signed_areas_without_changing_inventory(window):
    from apps.seoul_2026.pulse import window_figure

    figure = window_figure(window)
    meta = figure.layout.meta
    assert meta["system_area"] == pytest.approx(meta["matched_reference_area"], rel=1e-12)
    assert meta["fixed_inventory"] == {"2030": 1000, "2080": -1000}
    assert sum(meta["fixed_inventory"].values()) == 0
    assert meta["equivalent_kg"] == pytest.approx(meta["system_area"] / meta["reference_area_per_kg"])
    # Before the later removal, the experiment is exactly a +1 t pulse in 2030.
    if window == (2020, 2030, 2050):
        assert meta["equivalent_kg"] == pytest.approx(1000)
    if window == (2020, 2030, 2100):
        assert meta["equivalent_kg"] == pytest.approx(update_pulse(50).layout.meta["equivalent_kg"])


def test_reference_date_changes_equivalent_without_changing_the_project_response():
    from apps.seoul_2026.pulse import window_figure

    first = window_figure((2020, 2030, 2100))
    second = window_figure((2020, 2050, 2100))
    assert list(first.data[0].y) == list(second.data[0].y)
    assert first.layout.meta["system_area"] == second.layout.meta["system_area"]
    assert first.layout.meta["equivalent_kg"] != second.layout.meta["equivalent_kg"]


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("window", [(2020,2030,2050),(2020,2030,2100),(2090,2100,2200)])
def test_four_case_pulses_match_areas_and_preserve_native_responses(case,window):
    from apps.seoul_2026.case_pulse import case_window_figure
    from apps.seoul_2026.comparison import forcing_series

    figure=case_window_figure(case,window)
    meta=figure.layout.meta
    anchor=2035 if case=="Cement + CCS" else 2030
    assert list(zip(figure.data[0].x,figure.data[0].y)) == [(y+anchor,v) for y,v in forcing_series(case)]
    assert meta["system_area"] == pytest.approx(meta["matched_reference_area"],rel=1e-12,abs=1e-12)
    assert meta["equivalent_kg"] == pytest.approx(meta["system_area"]/meta["reference_area_per_kg"])
    assert meta["reference_area_per_kg"] > 0
    assert "not an ensemble quantile" in meta["equivalent_basis"]
    assert ("EU21" in meta["background"]) == (case=="ERW")


@pytest.mark.parametrize("case", CASES)
def test_four_case_reference_date_changes_only_the_matched_pulse(case):
    from apps.seoul_2026.case_pulse import case_window_figure

    first=case_window_figure(case,(2020,2030,2100))
    second=case_window_figure(case,(2020,2035,2100))
    assert first.data[0].x == second.data[0].x
    assert first.data[0].y == second.data[0].y
    assert first.layout.meta["system_area"] == second.layout.meta["system_area"]
    assert first.layout.meta["equivalent_kg"] != second.layout.meta["equivalent_kg"]


def test_core_content_has_no_exact_repeated_slide_bodies():
    from apps.seoul_2026.deck import content

    bodies = [repr(content(i, print_mode=True)) for i in range(1, CORE_COUNT)]
    assert len(set(bodies)) == len(bodies)


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("year", [2025, 2050])
def test_signed_activity_stacks_close_to_original_snapshot(case, year):
    from apps.seoul_2026.contributions import static_contributions

    groups = static_contributions(case, year)
    assert sum(groups.values()) == pytest.approx(snapshot(case, year), abs=1e-6)
    assert any(v > 0 for v in groups.values())
    assert any(v < 0 for v in groups.values())
    assert all(v * sign >= 0 for (_, sign), v in groups.items())
    from apps.seoul_2026.contributions import static_figure

    low, high = static_figure(case).layout.yaxis.range
    assert low < sum(v for v in groups.values() if v < 0)
    assert high > sum(v for v in groups.values() if v > 0)


@pytest.mark.parametrize("case", CASES)
def test_responsible_root_stacks_close_in_every_year_and_keep_both_signs(case):
    from collections import defaultdict
    from apps.seoul_2026.contributions import temporal_contributions, temporal_figure

    groups, labels = temporal_contributions(case)
    actual = defaultdict(float)
    for (_, sign), series in groups.items():
        assert all(v * sign >= 0 for v in series.values())
        for year, value in series.items():
            actual[year] += value
    expected = dict(annual_scores(case))
    assert all(
        abs(actual[y] - expected.get(y, 0)) < 1e-3
        for y in actual.keys() | expected.keys()
    )
    assert labels
    cumulative = temporal_figure(case)
    net = next(t for t in cumulative.data if t.name == "Cumulative GWP100")
    assert net.y[-1] == pytest.approx(sum(expected.values()), abs=1e-6)


def test_process_quantities_conserve_carbon_and_keep_energy_bases():
    from apps.seoul_2026.processes import process_quantities
    from apps.seoul_2026.erw import ROCK_KG, REFERENCE_UPTAKE_KG

    dac = process_quantities("DACCS")
    bio = process_quantities("BECCS")
    assert dac["gross_capture_t_co2"] == pytest.approx(
        dac["gross_storage_t_co2"] + dac["transport_loss_co2_t"]
    )
    assert bio["forest_co2_uptake_t"] == pytest.approx(
        bio["gross_storage_t_co2"]
        + bio["capture_loss_co2_t"]
        + bio["transport_loss_co2_t"]
    )
    assert bio["gross_heat_coproduct_gj"] == pytest.approx(
        bio["internal_capture_heat_gj"] + bio["net_heat_coproduct_gj"]
    )
    assert dac["heat_pump_electricity_mwh"] * 3.6 * dac[
        "heat_pump_cop"
    ] == pytest.approx(dac["delivered_low_temperature_heat_gj"])
    assert dac["capture_process_electricity_mwh"] + dac[
        "heat_pump_electricity_mwh"
    ] == pytest.approx(dac["capture_and_heat_pump_electricity_mwh"])
    erw = process_quantities("ERW")
    assert erw["rock_kg"] == ROCK_KG
    assert erw["eventual_uptake_kg"] == REFERENCE_UPTAKE_KG
    assert erw["nickel_upper_bound_kg"] == pytest.approx(NICKEL_KG)
    cement = process_quantities("Cement + CCS")
    assert cement["gross_co2_kg"] == pytest.approx(
        cement["stored_co2_kg"] + cement["known_air_co2_kg"]
    )
    assert cement["captured_co2_kg"] == pytest.approx(
        cement["gross_co2_kg"] * cement["capture_fraction"]
    )
    assert cement["known_air_co2_kg"] == pytest.approx(
        sum(
            cement[f"{k}_co2_kg"]
            for k in ["uncaptured", "liquefaction_loss", "transport_loss"]
        )
    )


@pytest.mark.parametrize("year", [2025, 2050])
def test_cement_origin_snapshot_split_closes_without_relabelling_other_effects(year):
    from apps.seoul_2026.cement_origins import static_origins, origin
    from apps.seoul_2026.carbon import FOSSIL, NON_FOSSIL, UPTAKE, OTHER

    groups = static_origins(year)
    assert sum(groups.values()) == pytest.approx(
        snapshot("Cement + CCS", year), abs=1e-6
    )
    assert groups[FOSSIL, -1] < 0 and groups[NON_FOSSIL, -1] < 0
    assert all(value * sign >= 0 for (_, sign), value in groups.items())
    assert origin("Carbon dioxide, non-fossil") == NON_FOSSIL
    assert origin("Carbon dioxide, fossil") == FOSSIL
    assert origin("Captured calcination CO₂ → storage") == FOSSIL
    assert origin("Carbon dioxide, in air") == UPTAKE
    assert origin("Methane, fossil") == OTHER
    assert origin("Electricity") == OTHER


def test_cement_temporal_origin_view_closes_independently_of_stage_roots():
    from collections import defaultdict
    from apps.seoul_2026.cement_origins import temporal_origins

    actual = defaultdict(float)
    for (_, sign), series in temporal_origins().items():
        assert all(value * sign >= 0 for value in series.values())
        for age, value in series.items():
            actual[age] += value
    expected = dict(annual_scores("Cement + CCS"))
    assert all(
        abs(actual[age] - expected.get(age, 0)) < 1e-6
        for age in actual.keys() | expected.keys()
    )


def test_result_slides_do_not_expose_supply_chain_co2_flow_views():
    for key in ("current", "future", "inventory", "response"):
        for print_mode in (False, True):
            figures = [
                node.figure
                for node in walk(render_slide(SLIDE_INDEX[key], print_mode=print_mode))
                if hasattr(node, "figure")
            ]
            assert len(figures) == 4
            assert all(not fig.layout.updatemenus for fig in figures)
            assert all(
                trace.visible is not False for fig in figures for trace in fig.data
            )


def test_cement_physical_origin_branches_conserve_full_stored_tonne():
    from apps.seoul_2026.processes import process_quantities, process_uri
    from apps.seoul_2026.carbon import ORIGINS, FOSSIL, NON_FOSSIL
    from urllib.parse import unquote

    q = process_quantities("Cement + CCS")
    assert q["stored_co2_kg"] == pytest.approx(1000)
    assert q["clinker_t"] > 1
    for field in [
        "captured_co2_kg",
        "stored_co2_kg",
        "uncaptured_co2_kg",
        "liquefaction_loss_co2_kg",
        "transport_loss_co2_kg",
    ]:
        assert sum(part[field] for part in q["origins"].values()) == pytest.approx(
            q[field]
        )
    for part in q["origins"].values():
        assert part["inlet_co2_kg"] == pytest.approx(
            part["stored_co2_kg"]
            + part["uncaptured_co2_kg"]
            + part["liquefaction_loss_co2_kg"]
            + part["transport_loss_co2_kg"]
        )
    svg = unquote(process_uri("Cement + CCS"))
    assert ORIGINS[FOSSIL] in svg and ORIGINS[NON_FOSSIL] in svg
    assert "Non-fossil:" in svg and "Fossil:" in svg
    assert 'stroke-dasharray="3 4"' in svg


def test_current_slide_has_signed_harmonized_activity_stacks_for_every_case():
    from apps.seoul_2026.contributions import CURRENT_TYPES

    for print_mode in (False, True):
        slide = render_slide(SLIDE_INDEX["current"], print_mode=print_mode)
        figures = [node.figure for node in walk(slide) if hasattr(node, "figure")]
        assert len(figures) == 4
        assert [fig.layout.meta["case"] for fig in figures] == list(CASES)
        assert len({tuple(fig.layout.yaxis.range) for fig in figures}) == 1
        for case, fig in zip(CASES, figures):
            bars = [
                trace
                for trace in fig.data
                if trace.type == "bar" and trace.visible is not False
            ]
            assert all(
                trace.marker.color == CURRENT_TYPES[trace.name] for trace in bars
            )
            positive = sum(max(trace.y[0], 0) for trace in bars)
            negative = sum(min(trace.y[0], 0) for trace in bars)
            assert positive > 0 and negative < 0
            assert positive + negative == pytest.approx(snapshot(case, 2025), abs=1e-6)
            assert fig.layout.yaxis.range[0] < negative
            assert fig.layout.yaxis.range[1] > positive
            assert all(list(trace.x) == ["2025"] for trace in bars)
            net = next(
                trace
                for trace in fig.data
                if trace.name == "Net GWP100" and trace.visible is not False
            )
            assert net.marker.symbol == "diamond"
            assert net.y[0] == pytest.approx(snapshot(case, 2025))
        cement = figures[-1]
        assert not cement.layout.updatemenus


def test_current_co2_terms_are_limited_to_fossil_and_non_fossil():
    from apps.seoul_2026.contributions import current_contributions, CURRENT_TYPES
    from apps.setac_2026.results import case_inventory

    allowed = {"fossil CO₂", "non-fossil CO₂"}
    assert {name for name in CURRENT_TYPES if "CO₂" in name} == allowed
    for case in CASES:
        groups = current_contributions(case)
        assert {name for name, _ in groups if "CO₂" in name} <= allowed
        assert sum(groups.values()) == pytest.approx(snapshot(case, 2025), abs=1e-6)
    bio = case_inventory("BECCS")
    groups = current_contributions("BECCS")
    assert groups["non-fossil CO₂", 1] == pytest.approx(
        1000 * (bio["capture_loss_co2_t"] + bio["transport_loss_co2_t"])
    )
    assert groups["Other direct effects", 1] > 0
    slide = render_slide(SLIDE_INDEX["current"])
    figures = [node.figure for node in walk(slide) if hasattr(node, "figure")]
    forbidden = {
        "CO₂ uptake",
        "Biogenic uptake",
        "Atmospheric uptake",
        "Fossil / mineral CO₂",
    }
    assert all(trace.name not in forbidden for fig in figures for trace in fig.data)


@pytest.mark.parametrize("year", [2025, 2050])
@pytest.mark.parametrize("case", ["DACCS", "BECCS"])
def test_foreground_co2_is_separate_from_complete_supplier_roots(case, year):
    from apps.seoul_2026.contributions import (
        cdr_static_roots,
        foreground_contributions,
        supplier_type,
    )

    data = cdr_static_roots(year)["cases"][case]
    groups = foreground_contributions(case, year)
    direct_negative = sum(
        r["score"] for r in data["foreground"] if r["flow"] == "Carbon dioxide, in air"
    )
    direct_positive = sum(
        r["score"]
        for r in data["foreground"]
        if r["flow"] == "Carbon dioxide, non-fossil"
    )
    assert groups["non-fossil CO₂", -1] == pytest.approx(direct_negative)
    assert groups["non-fossil CO₂", 1] == pytest.approx(direct_positive)
    assert not any(name == "fossil CO₂" for name, _ in groups)
    for kind in (
        "Electricity + heat",
        "Biomass supply",
        "Materials + equipment",
        "Transport + storage",
    ):
        for sign in (-1, 1):
            expected = sum(
                r["score"]
                for r in data["suppliers"]
                if supplier_type(r) == kind and r["score"] * sign >= 0
            )
            assert groups.get((kind, sign), 0) == pytest.approx(expected, abs=1e-9)
    assert sum(groups.values()) == pytest.approx(snapshot(case, year), abs=1e-6)
    if case == "DACCS":
        assert direct_negative == pytest.approx(-1028.80658436214, abs=1e-4)
        assert direct_positive == pytest.approx(28.80658436214, abs=1e-4)
        assert groups["Electricity + heat", 1] > 0
        assert (
            abs(direct_negative) < 1100
        )  # Upstream forest uptake is inside supplier roots.
    else:
        assert direct_negative == pytest.approx(-1143.118427069, abs=1e-4)
        assert groups["Other direct effects", 1] > 0  # CH4/N2O are not labelled CO₂.


@pytest.mark.parametrize("year", [2025, 2050])
def test_all_four_foreground_and_supply_chain_views_close(year):
    from apps.seoul_2026.contributions import foreground_contributions, CURRENT_TYPES

    for case in CASES:
        groups = foreground_contributions(case, year)
        assert set(name for name, _ in groups) <= set(CURRENT_TYPES)
        assert all(value * sign >= 0 for (_, sign), value in groups.items())
        assert sum(groups.values()) == pytest.approx(snapshot(case, year), abs=1e-6)


@pytest.mark.parametrize("case,expected_t", [
    ("DACCS",1.3193058228394454),
    ("BECCS",4.6689561350482975),
    ("ERW",1.20349037766868),
    ("Cement + CCS",1.4419326235774623),
])
def test_closing_gross_capture_matches_one_tonne_removal_area(case, expected_t):
    from apps.seoul_2026.closing_scores import summary_rows
    from apps.seoul_2026.case_pulse import case_window_figure

    row = next(row for row in summary_rows() if row["case"] == case)
    meta = case_window_figure(case).layout.meta
    assert row["gross_required_t"] == pytest.approx(expected_t)
    service_count = row["gross_required_t"] / row["gross_capture_per_service_t"]
    assert service_count * meta["system_area"] == pytest.approx(
        -1000 * meta["reference_area_per_kg"]
    )
    # The capture/storage cases include physical downstream losses; ERW uses
    # eventual gross uptake, without treating its rock mass as captured CO2.
    assert row["gross_capture_per_service_t"] >= 1
    assert (row["gross_capture_per_service_t"] == 1) == (case == "ERW")
