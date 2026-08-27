from __future__ import annotations

import re

from dash import dcc, html
from dash.development.base_component import Component

from .config import (
    ANONYMOUS_ORDER,
    APPENDIX_SLIDE_COUNT,
    APPENDIX_START_SLIDE,
    BACKUP_LINKS,
    CORE_SCENARIOS,
    CORE_SLIDE_COUNT,
    NARRATIVES,
    PREMISE_TRANSFORMATIONS,
    REGION_MAPPING,
    SLIDE_TITLES,
)
from .data import (
    iam_region_topologies,
    image_electricity_chain,
    image_end_use_transformations,
    image_total_energy_chain,
    lcia_contributions,
    lcia_results,
    pathways,
    premise_mapping_counts,
)
from .figures import (
    CAPSTONE_CASE_SPECS,
    CAPSTONE_INDICATOR_SPECS,
    carbon_budget_figure,
    capstone_contribution_figure,
    capstone_lcia_trajectory_figure,
    capstone_signal_figure,
    cdr_overshoot_summary_figure,
    cmip7_family_figure,
    cmip7_gmst_trajectory_figure,
    commodity_gwp_figure,
    controlled_comparison_figure,
    energy_accounting_example_figure,
    energy_emissions_change_figure,
    end_use_transformation_figure,
    final_energy_layer_figure,
    ghg_gas_figure,
    ghg_region_figure,
    ghg_sector_figure,
    iam_mechanics_figure,
    iam_world_geography_figure,
    image_geography_figure,
    integration_matrix_figure,
    lcia_evidence_figure,
    model_coverage_figure,
    primary_energy_layer_figure,
    rcp_forcing_trajectory_figure,
    rcp_gmst_trajectory_figure,
    remind_eu_geography_figure,
    same_net_zero_date_figure,
    scenario_trajectory,
    sector_mitigation_potential_figure,
    sector_snapshot,
    secondary_energy_layer_figure,
    sector_total_figure,
    ssp_baseline_comparison_figure,
    steel_causal_chain_figure,
    total_energy_system_figure,
)

PREMISE_NAME = re.compile(r"\bpremise\b", flags=re.IGNORECASE)
_ASSET_PREFIX = "/assets/"


def configure_asset_prefix(requests_prefix: str = "/") -> None:
    global _ASSET_PREFIX
    normalized = f"/{requests_prefix.strip('/')}" if requests_prefix.strip("/") else ""
    _ASSET_PREFIX = f"{normalized}/assets/"


def asset_url(filename: str) -> str:
    return f"{_ASSET_PREFIX}{filename}"


def style_premise_text(text: str):
    """Render every software-name mention as italicized, capitalized Premise."""
    matches = list(PREMISE_NAME.finditer(text))
    if not matches:
        return text
    children = []
    cursor = 0
    for match in matches:
        if match.start() > cursor:
            children.append(text[cursor : match.start()])
        children.append(html.Em("Premise", className="premise-name"))
        cursor = match.end()
    if cursor < len(text):
        children.append(text[cursor:])
    return children


def _style_premise_mentions(component):
    if isinstance(component, str):
        return style_premise_text(component)
    if not isinstance(component, Component):
        return component
    children = getattr(component, "children", None)
    if isinstance(children, str):
        component.children = style_premise_text(children)
    elif isinstance(children, (list, tuple)):
        styled_children = []
        for child in children:
            styled = _style_premise_mentions(child)
            if isinstance(child, str) and isinstance(styled, list):
                styled_children.extend(styled)
            else:
                styled_children.append(styled)
        component.children = styled_children
    elif isinstance(children, Component):
        component.children = _style_premise_mentions(children)
    return component


def eyebrow(text: str) -> html.Div:
    return html.Div(text, className="eyebrow")


def title(text: str, subtitle: str | None = None) -> html.Div:
    children = [html.H1(text, className="slide-title")]
    if subtitle:
        children.append(html.P(subtitle, className="slide-subtitle"))
    return html.Div(children, className="title-block")


def takeaway(text: str) -> html.Div:
    return html.Div(
        [html.Span("Takeaway", className="takeaway-label"), html.P(text)],
        className="takeaway",
    )


def source_note(text: str) -> html.Div:
    return html.Div(text, className="source-note")


def graph(figure, class_name: str = "graph-frame") -> html.Div:
    return html.Div(
        dcc.Graph(
            figure=figure,
            config={"displayModeBar": False, "responsive": True},
            className="workshop-graph",
        ),
        className=class_name,
    )


def info_card(heading: str, body: str, accent: str = "") -> html.Div:
    return html.Div(
        [html.H3(heading), html.P(body)], className=f"concept-card {accent}".strip()
    )


def metric_card(value: str, heading: str, body: str, accent: str = "") -> html.Div:
    return html.Div(
        [
            html.Div(value, className="metric-value"),
            html.Strong(heading),
            html.P(body),
        ],
        className=f"energy-metric-card {accent}".strip(),
    )


def vote_buttons(votes: dict[str, int], final: bool = False) -> html.Div:
    cards = []
    for scenario in ANONYMOUS_ORDER:
        narrative = NARRATIVES[scenario]
        choice = narrative["anonymous_id"]
        label = scenario if final else f"Future {choice}"
        cards.append(
            html.Button(
                [
                    html.Span(label, className="vote-name"),
                    html.Span(str(votes.get(choice, 0)), className="vote-count"),
                ],
                id={"type": "vote-button", "choice": choice},
                n_clicks=0,
                className="vote-button",
                title="Record one show of hands",
            )
        )
    return html.Div(cards, className="vote-grid")


def choice_controls(
    year: int,
    mode: str,
    modes: tuple[str, ...] = ("share", "absolute"),
    sector: str | None = None,
    sectors: tuple[tuple[str, str], ...] = (),
) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Span("Year", className="control-label"),
                    *[
                        html.Button(
                            str(value),
                            id={"type": "explore-year", "value": value},
                            n_clicks=0,
                            className=f"control-chip{' active' if value == year else ''}",
                        )
                        for value in (2020, 2040, 2060)
                    ],
                ],
                className="control-group",
            ),
            (
                html.Div(
                    [
                        html.Span("Sector", className="control-label"),
                        *[
                            html.Button(
                                label,
                                id={"type": "explore-sector", "value": value},
                                n_clicks=0,
                                className=f"control-chip{' active' if value == sector else ''}",
                            )
                            for value, label in sectors
                        ],
                    ],
                    className="control-group sector-control-group",
                )
                if sectors
                else None
            ),
            html.Div(
                [
                    html.Span("View", className="control-label"),
                    *[
                        html.Button(
                            value.title(),
                            id={"type": "explore-mode", "value": value},
                            n_clicks=0,
                            className=f"control-chip{' active' if value == mode else ''}",
                        )
                        for value in modes
                    ],
                ],
                className="control-group",
            ),
        ],
        className="plot-controls",
    )


def capstone_controls(
    case_key: str, scenario_key: str, year: int, indicator_key: str
) -> html.Div:
    case_options = [
        ("electricity", "Electricity"),
        ("steel", "Steel"),
        ("cement", "Cement"),
        ("passenger_cars", "Passenger cars"),
        ("dac", "Carbon removal"),
    ]
    indicator_options = [
        ("climate", "Climate"),
        ("metals", "Metals"),
        ("land", "Land"),
        ("water", "Water"),
    ]
    return html.Div(
        [
            html.Div(
                [
                    html.Span("Case", className="control-label"),
                    *[
                        html.Button(
                            label,
                            id={"type": "capstone-case", "value": value},
                            n_clicks=0,
                            className=f"control-chip{' active' if value == case_key else ''}",
                        )
                        for value, label in case_options
                    ],
                ],
                className="control-group capstone-case-controls",
            ),
            html.Div(
                [
                    html.Span("Scenario", className="control-label"),
                    *[
                        html.Button(
                            value,
                            id={"type": "capstone-scenario", "value": value},
                            n_clicks=0,
                            className=(
                                f"control-chip{' active' if value == scenario_key else ''}"
                            ),
                        )
                        for value in CORE_SCENARIOS
                    ],
                ],
                className="control-group capstone-scenario-controls",
            ),
            html.Div(
                [
                    html.Span("Year", className="control-label"),
                    *[
                        html.Button(
                            str(value),
                            id={"type": "capstone-year", "value": value},
                            n_clicks=0,
                            className=f"control-chip{' active' if value == year else ''}",
                        )
                        for value in (2020, 2040, 2060)
                    ],
                ],
                className="control-group",
            ),
            html.Div(
                [
                    html.Span("Indicator", className="control-label"),
                    *[
                        html.Button(
                            label,
                            id={"type": "capstone-indicator", "value": value},
                            n_clicks=0,
                            className=f"control-chip{' active' if value == indicator_key else ''}",
                        )
                        for value, label in indicator_options
                    ],
                ],
                className="control-group capstone-indicator-controls",
            ),
        ],
        className="plot-controls capstone-controls",
    )


def slide_welcome() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    eyebrow("PSI - Laboratory for Energy Systems Analyses"),
                    html.H1(
                        "IAM scenarios\nfor prospective LCA", className="hero-title"
                    ),
                    html.P(
                        "How scenarios shape a premise database",
                        className="hero-subtitle",
                    ),
                    html.Div(
                        [
                            html.Span("IAM theory", className="pill pill-dark"),
                            html.Span("Scenario narratives", className="pill"),
                            html.Span("Interactive pathways", className="pill"),
                            html.Span("premise + LCIA", className="pill"),
                        ],
                        className="pill-row",
                    ),
                ],
                className="hero-copy",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Narratives"),
                            html.Span("Policy goal"),
                            html.Span("Technology constraints"),
                        ],
                        className="hero-inputs",
                    ),
                    html.Div("↓", className="hero-flow-arrow hero-flow-down"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("IAM", className="hero-iam-badge"),
                                    html.Strong("Connected system"),
                                    html.Small("calculation based on assumptions"),
                                ],
                                className="hero-iam-core",
                            ),
                            html.Div(
                                "Economy + services", className="hero-domain domain-a"
                            ),
                            html.Div(
                                "Energy + industry", className="hero-domain domain-b"
                            ),
                            html.Div("Land + food", className="hero-domain domain-c"),
                            html.Div(
                                "Emissions + climate", className="hero-domain domain-d"
                            ),
                        ],
                        className="hero-iam-system",
                    ),
                    html.Div("↓", className="hero-flow-arrow hero-flow-down"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("Pathways"),
                                    html.Small("technologies · emissions"),
                                ],
                                className="hero-output-card pathway-output",
                            ),
                            html.Div("→", className="hero-flow-arrow"),
                            html.Div(
                                [
                                    html.Strong("Inventories"),
                                    html.Small("premise updates"),
                                ],
                                className="hero-output-card inventory-output",
                            ),
                            html.Div("→", className="hero-flow-arrow"),
                            html.Div(
                                [
                                    html.Strong("LCIA"),
                                    html.Small("impacts · trade-offs"),
                                ],
                                className="hero-output-card lcia-output",
                            ),
                        ],
                        className="hero-outputs",
                    ),
                    html.Div(
                        "A policy target becomes a pathway, an inventory and an LCA result",
                        className="hero-workflow-caption",
                    ),
                ],
                className="hero-system",
            ),
        ],
        className="slide hero-slide",
    )


def slide_energy_climate() -> html.Div:
    chain = [
        ("Needs", "comfort · access · participation"),
        ("Services", "passenger-km · heated m² · materials"),
        ("Stocks", "vehicles · buildings · factories"),
        ("Energy system", "efficiency · fuels · electricity mix"),
        ("Emissions", "CO₂ plus non-CO₂ gases"),
    ]
    chain_children = []
    for index, (label, detail) in enumerate(chain):
        chain_children.append(
            html.Div(
                [html.Strong(label), html.Span(detail)],
                className=(
                    "service-chain-step service-chain-emissions"
                    if label == "Emissions"
                    else "service-chain-step"
                ),
            )
        )
        if index < len(chain) - 1:
            chain_children.append(html.Span("→", className="service-chain-arrow"))
    return html.Div(
        [
            eyebrow("Why integrated assessment · energy services"),
            title(
                "People need services, not fuel",
                "Energy connects human needs and infrastructure to environmental pressure",
            ),
            html.Div(
                [
                    graph(
                        energy_emissions_change_figure(),
                        "graph-frame energy-trend-chart",
                    ),
                    html.Div(
                        [
                            metric_card(
                                "+60%",
                                "Primary energy",
                                "Global consumption, 2000–2024",
                                "metric-energy",
                            ),
                            metric_card(
                                "+51%",
                                "Fossil CO₂",
                                "Emissions excluding land-use change, 2000–2024",
                                "metric-co2",
                            ),
                            metric_card(
                                "−5.5%",
                                "CO₂ per unit energy",
                                "CO₂ grew more slowly than energy use, but still grew",
                                "metric-intensity",
                            ),
                            metric_card(
                                "+1.3% / +0.4%",
                                "Energy / CO₂ in 2025",
                                "Both still increased in the IEA estimate",
                                "metric-current",
                            ),
                        ],
                        className="energy-metric-grid",
                    ),
                ],
                className="energy-trend-layout",
            ),
            html.Div(
                chain_children,
                className="service-chain",
            ),
            source_note(
                "2000–2024: Energy Institute / U.S. EIA primary energy and Global Carbon Budget fossil CO₂, processed by Our World in Data. 2025: IEA Global Energy Review 2026."
            ),
            takeaway(
                "Climate analysis must connect services, technologies, infrastructure, energy flows and emissions. Energy supply alone is not enough."
            ),
        ],
        className="slide intro-energy-slide",
    )


def slide_emissions_system() -> html.Div:
    statistics = [
        (
            "59 ± 6.6",
            "Gt CO₂-eq in 2019",
            "All anthropogenic greenhouse gases",
            "emissions-stat-total",
        ),
        (
            "+54%",
            "Since 1990",
            "Annual global GHG emissions",
            "emissions-stat-growth",
        ),
        (
            "24 → 34%",
            "Industry",
            "Direct → with electricity and heat reassigned",
            "emissions-stat-indirect",
        ),
        (
            "6 → 16%",
            "Buildings",
            "Direct → with electricity and heat reassigned",
            "emissions-stat-indirect",
        ),
    ]
    return html.Div(
        [
            eyebrow("Why integrated assessment · greenhouse gases"),
            title(
                "Emissions come from a connected system",
                "How we group emissions changes what we see, but not the atmospheric total",
            ),
            html.Div(
                [
                    graph(ghg_sector_figure(), "graph-frame emissions-sector-chart"),
                    graph(ghg_gas_figure(), "graph-frame emissions-gas-chart"),
                    graph(ghg_region_figure(), "graph-frame emissions-region-chart"),
                ],
                className="emissions-visual-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(value, className="emissions-stat-value"),
                            html.Strong(heading),
                            html.P(detail),
                        ],
                        className=f"emissions-stat-card {accent}",
                    )
                    for value, heading, detail, accent in statistics
                ],
                className="emissions-stat-grid",
            ),
            source_note(
                "IPCC AR6 WGIII SPM B.1.1, B.2.1 and Figure SPM.2 · 2019 GWP100-AR6 values. Regional shares are production-based and sum to 99% through rounding."
            ),
            takeaway(
                "Links between sectors determine whether a technology moves, reduces or increases emissions across its life cycle."
            ),
        ],
        className="slide intro-emissions-slide",
    )


def slide_warming_budget() -> html.Div:
    statistics = [
        (
            "2,400 Gt",
            "Already emitted",
            "Cumulative CO₂, 1850–2019",
            "budget-stat-history",
        ),
        ("500 Gt", "1.5°C budget", "50% likelihood · from 2020", "budget-stat-limit"),
        ("1,150 Gt", "2°C budget", "67% likelihood · from 2020", "budget-stat-limit"),
        ("+200 Gt", "Cost of delay", "Schematic: 600 → 800 Gt", "budget-stat-delay"),
    ]
    return html.Div(
        [
            eyebrow("Why integrated assessment · cumulative change"),
            title(
                "CO₂ accumulates, so the full pathway matters",
                "Both the final target and the emissions released along the way affect warming",
            ),
            html.Div(
                [
                    graph(carbon_budget_figure(), "graph-frame budget-main-chart"),
                    graph(
                        same_net_zero_date_figure(),
                        "graph-frame budget-timing-chart",
                    ),
                ],
                className="budget-visual-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(value, className="budget-stat-value"),
                            html.Strong(heading),
                            html.P(detail),
                        ],
                        className=f"budget-stat-card {accent}",
                    )
                    for value, heading, detail, accent in statistics
                ],
                className="budget-stat-grid",
            ),
            source_note(
                "IPCC AR6 WGI SPM: historical emissions and remaining budgets from the start of 2020. Right-hand chart: schematic 40 Gt/yr example; areas are calculated, not an assessed pathway."
            ),
            takeaway(
                "The same emissions in the final year can hide very different cumulative emissions, temperature overshoot and removal needs."
            ),
        ],
        className="slide intro-budget-slide",
    )


def slide_why_integrate() -> html.Div:
    claims = [
        ("Mobility", "EVs"),
        ("Buildings", "Heat pumps"),
        ("Industry", "Electric heat"),
        ("H₂ + removals", "Electrolysis · DAC"),
    ]
    statistics = [
        ("5 × 6", "Systems × options", "Mapped in this teaching matrix"),
        ("4", "Simultaneous claims", "On clean power and grids"),
        ("40–70%", "Demand-side potential", "End-use GHG reduction by 2050"),
        ("≥ 50%", "Near-term potential", "2019 GHG level reducible by 2030"),
    ]
    return html.Div(
        [
            eyebrow("Why integrated assessment · decision system"),
            title(
                "Why do we need integrated assessment?",
                "Climate options interact across sectors, time, regions and policy goals",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("How to read the matrix"),
                                    html.Span(
                                        "Choose a system (row). Each cell shows how strongly an option (column) affects that system."
                                    ),
                                ],
                                className="matrix-reading-guide",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                className=f"matrix-swatch level-{level}"
                                            ),
                                            html.Span(label),
                                        ],
                                        className="matrix-legend-item",
                                    )
                                    for level, label in enumerate(
                                        ["Limited", "Small", "Strong", "Central"]
                                    )
                                ],
                                className="matrix-legend",
                            ),
                            graph(
                                integration_matrix_figure(),
                                "graph-frame integration-chart",
                            ),
                        ],
                        className="integration-matrix-panel",
                    ),
                    html.Div(
                        [
                            graph(
                                sector_mitigation_potential_figure(),
                                "graph-frame mitigation-potential-chart",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                className="mitigation-definition-swatch definition-2030"
                                            ),
                                            html.Div(
                                                [
                                                    html.Strong(
                                                        "2030 economic potential"
                                                    ),
                                                    html.Span(
                                                        "All sector options assessed at no more than USD 100 per tonne avoided in 2030. This includes supply, efficiency and process changes."
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mitigation-definition",
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                className="mitigation-definition-swatch definition-2050"
                                            ),
                                            html.Div(
                                                [
                                                    html.Strong(
                                                        "2050 demand-side potential"
                                                    ),
                                                    html.Span(
                                                        "Measures that avoid demand, shift activities or improve efficiency by 2050. These include behaviour, infrastructure and end-use technology, but exclude cleaner energy supply."
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mitigation-definition",
                                    ),
                                ],
                                className="mitigation-definition-grid",
                            ),
                        ],
                        className="mitigation-potential-panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "Worked example", className="resource-kicker"
                                    ),
                                    html.Strong("Electrification couples sectors"),
                                    html.Small(
                                        "Why four plausible sector plans cannot be planned separately"
                                    ),
                                ],
                                className="integration-example-title",
                            ),
                            html.Div(
                                [
                                    html.Span("1", className="integration-step-number"),
                                    html.Div(
                                        [
                                            html.Strong("Sector decisions"),
                                            html.Span(
                                                "Each looks feasible when considered alone"
                                            ),
                                        ]
                                    ),
                                ],
                                className="sector-decisions-step",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [html.Strong(heading), html.Span(detail)],
                                        className="sector-demand-chip",
                                    )
                                    for heading, detail in claims
                                ],
                                className="sector-demand-grid",
                            ),
                            html.Div(
                                [
                                    html.Span("↓", className="integration-flow-arrow"),
                                    html.Strong(
                                        "All four add demand to the same system"
                                    ),
                                ],
                                className="integration-flow-label",
                            ),
                            html.Div(
                                [
                                    html.Span("2", className="integration-step-number"),
                                    html.Div(
                                        [
                                            html.Strong("Power-system response"),
                                            html.Span(
                                                "Generation · grids · storage · timing · prices"
                                            ),
                                        ]
                                    ),
                                ],
                                className="power-system-step",
                            ),
                            html.Div(
                                [
                                    html.Span("↓", className="integration-flow-arrow"),
                                    html.Strong(
                                        "The IAM balances all demands and constraints over time"
                                    ),
                                ],
                                className="integration-flow-label",
                            ),
                            html.Div(
                                [
                                    html.Span("3", className="integration-step-number"),
                                    html.Div(
                                        [
                                            html.Strong(
                                                "Scenario outputs for prospective LCA"
                                            ),
                                            html.Span(
                                                "Technology use · electricity mix · efficiencies · upstream inventories"
                                            ),
                                        ]
                                    ),
                                ],
                                className="lca-output-step",
                            ),
                        ],
                        className="integration-example-panel",
                    ),
                ],
                className="integration-enriched-layout",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(value, className="integration-stat-value"),
                            html.Strong(heading),
                            html.P(detail),
                        ],
                        className="integration-stat-card",
                    )
                    for value, heading, detail in statistics
                ],
                className="integration-stat-grid",
            ),
            source_note(
                "2019 totals include electricity and heat reassigned to end-use sectors (IPCC AR6 WGIII Figure 2.12). Table 12.4: 2030 economic potential; Figure SPM.6 / Chapter 5: 2050 demand-side potential. The strips compare scale; they are not sequential reductions or residual forecasts."
            ),
            takeaway(
                "We need IAMs because separate sector plans can each look feasible but still conflict when combined."
            ),
        ],
        className="slide integration-slide",
    )


def slide_net_zero_pathway() -> html.Div:
    legend = [
        ("2050", "netzero-2050"),
        ("Before 2050", "netzero-before"),
        ("After 2050", "netzero-after"),
        ("Already achieved", "netzero-achieved"),
        ("No document", "netzero-none"),
    ]
    chain = [
        (
            "Political commitment",
            "Target year, gases, territorial boundary, legal status and treatment of offsets.",
        ),
        (
            "Emissions pathway",
            "Carbon budget, near-term pace, residual emissions, overshoot and removals.",
        ),
        (
            "Sector transformation",
            "Demand, technology portfolios, land use, fuels, trade and infrastructure.",
        ),
        (
            "Investment and deployment",
            "Capacity additions, retirements, grids, supply chains, learning and finance.",
        ),
        (
            "Prospective inventory",
            "Regional markets, efficiencies, suppliers and direct-emission factors.",
        ),
    ]
    target_years = [
        ("2030", "Norway"),
        ("2035", "Finland"),
        ("2040", "Austria · Iceland"),
        ("2045", "Sweden · Germany · Denmark"),
        (
            "2050",
            "Switzerland · United Kingdom · Canada · France · Japan · South Korea · Australia · New Zealand · Brazil · Chile · South Africa",
        ),
        ("2053", "Türkiye"),
        ("before 2060", "China"),
        ("2060", "Indonesia · Kazakhstan · Russia · Saudi Arabia"),
        ("2070", "India"),
    ]
    return html.Div(
        [
            eyebrow("Why integrated assessment · from pledge to pathway"),
            title(
                "A target date is not a pathway",
                "A net-zero year states the destination, but not how to get there",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src=asset_url("net-zero-commitments-map.png"),
                                className="netzero-map",
                                alt="World map grouping national net-zero commitments by target-year category",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        [html.I(className=f"legend-dot {css}"), label],
                                        className="netzero-legend-item",
                                    )
                                    for label, css in legend
                                ],
                                className="netzero-legend",
                            ),
                        ],
                        className="netzero-map-panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("National net-zero objectives"),
                                    html.Span("25 examples · checked August 2026"),
                                ],
                                className="netzero-target-heading",
                            ),
                            html.Table(
                                [
                                    html.Thead(
                                        html.Tr(
                                            [
                                                html.Th("Objective year"),
                                                html.Th("Countries"),
                                            ]
                                        )
                                    ),
                                    html.Tbody(
                                        [
                                            html.Tr(
                                                [
                                                    html.Td(year),
                                                    html.Td(countries),
                                                ]
                                            )
                                            for year, countries in target_years
                                        ]
                                    ),
                                ],
                                className="netzero-target-table",
                            ),
                        ],
                        className="netzero-target-panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(str(i), className="pathway-step-number"),
                                    html.Div([html.Strong(heading), html.P(detail)]),
                                ],
                                className="pathway-step",
                            )
                            for i, (heading, detail) in enumerate(chain, 1)
                        ],
                        className="pathway-chain",
                    ),
                ],
                className="netzero-layout",
            ),
            source_note(
                "Map: archival Climate Watch target-year view. Table: national sources and Net Zero Tracker, checked August 2026; definitions differ in legal status, gas coverage, boundaries and removals."
            ),
            takeaway(
                "IAMs turn goals and constraints into consistent pathways based on explicit assumptions about society, technology and policy."
            ),
        ],
        className="slide netzero-slide",
    )


