"""Focused backup explanations for the assumptions most likely to draw questions."""

from dash import html
import numpy as np
import plotly.graph_objects as go
from . import comparison as compare
from . import contributions as attribution
from .erw import campaign_profile
from .visuals import CASES
from .carbon import origin_key
from .layout import stack, text


def erw_timing():
    fig = go.Figure()
    values = []
    for duration, lag, colour in (
        (10, 1, "#008a82"),
        (30, 5, "#3292b5"),
        (100, 5, "#c18a1b"),
    ):
        p = campaign_profile(duration, lag, 1)
        uptake = np.cumsum(p["uptake_kg"]) / 10
        label = f"{duration}-year dissolution · {lag}-year lag"
        fig.add_scatter(
            x=p["age"],
            y=uptake,
            name=label,
            line=dict(color=colour, width=3),
            hovertemplate="Year +%{x:g}<br>%{y:.1f}% of reference potential<extra>%{fullData.name}</extra>",
        )
        values.append((label, f"{uptake[19]:.0f}%"))
    compare.style(fig, ytitle="Realized reference uptake · %")
    fig.update_xaxes(range=[0, 170], title="Years since start of 20-year rock deployment")
    fig.update_yaxes(range=[0, 105], dtick=25)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.25, x=0, font=dict(size=12)),
        margin=dict(l=58, r=18, t=30, b=95),
    )
    fig.add_vline(x=20, line_color="#607780", line_dash="dot")
    fig.add_annotation(
        x=20,
        y=103,
        text="20 years",
        showarrow=False,
        xanchor="left",
        font=dict(size=13),
    )
    return html.Div(
        [
            compare.graph(fig),
            html.Div(
                [
                    html.H2("Evidence and assumptions are separate"),
                    html.Ul(
                        [
                            html.Li(
                                "Mineral dissolution can take years to centuries in coastal sediments."
                            ),
                            html.Li(
                                "Atmospheric uptake follows alkalinity generation and site-dependent air–sea exchange."
                            ),
                            html.Li(
                                "These 10 / 30 / 100-year curves are sensitivities, not a field-calibrated probability range."
                            ),
                            html.Li(
                                "The same total rock is spread over twenty annual batches. Grain-size changes would also require new grinding inputs."
                            ),
                        ]
                    ),
                    html.Table(
                        [
                            html.Thead(
                                html.Tr(
                                    [
                                        html.Th("Illustrative clock"),
                                        html.Th("Uptake by year 20"),
                                    ]
                                )
                            ),
                            html.Tbody(
                                [
                                    html.Tr([html.Td(label), html.Td(value)])
                                    for label, value in values
                                ]
                            ),
                        ]
                    ),
                    text(
                        [
                            html.A(
                                "Geerts et al. (2025)",
                                href="https://doi.org/10.5194/bg-22-355-2025",
                                target="_blank",
                            ),
                            " · ",
                            html.A(
                                "He & Tyka (2023)",
                                href="https://doi.org/10.5194/bg-20-27-2023",
                                target="_blank",
                            ),
                        ],
                        "source",
                    ),
                ],
                className="technical-copy",
            ),
        ],
        className="technical-grid",
    )


def root_attribution():
    rows = []
    for case in CASES:
        static = sum(attribution.static_contributions(case, 2050).values())
        groups, _ = attribution.temporal_contributions(case)
        temporal = sum(sum(v.values()) for v in groups.values())
        rows.append(
            html.Tr(
                [
                    html.Th([case, origin_key(combined=True)])
                    if case == "Cement + CCS"
                    else html.Th(case),
                    html.Td(compare.number(static)),
                    html.Td(compare.number(temporal)),
                ]
            )
        )
    return stack(
        html.Div(
            [
                html.Div(
                    [
                        html.H2("One root, its upstream chain"),
                        text(
                            "Attribute each upstream contribution to the foreground activity that demanded it. Direct foreground exchanges remain assigned to their own root."
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.H2("Keep the sign before grouping"),
                        text(
                            "At each year, group positive and negative root scores separately by activity type. Then add them to recover the net score. Never add stage and flow decompositions together."
                        ),
                    ]
                ),
            ],
            className="attribution-principles",
        ),
        html.Table(
            [
                html.Caption("kg CO₂-eq per native service", className="table-unit"),
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Case / native service"),
                            html.Th("2050 snapshot"),
                            html.Th("Complete dated inventory"),
                        ]
                    )
                ),
                html.Tbody(rows),
            ],
            className="four-method-table",
        ),
        text(
            "kg CO₂-eq per native service. Each column closes to its own source total; different cohorts and lifetime conventions prevent interpreting the column difference as timing alone.",
            "source",
        ),
        text(
            "DACCS/BECCS: reviewed responsible-root attribution. ERW: extracted first-tier static intensities and depth-one temporal roots, with full residual solves. Cement: approved subprocess/stage attribution, CCS minus BAU.",
            "source",
        ),
    )
