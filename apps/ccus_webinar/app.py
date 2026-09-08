from __future__ import annotations

import json
import os
import time

from dash import ALL, ClientsideFunction, Dash, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate
from flask import abort, send_file
from .webinar.editorial import EVIDENCE, ROOT

from .webinar.config import (
    APPENDIX_START_SLIDE,
    CHAPTERS,
    CORE_LAST_SLIDE,
    CORE_SLIDE_COUNT,
    DISCUSSION_SLIDE,
    LAST_SLIDE,
    PRESENTATION_SECONDS,
    SLIDE_TITLES,
    chapter_for_slide,
    slide_seconds,
)
from .webinar.figures import (
    render_fair_response,
    render_pulse_equivalence,
    render_sensitivity,
    render_static_comparison,
    render_temporal_gwp,
    static_takeaway,
    temporal_takeaway,
    fair_takeaway,
    pulse_takeaway,
)
from .webinar.model import DEFAULT_RESULT_STATE
from .webinar.results import RESULT_BUNDLE
from .webinar.static_stages import (
    ELECTRICITY_OPTIONS, render_stage_comparison, compact_subprocess_key,
    sensitivity_selection, sensitivity_takeaway,
)
from .webinar.slides import presenter_notes, render_slide, slide_label

REQUESTS_PREFIX = os.getenv("CCUS_WEBINAR_REQUESTS_PREFIX", "/")

app = Dash(
    __name__,
    title="LCA of CCS and CCUS applied to cement production",
    suppress_callback_exceptions=True,
    update_title=None,
    requests_pathname_prefix=REQUESTS_PREFIX,
    assets_folder="assets",
)
server = app.server
from .webinar.access import install_password_gate
install_password_gate(server)


@server.get("/evidence/<name>")
def evidence_resource(name):
    # Fixed allowlist: project-owned assumptions and aggregated quantities only.
    if name not in EVIDENCE:
        abort(404)
    return send_file(
        ROOT / EVIDENCE[name], mimetype="application/json", as_attachment=False
    )


@server.get("/health")
def health():
    return {
        "status": "ok",
        "results": RESULT_BUNDLE.status,
        "bundle_id": RESULT_BUNDLE.bundle_id,
        "schema_version": RESULT_BUNDLE.manifest.get("schema_version"),
    }, 200


def _make_print_safe(component):
    prop_names = getattr(component, "_prop_names", ())
    if "id" in prop_names:
        component.id = None
    if isinstance(component, html.Button):
        component.disabled = True
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            _make_print_safe(child)
    elif children is not None:
        _make_print_safe(children)
    return component


def render_pdf_deck():
    """Render deterministic curated states and finish on resources/discussion."""

    resources_slide = CORE_LAST_SLIDE - 1
    order = [
        *range(resources_slide),
        *range(APPENDIX_START_SLIDE, LAST_SLIDE + 1),
        resources_slide,
        CORE_LAST_SLIDE,
    ]
    return [
        html.Section(
            _make_print_safe(
                render_slide(index, result_state=DEFAULT_RESULT_STATE, print_mode=True)
            ),
            className="print-page",
            **{"aria-label": slide_label(index)},
        )
        for index in order
    ]


def _header():
    return html.Header(
        [
            html.A(
                [
                    html.Img(
                        src=app.get_asset_url("psi-mark.svg"),
                        className="psi-mark",
                        alt="Paul Scherrer Institut PSI",
                    ),
                    html.Div(
                        [
                            html.Strong("PSI · Laboratory for Energy Systems Analysis"),
                            html.Span("Time in LCA · cement CCS and CCUS"),
                        ],
                        className="brand-copy",
                    ),
                ],
                className="brand-lockup",
                href="/",
            ),
            html.Nav(
                [
                    html.Button(
                        chapter["name"],
                        id={"type": "chapter-button", "slide": chapter["start"]},
                        n_clicks=0,
                        className="chapter-button",
                    )
                    for chapter in CHAPTERS
                ],
                className="chapter-nav",
                **{"aria-label": "Presentation chapters"},
            ),
            html.Div(
                [
                    html.Span("COST ACTION"),
                    html.Strong("TrANsMIT"),
                    html.Small("CA21127"),
                ],
                className="transmit-lockup",
            ),
            html.Div(id="slide-label", className="slide-label"),
        ],
        className="app-header",
    )


