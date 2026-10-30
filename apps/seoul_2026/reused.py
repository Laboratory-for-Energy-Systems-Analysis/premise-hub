"""Reuse existing teaching visuals without changing their source applications."""

from __future__ import annotations

import os
from dash import dcc, html
from apps.workshop.workshop import slides as workshop
from apps.setac_2026.figures import scenario_context_figure, scenario_context_rows
from .visuals import CASES, CASE, icon_svg, svg_uri, label


def _context_value(indicator, pathway, year):
    """Use the stored release without interpolation or a new scenario run."""
    rows = [r for r in scenario_context_rows()
            if r["indicator"] == indicator and r["region"] == "World"
            and r["pathway"] == pathway and int(r["year"]) == year]
    if len(rows) != 1:
        raise ValueError("Missing or ambiguous scenario teaching value")
    return float(rows[0]["value"])


def _icon(kind, colour):
    return html.Img(src=svg_uri(icon_svg(kind, colour), 64, 64, kind),
                    alt="", className="scenario-teaching-icon")

PREFIX = os.getenv("SEOUL_2026_REQUESTS_PREFIX", "/")


def find(component, css):
    if css in (getattr(component, "className", "") or "").split():
        return component
    children = getattr(component, "children", None)
    for child in children if isinstance(children, (list, tuple)) else [children]:
        if child is not None:
            found = find(child, css)
            if found is not None:
                return found
    return None


def adapt(component):
    value = getattr(component, "src", None)
    if isinstance(value, str) and "/assets/" in value:
        component.src = PREFIX + "workshop-assets/" + value.split("/assets/", 1)[1]
    children = getattr(component, "children", None)
    for child in children if isinstance(children, (list, tuple)) else [children]:
        if child is not None:
            adapt(child)
    return component


def _iam_linkage():
    """Broad IAM domain map; actual sector coverage and couplings vary by model."""
    body = '<defs><marker id="iam-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0 0L8 4L0 8Z" fill="#809ba6"/></marker></defs>'
    body += '<rect x="18" y="6" width="564" height="83" rx="18" fill="#e3eff5" stroke="#006b8f" stroke-width="2"/>'
    body += icon_svg("people", "#006b8f", 35, 24, 44)
    body += label(325, 40, "Economy, demand + investment", 25, "#006b8f")
    body += label(325, 69, "Services · consumption · trade", 21, "#435d6a", weight=400)
    sectors = (
        (18, 125, "power", "Energy + industry", "Power · fuels · materials", "#008a82"),
        (318, 125, "forest", "Land, food + forests", "Farming · bioenergy · land use", "#568044"),
        (18, 250, "buildings", "Transport + buildings", "Mobility · housing · infrastructure", "#8961a8"),
        (318, 250, "ocean", "Water + resources", "Availability · competing uses", "#3292b5"),
    )
    for x, y, kind, title, detail, colour in sectors:
        body += f'<rect x="{x}" y="{y}" width="264" height="100" rx="16" fill="white" stroke="{colour}" stroke-width="1.8"/>'
        body += icon_svg(kind, colour, x + 15, y + 17, 34)
        body += label(x + 157, y + 38, title, 20, colour)
        body += label(x + 132, y + 76, detail, 17, "#435d6a", weight=400)
    # Shared economic drivers and cross-sector resource/market interactions.
    for x in (150, 450):
        body += f'<path d="M{x} 89V118" stroke="#809ba6" stroke-width="2" marker-end="url(#iam-arrow)"/>'
    for y in (175, 300):
        body += f'<path d="M287 {y}H313" stroke="#809ba6" stroke-width="2" marker-start="url(#iam-arrow)" marker-end="url(#iam-arrow)"/>'
    for x in (150, 450):
        body += f'<path d="M{x} 231V244" stroke="#809ba6" stroke-width="2" marker-start="url(#iam-arrow)" marker-end="url(#iam-arrow)"/>'
        body += f'<path d="M{x} 350V380" stroke="#809ba6" stroke-width="2" marker-end="url(#iam-arrow)"/>'
    body += '<rect x="18" y="386" width="564" height="78" rx="18" fill="#f7eee7" stroke="#ad603d" stroke-width="2"/>'
    body += icon_svg("atmosphere", "#ad603d", 35, 401, 44)
    body += label(325, 420, "Emissions, climate + environment", 24, "#ad603d")
    body += label(325, 449, "Carbon cycle · air · water · ecosystems", 20, "#435d6a", weight=400)
    return html.Img(
        src=svg_uri(body, 600, 480, "IAM domains beyond energy: economy, industry, land, food, forests, transport, buildings, water, resources and environmental response"),
        alt="Conceptual IAM map. Economic demand and investment link energy and industry, land/food/forestry, transport/buildings and water/resources. These domains interact through shared resources, markets and trade, and contribute to emissions and climate/environmental responses. Actual scope and feedbacks differ between models and linked modules.",
        className="iam-linked-diagram",
    )


