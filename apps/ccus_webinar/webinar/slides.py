from __future__ import annotations

import csv
import json
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc, html

from .config import (
    APPENDIX_SLIDE_COUNT,
    APPENDIX_SECTION_IDS,
    APPENDIX_START_SLIDE,
    CORE_SLIDE_COUNT,
    SLIDE_TITLES,
)
from .figures import (
    render_fair_response,
    render_pulse_equivalence,
    render_static_comparison,
    render_sensitivity,
    static_takeaway,
    temporal_takeaway,
    fair_takeaway,
    pulse_takeaway,
    render_temporal_gwp,
)
from .model import (
    DEFAULT_RESULT_STATE,
    SYSTEM_COPY,
    SYSTEMS,
    normalize_result_state,
    project_timeline,
)
from .results import RESULT_BUNDLE, result_status_label
from .static_stages import render_stage_comparison, compact_subprocess_key, sensitivity_selection, STAGES
from .figures import STAGE_LABELS
from .diagrams import diagram_uri, icon_uri
from . import editorial
from .cover import route_uri
from .overview import three_system_overview
from .bau import bau_detail
from .capture import capture_detail

ROOT = Path(__file__).resolve().parents[1]

SYSTEM_DESCRIPTIONS = {
    "BAU": "Clinker production continues without capture investment.",
    "CCS": "Both captured carbon fractions are conditioned, shipped and stored.",
    "CCUS": "Fossil carbon is stored; non-fossil carbon becomes synthetic jet fuel.",
}

STUDY_URL = "https://doi.org/10.1016/j.jclepro.2023.138935"
SYSTEM_FLOW_PATH = ROOT / "data/runtime/system_flows_2025.json"
COMPONENT_LIFETIME_PATH = ROOT / "data/assumptions/component_lifetimes.json"


def _engineering_flows() -> dict[str, list[dict]]:
    if not SYSTEM_FLOW_PATH.is_file():
        return {}
    return json.loads(SYSTEM_FLOW_PATH.read_text(encoding="utf-8")).get("flows", {})


ENGINEERING_FLOWS = _engineering_flows()


def _component_lifetimes() -> tuple[dict, ...]:
    if not COMPONENT_LIFETIME_PATH.is_file():
        return ()
    return tuple(
        json.loads(COMPONENT_LIFETIME_PATH.read_text(encoding="utf-8")).get(
            "components", ()
        )
    )


COMPONENT_LIFETIMES = _component_lifetimes()


def _citation(label: str, href: str) -> html.A:
    return html.A(
        label, href=href, target="_blank", rel="noreferrer", className="source-link"
    )


def _slide_shell(
    index: int,
    body,
    *,
    eyebrow: str,
    lead: str = "",
    timeline: str | None = None,
    source=None,
    class_name: str = "",
    title: str | None = None,
):
    return html.Article(
        [
            html.Div(
                [
                    html.Span(eyebrow, className="slide-eyebrow"),
                    html.H1(title or SLIDE_TITLES[index]),
                    html.P(lead, className="slide-lead") if lead else None,
                ],
                className="slide-heading",
            ),
            html.Div(body, className="slide-body"),
            (
                _timeline(timeline)
                if timeline
                else (
                    html.Div(
                        [
                            html.Span("Historical uptake"),
                            html.Span("2035–2064 operation + replacements"),
                            html.Span("2065 final fuel use / end of life"),
                            *(
                                [html.Span("Climate response → 2200")]
                                if index >= 12
                                else []
                            ),
                        ],
                        className="chronology-rail",
                    )
                    if 10 <= index <= 15
                    else None
                )
            ),
            html.Div(source, className="slide-source") if source else None,
        ],
        className=f"webinar-slide redesigned-slide slide-{index + 1:02d} {class_name}",
        **{"data-slide": index},
    )


def _timeline(stage: str):
    rows = project_timeline(stage)
    low = min(row["start"] for row in rows)
    high = max(row["end"] for row in rows)
    span = max(1, high - low)
    return html.Div(
        [
            html.Span("How time enters the model", className="timeline-caption"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(row["label"]),
                            html.I(
                                style={
                                    "left": f"{100 * (row['start'] - low) / span:.2f}%",
                                    "width": f"{max(1.2, 100 * (row['end'] - row['start']) / span):.2f}%",
                                },
                                className=f"timeline-segment {row['kind']}",
                            ),
                        ],
                        className="timeline-row",
                    )
                    for row in rows
                ],
                className="timeline-rows",
            ),
            html.Div(
                [html.Span(str(low)), html.Span(str(high))], className="timeline-axis"
            ),
        ],
        className=f"project-timeline timeline-{stage}",
    )


def _node(label: str, kind: str, compact: bool = False):
    return html.Div(
        [
            html.Img(src=icon_uri(kind), alt="", className="illustrated-icon"),
            html.Strong(label),
        ],
        className=f"system-node node-{kind} {'compact' if compact else ''}",
    )


def system_diagram(system: str, *, compact: bool = False, quantities: bool = False):
    return html.Figure(
        html.Img(
            src=diagram_uri(system, ENGINEERING_FLOWS.get(system, []), compact=compact),
            alt=f"{system}: carbon, materials, energy and displaced products within the system boundary",
            className="system-svg",
        ),
        className=f"illustrated-system illustrated-{system.lower()} {'illustrated-compact' if compact else 'illustrated-detailed'}",
    )


def _control(label: str, component):
    if isinstance(component, (dcc.RadioItems, dcc.Checklist)):
        component.className = "contribution-view-toggle"
    return html.Div([html.Span(label), component], className="chart-control",
                    title=("Per tonne divides the full 30-year result by total clinker production. The alternative shows the full plant total."
                           if label == "Scale" else ""))


def _evidence_badge():
    if RESULT_BUNDLE.status == "stale":
        return html.Span("Model revised · recalculation required", className="candidate-evidence-badge")
    if RESULT_BUNDLE.status != "candidate":
        return None
    return html.Span("Preliminary results · review pending", className="candidate-evidence-badge")


def _takeaway(slide_key: str, fallback: str):
    return html.Div(
        [
            html.Span("What’s changed?"),
            html.Strong(fallback, id=f"takeaway-{slide_key}-text"),
        ],
        className="takeaway-box",
    )


def _chart_reading(*, pulse=False):
    return html.Div(
        [
            html.Span(
                "Per tonne = total impact / 30-year clinker output.", className="reading-year"
            ),
            html.Span(className="reading-values"),
            html.Button(
                "Operating years",
                type="button",
                className="chart-focus",
                title="Zoom to 2025–2070. Reset view restores the default time range.",
                style={"display": "none"} if pulse else {},
            ),
            html.Button(
                "Reset view",
                type="button",
                className="chart-reset",
                title="Restore the default axes and show all contributions",
            ),
        ],
        className="chart-reading",
        **{"aria-live": "polite"},
    )


