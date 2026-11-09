"""Plotly figures assembled from the precomputed Kent result bundle."""
from __future__ import annotations

import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import results

COLORS = {
    "ink": "#0b3b52",
    "muted": "#5b6a74",
    "keep": "#d99614",
    "replace": "#008a82",
    "good": "#008a82",
    "bad": "#c44e52",
    "grid": "#d9e0e4",
    "manufacturing": "#006b8f",
    "use": "#008a82",
    "maintenance": "#d99614",
    "replacement": "#7656a8",
    "end of life": "#84929a",
    "ICEV": "#d99614",
    "BEV": "#008a82",
    "FCEV": "#4193b8",
    "SYNTHETIC": "#7656a8",
}


def layout(**kwargs):
    base = dict(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color=COLORS["ink"], size=15),
        margin=dict(l=62, r=25, t=45, b=52),
        hoverlabel=dict(bgcolor="white"),
    )
    base.update(kwargs)
    return base


def option_figure(category="climate change"):
    source = results.option_comparison()
    cases = [
        ("Medium gasoline", "default|Medium|ICEV-p"),
        ("Small BEV", "default|Small|BEV"),
        ("Medium BEV", "default|Medium|BEV"),
        ("Large/SUV BEV", "default|Large SUV|BEV"),
        ("FCEV · SMR H₂", "hydrogen-smr|Medium|FCEV"),
    ]
    values = [source[key][category] for _, key in cases]
    scale = 1 if category == "climate change" else 1e6
    unit = "t CO₂-eq / vehicle life" if category == "climate change" else "incidences × 10⁶ / vehicle life"
    if category == "climate change":
        values = [v / 1000 for v in values]
    else:
        values = [v * scale for v in values]
    fig = go.Figure(go.Bar(
        x=[label for label, _ in cases], y=values,
        marker_color=[COLORS["keep"], "#4193b8", COLORS["replace"], "#3e7654", "#7656a8"],
        text=[f"{value:.1f}" if category == "climate change" else f"{value:.2f}" for value in values],
        textposition="outside", cliponaxis=False,
    ))
    fig.update_layout(**layout(yaxis_title=unit, showlegend=False, margin=dict(l=70, r=20, t=34, b=80)))
    fig.update_xaxes(tickangle=-12)
    fig.update_yaxes(gridcolor=COLORS["grid"], rangemode="tozero")
    return fig


def mobility_electricity_figure():
    """Passenger-car GWP as the electricity supplying vehicles and fuels cleans."""
    source = results.mobility_comparison()["electricity_sensitivity"]
    x_values = list(range(20, 601, 20))
    low_x = source["low_intensity"]
    high_x = source["high_intensity"]
    fig = go.Figure()
    for item in source["series"]:
        slope = (item["high_score"] - item["low_score"]) / (high_x - low_x)
        y_values = [item["low_score"] + (value - low_x) * slope for value in x_values]
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines",
            name=item["label"],
            line=dict(color=COLORS[item["powertrain"]], width=5),
            hovertemplate="%{x:.0f} g CO₂-eq/kWh<br>%{y:.0f} g CO₂-eq/pkm<extra>%{fullData.name}</extra>",
        ))
    reference = source["reference_intensity"]
    fig.add_vline(x=reference, line_color=COLORS["ink"], line_dash="dot", line_width=1.5)
    fig.add_annotation(
        x=reference,
        y=.97,
        yref="paper",
        text="2025 US mix",
        showarrow=False,
        xanchor="right",
        xshift=-4,
        font=dict(size=10, color=COLORS["ink"]),
        bgcolor="rgba(255,255,255,.88)",
    )
    fig.update_layout(**layout(
        xaxis_title="Electricity supply GWP · g CO₂-eq/kWh delivered",
        yaxis_title="Life-cycle GWP · g CO₂-eq/pkm",
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=9), itemwidth=30),
        margin=dict(l=65, r=14, t=42, b=50),
        font=dict(family="Arial, sans-serif", color=COLORS["ink"], size=11),
        hovermode="x unified",
    ))
    fig.update_xaxes(range=[20, 600], dtick=100, gridcolor=COLORS["grid"])
    fig.update_yaxes(range=[0, 800], dtick=200, gridcolor=COLORS["grid"])
    return fig


