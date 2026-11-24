"""Annex charts for FLODyM stocks and the Premise biomass profiles."""

import json
from pathlib import Path

from dash import html
import plotly.graph_objects as go


DATA = json.loads((Path(__file__).parent / "data" / "asset_timing_profiles.json").read_text())
PROFILES = DATA["profiles"]
REGISTRY = f"https://github.com/polca/premise/tree/{DATA['commit']}/premise/data/trails/temporal"
AMBER = "#a86a2b"
GREEN = "#3e7654"


def profile_bars(profile, label, color, *, width=.88):
    return go.Bar(
        x=profile["offsets"],
        y=profile["weights"],
        width=width,
        marker_color=color,
        name=label,
        hovertemplate="%{x:.2~f} ans · %{y:.2%}<extra>%{fullData.name}</extra>",
    )


def profile_figure(bars, *, x_range, x_ticks, y_range, y_ticks, x_title, y_title=None):
    figure = go.Figure(bars)
    figure.update_layout(
        template="none",
        font={"family": "Arial, sans-serif", "size": 13, "color": "#395663"},
        margin={"l": 55 if y_title else 36, "r": 12, "t": 9, "b": 51},
        showlegend=False,
        barmode="overlay",
        separators=", ",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={
            "range": x_range, "tickvals": x_ticks, "title": {"text": x_title, "standoff": 8},
            "zeroline": False, "showline": True, "linecolor": "#bedaDF",
            "tickfont": {"size": 12}, "fixedrange": True,
        },
        yaxis={
            "range": y_range, "tickvals": y_ticks, "tickformat": ".1~%",
            "title": {"text": y_title, "standoff": 4} if y_title else None,
            "showgrid": True, "gridcolor": "#dce8eb", "zeroline": False,
            "tickfont": {"size": 12}, "fixedrange": True,
        },
    )
    figure.add_vline(x=0, line_color="#7899a4", line_width=1.2, layer="below")
    return figure


def source_line(description):
    return html.P([
        html.A("Registre Premise 2.6.0", href=REGISTRY),
        f" · {description}",
    ], className="source")


STOCK = json.loads((Path(__file__).parent / "data" / "stock_vintage_examples.json").read_text())
BAND_COLOURS = ("#405872", "#247da2", "#74b4ce", "#1e806e", "#90bd91", "#bb7547")
BAND_ENDS = STOCK["build_band_end_years"]
BUILD_BANDS = [
    f"Avant {BAND_ENDS[0] + 1}",
    *(f"{start + 1}–{end}" for start, end in zip(BAND_ENDS, BAND_ENDS[1:])),
]


def stock_vintages(graph, examples):
    years = STOCK["years"]
    summary_year = STOCK["summary_year"]
    summary_index = years.index(summary_year)
    cards = []
    for key, title, unit in examples:
        case = STOCK["cases"][key]
        figure = go.Figure([
            go.Scatter(
                x=years, y=values, stackgroup="stock", mode="lines",
                line=dict(color=colour, width=.7), fillcolor=colour, name=band,
                hovertemplate=f"%{{x}} · %{{y:.2f}} {unit}<extra>{band}</extra>",
            )
            for band, colour, values in zip(BUILD_BANDS, BAND_COLOURS, case["stock"], strict=True)
        ])
        figure.update_layout(
            template="none", separators=", ", showlegend=False,
            font=dict(family="Arial, sans-serif", size=13, color="#395663"),
            margin=dict(l=55, r=18, t=12, b=45), hovermode="x",
            xaxis=dict(
                range=[years[0], years[-1]], tickvals=[2005, 2025, 2050, 2075, 2100],
                title=dict(text="Année du parc en service", standoff=8), fixedrange=True,
            ),
            yaxis=dict(
                title=dict(text=unit, standoff=5), rangemode="tozero", fixedrange=True,
                gridcolor="#dce8eb", zeroline=False,
            ),
        )
        figure.add_vline(x=summary_year, line_color="#314f5e", line_dash="dot", line_width=1)
        total = sum(values[summary_index] for values in case["stock"])
        total_label = f"{total:.1f}".replace(".", ",")
        age_label = f"{case['mean_age_at_summary_year']:.1f}".replace(".", ",")
        cards.append(html.Figure([
            html.H2(title, className="asset-profile-species"),
            graph(figure),
            html.Figcaption([
                f"Parc en {summary_year}", html.Strong(f"{total_label} {unit}"),
                html.Small(f"Âge moyen pondéré de {age_label} ans"),
            ]),
        ], className="asset-profile-card"))
    return html.Div([
        html.Div([
            html.Strong("Mise en service"),
            *[html.Span(band, style={"--vintage-colour": colour})
              for band, colour in zip(BUILD_BANDS, BAND_COLOURS, strict=True)],
        ], className="stock-vintage-legend"),
        html.Div(cards, className="asset-profile-grid stock-vintages"),
        html.P([
            html.A("iam-preprocessor", href="https://github.com/romainsacchi/iam-preprocessor"),
            f" · FLODyM · {STOCK['model']} {STOCK['scenario']} · stock en fin d’année",
        ], className="source"),
    ], className="asset-profile-layout")


def biomass_profiles(graph):
    cards = []
    for key, title, color in (("oak", "Chêne", AMBER), ("spruce", "Épicéa", GREEN)):
        profile = PROFILES[key]
        peak_index = profile["weights"].index(max(profile["weights"]))
        peak_offset = profile["offsets"][peak_index]
        peak = f"{peak_offset:g}".replace(".", ",")
        rotation = f"{profile['rotation']:g}".replace(".", ",")
        figure = profile_figure(
            [profile_bars(profile, title, color)],
            x_range=[-2, 127], x_ticks=[0, 25, 50, 75, 100, 125],
            y_range=[0, .031], y_ticks=[0, .01, .02, .03],
            x_title="Années après la récolte", y_title="Part du CO₂ absorbé",
        )
        figure.add_vline(x=peak_offset, line_color=color, line_dash="dot", line_width=1, layer="below")
        cards.append(html.Figure([
            html.H2(title, className="asset-profile-species"),
            graph(figure),
            html.Figcaption([
                html.Strong(f"{rotation} ans"),
                " de repousse modélisée",
                html.Small(f"Pic à {peak} ans"),
            ]),
        ], className="asset-profile-card"))

    return html.Div([
        html.Div([
            html.Strong("Premise associe un profil au flux de CO₂ dans l’air (matrice B)"),
            html.Span("→", **{"aria-hidden": "true"}),
            html.Strong("TRAILS répartit l’absorption par année"),
        ], className="asset-profile-flow"),
        html.Div(cards, className="asset-profile-grid biomass"),
        source_line("Profils ALIGNED du chêne et de l’épicéa · poids aux milieux des intervalles avant conversion en années TRAILS, supplément § 4.2."),
    ], className="asset-profile-layout")