def _title_slide(index: int, state: dict):
    return html.Article(
        [
            html.Div(
                [
                    html.H1("LCA of CCS and CCUS applied to cement production"),
                    html.H2("What Integrating Time Reveals About Climate Benefits of CCS and CCUS"),
                    html.Div(
                        [_cover_route(system) for system in SYSTEMS],
                        className="cover-system-stack",
                    ),
                    html.Div(
                        [
                            html.Strong("Dr. Romain Sacchi"),
                            html.Span(
                                "Researcher at the Laboratory for Energy Systems Analysis"
                            ),
                            html.Span("Paul Scherrer Institut (PSI)"),
                        ],
                        className="cover-presenter",
                    ),
                ],
                className="cover-copy",
            ),
        ],
        className="webinar-slide redesigned-slide title-slide",
        **{"data-slide": index},
    )


def _cover_route(system):
    return html.Div(
        [
            html.Div(
                [
                    html.Strong(system),
                    html.Span(
                        {
                            "BAU": "The kiln releases CO₂ without capture.",
                            "CCS": "Captured fossil and non-fossil CO₂ are stored.",
                            "CCUS": "Captured fossil CO₂ is stored. Non-fossil carbon is used to make fuels.",
                        }[system]
                    ),
                ],
                className="cover-route-heading",
            ),
            html.Img(
                src=route_uri(system),
                alt=f"{system}: rotary kiln, carbon route and destination",
                className="cover-route-illustration",
            ),
        ],
        className=f"cover-route cover-route-{system.lower()}",
    )


def _study(index: int, state: dict):
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Small(
                            "Gallego Dávila · Sacchi · Pizzol | Journal of Cleaner Production, 2023"
                        ),
                        html.H2(
                            "Preconditions for achieving carbon neutrality in cement production through CCUS"
                        ),
                        html.P("Aalborg, Denmark · an industrial cement case"),
                        html.Div(
                            [
                                html.Strong("Original question"),
                                html.Span(
                                    "Under which conditions can capture, storage and carbon reuse support carbon-neutral cement production?"
                                ),
                            ],
                            className="study-question",
                        ),
                        _citation("Read the original study", STUDY_URL),
                    ],
                    className="study-evidence",
                ),
                html.Div(
                    [
                        html.Figure(
                            [
                                html.Div(
                                    html.Img(
                                        src="assets/paper-figure-1.jpg",
                                        alt="Original paper Figure 1 showing clinker production, carbon capture, storage and the methanol-to-kerosene route",
                                    ),
                                    className="study-figure-media",
                                ),
                                html.Figcaption(
                                    _citation(
                                        "Figure 1. The original CCS and CCUS value chains ↗",
                                        "assets/paper-figure-1.jpg",
                                    )
                                ),
                            ],
                            className="study-original-figure",
                        ),
                        html.Figure(
                            [
                                html.Div(
                                    html.Div(
                                        html.Img(
                                            src="assets/paper-figure-2.jpg",
                                            alt="Detail of original paper Figure 2 showing electricity and water inputs, electrolysis, hydrogen and methanol synthesis",
                                        ),
                                        className="study-detail-crop",
                                    ),
                                    className="study-figure-media",
                                ),
                                html.Figcaption(
                                    _citation(
                                        "Figure 2 detail. Hydrogen and methanol production · Open full figure ↗",
                                        "assets/paper-figure-2.jpg",
                                    )
                                ),
                            ],
                            className="study-original-figure",
                        ),
                        html.Div(
                            [
                                _citation("Gallego Dávila et al. (2023)", STUDY_URL),
                                html.Span(
                                    " · Original figures, second figure cropped · "
                                ),
                                _citation(
                                    "CC BY 4.0",
                                    "https://creativecommons.org/licenses/by/4.0/",
                                ),
                            ],
                            className="study-figure-credit",
                        ),
                    ],
                    className="study-paper-figures",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Strong("Retained"),
                                html.Span(
                                    "The kiln, capture, storage and heat-recovery model."
                                ),
                            ],
                            className="study-change study-change-retained",
                        ),
                        html.Div(
                            [
                                html.Strong("Adapted"),
                                html.Span(
                                    "Revised methanol and fuel production, including diesel and naphtha."
                                ),
                            ],
                            className="study-change study-change-adapted",
                        ),
                        html.Div(
                            [
                                html.Strong("Extended"),
                                html.Span(
                                    "Future production conditions, emission dates and climate response."
                                ),
                            ],
                            className="study-change study-change-extended",
                        ),
                    ],
                    className="study-adaptation-strip",
                ),
            ],
            className="study-rebuilt",
        ),
        eyebrow="The case · original study",
        lead="The process model comes from the study. It is further adapted for the purpose of this webinar.",
    )


def _three_systems(index: int, state: dict):
    return _slide_shell(
        index,
        three_system_overview(),
        eyebrow="The case · three scenarios",
        lead="The kiln makes the same product (grey clinker). What changes is where its carbon goes and how its heat is used.",
    )


def _detailed_system(index: int, state: dict, system: str):
    if system == "BAU":
        return _slide_shell(
            index,
            bau_detail(),
            eyebrow="The case · BAU / reference",
            lead="CO₂ comes from limestone calcination and from burning fossil and non-fossil fuels.",
            source=editorial.link(
                "Published SI.2 inputs and interpolation", "bau-public"
            ),
        )
    if system in ("CCS", "CCUS"):
        return _slide_shell(
            index,
            capture_detail(system),
            eyebrow=f"The case · {system}",
            lead=(
                "Captured carbon goes to storage. What escapes capture or the transport chain still reaches the atmosphere."
                if system == "CCS"
                else "Fossil carbon goes to storage. Non-fossil carbon becomes jet fuel, diesel and naphtha, with the remaining carbon released as CO₂."
            ),
            source=editorial.link(
                "SI.2 + UOP ratios, carbon balance and assumptions",
                "capture-public",
            ),
        )
    callouts = {
        "BAU": (
            "All kiln CO₂ reaches the atmosphere",
            "Recovered heat is exported",
            "No capture infrastructure",
        ),
        "CCS": (
            "Capture includes fossil and non-fossil CO₂",
            "Export includes heat recovered after capture—not just kiln heat",
            "The stored stream reaches the North Sea in the same year",
        ),
        "CCUS": (
            "Fossil carbon is stored",
            "Non-fossil carbon feeds methanol-to-jet",
            "Avoided fossil production + combustion credited in production year",
        ),
    }[system]
    return _slide_shell(
        index,
        html.Div(
            [
                system_diagram(system, quantities=True),
                html.Div(
                    "FLOW KEY   ━ carbon / material / energy flows    ┄ displaced supply    ▧ foreground + background inside the complete product boundary",
                    className="flow-key",
                ),
                html.Div(
                    [
                        html.Div([html.Span(str(i + 1)), html.Strong(text)])
                        for i, text in enumerate(callouts)
                    ],
                    className="diagram-callouts",
                ),
            ],
            className="detailed-system-layout",
        ),
        eyebrow=f"The case · {system}",
        lead=SYSTEM_DESCRIPTIONS[system],
        source=html.Span(
            "Material and energy quantities are shown for 2025, per tonne of clinker."
        ),
    )