def audience_layout():
    return html.Div(
        [
            dcc.Store(id="ccus-slide-store", data=0, storage_type="memory"),
            dcc.Store(id="pdf-export-trigger", data=0),
            dcc.Store(id="pdf-export-complete", data=0),
            _header(),
            html.Div(
                [html.Div(id="progress-fill", className="progress-fill")],
                className="progress-track",
            ),
            html.Main(id="slide-content", className="slide-stage"),
            html.Footer(
                [
                    html.Button(
                        "← Back",
                        id="previous-button",
                        n_clicks=0,
                        className="nav-button nav-secondary",
                        accessKey="p",
                    ),
                    html.Button(
                        "Export PDF",
                        id="pdf-export-button",
                        n_clicks=0,
                        className="nav-button pdf-export-button",
                    ),
                    html.Div(id="chapter-label", className="footer-hint"),
                    html.Button(
                        "Next →",
                        id="next-button",
                        n_clicks=0,
                        className="nav-button nav-primary",
                        accessKey="n",
                    ),
                ],
                className="app-footer",
            ),
            html.Div(id="print-deck", className="print-deck"),
        ],
        className="app-shell audience-shell",
    )


def presenter_layout():
    return html.Div(
        [
            dcc.Interval(id="presenter-interval", interval=500, n_intervals=0),
            dcc.Store(
                id="presenter-master-timer",
                data={"running": False, "elapsed": 0.0, "started": None},
                storage_type="local",
            ),
            dcc.Store(
                id="presenter-slide-timer",
                data={"slide": 0, "elapsed": 0.0, "started": None},
                storage_type="local",
            ),
            html.Header(
                [
                    html.Div(
                        [
                            html.Span("PRIVATE PRESENTER VIEW"),
                            html.Strong("TrANsMIT · CA21127"),
                        ]
                    ),
                    html.A("Open audience view ↗", href="/", target="_blank"),
                ],
                className="presenter-header",
            ),
            html.Main(
                [
                    html.Div(
                        [
                            html.Span(id="presenter-slide-label"),
                            html.H1(id="presenter-title"),
                            html.Div(
                                id="presenter-chapter", className="presenter-chapter"
                            ),
                        ],
                        className="presenter-slide-context",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Small("Presentation"),
                                    html.Strong("45:00", id="presentation-time"),
                                    html.Span("of 45 minutes"),
                                ],
                                id="presentation-clock",
                                className="presenter-clock",
                            ),
                            html.Div(
                                [
                                    html.Small("Current slide"),
                                    html.Strong("00:30", id="slide-time"),
                                    html.Span("resets on slide change"),
                                ],
                                id="slide-clock",
                                className="presenter-clock",
                            ),
                        ],
                        className="presenter-clocks",
                    ),
                    html.Div(
                        [
                            html.Button(
                                "Start presentation", id="timer-start", n_clicks=0
                            ),
                            html.Button("Pause", id="timer-pause", n_clicks=0),
                            html.Button("Reset", id="timer-reset", n_clicks=0),
                        ],
                        className="presenter-timer-controls",
                    ),
                    html.Section(
                        [html.H2("Speaker notes"), html.Ul(id="presenter-notes")],
                        className="speaker-notes",
                    ),
                    html.P(
                        "Use the audience window to change slides and chart settings. This private view follows along and shows your notes and timers.",
                        className="presenter-help",
                    ),
                ],
                className="presenter-stage",
            ),
        ],
        className="presenter-shell",
    )


app.layout = html.Div(
    [
        dcc.Location(id="app-location", refresh=False),
        dcc.Store(id="audience-slide-local", data=0, storage_type="local"),
        html.Div(id="page-content"),
    ]
)


@app.callback(Output("page-content", "children"), Input("app-location", "pathname"))
def route(pathname):
    return (
        presenter_layout()
        if str(pathname or "").rstrip("/").endswith("/presenter")
        else audience_layout()
    )


