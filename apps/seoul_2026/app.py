from __future__ import annotations

import os
from pathlib import Path

from dash import ALL, ClientsideFunction, Dash, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate
from flask import abort, render_template, send_from_directory, Response, request

from apps.setac_2026.system_flows import system_flow_svg
from apps.setac_2026.app import update_mixes, update_context

from .deck import ALL_SLIDES, CHAPTERS, CORE_COUNT, render_slide, presenter_slides
from . import comparison as compare
from . import contributions as attribution
from . import case_pulse as pulse_lesson
from .routing import verified_route_path, shallow_route_json
from .visuals import CASES
from .layout import UPLOAD_NAME

ROOT = Path(__file__).resolve().parent
REQUESTS_PREFIX = os.getenv("SEOUL_2026_REQUESTS_PREFIX", "/")
LCA_ASSETS = ROOT.parent / "lca_time/assets"
SETAC_ASSETS = ROOT.parent / "setac_2026/assets"
CCUS_ASSETS = ROOT.parent / "ccus_webinar/assets"
SHARED = {
    name: LCA_ASSETS / name
    for name in (
        "styles.css",
        "psi-mark.svg",
        "cover-iam-trajectories.svg",
        "case-pathways.svg",
        "pik-logo.png",
        "premise-logo.png",
        "trails-logo.png",
        "lens-conventional.svg",
        "lens-prospective.svg",
        "lens-time-explicit.svg",
    )
}
SHARED.update(
    {
        name: SETAC_ASSETS / name
        for name in (
            "trails-annual-matrices.svg",
            "trails-temporal-routing.svg",
            "eu-emblem.jpg",
        )
    }
)
SHARED["setac.css"] = SETAC_ASSETS / "styles.css"
SHARED["ccus-pathways.svg"] = CCUS_ASSETS / "ccus-pathways.svg"
SHARED["routing-vis.min.js"] = LCA_ASSETS / "routing/lib/vis-9.1.2/vis-network.min.js"
SHARED.update(
    {
        name: ROOT.parent / "workshop/assets" / name
        for name in ("premise-library-bridge.svg", "premise-logo-transparent.png")
    }
)

app = Dash(
    __name__,
    title="SNU · Why timing matters in LCA",
    update_title=None,
    requests_pathname_prefix=REQUESTS_PREFIX,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        REQUESTS_PREFIX + "shared/styles.css",
        REQUESTS_PREFIX + "shared/setac.css",
    ],
)
server = app.server


@server.get("/shared/<path:filename>")
def shared_asset(filename):
    path = SHARED.get(filename)
    if path is None:
        abort(404)
    return send_from_directory(path.parent, path.name)


@server.get("/system-flows.svg")
def system_flows():
    return Response(system_flow_svg(), mimetype="image/svg+xml")


@server.get("/routing/<case_slug>.<extension>")
def temporal_routing_graph(case_slug, extension):
    if case_slug not in {"daccs", "beccs", "erw", "cement"}:
        abort(404)
    if extension == "html":
        return render_template("routing_graph.html", case_slug=case_slug)
    if extension == "json" and request.args.get("depth") == "3":
        return Response(shallow_route_json(case_slug), mimetype="application/json")
    if extension in {"json", "png"}:
        path = verified_route_path(case_slug, extension)
        return send_from_directory(path.parent, path.name)
    abort(404)


@server.get("/health")
def health():
    return {
        "status": "ok",
        "slides": CORE_COUNT,
        "all_slides": len(ALL_SLIDES),
        "pdf_pages": CORE_COUNT + len(CASES),
        "pdf_all_pages": len(ALL_SLIDES) + len(CASES),
        "slide_keys": [slide["key"] for slide in ALL_SLIDES],
        "teaching_seconds": 4200,
        "discussion_seconds": 1200,
    }


@server.get("/presenter")
def presenter():
    return render_template(
        "presenter.html",
        slides=presenter_slides(),
        core_count=CORE_COUNT,
        deck_url=REQUESTS_PREFIX,
    )


@server.get("/erw-review")
def erw_review():
    import json

    path = ROOT / "data/erw_review.json"
    if not path.exists():
        abort(404)
    return render_template(
        "erw_review.html", review=json.loads(path.read_text()),
        campaign=compare.campaign_results(), prefix=REQUESTS_PREFIX
    )


@server.get("/erw-inventory.xlsx")
def erw_workbook():
    return send_from_directory(
        ROOT / "data", "coastal_erw_ei312.xlsx", as_attachment=True
    )


@server.get("/erw-campaign-inventory.xlsx")
def erw_campaign_workbook():
    return send_from_directory(
        ROOT / "data", "coastal_erw_campaign.xlsx", as_attachment=True
    )