def _question(index: int, state: dict):
    from .investigation import investigation_map

    return _slide_shell(
        index,
        investigation_map(),
        eyebrow="The investigation",
        lead="We first hold conditions fixed, then include future changes and the timing of emissions.",
    )


def _concept(index: int, state: dict, stage: str, cards=()):
    from .temporal_story import temporal_story
    leads = {
        "current": "Evaluate the full life cycle using 2025 conditions, without preserving the dates of its events.",
        "trails": "The same clinker demand is compared over 30 years. CCS and CCUS investment begins in 2035.",
        "fair": "Greenhouse gases change how much heat Earth retains. Radiative forcing measures this energy imbalance. Temperature responds more slowly as the ocean and atmosphere adjust.",
        "pulse": "Compare the areas under the response curves over the same period, using a CO₂ pulse in 2035.",
    }
    return _slide_shell(
        index,
        temporal_story() if stage == "trails" else editorial.concept(stage),
        eyebrow={
            "current": "Current (static) LCA · concept",
            "trails": "Time-explicit LCA · inventory",
            "fair": "Time-explicit LCA · climate response",
            "pulse": "Time-explicit LCA · pulse equivalence",
        }[stage],
        lead=leads[stage],
        source=editorial.link("Timing and method assumptions", "contract"),
    )


def _current_result(index: int, state: dict):
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div([
                    dcc.Graph(id="current-static-chart",
                              figure=render_stage_comparison(RESULT_BUNDLE, prototype=True, fuel_share=30), responsive=True,
                              config={"displayModeBar": False, "responsive": True},
                              className="result-chart static-chart"),
                    html.Div([
                    html.Aside([
                        html.Div([
                        html.H3("Contributions by process"),
                        dcc.Dropdown(id="current-stage", options=[{"label": STAGE_LABELS[s], "value": s} for s in STAGES],
                                     value="synthetic_fuel", clearable=False, searchable=False),
                        html.P("Negative contributions distinguish CO₂ uptake, avoided emissions and capture transfers. Capture is not removal from air."),
                        ], className="static-detail-controls"),
                        html.Div(compact_subprocess_key(RESULT_BUNDLE), id="current-subprocess-key"),
                    ], className="static-stage-key"),
                    html.Aside([
                        html.Div([html.Strong("Operating electricity"), html.Span("Preliminary results" if RESULT_BUNDLE.status == "candidate" else "Precomputed grid", className="sensitivity-preview-badge")]),
                        dcc.Slider(id="current-preview-electricity", min=0, max=4, step=None, value=0, updatemode="drag", disabled=RESULT_BUNDLE.status == "invalidated",
                                   marks={0: "Market", 1: "Wind", 2: "PV", 3: "Gas", 4: "Coal"}),
                        html.Strong("Non-fossil share of kiln fuel"),
                        dcc.Slider(id="current-preview-fuel", min=0, max=100, step=10, value=30, updatemode="drag", disabled=RESULT_BUNDLE.status == "invalidated",
                                   marks={0: "0%", 50: "50%", 100: "100%"}),
                        html.P(sensitivity_selection(RESULT_BUNDLE, "ENC market", 30), id="current-preview-selection", role="status"),
                    ], className="static-sensitivity-controls"),
                    ], className="static-four-controls"),
                ], className="static-stage-layout static-four-layout"),
            ],
            className="result-layout",
        ),
        eyebrow="Current (static) LCA · result",
        lead="First, we compare all three options using 2025 conditions, without distinguishing when emissions occur.",
    )


def _prospective_concept(index: int, state: dict):
    from .future_markets import future_markets
    return _slide_shell(
        index,
        future_markets(RESULT_BUNDLE),
        eyebrow="Prospective (static) LCA · background",
        lead="The same investment connects to different suppliers as the economy changes.",
        source=editorial.link(
            "Scenario assumptions and data sources",
            "contract",
        ),
    )


def _prospective_result(index: int, state: dict):
    from .prospective_results import load_prospective_bundle, prospective_figure
    bundle = load_prospective_bundle()
    return _slide_shell(
        index,
        html.Div([
            html.Div([
                _control("Pathway", dcc.RadioItems(id="prospective-pathway", options=[
                    {"label":p, "value":p} for p in ("SSP2-NPi", "SSP2-PkBudg1000")],
                    value="SSP2-NPi", inline=True)),
                _control("Year", dcc.RadioItems(id="prospective-year", options=[
                    {"label":str(y), "value":y} for y in (2035,2050)],
                    value=2035, inline=True)),
                dcc.Checklist(id="prospective-reference", options=[
                    {"label":"Show 2025 comparison", "value":"2025"}],
                    value=[], inline=True),
            ],className="result-toolbar prospective-toolbar"),
            html.Div([
                dcc.Graph(id="prospective-static-chart",
                    figure=prospective_figure(bundle, RESULT_BUNDLE, "synthetic_fuel", "SSP2-NPi", "ENC market", 30),
                    responsive=True,config={"displayModeBar":False,"responsive":True},
                    className="result-chart static-chart"),
                html.Div([
                    html.Aside([
                        html.Div([
                            html.H3("Contributions by process"),
                            dcc.Dropdown(id="prospective-stage",options=[
                                {"label":STAGE_LABELS[s],"value":s} for s in STAGES],
                                value="synthetic_fuel",clearable=False,searchable=False),
                            html.P("Negative contributions distinguish CO₂ uptake, avoided emissions and capture transfers. Capture is not removal from air."),
                        ],className="static-detail-controls"),
                        html.Div(compact_subprocess_key(bundle, "synthetic_fuel", "prospective_static"),
                                 id="prospective-subprocess-key"),
                    ],className="static-stage-key"),
                    html.Aside([
                        html.Div([html.Strong("Operating electricity"),
                                  html.Span("Precomputed grid" if RESULT_BUNDLE.approved else "Preliminary results",className="sensitivity-preview-badge")]),
                        dcc.Slider(id="prospective-electricity",min=0,max=4,step=None,value=0,
                            updatemode="drag",disabled=bundle.status=="invalidated",
                            marks={0:"Market",1:"Wind",2:"PV",3:"Gas",4:"Coal"}),
                        html.Strong("Non-fossil share of kiln fuel"),
                        dcc.Slider(id="prospective-fuel",min=0,max=100,step=10,value=30,
                            updatemode="drag",disabled=bundle.status=="invalidated",
                            marks={0:"0%",50:"50%",100:"100%"}),
                        html.P(sensitivity_selection(bundle,"ENC market",30),id="prospective-selection",role="status"),
                    ],className="static-sensitivity-controls"),
                ],className="static-four-controls"),
            ],className="static-stage-layout static-four-layout"),
        ],className="result-layout"),
        eyebrow="Prospective (static) LCA · result",
        lead="The 2035 and 2050 snapshots use year-specific kiln fuel mixes, hydrogen electricity demand and background energy supplies.",
    )


