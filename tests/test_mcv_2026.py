"""Check regenerated MCV results, their French display and portal integration."""

import json
from io import BytesIO
from zipfile import ZipFile

import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from apps.mcv_2026 import figures
from apps.mcv_2026.app import pdf_deck, update_pulse
from apps.mcv_2026.deck import CORE_COUNT, SLIDES
from apps.setac_2026 import figures as original
from apps.setac_2026.scripts.regenerate_results import annual_forest_uptake_profile
from portal.wsgi import application


@pytest.mark.parametrize("name,args", [
    ("static_figure", ()), ("prospective_figure", ()),
    ("temporal_figure", ()), ("temporal_figure", ("unstacked",)),
    ("forcing_figure", (2140,)), ("pulse_figure", (2100,)),
    ("mix_figure", ("Electricity",)), ("scenario_context_figure", ()),
])
def test_french_figures_preserve_source_data_and_metadata(name, args):
    before = getattr(figures.source, name)(*args).to_plotly_json()
    after = getattr(figures, name)(*args).to_plotly_json()
    assert len(before["data"]) == len(after["data"])
    for a, b in zip(before["data"], after["data"], strict=True):
        for key in ("x", "y", "base", "meta", "stackgroup", "fillpattern", "marker"):
            assert json.dumps(a.get(key), sort_keys=True) == json.dumps(b.get(key), sort_keys=True)
    assert before["layout"].get("meta") == after["layout"].get("meta")
    if name == "temporal_figure":
        for axis in ("xaxis", "xaxis2"):
            assert after["layout"][axis]["range"] == [2000, 2130]


def test_mcv_result_reader_is_independent_of_setac():
    assert figures.static_score("BECCS") == pytest.approx(-960.0787784)
    assert figures.static_score("DACCS") == pytest.approx(-821.8606954)
    assert figures.static_score("BECCS") != original.static_score("BECCS")
    assert figures.pulse_value("BECCS") == pytest.approx(-223.5903, abs=0.05)
    assert figures.pulse_value("DACCS") == pytest.approx(-777.7718, abs=0.05)


def test_spruce_uptake_preserves_each_annual_midpoint_weight():
    scenario = {"model": "remind-eu", "pathway": "SSP2-PkBudg1000"}
    forest = {
        "source_year": 2030, "source_name": "spruce forestry",
        "source_reference_product": "wood", "source_location": "ENC", "rotation_years": 4,
    }
    prefix = "inventories/remind-eu/SSP2-PkBudg1000/2030/"
    with ZipFile(BytesIO(), "w") as archive:
        archive.writestr(prefix + "A_matrix_index.csv",
                         "index;name;reference product;location\n42;spruce forestry;wood;ENC\n")
        archive.writestr(prefix + "B_matrix_index.csv", "index;name\n7;Carbon dioxide, in air\n")
        archive.writestr(prefix + "B_matrix.csv",
                         "index of activity;index of biosphere flow;temporal_distribution;temporal_offsets;temporal_weights\n"
                         "42;7;6;[0.5,1.5,2.5,3.5];[0.1,0.2,0.3,0.4]\n")
        profile = annual_forest_uptake_profile(archive, scenario, forest)
    assert profile == {"offsets": [0, 1, 2, 3], "weights": [0.1, 0.2, 0.3, 0.4]}


@pytest.fixture
def mcv_client():
    return Client(application, Response, use_cookies=False)


def test_mounted_deck_presenter_assets_and_callback(mcv_client):
    client = mcv_client
    for path in ("/", "/presenter", "/health", "/_dash-layout", "/_dash-dependencies",
                 "/assets/mcv-logo.png", "/shared/styles.css", "/system-flows.svg", "/fair-handoff.svg"):
        response = client.get("/mcv-2026" + path)
        assert response.status_code == 200, path
        assert response.headers["Cache-Control"] == "private, no-store"
        assert "Set-Cookie" not in response.headers
    index = client.get("/mcv-2026/").text
    assert 'name="password"' not in index
    assert '<html lang="fr">' in index
    assert "/mcv-2026/_dash-component-suites/" in index
    assert "11:40" in client.get("/mcv-2026/presenter").text
    response = client.post("/mcv-2026/_dash-update-component", json={
        "output": "forcing-chart.figure", "outputs": {"id": "forcing-chart", "property": "figure"},
        "inputs": [{"id": "forcing-horizon", "property": "value", "value": 2140}],
        "state": [], "changedPropIds": ["forcing-horizon.value"],
    })
    assert response.status_code == 200
    assert "forçage" in response.json["response"]["forcing-chart"]["figure"]["layout"]["yaxis"]["title"]["text"]


@pytest.mark.parametrize("slug", ["daccs", "beccs"])
def test_routing_viewer_uses_the_regenerated_mcv_archive(slug, mcv_client):
    from apps.mcv_2026.app import update_routing

    client = mcv_client
    viewer = client.get(f"/mcv-2026/routing/{slug}.html")
    assert viewer.status_code == 200
    assert '<html lang="fr">' in viewer.text
    assert "Toutes les branches" in viewer.text
    assert 'id="network"' in viewer.text
    assert 'const foreground=true' in viewer.text
    assert 'value="1" selected' in viewer.text
    assert 'value="4"' not in viewer.text
    original = client.get(f"/mcv-2026/routing/{slug}.html?layout=original")
    assert 'const foreground=false' in original.text
    assert 'value="3" selected' in original.text
    assert 'value="4"' not in original.text
    response = client.get(f"/mcv-2026/routing/{slug}.json?depth=3")
    shallow = response.json
    full = client.get(f"/mcv-2026/routing/{slug}.json").json
    assert {full["metadata"]["package_sha256"]} == {
        row["package_sha256"] for row in figures.source.results.static_rows()
        if row["pathway"] == "SSP2-PkBudg1000"
    }
    assert shallow["metadata"] == full["metadata"]
    assert shallow["loaded_max_depth"] == 3
    assert max(node["depth"] for node in shallow["nodes"]) == 3
    assert max(node["depth"] for node in full["nodes"]) == 4
    assert client.get(f"/mcv-2026/routing/{slug}.png").status_code == 200
    assert client.get("/mcv-2026/shared/routing-vis.min.js").status_code == 200
    assert client.get("/mcv-2026/routing/unknown.html").status_code == 404
    expected = f"/mcv-2026/routing/{slug}.html"
    assert update_routing(slug.upper()) == (expected, expected)