def passenger_modes_figure():
    """Compare passenger modes as stage-resolved stacks per passenger-kilometre."""
    families = {family["key"]: family for family in results.mobility_comparison()["families"]}

    def candidate(family, label):
        return next(item for item in families[family]["candidates"] if item["label"] == label)

    selected = [
        ("Motorcycle<br>petrol", candidate("two-wheelers", "P moto.")),
        ("Motorcycle<br>BEV", candidate("two-wheelers", "E-moto.")),
        ("Car<br>gasoline", candidate("cars", "Gasoline")),
        ("Car<br>BEV", candidate("cars", "BEV")),
        ("Car<br>FCEV (NG)", candidate("cars", "FCEV (NG)")),
        ("Bus<br>diesel", candidate("buses", "Diesel")),
        ("Bus<br>BEV depot", candidate("buses", "Depot")),
        ("Bus<br>FCEV (NG)", candidate("buses", "FCEV (NG)")),
    ]
    labels = [label for label, _ in selected]
    stages = [
        ("vehicle production", "#2b6f85"),
        ("energy supply", "#168b87"),
        ("direct emissions", "#f2ab45"),
        ("maintenance and road", "#b98bd0"),
        ("end of life", "#82949c"),
    ]
    fig = go.Figure()
    for stage, color in stages:
        fig.add_trace(go.Bar(
            x=labels,
            y=[item["contributions"][stage] for _, item in selected],
            name=stage,
            marker=dict(color=color, line=dict(color="white", width=.55)),
            hovertemplate=f"%{{x}}<br>{stage}: %{{y:.1f}} g CO₂-eq/pkm<extra></extra>",
        ))
    totals = [item["total"] for _, item in selected]
    fig.add_trace(go.Scatter(
        x=labels,
        y=[value + 7 for value in totals],
        mode="text",
        text=[f"{value:.0f}" for value in totals],
        textfont=dict(size=10, color=COLORS["ink"]),
        hoverinfo="skip",
        showlegend=False,
    ))
    fig.add_vline(x=1.5, line_color=COLORS["grid"], line_width=1)
    fig.add_vline(x=4.5, line_color=COLORS["grid"], line_width=1)
    fig.update_layout(**layout(
        barmode="stack",
        bargap=.28,
        yaxis_title="Life-cycle GWP · g CO₂-eq/pkm",
        showlegend=False,
        margin=dict(l=64, r=12, t=20, b=64),
        font=dict(family="Arial, sans-serif", color=COLORS["ink"], size=10),
    ))
    fig.update_xaxes(tickfont=dict(size=9), showgrid=False)
    fig.update_yaxes(range=[0, 225], dtick=50, gridcolor=COLORS["grid"])
    return fig


