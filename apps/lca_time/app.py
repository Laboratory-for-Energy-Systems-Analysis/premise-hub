from __future__ import annotations

import os

from dash import ALL, ClientsideFunction, Dash, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate

from .workshop.config import (
    APPENDIX_START_SLIDE,
    CHAPTERS,
    CORE_LAST_SLIDE,
    CORE_SLIDE_COUNT,
    LAST_SLIDE,
    chapter_for_slide,
)
from .workshop.slides import (
    FAIR_RESPONSE_COMPARISON_YEAR,
    fair_response_comparison_year,
    prospective_driver_heading,
    prospective_insight,
    pulse_equivalence_selection,
    pulse_equivalence_value_label,
    render_co2_pulse_equivalence_figure,
    fair_response_value_label,
    fair_response_year_value_label,
    render_fair_response_figure,
    render_prospective_burden_figure,
    render_prospective_driver_figure,
    render_prospective_driver_legend,
    render_slide,
    render_static_contribution_legend,
    render_static_contribution_view,
    render_temporal_gwp_figure,
    slide_label,
    temporal_gwp_total_label,
)

REQUESTS_PREFIX = os.getenv("LCA_TIME_REQUESTS_PREFIX", "/")

app = Dash(
    __name__,
    title="LCA through time · LCSS 2026",
    suppress_callback_exceptions=True,
    update_title=None,
    requests_pathname_prefix=REQUESTS_PREFIX,
    assets_folder="assets",
)
server = app.server


@server.get("/health")
def health():
    return {"status": "ok"}, 200


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
    return [
        html.Section(
            _make_print_safe(render_slide(index, print_mode=True)),
            className="print-page",
            **{"aria-label": slide_label(index)},
        )
        for index in range(LAST_SLIDE + 1)
    ]


app.layout = html.Div(
    [
        dcc.Store(id="lca-time-slide-store", data=0, storage_type="session"),
        dcc.Store(
            id="fair-response-year-store",
            data=FAIR_RESPONSE_COMPARISON_YEAR,
            storage_type="session",
        ),
        dcc.Store(id="pdf-export-trigger", data=0),
        dcc.Store(id="pdf-export-complete", data=0),
        html.Header(
            [
                html.A(
                    [
                        html.Img(
                            src=app.get_asset_url("psi-mark.svg"),
                            className="psi-mark",
                            alt="Paul Scherrer Institute PSI",
                            title="Paul Scherrer Institute",
                        ),
                        html.Div(
                            [
                                html.Strong(
                                    "PSI – Laboratory for Energy Systems Analyses"
                                ),
                                html.Span("LCSS 2026 · LCA through time"),
                            ],
                            className="brand-copy",
                        ),
                    ],
                    href="/",
                    className="brand-lockup",
                    title="Paul Scherrer Institute",
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
                        html.A(
                            html.Img(
                                src=app.get_asset_url("fslci-logo.png"),
                                className="fslci-logo",
                                alt="Forum for Sustainability through Life Cycle Innovation",
                            ),
                            href="https://fslci.org/",
                            target="_blank",
                            rel="noopener noreferrer",
                            className="fslci-lockup",
                            title="Forum for Sustainability through Life Cycle Innovation",
                        ),
                        html.A(
                            html.Img(
                                src=app.get_asset_url("lcss-logo.png"),
                                className="lcss-logo",
                                alt="Life Cycle Summer School",
                            ),
                            href="https://fslci.org/events/lcss2026/",
                            target="_blank",
                            rel="noopener noreferrer",
                            className="lcss-lockup",
                            title="Life Cycle Summer School 2026",
                        ),
                    ],
                    className="event-lockup",
                ),
                html.Div(id="slide-label", className="slide-label"),
            ],
            className="app-header",
        ),
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
                ),
                html.Button(
                    [
                        html.Span(
                            "↓",
                            className="pdf-export-icon",
                            **{"aria-hidden": "true"},
                        ),
                        html.Span("Export PDF", className="pdf-export-label"),
                    ],
                    id="pdf-export-button",
                    n_clicks=0,
                    className="nav-button pdf-export-button",
                    title="Prepare all slides and open the browser's PDF print dialog",
                    **{"aria-label": "Export the presentation as a PDF"},
                ),
                html.Div(id="chapter-label", className="footer-hint"),
                html.Button(
                    "Next →",
                    id="next-button",
                    n_clicks=0,
                    className="nav-button nav-primary",
                ),
            ],
            className="app-footer",
        ),
        html.Div(id="print-deck", className="print-deck"),
    ],
    className="app-shell",
)


