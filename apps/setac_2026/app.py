from __future__ import annotations

import os
from pathlib import Path

from dash import ALL, ClientsideFunction, Dash, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate
from flask import Response, abort, render_template, send_from_directory

from .deck import (
    ALL_SLIDES,
    CORE_COUNT,
    SLIDES,
    UPLOAD_NAME,
    pulse_cards,
    pulse_comparison,
    pulse_configuration,
    pulse_takeaway,
    pulse_window_labels,
    render_slide,
)
from .figures import (
    PATHWAYS,
    forcing_figure,
    mix_figure,
    pulse_figure,
    scenario_context_figure,
    scenario_context_note,
    temporal_figure,
)
from .system_flows import system_flow_svg

REQUESTS_PREFIX = os.getenv("SETAC_2026_REQUESTS_PREFIX", "/")
SHARED_ASSETS = Path(__file__).resolve().parents[1] / "lca_time" / "assets"
SHARED_FILES = {
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
}
CHAPTERS = [
    ("Opening", 0),
    ("Question", 1),
    ("Static", 3),
    ("Prospective", 4),
    ("Time-explicit", 6),
    ("Climate", 8),
]
app = Dash(
    __name__,
    title="SETAC 2026 · Time-explicit LCA",
    update_title=None,
    requests_pathname_prefix=REQUESTS_PREFIX,
    suppress_callback_exceptions=True,
    external_stylesheets=[REQUESTS_PREFIX + "shared/styles.css"],
)
server = app.server


@server.get("/shared/<path:filename>")
def shared_asset(filename):
    """Serve the original lca_time design assets under this app's own prefix."""
    if filename not in SHARED_FILES:
        abort(404)
    return send_from_directory(SHARED_ASSETS, filename)


@server.get("/system-flows.svg")
def system_flows_asset():
    return Response(system_flow_svg(), mimetype="image/svg+xml")


@server.get("/health")
def health():
    return {"status": "ok", "core_slides": CORE_COUNT}


@server.get("/presenter")
def presenter():
    return render_template(
        "presenter.html",
        slides=ALL_SLIDES,
        core_count=CORE_COUNT,
        talk_seconds=720,
        deck_url=REQUESTS_PREFIX,
    )


def pdf_deck(include_backups=False):
    count = len(ALL_SLIDES) if include_backups else CORE_COUNT
    return [render_slide(i, print_mode=True) for i in range(count)]


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
                            alt="Paul Scherrer Institute PSI",
                        ),
                        html.Div(
                            [
                                html.Strong(
                                    "PSI – Laboratory for Energy Systems Analyses"
                                ),
                                html.Span("SETAC 2026 · LCA through time"),
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
                            id={"type": "setac-chapter", "slide": index},
                            n_clicks=0,
                            className="chapter-button",
                        )
                        for label, index in CHAPTERS
                    ]
                    + [
                        html.Button(
                            "Backup slides",
                            id="backup-button",
                            className="chapter-button",
                        ),
                    ],
                    className="chapter-nav",
                    **{"aria-label": "Presentation chapters"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Strong("SETAC Europe"),
                                html.Span("Bruges · 19 October 2026"),
                                html.Small("LCA Case Study Symposium · 1.01.T01"),
                            ],
                            className="setac-event-copy",
                        ),
                        html.Img(
                            src=app.get_asset_url("setac-logo.svg"),
                            alt="SETAC — Society of Environmental Toxicology and Chemistry",
                            className="setac-logo",
                        ),
                    ],
                    className="event-lockup setac-event",
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
                            [
                                html.Span("↓", className="pdf-export-icon"),
                                html.Span("Export PDF"),
                            ],
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
    className="app-shell setac-app",
)


def slide_index(value):
    try:
        return max(0, min(len(ALL_SLIDES) - 1, int(value or 0)))
    except (ValueError, TypeError):
        return 0


@app.callback(
    Output("current-slide", "data"),
    Input("previous-button", "n_clicks"),
    Input("next-button", "n_clicks"),
    Input("backup-button", "n_clicks"),
    Input({"type": "setac-chapter", "slide": ALL}, "n_clicks"),
    Input("location", "hash"),
    State("current-slide", "data"),
)
def navigate(previous, following, backup, chapters, fragment, current):
    del previous, following, backup, chapters
    current = slide_index(current)
    trigger = ctx.triggered_id
    if isinstance(trigger, dict) and trigger.get("type") == "setac-chapter":
        return slide_index(trigger["slide"])
    if trigger == "previous-button":
        return max(0, current - 1)
    if trigger == "next-button":
        limit = CORE_COUNT - 1 if current < CORE_COUNT else len(ALL_SLIDES) - 1
        return min(limit, current + 1)
    if trigger == "backup-button":
        return CORE_COUNT if current < CORE_COUNT else CORE_COUNT - 1
    if fragment and fragment.startswith("#slide-"):
        return slide_index(fragment.removeprefix("#slide-") if fragment else 0)
    return current