def _temporal_result(index: int, state: dict):
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        _control(
                            "Area",
                            dcc.RadioItems(
                                id="gwp-area",
                                options=[
                                    {"label": "Stacked", "value": "stacked"},
                                    {"label": "Unstacked", "value": "unstacked"},
                                ],
                                value="stacked",
                                inline=True,
                            ),
                        ),
                        _control(
                            "Group",
                            dcc.RadioItems(
                                id="gwp-grouping",
                                options=[
                                    {"label": "Process stage", "value": "stage"},
                                    {"label": "Elementary flow", "value": "flow"},
                                ],
                                value="stage",
                                inline=True,
                            ),
                        ),
                        _control(
                            "Scale",
                            dcc.RadioItems(
                                id="gwp-normalization",
                                options=[
                                    {"label": "Per tonne", "value": "per_tonne"},
                                    {"label": "30-year total", "value": "absolute"},
                                ],
                                value="per_tonne",
                                inline=True,
                            ),
                        ),
                        _evidence_badge(),
                    ],
                    className="result-toolbar temporal-toolbar",
                ),
                dcc.Graph(
                    id="temporal-gwp-chart",
                    figure=render_temporal_gwp(
                        "SSP2-PkBudg1000",
                        "stage",
                        "stacked",
                        "per_tonne",
                        RESULT_BUNDLE,
                    ),
                    responsive=True,
                    config={"displayModeBar": False, "responsive": True},
                    className="result-chart temporal-chart",
                ),
                _chart_reading(),
                _takeaway("gwp", temporal_takeaway("SSP2-PkBudg1000", RESULT_BUNDLE)),
            ],
            className="result-layout temporal-result-layout",
        ),
        eyebrow="Time-explicit LCA · GWP100 result",
        lead="Each year’s emissions use the same GWP100 factors. Areas show annual contributions on the left axis. The red line adds them over time on the right axis.",
    )


def _fair_result(index: int, state: dict):
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        _control(
                            "Response",
                            dcc.RadioItems(
                                id="fair-metric",
                                options=[
                                    {
                                        "label": "Radiative forcing",
                                        "value": "radiative_forcing",
                                    },
                                    {"label": "Temperature", "value": "temperature"},
                                ],
                                value="radiative_forcing",
                                inline=True,
                            ),
                        ),
                        _control(
                            "Area",
                            dcc.RadioItems(
                                id="fair-area",
                                options=[
                                    {"label": "Stacked", "value": "stacked"},
                                    {"label": "Unstacked", "value": "unstacked"},
                                ],
                                value="stacked",
                                inline=True,
                            ),
                        ),
                        _control(
                            "Group",
                            dcc.RadioItems(
                                id="fair-grouping",
                                options=[
                                    {"label": "Process stage", "value": "stage"},
                                    {"label": "Elementary flow", "value": "flow"},
                                ],
                                value="stage",
                                inline=True,
                            ),
                        ),
                        _control(
                            "Scale",
                            dcc.RadioItems(
                                id="fair-normalization",
                                options=[
                                    {"label": "Per tonne", "value": "per_tonne"},
                                    {"label": "30-year total", "value": "absolute"},
                                ],
                                value="per_tonne",
                                inline=True,
                            ),
                        ),
                        _control(
                            "Climate uncertainty",
                            dcc.Checklist(
                                id="fair-uncertainty",
                                options=[{"label": "FaIR ensemble", "value": "show"}],
                                value=[],
                                inline=True,
                            ),
                        ),
                        _evidence_badge(),
                    ],
                    className="result-toolbar temporal-toolbar",
                ),
                dcc.Graph(
                    id="fair-response-chart",
                    figure=render_fair_response(
                        "SSP2-PkBudg1000",
                        "radiative_forcing",
                        "stage",
                        "stacked",
                        "per_tonne",
                        False,
                        RESULT_BUNDLE,
                    ),
                    responsive=True,
                    config={"displayModeBar": False, "responsive": True},
                    className="result-chart temporal-chart",
                ),
                _chart_reading(),
                _takeaway(
                    "fair",
                    fair_takeaway(
                        "SSP2-PkBudg1000", "radiative_forcing", RESULT_BUNDLE
                    ),
                ),
            ],
            className="result-layout temporal-result-layout",
        ),
        eyebrow="Time-explicit LCA · FaIR result",
        lead="Areas: annual GWP100 contributions, left axis. Red line: the selected climate response, right axis. Dashed line: BAU.",
    )