def cumulative_figure(case_result=None, category="climate change", sensitivity=None):
    case_result = None if sensitivity is not None else (case_result or results.ownership_case())
    years = sensitivity["years"] if sensitivity is not None else list(range(2018, 2061))
    scale = 1 / 1000 if category == "climate change" else 1e6
    unit = "t CO₂-eq" if category == "climate change" else "10⁻³ disease incidences"
    fig = go.Figure()
    series = {}
    summary = sensitivity if sensitivity is not None else results.cumulative_summary(case_result, category)
    crossing_year = summary["break_even_year"]
    if crossing_year is not None:
        fig.add_vrect(
            x0=crossing_year,
            x1=2060.5,
            fillcolor="#dff3f0",
            opacity=.45,
            line_width=0,
            layer="below",
        )
    fig.add_vrect(x0=2026, x1=2027, fillcolor="#fff0c9", opacity=.55, line_width=0, layer="below")
    for path, label, color in (("keep", "Keep current car", COLORS["keep"]), ("replace", "Replace after 2026", COLORS["replace"])):
        values = (
            sensitivity[f"{path}_t"]
            if sensitivity is not None
            else [value * scale for value in results.cumulative(case_result[path], category)]
        )
        series[path] = values
        fig.add_trace(go.Scatter(
            x=years, y=values,
            mode="lines", name=label, line=dict(color=color, width=4.5),
            hovertemplate=f"%{{x}}<br>%{{y:.2f}} {unit}<extra>{label}</extra>",
        ))
    fig.add_vline(x=2026.5, line_dash="dot", line_color=COLORS["ink"], line_width=1.5)
    fig.add_annotation(x=2026.5, y=1, yref="paper", text="decision after 2026", showarrow=False, yshift=12, font=dict(size=11))
    if category == "climate change":
        shared = years.index(2019)
        decision = years.index(2026)
        fig.add_annotation(
            x=2019, y=series["keep"][shared], text="shared production<br>2018 components · 2019 assembly",
            showarrow=True, arrowhead=2, arrowcolor=COLORS["manufacturing"], ax=88, ay=-34,
            bgcolor="rgba(255,255,255,.92)", bordercolor=COLORS["grid"], font=dict(size=11),
        )
        fig.add_annotation(
            x=2026, y=series["replace"][decision], text="replacement production<br>before 2027 first use",
            showarrow=True, arrowhead=2, arrowcolor=COLORS["replace"], ax=90, ay=-44,
            bgcolor="rgba(255,255,255,.92)", bordercolor=COLORS["grid"], font=dict(size=11),
        )
        successor_year = 2042
        if sensitivity is not None and len(sensitivity.get("replace_cohorts", [])) > 2:
            successor_year = int(sensitivity["replace_cohorts"][2]["cohort"]) - 1
        successor_index = years.index(successor_year)
        fig.add_annotation(
            x=successor_year, y=series["replace"][successor_index], text="successor-production<br>steps recur",
            showarrow=True, arrowhead=2, arrowcolor=COLORS["manufacturing"], ax=76, ay=-38,
            bgcolor="rgba(255,255,255,.92)", bordercolor=COLORS["grid"], font=dict(size=11),
        )
        if crossing_year is not None:
            crossing = years.index(crossing_year)
            crossing_y = (series["replace"][crossing] + series["keep"][crossing]) / 2
            fig.add_trace(go.Scatter(
                x=[crossing_year], y=[crossing_y], mode="markers", showlegend=False,
                marker=dict(size=11, color="white", line=dict(color=COLORS["ink"], width=2.5)),
                hovertemplate=f"Sustained break-even: {crossing_year}<extra></extra>",
            ))
            fig.add_annotation(
                x=crossing_year, y=crossing_y, text=f"sustained break-even · {crossing_year}",
                showarrow=True, arrowhead=2, arrowcolor=COLORS["ink"], ax=0, ay=52,
                bgcolor=COLORS["ink"], bordercolor=COLORS["ink"], font=dict(size=11, color="white"),
            )
        fig.add_annotation(
            x=2060, y=series["keep"][-1], text=f"KEEP · {series['keep'][-1]:.1f} t",
            showarrow=False, xanchor="right", yshift=16,
            font=dict(size=11, color=COLORS["keep"]), bgcolor="rgba(255,255,255,.9)",
        )
        fig.add_annotation(
            x=2060, y=series["replace"][-1], text=f"REPLACE · {series['replace'][-1]:.1f} t",
            showarrow=False, xanchor="right", yshift=-16,
            font=dict(size=11, color=COLORS["replace"]), bgcolor="rgba(255,255,255,.9)",
        )
    else:
        if crossing_year is not None:
            crossing = years.index(crossing_year)
            crossing_y = (series["replace"][crossing] + series["keep"][crossing]) / 2
            fig.add_trace(go.Scatter(
                x=[crossing_year], y=[crossing_y], mode="markers", showlegend=False,
                marker=dict(size=11, color="white", line=dict(color=COLORS["ink"], width=2.5)),
                hovertemplate=f"Sustained break-even: {crossing_year}<extra></extra>",
            ))
            fig.add_annotation(
                x=crossing_year, y=crossing_y, text=f"sustained break-even · {crossing_year}",
                showarrow=True, arrowhead=2, arrowcolor=COLORS["ink"], ax=0, ay=52,
                bgcolor=COLORS["ink"], bordercolor=COLORS["ink"], font=dict(size=11, color="white"),
            )
        for path, label, color, shift in (
            ("keep", "KEEP", COLORS["keep"], 16),
            ("replace", "REPLACE", COLORS["replace"], -16),
        ):
            fig.add_annotation(
                x=2060, y=series[path][-1], text=f"{label} · {series[path][-1]:.2f}",
                showarrow=False, xanchor="right", yshift=shift,
                font=dict(size=11, color=color), bgcolor="rgba(255,255,255,.9)",
            )
    fig.update_layout(**layout(
        yaxis_title=f"Cumulative {unit}",
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=12)),
        margin=dict(l=75, r=18, t=48, b=58),
    ))
    fig.update_xaxes(range=[2017.7, 2060.5], dtick=5, gridcolor=COLORS["grid"])
    fig.update_yaxes(gridcolor=COLORS["grid"])
    return fig