@app.callback(
    Output("lca-time-slide-store", "data"),
    Input("previous-button", "n_clicks"),
    Input("next-button", "n_clicks"),
    Input({"type": "chapter-button", "slide": ALL}, "n_clicks"),
    State("lca-time-slide-store", "data"),
    prevent_initial_call=True,
)
def navigate(previous_clicks, next_clicks, chapter_clicks, slide):
    del previous_clicks, next_clicks, chapter_clicks
    slide = int(slide or 0)
    trigger = ctx.triggered_id
    if trigger == "previous-button":
        return max(0, slide - 1)
    if trigger == "next-button":
        if slide == CORE_LAST_SLIDE:
            return CORE_LAST_SLIDE
        return min(LAST_SLIDE, slide + 1)
    if isinstance(trigger, dict) and trigger.get("type") == "chapter-button":
        return int(trigger["slide"])
    raise PreventUpdate


@app.callback(
    Output("slide-content", "children"),
    Output("slide-label", "children"),
    Output("progress-fill", "style"),
    Output("previous-button", "disabled"),
    Output("next-button", "disabled"),
    Output("chapter-label", "children"),
    Input("lca-time-slide-store", "data"),
)
def display_slide(slide):
    slide = int(slide or 0)
    chapter = chapter_for_slide(slide)
    if slide < CORE_SLIDE_COUNT:
        progress = 100 * slide / CORE_LAST_SLIDE if CORE_LAST_SLIDE else 100
    else:
        appendix_offset = slide - APPENDIX_START_SLIDE
        appendix_span = LAST_SLIDE - APPENDIX_START_SLIDE
        progress = 100 * appendix_offset / appendix_span if appendix_span else 100
    return (
        render_slide(slide),
        slide_label(slide),
        {"width": f"{progress:.2f}%"},
        slide == 0,
        slide in {CORE_LAST_SLIDE, LAST_SLIDE},
        chapter["name"],
    )


@app.callback(
    Output("case-focus-view", "className"),
    Input("case-focus-control", "value"),
)
def display_case_focus(focus):
    focus = focus if focus in {"beccs", "daccs", "both"} else "both"
    return f"case-study-comparison focus-{focus}"


@app.callback(
    Output("beccs-system-state-view", "className"),
    Input("beccs-system-state-control", "value"),
)
def display_beccs_system_state(state):
    state = state if state in {"reference", "project", "balance"} else "reference"
    return f"system-boundary-layout system-boundary-beccs system-state-{state}"


@app.callback(
    Output("daccs-system-state-view", "className"),
    Input("daccs-system-state-control", "value"),
)
def display_daccs_system_state(state):
    state = (
        state
        if state in {"capture", "regeneration", "transport", "full"}
        else "capture"
    )
    return f"system-boundary-layout system-boundary-daccs system-state-{state}"


@app.callback(
    Output("scenario-focus-view", "className"),
    Input("scenario-focus-control", "value"),
)
def display_scenario_focus(focus):
    focus = (
        focus
        if focus in {"electricity", "heat", "materials", "summary"}
        else "electricity"
    )
    return f"scenario-focus-view scenario-focus-{focus}"


@app.callback(
    Output("method-focus-view", "className"),
    Input("method-focus-control", "value"),
)
def display_method_focus(focus):
    focus = focus if focus in {"compare", "decide"} else "compare"
    return f"method-focus-view method-focus-{focus}"


@app.callback(
    Output("contribution-chart", "children"),
    Output("contribution-legend", "children"),
    Input("contribution-view-toggle", "value"),
)
def display_contribution_view(view):
    view = view or "step"
    return render_static_contribution_view(view), render_static_contribution_legend(
        view
    )


@app.callback(
    Output("case-timing-image", "src"),
    Input("case-timing-year", "value"),
)
def display_case_timing_year(year):
    year = str(year or "2030")
    if year not in {"2030", "2040", "2049", "2050"}:
        year = "2030"
    return f"assets/case-temporal-distributions.svg#y{year}"


@app.callback(
    Output("prospective-driver-chart", "figure"),
    Output("prospective-driver-kicker", "children"),
    Output("prospective-driver-title", "children"),
    Output("prospective-driver-legend", "children"),
    Output("prospective-beccs-chart", "figure"),
    Output("prospective-daccs-chart", "figure"),
    Input("prospective-view-control", "value"),
    Input("prospective-year-control", "value"),
    Input("prospective-contribution-control", "value"),
)
def display_prospective_analysis(view, focus_year, contribution):
    view = view or "absolute"
    focus_year = focus_year or "all"
    contribution = contribution or "all"
    kicker, title = prospective_driver_heading(contribution)
    return (
        render_prospective_driver_figure(contribution, focus_year),
        kicker,
        title,
        render_prospective_driver_legend(contribution),
        render_prospective_burden_figure("BECCS", view, focus_year, contribution),
        render_prospective_burden_figure("DACCS", view, focus_year, contribution),
    )


