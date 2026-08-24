from __future__ import annotations

from collections.abc import Iterable
import json
from math import isfinite
from pathlib import Path

from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import (
    APPENDIX_SLIDE_COUNT,
    APPENDIX_START_SLIDE,
    CORE_SLIDE_COUNT,
    SLIDE_TITLES,
    chapter_for_slide,
)
from .results import (
    cohort_co2_pulse_equivalent,
    cohort_fair_response_series,
    cohort_fair_total_series,
    cohort_temporal_score_series,
    cohort_temporal_total,
    co2_reference_pulse_series,
    forest_pool_sensitivity,
    gross_storage_per_net_tonne,
    lifetime_annual_series,
    lifetime_net_storage_tonnes,
    lifetime_process_contributions,
    lifetime_score_per_net_tonne,
    net_removal_scale,
    process_step_attribution,
    scenario_sector_mix,
    scenario_sector_series,
    static_activity_contributions_per_net_tonne,
    static_score,
)
from .system_inventory import case_inventory


def _tag(text: str, tone: str = "blue"):
    return html.Span(text, className=f"tag tag-{tone}")


def _card(title: str, body, *, accent: str = "blue", kicker: str | None = None):
    children = []
    if kicker:
        children.append(html.Div(kicker, className="card-kicker"))
    children.extend([html.H3(title), body])
    return html.Article(children, className=f"content-card accent-{accent}")


def _bullets(items: Iterable[str]):
    return html.Ul([html.Li(item) for item in items], className="clean-list")


def _lens_visual(asset: str, alt: str, caption: str):
    return html.Figure(
        [
            html.Img(src=f"assets/{asset}", alt=alt),
            html.Figcaption(caption),
        ],
        className="lens-diagram",
    )


def _reading_list(items: Iterable[tuple[str, str, str]]):
    return html.Div(
        [
            html.Div("Further reading", className="lens-reading-label"),
            html.Ul(
                [
                    html.Li(
                        html.A(
                            label,
                            href=url,
                            title=title,
                            target="_blank",
                            rel="noopener noreferrer",
                        )
                    )
                    for label, url, title in items
                ],
                className="lens-reading-list",
            ),
        ],
        className="lens-reading",
    )


def _flow(items: Iterable[tuple[str, str]]):
    nodes = []
    items = list(items)
    for position, (title, subtitle) in enumerate(items):
        nodes.append(
            html.Div([html.Strong(title), html.Span(subtitle)], className="flow-node")
        )
        if position < len(items) - 1:
            nodes.append(html.Div("→", className="flow-arrow"))
    return html.Div(nodes, className="flow-row")


def _result_placeholder(title: str, note: str):
    return html.Div(
        [
            html.Div(
                [
                    html.Span("Validated result slot", className="result-status"),
                    html.Strong(title),
                ],
                className="result-heading",
            ),
            html.Div(
                [
                    html.Div(className="placeholder-bar bar-one"),
                    html.Div(className="placeholder-bar bar-two"),
                    html.Div(className="placeholder-bar bar-three"),
                ],
                className="placeholder-chart",
            ),
            html.P(note),
        ],
        className="result-placeholder",
    )


def _format_score(value: float) -> str:
    return f"{value:,.0f}".replace("-", "−")


def _score_bar(
    label: str,
    score: float,
    tone: str,
    *,
    scale: float = 1300,
    value_label: str | None = None,
):
    width = min(abs(score) / scale * 100, 100)
    return html.Div(
        [
            html.Div(
                [
                    html.Strong(label),
                    html.Span(value_label or _format_score(score)),
                ],
                className="score-bar-label",
            ),
            html.Div(
                html.Div(
                    className=f"score-bar-fill result-{tone}",
                    style={"width": f"{width:.2f}%"},
                ),
                className="score-bar-track",
            ),
        ],
        className="score-bar-row",
    )


def _result_panel(title: str, body, *, kicker: str):
    return html.Article(
        [
            html.Div(
                [html.Span(kicker, className="result-kicker"), html.H3(title)],
                className="result-panel-heading",
            ),
            body,
        ],
        className="result-panel",
    )


def _slide_shell(index: int, body, *, eyebrow: str | None = None, lead=None):
    chapter = chapter_for_slide(index)
    return html.Section(
        [
            html.Div(
                [
                    html.Div(eyebrow or chapter["name"], className="slide-eyebrow"),
                    html.H1(SLIDE_TITLES[index]),
                    html.P(lead, className="slide-lead") if lead else None,
                ],
                className="slide-heading",
            ),
            html.Div(body, className="slide-body"),
        ],
        className=f"slide slide-{index}",
    )


def _cover():
    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        "Life Cycle Summer School · Malmö · 2026",
                        className="cover-kicker",
                    ),
                    html.H1("How time changes LCA results"),
                    html.P(
                        "When does modelling time change the comparison between BECCS and DACCS?",
                        className="cover-subtitle",
                    ),
                    html.Div(
                        [
                            _tag("present-day snapshot", "grey"),
                            _tag("future scenarios", "amber"),
                            _tag("dated climate effects", "teal"),
                        ],
                        className="tag-row",
                    ),
                ],
                className="cover-copy",
            ),
            html.Img(
                src="assets/cover-iam-trajectories.svg",
                className="cover-iam-background",
                alt=(
                    "REMIND-EU trajectories for global carbon dioxide emissions and "
                    "global mean surface temperature for SSP2-NPi and "
                    "SSP2-PkBudg1000."
                ),
            ),
            html.Div(
                [
                    html.A(
                        "Romain Sacchi",
                        href="mailto:romain.sacchi@psi.ch",
                        className="presenter-link",
                    ),
                    html.Span("Prospective LCA · Lecture 05"),
                ],
                className="presenter-line",
            ),
        ],
        className="slide cover-slide",
    )


def _package_slide(index: int):
    return _slide_shell(
        index,
        [
            html.Div(
                [
                    html.Div("Same comparison", className="lens-anchor"),
                    html.Div("→", className="engine-arrow"),
                    html.Div(
                        "Three treatments of time",
                        className="lens-statement",
                    ),
                ],
                className="lens-line",
            ),
            html.Div(
                [
                    _card(
                        "Conventional",
                        html.Div(
                            [
                                html.P(
                                    "Model every exchange using one present-day background."
                                ),
                                _lens_visual(
                                    "lens-conventional.svg",
                                    "A product system and all its flows represented in one present-day state.",
                                    "One system state · all flows treated as simultaneous",
                                ),
                                _reading_list(
                                    [
                                        (
                                            "Rebitzer et al. (2004) · LCA framework",
                                            "https://doi.org/10.1016/j.envint.2003.11.005",
                                            "Life cycle assessment: Part 1: framework, goal and scope definition, inventory analysis, and applications",
                                        ),
                                    ]
                                ),
                            ],
                            className="lens-card-body",
                        ),
                        accent="grey",
                        kicker="01 · What is the impact today?",
                    ),
                    _card(
                        "Prospective",
                        html.Div(
                            [
                                html.P(
                                    "Model the same system in a selected future scenario and year."
                                ),
                                _lens_visual(
                                    "lens-prospective.svg",
                                    "Scenario pathways define the background system for a future LCA snapshot.",
                                    "Scenario → future background → LCA snapshot",
                                ),
                                _reading_list(
                                    [
                                        (
                                            "Sacchi et al. (2022) · prospective databases",
                                            "https://doi.org/10.1016/j.rser.2022.112311",
                                            "PRospective EnvironMental Impact asSEment (premise): a streamlined approach to producing databases for prospective life cycle assessment using integrated assessment models",
                                        ),
                                    ]
                                ),
                            ],
                            className="lens-card-body",
                        ),
                        accent="amber",
                        kicker="02 · How could the impact change?",
                    ),
                    _card(
                        "Time-explicit",
                        html.Div(
                            [
                                html.P(
                                    "Date each emission and removal, then calculate its climate response through time."
                                ),
                                _lens_visual(
                                    "lens-time-explicit.svg",
                                    "Dated carbon exchanges translated into a time-dependent climate response.",
                                    "Dated exchanges → climate response through time",
                                ),
                                _reading_list(
                                    [
                                        (
                                            "Müller et al. (2025) · time-explicit framework",
                                            "https://doi.org/10.1007/s11367-025-02539-3",
                                            "Time-explicit life cycle assessment: a flexible framework for coherent consideration of temporal dynamics",
                                        ),
                                    ]
                                ),
                            ],
                            className="lens-card-body",
                        ),
                        accent="teal",
                        kicker="03 · When do the climate effects occur?",
                    ),
                ],
                className="three-column lens-cards",
            ),
            html.Button(
                "Full references: Appendix B →",
                id={"type": "chapter-button", "slide": APPENDIX_START_SLIDE + 1},
                n_clicks=0,
                className="appendix-link-button",
                title="Open Appendix B with the complete reference list",
            ),
        ],
        lead="The comparison is unchanged; only the treatment of time changes.",
    )


def _cases_slide(index: int, print_mode: bool = False):
    focus = "both"
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Span("Focus", className="focus-control-label"),
                        dcc.RadioItems(
                            options=[
                                {"label": "BECCS", "value": "beccs"},
                                {"label": "DACCS", "value": "daccs"},
                                {"label": "Both", "value": "both"},
                            ],
                            value=focus,
                            inline=True,
                            className="contribution-view-toggle focus-control",
                            **({} if print_mode else {"id": "case-focus-control"}),
                        ),
                    ],
                    className="teaching-focus-toolbar print-expanded-control",
                ),
                html.Figure(
                    html.Img(
                        src="assets/case-pathways.svg",
                        alt=(
                            "Two pathways from atmospheric carbon to a shared geological "
                            "store. The BECCS pathway passes through a forest, woodchips, "
                            "combined heat and power, and post-combustion capture. The "
                            "BECCS counterfactual leaves the existing mature forest "
                            "standing and supplies equivalent electricity and heat from "
                            "Northern European markets. The project harvests the forest, "
                            "builds a new CHP with CCS and regrows the stand. The "
                            "DACCS pathway passes through a solid-sorbent direct-air-capture "
                            "unit and carbon dioxide conditioning."
                        ),
                    ),
                    className="case-system-map",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "BECCS project decision",
                                    className="case-question-label",
                                ),
                                html.Strong(
                                    "Is building a biomass CHP plant with CCS preferable to leaving the mature forest standing and buying equivalent electricity and heat?"
                                ),
                            ],
                            className="case-question case-question-forest",
                        ),
                        html.Div(
                            [
                                html.Span(
                                    "DACCS energy-supply sensitivity",
                                    className="case-question-label",
                                ),
                                html.Strong(
                                    "Which electricity and heat supplies should power direct air capture?"
                                ),
                            ],
                            className="case-question case-question-sky",
                        ),
                    ],
                    className="case-model-questions",
                ),
            ],
            className=f"case-study-comparison focus-{focus}",
            **({} if print_mode else {"id": "case-focus-view"}),
        ),
        eyebrow="Case studies",
        lead="Both pathways store atmospheric CO₂ permanently, but they use different carbon sources and energy systems.",
    )


def _functional_unit_slide(index: int):
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Strong("1.029 t"),
                                        html.Span("gross capture"),
                                    ],
                                    className="functional-equation-term capture",
                                ),
                                html.Span(
                                    "−", className="functional-equation-operator"
                                ),
                                html.Div(
                                    [
                                        html.Strong("0.029 t"),
                                        html.Span("transport loss"),
                                    ],
                                    className="functional-equation-term loss",
                                ),
                                html.Span(
                                    "=", className="functional-equation-operator"
                                ),
                                html.Div(
                                    [
                                        html.Strong("1.000 t"),
                                        html.Span("net CO₂ stored"),
                                    ],
                                    className="functional-equation-term net",
                                ),
                            ],
                            className="functional-equation",
                        ),
                        html.Div(
                            [
                                _tag("same physical denominator", "blue"),
                                _tag("BECCS", "grey"),
                                _tag("DACCS", "teal"),
                            ],
                            className="functional-equation-tags",
                        ),
                    ],
                    className="functional-equation-hero",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "GWP100 numerator", className="reporting-kicker"
                                ),
                                html.Strong(
                                    "All life-cycle GHG emissions and atmospheric removals are scored separately."
                                ),
                            ],
                            className="functional-numerator-note",
                        ),
                        html.Button(
                            "Characterisation factors and flow definitions: Appendix A →",
                            id={
                                "type": "chapter-button",
                                "slide": APPENDIX_START_SLIDE,
                            },
                            n_clicks=0,
                            className="appendix-link-button",
                        ),
                    ],
                    className="functional-unit-footer",
                ),
            ],
            className="functional-unit-layout functional-unit-simplified",
        ),
        lead=(
            "The denominator is physical storage after transport loss; life-cycle GHGs affect the numerator only."
        ),
    )


def _inventory_fact(label: str, value: str, tone: str):
    return html.Div(
        [html.Span(label), html.Strong(value)],
        className=f"inventory-fact inventory-fact-{tone}",
    )


def _net_removal_balance(
    gross_capture_t: float,
    physical_loss_t: float,
    supply_chain_ghg_kg: float,
    *,
    capture_source: str = "captured from air",
):
    """Keep the physical carbon denominator separate from LCIA impacts."""
    return html.Div(
        [
            html.Span("Physical removal balance", className="inventory-balance-label"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong(f"{gross_capture_t:.3f} t CO₂"),
                            html.Small(capture_source),
                        ],
                        className="balance-term balance-storage",
                    ),
                    html.B("−", className="balance-operator"),
                    html.Div(
                        [
                            html.Strong(f"{physical_loss_t:.3f} t CO₂"),
                            html.Small("transport loss"),
                        ],
                        className="balance-term balance-ghg",
                    ),
                    html.B("=", className="balance-operator"),
                    html.Div(
                        [
                            html.Strong("1.000 t CO₂"),
                            html.Small("delivered to storage"),
                        ],
                        className="balance-term balance-net",
                    ),
                ],
                className="inventory-balance-equation",
            ),
            html.Small(
                f"Supply-chain processes add {supply_chain_ghg_kg:.0f} kg CO₂-eq "
                "to the GWP100 numerator but do not change this physical balance.",
                className="inventory-impact-note",
            ),
        ],
        className="inventory-fact inventory-balance",
        **{
            "aria-label": (
                f"{gross_capture_t:.3f} tonnes captured minus {physical_loss_t:.3f} "
                "tonnes physically lost equals 1.000 tonne delivered to storage; life-cycle "
                f"GHG impacts add {supply_chain_ghg_kg:.0f} kilograms CO2 equivalent"
            )
        },
    )


def _flow_legend(case: str):
    """Shared visual key for the two foreground system diagrams."""
    entries = (
        (
            ("Electricity + heat", "energy"),
            ("CO₂", "co2"),
            ("Sorbent + materials", "other"),
        )
        if case == "DACCS"
        else (
            ("Biomass", "biomass"),
            ("Energy", "energy"),
            ("CO₂", "co2"),
            ("Other exchanges", "other"),
        )
    )
    return html.Div(
        [
            html.Span("Flow key", className="flow-legend-title"),
            *[
                html.Span(
                    [
                        html.Span(className=f"flow-legend-arrow flow-legend-{tone}"),
                        label,
                    ],
                    className="flow-legend-item",
                )
                for label, tone in entries
            ],
        ],
        className="flow-legend",
        **{
            "aria-label": "Arrow colours for the displayed material, energy and carbon-dioxide flows"
        },
    )


def _inventory_sources(sources: list[tuple[str, str, str]]):
    return html.Div(
        [
            html.Span("Inventory basis", className="inventory-sources-title"),
            html.Div(
                [
                    html.A(
                        [
                            html.Strong(component),
                            html.Span(citation),
                            html.Span("↗", className="inventory-source-linkmark"),
                        ],
                        href=href,
                        target="_blank",
                        rel="noopener noreferrer",
                        className="inventory-source",
                    )
                    for component, citation, href in sources
                ],
                className="inventory-source-items",
            ),
        ],
        className="inventory-sources",
    )


def _system_boundary_slide(
    index: int,
    *,
    case: str,
    print_mode: bool,
    asset: str,
    alt: str,
    lead: str,
    balance: tuple[float, float, float],
    facts: list[tuple[str, str, str]],
    sources: list[tuple[str, str, str]],
):
    if case == "BECCS":
        stages = (
            ("reference", "Reference", "Standing forest + equivalent market energy"),
            ("project", "Project", "Harvest, regrowth and new CHP+CCS"),
            ("balance", "Balance", "1.029 − 0.029 = 1.000 t stored"),
        )
        initial_stage = "reference"
    else:
        stages = (
            ("capture", "Capture", "1.029 t CO₂ enters the system"),
            ("regeneration", "Regeneration", "12.24 GJ heat · heat-pump COP 3"),
            ("transport", "Transport + storage", "2,000 km · 0.029 t physical loss"),
            ("full", "Full system", "1.000 net t reaches storage"),
        )
        initial_stage = "capture"
    state = "all" if print_mode else initial_stage
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Span("Reveal", className="focus-control-label"),
                        dcc.RadioItems(
                            options=[
                                {"label": label, "value": value}
                                for value, label, _note in stages
                            ],
                            value=initial_stage,
                            inline=True,
                            className="contribution-view-toggle system-reveal-control",
                            **(
                                {}
                                if print_mode
                                else {"id": f"{case.lower()}-system-state-control"}
                            ),
                        ),
                    ],
                    className="teaching-focus-toolbar system-reveal-toolbar print-expanded-control",
                ),
                html.Figure(
                    html.Img(src=f"assets/{asset}", alt=alt),
                    className="system-boundary-figure",
                ),
                html.Div(
                    [
                        _net_removal_balance(
                            *balance,
                            capture_source=(
                                "captured from flue gas"
                                if case == "BECCS"
                                else "captured from air"
                            ),
                        ),
                        *[
                            _inventory_fact(label, value, tone)
                            for label, value, tone in facts
                        ],
                    ],
                    className="inventory-facts",
                ),
                _inventory_sources(sources),
                html.Div(
                    [
                        _flow_legend(case),
                        html.Div(
                            "CO₂-eq is the aggregate life-cycle GHG burden, not a physical CO₂ mass flow.",
                            className="system-boundary-note",
                        ),
                    ],
                    className="system-boundary-meta",
                ),
                html.Div(
                    [
                        html.Article(
                            [
                                html.Span(f"{position:02d}"),
                                html.Strong(label),
                                html.Small(note),
                            ],
                            className=f"system-stage-card stage-{value}",
                        )
                        for position, (value, label, note) in enumerate(stages, start=1)
                    ],
                    className="system-stage-strip",
                ),
            ],
            className=(
                f"system-boundary-layout system-boundary-{case.lower()} "
                f"system-state-{state}"
            ),
            **({} if print_mode else {"id": f"{case.lower()}-system-state-view"}),
        ),
        eyebrow=f"Conventional LCA · {case} system definition",
        lead=lead,
    )


def _beccs_system_slide(index: int, print_mode: bool = False):
    inventory = case_inventory("BECCS")
    return _system_boundary_slide(
        index,
        case="BECCS",
        print_mode=print_mode,
        asset="system-boundary-beccs.svg",
        alt=(
            "BECCS system boundary comparing a standing mature spruce forest and "
            "Northern European electricity and heat with project harvest, future "
            "forest regrowth, a new wood-chip CHP with post-combustion capture, "
            "compression, pipeline transport and geological storage."
        ),
        lead=(
            "The project harvests and regrows an existing forest, builds a new CHP "
            "plant with CCS, and displaces Northern European electricity and useful heat."
        ),
        balance=(
            inventory["gross_capture_t_co2"],
            inventory["transport_loss_co2_t"],
            inventory["supply_chain_ghg_kg_co2eq"],
        ),
        facts=[
            (
                "Flue-gas CO₂ capture",
                f"{inventory['host_flue_gas_capture_rate']:.0%}",
                "forest",
            ),
            (
                "CHP energy balance",
                f"{inventory['biomass_fuel_energy_gj']:.1f} GJ fuel → "
                f"{inventory['gross_chp_energy_output_gj']:.1f} GJ useful output + "
                f"{inventory['chp_conversion_losses_gj']:.1f} GJ losses",
                "amber",
            ),
        ],
        sources=[
            (
                "Forest + CHP",
                "ecoinvent 3.12",
                "https://support.ecoinvent.org/ecoinvent-version-3.12",
            ),
            (
                "Amine capture",
                "Volkart et al. (2013)",
                "https://doi.org/10.1016/j.ijggc.2013.03.003",
            ),
            (
                "2,000 km CO₂ pipeline",
                "Koornneef (2008) + Terlouw (2021)",
                "https://doi.org/10.1021/acs.est.1c03263",
            ),
        ],
    )


def _daccs_system_slide(index: int, print_mode: bool = False):
    inventory = case_inventory("DACCS")
    return _system_boundary_slide(
        index,
        case="DACCS",
        print_mode=print_mode,
        asset="system-boundary-daccs.svg",
        alt=(
            "DACCS system boundary from atmospheric carbon dioxide through a "
            "solid-sorbent air contactor, heat-pump regeneration, compression, "
            "pipeline transport and geological storage, with selected electricity, "
            "heat and sorbent quantities."
        ),
        lead=(
            "Electricity powers the air contactor, heat pump and CO₂ compression. "
            "The heat pump supplies low-temperature heat to regenerate the sorbent."
        ),
        balance=(
            inventory["gross_capture_t_co2"],
            inventory["transport_loss_co2_t"],
            inventory["supply_chain_ghg_kg_co2eq"],
        ),
        facts=[
            (
                "Capture medium",
                f"Solid sorbent · {inventory['sorbent_kg']:.2f} kg make-up",
                "sky",
            ),
            (
                "Regeneration heat",
                f"{inventory['delivered_low_temperature_heat_gj']:.2f} GJ from heat pump · "
                f"COP {inventory['heat_pump_cop']:.0f}",
                "amber",
            ),
        ],
        sources=[
            (
                "Contactor + sorbent",
                "Deutz & Bardow (2021)",
                "https://doi.org/10.1038/s41560-020-00771-9",
            ),
            (
                "DAC energy assumptions",
                "Qiu et al. (2022)",
                "https://doi.org/10.1038/s41467-022-31146-1",
            ),
            (
                "2,000 km CO₂ pipeline",
                "Koornneef (2008) + Terlouw (2021)",
                "https://doi.org/10.1021/acs.est.1c03263",
            ),
        ],
    )


def _static_activity_contributions(case: str) -> tuple[tuple[str, float], ...]:
    treatment = (
        "not applicable"
        if case == "DACCS"
        else "new CHP+CCS vs standing forest and Northern European energy"
    )
    return static_activity_contributions_per_net_tonne(
        case, "SSP2-NPi", 2025, treatment
    )


def _group_static_process_contributions(case: str) -> list[tuple[str, float, str]]:
    if case == "BECCS":
        grouped = process_step_attribution()["BECCS"][
            "process_groups_kg_co2eq_per_net_tonne"
        ]
        return [
            (
                "Forest regrowth · 1.143 t",
                float(grouped["Forest regrowth"]),
                "biogenic",
            ),
            (
                "Residual stack · 0.114 t",
                float(grouped["Residual biogenic stack emissions"]),
                "direct",
            ),
            (
                "Harvest + biomass supply",
                float(grouped["Harvesting and biomass supply"]),
                "other",
            ),
            (
                "Avoided Northern European energy",
                float(grouped["Avoided Northern European electricity"])
                + float(grouped["Avoided Northern European heat"]),
                "energy",
            ),
            (
                "Pipeline loss · 0.029 t",
                float(grouped["Transport losses"]),
                "transport",
            ),
            (
                "CHP+CCS supply chain",
                sum(
                    float(grouped.get(label, 0.0))
                    for label in (
                        "Capture electricity",
                        "Capture chemicals and operating materials",
                        "Compression and recompression",
                        "Pipeline and geological storage",
                        "CCS infrastructure and end-of-life",
                        "New CHP infrastructure and end-of-life",
                        "Other CHP operating emissions",
                        "Other CHP and CCS supply-chain GHG emissions",
                    )
                ),
                "other",
            ),
        ]

    rows = _static_activity_contributions(case)
    grouped = {
        "removal": 0.0,
        "biogenic": 0.0,
        "electricity": 0.0,
        "heat": 0.0,
        "transport": 0.0,
        "other": 0.0,
    }
    biogenic_processes = (
        "supply of forest residue",
        "plywood production",
        "three and five layered board production",
        "treatment of sewage sludge by anaerobic digestion",
        "hardwood forestry",
    )
    for contributor, score in rows:
        contributor_lower = contributor.lower()
        if (
            "direct air capture system" in contributor
            or "carbon dioxide removal, BECCS" in contributor
        ):
            grouped["removal"] += score
        elif "carbon dioxide transport extension" in contributor:
            grouped["transport"] += score
        elif score < 0 and any(name in contributor for name in biogenic_processes):
            grouped["biogenic"] += score
        elif "| electricity" in contributor_lower:
            grouped["electricity"] += score
        elif "| heat" in contributor_lower:
            grouped["heat"] += score
        else:
            grouped["other"] += score

    removal_label = (
        "Direct capture + storage" if case == "DACCS" else "Retrofit capture + storage"
    )
    return [
        (
            "Captured from air · 1.029 t" if case == "DACCS" else removal_label,
            grouped["removal"],
            "direct",
        ),
        ("Upstream biogenic uptake", grouped["biogenic"], "biogenic"),
        ("Electricity", grouped["electricity"], "energy"),
        ("Heat", grouped["heat"], "heat"),
        ("Pipeline loss · 0.029 t", grouped["transport"], "transport"),
        ("Other supply chain", grouped["other"], "other"),
    ]


def _activity_location(contributor: str) -> str:
    parts = [part.strip() for part in contributor.split("|")]
    return parts[-1] if len(parts) >= 3 else "Other / mixed"


def _location_label(location: str) -> str:
    return {
        "ENC": "Northern Europe",
        "FI": "Finland",
        "SE": "Sweden",
        "DK": "Denmark",
        "CHA": "China",
        "GLO": "Global",
        "RoW": "Rest of world",
    }.get(location, location)


def _activity_group_key(contributor: str) -> str:
    parts = [part.strip() for part in contributor.split("|")]
    return " | ".join(parts[:-1]) if len(parts) >= 3 else contributor


def _activity_label(contributor: str, case: str) -> str:
    lower = contributor.lower()
    if contributor == "Other":
        return "Unranked activities"
    if "direct air capture system" in lower:
        return "Direct-air capture system"
    if "carbon dioxide removal, beccs" in lower:
        return "Greenfield BECCS system"
    if "supply of forest residue" in lower:
        return "Forest-residue supply"
    if "heat and power co-generation, wood chips" in lower:
        return (
            "Wood-chip CHP electricity"
            if "electricity" in lower
            else "Wood-chip CHP heat"
        )
    if "carbon dioxide transport extension" in lower:
        return "CO₂ pipeline extension"
    if "biomass-fired igcc" in lower:
        return "Biomass IGCC electricity"
    if "natural gas, subcritical" in lower:
        return "Natural-gas electricity"
    if "plywood production" in lower:
        return "Plywood production"
    if "three and five layered board" in lower:
        return "Wood-panel production"
    if "sewage sludge" in lower:
        return "Sewage-sludge digestion"
    if "hardwood forestry" in lower:
        return "Hardwood forestry"
    if "pig iron production" in lower:
        return "Pig-iron production"
    if "natural gas venting" in lower:
        return "Natural-gas venting"
    del case
    return contributor.split("|")[0].strip()


def _collapse_contribution_groups(
    values: dict[str, float],
    *,
    top_n: int,
    remainder_label: str,
) -> list[tuple[str, float]]:
    ranked = sorted(values.items(), key=lambda item: abs(item[1]), reverse=True)
    kept = ranked[:top_n]
    remainder = sum(value for _, value in ranked[top_n:])
    if len(ranked) > top_n:
        kept.append((remainder_label, remainder))
    return kept


def _group_static_location_contributions(case: str) -> list[tuple[str, float, str]]:
    grouped: dict[str, float] = {}
    for contributor, score in _static_activity_contributions(case):
        location = _activity_location(contributor)
        grouped[location] = grouped.get(location, 0.0) + score
    collapsed = _collapse_contribution_groups(
        grouped, top_n=5, remainder_label="Other locations"
    )
    return [
        (_location_label(label), value, "benefit" if value < 0 else "burden")
        for label, value in collapsed
    ]