def _pulse_result(index: int, state: dict):
    from .pulse_view import endpoint_cards
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        _control(
                            "Equivalent",
                            dcc.RadioItems(
                                id="pulse-metric",
                                options=[
                                    {"label": "Forcing", "value": "forcing"},
                                    {"label": "Temperature", "value": "temperature"},
                                ],
                                value="forcing",
                                inline=True,
                            ),
                        ),
                        _control(
                            "Scale",
                            dcc.RadioItems(
                                id="pulse-normalization",
                                options=[
                                    {"label": "Per tonne", "value": "per_tonne"},
                                    {"label": "30-year total", "value": "absolute"},
                                ],
                                value="per_tonne",
                                inline=True,
                            ),
                        ),
                        _control(
                            "Climate uncertainty",
                            dcc.Checklist(
                                id="pulse-uncertainty",
                                options=[{"label": "FaIR ensemble", "value": "show"}],
                                value=[],
                                inline=True,
                            ),
                        ),
                        _control(
                            "Choose the three dates",
                            html.Div([
                                dcc.RangeSlider(
                                    id="pulse-window", min=1995, max=2200, step=5,
                                    value=[2025, 2035, 2100], allowCross=False, pushable=5,
                                    marks={1995: "1995", 2050: "2050", 2100: "2100", 2150: "2150", 2200: "2200"},
                                    tooltip={"placement": "bottom"}, updatemode="mouseup",
                                ),
                                html.Div([
                                    html.Span("1 · Window start"),
                                    html.Span("2 · Reference pulse", className="pulse-reference-key"),
                                    html.Span("3 · Window end"),
                                ], className="pulse-handle-key"),
                            ]),
                        ),
                        _evidence_badge(),
                    ],
                    className="result-toolbar pulse-toolbar",
                ),
                html.Div([
                    dcc.Graph(
                        id="pulse-chart",
                        figure=render_pulse_equivalence("forcing", "per_tonne", 2025, 2100, False, RESULT_BUNDLE),
                        responsive=True, config={"displayModeBar": False, "responsive": True},
                        className="pulse-linked-chart",
                    ),
                    html.Div([
                        html.Div("2025–2100 · pulse in 2035", id="pulse-window-label", className="pulse-window-label"),
                        html.Div(endpoint_cards(render_pulse_equivalence(
                            "forcing", "per_tonne", 2025, 2100, False, RESULT_BUNDLE)), id="pulse-endpoints"),
                        html.P("Highlighted bars and the values above use the selected comparison period. The bars are alternative estimates, not annual emissions.", className="pulse-window-note"),
                    ], className="pulse-side-column"),
                ], className="pulse-linked-grid"),
            ],
            className="result-layout pulse-linked-layout",
        ),
        eyebrow="Time-explicit LCA · CO₂-pulse equivalent",
        lead="Each bar estimates a pulse in the selected reference year, using a different comparison end year.",
    )


def _synthesis(index: int, state: dict):
    table = dict(RESULT_BUNDLE.tables)
    # Slide 10 loads its checked diagnostic independently of the main bundle.
    # Reuse that exact baseline, never a sensitivity cell or an older CSV.
    if RESULT_BUNDLE.status in ('candidate', 'approved'):
        from .prospective_results import load_prospective_bundle
        prospective = load_prospective_bundle(2035, 'SSP2-NPi')
        fresh = prospective.tables.get('static_totals', ())
        if fresh:
            table['static_totals'] = tuple(r for r in table.get('static_totals', ())
                if not (r.get('lens') == 'prospective_static' and r.get('pathway') == 'SSP2-NPi')) + tuple(fresh)
    forcing_rows = [
        r
        for r in table.get("fair_responses", ())
        if r.get("metric") in {"radiative forcing", "radiative_forcing"}
        and r.get("statistic") in {"median", "q50"}
        and r.get("pathway") == "SSP2-PkBudg1000"
    ]
    common_years = set.intersection(
        *[
            {
                float(r["year"])
                for r in forcing_rows
                if r.get("system") == s and float(r["year"]) <= 2200.5
            }
            for s in SYSTEMS
        ]
    )
    final_forcing_year = max(common_years, default=2200)
    stages = (
        (
            "2025 GWP100",
            "SSP2-NPi · static LCA · kg CO₂-eq/t",
            "static_totals",
            "score",
            1,
            lambda r: r.get("lens") == "current_static"
            and r.get("pathway") == "SSP2-NPi",
        ),
        (
            "2035 GWP100",
            "SSP2-NPi · static LCA · kg CO₂-eq/t",
            "static_totals",
            "score",
            1,
            lambda r: r.get("lens") == "prospective_static"
            and r.get("pathway") == "SSP2-NPi",
        ),
        (
            "Cumulative GWP100",
            "PkBudg1000 · 2035–2064 · kg CO₂-eq/t",
            "temporal_totals",
            "score",
            1,
            lambda r: r.get("pathway") == "SSP2-PkBudg1000",
        ),
        (
            "Forcing near 2200",
            f"PkBudg1000 · sample {final_forcing_year:g} · pW/m²/t",
            "fair_responses",
            "value",
            1e12,
            lambda r: r.get("pathway") == "SSP2-PkBudg1000"
            and r.get("metric") in {"radiative forcing", "radiative_forcing"}
            and r.get("statistic") in {"median", "q50"}
            and float(r["year"]) == final_forcing_year,
        ),
        (
            "CO₂-pulse equivalent",
            "PkBudg1000 · 2025–2100 · ref. 2035 · kg CO₂ pulse-eq/t",
            "pulse_equivalence",
            "value",
            1,
            lambda r: r.get("pathway") == "SSP2-PkBudg1000"
            and r.get("metric") == "integrated_rf"
            and r.get("statistic") in {"median", "q50"}
            and int(float(r.get("window_start", 0))) == 2025
            and int(float(r.get("reference_year", 2035))) == 2035
            and int(float(r.get("window_end", 0))) == 2100,
        ),
    )
    columns = []
    for title, scope, name, key, scale, select in stages:
        values = {}
        for row in table.get(name, ()):
            if select(row) and row.get("system") in SYSTEMS:
                values[row["system"]] = (
                    values.get(row["system"], 0) + float(row[key]) * scale
                )
        columns.append(values)
    headers = ["System"] + [
        html.Div([html.Strong(s[0]), html.Small(s[1])]) for s in stages
    ]
    rows = []
    for system in SYSTEMS:
        cells = [html.Strong(system)]
        for i, values in enumerate(columns):
            if set(values) != set(SYSTEMS):
                cells.append(html.Span('Calculation pending', className='synthesis-pending'))
                continue
            rank = sorted(values, key=values.get).index(system) + 1
            value = values[system]
            cells.append(
                html.Div(
                    [
                        html.Strong(f"{value:.3g}" if i == 3 else f"{value:,.0f}"),
                        html.Span(
                            f"Rank {rank}"
                        ),
                    ],
                    className="synthesis-value " + ('synthesis-negative' if value < 0 else 'synthesis-positive'),
                )
            )
        rows.append(cells)
    # Show changes only if a complete, distinguishable three-system ordering exists.
    annual = {}
    for r in table.get("fair_responses", ()):
        if (
            r.get("metric") in {"radiative forcing", "radiative_forcing"}
            and r.get("statistic") in {"median", "q50"}
            and r.get("pathway") == "SSP2-PkBudg1000"
        ):
            y = float(r["year"])
            if 2035 <= y <= 2200.5:
                annual.setdefault(y, {})[r["system"]] = float(r["value"])
    spans = []
    for y, values in sorted(annual.items()):
        if set(values) != set(SYSTEMS):
            continue
        tolerance = max(abs(v) for v in values.values()) * 1e-6
        order = tuple(sorted(values, key=values.get))
        label = order[0] + "".join(
            (
                " ≈ "
                if abs(values[order[i]] - values[order[i + 1]]) <= tolerance
                else " < "
            )
            + order[i + 1]
            for i in (0, 1)
        )
        if spans and spans[-1][2] == label and spans[-1][1] == y - 1:
            spans[-1][1] = y
        else:
            spans.append([y, y, label])
    timeline = (
        html.Div(
            [html.Span(f"{int(a)}–{int(b)}: {label}") for a, b, label in spans],
            className="ranking-intervals",
        )
        if spans
        else html.P("The annual radiative forcing results are not yet available.")
    )
    complete = [values for values in columns if set(values) == set(SYSTEMS)]
    orders = [tuple(sorted(values, key=values.get)) for values in complete]
    ranking_message = (
        ' < '.join(orders[0]) + ' at all calculated endpoints.'
        if len(orders) >= 4 and len(set(orders)) == 1
        else 'Compare the ordering within each column, not the numerical values across metrics.'
    )
    changed_sign = [s for s in SYSTEMS
        if s in columns[2] and s in columns[3] and columns[2][s] > 0 and columns[3][s] < 0]
    sign_message = (
        ' and '.join(changed_sign) + ': positive cumulative GWP, but negative forcing near 2200.'
        if changed_sign else 'A negative GWP and negative forcing describe different climate outcomes.'
    )
    return _slide_shell(
        index,
        html.Div(
            [
                editorial.table(headers, rows, "synthesis-matrix"),
                html.Div(
                    [
                        html.Strong(
                            "What this case tells us"
                        ),
                        html.Ul([
                            html.Li("We compared three LCA modelling approaches using GWP100, radiative forcing and CO₂-pulse equivalents."),
                            html.Li(
                                "None changed the ranking in the default comparisons: CCS first, CCUS second, BAU last."
                                if len(orders) == 5 and set(orders) == {('CCS', 'CCUS', 'BAU')}
                                else "The ranking depends on the results and assumptions shown above."
                            ),
                            html.Li("The electricity supply is a key assumption for CCUS, particularly for hydrogen production. Low-carbon supply reduces this burden."),
                            html.Li("Including time better represents when emissions and climate effects occur. Even without changing the ranking, this can inform investment decisions."),
                        ], className="synthesis-takeaways"),
                    ],
                    className="rank-timing",
                ),
            ],
            className="synthesis-rebuilt",
        ),
        eyebrow="What changes · synthesis",
        title=(SLIDE_TITLES[index] if len(orders) == 5 and set(orders) == {('CCS', 'CCUS', 'BAU')}
               else "Compare the three systems at each assessment stage."),
        lead="The ranking is unchanged at these endpoints. The time-explicit results also show when emissions and climate effects occur.",
    )


