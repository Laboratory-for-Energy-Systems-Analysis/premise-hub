from __future__ import annotations

import os

from dash import dcc, html

from apps.lca_time.workshop import results
from .figures import (
    CASES,
    DEFAULT_END,
    PATHWAYS,
    REFERENCE_YEAR,
    WINDOW_MIN,
    WINDOW_START,
    forcing_figure,
    mix_figure,
    prospective_figure,
    pulse_figure,
    pulse_value,
    removal_requirements,
    scenario_context_figure,
    scenario_context_note,
    static_figure,
    static_score,
    temporal_figure,
)

TITLE = "How time integration changes LCA: the case of CDR"
UPLOAD_NAME = "1.01.T01_Romain Sacchi"
SLIDES = [
    dict(
        title=TITLE,
        phase="SETAC Europe LCA Case Study Symposium",
        seconds=20,
        notes="Introduce the title and the contribution: connecting future backgrounds, dated inventories and climate response. We follow the same BECCS and DACCS examples through three treatments of time. Move to the research question before discussing results.",
    ),
    dict(
        title="Does timing change the BECCS–DACCS comparison?",
        phase="Research question / Future supply chains and emission dates",
        seconds=25,
        notes="Pose the question: can the comparison between BECCS and DACCS change when we include future supply chains, the dates of emissions and removals, and the resulting climate response? Follow the same cases from current static to prospective static and then time-explicit assessment. The next slide introduces the physical systems. This is a methods illustration under fixed assumptions, not a universal technology ranking.",
    ),
    dict(
        title="BECCS and DACCS: material, energy and CO₂ flows",
        phase="CDR systems / Inputs and outputs per tonne stored",
        seconds=45,
        notes="Use the original lca_time system artwork to follow the selected 2025 physical flows. Both routes capture 1.029 tonnes of CO₂, lose 0.029 tonnes along the 2,000 km transport chain and store one tonne. This is physical net storage, before subtracting supply-chain GHG burdens. BECCS uses 0.630 tonnes of dry wood chips (12.85 GJ): forest uptake is 1.143 tonnes, 90% is captured and 0.114 tonnes return to the atmosphere at the stack. The new CHP supplies capture heat internally and exports 0.564 MWh electricity and 0.249 GJ heat; the reference leaves the mature forest standing and buys equivalent market energy. Capture also requires chemicals and cooling water. DACCS captures from air, uses 3.086 kg make-up sorbent and 1.854 MWh capture electricity, of which 1.134 MWh drives a heat pump supplying 12.243 GJ heat at COP 3. The heat is produced from the shown electricity, not an additional energy input. Both routes use a further 0.139 MWh for compression and storage. These are selected operating flows from the existing reviewed inventory, not a complete life-cycle inventory or a GWP balance. Point to the different dependencies, then move to the stacked LCA results.",
    ),
    dict(
        title="BECCS has the lower GWP100 score in 2025",
        phase="01 / Static LCA with Northern European supply chains",
        seconds=65,
        notes="Read the stacked bars from zero: emissions extend upward; CO₂ uptake and avoided-energy credits extend downward. White diamonds mark the net GWP100 scores, about −963 for BECCS and −831 for DACCS. Do not mistake the bottom of the negative stack for the net score. BECCS includes forest regrowth, residual stack emissions, harvesting, transport loss and CHP+CCS supply-chain burdens, with an avoided-energy credit. DACCS includes direct capture, upstream biogenic uptake, electricity supply, transport loss and other supply-chain contributions. The upstream uptake is inherited supply-chain accounting, not extra DAC operation; read it together with the energy burdens. The BECCS forest reference is held fixed. Under the 2025 background BECCS has the more negative GWP100 total, but the bars do not tell us when the removals or emissions occur.",
    ),
    dict(
        title="Future electricity, heat and material supply",
        phase="02 / Prospective backgrounds from REMIND-EU and premise",
        seconds=55,
        notes="Introduce integrated assessment models: scenarios connect socioeconomic assumptions and climate policy to future energy and industrial systems. premise maps the REMIND-EU SSP2 pathways into changes in ecoinvent supply mixes, process efficiency and emissions. These are conditional scenarios, not forecasts. The plots show premise-generated market shares in Northern Europe (ENC), for 2025, 2030 and 2050. Start with PkBudg1000: solar expands, market heat supply shifts away from oil toward electric and biomass routes, and steel shifts from BF–BOF toward direct reduction and scrap EAF. Switch to NPi to show that the direction and scale differ across sectors. The third selector also exposes clinker CCS and truck electrification. Hover for exact shares; do not imply smooth interpolation between the three stored snapshots. Steel abbreviations: BF–BOF is blast furnace/basic oxygen furnace; DRI–EAF is direct reduced iron/electric arc furnace. The heat shares come from the single ENC market named “market for heat, district or industrial”; the export does not distinguish district and industrial uses. This is not the DAC heat pump itself. The left plot compares GMST, CO₂ emissions or population across both pathways, for World or Northern Europe. GMST is global and therefore fixes the region to World. The selected pathway is highlighted and drives the three mix plots. The PDF fixes World GMST and PkBudg1000 mixes for electricity, heat and steel. Spend about 55 seconds here and move to the consequences for CDR scores.",
    ),
    dict(
        title="CDR scores with 2025, 2030 and 2050 backgrounds",
        phase="02 / Prospective static LCA under two SSP2 scenarios",
        seconds=55,
        notes="Each cluster is a background year; the left hatched stack uses NPi and the right solid stack uses PkBudg1000. The two panels show BECCS and DACCS. White diamonds and labels mark the net scores. Each bar is a separate static snapshot, not a plant cohort. Both systems improve under these backgrounds, with a larger change for DACCS. These stacks group the existing activity contributions consistently for every year; they differ from the explicit 2025 BECCS foreground-step attribution on slide 4. Electricity and heat activities can contribute on either side of zero, including substitution effects; do not interpret one activity category as the complete foreground avoided-energy service. All retained activity contributions and the source Other remainder are included, and opposite signs are stacked separately. This adds a future background year, but still does not tell us when the project's individual emissions and removals occur.",
    ),
    dict(
        title="TRAILS: matrices and supply chains through time",
        phase="03 / Annual backgrounds and temporal routing",
        seconds=50,
        notes="Introduce TRAILS: Temporal Routing and Aggregation of Impacts across Life-cycle Systems. On the left, premise supplies scenario-year snapshots. TRAILS interpolates annual technosphere A and biosphere B matrices: the third dimension is year. A links activities and products; B links activities and elementary flows. On the right, temporal distributions turn exchanges into demands and emissions in particular years. Each graph node is an activity in a calendar year; depth runs downward and years run horizontally. This is the schematic from the longer talk, not a BECCS or DACCS result. Explicit routing stops at a selected frontier, and remaining demand is still solved using annual background matrices; it is not discarded. Outside the scenario horizon, available endpoint backgrounds are used while the actual inventory dates are retained. The output keeps activity, elementary flow and year, ready for annual characterization or climate modelling of the dated gas inventory. Spend 50 seconds, then show the plant-cohort timelines and results.",
    ),
    dict(
        title="When do emissions and CO₂ removals occur?",
        phase="03 / Time-explicit LCA for plants operating in 2030–2049",
        seconds=60,
        notes="Move to complete plants commissioned in 2030. Construction is in 2027–2029, operation in 2030–2049, and end-of-life in 2050. TRAILS combines dated foreground and background exchanges with annual scenario matrices. Every BECCS harvest has an 83-year replacement-stand regrowth tail, reaching 2132 for the final harvest. DACCS captures during operation. The stacked areas separate uptake, energy, CO₂ and stack emissions, materials and other supply-chain contributions. Uptake contains forest regrowth and direct air capture. Energy includes biomass supply, electricity and compression, as well as avoided electricity and heat. The CO₂ and stack-emissions category contains the complete residual stack-emission branch and CO₂ transport losses; the branch-level GWP data do not separate individual stack gases. Materials includes chemicals, sorbent, construction and their end-of-life branches. Bundled pipeline/storage and remaining supply-chain branches stay in Other. Negative supply-chain values remain with their source category, so energy credits are not relabelled as uptake. Both panels start in 2000. The red line shows cumulative net GWP100 on each right-hand axis, accumulated over the full inventory including upstream contributions before 2000. Its endpoint closes to the cohort total. Both cases use the same annual and cumulative scales; zeros align between the axes. Cumulative GWP100 remains a sum of characterized inventory, not a climate-response trajectory. Small pre-operation DACCS contributions belong to upstream biogenic timing, not early DAC operation. These remain characterized inventories, not forcing trajectories.",
    ),
    dict(
        title="GWP100 does not distinguish emission dates, but radiative forcing does",
        phase="04 / Coupling temporal TRAILS inventories to the FaIR climate model",
        seconds=60,
        notes="GWP100 has a time horizon, but its standard factors are not indexed to the calendar date of each emission. Point to the coupling diagram: temporal TRAILS inventories provide annual emissions and removals, retaining the individual gas and its calendar year. These flows are combined with the background scenario in the FaIR climate model to calculate time-resolved radiative forcing. Use the FaIR trajectories to show the information lost in a single GWP total. FaIR evaluates a scenario with the project perturbation against the same scenario without it. The vertical axis is the change in global radiative forcing per physical lifetime net storage: positive values add forcing, negative values reduce it. DACCS gives an earlier reduction during operation; the modeled BECCS benefit builds with forest regrowth. Shading identifies operation. These are the existing median display trajectories from 841 calibrated configurations. We pass the dated gas inventory, not its CO₂-equivalent sum, to FaIR. A dated GWP inventory remains useful bookkeeping, but its sum cannot answer a fixed-calendar climate question. This is a limitation for the question being asked, not a claim that GWP100 is undefined.",
    ),
    dict(
        title="Comparing CDR with CO₂-pulse equivalents",
        phase="05 / Integrated radiative forcing relative to a dated CO₂ pulse",
        seconds=135,
        notes="Ask: what signed mass of a CO₂ pulse in 2030 gives the same integrated forcing over our chosen calendar window? Divide the system's integrated forcing by the response per kilogram of the reference pulse over exactly the same window. Negative values denote a removal-equivalent cooling benefit. The three handles select the window start, reference-pulse year and window end, in that order. The slider starts at 2000; defaults are 2020, 2030 and 2100. Handles remain five years apart so the reference pulse stays strictly inside the window. At the default endpoint of 2100, the equivalents are about −429 for BECCS and −823 for DACCS. Move the endpoint to 2300: about −1051 and −895. Changing the window start or pulse year updates the curve, values and endpoint comparison together. The comparison changes with the window. Ratios are calculated separately for all 841 configurations and then summarized; they are not ratios of the plotted median curves. This is a dated metric of integrated forcing, not physical tonnes stored or an identical climate trajectory. In a PDF, use the two endpoint rows already visible beneath the chart. Answer the research question using the endpoint comparison: here the ranking depends on the assessment window. Keep the forcing curve alongside the scalar, then move to the next slide for the conclusions and contact details.",
    ),
    dict(
        title="Conclusions",
        phase="06 / Time-explicit LCA for CDR",
        seconds=30,
        notes="Start with the two methodological steps: prospective LCA better represents future operating conditions and anticipates system-wide changes; dynamic LCA reveals how impacts unfold over long-lived operations in a rapidly changing system. Then connect these steps to the results: future supply chains and emission timing can change the comparison between BECCS and DACCS; radiative forcing shows when climate effects occur; CO₂-pulse equivalents account for timing while expressing the result in a mass unit. State the scenario, reference-pulse year and assessment window. The framed comparison scales the time-explicit cohort scores to a −1 tonne target: BECCS needs 1.02 net tonnes stored for −1 t CO₂-eq and 2.33 for −1 t CO₂-pulse-eq; DACCS needs 1.10 and 1.21 respectively. GWP100 uses the full temporal cohort; pulse equivalence uses the default 2020–2100 window and 2030 reference pulse. Amounts are −1000 kg-equivalent divided by each per-net-tonne score, using linear scaling of the existing results. They refer to atmospheric CO₂ reaching storage after transport loss, not gross capture or gross forest uptake. Thank the audience, then show the final sources slide. Backup material follows only through the backup control.",
    ),
    dict(
        title="Data sources and model versions",
        phase="References / Inventory data, methods and software",
        seconds=0,
        notes="All case-study values are read directly from the reviewed lca_time artifacts in this repository. The SETAC app adds presentation views only; it does not rerun or change the LCA or FaIR model. The longer presentation has the detailed inventories and attribution views. This is the final main slide and is included in the default PDF export. Keep it available for questions without adding a separate speaking segment.",
    ),
]
CORE_COUNT = len(SLIDES)
BACKUPS = [
    dict(
        title="Functional unit, reference systems and timing",
        phase="Backup / Assumptions used in the comparison",
        seconds=0,
        notes="These are the assumptions of the reused LCA-through-time results. The reference forest remains at constant mature carbon stock; shared pre-decision forest history cancels. Upstream timing can precede commissioning. Pulse-equivalence controls span 2000–2300; the defaults are a 2020 window start, a 2030 reference pulse and a 2100 endpoint. Ratios are taken configuration by configuration. The temporal inventory extends to 1882; the stored FaIR response starts in 1940.",
    ),
    dict(
        title="BECCS sensitivity to additional forest-carbon losses",
        phase="Backup / Illustrative 10% correction to regrowth uptake",
        seconds=0,
        notes="This is the existing presentation-level screen, not a recalculated forest model. It adds a positive correction equal to 10% of modeled gross regrowth to the routed BECCS GWP score. It is illustrative and not propagated into the FaIR or pulse-equivalence results because a site-specific magnitude and temporal profile are unavailable. Do not use it to qualify the displayed climate trajectories numerically.",
    ),
]
ALL_SLIDES = SLIDES + BACKUPS