def _group_static_activity_name_contributions(
    case: str,
) -> list[tuple[str, float, str]]:
    grouped: dict[str, float] = {}
    for contributor, score in _static_activity_contributions(case):
        key = _activity_group_key(contributor)
        grouped[key] = grouped.get(key, 0.0) + score
    unranked_remainder = grouped.pop("Other", 0.0)
    ranked = sorted(grouped.items(), key=lambda item: abs(item[1]), reverse=True)
    collapsed = ranked[:5]
    collapsed.append(
        (
            "Other activities",
            unranked_remainder + sum(value for _, value in ranked[5:]),
        )
    )
    return [
        (
            _activity_label(label, case),
            value,
            "benefit" if value < 0 else "burden",
        )
        for label, value in collapsed
    ]


def _group_static_contributions(case: str, view: str) -> list[tuple[str, float, str]]:
    if view == "step":
        return _group_static_process_contributions(case)
    if view == "location":
        return _group_static_location_contributions(case)
    if view == "activity":
        return _group_static_activity_name_contributions(case)
    raise ValueError(f"Unknown contribution view: {view}")


def _contribution_row(label: str, value: float, tone: str):
    negative = value < 0
    positive = value > 0
    scale = 1300 if negative else 650
    width = min(abs(value) / scale * 100, 100)
    return html.Div(
        [
            html.Div(label, className="contribution-label", title=label),
            html.Div(
                _format_score(value) if negative else "",
                className="contribution-value contribution-value-negative",
            ),
            html.Div(
                html.Div(
                    className=f"contribution-bar contribution-{tone}",
                    style={"width": f"{width:.2f}%" if negative else "0"},
                ),
                className="contribution-track contribution-track-negative",
            ),
            html.Div(className="contribution-zero"),
            html.Div(
                html.Div(
                    className=f"contribution-bar contribution-{tone}",
                    style={"width": f"{width:.2f}%" if positive else "0"},
                ),
                className="contribution-track contribution-track-positive",
            ),
            html.Div(
                f"+{_format_score(value)}" if positive else ("0" if value == 0 else ""),
                className="contribution-value contribution-value-positive",
            ),
        ],
        className="contribution-row",
    )


def _contribution_panel(case: str, subtitle: str, tone: str, view: str):
    contributions = _group_static_contributions(case, view)
    total = sum(value for _, value, _ in contributions)
    return html.Article(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(case, className=f"contribution-case case-{tone}"),
                            html.Span(subtitle, className="contribution-subtitle"),
                        ],
                        className="contribution-panel-title",
                    ),
                    html.Div(
                        f"Σ = {_format_score(total)}",
                        className="contribution-net",
                    ),
                ],
                className="contribution-panel-heading",
            ),
            html.Div(
                [
                    html.Span("lower GWP100 ←", className="axis-benefit"),
                    html.Span("0", className="axis-zero"),
                    html.Span("→ higher GWP100", className="axis-burden"),
                ],
                className="contribution-axis",
            ),
            html.Div(
                [_contribution_row(*contribution) for contribution in contributions],
                className="contribution-rows",
            ),
            html.Div(
                "kg CO₂-eq / net t stored",
                className="contribution-equation contribution-unit",
            ),
        ],
        className=f"contribution-panel contribution-panel-{tone}",
    )


def render_static_contribution_view(view: str = "step"):
    view = view if view in {"step", "location", "activity"} else "step"
    takeaway = {
        "step": (
            "For greenfield BECCS, forest regrowth and avoided Northern European energy "
            "outweigh harvest, plant, capture and transport burdens. For DACCS, "
            "electricity for capture and sorbent regeneration dominates. The baseline "
            "does not assign a flux to residues, roots or soil carbon."
        ),
        "location": (
            "This view locates the contributing activities, not the eventual atmospheric climate effect. "
            "Lower-ranked locations remain in the exact ‘Other locations’ balance."
        ),
        "activity": (
            "Repeated activities are combined across locations. The five largest absolute activity scores "
            "are shown; ‘Other activities’ preserves the exact total."
        ),
    }[view]
    content = [
        html.Div(
            [
                _contribution_panel("BECCS", "new CHP+CCS", "forest", view),
                _contribution_panel("DACCS", "solid sorbent + heat pump", "sky", view),
            ],
            className="contribution-comparison",
        ),
    ]
    if view == "step":
        sensitivity = forest_pool_sensitivity("static")
        fraction_pct = 100 * float(sensitivity["stress_test_fraction"])
        break_even_pct = 100 * float(sensitivity["break_even_fraction"])
        stress_gap = float(sensitivity["comparator_daccs"]) - float(
            sensitivity["stress_test_beccs"]
        )
        content.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Unmodelled forest-carbon sensitivity"),
                            html.Span(
                                "What if harvest causes extra CO₂ emissions from residues, roots or soil?"
                            ),
                            html.Small("Separate from the upper contribution bars"),
                        ],
                        className="forest-sensitivity-heading",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("BECCS baseline"),
                                    html.Strong(
                                        f"{_format_score(float(sensitivity['baseline_beccs']))} kg"
                                    ),
                                ],
                                className="forest-sensitivity-step",
                            ),
                            html.B("+", className="forest-sensitivity-operator"),
                            html.Div(
                                [
                                    html.Span(f"Illustrative {fraction_pct:.0f}% test"),
                                    html.Strong(
                                        f"+{float(sensitivity['stress_test_correction']):,.0f} kg"
                                    ),
                                    html.Small(
                                        f"{fraction_pct:.0f}% of the 1,143 kg regrowth uptake"
                                    ),
                                ],
                                className=(
                                    "forest-sensitivity-step "
                                    "forest-sensitivity-assumption"
                                ),
                            ),
                            html.B("=", className="forest-sensitivity-operator"),
                            html.Div(
                                [
                                    html.Span("Adjusted BECCS"),
                                    html.Strong(
                                        f"{_format_score(float(sensitivity['stress_test_beccs']))} kg"
                                    ),
                                ],
                                className=(
                                    "forest-sensitivity-step "
                                    "forest-sensitivity-adjusted"
                                ),
                            ),
                        ],
                        className="forest-sensitivity-equation",
                    ),
                    html.Div(
                        [
                            html.Strong(
                                f"DACCS baseline {_format_score(float(sensitivity['comparator_daccs']))} kg"
                            ),
                            html.Span(
                                f"In the 10% test, BECCS remains {stress_gap:.0f} kg lower."
                            ),
                            html.Em(
                                "Ranking changes if extra forest emissions exceed "
                                f"{float(sensitivity['break_even_correction']):,.0f} kg "
                                f"({break_even_pct:.1f}% of regrowth uptake)."
                            ),
                        ],
                        className="forest-sensitivity-verdict",
                    ),
                ],
                className="forest-sensitivity",
            )
        )
    content.extend(
        [
            html.Div(
                [
                    html.Strong(
                        "The same storage service does not imply the same GWP100 score. "
                    ),
                    html.Span(takeaway),
                ],
                className="contribution-takeaway",
            ),
            html.Div(
                "Characterised activity contributions · uptake-only baseline plus a separate sensitivity calculation · IPCC 2021 GWP100 including biogenic CO₂ · SSP2-NPi · Northern Europe · 2025 · functional unit: 1 net tonne stored after transport loss",
                className="contribution-footnote",
            ),
        ]
    )
    return content


def render_static_contribution_legend(view: str = "step"):
    if view == "step":
        entries = (
            ("Capture + storage", "direct"),
            ("Biogenic uptake", "biogenic"),
            ("Electricity", "energy"),
            ("Heat", "heat"),
            ("CO₂ transport", "transport"),
            ("Other", "other"),
        )
    else:
        entries = (
            ("Negative contribution", "benefit"),
            ("Positive contribution", "burden"),
        )
    return [
        html.Span(
            [
                html.Span(className=f"contribution-legend-swatch contribution-{tone}"),
                label,
            ],
            className="contribution-legend-item",
        )
        for label, tone in entries
    ]


def _static_contribution_slide(index: int):
    return _slide_shell(
        index,
        [
            html.Div(
                [
                    html.Div(
                        render_static_contribution_legend("step"),
                        id="contribution-legend",
                        className="contribution-legend",
                    ),
                    html.Div(
                        [
                            html.Span(
                                "Group contributions by",
                                className="contribution-toggle-label",
                            ),
                            dcc.RadioItems(
                                id="contribution-view-toggle",
                                options=[
                                    {"label": "Process step", "value": "step"},
                                    {
                                        "label": "Activity location",
                                        "value": "location",
                                    },
                                    {"label": "Activity name", "value": "activity"},
                                ],
                                value="step",
                                inline=True,
                                persistence=True,
                                persistence_type="session",
                                className="contribution-view-toggle",
                            ),
                        ],
                        className="contribution-toggle-group",
                    ),
                ],
                className="contribution-toolbar",
            ),
            html.Div(
                render_static_contribution_view("step"),
                id="contribution-chart",
                className="contribution-view",
            ),
            html.Div(
                [
                    html.Strong("Why is this only a sensitivity?"),
                    html.Span(
                        "we do not yet have site-specific magnitudes or timing for residue, root and soil-carbon emissions."
                    ),
                ],
                className="contribution-plain-language-note",
            ),
        ],
        lead=(
            "Functional unit: 1 net tonne stored after transport losses. Gross capture "
            "is 1.029 t; transport loss is 0.029 t."
        ),
    )


def _policy_path_card(
    pathway: str,
    label: str,
    tone: str,
    policy_text: str,
    outcomes: tuple[tuple[str, str], tuple[str, str]],
):
    return html.Article(
        [
            html.Div(
                [_tag(pathway, tone), html.Strong(label)],
                className="policy-path-heading",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("CLIMATE POLICY"),
                            html.P(policy_text),
                        ],
                        className="policy-path-copy",
                    ),
                    html.Div(
                        [
                            html.Span(className="trajectory-segment segment-one"),
                            html.Span(className="trajectory-segment segment-two"),
                            html.Span(className="trajectory-segment segment-three"),
                        ],
                        className=f"policy-trajectory trajectory-{tone}",
                    ),
                    html.Div(
                        [
                            html.Div([html.Strong(value), html.Span(metric)])
                            for value, metric in outcomes
                        ],
                        className="policy-outcome-metrics",
                    ),
                ],
                className="policy-path-body",
            ),
        ],
        className=f"policy-path-card policy-{tone}",
    )


def _premise_sector_tile(icon: str, title: str, change: str, tone: str):
    return html.Div(
        [
            html.Span(
                html.Img(src=icon, alt=""),
                className=f"premise-sector-icon update-{tone}",
            ),
            html.Div(
                [html.B(title), html.Span(change)],
                className="premise-sector-copy",
            ),
            html.Div(
                [html.I(), html.I(), html.I()],
                className=f"premise-sector-signal signal-{tone}",
                **{"aria-hidden": "true"},
            ),
        ],
        className="premise-sector-tile",
    )


def _prospective_intro_combined(index: int):
    return _slide_shell(
        index,
        [
            html.Div(
                [
                    html.Article(
                        [
                            html.Span(
                                "SHARED SOCIOECONOMIC PATHWAY",
                                className="iam-card-kicker",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H3("SSP2"),
                                            html.Strong("Middle of the Road"),
                                        ],
                                        className="iam-ssp2-title",
                                    ),
                                    html.Div(
                                        [
                                            html.Img(
                                                src="assets/ssp2-middle-road.svg",
                                                alt=(
                                                    "A middle-of-the-road society with "
                                                    "urban, industrial, agricultural and "
                                                    "energy systems."
                                                ),
                                            ),
                                        ],
                                        className="iam-ssp2-visual-panel",
                                    ),
                                ],
                                className="iam-ssp2-hero",
                            ),
                            html.P(
                                "SSP2 assumes that recent social and economic trends continue. "
                                "Development remains uneven, institutions improve gradually, "
                                "and environmental pressures persist.",
                                className="iam-ssp2-summary",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.B("↗"),
                                            html.Span(
                                                [
                                                    html.Strong("Demography"),
                                                    html.Small("moderate growth"),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.B("↗"),
                                            html.Span(
                                                [
                                                    html.Strong("Economy"),
                                                    html.Small("uneven growth"),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.B("→"),
                                            html.Span(
                                                [
                                                    html.Strong("Technology"),
                                                    html.Small("gradual, balanced"),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.B("↔"),
                                            html.Span(
                                                [
                                                    html.Strong("Institutions"),
                                                    html.Small("slow progress"),
                                                ]
                                            ),
                                        ]
                                    ),
                                ],
                                className="iam-ssp2-drivers",
                            ),
                            html.Div(
                                [
                                    html.B("Same in both policy runs"),
                                    html.Span(
                                        "Population, economic growth and broader social trends "
                                        "follow the same SSP2 assumptions."
                                    ),
                                ],
                                className="iam-shared-note",
                            ),
                        ],
                        className="iam-ssp2-card",
                    ),
                    html.Article(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "INTEGRATED ASSESSMENT MODEL",
                                                className="iam-card-kicker",
                                            ),
                                            html.H3("REMIND-EU policy pathways"),
                                        ]
                                    ),
                                    html.Img(
                                        src="assets/pik-logo.png",
                                        alt="Potsdam Institute for Climate Impact Research",
                                        className="pik-logo",
                                    ),
                                ],
                                className="iam-chart-heading",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.I(),
                                            html.Div(
                                                [
                                                    html.Strong(
                                                        "SSP2-NPi · policies already implemented"
                                                    ),
                                                    html.Span(
                                                        "No global cumulative CO₂ limit"
                                                    ),
                                                ]
                                            ),
                                            html.B(
                                                "28 Gt CO₂ yr⁻¹ · 2.57 °C",
                                                className="iam-policy-outcome",
                                            ),
                                        ],
                                        className="iam-policy-legend iam-policy-npi",
                                    ),
                                    html.Div(
                                        [
                                            html.I(),
                                            html.Div(
                                                [
                                                    html.Strong(
                                                        "SSP2-PkBudg1000 · cumulative limit"
                                                    ),
                                                    html.Span(
                                                        "The same SSP2 world with a 1000 Gt global CO₂ budget"
                                                    ),
                                                ]
                                            ),
                                            html.B(
                                                "−0.8 Gt CO₂ yr⁻¹ · 1.76 °C",
                                                className="iam-policy-outcome",
                                            ),
                                        ],
                                        className="iam-policy-legend iam-policy-budget",
                                    ),
                                ],
                                className="iam-policy-legends",
                            ),
                            html.Img(
                                src="assets/slide8-iam-pathways.svg",
                                alt=(
                                    "REMIND-EU global population, GDP, carbon dioxide "
                                    "emissions and temperature trajectories for "
                                    "SSP2-NPi and SSP2-PkBudg1000 from 2020 to 2100."
                                ),
                                className="iam-pathways-chart",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "Population · GDP (PPP) · CO₂ · temperature"
                                    ),
                                    html.Span("Global REMIND-EU / MAGICC7 outputs"),
                                ],
                                className="iam-chart-caption",
                            ),
                        ],
                        className="iam-chart-card",
                    ),
                ],
                className="iam-narrative-layout",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("IAM OUTPUTS"),
                            html.Img(
                                src="assets/icons/iam-data-cube.svg",
                                alt=(
                                    "IAM output data cube indexed by time, region "
                                    "and technology."
                                ),
                                className="iam-output-cube",
                            ),
                            html.Div(
                                [
                                    html.Span("years"),
                                    html.Span("regions"),
                                    html.Span("technologies"),
                                ],
                                className="iam-output-dimensions",
                            ),
                        ],
                        className="iam-output-node",
                    ),
                    html.Div("→", className="visual-flow-arrow"),
                    html.Div(
                        [
                            html.Img(
                                src="assets/premise-logo.png",
                                alt="premise",
                                className="premise-official-logo",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "FROM IAM PATHWAYS TO LCI BACKGROUNDS",
                                        className="iam-card-kicker",
                                    ),
                                    html.H4("What premise changes"),
                                    html.Div(
                                        [
                                            html.Span("1", className="action-number"),
                                            html.B("Map IAM variables"),
                                            html.Span("to LCI technologies"),
                                        ],
                                        className="premise-action-row",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("2", className="action-number"),
                                            html.B("Update processes"),
                                            html.Span("efficiency + emissions"),
                                        ],
                                        className="premise-action-row",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("3", className="action-number"),
                                            html.B("Rebuild markets"),
                                            html.Span("technology shares"),
                                        ],
                                        className="premise-action-row",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("4", className="action-number"),
                                            html.B("Relink suppliers"),
                                            html.Span("regional consistency"),
                                        ],
                                        className="premise-action-row",
                                    ),
                                ],
                                className="premise-action-list",
                            ),
                        ],
                        className="premise-brand-engine",
                    ),
                    html.Div("→", className="visual-flow-arrow"),
                    html.Div(
                        [
                            html.Span(
                                "BACKGROUND SECTORS UPDATED",
                                className="premise-sector-map-label",
                            ),
                            _premise_sector_tile(
                                "assets/icons/power.svg",
                                "Power",
                                "mix + efficiency",
                                "electricity",
                            ),
                            _premise_sector_tile(
                                "assets/icons/heat.svg",
                                "Heat & fuels",
                                "routes + emissions",
                                "heat",
                            ),
                            _premise_sector_tile(
                                "assets/icons/mobility.svg",
                                "Mobility",
                                "fleet + efficiency",
                                "transport",
                            ),
                            _premise_sector_tile(
                                "assets/icons/industry.svg",
                                "Industry",
                                "routes + CCS",
                                "materials",
                            ),
                            _premise_sector_tile(
                                "assets/icons/resources.svg",
                                "Resources",
                                "regional supply",
                                "biomass",
                            ),
                            _premise_sector_tile(
                                "assets/icons/removal.svg",
                                "Removal",
                                "deployment + energy",
                                "cdr",
                            ),
                        ],
                        className="premise-sector-map",
                    ),
                    html.Div("→", className="visual-flow-arrow"),
                    html.Div(
                        [
                            html.H4("Prospective LCI"),
                            *[
                                html.Div(
                                    [
                                        html.Strong(str(year)),
                                        html.Div(
                                            [html.Span(), html.Span(), html.Span()],
                                            className="database-layers",
                                        ),
                                        html.Span("scenario LCI"),
                                    ],
                                    className="future-database",
                                )
                                for year in (2025, 2030, 2050)
                            ],
                        ],
                        className="future-database-stack",
                    ),
                ],
                className="premise-transformation-layout",
            ),
        ],
        lead=(
            "Both scenarios use SSP2 socioeconomic assumptions but differ in climate "
            "policy. premise maps each REMIND-EU pathway to a consistent LCI background."
        ),
    )


def _prospective_intro(index: int):
    """Show only the shared SSP2 story and the policy-pathway contrast."""

    slide = _prospective_intro_combined(index)
    body = slide.children[1]
    chart_card = body.children[0].children[1]
    shared_assumptions = html.Div(
        [
            html.Div(
                [
                    html.Img(
                        src="assets/ssp2-middle-road.svg",
                        alt="SSP2 middle-of-the-road socioeconomic pathway",
                    ),
                    html.Div(
                        [
                            html.Span("Shared socioeconomic pathway"),
                            html.Strong("SSP2 · Middle of the Road"),
                        ]
                    ),
                ],
                className="iam-shared-world-title",
            ),
            html.Div(
                [
                    html.Span([html.B("Population"), "moderate growth"]),
                    html.Span([html.B("Economy"), "uneven growth"]),
                    html.Span([html.B("Technology"), "gradual change"]),
                    html.Span([html.B("Institutions"), "slow progress"]),
                ],
                className="iam-shared-assumption-chips",
            ),
            html.Div(
                [
                    html.B("Held constant"),
                    html.Span(
                        "The socioeconomic storyline is shared; climate policy creates the fork."
                    ),
                ],
                className="iam-shared-policy-note",
            ),
        ],
        className="iam-shared-assumptions-strip",
    )
    body.children = [
        html.Div(
            [shared_assumptions, chart_card],
            className="iam-expanded-chart-layout",
        )
    ]
    return slide


def _prospective_transformation(index: int):
    """Show how premise turns IAM outputs into prospective LCI backgrounds."""

    slide = _prospective_intro_combined(index)
    body = slide.children[1]
    body.children = [
        body.children[1],
        html.Button(
            "Detailed transformation sources: Appendix B →",
            id={"type": "chapter-button", "slide": APPENDIX_START_SLIDE + 1},
            n_clicks=0,
            className="appendix-link-button",
        ),
    ]
    heading = slide.children[0]
    heading.children[2] = html.P(
        "premise maps each REMIND-EU pathway to consistent sector inventories and target-year databases.",
        className="slide-lead",
    )
    return slide


MIX_COLOURS = {
    "Hydro": "#4193b8",
    "Wind": "#008a82",
    "Solar": "#d99614",
    "Nuclear": "#7656a8",
    "Biomass": "#3e7654",
    "Electric": "#4193b8",
    "Recovered heat": "#7656a8",
    "Hydrogen": "#00a49a",
    "Natural gas": "#c44e52",
    "Oil": "#b7792b",
    "Coal": "#4f5961",
    "Coal and oil": "#616d74",
    "Conventional": "#89999f",
    "CCS": "#00a49a",
    "BF–BOF": "#4f5961",
    "BF–BOF + CCS": "#147d78",
    "DRI–EAF": "#d99614",
    "H₂–DRI/EAF": "#00a49a",
    "Scrap EAF": "#7656a8",
    "Electrowinning": "#4193b8",
    "Battery electric": "#4193b8",
    "Diesel truck": "#4f5961",
    "Fuel cell": "#00a49a",
    "Compressed gas": "#d99614",
    "Other": "#bbc7cb",
}


def _technology_mix_bar(sector: str, pathway: str, year: int):
    return html.Div(
        [
            html.Span(
                f"{share * 100:.0f}%" if share >= 0.12 else "",
                className="technology-mix-segment",
                style={
                    "width": f"{share * 100:.5f}%",
                    "backgroundColor": MIX_COLOURS[category],
                    "color": "#0b3b52" if category == "Solar" else "white",
                },
                title=f"{category}: {share * 100:.1f}%",
            )
            for category, share in scenario_sector_mix(sector, pathway, year)
            if share > 1e-7
        ],
        className="technology-mix-bar",
    )


def _mix_year_group(
    sector: str,
    year: int,
    intensity: dict[str, dict[int, float]],
    scale: int,
):
    rows = (
        [("both", "SSP2-NPi")]
        if year == 2025
        else [("NPi", "SSP2-NPi"), ("PkBudg1000", "SSP2-PkBudg1000")]
    )
    return html.Div(
        [
            html.Strong(str(year), className="mix-year"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(label, className=f"mix-pathway mix-{label}"),
                            _technology_mix_bar(sector, pathway, year),
                            html.Span(
                                (
                                    f"{intensity[pathway][year] * scale:.0f}"
                                    if year in (2025, 2050)
                                    else ""
                                ),
                                className=(
                                    "mix-row-intensity "
                                    f"mix-intensity-{label} "
                                    f"{'mix-intensity-hidden' if year == 2030 else ''}"
                                ),
                            ),
                        ],
                        className=(
                            "mix-scenario-row "
                            f"{'mix-row-baseline' if year == 2025 else ''} "
                            f"{'mix-row-emphasis' if year == 2050 else ''}"
                        ),
                    )
                    for label, pathway in rows
                ],
                className="mix-scenario-stack",
            ),
        ],
        className="mix-year-group",
    )


def _sector_mix_panel(sector: str):
    is_electricity = sector == "Electricity"
    scale = 1000
    unit = "g CO₂-eq/kWh" if is_electricity else "g CO₂-eq/MJ"
    relevance = (
        "Northern European high-voltage supply mix · intensity after delivery at medium voltage"
        if is_electricity
        else "Northern European district and industrial heat market"
    )
    intensity = {
        pathway: dict(scenario_sector_series(sector, pathway))
        for pathway in ("SSP2-NPi", "SSP2-PkBudg1000")
    }
    categories = [
        category
        for category, _ in scenario_sector_mix(sector, "SSP2-NPi", 2025)
        if category != "Other"
    ]
    gap = 100 * (1 - intensity["SSP2-PkBudg1000"][2050] / intensity["SSP2-NPi"][2050])
    icon = "assets/icons/power.svg" if is_electricity else "assets/icons/heat.svg"
    icon_tone = "electricity" if is_electricity else "heat"
    deltas = (
        (
            ("Hydro", "+26 pp", MIX_COLOURS["Hydro"]),
            ("Wind", "−28 pp", MIX_COLOURS["Wind"]),
            ("Climate intensity", f"−{gap:.0f}%", "#0b3b52"),
        )
        if is_electricity
        else (
            ("Oil", "−7 pp", MIX_COLOURS["Oil"]),
            ("Hydrogen", "+7 pp", MIX_COLOURS["Hydrogen"]),
            ("Climate intensity", f"−{gap:.0f}%", "#0b3b52"),
        )
    )
    return html.Article(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                html.Img(src=icon, alt=""),
                                className=(
                                    "premise-sector-icon "
                                    f"update-{icon_tone} mix-panel-icon"
                                ),
                            ),
                            html.Div([html.H3(sector), html.P(relevance)]),
                        ],
                        className="mix-panel-title mix-panel-title-with-icon",
                    ),
                    html.Div(
                        [
                            html.Span("PkBudg1000 vs NPi"),
                            html.Strong(f"{gap:.0f}% lower"),
                            html.Small("climate intensity"),
                        ],
                        className="mix-policy-gap",
                    ),
                ],
                className="mix-panel-heading",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("year"),
                            html.Span("scenario"),
                            html.Span("technology share"),
                            html.Span(unit),
                        ],
                        className="mix-timeline-head",
                    ),
                    *[
                        _mix_year_group(sector, year, intensity, scale)
                        for year in (2025, 2030, 2050)
                    ],
                ],
                className="mix-timeline",
            ),
            html.Div(
                [
                    html.Span(
                        [
                            html.I(style={"backgroundColor": MIX_COLOURS[category]}),
                            "Electric heat" if category == "Electric" else category,
                        ]
                    )
                    for category in categories
                ],
                className="technology-mix-legend",
            ),
            html.Div(
                [
                    html.Span("PKBUDG1000 VS NPI · 2050"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(style={"backgroundColor": colour}),
                                    html.Span(label),
                                    html.Strong(delta),
                                ],
                                className="mix-delta-chip",
                            )
                            for label, delta, colour in deltas
                        ],
                        className="mix-delta-chips",
                    ),
                ],
                className="mix-delta-summary",
            ),
        ],
        className=f"sector-mix-panel mix-panel-{'electricity' if is_electricity else 'heat'}",
    )


def _economy_mix_bar(sector: str, pathway: str, year: int):
    return html.Div(
        [
            html.Span(
                f"{share * 100:.0f}%" if share >= 0.18 else "",
                className="economy-mix-segment",
                style={
                    "width": f"{share * 100:.5f}%",
                    "backgroundColor": MIX_COLOURS[category],
                },
                title=f"{category}: {share * 100:.1f}%",
            )
            for category, share in scenario_sector_mix(sector, pathway, year)
            if share > 1e-7
        ],
        className="economy-mix-bar",
    )