def pdf_deck(include_backups=False):
    pages=[]
    for i in range(len(ALL_SLIDES) if include_backups else CORE_COUNT):
        key=ALL_SLIDES[i]["key"]
        if key=="supply-chain":
            pages.extend(render_slide(i,print_mode=True,process_case=c) for c in CASES)
        elif key=="pulse-equivalence":
            pages.extend(render_slide(i,print_mode=True,pulse_view=v) for v in ("method","cases"))
        else:
            pages.append(render_slide(i,print_mode=True))
    return pages


app.layout = html.Div(
    [
        dcc.Location(id="location", refresh=False),
        dcc.Store(id="current-slide", storage_type="session", data=0),
        dcc.Store(id="presenter-sync"),
        dcc.Store(id="print-trigger"),
        dcc.Store(id="print-complete"),
        html.Header(
            [
                html.A(
                    [
                        html.Img(
                            src=REQUESTS_PREFIX + "shared/psi-mark.svg",
                            className="psi-mark",
                            alt="Paul Scherrer Institut",
                        ),
                        html.Div(
                            [
                                html.Strong("PSI · Energy Systems Analyses"),
                                html.Span("Why timing matters in LCA"),
                            ],
                            className="brand-copy",
                        ),
                    ],
                    href="/",
                    className="brand-lockup",
                ),
                html.Nav(
                    [
                        html.Button(
                            label,
                            id={"type": "snu-chapter", "slide": index},
                            className="chapter-button",
                        )
                        for label, index in CHAPTERS
                    ],
                    className="chapter-nav",
                    **{"aria-label": "Presentation chapters"},
                ),
                html.Div(
                    [
                        html.Strong("Seoul National University"),
                        html.Span("30 October 2026 · guest lecture"),
                    ],
                    className="snu-event",
                ),
            ],
            className="app-header",
        ),
        html.Div(
            html.Div(id="progress-fill", className="progress-fill"),
            className="progress-track",
        ),
        html.Main(id="stage", className="slide-stage"),
        html.Footer(
            [
                html.Button(
                    "← Back", id="previous-button", className="nav-button nav-secondary"
                ),
                html.Div(
                    [
                        html.Button(
                            "↓ Export PDF",
                            id="pdf-button",
                            className="nav-button pdf-export-button",
                        ),
                        dcc.Checklist(
                            id="print-backups",
                            options=[{"label": "Include backup", "value": "yes"}],
                            value=[],
                            inline=True,
                        ),
                    ],
                    className="export-controls",
                ),
                html.Div(
                    [
                        html.Span(id="slide-counter"),
                        html.Button(
                            "Full screen",
                            id="fullscreen-button",
                            className="footer-link",
                        ),
                        html.Button(
                            "Backup", id="backup-button", className="footer-link"
                        ),
                    ],
                    className="footer-hint setac-footer-tools",
                ),
                html.Button(
                    "Next →", id="next-button", className="nav-button nav-primary"
                ),
            ],
            className="app-footer",
        ),
        html.Div(id="print-status", className="print-status", role="status"),
        html.Div(id="print-deck", className="print-deck", **{"aria-hidden": "true"}),
    ],
    className="app-shell setac-app snu-app",
)


def slide_index(value):
    try:
        return max(0, min(len(ALL_SLIDES) - 1, int(value or 0)))
    except (ValueError, TypeError, OverflowError):
        return 0


@app.callback(
    Output("current-slide", "data"),
    Input("previous-button", "n_clicks"),
    Input("next-button", "n_clicks"),
    Input("backup-button", "n_clicks"),
    Input({"type": "snu-chapter", "slide": ALL}, "n_clicks"),
    Input("location", "hash"),
    State("current-slide", "data"),
)
def navigate(previous, following, backup, chapters, fragment, current):
    del previous, following, backup, chapters
    current = slide_index(current)
    trigger = ctx.triggered_id
    if isinstance(trigger, dict):
        return slide_index(trigger["slide"])
    if trigger == "previous-button":
        return max(0, current - 1)
    if trigger == "next-button":
        return min(
            CORE_COUNT - 1 if current < CORE_COUNT else len(ALL_SLIDES) - 1, current + 1
        )
    if trigger == "backup-button":
        return CORE_COUNT if current < CORE_COUNT else CORE_COUNT - 1
    if fragment and fragment.startswith("#slide-"):
        return slide_index(fragment.removeprefix("#slide-"))
    return current


@app.callback(
    Output("stage", "children"),
    Output("slide-counter", "children"),
    Output("previous-button", "disabled"),
    Output("next-button", "disabled"),
    Output("progress-fill", "style"),
    Input("current-slide", "data"),
)
def show_slide(current):
    current = slide_index(current)
    label = (
        f"{current + 1} / {CORE_COUNT}"
        if current < CORE_COUNT
        else f"Backup {current - CORE_COUNT + 1}"
    )
    return (
        render_slide(current),
        label,
        current == 0,
        current in (CORE_COUNT - 1, len(ALL_SLIDES) - 1),
        {"width": f"{min(current, CORE_COUNT - 1) / (CORE_COUNT - 1) * 100:.2f}%"},
    )