@app.callback(
    Output("prospective-insight-copy", "children"),
    Input("prospective-view-control", "value"),
    Input("prospective-year-control", "value"),
    Input("prospective-contribution-control", "value"),
    Input("prospective-beccs-chart", "hoverData"),
    Input("prospective-daccs-chart", "hoverData"),
)
def display_prospective_insight(
    view, focus_year, contribution, beccs_hover, daccs_hover
):
    hover_data = None
    if ctx.triggered_id == "prospective-beccs-chart":
        hover_data = beccs_hover
    elif ctx.triggered_id == "prospective-daccs-chart":
        hover_data = daccs_hover
    return prospective_insight(
        view or "absolute",
        focus_year or "all",
        contribution or "all",
        hover_data,
    )


@app.callback(
    Output("temporal-gwp-beccs-chart", "figure"),
    Output("temporal-gwp-daccs-chart", "figure"),
    Output("temporal-gwp-beccs-total", "children"),
    Output("temporal-gwp-daccs-total", "children"),
    Input("temporal-gwp-normalization-toggle", "value"),
    Input("temporal-gwp-area-toggle", "value"),
)
def display_temporal_gwp(normalization, area_mode):
    normalization = normalization or "per_tonne"
    area_mode = area_mode or "stacked"
    return (
        render_temporal_gwp_figure("BECCS", normalization, area_mode),
        render_temporal_gwp_figure("DACCS", normalization, area_mode),
        temporal_gwp_total_label("BECCS", normalization),
        temporal_gwp_total_label("DACCS", normalization),
    )


@app.callback(
    Output("fair-response-year-store", "data"),
    Input("fair-response-beccs-chart", "relayoutData"),
    State("fair-response-year-store", "data"),
    prevent_initial_call=True,
)
def update_fair_response_year(relayout_data, current_year):
    current_year = current_year or FAIR_RESPONSE_COMPARISON_YEAR
    comparison_year = fair_response_comparison_year(relayout_data, current_year)
    if comparison_year == current_year:
        raise PreventUpdate
    return comparison_year


@app.callback(
    Output("fair-response-beccs-chart", "figure"),
    Output("fair-response-daccs-chart", "figure"),
    Output("fair-response-beccs-selected-value", "children"),
    Output("fair-response-daccs-selected-value", "children"),
    Output("fair-response-beccs-value", "children"),
    Output("fair-response-daccs-value", "children"),
    Input("fair-response-metric-toggle", "value"),
    Input("fair-response-view-toggle", "value"),
    Input("fair-response-year-store", "data"),
)
def display_fair_response(
    metric,
    contribution_view,
    comparison_year=FAIR_RESPONSE_COMPARISON_YEAR,
):
    metric = metric or "radiative forcing"
    contribution_view = contribution_view or "process"
    comparison_year = comparison_year or FAIR_RESPONSE_COMPARISON_YEAR
    return (
        render_fair_response_figure(
            "BECCS", metric, contribution_view, comparison_year
        ),
        render_fair_response_figure(
            "DACCS", metric, contribution_view, comparison_year
        ),
        fair_response_year_value_label(
            "BECCS", metric, contribution_view, comparison_year
        ),
        fair_response_year_value_label(
            "DACCS", metric, contribution_view, comparison_year
        ),
        fair_response_value_label("BECCS", metric, contribution_view),
        fair_response_value_label("DACCS", metric, contribution_view),
    )


@app.callback(
    Output("pulse-equivalence-chart", "figure"),
    Output("pulse-equivalence-beccs-value", "children"),
    Output("pulse-equivalence-daccs-value", "children"),
    Output("pulse-equivalence-window-label", "children"),
    Input("pulse-equivalence-metric-toggle", "value"),
    Input("pulse-equivalence-window-slider", "value"),
)
def display_pulse_equivalence(metric, selection):
    metric = metric or "radiative forcing"
    window_start, reference_year, window_end = pulse_equivalence_selection(selection)
    return (
        render_co2_pulse_equivalence_figure(
            metric, window_start, window_end, reference_year
        ),
        pulse_equivalence_value_label(
            "BECCS", metric, window_start, window_end, reference_year
        ),
        pulse_equivalence_value_label(
            "DACCS", metric, window_start, window_end, reference_year
        ),
        f"Start {window_start} · reference pulse {reference_year} · end {window_end}",
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
    ClientsideFunction(namespace="workshop", function_name="syncProspectiveHover"),
    Output("prospective-hover-sync", "data"),
    Input("prospective-beccs-chart", "hoverData"),
    Input("prospective-daccs-chart", "hoverData"),
    prevent_initial_call=True,
)


app.clientside_callback(
    ClientsideFunction(namespace="workshop", function_name="exportPdf"),
    Output("pdf-export-complete", "data"),
    Input("pdf-export-trigger", "data"),
    prevent_initial_call=True,
)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