def _economy_sector_card(sector: str):
    config = {
        "Cement clinker": {
            "title": "Cement clinker",
            "subtitle": "Northern European production routes",
            "icon": "assets/icons/resources.svg",
            "tone": "cement",
            "indicator": "Cement",
            "unit": "kg CO₂-eq/kg",
        },
        "Steel": {
            "title": "Low-alloyed steel",
            "subtitle": "Northern European production routes",
            "icon": "assets/icons/industry.svg",
            "tone": "steel",
            "indicator": "Steel",
            "unit": "kg CO₂-eq/kg",
        },
        "Truck transport": {
            "title": "Truck transport",
            "subtitle": "Northern European freight-lorry fleet",
            "icon": "assets/icons/truck.svg",
            "tone": "transport",
            "indicator": None,
            "share_category": "Battery electric",
            "unit": "battery-electric share",
        },
    }[sector]
    views = (
        ("2025", "SSP2-NPi", 2025, "baseline"),
        ("2050 NPi", "SSP2-NPi", 2050, "npi"),
        ("2050 PkBudg1000", "SSP2-PkBudg1000", 2050, "budget"),
    )

    if config["indicator"]:
        intensity = {
            pathway: dict(scenario_sector_series(config["indicator"], pathway))
            for pathway in ("SSP2-NPi", "SSP2-PkBudg1000")
        }
        npi_2050 = intensity["SSP2-NPi"][2050]
        budget_2050 = intensity["SSP2-PkBudg1000"][2050]
        gap = 100 * (1 - budget_2050 / npi_2050)
        signal = f"{gap:.0f}% lower"
        values = {
            (pathway, year): f"{intensity[pathway][year]:.2f}"
            for _, pathway, year, _ in views
        }
    else:
        selected_share = {
            (pathway, year): dict(scenario_sector_mix(sector, pathway, year))[
                config["share_category"]
            ]
            for _, pathway, year, _ in views
        }
        signal = (
            f"{selected_share[('SSP2-NPi', 2050)] * 100:.0f}% → "
            f"{selected_share[('SSP2-PkBudg1000', 2050)] * 100:.0f}%"
        )
        values = {key: f"{share * 100:.0f}%" for key, share in selected_share.items()}

    categories = [
        category
        for category, _ in scenario_sector_mix(sector, "SSP2-NPi", 2025)
        if category != "Other"
        and any(
            dict(scenario_sector_mix(sector, pathway, year))[category] >= 0.005
            for _, pathway, year, _ in views
        )
    ]
    return html.Article(
        [
            html.Div(
                [
                    html.Span(
                        html.Img(src=config["icon"], alt=""),
                        className=f"economy-card-icon economy-icon-{config['tone']}",
                    ),
                    html.Div([html.H4(config["title"]), html.P(config["subtitle"])]),
                    html.Div(
                        [html.Strong(signal), html.Small(config["unit"])],
                        className="economy-card-signal",
                    ),
                ],
                className="economy-card-header",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(label, className="economy-row-label"),
                            _economy_mix_bar(sector, pathway, year),
                            html.Strong(
                                values[(pathway, year)],
                                className="economy-row-value",
                            ),
                        ],
                        className=f"economy-mix-row economy-row-{row_tone}",
                    )
                    for label, pathway, year, row_tone in views
                ],
                className="economy-card-rows",
            ),
            html.Div(
                [
                    html.Span(
                        [
                            html.I(style={"backgroundColor": MIX_COLOURS[category]}),
                            category,
                        ]
                    )
                    for category in categories
                ],
                className="economy-card-legend",
            ),
        ],
        className=f"economy-sector-card economy-card-{config['tone']}",
    )


def _scenario_slide_base(index: int):
    return _slide_shell(
        index,
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(className="scenario-key-line key-npi"),
                            html.Strong("SSP2-NPi"),
                            html.Span("implemented policies"),
                        ],
                        className="scenario-key",
                    ),
                    html.Div(
                        [
                            html.Span(className="scenario-key-line key-budget"),
                            html.Strong("SSP2-PkBudg1000"),
                            html.Span("1000 Gt CO₂ budget"),
                        ],
                        className="scenario-key",
                    ),
                    html.Div(
                        "REMIND-EU · Northern Europe",
                        className="scenario-method-note",
                    ),
                ],
                className="scenario-plot-toolbar",
            ),
            html.Div(
                [_sector_mix_panel("Electricity"), _sector_mix_panel("District heat")],
                className="sector-mix-grid",
            ),
            html.Div(
                [
                    html.Strong("2050 pathway sensitivity"),
                    html.Div(
                        [
                            html.Img(src="assets/icons/power.svg", alt=""),
                            html.Span("Electricity"),
                            html.B("−5%"),
                        ],
                        className="scenario-sensitivity sensitivity-electricity",
                    ),
                    html.Div(
                        [
                            html.Img(src="assets/icons/heat.svg", alt=""),
                            html.Span("District heat"),
                            html.B("−40%"),
                        ],
                        className="scenario-sensitivity sensitivity-heat",
                    ),
                    html.P(
                        "In 2050, SSP2-PkBudg1000 reduces the GWP100 intensity of district "
                        "heat and steel much more than that of electricity or cement."
                    ),
                ],
                className="scenario-takeaway-strip",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Beyond energy"),
                            html.Span(
                                "2050 production mixes and climate intensity · 2025 shared baseline"
                            ),
                        ],
                        className="scenario-economy-heading",
                    ),
                    html.Div(
                        [
                            _economy_sector_card("Cement clinker"),
                            _economy_sector_card("Steel"),
                            _economy_sector_card("Truck transport"),
                        ],
                        className="scenario-economy-cards",
                    ),
                ],
                className="scenario-economy-block",
            ),
            html.Div(
                [
                    html.Span("premise-transformed markets"),
                    html.Span("IPCC 2021 GWP100 including biogenic CO₂"),
                    html.Span("technology shares sum to 100%"),
                ],
                className="scenario-method-footer",
            ),
        ],
        lead=(
            "By 2050, SSP2-PkBudg1000 reduces GWP100 intensity relative to SSP2-NPi "
            "by 40% for district heat and 38% for steel, but only 5% for electricity."
        ),
    )


def _scenario_slide(index: int, print_mode: bool = False):
    slide = _scenario_slide_base(index)
    body = slide.children[1]
    content = list(body.children)
    focus = "summary" if print_mode else "electricity"
    body.children = [
        html.Div(
            [
                html.Span("Focus", className="focus-control-label"),
                dcc.RadioItems(
                    options=[
                        {"label": "Electricity", "value": "electricity"},
                        {"label": "District heat", "value": "heat"},
                        {"label": "Materials", "value": "materials"},
                        {"label": "Summary", "value": "summary"},
                    ],
                    value=focus,
                    inline=True,
                    className="contribution-view-toggle scenario-focus-control",
                    **({} if print_mode else {"id": "scenario-focus-control"}),
                ),
            ],
            className="teaching-focus-toolbar print-expanded-control",
        ),
        html.Div(
            content,
            className=f"scenario-focus-view scenario-focus-{focus}",
            **({} if print_mode else {"id": "scenario-focus-view"}),
        ),
    ]
    return slide


def _prospective_beccs_burdens(pathway: str, year: int) -> dict[str, float]:
    """Return closing BECCS burdens for one operation year of the cohort."""

    values = dict(lifetime_process_contributions("BECCS", pathway, year))
    return {
        "forest_carbon": (
            values["Forest regrowth"] + values["Residual biogenic stack emissions"]
        ),
        "biomass_chp": (
            values["Harvesting and biomass supply"]
            + values["New CHP infrastructure and end-of-life"]
            + values["Other CHP operating emissions"]
        ),
        "avoided_energy": (
            values["Avoided Northern European electricity"]
            + values["Avoided Northern European heat"]
        ),
        "compression": values["Compression and recompression"],
        "transport": (
            values["Pipeline and geological storage"] + values["Transport losses"]
        ),
        "other": sum(
            value
            for label, value in values.items()
            if label
            in {
                "Capture electricity",
                "Capture chemicals and operating materials",
                "CCS infrastructure and end-of-life",
                "Other CHP and CCS supply-chain GHG emissions",
            }
        ),
    }


def _prospective_daccs_burdens(pathway: str, year: int) -> dict[str, float]:
    """Return the complete signed DACCS balance for one cohort operation year."""

    values = dict(lifetime_process_contributions("DACCS", pathway, year))
    return {
        "atmospheric_capture": values["Gross atmospheric CO2 capture"],
        "capture_electricity": values["Direct-capture electricity"],
        "heat_pump_electricity": values["Heat-pump electricity"],
        "compression": values["Compression and recompression"],
        "transport": (
            values["Pipeline and geological storage"] + values["Transport losses"]
        ),
        "other": values["Other supply-chain GHG emissions"],
    }


def _prospective_case_burdens(case: str, pathway: str, year: int) -> dict[str, float]:
    """Return the presentation-ready burden decomposition for either system."""

    if case == "BECCS":
        return _prospective_beccs_burdens(pathway, year)
    if case == "DACCS":
        return _prospective_daccs_burdens(pathway, year)
    raise LookupError(f"Unknown prospective process case: {case}")


def _prospective_categories(case: str) -> tuple[tuple[str, str, str], ...]:
    """Return ordered display metadata for one removal system."""

    if case == "BECCS":
        return (
            ("Forest regrowth − residual stack", "forest_carbon", "#3e7654"),
            ("Harvest + new CHP", "biomass_chp", "#a56a43"),
            ("Avoided Northern European energy", "avoided_energy", "#d99614"),
            ("Compression electricity", "compression", "#2f6478"),
            ("CO₂ transport + storage", "transport", "#7656a8"),
            ("Capture materials + CCS plant", "other", "#7d8d95"),
        )
    if case == "DACCS":
        return (
            ("Atmospheric CO₂ capture", "atmospheric_capture", "#008a82"),
            ("Direct-capture electricity", "capture_electricity", "#4193b8"),
            ("Heat-pump electricity", "heat_pump_electricity", "#d39b32"),
            ("Compression electricity", "compression", "#2f6478"),
            ("CO₂ transport + storage", "transport", "#7656a8"),
            ("Other GHG emissions · sorbent + DAC plant", "other", "#7d8d95"),
        )
    raise LookupError(f"Unknown prospective process case: {case}")


def _focus_year_value(focus_year: str | int | None) -> int | None:
    if focus_year in (None, "all"):
        return None
    year = int(focus_year)
    if year not in {2030, 2040, 2049}:
        raise LookupError(f"Unknown prospective focus year: {focus_year}")
    return year


def _gross_storage_figure(
    years: tuple[int, ...], focus_year: str | int | None = "all"
) -> go.Figure:
    figure = go.Figure()
    focused = _focus_year_value(focus_year)
    for case, pathway, colour, dash, symbol in (
        ("DACCS", "SSP2-NPi", "#4193b8", "solid", "circle"),
        ("DACCS", "SSP2-PkBudg1000", "#4193b8", "dash", "diamond"),
        ("BECCS", "SSP2-NPi", "#3e7654", "solid", "circle"),
        ("BECCS", "SSP2-PkBudg1000", "#3e7654", "dash", "diamond"),
    ):
        series = dict(lifetime_annual_series(case, pathway))
        values = [series[year] for year in years]
        figure.add_trace(
            go.Scatter(
                x=list(years),
                y=values,
                name=f"{case} · {pathway}",
                mode="lines+markers",
                line={"color": colour, "dash": dash, "width": 3.4},
                marker={
                    "color": "white" if dash == "dash" else colour,
                    "line": {"color": colour, "width": 2.2},
                    "size": [
                        11 if focused == year else 8 if focused else 9 for year in years
                    ],
                    "opacity": [
                        1 if focused in (None, year) else 0.28 for year in years
                    ],
                    "symbol": symbol,
                },
                hovertemplate=(
                    "%{x}: %{y:.0f} kg CO₂-eq / net t stored"
                    "<extra>%{fullData.name}</extra>"
                ),
                showlegend=False,
            )
        )
        average = lifetime_score_per_net_tonne(case, pathway)
        figure.add_trace(
            go.Scatter(
                x=[years[0], years[-1]],
                y=[average, average],
                mode="lines",
                line={
                    "color": colour,
                    "dash": "solid" if pathway == "SSP2-NPi" else "dash",
                    "width": 1.5,
                },
                opacity=0.82,
                name=f"{case} · {pathway} lifetime average",
                meta="lifetime-average",
                hovertemplate=(
                    f"lifetime average: {average:.0f} kg CO₂-eq / net t stored"
                    "<extra>%{fullData.name}</extra>"
                ),
                showlegend=False,
            )
        )
    figure.add_hrect(
        y0=-1000,
        y1=-952,
        fillcolor="rgba(62,118,84,.075)",
        line_width=0,
        layer="below",
    )
    figure.add_hrect(
        y0=-940,
        y1=-870,
        fillcolor="rgba(65,147,184,.075)",
        line_width=0,
        layer="below",
    )
    figure.add_annotation(
        x=2030,
        y=-992,
        text="<b>BECCS</b>",
        showarrow=False,
        xanchor="left",
        font={"color": "#315d42", "size": 9},
    )
    figure.add_annotation(
        x=2030,
        y=-873,
        text="<b>DACCS</b>",
        showarrow=False,
        xanchor="left",
        font={"color": "#276c8a", "size": 9},
    )
    if focused:
        figure.add_vline(
            x=focused,
            line_width=1.2,
            line_dash="dot",
            line_color="#0f7f84",
        )
    figure.update_layout(
        autosize=True,
        margin={"l": 58, "r": 18, "t": 8, "b": 42},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f2f6f7",
        font={"family": "Arial, Helvetica, sans-serif", "color": "#17232c", "size": 10},
        hovermode="x unified",
        xaxis={
            "range": [2029.4, 2049.6],
            "tickvals": [2030, 2035, 2040, 2045, 2049],
            "showgrid": False,
            "title": None,
            "zeroline": False,
        },
        yaxis={
            "range": [-1005, -860],
            "dtick": 25,
            "gridcolor": "#dbe4e7",
            "title": "kg CO₂-eq / net t stored",
            "zeroline": False,
        },
    )
    return figure


def _sector_driver_figure(
    sector: str, focus_year: str | int | None = "all"
) -> go.Figure:
    """Render the background intensity that drives a selected contribution."""

    figure = go.Figure()
    focused = _focus_year_value(focus_year)
    scale, unit = (
        (1000, "g CO₂-eq / kWh")
        if sector == "Electricity"
        else (
            1000,
            "kg CO₂-eq / GJ",
        )
    )
    for pathway, dash, symbol in (
        ("SSP2-NPi", "solid", "circle"),
        ("SSP2-PkBudg1000", "dash", "diamond"),
    ):
        series = scenario_sector_series(sector, pathway)
        years = [year for year, _ in series]
        values = [score * scale for _, score in series]
        figure.add_trace(
            go.Scatter(
                x=years,
                y=values,
                name=pathway,
                mode="lines+markers",
                line={"color": "#0f7f84", "dash": dash, "width": 3},
                marker={
                    "size": [
                        10 if focused == year else 7 if focused else 8 for year in years
                    ],
                    "opacity": [
                        1 if focused in (None, year) else 0.28 for year in years
                    ],
                    "symbol": symbol,
                    "color": "white" if dash == "dash" else "#0f7f84",
                    "line": {"color": "#0f7f84", "width": 2},
                },
                hovertemplate=f"%{{x}}: %{{y:.1f}} {unit}<extra>{pathway}</extra>",
                showlegend=False,
            )
        )
    if focused:
        figure.add_vline(
            x=focused,
            line_width=1.2,
            line_dash="dot",
            line_color="#0f7f84",
        )
    figure.update_layout(
        autosize=True,
        margin={"l": 54, "r": 12, "t": 8, "b": 36},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f2f6f7",
        font={"family": "Arial, Helvetica, sans-serif", "color": "#17232c", "size": 9},
        hovermode="x unified",
        xaxis={"tickvals": [2025, 2030, 2050], "showgrid": False},
        yaxis={"title": {"text": unit, "font": {"size": 9}}, "gridcolor": "#dbe4e7"},
    )
    return figure


def _contribution_driver_figure(
    contribution: str, focus_year: str | int | None = "all"
) -> go.Figure:
    """Render one foreground contribution across systems and pathways."""

    years = tuple(range(2030, 2050))
    focused = _focus_year_value(focus_year)
    figure = go.Figure()
    for case, case_colour in (("BECCS", "#3e7654"), ("DACCS", "#4193b8")):
        available = {key for _, key, _ in _prospective_categories(case)}
        if contribution not in available:
            continue
        for pathway, dash, symbol in (
            ("SSP2-NPi", "solid", "circle"),
            ("SSP2-PkBudg1000", "dash", "diamond"),
        ):
            values = [
                _prospective_case_burdens(case, pathway, year)[contribution]
                for year in years
            ]
            figure.add_trace(
                go.Scatter(
                    x=list(years),
                    y=values,
                    name=f"{case} · {pathway}",
                    mode="lines+markers",
                    line={"color": case_colour, "dash": dash, "width": 3},
                    marker={
                        "size": [
                            10 if focused == year else 7 if focused else 8
                            for year in years
                        ],
                        "opacity": [
                            1 if focused in (None, year) else 0.28 for year in years
                        ],
                        "symbol": symbol,
                        "color": "white" if dash == "dash" else case_colour,
                        "line": {"color": case_colour, "width": 2},
                    },
                    hovertemplate=(
                        "%{x}: %{y:.1f} kg CO₂-eq / net t stored"
                        "<extra>%{fullData.name}</extra>"
                    ),
                    showlegend=False,
                )
            )
    if focused:
        figure.add_vline(
            x=focused,
            line_width=1.2,
            line_dash="dot",
            line_color="#0f7f84",
        )
    figure.update_layout(
        autosize=True,
        margin={"l": 54, "r": 12, "t": 8, "b": 36},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f2f6f7",
        font={"family": "Arial, Helvetica, sans-serif", "color": "#17232c", "size": 9},
        hovermode="x unified",
        xaxis={"tickvals": [2030, 2035, 2040, 2045, 2049], "showgrid": False},
        yaxis={
            "rangemode": "tozero",
            "title": {"text": "kg CO₂-eq / net t stored", "font": {"size": 9}},
            "gridcolor": "#dbe4e7",
        },
    )
    return figure


def render_prospective_driver_figure(
    contribution: str = "all", focus_year: str | int | None = "all"
) -> go.Figure:
    """Render the linked driver panel for the active contribution."""

    if contribution == "all":
        return _gross_storage_figure(tuple(range(2030, 2050)), focus_year)
    return _contribution_driver_figure(contribution, focus_year)


def prospective_driver_heading(contribution: str = "all") -> tuple[str, str]:
    """Return kicker and title for the linked driver panel."""

    headings = {
        "all": (
            "2030 cohort · operation through 2049",
            "Annual result + lifetime average",
        ),
        "forest_carbon": (
            "BECCS operation",
            "Forest-carbon balance over the plant life",
        ),
        "atmospheric_capture": (
            "DACCS operation",
            "Atmospheric CO₂ capture",
        ),
        "biomass_chp": ("BECCS operation", "Harvest and new-CHP burden"),
        "avoided_energy": ("BECCS operation", "Avoided Northern European energy"),
        "capture_electricity": ("DACCS operation", "Direct-capture electricity burden"),
        "heat_pump_electricity": ("DACCS operation", "Heat-pump electricity burden"),
        "compression": ("shared operation", "Compression-electricity burden"),
        "transport": ("shared foreground", "CO₂ transport, loss and storage"),
        "other": ("capture systems", "Other materials and GHG over time"),
    }
    return headings.get(contribution, headings["all"])


def render_prospective_driver_legend(contribution: str = "all"):
    """Render the legend appropriate to the linked driver panel."""

    children = []
    if contribution in {"all", "transport", "other"}:
        children.extend(
            [
                html.Span("Case", className="prospective-key-label"),
                html.Span([html.I(className="line-key line-key-daccs"), "DACCS"]),
                html.Span([html.I(className="line-key line-key-beccs"), "BECCS"]),
                html.Span(className="prospective-key-divider"),
            ]
        )
    if contribution == "all":
        children.append(html.Span("Scenario", className="prospective-key-label"))
    children.extend(
        [
            html.Span(
                [html.I(className="line-key line-key-current"), "SSP2-NPi · filled"]
            ),
            html.Span(
                [
                    html.I(className="line-key line-key-budget"),
                    "SSP2-PkBudg1000 · open",
                ]
            ),
        ]
    )
    if contribution == "all":
        children.extend(
            [
                html.Span(className="prospective-key-divider"),
                html.Span(
                    [html.I(className="lifetime-average-key"), "lifetime average"]
                ),
            ]
        )
    return children


def render_prospective_burden_figure(
    case: str = "BECCS",
    view: str = "absolute",
    focus_year: str | int | None = "all",
    contribution: str = "all",
) -> go.Figure:
    """Render one linked grouped-and-stacked burden decomposition."""

    if view not in {"absolute", "change", "share"}:
        view = "absolute"
    focused = _focus_year_value(focus_year)
    years = (2030, 2040, 2049)
    year_categories = [f"year-{year}" for year in years]
    pathways = ("SSP2-NPi", "SSP2-PkBudg1000")
    categories = _prospective_categories(case)
    raw_results = {
        pathway: [_prospective_case_burdens(case, pathway, year) for year in years]
        for pathway in pathways
    }
    raw_magnitudes = {
        pathway: [
            sum(abs(value) for value in row.values()) for row in raw_results[pathway]
        ]
        for pathway in pathways
    }
    if view == "change":
        results = {
            pathway: [
                {
                    key: row[key] - raw_results[pathway][0][key]
                    for _, key, _ in categories
                }
                for row in raw_results[pathway]
            ]
            for pathway in pathways
        }
        units = "kg CO₂-eq change / net t stored"
        hover_value = "%{y:+.1f} kg CO₂-eq from 2030"
        y_range = [-175, 25]
        barmode = "relative"
    elif view == "share":
        results = {
            pathway: [
                {key: 100 * row[key] / magnitude for _, key, _ in categories}
                for row, magnitude in zip(
                    raw_results[pathway], raw_magnitudes[pathway], strict=True
                )
            ]
            for pathway in pathways
        }
        units = "% of absolute contribution magnitude"
        hover_value = "%{y:.1f}% of absolute contribution magnitude"
        y_range = [-110, 110]
        barmode = "relative"
    else:
        results = raw_results
        units = "kg CO₂-eq contribution / net t stored"
        hover_value = "%{y:.1f} kg CO₂-eq"
        y_range = [-1100, 200]
        barmode = "relative"

    totals = {
        pathway: [sum(row.values()) for row in results[pathway]] for pathway in pathways
    }
    figure = go.Figure()
    selected_points = [years.index(focused)] if focused else None
    for pathway in pathways:
        pattern = "" if pathway == "SSP2-NPi" else "/"
        for label, key, colour in categories:
            figure.add_trace(
                go.Bar(
                    x=year_categories,
                    y=[row[key] for row in results[pathway]],
                    name=label,
                    offsetgroup=pathway,
                    legendgroup=pathway,
                    opacity=1 if contribution in {"all", key} else 0.14,
                    selectedpoints=selected_points,
                    selected={"marker": {"opacity": 1}},
                    unselected={"marker": {"opacity": 0.22 if focused else 1}},
                    marker={
                        "color": colour,
                        "line": {"color": "white", "width": 0.7},
                        "pattern": {
                            "shape": pattern,
                            "fgcolor": "rgba(255,255,255,.72)",
                            "solidity": 0.16,
                            "size": 6,
                        },
                    },
                    customdata=[
                        [
                            case,
                            pathway,
                            year,
                            key,
                            label,
                            raw_row[key],
                            100 * raw_row[key] / raw_magnitude,
                        ]
                        for year, raw_row, raw_magnitude in zip(
                            years,
                            raw_results[pathway],
                            raw_magnitudes[pathway],
                            strict=True,
                        )
                    ],
                    hovertemplate=(
                        "%{customdata[2]} · %{customdata[1]}<br>"
                        + hover_value
                        + " · %{customdata[6]:.0f}%"
                        + "<extra>%{fullData.name}</extra>"
                    ),
                    showlegend=False,
                )
            )

    if view != "share":
        for pathway, xshift in (("SSP2-NPi", -17), ("SSP2-PkBudg1000", 17)):
            for year, total in zip(years, totals[pathway], strict=True):
                if view == "change" and year == 2030:
                    continue
                total_label = (
                    f"{total:+.0f}" if view == "change" else f"{total:.0f}"
                ).replace("-", "−")
                figure.add_annotation(
                    x=f"year-{year}",
                    y=total,
                    text=f"◆<br><b>Σ {total_label}</b>",
                    showarrow=False,
                    xshift=xshift,
                    yshift=-12 if view == "change" else 0,
                    opacity=1 if focused in (None, year) else 0.22,
                    bgcolor="rgba(255,255,255,.94)",
                    bordercolor="#8fa4ac",
                    borderpad=1,
                    font={"color": "#0b3b52", "size": 8},
                )

    figure.update_layout(
        autosize=True,
        margin={"l": 44, "r": 8, "t": 8, "b": 31},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f2f6f7",
        font={"family": "Arial, Helvetica, sans-serif", "color": "#17232c", "size": 8},
        barmode=barmode,
        bargap=0.24,
        bargroupgap=0.08,
        hovermode="closest",
        uirevision=f"{case}-{view}-{contribution}",
        xaxis={
            "type": "category",
            "tickvals": year_categories,
            "ticktext": [str(year) for year in years],
            "showgrid": False,
            "title": None,
            "zeroline": False,
            "tickfont": {"size": 9},
        },
        yaxis={
            "range": y_range,
            "dtick": 50 if view in {"change", "share"} else 200,
            "gridcolor": "#dbe4e7",
            "title": {"text": units, "font": {"size": 8}},
            "zeroline": True,
            "zerolinecolor": "#8da0a9",
        },
    )
    return figure


def render_prospective_burden_legend(case: str = "BECCS"):
    """Render the legend matching the selected burden chart."""

    entries = (
        (
            ("Forest carbon", "forest"),
            ("Harvest + new CHP", "other"),
            ("Avoided Northern European energy", "energy"),
            ("Compression electricity", "compression"),
            ("CO₂ transport + storage", "transport"),
            ("Capture materials + CCS plant", "other"),
        )
        if case == "BECCS"
        else (
            ("Atmospheric CO₂ capture", "direct"),
            ("Direct-capture electricity", "electricity"),
            ("Heat-pump electricity", "heatpump"),
            ("Compression electricity", "compression"),
            ("CO₂ transport + storage", "transport"),
            ("Other GHG emissions · sorbent + DAC plant", "other"),
        )
    )
    return [
        html.Span(
            [
                html.I(className=f"contribution-legend-swatch contribution-{tone}"),
                label,
            ],
            className="contribution-legend-item",
        )
        for label, tone in entries
    ]


def _prospective_contribution_options():
    entries = (
        ("All contributions", "all", "all"),
        ("Forest carbon", "forest_carbon", "forest"),
        ("Harvest + new CHP", "biomass_chp", "other"),
        ("Avoided energy", "avoided_energy", "energy"),
        ("Atmospheric uptake", "atmospheric_capture", "direct"),
        ("Capture power", "capture_electricity", "electricity"),
        ("Heat pump", "heat_pump_electricity", "heatpump"),
        ("Compression", "compression", "compression"),
        ("CO₂ transport + storage", "transport", "transport"),
        ("Other GHG emissions", "other", "other"),
    )
    return [
        {
            "label": html.Span(
                [
                    html.I(
                        className=("contribution-legend-swatch " f"contribution-{tone}")
                    ),
                    label,
                ]
            ),
            "value": value,
        }
        for label, value, tone in entries
    ]