@app.callback(
    Output("ccus-slide-store", "data"),
    Input("previous-button", "n_clicks"),
    Input("next-button", "n_clicks"),
    Input({"type": "chapter-button", "slide": ALL}, "n_clicks"),
    State("ccus-slide-store", "data"),
    prevent_initial_call=True,
)
def navigate(previous_clicks, next_clicks, chapter_clicks, slide):
    del previous_clicks, next_clicks, chapter_clicks
    slide = int(slide or 0)
    trigger = ctx.triggered_id
    if trigger == "previous-button":
        return max(0, slide - 1)
    if trigger == "next-button":
        return (
            CORE_LAST_SLIDE if slide == CORE_LAST_SLIDE else min(LAST_SLIDE, slide + 1)
        )
    if isinstance(trigger, dict) and trigger.get("type") == "chapter-button":
        return int(trigger["slide"])
    raise PreventUpdate


app.clientside_callback(
    "function(slide){ return slide == null ? 0 : slide; }",
    Output("audience-slide-local", "data"),
    Input("ccus-slide-store", "data"),
)


@app.callback(
    Output("slide-content", "children"),
    Output("slide-label", "children"),
    Output("progress-fill", "style"),
    Output("previous-button", "disabled"),
    Output("next-button", "disabled"),
    Output("chapter-label", "children"),
    Input("ccus-slide-store", "data"),
)
def display_slide(slide):
    slide = int(slide or 0)
    chapter = chapter_for_slide(slide)
    if slide < CORE_SLIDE_COUNT:
        progress = 100 * slide / CORE_LAST_SLIDE
    else:
        progress = (
            100
            * (slide - APPENDIX_START_SLIDE)
            / max(1, LAST_SLIDE - APPENDIX_START_SLIDE)
        )
    return (
        render_slide(slide),
        slide_label(slide),
        {"width": f"{progress:.2f}%"},
        slide == 0,
        slide in {CORE_LAST_SLIDE, LAST_SLIDE},
        (
            f"{slide + 1} / {CORE_SLIDE_COUNT} · {chapter['name']} · {chapter['minutes']:g} min"
            if chapter["minutes"]
            else f"{slide_label(slide)} · {chapter['name']}"
        ),
    )


@app.callback(
    Output("current-static-chart", "figure"),
    Output("current-subprocess-key", "children"),
    Input("current-stage", "value"),
    Input("current-preview-electricity", "value"),
    Input("current-preview-fuel", "value"),
)
def update_current(stage, electricity_index=0, fuel_share=30):
    stage = stage or "synthetic_fuel"
    electricity = ELECTRICITY_OPTIONS[max(0, min(len(ELECTRICITY_OPTIONS) - 1, int(electricity_index or 0)))]
    fuel_share = int(fuel_share if fuel_share is not None else 30)
    return (render_stage_comparison(RESULT_BUNDLE, stage, prototype=True,
                                    electricity=electricity, fuel_share=fuel_share),
            compact_subprocess_key(RESULT_BUNDLE, stage))


@app.callback(Output("current-preview-selection", "children"),
              Input("current-preview-electricity", "value"),
              Input("current-preview-fuel", "value"))
def update_current_preview(electricity_index, share):
    electricity = ELECTRICITY_OPTIONS[max(0, min(len(ELECTRICITY_OPTIONS) - 1, int(electricity_index or 0)))]
    return sensitivity_selection(RESULT_BUNDLE, electricity, share)


@app.callback(Output("future-sector-chart", "figure"),
              Output("future-sector-context", "children"),
              Output("future-metric-note", "children"),
              Output("future-metric", "options"),
              Output("future-metric", "value"),
              Input("future-sector", "value"), Input("future-metric", "value"))
