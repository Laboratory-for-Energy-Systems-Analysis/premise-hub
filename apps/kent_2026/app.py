from __future__ import annotations

import os
from pathlib import Path

from dash import ALL, ClientsideFunction, Dash, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate
from flask import abort, render_template, send_from_directory

from . import results
from .deck import (
    ALL_SLIDES,
    CORE_COUNT,
    SLIDES,
    UPLOAD_NAME,
    configuration_fingerprint,
    landscape_insights,
    render_slide,
    sensitivity_ladder,
)
from .figures import cumulative_figure, decision_matrix_figure, heatmap_figure

REQUESTS_PREFIX = os.getenv("KENT_2026_REQUESTS_PREFIX", "/")
SHARED_ASSETS = Path(__file__).resolve().parents[1] / "lca_time" / "assets"
SHARED_FILES = {"styles.css", "psi-mark.svg", "cover-iam-trajectories.svg"}
CHAPTERS = [("Mobility + tool", 2), ("Replacement", 6), ("Decision explorer", 8)]

app = Dash(
    __name__,
    title="Kent Seminar · Keep It or Replace It?",
    update_title=None,
    requests_pathname_prefix=REQUESTS_PREFIX,
    suppress_callback_exceptions=True,
    external_stylesheets=[REQUESTS_PREFIX + "shared/styles.css"],
)
server = app.server


@server.get("/shared/<path:filename>")
def shared_asset(filename):
    """Serve the same PSI shell assets used by the other presentation apps."""
    if filename not in SHARED_FILES:
        abort(404)
    return send_from_directory(SHARED_ASSETS, filename)


@server.get("/health")
def health():
    return {"status": "ok", "core_slides": CORE_COUNT, "backup_slides": len(ALL_SLIDES) - CORE_COUNT}


@server.get("/presenter")
def presenter():
    talk_seconds = sum(slide["seconds"] for slide in SLIDES)
    talk_label = f"{talk_seconds // 60:02d}:{talk_seconds % 60:02d}"
    return render_template(
        "presenter.html", slides=ALL_SLIDES, core_count=CORE_COUNT,
        talk_seconds=talk_seconds, talk_label=talk_label, deck_url=REQUESTS_PREFIX,
    )


def pdf_deck(include_backups=False):
    count = len(ALL_SLIDES) if include_backups else CORE_COUNT
    return [render_slide(index, print_mode=True) for index in range(count)]


def graph_count(component):
    if isinstance(component, dcc.Graph):
        return 1
    children = getattr(component, "children", None)
    if children is None:
        return 0
    if not isinstance(children, (list, tuple)):
        children = [children]
    return sum(graph_count(child) for child in children if child is not None)


app.layout = html.Div([
    dcc.Location(id="location", refresh=False),
    dcc.Store(id="current-slide", storage_type="session", data=0),
    dcc.Store(id="presenter-sync"), dcc.Store(id="print-trigger"), dcc.Store(id="print-complete"),
    html.Header([
        html.A([
            html.Img(src=REQUESTS_PREFIX + "shared/psi-mark.svg", className="psi-mark", alt="Paul Scherrer Institute PSI"),
            html.Div([html.Strong("PSI – Laboratory for Energy Systems Analyses"), html.Span("Kent Seminar · LCA of car replacement")], className="brand-copy"),
        ], href="/", className="brand-lockup"),
        html.Nav([html.Button(label, id={"type": "kent-chapter", "slide": slide}, className="chapter-button") for label, slide in CHAPTERS] + [html.Button("Backup slides", id="backup-button", className="chapter-button")], className="chapter-nav", **{"aria-label": "Presentation chapters"}),
        html.Div([html.Strong("University of Kent"), html.Span("12 November 2026"), html.Small("Passenger-car life-cycle assessment")], className="event-lockup kent-event"),
    ], className="app-header"),
    html.Div(html.Div(id="progress-fill", className="progress-fill"), className="progress-track"),
    html.Main(id="stage", className="slide-stage"),
    html.Footer([
        html.Button("← Back", id="previous-button", className="nav-button nav-secondary"),
        html.Div([html.Button([html.Span("↓", className="pdf-export-icon"), html.Span("Export PDF")], id="pdf-button", className="nav-button pdf-export-button"), dcc.Checklist(id="print-backups", options=[{"label": "Include backup", "value": "yes"}], value=[], inline=True)], className="export-controls"),
        html.Div([html.Span(id="slide-counter"), html.Button("Full screen", id="fullscreen-button", className="footer-link")], className="footer-hint kent-footer-tools"),
        html.Button("Next →", id="next-button", className="nav-button nav-primary"),
    ], className="app-footer"),
    html.Div(id="print-status", className="print-status", role="status"),
    html.Div(id="print-deck", className="print-deck", **{"aria-hidden": "true"}),
], className="app-shell kent-app")