def prospective_insight(
    view: str = "absolute",
    focus_year: str | int | None = "all",
    contribution: str = "all",
    hover_data: dict | None = None,
) -> str:
    """Return a concise interpretation for the active interaction state."""

    if hover_data and hover_data.get("points"):
        point = hover_data["points"][0]
        custom = point.get("customdata") or []
        if len(custom) >= 7:
            case, pathway, year, _, label, raw_value, share = custom[:7]
            if view == "change":
                return (
                    f"{case} · {year} · {pathway}: {label} changed by "
                    f"{float(point.get('y', 0)):+.1f} kg CO₂-eq relative to 2030; "
                    f"its contribution in {year} is {float(raw_value):.1f} kg."
                )
            return (
                f"{case} · {year} · {pathway}: {label}: "
                f"{float(raw_value):.1f} kg CO₂-eq, or {float(share):.0f}% "
                "of the absolute contribution magnitude."
            )

    year = _focus_year_value(focus_year) or 2049
    if contribution != "all":
        labels = {
            key: label
            for case in ("BECCS", "DACCS")
            for label, key, _ in _prospective_categories(case)
        }
        comparisons = []
        for case in ("BECCS", "DACCS"):
            if contribution not in {key for _, key, _ in _prospective_categories(case)}:
                continue
            npi = _prospective_case_burdens(case, "SSP2-NPi", year)[contribution]
            pk = _prospective_case_burdens(case, "SSP2-PkBudg1000", year)[contribution]
            comparisons.append(f"{case} {npi:.1f} → {pk:.1f} kg")
        return (
            f"{labels.get(contribution, contribution)} in {year}: "
            + "; ".join(comparisons)
            + " when moving from SSP2-NPi to SSP2-PkBudg1000."
        )

    if focus_year not in (None, "all"):
        gaps = []
        for case in ("BECCS", "DACCS"):
            npi = sum(_prospective_case_burdens(case, "SSP2-NPi", year).values())
            pk = sum(_prospective_case_burdens(case, "SSP2-PkBudg1000", year).values())
            gaps.append(f"{case} {pk - npi:+.1f} kg")
        return (
            f"In {year}, SSP2-PkBudg1000 changes the signed result relative to "
            "SSP2-NPi by " + "; ".join(gaps) + "."
        )

    if view == "change":
        changes = []
        for case in ("BECCS", "DACCS"):
            baseline = sum(
                _prospective_case_burdens(case, "SSP2-PkBudg1000", 2030).values()
            )
            future = sum(
                _prospective_case_burdens(case, "SSP2-PkBudg1000", 2049).values()
            )
            changes.append(f"{case} {future - baseline:+.0f} kg")
        return (
            "Under SSP2-PkBudg1000, the signed result changes from 2030 to 2049 by "
            + "; ".join(changes)
            + "."
        )
    if view == "share":
        baseline = _prospective_daccs_burdens("SSP2-NPi", 2030)
        future = _prospective_daccs_burdens("SSP2-PkBudg1000", 2049)
        capture_2030 = abs(baseline["atmospheric_capture"]) / sum(
            abs(value) for value in baseline.values()
        )
        capture_2049 = abs(future["atmospheric_capture"]) / sum(
            abs(value) for value in future.values()
        )
        return (
            "As positive DACCS burdens fall, atmospheric capture grows from "
            f"{100 * capture_2030:.0f}% to {100 * capture_2049:.0f}% of the absolute "
            "contribution magnitude."
        )

    beccs_npi = lifetime_score_per_net_tonne("BECCS", "SSP2-NPi")
    beccs_pk = lifetime_score_per_net_tonne("BECCS", "SSP2-PkBudg1000")
    daccs_npi = lifetime_score_per_net_tonne("DACCS", "SSP2-NPi")
    daccs_pk = lifetime_score_per_net_tonne("DACCS", "SSP2-PkBudg1000")
    return (
        "Over 2030–2049, switching from SSP2-NPi to SSP2-PkBudg1000 changes the "
        "lifetime average to "
        f"BECCS {_format_score(beccs_npi)} → {_format_score(beccs_pk)} and "
        f"DACCS {_format_score(daccs_npi)} → {_format_score(daccs_pk)} kg CO₂-eq "
        "per net tonne stored."
    )


def prospective_burden_takeaway(case: str = "BECCS") -> str:
    """Return the interpretation shown beneath the selected chart."""

    if case == "DACCS":
        return (
            "The DACCS chart includes the fixed negative atmospheric capture and "
            "separates the positive electricity, transport, plant and material burdens."
        )
    return (
        "Greenfield BECCS includes the new CHP, biomass supply and future forest "
        "regrowth. Exported electricity and net heat displace the matching Northern "
        "European markets in every operating year."
    )


def _prospective_pathway_key():
    """Render the shared style key used by both grouped bar charts."""

    return html.Div(
        [
            html.Span(
                [html.I(className="scenario-bar-key scenario-bar-npi"), "SSP2-NPi"]
            ),
            html.Span(
                [
                    html.I(className="scenario-bar-key scenario-bar-pkbudg"),
                    "SSP2-PkBudg1000",
                ]
            ),
            html.Span(
                [html.I(className="prospective-net-key"), "Σ net result"],
                className="prospective-net-key-item",
            ),
        ],
        className="prospective-pathway-key",
    )


def _prospective_results_base(index: int):
    return _slide_shell(
        index,
        [
            dcc.Store(id="prospective-hover-sync", data={}),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("View", className="prospective-control-label"),
                            dcc.RadioItems(
                                id="prospective-view-control",
                                options=[
                                    {"label": "Absolute", "value": "absolute"},
                                    {"label": "Δ from 2030", "value": "change"},
                                    {"label": "% magnitude", "value": "share"},
                                ],
                                value="absolute",
                                inline=True,
                                persistence=True,
                                persistence_type="session",
                                className="contribution-view-toggle prospective-mode-toggle",
                            ),
                        ],
                        className="prospective-control-group",
                    ),
                    html.Div(
                        [
                            html.Span(
                                "Focus year", className="prospective-control-label"
                            ),
                            dcc.RadioItems(
                                id="prospective-year-control",
                                options=[
                                    {"label": "All", "value": "all"},
                                    {"label": "2030", "value": "2030"},
                                    {"label": "2040", "value": "2040"},
                                    {"label": "2049", "value": "2049"},
                                ],
                                value="all",
                                inline=True,
                                persistence=True,
                                persistence_type="session",
                                className="contribution-view-toggle prospective-year-toggle",
                            ),
                        ],
                        className="prospective-control-group",
                    ),
                    html.Div(
                        [
                            html.Span(
                                "Highlight contribution",
                                className="prospective-control-label",
                            ),
                            dcc.RadioItems(
                                id="prospective-contribution-control",
                                options=_prospective_contribution_options(),
                                value="all",
                                inline=True,
                                persistence=True,
                                persistence_type="session",
                                className="prospective-contribution-toggle",
                            ),
                        ],
                        className=(
                            "prospective-control-group "
                            "prospective-contribution-control"
                        ),
                    ),
                ],
                className="prospective-control-deck",
            ),
            html.Div(
                [
                    _result_panel(
                        "BECCS",
                        html.Div(
                            [
                                _prospective_pathway_key(),
                                dcc.Graph(
                                    id="prospective-beccs-chart",
                                    figure=render_prospective_burden_figure("BECCS"),
                                    clear_on_unhover=True,
                                    config={
                                        "displayModeBar": False,
                                        "responsive": True,
                                    },
                                    className="prospective-chart prospective-process-chart",
                                ),
                            ],
                            className="prospective-chart-wrap",
                        ),
                        kicker="signed contributions",
                    ),
                    _result_panel(
                        "DACCS",
                        html.Div(
                            [
                                _prospective_pathway_key(),
                                dcc.Graph(
                                    id="prospective-daccs-chart",
                                    figure=render_prospective_burden_figure("DACCS"),
                                    clear_on_unhover=True,
                                    config={
                                        "displayModeBar": False,
                                        "responsive": True,
                                    },
                                    className="prospective-chart prospective-process-chart",
                                ),
                            ],
                            className="prospective-chart-wrap",
                        ),
                        kicker="signed contributions",
                    ),
                    _result_panel(
                        html.Span(
                            "Annual result + lifetime average",
                            id="prospective-driver-title",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    render_prospective_driver_legend("all"),
                                    id="prospective-driver-legend",
                                    className="prospective-line-key",
                                ),
                                dcc.Graph(
                                    id="prospective-driver-chart",
                                    figure=render_prospective_driver_figure(),
                                    config={
                                        "displayModeBar": False,
                                        "responsive": True,
                                    },
                                    className="prospective-chart prospective-line-chart",
                                ),
                            ],
                            className="prospective-chart-wrap",
                        ),
                        kicker=html.Span(
                            "2030 cohort · operation through 2049",
                            id="prospective-driver-kicker",
                        ),
                    ),
                ],
                className="result-grid prospective-grid prospective-visual-grid",
            ),
            html.Div(
                [
                    html.Strong("Lifetime result"),
                    html.Span(
                        prospective_insight(),
                        id="prospective-insight-copy",
                    ),
                ],
                className="prospective-takeaway",
            ),
            html.Div(
                "2030 commissioning · 20 operating years · annual REMIND-EU backgrounds · IPCC 2021 GWP100 including biogenic CO₂ · denominator: lifetime physical net atmospheric CO₂ stored after transport loss",
                className="prospective-method-note",
            ),
        ],
        lead=(
            "All panels use 1 net tonne stored after transport losses. Negative values "
            "are atmospheric removals or avoided emissions; positive values are "
            "emissions and supply-chain burdens."
        ),
    )


def _prospective_results(index: int, print_mode: bool = False):
    slide = _prospective_results_base(index)
    body = slide.children[1]
    content = list(body.children)
    controls = content[1]
    control_groups = list(controls.children)
    contribution_control = control_groups.pop()
    control_groups.append(
        html.Details(
            [
                html.Summary("Explore contributors"),
                contribution_control,
            ],
            open=print_mode,
            className="prospective-contributor-details",
        )
    )
    controls.children = control_groups
    scenario_effect = html.Div(
        [
            html.Span("NPi → PkBudg1000", className="scenario-effect-kicker"),
            html.Div(
                [html.Strong("≈ −6 kg"), html.Span("BECCS / net t stored")],
                className="scenario-effect-metric effect-beccs",
            ),
            html.Div(
                [html.Strong("≈ −9 kg"), html.Span("DACCS / net t stored")],
                className="scenario-effect-metric effect-daccs",
            ),
            html.Span(
                "The policy pathway changes both results, but not their ranking.",
                className="scenario-effect-reading",
            ),
        ],
        className="prospective-scenario-effect",
    )
    body.children = [content[0], scenario_effect, controls, *content[2:]]
    heading = slide.children[0]
    heading.children[2] = html.P(
        "The scenario shift is small but systematic. All panels use 1 net tonne stored after transport losses. Negative values are atmospheric removals or avoided emissions; positive values are emissions and supply-chain burdens.",
        className="slide-lead",
    )
    return slide


def _time_intro_base(index: int):
    return _slide_shell(
        index,
        [
            html.Figure(
                html.Img(
                    src="assets/time-story-wood.svg",
                    alt=(
                        "A static LCA diagram places forest growth, use as construction "
                        "timber, and combustion at one reference time. A time-explicit "
                        "diagram places forest growth before construction, stores carbon "
                        "in the building for 60 years, and releases it at end-of-life."
                    ),
                ),
                className="wood-time-comparison",
            ),
            html.Div(
                [
                    html.Article(
                        [
                            html.Span("Common endpoint"),
                            html.Strong(
                                "With a fixed 2100 endpoint, a 2025 emission is counted "
                                "for 75 years; a 2080 emission for 20 years."
                            ),
                            html.Img(
                                src="assets/timing-common-endpoint.svg",
                                alt=(
                                    "A 2025 emission influences 75 years before the "
                                    "common 2100 endpoint, compared with 20 years for "
                                    "an otherwise identical 2080 emission."
                                ),
                                className="wood-time-mini-diagram",
                            ),
                            html.Div(
                                [
                                    html.A(
                                        "Levasseur et al. 2010",
                                        href="https://pubs.acs.org/doi/10.1021/es9030003",
                                        target="_blank",
                                        rel="noopener noreferrer",
                                    ),
                                    html.Span("·"),
                                    html.A(
                                        "Sproul et al. 2019",
                                        href="https://pubs.acs.org/doi/10.1021/acs.est.9b00514",
                                        target="_blank",
                                        rel="noopener noreferrer",
                                    ),
                                ],
                                className="wood-time-reading",
                            ),
                        ],
                        className="wood-time-summary summary-horizon",
                    ),
                    html.Article(
                        [
                            html.Span("Different gas clocks"),
                            html.Strong(
                                "CH₄ causes stronger near-term warming; the CO₂ response "
                                "persists much longer."
                            ),
                            html.Img(
                                src="assets/timing-gas-clocks.svg",
                                alt=(
                                    "Methane has a strong but comparatively short-lived "
                                    "climate response, while the response to carbon "
                                    "dioxide persists much longer."
                                ),
                                className="wood-time-mini-diagram",
                            ),
                            html.Div(
                                [
                                    html.A(
                                        "Balcombe et al. 2018",
                                        href="https://pubs.rsc.org/en/content/articlehtml/2018/em/c8em00414e",
                                        target="_blank",
                                        rel="noopener noreferrer",
                                    ),
                                    html.Span("·"),
                                    html.A(
                                        "Lan & Yao 2022",
                                        href="https://pubs.acs.org/doi/10.1021/acs.est.1c05923",
                                        target="_blank",
                                        rel="noopener noreferrer",
                                    ),
                                ],
                                className="wood-time-reading",
                            ),
                        ],
                        className="wood-time-summary summary-gases",
                    ),
                    html.Article(
                        [
                            html.Span("Peak versus total"),
                            html.Strong(
                                "Equal CO₂-eq totals can follow different climate trajectories."
                            ),
                            html.Img(
                                src="assets/timing-peak-versus-total.svg",
                                alt=(
                                    "A front-loaded and a later emissions pathway have "
                                    "equal totals but different peaks and trajectories."
                                ),
                                className="wood-time-mini-diagram",
                            ),
                            html.Div(
                                [
                                    html.A(
                                        "Schwietzke et al. 2011",
                                        href="https://pubmed.ncbi.nlm.nih.gov/21866889/",
                                        target="_blank",
                                        rel="noopener noreferrer",
                                    ),
                                    html.Span("·"),
                                    html.A(
                                        "Edwards & Trancik 2014",
                                        href="https://www.nature.com/articles/nclimate2204",
                                        target="_blank",
                                        rel="noopener noreferrer",
                                    ),
                                ],
                                className="wood-time-reading",
                            ),
                        ],
                        className="wood-time-summary summary-peak",
                    ),
                ],
                className="wood-time-summary-strip",
            ),
        ],
        lead=(
            "General teaching example—not part of the greenfield BECCS result. Static "
            "LCA omits the time during which carbon remains stored in the wood product."
        ),
    )


def _time_intro(index: int):
    slide = _time_intro_base(index)
    body = slide.children[1]
    summaries = body.children[1]
    summaries.children = [summaries.children[0], summaries.children[2]]
    heading = slide.children[0]
    heading.children[2] = html.P(
        "The same total can produce a different climate trajectory when uptake, storage and release occur in different years.",
        className="slide-lead",
    )
    return slide


def _premise_trails_handoff_combined(index: int):
    return _slide_shell(
        index,
        [
            html.Figure(
                [
                    html.Img(
                        src="assets/premise-trails-handoff.svg",
                        alt=(
                            "IAM assumptions enter premise, which exports paired matrix "
                            "snapshots. TRAILS interpolates a three-dimensional annual "
                            "background, distributes temporal exchanges into dated "
                            "pulses, routes them through a calendar-year network, and "
                            "constructs one inventory matrix G for each year, then "
                            "left-multiplies every annual G matrix by the same diagonal "
                            "Q equals diag of CF matrix for the selected LCIA method."
                        ),
                        className="premise-trails-handoff-base",
                    ),
                    html.Img(
                        src="assets/premise-logo.png",
                        alt="premise logo",
                        className="handoff-brand-logo premise-handoff-logo",
                    ),
                    html.Img(
                        src="assets/trails-logo.png",
                        alt="TRAILS logo",
                        className="handoff-brand-logo trails-handoff-logo",
                    ),
                ],
                className="temporal-method-figure premise-trails-handoff-figure",
            ),
            html.Div(
                [
                    html.Span("Matrix handoff"),
                    html.A(
                        "Sacchi et al. 2022 · premise",
                        href="https://doi.org/10.1016/j.rser.2022.112311",
                        target="_blank",
                        rel="noopener noreferrer",
                    ),
                    html.Span("·"),
                    html.A(
                        "Sacchi et al. 2026 · TRAILS preprint",
                        href="https://www.researchsquare.com/article/rs-10139523/v1",
                        target="_blank",
                        rel="noopener noreferrer",
                    ),
                ],
                className="temporal-method-sources",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("1 · Annual background"),
                            html.Strong(
                                "A(y) links activities; B(y) records elementary flows"
                            ),
                            html.Small(
                                "premise provides matrices for selected IAM years; TRAILS "
                                "interpolates the years between them."
                            ),
                        ],
                        className="handoff-outcome-card handoff-outcome-background",
                    ),
                    html.Div(
                        [
                            html.Span("2 · Dated routing"),
                            html.Strong(
                                "Temporal exchanges assign demand to specific years"
                            ),
                            html.Small(
                                "TRAILS follows selected branches explicitly; remaining "
                                "demand is solved with the background matrix for that year."
                            ),
                        ],
                        className="handoff-outcome-card handoff-outcome-routing",
                    ),
                    html.Div(
                        [
                            html.Span("3 · Traceable result"),
                            html.Strong(
                                "Hᵧ preserves activity, flow and year attribution"
                            ),
                            html.Small(
                                "Annual characterised inventories can be summed or passed "
                                "to a climate model."
                            ),
                        ],
                        className="handoff-outcome-card handoff-outcome-result",
                    ),
                ],
                className="handoff-outcome-strip",
            ),
        ],
        lead=(
            "premise provides background matrices for selected scenario years. TRAILS "
            "interpolates annual matrices and matches each dated demand to its year."
        ),
    )


def _annual_matrices_slide(index: int):
    combined = _premise_trails_handoff_combined(index)
    combined_body = combined.children[1]
    figure, sources = combined_body.children[:2]
    return _slide_shell(
        index,
        [
            figure,
            html.Div(
                [
                    html.Article(
                        [
                            html.Span("01"),
                            html.Strong("Start from IAM anchor years"),
                            html.Small(
                                "2005–2100 snapshots carry scenario-specific technologies and markets."
                            ),
                        ],
                        className="annual-matrix-step",
                    ),
                    html.Article(
                        [
                            html.Span("02"),
                            html.Strong("Interpolate every intervening year"),
                            html.Small(
                                "TRAILS builds a continuous annual background without creating separate packages."
                            ),
                        ],
                        className="annual-matrix-step",
                    ),
                    html.Article(
                        [
                            html.Span("03"),
                            html.Strong("Solve with A(y) and B(y)"),
                            html.Small(
                                "Each calendar year has its own activity links and elementary-flow inventory."
                            ),
                        ],
                        className="annual-matrix-step",
                    ),
                ],
                className="annual-matrix-steps",
            ),
            sources,
        ],
        lead=(
            "premise supplies scenario snapshots; TRAILS interpolates them into annual technosphere A(y) and biosphere B(y) matrices."
        ),
    )


def _dated_inventories_slide(index: int):
    combined = _premise_trails_handoff_combined(index)
    combined_body = combined.children[1]
    figure, sources = combined_body.children[:2]
    route_steps = (
        ("01", "Distribute", "Turn each temporal exchange into dated demand."),
        ("02", "Route", "Follow the selected foreground branches explicitly."),
        ("03", "Stop", "Solve remaining demand in that calendar year's background."),
        (
            "04",
            "Characterise",
            "Build and score one attributable inventory for each year.",
        ),
    )
    return _slide_shell(
        index,
        [
            figure,
            html.Div(
                [
                    html.Article(
                        [html.Span(number), html.Strong(title), html.Small(note)],
                        className="dated-routing-step",
                    )
                    for number, title, note in route_steps
                ],
                className="dated-routing-steps",
            ),
            html.Div(
                [
                    sources,
                    html.Button(
                        "Q, Gᵧ and Hᵧ matrix details: Appendix A →",
                        id={"type": "chapter-button", "slide": APPENDIX_START_SLIDE},
                        n_clicks=0,
                        className="appendix-link-button",
                    ),
                ],
                className="dated-routing-footer",
            ),
        ],
        lead=(
            "Dated exchanges are routed until demand is stopped in a year-specific background, then characterised annually."
        ),
    )


def _case_timing(index: int):
    return _slide_shell(
        index,
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Example: operating year or end-of-life"),
                            html.Span(
                                "Select 2030–2049 to trace an operating cohort; select 2050 to isolate end-of-life."
                            ),
                        ],
                        className="case-timing-control-copy",
                    ),
                    dcc.RadioItems(
                        id="case-timing-year",
                        options=[
                            {"label": "2030", "value": "2030"},
                            {"label": "2040", "value": "2040"},
                            {"label": "2049", "value": "2049"},
                            {"label": "2050", "value": "2050"},
                        ],
                        value="2030",
                        inline=True,
                        className="case-timing-year-toggle",
                    ),
                ],
                className="case-timing-control-deck",
            ),
            html.Figure(
                html.Img(
                    id="case-timing-image",
                    src="assets/case-temporal-distributions.svg#y2030",
                    alt=(
                        "Aligned BECCS and DACCS cohort timelines. Both operate "
                        "annually from 2030 through 2049. The shared forest, biomass "
                        "history is shown once and cancelled. The greenfield BECCS "
                        "route then shows a new CHP+CCS build, twenty annual harvest, "
                        "operation, energy-export, capture and storage cohorts, one "
                        "end-of-life event, and future forest regrowth through 2132. "
                        "DACCS has a three-year construction period and one end-of-life "
                        "event. Both cases show the atmosphere and connect their annual "
                        "actions to every operating year. The selected state links an "
                        "operating cohort to that year's background, or isolates the "
                        "one-off equipment end-of-life event in 2050."
                    ),
                ),
                className="temporal-method-figure case-temporal-figure",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Shared history cancels"),
                            html.Span("before the project decision"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("2050 end-of-life"),
                            html.Span("one equipment event"),
                        ]
                    ),
                    html.Div(
                        [html.Strong("Regrowth to 2132"), html.Span("BECCS only")]
                    ),
                ],
                className="timeline-callout-strip",
            ),
            html.Div(
                [
                    html.Span("Timing anchors"),
                    html.A(
                        "Sacchi et al. 2026 · temporal routing",
                        href="https://www.researchsquare.com/article/rs-10139523/v1",
                        target="_blank",
                        rel="noopener noreferrer",
                    ),
                ],
                className="temporal-method-sources",
            ),
        ],
        lead=(
            "Construction occurs in 2027–2029; twenty operating cohorts run from 2030 "
            "to 2049; end-of-life occurs in 2050; each harvest triggers 83 years of regrowth."
        ),
    )


TEMPORAL_GWP_CASES = {
    "BECCS": {
        "title": "BECCS · new CHP+CCS",
        "accent": "#3e7654",
        "storage": "20 years · 149 kt net CO₂ stored",
    },
    "DACCS": {
        "title": "DACCS · solid sorbent",
        "accent": "#4193b8",
        "storage": "20 years · 1.944 Mt net CO₂ stored",
    },
}

TEMPORAL_GWP_CALCULATION_YEARS = tuple(range(1940, 2141))
TEMPORAL_GWP_VIEW_RANGE = (1940, 2140)
TEMPORAL_GWP_MAX_LEGEND_HANDLES = 10
TEMPORAL_GWP_STATIC_PATHWAY = "SSP2-PkBudg1000"
TEMPORAL_GWP_STATIC_REFERENCES = (
    (2025, "#667981", "longdash"),
    (2030, "#00728a", "dot"),
)


def _temporal_grouped_score_series(
    case: str, normalization: str
) -> tuple[tuple[str, tuple[tuple[int, float], ...]], ...]:
    """Return the reviewed root-attributed process categories for the slide."""

    return cohort_temporal_score_series(case, normalization)


def _temporal_contributor_label(case: str, contributor: str) -> str:
    del case
    if contributor in {
        "Forest regrowth",
        "Harvesting and biomass supply",
        "Residual biogenic stack emissions",
        "New CHP infrastructure and end-of-life",
        "Other CHP operating emissions",
        "Avoided Northern European electricity",
        "Avoided Northern European heat",
        "Capture electricity",
        "Capture chemicals and operating materials",
        "Compression and recompression",
        "Pipeline and geological storage",
        "Transport losses",
        "CCS infrastructure and end-of-life",
        "Other CHP and CCS supply-chain GHG emissions",
    }:
        return contributor
    labels = (
        (
            "carbon dioxide, captured and stored, with a sorbent-based",
            "Atmospheric CO₂ capture",
        ),
        ("softwood forestry, spruce", "Spruce forestry"),
        (
            "heat and power co-generation, wood chips, 6667 kW, state-of-the-art 2014 | electricity",
            "CHP electricity",
        ),
        (
            "heat and power co-generation, wood chips, 6667 kW, state-of-the-art 2014 | heat",
            "CHP heat",
        ),
        (
            "electricity production, Nordic spruce CHP with post-combustion CCS",
            "Retrofit electricity balance",
        ),
        (
            "heat production, Nordic spruce CHP with post-combustion CCS",
            "Retrofit heat balance",
        ),
        ("carbon dioxide transport extension", "Pipeline extension"),
        (
            "carbon dioxide compression, transport and storage",
            "Compression, transport & storage",
        ),
        (
            "carbon dioxide, captured and stored, at Nordic spruce CHP",
            "Post-combustion capture",
        ),
        ("amine-based silica production", "Sorbent make-up"),
        ("market group for electricity, medium voltage", "Electricity"),
        (
            "treatment of direct air capture system",
            "DAC plant end-of-life",
        ),
        (
            "direct air capture system, sorbent-based, 100ktCO2",
            "DAC plant infrastructure",
        ),
        ("market for reinforcing steel", "Reinforcing steel"),
        ("market for drawing of pipe, steel", "Steel pipe production"),
        ("market for diesel, burned", "Construction diesel"),
        ("market for bitumen seal", "Bitumen seal"),
        ("market for polyethylene, low density", "Polyethylene"),
        ("market for sand", "Sand"),
        ("market for transport, freight, lorry", "Freight transport"),
        (
            "treatment of waste reinforcement steel",
            "Steel recycling",
        ),
        ("treatment of waste polyethylene", "Polyethylene end-of-life"),
        ("treatment of waste bitumen", "Bitumen end-of-life"),
    )
    for pattern, label in labels:
        if pattern in contributor:
            return label
    return contributor.split(" | ", 1)[0]


def _temporal_contributor_colour(case: str, contributor: str) -> str:
    grouped_colours = {
        "Forest regrowth": "#3e7654",
        "Harvesting and biomass supply": "#a56a43",
        "Residual biogenic stack emissions": "#c44e52",
        "New CHP infrastructure and end-of-life": "#607983",
        "Other CHP operating emissions": "#8c6d5a",
        "Avoided Northern European electricity": "#d99614",
        "Avoided Northern European heat": "#e6ab02",
        "Capture electricity": "#4193b8",
        "Capture chemicals and operating materials": "#cc79a7",
        "Compression and recompression": "#6f4e7c",
        "Pipeline and geological storage": "#0072b2",
        "Transport losses": "#d55e00",
        "CCS infrastructure and end-of-life": "#607983",
        "Other CHP and CCS supply-chain GHG emissions": "#78909c",
    }
    if contributor in grouped_colours:
        return grouped_colours[contributor]
    colours = (
        ("carbon dioxide, captured and stored, with a sorbent-based", "#008a82"),
        ("softwood forestry, spruce", "#3e7654"),
        (
            "heat and power co-generation, wood chips, 6667 kW, state-of-the-art 2014 | electricity",
            "#4193b8",
        ),
        (
            "heat and power co-generation, wood chips, 6667 kW, state-of-the-art 2014 | heat",
            "#d99614",
        ),
        (
            "electricity production, Nordic spruce CHP with post-combustion CCS",
            "#2f6478",
        ),
        (
            "heat production, Nordic spruce CHP with post-combustion CCS",
            "#c44e52",
        ),
        ("carbon dioxide transport extension", "#d55e00"),
        ("carbon dioxide compression, transport and storage", "#6f4e7c"),
        ("carbon dioxide, captured and stored, at Nordic spruce CHP", "#2f6478"),
        ("amine-based silica production", "#cc79a7"),
        ("market group for electricity, medium voltage", "#4c78a8"),
        ("treatment of direct air capture system", "#e15759"),
        ("direct air capture system, sorbent-based, 100ktCO2", "#59a14f"),
        ("market for reinforcing steel", "#8c564b"),
        ("market for drawing of pipe, steel", "#4e79a7"),
        ("market for diesel, burned", "#e6ab02"),
        ("market for bitumen seal", "#b07aa1"),
        ("market for polyethylene, low density", "#17a2b8"),
        ("market for sand", "#7b8f00"),
        ("market for transport, freight, lorry", "#e17c05"),
        ("treatment of waste reinforcement steel", "#6b7280"),
        ("treatment of waste polyethylene", "#ff9da7"),
        ("treatment of waste bitumen", "#9c755f"),
    )
    for pattern, colour in colours:
        if pattern in contributor:
            return colour
    return "#78909c"


def _hex_rgba(colour: str, alpha: float) -> str:
    value = colour.lstrip("#")
    red, green, blue = (
        int(value[position : position + 2], 16) for position in (0, 2, 4)
    )
    return f"rgba({red},{green},{blue},{alpha})"