def text(value, className=""):
    return html.P(value, className=className)


def shared_image(filename, alt, className=""):
    return html.Img(
        src=os.getenv("SETAC_2026_REQUESTS_PREFIX", "/") + "shared/" + filename,
        alt=alt,
        className=className,
    )


def callout(value):
    return html.Div(value, className="callout")


def graph(figure, identifier=None):
    props = dict(
        figure=figure,
        config={"displayModeBar": False, "responsive": True},
        responsive=True,
        className="chart",
        style={"height": "100%", "width": "100%"},
    )
    if identifier:
        props["id"] = identifier
    return dcc.Graph(**props)


def step(number, title, detail, logo=None):
    return html.Div(
        [
            logo if logo is not None else html.Span(number, className="step-number"),
            html.Div([html.H3(title), text(detail)]),
        ],
        className="story-step",
    )


def case_key():
    return html.Div(
        [html.Span(case, className=f"case-key {case.lower()}") for case in CASES],
        className="case-keys",
    )


def score_card(case, value, unit):
    return html.Div(
        [
            html.Span(case, className="small-label"),
            html.Strong(f"{value:,.0f}", className="score"),
            html.Span(unit, className="score-unit"),
        ],
        className=f"score-card {case.lower()}",
    )


def pulse_cards(end, *, start=WINDOW_START, reference=REFERENCE_YEAR):
    return [
        score_card(
            case,
            pulse_value(case, end, start=start, reference=reference),
            "kg CO₂ pulse-eq / net t stored",
        )
        for case in CASES
    ]


