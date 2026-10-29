"""Worked teaching views adapted from the four source lectures.

These explain the existing model; they neither rebuild inventories nor import
legacy climate results. Quantitative contribution examples use Seoul's checked
foreground/root extracts, including the full upstream score of each supplier.
"""

from functools import lru_cache
import json
from pathlib import Path

from dash import html
import plotly.graph_objects as go

from .visuals import CASES, CASE, timeline, icon_svg, svg_uri
from . import comparison as compare
from .layout import PREFIX
from .branding import logo, logo_uri, database_icon


def lesson_switch(name, panels, *, print_mode=False):
    """Keep live panels mounted; export only the curated first view."""
    if print_mode:
        return panels[0][1]
    return html.Div(
        [
            html.Div(
                [
                    html.Button(
                        title,
                        role="tab",
                        tabIndex=0 if i == 0 else -1,
                        **{"aria-selected": str(i == 0).lower(), "data-lesson-select": i},
                    )
                    for i, (title, _) in enumerate(panels)
                ],
                role="tablist",
                **{"aria-label": name},
                className="lesson-tabs",
            ),
            *[
                html.Div(
                    panel,
                    hidden=i != 0,
                    role="tabpanel",
                    className="lesson-panel",
                    **{"aria-label": title, "data-lesson-panel": i},
                )
                for i, (title, panel) in enumerate(panels)
            ],
        ],
        className="lesson-switch",
        **{"data-lesson-index": 0},
    )


def _case_name(case):
    return html.Strong(case, style={"color": CASE[case]["colour"]})


def reference_systems():
    projects = (
        ("Air capture + geological storage", "No DAC plant", "1 t CO₂ physically stored"),
        ("Harvest + CHP + capture + regrowth", "Forest left standing + equivalent market energy", "1 t CO₂ physically stored"),
        ("Grind + spread rock → later atmospheric uptake", "No additional rock deployment", "1.25 t rock deployed"),
        ("Clinker production with capture + storage", "The same clinker without capture", "1 t CO₂ stored · matching clinker · CCS − BAU"),
    )
    return html.Div(
        [
            html.Div(
                [html.Strong("Physical service ≠ life-cycle climate benefit"),
                 html.Span("Define the project and its reference before reading a negative score.")],
                className="method-message",
            ),
            html.Div(
                [
                    html.Article(
                        [
                            html.Div([_case_name(case), html.Span(service)], className="reference-heading"),
                            html.Div(
                                [
                                    html.Div([html.Span("PROJECT"), html.Strong(project)], className="reference-project"),
                                    html.B("vs"),
                                    html.Div([html.Span("REFERENCE"), html.Strong(reference)], className="reference-baseline"),
                                ], className="reference-pair",
                            ),
                        ],
                        className="reference-card",
                        style={"--case-colour": CASE[case]["colour"]},
                        **{"data-case": case},
                    )
                    for case, (project, reference, service) in zip(CASES, projects)
                ], className="reference-grid",
            ),
        ], className="method-page",
        **{"data-reused-from": "/lca-time/ · functional unit and project versus reference"},
    )


@lru_cache(maxsize=2)
def electricity_root_score(year):
    data = json.loads((Path(__file__).parent / "data" / f"cdr_static_roots_{year}.json").read_text())
    return sum(
        row["score"] for row in data["cases"]["DACCS"]["suppliers"]
        if (row["activity"], row["reference_product"], row["location"]) ==
        ("market group for electricity, medium voltage", "electricity, medium voltage", "ENC")
    )