def _temporal_gwp_extents(
    case: str, normalization: str, area_mode: str
) -> tuple[float, float, float, float]:
    """Return annual and cumulative extrema for one temporal-score panel."""

    years = list(TEMPORAL_GWP_CALCULATION_YEARS)
    scale = 1e6 if normalization == "cohort" else 1.0
    values_by_contributor: list[list[float]] = []
    annual_totals = [0.0] * len(years)
    for _contributor, series in _temporal_grouped_score_series(case, normalization):
        annual = dict(series)
        values = [annual.get(year, 0.0) / scale for year in years]
        values_by_contributor.append(values)
        annual_totals = [
            total + value for total, value in zip(annual_totals, values, strict=True)
        ]

    if area_mode == "stacked":
        annual_min = min(
            sum(min(values[position], 0.0) for values in values_by_contributor)
            for position in range(len(years))
        )
        annual_max = max(
            sum(max(values[position], 0.0) for values in values_by_contributor)
            for position in range(len(years))
        )
    else:
        annual_min = min(min(values) for values in values_by_contributor)
        annual_max = max(max(values) for values in values_by_contributor)

    cumulative_values: list[float] = []
    cumulative_score = 0.0
    for value in annual_totals:
        cumulative_score += value
        cumulative_values.append(cumulative_score)
    return (
        annual_min,
        annual_max,
        min(min(cumulative_values), 0.0),
        max(max(cumulative_values), 0.0),
    )


def _padded_axis_extent(
    lower: float, upper: float, padding_fraction: float = 0.04
) -> tuple[float, float]:
    span = max(upper - lower, 1e-12)
    return (
        min(lower, 0.0) - padding_fraction * span,
        max(upper, 0.0) + padding_fraction * span,
    )


def _axis_range_at_zero_fraction(
    lower: float, upper: float, zero_fraction: float
) -> list[float]:
    """Expand an extent so zero occupies a requested fraction of axis height."""

    zero_fraction = min(max(float(zero_fraction), 0.12), 0.88)
    required_span = max(
        max(-lower, 0.0) / zero_fraction,
        max(upper, 0.0) / (1.0 - zero_fraction),
        1e-12,
    )
    return [
        -zero_fraction * required_span,
        (1.0 - zero_fraction) * required_span,
    ]


def _temporal_gwp_axis_ranges(
    normalization: str, area_mode: str
) -> dict[str, tuple[list[float], list[float]]]:
    """Synchronize zero height and comparable secondary axes across panels."""

    extents = {
        case: _temporal_gwp_extents(case, normalization, area_mode)
        for case in TEMPORAL_GWP_CASES
    }
    padded_annual = {
        case: _padded_axis_extent(values[0], values[1])
        for case, values in extents.items()
    }
    local_zero_fractions = [
        -lower / (upper - lower) for lower, upper in padded_annual.values()
    ]
    shared_zero_fraction = sum(local_zero_fractions) / len(local_zero_fractions)

    if normalization == "per_tonne":
        common_annual = _axis_range_at_zero_fraction(
            min(lower for lower, _upper in padded_annual.values()),
            max(upper for _lower, upper in padded_annual.values()),
            shared_zero_fraction,
        )
        annual_ranges = {case: list(common_annual) for case in TEMPORAL_GWP_CASES}
    else:
        annual_ranges = {
            case: _axis_range_at_zero_fraction(lower, upper, shared_zero_fraction)
            for case, (lower, upper) in padded_annual.items()
        }
    if normalization == "per_tonne":
        # Static 2025 and prospective 2030 benchmarks live on the cumulative
        # axis too. Include them explicitly and give this shared comparison
        # scale extra breathing room so neither panel clips a reference line.
        padded_cumulative = {}
        for case, values in extents.items():
            reference_values = [
                _temporal_static_gwp_reference(case, year, normalization)
                for year, _colour, _dash in TEMPORAL_GWP_STATIC_REFERENCES
            ]
            padded_cumulative[case] = _padded_axis_extent(
                min(values[2], *reference_values),
                max(values[3], *reference_values),
                padding_fraction=0.08,
            )
        common_cumulative = _axis_range_at_zero_fraction(
            min(lower for lower, _upper in padded_cumulative.values()),
            max(upper for _lower, upper in padded_cumulative.values()),
            shared_zero_fraction,
        )
        cumulative_ranges = {
            case: list(common_cumulative) for case in TEMPORAL_GWP_CASES
        }
    else:
        padded_cumulative = {
            case: _padded_axis_extent(values[2], values[3])
            for case, values in extents.items()
        }
        cumulative_ranges = {
            case: _axis_range_at_zero_fraction(lower, upper, shared_zero_fraction)
            for case, (lower, upper) in padded_cumulative.items()
        }
    return {
        case: (annual_ranges[case], cumulative_ranges[case])
        for case in TEMPORAL_GWP_CASES
    }


def _temporal_static_gwp_reference(case: str, year: int, normalization: str) -> float:
    """Return a static GWP100 benchmark in the cumulative-axis unit."""

    chp_treatment = (
        "new CHP+CCS vs standing forest and Northern European energy"
        if case == "BECCS"
        else "not applicable"
    )
    value_per_tonne = static_score(
        case,
        TEMPORAL_GWP_STATIC_PATHWAY,
        year,
        chp_treatment,
    )
    if normalization == "per_tonne":
        return value_per_tonne
    return value_per_tonne * lifetime_net_storage_tonnes(case) / 1e6


def render_temporal_gwp_figure(
    case: str,
    normalization: str = "cohort",
    area_mode: str = "stacked",
) -> go.Figure:
    """Render the slide-16 chart in the style of TRAILS temporal-score plots."""

    if case not in TEMPORAL_GWP_CASES:
        raise ValueError(f"Unknown temporal GWP case: {case}.")
    if normalization not in {"cohort", "per_tonne"}:
        normalization = "cohort"
    if area_mode not in {"stacked", "unstacked"}:
        area_mode = "stacked"
    scale = 1e6 if normalization == "cohort" else 1.0
    unit = (
        "kt CO₂-eq per year"
        if normalization == "cohort"
        else "kg CO₂-eq per net t stored · year"
    )
    series_by_contributor = _temporal_grouped_score_series(case, normalization)
    years = list(TEMPORAL_GWP_CALCULATION_YEARS)
    totals = {year: 0.0 for year in years}
    figure = go.Figure()
    for contributor_index, (contributor, series) in enumerate(series_by_contributor):
        annual = dict(series)
        values = [annual.get(year, 0.0) / scale for year in years]
        for year, value in zip(years, values, strict=True):
            totals[year] += value
        colour = _temporal_contributor_colour(case, contributor)
        label = _temporal_contributor_label(case, contributor)
        # Reserve one handle for the cumulative curve and two for the static
        # reference lines in the per-tonne view.
        show_in_legend = contributor_index < TEMPORAL_GWP_MAX_LEGEND_HANDLES - 3
        hover = (
            "<b>%{fullData.name}</b><br>"
            "Year %{x}<br>%{y:.3g} "
            f"{unit}<extra></extra>"
        )
        if area_mode == "unstacked":
            figure.add_trace(
                go.Scatter(
                    x=years,
                    y=values,
                    name=label,
                    legendgroup=label,
                    showlegend=show_in_legend,
                    mode="lines",
                    line={"color": colour, "width": 1.7},
                    fill="tozeroy",
                    fillcolor=_hex_rgba(colour, 0.34),
                    opacity=0.86,
                    hovertemplate=hover,
                )
            )
            continue

        positive = [max(value, 0.0) for value in values]
        negative = [min(value, 0.0) for value in values]
        has_positive = any(value != 0.0 for value in positive)
        has_negative = any(value != 0.0 for value in negative)
        if has_positive:
            figure.add_trace(
                go.Scatter(
                    x=years,
                    y=positive,
                    name=label,
                    legendgroup=label,
                    showlegend=show_in_legend,
                    mode="lines",
                    line={"color": colour, "width": 1.1},
                    fillcolor=_hex_rgba(colour, 0.62),
                    stackgroup="positive",
                    hoverinfo="skip",
                )
            )
        if has_negative:
            figure.add_trace(
                go.Scatter(
                    x=years,
                    y=negative,
                    name=label,
                    legendgroup=label,
                    showlegend=show_in_legend and not has_positive,
                    mode="lines",
                    line={"color": colour, "width": 1.1},
                    fillcolor=_hex_rgba(colour, 0.62),
                    stackgroup="negative",
                    hoverinfo="skip",
                )
            )
        # Stacked areas use separate positive and negative rendering traces.
        # One invisible marker proxy per contributor provides a uniform colored
        # dot and one signed value in Plotly's unified hover popup.
        figure.add_trace(
            go.Scatter(
                x=years,
                y=values,
                name=label,
                legendgroup=label,
                showlegend=False,
                mode="markers",
                marker={"color": colour, "size": 0.1},
                hovertemplate=hover,
            )
        )
    cumulative_values: list[float] = []
    cumulative_score = 0.0
    for year in years:
        cumulative_score += totals[year]
        cumulative_values.append(cumulative_score)
    cumulative_unit = (
        "kt CO₂-eq" if normalization == "cohort" else "kg CO₂-eq per net t stored"
    )
    figure.add_trace(
        go.Scatter(
            x=years,
            y=cumulative_values,
            name="Cumulative GWP100",
            showlegend=True,
            mode="lines",
            line={"color": "#c44e52", "width": 4.0},
            yaxis="y2",
            hovertemplate=(
                "<b>Cumulative GWP100</b><br>Up to %{x}<br>%{y:.3g} "
                f"{cumulative_unit}<extra></extra>"
            ),
        )
    )

    annual_range, cumulative_range = _temporal_gwp_axis_ranges(
        normalization, area_mode
    )[case]
    figure.add_vrect(
        x0=2030,
        x1=2050,
        fillcolor=_hex_rgba(TEMPORAL_GWP_CASES[case]["accent"], 0.08),
        line_width=0,
        layer="below",
    )
    if case == "BECCS":
        figure.add_vrect(
            x0=2030,
            x1=2132,
            fillcolor="rgba(62,118,84,0.045)",
            line_width=0,
            layer="below",
            annotation_text="replacement-stand regrowth",
            annotation_position="bottom right",
            annotation_font_size=9,
            annotation_font_color="#3e7654",
        )
        figure.add_vrect(
            x0=TEMPORAL_GWP_VIEW_RANGE[0],
            x1=2026.999,
            fillcolor="rgba(120,144,156,0.10)",
            line_width=0,
            layer="below",
            annotation_text="shared pre-decision forest history cancels",
            annotation_position="top left",
            annotation_font_size=9,
            annotation_font_color="#60757e",
        )
    figure.add_vline(x=2030, line_width=1.1, line_dash="dot", line_color="#60747c")
    if normalization == "per_tonne":
        for reference_year, colour, dash in TEMPORAL_GWP_STATIC_REFERENCES:
            reference_value = _temporal_static_gwp_reference(
                case, reference_year, normalization
            )
            reference_label = (
                "Current static GWP100 · 2025"
                if reference_year == 2025
                else "Prospective static GWP100 · 2030"
            )
            figure.add_trace(
                go.Scatter(
                    x=list(TEMPORAL_GWP_VIEW_RANGE),
                    y=[reference_value, reference_value],
                    name=reference_label,
                    mode="lines",
                    line={"color": colour, "width": 1.8, "dash": dash},
                    yaxis="y2",
                    showlegend=True,
                    hoverinfo="skip",
                    meta="static-gwp-reference",
                )
            )
    figure.update_layout(
        autosize=True,
        margin={"l": 58, "r": 59, "t": 80, "b": 42},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f2f6f7",
        font={
            "family": "Arial, Helvetica, sans-serif",
            "color": "#17232c",
            "size": 10,
        },
        legend={
            "orientation": "h",
            "y": 1.04,
            "x": 0,
            "yanchor": "bottom",
            "font": {"size": 8},
            "tracegroupgap": 2,
        },
        xaxis={
            "range": list(TEMPORAL_GWP_VIEW_RANGE),
            "tick0": 1940,
            "dtick": 20,
            "title": None,
            "showgrid": True,
            "gridcolor": "#dce5e8",
            "zeroline": False,
        },
        yaxis={
            "title": {"text": unit, "standoff": 5},
            "range": annual_range,
            "showgrid": True,
            "gridcolor": "#dce5e8",
            "zeroline": True,
            "zerolinecolor": "#7f929a",
            "zerolinewidth": 1.2,
        },
        yaxis2={
            "title": {
                "text": f"Cumulative GWP100 · {cumulative_unit}",
                "font": {"color": "#c44e52", "size": 9},
                "standoff": 4,
            },
            "range": cumulative_range,
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
            "zeroline": False,
            "tickfont": {"color": "#c44e52", "size": 8},
        },
        hovermode="x unified",
        hoverlabel={"namelength": -1},
        uirevision=f"temporal-gwp-{case}-{normalization}-{area_mode}",
    )
    return figure


def temporal_gwp_total_label(case: str, normalization: str = "cohort") -> str:
    value = sum(
        score
        for _contributor, series in _temporal_grouped_score_series(case, normalization)
        for _year, score in series
    )
    if normalization == "per_tonne":
        return f"{value:,.0f} kg CO₂-eq / net t stored"
    return f"{value / 1e9:,.3f} Mt CO₂-eq / cohort"


def _temporal_gwp_slide(index: int):
    normalization = "per_tonne"
    area_mode = "stacked"
    panels = []
    for case in ("BECCS", "DACCS"):
        settings = TEMPORAL_GWP_CASES[case]
        panels.append(
            html.Article(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(className="temporal-case-dot"),
                                    html.H3(settings["title"]),
                                ],
                                className="temporal-case-title",
                            ),
                            html.Span(
                                settings["storage"], className="temporal-storage"
                            ),
                        ],
                        className="temporal-gwp-panel-heading",
                    ),
                    dcc.Graph(
                        id=f"temporal-gwp-{case.lower()}-chart",
                        figure=render_temporal_gwp_figure(
                            case, normalization, area_mode
                        ),
                        config={
                            "displayModeBar": False,
                            "responsive": True,
                            "scrollZoom": False,
                        },
                        className="temporal-gwp-chart",
                    ),
                    html.Div(
                        [
                            html.Span("Cohort GWP100 total"),
                            html.Strong(
                                temporal_gwp_total_label(case, normalization),
                                id=f"temporal-gwp-{case.lower()}-total",
                            ),
                        ],
                        className="temporal-gwp-total",
                    ),
                ],
                className=(f"temporal-gwp-panel temporal-gwp-panel-{case.lower()}"),
            )
        )
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Strong("Display"),
                                html.Span(
                                    "BECCS: shared pre-decision forest history cancels. "
                                    "DACCS: negative pre-2030 electricity contributions "
                                    "are upstream biogenic uptake, not plant operation."
                                ),
                            ],
                            className="temporal-gwp-control-copy",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("Normalisation"),
                                        dcc.RadioItems(
                                            id="temporal-gwp-normalization-toggle",
                                            options=[
                                                {
                                                    "label": "Per net tonne stored",
                                                    "value": "per_tonne",
                                                },
                                                {
                                                    "label": "Whole cohort",
                                                    "value": "cohort",
                                                },
                                            ],
                                            value=normalization,
                                            inline=True,
                                            className=(
                                                "contribution-view-toggle "
                                                "temporal-gwp-toggle "
                                                "temporal-gwp-normalization-toggle"
                                            ),
                                        ),
                                    ],
                                    className="temporal-gwp-control-group",
                                ),
                                html.Div(
                                    [
                                        html.Span("Areas"),
                                        dcc.RadioItems(
                                            id="temporal-gwp-area-toggle",
                                            options=[
                                                {
                                                    "label": "Stacked",
                                                    "value": "stacked",
                                                },
                                                {
                                                    "label": "Unstacked",
                                                    "value": "unstacked",
                                                },
                                            ],
                                            value=area_mode,
                                            inline=True,
                                            className=(
                                                "contribution-view-toggle "
                                                "temporal-gwp-toggle "
                                                "temporal-gwp-area-toggle"
                                            ),
                                        ),
                                    ],
                                    className="temporal-gwp-control-group",
                                ),
                            ],
                            className="temporal-gwp-controls",
                        ),
                    ],
                    className="temporal-gwp-toolbar",
                ),
                html.Div(panels, className="temporal-gwp-grid"),
                html.Div(
                    [
                        html.Span("Negative area", className="temporal-sign negative"),
                        html.Span("atmospheric CO₂ uptake or avoided emissions"),
                        html.Span("Positive area", className="temporal-sign positive"),
                        html.Span("emissions to air and supply-chain GHG burdens"),
                        html.Span(
                            "Thick red curve", className="temporal-sign cumulative"
                        ),
                        html.Span("cumulative GWP100 on the right axis"),
                        html.Span("·"),
                        html.Span(
                            "GWP100 incl. biogenic CO₂ · uptake-only forest baseline · SSP2-PkBudg1000 · Northern Europe · 2030 cohort"
                        ),
                    ],
                    className="temporal-gwp-note",
                ),
            ],
            className="temporal-gwp-slide",
        ),
        eyebrow="Time-explicit LCA · TRAILS temporal scores",
        lead=(
            "Annual areas locate each GWP100 contribution in time; the red line shows "
            "the cumulative cohort score."
        ),
    )


FAIR_RESPONSE_METRICS = {
    "radiative forcing": {
        "label": "Radiative forcing",
        "axis": "10⁻¹² W m⁻² per net t stored",
        "footer": "Net forcing in 2300",
        "unit": "× 10⁻¹² W m⁻² / net t",
    },
    "temperature anomaly": {
        "label": "Temperature anomaly",
        "axis": "10⁻¹² °C per net t stored",
        "footer": "Temperature anomaly in 2300",
        "unit": "× 10⁻¹² °C / net t",
    },
}
FAIR_RESPONSE_VIEWS = {"process", "elementary_flow"}
FAIR_RESPONSE_QUANTILES = (2.5, 50.0, 97.5)
FAIR_RESPONSE_MAX_FLOW_GROUPS = 6
FAIR_RESPONSE_SCALE = 1e12
FAIR_RESPONSE_VIEW_RANGE = (1940, 2300)
FAIR_RESPONSE_COMPARISON_YEAR = 2100
FAIR_RESPONSE_COMPARISON_COLOUR = "#3e7654"
FAIR_RESPONSE_YEAR_MARKER_NAME = "Selected comparison year"
FAIR_RESPONSE_REFERENCE_NAME = "BECCS median response at selected year"
FAIR_RESPONSE_YEAR_MARKER_SHAPE_INDEX = 0


def fair_response_comparison_year(
    relayout_data: dict | None,
    current_year: int = FAIR_RESPONSE_COMPARISON_YEAR,
) -> int:
    """Return a rounded comparison year from a Plotly shape-drag event."""

    candidates = []
    if isinstance(relayout_data, dict):
        for coordinate in ("x0", "x1"):
            key = f"shapes[{FAIR_RESPONSE_YEAR_MARKER_SHAPE_INDEX}].{coordinate}"
            if key in relayout_data:
                candidates.append(relayout_data[key])

        shapes = relayout_data.get("shapes")
        if isinstance(shapes, list):
            for shape in shapes:
                if not isinstance(shape, dict):
                    continue
                if shape.get("name") != FAIR_RESPONSE_YEAR_MARKER_NAME:
                    continue
                candidates.extend(
                    shape[coordinate]
                    for coordinate in ("x0", "x1")
                    if coordinate in shape
                )
                break

    numeric_candidates = []
    for candidate in candidates:
        try:
            value = float(candidate)
        except (TypeError, ValueError):
            continue
        if isfinite(value):
            numeric_candidates.append(value)

    if not numeric_candidates:
        return int(current_year)
    year = int(sum(numeric_candidates) / len(numeric_candidates) + 0.5)
    return max(FAIR_RESPONSE_VIEW_RANGE[0], min(FAIR_RESPONSE_VIEW_RANGE[1], year))


def _fair_response_display_series(
    case: str,
    metric: str,
    contribution_view: str,
    quantile: float = 50.0,
) -> tuple[tuple[str, tuple[tuple[int, float], ...]], ...]:
    """Return slide-ready FaIR contributors, grouping only the long flow tail."""

    raw = cohort_fair_response_series(case, metric, contribution_view, quantile)
    if (
        contribution_view != "elementary_flow"
        or len(raw) <= FAIR_RESPONSE_MAX_FLOW_GROUPS
    ):
        return raw
    median = cohort_fair_response_series(case, metric, contribution_view, 50.0)
    retained = {
        contributor
        for contributor, _series in median[: FAIR_RESPONSE_MAX_FLOW_GROUPS - 1]
    }
    grouped: dict[str, dict[int, float]] = {}
    for contributor, series in raw:
        label = (
            contributor if contributor in retained else "Other mapped elementary flows"
        )
        annual = grouped.setdefault(label, {})
        for year, value in series:
            annual[year] = annual.get(year, 0.0) + value
    order = [name for name, _series in median if name in retained]
    order.append("Other mapped elementary flows")
    return tuple(
        (name, tuple(sorted(grouped[name].items())))
        for name in order
        if name in grouped
    )


def _fair_flow_label(contributor: str) -> str:
    labels = {
        "Carbon dioxide, in air": "Atmospheric CO₂ uptake",
        "Carbon dioxide, fossil": "Fossil CO₂",
        "Carbon dioxide, non-fossil": "Biogenic CO₂ release",
        "Carbon dioxide, from soil or biomass stock": "Biogenic CO₂",
        "Methane, fossil": "Fossil CH₄",
        "Methane, non-fossil": "Biogenic CH₄",
        "Methane, from soil or biomass stock": "Biogenic CH₄",
        "Dinitrogen monoxide": "N₂O",
    }
    return labels.get(contributor, contributor)


def _fair_response_label(contribution_view: str, contributor: str) -> str:
    if contribution_view == "process":
        compact = {
            "Biogenic CO₂ uptake": "Biogenic uptake",
            "Biomass supply-chain emissions": "Biomass supply chain",
            "Uncaptured CHP emissions": "Uncaptured CHP emissions",
        }
        if contributor in compact:
            return compact[contributor]
        if "carbon dioxide compression, transport and storage" in contributor:
            return "Compression & storage"
        if "carbon dioxide, captured and stored, at Nordic spruce CHP" in contributor:
            return "Capture plant"
        return _temporal_contributor_label("BECCS", contributor)
    return _fair_flow_label(contributor)


def _fair_response_colour(case: str, contribution_view: str, contributor: str) -> str:
    if contribution_view == "process":
        return _temporal_contributor_colour(case, contributor)
    flow_colours = (
        ("Carbon dioxide, in air", "#3e7654"),
        ("Carbon dioxide, non-fossil", "#8a6a45"),
        ("Carbon dioxide, from soil or biomass stock", "#9c755f"),
        ("Carbon dioxide, fossil", "#c44e52"),
        ("Methane, fossil", "#d55e00"),
        ("Methane, non-fossil", "#cc79a7"),
        ("Methane, from soil or biomass stock", "#b279a2"),
        ("Dinitrogen monoxide", "#6f4e7c"),
        ("Sulfur dioxide", "#e6ab02"),
        ("Nitrogen oxides", "#4193b8"),
        ("Other mapped elementary flows", "#78909c"),
    )
    for pattern, colour in flow_colours:
        if pattern in contributor:
            return colour
    palette = (
        "#0072b2",
        "#009e73",
        "#e69f00",
        "#56b4e9",
        "#8c564b",
        "#7b8f00",
        "#17a2b8",
    )
    return palette[sum(ord(character) for character in contributor) % len(palette)]


def _fair_response_axis_range(metric: str, contribution_view: str) -> list[float]:
    minima: list[float] = []
    maxima: list[float] = []
    years = range(FAIR_RESPONSE_VIEW_RANGE[0], FAIR_RESPONSE_VIEW_RANGE[1] + 1)
    for case in ("BECCS", "DACCS"):
        series = _fair_response_display_series(case, metric, contribution_view, 50.0)
        annual = [dict(values) for _name, values in series]
        for year in years:
            minima.append(
                sum(min(values.get(year, 0.0), 0.0) for values in annual)
                * FAIR_RESPONSE_SCALE
            )
            maxima.append(
                sum(max(values.get(year, 0.0), 0.0) for values in annual)
                * FAIR_RESPONSE_SCALE
            )
        for quantile in (2.5, 97.5):
            totals = dict(
                cohort_fair_total_series(case, metric, contribution_view, quantile)
            )
            values = [totals.get(year, 0.0) * FAIR_RESPONSE_SCALE for year in years]
            minima.append(min(values))
            maxima.append(max(values))
    lower, upper = min(minima), max(maxima)
    return list(_padded_axis_extent(lower, upper))