def pulse_configuration(start, reference, end):
    return [
        text(f"Reference pulse: {reference}", "emphasis"),
        text(f"Window: {start}–{end}", "muted"),
    ]


def pulse_window_labels(start, reference, end):
    return [
        html.Span(f"{label}: {year}", className=f"window-{key}")
        for label, key, year in (
            ("Start", "start", start),
            ("CO₂ pulse", "reference", reference),
            ("End", "end", end),
        )
    ]


def pulse_comparison(start=WINDOW_START, reference=REFERENCE_YEAR):
    rows = [html.Tr([html.Th("Window end"), html.Th("BECCS"), html.Th("DACCS")])]
    for year in (2100, 2300):
        rows.append(
            html.Tr(
                [html.Td(str(year))]
                + [
                    html.Td(
                        (
                            f"{pulse_value(case, year, start=start, reference=reference):,.0f}"
                            if year > reference
                            else "—"
                        ),
                        className=f"{case.lower()}-text",
                    )
                    for case in CASES
                ]
            )
        )
    note = "\n—: endpoint must follow the pulse." if reference >= 2100 else ""
    return [
        html.Table(rows),
        text(
            f"kg CO₂ pulse-eq / net t stored\nStart: {start} · CO₂ pulse: {reference}"
            + note,
            "source",
        ),
    ]