def decision_landscape_figure(lifetime_km=200_000, horizon=2040):
    source = results.landscape_state(lifetime_km, horizon)
    fig = go.Figure()
    for outcome, label, color in (
        ("keep", "KEEP clearly lower", COLORS["keep"]),
        ("replace", "REPLACE clearly lower", COLORS["replace"]),
    ):
        points = [point for point in source["points"] if point["outcome"] == outcome]
        fig.add_trace(go.Scatter3d(
            x=[point["decision_year"] for point in points],
            y=[point["annual_km"] / 1000 for point in points],
            z=[point["intensity"] for point in points],
            mode="markers",
            name=label,
            marker=dict(size=5.5, color=color, opacity=.84, line=dict(color="white", width=.45)),
            customdata=[
                [
                    point["annual_km"] * results.MILES_PER_KM,
                    lifetime_km,
                    lifetime_km * results.MILES_PER_KM,
                    horizon,
                    point["delta_t"],
                ]
                for point in points
            ],
            hovertemplate=(
                "Replacement after %{x}<br>"
                "Annual driving: %{y:.0f}k km · %{customdata[0]:,.0f} mi<br>"
                "Charging CI: %{z:.0f} g CO₂-eq/kWh<br>"
                "Lifetime: %{customdata[1]:,.0f} km · %{customdata[2]:,.0f} mi<br>"
                "Outcome through %{customdata[3]}<br>"
                "Replace − keep: %{customdata[4]:+.1f} t CO₂-eq"
                f"<extra>{label}</extra>"
            ),
        ))
    fig.update_layout(**layout(
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(
            orientation="h", x=.02, y=1.02,
            bgcolor="rgba(255,255,255,.88)", bordercolor=COLORS["grid"], borderwidth=1,
            font=dict(size=12),
        ),
        scene=dict(
            xaxis=dict(
                title=dict(text="Replacement year", font=dict(size=13)),
                tickfont=dict(size=11), range=[2019.5, 2035.5], dtick=5,
                backgroundcolor="#f5f9fa", gridcolor="#c8d8dd", zeroline=False,
            ),
            yaxis=dict(
                title=dict(text="Annual driving (10³ km/y)", font=dict(size=13)),
                tickfont=dict(size=11), range=[4.3, 20.8],
                tickvals=[5, 8, 12, 20], backgroundcolor="#f8fbfb",
                gridcolor="#c8d8dd", zeroline=False,
            ),
            zaxis=dict(
                title=dict(text="Charging CI (g CO₂-eq/kWh)", font=dict(size=13)),
                tickfont=dict(size=11), range=[25, 680],
                tickvals=[50, 150, 300, 450, 650], backgroundcolor="#f4f8f9",
                gridcolor="#c8d8dd", zeroline=False,
            ),
            camera=dict(
                eye=dict(x=.95, y=.82, z=.62),
                projection=dict(type="orthographic"),
            ),
            aspectmode="manual",
            aspectratio=dict(x=1.7, y=1.2, z=1.0),
        ),
    ))
    return fig