def slide_iam_definition() -> html.Div:
    meanings = [
        (
            "I",
            "Integrated",
            "A change in one human or natural system can affect the others.",
            "iam-meaning-integrated",
        ),
        (
            "A",
            "Assessment",
            "Results are organised around an explicit decision question.",
            "iam-meaning-assessment",
        ),
        (
            "M",
            "Model",
            "Equations, constraints and rules about behaviour generate pathways.",
            "iam-meaning-model",
        ),
    ]
    experiment_steps = [
        ("Question", "What if a target, policy or technology constraint changes?"),
        (
            "Assumptions + model rules",
            "Society, technology and policy are represented through equations, constraints and rules",
        ),
        (
            "Conditional outputs",
            "Regional energy, land, emissions and removals. These are not a complete inventory.",
        ),
    ]
    experiment_modes = [
        ("Target-seeking", "meet a budget"),
        ("Policy", "test an instrument"),
        ("Cost–benefit", "compare trade-offs"),
    ]
    human_system = [
        "Population & services",
        "Economy & investment",
        "Energy, industry & transport",
        "Agriculture & land use",
    ]
    natural_system = [
        "Atmosphere & climate",
        "Carbon & nutrient cycles",
        "Land, water & ecosystems",
        "Damages & physical impacts",
    ]
    return html.Div(
        [
            eyebrow("Why integrated assessment · definition"),
            title(
                "An IAM is a structured thought experiment",
                "It calculates futures under stated assumptions; it does not predict which future will occur",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(letter, className="iam-meaning-letter"),
                            html.Div([html.Strong(heading), html.P(body)]),
                        ],
                        className=f"iam-meaning-card {accent}",
                    )
                    for letter, heading, body, accent in meanings
                ],
                className="iam-meaning-strip",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("A disciplined experiment"),
                                    html.Span(
                                        "Follow the reasoning from assumptions to results"
                                    ),
                                ],
                                className="iam-experiment-heading",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                str(i),
                                                className="iam-experiment-number",
                                            ),
                                            html.Div(
                                                [html.Strong(heading), html.P(detail)]
                                            ),
                                        ],
                                        className=f"iam-experiment-step iam-experiment-step-{i}",
                                    )
                                    for i, (heading, detail) in enumerate(
                                        experiment_steps, 1
                                    )
                                ],
                                className="iam-experiment-chain",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [html.Strong(heading), html.Span(detail)],
                                        className="iam-mode-chip",
                                    )
                                    for heading, detail in experiment_modes
                                ],
                                className="iam-mode-grid",
                            ),
                        ],
                        className="iam-experiment-panel",
                    ),
                    html.Figure(
                        [
                            html.Figcaption(
                                [
                                    html.Strong("Model rules · connected systems"),
                                    html.Span(
                                        "Optimisation or simulation connects services, resources, technologies and emissions"
                                    ),
                                ],
                                className="iam-coupling-caption",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Strong("Society · assumed"),
                                                    html.Span(
                                                        "Population · GDP · urbanisation · service demand"
                                                    ),
                                                ],
                                                className="iam-driver-card",
                                            ),
                                            html.Div(
                                                [
                                                    html.Strong("Technology · assumed"),
                                                    html.Span(
                                                        "Costs · availability · learning · build rates"
                                                    ),
                                                ],
                                                className="iam-driver-card iam-technology-card",
                                            ),
                                            html.Div(
                                                [
                                                    html.Strong("Policy · experiment"),
                                                    html.Span(
                                                        "Budgets · prices · standards · timing"
                                                    ),
                                                ],
                                                className="iam-driver-card iam-policy-card",
                                            ),
                                        ],
                                        className="iam-driver-band",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Strong("Human systems"),
                                                    html.Div(
                                                        [
                                                            html.Span(item)
                                                            for item in human_system
                                                        ],
                                                        className="iam-system-node-grid",
                                                    ),
                                                ],
                                                className="iam-system-zone iam-human-zone",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Strong(
                                                                "GHG emissions"
                                                            ),
                                                            html.Span("→"),
                                                        ],
                                                        className="iam-exchange iam-exchange-emissions",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Span("←"),
                                                            html.Strong(
                                                                "Impacts + resource feedbacks"
                                                            ),
                                                        ],
                                                        className="iam-exchange iam-exchange-feedback",
                                                    ),
                                                ],
                                                className="iam-exchange-column",
                                            ),
                                            html.Div(
                                                [
                                                    html.Strong("Natural systems"),
                                                    html.Div(
                                                        [
                                                            html.Span(item)
                                                            for item in natural_system
                                                        ],
                                                        className="iam-system-node-grid",
                                                    ),
                                                ],
                                                className="iam-system-zone iam-natural-zone",
                                            ),
                                        ],
                                        className="iam-coupled-core",
                                    ),
                                    html.Div(
                                        [
                                            html.Strong("Conditional outputs"),
                                            html.Span(
                                                "regional demand · deployment · energy · land · emissions · climate"
                                            ),
                                            html.B(
                                                "→ inputs for premise, not a complete LCI"
                                            ),
                                        ],
                                        className="iam-pathway-band",
                                    ),
                                ],
                                className="iam-coupling-diagram",
                            ),
                        ],
                        className="iam-coupling-figure",
                    ),
                ],
                className="iam-definition-layout",
            ),
            source_note(
                "The boundary is simplified. Behaviour and distribution are often represented in broad terms. Political implementation, climate damage and Earth-system feedbacks may be linked to the model, set externally or omitted."
            ),
            takeaway(
                "Do not ask only whether the forecast is right. Ask which systems, assumptions and feedbacks produced the pathway."
            ),
        ],
        className="slide iam-definition-slide",
    )


def slide_iam_system_coverage() -> html.Div:
    model_system_coverage = [
        ("IMAGE", "◐", "●", "●", "●", "●"),
        ("MESSAGEix–GLOBIOM", "◐", "●", "●", "◐", "◐"),
        ("REMIND–MAgPIE", "●", "●", "●", "◐", "◐"),
        ("GCAM", "●", "●", "●", "●", "●"),
        ("TIAM-UCL", "◐", "●", "○", "◐", "○"),
    ]
    coverage_classes = {
        "●": "iam-coverage-cell-core",
        "◐": "iam-coverage-cell-linked",
        "○": "iam-coverage-cell-outside",
    }
    return html.Div(
        [
            eyebrow("Why integrated assessment · model boundaries"),
            title(
                "IAMs represent different parts of the system",
                "Some systems respond directly inside the model, some are simplified and linked, and others are excluded",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("●", className="iam-coverage-key-symbol"),
                            html.Div(
                                [
                                    html.Strong("Inside the model"),
                                    html.Span(
                                        "Can respond directly during the calculation, for example energy investment or land allocation"
                                    ),
                                ],
                                className="iam-coverage-key-copy",
                            ),
                        ],
                        className="iam-coverage-key iam-coverage-key-core",
                    ),
                    html.Div(
                        [
                            html.Span("◐", className="iam-coverage-key-symbol"),
                            html.Div(
                                [
                                    html.Strong("Linked / simplified"),
                                    html.Span(
                                        "Represented through a simpler connected module, so its influence should be tested"
                                    ),
                                ],
                                className="iam-coverage-key-copy",
                            ),
                        ],
                        className="iam-coverage-key iam-coverage-key-linked",
                    ),
                    html.Div(
                        [
                            html.Span("○", className="iam-coverage-key-symbol"),
                            html.Div(
                                [
                                    html.Strong("Outside the model"),
                                    html.Span(
                                        "Must be assessed elsewhere, for example politics, behaviour or material supply"
                                    ),
                                ],
                                className="iam-coverage-key-copy",
                            ),
                        ],
                        className="iam-coverage-key iam-coverage-key-outside",
                    ),
                ],
                className="iam-coverage-key-grid",
            ),
            html.Div(
                [
                    html.Div(
                        "Illustrative coverage of IAM families used in scenario research",
                        className="iam-coverage-slide-heading",
                    ),
                    html.Table(
                        [
                            html.Thead(
                                [
                                    html.Tr(
                                        [
                                            html.Th("Model", rowSpan=2),
                                            html.Th("Human systems", colSpan=3),
                                            html.Th("Natural systems", colSpan=2),
                                        ]
                                    ),
                                    html.Tr(
                                        [
                                            html.Th("Economy"),
                                            html.Th("Energy + industry"),
                                            html.Th("Land + food"),
                                            html.Th("Climate + carbon"),
                                            html.Th("Water + ecosystems"),
                                        ]
                                    ),
                                ]
                            ),
                            html.Tbody(
                                [
                                    html.Tr(
                                        [
                                            html.Th(model),
                                            *[
                                                html.Td(
                                                    value,
                                                    className=f"iam-coverage-cell {coverage_classes[value]}",
                                                )
                                                for value in values
                                            ],
                                        ]
                                    )
                                    for model, *values in model_system_coverage
                                ]
                            ),
                        ],
                        className="iam-coverage-table iam-coverage-table-large",
                    ),
                ],
                className="iam-model-coverage iam-model-coverage-large",
            ),
            source_note(
                "Coverage is schematic: official IMAGE, MESSAGEix–GLOBIOM, REMIND–MAgPIE, GCAM and TIAM-UCL documentation; versions and experiment setups vary."
            ),
            takeaway(
                "Choose an IAM that represents the systems central to the LCA question, and document what must be assessed outside the model."
            ),
        ],
        className="slide iam-coverage-slide",
    )


def slide_iam_history_policy() -> html.Div:
    milestones = [
        (
            "1990–92",
            "IPCC emissions scenarios",
            "IS92 supplied alternative GHG trajectories to climate models and impact studies.",
            "This created a shared baseline for comparing climate responses across research groups.",
        ),
        (
            "2000",
            "SRES storylines",
            "Scenario families focused on population, development, technology and globalisation without adding climate mitigation policy.",
            "The scenarios described several possible stories instead of presenting one forecast.",
        ),
        (
            "2007–10",
            "IAMC and RCPs",
            "A coordinated IAM community produced forcing pathways, emissions and land-use inputs for CMIP5.",
            "Common forcing levels allowed IAM and climate-model teams to run experiments separately and compare them later.",
        ),
        (
            "2015",
            "Paris Agreement",
            "Temperature goals, NDC cycles and long-term strategies created demand for quantified transition pathways.",
            "The question shifted from what might happen to what must change, how fast and with which trade-offs.",
        ),
        (
            "2017–22",
            "SSPs, SR1.5 and AR6",
            "Large groups of model runs compared development patterns, mitigation timing, net zero, overshoot and sector transitions.",
            "Timing, demand, removals and feasibility became central to assessing 1.5°C-compatible pathways.",
        ),
        (
            "2026 →",
            "AR7 and CMIP7",
            "Representative emission families update the common experiments used across mitigation, climate and impacts research.",
            "The new design puts emissions trajectories at the centre while keeping the research areas connected.",
        ),
    ]
    interface = [
        (
            "1",
            "Political question",
            "Goal, fairness principle, constraints and near-term priorities",
        ),
        (
            "2",
            "Model experiments",
            "Multiple IAMs and sensitivity tests show pathways and trade-offs",
        ),
        (
            "3",
            "Assessment",
            "IPCC evaluates evidence, robustness, uncertainty and feasibility",
        ),
        (
            "4",
            "Policy use",
            "NDCs, long-term strategies, sector plans, investment tests and public scrutiny",
        ),
    ]
    return html.Div(
        [
            eyebrow("Why integrated assessment · history and policy"),
            title(
                "From emissions scenarios to policy evidence",
                "IAMs became influential by making long-term goals quantitatively testable and comparable",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(year, className="history-year"),
                                    html.Div(
                                        [
                                            html.Strong(heading),
                                            html.P(
                                                [
                                                    detail,
                                                    html.Span(
                                                        interpretation,
                                                        className="history-more",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="history-copy",
                                    ),
                                ],
                                className="history-item",
                            )
                            for year, heading, detail, interpretation in milestones
                        ],
                        className="history-timeline",
                    ),
                    html.Div(
                        [
                            html.H2("How evidence reaches policy"),
                            *[
                                html.Div(
                                    [
                                        html.Span(number, className="policy-number"),
                                        html.Div(
                                            [html.Strong(heading), html.P(detail)]
                                        ),
                                    ],
                                    className="policy-interface-step",
                                )
                                for number, heading, detail in interface
                            ],
                            html.Div(
                                [
                                    html.Strong("Evidence does not make the decision"),
                                    html.P(
                                        "IAMs clarify consequences; they cannot choose social values, political legitimacy or an acceptable distribution of costs."
                                    ),
                                ],
                                className="policy-caution",
                            ),
                        ],
                        className="policy-interface",
                    ),
                ],
                className="history-policy-layout",
            ),
            source_note(
                "Sources: IPCC scenario history; IAMC history; UNFCCC Paris Agreement; IPCC AR6 WGIII Chapter 3; ScenarioMIP-CMIP7 (2026)."
            ),
            takeaway(
                "IAMs support policy by comparing pathways and their near-term implications. Neither an IAM nor the IPCC chooses a national plan."
            ),
        ],
        className="slide iam-history-slide",
    )


def slide_ssp_quantitative() -> html.Div:
    charts = [
        (
            "population",
            "Demography",
            "Education, fertility and mortality assumptions make SSP3 keep growing while SSP1 and SSP5 peak and decline.",
        ),
        (
            "gdp",
            "Economic development",
            "All SSPs become wealthier, but the pace and distribution of growth differ substantially.",
        ),
        (
            "fossil",
            "Energy orientation",
            "The socioeconomic baseline can raise or lower fossil use even before a climate target is imposed.",
        ),
    ]
    challenge_rows = [
        ("SSP1", "low", "low"),
        ("SSP2", "medium", "medium"),
        ("SSP3", "high", "high"),
        ("SSP4", "low", "high"),
        ("SSP5", "high", "low"),
    ]
    return html.Div(
        [
            eyebrow("Scenario language · socioeconomic trajectories"),
            title(
                "SSPs differ before climate policy is added",
                "Population and GDP are shared inputs; each IAM turns the baseline storyline into energy-system results",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("One storyline, several quantified layers"),
                            html.Span(
                                "Population and economic projections enter the IAM, which then calculates energy, land use and emissions."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Indices make comparison easier"),
                            html.Span(
                                "GDP and fossil-energy curves use 2010 = 100; population remains in billions."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("A baseline still changes"),
                            html.Span(
                                "No additional climate policy still allows efficiency, innovation and structural change."
                            ),
                        ]
                    ),
                ],
                className="ssp-quant-method-band",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [html.Strong(label), html.Span(explanation)],
                                className="ssp-quant-card-heading",
                            ),
                            graph(
                                ssp_baseline_comparison_figure(metric),
                                "ssp-quant-graph",
                            ),
                        ],
                        className="ssp-quant-card",
                    )
                    for metric, label, explanation in charts
                ],
                className="ssp-quant-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong(code),
                            html.Span(f"mitigation {mitigation}"),
                            html.Span(f"adaptation {adaptation}"),
                        ],
                        className=f"ssp-challenge-summary ssp-challenge-summary-{code.lower()}",
                    )
                    for code, mitigation, adaptation in challenge_rows
                ],
                className="ssp-challenge-summary-row",
            ),
            source_note(
                "Sources: IIASA SSP Database · O’Neill et al. (2016, 2017) · Riahi et al. (2017). Population and GDP follow the standard SSP projections. Fossil energy is an illustrative index based on baseline patterns from representative models."
            ),
            takeaway(
                "The SSP number changes demand, resources and development conditions before the model is asked to meet any climate target."
            ),
        ],
        className="slide ssp-quantitative-slide",
    )


def slide_ssp_1_to_3() -> html.Div:
    stories = [
        {
            "code": "SSP1",
            "name": "Sustainability",
            "tagline": "Taking the Green Road",
            "thesis": "Development, social inclusion and environmental protection reinforce one another.",
            "sections": [
                (
                    "People & institutions",
                    "High education and health investment accelerate the demographic transition; inequality falls and global cooperation strengthens.",
                ),
                (
                    "Economy & demand",
                    "Economic growth continues, but well-being, compact cities and lower material intensity restrain demand for energy and resources.",
                ),
                (
                    "Technology & environment",
                    "Efficiency and low-carbon technologies spread quickly, and countries cooperate more to protect the shared environment.",
                ),
            ],
            "lca": "Expect slower growth in service demand and faster technology improvement. Still examine biomass, land use and rebound effects instead of assuming that low-carbon options have no impacts.",
            "signals": [
                ("Population 2100", "6.9 bn"),
                ("GDP", "high"),
                ("Fossil baseline", "lower"),
            ],
            "mitigation": "low",
            "adaptation": "low",
        },
        {
            "code": "SSP2",
            "name": "Middle of the Road",
            "tagline": "Current trends continue",
            "thesis": "Historical tendencies persist: progress occurs, but unevenly and without a decisive structural break.",
            "sections": [
                (
                    "People & institutions",
                    "Population growth is moderate. Institutions pursue development goals slowly; inequality and vulnerability improve only gradually.",
                ),
                (
                    "Economy & demand",
                    "Income and urbanisation rise unevenly. Resource and energy intensity decline, but consumption and service demand continue growing.",
                ),
                (
                    "Technology & environment",
                    "Technology spreads at a moderate pace. Environmental damage continues despite gradual improvements.",
                ),
            ],
            "lca": "Useful as an anchor, but neither neutral nor most likely. Pair it with contrasting SSPs and multiple emissions pathways.",
            "signals": [
                ("Population 2100", "9.0 bn"),
                ("GDP", "medium"),
                ("Fossil baseline", "middle"),
            ],
            "mitigation": "medium",
            "adaptation": "medium",
        },
        {
            "code": "SSP3",
            "name": "Regional Rivalry",
            "tagline": "A Rocky Road",
            "thesis": "Security, nationalism and regional conflict displace cooperation and long-term development.",
            "sections": [
                (
                    "People & institutions",
                    "Education and health investment weaken; population remains high in poorer regions and international coordination erodes.",
                ),
                (
                    "Economy & demand",
                    "Growth and trade slow while inequalities persist. Food, materials and energy security favour domestic supply and redundancy.",
                ),
                (
                    "Technology & environment",
                    "Innovation spreads slowly. Material-intensive consumption and local fossil resources remain important.",
                ),
            ],
            "lca": "Expect slower technology improvement, continued fossil supply, more regional trade and strong location effects. Many IAMs may not find a feasible pathway to very low forcing targets.",
            "signals": [
                ("Population 2100", "12.6 bn"),
                ("GDP", "low"),
                ("Fossil baseline", "higher"),
            ],
            "mitigation": "high",
            "adaptation": "high",
        },
    ]
    return html.Div(
        [
            eyebrow("SSP narratives · development and cooperation"),
            title(
                "SSP1–SSP3: from cooperation to fragmentation",
                "The narratives change who develops, how demand grows, how technology spreads and how quickly countries can act together",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong(story["code"]),
                                    html.Div(
                                        [
                                            html.H2(story["name"]),
                                            html.Span(story["tagline"]),
                                        ],
                                        className="ssp-story-name",
                                    ),
                                ],
                                className="ssp-story-header",
                            ),
                            html.P(story["thesis"], className="ssp-story-thesis"),
                            html.Div(
                                [
                                    html.Div(
                                        [html.Strong(heading), html.P(body)],
                                        className="ssp-story-section",
                                    )
                                    for heading, body in story["sections"]
                                ],
                                className="ssp-story-sections",
                            ),
                            html.Div(
                                [
                                    html.Strong("What this means for prospective LCA"),
                                    html.P(story["lca"]),
                                ],
                                className="ssp-story-lca",
                            ),
                            html.Div(
                                [
                                    html.Div([html.Span(label), html.Strong(value)])
                                    for label, value in story["signals"]
                                ],
                                className="ssp-story-signals",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("Mitigation challenge"),
                                            html.Strong(story["mitigation"]),
                                        ],
                                        className=f"ssp-challenge-badge challenge-{story['mitigation']}",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Adaptation challenge"),
                                            html.Strong(story["adaptation"]),
                                        ],
                                        className=f"ssp-challenge-badge challenge-{story['adaptation']}",
                                    ),
                                ],
                                className="ssp-challenge-pair",
                            ),
                        ],
                        className=f"ssp-story-card ssp-story-{story['code'].lower()}",
                    )
                    for story in stories
                ],
                className="ssp-story-grid-three",
            ),
            source_note(
                "Sources: O’Neill et al. (2016, 2017) · Riahi et al. (2017) · IIASA SSP Database."
            ),
            takeaway(
                "SSP2 is not simply halfway between SSP1 and SSP3. Each storyline combines a consistent set of assumptions about institutions, demand, technology and inequality."
            ),
        ],
        className="slide ssp-narrative-slide",
    )


def slide_ssp_4_to_5() -> html.Div:
    stories = [
        {
            "code": "SSP4",
            "name": "Inequality",
            "tagline": "A Road Divided",
            "thesis": "A globally connected, technology-rich elite coexists with fragmented, vulnerable and low-income populations.",
            "sections": [
                (
                    "Institutions & distribution",
                    "Power, human capital and political influence concentrate. Social cohesion weakens and adaptation capacity is distributed extremely unevenly.",
                ),
                (
                    "Technology & production",
                    "Advanced sectors innovate rapidly, while low-tech, labour-intensive production persists elsewhere. Averages conceal both systems.",
                ),
                (
                    "Energy & environment",
                    "The globally connected energy sector diversifies into both low-carbon and carbon-intensive options; environmental policy protects advantaged areas first.",
                ),
                (
                    "Why mitigation can still be difficult",
                    "Technology helps, but land-use governance, poverty and unequal participation make the most stringent targets hard to implement consistently.",
                ),
            ],
            "lca": "Compare regions and social groups. Clean electricity for one group can coexist with traditional fuels, poor infrastructure and impacts shifted elsewhere.",
            "signals": [
                ("Population 2100", "9.3 bn"),
                ("Technology", "fast · unequal"),
                ("Energy", "mixed"),
            ],
            "mitigation": "low",
            "adaptation": "high",
        },
        {
            "code": "SSP5",
            "name": "Fossil-fuelled Development",
            "tagline": "Taking the Highway",
            "thesis": "Rapid growth, strong institutions and technological confidence are powered by abundant fossil energy and energy-intensive lifestyles.",
            "sections": [
                (
                    "Institutions & development",
                    "Global markets integrate; health, education and human capital improve. Population peaks and declines as incomes rise.",
                ),
                (
                    "Technology & production",
                    "Innovation and productivity grow quickly, including the capacity to manage local environmental problems and build infrastructure at scale.",
                ),
                (
                    "Energy & demand",
                    "High mobility, large homes, material consumption and abundant fossil resources drive the highest energy demand and baseline emissions.",
                ),
                (
                    "Climate-policy implication",
                    "A stringent forcing target requires a sharp departure from the baseline, rapid capital replacement and often extensive carbon removal.",
                ),
            ],
            "lca": "Fast technology improvement does not guarantee low impacts. High service demand, continued dependence on fossil fuels, rapid infrastructure replacement and reliance on carbon removal can dominate prospective inventories.",
            "signals": [
                ("Population 2100", "7.4 bn"),
                ("Technology", "fast"),
                ("Energy", "very high fossil"),
            ],
            "mitigation": "high",
            "adaptation": "low",
        },
    ]
    return html.Div(
        [
            eyebrow("SSP narratives · capability, distribution and energy"),
            title(
                "Fast innovation does not guarantee sustainability",
                "SSP4 and SSP5 both innovate quickly, but they distribute opportunity differently and make opposite assumptions about energy use",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong(story["code"]),
                                    html.Div(
                                        [
                                            html.H2(story["name"]),
                                            html.Span(story["tagline"]),
                                        ],
                                        className="ssp-story-name",
                                    ),
                                ],
                                className="ssp-story-header",
                            ),
                            html.P(story["thesis"], className="ssp-story-thesis"),
                            html.Div(
                                [
                                    html.Div(
                                        [html.Strong(heading), html.P(body)],
                                        className="ssp-story-section",
                                    )
                                    for heading, body in story["sections"]
                                ],
                                className="ssp-pair-story-sections",
                            ),
                            html.Div(
                                [
                                    html.Strong("What this means for prospective LCA"),
                                    html.P(story["lca"]),
                                ],
                                className="ssp-story-lca",
                            ),
                            html.Div(
                                [
                                    html.Div([html.Span(label), html.Strong(value)])
                                    for label, value in story["signals"]
                                ],
                                className="ssp-story-signals",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("Mitigation challenge"),
                                            html.Strong(story["mitigation"]),
                                        ],
                                        className=f"ssp-challenge-badge challenge-{story['mitigation']}",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Adaptation challenge"),
                                            html.Strong(story["adaptation"]),
                                        ],
                                        className=f"ssp-challenge-badge challenge-{story['adaptation']}",
                                    ),
                                ],
                                className="ssp-challenge-pair",
                            ),
                        ],
                        className=f"ssp-story-card ssp-story-{story['code'].lower()}",
                    )
                    for story in stories
                ],
                className="ssp-story-grid-two",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Shared capability"),
                            html.Span("rapid innovation in leading sectors"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("SSP4 dividing line"),
                            html.Span("who gains access and protection"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("SSP5 dividing line"),
                            html.Span(
                                "how much energy and fossil carbon growth requires"
                            ),
                        ]
                    ),
                ],
                className="ssp-pair-contrast-band",
            ),
            source_note(
                "Sources: O’Neill et al. (2016, 2017) · Riahi et al. (2017) · IIASA SSP Database."
            ),
            takeaway(
                "Technology alone does not make a future sustainable. Access, demand and the energy system determine how that technology is used."
            ),
        ],
        className="slide ssp-narrative-slide ssp-pair-slide",
    )


def trajectory_card(label: str, note: str, figure) -> html.Div:
    return html.Div(
        [
            html.Div(
                [html.Strong(label), html.Span(note)],
                className="forcing-chart-label",
            ),
            graph(
                figure,
                "forcing-trajectory-graph forcing-trajectory-graph-large",
            ),
        ],
        className="forcing-chart-card",
    )