def pulse_takeaway(start=WINDOW_START, reference=REFERENCE_YEAR):
    if reference >= 2100:
        headline = "The 2100 endpoint precedes the reference pulse."
    else:
        winners = [
            min(
                CASES,
                key=lambda case: pulse_value(
                    case, end, start=start, reference=reference
                ),
            )
            for end in (2100, 2300)
        ]
        headline = (
            f"{winners[0]} ranks first to 2100; {winners[1]} to 2300."
            if winners[0] != winners[1]
            else f"{winners[0]} has the lower equivalent at both endpoints."
        )
    return [
        html.Strong(headline),
        text(
            "Report the scenario, reference-pulse year and assessment window with each result."
        ),
    ]


def _cover():
    # Use the same cover composition and artwork as lca_time.
    return [
        html.Div(
            [
                html.Div(
                    "SETAC Europe · Bruges · 19 October 2026", className="cover-kicker"
                ),
                html.H1(TITLE),
                html.P(
                    "Time-Explicit Life Cycle Assessment Linked to Prospective Background Scenarios and Climate Emulator",
                    className="cover-subtitle",
                ),
            ],
            className="cover-copy",
        ),
        shared_image(
            "cover-iam-trajectories.svg",
            "REMIND-EU global CO₂ emissions and temperature pathways for SSP2-NPi and SSP2-PkBudg1000.",
            "cover-iam-background",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.A(
                            "Romain Sacchi",
                            href="mailto:romain.sacchi@psi.ch",
                            className="presenter-link",
                        ),
                        ", Tom Terlouw, Karin Treyer, Alvaro Hahn Menacho, Arthur Jakobs and Christian Bauer",
                    ],
                    className="cover-authors",
                ),
                html.Span("1.01.T01 · 14:05 · Foyer 3", className="cover-session"),
            ],
            className="presenter-line",
        ),
    ]


def _research_question():
    return html.Div(
        [
            callout(
                [
                    html.Strong("Compare BECCS and DACCS for "),
                    "1 net tonne of atmospheric CO₂ stored after transport loss",
                ]
            ),
            html.Figure(
                shared_image(
                    "case-pathways.svg",
                    "BECCS and DACCS carbon pathways leading to permanent geological storage.",
                ),
                className="case-system-map setac-case-map",
            ),
            html.Div(
                [
                    step("01", "Current static LCA", "2025 supply chains"),
                    step("02", "Prospective static LCA", "2030 and 2050 supply chains"),
                    step(
                        "03", "Time-explicit LCA", "Emission dates and climate response"
                    ),
                ],
                className="question-steps",
            ),
        ],
        className="stack question-stack",
    )


def _systems():
    return html.Div(
        [
            callout(
                [
                    html.Strong("Material, energy and CO₂ flows · "),
                    "per 1 net tonne of CO₂ stored after transport loss",
                ]
            ),
            html.Figure(
                html.Img(
                    src=os.getenv("SETAC_2026_REQUESTS_PREFIX", "/")
                    + "system-flows.svg",
                    alt="BECCS: wood chips, capture heat, chemicals and water; exported electricity and heat. DACCS: sorbent and electricity for capture and heat-pump heat. Both routes capture 1.029 tonnes of CO₂, lose 0.029 tonnes in transport and store 1 tonne.",
                ),
                className="systems-flow-map",
            ),
            text(
                "2025 · Northern Europe · Selected operating flows; life-cycle GHG impacts follow on the next slide.\nBECCS reference: forest left standing + equivalent market electricity and heat. CHP = combined heat and power; COP = coefficient of performance.",
                "source",
            ),
        ],
        className="stack systems-stack",
    )


def _static():
    return html.Div(
        [
            html.Div(
                [
                    graph(static_figure()),
                    text(
                        "Stacks: emissions above zero; uptake and credits below. ◇ Net GWP100 = sum of all contributions.",
                        "source",
                    ),
                ],
                className="chart-stack",
            ),
            callout(
                (
                    f"BECCS: {static_score('BECCS'):,.0f}; "
                    f"DACCS: {static_score('DACCS'):,.0f} kg CO₂-eq per net tonne stored."
                ).replace("-", "−")
            ),
            text(
                "2025 · Northern Europe · IPCC 2021 GWP100 including biogenic CO₂ · per net tonne stored after transport loss.\nBECCS: new CHP + CCS vs standing forest and equivalent market energy. DACCS: solid sorbent, grid electricity and heat-pump heat.",
                "source",
            ),
        ],
        className="stack static-stack",
    )