def supplier_trace():
    steps = (
        ("01", "Scenario evidence", "REMIND-EU · ENC", "Electricity technology shares and efficiencies"),
        ("02", "premise transforms", "Map → update → relink", "Rebuild the market and its generation suppliers"),
        ("03", "Foreground connects", "DACCS buys electricity", "Its kWh demand links to the transformed market"),
    )
    fig = go.Figure()
    fig.add_bar(
        x=["2025 · NPi", "2050 · PkBudg1000"],
        y=[electricity_root_score(y) for y in (2025, 2050)],
        marker_color=["#8ab9cd", CASE["DACCS"]["colour"]],
        text=[f"+{electricity_root_score(y):.1f}" for y in (2025, 2050)],
        textposition="outside", cliponaxis=False,
        hovertemplate="%{x}<br>Electricity roots: %{y:.2f} kg CO₂-eq / net t stored<extra></extra>",
    )
    compare.style(fig, ytitle="kg CO₂-eq / net t stored")
    fig.update_yaxes(range=[0, 120])
    fig.update_layout(margin=dict(l=62, r=20, t=28, b=48), meta=dict(
        source="Seoul checked static root extracts", boundary="complete electricity root suppliers",
        comparison="different year and scenario; not an isolated policy experiment",
    ))
    choices = (
        "Electricity demand · heat pump · sorbent",
        "Forest reference · harvest · energy exports",
        "Grain size · grinding · uptake kinetics",
        "Kiln fuel · capture rate · utilities",
    )

    def step(number, title, main, detail):
        return html.Article([
            html.Span(number), html.H2(title),
            *([logo("premise", "trace-premise-logo")] if number == "02" else []),
            html.Strong(main), html.P(detail),
            *([html.Div([
                html.Div([
                    html.Div([database_icon(), logo("ecoinvent", "trace-ecoinvent-logo")],
                             className="trace-database-brand"),
                    html.Span("3.12 · cut-off background"),
                ], className="trace-database-input"),
                html.B("→", className="trace-database-arrow"),
                html.Div([database_icon(), html.Span("Scenario-updated suppliers")],
                         className="trace-database-output"),
            ], className="trace-background-transform")]
              if number == "02" else []),
        ], className="trace-transform-step" if number == "02" else "")

    return html.Div(
        [
            html.Div([
                step(n, title, main, detail)
                for n, title, main, detail in steps
            ], className="trace-steps"),
            html.Div(
                [
                    html.Article(
                        [html.Span("04 · OBSERVE THE CONTRIBUTION", className="method-kicker"),
                         html.H2("DACCS electricity supply"), compare.graph(fig)],
                        className="trace-result",
                    ),
                    html.Article(
                        [html.H2("The analyst supplies the foreground"),
                         *[html.Div([_case_name(case), html.Span(choice)], className="foreground-choice")
                           for case, choice in zip(CASES, choices)]],
                        className="foreground-choices",
                    ),
                ], className="trace-bottom",
            ),
        ], className="method-page supplier-trace",
        **{"data-reused-from": "/workshop/ · transformation coverage and result tracer"},
    )


def clocks(print_mode=False):
    return html.Div([
        html.Div([
            html.Span([html.I(className="clock-equipment-key"), "Equipment + recurring inputs"]),
            html.Span([html.I(className="clock-carbon-key"), "Carbon pathways"]),
            html.Strong("Equipment stages + ERW arrows schematic"),
        ], className="project-clocks-key"),
        timeline(),
    ], className="project-clocks", **{"data-reused-from": "/ccus-webinar/ · component calendar; /lca-time/ · cohort timeline"})


def routing_lesson(print_mode=False):
    from .routing import routing_lesson as split_routing_lesson

    return split_routing_lesson(print_mode)


def fair_handoff():
    """One scenario branches into the inventory economy and climate background."""
    from .visuals import label

    teal, blue, purple = "#008a82", "#527b90", "#7656a8"
    body = (
        '<defs>'
        + ''.join(f'<marker id="arrow-{name}" markerWidth="7" markerHeight="7" '
                  f'refX="6" refY="3.5" orient="auto"><path d="M0 0L7 3.5L0 7" '
                  f'fill="{colour}"/></marker>'
                  for name, colour in (("economy",teal),("atmosphere",blue),("response",purple)))
        + '</defs>'
        # A single source visibly branches into the two scenario-dependent inputs.
        f'<path d="M176 73H205" fill="none" stroke="{teal}" stroke-width="3"/>'
        f'<circle cx="205" cy="73" r="4" fill="{teal}"/>'
        + ''.join(f'<path d="{path}" fill="none" stroke="{teal}" stroke-width="3" '
                  'marker-end="url(#arrow-economy)"/>'
                  for path in ("M205 73V32H242", "M482 32H532",
                               "M786 32H820Q838 32 838 50V63H871"))
        + f'<path d="M205 73V113H242" fill="none" stroke="{blue}" stroke-width="3" '
        'marker-end="url(#arrow-atmosphere)"/>'
        f'<path d="M662 113H871" fill="none" stroke="{blue}" stroke-width="3" '
        'marker-end="url(#arrow-atmosphere)"/>'
        f'<path d="M1138 82H1194" fill="none" stroke="{purple}" stroke-width="3" '
        'marker-end="url(#arrow-response)"/>'
        # Economy branch: premise suppliers become dated project emissions.
        '<rect x="1" y="39" width="175" height="69" rx="12" fill="#eaf4f2" stroke="#91bfb8"/>'
        + label(88,68,"IAM scenario",21,anchor="middle",weight=750)
        + label(88,91,"One shared pathway",15,teal,weight=500)
        + '<rect x="242" y="2" width="240" height="60" rx="10" fill="#edf8f4" stroke="#b5d9d0"/>'
        + f'<image href="{logo_uri("premise")}" x="253" y="12" width="40" height="40"/>'
        + label(306,27,"premise",22,anchor="start",weight=750)
        + label(306,49,"Future LCA suppliers",16,anchor="start",weight=500)
        + '<rect x="532" y="2" width="254" height="60" rx="10" fill="#edf8f4" stroke="#b5d9d0"/>'
        + f'<image href="{logo_uri("trails")}" x="543" y="12" width="40" height="40"/>'
        + label(597,27,"TRAILS inventory",21,anchor="start",weight=750)
        + label(597,49,"Dated project emissions",16,anchor="start",weight=500)
        # Atmospheric branch: scenario emissions drive FaIR concentrations.
        + '<rect x="242" y="87" width="420" height="51" rx="10" fill="#edf4fa" stroke="#bfd1df"/>'
        + f'<g fill="none" stroke="{blue}" stroke-width="2.2">'
          '<path d="M258 98V128H295M262 101L271 105L280 116L292 122"/>'
          '<path d="M262 113L272 115L282 121L292 124" opacity=".5"/></g>'
        + label(309,109,"Future background GHG emissions",19,anchor="start",weight=700)
        + label(309,129,"From that same IAM scenario",15,blue,anchor="start",weight=500)
        + '<rect x="871" y="36" width="267" height="102" rx="12" fill="#f0f5fa" stroke="#a8c2d3"/>'
        + f'<g transform="translate(886 47) scale(.55)" fill="none" stroke="{blue}" stroke-width="2.2">'
          '<circle cx="32" cy="32" r="25"/><ellipse cx="32" cy="32" rx="12" ry="25"/>'
          '<path d="M8 24h48M8 40h48M32 7v50"/></g>'
        + label(935,66,"FaIR",23,anchor="start",weight=750)
        + label(1004,94,"→ Gas concentrations",18,blue,weight=650)
        + label(1004,121,"With project − without project",15,blue,weight=500)
        + '<rect x="1194" y="39" width="205" height="90" rx="12" fill="#f3eff9" stroke="#cbbddd"/>'
        + label(1296,70,"Climate response",21,purple,weight=750)
        + label(1296,99,"Δ forcing → Δ temperature",15,purple,weight=500)
    )
    description = (
        "One IAM scenario branches into premise's future LCA suppliers, then the dated "
        "TRAILS project inventory, and into future background GHG emissions. Both feed "
        "FaIR, which calculates gas concentrations and compares with-project against "
        "without-project to obtain the climate response."
    )
    return html.Div(
        html.Img(src=svg_uri(body,1400,142,description),alt=description,
                 className="fair-consistency-graph"),
        className="fair-handoff",
        **{"data-reused-from": "/setac-2026/ · TRAILS inventories into FaIR"},
    )


