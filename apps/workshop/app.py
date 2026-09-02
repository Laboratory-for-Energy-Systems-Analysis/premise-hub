from __future__ import annotations

import os

from dash import ALL, ClientsideFunction, Dash, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate

from .workshop.config import (
    ANONYMOUS_SLIDE,
    APPENDIX_START_SLIDE,
    CHAPTERS,
    CORE_LAST_SLIDE,
    CORE_SLIDE_COUNT,
    LAST_SLIDE,
    chapter_for_slide,
)
from .workshop.slides import (
    configure_asset_prefix,
    render_slide,
    slide_label,
    slide_number,
    style_premise_text,
)

REQUESTS_PREFIX = os.getenv("WORKSHOP_REQUESTS_PREFIX", "/")
configure_asset_prefix(REQUESTS_PREFIX)

app = Dash(
    __name__,
    title="IAM Scenarios for Prospective LCA",
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
    """Remove callback IDs from a freshly rendered slide tree."""
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


def render_pdf_deck(votes, explore, capstone, iam_map):
    """Render every presenter state for the browser's PDF print view."""
    return [
        html.Section(
            [
                _make_print_safe(
                    render_slide(
                        index,
                        1,  # A static export needs the anonymous labels revealed.
                        votes,
                        explore,
                        capstone,
                        iam_map,
                    )
                ),
                html.Span(slide_number(index), className="print-slide-number"),
            ],
            className="print-page",
            **{"aria-label": slide_label(index)},
        )
        for index in range(LAST_SLIDE + 1)
    ]


app.layout = html.Div(
    [
        dcc.Store(id="slide-store", data=0, storage_type="session"),
        dcc.Store(id="reveal-store", data=0, storage_type="session"),
        dcc.Store(id="backup-return-store", data=0, storage_type="session"),
        dcc.Store(
            id="vote-store",
            data={"A": 0, "B": 0, "C": 0, "D": 0},
            storage_type="session",
        ),
        dcc.Store(
            id="explore-store",
            data={"sector": "Electricity", "year": 2060, "mode": "share"},
            storage_type="session",
        ),
        dcc.Store(id="iam-map-store", data="image", storage_type="session"),
        dcc.Store(id="pdf-export-trigger", data=0),
        dcc.Store(id="pdf-export-complete", data=0),
        dcc.Store(
            id="capstone-store",
            data={
                "case": "steel",
                "scenario": "SSP2-VLHO",
                "year": 2060,
                "indicator": "climate",
            },
            storage_type="session",
        ),
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
                                    "PSI - Laboratory for Energy Systems Analyses"
                                ),
                                html.Span("IAM scenarios · prospective LCA"),
                            ],
                            className="brand-copy",
                        ),
                    ],
                    className="brand-lockup",
                    href="/",
                    title="Back to Premise resources",
                ),
                html.Nav(
                    [
                        html.Button(
                            style_premise_text(chapter["name"]),
                            id={"type": "chapter-button", "slide": chapter["start"]},
                            n_clicks=0,
                            className="chapter-button",
                        )
                        for chapter in CHAPTERS
                    ],
                    className="chapter-nav",
                    **{"aria-label": "Workshop chapters"},
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
                    accessKey="p",
                ),
                html.Button(
                    "Reveal",
                    id="reveal-button",
                    n_clicks=0,
                    className="nav-button reveal-button",
                    accessKey="r",
                ),
                html.Button(
                    [
                        html.Span(
                            "↓", className="pdf-export-icon", **{"aria-hidden": "true"}
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
                html.Div(id="slide-number", className="slide-number"),
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
    className="app-shell",
)


@app.callback(
    Output("print-deck", "children"),
    Output("pdf-export-trigger", "data"),
    Input("pdf-export-button", "n_clicks"),
    State("vote-store", "data"),
    State("explore-store", "data"),
    State("iam-map-store", "data"),
    State("capstone-store", "data"),
    prevent_initial_call=True,
    running=[(Output("pdf-export-button", "disabled"), True, False)],
)
def prepare_pdf_export(n_clicks, votes, explore, iam_map, capstone):
    if not n_clicks:
        raise PreventUpdate
    votes = votes or {"A": 0, "B": 0, "C": 0, "D": 0}
    return render_pdf_deck(votes, explore, capstone, iam_map), n_clicks


app.clientside_callback(
    ClientsideFunction(namespace="workshop", function_name="exportPdf"),
    Output("pdf-export-complete", "data"),
    Input("pdf-export-trigger", "data"),
    prevent_initial_call=True,
)


@app.callback(
    Output("slide-store", "data"),
    Output("reveal-store", "data"),
    Output("backup-return-store", "data"),
    Input("previous-button", "n_clicks"),
    Input("next-button", "n_clicks"),
    Input("reveal-button", "n_clicks"),
    Input({"type": "chapter-button", "slide": ALL}, "n_clicks"),
    Input({"type": "backup-button", "slide": ALL}, "n_clicks"),
    Input({"type": "return-from-backup", "slide": ALL}, "n_clicks"),
    State("slide-store", "data"),
    State("reveal-store", "data"),
    State("backup-return-store", "data"),
    prevent_initial_call=True,
)
def navigate(
    previous_clicks,
    next_clicks,
    reveal_clicks,
    chapter_clicks,
    backup_clicks,
    return_clicks,
    slide,
    reveal,
    backup_return,
):
    del (
        previous_clicks,
        next_clicks,
        reveal_clicks,
        chapter_clicks,
        backup_clicks,
        return_clicks,
    )
    trigger = ctx.triggered_id
    trigger_value = ctx.triggered[0].get("value") if ctx.triggered else None
    slide = int(slide or 0)
    reveal = int(reveal or 0)
    backup_return = int(backup_return or 0)
    if trigger == "previous-button":
        return max(0, slide - 1), 0, backup_return
    if trigger == "next-button":
        if slide == CORE_LAST_SLIDE:
            return CORE_LAST_SLIDE, 0, backup_return
        return min(LAST_SLIDE, slide + 1), 0, backup_return
    if trigger == "reveal-button":
        if slide == ANONYMOUS_SLIDE:
            return slide, 0 if reveal else 1, backup_return
    if isinstance(trigger, dict) and trigger.get("type") == "chapter-button":
        target = int(trigger["slide"])
        if target >= APPENDIX_START_SLIDE:
            origin = slide if slide < APPENDIX_START_SLIDE else backup_return
        else:
            origin = target
        return target, 0, origin
    if isinstance(trigger, dict) and trigger.get("type") == "backup-button":
        if not trigger_value:
            raise PreventUpdate
        target = int(trigger["slide"])
        if target < APPENDIX_START_SLIDE or target > LAST_SLIDE:
            raise PreventUpdate
        origin = slide if slide < APPENDIX_START_SLIDE else backup_return
        return target, 0, origin
    if isinstance(trigger, dict) and trigger.get("type") == "return-from-backup":
        if not trigger_value:
            raise PreventUpdate
        target = (
            backup_return
            if 0 <= backup_return < APPENDIX_START_SLIDE
            else CORE_LAST_SLIDE
        )
        return target, 0, target
    raise PreventUpdate


@app.callback(
    Output("explore-store", "data"),
    Input({"type": "explore-year", "value": ALL}, "n_clicks"),
    Input({"type": "explore-mode", "value": ALL}, "n_clicks"),
    Input({"type": "explore-sector", "value": ALL}, "n_clicks"),
    State("explore-store", "data"),
    prevent_initial_call=True,
)
def update_explorer(year_clicks, mode_clicks, sector_clicks, current):
    del year_clicks, mode_clicks, sector_clicks
    trigger = ctx.triggered_id
    trigger_value = ctx.triggered[0].get("value") if ctx.triggered else None
    if not isinstance(trigger, dict) or not trigger_value:
        raise PreventUpdate
    updated = {"sector": "Electricity", "year": 2060, "mode": "share"}
    updated.update(current or {})
    if trigger.get("type") == "explore-year":
        updated["year"] = int(trigger["value"])
    elif trigger.get("type") == "explore-mode":
        updated["mode"] = trigger["value"]
    elif trigger.get("type") == "explore-sector":
        updated["sector"] = trigger["value"]
    else:
        raise PreventUpdate
    return updated


@app.callback(
    Output("iam-map-store", "data"),
    Input({"type": "iam-map-model", "value": ALL}, "n_clicks"),
    State("iam-map-store", "data"),
    prevent_initial_call=True,
)
def update_iam_map(clicks, current):
    del clicks, current
    trigger = ctx.triggered_id
    trigger_value = ctx.triggered[0].get("value") if ctx.triggered else None
    if not isinstance(trigger, dict) or not trigger_value:
        raise PreventUpdate
    model = str(trigger.get("value", "image"))
    if model not in {"image", "message", "remind", "remind-eu", "tiam-ucl", "gcam"}:
        raise PreventUpdate
    return model


@app.callback(
    Output("capstone-store", "data"),
    Input({"type": "capstone-case", "value": ALL}, "n_clicks"),
    Input({"type": "capstone-scenario", "value": ALL}, "n_clicks"),
    Input({"type": "capstone-year", "value": ALL}, "n_clicks"),
    Input({"type": "capstone-indicator", "value": ALL}, "n_clicks"),
    State("capstone-store", "data"),
    prevent_initial_call=True,
)
def update_capstone(
    case_clicks, scenario_clicks, year_clicks, indicator_clicks, current
):
    del case_clicks, scenario_clicks, year_clicks, indicator_clicks
    trigger = ctx.triggered_id
    trigger_value = ctx.triggered[0].get("value") if ctx.triggered else None
    if not isinstance(trigger, dict) or not trigger_value:
        raise PreventUpdate
    updated = {
        "case": "steel",
        "scenario": "SSP2-VLHO",
        "year": 2060,
        "indicator": "climate",
    }
    updated.update(current or {})
    if trigger.get("type") == "capstone-case":
        updated["case"] = str(trigger["value"])
    elif trigger.get("type") == "capstone-scenario":
        updated["scenario"] = str(trigger["value"])
    elif trigger.get("type") == "capstone-year":
        updated["year"] = int(trigger["value"])
    elif trigger.get("type") == "capstone-indicator":
        updated["indicator"] = str(trigger["value"])
    else:
        raise PreventUpdate
    return updated


@app.callback(
    Output("vote-store", "data"),
    Input({"type": "vote-button", "choice": ALL}, "n_clicks"),
    State("vote-store", "data"),
    prevent_initial_call=True,
)
def record_vote(clicks, votes):
    del clicks
    trigger = ctx.triggered_id
    trigger_value = ctx.triggered[0].get("value") if ctx.triggered else None
    if not isinstance(trigger, dict):
        raise PreventUpdate
    if not trigger_value:
        # Dynamic vote buttons are inserted whenever their slide is rendered.
        # Their initial n_clicks=0 event is not a hand raised.
        raise PreventUpdate
    choice = trigger.get("choice")
    if choice not in {"A", "B", "C", "D"}:
        raise PreventUpdate
    updated = {"A": 0, "B": 0, "C": 0, "D": 0}
    updated.update(votes or {})
    updated[choice] += 1
    return updated


@app.callback(
    Output("slide-content", "children"),
    Output("slide-label", "children"),
    Output("progress-fill", "style"),
    Output("previous-button", "disabled"),
    Output("next-button", "disabled"),
    Output("next-button", "children"),
    Output("reveal-button", "style"),
    Output("reveal-button", "children"),
    Output("chapter-label", "children"),
    Output("slide-number", "children"),
    Input("slide-store", "data"),
    Input("reveal-store", "data"),
    Input("vote-store", "data"),
    Input("explore-store", "data"),
    Input("iam-map-store", "data"),
    Input("capstone-store", "data"),
)
def display_slide(slide, reveal, votes, explore, iam_map, capstone):
    slide = int(slide or 0)
    reveal = int(reveal or 0)
    votes = votes or {"A": 0, "B": 0, "C": 0, "D": 0}
    if slide < CORE_SLIDE_COUNT:
        progress = 100 * slide / CORE_LAST_SLIDE if CORE_LAST_SLIDE else 100
    else:
        appendix_offset = slide - APPENDIX_START_SLIDE
        appendix_span = LAST_SLIDE - APPENDIX_START_SLIDE
        progress = 100 * appendix_offset / appendix_span if appendix_span else 100
    show_reveal = slide == ANONYMOUS_SLIDE
    if slide == ANONYMOUS_SLIDE:
        reveal_text = "Hide labels" if reveal else "Reveal labels"
    else:
        reveal_text = "Reveal"
    return (
        render_slide(slide, reveal, votes, explore, capstone, iam_map),
        style_premise_text(slide_label(slide)),
        {"width": f"{progress:.2f}%"},
        slide == 0,
        slide in {CORE_LAST_SLIDE, LAST_SLIDE},
        "Next →",
        {"visibility": "visible" if show_reveal else "hidden"},
        reveal_text,
        style_premise_text(chapter_for_slide(slide)),
        slide_number(slide),
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
