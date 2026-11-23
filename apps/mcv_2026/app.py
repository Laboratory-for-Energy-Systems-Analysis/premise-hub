from __future__ import annotations

import os
from pathlib import Path

from dash import ALL, ClientsideFunction, Dash, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate
from flask import Response, abort, render_template, render_template_string, request, send_from_directory
from werkzeug.security import generate_password_hash

from portal.auth import PresentationPasswordGate

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
from .fair_handoff import diagram_svg
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

REQUESTS_PREFIX = os.getenv("MCV_2026_REQUESTS_PREFIX", "/")
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
    "routing-vis.min.js",
}
CHAPTERS = [
    ("Introduction", 0),
    ("Systèmes", 1),
    ("Bilan", 2),
    ("Temporalité", 3),
    ("Question", 6),
    ("Climat", 7),
]
app = Dash(
    __name__,
    title="MCV2026 · Carbone biogénique et temporalité",
    update_title=None,
    requests_pathname_prefix=REQUESTS_PREFIX,
    suppress_callback_exceptions=True,
    external_stylesheets=[REQUESTS_PREFIX + "shared/styles.css"],
)
server = app.server
mcv_password = os.getenv("MCV_2026_PASSWORD")
server.wsgi_app = PresentationPasswordGate(
    server.wsgi_app,
    presentation_id="mcv-biogenic-carbon-2026-11-25",
    title="Élimination du CO₂ : une ACV prospective et dynamique couplée à un modèle climatique",
    password_hash=generate_password_hash(mcv_password) if mcv_password else None,
    mount_path=REQUESTS_PREFIX,
)
app.index_string = app.index_string.replace('<html>', '<html lang="fr">')


@server.after_request
def prevent_shared_caching(response):
    response.headers["Cache-Control"] = "private, no-store"
    return response


@server.get("/shared/<path:filename>")
def shared_asset(filename):
    """Serve shared design assets, with the French cover under this prefix."""
    if filename not in SHARED_FILES:
        abort(404)
    if filename == "cover-iam-trajectories.svg":
        return send_from_directory(Path(__file__).resolve().parent / "assets", filename)
    if filename == "routing-vis.min.js":
        return send_from_directory(SHARED_ASSETS / "routing/lib/vis-9.1.2", "vis-network.min.js")
    return send_from_directory(SHARED_ASSETS, filename)


@server.get("/system-flows.svg")
def system_flows_asset():
    return Response(system_flow_svg(), mimetype="image/svg+xml")


@server.get("/fair-handoff.svg")
def fair_handoff_asset():
    response = Response(diagram_svg(), mimetype="image/svg+xml")
    response.add_etag()
    return response.make_conditional(request)


@server.get("/routing/<case_slug>.<extension>")
def temporal_routing_graph(case_slug, extension):
    from .routing import (
        FOREST_DIESEL_CONTEXT, MAX_VIEW_DEPTH, SUBSTITUTION_NAMES, foreground_route, foreground_route_json,
        foreground_template_options, french_graph_template,
        route_json, verified_route_path,
    )

    if case_slug not in {"daccs", "beccs"}:
        abort(404)
    if extension == "html":
        if request.args.get("layout") == "original":
            return render_template_string(
                french_graph_template(), case_slug=case_slug, max_depth=MAX_VIEW_DEPTH,
                substitution_names=SUBSTITUTION_NAMES,
                supply_context=FOREST_DIESEL_CONTEXT if case_slug == "beccs" else None,
                layout_switch={"url": f"./{case_slug}.html", "label": "Premier plan"},
            )
        return render_template_string(
            french_graph_template(), case_slug=case_slug,
            layout_switch={"url": "?layout=original", "label": "Routage d’origine"},
            **foreground_template_options(foreground_route(case_slug)),
        )
    if extension == "json":
        if request.args.get("layout") == "foreground":
            return Response(foreground_route_json(case_slug, request.args.get("depth") == "1"),
                            mimetype="application/json")
        return Response(route_json(case_slug, request.args.get("depth") == "3"),
                        mimetype="application/json")
    if extension == "png":
        path = verified_route_path(case_slug, extension)
        return send_from_directory(path.parent, path.name)
    abort(404)