def _premise(print_mode):
    scenario = (
        html.Span(
            "Mixes: SSP2-PkBudg1000 · Northern Europe (ENC)", className="print-setting"
        )
        if print_mode
        else dcc.RadioItems(
            id="mix-pathway",
            options=[
                {"label": "NPi · policies in place", "value": PATHWAYS[0]},
                {"label": "PkBudg1000 · carbon budget", "value": PATHWAYS[1]},
            ],
            value=PATHWAYS[1],
            inline=True,
            className="segmented",
        )
    )
    material = (
        html.H3("Steel")
        if print_mode
        else dcc.Dropdown(
            id="mix-material-sector",
            options=["Steel", "Cement clinker", "Truck transport"],
            value="Steel",
            clearable=False,
            searchable=False,
            className="mix-sector-select",
        )
    )
    context_controls = (
        html.Div(
            [html.H3("GMST"), html.Span("World", className="print-setting")],
            className="context-controls",
        )
        if print_mode
        else html.Div(
            [
                dcc.Dropdown(
                    id="context-indicator",
                    options=[
                        {"label": "GMST", "value": "GMST"},
                        {"label": "CO₂ emissions", "value": "CO2"},
                        {"label": "Population", "value": "Population"},
                    ],
                    value="GMST",
                    clearable=False,
                    searchable=False,
                    className="mix-sector-select",
                ),
                dcc.Dropdown(
                    id="context-region",
                    options=[
                        {"label": "World", "value": "World"},
                        {"label": "Northern Europe", "value": "ENC", "disabled": True},
                    ],
                    value="World",
                    clearable=False,
                    searchable=False,
                    className="mix-sector-select",
                ),
            ],
            className="context-controls",
        )
    )
    context_panel = html.Div(
        [
            context_controls,
            graph(scenario_context_figure(), None if print_mode else "context-chart"),
            html.P(
                scenario_context_note("GMST", "World"),
                className="source context-note",
                **({} if print_mode else {"id": "context-note"}),
            ),
        ],
        className="chart-stack context-panel",
    )
    panels = []
    for sector, label, identifier in (
        ("Electricity", "Electricity", "mix-electricity"),
        ("District heat", "Heat supply", "mix-heat"),
        ("Steel", "Steel", "mix-material"),
    ):
        panels.append(
            html.Div(
                [
                    material if sector == "Steel" else html.H3(label),
                    graph(mix_figure(sector), None if print_mode else identifier),
                ],
                className="chart-stack mix-panel",
            )
        )
    return html.Div(
        [
            html.Div(
                [
                    step(
                        "IAM",
                        "REMIND-EU scenarios",
                        "Integrated assessment model · SSP2",
                        logo=shared_image(
                            "pik-logo.png",
                            "Potsdam Institute for Climate Impact Research (PIK)",
                            "workflow-logo workflow-logo-pik",
                        ),
                    ),
                    step(
                        "→",
                        "premise",
                        "Updates mixes, efficiency and emissions",
                        logo=shared_image(
                            "premise-logo.png", "premise", "workflow-logo"
                        ),
                    ),
                    step(
                        "→",
                        "Prospective ecoinvent",
                        "Northern Europe (ENC) · 2025–2050",
                    ),
                ],
                className="setac-premise-workflow",
            ),
            html.Div(
                [
                    html.Strong("IAM scenarios and Northern European supply mixes"),
                    scenario,
                ],
                className="control-row mix-controls",
            ),
            html.Div(
                [context_panel, html.Div(panels, className="mix-panels")],
                className="premise-panels",
            ),
            text(
                "Conditional scenarios, not forecasts · ENC market shares sum to 100%. Routes below 1% in every snapshot: Other. Electricity: high voltage. Heat: combined district/industrial market.",
                "source",
            ),
        ],
        className="stack premise-stack",
    )


def _prospective():
    return html.Div(
        [
            html.Div(
                [
                    html.Strong("GWP100 contributions by background year and scenario"),
                    html.Div(
                        [
                            html.Span(
                                [html.I(className="pattern-key hatched"), "NPi · left"]
                            ),
                            html.Span(
                                [html.I(className="pattern-key"), "PkBudg1000 · right"]
                            ),
                        ],
                        className="scenario-patterns",
                    ),
                ],
                className="control-row",
            ),
            html.Div(
                [
                    graph(prospective_figure()),
                    text(
                        "Signed activity contributions, grouped consistently across years · ◇ net GWP100 · same physical storage service",
                        "source",
                    ),
                ],
                className="chart-stack",
            ),
            callout(
                "The GWP100 score improves more for DACCS as supply chains change."
            ),
        ],
        className="stack prospective-stack",
    )


def _trails():
    prefix = os.getenv("SETAC_2026_REQUESTS_PREFIX", "/")
    return html.Div(
        [
            html.Div(
                [
                    shared_image("trails-logo.png", "TRAILS", "trails-intro-logo"),
                    text(
                        "TRAILS combines annual background matrices with the dates of individual exchanges."
                    ),
                ],
                className="trails-intro",
            ),
            html.Div(
                [
                    html.Article(
                        [
                            html.H3("1 · Stack A and B by year"),
                            text(
                                "Interpolate between the scenario snapshots supplied by premise."
                            ),
                            html.Img(
                                src=prefix + "assets/trails-annual-matrices.svg",
                                alt="Three-dimensional technosphere A: activity × product × year; biosphere B: activity × elementary flow × year.",
                            ),
                            text(
                                "Each slice describes the background supply system in year y.",
                                "trails-card-note",
                            ),
                        ],
                        className="trails-method-card",
                    ),
                    html.Article(
                        [
                            html.H3("2 · Route each exchange to its year"),
                            text(
                                "Follow demand through the supply graph, using exchange timing."
                            ),
                            html.Img(
                                src=prefix + "assets/trails-temporal-routing.svg",
                                alt="Schematic supply graph with activity–year nodes. Depth increases downward, calendar year runs to the right, and stopped branches remain background demands.",
                            ),
                            text(
                                "When routing stops, solve the remaining demand with A(y) and B(y).",
                                "trails-card-note",
                            ),
                        ],
                        className="trails-method-card",
                    ),
                ],
                className="trails-method-panels",
            ),
            callout(
                "Result: an inventory by activity, elementary flow and year → annual LCA or climate response."
            ),
        ],
        className="stack trails-stack",
    )