def _resources(index: int, state: dict):
    groups = (
        (
            "Case and assumptions",
            (
                ("Gallego Dávila et al. (2023) · cement CCUS", STUDY_URL),
                (
                    "UOP patent (2026) · fuel conversion, Table 2",
                    "https://patents.justia.com/patent/20260098223",
                ),
                ("JRC99380 · methanol process", "https://publications.jrc.ec.europa.eu/repository/bitstream/JRC99380/ld1a27629enn.pdf"),
                (
                    "Levasseur et al. (2010) · time accounting",
                    "https://doi.org/10.1021/es9030003",
                ),
                (
                    "Guest et al. (2013) · biomass carbon timing",
                    "https://doi.org/10.1111/j.1530-9290.2012.00507.x",
                ),
                ("COST Action TrANsMIT", "https://www.cost.eu/actions/CA21127/"),
            ),
        ),
        (
            "Inventories and scenarios",
            (
                ("ecoinvent", "https://ecoinvent.org/"),
                (
                    "REMIND · model behind REMIND-EU",
                    "https://www.pik-potsdam.de/en/institute/departments/transformation-pathways/models/remind",
                ),
                ("premise", "https://premise.readthedocs.io/"),
                (
                    "Open PEM component inventory",
                    "https://doi.org/10.17632/tm67kg6cdv.1",
                ),
            ),
        ),
        (
            "Calculation",
            (
                ("Brightway", "https://docs.brightway.dev/"),
                ("TRAILS", "https://github.com/romainsacchi/trails"),
                ("FaIR", "https://docs.fairmodel.net/"),
                ("IPCC Sixth Assessment", "https://www.ipcc.ch/report/ar6/wg1/"),
            ),
        ),
        (
            "Contact and code",
            (
                ("romain.sacchi@psi.ch", "mailto:romain.sacchi@psi.ch"),
                ("github.com/romainsacchi", "https://github.com/romainsacchi"),
                ("Webinar application", "./"),
                ("Material and energy quantities", "evidence/quantities"),
                ("Assumptions and timing", "evidence/contract"),
            ),
        ),
    )
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.H2(title),
                        *[_citation(label + " ↗", url) for label, url in links],
                    ],
                    className="resource-group",
                )
                for title, links in groups
            ],
            className="resource-atlas",
        ),
        eyebrow="What changes · resources",
        lead="Follow these links to read the sources, check the assumptions and access the code.",
    )


def _discussion(index: int, state: dict):
    questions = (
        "Could non-climate indicators change which investment is preferred from an environmental viewpoint?",
        "For a 30-year capture investment, which timing assumptions must be known before time-explicit LCA becomes decision-relevant?",
        "Should we favour an option that reduces warming sooner, even if its long-term climate benefit is smaller?",
    )
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Div([html.Span(f"0{i + 1}"), html.H2(question)])
                        for i, question in enumerate(questions)
                    ],
                    className="discussion-questions",
                ),
                html.Div(
                    [
                        html.Strong("Dr. Romain Sacchi"),
                        html.A(
                            "romain.sacchi@psi.ch", href="mailto:romain.sacchi@psi.ch"
                        ),
                        html.A(
                            "github.com/romainsacchi",
                            href="https://github.com/romainsacchi",
                            target="_blank",
                        ),
                    ],
                    className="discussion-contact",
                ),
            ],
            className="discussion-layout",
        ),
        eyebrow="Discussion",
        lead="Climate change is the only impact category assessed in this webinar.",
    )