app.callback(
    Output("mix-electricity", "figure"),
    Output("mix-heat", "figure"),
    Output("mix-material", "figure"),
    Input("mix-pathway", "value"),
    Input("mix-material-sector", "value"),
)(update_mixes)
app.callback(
    Output("context-chart", "figure"),
    Output("context-region", "options"),
    Output("context-region", "value"),
    Output("context-note", "children"),
    Input("context-indicator", "value"),
    Input("context-region", "value"),
    Input("mix-pathway", "value"),
)(update_context)


@app.callback(
    [Output(f"future-case-{i}", "figure") for i in range(4)]
    + [Output(f"future-score-{i}", "children") for i in range(4)],
    Input("future-pathway", "value"),
)
def update_future_pathway(pathway):
    if pathway not in ("SSP2-NPi", "SSP2-PkBudg1000"):
        raise PreventUpdate
    figures = [attribution.static_figure(case, years=(2025, 2035, 2050),
                co2_terms=True, default_view="activities", pathway=pathway,
                show_scenarios=True) for case in CASES]
    scores = ["2050: " + compare.number(compare.snapshot(case, 2050, pathway)) for case in CASES]
    return figures + scores


@app.callback(
    [Output(f"four-time-{i}", "figure") for i in range(4)],
    Input("erw-duration", "value", allow_optional=True),
    Input("erw-lag", "value", allow_optional=True),
    Input("erw-efficiency", "value", allow_optional=True),
)
def update_erw(duration, lag, efficiency):
    if duration is None and lag is None and efficiency is None:
        raise PreventUpdate
    return tuple(
        compare.temporal_figure(
            c,
            "cumulative",
            duration if duration in (10, 30, 100) else 10,
            lag if lag in (0, 1, 5) else 1,
            efficiency if efficiency in (0.5, 0.8, 1) else 1,
            end=170,
        )
        for c in CASES
    )
@app.callback(
    [Output(f"four-forcing-{i}", "figure") for i in range(4)]
    + [Output(f"four-forcing-area-{i}", "children") for i in range(4)]
    + [Output("response-window-label", "children")],
    Input("response-horizon", "value"),
)
def update_response(window):
    window = compare.response_window(window)
    figures = tuple(compare.forcing_figure(c, window) for c in CASES)
    return (*figures, *(compare.forcing_area_readout(f) for f in figures),
            f"{window[0]:g}–{window[1]:g}")


@app.callback(Output("pulse-timing-chart", "figure"), Input("pulse-delay", "value"))
def update_pulse(delay):
    return compare.pulse_timing_figure(delay if delay in (0, 20, 50) else 0)


@app.callback(
    [Output(f"case-equivalence-{i}", "figure") for i in range(4)]
    + [Output(f"case-equivalence-readout-{i}", "children") for i in range(4)]
    + [Output("case-equivalence-window-summary","children")],
    Input("equivalence-window", "value"),
)
def update_equivalence(window):
    try:
        figures = tuple(pulse_lesson.case_window_figure(c,window or pulse_lesson.DEFAULT_WINDOW) for c in CASES)
    except (TypeError, ValueError):
        figures = tuple(pulse_lesson.case_window_figure(c) for c in CASES)
    meta=figures[0].layout.meta
    return (*figures,*(pulse_lesson.window_readout(f) for f in figures),
            f"{meta['window_start']}–{meta['window_end']} · pulse {meta['reference_year']}")


@app.callback(
    Output("print-deck", "children"),
    Output("print-trigger", "data"),
    Input("pdf-button", "n_clicks"),
    State("print-backups", "value"),
    prevent_initial_call=True,
    running=[(Output("pdf-button", "disabled"), True, False)],
)
def prepare_pdf(clicks, backups):
    if not clicks:
        raise PreventUpdate
    slides = pdf_deck("yes" in (backups or []))
    pending, graph_count = list(slides), 0
    while pending:
        component = pending.pop()
        graph_count += isinstance(component, dcc.Graph)
        children = getattr(component, "children", None)
        pending.extend(
            children
            if isinstance(children, (list, tuple))
            else [children]
            if children is not None
            else []
        )
    return slides, dict(
        click=clicks,
        filename=UPLOAD_NAME,
        slide_count=len(slides),
        graph_count=graph_count,
    )


app.clientside_callback(
    ClientsideFunction(namespace="snu", function_name="syncSlide"),
    Output("presenter-sync", "data"),
    Input("current-slide", "data"),
)
app.clientside_callback(
    ClientsideFunction(namespace="snu", function_name="exportPdf"),
    Output("print-complete", "data"),
    Input("print-trigger", "data"),
    prevent_initial_call=True,
)


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