def _temporal():
    return html.Div(
        [
            html.Div(
                [
                    html.Div([html.Strong(year), html.Span(label)])
                    for year, label in (
                        ("2027–2029", "Construction"),
                        ("2030–2049", "Operation"),
                        ("2050", "End-of-life"),
                        ("→ 2132", "Final BECCS regrowth tail"),
                    )
                ],
                className="timeline",
            ),
            graph(temporal_figure()),
            callout(
                "TRAILS assigns exchanges to years and uses each year's background supply chains."
            ),
            text(
                "2030 cohorts · SSP2-PkBudg1000 · GWP100 per lifetime net tonne stored. Uptake: forest regrowth and DAC. Energy includes avoided supply; supply-chain categories retain upstream biogenic uptake. Red line: cumulative net GWP100 (right axis), including contributions before the 2000 view start.",
                "source",
            ),
        ],
        className="stack temporal-stack",
    )


def _gwp():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Emission and removal in 2030"),
                            html.Strong("0 kg CO₂-eq", className="zero"),
                            html.Div(
                                [
                                    html.Span("+1 t CO₂ · 2030", className="emission"),
                                    html.Span("−1 t CO₂ · 2030", className="removal"),
                                ],
                                className="pulse-pair",
                            ),
                        ],
                        className="timing-example",
                    ),
                    html.Div(
                        [
                            html.Span("Emission in 2030, removal in 2080"),
                            html.Strong("0 kg CO₂-eq", className="zero"),
                            html.Div(
                                [
                                    html.Span("+1 t CO₂ · 2030", className="emission"),
                                    html.Span("50 years →", className="delay"),
                                    html.Span("−1 t CO₂ · 2080", className="removal"),
                                ],
                                className="pulse-pair",
                            ),
                            text("Positive forcing persists before the removal."),
                        ],
                        className="timing-example delayed",
                    ),
                    text(
                        "Illustrative CO₂-only schedules; these are not the BECCS and DACCS inventories.",
                        "source",
                    ),
                ],
                className="timing-examples",
            ),
            html.Div(
                [
                    html.H2("Same GWP100 score, different radiative forcing"),
                    text(
                        "Standard GWP100 applies the same factor regardless of the emission date."
                    ),
                    callout(
                        "Annual gas emissions and removals → FaIR → radiative forcing"
                    ),
                    text(
                        "Pass the individual gases and their dates to FaIR.", "emphasis"
                    ),
                    html.A(
                        "IPCC AR6 WG I, §7.6 · emission metrics",
                        href="https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/",
                        target="_blank",
                        className="source",
                    ),
                ],
                className="narrative",
            ),
        ],
        className="split equal",
    )


def _forcing(print_mode):
    controls = (
        html.Span("Full response through 2300", className="print-setting")
        if print_mode
        else dcc.RadioItems(
            id="forcing-horizon",
            options=[
                {"label": "Through 2140", "value": 2140},
                {"label": "Through 2300", "value": 2300},
            ],
            value=2300,
            inline=True,
            className="segmented",
        )
    )
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("TRAILS"),
                                    html.Span("Emissions and removals by gas and year"),
                                ],
                                className="forcing-pipeline-node",
                            ),
                            html.Span(
                                "→",
                                className="forcing-pipeline-arrow",
                                **{"aria-hidden": "true"},
                            ),
                            html.Div(
                                [
                                    html.Strong("FaIR"),
                                    html.Span("Climate model + background scenario"),
                                ],
                                className="forcing-pipeline-node",
                            ),
                            html.Span(
                                "→",
                                className="forcing-pipeline-arrow",
                                **{"aria-hidden": "true"},
                            ),
                            html.Div(
                                [
                                    html.Strong("Radiative forcing"),
                                    html.Span("Climate response over time"),
                                ],
                                className="forcing-pipeline-node",
                            ),
                        ],
                        className="forcing-pipeline",
                        role="group",
                        **{
                            "aria-label": "Temporal TRAILS gas inventories feed the FaIR climate model to calculate radiative forcing over time"
                        },
                    ),
                    controls,
                ],
                className="control-row forcing-control-row",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            graph(
                                forcing_figure(),
                                None if print_mode else "forcing-chart",
                            ),
                        ],
                        className="chart-stack",
                    ),
                    html.Div(
                        [
                            html.H2("TRAILS inventories → FaIR"),
                            html.P(
                                "We feed the annual TRAILS emissions and removals into FaIR, preserving each gas and its timing."
                            ),
                            html.P(
                                [
                                    html.Strong("DACCS: "),
                                    "earlier forcing reduction during operation.",
                                ],
                                className="daccs-text",
                            ),
                            html.P(
                                [
                                    html.Strong("BECCS: "),
                                    "the modeled benefit builds with forest regrowth.",
                                ],
                                className="beccs-text",
                            ),
                            callout(
                                "Negative Δ forcing means a cooling influence relative to the scenario."
                            ),
                            text(
                                "SSP2-PkBudg1000 · median display trajectories · 841 FaIR configurations",
                                "source",
                            ),
                        ],
                        className="narrative forcing-narrative",
                    ),
                ],
                className="split chart-first",
            ),
        ],
        className="stack",
    )