def _appendix(index: int, state: dict):
    appendix = APPENDIX_SECTION_IDS[index - APPENDIX_START_SLIDE]
    if appendix == 4:
        sensitivity_ready = any(str(r.get("available", "false")).lower() in {"1", "true", "yes"}
                                for r in RESULT_BUNDLE.tables.get("sensitivity_availability", ()))
        body = html.Div(
            [
                html.Div(
                    [
                        _control(
                            "Avoided heat",
                            dcc.Dropdown(
                                id="sensitivity-heat",
                                options=[
                                    "ENC market",
                                    "biomass CHP",
                                    "wind heat pump",
                                    "coal CHP",
                                    "natural gas CHP",
                                ],
                                value="ENC market",
                                clearable=False,
                            ),
                        ),
                        _control(
                            "Operating electricity",
                            dcc.Dropdown(
                                id="sensitivity-electricity",
                                options=[
                                    "ENC market",
                                    "wind",
                                    "photovoltaic",
                                    "natural gas",
                                    "coal",
                                ],
                                value="ENC market",
                                clearable=False,
                            ),
                        ),
                        _control(
                            "Non-fossil kiln share",
                            dcc.Slider(
                                id="sensitivity-fuel",
                                min=0,
                                max=100,
                                step=20,
                                value=60,
                                disabled=not sensitivity_ready,
                                marks={
                                    value: f"{value}%" for value in range(0, 101, 20)
                                },
                            ),
                        ),
                        _control(
                            "Metric",
                            dcc.RadioItems(
                                id="sensitivity-metric",
                                options=[
                                    {
                                        "label": "Cumulative GWP100",
                                        "value": "cumulative_gwp100",
                                    },
                                    {"label": "Forcing", "value": "radiative_forcing"},
                                    {"label": "Temperature", "value": "temperature"},
                                ],
                                value="cumulative_gwp100",
                            ),
                        ),
                        html.Div(
                            "Only precomputed combinations can be selected.",
                            id="sensitivity-status",
                            className="sensitivity-status",
                        ),
                    ],
                    className="sensitivity-controls",
                ),
                dcc.Graph(
                    id="sensitivity-chart",
                    figure=render_sensitivity(
                        "ENC market",
                        "ENC market",
                        60,
                        "cumulative_gwp100",
                        RESULT_BUNDLE,
                    ),
                    responsive=True,
                    config={"displayModeBar": False, "responsive": True},
                    className="sensitivity-chart",
                ),
                editorial.availability(RESULT_BUNDLE),
            ],
            className="sensitivity-layout"
            + (
                " no-sensitivity"
                if not any(
                    str(r.get("available", "false")).lower() in {"1", "true", "yes"}
                    for r in RESULT_BUNDLE.tables.get("sensitivity_availability", ())
                )
                else ""
            ),
        )

    elif appendix == 0:
        body = editorial.concept("primer")
    elif appendix == 1:
        body = editorial.quantity_table(ENGINEERING_FLOWS)
    elif appendix == 2:
        body = editorial.assumptions()
    elif appendix == 3:
        body = editorial.lifetime_calendar()
    elif appendix == 5:
        body = html.Div(
            [
                editorial.market_figure(RESULT_BUNDLE, other=True),
            ],
            className="market-layout",
        )
    else:
        body = editorial.provenance(RESULT_BUNDLE)
    return _slide_shell(
        index,
        body,
        eyebrow=f"Appendix {chr(65 + index - APPENDIX_START_SLIDE)}",
        class_name="appendix-slide",
        source=editorial.link("Model scope and assumptions", "contract"),
    )


RENDERERS = (
    _title_slide,
    _study,
    _three_systems,
    lambda i, s: _detailed_system(i, s, "BAU"),
    lambda i, s: _detailed_system(i, s, "CCS"),
    lambda i, s: _detailed_system(i, s, "CCUS"),
    _question,
    _current_result,
    _prospective_concept,
    _prospective_result,
    lambda i, s: _concept(
        i,
        s,
        "trails",
        (
            ("Construction", "2035"),
            ("Operation", "2035–2064"),
            ("Fuel use + EOL", "2065"),
        ),
    ),
    _temporal_result,
    lambda i, s: _concept(
        i,
        s,
        "fair",
        (
            ("Inventory", "Species resolved"),
            ("Response", "Forcing → temperature"),
            ("Horizon", "to 2200"),
        ),
    ),
    _fair_result,
    lambda i, s: _concept(
        i,
        s,
        "pulse",
        (
            ("Reference pulse", "2035"),
            ("Default window", "2025–2100"),
            ("Outputs", "Forcing / temperature eq."),
        ),
    ),
    _pulse_result,
    _synthesis,
    _resources,
    _discussion,
    *([_appendix] * APPENDIX_SLIDE_COUNT),
)