def update_future_sector(sector, metric="shares"):
    from .webinar.future_markets import CONTEXT, sector_figure
    from .webinar.background_gwp import available, gwp_figure, load_scores
    sector = sector if sector in CONTEXT else "Electricity"
    rows = load_scores()
    if not available(sector, rows):
        metric = "shares"
    options = [{"label":"Supply shares", "value":"shares"},
               {"label":"GWP per unit", "value":"gwp", "disabled":not available(sector, rows)}]
    if metric == "gwp" and available(sector, rows):
        figure = gwp_figure(sector, rows)
        note = "IPCC 2021 GWP100 including non-fossil CO₂ · ecoinvent 3.12 cutoff · values for each selected year"
    else:
        figure = sector_figure(RESULT_BUNDLE, sector)
        note = ""
        if sector == "Gas":
            note = "REMIND-EU · ENC gas production by energy · values from the IAM scenario"
    context = CONTEXT[sector]
    if sector == "Electricity":
        if metric == "gwp":
            context = "ENC electricity delivered at low voltage · 1 kWh"
        else:
            context = "Shares: high-voltage generation. GWP: delivered low-voltage electricity."
    return figure, context, note, options, metric


@app.callback(Output("current-stage", "value"), Input("current-static-chart", "clickData"), prevent_initial_call=True)
def inspect_current_stage(click):
    from .lca_model.pipeline import STAGES
    points = (click or {}).get("points", [])
    stage = points[0].get("customdata") if points else None
    if stage not in STAGES:
        raise PreventUpdate
    return stage


@app.callback(
    Output("prospective-static-chart", "figure"),
    Output("prospective-subprocess-key", "children"),
    Output("prospective-selection", "children"),
    Output("prospective-electricity", "disabled"),
    Output("prospective-fuel", "disabled"),
    Output("prospective-fuel", "min"),
    Output("prospective-fuel", "value"),
    Output("prospective-fuel", "marks"),
    Input("prospective-pathway", "value"),
    Input("prospective-year", "value"),
    Input("prospective-stage", "value"),
    Input("prospective-electricity", "value"),
    Input("prospective-fuel", "value"),
    Input("prospective-reference", "value"),
)
def update_prospective(pathway, year, stage, electricity_index, share, reference):
    from .webinar.prospective_results import load_prospective_bundle, prospective_figure, PATHWAYS, YEARS
    from .webinar.static_stages import compact_subprocess_key, sensitivity_selection
    pathway = pathway if pathway in PATHWAYS else "SSP2-NPi"
    year = year if year in YEARS else 2035
    stage = stage or "synthetic_fuel"
    electricity = ELECTRICITY_OPTIONS[max(0,min(4,int(electricity_index or 0)))]
    share = 30 if share is None else share
    bundle = load_prospective_bundle(year,pathway)
    disabled = bundle.status == "invalidated"
    available_shares = sorted({c["fuel_share"] for c in bundle.payloads.get("current_static_sensitivity",{}).get("cells",[])})
    minimum = min(available_shares) if available_shares else 0
    if available_shares and share not in available_shares:
        share = min(available_shares,key=lambda s:abs(s-share))
    note = bundle.message if disabled else f"{year} · " + sensitivity_selection(bundle,electricity,share)
    if minimum:
        note += f" Below {minimum}% unavailable: missing fossil endmember."
    return (prospective_figure(bundle,RESULT_BUNDLE,stage,pathway,electricity,share,bool(reference)),
            compact_subprocess_key(bundle,stage,"prospective_static",pathway),
            note,disabled,disabled,minimum,share,
            {s:f"{s}%" for s in sorted({minimum,50,100}) if s>=minimum})


@app.callback(
    Output("temporal-gwp-chart", "figure"),
    Output("takeaway-gwp-text", "children"),
    Input("gwp-area", "value"),
    Input("gwp-grouping", "value"),
    Input("gwp-normalization", "value"),
)
def update_gwp(area_mode, grouping, normalization):
    return render_temporal_gwp(
        "SSP2-PkBudg1000",
        grouping or "stage",
        area_mode or "stacked",
        normalization or "per_tonne",
        RESULT_BUNDLE,
    ), temporal_takeaway("SSP2-PkBudg1000", RESULT_BUNDLE)


@app.callback(
    Output("fair-response-chart", "figure"),
    Output("takeaway-fair-text", "children"),
    Input("fair-metric", "value"),
    Input("fair-grouping", "value"),
    Input("fair-area", "value"),
    Input("fair-normalization", "value"),
    Input("fair-uncertainty", "value"),
)
def update_fair(metric, grouping, area_mode, normalization, uncertainty):
    metric = metric or "radiative_forcing"
    return render_fair_response(
        "SSP2-PkBudg1000",
        metric,
        grouping or "stage",
        area_mode or "stacked",
        normalization or "per_tonne",
        "show" in (uncertainty or []),
        RESULT_BUNDLE,
    ), fair_takeaway("SSP2-PkBudg1000", metric, RESULT_BUNDLE)