def decision_slices_figure(lifetime_km=200_000, horizon=2040):
    """Four synchronized 2D slices through the decision landscape."""
    source = results.landscape_state(lifetime_km, horizon)
    dimensions = results.slide10_landscape()["dimensions"]
    decisions = dimensions["decision_year"]
    intensities = dimensions["intensity_g_per_kwh"]
    mileages = dimensions["annual_km"]
    point_lookup = {
        (point["annual_km"], point["decision_year"], point["intensity"]): point
        for point in source["points"]
    }
    titles = []
    panel_counts = {}
    for annual in mileages:
        points = [point for point in source["points"] if point["annual_km"] == annual]
        valid_decisions = sum(
            decision <= results.last_use_year(results.CURRENT_START, annual, lifetime_km)
            for decision in decisions
        )
        counts = {
            "keep": sum(point["outcome"] == "keep" for point in points),
            "replace": sum(point["outcome"] == "replace" for point in points),
        }
        counts["ties"] = valid_decisions * len(intensities) - counts["keep"] - counts["replace"]
        panel_counts[annual] = counts
        titles.append(
            f"<b>{annual:,} km/y · {annual * results.MILES_PER_KM:,.0f} mi/y</b>"
            f"<br><span style='font-size:10px;color:{COLORS['muted']}'>"
            f"{counts['keep']} KEEP · {counts['replace']} REPLACE · {counts['ties']} hidden</span>"
        )
    fig = make_subplots(
        rows=2, cols=2, subplot_titles=titles,
        shared_xaxes=True, shared_yaxes=True,
        horizontal_spacing=.075, vertical_spacing=.16,
    )
    colorscale = [
        [0, COLORS["replace"]], [.499, COLORS["replace"]],
        [.5, "#d9e0e4"], [.501, COLORS["keep"]], [1, COLORS["keep"]],
    ]
    for position, annual in enumerate(mileages):
        row, col = position // 2 + 1, position % 2 + 1
        z, custom = [], []
        natural_end = results.last_use_year(results.CURRENT_START, annual, lifetime_km)
        for intensity in intensities:
            z_row, custom_row = [], []
            for decision in decisions:
                point = point_lookup.get((annual, decision, intensity))
                if decision > natural_end:
                    z_row.append(0)
                    custom_row.append(["Invalid configuration", "Current vehicle lifetime already reached"])
                elif point is None:
                    z_row.append(None)
                    custom_row.append(["Near tie hidden", "|replace − keep| < 2 t CO₂-eq"])
                elif point["outcome"] == "tie":
                    z_row.append(None)
                    custom_row.append(["Near tie hidden", f"Replace − keep: {point['delta_t']:+.1f} t CO₂-eq"])
                else:
                    z_row.append(1 if point["outcome"] == "keep" else -1)
                    custom_row.append([
                        "KEEP clearly lower" if point["outcome"] == "keep" else "REPLACE clearly lower",
                        f"Replace − keep: {point['delta_t']:+.1f} t CO₂-eq",
                    ])
            z.append(z_row)
            custom.append(custom_row)
        fig.add_trace(go.Heatmap(
            x=decisions, y=intensities, z=z, customdata=custom,
            zmin=-1, zmax=1, colorscale=colorscale, showscale=False,
            xgap=2, ygap=2,
            hovertemplate=(
                "Replacement after %{x}<br>"
                "Charging CI: %{y:.0f} g CO₂-eq/kWh<br>"
                f"Annual driving: {annual:,} km · {annual * results.MILES_PER_KM:,.0f} mi<br>"
                "%{customdata[0]}<br>%{customdata[1]}<extra></extra>"
            ),
        ), row=row, col=col)
        fig.update_xaxes(
            tickvals=[2020, 2025, 2030, 2035], tickfont=dict(size=10),
            showgrid=False, showticklabels=row == 2,
            title_text="Replacement year" if row == 2 else None,
            title_font=dict(size=12), row=row, col=col,
        )
        fig.update_yaxes(
            tickvals=intensities, tickfont=dict(size=10),
            showgrid=False, showticklabels=col == 1,
            title_text="Charging CI · g CO₂-eq/kWh" if col == 1 else None,
            title_font=dict(size=12), row=row, col=col,
        )
    fig.update_layout(**layout(
        margin=dict(l=80, r=20, t=56, b=50),
        showlegend=False,
    ))
    for annotation in fig.layout.annotations:
        annotation.font = dict(size=13, color=COLORS["ink"])
    return fig