PRESENTER_NOTES = {
    0: (
        "Start with the choice between no capture investment, CCS and CCUS.",
        "Name the three systems in one sentence.",
        "Move directly to the source study.",
    ),
    1: (
        "The cement plant model comes from this publication.",
        "Stress that none of its LCA results are reused.",
        "We adapted the process model and added future conditions and emission timing.",
    ),
    2: (
        "The same amount of clinker is produced, but carbon destinations and heat use differ.",
        "Trace three CO₂ origins: limestone calcination, fossil fuel and non-fossil fuel.",
        "CCUS stores both fossil sources. Only captured non-fossil carbon becomes jet fuel.",
        "Lines identify origins, not quantities. Utilities, losses and fuel use follow on the detailed slides.",
    ),
    3: (
        "BAU means continuing clinker production without investing in capture.",
        "Chalk is approximately 1,300 kg as approved for display. This is rounded, not a public plant measurement.",
        "Fuel masses and fuel CO₂ are derived from published SI.2 using 2020-to-2050 interpolation. The LCA results have not yet been updated to match these fuel quantities.",
        "RDF contains both fossil and non-fossil carbon. Waste fuel does not mean entirely non-fossil fuel.",
        "Trace calcination, fossil fuel and non-fossil fuel CO₂ separately to the atmosphere.",
        "Electricity supplies both the kiln and heat recovery. Exported heat displaces gas-boiler heat in 2025.",
    ),
    4: (
        "CCS captures both fossil and non-fossil kiln carbon.",
        "Recovered heat first serves capture; only surplus is exported.",
        "Transport and North Sea storage occur in the production year.",
        "Read the carbon balance in kilograms of carbon, not CO₂ or CO₂-equivalent. Input equals air plus storage, for each fuel origin.",
        "Calcination and capture-boiler carbon follow the same route but are unquantified. This is not a complete plant carbon balance, and it does not update the LCA results.",
        "The SI.2 inventory implies 5% liquefaction and 1.44% transport loss. SI.1 prose instead mentions 3% injection loss. These are not combined here.",
    ),
    5: (
        "CCUS preserves carbon origin after capture.",
        "Fossil carbon is stored. Non-fossil carbon enters methanol-to-X, yielding jet fuel plus diesel and naphtha.",
        "The synthetic fuel displaces conventional jet fuel and burns one year later.",
        "The carbon balance shows carbon in jet fuel when it is produced. Combustion later releases that same carbon.",
        "85% methanol-carbon-to-jet yield and 85% jet carbon mass fraction are separate webinar assumptions, not measured published yields.",
        "Diesel and naphtha amounts follow UOP Table 2 normalized to pure methanol. Product carbon fractions are assumed, not measured.",
        "Residual carbon excludes all three products and is released as production-year CO₂. MTX uses separate gas-boiler heat at 0.9672 MJ/kg methanol, with uncaptured boiler emissions and no heat-recovery credit. Cooling, equipment and background-carbon checks remain open.",
        "Diesel and naphtha replace fossil fuel production and combustion. These credits occur in the production year, while the synthetic fuels burn one year later. No allocation is used.",
        "The avoided conventional jet production and combustion credit remains in the production year and is not another physical destination for captured carbon.",
    ),
    6: (
        "Do not announce a winner.",
        "LCA supports the investment decision: what climate benefits do CCS and CCUS deliver relative to BAU with neither investment? This is not a financial appraisal.",
        "First compare three inventory approaches. Then use the dated inventory to calculate climate response and pulse equivalents.",
        "More complex does not automatically mean more useful. Ask whether the added information changes the investment case.",
        "These diagrams explain the methods, not the results. Move directly to the 2025 results.",
    ),
    7: (
        "Use 2025 foreground and SSP2-NPi background conditions throughout the life-cycle inventory.",
        "Uptake and releases are aggregated without preserving their dates. Physical events do not all occur in 2025.",
        "Introduce this baseline method while reading the chart, without a separate concept slide.",
        "Read the first ranking from the chart.",
        "Three panels use identical Y scales. Each stage bar separates its positive and negative sub-process contributions.",
        "Start with the methanol-to-X key: distinguish avoided jet production and fossil combustion from synthetic-fuel combustion. Click another stage if useful.",
        "Ask what changes when the background moves to 2035.",
    ),
    8: (
        "Premise translates each REMIND-EU pathway into annual background matrices.",
        "Compare Northern European electricity and heat around 2035.",
        "The next results also include changes to the kiln and capture processes.",
    ),
    9: (
        "Start with NPi, then switch pathway.",
        "Point out any change in ranking or any result crossing zero.",
        "Timing inside the life cycle is still missing.",
    ),
    10: (
        "Construction, operation, replacement, uptake, and use now receive dates.",
        "The plant operates from 2035 through 2064.",
        "Historical uptake may begin before 2035; climate response continues to 2200.",
    ),
    11: (
        "Areas are annual; red is cumulative.",
        "GWP100 factors stay fixed. The inventory dates and background evolve.",
        "Emissions from suppliers can occur before or after the fuel-uptake periods shown.",
        "Explain that results are divided by total clinker production over 30 years before switching to absolute values.",
        "A flat cumulative GWP curve does not mean the climate response has ended.",
    ),
    12: (
        "TRAILS supplies annual emissions and uptake for each greenhouse gas.",
        "FaIR converts those emissions into forcing and temperature.",
        "GWP, forcing, and temperature answer different questions.",
    ),
    13: (
        "Forcing is the default.",
        "Use temperature and uncertainty only if time permits.",
        "BAU is the faint benchmark in CCS and CCUS panels.",
    ),
    14: (
        "The reference is one CO2 pulse in 2035.",
        "Equivalence matches integrated forcing or temperature over a chosen window.",
        "Use the equation to explain the ratio of the two areas.",
    ),
    15: (
        "Move the end-year handle first. Each bar is a separate window calculation, not an annual emission.",
        "The middle, orange handle changes the reference-pulse year. This does not change the plant’s emissions or its 2035 investment date.",
        "Compare the three options before moving to the summary.",
    ),
    16: (
        "Follow the ranking across methods and time.",
        "Do not reduce a time-varying ranking to one endpoint.",
        "Show the sources, then open the discussion.",
    ),
    17: (
        "Distinguish what comes from the original study from what we changed or added.",
        "Point to the public code and the tools used for the calculations.",
        "All citations remain clickable after the webinar.",
    ),
    18: (
        "Do not repeat the conclusion.",
        "Choose one of the three specific questions.",
        "Leave this slide on screen during Q&A.",
    ),
    19: (
        "Distinguish kilograms of CO₂ from kilograms of CO₂-equivalent.",
        "A characterization factor converts an inventory flow into its contribution to GWP100.",
        "Add releases, uptake and avoided emissions with their signs preserved.",
    ),
    20: (
        "These engineering records are not the SI-based illustrations on slides 4–6.",
        "Jet output differs between those records. Do not use this table as a reconciled carbon balance.",
        "Electricity stage values are included in the total, not additional to it.",
    ),
    21: (
        "Separate heat supplied to capture, gas-boiler heat for fuel conversion, and displaced heat supply.",
        "Board and paper sludge use the revised 15-year growth plus one-year delay assumptions.",
        "FaIR uncertainty covers climate-model parameters, not fuel histories or future energy scenarios.",
    ),
    22: (
        "Filled markers denote quantified equipment. Hollow markers show assumed schedules without equipment burdens.",
        "The existing storage site does not require new drilling in this model.",
        "Separate capture and fuel-conversion plant construction remain unquantified.",
    ),
    23: (
        "This is the dynamic sensitivity grid, separate from the static slide controls.",
        "Only calculated combinations may be interpreted. If none are available, skip the demonstration.",
        "Do not infer scores for disabled energy and fuel combinations.",
    ),
    24: (
        "Compare each sector across the two scenario columns.",
        "The vertical marker locates 2035. Areas show supply shares, not GWP contributions.",
        "Explain steelmaking abbreviations only if the audience asks about that sector.",
    ),
    25: (
        "Show the calculation records, not versions currently installed on the computer.",
        "A model identifier supports reproducibility but does not establish scientific validity.",
        "Review status and unresolved inventory assumptions remain separate from numerical checks.",
    ),
}


def render_slide(
    index: int, result_state: dict | None = None, print_mode: bool = False
):
    del print_mode
    index = max(0, min(len(RENDERERS) - 1, int(index)))
    state = normalize_result_state(result_state or DEFAULT_RESULT_STATE)
    return RENDERERS[index](index, state)


def slide_label(index: int) -> str:
    if index < CORE_SLIDE_COUNT:
        return f"{index + 1:02d} / {CORE_SLIDE_COUNT}"
    return f"A{index - APPENDIX_START_SLIDE + 1} / {APPENDIX_SLIDE_COUNT}"


def presenter_notes(index: int) -> tuple[str, ...]:
    if APPENDIX_START_SLIDE <= index < APPENDIX_START_SLIDE + APPENDIX_SLIDE_COUNT:
        index = APPENDIX_START_SLIDE + APPENDIX_SECTION_IDS[index - APPENDIX_START_SLIDE]
    return PRESENTER_NOTES.get(
        index,
        (
            "Explain the main point.",
            "Use the diagram or chart to explain it.",
            "Use one sentence to transition.",
        ),
    )