def render_fair_response_figure(
    case: str,
    metric: str = "radiative forcing",
    contribution_view: str = "process",
    comparison_year: int = FAIR_RESPONSE_COMPARISON_YEAR,
) -> go.Figure:
    """Render median FaIR response areas and the ensemble response band."""

    if case not in TEMPORAL_GWP_CASES:
        raise ValueError(f"Unknown FaIR-response case: {case}.")
    if metric not in FAIR_RESPONSE_METRICS:
        metric = "radiative forcing"
    if contribution_view not in FAIR_RESPONSE_VIEWS:
        contribution_view = "process"
    comparison_year = max(
        FAIR_RESPONSE_VIEW_RANGE[0],
        min(FAIR_RESPONSE_VIEW_RANGE[1], int(round(comparison_year))),
    )
    years = list(range(FAIR_RESPONSE_VIEW_RANGE[0], FAIR_RESPONSE_VIEW_RANGE[1] + 1))
    figure = go.Figure()
    axis_range = _fair_response_axis_range(metric, contribution_view)
    figure.add_trace(
        go.Scatter(
            x=[2030, 2050, 2050, 2030, 2030],
            y=[
                axis_range[0],
                axis_range[0],
                axis_range[1],
                axis_range[1],
                axis_range[0],
            ],
            mode="lines",
            line={"width": 0},
            fill="toself",
            fillcolor=_hex_rgba(TEMPORAL_GWP_CASES[case]["accent"], 0.07),
            name="2030–2050 operation period",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    series_by_contributor = _fair_response_display_series(
        case, metric, contribution_view, 50.0
    )
    for contributor_index, (contributor, series) in enumerate(series_by_contributor):
        annual = dict(series)
        values = [annual.get(year, 0.0) * FAIR_RESPONSE_SCALE for year in years]
        positive = [max(value, 0.0) for value in values]
        negative = [min(value, 0.0) for value in values]
        colour = _fair_response_colour(case, contribution_view, contributor)
        label = _fair_response_label(contribution_view, contributor)
        hover = (
            "<b>%{fullData.name}</b><br>Year %{x}<br>"
            "%{y:.3g} "
            f"{FAIR_RESPONSE_METRICS[metric]['axis']}<extra></extra>"
        )
        for sign, values_for_sign in (
            ("positive", positive),
            ("negative", negative),
        ):
            if not any(value != 0.0 for value in values_for_sign):
                continue
            figure.add_trace(
                go.Scatter(
                    x=years,
                    y=values_for_sign,
                    name=label,
                    legendgroup=label,
                    showlegend=(
                        contributor_index < 6
                        and (sign == "positive" or not any(positive))
                    ),
                    mode="lines",
                    line={"color": colour, "width": 1.1},
                    fillcolor=_hex_rgba(colour, 0.58),
                    stackgroup=sign,
                    hovertemplate=hover,
                )
            )

    totals_by_quantile = {
        quantile: dict(
            cohort_fair_total_series(case, metric, contribution_view, quantile)
        )
        for quantile in FAIR_RESPONSE_QUANTILES
    }
    lower = [
        totals_by_quantile[2.5].get(year, 0.0) * FAIR_RESPONSE_SCALE for year in years
    ]
    upper = [
        totals_by_quantile[97.5].get(year, 0.0) * FAIR_RESPONSE_SCALE for year in years
    ]
    median = [
        totals_by_quantile[50.0].get(year, 0.0) * FAIR_RESPONSE_SCALE for year in years
    ]
    figure.add_trace(
        go.Scatter(
            x=years,
            y=lower,
            name="FaIR 2.5–97.5% range",
            legendgroup="fair-uncertainty",
            mode="lines",
            line={"width": 0},
            showlegend=False,
            hoverinfo="skip",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=years,
            y=upper,
            mode="lines",
            line={"width": 0},
            fill="tonexty",
            fillcolor="rgba(73, 91, 101, 0.16)",
            name="FaIR 2.5–97.5% range",
            legendgroup="fair-uncertainty",
            showlegend=True,
            legendrank=900,
            hoverinfo="skip",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=years,
            y=median,
            name="Net median response",
            mode="lines",
            line={"color": "#c44e52", "width": 4.0},
            showlegend=False,
            hovertemplate=(
                "<b>Net median response</b><br>Year %{x}<br>"
                "%{y:.3g} "
                f"{FAIR_RESPONSE_METRICS[metric]['axis']}<extra></extra>"
            ),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[2030, 2030],
            y=axis_range,
            mode="lines",
            line={"width": 1.1, "dash": "dot", "color": "#60747c"},
            name="Operation start",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    beccs_reference_value = (
        dict(cohort_fair_total_series("BECCS", metric, contribution_view, 50.0)).get(
            comparison_year, 0.0
        )
        * FAIR_RESPONSE_SCALE
    )
    figure.add_shape(
        type="line",
        xref="x",
        yref="paper",
        x0=comparison_year,
        x1=comparison_year,
        y0=0,
        y1=1,
        line={"color": "#3f5965", "width": 1.7, "dash": "dot"},
        opacity=0.82,
        name=FAIR_RESPONSE_YEAR_MARKER_NAME,
        showlegend=False,
        editable=case == "BECCS",
        label={
            "text": (
                f"↔ drag · {comparison_year}"
                if case == "BECCS"
                else str(comparison_year)
            ),
            "textposition": "end",
            "textangle": 0,
            "font": {"size": 8, "color": "#3f5965"},
            "padding": 3,
        },
    )
    figure.add_trace(
        go.Scatter(
            x=list(FAIR_RESPONSE_VIEW_RANGE),
            y=[beccs_reference_value, beccs_reference_value],
            mode="lines",
            line={
                "color": FAIR_RESPONSE_COMPARISON_COLOUR,
                "width": 1.25,
                "dash": "dash",
            },
            opacity=0.72,
            name=FAIR_RESPONSE_REFERENCE_NAME,
            showlegend=False,
            hoverinfo="skip",
        )
    )
    if case == "DACCS":
        figure.add_annotation(
            x=2288,
            y=beccs_reference_value,
            xref="x",
            yref="y",
            text=f"BECCS median · {comparison_year}",
            showarrow=False,
            xanchor="right",
            yshift=9,
            font={
                "size": 8,
                "color": FAIR_RESPONSE_COMPARISON_COLOUR,
            },
            bgcolor="rgba(242,246,247,0.82)",
            borderpad=2,
        )
    figure.update_layout(
        autosize=True,
        margin={"l": 65, "r": 18, "t": 76, "b": 42},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f2f6f7",
        font={
            "family": "Arial, Helvetica, sans-serif",
            "color": "#17232c",
            "size": 10,
        },
        legend={
            "orientation": "h",
            "y": 1.02,
            "x": 0,
            "yanchor": "bottom",
            "xanchor": "left",
            "font": {"size": 7},
            "tracegroupgap": 2,
            "groupclick": "togglegroup",
        },
        xaxis={
            "range": list(FAIR_RESPONSE_VIEW_RANGE),
            "tick0": 1940,
            "dtick": 40,
            "title": None,
            "showgrid": True,
            "gridcolor": "#dce5e8",
            "zeroline": False,
        },
        yaxis={
            "title": {
                "text": FAIR_RESPONSE_METRICS[metric]["axis"],
                "standoff": 5,
            },
            "range": axis_range,
            "showgrid": True,
            "gridcolor": "#dce5e8",
            "zeroline": True,
            "zerolinecolor": "#7f929a",
            "zerolinewidth": 1.2,
        },
        hovermode="x unified",
        hoverlabel={"namelength": -1},
        uirevision=f"fair-response-{case}-{metric}-{contribution_view}",
        editrevision=f"fair-response-year-{comparison_year}",
    )
    return figure


def fair_response_value_label(
    case: str,
    metric: str = "radiative forcing",
    contribution_view: str = "process",
) -> str:
    if metric not in FAIR_RESPONSE_METRICS:
        metric = "radiative forcing"
    if contribution_view not in FAIR_RESPONSE_VIEWS:
        contribution_view = "process"
    totals = dict(cohort_fair_total_series(case, metric, contribution_view, 50.0))
    value = totals.get(FAIR_RESPONSE_VIEW_RANGE[1], 0.0) * FAIR_RESPONSE_SCALE
    return f"{value:,.3f} {FAIR_RESPONSE_METRICS[metric]['unit']}"


def fair_response_year_value_label(
    case: str,
    metric: str = "radiative forcing",
    contribution_view: str = "process",
    comparison_year: int = FAIR_RESPONSE_COMPARISON_YEAR,
) -> str:
    if metric not in FAIR_RESPONSE_METRICS:
        metric = "radiative forcing"
    if contribution_view not in FAIR_RESPONSE_VIEWS:
        contribution_view = "process"
    comparison_year = max(
        FAIR_RESPONSE_VIEW_RANGE[0],
        min(FAIR_RESPONSE_VIEW_RANGE[1], int(round(comparison_year))),
    )
    totals = dict(cohort_fair_total_series(case, metric, contribution_view, 50.0))
    value = totals.get(comparison_year, 0.0) * FAIR_RESPONSE_SCALE
    return f"{value:,.3f} {FAIR_RESPONSE_METRICS[metric]['unit']}"


def _fair_response_slide(index: int):
    metric = "radiative forcing"
    contribution_view = "process"
    panels = []
    for case in ("BECCS", "DACCS"):
        settings = TEMPORAL_GWP_CASES[case]
        panels.append(
            html.Article(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(className="temporal-case-dot"),
                                    html.H3(settings["title"]),
                                ],
                                className="temporal-case-title",
                            ),
                            html.Span(
                                "FaIR ensemble median",
                                className="temporal-storage",
                            ),
                        ],
                        className="temporal-gwp-panel-heading",
                    ),
                    dcc.Graph(
                        id=f"fair-response-{case.lower()}-chart",
                        figure=render_fair_response_figure(
                            case, metric, contribution_view
                        ),
                        config={
                            "displayModeBar": False,
                            "responsive": True,
                            "scrollZoom": False,
                            "edits": {"shapePosition": case == "BECCS"},
                            "showTips": False,
                        },
                        className="temporal-gwp-chart",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        f"Selected year · {FAIR_RESPONSE_COMPARISON_YEAR}"
                                    ),
                                    html.Strong(
                                        fair_response_year_value_label(
                                            case,
                                            metric,
                                            contribution_view,
                                            FAIR_RESPONSE_COMPARISON_YEAR,
                                        ),
                                        id=f"fair-response-{case.lower()}-selected-value",
                                    ),
                                ],
                                className="fair-result-callout selected",
                            ),
                            html.Div(
                                [
                                    html.Span("Net response · 2300"),
                                    html.Strong(
                                        fair_response_value_label(
                                            case, metric, contribution_view
                                        ),
                                        id=f"fair-response-{case.lower()}-value",
                                    ),
                                ],
                                className="fair-result-callout final",
                            ),
                        ],
                        className="temporal-gwp-total fair-result-callouts",
                    ),
                ],
                className=(f"temporal-gwp-panel temporal-gwp-panel-{case.lower()}"),
            )
        )
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Strong("FaIR response"),
                                html.Span(
                                    "Filled areas show median contributions per net tonne. "
                                    "Drag the year guide in the BECCS panel to compare both pathways."
                                ),
                            ],
                            className="temporal-gwp-control-copy",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("Response"),
                                        dcc.RadioItems(
                                            id="fair-response-metric-toggle",
                                            options=[
                                                {
                                                    "label": "Radiative forcing",
                                                    "value": "radiative forcing",
                                                },
                                                {
                                                    "label": "Temperature anomaly",
                                                    "value": "temperature anomaly",
                                                },
                                            ],
                                            value=metric,
                                            inline=True,
                                            className=(
                                                "contribution-view-toggle "
                                                "temporal-gwp-toggle "
                                                "fair-response-metric-toggle"
                                            ),
                                        ),
                                    ],
                                    className="temporal-gwp-control-group",
                                ),
                                html.Div(
                                    [
                                        html.Span("Attribution"),
                                        dcc.RadioItems(
                                            id="fair-response-view-toggle",
                                            options=[
                                                {
                                                    "label": "By process",
                                                    "value": "process",
                                                },
                                                {
                                                    "label": "By elementary flow",
                                                    "value": "elementary_flow",
                                                },
                                            ],
                                            value=contribution_view,
                                            inline=True,
                                            className=(
                                                "contribution-view-toggle "
                                                "temporal-gwp-toggle "
                                                "fair-response-view-toggle"
                                            ),
                                        ),
                                    ],
                                    className="temporal-gwp-control-group",
                                ),
                            ],
                            className="temporal-gwp-controls",
                        ),
                    ],
                    className="temporal-gwp-toolbar",
                ),
                html.Div(panels, className="temporal-gwp-grid"),
                html.Div(
                    [
                        html.Span("Filled areas", className="temporal-sign negative"),
                        html.Span("median response for the selected attribution"),
                        html.Span(
                            "Uncertainty band", className="temporal-sign fair-band"
                        ),
                        html.Span("2.5–97.5% range across FaIR configurations"),
                        html.Span(
                            "Thick red curve", className="temporal-sign cumulative"
                        ),
                        html.Span("net median climate response"),
                        html.Span("·"),
                        html.Span(
                            "FaIR · SSP2-PkBudg1000 · Northern Europe · 2030 cohort"
                        ),
                    ],
                    className="temporal-gwp-note",
                ),
            ],
            className="temporal-gwp-slide fair-response-slide",
        ),
        eyebrow="Time-explicit LCA · FaIR climate response",
        lead=(
            "FaIR converts dated emissions and removals into radiative-forcing and "
            "temperature responses that continue to evolve after each exchange."
        ),
    )


PULSE_EQUIVALENCE_METRICS = {
    "radiative forcing": {
        "label": "Integrated radiative forcing",
        "short": "RF-based",
        "symbol": "ΔRF",
    },
    "temperature anomaly": {
        "label": "Integrated temperature anomaly",
        "short": "Temperature-based",
        "symbol": "ΔT",
    },
}
PULSE_EQUIVALENCE_YEAR_RANGE = (1940, 2300)
PULSE_EQUIVALENCE_DEFAULT_WINDOW = (2000, 2100)
PULSE_EQUIVALENCE_DEFAULT_REFERENCE_YEAR = 2030
PULSE_EQUIVALENCE_REFERENCE_STEP = 5


def _pulse_equivalence_window(window) -> tuple[int, int]:
    if not isinstance(window, (list, tuple)) or len(window) != 2:
        return PULSE_EQUIVALENCE_DEFAULT_WINDOW
    start, end = (int(round(float(value))) for value in window)
    lower, upper = PULSE_EQUIVALENCE_YEAR_RANGE
    start = max(lower, min(upper - PULSE_EQUIVALENCE_REFERENCE_STEP, start))
    end = max(
        start + PULSE_EQUIVALENCE_REFERENCE_STEP,
        min(upper, end),
    )
    return start, end


def pulse_equivalence_reference_year(
    reference_year: int | float | None,
    window_start: int,
    window_end: int,
) -> int:
    """Return a selectable reference year contained in the integration window."""

    window_start, window_end = _pulse_equivalence_window([window_start, window_end])
    upper = window_end - PULSE_EQUIVALENCE_REFERENCE_STEP
    if reference_year is None:
        reference_year = PULSE_EQUIVALENCE_DEFAULT_REFERENCE_YEAR
    rounded = int(
        round(float(reference_year) / PULSE_EQUIVALENCE_REFERENCE_STEP)
        * PULSE_EQUIVALENCE_REFERENCE_STEP
    )
    return max(window_start, min(upper, rounded))


def pulse_equivalence_selection(selection) -> tuple[int, int, int]:
    """Return ordered start, reference-pulse and end handles."""

    if not isinstance(selection, (list, tuple)) or len(selection) != 3:
        return (
            PULSE_EQUIVALENCE_DEFAULT_WINDOW[0],
            PULSE_EQUIVALENCE_DEFAULT_REFERENCE_YEAR,
            PULSE_EQUIVALENCE_DEFAULT_WINDOW[1],
        )
    step = PULSE_EQUIVALENCE_REFERENCE_STEP
    lower, upper = PULSE_EQUIVALENCE_YEAR_RANGE
    values = [int(round(float(value) / step) * step) for value in selection]
    start = max(lower, min(upper - 2 * step, values[0]))
    reference = max(start + step, min(upper - step, values[1]))
    end = max(reference + step, min(upper, values[2]))
    return start, reference, end


def pulse_equivalence_value_label(
    case: str,
    metric: str = "radiative forcing",
    window_start: int = PULSE_EQUIVALENCE_DEFAULT_WINDOW[0],
    window_end: int = PULSE_EQUIVALENCE_DEFAULT_WINDOW[1],
    reference_year: int = PULSE_EQUIVALENCE_DEFAULT_REFERENCE_YEAR,
) -> str:
    if metric not in PULSE_EQUIVALENCE_METRICS:
        metric = "radiative forcing"
    value = cohort_co2_pulse_equivalent(
        case,
        metric,
        int(window_start),
        int(window_end),
        50.0,
        int(reference_year),
    )
    return f"{value:,.0f} kg CO₂"


def render_co2_pulse_equivalence_figure(
    metric: str = "radiative forcing",
    window_start: int = PULSE_EQUIVALENCE_DEFAULT_WINDOW[0],
    window_end: int = PULSE_EQUIVALENCE_DEFAULT_WINDOW[1],
    reference_year: int = PULSE_EQUIVALENCE_DEFAULT_REFERENCE_YEAR,
) -> go.Figure:
    """Render the climate response and pulse-equivalent integration result."""

    if metric not in PULSE_EQUIVALENCE_METRICS:
        metric = "radiative forcing"
    window_start, window_end = _pulse_equivalence_window([window_start, window_end])
    reference_year = pulse_equivalence_reference_year(
        reference_year, window_start, window_end
    )
    horizon_years = list(
        range(
            max(
                window_start + PULSE_EQUIVALENCE_REFERENCE_STEP,
                reference_year + PULSE_EQUIVALENCE_REFERENCE_STEP,
            ),
            PULSE_EQUIVALENCE_YEAR_RANGE[1] + 1,
            PULSE_EQUIVALENCE_REFERENCE_STEP,
        )
    )
    settings = {
        "BECCS": {
            "colour": "#3e7654",
            "fill": "rgba(62,118,84,.22)",
            "title": "BECCS · new CHP+CCS",
        },
        "DACCS": {
            "colour": "#3292b5",
            "fill": "rgba(50,146,181,.20)",
            "title": "DACCS · solid sorbent",
        },
    }
    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.18,
        row_heights=[0.47, 0.53],
    )
    response_scale = 1.0e15
    for case, style in settings.items():
        response = [
            (year, value * response_scale)
            for year, value in cohort_fair_total_series(
                case, "radiative forcing", "process", 50.0
            )
            if PULSE_EQUIVALENCE_YEAR_RANGE[0]
            <= year
            <= PULSE_EQUIVALENCE_YEAR_RANGE[1]
        ]
        figure.add_trace(
            go.Scatter(
                x=[year for year, _value in response],
                y=[value for _year, value in response],
                name=case,
                legendgroup=case,
                mode="lines",
                line={"color": style["colour"], "width": 2.4},
                fill="tozeroy",
                fillcolor=style["fill"],
                hovertemplate=(
                    f"<b>{style['title']}</b><br>Year %{{x}}<br>"
                    "%{y:.2f}<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )
        values = [
            cohort_co2_pulse_equivalent(
                case,
                metric,
                window_start,
                horizon,
                50.0,
                reference_year,
            )
            for horizon in horizon_years
        ]
        selected = cohort_co2_pulse_equivalent(
            case,
            metric,
            window_start,
            window_end,
            50.0,
            reference_year,
        )
        figure.add_trace(
            go.Scatter(
                x=horizon_years,
                y=values,
                name=f"{style['title']} · pulse-eq",
                legendgroup=case,
                mode="lines",
                line={"color": style["colour"], "width": 3.2},
                showlegend=False,
                hovertemplate=(
                    f"<b>{style['title']}</b><br>Window "
                    f"{window_start}–%{{x}} · pulse {reference_year}<br>"
                    "%{y:,.0f} kg CO₂ pulse-eq"
                    "<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )
        figure.add_trace(
            go.Scatter(
                x=[window_end],
                y=[selected],
                name=f"{case} selected window",
                mode="markers",
                marker={
                    "color": style["colour"],
                    "size": 10,
                    "line": {"color": "white", "width": 2},
                },
                showlegend=False,
                hovertemplate=(
                    f"<b>{case} · {window_start}–{window_end}</b><br>"
                    f"Reference pulse {reference_year}<br>"
                    "%{y:,.0f} kg CO₂ pulse-eq<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )
    reference_response = [
        (year, value * 1000.0 * response_scale)
        for year, value in co2_reference_pulse_series(
            "radiative forcing", 50.0, reference_year
        )
        if PULSE_EQUIVALENCE_YEAR_RANGE[0] <= year <= PULSE_EQUIVALENCE_YEAR_RANGE[1]
    ]
    figure.add_trace(
        go.Scatter(
            x=[year for year, _value in reference_response],
            y=[value for _year, value in reference_response],
            name=f"+1 t CO₂ pulse · {reference_year}",
            legendgroup="reference-pulse",
            mode="lines",
            line={"color": "#d88f08", "width": 2.1, "dash": "dash"},
            cliponaxis=True,
            hovertemplate=(
                f"<b>+1 t CO₂ pulse · {reference_year}</b><br>"
                "Year %{x}<br>%{y:.2f}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )
    pulse_response = dict(reference_response).get(reference_year)
    if pulse_response is not None:
        figure.add_trace(
            go.Scatter(
                x=[reference_year],
                y=[pulse_response],
                name="Reference-pulse emission year",
                mode="markers",
                marker={
                    "color": "#d88f08",
                    "size": 8,
                    "line": {"color": "white", "width": 1.5},
                },
                showlegend=False,
                cliponaxis=True,
                hovertemplate=(
                    f"<b>+1 t CO₂ emitted in {reference_year}</b><br>"
                    "%{y:.2f} fW m⁻²<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )
    for row in (1, 2):
        figure.add_vrect(
            x0=window_start,
            x1=window_end,
            fillcolor="rgba(50,146,181,.12)",
            line={"color": "rgba(50,146,181,.42)", "width": 1},
            layer="below",
            row=row,
            col=1,
        )
        figure.add_vline(
            x=window_end,
            line={"color": "#526a73", "width": 1.2, "dash": "dot"},
            row=row,
            col=1,
        )
        figure.add_hline(
            y=0,
            line={"color": "#7f929a", "width": 1.0},
            row=row,
            col=1,
        )
    figure.add_annotation(
        x=(window_start + window_end) / 2,
        y=0.955,
        xref="x",
        yref="paper",
        text=f"integrated · {window_start}–{window_end}",
        showarrow=False,
        bgcolor="rgba(224,240,245,.96)",
        bordercolor="rgba(50,146,181,.45)",
        borderpad=3,
        font={"size": 9, "color": "#315d6b"},
    )
    figure.add_annotation(
        x=0,
        y=1.105,
        xref="paper",
        yref="paper",
        text="<b>Net radiative forcing</b> · unstacked areas · 1 t basis",
        showarrow=False,
        xanchor="left",
        font={"size": 10, "color": "#203743"},
    )
    figure.add_annotation(
        x=0,
        y=0.49,
        xref="paper",
        yref="paper",
        text="<b>CO₂-pulse equivalent</b> · as the integration window closes",
        showarrow=False,
        xanchor="left",
        font={"size": 10, "color": "#203743"},
    )
    response_unit = "fW m⁻² / t basis"
    figure.update_layout(
        autosize=True,
        margin={"l": 66, "r": 16, "t": 42, "b": 42},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f2f6f7",
        font={
            "family": "Arial, Helvetica, sans-serif",
            "color": "#17232c",
            "size": 10,
        },
        legend={
            "orientation": "h",
            "x": 0.32,
            "y": 1.125,
            "font": {"size": 9},
            "itemwidth": 32,
        },
        hovermode="x",
        uirevision=(f"co2-pulse-equivalence-{metric}-{window_start}-{reference_year}"),
    )
    figure.update_xaxes(
        range=list(PULSE_EQUIVALENCE_YEAR_RANGE),
        tick0=1940,
        dtick=60,
        showgrid=True,
        gridcolor="#dce5e8",
        zeroline=False,
    )
    figure.update_xaxes(
        title={"text": "Calendar year · lower panel uses year as window end"},
        row=2,
        col=1,
    )
    figure.update_yaxes(
        title={"text": response_unit, "standoff": 5},
        showgrid=True,
        gridcolor="#dce5e8",
        zeroline=False,
        tickformat=".0f",
        row=1,
        col=1,
    )
    figure.update_yaxes(
        title={"text": "kg CO₂-eq / net t", "standoff": 5},
        showgrid=True,
        gridcolor="#dce5e8",
        zeroline=False,
        row=2,
        col=1,
    )
    return figure


def _pulse_equivalence_combined(index: int):
    metric = "radiative forcing"
    window_start, window_end = PULSE_EQUIVALENCE_DEFAULT_WINDOW
    reference_year = PULSE_EQUIVALENCE_DEFAULT_REFERENCE_YEAR
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "Equivalent reference pulse",
                                    className="pulse-method-kicker",
                                ),
                                html.Div(
                                    [
                                        html.Span("m"),
                                        html.Sub("CO₂-eq"),
                                        html.Sup("X,[t₀,t₁]"),
                                        html.Span("="),
                                        html.Span("m"),
                                        html.Sub("ref"),
                                        html.Span("×"),
                                        html.Div(
                                            [
                                                html.Span("∫[t₀,t₁] ΔXsystem(t) dt"),
                                                html.Span(
                                                    "∫[t₀,t₁] ΔXreference pulse(t) dt"
                                                ),
                                            ],
                                            className="pulse-equation-fraction",
                                        ),
                                    ],
                                    className="pulse-equation",
                                ),
                            ],
                            className="pulse-equation-card",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            "ΔX", className="pulse-definition-key"
                                        ),
                                        html.Span(
                                            "radiative forcing or temperature response"
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            "Reference",
                                            className="pulse-definition-key",
                                        ),
                                        html.Span(
                                            f"positive CO₂ pulse emitted in {reference_year}",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            "Negative result",
                                            className="pulse-definition-key cooling",
                                        ),
                                        html.Span(
                                            "cooling equivalent to a CO₂ removal"
                                        ),
                                    ]
                                ),
                            ],
                            className="pulse-definitions",
                        ),
                    ],
                    className="pulse-method-band",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("Response basis"),
                                dcc.RadioItems(
                                    id="pulse-equivalence-metric-toggle",
                                    options=[
                                        {
                                            "label": "Radiative forcing",
                                            "value": "radiative forcing",
                                        },
                                        {
                                            "label": "Temperature response",
                                            "value": "temperature anomaly",
                                        },
                                    ],
                                    value=metric,
                                    inline=True,
                                    className=(
                                        "contribution-view-toggle "
                                        "pulse-equivalence-metric-toggle"
                                    ),
                                ),
                            ],
                            className="pulse-control-basis",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("Integration window"),
                                        html.Strong(
                                            (
                                                f"Start {window_start} · reference pulse "
                                                f"{reference_year} · end {window_end}"
                                            ),
                                            id="pulse-equivalence-window-label",
                                        ),
                                    ],
                                    className="pulse-window-heading",
                                ),
                                dcc.RangeSlider(
                                    id="pulse-equivalence-window-slider",
                                    min=PULSE_EQUIVALENCE_YEAR_RANGE[0],
                                    max=PULSE_EQUIVALENCE_YEAR_RANGE[1],
                                    step=PULSE_EQUIVALENCE_REFERENCE_STEP,
                                    value=[
                                        window_start,
                                        reference_year,
                                        window_end,
                                    ],
                                    marks={
                                        1940: "1940",
                                        2000: "2000",
                                        2030: "2030",
                                        2100: "2100",
                                        2200: "2200",
                                        2300: "2300",
                                    },
                                    allowCross=False,
                                    pushable=5,
                                    tooltip={"placement": "bottom"},
                                ),
                                html.Div(
                                    [
                                        html.Span([html.B("1"), "Window start"]),
                                        html.Span(
                                            [html.B("2"), "Reference-pulse year"],
                                            className="reference-handle",
                                        ),
                                        html.Span([html.B("3"), "Window end"]),
                                    ],
                                    className="pulse-handle-key",
                                ),
                            ],
                            className=("pulse-window-control pulse-combined-control"),
                        ),
                    ],
                    className="pulse-controls",
                ),
                html.Div(
                    [
                        html.Article(
                            dcc.Graph(
                                id="pulse-equivalence-chart",
                                figure=render_co2_pulse_equivalence_figure(
                                    metric,
                                    window_start,
                                    window_end,
                                    reference_year,
                                ),
                                config={
                                    "displayModeBar": False,
                                    "responsive": True,
                                    "scrollZoom": False,
                                    "showTips": False,
                                },
                                className="pulse-equivalence-chart",
                            ),
                            className="pulse-chart-card",
                        ),
                        html.Aside(
                            [
                                html.Div(
                                    [
                                        html.Span("BECCS · new CHP+CCS"),
                                        html.Strong(
                                            pulse_equivalence_value_label(
                                                "BECCS",
                                                metric,
                                                window_start,
                                                window_end,
                                                reference_year,
                                            ),
                                            id="pulse-equivalence-beccs-value",
                                        ),
                                        html.Small("pulse-eq / net t stored"),
                                    ],
                                    className="pulse-result-card pulse-result-beccs",
                                ),
                                html.Div(
                                    [
                                        html.Span("DACCS · solid sorbent"),
                                        html.Strong(
                                            pulse_equivalence_value_label(
                                                "DACCS",
                                                metric,
                                                window_start,
                                                window_end,
                                                reference_year,
                                            ),
                                            id="pulse-equivalence-daccs-value",
                                        ),
                                        html.Small("pulse-eq / net t stored"),
                                    ],
                                    className="pulse-result-card pulse-result-daccs",
                                ),
                                html.Div(
                                    [
                                        html.Strong(
                                            "Reference pulse ≠ physical storage date."
                                        ),
                                        html.Span(
                                            "The window dates set which response years are counted; "
                                            "the orange handle dates the comparison pulse. A short "
                                            "window excludes part of delayed forest uptake. The handles "
                                            "change the equivalent mass, not the CO₂ stored."
                                        ),
                                    ],
                                    className="pulse-window-insight",
                                ),
                            ],
                            className="pulse-result-column",
                        ),
                    ],
                    className="pulse-results-grid",
                ),
                html.Div(
                    [
                        html.Span(
                            "Calculated for each FaIR configuration; median reported"
                        ),
                        html.Span("·"),
                        html.Span("Reference response scaled from 1 Mt to 1 kg CO₂"),
                        html.Span("·"),
                        html.Span(
                            "841 configurations · SSP2-PkBudg1000 · 2030 cohort · per net t stored"
                        ),
                    ],
                    className="pulse-method-note",
                ),
            ],
            className="pulse-equivalence-slide",
        ),
        eyebrow="Time-explicit LCA · CO₂-pulse equivalence",
        lead=(
            "The indicator divides the system's time-integrated climate response by "
            "the response to a dated reference CO₂ pulse. The integration window "
            "therefore changes the result."
        ),
    )