def slide_forcing_families() -> html.Div:
    rcps = [
        ("RCP8.5", "8.5", "very high", "Rising forcing"),
        ("RCP6.0", "6.0", "high", "Stabilisation"),
        ("RCP4.5", "4.5", "medium", "Stabilisation"),
        ("RCP2.6", "2.6", "low", "Peak then decline"),
        ("SSP1-1.9", "1.9", "CMIP6 extension", "Peak then decline"),
    ]
    return html.Div(
        [
            eyebrow("Scenario language · concentration experiment"),
            title(
                "RCPs define radiative-forcing experiments",
                "The label gives an approximate forcing level in 2100; the full curve shows how forcing develops over time",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        "CMIP5 RCPs · plus the CMIP6 1.9 extension"
                                    ),
                                    html.P(
                                        "The number approximates radiative forcing in 2100. SSP1-1.9 later extended the CMIP5 range downward for Paris-aligned experiments."
                                    ),
                                ],
                                className="forcing-panel-heading",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Strong(code),
                                            html.B(f"{value} W/m²"),
                                            html.Span(label),
                                            html.I(shape),
                                        ],
                                        className=f"rcp-ladder-row rcp-ladder-{value.replace('.', '')}",
                                    )
                                    for code, value, label, shape in rcps
                                ],
                                className="rcp-ladder",
                            ),
                            html.Div(
                                [
                                    html.Strong("Read the label carefully"),
                                    html.Span(
                                        "It is not a policy, probability, socioeconomic narrative or guaranteed temperature."
                                    ),
                                ],
                                className="forcing-definition-note",
                            ),
                        ],
                        className="forcing-framework-panel rcp-framework-panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("Inputs set in advance"),
                                    html.Span(
                                        "Concentrations and forcing are inputs to the climate-model run."
                                    ),
                                ],
                                className="forcing-reading-card",
                            ),
                            html.Div(
                                [
                                    html.Strong("Modelled response"),
                                    html.Span(
                                        "Global mean surface temperature (GMST) is a range of model results, not a number contained in the RCP label."
                                    ),
                                ],
                                className="forcing-reading-card",
                            ),
                            html.Div(
                                [
                                    html.Strong("Timing matters"),
                                    html.Span(
                                        "Equal 2100 forcing would not imply equal peak warming or cumulative impacts."
                                    ),
                                ],
                                className="forcing-reading-card",
                            ),
                        ],
                        className="forcing-reading-grid",
                    ),
                ],
                className="forcing-overview-layout",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        "Read the forcing curve together with its climate response"
                                    ),
                                    html.P(
                                        "Warming responds with a delay, and climate models produce a range of temperatures for the same forcing pathway."
                                    ),
                                ],
                                className="forcing-trajectory-heading",
                            ),
                            html.Div(
                                "Central teaching curves · actual GMST is uncertain.",
                                className="forcing-trajectory-caveat",
                            ),
                        ],
                        className="forcing-trajectory-title-row",
                    ),
                    html.Div(
                        [
                            trajectory_card(
                                "Forcing trajectory set in advance",
                                "RCP number ≈ 2100 forcing level",
                                rcp_forcing_trajectory_figure(compact=True),
                            ),
                            trajectory_card(
                                "Illustrative temperature response",
                                "central GMST estimate relative to 1850–1900",
                                rcp_gmst_trajectory_figure(compact=True),
                            ),
                        ],
                        className="forcing-trajectory-grid forcing-trajectory-pair-grid",
                    ),
                ],
                className="forcing-trajectory-panel forcing-trajectory-pair-panel",
            ),
            source_note(
                "Sources: van Vuuren et al. (2011); Gidden et al. (2019); IPCC AR6. SSP1-1.9 is the CMIP6 low-end extension; curves are teaching approximations."
            ),
            takeaway(
                "An RCP defines a forcing experiment. Temperature is the uncertain climate response to the full forcing trajectory."
            ),
        ],
        className="slide forcing-families-slide forcing-rcp-slide",
    )


def slide_emission_families() -> html.Div:
    cmip7_families = [
        ("H", "High", "high throughout"),
        ("HL", "High→Low", "high first, lower later"),
        ("M", "Medium", "middle trajectory"),
        ("ML", "Medium→Low", "delayed decline"),
        ("L", "Low", "strong reductions"),
        ("LN", "Low→Negative", "net negative later"),
        ("VL", "Very Low", "fastest reductions"),
    ]
    return html.Div(
        [
            eyebrow("Scenario language · emissions experiment"),
            title(
                "CMIP7 families describe how emissions change over time",
                "The names describe both the emissions level and its timing; Earth-system models calculate the resulting forcing and temperature",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        "ScenarioMIP-CMIP7 · seven emissions families"
                                    ),
                                    html.P(
                                        "H, M and L indicate broad emissions levels. A second letter describes how emissions change later. VL marks the fastest reductions, while LN becomes net negative later."
                                    ),
                                ],
                                className="forcing-panel-heading",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Strong(code),
                                            html.B(label),
                                            html.Span(description),
                                        ],
                                        className=f"emission-family-chip emission-family-{code.lower()}",
                                    )
                                    for code, label, description in cmip7_families
                                ],
                                className="emission-family-grid",
                            ),
                        ],
                        className="forcing-framework-panel emissions-framework-panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("H · M · L"),
                                    html.Span("level and broad direction"),
                                ],
                                className="forcing-reading-card",
                            ),
                            html.Div(
                                [
                                    html.Strong("HL · ML"),
                                    html.Span(
                                        "timing changes the peak and cumulative total"
                                    ),
                                ],
                                className="forcing-reading-card",
                            ),
                            html.Div(
                                [
                                    html.Strong("VL · LN"),
                                    html.Span(
                                        "very fast decline versus later net-negative emissions"
                                    ),
                                ],
                                className="forcing-reading-card",
                            ),
                        ],
                        className="emission-family-reading-row",
                    ),
                ],
                className="emission-family-overview",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        "Read the emissions curve together with its climate response"
                                    ),
                                    html.P(
                                        "Emissions can peak before temperature, while sustained net-negative emissions can reverse warming only after a delay."
                                    ),
                                ],
                                className="forcing-trajectory-heading",
                            ),
                            html.Div(
                                "Central illustrative curves based on FaIR · the dotted line marks 1.5 °C.",
                                className="forcing-trajectory-caveat",
                            ),
                        ],
                        className="forcing-trajectory-title-row",
                    ),
                    html.Div(
                        [
                            trajectory_card(
                                "Emissions trajectory set in advance",
                                "illustrative global GHG emissions · Gt CO₂-eq/yr",
                                cmip7_family_figure(compact=True),
                            ),
                            trajectory_card(
                                "Illustrative temperature response",
                                "central GMST estimate relative to 1850–1900",
                                cmip7_gmst_trajectory_figure(compact=True),
                            ),
                        ],
                        className="forcing-trajectory-grid forcing-trajectory-pair-grid",
                    ),
                ],
                className="forcing-trajectory-panel forcing-trajectory-pair-panel",
            ),
            source_note(
                "Source: Van Vuuren et al. (2026), ScenarioMIP-CMIP7, doi:10.5194/gmd-19-2627-2026. Curves are central teaching approximations."
            ),
            takeaway(
                "The family describes the emissions experiment, not the society producing it. GMST is the uncertain climate response."
            ),
        ],
        className="slide forcing-families-slide forcing-emissions-slide",
    )


def slide_scenario_combinations() -> html.Div:
    matrix_columns = ["SSP1", "SSP4", "SSP2", "SSP3", "SSP5"]
    matrix_rows = [
        ("8.5", ["×", "×", "×", "×", "4/4"]),
        ("6.0", ["6/6", "3/3", "6/6", "4/4", "4/4"]),
        ("4.5", ["6/6", "3/3", "6/6", "4/4", "4/4"]),
        ("3.4", ["6/6", "3/3", "6/6", "4/4", "4/4"]),
        ("2.6", ["6/6", "3/3", "6/6", "0/4", "3/4"]),
        ("1.9", ["6/6", "1/3", "4/6", "0/4", "2/4"]),
    ]
    examples = [
        ("CMIP6 convention", "SSP2", "4.5", "SSP2-4.5"),
        ("Workshop IAM file", "SSP2", "M", "SSP2-M"),
        ("Workshop IAM file", "SSP2", "VLHO", "SSP2-VLHO"),
    ]

    def matrix_cell_class(value: str) -> str:
        if value == "×":
            return "scenario-matrix-cell scenario-matrix-na"
        success, attempted = (int(part) for part in value.split("/"))
        if success == 0:
            return "scenario-matrix-cell scenario-matrix-none"
        if success == attempted:
            return "scenario-matrix-cell scenario-matrix-all"
        return "scenario-matrix-cell scenario-matrix-partial"

    return html.Div(
        [
            eyebrow("Scenario language · combine the layers"),
            title(
                "A quantitative scenario combines three layers",
                "The same societal storyline or climate experiment can produce different pathways because each IAM uses its own assumptions and methods",
            ),
            html.Div(
                [
                    html.Div(
                        [html.Strong("Societal storyline"), html.Span("SSP")],
                        className="scenario-equation-part equation-storyline",
                    ),
                    html.I("+"),
                    html.Div(
                        [
                            html.Strong("Climate pathway"),
                            html.Span("forcing or emissions family"),
                        ],
                        className="scenario-equation-part equation-pathway",
                    ),
                    html.I("+"),
                    html.Div(
                        [html.Strong("IAM"), html.Span("assumptions + model rules")],
                        className="scenario-equation-part equation-model",
                    ),
                    html.I("→"),
                    html.Div(
                        [
                            html.Strong("Quantitative pathway"),
                            html.Span("technology, energy, land, emissions"),
                        ],
                        className="scenario-equation-part equation-output",
                    ),
                ],
                className="scenario-equation",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H2("Read the label, then verify the source"),
                            html.P(
                                "The code is only a short label. Check its definition, IAM and model variant before interpreting its ambition or consequences."
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(context),
                                            html.Strong(storyline),
                                            html.I("+"),
                                            html.Strong(pathway),
                                            html.I("→"),
                                            html.B(result),
                                        ],
                                        className="scenario-label-example",
                                    )
                                    for context, storyline, pathway, result in examples
                                ],
                                className="scenario-label-examples",
                            ),
                            html.Div(
                                [
                                    html.Strong("Important"),
                                    html.Span(
                                        "The label alone does not define the scenario. Investments, technology mixes and inventory changes depend on how the IAM implements it."
                                    ),
                                ],
                                className="scenario-label-caution",
                            ),
                        ],
                        className="scenario-label-panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H2(
                                                "Whether a target can be reached depends on the storyline and IAM"
                                            ),
                                            html.P(
                                                "Forcing levels become more stringent downward; SSPs are arranged roughly from lower to higher mitigation challenge."
                                            ),
                                        ],
                                        className="scenario-matrix-heading",
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                "Lower mitigation challenge",
                                                className="matrix-direction-label",
                                            ),
                                            html.Span(
                                                "→", className="matrix-direction-arrow"
                                            ),
                                            html.Span(
                                                "Higher mitigation challenge",
                                                className="matrix-direction-label",
                                            ),
                                        ],
                                        className="matrix-direction",
                                    ),
                                ],
                                className="scenario-matrix-title-row",
                            ),
                            html.Table(
                                [
                                    html.Thead(
                                        html.Tr(
                                            [html.Th("2100 forcing")]
                                            + [
                                                html.Th(column)
                                                for column in matrix_columns
                                            ]
                                        )
                                    ),
                                    html.Tbody(
                                        [
                                            html.Tr(
                                                [
                                                    html.Th(
                                                        [
                                                            html.Strong(forcing),
                                                            html.Span("W/m²"),
                                                        ]
                                                    )
                                                ]
                                                + [
                                                    html.Td(
                                                        value,
                                                        className=matrix_cell_class(
                                                            value
                                                        ),
                                                    )
                                                    for value in values
                                                ]
                                            )
                                            for forcing, values in matrix_rows
                                        ]
                                    ),
                                ],
                                className="scenario-matrix-table",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                className="matrix-legend-swatch matrix-legend-all"
                                            ),
                                            html.Span("all models succeeded"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                className="matrix-legend-swatch matrix-legend-partial"
                                            ),
                                            html.Span("some succeeded"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                className="matrix-legend-swatch matrix-legend-none"
                                            ),
                                            html.Span("none succeeded"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                className="matrix-legend-swatch matrix-legend-na"
                                            ),
                                            html.Span("× no scenario in exercise"),
                                        ]
                                    ),
                                ],
                                className="scenario-matrix-legend",
                            ),
                            html.P(
                                "Each cell shows the number of IAMs that reached the target divided by the number tested for that SSP. A failed model run reflects its structure and assumptions; it does not prove that the pathway is impossible.",
                                className="scenario-matrix-reading",
                            ),
                        ],
                        className="scenario-matrix-panel",
                    ),
                ],
                className="scenario-combination-layout",
            ),
            source_note(
                "Matrix: Carbon Brief, adapted from Rogelj et al. (2018), Figure S1 · SSP database model runs."
            ),
            takeaway(
                "Use the label to locate the scenario, then inspect its assumptions, IAM and trajectories before using it in prospective LCA."
            ),
        ],
        className="slide scenario-combination-slide",
    )


def slide_anonymous(reveal: int) -> html.Div:
    names_visible = reveal > 0
    return html.Div(
        [
            eyebrow("Interactive checkpoint · initial screening"),
            title(
                "Choose a pathway before seeing its assumptions",
                "Which CO₂ pathway would you use for 2060, and what must you check before building the database?",
            ),
            html.Div(
                [
                    graph(
                        scenario_trajectory(
                            "Carbon Dioxide emissions",
                            "Annual CO₂ trajectories",
                            names_visible,
                        )
                    ),
                    html.Div(
                        [
                            html.H3(
                                "Use the curve only as a first filter",
                                className="panel-heading",
                            ),
                            html.P(
                                "Before revealing the labels, separate what the curve supports from what remains unknown."
                            ),
                            html.Div(
                                [
                                    html.Strong("You can read"),
                                    html.Ul(
                                        [
                                            html.Li(
                                                "the timing and rate of global CO₂ decline"
                                            ),
                                            html.Li(
                                                "whether and when net zero or net-negative emissions occur"
                                            ),
                                            html.Li(
                                                "relative cumulative emissions (the area under each curve)"
                                            ),
                                        ]
                                    ),
                                ],
                                className="evidence-gap-section evidence-gap-readable",
                            ),
                            html.Div(
                                [
                                    html.Strong("You still need"),
                                    html.Ul(
                                        [
                                            html.Li(
                                                "storyline, IAM, model version and policy design"
                                            ),
                                            html.Li(
                                                "sector and regional pathways behind the global total"
                                            ),
                                            html.Li(
                                                "technology, removals and premise transformation coverage"
                                            ),
                                        ]
                                    ),
                                ],
                                className="evidence-gap-section evidence-gap-missing",
                            ),
                            html.Div(
                                [
                                    html.Strong("Selection rule"),
                                    html.Span(
                                        "Reject curves that do not fit the question. Compare the remaining databases only after checking the assumptions hidden behind each curve."
                                    ),
                                ],
                                className="evidence-screen-rule",
                            ),
                        ],
                        className="side-panel evidence-screen-panel",
                    ),
                ],
                className="two-column chart-and-panel",
            ),
            takeaway(
                "A CO₂ curve can filter scenarios, but it cannot justify a database without the storyline, IAM and sector assumptions."
            ),
        ],
        className="slide anonymous-scenario-slide",
    )


def slide_vocabulary() -> html.Div:
    checks = [
        (
            "Decision relevance",
            "Which choice, functional unit, geography and time horizon should the scenario test?",
            "decision · functional unit · geography · horizon",
        ),
        (
            "Exact scenario",
            "Which exact model, pathway, region, year and variable support the claim?",
            "IAM + version · scenario · region · year · variable",
        ),
        (
            "Inventory link",
            "Which premise rules carry the pathway into the database, and which sectors are actually transformed?",
            "database version · mapping · transformation · coverage",
        ),
        (
            "Boundary of claim",
            "What stays fixed, simplified, uncertain or outside both the IAM and the LCA model?",
            "fixed foreground · omissions · uncertainty · comparability",
        ),
    ]
    return html.Div(
        [
            eyebrow("Scenario literacy · reporting in practice"),
            title(
                "Turn a scenario result into a well-supported LCA statement",
                "Connect the decision, exact scenario, inventory changes and limits of the claim",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("QUESTION"),
                            html.Span("decision + functional unit"),
                        ]
                    ),
                    html.I("+"),
                    html.Div(
                        [
                            html.Strong("SCENARIO"),
                            html.Span("IAM · pathway · region · year"),
                        ]
                    ),
                    html.I("+"),
                    html.Div(
                        [
                            html.Strong("CHANGES"),
                            html.Span("documented premise transformations"),
                        ]
                    ),
                    html.I("→"),
                    html.Div(
                        [html.Strong("RESULT"), html.Span("conditional LCIA result")]
                    ),
                ],
                className="conditional-statement",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(str(index), className="conditional-check-number"),
                            html.H2(label),
                            html.P(body),
                            html.Div(
                                [html.Strong("Record"), html.Span(record)],
                                className="conditional-record",
                            ),
                        ],
                        className="conditional-check-card",
                    )
                    for index, (label, body, record) in enumerate(checks, 1)
                ],
                className="conditional-evidence-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Report"),
                            html.P(
                                "“For 1 kWh supplied in CH in 2050, the IMAGE SSP2-M database gives … under the documented premise transformations.”"
                            ),
                        ],
                        className="evidence-language-card evidence-language-report",
                    ),
                    html.Div(
                        [
                            html.Strong("Avoid"),
                            html.P(
                                "“Electricity will have impact X in 2050” or “SSP2-M is the most likely future.”"
                            ),
                        ],
                        className="evidence-language-card evidence-language-avoid",
                    ),
                ],
                className="evidence-language-grid",
            ),
            takeaway(
                "A well-supported result names the decision, exact scenario, inventory changes and uncertainty. The scenario label alone is not enough."
            ),
        ],
        className="slide conditional-evidence-slide",
    )


def slide_mechanics() -> html.Div:
    return html.Div(
        [
            eyebrow("IAM theory · stocks, flows and technology"),
            title(
                "Investment changes the system over time",
                "REMIND SSP2-PkBudg650 · a strict global carbon-budget case · electrolysis, 2020–2060",
            ),
            graph(iam_mechanics_figure(), "graph-frame mechanics-chart"),
            html.Div(
                [
                    metric_card(
                        "$116 bn/yr",
                        "Investment peak · 2035",
                        "An annual flow: concentrated spending builds assets that remain in the stock.",
                        "mechanics-investment-card",
                    ),
                    metric_card(
                        "32.1 EJ/yr",
                        "Hydrogen output · 2060",
                        "Output keeps rising after the investment peak as installed capacity accumulates.",
                        "mechanics-output-card",
                    ),
                    metric_card(
                        "61 → 75%",
                        "Conversion efficiency",
                        "The model assumes a 14 percentage-point gain, which lowers the electricity needed per unit of hydrogen.",
                        "mechanics-efficiency-card",
                    ),
                    metric_card(
                        "Partial link",
                        "How premise uses it",
                        "Production and efficiency can update operating inventories. Investment requires separate data for capital goods.",
                        "mechanics-premise-card",
                    ),
                ],
                className="mechanics-stat-grid",
            ),
            source_note(
                "Source: REMIND 3.5 · SSP2-PkBudg650 · World · original REMIND_generic_SSP2-PkBudg650.mif; exact reported time steps, no interpolation. Efficiency is a technology parameter, not an observed fleet average."
            ),
            takeaway(
                "A pathway is a sequence: investment changes the stock, the stock supplies output, and efficiency changes its input requirements."
            ),
        ],
        className="slide mechanics-slide",
    )


def slide_total_energy_accounting_chain() -> html.Div:
    chain = image_total_energy_chain()

    def value(
        year: int, stage: str, group: str, destination: str | None = None
    ) -> float:
        subset = chain.loc[
            chain["year"].eq(year) & chain["stage"].eq(stage) & chain["group"].eq(group)
        ]
        if destination is not None:
            subset = subset[subset["destination"].eq(destination)]
        return float(subset["value"].sum())

    primary_total = {
        year: float(
            chain.loc[
                chain["year"].eq(year) & chain["stage"].eq("Primary energy supply"),
                "value",
            ].sum()
        )
        for year in (2020, 2060)
    }
    final_total = {
        year: float(
            chain.loc[
                chain["year"].eq(year) & chain["stage"].eq("Final energy flow"),
                "value",
            ].sum()
        )
        for year in (2020, 2060)
    }
    scale_total = max(primary_total.values())

    def comparison_panel(year: int, label: str) -> html.Div:
        secondary = {
            group: value(year, "Secondary carrier indicator", group)
            for group in [
                "Electricity output",
                "Liquid-fuel consumption",
                "Hydrogen output",
            ]
        }
        delivered = {
            group: value(year, "Final energy flow", group)
            for group in [
                "Electricity",
                "Liquids",
                "Gases",
                "Solids + biomass",
                "Heat",
                "Hydrogen",
            ]
        }
        return html.Div(
            [
                html.Div(
                    [
                        html.Strong(str(year)),
                        html.Span(label),
                        html.B(f"{primary_total[year]:.2f} EJ/yr primary"),
                    ],
                    className="energy-compare-heading",
                ),
                html.Div(
                    [
                        html.Span("PRIMARY SUPPLY"),
                        html.B("→"),
                        html.Span("CONVERSION / DIRECT DELIVERY"),
                        html.B("→"),
                        html.Span("SECONDARY + DELIVERED CARRIERS"),
                        html.B("→"),
                        html.Span("FINAL USE"),
                    ],
                    className="energy-stage-route energy-stage-route-four-wide",
                ),
                graph(
                    total_energy_system_figure(year, scale_total),
                    "graph-frame energy-compare-chart",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("REPORTED SECONDARY INDICATORS"),
                                html.Strong(
                                    f"Electricity {secondary['Electricity output']:.2f} · "
                                    f"liquids {secondary['Liquid-fuel consumption']:.2f} · "
                                    f"H₂ {secondary['Hydrogen output']:.2f} EJ/yr"
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.Span(
                                    f"FINAL CARRIERS DELIVERED · {final_total[year]:.2f} EJ/YR"
                                ),
                                html.Strong(
                                    f"Elec {delivered['Electricity']:.1f} · "
                                    f"liquids {delivered['Liquids']:.1f} · "
                                    f"gases {delivered['Gases']:.1f} · "
                                    f"solids/bio {delivered['Solids + biomass']:.1f} · "
                                    f"heat {delivered['Heat']:.1f} · "
                                    f"H₂ {delivered['Hydrogen']:.1f}"
                                ),
                            ]
                        ),
                    ],
                    className="total-energy-indicators",
                ),
            ],
            className="energy-comparison-panel total-energy-panel",
        )

    return html.Div(
        [
            eyebrow("IAM output · whole-system energy accounting"),
            title(
                "First, compare the whole energy system",
                "IMAGE 3.4 · SSP2-VLHO · World · 2020 versus 2060 · the same scale is used for all flow widths",
            ),
            html.Div(
                [
                    comparison_panel(2020, "HISTORICAL START"),
                    comparison_panel(2060, "STRONG-MITIGATION FUTURE"),
                ],
                className="energy-comparison-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("System expands"),
                            html.Span("Primary: 555.51 → 670.93 EJ/yr (+21%)"),
                            html.B("Final: 338.53 → 396.34 EJ/yr (+17%)"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Supply transforms"),
                            html.Span("Fossil primary: 465.87 → 207.97 EJ/yr (−55%)"),
                            html.B("Non-biomass renewables: 24.77 → 320.62 EJ/yr"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Electricity becomes central"),
                            html.Span("Delivered electricity: 75.03 → 237.23 EJ/yr"),
                            html.B("Share of final energy: 22% → 60%"),
                        ]
                    ),
                ],
                className="energy-change-strip",
            ),
            source_note(
                "Source: original IMAGE 3.4 SSP2-VLHO workbook · World. Carrier nodes use reported final-energy detail and therefore balance exactly with end-use sectors. They show energy delivered to users, not total secondary-energy production. The footer keeps the separately reported electricity, liquid-fuel and hydrogen indicators. Transport carrier shares are scaled to reported passenger and freight totals; international passenger aviation is excluded. The difference between primary and final energy includes conversion losses, energy used by the energy system, non-energy uses, international transport fuels and primary-energy accounting conventions."
            ),
            takeaway(
                "World final energy grows by only 17%, but delivered electricity more than triples and reaches 60% of final energy. The energy mix changes much more than the total."
            ),
        ],
        className="slide energy-accounting-slide energy-example-slide total-energy-slide",
    )


def slide_energy_accounting_chain() -> html.Div:
    chain = image_electricity_chain()

    def value(year: int, stage: str, group: str) -> float:
        return float(
            chain.loc[
                chain["year"].eq(year)
                & chain["stage"].eq(stage)
                & chain["group"].eq(group),
                "value",
            ].iloc[0]
        )

    primary_total = {
        year: float(
            chain.loc[
                chain["year"].eq(year)
                & chain["stage"].eq("Primary input to electricity"),
                "value",
            ].sum()
        )
        for year in (2020, 2060)
    }
    scale_total = max(primary_total.values())

    def comparison_panel(year: int, label: str) -> html.Div:
        passenger_service = value(year, "Energy service", "Passenger mobility")
        passenger_electricity = value(year, "Final electricity", "Passenger transport")
        return html.Div(
            [
                html.Div(
                    [
                        html.Strong(str(year)),
                        html.Span(label),
                        html.B(f"{primary_total[year]:.2f} EJ/yr primary input"),
                    ],
                    className="energy-compare-heading",
                ),
                html.Div(
                    [
                        html.Span("PRIMARY INPUT"),
                        html.B("→"),
                        html.Span("CONVERSION"),
                        html.B("→"),
                        html.Span("SECONDARY"),
                        html.B("→"),
                        html.Span("FINAL ELECTRICITY"),
                    ],
                    className="energy-stage-route",
                ),
                graph(
                    energy_accounting_example_figure(year, scale_total),
                    "graph-frame energy-compare-chart",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("PASSENGER ELECTRICITY"),
                                html.Strong(f"{passenger_electricity:.2f} EJ/yr"),
                            ]
                        ),
                        html.Div(
                            [
                                html.Span("PASSENGER SERVICE · ALL MODES"),
                                html.Strong(f"{passenger_service:,.0f} billion pkm/yr"),
                            ]
                        ),
                    ],
                    className="energy-service-context",
                ),
            ],
            className="energy-comparison-panel",
        )

    return html.Div(
        [
            eyebrow("IAM output · electricity zoom"),
            title(
                "Then examine the electricity chain",
                "IMAGE 3.4 · SSP2-VLHO · Europe (WEU + CEU) · the same scale is used for all flow widths",
            ),
            html.Div(
                [
                    comparison_panel(2020, "HISTORICAL START"),
                    comparison_panel(2060, "STRONG-MITIGATION FUTURE"),
                ],
                className="energy-comparison-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Supply shifts"),
                            html.Span("Fossil 10.00 → 4.59 EJ/yr"),
                            html.B("Wind + solar 2.33 → 17.66 EJ/yr"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Electricity expands"),
                            html.Span("12.16 → 23.01 EJ/yr output"),
                            html.B(
                                "System output/input ratio, not power-plant efficiency: 62% → 75%"
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Mobility electrifies"),
                            html.Span("Passenger electricity: 0.32 → 2.85 EJ/yr"),
                            html.B("Total passenger service: +61%"),
                        ]
                    ),
                ],
                className="energy-change-strip",
            ),
            source_note(
                "Source: original IMAGE 3.4 SSP2-VLHO workbook · WEU + CEU. All Sankey widths use the same EJ/yr scale. ‘Other uses + balance’ is the final electricity left after the named uses are subtracted. IMAGE reports passenger transport service in billion passenger-km/yr, not useful energy. It covers all passenger modes and is therefore shown outside the energy balance."
            ),
            takeaway(
                "By 2060, the system delivers 89% more electricity and 61% more passenger mobility. The supply mix changes sharply, and transport uses much more electricity."
            ),
        ],
        className="slide energy-accounting-slide energy-example-slide",
    )