@app.callback(
    Output("pulse-chart", "figure"),
    Output("pulse-endpoints", "children"),
    Output("pulse-window-label", "children"),
    Input("pulse-metric", "value"),
    Input("pulse-normalization", "value"),
    Input("pulse-window", "value"),
    Input("pulse-uncertainty", "value"),
)
def update_pulse(metric, normalization, selection, uncertainty):
    from .webinar.pulse_view import endpoint_cards, pulse_selection
    metric = metric or "forcing"
    start, reference, end = pulse_selection(selection)
    figure = render_pulse_equivalence(
        metric,
        normalization or "per_tonne",
        start,
        end,
        "show" in (uncertainty or []),
        RESULT_BUNDLE,
        reference_year=reference,
    )
    return figure, endpoint_cards(figure), f"Start {start} · pulse {reference} · end {end}"


def _is_available(row: dict) -> bool:
    return str(row.get("available", "true")).lower() in {"1", "true", "yes"}


@app.callback(
    Output("sensitivity-chart", "figure"),
    Output("sensitivity-heat", "options"),
    Output("sensitivity-electricity", "options"),
    Output("sensitivity-fuel", "marks"),
    Output("sensitivity-status", "children"),
    Output("sensitivity-status", "className"),
    Input("sensitivity-heat", "value"),
    Input("sensitivity-electricity", "value"),
    Input("sensitivity-fuel", "value"),
    Input("sensitivity-metric", "value"),
)
def update_sensitivity(heat, electricity, fuel_share, metric):
    heat = heat or "ENC market"
    electricity = electricity or "ENC market"
    fuel_share = int(fuel_share if fuel_share is not None else 60)
    availability = RESULT_BUNDLE.tables.get("sensitivity_availability", ())
    heat_values = [
        "ENC market",
        "biomass CHP",
        "wind heat pump",
        "coal CHP",
        "natural gas CHP",
    ]
    electricity_values = ["ENC market", "wind", "photovoltaic", "natural gas", "coal"]
    if availability:
        usable = [row for row in availability if _is_available(row)]
        heat_options = [
            {
                "label": value,
                "value": value,
                "disabled": not any(
                    row.get("avoided_heat") == value
                    and row.get("operating_electricity") == electricity
                    and int(float(row.get("non_fossil_kiln_share", -1))) == fuel_share
                    for row in usable
                ),
            }
            for value in heat_values
        ]
        electricity_options = [
            {
                "label": value,
                "value": value,
                "disabled": not any(
                    row.get("avoided_heat") == heat
                    and row.get("operating_electricity") == value
                    and int(float(row.get("non_fossil_kiln_share", -1))) == fuel_share
                    for row in usable
                ),
            }
            for value in electricity_values
        ]
        marks = {
            value: {
                "label": f"{value}%",
                "style": {
                    "color": (
                        "#46636e"
                        if any(
                            row.get("avoided_heat") == heat
                            and row.get("operating_electricity") == electricity
                            and int(float(row.get("non_fossil_kiln_share", -1)))
                            == value
                            for row in usable
                        )
                        else "#c1c9cc"
                    )
                },
            }
            for value in range(0, 101, 20)
        }
        combination_available = any(
            row.get("avoided_heat") == heat
            and row.get("operating_electricity") == electricity
            and int(float(row.get("non_fossil_kiln_share", -1))) == fuel_share
            for row in usable
        )
    else:
        heat_options = [{"label": value, "value": value, "disabled": True} for value in heat_values]
        electricity_options = [
            {"label": value, "value": value, "disabled": True} for value in electricity_values
        ]
        marks = {value: f"{value}%" for value in range(0, 101, 20)}
        combination_available = False
    status = (
        "Precomputed combination available"
        if combination_available
        else "No results are available for this combination"
    )
    return (
        render_sensitivity(
            heat, electricity, fuel_share, metric or "cumulative_gwp100", RESULT_BUNDLE
        ),
        heat_options,
        electricity_options,
        marks,
        status,
        (
            "sensitivity-status"
            if combination_available
            else "sensitivity-status sensitivity-missing"
        ),
    )