@app.callback(
    Output("mcv-route-frame", "src"), Output("mcv-route-open", "href"),
    Input("mcv-route-case", "value"),
)
def update_routing(case):
    slug = "beccs" if case == "BECCS" else "daccs"
    href = REQUESTS_PREFIX + f"routing/{slug}.html"
    return href, href


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
                                    "PSI – Analyse des systèmes énergétiques"
                                ),
                                html.Span("MCV2026 · Carbone biogénique et temps"),
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
                            id={"type": "mcv-chapter", "slide": index},
                            n_clicks=0,
                            className="chapter-button",
                        )
                        for label, index in CHAPTERS
                    ]
                    + [
                        html.Button(
                            "Annexes",
                            id="backup-button",
                            className="chapter-button",
                        ),
                    ],
                    className="chapter-nav",
                    **{"aria-label": "Chapitres de la présentation"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("Lille · 25 novembre 2026"),
                            ],
                            className="mcv-event-copy",
                        ),
                        html.Img(
                            src=app.get_asset_url("mcv-logo.png"),
                            alt="Logo officiel MCV2026",
                            className="mcv-logo",
                        ),
                    ],
                    className="event-lockup mcv-event",
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
                    "← Précédente", id="previous-button", className="nav-button nav-secondary"
                ),
                html.Div(
                    [
                        html.Button(
                            [
                                html.Span("↓", className="pdf-export-icon"),
                                html.Span("Exporter le PDF"),
                            ],
                            id="pdf-button",
                            className="nav-button pdf-export-button",
                        ),
                        dcc.Checklist(
                            id="print-backups",
                            options=[{"label": "Avec annexes", "value": "yes"}],
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
                            "Plein écran",
                            id="fullscreen-button",
                            className="footer-link",
                        ),
                    ],
                    className="footer-hint mcv-footer-tools",
                ),
                html.Button(
                    "Suivante →", id="next-button", className="nav-button nav-primary"
                ),
            ],
            className="app-footer",
        ),
        html.Div(id="print-status", className="print-status", role="status"),
        html.Div(id="print-deck", className="print-deck", **{"aria-hidden": "true"}),
    ],
    className="app-shell mcv-app",
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
    Input({"type": "mcv-chapter", "slide": ALL}, "n_clicks"),
    Input("location", "hash"),
    State("current-slide", "data"),
)
def navigate(previous, following, backup, chapters, fragment, current):
    del previous, following, backup, chapters
    current = slide_index(current)
    trigger = ctx.triggered_id
    if isinstance(trigger, dict) and trigger.get("type") == "mcv-chapter":
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
        else f"Annexe {current - CORE_COUNT + 1} / {len(ALL_SLIDES) - CORE_COUNT}"
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
        "Annexes" if core else "Retour à l’exposé",
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
        {"label": "Monde", "value": "World"},
        {"label": "Europe du Nord", "value": "ENC", "disabled": indicator == "GMST"},
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
    include_backups = "yes" in (backups or [])
    slides = pdf_deck(include_backups)
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
        "filename": UPLOAD_NAME + ("_avec_annexes" if include_backups else ""),
        "slide_count": len(slides),
        "graph_count": graph_count,
    }


app.clientside_callback(
    ClientsideFunction(namespace="mcv", function_name="syncSlide"),
    Output("presenter-sync", "data"),
    Input("current-slide", "data"),
)
app.clientside_callback(
    ClientsideFunction(namespace="mcv", function_name="exportPdf"),
    Output("print-complete", "data"),
    Input("print-trigger", "data"),
    prevent_initial_call=True,
)


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