def slide_primary_energy_layer() -> html.Div:
    return html.Div(
        [
            eyebrow("IAM output · primary energy"),
            title(
                "Primary energy: resources entering the system",
                "IMAGE 3.4 · World and Europe (WEU + CEU) · six carrier groups · 2020–2100",
            ),
            graph(primary_energy_layer_figure(), "graph-frame energy-layer-chart"),
            html.Div(
                [
                    metric_card(
                        "−54%",
                        "World · SSP1-L fossil input · 2020→2060",
                        "Coal, oil and gas fall from 465.9 to 214.1 EJ/yr.",
                        "energy-layer-good",
                    ),
                    metric_card(
                        "+18%",
                        "World · SSP3-H fossil input · 2020→2060",
                        "Fragmentation sustains 551.0 EJ/yr of fossil primary energy in 2060.",
                        "energy-layer-risk",
                    ),
                    metric_card(
                        "Feedstocks",
                        "How premise uses this information",
                        "Mapped biomass categories can change where regional feedstocks come from and how supply is shared.",
                        "energy-layer-premise",
                    ),
                ],
                className="energy-layer-stat-grid",
            ),
            source_note(
                "Source: original IMAGE 3.4 workbooks · exact decadal time steps. Europe sums WEU + CEU; Turkey, Ukraine and Russia remain separate IMAGE regions. Rows use independent vertical scales."
            ),
            takeaway(
                "Primary energy reveals resource dependence, but it is not a technology mix and it is not energy delivered to users."
            ),
        ],
        className="slide energy-layer-slide",
    )


def slide_secondary_energy_layer() -> html.Div:
    return html.Div(
        [
            eyebrow("IAM output · secondary energy"),
            title(
                "Secondary energy: carriers produced after conversion",
                "World and Europe (WEU + CEU) · electricity shown; IMAGE also reports hydrogen, liquids and heat",
            ),
            graph(secondary_energy_layer_figure(), "graph-frame energy-layer-chart"),
            html.Div(
                [
                    metric_card(
                        "71%",
                        "World · solar + wind · SSP2-VLHO · 2060",
                        "239.2 of 336.7 EJ/yr of reported electricity output.",
                        "energy-layer-good",
                    ),
                    metric_card(
                        "1.8×",
                        "World · VLHO output compared with SSP3-H · 2060",
                        "Deep mitigation combines clean supply with more electrified end uses.",
                        "energy-layer-signal",
                    ),
                    metric_card(
                        "Mix + efficiency",
                        "How premise uses this information",
                        "Generation shares and technology efficiencies update regional electricity markets and their inputs.",
                        "energy-layer-premise",
                    ),
                ],
                className="energy-layer-stat-grid",
            ),
            source_note(
                "Source: original IMAGE 3.4 workbooks · exact decadal time steps. Europe = WEU + CEU; rows use independent vertical scales. Solar and wind combine the relevant IMAGE classes; ‘Other’ contains the remaining generation."
            ),
            takeaway(
                "For prospective LCA, the carrier mix and conversion efficiency usually matter more than the carrier total alone."
            ),
        ],
        className="slide energy-layer-slide",
    )


def slide_final_energy_layer() -> html.Div:
    return html.Div(
        [
            eyebrow("IAM output · final energy"),
            title(
                "Final energy: energy delivered to users",
                "World and Europe (WEU + CEU) · selected services · independent vertical scales by region and service",
            ),
            graph(final_energy_layer_figure(), "graph-frame energy-layer-chart"),
            html.Div(
                [
                    metric_card(
                        "+71%",
                        "World · SSP3-H passenger energy · 2020→2060",
                        "Population, mobility and slow efficiency gains lift demand to 100.2 EJ/yr.",
                        "energy-layer-risk",
                    ),
                    metric_card(
                        "−24%",
                        "World · SSP1-L passenger energy · 2020→2060",
                        "Demand restraint, mode shifts and efficient drivetrains reduce delivered energy.",
                        "energy-layer-good",
                    ),
                    metric_card(
                        "Not the functional unit",
                        "Use in prospective LCA",
                        "IAM demand guides market and efficiency changes; the study still defines its functional unit and scale.",
                        "energy-layer-premise",
                    ),
                ],
                className="energy-layer-stat-grid",
            ),
            source_note(
                "Source: original IMAGE 3.4 workbooks · exact decadal time steps. Europe = WEU + CEU. Space heating sums residential + commercial aggregates; panels are selected services, not a complete balance."
            ),
            takeaway(
                "Final energy connects societal demand to technologies, but identical services can require very different delivered energy."
            ),
        ],
        className="slide energy-layer-slide",
    )


def _end_use_change(domain: str, metric: str, year: int) -> float:
    frame = image_end_use_transformations()
    value = frame.loc[
        frame["domain"].eq(domain)
        & frame["metric"].eq(metric)
        & frame["year"].eq(year),
        "value",
    ]
    return float(value.sum())


def _end_use_share(domain: str, groups: list[str], year: int) -> float:
    frame = image_end_use_transformations()
    mix = frame.loc[
        frame["domain"].eq(domain)
        & frame["metric"].eq("technology mix")
        & frame["year"].eq(year)
    ]
    total = float(mix["value"].sum())
    selected = float(mix.loc[mix["group"].isin(groups), "value"].sum())
    return selected / total if total else 0.0


def slide_passenger_car_transformation() -> html.Div:
    battery_2020 = _end_use_share("Passenger cars", ["Battery electric"], 2020)
    battery_2060 = _end_use_share("Passenger cars", ["Battery electric"], 2060)
    energy_2020 = _end_use_change("Passenger cars", "specific energy", 2020)
    energy_2060 = _end_use_change("Passenger cars", "specific energy", 2060)
    service_2020 = _end_use_change("Passenger cars", "context total", 2020)
    service_2060 = _end_use_change("Passenger cars", "context total", 2060)
    return html.Div(
        [
            eyebrow("Final-energy consumers · road mobility"),
            title(
                "Passenger cars: electrification reduces energy per kilometre",
                "IMAGE 3.4 · SSP2-VLHO · World · absolute activity, relative market shares and delivered energy per passenger-kilometre",
            ),
            graph(
                end_use_transformation_figure("Passenger cars"),
                "graph-frame end-use-transformation-chart",
            ),
            html.Div(
                [
                    metric_card(
                        f"{battery_2020:.1%} → {battery_2060:.1%}",
                        "Battery-electric activity share · 2020→2060",
                        "Combustion falls from almost the entire market to 38%.",
                        "energy-layer-good",
                    ),
                    metric_card(
                        f"{energy_2060 / energy_2020 - 1:+.0%}",
                        "Energy per passenger-km · 2020→2060",
                        f"{energy_2020:.2f} → {energy_2060:.2f} MJ/pkm as drivetrains electrify.",
                        "energy-layer-signal",
                    ),
                    metric_card(
                        f"{service_2060 / service_2020 - 1:+.0%}",
                        "Passenger-kilometres · 2020→2060",
                        "Efficiency improves while global light-duty mobility continues to grow.",
                        "energy-layer-risk",
                    ),
                    metric_card(
                        "Technology mix + efficiency",
                        "What premise needs",
                        "Regional powertrain shares, fuel suppliers, electricity markets and vehicle efficiencies.",
                        "energy-layer-premise",
                    ),
                ],
                className="end-use-stat-grid",
            ),
            source_note(
                "Source: IMAGE 3.4 SSP2-VLHO. Absolute powertrain activity and relative shares: consolidated workshop scenario extract; the source reports an unspecified model activity unit rather than vehicle production. Specific energy: original workbook final energy for light-duty vehicles divided by reported light-duty passenger-km."
            ),
            takeaway(
                "A transport service can grow while its final-energy use falls. Market shares and energy use per kilometre must be updated together."
            ),
        ],
        className="slide end-use-transformation-slide",
    )


def slide_cement_transformation() -> html.Div:
    ccs_2060 = _end_use_share("Cement", ["MEA CCS", "On-site CCS", "Oxyfuel CCS"], 2060)
    energy_2020 = _end_use_change("Cement", "specific energy", 2020)
    energy_2060 = _end_use_change("Cement", "specific energy", 2060)
    output_2020 = _end_use_change("Cement", "context total", 2020)
    output_2060 = _end_use_change("Cement", "context total", 2060)
    return html.Div(
        [
            eyebrow("Final-energy consumers · cement"),
            title(
                "Cement: lower emissions require a different kiln mix",
                "IMAGE 3.4 · SSP2-VLHO · World · absolute kiln output, relative route shares and an estimated sector energy trend",
            ),
            graph(
                end_use_transformation_figure("Cement"),
                "graph-frame end-use-transformation-chart",
            ),
            html.Div(
                [
                    metric_card(
                        f"{ccs_2060:.0%}",
                        "Cement output from CCS kilns · 2060",
                        "Monoethanolamine (MEA), on-site and oxyfuel capture enter with different energy needs and inventory effects.",
                        "energy-layer-good",
                    ),
                    metric_card(
                        f"{energy_2060 / energy_2020 - 1:+.0%}",
                        "Estimated sector energy · 2020→2060",
                        f"{energy_2020:.2f} → {energy_2060:.2f} GJ/t; use this as a trend, not as the energy use of a specific kiln.",
                        "energy-layer-signal",
                    ),
                    metric_card(
                        f"{output_2060 / output_2020 - 1:+.0%}",
                        "Cement output · 2020→2060",
                        "A modest demand decline does not remove the need to transform the production fleet.",
                        "energy-layer-risk",
                    ),
                    metric_card(
                        "Kiln + CCS",
                        "What premise needs",
                        "Route shares, thermal fuels, electricity demand, capture rate and captured-CO₂ handling.",
                        "energy-layer-premise",
                    ),
                ],
                className="end-use-stat-grid",
            ),
            source_note(
                "Source: IMAGE 3.4 SSP2-VLHO. Absolute kiln output and relative shares: consolidated workshop scenario extract. The intensity panel divides original-workbook final energy for all non-metallic minerals by cement output; it therefore includes glass and ceramics and is explicitly a sector proxy."
            ),
            takeaway(
                "For cement, a scenario is not simply about using less energy. It shifts output among kiln and capture technologies with different environmental impacts."
            ),
        ],
        className="slide end-use-transformation-slide",
    )


def slide_steel_transformation() -> html.Div:
    secondary_2020 = _end_use_share("Steel", ["Secondary steel"], 2020)
    secondary_2060 = _end_use_share("Steel", ["Secondary steel"], 2060)
    new_routes_2060 = _end_use_share(
        "Steel", ["Hydrogen + electrowinning", "Primary with CCS"], 2060
    )
    energy_2020 = _end_use_change("Steel", "specific energy", 2020)
    energy_2060 = _end_use_change("Steel", "specific energy", 2060)
    output_2020 = _end_use_change("Steel", "context total", 2020)
    output_2060 = _end_use_change("Steel", "context total", 2060)
    return html.Div(
        [
            eyebrow("Final-energy consumers · steel"),
            title(
                "Steel: recycled and electric routes replace blast furnaces",
                "IMAGE 3.4 · SSP2-VLHO · World · absolute route allocation, relative shares and final energy per tonne of crude steel",
            ),
            graph(
                end_use_transformation_figure("Steel"),
                "graph-frame end-use-transformation-chart",
            ),
            html.Div(
                [
                    metric_card(
                        f"{secondary_2020:.0%} → {secondary_2060:.0%}",
                        "Secondary-steel share · 2020→2060",
                        "Scrap availability and electric-arc-furnace inputs become key assumptions.",
                        "energy-layer-good",
                    ),
                    metric_card(
                        f"{new_routes_2060:.0%}",
                        "Hydrogen, electrowinning + CCS routes · 2060",
                        "New primary routes add electricity, hydrogen and capture infrastructure dependencies.",
                        "energy-layer-signal",
                    ),
                    metric_card(
                        f"{energy_2060 / energy_2020 - 1:+.0%}",
                        "Final energy per tonne · 2020→2060",
                        f"{energy_2020:.1f} → {energy_2060:.1f} GJ/t while output grows {output_2060 / output_2020 - 1:+.0%}.",
                        "energy-layer-risk",
                    ),
                    metric_card(
                        "Production route + inputs",
                        "What premise needs",
                        "Steel-route markets plus route-specific coal, scrap, electricity, hydrogen and capture flows.",
                        "energy-layer-premise",
                    ),
                ],
                className="end-use-stat-grid",
            ),
            source_note(
                "Source: IMAGE 3.4 SSP2-VLHO. Absolute route allocation and relative shares: consolidated workshop scenario extract. Specific energy: original-workbook iron-and-steel final energy divided by crude-steel production. Route allocation and aggregate crude-steel production are complementary reporting layers and do not reconcile as one material balance."
            ),
            takeaway(
                "Lower energy intensity does not imply lower sector demand: prospective inventories must capture both a changing route mix and growing steel output."
            ),
        ],
        className="slide end-use-transformation-slide",
    )


def slide_space_heating_transformation() -> html.Div:
    fossil_2020 = _end_use_share("Space heating", ["Fossil boilers"], 2020)
    fossil_2060 = _end_use_share("Space heating", ["Fossil boilers"], 2060)
    network_electric_2060 = _end_use_share(
        "Space heating", ["Electric heating", "District heat"], 2060
    )
    energy_2020 = _end_use_change("Space heating", "specific energy", 2020)
    energy_2060 = _end_use_change("Space heating", "specific energy", 2060)
    total_2020 = _end_use_change("Space heating", "context total", 2020)
    total_2060 = _end_use_change("Space heating", "context total", 2060)
    return html.Div(
        [
            eyebrow("Final-energy consumers · space heating"),
            title(
                "Space heating: electricity and heat networks replace fossil boilers",
                "IMAGE 3.4 · SSP2-VLHO · World · absolute delivered energy, relative carrier shares and final energy per person",
            ),
            graph(
                end_use_transformation_figure("Space heating"),
                "graph-frame end-use-transformation-chart",
            ),
            html.Div(
                [
                    metric_card(
                        f"{fossil_2020:.0%} → {fossil_2060:.0%}",
                        "Fossil-boiler share · 2020→2060",
                        "Gas, oil and coal lose share across residential and commercial heating.",
                        "energy-layer-good",
                    ),
                    metric_card(
                        f"{network_electric_2060:.0%}",
                        "Electric + district heat share · 2060",
                        "More of the environmental impact comes from electricity grids, heat production and network infrastructure.",
                        "energy-layer-signal",
                    ),
                    metric_card(
                        f"{energy_2060 / energy_2020 - 1:+.0%}",
                        "Space-heating energy per person · 2020→2060",
                        f"{energy_2020:.2f} → {energy_2060:.2f} GJ/person; total final energy falls {total_2060 / total_2020 - 1:+.0%}.",
                        "energy-layer-risk",
                    ),
                    metric_card(
                        "Carrier-based estimate",
                        "What premise can derive",
                        "Map delivered carriers to heating technologies, then apply technology-specific efficiencies and markets.",
                        "energy-layer-premise",
                    ),
                ],
                className="end-use-stat-grid",
            ),
            source_note(
                "Source: original IMAGE 3.4 SSP2-VLHO workbook. Absolute volumes and shares sum residential and commercial space-heating carriers. Electricity is a technology proxy including heat pumps and resistance heating; IMAGE does not report useful heat or floor area in this export, so specific use is shown per person."
            ),
            takeaway(
                "Final-energy carriers show the direction of change, but premise still needs an explicit mapping from each carrier to heating technologies and efficiencies."
            ),
        ],
        className="slide end-use-transformation-slide",
    )


def slide_model_landscape() -> html.Div:
    return html.Div(
        [
            eyebrow("IAM output · mapped detail"),
            title(
                "Premise gets different levels of detail from each IAM",
                "Each cell counts the distinct IAM variables that premise 2.4.6 can use for that model and sector",
            ),
            graph(
                model_coverage_figure(),
                "graph-frame model-mapping-heatmap-large",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("What the count means"),
                            html.Span(
                                "A larger number means premise can access more distinct activity, efficiency or energy-use signals."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Read zero carefully"),
                            html.Span(
                                "Zero means that these mapping files contain no matching variable. It does not mean that the IAM lacks the sector."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Do not rank the IAMs"),
                            html.Span(
                                "Mapping density measures usable transformation detail, not scenario quality or accuracy."
                            ),
                        ]
                    ),
                ],
                className="model-heatmap-reading",
            ),
            source_note(
                "Source: premise 2.4.6 IAM-variable mapping YAML files. Counts include distinct model-specific variable names for activity, efficiency and energy use. Carbon-removal and biomass mappings remain in the checked data extract but are omitted here to keep the figure readable."
            ),
            takeaway(
                "Before choosing an IAM, verify that premise can observe the sector signals needed to transform your inventory."
            ),
        ],
        className="slide model-mapping-heatmap-slide",
    )


def slide_model_architecture() -> html.Div:
    architecture_rows = [
        (
            "How the model solves",
            "Step-by-step simulation",
            "Linear optimisation across all periods",
            "Nonlinear general-equilibrium optimisation across all periods",
            "REMIND optimisation with more EU detail",
            "Linear energy-system optimisation across all periods",
            "Step-by-step market equilibrium",
        ),
        (
            "How far ahead it looks",
            "Limited look-ahead / rules",
            "All-period benchmark",
            "All-period benchmark",
            "All-period benchmark",
            "Usually all periods",
            "Limited look-ahead",
        ),
        (
            "Regional and time detail",
            "26 regions + World · recursive time grid",
            "11 regions · multi-period horizon",
            "12-region default · 5→10-year steps",
            "Enhanced EU detail · REMIND time grid",
            "16 regions · seasonal/day time slices",
            "32 regions · 5-year steps",
        ),
        (
            "Connected systems",
            "Energy–land–climate modules",
            "MESSAGEix–GLOBIOM–MACRO / GAINS",
            "Macro–energy core + MAgPIE / MAGICC",
            "REMIND–MAgPIE + European modules",
            "Technology-rich energy + climate / macro",
            "Energy–land–water–climate markets",
        ),
    ]
    architecture_models = [
        "IMAGE",
        "MESSAGE",
        "REMIND",
        "REMIND-EU",
        "TIAM-UCL",
        "GCAM",
    ]
    return html.Div(
        [
            eyebrow("Why integrated assessment · model architecture"),
            title(
                "IAMs can answer the same question differently",
                "How a model solves, looks ahead, divides time and regions, and connects systems shapes the pathway it produces",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("How the IAMs differ structurally"),
                                    html.Span(
                                        "Use the columns to compare model structures, not to rank the IAMs"
                                    ),
                                ],
                                className="model-architecture-heading",
                            ),
                            html.Table(
                                [
                                    html.Thead(
                                        html.Tr(
                                            [html.Th("Property")]
                                            + [
                                                html.Th(model)
                                                for model in architecture_models
                                            ]
                                        )
                                    ),
                                    html.Tbody(
                                        [
                                            html.Tr(
                                                [html.Th(row[0])]
                                                + [html.Td(value) for value in row[1:]]
                                            )
                                            for row in architecture_rows
                                        ]
                                    ),
                                ],
                                className="model-architecture-table",
                            ),
                        ],
                        className="model-architecture-panel model-architecture-panel-large",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("Transition timing"),
                                    html.Span(
                                        "How far ahead the model looks and how it solves affect when assets are built, retired or kept in use."
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Strong("Visible bottlenecks"),
                                    html.Span(
                                        "Detail in time, geography and technology determines which constraints the model can show."
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Strong("Feedbacks represented"),
                                    html.Span(
                                        "The connected modules determine whether energy, the economy, land, water and climate respond together."
                                    ),
                                ]
                            ),
                        ],
                        className="model-architecture-implications",
                    ),
                ],
                className="model-architecture-layout",
            ),
            source_note(
                "Architecture: official IMAGE, MESSAGEix–GLOBIOM, REMIND 2.1, TIAM-UCL 4.1.1 and GCAM 8.2 documentation. REMIND-EU inherits the REMIND solution logic with enhanced European detail. Exact regional aggregations and experiment setups vary by version."
            ),
            takeaway(
                "Two IAMs with a similar climate objective can still produce different timings, technologies and regional patterns."
            ),
        ],
        className="slide model-architecture-slide",
    )


def slide_limitations() -> html.Div:
    limitations = [
        (
            "Optimistic technology assumptions",
            "Deployment follows assumed costs, learning and build-rate constraints. Permitting, supply chains and public acceptance can make real scale-up slower.",
            ["MESSAGE", "REMIND", "REMIND-EU", "TIAM-UCL"],
        ),
        (
            "Perfect foresight",
            "An optimiser can anticipate future targets and avoid stranded assets. Real actors face uncertainty, delays and fragmented decisions.",
            ["MESSAGE", "REMIND", "REMIND-EU", "TIAM-UCL"],
        ),
        (
            "Regional aggregation",
            "National grids, trade corridors and inequalities disappear inside large regions. Resource and infrastructure sharing can therefore look easier.",
            ["MESSAGE", "REMIND", "TIAM-UCL"],
        ),
        (
            "Demand and behaviour",
            "Service demand often follows broad assumptions about population, income and lifestyles. Differences among households, demand reduction, rebound effects and social practices are simplified.",
            ["IMAGE", "MESSAGE", "REMIND / EU", "TIAM-UCL", "GCAM"],
        ),
        (
            "Uneven sector detail",
            "Electricity, steel and road transport often have explicit technology routes. Chemicals, construction and other industries may remain aggregated.",
            ["IMAGE", "MESSAGE", "REMIND / EU", "TIAM-UCL", "GCAM"],
        ),
        (
            "Physical and environmental constraints",
            "Land and water may be detailed, while minerals, biodiversity and local ecosystem limits are only partly represented. These limits may need separate checks.",
            ["TIAM-UCL", "REMIND / EU", "MESSAGE"],
        ),
        (
            "Non-energy and emerging sectors",
            "Agriculture is commonly represented through land, food and emissions rather than detailed equipment. IT, data-centre and AI demand are often set outside the model or omitted.",
            ["IMAGE", "MESSAGE", "REMIND / EU", "TIAM-UCL", "GCAM"],
        ),
        (
            "Equity and justice",
            "Cost-efficient burden sharing can conceal affordability, ownership and within-region distribution. Procedural justice is not solved by an IAM.",
            ["IMAGE", "MESSAGE", "REMIND / EU", "TIAM-UCL", "GCAM"],
        ),
        (
            "Climate feedbacks",
            "Simplified climate modules translate emissions into warming, but climate damage and adaptation rarely change the mitigation pathway in return.",
            ["IMAGE", "MESSAGE", "REMIND / EU", "TIAM-UCL", "GCAM"],
        ),
        (
            "No probabilities",
            "Groups of scenarios are conditional experiments, not probabilities. Agreement across models does not make an outcome more likely.",
            ["IMAGE", "MESSAGE", "REMIND / EU", "TIAM-UCL", "GCAM"],
        ),
    ]
    return html.Div(
        [
            eyebrow("IAM theory · critical reading"),
            title(
                "What IAMs leave out",
                "All models simplify reality; the tags show which issues need particular attention in typical global versions",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(heading),
                            html.P(body),
                            html.Div(
                                [
                                    html.Span(
                                        "Needs particular attention in",
                                        className="limitation-model-label",
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                model,
                                                className="limitation-model-chip",
                                            )
                                            for model in models
                                        ],
                                        className="limitation-model-chips",
                                    ),
                                ],
                                className="limitation-models",
                            ),
                        ],
                        className="concept-card limitation-card",
                    )
                    for heading, body, models in limitations
                ],
                className="limitations-grid",
            ),
            source_note(
                "Model tags reflect typical global versions described in the official IMAGE, MESSAGEix–GLOBIOM, REMIND 2.1, TIAM-UCL 4.1.1 and GCAM 8.2 documentation. The tags are questions to investigate, not complete lists of limitations or model rankings. Other versions and model links can change them."
            ),
            takeaway(
                "Ask which missing factor could change your LCA conclusion. Then test it through sensitivity analysis, an external constraint or another model."
            ),
        ],
        className="slide limitations-slide",
    )


def slide_frameworks() -> html.Div:
    comparisons = [
        (
            "RCP2.6",
            "CMIP5 forcing experiment",
            "Prescribes a concentration and forcing trajectory; socioeconomic conditions are not encoded in the label.",
            "Compare forcing, concentrations and climate response.",
            "concentration and forcing time series",
            "society, sector transition and IAM pathway",
        ),
        (
            "SSP1-2.6",
            "CMIP6 socioeconomic implementation",
            "Combines an SSP1 implementation with a 2.6 W/m² forcing class and a specific IAM marker pathway.",
            "Compare energy, land, emissions and the climate input.",
            "selected SSP1 marker and forcing class",
            "alternative IAM implementations and impact response",
        ),
        (
            "CMIP7 L / VL",
            "Emissions-family experiment",
            "Groups trajectories by direction and timing; several source pathways can belong to the same family.",
            "Compare actual emissions, overshoot and resulting climate ranges.",
            "broad emissions direction and timing",
            "exact marker, society and climate-response spread",
        ),
    ]
    workflow = [
        (
            "1",
            "Align the metric",
            "forcing, cumulative CO₂, peak warming or net-zero year",
        ),
        (
            "2",
            "Align the timing",
            "near-term action, peak, overshoot and net-negative period",
        ),
        ("3", "Align the scope", "gases, sectors, regions, units and system boundary"),
        (
            "4",
            "Track provenance",
            "framework generation, IAM, marker, version and data source",
        ),
    ]
    return html.Div(
        [
            eyebrow("Scenario frameworks · cross-generation comparison"),
            title(
                "Compare trajectories, not labels, across frameworks",
                "RCP2.6, SSP1-2.6 and a CMIP7 low family are related experiments, not interchangeable datasets",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(label, className="framework-comparison-label"),
                            html.H2(kind),
                            html.P(description),
                            html.Div(
                                [
                                    html.Div([html.Strong("Fixed"), html.Span(fixed)]),
                                    html.Div(
                                        [
                                            html.Strong("Still open"),
                                            html.Span(open_dimension),
                                        ]
                                    ),
                                ],
                                className="framework-comparison-details",
                            ),
                            html.Div(use, className="framework-comparison-use"),
                        ],
                        className="framework-comparison-card",
                    )
                    for label, kind, description, use, fixed, open_dimension in comparisons
                ],
                className="framework-comparison-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong(number),
                            html.Div([html.B(label), html.Span(detail)]),
                        ],
                        className="crosswalk-step",
                    )
                    for number, label, detail in workflow
                ],
                className="crosswalk-workflow",
            ),
            html.Div(
                [
                    html.Strong("No one-to-one conversion"),
                    html.Span(
                        "A shared forcing level or family name does not guarantee the same cumulative emissions, sector pathway, temperature peak or prospective inventory."
                    ),
                ],
                className="crosswalk-caution",
            ),
            source_note(
                "Van Vuuren et al. (2026), ScenarioMIP-CMIP7 · doi:10.5194/gmd-19-2627-2026"
            ),
            takeaway(
                "Use labels for orientation; use the underlying trajectories and provenance for quantitative comparison."
            ),
        ],
        className="slide framework-crosswalk-slide",
    )


