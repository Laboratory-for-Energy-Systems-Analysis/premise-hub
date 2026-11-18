"""Check that the adaptation preserves results and works beside the SETAC app."""

import json

import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from apps.mcv_2026 import figures
from apps.mcv_2026.app import pdf_deck, update_pulse
from apps.mcv_2026.deck import CORE_COUNT, SLIDES
from apps.setac_2026 import figures as original
from portal.wsgi import application


@pytest.mark.parametrize("name,args", [
    ("static_figure", ()), ("prospective_figure", ()),
    ("temporal_figure", ()), ("temporal_figure", ("unstacked",)),
    ("forcing_figure", (2140,)), ("pulse_figure", (2100,)),
    ("mix_figure", ("Electricity",)), ("scenario_context_figure", ()),
])
def test_french_figures_preserve_source_data_and_metadata(name, args):
    before = getattr(original, name)(*args).to_plotly_json()
    after = getattr(figures, name)(*args).to_plotly_json()
    assert len(before["data"]) == len(after["data"])
    for a, b in zip(before["data"], after["data"], strict=True):
        for key in ("x", "y", "base", "meta", "stackgroup", "fillpattern", "marker"):
            assert json.dumps(a.get(key), sort_keys=True) == json.dumps(b.get(key), sort_keys=True)
    assert before["layout"].get("meta") == after["layout"].get("meta")


def test_password_gate_protects_all_mcv_routes():
    client = Client(application, Response)
    for path in ("/", "/presenter", "/_dash-layout", "/_dash-dependencies",
                 "/assets/mcv-logo.png", "/fair-handoff.svg", "/system-flows.svg",
                 "/routing/beccs.json", "/shared/styles.css"):
        response = client.get("/mcv-2026" + path)
        assert response.status_code == 401, path
        assert response.headers["Cache-Control"] == "no-store"
    assert client.post("/mcv-2026/_dash-update-component", json={}).status_code == 401
    assert client.post("/mcv-2026/", data={"password": "wrong"}).status_code == 401
    assert client.get("/setac-2026/health").json["core_slides"] == 12


@pytest.fixture
def mcv_client():
    client = Client(application, Response)
    login = client.post("/mcv-2026/", data={"password": "test-mcv-password"})
    assert login.status_code == 303
    assert login.headers["Location"] == "/mcv-2026/"
    assert "HttpOnly" in login.headers["Set-Cookie"]
    return client


def test_mounted_deck_presenter_assets_and_callback(mcv_client):
    client = mcv_client
    for path in ("/", "/presenter", "/health", "/_dash-layout", "/_dash-dependencies",
                 "/assets/mcv-logo.png", "/shared/styles.css", "/system-flows.svg"):
        response = client.get("/mcv-2026" + path)
        assert response.status_code == 200, path
        assert response.headers["Cache-Control"] == "private, no-store"
    assert b'<html lang="fr">' in client.get("/mcv-2026/").data
    assert "/mcv-2026/_dash-component-suites/" in client.get("/mcv-2026/").text
    assert "11:40" in client.get("/mcv-2026/presenter").text
    response = client.post("/mcv-2026/_dash-update-component", json={
        "output": "forcing-chart.figure", "outputs": {"id": "forcing-chart", "property": "figure"},
        "inputs": [{"id": "forcing-horizon", "property": "value", "value": 2140}],
        "state": [], "changedPropIds": ["forcing-horizon.value"],
    })
    assert response.status_code == 200
    assert "forçage" in response.json["response"]["forcing-chart"]["figure"]["layout"]["yaxis"]["title"]["text"]


@pytest.mark.parametrize("slug", ["daccs", "beccs"])
def test_routing_viewer_reuses_verified_seoul_exports(slug, mcv_client):
    from apps.mcv_2026.app import update_routing
    from apps.seoul_2026.routing import shallow_route_json

    client = mcv_client
    viewer = client.get(f"/mcv-2026/routing/{slug}.html")
    assert viewer.status_code == 200
    assert '<html lang="fr">' in viewer.text
    assert "Toutes les branches" in viewer.text
    response = client.get(f"/mcv-2026/routing/{slug}.json?depth=3")
    assert response.data == shallow_route_json(slug).encode()
    assert client.get(f"/mcv-2026/routing/{slug}.png").status_code == 200
    assert client.get("/mcv-2026/shared/routing-vis.min.js").status_code == 200
    assert client.get("/mcv-2026/routing/unknown.html").status_code == 404
    expected = f"/mcv-2026/routing/{slug}.html"
    assert update_routing(slug.upper()) == (expected, expected)


def test_pulse_controls_update_french_interpretation_and_all_three_dates():
    figure, cards, config, labels, comparison, interpretation, window = update_pulse([2000, 2035, 2300])
    assert figure.layout.meta == {"start": 2000, "reference": 2035, "end": 2300}
    assert window == [2000, 2035, 2300]
    assert cards[0].children[1].children.startswith("−")
    assert "2035" in config[0].children
    assert "2000–2300" in interpretation[0].children[-1].children[2]
    assert labels[1].children == "Impulsion CO₂ : 2035"


@pytest.mark.parametrize("end,expected", [
    (2100, ("4,57 t nettes de CO₂", "1,26 t nettes de CO₂")),
    (2300, ("1,22 t nettes de CO₂", "1,13 t nettes de CO₂")),
])
def test_inverse_pulse_interpretation_matches_reviewed_endpoint_scores(end, expected):
    from apps.mcv_2026.deck import pulse_takeaway

    interpretations = pulse_takeaway(end=end)
    for interpretation, amount in zip(interpretations, expected, strict=True):
        inverse = interpretation.children[-1]
        assert inverse.children[1].children == amount
        assert "retrait de 1 t CO₂ en 2030" in inverse.children[2]


def test_print_deck_has_no_live_control_ids_and_includes_cover_logo():
    core, full = pdf_deck(), pdf_deck(True)
    assert len(core) == CORE_COUNT == 10
    assert len(full) == 16
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