@app.callback(
    Output("stage", "children"),
    Output("slide-counter", "children"),
    Output("previous-button", "disabled"),
    Output("next-button", "disabled"),
    Output("backup-button", "children"),
    Output("progress-fill", "style"),
    Input("current-slide", "data"),
)
def show_slide(current):
    current = slide_index(current)
    core = current < CORE_COUNT
    label = (
        f"{current + 1} / {CORE_COUNT}"
        if core
        else f"Backup {current - CORE_COUNT + 1} / {len(ALL_SLIDES) - CORE_COUNT}"
    )
    progress = (
        current / (CORE_COUNT - 1)
        if core
        else (current - CORE_COUNT) / max(1, len(ALL_SLIDES) - CORE_COUNT - 1)
    )
    return (
        render_slide(current),
        label,
        current == 0,
        current in (CORE_COUNT - 1, len(ALL_SLIDES) - 1),
        "Backup slides" if core else "Return to talk",
        {"width": f"{progress * 100:.2f}%"},
    )


@app.callback(Output("forcing-chart", "figure"), Input("forcing-horizon", "value"))
def update_forcing(end):
    return forcing_figure(end if end in (2140, 2300) else 2300)


@app.callback(Output("temporal-chart", "figure"), Input("temporal-view", "value"))
def update_temporal(view):
    return temporal_figure("unstacked" if view == "unstacked" else "stacked")


@app.callback(
    Output("mix-electricity", "figure"),
    Output("mix-heat", "figure"),
    Output("mix-material", "figure"),
    Input("mix-pathway", "value"),
    Input("mix-material-sector", "value"),
)
def update_mixes(pathway, material):
    pathway = pathway if pathway in PATHWAYS else PATHWAYS[1]
    material = (
        material
        if material in ("Steel", "Cement clinker", "Truck transport")
        else "Steel"
    )
    return tuple(
        mix_figure(sector, pathway)
        for sector in ("Electricity", "District heat", material)
    )


@app.callback(
    Output("context-chart", "figure"),
    Output("context-region", "options"),
    Output("context-region", "value"),
    Output("context-note", "children"),
    Input("context-indicator", "value"),
    Input("context-region", "value"),
    Input("mix-pathway", "value"),
)
def update_context(indicator, region, pathway):
    indicator = indicator if indicator in ("GMST", "CO2", "Population") else "GMST"
    region = region if region in ("World", "ENC") and indicator != "GMST" else "World"
    pathway = pathway if pathway in PATHWAYS else PATHWAYS[1]
    options = [
        {"label": "World", "value": "World"},
        {"label": "Northern Europe", "value": "ENC", "disabled": indicator == "GMST"},
    ]
    return (
        scenario_context_figure(indicator, region, pathway),
        options,
        region,
        scenario_context_note(indicator, region),
    )


@app.callback(
    Output("pulse-chart", "figure"),
    Output("pulse-values", "children"),
    Output("pulse-configuration", "children"),
    Output("pulse-window-labels", "children"),
    Output("pulse-comparison", "children"),
    Output("pulse-takeaway", "children"),
    Output("pulse-window", "value"),
    Input("pulse-window", "value"),
)
def update_pulse(window):
    try:
        start, reference, end = [5 * round(float(year) / 5) for year in window]
    except (TypeError, ValueError, OverflowError):
        start, reference, end = 2020, 2030, 2100
    start = max(2000, min(2290, start))
    reference = max(start + 5, min(2295, reference))
    end = max(reference + 5, min(2300, end))
    return (
        pulse_figure(end, start=start, reference=reference),
        pulse_cards(end, start=start, reference=reference),
        pulse_configuration(start, reference, end),
        pulse_window_labels(start, reference, end),
        pulse_comparison(start, reference),
        pulse_takeaway(start, reference, end),
        [start, reference, end],
    )


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
    # Count the rendered graphs so replacing or adding slide content cannot
    # leave the client waiting for an outdated fixed chart count.
    pending = list(slides)
    graph_count = 0
    while pending:
        component = pending.pop()
        if isinstance(component, dcc.Graph):
            graph_count += 1
        children = getattr(component, "children", None)
        if isinstance(children, (list, tuple)):
            pending.extend(children)
        elif children is not None:
            pending.append(children)
    return slides, {
        "click": clicks,
        "filename": UPLOAD_NAME,
        "slide_count": len(slides),
        "graph_count": graph_count,
    }


app.clientside_callback(
    ClientsideFunction(namespace="setac", function_name="syncSlide"),
    Output("presenter-sync", "data"),
    Input("current-slide", "data"),
)
app.clientside_callback(
    ClientsideFunction(namespace="setac", function_name="exportPdf"),
    Output("print-complete", "data"),
    Input("print-trigger", "data"),
    prevent_initial_call=True,
)


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