def uncertainty_map():
    sources = (
        ("01", "Scenario assumptions", "Different possible supply systems", "REMIND policy pathway, energy mix and material routes. Scenario alternatives are not probability bands."),
        ("02", "Foreground + reference", "A different project comparison", "DAC energy demand; BECCS forest and displaced energy; ERW grinding; cement’s clinker reference."),
        ("03", "Timing evidence", "A different schedule", "Regrowth, dissolution, air–sea uptake, equipment life and replacement dates."),
        ("04", "Climate parameters", "A different response to the inventory", "FaIR configurations describe climate-model uncertainty. They do not sample the other three layers."),
    )
    return html.Div(
        [html.Div([html.Strong("One uncertainty band does not cover the whole study"),
                   html.Span("Change one assumption at a time to understand what drives the answer.")], className="method-message"),
         html.Div([
             html.Article([html.Span(n, className="method-kicker"), html.H2(title), html.Strong(main), html.P(detail)], className="uncertainty-card")
             for n, title, main, detail in sources
         ], className="reference-grid")], className="method-page",
        **{"data-reused-from": "/workshop/ · limitations; /ccus-webinar/ · uncertainty scope; /setac-2026/ · forest sensitivity"},
    )


def method_choices():
    rows = (
        ("1 · CHOOSE THE INVENTORY MODEL", (
            ("Current static", "One present-day supply system", "Screen today’s hotspots"),
            ("Prospective static", "One scenario + future year", "Test future production conditions"),
            ("Time-explicit", "Dated events + annual backgrounds", "Retain operation, regrowth and uptake schedules"),
        )),
        ("2 · CHOOSE THE CLIMATE QUESTION", (
            ("GWP100", "What is the aggregate inventory score?", "Fixed factors, including for a dated inventory"),
            ("Climate trajectory", "When does the influence occur?", "Forcing and temperature through time"),
            ("CO₂-pulse-eq", "What dated pulse matches the integrated effect?", "Declared background, window and reference pulse"),
        )),
    )
    return html.Div(
        [
            *[html.Div([html.Strong(heading, className="method-row-heading"),
                        html.Div([html.Article([html.H2(title), html.Strong(question), html.P(detail)])
                                  for title, question, detail in items], className="method-choice-row")], className="method-choice-layer")
              for heading, items in rows],
            html.Div([html.Strong("A stable ranking can still hide a delayed benefit."),
                      html.Span("Use enough temporal detail to answer the decision question.")], className="method-message decision-message"),
        ], className="method-page method-choices",
        **{"data-reused-from": "/ccus-webinar/ · inventory approaches then climate response; /lca-time/ · method choice"},
    )