def _iam_model_strip():
    import json
    from pathlib import Path

    models = json.loads((Path(__file__).parent / "data/iam_logos.json").read_text())["models"]
    return html.Div([
        html.A([
            html.Div(html.Img(src=PREFIX + "assets/iam-logos/" + model["filename"],
                             alt=model["image_alt"]),
                     className="iam-model-logo dark" if model.get("dark") else "iam-model-logo"),
            html.Div([html.Strong(model["name"]), html.Span(model["caption"])], className="iam-model-label"),
        ], href=model["homepage"], target="_blank", rel="noopener noreferrer",
           className="iam-model-card", title=model["name"] + " · " + model["kind"])
        for model in models
    ], className="iam-model-strip", **{"aria-label": "Widely used IAM model families and their official model or team marks"})


def _iam_context_graph(indicator):
    figure = scenario_context_figure(indicator, "World", "SSP2-PkBudg1000")
    figure.update_layout(title=None, height=None,
        font=dict(family="Arial", size=14, color="#173747"),
        margin=dict(l=42, r=10, t=12, b=38),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(x=0, y=-.24, orientation="h", font=dict(size=12)))
    figure.update_xaxes(range=[2024, 2102], tickvals=[2025, 2050, 2100],
                        tickfont_size=12, title=None)
    figure.update_yaxes(tickfont_size=12, gridcolor="#dce6ea", title=None)
    if indicator == "Population":
        # Both policy scenarios share exactly the same population inputs.
        if list(figure.data[0].y) != list(figure.data[1].y):
            raise ValueError("Population assumptions differ between the scenario extracts")
        figure.data = (figure.data[0],)
        figure.data[0].update(name="SSP2 · both pathways", opacity=1,
            line=dict(color="#3292b5", width=3, dash="solid"), fill="tozeroy",
            fillcolor="rgba(50,146,181,.10)")
        figure.update_yaxes(range=[7, 11], tickvals=[8, 9, 10, 11])
        figure.update_layout(showlegend=False)
    else:
        figure.update_yaxes(range=[1, 3], tickvals=[1, 2, 3])
    return dcc.Graph(figure=figure, config={"displayModeBar": False},
                     responsive=True, className="iam-context-chart")


