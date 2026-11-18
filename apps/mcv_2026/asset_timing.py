"""Annex figures using the temporal profiles from the Premise revision cited by TRAILS."""

import json
from pathlib import Path

from dash import html
import plotly.graph_objects as go


DATA = json.loads((Path(__file__).parent / "data" / "asset_timing_profiles.json").read_text())
PROFILES = DATA["profiles"]
REGISTRY = f"https://github.com/polca/premise/tree/{DATA['commit']}/premise/data/trails/temporal"
BLUE = "#087ca1"
TEAL = "#008a82"
PURPLE = "#7c699d"
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


def construction_profiles(graph):
    cards = []
    for key, title, weighting, color in (
        ("photovoltaic", "Photovoltaïque", "États-Unis · puissance nette estivale", TEAL),
        ("nuclear", "Nucléaire", "États-Unis · puissance nette estivale", BLUE),
        ("low_voltage", "Réseau basse tension", "France · longueur du réseau · SIGEIF", PURPLE),
    ):
        profile = PROFILES[key]
        mean = -sum(year * weight for year, weight in zip(profile["offsets"], profile["weights"], strict=True))
        mean_age = f"{mean:.1f}".replace(".", ",")
        figure = profile_figure(
            [profile_bars(profile, title, color, width=1.8 if key == "low_voltage" else .88)],
            x_range=[-80, 3], x_ticks=[-80, -60, -40, -20, 0],
            y_range=[0, .4], y_ticks=[0, .1, .2, .3, .4],
            x_title="Décalage avant le service (ans)",
        )
        cards.append(html.Figure([
            html.Div([html.H2(title), html.P(weighting)], className="asset-profile-heading"),
            graph(figure),
            html.Figcaption([html.Strong(f"{mean_age} ans"), " d’âge moyen pondéré"]),
        ], className="asset-profile-card"))

    return html.Div([
        html.Div([
            html.Strong("Âges du parc en service"),
            html.Span("→", **{"aria-hidden": "true"}),
            html.Strong("Décalages −âge et poids normalisés"),
            html.Span("→", **{"aria-hidden": "true"}),
            html.Strong("Profil de l’échange service → fournisseur d’actif"),
        ], className="asset-profile-flow"),
        html.Div(cards, className="asset-profile-grid construction"),
        source_line("Poids en % du total dans chaque panneau. Le zéro est l’année du service. Sources · EIA-860 (2025) et SIGEIF (2023), supplément TRAILS, fig. 5 et 8."),
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