def decision_matrix_figure(decision_year=2026, lifetime_km=200_000, horizon=2040):
    """A legible decision frontier for one replacement year.

    Each valid cell reports the modeled climate difference (REPLACE minus KEEP).
    The fixed color range keeps animated transitions between years comparable.
    """
    source = results.landscape_state(lifetime_km, horizon)
    dimensions = results.slide10_landscape()["dimensions"]
    intensities = dimensions["intensity_g_per_kwh"]
    mileages = dimensions["annual_km"]
    points = {
        (point["annual_km"], point["intensity"]): point
        for point in source["points"]
        if point["decision_year"] == decision_year
    }
    z = []
    custom = []
    annotations = []
    for annual in mileages:
        z_row, custom_row = [], []
        valid = decision_year <= results.last_use_year(results.CURRENT_START, annual, lifetime_km)
        for intensity in intensities:
            point = points.get((annual, intensity)) if valid else None
            if point is None:
                z_row.append(None)
                custom_row.append(["Existing car already reaches its assumed lifetime", "—"])
                label = "retired"
                color = COLORS["muted"]
            else:
                delta = point["delta_t"]
                z_row.append(delta)
                if point["outcome"] == "tie":
                    outcome = "close call"
                elif point["outcome"] == "replace":
                    outcome = "REPLACE"
                else:
                    outcome = "KEEP"
                custom_row.append([outcome, f"{delta:+.1f} t CO₂-eq"])
                label = f"<b>{delta:+.1f}</b><br>{outcome}"
                color = "white" if abs(delta) >= 9 else COLORS["ink"]
            annotations.append(dict(
                x=intensity, y=annual, text=label, showarrow=False,
                font=dict(size=15, color=color), align="center",
            ))
        z.append(z_row)
        custom.append(custom_row)

    fig = go.Figure(go.Heatmap(
        x=intensities,
        y=mileages,
        z=z,
        customdata=custom,
        zmin=-30,
        zmax=30,
        zmid=0,
        colorscale=[
            [0, "#007c76"], [.42, "#a8ddd8"], [.485, "#eff8f7"],
            [.5, "#ffffff"], [.515, "#fff8e8"], [.58, "#f4cf7b"], [1, "#d58f08"],
        ],
        showscale=False,
        xgap=4,
        ygap=4,
        hovertemplate=(
            f"Replacement after {decision_year}<br>"
            "Annual driving: %{y:,} km/y<br>"
            "Charging CI: %{x:.0f} g CO₂-eq/kWh<br>"
            "%{customdata[0]} · %{customdata[1]}<extra></extra>"
        ),
    ))
    fig.update_layout(**layout(
        margin=dict(l=118, r=18, t=42, b=76),
        annotations=annotations,
        plot_bgcolor="#d9e0e4",
        xaxis_title="Charging carbon intensity · g CO₂-eq/kWh",
        yaxis_title="Annual driving",
    ))
    fig.update_xaxes(
        tickmode="array", tickvals=intensities,
        ticktext=["50<br>very clean", "150", "300", "450<br>GECO reference", "650<br>carbon intensive"],
        tickfont=dict(size=13), title_font=dict(size=15), side="bottom",
        showgrid=False, fixedrange=True,
    )
    fig.update_yaxes(
        tickmode="array", tickvals=mileages,
        ticktext=[f"{value:,} km/y<br>{value * results.MILES_PER_KM:,.0f} mi/y" for value in mileages],
        tickfont=dict(size=13), title_font=dict(size=15),
        showgrid=False, fixedrange=True,
    )
    fig.add_annotation(
        x=.5, y=1.09, xref="paper", yref="paper", showarrow=False,
        text=f"<b>REPLACE − KEEP through {horizon}</b> · t CO₂-eq · ±2 t shown as a close call",
        font=dict(size=14, color=COLORS["muted"]),
    )
    return fig