def _pulse_equivalence_concept(index: int):
    combined = _pulse_equivalence_combined(index)
    content = combined.children[1].children
    method_band = content.children[0]
    dates = (
        ("t₀", "Window start", "first response year included"),
        ("tₚ", "Reference-pulse date", "when the comparison pulse is emitted"),
        ("t₁", "Window end", "last response year included"),
    )
    return _slide_shell(
        index,
        html.Div(
            [
                method_band,
                html.Div(
                    [
                        html.Article(
                            [html.Span(symbol), html.Strong(label), html.Small(note)],
                            className="pulse-date-card",
                        )
                        for symbol, label, note in dates
                    ],
                    className="pulse-date-grid",
                ),
                html.Div(
                    [
                        html.Strong("A comparison mass, not physical storage"),
                        html.P(
                            "Pulse equivalence asks what one-time CO₂ pulse would produce the same integrated response. A negative result represents cooling equivalent to removing that comparison mass."
                        ),
                    ],
                    className="pulse-concept-plain-language",
                ),
                html.Button(
                    "Implementation and scaling detail: Appendix A →",
                    id={"type": "chapter-button", "slide": APPENDIX_START_SLIDE},
                    n_clicks=0,
                    className="appendix-link-button",
                ),
            ],
            className="pulse-concept-slide",
        ),
        eyebrow="Time-explicit LCA · CO₂-pulse equivalence",
        lead=(
            "The indicator compares integrated climate responses over a dated window; it does not redefine the amount physically stored."
        ),
    )


def _pulse_equivalence_slide(index: int, print_mode: bool = False):
    combined = _pulse_equivalence_combined(index)
    content = combined.children[1].children
    controls, results, note = content.children[1:]
    insight = results.children[1].children[2]
    insight.children[1] = html.Span(
        "The dates change the comparison window and pulse, not the physical CO₂ stored."
    )
    body = html.Div(
        [
            controls,
            html.Div(
                [
                    html.Strong("Window boundary"),
                    html.Span(
                        "Delayed forest uptake after the selected end year is excluded from the BECCS equivalence."
                    ),
                ],
                className="pulse-excluded-uptake",
            ),
            results,
            note,
        ],
        className=(
            "pulse-equivalence-slide pulse-interactive-slide "
            + ("print-expanded" if print_mode else "")
        ),
    )
    return _slide_shell(
        index,
        body,
        eyebrow="Time-explicit LCA · CO₂-pulse equivalence",
        lead=(
            "Move the three dates to see how the included climate response changes the comparison mass."
        ),
    )


def _routing_graph_slide(index: int, case: str):
    provenance = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "assets"
            / "routing"
            / "routing-graphs.json"
        ).read_text(encoding="utf-8")
    )
    graph = provenance["cases"][case]
    routed_years = [int(year) for year in graph["years"]]
    settings = {
        "BECCS": {
            "tone": "forest",
            "file": "beccs-routing.html",
            "preview": "beccs-routing-preview.png",
            "lead": (
                "The graph opens at depth 3. Select Branch to isolate one annual input; "
                "increase Depth to reveal more supply-chain layers. It covers construction "
                "in 2027–2029, operation in 2030–2049 and forest regrowth through 2131."
            ),
        },
        "DACCS": {
            "tone": "sky",
            "file": "daccs-routing.html",
            "preview": "daccs-routing-preview.png",
            "lead": (
                "The graph opens at depth 3. Select Branch to isolate one annual input; "
                "increase Depth to reveal more supply-chain layers. It covers construction "
                "in 2027–2029, operation with annual backgrounds in 2030–2049 and "
                "end-of-life in 2050."
            ),
        },
    }[case]
    settings["nodes"] = f"{int(graph['nodes']):,}"
    settings["edges"] = f"{int(graph['edges']):,}"
    settings["span"] = f"{min(routed_years)}–{max(routed_years)}"
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [html.Span("Scenario"), html.Strong("SSP2-PkBudg1000")]
                        ),
                        html.Div(
                            [
                                html.Span("Operating cohort"),
                                html.Strong("2030–2049 · Northern Europe"),
                            ]
                        ),
                        html.Div(
                            [
                                html.Span("Explicit graph"),
                                html.Strong(
                                    f"{settings['nodes']} nodes · {settings['edges']} edges"
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.Span("Routed years"),
                                html.Strong(f"{settings['span']} · depth 0–4"),
                            ]
                        ),
                    ],
                    className=f"routing-metadata routing-metadata-{settings['tone']}",
                ),
                html.Div(
                    [
                        html.Iframe(
                            src=f"assets/routing/{settings['file']}",
                            title=f"Interactive TRAILS {case} temporal routing graph",
                            className="routing-iframe",
                        ),
                        html.Img(
                            src=f"assets/routing/{settings['preview']}",
                            alt=f"Static preview of the TRAILS {case} routing graph",
                            className="routing-print-preview",
                        ),
                    ],
                    className=f"routing-frame routing-frame-{settings['tone']}",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.B("1"),
                                html.Strong("Overview"),
                                html.Span(
                                    "branch: all opens the complete routed network"
                                ),
                            ],
                            className="routing-coach-mark",
                        ),
                        html.Div(
                            [
                                html.B("2"),
                                html.Strong("Branch selector"),
                                html.Span("isolate one annual input"),
                            ],
                            className="routing-coach-mark",
                        ),
                        html.Div(
                            [
                                html.B("3"),
                                html.Strong("Supply-chain depth"),
                                html.Span("add layers from depth 0 to 4"),
                            ],
                            className="routing-coach-mark",
                        ),
                    ],
                    className="routing-guide",
                ),
                (
                    html.Div(
                        "No forest-regrowth branch; routing ends in 2050.",
                        className="routing-stop-annotation",
                    )
                    if case == "DACCS"
                    else None
                ),
            ],
            className="routing-slide",
        ),
        eyebrow="Time-explicit LCA · TRAILS routing graph",
        lead=settings["lead"],
    )


def _beccs_routing_graph_slide(index: int):
    return _routing_graph_slide(index, "BECCS")


def _daccs_routing_graph_slide(index: int):
    return _routing_graph_slide(index, "DACCS")


def _card_synthesis(index: int):
    static_beccs = static_score(
        "BECCS",
        "SSP2-NPi",
        2025,
        "new CHP+CCS vs standing forest and Northern European energy",
    )
    static_daccs = static_score("DACCS", "SSP2-NPi", 2025, "not applicable")
    lifetime = {
        case: {
            pathway: lifetime_score_per_net_tonne(case, pathway)
            for pathway in ("SSP2-NPi", "SSP2-PkBudg1000")
        }
        for case in ("BECCS", "DACCS")
    }
    pulse = {
        case: cohort_co2_pulse_equivalent(
            case, "radiative forcing", 1940, 2100, 50.0, 2030
        )
        for case in ("BECCS", "DACCS")
    }

    def static_result_row(case: str, value: float, tone: str, driver: str):
        return html.Div(
            [
                html.Strong(case),
                html.Div(
                    html.Span(
                        className=f"summary-static-fill summary-fill-{tone}",
                        style={"width": f"{abs(value) / 10:.1f}%"},
                    ),
                    className="summary-static-track",
                ),
                html.B(f"−{abs(value):,.0f}"),
                html.Em(driver),
            ],
            className="summary-static-row",
        )

    def scenario_result_row(case: str, tone: str):
        npi = lifetime[case]["SSP2-NPi"]
        budget = lifetime[case]["SSP2-PkBudg1000"]
        return html.Div(
            [
                html.Strong(case, className=f"summary-case summary-case-{tone}"),
                html.Span(f"−{abs(npi):,.0f}", className="summary-scenario-value"),
                html.B("→"),
                html.Span(f"−{abs(budget):,.0f}", className="summary-scenario-value"),
                html.Em(f"Δ −{abs(budget - npi):.0f}"),
            ],
            className="summary-scenario-row",
        )

    def ranking_row(case: str, tone: str):
        static_value = lifetime[case]["SSP2-PkBudg1000"]
        return html.Div(
            [
                html.Strong(case, className=f"summary-case summary-case-{tone}"),
                html.Span(f"−{abs(static_value):,.0f}"),
                html.Span(f"−{abs(pulse[case]):,.0f}"),
            ],
            className="summary-ranking-row",
        )

    findings = [
        {
            "number": "01",
            "tone": "blue",
            "kicker": "Conventional · 2025",
            "title": "Similar totals hide different burdens",
            "body": (
                "Greenfield BECCS is 132 kg more negative in 2025. Its dominant term "
                "is −1,143 kg from future forest regrowth; DACCS is dominated by "
                "electricity for capture and its heat pump."
            ),
            "evidence": "IPCC 2021 GWP100 · kg CO₂-eq per net t stored",
            "visual": html.Div(
                [
                    static_result_row(
                        "BECCS", static_beccs, "forest", "regrowth −1,143"
                    ),
                    static_result_row("DACCS", static_daccs, "sky", "electricity +492"),
                ],
                className="finding-visual summary-static-visual",
            ),
        },
        {
            "number": "02",
            "tone": "amber",
            "kicker": "Prospective · 2030–2049",
            "title": "The pathway shifts DACCS slightly more",
            "body": (
                "Moving from NPi to PkBudg1000 makes the BECCS lifetime score 6 kg "
                "more negative, compared with 9 kg for DACCS under the same twenty "
                "annual backgrounds."
            ),
            "evidence": "SSP2-NPi → SSP2-PkBudg1000 · kg CO₂-eq/net t",
            "visual": html.Div(
                [
                    html.Div(
                        [
                            html.Span("NPi"),
                            html.Span("PkBudg1000"),
                            html.Span("change"),
                        ],
                        className="summary-scenario-header",
                    ),
                    scenario_result_row("BECCS", "forest"),
                    scenario_result_row("DACCS", "sky"),
                ],
                className="finding-visual summary-scenario-visual",
            ),
        },
        {
            "number": "03",
            "tone": "teal",
            "kicker": "Time-explicit · climate response",
            "title": "Timing changes magnitudes, not the ranking",
            "body": (
                "Static lifetime GWP100 and integrated forcing both favour greenfield "
                "BECCS in this reference. Its response begins with construction in "
                "2027 and includes project regrowth after each harvest."
            ),
            "evidence": "Pulse-equivalent: 1940–2100 · reference pulse in 2030",
            "visual": html.Div(
                [
                    html.Div(
                        [
                            html.Span("Static GWP100"),
                            html.Span("RF pulse-eq"),
                        ],
                        className="summary-ranking-header",
                    ),
                    ranking_row("BECCS", "forest"),
                    ranking_row("DACCS", "sky"),
                ],
                className="finding-visual summary-ranking-visual",
            ),
        },
    ]
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Article(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            finding["number"],
                                            className="finding-number",
                                        ),
                                        html.Span(
                                            finding["kicker"],
                                            className="finding-kicker",
                                        ),
                                    ],
                                    className="finding-card-heading",
                                ),
                                finding["visual"],
                                html.H3(finding["title"]),
                                html.P(finding["body"]),
                                html.Div(
                                    finding["evidence"],
                                    className="finding-evidence",
                                ),
                            ],
                            className=(
                                "finding-card " f"finding-card-{finding['tone']}"
                            ),
                        )
                        for finding in findings
                    ],
                    className="findings-grid",
                ),
                html.Div(
                    [
                        html.Span("The reporting rule", className="finding-rule-label"),
                        html.Strong(
                            "There is no context-free ranking: the answer is technology "
                            "× counterfactual × scenario × timing × horizon."
                        ),
                    ],
                    className="finding-rule",
                ),
            ],
            className="findings-slide",
        ),
        eyebrow="Synthesis · results per physical net tonne stored",
        lead=(
            "The same denominator produces similar present-day totals, unequal "
            "scenario sensitivity and different time-explicit magnitudes."
        ),
    )


def _summary_ranking_figure(
    static_beccs: float,
    static_daccs: float,
    lifetime_beccs: float,
    lifetime_daccs: float,
    pulse_beccs: float,
    pulse_daccs: float,
):
    stages = [
        "2025 static<br><span style='font-size:9px'>GWP100</span>",
        "2030–2049 cohort<br><span style='font-size:9px'>GWP100 · PkBudg1000</span>",
        "Dated response<br><span style='font-size:9px'>RF pulse-equivalent</span>",
    ]
    figure = go.Figure()
    series = [
        (
            "BECCS",
            [2, 2, 2],
            [static_beccs, lifetime_beccs, pulse_beccs],
            "#3e7654",
            ["bottom right", "bottom right", "top right"],
        ),
        (
            "DACCS",
            [1, 1, 1],
            [static_daccs, lifetime_daccs, pulse_daccs],
            "#4193b8",
            ["top left", "top left", "bottom left"],
        ),
    ]
    for name, ranks, values, color, positions in series:
        figure.add_trace(
            go.Scatter(
                x=[0, 1, 2],
                y=ranks,
                mode="lines+markers+text",
                name=name,
                text=[f"−{abs(value):,.0f}" for value in values],
                textposition=positions,
                textfont={"size": 11, "color": color},
                customdata=[
                    [
                        stage.replace("<br>", " ").split("<span")[0],
                        f"{value:,.0f}",
                    ]
                    for stage, value in zip(stages, values)
                ],
                hovertemplate=(
                    f"<b>{name}</b><br>%{{customdata[0]}}<br>"
                    "%{customdata[1]} kg per net t<extra></extra>"
                ),
                line={"width": 5, "color": color, "shape": "spline"},
                marker={
                    "size": 16,
                    "color": color,
                    "line": {"width": 4, "color": "white"},
                },
                cliponaxis=False,
            )
        )
    band_colors = [
        "rgba(0,107,143,.055)",
        "rgba(217,150,20,.07)",
        "rgba(0,138,130,.06)",
    ]
    for x, color in enumerate(band_colors):
        figure.add_vrect(
            x0=x - 0.34,
            x1=x + 0.34,
            fillcolor=color,
            line_width=0,
            layer="below",
        )
    figure.add_annotation(
        x=1.5,
        y=1.5,
        text="RANKING HOLDS",
        showarrow=False,
        bgcolor="#fff2cf",
        bordercolor="#e4bf58",
        borderpad=5,
        font={"size": 9, "color": "#6d510c"},
    )
    figure.update_layout(
        margin={"l": 66, "r": 34, "t": 9, "b": 54},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="closest",
        showlegend=True,
        legend={
            "orientation": "h",
            "x": 0,
            "y": 1.05,
            "xanchor": "left",
            "yanchor": "bottom",
            "font": {"size": 10},
            "itemsizing": "constant",
        },
        xaxis={
            "range": [-0.4, 2.4],
            "tickmode": "array",
            "tickvals": [0, 1, 2],
            "ticktext": stages,
            "tickfont": {"size": 10, "color": "#425b65"},
            "showgrid": False,
            "zeroline": False,
            "fixedrange": True,
        },
        yaxis={
            "range": [2.35, 0.65],
            "tickmode": "array",
            "tickvals": [1, 2],
            "ticktext": ["1 · stronger", "2"],
            "tickfont": {"size": 9, "color": "#657981"},
            "title": {
                "text": "RANK WITHIN EACH LENS",
                "font": {"size": 9, "color": "#657981"},
            },
            "showgrid": True,
            "gridcolor": "rgba(122,145,154,.18)",
            "zeroline": False,
            "fixedrange": True,
        },
        font={"family": "Arial, Helvetica, sans-serif", "color": "#17232c"},
    )
    return figure


def _cross_metric_synthesis(index: int):
    static_beccs = static_score(
        "BECCS",
        "SSP2-NPi",
        2025,
        "new CHP+CCS vs standing forest and Northern European energy",
    )
    static_daccs = static_score("DACCS", "SSP2-NPi", 2025, "not applicable")
    lifetime = {
        case: {
            pathway: lifetime_score_per_net_tonne(case, pathway)
            for pathway in ("SSP2-NPi", "SSP2-PkBudg1000")
        }
        for case in ("BECCS", "DACCS")
    }
    pulse = {
        case: cohort_co2_pulse_equivalent(
            case, "radiative forcing", 1940, 2100, 50.0, 2030
        )
        for case in ("BECCS", "DACCS")
    }
    window_values = [
        (
            start,
            cohort_co2_pulse_equivalent(
                "BECCS", "radiative forcing", start, 2100, 50.0, 2030
            ),
        )
        for start in (1940, 2000, 2025)
    ]
    beccs_shift = abs(
        lifetime["BECCS"]["SSP2-PkBudg1000"] - lifetime["BECCS"]["SSP2-NPi"]
    )
    daccs_shift = abs(
        lifetime["DACCS"]["SSP2-PkBudg1000"] - lifetime["DACCS"]["SSP2-NPi"]
    )
    ranking_figure = _summary_ranking_figure(
        static_beccs,
        static_daccs,
        lifetime["BECCS"]["SSP2-PkBudg1000"],
        lifetime["DACCS"]["SSP2-PkBudg1000"],
        pulse["BECCS"],
        pulse["DACCS"],
    )
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Section(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span("The result in one view"),
                                                html.H3(
                                                    "Who has the stronger removal score?"
                                                ),
                                            ]
                                        ),
                                        html.Span(
                                            "Exact values shown at every marker",
                                            className="summary-panel-note",
                                        ),
                                    ],
                                    className="summary-panel-heading",
                                ),
                                dcc.Graph(
                                    id="summary-ranking-graph",
                                    figure=ranking_figure,
                                    config={
                                        "displayModeBar": False,
                                        "responsive": True,
                                    },
                                    className="summary-ranking-graph",
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            [
                                                html.Img(
                                                    src="assets/icons/heat.svg", alt=""
                                                ),
                                                html.B("BECCS"),
                                                "future regrowth −1,143",
                                            ]
                                        ),
                                        html.Span(
                                            [
                                                html.Img(
                                                    src="assets/icons/power.svg", alt=""
                                                ),
                                                html.B("DACCS"),
                                                "electricity +492",
                                            ]
                                        ),
                                        html.Em("kg CO₂-eq / net t · 2025"),
                                    ],
                                    className="summary-driver-strip",
                                ),
                            ],
                            className="summary-ranking-panel",
                        ),
                        html.Div(
                            [
                                html.Article(
                                    [
                                        html.Div(
                                            [
                                                html.Span("Scenario effect"),
                                                html.Strong("3.2×"),
                                            ],
                                            className="summary-insight-heading",
                                        ),
                                        html.H3(
                                            "DACCS moves slightly more between pathways"
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.B("BECCS"),
                                                        html.Span(
                                                            f"−{abs(lifetime['BECCS']['SSP2-NPi']):,.0f}"
                                                        ),
                                                        html.I("→"),
                                                        html.Span(
                                                            f"−{abs(lifetime['BECCS']['SSP2-PkBudg1000']):,.0f}"
                                                        ),
                                                        html.Em(
                                                            f"Δ −{beccs_shift:.0f}"
                                                        ),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.B("DACCS"),
                                                        html.Span(
                                                            f"−{abs(lifetime['DACCS']['SSP2-NPi']):,.0f}"
                                                        ),
                                                        html.I("→"),
                                                        html.Span(
                                                            f"−{abs(lifetime['DACCS']['SSP2-PkBudg1000']):,.0f}"
                                                        ),
                                                        html.Em(
                                                            f"Δ −{daccs_shift:.0f}"
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            className="summary-pathway-rows",
                                        ),
                                        html.P(
                                            "SSP2-NPi → SSP2-PkBudg1000 · "
                                            "2030–2049 lifetime GWP100"
                                        ),
                                    ],
                                    className="summary-insight summary-insight-scenario",
                                ),
                                html.Article(
                                    [
                                        html.Div(
                                            [
                                                html.Span("Window effect"),
                                                html.Strong(
                                                    f"−{abs(window_values[0][1]):,.0f} "
                                                    f"→ −{abs(window_values[-1][1]):,.0f}"
                                                ),
                                            ],
                                            className="summary-insight-heading",
                                        ),
                                        html.H3("Pre-construction window starts agree"),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.B(str(start)),
                                                        html.Span(
                                                            f"−{abs(value):,.0f}"
                                                        ),
                                                    ]
                                                )
                                                for start, value in window_values
                                            ],
                                            className="summary-window-points",
                                        ),
                                        html.P(
                                            "Window start · end 2100 · 2030 "
                                            "reference pulse · BECCS"
                                        ),
                                    ],
                                    className="summary-insight summary-insight-window",
                                ),
                            ],
                            className="summary-insight-stack",
                        ),
                    ],
                    className="summary-main-grid",
                ),
                html.Div(
                    [
                        html.Strong("The ranking is conditional."),
                        html.Span("technology"),
                        html.B("×"),
                        html.Span("counterfactual"),
                        html.B("×"),
                        html.Span("scenario"),
                        html.B("×"),
                        html.Span("timing"),
                        html.B("×"),
                        html.Span("horizon"),
                    ],
                    className="summary-verdict",
                ),
            ],
            className="summary-results-slide",
        ),
        eyebrow="Synthesis · actual results per physical net tonne stored",
        lead=(
            "Greenfield BECCS leads under prospective static GWP100 and the dated "
            "response in this standing-forest reference; its future regrowth is an "
            "explicit project consequence."
        ),
    )


def _summary_gwp_figure(
    static_beccs: float,
    static_daccs: float,
    lifetime_beccs_npi: float,
    lifetime_daccs_npi: float,
    lifetime_beccs_budget: float,
    lifetime_daccs_budget: float,
):
    rows = [
        "2025 static · NPi",
        "2030–2049 cohort · NPi",
        "2030–2049 cohort · PkBudg1000",
    ]
    beccs = [static_beccs, lifetime_beccs_npi, lifetime_beccs_budget]
    daccs = [static_daccs, lifetime_daccs_npi, lifetime_daccs_budget]
    all_values = [*beccs, *daccs]
    span = max(all_values) - min(all_values)
    padding = max(18.0, span * 0.12)
    x_range = [min(all_values) - padding, max(all_values) + padding]
    figure = go.Figure()
    for row, left, right in zip(rows, beccs, daccs):
        figure.add_shape(
            type="line",
            x0=min(left, right),
            x1=max(left, right),
            y0=row,
            y1=row,
            line={"color": "#b7c9cf", "width": 4},
            layer="below",
        )
    for case, values, color, position in (
        ("BECCS", beccs, "#3e7654", "bottom center"),
        ("DACCS", daccs, "#4193b8", "top center"),
    ):
        figure.add_trace(
            go.Scatter(
                x=values,
                y=rows,
                mode="markers+text",
                name=case,
                text=[f"−{abs(value):,.0f}" for value in values],
                textposition=position,
                textfont={"size": 10, "color": color},
                customdata=[[row, f"{value:,.0f}"] for row, value in zip(rows, values)],
                hovertemplate=(
                    f"<b>{case}</b><br>%{{customdata[0]}}<br>"
                    "%{customdata[1]} kg CO₂-eq / net t<extra></extra>"
                ),
                marker={
                    "size": 15,
                    "color": color,
                    "line": {"width": 4, "color": "white"},
                },
                cliponaxis=False,
            )
        )
    figure.add_annotation(
        x=x_range[0] + padding * 0.35,
        y=1.16,
        text="← lower GWP100",
        showarrow=False,
        xanchor="left",
        font={"size": 8, "color": "#6a7d85"},
    )
    figure.update_layout(
        margin={"l": 165, "r": 26, "t": 22, "b": 39},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="closest",
        legend={
            "orientation": "h",
            "x": 0,
            "y": 1.12,
            "xanchor": "left",
            "yanchor": "bottom",
            "font": {"size": 10},
            "itemsizing": "constant",
        },
        xaxis={
            "range": x_range,
            "title": {
                "text": "kg CO₂-eq per net t stored",
                "font": {"size": 9, "color": "#60757e"},
            },
            "tickfont": {"size": 8, "color": "#60757e"},
            "showgrid": True,
            "gridcolor": "rgba(122,145,154,.16)",
            "zeroline": False,
            "fixedrange": True,
        },
        yaxis={
            "categoryorder": "array",
            "categoryarray": list(reversed(rows)),
            "tickfont": {"size": 9, "color": "#425b65"},
            "showgrid": False,
            "fixedrange": True,
        },
        font={"family": "Arial, Helvetica, sans-serif", "color": "#17232c"},
    )
    return figure


def _summary_pulse_end_figure(
    window_ends: list[int],
    beccs_values: list[float],
    daccs_values: list[float],
):
    """Show pulse-equivalence directly against the chosen window end year."""

    figure = go.Figure()
    for case, values, color, positions in (
        (
            "BECCS",
            beccs_values,
            "#3e7654",
            ["top center", "top left", "bottom left", "bottom center"],
        ),
        (
            "DACCS",
            daccs_values,
            "#4193b8",
            ["bottom center", "bottom right", "top right", "top center"],
        ),
    ):
        figure.add_trace(
            go.Scatter(
                x=window_ends,
                y=values,
                mode="lines+markers+text",
                name=case,
                text=[f"−{abs(value):,.0f}" for value in values],
                textposition=positions,
                textfont={"size": 10, "color": color},
                customdata=[
                    [end, f"{value:,.0f}"]
                    for end, value in zip(window_ends, values, strict=True)
                ],
                hovertemplate=(
                    f"<b>{case}</b><br>Window ends %{{customdata[0]}}<br>"
                    "%{customdata[1]} kg CO₂ pulse-eq / net t<extra></extra>"
                ),
                line={"width": 3.2, "color": color},
                marker={
                    "size": 11,
                    "color": color,
                    "line": {"width": 2.5, "color": "white"},
                },
                cliponaxis=False,
            )
        )
    figure.add_vline(
        x=2132,
        line={"color": "#6b8f75", "width": 1.6, "dash": "dot"},
    )
    figure.add_annotation(
        x=2132,
        y=-350,
        xref="x",
        yref="y",
        text="2132 · regrowth complete",
        showarrow=False,
        xanchor="left",
        yanchor="top",
        bgcolor="rgba(243,247,247,.92)",
        borderpad=2,
        font={"size": 8, "color": "#4e7259"},
    )
    figure.add_annotation(
        x=2170,
        y=(beccs_values[2] + daccs_values[2]) / 2,
        text="ranking flips ≈ 2170",
        showarrow=True,
        arrowhead=2,
        arrowwidth=1,
        arrowcolor="#526a73",
        ax=42,
        ay=34,
        bgcolor="rgba(255,255,255,.94)",
        bordercolor="#cbdadc",
        borderpad=2,
        font={"size": 8, "color": "#405861"},
    )
    figure.update_layout(
        margin={"l": 54, "r": 14, "t": 26, "b": 38},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f3f7f7",
        hovermode="closest",
        legend={
            "orientation": "h",
            "x": 1,
            "y": 1.16,
            "xanchor": "right",
            "yanchor": "bottom",
            "font": {"size": 9},
            "itemsizing": "constant",
        },
        xaxis={
            "range": [2085, 2310],
            "tickmode": "array",
            "tickvals": window_ends,
            "ticktext": [str(year) for year in window_ends],
            "title": {
                "text": "Integration-window end year",
                "font": {"size": 9, "color": "#60757e"},
            },
            "tickfont": {"size": 8, "color": "#60757e"},
            "showgrid": True,
            "gridcolor": "rgba(122,145,154,.14)",
            "zeroline": False,
            "fixedrange": True,
        },
        yaxis={
            "range": [-1125, -325],
            "tickmode": "array",
            "tickvals": [-1000, -800, -600, -400],
            "title": {
                "text": "kg CO₂ pulse-eq / net t",
                "font": {"size": 9, "color": "#60757e"},
            },
            "tickfont": {"size": 8, "color": "#60757e"},
            "showgrid": True,
            "gridcolor": "rgba(122,145,154,.16)",
            "zeroline": False,
            "fixedrange": True,
        },
        font={"family": "Arial, Helvetica, sans-serif", "color": "#17232c"},
    )
    return figure