def slide_index(value):
    try:
        return max(0, min(len(ALL_SLIDES) - 1, int(value or 0)))
    except (TypeError, ValueError):
        return 0


@app.callback(
    Output("current-slide", "data"),
    Input("previous-button", "n_clicks"), Input("next-button", "n_clicks"), Input("backup-button", "n_clicks"),
    Input({"type": "kent-chapter", "slide": ALL}, "n_clicks"), Input("location", "hash"),
    State("current-slide", "data"),
)
def navigate(previous, following, backup, chapters, fragment, current):
    del previous, following, backup, chapters
    current = slide_index(current)
    trigger = ctx.triggered_id
    if isinstance(trigger, dict): return slide_index(trigger["slide"])
    if trigger == "previous-button": return max(0, current - 1)
    if trigger == "next-button": return min(CORE_COUNT - 1 if current < CORE_COUNT else len(ALL_SLIDES) - 1, current + 1)
    if trigger == "backup-button": return CORE_COUNT if current < CORE_COUNT else CORE_COUNT - 1
    if fragment and fragment.startswith("#slide-"): return slide_index(fragment.removeprefix("#slide-"))
    return current


@app.callback(
    Output("stage", "children"), Output("slide-counter", "children"), Output("previous-button", "disabled"), Output("next-button", "disabled"),
    Output("backup-button", "children"), Output("progress-fill", "style"),
    Input("current-slide", "data"),
)
def show_slide(current):
    current = slide_index(current)
    core = current < CORE_COUNT
    label = f"{current + 1} / {CORE_COUNT}" if core else f"Backup {current - CORE_COUNT + 1} / {len(ALL_SLIDES) - CORE_COUNT}"
    progress = current / max(1, CORE_COUNT - 1) if core else (current - CORE_COUNT) / max(1, len(ALL_SLIDES) - CORE_COUNT - 1)
    return render_slide(current), label, current == 0, current == (CORE_COUNT - 1 if core else len(ALL_SLIDES) - 1), "Backup" if core else "Main deck", {"width": f"{100 * progress:.1f}%"}


@app.callback(
    Output("interactive-map", "figure"),
    Output("config-fingerprint", "children"),
    Output("sensitivity-ladder", "children"),
    Input("map-state", "value"),
    prevent_initial_call=True,
)
def update_map(state):
    state = state or "baseline"
    return heatmap_figure(state), configuration_fingerprint(state), sensitivity_ladder(state)