def slide_narratives() -> html.Div:
    pathway_frame = pathways()
    electricity = pathway_frame[
        pathway_frame["model"].eq("image")
        & pathway_frame["scenario"].eq("SSP2-VLHO")
        & pathway_frame["sector"].eq("Electricity")
        & pathway_frame["region"].isin(["WEU", "CEU"])
        & pathway_frame["year"].isin([2020, 2060])
    ].copy()
    electricity["wind_or_solar"] = electricity["variable"].str.contains(
        "Wind|Solar", regex=True
    )

    def wind_solar_share(year: int) -> float:
        year_data = electricity[electricity["year"].eq(year)]
        return float(
            year_data.loc[year_data["wind_or_solar"], "display_value"].sum()
            / year_data["display_value"].sum()
        )

    share_2020 = wind_solar_share(2020)
    share_2060 = wind_solar_share(2060)
    mapping_frame = premise_mapping_counts()
    image_electricity_aliases = int(
        mapping_frame.loc[
            mapping_frame["model"].eq("image")
            & mapping_frame["sector"].eq("Electricity"),
            "mapped_variable_count",
        ].iloc[0]
    )
    scores = lcia_results()

    def electricity_gwp(scenario: str) -> float:
        return float(
            scores.loc[
                scores["case"].eq("electricity")
                & scores["scenario"].eq(scenario)
                & scores["year"].eq(2060)
                & scores["method_family"].eq("IPCC 2021"),
                "score",
            ].iloc[0]
        )

    vlho_gwp = electricity_gwp("SSP2-VLHO")
    medium_gwp = electricity_gwp("SSP2-M")
    return html.Div(
        [
            eyebrow("Scenario frameworks · traceability"),
            title(
                "Can you explain why the LCA result changed?",
                "Follow one IMAGE result through premise, the inventory and LCIA; every step needs evidence",
            ),
            html.Div(
                [
                    html.Strong("Example setup"),
                    html.Span("IMAGE 3.4"),
                    html.Span("SSP2-VLHO"),
                    html.Span("Teaching extract: WEU + CEU"),
                    html.Span("premise mapping: CH → WEU"),
                    html.Span("Inventory: CH"),
                    html.Span("2060"),
                    html.Span("ecoinvent 3.12 cutoff · premise 2.4.6"),
                ],
                className="traceability-coordinate",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("1 · IAM evidence"),
                            html.H2("The reported generation mix changes"),
                            html.P(
                                "Wind and solar share in the workshop WEU + CEU extract. The next slide separates this teaching aggregation from the WEU region used to transform CH."
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("2020"),
                                            html.Div(
                                                html.I(
                                                    style={"width": f"{share_2020:.1%}"}
                                                )
                                            ),
                                            html.B(f"{share_2020:.0%}"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Span("2060"),
                                            html.Div(
                                                html.I(
                                                    style={"width": f"{share_2060:.1%}"}
                                                )
                                            ),
                                            html.B(f"{share_2060:.0%}"),
                                        ]
                                    ),
                                ],
                                className="traceability-share-bars",
                            ),
                            html.Small(
                                "Source variables: Secondary Energy|Electricity|Wind|… and |Solar|…"
                            ),
                        ],
                        className="traceability-evidence-card traceability-iam-card",
                    ),
                    html.Div("→", className="traceability-arrow"),
                    html.Div(
                        [
                            html.Strong("2 · premise mapping"),
                            html.Div(
                                str(image_electricity_aliases),
                                className="traceability-big-number",
                            ),
                            html.H2("Mapped IMAGE electricity variables"),
                            html.P(
                                "premise uses all mapped technologies, calculates regional shares and efficiencies, and estimates values between model years when needed."
                            ),
                            html.Small(
                                "Evidence: premise 2.4.6 electricity.yaml mapping"
                            ),
                        ],
                        className="traceability-evidence-card traceability-premise-card",
                    ),
                    html.Div("→", className="traceability-arrow"),
                    html.Div(
                        [
                            html.Strong("3 · Inventory change"),
                            html.H2("The electricity market is rebuilt"),
                            html.P(
                                "Regional generation markets and technology datasets receive scenario-specific shares and performance values. The scenario label itself never changes an exchange."
                            ),
                            html.Div(
                                [
                                    html.Span("technology shares"),
                                    html.Span("efficiencies"),
                                    html.Span("regional suppliers"),
                                ],
                                className="traceability-rule-chips",
                            ),
                            html.Small(
                                "Validated workshop transformation: electricity"
                            ),
                        ],
                        className="traceability-evidence-card traceability-inventory-card",
                    ),
                    html.Div("→", className="traceability-arrow"),
                    html.Div(
                        [
                            html.Strong("4 · LCIA observation"),
                            html.H2("The kWh result differs"),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("SSP2-VLHO"),
                                            html.B(f"{vlho_gwp:+.3f}"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Span("SSP2-M"),
                                            html.B(f"{medium_gwp:+.3f}"),
                                        ]
                                    ),
                                ],
                                className="traceability-lcia-values",
                            ),
                            html.P(
                                "kg CO₂-eq per kWh, CH low-voltage electricity, 2060. The score includes the full transformed supply chain, not only wind and solar."
                            ),
                            html.Small("Method: IPCC 2021 GWP100"),
                        ],
                        className="traceability-evidence-card traceability-lcia-card",
                    ),
                ],
                className="traceability-evidence-chain",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Well-supported statement"),
                            html.P(
                                f"In the premise-transformed IMAGE SSP2-VLHO 2060 database, this Swiss low-voltage electricity activity scores {vlho_gwp:.3f} kg CO₂-eq/kWh."
                            ),
                        ],
                        className="traceability-inference traceability-inference-valid",
                    ),
                    html.Div(
                        [
                            html.Strong("Overclaim to avoid"),
                            html.P(
                                "“SSP2-VLHO electricity is carbon-negative because wind and solar reach 74%.” The sign also depends on biomass, CCS, allocation and upstream inventories."
                            ),
                        ],
                        className="traceability-inference traceability-inference-invalid",
                    ),
                ],
                className="traceability-inference-grid",
            ),
            source_note(
                "Sources: IMAGE 3.4 SSP2-VLHO pathway extract (WEU + CEU teaching aggregation); premise 2.4.6 CH → WEU mapping; workshop ecoinvent 3.12 cutoff scenario databases and LCIA results."
            ),
            takeaway(
                "Traceability prevents a scenario label or one attractive trend from being mistaken for the cause of an LCA result."
            ),
        ],
        className="slide traceability-slide",
    )


def slide_applied_geography() -> html.Div:
    steps = [
        (
            "1",
            "LCA question",
            "1 kWh · CH · 2060",
            "The activity location and functional unit to calculate.",
        ),
        (
            "2",
            "Region lookup",
            "IMAGE: CH → WEU · REMIND-EU: CH → NEN",
            "premise selects the model-specific IAM region containing Switzerland.",
        ),
        (
            "3",
            "Inventory transformation",
            "The selected regional trend updates CH",
            "WEU or NEN technology shares and efficiencies guide the scenario-dependent suppliers used by the CH electricity market.",
        ),
        (
            "4",
            "Reported result",
            "kg CO₂-eq / kWh CH",
            "The result remains Swiss; the IAM model and selected scenario region are disclosed with it.",
        ),
    ]
    return html.Div(
        [
            eyebrow("Scenario frameworks · applied geography"),
            title(
                "A Swiss inventory can map to different IAM regions",
                "Before applying scenario trends, premise maps CH to IMAGE region WEU or REMIND-EU region NEN",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Strong("IMAGE"),
                                                    html.Span("5 European regions"),
                                                ]
                                            ),
                                            html.B("CH → WEU"),
                                        ],
                                        className="geography-map-heading",
                                    ),
                                    html.P(
                                        "WEU is the blue Western European region, not the whole continent."
                                    ),
                                    graph(
                                        image_geography_figure(),
                                        "graph-frame geography-map-graph",
                                    ),
                                ],
                                className="geography-map-card",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Strong("REMIND-EU"),
                                                    html.Span("11 European regions"),
                                                ]
                                            ),
                                            html.B("CH → NEN"),
                                        ],
                                        className="geography-map-heading",
                                    ),
                                    html.P(
                                        "Europe is split more finely; Switzerland belongs to Northern non-EU (NEN)."
                                    ),
                                    graph(
                                        remind_eu_geography_figure(),
                                        "graph-frame geography-map-graph",
                                    ),
                                ],
                                className="geography-map-card",
                            ),
                        ],
                        className="geography-map-pair",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        number, className="geography-step-number"
                                    ),
                                    html.Div(
                                        [
                                            html.Strong(label),
                                            html.H2(value),
                                            html.P(detail),
                                        ],
                                        className="geography-step-copy",
                                    ),
                                ],
                                className="geography-step geography-chain-step",
                            )
                            for number, label, value, detail in steps
                        ],
                        className="geography-step-list geography-chain",
                    ),
                ],
                className="geography-applied-grid",
            ),
            source_note(
                "Geographies: premise 2.4.6 image-topology.json and remind-eu-topology.json · inventory activity: CH low-voltage electricity · REMIND-EU European-region count excludes the broader REF region."
            ),
            takeaway(
                "Report the inventory location, IAM and IAM region: CH with WEU for IMAGE, or CH with NEN for REMIND-EU."
            ),
        ],
        className="slide applied-geography-slide",
    )


def slide_iam_region_explorer(selected_model: str = "image") -> html.Div:
    model_labels = {
        "image": "IMAGE",
        "message": "MESSAGE",
        "remind": "REMIND",
        "remind-eu": "REMIND-EU",
        "tiam-ucl": "TIAM-UCL",
        "gcam": "GCAM",
    }
    topologies = iam_region_topologies()
    if selected_model not in model_labels:
        selected_model = "image"
    topology = topologies[selected_model]
    regions = topology["regions"]
    swiss_region = next(
        (region for region, countries in regions.items() if "CHE" in countries),
        "not mapped",
    )
    largest_region, largest_countries = max(
        regions.items(), key=lambda item: len(item[1])
    )
    region_examples = list(regions)[: min(6, len(regions))]
    return html.Div(
        [
            eyebrow("Scenario frameworks · geographic detail"),
            title(
                "Six IAMs group countries into different regions",
                "Select an IAM to update the map; every colour represents a region defined by that model",
            ),
            html.Div(
                [
                    html.Span("IAM model", className="iam-map-control-label"),
                    *[
                        html.Button(
                            label,
                            id={"type": "iam-map-model", "value": slug},
                            n_clicks=0,
                            className=(
                                "iam-map-button active"
                                if slug == selected_model
                                else "iam-map-button"
                            ),
                        )
                        for slug, label in model_labels.items()
                    ],
                ],
                className="iam-map-controls",
            ),
            html.Div(
                [
                    graph(
                        iam_world_geography_figure(selected_model),
                        "graph-frame iam-world-map-graph",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Selected model"),
                                    html.H2(topology["model"]),
                                    html.P(
                                        "Hover over a country to see the region assigned by the selected IAM."
                                    ),
                                ],
                                className="iam-map-selected",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Strong(str(topology["region_count"])),
                                            html.Span("global IAM regions"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Strong(swiss_region),
                                            html.Span("region containing CH"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Strong(largest_region),
                                            html.Span(
                                                f"largest region group · {len(largest_countries)} territories"
                                            ),
                                        ]
                                    ),
                                ],
                                className="iam-map-metrics",
                            ),
                            html.Div(
                                [
                                    html.Strong("Region-name examples"),
                                    html.Div(
                                        [
                                            html.Span(region)
                                            for region in region_examples
                                        ],
                                        className="iam-map-region-chips",
                                    ),
                                    html.P(
                                        "The number of regions shows geographic detail, not scenario quality. Sector detail can still differ within the same IAM."
                                    ),
                                ],
                                className="iam-map-reading",
                            ),
                        ],
                        className="iam-map-side",
                    ),
                ],
                className="iam-map-layout",
            ),
            source_note(
                "Geographies: premise 2.4.6 model topology files for IMAGE, MESSAGE, REMIND, REMIND-EU, TIAM-UCL and GCAM. Country codes are normalized to ISO-3 for display."
            ),
            takeaway(
                "IAM geography determines which regional differences premise can apply to an inventory."
            ),
        ],
        className="slide iam-map-slide",
    )


def slide_controlled_comparisons() -> html.Div:
    comparisons = [
        (
            "Climate-objective experiment",
            "Hold MESSAGE + SSP2",
            "Vary VL → L → ML → M",
            "Socioeconomic assumptions and model structure remain fixed; only the emissions-family ambition changes. Peak warming spans 1.82–2.87°C in these runs.",
        ),
        (
            "Model-structure experiment",
            "Hold SSP2 + low objective",
            "Vary four IAMs",
            "IMAGE SSP2-L, MESSAGE SSP2-L, REMIND SSP2-PkBudg1000 and TIAM-UCL SSP2-RCP26 all peak at 1.82–1.92°C; native constraint names still differ.",
        ),
    ]
    return html.Div(
        [
            eyebrow("Read the pathways · controlled comparisons"),
            title(
                "Change one dimension at a time",
                "The left comparison changes only climate ambition; the right changes only the IAM for a matched low-emissions SSP2 objective",
            ),
            graph(
                controlled_comparison_figure(),
                "graph-frame controlled-comparison-graph",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong(label),
                            html.Div(
                                [
                                    html.Span(held),
                                    html.I("→"),
                                    html.Span(varied),
                                ],
                                className="controlled-formula",
                            ),
                            html.P(question),
                        ],
                        className="controlled-comparison-card",
                    )
                    for label, held, varied, question in comparisons
                ],
                className="controlled-comparison-cards",
            ),
            takeaway(
                "Controlled comparisons help explain why results differ. When comparing IAMs, explain how you matched their different scenario constraints."
            ),
        ],
        className="slide controlled-comparison-slide",
    )


def slide_sector_explorer(sector: str, year: int, mode: str) -> html.Div:
    sectors = (
        ("Electricity", "Electricity"),
        ("Transport Passenger Cars", "Passenger cars"),
        ("Cement", "Cement"),
        ("Steel", "Steel"),
    )
    sector_specs = {
        "Electricity": (
            "Electricity",
            "Compare the generation mix, total output and regional suppliers updated by premise",
            "Which foreground exchanges use this mix? Which conclusions also depend on biomass or CCS?",
        ),
        "Transport Passenger Cars": (
            "Passenger cars",
            "Powertrain shares, total mobility activity and energy-system dependence",
            "Would the comparison change through the vehicle fleet, mobility demand, fuel supply or electricity background?",
        ),
        "Cement": (
            "Cement",
            "Kiln routes, capture configurations and total material production",
            "Does the foreground depend on lower cement demand, a different kiln fleet, CCS, or all three?",
        ),
        "Steel": (
            "Steel",
            "Primary, secondary, CCS and hydrogen routes at different production scales",
            "Which changes in production routes and suppliers affect this steel-intensive foreground system?",
        ),
    }
    if sector not in sector_specs:
        sector = "Electricity"
    display_name, subtitle, question = sector_specs[sector]
    mapping_sector = {
        "Electricity": "Electricity",
        "Transport Passenger Cars": "Passenger cars",
        "Cement": "Cement",
        "Steel": "Steel",
    }[sector]
    mapping_frame = premise_mapping_counts()
    mapped_count = int(
        mapping_frame.loc[
            mapping_frame["model"].eq("image")
            & mapping_frame["sector"].eq(mapping_sector),
            "mapped_variable_count",
        ].iloc[0]
    )
    absolute_notes = {
        "Electricity": "CH low-voltage intensity × IMAGE World generation; a rough total based on inventory intensity, not a geographically matched system LCA.",
        "Transport Passenger Cars": "Not scaled: IMAGE activity is not identified as vehicle-km in this extract. A documented activity or occupancy conversion is required.",
        "Cement": "CH cement intensity × IMAGE World production; a rough total based on inventory intensity, not a geographically matched system LCA.",
        "Steel": "WEU steel intensity × IMAGE World production; a rough total based on inventory intensity, not a geographically matched system LCA.",
    }
    audit_label = (
        "Absolute GWP audit" if mode == "absolute" else f"{display_name} audit"
    )
    audit_text = absolute_notes[sector] if mode == "absolute" else question
    source_text = (
        "Absolute GWP multiplies calculated regional premise intensities by IMAGE World activity after converting the units. It is labelled as a rough inventory-based total. Passenger cars remain unscaled because the IAM activity unit is unclear."
        if mode == "absolute"
        else "IAM charts: World · four IMAGE pathways. GWP: premise 2.4.6 + ecoinvent 3.12 cutoff · IPCC 2021 GWP100 incl. biogenic CO₂ · calculated 2020/2040/2060 points; lines guide the eye."
    )
    return html.Div(
        [
            eyebrow("Interactive pathway explorer · IMAGE"),
            title("Explore how scenarios change each sector", subtitle),
            choice_controls(year, mode, sector=sector, sectors=sectors),
            html.Div(
                [
                    graph(
                        sector_snapshot(sector, year, mode),
                        "graph-frame sector-main",
                    ),
                    graph(
                        sector_total_figure(sector),
                        "graph-frame sector-side",
                    ),
                    graph(
                        commodity_gwp_figure(sector, mode),
                        "graph-frame sector-gwp",
                    ),
                ],
                className="sector-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong(str(mapped_count)),
                            html.Span(
                                f"mapped IMAGE {mapping_sector.lower()} variables in premise 2.4.6"
                            ),
                        ],
                        className="sector-mapping-badge",
                    ),
                    html.Div(
                        [html.Strong(audit_label), html.Span(audit_text)],
                        className="sector-audit-question",
                    ),
                ],
                className="sector-explorer-footer",
            ),
            source_note(source_text),
        ],
        className="slide consolidated-sector-slide",
    )


def slide_cdr_summary() -> html.Div:
    frame = pathways()
    reported = set(
        frame.loc[
            frame["model"].eq("image")
            & frame["sector"].eq("Carbon Dioxide Removal")
            & frame["region"].eq("World"),
            "scenario",
        ]
    )
    missing = [scenario for scenario in CORE_SCENARIOS if scenario not in reported]
    return html.Div(
        [
            eyebrow("Read the pathways · removal dependence"),
            title(
                "Low warming in 2100 can depend on large future removals",
                "Compare annual removals, the cumulative amount removed and the temperature change from its peak to 2100",
            ),
            graph(cdr_overshoot_summary_figure(), "graph-frame cdr-summary-graph"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Large temperature overshoot"),
                            html.Strong("SSP2-VLHO"),
                            html.H2("479 Gt cumulative"),
                            html.P(
                                "12.2 Gt CO₂/yr in 2100 · warming falls from 2.02°C to 1.59°C."
                            ),
                        ],
                        className="cdr-reading-card cdr-reading-high",
                    ),
                    html.Div(
                        [
                            html.Span("Less reliance on removals"),
                            html.Strong("SSP1-L"),
                            html.H2("120 Gt cumulative"),
                            html.P(
                                "4.4 Gt CO₂/yr in 2100 · warming falls from 1.89°C to 1.69°C."
                            ),
                        ],
                        className="cdr-reading-card cdr-reading-low",
                    ),
                    html.Div(
                        [
                            html.Span("No comparable decline"),
                            html.Strong("SSP2-M · SSP3-H"),
                            html.H2("warming still rises"),
                            html.P(
                                f"SSP2-M reaches 2.85°C; SSP3-H reaches 3.56°C. There is no reported CDR row for {', '.join(missing) if missing else 'the missing pathway'}. Missing data do not mean zero removals."
                            ),
                        ],
                        className="cdr-reading-card cdr-reading-missing",
                    ),
                ],
                className="cdr-reading-grid",
            ),
            takeaway(
                "Compare the climate result with its reliance on carbon removal. CDR changes future energy, biomass, material, transport and storage needs."
            ),
        ],
        className="slide cdr-summary-slide",
    )


def slide_transformation_coverage() -> html.Div:
    mapping_frame = premise_mapping_counts()
    image_counts = dict(
        mapping_frame.loc[mapping_frame["model"].eq("image")]
        .set_index("sector")["mapped_variable_count"]
        .astype(int)
    )
    sectors = [
        (
            "electricity",
            "EL",
            "Electricity",
            "Electricity",
            "Generation mix + efficiency",
            "Regional markets + power plants",
            "Every electricity-consuming activity",
            "Device demand + foreground exchanges",
        ),
        (
            "steel",
            "ST",
            "Steel",
            "Steel",
            "Route shares + production",
            "Steel markets + production routes",
            "Steel-intensive products",
            "Product mass, lifetime + design",
        ),
        (
            "transport",
            "TR",
            "Transport",
            "Passenger cars",
            "Fleet mix + energy intensity",
            "Vehicles + operation + fuels",
            "Passenger transport services",
            "Mobility demand, occupancy + lifetime",
        ),
        (
            "cement",
            "CE",
            "Cement",
            "Cement",
            "Kiln mix + CCS + efficiency",
            "Clinker + cement production",
            "Buildings and infrastructure",
            "Material demand + structural design",
        ),
        (
            "dac",
            "CDR",
            "Carbon removal",
            "Carbon removal",
            "Deployment + cumulative learning",
            "Solvent + sorbent DAC inventories",
            "Removal burdens and credits",
            "Removal service + permanence boundary",
        ),
    ]
    cards = []
    for (
        key,
        abbreviation,
        label,
        mapping_sector,
        signal,
        inventory,
        effect,
        outside,
    ) in sectors:
        cards.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.B(abbreviation, className="coverage-sector-code"),
                            html.Div(
                                [
                                    html.Strong(label),
                                    html.Span(
                                        f"{image_counts[mapping_sector]} IMAGE aliases mapped"
                                    ),
                                ]
                            ),
                        ],
                        className="coverage-sector-heading",
                    ),
                    html.Div(
                        [
                            html.Span("IAM signal"),
                            html.B(signal),
                            html.I("premise maps ↓"),
                            html.Span("Inventory change"),
                            html.B(inventory),
                        ],
                        className="coverage-sector-path",
                    ),
                    html.P(
                        [html.Strong("Affects · "), effect],
                        className="coverage-sector-effect",
                    ),
                    html.Div(
                        [
                            html.Span("You still define"),
                            html.B(outside),
                        ],
                        className="coverage-sector-outside",
                    ),
                ],
                className=f"coverage-sector-card coverage-sector-{key}",
            )
        )
    flow_steps = [
        (
            "1",
            "IAM evidence",
            "Regional activity, technology shares and efficiency pathways",
            "coverage-flow-iam",
        ),
        (
            "2",
            "premise rules",
            "Map model variables; calculate shares, efficiencies and technology improvements",
            "coverage-flow-rules",
        ),
        (
            "3",
            "Background database",
            "Update markets, suppliers and selected production datasets",
            "coverage-flow-database",
        ),
        (
            "4",
            "Your LCA model",
            "Combine the transformed background with foreground choices",
            "coverage-flow-study",
        ),
    ]
    return html.Div(
        [
            eyebrow("From IAM to premise · transformation coverage"),
            title(
                "premise updates selected parts of the background database",
                "IAM evidence updates mapped markets, technologies and efficiencies. It does not change the foreground model.",
            ),
            html.Div(
                [
                    *[
                        item
                        for index, (number, heading, body, class_name) in enumerate(
                            flow_steps
                        )
                        for item in (
                            html.Div(
                                [
                                    html.B(number),
                                    html.Div([html.Strong(heading), html.Span(body)]),
                                ],
                                className=f"coverage-flow-step {class_name}",
                            ),
                            *(
                                [html.I("→", className="coverage-flow-arrow")]
                                if index < len(flow_steps) - 1
                                else []
                            ),
                        )
                    ]
                ],
                className="coverage-flow",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Five applied examples"),
                            html.Span(
                                "Counts show mapped IMAGE variables in premise 2.4.6. They do not rank model quality."
                            ),
                        ],
                        className="coverage-examples-heading",
                    ),
                    html.Div(cards, className="coverage-sector-grid"),
                ],
                className="coverage-examples",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("premise does not make these choices"),
                            html.Span("The LCA study must define them"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("Functional unit"),
                            html.Span("Foreground demand"),
                            html.Span("Lifetime + design"),
                            html.Span("Unmapped processes"),
                        ],
                        className="coverage-boundary-chips",
                    ),
                ],
                className="coverage-boundary",
            ),
            takeaway(
                "Prospective LCA changes only where scenario evidence is mapped; everything else remains a study assumption."
            ),
        ],
        className="slide coverage-slide",
    )


def slide_lcia_evidence() -> html.Div:
    return html.Div(
        [
            eyebrow("Prospective impact assessment · evidence layers"),
            title(
                "Unit impact, deployment and causes are different questions",
                "Keep units and boundaries visible, then inspect the main contributors before explaining a score",
            ),
            graph(lcia_evidence_figure(), "graph-frame lcia-evidence-graph"),
            html.Div(
                [
                    html.Span("Intensity · Brightway functional unit"),
                    html.Span("Deployment · IAM system activity"),
                    html.Span(
                        "Main causes · activity contributions + remaining difference"
                    ),
                ],
                className="lcia-reading-strip",
            ),
            source_note(
                "IMAGE 3.4 · premise 2.4.6 · ecoinvent 3.12 cutoff · IPCC 2021 GWP100 including biogenic CO₂ · the remaining difference makes the listed contributions add up to the stored score."
            ),
            takeaway(
                "An unusual LCIA result is something to investigate. One visible pathway trend does not, by itself, explain the result."
            ),
        ],
        className="slide lcia-evidence-slide",
    )