def annual_stage_figure(case_result=None, category="climate change"):
    case_result = case_result or results.ownership_case()
    years = list(range(2018, 2061))
    scale = 1 / 1000 if category == "climate change" else 1e6
    unit = "t CO₂-eq / year" if category == "climate change" else "incidences × 10⁶ / year"
    stages = ("manufacturing", "use", "maintenance", "replacement", "end of life")
    paths = (
        ("keep", "KEEP · current ICEV → 2036 BEV → 2053 BEV", COLORS["keep"]),
        ("replace", "REPLACE · 2027 BEV → 2043 BEV → 2060 BEV", COLORS["replace"]),
    )
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=.15,
        subplot_titles=[label for _, label, _ in paths],
    )
    maximum = 0.0
    for row, (path, label, _) in enumerate(paths, start=1):
        annual = case_result[path]["annual"].get(category, {})
        totals = [
            sum(annual.get(str(year), {}).get(stage, 0.0) for stage in stages) * scale
            for year in years
        ]
        maximum = max(maximum, max(totals, default=0.0))
        for stage in stages:
            values = [annual.get(str(year), {}).get(stage, 0.0) * scale for year in years]
            fig.add_trace(go.Bar(
                x=years,
                y=values,
                name=stage.title(),
                legendgroup=stage,
                showlegend=row == 1,
                marker=dict(color=COLORS[stage], line=dict(color="white", width=.35)),
                hovertemplate=f"{label.split(' · ')[0]} · %{{x}}<br>{stage.title()}: %{{y:.3f}} {unit}<extra></extra>",
            ), row=row, col=1)

    upper = maximum * 1.12
    for row, (_, _, color) in enumerate(paths, start=1):
        fig.add_vline(x=2026.5, line_dash="dot", line_color=COLORS["ink"], line_width=1.5, row=row, col=1)
        fig.add_annotation(
            x=2026.5,
            y=upper * .94,
            text="decision",
            showarrow=False,
            xanchor="left",
            xshift=5,
            font=dict(size=10, color=COLORS["ink"]),
            bgcolor="rgba(255,255,255,.88)",
            row=row,
            col=1,
        )
        fig.add_shape(
            type="line", x0=2018, x1=2060, y0=upper, y1=upper,
            line=dict(color=color, width=3), row=row, col=1,
        )

    fig.update_layout(**layout(
        barmode="relative",
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=12), itemwidth=32),
        margin=dict(l=76, r=18, t=60, b=48),
        bargap=.18,
        hovermode="x unified",
    ))
    for annotation, (_, _, color) in zip(fig.layout.annotations[:2], paths):
        annotation.update(x=.01, xanchor="left", font=dict(size=13, color=color), yshift=5)
    fig.update_xaxes(range=[2017.5, 2060.5], dtick=5, gridcolor=COLORS["grid"], showgrid=True)
    fig.update_yaxes(range=[0, upper * 1.02], dtick=2, gridcolor=COLORS["grid"], title_text=unit, rangemode="tozero")
    fig.update_xaxes(title_text="Calendar year", row=2, col=1)
    return fig


