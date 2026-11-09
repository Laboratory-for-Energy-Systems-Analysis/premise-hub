"""Slide 14: data handoff and actual TRAILS temporal-routing exports.

Public exports retain all routed nodes and links at depth four, without private
coefficients. The initial view requests an exact level-zero-to-three projection;
level four is fetched on demand. Iframes load only for the active technology.
"""

import base64
import gzip
import hashlib
import json
from functools import lru_cache
from pathlib import Path

from dash import html

from .branding import database_icon, logo, tool_link
from .layout import PREFIX
from .visuals import CASE, CASES

SLUGS = dict(zip(CASES, ("daccs", "beccs", "erw", "cement")))


ROUTING_MANIFEST_SHA256 = "d56aff79198e809c5f4b022c9fdf02d8794016ec27ae03b58adf9f7f2f0974b1"
# Exact response bytes extracted from the unchanged, verified full exports by
# scripts/build_seoul_route_previews.py. Pinning prevents stale projections.
SHALLOW_ROUTE_SHA256 = {
    "daccs": "306fbb388d41574954c88ef14f8e1cadc1db61c5508173e9e9a46df905db1e46",
    "beccs": "8b43b9157b1d62a74ff7ccc5b00b404f92981a4df2307ea36dc75cbb22fd5d0c",
    "erw": "5e6488b0b3843ddd7012aba717bc7212b31dbc4b7bafe9fbf3b6b28a42d48b0a",
    "cement": "b7a470a90fa55492e8a3701a2b8527ea79e8cec83800915c7fcde8f2eceee974",
}


def _file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=8)
def verified_route_path(slug, extension):
    if slug not in SLUGS.values() or extension not in {"json", "png"}:
        raise ValueError("Unknown graph asset")
    folder = Path(__file__).parent / "data/routing"
    raw = (folder / "manifest.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != ROUTING_MANIFEST_SHA256:
        raise ValueError("Routing manifest differs from the checked export")
    manifest = json.loads(raw)
    path = folder / f"{slug}.{extension}"
    expected = manifest["cases"][slug]["graph_sha256" if extension == "json" else "preview_sha256"]
    if _file_sha256(path) != expected:
        raise ValueError("Routing graph asset differs from its checked export")
    return path


@lru_cache(maxsize=4)
def shallow_route_json(slug):
    """Serve only levels zero to three until the viewer requests level four."""
    source = verified_route_path(slug, "json")
    path = source.with_name(f"{slug}-depth3.json.gz")
    payload = gzip.decompress(path.read_bytes())
    if hashlib.sha256(payload).hexdigest() != SHALLOW_ROUTE_SHA256[slug]:
        raise ValueError("Routing preview differs from its checked projection")
    # No JSON object tree is built on the server. Keep the original provenance,
    # counts, node/edge ordering and response text byte-for-byte intact.
    return payload.decode("utf-8")


def _workflow():
    return html.Div([
        html.Div([
            html.Div([html.Div([html.Span("IAM scenarios"), html.Strong("REMIND-EU"),
                               html.Span("Pathway + future years")]),
                      html.B("+"),
                      html.Div([html.Div([database_icon(), logo("ecoinvent", "route-ecoinvent")],
                                              className="route-database"), html.Span("3.12 · cut-off inventories")])],
                     className="route-inputs"),
        ], className="route-workflow-card route-input-card"),
        html.Div("↓", className="route-flow-arrow", **{"aria-hidden": "true"}),
        html.Div([logo("premise", "route-premise"), html.Div([
            html.Strong([tool_link("premise"), ": scenario-updated LCA data"]), html.Span("Transform suppliers · export scenario years")])],
                 className="route-workflow-card route-premise-card"),
        html.Div("↓", className="route-flow-arrow", **{"aria-hidden": "true"}),
        html.Div([
            html.Div([html.Strong("Scenario data package"), html.Span("3D stacks: two inventory dimensions + year")],
                     className="route-package-heading"),
            html.Img(src=PREFIX + "shared/trails-annual-matrices.svg",
                     alt="Technosphere A: product, activity, year. Biosphere B: elementary flow, activity, year.",
                     className="route-package-matrices"),
            html.Div([html.Strong("+ Encode temporal distributions"),
                      html.Span("Analyst’s foreground: build · operate · regrow / dissolve")],
                     className="route-temporal-input"),
        ], className="route-workflow-card route-package-card"),
        html.Div("↓", className="route-flow-arrow", **{"aria-hidden": "true"}),
        html.Div([logo("trails", "route-trails"), html.Div([
            html.Strong([tool_link("trails"), ": route in time → solve by year"]),
            html.Span("Interpolate backgrounds · retain the remaining supply chain")])],
                 className="route-workflow-card route-trails-card"),
    ], className="route-data-workflow")


def _case_panel(case, print_mode=False):
    slug = SLUGS[case]
    href = PREFIX + f"routing/{slug}.html"
    if print_mode:
        path = verified_route_path(slug, "png")
        image_uri = "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")
        viewer = html.Div([
            html.Strong("Level 0 · " + ("1 t eventual gross uptake potential" if case == "ERW" else "1 t CO₂ physically stored"), className="route-print-service"),
            html.Img(src=image_uri, alt=f"Actual TRAILS routing graph for {case}, default levels zero to three", className="route-printed-graph"),
        ], className="route-print-view")
    else:
        viewer = html.Iframe(src="about:blank", title=f"{case} actual TRAILS temporal-routing graph",
            className="route-frame", **{"data-route-src": href}, allow="fullscreen")
    return html.Div([
        html.Div([html.Span(case), html.A("Open full graph ↗", href=href, target="_blank", rel="noopener")], className="route-case-title"),
        viewer,
    ], className="route-example route-case-panel", style={"--case-colour": CASE[case]["colour"]},
        **{"data-case": case, "data-routing-kind": "actual-trails-graph"})


def routing_lesson(print_mode=False):
    from .methods import lesson_switch

    return html.Div([
        html.Section([html.H2("01 · Assemble the time-aware model"), _workflow()], className="route-left-pane"),
        html.Section([
            html.Div([html.H2("02 · Follow the temporal routes"),
                      html.Span("Actual TRAILS output · functional unit at level 0 → level 4")], className="route-right-heading"),
            lesson_switch("Temporal routes by technology", [(c, _case_panel(c, print_mode)) for c in CASES], print_mode=print_mode),
        ], className="route-right-pane"),
    ], className="routing-split", **{"data-reused-from": "/setac-2026/ · annual matrix stacks; /lca-time/ · TRAILS logo"})