@pytest.mark.parametrize("slug,construction,operation,retirement,negative", [
    ("daccs", "direct air capture system, sorbent-based, 100ktCO2",
     "market group for electricity, medium voltage",
     "treatment of direct air capture system, sorbent-based, 100ktCO2", False),
    ("beccs", "market for heat and power co-generation unit, organic Rankine cycle, 1000kW electrical",
     "market group for electricity, high voltage",
     "treatment of waste concrete, inert material landfill", True),
])
def test_foreground_network_promotes_real_dated_exchanges(slug, construction, operation, retirement, negative, mcv_client):
    url = f"/mcv-2026/routing/{slug}.json"
    raw = mcv_client.get(url).json
    initial = mcv_client.get(url + "?layout=foreground&depth=1").json
    full = mcv_client.get(url + "?layout=foreground").json
    nodes = {n["id"]: n for n in initial["nodes"]}
    root, = [n for n in nodes.values() if n["depth"] == 0]
    assert root["year"] == 2030
    assert initial["loaded_max_depth"] == 1
    assert set(n["depth"] for n in nodes.values()) == {0, 1}
    assert initial["nodes"] == [n for n in full["nodes"] if n["depth"] <= 1]
    assert {n["id"] for n in full["nodes"]} <= {n["id"] for n in raw["nodes"]}
    for name, years, sign in (
        (construction, set(range(2027, 2030)), False),
        (operation, set(range(2030, 2050)), negative),
        (retirement, {2050}, False),
    ):
        edges = [e for e in initial["edges"] if e["source"] == root["id"] and nodes[e["target"]]["name"] == name]
        assert {nodes[e["target"]]["year"] for e in edges} == years
        assert {e["negative"] for e in edges} == {sign}
        assert all(bool(e.get("via")) == (not sign) for e in edges)


def test_daccs_keeps_the_foreground_schedule_in_the_routed_graph(mcv_client):
    graph = mcv_client.get("/mcv-2026/routing/daccs.json?depth=3").json
    nodes = {node["id"]: node for node in graph["nodes"]}
    commissioning = {
        node["id"] for node in nodes.values()
        if node["depth"] == 2 and node["location"] == "ENC" and node["year"] == 2030
        and node["name"].startswith("carbon dioxide, captured and stored, with a sorbent-based")
    }
    assert len(commissioning) == 1
    supplier_years = {}
    for edge in graph["edges"]:
        if edge["source"] in commissioning:
            supplier = nodes[edge["target"]]
            supplier_years.setdefault(supplier["name"], set()).add(supplier["year"])
    assert supplier_years["direct air capture system, sorbent-based, 100ktCO2"] == {2027, 2028, 2029}
    assert supplier_years["market group for electricity, medium voltage"] == set(range(2030, 2050))
    assert supplier_years["treatment of direct air capture system, sorbent-based, 100ktCO2"] == {2050}


def test_pulse_controls_update_french_interpretation_and_all_three_dates():
    figure, cards, config, labels, comparison, interpretation, window = update_pulse([2000, 2035, 2300])
    assert figure.layout.meta == {"start": 2000, "reference": 2035, "end": 2300}
    assert window == [2000, 2035, 2300]
    assert cards[0].children[1].children.startswith("−")
    assert "2035" in config[0].children
    assert "2000–2300" in interpretation[0].children[-1].children[2]
    assert labels[1].children == "Impulsion CO₂ : 2035"


@pytest.mark.parametrize("end", [2100, 2300])
def test_inverse_pulse_interpretation_matches_endpoint_scores(end):
    from apps.mcv_2026.deck import number, pulse_takeaway

    interpretations = pulse_takeaway(end=end)
    for case, interpretation in zip(figures.CASES, interpretations, strict=True):
        inverse = interpretation.children[-1]
        assert inverse.children[1].children == (
            f"{number(-1000 / figures.pulse_value(case, end), 2)} t nettes de CO₂"
        )
        assert "retrait de 1 t CO₂ en 2030" in inverse.children[2]


def test_print_deck_has_no_live_control_ids_and_includes_cover_logo():
    core, full = pdf_deck(), pdf_deck(True)
    assert len(core) == CORE_COUNT == 10
    assert len(full) == 17
    assert sum(slide["seconds"] for slide in SLIDES) == 700
    pending = list(full)
    images = []
    while pending:
        component = pending.pop()
        assert getattr(component, "id", None) is None
        if hasattr(component, "src"):
            images.append(component.src)
        children = getattr(component, "children", None)
        if isinstance(children, (tuple, list)):
            pending.extend(children)
        elif children is not None:
            pending.append(children)
    assert sum(src.endswith("mcv-logo.png") for src in images) == len(full)