def iam_systems():
    panels = html.Div(
        [
            html.Section([
                html.H2("1 · Set assumptions"),
                html.Div([_icon("people", "#3292b5"), html.Div([
                    html.Strong("Population + income"), html.Span("Demand for energy and services")
                ])], className="iam-icon-row"),
                html.Div([html.Strong("World population · SSP2"), html.Span("Billion people · shared by both pathways")], className="iam-chart-heading"),
                _iam_context_graph("Population"),
                html.Div([_icon("investment", "#c18a1b"), html.Div([
                    html.Strong("Technology + resources"), html.Span("Costs, learning and available options")
                ])], className="iam-icon-row"),
                html.Div([_icon("policy", "#008a82"), html.Div([
                    html.Strong("Policy constraints"), html.Span("Taxes, targets and carbon budgets")
                ])], className="iam-icon-row"),
            ], className="iam-inputs"),
            html.Section([
                html.H2("2 · Link sectors and constraints"),
                _iam_linkage(),
                html.Div([html.Strong("Competing demands, shared constraints"),
                    html.Span("Energy, land, food and materials interact; coverage varies by model.")
                ], className="iam-investment-question"),
                html.A("IMAGE framework · human and Earth systems",
                    href="https://models.pbl.nl/image/IMAGE_framework", target="_blank", rel="noopener noreferrer"),
            ], className="iam-engine"),
            html.Section([
                html.H2("3 · Read conditional outputs"),
                html.Div([html.Strong("Scenario climate background"), html.Span("Global warming · °C above 1850–1900")], className="iam-chart-heading"),
                _iam_context_graph("GMST"),
                html.Div("Stored MAGICC7 medians", className="iam-data-label"),
                html.Div([_icon("power", "#008a82"), html.Div([
                    html.Strong("Technology and fuel mixes"), html.Span("Power, heat, transport and industry")
                ])], className="iam-icon-row"),
                html.Div([_icon("atmosphere", "#ad603d"), html.Div([
                    html.Strong("Land, water + emissions"), html.Span("Regional production and environmental pressures")
                ])], className="iam-icon-row"),
                html.Div("→ Evidence for future LCA suppliers", className="iam-lca-destination"),
            ], className="iam-outputs"),
        ], className="iam-visual-tour",
        **{"data-reused-from": "/workshop/ · coupled IAM lesson; /setac-2026/ · stored REMIND-EU scenario context"},
    )
    return html.Div([panels, _iam_model_strip()], className="iam-expanded-lesson")


def scenario_layers(ssp_index, pathways_index):
    original = workshop.slide_scenario_combinations()
    equation = find(original, "scenario-equation")
    parts = [c for c in equation.children
             if "scenario-equation-part" in (getattr(c, "className", "") or "").split()]
    assert len(parts) == 4
    for part, (name, detail) in zip(parts, (
        ("Societal storyline", "How might society develop?"),
        ("IAM model", "How are systems represented?"),
        ("Climate assumptions", "Policies or forcing constraint"),
        ("Conditional pathways", "Energy, land, production, emissions"),
    )):
        part.children = [html.Strong(name), html.Span(detail)]
    stories = (
        ("SSP1", "Sustainability", "Cooperation, resource efficiency, less inequality.", "#008a82"),
        ("SSP2", "Middle of the road", "Uneven progress; development follows past trends.", "#3292b5"),
        ("SSP3", "Regional rivalry", "Fragmentation, weak cooperation, slow development.", "#ad603d"),
        ("SSP4", "Inequality", "Large gaps in wealth, opportunity and capabilities.", "#8961a8"),
        ("SSP5", "Fossil-fuelled development", "Rapid growth and energy-intensive fossil use.", "#8e4656"),
    )
    pathways = (
        ("SSP1-1.9", "Very low emissions", "Rapid cuts; net-zero CO₂ around mid-century.", "#008a82"),
        ("SSP1-2.6", "Low emissions", "Strong cuts; net-zero CO₂ later in the century.", "#2876ad"),
        ("SSP2-4.5", "Intermediate emissions", "CO₂ stays near today's level, then declines.", "#b58a20"),
        ("SSP3-7.0", "High emissions", "Emissions keep rising through much of the century.", "#c26b36"),
        ("SSP5-8.5", "Very high emissions", "Fossil-intensive growth; CO₂ roughly doubles by 2050.", "#9a3d50"),
    )

    def rows(items):
        return html.Div([
            html.Div([
                html.Strong(code, className="scenario-row-code", style={"color": colour}),
                html.Div([html.B(name), html.Span(detail)]),
            ], role="listitem", className="scenario-detail-row", style={"--row-colour": colour})
            for code, name, detail, colour in items
        ], role="list", className="scenario-detail-rows")

    return html.Div([
        equation,
        html.Div([
            html.Article([
                html.Span("SOCIETY · FIVE DEVELOPMENT STORIES", className="scenario-detail-eyebrow"),
                html.H2("Shared Socioeconomic Pathways"),
                rows(stories),
            ], className="scenario-storylines"),
            html.Article([
                html.Span("MODEL · COMBINE THE ASSUMPTIONS", className="scenario-detail-eyebrow"),
                html.H2("One SSP, several climate pathways"),
                html.Div([
                    html.Strong("SSP1"), html.Span("→"),
                    html.Div([html.B("SSP1-1.9"), html.B("SSP1-2.6")]),
                ], className="scenario-assumption-fork", **{"aria-label": "The same SSP1 storyline can underpin very-low and low-emission pathways"}),
                html.P("The IAM translates socioeconomic and climate assumptions into regional, sector-specific trajectories."),
                html.Div([
                    html.Strong("In this lecture"),
                    html.B("SSP2 + REMIND-EU"),
                    html.Div([html.Span("NPi"), html.Small("Implemented national policies")]),
                    html.Div([html.Span("PkBudg1000"), html.Small("Carbon-budget constraint")]),
                    html.Small("Median GMST · above 1850–1900"),
                ], className="scenario-lecture-example"),
            ], className="scenario-model-link"),
            html.Article([
                html.Span("CLIMATE · FIVE AR6 EXAMPLES", className="scenario-detail-eyebrow"),
                html.H2("Illustrative emissions pathways"),
                html.Div("Numeric suffix ≈ forcing in 2100 · W/m²", className="scenario-forcing-key"),
                rows(pathways),
            ], className="scenario-climate-pathways"),
        ], className="scenario-detail-grid"),
        html.Div([
            html.Div([
                html.Span("IPCC · Intergovernmental Panel on Climate Change", className="scenario-ipcc-title"),
                html.Strong("Research teams develop scenarios → IPCC assesses the evidence"),
            ], className="scenario-ipcc-message"),
            html.Div([
                html.Span([html.B("WG I"), "Climate response"]),
                html.Span([html.B("WG II"), "Impacts + adaptation"]),
                html.Span([html.B("WG III"), "Mitigation pathways"]),
            ], className="scenario-ipcc-groups"),
        ], className="scenario-ipcc"),
        html.Div([
            html.A("SSP narratives · more detail →", href=f"#slide-{ssp_index}", className="scenario-detail-link"),
            html.A("RCP / emissions trajectories · more detail →", href=f"#slide-{pathways_index}", className="scenario-detail-link"),
        ], className="scenario-backup-links"),
        html.Div([
            html.A("IPCC AR6 · SSP framework", href="https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1/", target="_blank", rel="noopener noreferrer"),
            html.A("AR6 illustrative scenarios", href="https://www.ipcc.ch/report/ar6/wg1/chapter/summary-for-policymakers/", target="_blank", rel="noopener noreferrer"),
            html.A("IPCC assessment role", href="https://www.ipcc.ch/working-groups/", target="_blank", rel="noopener noreferrer"),
        ], className="scenario-detail-references"),
    ], className="scenario-details",
       **{"data-reused-from": "/workshop/ · scenario combinations, five SSP narratives and IPCC assessment role"})