def heatmap_figure(state="baseline", category="climate change"):
    data = results.decision_map(state)
    values = data["values"][category]
    if category == "climate change":
        z = [[None if value is None else value / 1000 for value in row] for row in values]
        unit = "t CO₂-eq through 2060"
    else:
        z = [[None if value is None else value * 1e6 for value in row] for row in values]
        unit = "incidences × 10⁶ through 2060"
    bound = max(abs(value) for row in z for value in row if value is not None)
    fig = go.Figure(go.Heatmap(
        x=data["decision_years"],
        y=[f"{value/1000:g}k km · {value*results.MILES_PER_KM/1000:.1f}k mi" for value in data["annual_km"]],
        z=z,
        zmin=-bound,
        zmax=bound,
        zmid=0,
        colorscale=[[0, "#008a82"], [0.48, "#d7f0ed"], [0.5, "#f8f5ee"], [0.52, "#f3dedf"], [1, "#c44e52"]],
        colorbar=dict(title="Replace − keep<br>" + unit, thickness=18),
        hovertemplate="Decision %{x}<br>%{y}<br>Δ %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(**layout(xaxis_title="Replacement decision year", yaxis_title="Annual driving", margin=dict(l=120, r=150, t=35, b=60)))
    fig.update_xaxes(dtick=2)
    return fig


def indicator_conflict_figure():
    case_result = results.ownership_case()
    climate = results.delta(case_result, "climate change") / 1000
    pm = results.delta(case_result, "particulate matter formation") * 1e6
    values = [climate, pm]
    labels = ["Climate change\n(t CO₂-eq)", "Particulate matter\n(incidences × 10⁶)"]
    colors = [COLORS["good"] if value < 0 else COLORS["bad"] for value in values]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors, text=[f"{v:+.2f}" for v in values], textposition="outside"))
    fig.add_hline(y=0, line_color=COLORS["ink"], line_width=1)
    fig.update_layout(**layout(yaxis_title="Replace − keep (different units)", showlegend=False, margin=dict(l=90, r=30, t=30, b=70)))
    fig.update_yaxes(gridcolor=COLORS["grid"])
    return fig


def scenario_bars():
    labels, values, groups = [], [], []
    for case, label in (("baseline", "NPi + reference"), ("transition", "PkBudg1000 + NDC/LTS"), ("rapid", "PkBudg650 + 1.5°C")):
        item = results.ownership_case(case=case)
        labels.append(label)
        values.append(results.delta(item, "climate change") / 1000)
        groups.append("Paired background + electricity")
    for case, label in (("baseline", "Reference"), ("electricity_ndc", "NDC/LTS"), ("electricity_15c", "1.5°C")):
        item = results.ownership_case(case=case)
        labels.append(label)
        values.append(results.delta(item, "climate change") / 1000)
        groups.append("Electricity only · SSP2-NPi fixed")
    fig = go.Figure(go.Bar(x=[groups, labels], y=values, marker_color=[COLORS["keep"] if v > 0 else COLORS["replace"] for v in values], text=[f"{v:+.1f}" for v in values], textposition="outside"))
    fig.add_hline(y=0, line_color=COLORS["ink"])
    fig.update_layout(**layout(yaxis_title="Replace − keep · t CO₂-eq through 2060", margin=dict(l=90, r=20, t=30, b=105)))
    fig.update_yaxes(gridcolor=COLORS["grid"])
    return fig


def fuel_replacement_figure():
    cases = (
        ("Medium BEV", "BEV", "baseline"),
        ("Efficient gasoline", "ICEV-p", "baseline"),
        ("Corn E85", "ICEV-p", "fuel_e85"),
        ("Synthetic petrol", "ICEV-p", "fuel_synthetic"),
        ("FCEV · SMR H₂", "FCEV", "fuel_hydrogen"),
    )
    values = []
    for _, powertrain, successor_case in cases:
        item = results.ownership_case(
            successor=powertrain,
            successor_case=successor_case,
        )
        values.append(results.delta(item, "climate change") / 1000)
    fig = go.Figure(go.Bar(
        x=[label for label, _, _ in cases], y=values,
        marker_color=[COLORS["keep"] if value > 0 else COLORS["replace"] for value in values],
        text=[f"{value:+.1f}" for value in values], textposition="outside",
    ))
    fig.add_hline(y=0, line_color=COLORS["ink"])
    fig.update_layout(**layout(
        yaxis_title="Replace − keep · t CO₂-eq through 2060",
        margin=dict(l=90, r=20, t=30, b=85),
    ))
    fig.update_yaxes(gridcolor=COLORS["grid"])
    return fig