def _pulse(print_mode):
    controls = (
        html.Div(
            pulse_window_labels(WINDOW_START, REFERENCE_YEAR, DEFAULT_END),
            className="window-labels print-setting",
        )
        if print_mode
        else html.Div(
            [
                html.Div(
                    pulse_window_labels(WINDOW_START, REFERENCE_YEAR, DEFAULT_END),
                    id="pulse-window-labels",
                    className="window-labels",
                ),
                dcc.RangeSlider(
                    id="pulse-window",
                    min=WINDOW_MIN,
                    max=2300,
                    step=5,
                    value=[WINDOW_START, REFERENCE_YEAR, DEFAULT_END],
                    allowCross=False,
                    pushable=5,
                    updatemode="drag",
                    marks={
                        2000: "2000",
                        2050: "2050",
                        2100: "2100",
                        2200: "2200",
                        2300: "2300",
                    },
                    tooltip={"placement": "top", "always_visible": False},
                ),
            ],
            className="slider-control",
        )
    )
    return html.Div(
        [
            html.Div(
                [
                    html.H2("CO₂ pulse mass with the same integrated forcing"),
                    html.Div(
                        [
                            html.Span("System forcing integrated over the window"),
                            html.Hr(),
                            html.Span(
                                "Forcing per kg of a CO₂ pulse over the same window"
                            ),
                        ],
                        className="equation",
                    ),
                    html.Div(
                        pulse_configuration(WINDOW_START, REFERENCE_YEAR, DEFAULT_END),
                        **({} if print_mode else {"id": "pulse-configuration"}),
                    ),
                    html.Div(
                        pulse_cards(DEFAULT_END),
                        **({} if print_mode else {"id": "pulse-values"}),
                        className="pulse-values",
                    ),
                    html.Div(
                        pulse_takeaway(),
                        **({} if print_mode else {"id": "pulse-takeaway"}),
                        className="callout pulse-takeaway",
                    ),
                ],
                className="pulse-concept",
            ),
            html.Div(
                [
                    graph(pulse_figure(), None if print_mode else "pulse-chart"),
                    controls,
                    html.Div(
                        pulse_comparison(),
                        **({} if print_mode else {"id": "pulse-comparison"}),
                        className="endpoint-comparison",
                    ),
                ],
                className="pulse-results",
            ),
        ],
        className="pulse-layout",
    )


def _closing_removal_table():
    amounts = {case: removal_requirements(case) for case in CASES}
    return html.Div(
        [
            html.H3("CO₂ storage needed for each climate target"),
            text(
                "Life-cycle GHG emissions are included in both target scores.",
                "removal-unit",
            ),
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [html.Th("Target score", scope="col")]
                            + [html.Th(case, scope="col") for case in CASES]
                        )
                    ),
                    html.Tbody(
                        [
                            html.Tr(
                                [html.Th(label, scope="row")]
                                + [
                                    html.Td(f"{amounts[case][metric]:.2f} t")
                                    for case in CASES
                                ]
                            )
                            for metric, label in (
                                ("gwp100", "−1 t CO₂-eq · GWP100"),
                                ("pulse", "−1 t CO₂-pulse-eq"),
                            )
                        ]
                    ),
                ],
                **{
                    "aria-label": "CO₂ storage required for a minus-one-tonne life-cycle climate score"
                },
            ),
            text(
                "Amounts: t CO₂ stored after transport loss · target ÷ score\n2030 cohorts · SSP2-PkBudg1000\nPulse: 2020–2100 window; 2030 reference year.",
                "removal-basis",
            ),
        ],
        className="closing-removal-frame",
    )


def _closing():
    return html.Div(
        [
            html.Div(
                [
                    html.Ul(
                        [
                            html.Li(
                                [
                                    "Moving from ",
                                    html.Strong("current to prospective LCA"),
                                    " better represents future operating conditions and anticipates system-wide changes.",
                                ]
                            ),
                            html.Li(
                                [
                                    "Moving from ",
                                    html.Strong("static to dynamic LCA"),
                                    " reveals how impacts unfold over long-lived operations in a rapidly changing system.",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong(
                                        "Future supply chains and emission timing"
                                    ),
                                    " can change the ranking of BECCS and DACCS.",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Radiative forcing"),
                                    " shows when climate effects occur; a GWP100 total does not.",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("CO₂-pulse equivalents"),
                                    " express climate effects as a CO₂ mass for a stated scenario, reference year and assessment window.",
                                ]
                            ),
                        ],
                        className="closing-takeaways",
                    ),
                    _closing_removal_table(),
                ],
                className="closing-summary",
            ),
            html.Div(
                [
                    html.H2("Thank you"),
                    html.P("Romain Sacchi", className="closing-name"),
                    html.Address(
                        [
                            html.P("Laboratory for Energy Systems Analyses"),
                            html.P("Paul Scherrer Institute (PSI)"),
                            html.A(
                                "romain.sacchi@psi.ch",
                                href="mailto:romain.sacchi@psi.ch",
                            ),
                        ]
                    ),
                ],
                className="closing-contact",
            ),
        ],
        className="closing-layout",
    )