def premise_bridge():
    original = workshop.slide_premise_library()
    layout = find(original, "premise-library-visual-layout")
    stats = find(layout, "premise-library-stat-ribbon")
    if stats is not None:
        stats.children = []
    return adapt(
        html.Div(
            [layout],
            className="reused-premise",
            **{
                "data-reused-from": "/workshop/ · Premise translates scenarios; it is not a scenario model"
            },
        )
    )


def pathway_story():
    baseline = _context_value("CO2", "SSP2-NPi", 2025) * 1e-9
    values = {p: _context_value("CO2", "SSP2-" + p, 2050) * 1e-9
              for p in ("NPi", "PkBudg1000")}
    figure = scenario_context_figure("CO2", "World", "SSP2-PkBudg1000")
    figure.update_layout(font=dict(family="Arial", size=16), height=None,
        title=None, margin=dict(l=60, r=16, t=35, b=45),
        legend=dict(x=0, y=1.13, orientation="h", font=dict(size=15)))
    figure.update_xaxes(range=[2024, 2053], tickvals=[2025, 2035, 2050],
                        tickfont_size=15, title="Calendar year")
    figure.update_yaxes(title="Global net CO₂ · Gt / year", tickfont_size=14, range=[0, 48])
    figure.data[1].update(fill="tonexty", fillcolor="rgba(0,138,130,.10)")
    figure.add_vline(x=2050, line_dash="dot", line_color="#607780")
    figure.add_annotation(x=2025, y=baseline, text=f"Common 2025: {baseline:.1f}",
        showarrow=False, xanchor="left", yshift=17, font=dict(size=14, color="#173747"))
    for pathway, colour in (("NPi", "#607780"), ("PkBudg1000", "#008a82")):
        figure.add_annotation(x=2050, y=values[pathway],
            text=f"{pathway}: {values[pathway]:.1f}", showarrow=False,
            xanchor="right", yshift=17, font=dict(size=15, color=colour))
    figure.add_annotation(x=2043, y=25, text=f"{values['NPi'] - values['PkBudg1000']:.1f} Gt/yr apart<br>in 2050",
        showarrow=False, font=dict(size=14, color="#006d65"), bgcolor="rgba(255,255,255,.8)", borderpad=5)
    policies = (("NPi", "National policies implemented", "#607780"),
                ("PkBudg1000", "Carbon-budget constraint", "#008a82"))
    dependencies = (
        ("power", "Energy to run capture", "Cleaner power and heat can reduce operating burdens."),
        ("forest", "The displaced energy system", "Cleaner alternatives can shrink electricity and heat credits."),
        ("rock", "Rock preparation + transport", "Grinding power and haulage technologies change."),
        ("kiln", "Capture utilities + kiln fuels", "Fuel mix, heat supply and capture design evolve."),
    )
    return html.Div([
        html.Div([
            html.Div([
                html.Div("SAME YEAR · DIFFERENT FUTURE SYSTEMS", className="pathway-story-kicker"),
                dcc.Graph(figure=figure, config={"displayModeBar": False}, responsive=True, className="chart"),
            ], className="pathway-evidence"),
            html.Div([
                html.Div("2050 · TWO CONDITIONAL WORLDS", className="pathway-story-kicker"),
                html.H2("Policy changes investment choices"),
                html.Div([
                    html.Article([
                        html.Strong(p), html.Span(description),
                        html.Div([html.B(f"{values[p]:.1f}"), html.Span("Gt CO₂ / year")], className="pathway-value"),
                        html.Small(f"{100 * (1 - values[p] / baseline):.0f}% below the common 2025 level"),
                    ], style={"--pathway-colour": colour})
                    for p, description, colour in policies
                ], className="pathway-policy-cards"),
                html.Div([html.Strong("Power · heat · fuels · industrial routes"),
                    html.Span("The regional and sector-specific changes determine which suppliers a future project uses.")
                ], className="pathway-translation"),
                html.P("The global curve provides context; it is not an electricity emission factor.", className="pathway-scope"),
            ], className="pathway-implications"),
        ], className="pathway-decision"),
        html.Div([
            html.Article([
                html.Div([_icon(kind, CASE[case]["colour"]), html.Strong(case)], className="pathway-case-heading"),
                html.B(title), html.Span(detail),
            ], style={"--case-colour": CASE[case]["colour"]}, **{"data-case": case})
            for case, (kind, title, detail) in zip(CASES, dependencies)
        ], className="pathway-case-links"),
    ], className="pathway-story",
       **{"data-reused-from": "/setac-2026/ · stored REMIND-EU / SSP2 scenario context"})

def thank_you():
    """Adapt SETAC's two-column conclusion/contact slide to the Seoul lecture."""
    from apps.setac_2026 import deck as setac
    from .layout import _rewrite

    closing = setac._closing()
    summary = find(closing, "closing-summary")
    outlook = find(closing, "closing-outlook")
    from .closing_scores import score_table
    summary.children = [score_table()]
    outlook.children = [
        html.Span(
            "Seoul National University · 30 October 2026", className="small-label"
        ),
        html.H3("Graduate LCA seminar"),
        html.P("With thanks to Jooyoung Park and the course participants."),
    ]
    funding = find(closing, "funding-acknowledgement")
    funding.children[1].children[1].children = [
        "European Union · ",
        html.A(
            "Grant agreement 101081521",
            href="https://cordis.europa.eu/project/id/101081521",
            target="_blank",
        ),
    ]
    return _rewrite(
        html.Div(
            [closing],
            className="reused-setac-closing",
            **{"data-reused-from": "/setac-2026/ · conclusions and thank-you slide"},
        )
    )