@app.callback(
    Output("cumulative-interactive", "figure"),
    Output("cumulative-summary", "children"),
    Output("lifetime-readout", "children"),
    Output("mileage-readout", "children"),
    Input("cumulative-lifetime", "value"),
    Input("cumulative-mileage", "value"),
    Input("cumulative-electricity", "value"),
    Input("cumulative-fuel", "value"),
    Input("cumulative-indicator", "value"),
    prevent_initial_call=True,
)
def update_cumulative(lifetime_index, mileage_index, electricity_index, fuel_index, indicator):
    lifetimes = [150_000, 200_000, 250_000, 300_000]
    mileages = [5_000, 8_000, 12_000, 20_000]
    electricity = ["reference", "mid", "transition", "rapid"]
    electricity_labels = ["SSP2-NPi + Reference", "Mid-transition", "SSP2-PkBudg1000 + NDC/LTS", "SSP2-PkBudg650 + 1.5°C"]
    fuels = ["petrol", "e20", "e50", "e85"]
    fuel_labels = ["Petrol", "E20 · corn", "E50 · corn", "E85 · corn"]
    lifetime = lifetimes[int(lifetime_index or 0)]
    mileage = mileages[int(mileage_index or 0)]
    electricity_position = int(electricity_index or 0)
    fuel_position = int(fuel_index or 0)
    data = results.cumulative_sensitivity(
        lifetime_km=lifetime,
        annual_km=mileage,
        electricity=electricity[electricity_position],
        fuel=fuels[fuel_position],
        indicator=indicator or "climate change",
    )
    crossing = str(data["break_even_year"]) if data["break_even_year"] is not None else "—"
    delta = data["delta_2060_t"]
    outcome = "replacement advantage in 2060" if delta < 0 else "keeping advantage in 2060"
    if data["indicator"] == "climate change":
        delta_label = f"{abs(delta):.1f} t CO₂-eq"
    else:
        delta_label = f"{abs(delta):.2f} × 10⁻³ incidences"
    summary = [
        html.Div([html.Strong(crossing), html.Span("sustained break-even" if data["break_even_year"] else "no sustained break-even by 2060")]),
        html.Div([html.Strong(delta_label), html.Span(outcome)]),
        html.Div([
            html.Strong(f"{electricity_labels[electricity_position]} · {fuel_labels[fuel_position]}"),
            html.Span("IAM background + calendar-year GECO charging mix"),
        ]),
    ]
    return (
        cumulative_figure(sensitivity=data, category=data["indicator"]),
        summary,
        f"{lifetime // 1000}k km · {round(lifetime * results.MILES_PER_KM / 1000):.0f}k mi",
        f"{mileage // 1000}k km/y · {mileage * results.MILES_PER_KM / 1000:.1f}k mi/y",
    )


@app.callback(
    Output("decision-landscape", "figure"),
    Output("landscape-insights", "children"),
    Input("landscape-year", "value"),
    Input("landscape-lifetime", "value"),
    Input("landscape-horizon", "value"),
    prevent_initial_call=True,
)
def update_landscape(year_index, lifetime_km, horizon):
    decision_years = [2020, 2026, 2030, 2035]
    decision_year = decision_years[int(year_index or 0)]
    lifetime_km = int(lifetime_km or 200_000)
    horizon = int(horizon or 2040)
    return (
        decision_matrix_figure(decision_year, lifetime_km, horizon),
        landscape_insights(decision_year, lifetime_km, horizon),
    )


@app.callback(Output("location", "hash"), Input("current-slide", "data"))
def update_hash(current):
    return f"#slide-{slide_index(current)}"


app.clientside_callback(ClientsideFunction(namespace="kent", function_name="syncSlide"), Output("presenter-sync", "data"), Input("current-slide", "data"))


@app.callback(Output("print-deck", "children"), Output("print-trigger", "data"), Input("pdf-button", "n_clicks"), State("print-backups", "value"), prevent_initial_call=True)
def prepare_pdf(clicks, backups):
    if not clicks: raise PreventUpdate
    include = "yes" in (backups or [])
    slides = pdf_deck(include)
    return slides, {
        "click": clicks,
        "filename": UPLOAD_NAME,
        "slide_count": len(slides),
        "graph_count": sum(graph_count(slide) for slide in slides),
    }


app.clientside_callback(ClientsideFunction(namespace="kent", function_name="exportPdf"), Output("print-complete", "data"), Input("print-trigger", "data"))


if __name__ == "__main__":
    app.run(debug=True)