def slide_process_system_boundary() -> html.Div:
    result = lcia_results()
    score = float(
        result.loc[
            result["case"].eq("electricity")
            & result["scenario"].eq("SSP1-L")
            & result["year"].eq(2060)
            & result["method_family"].eq("IPCC 2021"),
            "score",
        ].iloc[0]
    )
    pathway = pathways()
    activity = float(
        pathway.loc[
            pathway["model"].eq("image")
            & pathway["scenario"].eq("SSP1-L")
            & pathway["year"].eq(2060)
            & pathway["sector"].eq("Electricity")
            & pathway["region"].isin(["WEU", "CEU"]),
            "display_value",
        ].sum()
    )
    gates = [
        (
            "Geography",
            "CH low-voltage supply",
            "WEU + CEU generation",
            "mismatch",
        ),
        (
            "Product boundary",
            "delivered low-voltage kWh",
            "electricity generation",
            "mismatch",
        ),
        ("Year + pathway", "2060 · IMAGE SSP1-L", "2060 · IMAGE SSP1-L", "match"),
        (
            "Unit + coverage",
            "kg CO₂-eq/kWh",
            "EJ/yr; all routes required",
            "conditional",
        ),
    ]
    return html.Div(
        [
            eyebrow("Applied evidence · analytical boundary"),
            title(
                "Match boundaries before calculating total impact",
                "The unit result and IAM activity answer different questions until their geography, product boundary, year and scope match",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Prospective LCA intensity"),
                            html.H2(f"{score:.3f} kg CO₂-eq/kWh"),
                            html.Strong("CH low-voltage electricity · 2060"),
                            html.P("Answers: what is the impact of one supplied kWh?"),
                        ],
                        className="boundary-evidence-card boundary-intensity-card",
                    ),
                    html.Div(
                        [
                            html.Strong("≠"),
                            html.Span("not yet a system total"),
                        ],
                        className="boundary-not-equal",
                    ),
                    html.Div(
                        [
                            html.Span("IAM deployment activity"),
                            html.H2(f"{activity:.1f} EJ/yr"),
                            html.Strong("IMAGE WEU + CEU generation · 2060"),
                            html.P(
                                "Answers: how large is the regional electricity system?"
                            ),
                        ],
                        className="boundary-evidence-card boundary-activity-card",
                    ),
                ],
                className="boundary-evidence-row",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Compatibility check"),
                            html.Span("Intensity side"),
                            html.Span("Activity side"),
                            html.Span("Result"),
                        ],
                        className="boundary-gate-heading",
                    ),
                    *[
                        html.Div(
                            [
                                html.Strong(label),
                                html.Span(left),
                                html.Span(right),
                                html.B(
                                    (
                                        "✓ match"
                                        if status == "match"
                                        else (
                                            "△ resolve"
                                            if status == "conditional"
                                            else "✕ mismatch"
                                        )
                                    ),
                                    className=f"boundary-gate-status boundary-{status}",
                                ),
                            ],
                            className="boundary-gate-row",
                        )
                        for label, left, right, status in gates
                    ],
                ],
                className="boundary-gate-table",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("For a product question"),
                            html.P(
                                "Keep the functional-unit result. Compare scenario-specific kg CO₂-eq/kWh without importing an unrelated activity total."
                            ),
                        ],
                        className="boundary-outcome boundary-product-outcome",
                    ),
                    html.Div(
                        [
                            html.Strong("For a system question"),
                            html.P(
                                "First build an intensity covering the same region, energy chain, year and technologies; then convert units and multiply."
                            ),
                        ],
                        className="boundary-outcome boundary-system-outcome",
                    ),
                ],
                className="boundary-outcome-grid",
            ),
            source_note(
                "Example: workshop IMAGE 3.4 SSP1-L 2060 pathway and premise 2.4.6 + ecoinvent 3.12 cutoff electricity result. The displayed IAM activity is WEU + CEU generation; the LCIA functional unit is CH low-voltage supply."
            ),
            takeaway(
                "Total system impact must be calculated; it is not a direct IAM output. The result is well supported only when the activity and LCA boundaries match."
            ),
        ],
        className="slide process-system-slide",
    )


def slide_result_tracer(capstone: dict | None = None) -> html.Div:
    capstone = capstone or {
        "case": "steel",
        "scenario": "SSP2-VLHO",
        "year": 2060,
        "indicator": "climate",
    }
    case_key = str(capstone.get("case", "steel"))
    if case_key not in CAPSTONE_CASE_SPECS:
        case_key = "steel"
    scenario_key = str(capstone.get("scenario", "SSP2-VLHO"))
    if scenario_key not in CORE_SCENARIOS:
        scenario_key = "SSP2-VLHO"
    year = int(capstone.get("year", 2060))
    if year not in {2020, 2040, 2060}:
        year = 2060
    indicator_key = str(capstone.get("indicator", "climate"))
    if indicator_key not in CAPSTONE_INDICATOR_SPECS:
        indicator_key = "climate"
    case = CAPSTONE_CASE_SPECS[case_key]
    indicator = CAPSTONE_INDICATOR_SPECS[indicator_key]
    frame = lcia_results()
    mask = (
        frame["model"].eq("image")
        & frame["case"].eq(case_key)
        & frame["technology"].eq(case["technology"])
        & frame["scenario"].eq(scenario_key)
        & frame["year"].eq(year)
        & frame["method_family"].eq(indicator["method_family"])
    )
    if indicator["category"]:
        mask &= frame["category"].eq(indicator["category"])
    row = frame.loc[mask].iloc[0]
    premise_key = "transport" if case_key == "passenger_cars" else case_key
    transformation = PREMISE_TRANSFORMATIONS[premise_key]
    contribution_frame = lcia_contributions()
    contribution_mask = (
        contribution_frame["case"].eq(case_key)
        & contribution_frame["technology"].eq(case["technology"])
        & contribution_frame["scenario"].eq(scenario_key)
        & contribution_frame["year"].eq(year)
        & contribution_frame["method_family"].eq(indicator["method_family"])
    )
    if indicator["category"]:
        contribution_mask &= contribution_frame["category"].eq(indicator["category"])
    contribution_count = int(contribution_mask.sum())
    score = float(row["score"])
    score_text = f"{score:.3f}" if abs(score) >= 0.01 else f"{score:.2e}"
    scenario_color = NARRATIVES[scenario_key]["color"]
    mapping_status = {
        "validated_against_premise_2.4.6_smoke_build": (
            "checked in a premise 2.4.6 test build"
        ),
        "teaching_summary": "teaching summary; not checked in a test build",
    }.get(transformation["status"], transformation["status"].replace("_", " "))
    return html.Div(
        [
            eyebrow("Applied evidence · interactive audit trail"),
            title(
                "Trace an LCA result back to the scenario data",
                "Select one result; every panel then follows the same scenario, year, case and indicator",
            ),
            capstone_controls(case_key, scenario_key, year, indicator_key),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("1"),
                                    html.Div(
                                        [
                                            html.Strong("What changes in the pathway?"),
                                            html.Small(
                                                f"{case['signal']} · {scenario_key} · {year}"
                                            ),
                                        ]
                                    ),
                                ],
                                className="tracer-step-heading",
                            ),
                            graph(
                                capstone_signal_figure(case_key, year, scenario_key),
                                "graph-frame tracer-top-graph tracer-signal-graph",
                            ),
                        ],
                        className="tracer-step-panel tracer-iam-panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("2"),
                                    html.Div(
                                        [
                                            html.Strong("What does premise transform?"),
                                            html.Small(
                                                "Model evidence → inventory change"
                                            ),
                                        ]
                                    ),
                                ],
                                className="tracer-step-heading",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("IAM evidence"),
                                            html.B(transformation["iam_input"]),
                                        ],
                                        className="tracer-mapping-stage",
                                    ),
                                    html.I("↓"),
                                    html.Div(
                                        [
                                            html.Span("Mapped parameter"),
                                            html.B(transformation["derived_parameter"]),
                                        ],
                                        className="tracer-mapping-stage tracer-mapping-derived",
                                    ),
                                    html.I("↓"),
                                    html.Div(
                                        [
                                            html.Span("Inventory change"),
                                            html.B(transformation["inventory_change"]),
                                        ],
                                        className="tracer-mapping-stage tracer-mapping-inventory",
                                    ),
                                ],
                                className="tracer-mapping-flow",
                            ),
                            html.Div(
                                [
                                    html.Strong("Mapping status"),
                                    html.Span(mapping_status),
                                ],
                                className="tracer-mapping-status",
                            ),
                        ],
                        className="tracer-mapping-card",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("3"),
                                    html.Div(
                                        [
                                            html.Strong(
                                                "How does the unit result change over time?"
                                            ),
                                            html.Small(
                                                f"{indicator['label']} across four scenarios"
                                            ),
                                        ]
                                    ),
                                ],
                                className="tracer-step-heading",
                            ),
                            graph(
                                capstone_lcia_trajectory_figure(
                                    case_key,
                                    indicator_key,
                                    scenario_key,
                                    year,
                                ),
                                "graph-frame tracer-top-graph tracer-result-graph",
                            ),
                        ],
                        className="tracer-step-panel tracer-lcia-panel",
                    ),
                ],
                className="tracer-top-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("4"),
                                    html.Div(
                                        [
                                            html.Strong(
                                                "Why is the selected result different?"
                                            ),
                                            html.Small(
                                                "Activity contributions plus the remaining difference"
                                            ),
                                        ]
                                    ),
                                ],
                                className="tracer-step-heading",
                            ),
                            graph(
                                capstone_contribution_figure(
                                    case_key,
                                    year,
                                    indicator_key,
                                    scenario_key,
                                ),
                                "graph-frame tracer-contribution-graph tracer-cause-graph",
                            ),
                        ],
                        className="tracer-contribution-panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("Selected point"),
                                    html.Small(
                                        f"{scenario_key} · {year} · {indicator['label']}"
                                    ),
                                ],
                                className="tracer-result-heading",
                            ),
                            html.Div(score_text, className="tracer-score-value"),
                            html.Div(str(row["unit"]), className="tracer-score-unit"),
                            html.Div(
                                [
                                    html.Span(scenario_key),
                                    html.Span(str(year)),
                                    html.Span(indicator["label"]),
                                ],
                                className="tracer-result-chips",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Strong("Functional unit"),
                                            html.Span(str(row["functional_unit"])),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Strong("Activity · location"),
                                            html.Span(
                                                f"{case['technology']} · {row['region']}"
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Strong("Method"),
                                            html.Span(str(row["indicator"])),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Strong("Contributors"),
                                            html.Span(
                                                f"{contribution_count} rows + remaining difference"
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Strong("Database"),
                                            html.Span(str(row["database_name"])),
                                        ]
                                    ),
                                ],
                                className="tracer-result-receipt",
                            ),
                        ],
                        className="tracer-selected-result",
                        style={"borderTopColor": scenario_color},
                    ),
                ],
                className="tracer-bottom-grid",
            ),
            source_note(
                "Calculated evidence: IMAGE 3.4 · premise 2.4.6 · ecoinvent 3.12 cutoff · 2020/2040/2060. Faded series provide context. The selected point, score card and contribution chart all use the same scenario, year, case and indicator."
            ),
        ],
        className="slide result-tracer-slide",
    )


def slide_steel_causal_chain() -> html.Div:
    pathway_frame = pathways()
    steel_pathway = pathway_frame.loc[
        pathway_frame["model"].eq("image")
        & pathway_frame["scenario"].eq("SSP2-VLHO")
        & pathway_frame["region"].eq("WEU")
        & pathway_frame["sector"].eq("Steel")
    ].copy()
    totals = steel_pathway.groupby("year", observed=True)["display_value"].sum()
    secondary = (
        steel_pathway.loc[steel_pathway["variable"].eq("secondary")]
        .groupby("year", observed=True)["display_value"]
        .sum()
    )
    secondary_2020 = float(secondary.loc[2020] / totals.loc[2020])
    secondary_2060 = float(secondary.loc[2060] / totals.loc[2060])
    production_2020 = float(totals.loc[2020])
    production_2060 = float(totals.loc[2060])
    steel_scores = lcia_results().loc[
        lcia_results()["case"].eq("steel")
        & lcia_results()["technology"].eq("low-alloyed steel market")
        & lcia_results()["scenario"].eq("SSP2-VLHO")
        & lcia_results()["method_family"].eq("IPCC 2021")
    ]
    score_2020 = float(steel_scores.loc[steel_scores["year"].eq(2020), "score"].iloc[0])
    score_2060 = float(steel_scores.loc[steel_scores["year"].eq(2060), "score"].iloc[0])
    return html.Div(
        [
            eyebrow("Applied case · steel"),
            title(
                "Steel links production routes, unit impact and total output",
                "IMAGE supplies the SSP2-VLHO steel-route pathway for WEU. premise updates WEU production inventories, and Brightway calculates one kilogram from the WEU market.",
            ),
            graph(steel_causal_chain_figure(), "graph-frame steel-causal-graph"),
            html.Div(
                [
                    metric_card(
                        f"{secondary_2020:.0%} → {secondary_2060:.0%}",
                        "WEU secondary-route share",
                        "More scrap-based production changes electricity and upstream material dependencies.",
                        "energy-layer-good",
                    ),
                    metric_card(
                        f"{score_2060 / score_2020 - 1:+.0%}",
                        "GWP per kg · SSP2-VLHO",
                        f"{score_2020:.2f} → {score_2060:.2f} kg CO₂-eq/kg in the WEU market.",
                        "energy-layer-signal",
                    ),
                    metric_card(
                        f"{production_2060 / production_2020 - 1:+.0%}",
                        "Reported WEU steel output",
                        f"{production_2020:.0f} → {production_2060:.0f} Mt/yr; regional demand and trade still need separate interpretation.",
                        "energy-layer-risk",
                    ),
                    metric_card(
                        "WEU → WEU → WEU",
                        "One regional boundary",
                        "The IAM route mix, premise steel market and LCIA contributions now refer to WEU; Swiss consumption is not inferred.",
                        "energy-layer-premise",
                    ),
                ],
                className="steel-causal-metrics",
            ),
            source_note(
                "All quantitative panels use WEU. Workshop calculation: IMAGE 3.4 SSP2-VLHO · premise 2.4.6 · ecoinvent 3.12 cutoff · IPCC 2021 GWP100 including biogenic CO₂. Case framing adapted from Harpprecht et al. (2025) in the provided source decks."
            ),
            takeaway(
                "Within one WEU boundary, a lower impact per kilogram is still only one part of the decision: route feasibility, suppliers, demand and trade remain separate questions."
            ),
        ],
        className="slide steel-causal-slide",
    )


def slide_pv_inventory_resolution() -> html.Div:
    completion_steps = [
        ("IAM evidence", "Solar-PV deployment and aggregate electricity-system role"),
        (
            "External evidence",
            "Module technology, efficiency, manufacturing geography and materials",
        ),
        (
            "premise representation",
            "Current module inventories extended globally and improved through time",
        ),
        (
            "LCA consequence",
            "Climate intensity, land, water and material-resource indicators",
        ),
    ]
    return html.Div(
        [
            eyebrow("Applied case · technology detail"),
            title(
                "The IAM says solar; the LCA needs a specific module technology",
                "Prospective inventories add details that the IAM does not provide",
            ),
            html.Div(
                [
                    html.Div(
                        html.Img(
                            src=asset_url("pv-module-efficiency-premise.png"),
                            alt="Photovoltaic module efficiency trajectories used in premise",
                        ),
                        className="pv-efficiency-figure",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("Missing detail"),
                                    html.P(
                                        "The IAM reports aggregate solar deployment; it does not prescribe the future c-Si, CdTe, CIGS, perovskite or tandem market mix."
                                    ),
                                ],
                                className="pv-resolution-warning",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(str(index)),
                                            html.Div(
                                                [html.B(label), html.Small(detail)]
                                            ),
                                        ],
                                        className="pv-completion-step",
                                    )
                                    for index, (label, detail) in enumerate(
                                        completion_steps, 1
                                    )
                                ],
                                className="pv-completion-chain",
                            ),
                            html.Div(
                                [
                                    html.Strong("Assumptions defined by the LCA study"),
                                    html.Span("subtechnology shares"),
                                    html.Span("efficiency curve"),
                                    html.Span("lifetime"),
                                    html.Span("manufacturing mix"),
                                ],
                                className="pv-assumption-chips",
                            ),
                        ],
                        className="pv-resolution-panel",
                    ),
                ],
                className="pv-resolution-grid",
            ),
            source_note(
                "Source figure: provided presentation_IEA_PVPS_Task_12_2026.pptx, slide 10. The figure lists its underlying IEA, Fraunhofer, NREL, ITRPV and literature sources; shaded bands are reported min–max ranges."
            ),
            takeaway(
                "You must add details that the IAM does not provide. Make each added assumption visible, cite its source and test its influence instead of presenting it as an IAM result."
            ),
        ],
        className="slide pv-resolution-slide",
    )


def slide_pv_indicator_uncertainty() -> html.Div:
    return html.Div(
        [
            eyebrow("Applied case · uncertainty propagation"),
            title(
                "PV uncertainty affects indicators differently",
                "Uncertainty about module technology may have little effect on climate results but a large effect on resource results",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("1 · Possible technology mix"),
                            html.Img(
                                src=asset_url("pv-subtechnology-market-shares.png"),
                                alt="Uncertain global photovoltaic subtechnology market shares",
                            ),
                        ],
                        className="pv-market-panel",
                    ),
                    html.Div(
                        [
                            html.Strong("2 · Climate impact · Europe / USA / China"),
                            html.Div(
                                html.Img(
                                    src=asset_url("pv-system-uncertainty.png"),
                                    alt="Climate impact uncertainty across three regional PV pathways",
                                ),
                                className="pv-system-crop pv-system-climate-crop",
                            ),
                        ],
                        className="pv-system-column-panel",
                    ),
                    html.Div(
                        [
                            html.Strong("3 · Other impacts · index relative to 2020"),
                            html.Div(
                                html.Img(
                                    src=asset_url("pv-system-uncertainty.png"),
                                    alt="Non-climate impact uncertainty across three regional PV pathways",
                                ),
                                className="pv-system-crop pv-system-impact-crop",
                            ),
                        ],
                        className="pv-system-column-panel",
                    ),
                ],
                className="pv-uncertainty-evidence",
            ),
            html.Div(
                [
                    info_card(
                        "Climate results are less sensitive",
                        "Cleaner electricity dominates the climate result, so alternative PV module shares produce a narrow range.",
                    ),
                    info_card(
                        "Mineral results are highly sensitive",
                        "Material composition and manufacturing choices strongly affect mineral-resource results even under the same deployment pathway.",
                        "concept-accent",
                    ),
                    info_card(
                        "The wider system still matters",
                        "PV is not the sole driver of metals, land or water pressure; wind, grids, storage and electrified demand contribute too.",
                    ),
                ],
                className="pv-uncertainty-lessons",
            ),
            source_note(
                "Source figures: provided presentation_IEA_PVPS_Task_12_2026.pptx, slides 12–13. Market-share bands derive from 1,000 pseudo-random trajectories; system panels show the source study’s medians and uncertainty bands."
            ),
            takeaway(
                "Focus sensitivity analysis on the indicators that matter for the decision. A detail with little effect on GWP may strongly affect conclusions about material supply."
            ),
        ],
        className="slide pv-uncertainty-slide",
    )


def slide_system_tradeoffs() -> html.Div:
    findings = [
        (
            "Climate and air pollution",
            "Many <2°C pathways reduce particulate matter and aggregate health or ecosystem damage.",
        ),
        (
            "Land, water and minerals",
            "The same pathways can increase resource pressures through bioenergy, electrification and infrastructure.",
        ),
        (
            "Symbols show model choices",
            "Marker shape identifies the IAM, line style identifies the SSP and colour groups the warming outcomes.",
        ),
        (
            "Equal warming does not mean equal impacts",
            "Pathways with similar temperatures can still produce very different environmental outcomes.",
        ),
    ]
    return html.Div(
        [
            eyebrow("Applied evidence · system perspective"),
            title(
                "Similar warming can still have very different impacts",
                "System-wide prospective LCA shows trade-offs that a climate target alone cannot compare",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                html.Img(
                                    src=asset_url("system-lca-tradeoffs.png"),
                                    alt="Human-health trajectories across IAM, SSP and warming groups",
                                ),
                                className="tradeoff-panel-crop tradeoff-crop-health",
                            ),
                            html.Div(
                                html.Img(
                                    src=asset_url("system-lca-tradeoffs.png"),
                                    alt="Land-use trajectories across IAM, SSP and warming groups",
                                ),
                                className="tradeoff-panel-crop tradeoff-crop-land",
                            ),
                            html.Div(
                                html.Img(
                                    src=asset_url("system-lca-tradeoffs.png"),
                                    alt="Mineral-resource-scarcity trajectories across IAM, SSP and warming groups",
                                ),
                                className="tradeoff-panel-crop tradeoff-crop-minerals",
                            ),
                            html.Div(
                                [
                                    html.Strong(
                                        "Selected indicators shown at larger scale"
                                    ),
                                    html.Span(
                                        "Human health, land use and mineral scarcity show different outcomes for pathways with similar warming."
                                    ),
                                ],
                                className="tradeoff-selected-note",
                            ),
                        ],
                        className="system-tradeoff-figure system-tradeoff-selected",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("How to read the figure"),
                                    html.Div(
                                        [
                                            html.Span(
                                                [
                                                    html.I(
                                                        className="tradeoff-swatch swatch-low"
                                                    ),
                                                    "<2.0°C",
                                                ]
                                            ),
                                            html.Span(
                                                [
                                                    html.I(
                                                        className="tradeoff-swatch swatch-mid"
                                                    ),
                                                    "2.0–2.5°C",
                                                ]
                                            ),
                                            html.Span(
                                                [
                                                    html.I(
                                                        className="tradeoff-swatch swatch-high"
                                                    ),
                                                    ">2.5°C",
                                                ]
                                            ),
                                        ],
                                        className="tradeoff-color-key",
                                    ),
                                    html.P(
                                        "Values are percent change from 2020, not comparable physical units."
                                    ),
                                ],
                                className="tradeoff-read-card",
                            ),
                            *[
                                html.Div(
                                    [html.Strong(label), html.P(detail)],
                                    className="tradeoff-finding-card",
                                )
                                for label, detail in findings
                            ],
                        ],
                        className="tradeoff-reading-panel",
                    ),
                ],
                className="system-tradeoff-grid",
            ),
            source_note(
                "Source figure: provided ESD_PEA_course_Sacchi_280426.pptx, slide 30; Hahn Menacho et al. (2026, in review). The source compares IMAGE, MESSAGE and REMIND across SSP and GMST groups."
            ),
            takeaway(
                "Choose scenarios that represent different technologies and resource demands, not only different temperatures. The design of the transition determines where impacts move."
            ),
        ],
        className="slide system-tradeoff-slide",
    )


def slide_audit_chain() -> html.Div:
    checks = [
        (
            "01",
            "Scenario identity",
            "Which model, pathway, climate objective and year?",
            "Record the exact label used by the model and its narrative.",
        ),
        (
            "02",
            "Geography",
            "How does the inventory location map to an IAM region?",
            "State exact, aggregate or approximate mapping.",
        ),
        (
            "03",
            "Transformation coverage",
            "Which relevant sectors and variables were actually mapped?",
            "List the factors that were updated and those that were not mapped.",
        ),
        (
            "04",
            "Foreground consistency",
            "Could the foreground technology exist at this scale and time?",
            "Check deployment, lifetime, demand and design.",
        ),
        (
            "05",
            "Functional unit",
            "Is this a product intensity or a system total?",
            "Record product, amount, location and boundary.",
        ),
        (
            "06",
            "LCIA method",
            "Which method version, unit and carbon convention were used?",
            "Keep biogenic carbon and indicator variants explicit.",
        ),
        (
            "07",
            "Sensitivity",
            "Would another IAM, pathway or technology assumption change the decision?",
            "Change one assumption at a time instead of testing unrelated scenarios.",
        ),
        (
            "08",
            "Interpretation",
            "What changed, why, and what remains outside?",
            "Report the main contributors, the remaining difference and the conditions that apply.",
        ),
    ]
    return html.Div(
        [
            eyebrow("Applied evidence · reporting discipline"),
            title(
                "Check the full chain before reporting a result",
                "A prospective score can be trusted only when every step links to a model, mapping, inventory or explicit study choice",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(number, className="audit-number"),
                            html.Div(
                                [
                                    html.Strong(heading),
                                    html.P(question),
                                    html.Small(record),
                                ]
                            ),
                        ],
                        className="audit-card",
                    )
                    for number, heading, question, record in checks
                ],
                className="audit-grid",
            ),
            html.Div(
                [
                    html.Strong("Minimum reporting statement"),
                    html.P(
                        "For [functional unit] in [location, year], the [model + pathway] background built with [premise + source database] changes [mapped factors]. The result changes because of [contributors]; [foreground and unmapped assumptions] remain defined by the study."
                    ),
                    html.Div(
                        [
                            html.Span("model + pathway"),
                            html.Span("year + geography"),
                            html.Span("versions"),
                            html.Span("functional unit"),
                            html.Span("method + unit"),
                            html.Span("rationale + limitations"),
                        ],
                        className="audit-receipt-chips",
                    ),
                ],
                className="audit-report-template",
            ),
            takeaway(
                "A clear audit trail turns a scenario-dependent number into evidence that another analyst can reproduce, question and improve."
            ),
        ],
        className="slide audit-chain-slide",
    )


def slide_case_library() -> html.Div:
    groups = [
        (
            "Sector transition",
            "Use when output and production routes are both scenario-dependent.",
            [
                (
                    "ST",
                    "Steel",
                    "Can cleaner production routes offset growth in steel demand?",
                    "IMAGE + premise",
                    "routes · electricity · hydrogen · CCS",
                ),
                (
                    "CE",
                    "Cement",
                    "How much do kiln changes and CCS reduce unit burden?",
                    "IMAGE + premise",
                    "kilns · fuels · capture · clinker",
                ),
            ],
        ),
        (
            "Technology + supply chain",
            "Use when IAM results need more detail about technologies or material supply.",
            [
                (
                    "EV",
                    "Cars + metals",
                    "Do cleaner vehicles and metal supply evolve together?",
                    "REMIND + premise",
                    "vehicles · electricity · metal supply",
                ),
                (
                    "PV",
                    "Solar PV",
                    "Which conclusions depend on technology details that the IAM does not provide?",
                    "IAM/ESM + external inventories",
                    "module technology · efficiency · materials",
                ),
            ],
        ),
        (
            "Infrastructure + geography",
            "Use when networks, scale or national boundaries define the decision.",
            [
                (
                    "H₂",
                    "Hydrogen + ammonia",
                    "Where do scale and long-lived infrastructure shape the result?",
                    "IEA scenarios + premise",
                    "regional routes · electricity · CCS",
                ),
                (
                    "CH/FR",
                    "National systems",
                    "How do national pathways shift impacts across borders?",
                    "TIMES / RTE datapackages",
                    "demand · energy supply · national markets",
                ),
            ],
        ),
    ]
    return html.Div(
        [
            eyebrow("Applied evidence · case library"),
            title(
                "Choose a scenario source with the detail your decision needs",
                "Different decisions require different levels of sector, technology and geographic detail",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(group_name),
                                    html.P(group_rule),
                                ],
                                className="case-library-group-heading",
                            ),
                            *[
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span(
                                                    code,
                                                    className="case-library-code",
                                                ),
                                                html.H3(name),
                                            ],
                                            className="case-library-case-heading",
                                        ),
                                        html.P(question),
                                        html.Div(
                                            [
                                                html.Span("Evidence source"),
                                                html.B(source),
                                                html.Span("Scenario factors"),
                                                html.B(levers),
                                            ],
                                            className="case-library-case-details",
                                        ),
                                    ],
                                    className="case-library-case",
                                )
                                for code, name, question, source, levers in cases
                            ],
                        ],
                        className="case-library-group",
                    )
                    for group_name, group_rule, cases in groups
                ],
                className="case-library-grid",
            ),
            html.Div(
                [
                    html.Strong("How to choose"),
                    *[
                        item
                        for index, item in enumerate(
                            [
                                html.Span("Decision question"),
                                html.Span("Required detail"),
                                html.Span("Scenario source"),
                                html.Span("premise mapping"),
                                html.Span("Study-defined foreground"),
                            ]
                        )
                        for item in (
                            item,
                            *(
                                [html.I("→", className="case-library-arrow")]
                                if index < 4
                                else []
                            ),
                        )
                    ],
                ],
                className="case-library-scope",
            ),
            source_note(
                "Cases synthesized from the provided Background scenarios, ESD_PEA, Paris premise and IEA PVPS presentations."
            ),
            takeaway(
                "Start with the decision, not a favourite model. Then choose a source with enough detail to represent the factors that could change that decision."
            ),
        ],
        className="slide case-library-slide",
    )