@app.callback(
    Output("print-deck", "children"),
    Output("pdf-export-trigger", "data"),
    Input("pdf-export-button", "n_clicks"),
    prevent_initial_call=True,
    running=[(Output("pdf-export-button", "disabled"), True, False)],
)
def prepare_pdf_export(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return render_pdf_deck(), n_clicks


app.clientside_callback(
    ClientsideFunction(namespace="ccusWebinar", function_name="exportPdf"),
    Output("pdf-export-complete", "data"),
    Input("pdf-export-trigger", "data"),
    prevent_initial_call=True,
)


def _clock(remaining: float) -> str:
    sign = "−" if remaining < 0 else ""
    seconds = int(abs(round(remaining)))
    return f"{sign}{seconds // 60:02d}:{seconds % 60:02d}"


def _elapsed(timer: dict, now: float) -> float:
    value = float(timer.get("elapsed", 0.0))
    if timer.get("running") and timer.get("started") is not None:
        value += max(0.0, now - float(timer["started"]))
    return value


@app.callback(
    Output("presenter-master-timer", "data"),
    Output("presenter-slide-timer", "data"),
    Output("presentation-time", "children"),
    Output("slide-time", "children"),
    Output("presentation-clock", "className"),
    Output("slide-clock", "className"),
    Output("timer-pause", "children"),
    Output("presenter-slide-label", "children"),
    Output("presenter-title", "children"),
    Output("presenter-chapter", "children"),
    Output("presenter-notes", "children"),
    Input("presenter-interval", "n_intervals"),
    Input("timer-start", "n_clicks"),
    Input("timer-pause", "n_clicks"),
    Input("timer-reset", "n_clicks"),
    State("presenter-master-timer", "data"),
    State("presenter-slide-timer", "data"),
    State("audience-slide-local", "data"),
)
def update_presenter(
    _tick, _start, _pause, _reset, master, slide_timer, audience_slide
):
    del _tick, _start, _pause, _reset
    now = time.time()
    slide = max(0, min(LAST_SLIDE, int(audience_slide or 0)))
    master = dict(master or {"running": False, "elapsed": 0.0, "started": None})
    slide_timer = dict(slide_timer or {"slide": slide, "elapsed": 0.0, "started": None})
    trigger = ctx.triggered_id
    if trigger == "timer-reset":
        master = {"running": False, "elapsed": 0.0, "started": None}
        slide_timer = {"slide": slide, "elapsed": 0.0, "started": None}
    elif trigger == "timer-start" and not master.get("running"):
        master = {**master, "running": True, "started": now}
        slide_timer = {"slide": slide, "elapsed": 0.0, "running": True, "started": now}
    elif trigger == "timer-pause":
        if master.get("running"):
            master = {
                "running": False,
                "elapsed": _elapsed(master, now),
                "started": None,
            }
            slide_timer = {
                **slide_timer,
                "running": False,
                "elapsed": _elapsed(slide_timer, now),
                "started": None,
            }
        else:
            master = {**master, "running": True, "started": now}
            slide_timer = {**slide_timer, "running": True, "started": now}
    if int(slide_timer.get("slide", -1)) != slide:
        slide_timer = {
            "slide": slide,
            "running": bool(master.get("running")),
            "elapsed": 0.0,
            "started": now if master.get("running") else None,
        }
    master_remaining = PRESENTATION_SECONDS - _elapsed(master, now)
    slide_remaining = slide_seconds(slide) - _elapsed(slide_timer, now)
    chapter = chapter_for_slide(slide)
    return (
        master,
        slide_timer,
        _clock(master_remaining),
        _clock(slide_remaining),
        "presenter-clock overrun" if master_remaining < 0 else "presenter-clock",
        "presenter-clock overrun" if slide_remaining < 0 else "presenter-clock",
        "Pause" if master.get("running") else "Resume",
        slide_label(slide),
        SLIDE_TITLES[slide],
        chapter["name"],
        [html.Li(note) for note in presenter_notes(slide)],
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