def _accounting():
    return html.Div(
        [
            html.Div(
                [
                    html.H2("Functional unit and reference systems"),
                    text(
                        "Denominator: atmospheric CO₂ reaching geological storage after transport loss. Supply-chain GHG emissions remain in the climate-impact numerator."
                    ),
                    text(
                        "BECCS: new CHP + CCS versus a mature forest at constant carbon stock and equivalent Northern European market electricity and heat. Shared pre-decision forest history cancels."
                    ),
                    text(
                        "DACCS: solid sorbent, grid electricity and heat-pump heat; 100 kt CO₂/year capture capacity."
                    ),
                ],
                className="backup-card",
            ),
            html.Div(
                [
                    html.H2("Plant lifetime, forest regrowth and FaIR settings"),
                    text(
                        "Construction: 2027–2029. Operation: 2030–2049. End-of-life: 2050. Every BECCS harvest starts 83 years of replacement-stand regrowth; the final tail ends in 2132."
                    ),
                    text(
                        "Generic upstream distributions can predate commissioning. Temporal inventories begin as early as 1882. The stored FaIR response spans 1940–2300. Pulse-equivalence controls span 2000–2300, defaulting to a 2020–2100 window and a 2030 reference pulse."
                    ),
                    text(
                        "Pulse equivalents use the same scenario and window for system and reference. For each FaIR configuration: integrate, divide by the per-kg pulse response, then take the ensemble median."
                    ),
                ],
                className="backup-card",
            ),
        ],
        className="two-columns",
    )


def _sensitivity():
    values = results.forest_pool_sensitivity("routed")
    return html.Div(
        [
            text(
                "Additional CO₂ from post-harvest residues, roots and soil: an illustrative correction to the baseline.",
                "emphasis",
            ),
            html.Div(
                [
                    score_card(
                        "BECCS",
                        values["baseline_beccs"],
                        "baseline · kg CO₂-eq / net t stored",
                    ),
                    score_card(
                        "BECCS",
                        values["stress_test_beccs"],
                        "10% regrowth correction · kg CO₂-eq / net t",
                    ),
                    score_card(
                        "DACCS",
                        values["comparator_daccs"],
                        "comparison · kg CO₂-eq / net t stored",
                    ),
                ],
                className="three-columns",
            ),
            callout(
                f"The routed GWP100 ranking changes at a correction of {values['break_even_fraction']:.1%} of modeled gross regrowth."
            ),
            text(
                "The 10% correction is illustrative, not calibrated. It is not propagated into FaIR or pulse equivalence: a site-specific magnitude and time profile are unavailable."
            ),
        ],
        className="stack",
    )


REFERENCES = [
    ("premise · Sacchi et al. (2022)", "https://doi.org/10.1016/j.rser.2022.112311"),
    ("Dynamic LCA · Levasseur et al. (2010)", "https://doi.org/10.1021/es9030003"),
    (
        "Emission metrics · IPCC AR6 WG I, §7.6",
        "https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/",
    ),
    ("FaIR · Leach et al. (2021)", "https://doi.org/10.5194/gmd-14-3007-2021"),
    (
        "TRAILS · Sacchi et al. (2026), preprint",
        "https://www.researchsquare.com/article/rs-10139523/v1",
    ),
    (
        "DAC inventory · Deutz & Bardow (2021)",
        "https://doi.org/10.1038/s41560-020-00771-9",
    ),
    ("DAC energy · Qiu et al. (2022)", "https://doi.org/10.1038/s41467-022-31146-1"),
    (
        "CO₂ transport · Terlouw et al. (2021)",
        "https://doi.org/10.1021/acs.est.1c03263",
    ),
]


def _sources():
    return html.Div(
        [
            html.Ul(
                [
                    html.Li(html.A(label, href=url, target="_blank"))
                    for label, url in REFERENCES
                ],
                className="references",
            ),
            html.Div(
                [
                    html.H2("Databases, scenarios and software"),
                    text("ecoinvent 3.12 cutoff · REMIND-EU · Northern Europe"),
                    text(
                        "Static: SSP2-NPi and SSP2-PkBudg1000. Temporal and FaIR: SSP2-PkBudg1000; 2030 plant cohorts."
                    ),
                    text(
                        "premise 2.4.9.1 · TRAILS 1.0.1 · FaIR ensemble: 841 calibrated configurations"
                    ),
                    text(
                        "Source: LCA-through-time processed artifacts. Values and model assumptions are reused without recalculation."
                    ),
                    text(
                        "The forest sensitivity is a separate presentation-level screen. It does not modify any of the source result files.",
                        "source",
                    ),
                ],
                className="backup-card",
            ),
        ],
        className="two-columns",
    )


def render_slide(index, *, print_mode=False):
    index = int(index)
    if not 0 <= index < len(ALL_SLIDES):
        raise IndexError(index)
    meta = ALL_SLIDES[index]
    renderers = [
        _cover,
        _research_question,
        _systems,
        _static,
        lambda: _premise(print_mode),
        _prospective,
        _trails,
        _temporal,
        lambda: _forcing(print_mode),
        lambda: _pulse(print_mode),
        _closing,
        _sources,
        _accounting,
        _sensitivity,
    ]
    label = (
        f"{index + 1:02d} / {CORE_COUNT:02d}"
        if index < CORE_COUNT
        else f"Backup {index - CORE_COUNT + 1} / {len(BACKUPS)}"
    )
    if index == 0:
        children = _cover()
    else:
        children = [
            html.Div(
                [
                    html.Div(meta["phase"], className="slide-eyebrow"),
                    html.H1(meta["title"]),
                ],
                className="slide-heading",
            ),
            html.Div(renderers[index](), className="slide-body"),
        ]
    children.append(html.Div(label, className="slide-number"))
    if print_mode:
        children.append(
            html.Img(
                src=os.getenv("SETAC_2026_REQUESTS_PREFIX", "/")
                + "assets/setac-logo.svg",
                alt="SETAC — Society of Environmental Toxicology and Chemistry",
                className="setac-print-logo",
            )
        )
    return html.Section(
        children,
        className=f"slide setac-slide setac-slide-{index + 1}"
        + (" cover-slide" if index == 0 else ""),
        **{"data-slide": index, "aria-label": f"{label}: {meta['title']}"},
    )