def _legacy_slide_premise_library() -> html.Div:
    inputs = [
        (
            "Scenario evidence",
            "IAM or ESM pathways",
            "model · pathway · region · year · variable",
        ),
        (
            "Background inventory",
            "ecoinvent",
            "linked activities, exchanges and biosphere flows",
        ),
        (
            "Technology evidence",
            "Additional inventories",
            "emerging routes absent from the source database",
        ),
    ]
    outputs = [
        (
            "Scenario databases",
            "A transformed inventory for each model, pathway and year combination",
        ),
        (
            "Interoperable packages",
            "Brightway databases, superstructures and exchange formats",
        ),
    ]
    return html.Div(
        [
            eyebrow("Premise · library identity"),
            title(
                "Premise translates scenarios; it is not a scenario model",
                "An open-source Python library that converts quantified pathways into internally consistent prospective life-cycle inventories",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(kicker),
                                    html.Strong(heading),
                                    html.P(detail),
                                ],
                                className="premise-library-input",
                            )
                            for kicker, heading, detail in inputs
                        ],
                        className="premise-library-inputs",
                    ),
                    html.Div("→", className="premise-library-arrow"),
                    html.Div(
                        [
                            html.Span("PYTHON LIBRARY"),
                            html.H2("Premise"),
                            html.P(
                                "Maps scenario variables to sector-specific inventory transformations"
                            ),
                            html.Div(
                                [
                                    html.Code("NewDatabase"),
                                    html.Code("update"),
                                    html.Code("write/export"),
                                ],
                                className="premise-library-api",
                            ),
                        ],
                        className="premise-library-hub",
                    ),
                    html.Div("→", className="premise-library-arrow"),
                    html.Div(
                        [
                            html.Div(
                                [html.Strong(heading), html.P(detail)],
                                className="premise-library-output",
                            )
                            for heading, detail in outputs
                        ],
                        className="premise-library-outputs",
                    ),
                ],
                className="premise-library-flow",
            ),
            html.Div(
                [
                    html.Div([html.Strong("6"), html.Span("linked IAM models")]),
                    html.Div([html.Strong("≈30"), html.Span("IAM scenarios")]),
                    html.Div(
                        [html.Strong("2,300+"), html.Span("added technology datasets")]
                    ),
                    html.Div(
                        [
                            html.Strong("3.6–3.11"),
                            html.Span("ecoinvent versions in the supplied 2026 deck"),
                        ]
                    ),
                ],
                className="premise-library-stats",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("It does"),
                            html.Span(
                                "transform markets, efficiencies, emissions, technologies and links where mappings exist"
                            ),
                        ],
                        className="premise-library-does",
                    ),
                    html.Div(
                        [
                            html.Strong("It does not"),
                            html.Span(
                                "predict the future, replace the IAM, redesign every foreground process or calculate LCIA by itself"
                            ),
                        ],
                        className="premise-library-does premise-library-does-not",
                    ),
                ],
                className="premise-library-boundary",
            ),
            source_note(
                "Synthesized from Paris Premise introduction slides 13–23 and Background scenarios slides 9–19. Statistics reflect the supplied 2026 presentations."
            ),
            takeaway(
                "Premise uses selected scenario data to update life-cycle inventory databases. It does not turn an LCA model into an IAM."
            ),
        ],
        className="slide premise-library-slide",
    )


def _legacy_slide_premise_history() -> html.Div:
    milestones = [
        (
            "2018",
            "Background matters",
            "IMAGE pathways are linked to ecoinvent, showing how IAM changes can flow through product systems.",
            "METHOD",
        ),
        (
            "2020",
            "Automation emerges",
            "Premise generalizes repeatable IAM-to-ecoinvent transformations beyond one-off database modifications.",
            "TOOL",
        ),
        (
            "2022",
            "Open method + library",
            "The method paper and versioned Python package establish a reproducible, peer-reviewed workflow.",
            "RELEASE",
        ),
        (
            "2023–24",
            "Interoperability grows",
            "User scenarios, data-package export, consequential workflows, Brightway 2.5 and openLCA pathways broaden access.",
            "ECOSYSTEM",
        ),
        (
            "2025–26",
            "Coverage expands",
            "Six IAMs, ScenarioMIP families, incremental builds and additional heat, CDR, shipping and steel transformations.",
            "INFRASTRUCTURE",
        ),
    ]
    return html.Div(
        [
            eyebrow("Premise · development history"),
            title(
                "From one-off research links to shared scenario tools",
                "The library grew by separating reusable transformation rules from individual prospective-LCA case studies",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(tag, className="premise-history-tag"),
                            html.Strong(year, className="premise-history-year"),
                            html.H3(heading),
                            html.P(detail),
                        ],
                        className="premise-history-card",
                    )
                    for year, heading, detail, tag in milestones
                ],
                className="premise-history-timeline",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Research lineage"),
                            html.Span(
                                "THEMIS, wurst and early IMAGE/REMIND links showed both the value and the maintenance burden of scenario-adjusted backgrounds."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Infrastructure shift"),
                            html.Span(
                                "Versioned mappings, inventories and exports make the link easy to inspect, repeat and reuse beyond one publication."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Still evolving"),
                            html.Span(
                                "Coverage follows available scenario variables and LCI evidence; new sectors require explicit mappings and inventories."
                            ),
                        ]
                    ),
                ],
                className="premise-history-reading",
            ),
            source_note(
                "Timeline reconstructed from the supplied Paris Premise introduction and Background scenarios decks; method lineage includes Mendoza Beltran et al. (2018) and Sacchi et al. (2022)."
            ),
            takeaway(
                "Premise turns lessons from individual IAM–LCA studies into maintained, reusable transformation infrastructure."
            ),
        ],
        className="slide premise-history-slide",
    )


def _legacy_slide_premise_workflow() -> html.Div:
    steps = [
        (
            "1",
            "Define the scenario",
            "Model · pathway · year · region",
        ),
        (
            "2",
            "Read scenario signals",
            "Shares · efficiency · production · emissions",
        ),
        (
            "3",
            "Apply sector rules",
            "Markets · datasets · exchanges · parameters",
        ),
        (
            "4",
            "Relink the system",
            "Regional suppliers and new technologies",
        ),
        (
            "5",
            "Write or export",
            "Database · superstructure · data package",
        ),
    ]
    return html.Div(
        [
            eyebrow("Premise · executable workflow"),
            title(
                "A build converts scenario choices into inventory changes",
                "Three evidence inputs pass through documented mappings before any prospective database is calculated",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("A"),
                            html.Strong("Baseline LCI"),
                            html.P("ecoinvent version + system model"),
                        ],
                        className="premise-workflow-input",
                    ),
                    html.Div(
                        [
                            html.Span("B"),
                            html.Strong("Scenario data"),
                            html.P("IAM/ESM variables + regions + years"),
                        ],
                        className="premise-workflow-input",
                    ),
                    html.Div(
                        [
                            html.Span("C"),
                            html.Strong("Added evidence"),
                            html.P("new inventories + external datapackages"),
                        ],
                        className="premise-workflow-input",
                    ),
                ],
                className="premise-workflow-inputs",
            ),
            html.Div(
                [
                    item
                    for index, step in enumerate(steps)
                    for item in (
                        html.Div(
                            [
                                html.Span(step[0]),
                                html.Strong(step[1]),
                                html.P(step[2]),
                            ],
                            className="premise-workflow-step",
                        ),
                        *(
                            [html.I("→", className="premise-workflow-arrow")]
                            if index < len(steps) - 1
                            else []
                        ),
                    )
                ],
                className="premise-workflow-steps",
            ),
            html.Div(
                [
                    html.Pre(
                        [
                            html.Code(
                                "ndb = NewDatabase(scenarios=..., source_db=..., source_version=...)\n"
                                "ndb.update()\n"
                                'ndb.write_db_to_brightway("scenario_database")'
                            )
                        ],
                        className="premise-code-card",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("Build contract"),
                                    html.Span(
                                        "model · pathway · year · database version · system model"
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Strong("Validation"),
                                    html.Span(
                                        "mapped variables · links · new activities · one LCIA smoke test"
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Strong("Reproducibility"),
                                    html.Span(
                                        "code + versions + scenario source + transformation scope"
                                    ),
                                ]
                            ),
                        ],
                        className="premise-workflow-contract",
                    ),
                ],
                className="premise-workflow-bottom",
            ),
            source_note(
                "Workflow adapted from the five-stage diagrams in the supplied Paris, Background scenarios and IEA PVPS presentations; API pattern follows Premise NewDatabase."
            ),
            takeaway(
                "A prospective database is a build output with an explicit scenario, transformation scope and version record."
            ),
        ],
        className="slide premise-workflow-slide",
    )


def _legacy_slide_premise_ecosystem() -> html.Div:
    stages = [
        (
            "1",
            "Scenario sources",
            "IAM · ESM · user datapackage",
            "Quantified changes by region and year",
        ),
        (
            "2",
            "Premise + wurst",
            "Transformation layer",
            "Map, modify, add, relink and export inventories",
        ),
        (
            "3",
            "Brightway",
            "Data + calculation framework",
            "Store databases, build matrices and calculate LCI/LCIA",
        ),
        (
            "4",
            "Activity Browser",
            "Graphical workflow",
            "Inspect activities and compare scenarios through a superstructure",
        ),
    ]
    destinations = [
        (
            "Python analysis",
            "bw2calc / notebooks",
            "Automated LCIA, contributions, uncertainty and sensitivity",
        ),
        (
            "Activity Browser",
            "superstructure",
            "Switch year or scenario without duplicating the full database",
        ),
        (
            "Exchange",
            "unfold / openLCA / SimaPro",
            "Share scenario inventories beyond one Brightway project",
        ),
        (
            "System analysis",
            "Pathways",
            "Scale unit inventories with scenario activity and trace origins",
        ),
    ]
    return html.Div(
        [
            eyebrow("Premise · software ecosystem"),
            title(
                "Premise changes inventories; Brightway calculates results",
                "Premise changes inventory data, while neighbouring tools store, calculate, compare and scale the results",
            ),
            html.Div(
                [
                    item
                    for index, stage in enumerate(stages)
                    for item in (
                        html.Div(
                            [
                                html.Span(stage[0]),
                                html.H2(stage[1]),
                                html.Strong(stage[2]),
                                html.P(stage[3]),
                            ],
                            className="premise-ecosystem-stage",
                        ),
                        *(
                            [html.I("→", className="premise-ecosystem-arrow")]
                            if index < len(stages) - 1
                            else []
                        ),
                    )
                ],
                className="premise-ecosystem-flow",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                str(index),
                                className="premise-ecosystem-destination-number",
                            ),
                            html.Div(
                                [
                                    html.Strong(heading),
                                    html.Small(interface),
                                    html.P(detail),
                                ]
                            ),
                        ],
                        className="premise-ecosystem-destination",
                    )
                    for index, (heading, interface, detail) in enumerate(
                        destinations, 1
                    )
                ],
                className="premise-ecosystem-destinations",
            ),
            html.Div(
                [
                    html.Strong("Superstructure idea"),
                    html.Span(
                        "Store the exchanges that differ across scenarios once, then select the scenario column during calculation. This works well for comparing years and pathways in Activity Browser."
                    ),
                ],
                className="premise-superstructure-note",
            ),
            source_note(
                "Ecosystem roles synthesized from the open-source tool, workflow, Activity Browser and Pathways slides in the supplied presentations."
            ),
            takeaway(
                "Premise prepares scenario-dependent inventories; Brightway and Activity Browser turn them into reproducible calculations and comparisons."
            ),
        ],
        className="slide premise-ecosystem-slide",
    )


def _legacy_slide_premise_analysis_modes() -> html.Div:
    modes = [
        (
            "01",
            "Process-level LCA",
            "How does one functional unit change?",
            "LCIA intensity",
            "1 kWh · 1 kg steel · 1 pkm",
            "Compare years, pathways, technologies and contribution trees.",
        ),
        (
            "02",
            "Scenario comparison",
            "Which assumption changes the decision?",
            "Controlled contrasts",
            "same product × several backgrounds",
            "Use superstructures for model, pathway, year and technology sensitivity.",
        ),
        (
            "03",
            "System-level analysis",
            "What is the total transition burden?",
            "Intensity × activity",
            "kg CO₂-eq/kWh × EJ/yr",
            "Combine prospective inventories with IAM activity using Pathways or a study-defined scaling model.",
        ),
    ]
    return html.Div(
        [
            eyebrow("Premise · analytical possibilities"),
            title(
                "One set of databases supports three scales of analysis",
                "The database is shared; the functional unit, activity scaling and interpretation determine the question answered",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [html.Span(number), html.H2(heading)],
                                className="premise-analysis-heading",
                            ),
                            html.H3(question),
                            html.Div(
                                [html.Strong(calculation), html.Code(example)],
                                className="premise-analysis-equation",
                            ),
                            html.P(detail),
                        ],
                        className="premise-analysis-mode",
                    )
                    for number, heading, question, calculation, example, detail in modes
                ],
                className="premise-analysis-grid",
            ),
            html.Div(
                [
                    html.Strong("Dimensions that can be varied"),
                    html.Span("IAM model"),
                    html.Span("pathway"),
                    html.Span("year"),
                    html.Span("region"),
                    html.Span("technology detail"),
                    html.Span("LCIA method"),
                ],
                className="premise-analysis-dimensions",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Attribution"),
                            html.Span(
                                "Contribution analysis traces a score to transformed suppliers, technologies and biosphere flows."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Uncertainty"),
                            html.Span(
                                "Cross-IAM and technology sensitivity expose conclusions that depend on unresolved scenario detail."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Boundary rule"),
                            html.Span(
                                "Absolute system impacts require compatible geography, products, coverage and activity units."
                            ),
                        ]
                    ),
                ],
                className="premise-analysis-reading",
            ),
            source_note(
                "Analysis modes adapted from the process-LCA, Activity Browser superstructure and Pathways system-analysis examples in the supplied decks."
            ),
            takeaway(
                "Premise enables scenario-consistent inventories; the analysis design determines whether the result is an intensity, a comparison or a system total."
            ),
        ],
        className="slide premise-analysis-slide",
    )


def slide_premise_library() -> html.Div:
    stories = [
        (
            "01",
            "A Python library",
            "A programmable, versioned workflow rather than a collection of ready-made forecasts.",
            "blue",
        ),
        (
            "02",
            "A translation layer",
            "Maps scenario variables to markets, efficiencies, emissions, technologies and supplier links.",
            "teal",
        ),
        (
            "03",
            "A database generator",
            "Produces one transformed inventory for each model, pathway and year combination.",
            "amber",
        ),
    ]
    return html.Div(
        [
            eyebrow("Premise · library identity"),
            title(
                "Premise translates scenarios; it is not a scenario model",
                "This open-source Python library converts quantified pathways into consistent prospective life-cycle inventories",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Img(
                                        src=asset_url("premise-library-bridge.svg"),
                                        alt="Premise bridges IAM and ESM scenario evidence to prospective life-cycle inventory databases",
                                        className="premise-library-bridge-art",
                                    ),
                                    html.Img(
                                        src=asset_url("premise-logo-transparent.png"),
                                        alt="Official Premise logo",
                                        className="premise-library-official-logo",
                                    ),
                                ],
                                className="premise-library-figure",
                            ),
                            html.Div(
                                [
                                    html.Span([html.Strong("6"), " linked IAM models"]),
                                    html.Span([html.Strong("≈30"), " IAM scenarios"]),
                                    html.Span(
                                        [html.Strong("2,300+"), " added datasets"]
                                    ),
                                    html.Span(
                                        [
                                            html.Strong("3.6–3.11"),
                                            " ecoinvent range in the supplied deck",
                                        ]
                                    ),
                                ],
                                className="premise-library-stat-ribbon",
                            ),
                        ],
                        className="premise-library-art-panel",
                    ),
                    html.Div(
                        [
                            *[
                                html.Div(
                                    [
                                        html.Span(number),
                                        html.Div(
                                            [html.Strong(heading), html.P(detail)]
                                        ),
                                    ],
                                    className=f"premise-library-story premise-library-story-{color}",
                                )
                                for number, heading, detail, color in stories
                            ],
                            html.Div(
                                [
                                    html.Strong("Boundary"),
                                    html.P(
                                        "It does not predict the future, replace the IAM, redesign every foreground process or calculate LCIA by itself."
                                    ),
                                ],
                                className="premise-library-caveat",
                            ),
                        ],
                        className="premise-library-story-panel",
                    ),
                ],
                className="premise-library-visual-layout",
            ),
            source_note(
                "Synthesized from Paris Premise introduction slides 13–23 and Background scenarios slides 9–19. Statistics reflect the supplied 2026 presentations."
            ),
            takeaway(
                "Premise applies selected scenario evidence to LCI databases. It does not turn an LCA model into an IAM."
            ),
        ],
        className="slide premise-library-slide premise-library-visual-slide",
    )


def slide_premise_history() -> html.Div:
    milestones = [
        (
            "2018",
            "PAPER",
            "≋",
            "Background matters",
            "IMAGE pathways are linked to ecoinvent, so energy-system changes flow through product systems.",
        ),
        (
            "2020",
            "CODE",
            "</>",
            "Automated updates",
            "Reusable rules replace one-off database modifications.",
        ),
        (
            "2022",
            "RELEASE",
            "v1",
            "Open method + library",
            "A versioned package makes the workflow reproducible.",
        ),
        (
            "2023–24",
            "CONNECT",
            "⇄",
            "More tools connect",
            "User scenarios, more exports and openLCA broaden access.",
        ),
        (
            "2025–26",
            "SCALE",
            "6×",
            "Coverage expands",
            "Six IAMs and more sector transformations expand coverage.",
        ),
    ]
    return html.Div(
        [
            eyebrow("Premise · development history"),
            title(
                "From one-off research links to shared scenario tools",
                "The library grew by turning rules from individual prospective-LCA studies into reusable tools",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("ONE-OFF STUDY METHODS"),
                            html.I("→"),
                            html.Span("REUSABLE LIBRARY"),
                            html.I("→"),
                            html.Span("SHARED TOOLS"),
                        ],
                        className="premise-history-era-ribbon",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        icon, className="premise-history-visual-icon"
                                    ),
                                    html.Span(
                                        tag, className="premise-history-visual-tag"
                                    ),
                                    html.Strong(
                                        year, className="premise-history-visual-year"
                                    ),
                                    html.H3(heading),
                                    html.P(detail),
                                ],
                                className="premise-history-visual-stop",
                            )
                            for year, tag, icon, heading, detail in milestones
                        ],
                        className="premise-history-visual-stops",
                    ),
                ],
                className="premise-history-visual",
            ),
            html.Div(
                [
                    html.Strong("What changed?"),
                    html.Span(
                        "One-off study scripts became versioned mappings, inventories and exports that others can inspect and reuse."
                    ),
                    html.I(
                        "Coverage still follows the scenario variables and LCI evidence available."
                    ),
                ],
                className="premise-history-shift-ribbon",
            ),
            source_note(
                "Timeline reconstructed from the supplied Paris Premise introduction and Background scenarios decks; method lineage includes Mendoza Beltran et al. (2018) and Sacchi et al. (2022)."
            ),
            takeaway(
                "Premise turns lessons from individual IAM–LCA studies into maintained, reusable transformation tools."
            ),
        ],
        className="slide premise-history-slide premise-history-visual-slide",
    )


def slide_premise_workflow() -> html.Div:
    return html.Div(
        [
            eyebrow("Premise · executable workflow"),
            title(
                "A build converts scenario choices into inventory changes",
                "Mapping, update and relinking rules combine scenario evidence with inventory data before the prospective database is used",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src=asset_url("premise-transformation-engine.svg"),
                                alt="Scenario data and background inventories enter the Premise mapping, update and relinking engine and leave as prospective databases",
                                className="premise-engine-art",
                            )
                        ],
                        className="premise-engine-art-panel",
                    ),
                    html.Div(
                        [
                            html.Span("BUILD RECORD"),
                            html.H2("Three calls create the output"),
                            html.Pre(
                                html.Code(
                                    "ndb = NewDatabase(\n"
                                    "  scenarios=...,\n"
                                    "  source_db=...,\n"
                                    "  source_version=...\n"
                                    ")\n\n"
                                    "ndb.update()\n\n"
                                    "ndb.write_db_to_brightway(\n"
                                    '  "scenario_database"\n'
                                    ")"
                                ),
                                className="premise-build-code",
                            ),
                            html.Ol(
                                [
                                    html.Li(
                                        [
                                            html.Strong("Scenario"),
                                            " · model, pathway, year, region",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Scope"),
                                            " · mapped sectors and variables",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Versions"),
                                            " · library, source database, system model",
                                        ]
                                    ),
                                ],
                                className="premise-build-receipt-list",
                            ),
                        ],
                        className="premise-build-receipt",
                    ),
                ],
                className="premise-engine-layout",
            ),
            html.Div(
                [
                    html.Span(
                        [html.Strong("INPUT"), " scenario + LCI + added evidence"]
                    ),
                    html.I("→"),
                    html.Span([html.Strong("TRANSFORM"), " map + update + relink"]),
                    html.I("→"),
                    html.Span(
                        [html.Strong("OUTPUT"), " database + superstructure + package"]
                    ),
                ],
                className="premise-engine-summary-ribbon",
            ),
            source_note(
                "Workflow adapted from the supplied Paris, Background scenarios and IEA PVPS presentations; API pattern follows Premise NewDatabase."
            ),
            takeaway(
                "A prospective database is a build output with an explicit scenario, transformation scope and version record."
            ),
        ],
        className="slide premise-workflow-slide premise-engine-slide",
    )


def slide_premise_ecosystem() -> html.Div:
    roles = [
        ("Transform", "Premise + wurst", "Map and relink inventory data.", "teal"),
        ("Store + calculate", "Brightway", "Store projects and run LCI/LCIA.", "blue"),
        (
            "Explore",
            "Activity Browser",
            "Inspect activities and switch scenarios.",
            "red",
        ),
        ("Scale", "Pathways", "Scale inventories with scenario activity.", "amber"),
        (
            "Add time",
            "Trails",
            "Run time-explicit LCA from scenario inventories.",
            "orange",
        ),
        ("Exchange", "unfold · openLCA", "Exchange scenario inventories.", "purple"),
    ]
    return html.Div(
        [
            eyebrow("Premise · software ecosystem"),
            title(
                "Premise changes inventories; Brightway calculates results",
                "Other connected tools store, inspect, compare, exchange and scale the scenario results",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src=asset_url("premise-ecosystem-network.svg"),
                                alt="Premise connects scenario sources and ecoinvent to Brightway, Activity Browser, Pathways, Trails and exchange formats",
                                className="premise-network-art",
                            ),
                            html.Img(
                                src=asset_url("premise-logo-transparent.png"),
                                alt="Official Premise logo",
                                className="premise-network-official-logo",
                            ),
                            html.Img(
                                src=asset_url("brightway-logo.svg"),
                                alt="Official Brightway logo",
                                className="premise-network-brightway-logo",
                            ),
                            html.Img(
                                src=asset_url("pathways-logo.png"),
                                alt="Official Pathways logo",
                                className="premise-network-pathways-logo",
                            ),
                            html.Img(
                                src=asset_url("trails-logo-mark.png"),
                                alt="Official Trails logo",
                                className="premise-network-trails-logo",
                            ),
                        ],
                        className="premise-network-art-panel",
                    ),
                    html.Div(
                        [
                            html.Span("WHO DOES WHAT?"),
                            *[
                                html.Div(
                                    [
                                        html.I(
                                            className=f"premise-role-dot premise-role-{color}"
                                        ),
                                        html.Div(
                                            [
                                                html.Small(action),
                                                html.Strong(tool),
                                                html.P(detail),
                                            ]
                                        ),
                                    ],
                                    className="premise-role-row",
                                )
                                for action, tool, detail, color in roles
                            ],
                        ],
                        className="premise-role-legend",
                    ),
                ],
                className="premise-network-layout",
            ),
            html.Div(
                [
                    html.Strong("Compare scenarios efficiently"),
                    html.Span(
                        "Store only exchanges that differ across scenarios, then select the pathway/year column during calculation."
                    ),
                ],
                className="premise-superstructure-note",
            ),
            source_note(
                "Ecosystem roles synthesized from the open-source projects and the software-workflow slides in the supplied presentations."
            ),
            takeaway(
                "Premise prepares scenario-dependent inventories; Brightway and Activity Browser turn them into reproducible calculations and comparisons."
            ),
        ],
        className="slide premise-ecosystem-slide premise-network-slide",
    )