def _synthesis(index: int):
    static = {
        "BECCS": static_score(
            "BECCS",
            "SSP2-NPi",
            2025,
            "new CHP+CCS vs standing forest and Northern European energy",
        ),
        "DACCS": static_score("DACCS", "SSP2-NPi", 2025, "not applicable"),
    }
    lifetime = {
        case: {
            pathway: lifetime_score_per_net_tonne(case, pathway)
            for pathway in ("SSP2-NPi", "SSP2-PkBudg1000")
        }
        for case in ("BECCS", "DACCS")
    }
    window_ends = [2100, 2140, 2170, 2300]
    pulse = {
        case: [
            cohort_co2_pulse_equivalent(
                case, "radiative forcing", 2025, end, 50.0, 2030
            )
            for end in window_ends
        ]
        for case in ("BECCS", "DACCS")
    }
    window_change = {
        case: pulse[case][-1] - pulse[case][0] for case in ("BECCS", "DACCS")
    }
    routed_temporal = {
        case: cohort_temporal_total(case, "per_tonne") for case in ("BECCS", "DACCS")
    }
    forest_screen = forest_pool_sensitivity("routed")
    pulse_gap = abs(pulse["DACCS"][0] - pulse["BECCS"][0])
    final_pulse_gap = abs(pulse["DACCS"][-1] - pulse["BECCS"][-1])
    gwp_figure = _summary_gwp_figure(
        static["BECCS"],
        static["DACCS"],
        lifetime["BECCS"]["SSP2-NPi"],
        lifetime["DACCS"]["SSP2-NPi"],
        lifetime["BECCS"]["SSP2-PkBudg1000"],
        lifetime["DACCS"]["SSP2-PkBudg1000"],
    )
    pulse_end_figure = _summary_pulse_end_figure(
        window_ends, pulse["BECCS"], pulse["DACCS"]
    )
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Span("Static inventory score"),
                        html.Strong("≠"),
                        html.Span("Dated climate-response equivalence"),
                    ],
                    className="summary-indicator-banner",
                ),
                html.Div(
                    [
                        html.Section(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span("Inventory accounting"),
                                                html.H3("IPCC 2021 GWP100"),
                                            ]
                                        ),
                                        html.P(
                                            "Baseline scores, with a separate forest-carbon sensitivity"
                                        ),
                                    ],
                                    className="summary-metric-heading",
                                ),
                                dcc.Graph(
                                    id="summary-gwp-graph",
                                    figure=gwp_figure,
                                    config={
                                        "displayModeBar": False,
                                        "responsive": True,
                                    },
                                    className="summary-metric-graph",
                                ),
                                html.Div(
                                    [
                                        html.Strong("Result"),
                                        html.Span(
                                            "The routed uptake-only BECCS result needs only "
                                            f"+{float(forest_screen['break_even_correction']):,.0f} kg "
                                            f"({100 * float(forest_screen['break_even_fraction']):.1f}% "
                                            "of gross regrowth) to tie DACCS."
                                        ),
                                        html.Em(
                                            f"10% test: BECCS {_format_score(float(forest_screen['stress_test_beccs']))} · "
                                            f"DACCS {_format_score(routed_temporal['DACCS'])} kg"
                                        ),
                                    ],
                                    className="summary-metric-finding",
                                ),
                            ],
                            className="summary-metric-panel summary-metric-gwp",
                        ),
                        html.Section(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span("Dated climate response"),
                                                html.H3("CO₂ pulse-equivalence"),
                                            ]
                                        ),
                                        html.P(
                                            "Baseline only: how does the equivalent change as "
                                            "the horizon includes delayed forest regrowth?"
                                        ),
                                    ],
                                    className="summary-metric-heading",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span("Fixed comparison"),
                                                html.B("·"),
                                                html.Span("window starts in 2025"),
                                                html.B("·"),
                                                html.Span(
                                                    "positive reference pulse fixed in 2030"
                                                ),
                                            ],
                                            className="summary-pulse-fixed",
                                        ),
                                        dcc.Graph(
                                            id="summary-pulse-end-graph",
                                            figure=pulse_end_figure,
                                            config={
                                                "displayModeBar": False,
                                                "responsive": True,
                                            },
                                            className="summary-pulse-end-graph",
                                        ),
                                    ],
                                    id="summary-pulse-window-timelines",
                                    className="summary-pulse-end-panel",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Strong(f"{pulse_gap:,.0f} kg"),
                                                html.Span("DACCS lead at 2100"),
                                            ],
                                            className="summary-metric-tile tile-daccs",
                                        ),
                                        html.Div(
                                            [
                                                html.Strong("≈ 2170"),
                                                html.Span("ranking crosses"),
                                            ],
                                            className="summary-metric-tile tile-crossing",
                                        ),
                                        html.Div(
                                            [
                                                html.Strong(
                                                    f"{final_pulse_gap:,.0f} kg"
                                                ),
                                                html.Span("BECCS lead at 2300"),
                                            ],
                                            className="summary-metric-tile tile-beccs",
                                        ),
                                    ],
                                    className="summary-metric-tiles",
                                ),
                            ],
                            className="summary-metric-panel summary-metric-pulse",
                        ),
                    ],
                    className="summary-separated-grid",
                ),
                html.Div(
                    [
                        html.Strong("The indicators answer different questions."),
                        html.Span(
                            "The forest-carbon sensitivity changes GWP totals only; updating FaIR "
                            "also requires a defensible residue, root and soil-carbon time profile."
                        ),
                    ],
                    className="summary-separate-verdict",
                ),
            ],
            className="summary-separated-slide",
        ),
        eyebrow="Synthesis · two indicators, two analytical questions",
        lead=(
            "BECCS leads in the uptake-only baseline, but a small post-harvest "
            "forest-carbon correction can reverse its GWP100 ranking."
        ),
    )


def _method_lens_card(
    *,
    number: str,
    title: str,
    shorthand: str,
    question: str,
    strengths: tuple[str, ...],
    limitations: tuple[str, ...],
    tone: str,
):
    visual = {
        "current": {
            "positions": (50,),
            "caption": "one present-day snapshot",
            "background": "today",
            "timing": "collapsed",
            "effort": 1,
        },
        "prospective": {
            "positions": (18, 50, 82),
            "caption": "choose a scenario + target year",
            "background": "future",
            "timing": "snapshot",
            "effort": 2,
        },
        "explicit": {
            "positions": (10, 36, 63, 90),
            "caption": "route each event on the calendar",
            "background": "annual",
            "timing": "dated",
            "effort": 3,
        },
    }[tone]
    return html.Article(
        [
            html.Div(
                [
                    html.Div(
                        [html.Strong(shorthand), html.Small(number)],
                        className="method-lens-glyph",
                    ),
                    html.Div(
                        [
                            html.Span(number),
                            html.H3(title),
                            html.P(question),
                        ],
                        className="method-lens-heading",
                    ),
                ],
                className="method-lens-header",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            *[
                                html.Span(
                                    className="method-time-node",
                                    style={"left": f"{position}%"},
                                )
                                for position in visual["positions"]
                            ],
                            html.Em(visual["caption"]),
                        ],
                        className=f"method-time-track method-time-track-{tone}",
                    ),
                    html.Div(
                        [
                            html.Span([html.Small("Background"), visual["background"]]),
                            html.Span([html.Small("Timing"), visual["timing"]]),
                            html.Span(
                                [
                                    html.Small("Effort"),
                                    html.I(
                                        [
                                            html.B(
                                                className=(
                                                    "active"
                                                    if dot < visual["effort"]
                                                    else ""
                                                )
                                            )
                                            for dot in range(3)
                                        ]
                                    ),
                                ]
                            ),
                        ],
                        className="method-lens-signals",
                    ),
                ],
                className="method-lens-visual",
            ),
            html.Div(
                [
                    html.Section(
                        [
                            html.Strong("Pros"),
                            html.Ul([html.Li(item) for item in strengths]),
                        ],
                        className="method-lens-list method-lens-pros",
                    ),
                    html.Section(
                        [
                            html.Strong("Cons"),
                            html.Ul([html.Li(item) for item in limitations]),
                        ],
                        className="method-lens-list method-lens-cons",
                    ),
                ],
                className="method-lens-tradeoffs",
            ),
        ],
        className=f"method-lens-card method-lens-{tone}",
    )


def _method_choice_card(
    *,
    first: str,
    second: str,
    first_when: str,
    second_when: str,
    gain: str,
    tone: str,
):
    return html.Article(
        [
            html.Div(
                [
                    html.Span(first),
                    html.Div(html.B(html.Span("?")), className="method-choice-route"),
                    html.Span(second),
                ],
                className="method-choice-transition",
            ),
            html.Div(
                [
                    html.Section(
                        [html.Strong(f"Stay with {first}"), html.P(first_when)]
                    ),
                    html.Section(
                        [html.Strong(f"Choose {second}"), html.P(second_when)]
                    ),
                ],
                className="method-choice-decisions",
            ),
            html.Div(
                [
                    html.B("+", className="method-choice-gain-icon"),
                    html.Strong("What the next layer adds"),
                    html.Span(gain),
                ],
                className="method-choice-gain",
            ),
        ],
        className=f"method-choice-card method-choice-{tone}",
    )


def _method_tradeoff_summary_base(index: int):
    return _slide_shell(
        index,
        html.Div(
            [
                html.Section(
                    [
                        html.Div(
                            [
                                html.Span("1", className="method-summary-step"),
                                html.Div(
                                    [
                                        html.H2("Compare the three analytical lenses"),
                                        html.P(
                                            "More temporal detail improves realism but requires more data and validation."
                                        ),
                                    ]
                                ),
                            ],
                            className="method-summary-block-heading",
                        ),
                        html.Div(
                            [
                                _method_lens_card(
                                    number="Present day",
                                    title="Current static LCA",
                                    shorthand="t₀",
                                    question="What is the impact today?",
                                    strengths=(
                                        "Fast + established",
                                        "Useful screening benchmark",
                                    ),
                                    limitations=(
                                        "Present-day background only",
                                        "No event timing",
                                    ),
                                    tone="current",
                                ),
                                _method_lens_card(
                                    number="Future scenario",
                                    title="Prospective static LCA",
                                    shorthand="tᵧ",
                                    question="What is the impact in a future scenario and year?",
                                    strengths=(
                                        "Future technologies and markets",
                                        "Explicit scenario assumptions",
                                    ),
                                    limitations=(
                                        "Events remain undated",
                                        "Scenario uncertainty",
                                    ),
                                    tone="prospective",
                                ),
                                _method_lens_card(
                                    number="Dated pathway",
                                    title="Time-explicit prospective LCA",
                                    shorthand="t→",
                                    question="When do exchanges and effects occur?",
                                    strengths=(
                                        "Dates every event",
                                        "Tracks climate response",
                                    ),
                                    limitations=(
                                        "More data and validation",
                                        "Result depends on horizon",
                                    ),
                                    tone="explicit",
                                ),
                            ],
                            className="method-lens-grid",
                        ),
                    ],
                    className="method-summary-block method-summary-comparison",
                ),
                html.Section(
                    [
                        html.Div(
                            [
                                html.Span("2", className="method-summary-step"),
                                html.Div(
                                    [
                                        html.H2(
                                            "Decide whether the extra temporal detail is needed"
                                        ),
                                        html.P(
                                            "Use the simplest method that still captures mechanisms that could change the conclusion."
                                        ),
                                    ]
                                ),
                            ],
                            className="method-summary-block-heading",
                        ),
                        html.Div(
                            [
                                _method_choice_card(
                                    first="current static",
                                    second="prospective static",
                                    first_when=(
                                        "Use when background change is unlikely to alter the ranking."
                                    ),
                                    second_when=(
                                        "Use when future energy, materials, policy or technology could alter the result."
                                    ),
                                    gain=(
                                        "Future context · scenarios · target years · technology change"
                                    ),
                                    tone="future",
                                ),
                                _method_choice_card(
                                    first="prospective static",
                                    second="time-explicit",
                                    first_when=(
                                        "Future context matters; event order and delay do not."
                                    ),
                                    second_when=(
                                        "Use when the timing of construction, uptake, release, regrowth or end-of-life matters."
                                    ),
                                    gain=(
                                        "Event order · persistence · cohorts · climate response"
                                    ),
                                    tone="timing",
                                ),
                            ],
                            className="method-choice-grid",
                        ),
                    ],
                    className="method-summary-block method-summary-choice",
                ),
            ],
            className="method-summary-slide",
        ),
        eyebrow="Synthesis · method choice",
        lead=("Add temporal detail only when timing could change the conclusion."),
    )


def _method_tradeoff_summary(index: int, print_mode: bool = False):
    slide = _method_tradeoff_summary_base(index)
    body = slide.children[1]
    summary = body.children
    focus = "combined" if print_mode else "compare"
    body.children = [
        html.Div(
            [
                html.Span("Focus", className="focus-control-label"),
                dcc.RadioItems(
                    options=[
                        {"label": "Compare methods", "value": "compare"},
                        {"label": "Decision rules", "value": "decide"},
                    ],
                    value="compare",
                    inline=True,
                    className="contribution-view-toggle method-focus-control",
                    **({} if print_mode else {"id": "method-focus-control"}),
                ),
            ],
            className="teaching-focus-toolbar print-expanded-control",
        ),
        html.Div(
            summary,
            className=f"method-focus-view method-focus-{focus}",
            **({} if print_mode else {"id": "method-focus-view"}),
        ),
    ]
    return slide


def _tool_mark(kind: str):
    if kind == "premise":
        return html.Img(src="assets/premise-logo.png", alt="premise")
    if kind == "trails":
        return html.Img(src="assets/trails-logo.png", alt="TRAILS")
    if kind == "remind":
        return html.Img(src="assets/pik-logo.png", alt="PIK")
    labels = {
        "ecoinvent": ("LCI", "database"),
        "brightway": ("A × B", "LCA"),
        "fair": ("ΔRF", "→ ΔT"),
    }
    primary, secondary = labels[kind]
    return html.Div(
        [html.Strong(primary), html.Span(secondary)],
        className=f"tool-glyph tool-glyph-{kind}",
    )


def _tool_card(tool: dict[str, str]):
    return html.A(
        [
            html.Div(_tool_mark(tool["kind"]), className="tool-mark"),
            html.Div(
                [
                    html.Div(
                        [html.H3(tool["name"]), html.Span("↗")],
                        className="tool-card-title",
                    ),
                    html.P(tool["role"]),
                    html.Span(tool["host"], className="tool-host"),
                ],
                className="tool-card-copy",
            ),
        ],
        href=tool["href"],
        target="_blank",
        rel="noopener noreferrer",
        className=f"tool-card tool-card-{tool['kind']}",
        title=f"Open {tool['name']} documentation",
    )


def _tools_slide(index: int):
    groups = [
        (
            "Scenarios & inventory data",
            "What assumptions and supply-chain data define the starting point?",
            [
                {
                    "kind": "remind",
                    "name": "REMIND",
                    "role": "Integrated-assessment pathways for energy, industry and climate policy.",
                    "host": "rse.pik-potsdam.de",
                    "href": "https://rse.pik-potsdam.de/doc/remind/3.7.0/",
                },
                {
                    "kind": "ecoinvent",
                    "name": "ecoinvent",
                    "role": "Unit-process life-cycle inventory data for background systems.",
                    "host": "ecoinvent.org/database",
                    "href": "https://ecoinvent.org/database/",
                },
            ],
        ),
        (
            "Prospective LCA",
            "How are scenario pathways translated into LCA inventories?",
            [
                {
                    "kind": "premise",
                    "name": "premise",
                    "role": "Maps background inventories to IAM pathways and target years.",
                    "host": "premise.readthedocs.io",
                    "href": "https://premise.readthedocs.io/en/latest/",
                },
                {
                    "kind": "brightway",
                    "name": "Brightway",
                    "role": "Open Python ecosystem for inventory modelling and LCIA calculations.",
                    "host": "docs.brightway.dev",
                    "href": "https://docs.brightway.dev/en/latest/",
                },
            ],
        ),
        (
            "Time & climate response",
            "When do exchanges occur, and how does the climate respond?",
            [
                {
                    "kind": "trails",
                    "name": "TRAILS",
                    "role": "Routes dated exchanges through annual inventories while preserving year and source.",
                    "host": "trails.readthedocs.io",
                    "href": "https://trails.readthedocs.io/en/latest/",
                },
                {
                    "kind": "fair",
                    "name": "FaIR",
                    "role": "Converts dated emissions and removals into forcing and temperature responses.",
                    "host": "docs.fairmodel.net",
                    "href": "https://docs.fairmodel.net/en/latest/",
                },
            ],
        ),
    ]
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    [
                        html.Section(
                            [
                                html.Div(
                                    [
                                        html.Span(f"0{position}"),
                                        html.Div([html.H2(title), html.P(question)]),
                                    ],
                                    className="tool-group-heading",
                                ),
                                html.Div(
                                    [_tool_card(tool) for tool in tools],
                                    className="tool-card-stack",
                                ),
                            ],
                            className="tool-group",
                        )
                        for position, (title, question, tools) in enumerate(
                            groups, start=1
                        )
                    ],
                    className="tool-groups",
                ),
                html.Div(
                    [
                        html.Strong("Workflow used here"),
                        html.Span("REMIND + ecoinvent"),
                        html.B("→"),
                        html.Span("premise"),
                        html.B("→"),
                        html.Span("TRAILS / Brightway"),
                        html.B("→"),
                        html.Span("FaIR"),
                        html.Em("Click any card to open its documentation ↗"),
                    ],
                    className="tool-workflow",
                ),
                html.Div(
                    [
                        html.Span([html.B("Database"), "ecoinvent 3.12"]),
                        html.Span([html.B("Temporal engine"), "TRAILS 1.0.1"]),
                        html.Span(
                            [html.B("Scenario"), "REMIND-EU SSP2-NPi / PkBudg1000"]
                        ),
                        html.Span([html.B("Calculated"), "23 Aug 2026"]),
                    ],
                    className="reproducibility-strip",
                ),
            ],
            className="tools-slide",
        ),
        eyebrow="Resources · open documentation and project pages",
        lead=(
            "The workflow separates scenario assumptions, inventory data, "
            "scenario-to-inventory mapping, temporal routing and climate response."
        ),
    )


def _thank_you_slide(index: int):
    return _slide_shell(
        index,
        html.Div(
            [
                html.Div(
                    "Model time explicitly when timing can change the interpretation or decision.",
                    className="closing-takeaway",
                ),
                html.Section(
                    [
                        html.Span("Closing discussion", className="thank-you-kicker"),
                        html.H2("Questions for discussion"),
                        html.P(
                            "This analysis covers GHG emissions and climate response, not "
                            "a complete environmental assessment.",
                            className="thank-you-scope",
                        ),
                        html.Div(
                            [
                                html.Article(
                                    [
                                        html.Span(
                                            "01", className="thank-you-question-number"
                                        ),
                                        html.Strong("Beyond climate"),
                                        html.P(
                                            "Could land use, water, biodiversity, toxicity "
                                            "or material supply change the conclusion?"
                                        ),
                                    ]
                                ),
                                html.Article(
                                    [
                                        html.Span(
                                            "02", className="thank-you-question-number"
                                        ),
                                        html.Strong("Value of timing"),
                                        html.P(
                                            "When do delays, temporary storage or changing "
                                            "backgrounds justify time-explicit LCA?"
                                        ),
                                    ]
                                ),
                                html.Article(
                                    [
                                        html.Span(
                                            "03", className="thank-you-question-number"
                                        ),
                                        html.Strong("Sensitivity to assumptions"),
                                        html.P(
                                            "How do the counterfactual, forest growth, plant lifetime "
                                            "and assessment horizon affect the result?"
                                        ),
                                    ]
                                ),
                            ],
                            className="thank-you-questions",
                        ),
                    ],
                    className="thank-you-prompt",
                ),
                html.A(
                    [
                        html.Img(
                            src="assets/psi-mark.svg", alt="Paul Scherrer Institute"
                        ),
                        html.Div(
                            [
                                html.Span(
                                    "Contact", className="thank-you-contact-label"
                                ),
                                html.H2("Romain Sacchi"),
                                html.P("Laboratory for Energy Systems Analyses"),
                                html.P("Paul Scherrer Institute (PSI)"),
                                html.Strong("romain.sacchi@psi.ch"),
                            ]
                        ),
                        html.Span(
                            "Write to me ↗", className="thank-you-contact-action"
                        ),
                    ],
                    href="mailto:romain.sacchi@psi.ch",
                    className="thank-you-contact",
                    title="Email Romain Sacchi",
                ),
                html.A(
                    "Life Cycle Summer School 2026 · fslci.org/events/lcss2026",
                    href="https://fslci.org/events/lcss2026/",
                    target="_blank",
                    rel="noopener noreferrer",
                    className="thank-you-event-link",
                ),
            ],
            className="thank-you-layout",
        ),
        eyebrow="Life Cycle Summer School · Malmö · 2026",
        lead="Thank you. Which assumption, method or result should we examine next?",
    )


def _appendix_accounting(index: int):
    slide = _slide_shell(
        index,
        html.Div(
            [
                html.Section(
                    [
                        html.H2("Physical service and GWP100 accounting"),
                        html.Div(
                            [
                                html.Strong("Denominator"),
                                html.Span(
                                    "gross capture − physical transport loss = 1 net tonne stored"
                                ),
                                html.Strong("Numerator"),
                                html.Span(
                                    "CO₂ in air: CF −1 · non-fossil CO₂: CF +1 · other GHGs in CO₂-eq"
                                ),
                            ],
                            className="appendix-equation-ledger",
                        ),
                        html.P(
                            "Supply-chain GHGs change the impact numerator; they do not change the physical storage denominator."
                        ),
                    ],
                    className="appendix-card appendix-accounting-card",
                ),
                html.Section(
                    [
                        html.H2("Annual matrices and attribution"),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Strong("A(y)"),
                                        html.Span("year-specific technosphere"),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Strong("B(y)"),
                                        html.Span("year-specific biosphere"),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Strong("Gᵧ"),
                                        html.Span("inventory attributed to year y"),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Strong("Q"),
                                        html.Span("diagonal characterisation factors"),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Strong("Hᵧ = QGᵧ"),
                                        html.Span("characterised annual inventory"),
                                    ]
                                ),
                            ],
                            className="appendix-matrix-grid",
                        ),
                    ],
                    className="appendix-card appendix-matrix-card",
                ),
                html.Section(
                    [
                        html.H2("Pulse-equivalence scaling and gas clocks"),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Strong(
                                            "mₑₚ = mᵣᵉᶠ × ∫ΔXₛᵧₛₜₑₘ dt / ∫ΔXᵣᵉᶠ dt"
                                        ),
                                        html.Span(
                                            "configuration-first ratio; median across 841 FaIR configurations"
                                        ),
                                    ],
                                    className="appendix-pulse-equation",
                                ),
                                html.Img(
                                    src="assets/timing-gas-clocks.svg",
                                    alt="Methane has a strong near-term response while carbon dioxide persists much longer.",
                                    className="appendix-gas-clock",
                                ),
                            ],
                            className="appendix-pulse-grid",
                        ),
                    ],
                    className="appendix-card appendix-pulse-card",
                ),
            ],
            className="appendix-a-grid",
        ),
        eyebrow="Appendix · accounting detail",
        lead="Definitions and equations moved out of the teaching sequence.",
    )
    slide.id = "appendix-a"
    return slide


def _appendix_sources(index: int):
    references = (
        (
            "Rebitzer et al. (2004) · LCA framework",
            "https://doi.org/10.1016/j.envint.2003.11.005",
        ),
        (
            "Hellweg & Milà i Canals (2014) · LCA challenges",
            "https://doi.org/10.1126/science.1248361",
        ),
        (
            "Mendoza Beltran et al. (2020) · IAM backgrounds",
            "https://doi.org/10.1111/jiec.12825",
        ),
        (
            "Sacchi et al. (2022) · premise",
            "https://doi.org/10.1016/j.rser.2022.112311",
        ),
        (
            "Levasseur et al. (2010) · dynamic climate",
            "https://doi.org/10.1021/es9030003",
        ),
        (
            "Müller et al. (2025) · time-explicit LCA",
            "https://doi.org/10.1007/s11367-025-02539-3",
        ),
        (
            "Sacchi et al. (2026) · deep temporalisation",
            "https://www.researchsquare.com/article/rs-10139523/v1",
        ),
        (
            "Wanielik et al. (2025) · dynamic wood carbon",
            "https://doi.org/10.1016/j.procir.2025.01.089",
        ),
        (
            "Menichetti et al. (2025) · post-harvest forest carbon",
            "https://pub.epsilon.slu.se/37940/1/menichetti-l-et-al-20250721.pdf",
        ),
        (
            "Deutz & Bardow (2021) · DAC inventory",
            "https://doi.org/10.1038/s41560-020-00771-9",
        ),
        (
            "Qiu et al. (2022) · DAC energy",
            "https://doi.org/10.1038/s41467-022-31146-1",
        ),
        (
            "Koornneef / Terlouw · CO₂ transport",
            "https://doi.org/10.1021/acs.est.1c03263",
        ),
    )
    slide = _slide_shell(
        index,
        html.Div(
            [
                html.Section(
                    [
                        html.H2("References"),
                        html.Ul(
                            [
                                html.Li(
                                    html.A(
                                        label,
                                        href=href,
                                        target="_blank",
                                        rel="noopener noreferrer",
                                    )
                                )
                                for label, href in references
                            ],
                            className="appendix-reference-list",
                        ),
                    ],
                    className="appendix-card appendix-reference-card",
                ),
                html.Section(
                    [
                        html.H2("Inventory and scenario basis"),
                        _bullets(
                            [
                                "ecoinvent 3.12 cutoff · Northern Europe",
                                "REMIND-EU · SSP2-NPi and SSP2-PkBudg1000 · 2005–2100 anchors",
                                "Foreground sources: Volkart (capture), Deutz & Bardow / Qiu (DACCS), Koornneef / Terlouw (pipeline)",
                                "IPCC 2021 GWP100 including biogenic CO₂ · FaIR ensemble: 841 configurations",
                            ]
                        ),
                    ],
                    className="appendix-card appendix-inventory-card",
                ),
                html.Section(
                    [
                        html.H2("Software and calculation record"),
                        html.Dl(
                            [
                                html.Dt("premise / TRAILS"),
                                html.Dd("2.4.9.1 / 1.0.1"),
                                html.Dt("Database"),
                                html.Dd("ecoinvent 3.12 cutoff"),
                                html.Dt("Scenarios"),
                                html.Dd("SSP2-NPi / SSP2-PkBudg1000"),
                                html.Dt("Climate model"),
                                html.Dd("FaIR · 841 configurations"),
                                html.Dt("Calculation date"),
                                html.Dd("23 August 2026"),
                            ],
                            className="appendix-provenance-list",
                        ),
                    ],
                    className="appendix-card appendix-provenance-card",
                ),
            ],
            className="appendix-b-grid",
        ),
        eyebrow="Appendix · sources and provenance",
        lead="Full references, inventory sources, scenario metadata and software versions.",
    )
    slide.id = "appendix-b"
    return slide


RENDERERS = [
    _cover,
    _package_slide,
    _cases_slide,
    _functional_unit_slide,
    _beccs_system_slide,
    _daccs_system_slide,
    _static_contribution_slide,
    _prospective_intro,
    _prospective_transformation,
    _scenario_slide,
    _prospective_results,
    _time_intro,
    _annual_matrices_slide,
    _case_timing,
    _beccs_routing_graph_slide,
    _daccs_routing_graph_slide,
    _temporal_gwp_slide,
    _fair_response_slide,
    _pulse_equivalence_concept,
    _pulse_equivalence_slide,
    _synthesis,
    _method_tradeoff_summary,
    _tools_slide,
    _thank_you_slide,
    _appendix_accounting,
    _appendix_sources,
]


PRINT_AWARE_SLIDES = {2, 4, 5, 9, 10, 19, 21}


def render_slide(index: int, *, print_mode: bool = False):
    if index < 0 or index >= len(RENDERERS):
        raise IndexError(f"Unknown slide index: {index}")
    renderer = RENDERERS[index]
    if index == 0:
        slide = renderer()
    elif index in PRINT_AWARE_SLIDES:
        slide = renderer(index, print_mode=print_mode)
    else:
        slide = renderer(index)
    if index < CORE_SLIDE_COUNT:
        aria_label = f"Core slide {index + 1} of {CORE_SLIDE_COUNT}"
    else:
        appendix_number = index - APPENDIX_START_SLIDE + 1
        aria_label = f"Appendix slide {appendix_number} of {APPENDIX_SLIDE_COUNT}"
    slide.children = list(slide.children) + [
        html.Div(
            slide_label(index),
            className="slide-number",
            **{"aria-label": aria_label},
        )
    ]
    return slide


def slide_label(index: int) -> str:
    if index < 0 or index >= len(SLIDE_TITLES):
        raise IndexError(f"Unknown slide index: {index}")
    if index < CORE_SLIDE_COUNT:
        return f"{index + 1:02d} / {CORE_SLIDE_COUNT:02d}"
    appendix_number = index - APPENDIX_START_SLIDE + 1
    return f"A{appendix_number} / {APPENDIX_SLIDE_COUNT}"