def slide_premise_analysis_modes() -> html.Div:
    modes = [
        (
            "01",
            "IAM activity",
            "How much is produced?",
            "Electricity output by technology, in EJ.",
            "blue",
        ),
        (
            "02",
            "Process LCA",
            "What is the impact per unit?",
            "Prospective intensity relative to 2025.",
            "teal",
        ),
        (
            "03",
            "System LCA",
            "What is the total burden?",
            "Activity × intensity, relative to 2025.",
            "amber",
        ),
    ]
    indicators = [
        ("Acidification", "#1f77b4"),
        ("Climate change", "#ff7f0e"),
        ("Freshwater toxicity", "#2ca02c"),
        ("Freshwater eutrophication", "#d62728"),
        ("Human toxicity (carc.)", "#9467bd"),
        ("Human toxicity (non-carc.)", "#8c564b"),
        ("PM formation", "#e377c2"),
        ("Smog formation", "#7f7f7f"),
    ]
    return html.Div(
        [
            eyebrow("Premise · analytical possibilities"),
            title(
                "One set of databases supports three scales of analysis",
                "A REMIND electricity example connects IAM production volumes, prospective unit scores and system-wide impacts",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("REMIND · SSP2-1000"),
                                    html.Span("Global electricity · <2 °C pathway"),
                                ],
                                className="premise-analysis-example-heading",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        [
                                            html.I(style={"backgroundColor": color}),
                                            html.Span(label),
                                        ]
                                    )
                                    for label, color in indicators
                                ],
                                className="premise-analysis-curve-legend",
                                role="list",
                                **{
                                    "aria-label": "Environmental indicator curve colours"
                                },
                            ),
                            html.Img(
                                src=asset_url("premise-analysis-electricity.png"),
                                alt="Electricity production volume, prospective per-unit environmental intensity and activity-scaled system impacts in REMIND SSP2-1000",
                                className="premise-analysis-example-image",
                            ),
                        ],
                        className="premise-analysis-example-panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(number),
                                    html.Div(
                                        [
                                            html.H2(heading),
                                            html.Strong(question),
                                            html.P(detail),
                                        ]
                                    ),
                                ],
                                className=f"premise-analysis-evidence-card premise-analysis-evidence-card-{color}",
                            )
                            for number, heading, question, detail, color in modes
                        ],
                        className="premise-analysis-evidence-cards",
                    ),
                ],
                className="premise-analysis-evidence-layout",
            ),
            html.Div(
                [
                    html.Strong("Read left → right"),
                    html.Span(
                        "A falling impact per kWh does not guarantee a falling system burden: production volume and technology deployment matter too."
                    ),
                ],
                className="premise-analysis-reading-ribbon",
            ),
            source_note(
                "Electricity example adapted from the supplied Background scenarios deck, slide 26; REMIND SSP2-1000."
            ),
            takeaway(
                "Premise supplies prospective intensities; system LCA becomes meaningful only when they are scaled with compatible IAM activity."
            ),
        ],
        className="slide premise-analysis-slide premise-scale-slide",
    )


def slide_resources() -> html.Div:
    groups = [
        (
            "Build prospective databases",
            "Code and documentation",
            [
                (
                    "Premise · GitHub",
                    "Source code, releases, issues and examples",
                    "https://github.com/polca/premise",
                ),
                (
                    "Premise · user guide",
                    "Installation, IAM selection, mappings and transformations",
                    "https://premise.readthedocs.io/en/latest/",
                ),
                (
                    "Activity Browser",
                    "Graphical Brightway workflow and superstructure comparisons",
                    "https://github.com/LCA-ActivityBrowser/activity-browser",
                ),
                (
                    "Brightway documentation",
                    "LCA projects, databases, calculations and tutorials",
                    "https://docs.brightway.dev/en/latest/",
                ),
                (
                    "Pathways · GitHub",
                    "System-wide prospective LCA from Premise data packages",
                    "https://github.com/polca/pathways",
                ),
            ],
        ),
        (
            "Explore pathways and dynamics",
            "Scenario data, assessments and temporal LCA",
            [
                (
                    "IIASA AR6 Scenario Explorer",
                    "IAM pathways assessed in IPCC AR6 WGIII",
                    "https://data.ece.iiasa.ac.at/ar6/",
                ),
                (
                    "IIASA SSP Explorer",
                    "Population, GDP and socioeconomic assumptions",
                    "https://ssp.apps.ece.iiasa.ac.at/",
                ),
                (
                    "IPCC AR6 WGIII · Chapter 3",
                    "Mitigation pathways compatible with long-term goals",
                    "https://www.ipcc.ch/report/ar6/wg3/chapter/chapter-3/",
                ),
                (
                    "ecoinvent",
                    "Source background inventory database and licensing",
                    "https://ecoinvent.org/",
                ),
                (
                    "Trails · GitHub",
                    "Time-explicit LCA with inventories that describe when exchanges occur",
                    "https://github.com/Laboratory-for-Energy-Systems-Analysis/trails",
                ),
            ],
        ),
        (
            "Reference the frameworks",
            "Core papers used in this workshop",
            [
                (
                    "Premise method · Sacchi et al. (2022)",
                    "Streamlined IAM-to-LCI database transformation workflow",
                    "https://doi.org/10.1016/j.rser.2022.112311",
                ),
                (
                    "SSP narratives · O’Neill et al. (2017)",
                    "Five societal worlds and challenges to mitigation/adaptation",
                    "https://doi.org/10.1016/j.gloenvcha.2016.10.009",
                ),
                (
                    "SSP quantification · Riahi et al. (2017)",
                    "Energy, land-use and emissions implications",
                    "https://doi.org/10.1016/j.gloenvcha.2016.05.009",
                ),
                (
                    "RCP overview · van Vuuren et al. (2011)",
                    "Radiative-forcing pathways used for climate experiments",
                    "https://doi.org/10.1007/s10584-011-0148-z",
                ),
                (
                    "ScenarioMIP-CMIP7 · Meinshausen et al. (2026)",
                    "New prescribed emissions families and experiment design",
                    "https://gmd.copernicus.org/articles/19/2627/2026/",
                ),
            ],
        ),
    ]
    return html.Div(
        [
            eyebrow("Workshop resources · code, data and references"),
            title(
                "Resources for building and documenting scenarios",
                "Open a link to reproduce the workflow, inspect pathway assumptions or cite the scenario framework",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [html.Span(kicker), html.H2(heading)],
                                className="resource-group-heading",
                            ),
                            *[
                                html.A(
                                    [
                                        html.Div([html.Strong(label), html.Span("↗")]),
                                        html.P(description),
                                        html.Small(url.replace("https://", "")),
                                    ],
                                    href=url,
                                    target="_blank",
                                    rel="noopener noreferrer",
                                    className="resource-link-card",
                                )
                                for label, description, url in links
                            ],
                        ],
                        className="resource-group",
                    )
                    for heading, kicker, links in groups
                ],
                className="resource-grid",
            ),
            html.Div(
                [
                    html.Strong("Minimum citation record"),
                    html.Span(
                        "IAM model + version · pathway · year · region mapping · premise version · source database · LCIA method"
                    ),
                ],
                className="resource-citation-strip",
            ),
            takeaway(
                "Reproducibility requires discoverable code, scenario sources, mappings and software versions."
            ),
        ],
        className="slide resources-slide",
    )


def slide_detective(reveal: int) -> html.Div:
    clue = min(reveal, 5)
    names_visible = reveal >= 6
    figure, clue_title = detective_figure(clue, names_visible)
    cards = []
    if names_visible:
        cards = [
            html.Div(
                [
                    html.Div(
                        s,
                        className="scenario-card-id",
                        style={"color": NARRATIVES[s]["color"]},
                    ),
                    html.Strong(NARRATIVES[s]["display_name"]),
                    html.P(NARRATIVES[s]["storyline"]),
                    html.P(NARRATIVES[s]["watch"], className="watch-text"),
                ],
                className="scenario-reveal-card",
            )
            for s in ANONYMOUS_ORDER
        ]
    prompt = (
        "Names revealed. Which clues helped, and which were misleading?"
        if names_visible
        else "Assign A–D to the four stories. Justify each answer with two clues."
    )
    return html.Div(
        [
            eyebrow(f"Interactive investigation · {clue_title}"),
            title("Scenario detective", prompt),
            graph(figure, "graph-frame detective-graph"),
            (
                html.Div(cards, className="scenario-reveal-grid")
                if cards
                else html.Div(
                    [html.Span(x) for x in "ABCD"], className="detective-choices"
                )
            ),
            source_note(
                "IMAGE 3.4 · World · source values retained; missing rows remain missing"
            ),
        ],
        className="slide",
    )


def slide_same_ssp() -> html.Div:
    return html.Div(
        [
            eyebrow("Controlled comparison"),
            title(
                "Same SSP2 storyline. Very different pathway.",
                "SSP2-VLHO versus SSP2-M in IMAGE",
            ),
            graph(pathway_comparison()),
            html.Div(
                [
                    info_card(
                        "Held broadly constant",
                        "SSP2 population, GDP and middle-of-the-road socioeconomic framing.",
                    ),
                    info_card(
                        "Policy experiment",
                        "Mitigation timing and stringency change the emissions constraint imposed on the same IAM.",
                        "concept-accent",
                    ),
                    info_card(
                        "Pathway response",
                        "Technology deployment, energy demand, overshoot and removal dependence emerge differently.",
                    ),
                    info_card(
                        "pLCA implication",
                        "The databases share a socioeconomic family but not the same electricity, fuels, materials or learning state.",
                    ),
                ],
                className="four-card-grid",
            ),
            takeaway(
                "An SSP is not a climate target. A shared narrative can support sharply different inventory pathways."
            ),
        ],
        className="slide",
    )


def sector_slide(
    sector: str, heading: str, subtitle: str, year: int, mode: str, question: str
) -> html.Div:
    figure = sector_snapshot(sector, year, mode)
    return html.Div(
        [
            eyebrow("Interactive pathway explorer · IMAGE"),
            title(heading, subtitle),
            choice_controls(year, mode),
            html.Div(
                [
                    graph(figure, "graph-frame sector-main"),
                    graph(sector_total_figure(sector), "graph-frame sector-side"),
                ],
                className="sector-grid",
            ),
            html.Div(question, className="question-banner"),
            source_note(
                "Reading protocol: compare total activity → composition → efficiency → regional mapping. World · four IMAGE pathways; click legend items to isolate technologies."
            ),
        ],
        className="slide",
    )


def slide_electricity(year: int, mode: str) -> html.Div:
    return sector_slide(
        "Electricity",
        "Electricity transition",
        "Total generation and technology composition answer different questions",
        year,
        mode,
        "Which pathway decarbonises through lower demand, faster clean deployment, or greater reliance on CCS and biomass?",
    )


def slide_transport(year: int, mode: str) -> html.Div:
    return sector_slide(
        "Transport Passenger Cars",
        "Transport transition",
        "Technology shares do not reveal total mobility demand",
        year,
        mode,
        "Would a battery comparison change because of vehicle technology, total activity, or the transformed electricity supply?",
    )


def slide_steel(year: int, mode: str) -> html.Div:
    return sector_slide(
        "Steel",
        "Steel transition",
        "Similar climate ambition can hide different production-route stories",
        year,
        mode,
        "Which route changes would matter most for a steel-intensive foreground system?",
    )


def slide_cdr(year: int, mode: str) -> html.Div:
    figure = (
        cumulative_cdr_figure()
        if mode == "cumulative"
        else sector_snapshot(
            "Carbon Dioxide Removal",
            year,
            "absolute" if mode == "absolute" else "share",
        )
    )
    return html.Div(
        [
            eyebrow("Interactive pathway explorer · IMAGE"),
            title(
                "Carbon removal and overshoot",
                "Annual deployment, technology composition and cumulative removal are not interchangeable",
            ),
            choice_controls(year, mode, ("share", "absolute", "cumulative")),
            html.Div(
                [
                    graph(figure, "graph-frame sector-main"),
                    graph(
                        scenario_trajectory("GMST increase", "Warming response", True),
                        "graph-frame sector-side",
                    ),
                ],
                className="sector-grid",
            ),
            html.Div(
                "Missing CDR rows are displayed as missing, never silently converted to zero.",
                className="honesty-note",
            ),
            takeaway(
                "Overshoot pathways transfer part of the mitigation burden into large, sustained future removal assumptions."
            ),
        ],
        className="slide",
    )


def slide_cross_iam() -> html.Div:
    return html.Div(
        [
            eyebrow("Model uncertainty"),
            title(
                "Same label, different IAM",
                "A scenario family does not erase model structure",
            ),
            graph(cross_iam_figure(), "graph-frame cross-iam-chart"),
            html.Div(
                [
                    info_card(
                        "Shared framing",
                        "SSP2 and a medium-emissions label define a common experiment, but not identical inputs.",
                    ),
                    info_card(
                        "Structural causes",
                        "Foresight, solution logic, regions, technology menus, constraints and land representation.",
                        "concept-accent",
                    ),
                    info_card(
                        "Diagnose before using",
                        "Check variable definitions, units, baseline calibration and regional aggregation before calling spread uncertainty.",
                    ),
                    info_card(
                        "pLCA consequence",
                        "A difference matters only if a premise transformation carries it into the product system.",
                    ),
                ],
                className="four-card-grid",
            ),
            takeaway(
                "Cross-IAM spread can be a material part of prospective-LCA scenario uncertainty."
            ),
        ],
        className="slide cross-iam-slide",
    )


def slide_r10() -> html.Div:
    statuses = [
        ("Exact", "Native geography matches R10", "mapping-exact"),
        ("Aggregated", "Complete native regions sum to R10", "mapping-aggregate"),
        ("Approximate", "Boundary or membership differs", "mapping-approximate"),
        ("Unavailable", "Resolution cannot support mapping", "mapping-unavailable"),
    ]
    return html.Div(
        [
            eyebrow("Geographic comparability"),
            title(
                "Where is “Europe”?",
                "A common label does not guarantee a common boundary",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                "Native model regions", className="region-heading"
                            ),
                            html.Div(
                                [
                                    html.Span("IMAGE"),
                                    html.Strong("WEU · CEU · TUR · UKR · RUS"),
                                ],
                                className="region-row",
                            ),
                            html.Div(
                                [html.Span("MESSAGE"), html.Strong("WEU · EEU · FSU")],
                                className="region-row",
                            ),
                            html.Div(
                                [html.Span("REMIND"), html.Strong("EUR · NEU · REF")],
                                className="region-row",
                            ),
                        ],
                        className="region-source-card",
                    ),
                    html.Div("→", className="region-arrow"),
                    html.Div(
                        [
                            html.Div("R10 Europe", className="region-heading"),
                            html.P(
                                "A documented country grouping, not just a different label."
                            ),
                            html.A(
                                "Open the common definition",
                                href=REGION_MAPPING["source"],
                                target="_blank",
                                className="source-link",
                            ),
                        ],
                        className="region-target-card",
                    ),
                ],
                className="region-map",
            ),
            html.Div(
                [
                    html.Div(
                        [html.H3(label), html.P(detail)],
                        className=f"mapping-card {style}",
                    )
                    for label, detail, style in statuses
                ],
                className="mapping-grid",
            ),
            takeaway("Display mapping quality beside every regional value."),
        ],
        className="slide",
    )


def pipeline_step(
    number: str, heading: str, detail: str, accent: bool = False
) -> html.Div:
    return html.Div(
        [
            html.Div(number, className="pipeline-number"),
            html.H3(heading),
            html.P(detail),
        ],
        className=f"pipeline-step{' pipeline-accent' if accent else ''}",
    )


def slide_premise_pipeline() -> html.Div:
    electricity = PREMISE_TRANSFORMATIONS["electricity"]
    return html.Div(
        [
            eyebrow("Coupling logic"),
            title(
                "From IAM output to a transformed inventory",
                "Trace evidence across interfaces without treating the models as interchangeable",
            ),
            html.Div(
                [
                    pipeline_step(
                        "1",
                        "Narrative + policy",
                        "Socioeconomic assumptions, targets and technology constraints",
                    ),
                    html.Div("→", className="pipeline-arrow"),
                    pipeline_step("2", "IAM pathway", electricity["iam_input"]),
                    html.Div("→", className="pipeline-arrow"),
                    pipeline_step(
                        "3", "premise parameter", electricity["derived_parameter"], True
                    ),
                    html.Div("→", className="pipeline-arrow"),
                    pipeline_step("4", "Inventory", electricity["inventory_change"]),
                    html.Div("→", className="pipeline-arrow"),
                    pipeline_step("5", "LCIA", electricity["downstream_effect"]),
                ],
                className="pipeline",
            ),
            html.Div(
                [
                    info_card(
                        "What changes",
                        "Selected background markets, efficiencies, emissions and technology-specific datasets.",
                    ),
                    info_card(
                        "What does not", electricity["not_changed"], "concept-accent"
                    ),
                ],
                className="comparison-row",
            ),
            takeaway(
                "premise makes selected sectors scenario-dependent; it does not convert every ecoinvent process into an IAM output."
            ),
        ],
        className="slide",
    )


def slide_transformations() -> html.Div:
    rows = [
        (
            "Electricity",
            "Generation shares + efficiencies",
            "Regional markets and power plants",
            "Every electricity-consuming supply chain",
        ),
        (
            "Steel",
            "Production volumes + route shares",
            "Primary, secondary, CCS and hydrogen routes",
            "Steel-intensive products and infrastructure",
        ),
        (
            "Transport",
            "Fleet technologies + efficiencies",
            "Vehicle and fuel supply datasets",
            "Passenger and freight services",
        ),
        (
            "Cement",
            "Kiln routes + CCS + energy",
            "Clinker and cement production",
            "Buildings and infrastructure",
        ),
        (
            "DAC",
            "Deployment + cumulative learning",
            "Solvent and sorbent DAC inventories",
            "Captured and durably stored CO₂",
        ),
    ]
    return html.Div(
        [
            eyebrow("premise transformation coverage"),
            title(
                "What premise changes",
                "The mapping is sector-specific, regional and version-dependent",
            ),
            html.Div(
                [
                    html.Div(
                        [html.Strong(a), html.Span(b), html.Span(c), html.Span(d)],
                        className="transformation-row",
                    )
                    for a, b, c, d in rows
                ],
                className="transformation-table",
            ),
            html.Div(
                [
                    html.Strong("Read every row left to right: "),
                    "IAM evidence → derived parameter → inventory datasets → downstream consequence",
                ],
                className="question-banner",
            ),
            takeaway(
                "Equal warming can coexist with different background technologies, efficiencies and upstream burdens."
            ),
        ],
        className="slide",
    )


def slide_lcia() -> html.Div:
    results = lcia_results()
    status = (
        f"{len(results):,} validated result rows loaded"
        if not results.empty
        else "Awaiting precomputed results from the included build and LCIA scripts"
    )
    return html.Div(
        [
            eyebrow("Prospective impact assessment"),
            title(
                "LCIA: intensity and scale tell different stories",
                "Compare per-unit improvement with total system deployment",
            ),
            html.Div(
                [
                    graph(lcia_comparison_figure(), "graph-frame lcia-main"),
                    html.Div(
                        [
                            html.Div(
                                status,
                                className=f"status-chip {'status-ready' if not results.empty else 'status-pending'}",
                            ),
                            info_card(
                                "What is plotted",
                                "Each score is indexed to SSP2-M 2040 within the same case, technology and indicator.",
                            ),
                            info_card(
                                "What the index permits",
                                "Compare direction and magnitude within an indicator; never compare unlike LCIA units.",
                            ),
                            info_card(
                                "What remains to calculate",
                                "For system scale, match boundaries and multiply per-unit scores by scenario activity or deployment.",
                                "concept-accent",
                            ),
                            info_card(
                                "Diagnose burden shifting",
                                "Use the contribution table to identify which transformed suppliers drive each change.",
                            ),
                        ],
                        className="side-panel dense-panel",
                    ),
                ],
                className="two-column chart-and-panel",
            ),
            html.Div(
                "No illustrative LCIA values are fabricated. The public app displays only reproducible aggregated results.",
                className="honesty-note",
            ),
            takeaway(
                "A cleaner process can still create greater total pressure if the scenario deploys it at much larger scale."
            ),
        ],
        className="slide lcia-slide",
    )


def slide_selection(votes: dict[str, int]) -> html.Div:
    prompts = [
        "Define the study question and decision year.",
        "Identify the background transformations that matter.",
        "Choose an anchor scenario and state the conditional question.",
        "Add a contrast that tests a different narrative, policy, model or technology dependency.",
        "Report model, pathway, year, region mapping, premise version, source database and rationale.",
    ]
    return html.Div(
        [
            eyebrow("Decision exercise"),
            title(
                "Choose a contrastive range",
                "Return to the opening decision with more evidence",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [html.Span(str(i)), html.P(prompt)],
                                className="selection-step",
                            )
                            for i, prompt in enumerate(prompts, 1)
                        ],
                        className="selection-list",
                    ),
                    html.Div(
                        [
                            html.H2("Record the room's revised anchor"),
                            vote_buttons(votes, final=True),
                            html.P(
                                "What evidence changed your choice?",
                                className="facilitator-hint",
                            ),
                        ],
                        className="side-panel selection-panel",
                    ),
                ],
                className="two-column selection-layout",
            ),
            takeaway(
                "Choose scenarios to test a decision, not to declare one future correct."
            ),
        ],
        className="slide",
    )


def render_slide(
    index: int,
    reveal: int,
    votes: dict[str, int],
    explore: dict | None = None,
    capstone: dict | None = None,
    iam_map: str | None = None,
) -> html.Div:
    explore = explore or {"sector": "Electricity", "year": 2060, "mode": "share"}
    capstone = capstone or {"case": "steel", "year": 2060, "indicator": "climate"}
    sector = str(explore.get("sector", "Electricity"))
    year = int(explore.get("year", 2060))
    mode = str(explore.get("mode", "share"))
    iam_map = str(iam_map or "image")
    renderers = {
        "IAM scenarios for prospective LCA": slide_welcome,
        "People need services, not fuel": slide_energy_climate,
        "Emissions come from a connected system": slide_emissions_system,
        "CO₂ accumulates, so the full pathway matters": slide_warming_budget,
        "Why do we need integrated assessment?": slide_why_integrate,
        "A target date is not a pathway": slide_net_zero_pathway,
        "An IAM is a structured thought experiment": slide_iam_definition,
        "IAMs represent different parts of the system": slide_iam_system_coverage,
        "IAMs can answer the same question differently": slide_model_architecture,
        "From emissions scenarios to policy evidence": slide_iam_history_policy,
        "SSPs differ before climate policy is added": slide_ssp_quantitative,
        "SSP1–SSP3: from cooperation to fragmentation": slide_ssp_1_to_3,
        "Fast innovation does not guarantee sustainability": slide_ssp_4_to_5,
        "RCPs define radiative-forcing experiments": slide_forcing_families,
        "CMIP7 families describe how emissions change over time": slide_emission_families,
        "A quantitative scenario combines three layers": slide_scenario_combinations,
        "Choose a pathway before seeing its assumptions": lambda: slide_anonymous(
            reveal
        ),
        "Investment changes the system over time": slide_mechanics,
        "First, compare the whole energy system": slide_total_energy_accounting_chain,
        "Then examine the electricity chain": slide_energy_accounting_chain,
        "Primary energy: resources entering the system": slide_primary_energy_layer,
        "Secondary energy: carriers produced after conversion": slide_secondary_energy_layer,
        "Final energy: energy delivered to users": slide_final_energy_layer,
        "Passenger cars: electrification reduces energy per kilometre": slide_passenger_car_transformation,
        "Cement: lower emissions require a different kiln mix": slide_cement_transformation,
        "Steel: recycled and electric routes replace blast furnaces": slide_steel_transformation,
        "Space heating: electricity and heat networks replace fossil boilers": slide_space_heating_transformation,
        "Premise gets different levels of detail from each IAM": slide_model_landscape,
        "What IAMs leave out": slide_limitations,
        "Can you explain why the LCA result changed?": slide_narratives,
        "Six IAMs group countries into different regions": lambda: slide_iam_region_explorer(
            iam_map
        ),
        "A Swiss inventory can map to different IAM regions": slide_applied_geography,
        "Change one dimension at a time": slide_controlled_comparisons,
        "Explore how scenarios change each sector": lambda: slide_sector_explorer(
            sector, year, mode
        ),
        "Low warming in 2100 can depend on large future removals": slide_cdr_summary,
        "Premise updates selected parts of the background database": slide_transformation_coverage,
        "Turn a scenario result into a well-supported LCA statement": slide_vocabulary,
        "Unit impact, deployment and causes are different questions": slide_lcia_evidence,
        "Match boundaries before calculating total impact": slide_process_system_boundary,
        "Trace an LCA result back to the scenario data": lambda: slide_result_tracer(
            capstone
        ),
        "Steel links production routes, unit impact and total output": slide_steel_causal_chain,
        "The IAM says solar; the LCA needs a specific module technology": slide_pv_inventory_resolution,
        "PV uncertainty affects indicators differently": slide_pv_indicator_uncertainty,
        "Similar warming can still have very different impacts": slide_system_tradeoffs,
        "Check the full chain before reporting a result": slide_audit_chain,
        "Choose a scenario source with the detail your decision needs": slide_case_library,
        "Premise translates scenarios; it is not a scenario model": slide_premise_library,
        "From one-off research links to shared scenario tools": slide_premise_history,
        "A build converts scenario choices into inventory changes": slide_premise_workflow,
        "Premise changes inventories; Brightway calculates results": slide_premise_ecosystem,
        "One set of databases supports three scales of analysis": slide_premise_analysis_modes,
        "Resources for building and documenting scenarios": slide_resources,
    }
    slide_title = SLIDE_TITLES[index]
    rendered = _style_premise_mentions(renderers[slide_title]())
    if index >= APPENDIX_START_SLIDE:
        rendered.className = f"{rendered.className or ''} backup-slide".strip()
        children = rendered.children
        if not isinstance(children, (list, tuple)):
            children = [children]
        rendered.children = [
            html.Div(
                [
                    html.Span("Backup", className="backup-slide-marker"),
                    html.Button(
                        "← Return to original slide",
                        id={"type": "return-from-backup", "slide": index},
                        n_clicks=0,
                        className="backup-return-button",
                    ),
                ],
                className="backup-slide-toolbar",
            ),
            *children,
        ]
    elif slide_title in BACKUP_LINKS:
        link = BACKUP_LINKS[slide_title]
        rendered.className = f"{rendered.className or ''} has-backup-link".strip()
        children = rendered.children
        if not isinstance(children, (list, tuple)):
            children = [children]
        rendered.children = [
            html.Button(
                [
                    html.Span("Backup", className="backup-link-kicker"),
                    html.Span(str(link["label"])),
                ],
                id={
                    "type": "backup-button",
                    "slide": SLIDE_TITLES.index(str(link["target"])),
                },
                n_clicks=0,
                className="backup-link-button",
            ),
            *children,
        ]
    return rendered


def slide_label(index: int) -> str:
    if index < APPENDIX_START_SLIDE:
        counter = f"{index + 1:02d}/{CORE_SLIDE_COUNT}"
    else:
        counter = f"B{index - APPENDIX_START_SLIDE + 1:02d}/" f"{APPENDIX_SLIDE_COUNT}"
    return f"{counter} · {SLIDE_TITLES[index]}"
