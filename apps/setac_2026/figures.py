"""Presentation views of lca_time results and scenario market extracts."""

from __future__ import annotations

import csv
import math
from functools import lru_cache
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import results

CASES = ("BECCS", "DACCS")
COLOURS = {"BECCS": "#3e7654", "DACCS": "#3292b5"}
PATHWAYS = ("SSP2-NPi", "SSP2-PkBudg1000")
SNAPSHOT_YEARS = (2025, 2030, 2050)
MIX_YEARS = (2025, 2030, 2035, 2040, 2045, 2050)
MIX_SECTORS = (
    "Electricity",
    "District heat",
    "Steel",
    "Cement clinker",
    "Truck transport",
)
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
FAIR_START = 1940
WINDOW_MIN = 2000
WINDOW_START = 2020
REFERENCE_YEAR = 2030
DEFAULT_END = 2100
METRIC = "radiative forcing"
BECCS_REFERENCE = "new CHP+CCS vs standing forest and Northern European energy"


def regrowth_end():
    return max(
        int(row["impact_year"])
        for row in results.cohort_temporal_score_rows()
        if row["case"] == "BECCS" and row["contributor"] == "Forest regrowth"
    )


def inventory_start():
    return min(int(row["impact_year"]) for row in results.cohort_temporal_score_rows())


def temporal_years():
    years = [int(row["impact_year"]) for row in results.cohort_temporal_score_rows()]
    return range(min(2000, min(years)) // 10 * 10, math.ceil(max(years) / 10) * 10 + 1)


def static_score(case, pathway="SSP2-NPi", year=2025):
    return results.static_score(
        case, pathway, year, BECCS_REFERENCE if case == "BECCS" else "not applicable"
    )


def static_contributions(case):
    """Use the long deck's process grouping, with shared names for the two bars.

    BECCS has an explicit foreground-step attribution. DACCS uses activity
    contributions only; the alternative biosphere-flow view must not be added.
    """
    if case == "BECCS":
        steps = results.process_step_attribution()[case][
            "process_groups_kg_co2eq_per_net_tonne"
        ]
        mapping = {
            "Forest regrowth": "Forest regrowth",
            "Residual biogenic stack emissions": "Residual stack emissions",
            "Harvesting and biomass supply": "Harvest + biomass supply",
            "Avoided Northern European electricity": "Avoided electricity + heat",
            "Avoided Northern European heat": "Avoided electricity + heat",
            "Transport losses": "CO₂ transport losses",
        }
        grouped = {}
        for step, value in steps.items():
            label = mapping.get(step, "Other supply chain")
            grouped[label] = grouped.get(label, 0.0) + float(value)
        return grouped
    if case != "DACCS":
        raise ValueError(f"Unknown CDR case: {case}")
    upstream_biogenic = (
        "supply of forest residue",
        "plywood production",
        "three and five layered board production",
        "treatment of sewage sludge by anaerobic digestion",
        "hardwood forestry",
    )
    grouped = {}
    for contributor, value in results.static_activity_contributions_per_net_tonne(
        case, "SSP2-NPi", 2025, "not applicable"
    ):
        contributor = contributor.lower()
        if "direct air capture system" in contributor:
            label = "Direct air capture"
        elif "carbon dioxide transport extension" in contributor:
            label = "CO₂ transport losses"
        elif value < 0 and any(name in contributor for name in upstream_biogenic):
            label = "Upstream biogenic uptake"
        elif "| electricity" in contributor or "| heat" in contributor:
            label = "Electricity + heat supply"
        else:
            label = "Other supply chain"
        grouped[label] = grouped.get(label, 0.0) + value
    return grouped


def static_figure():
    contributions = {case: static_contributions(case) for case in CASES}
    fig = go.Figure()
    for label, colour in (
        ("Forest regrowth", "#3e7654"),
        ("Direct air capture", "#3292b5"),
        ("Upstream biogenic uptake", "#9bbd8f"),
        ("Avoided electricity + heat", "#008a82"),
        ("Residual stack emissions", "#d49a61"),
        ("Harvest + biomass supply", "#9b826b"),
        ("Electricity + heat supply", "#e4b543"),
        ("CO₂ transport losses", "#c5685b"),
        ("Other supply chain", "#8497a3"),
    ):
        fig.add_bar(
            x=[0, 1],
            y=[contributions[case].get(label, 0.0) for case in CASES],
            name=label,
            customdata=CASES,
            marker_color=colour,
            width=0.45,
            hovertemplate="%{customdata}: %{y:,.1f} kg CO₂-eq<extra>%{fullData.name}</extra>",
        )
    fig.add_scatter(
        x=[0, 1],
        y=[static_score(case) for case in CASES],
        name="Net GWP100",
        customdata=CASES,
        mode="markers",
        marker=dict(
            symbol="diamond",
            size=13,
            color="white",
            line=dict(color="#17232c", width=2),
        ),
        hovertemplate="%{customdata}: %{y:,.0f} kg CO₂-eq<extra>Net GWP100</extra>",
    )
    for index, case in enumerate(CASES):
        fig.add_annotation(
            x=index + 0.26,
            y=static_score(case),
            text=f"<b>Net {static_score(case):,.0f}</b>".replace("-", "−"),
            showarrow=False,
            xanchor="left",
            bgcolor="rgba(255,255,255,.94)",
            borderpad=4,
            font=dict(size=17, color="#17232c"),
        )
    frame(fig, ytitle="kg CO₂-eq / net t stored", xtitle=None)
    fig.update_layout(
        barmode="relative",
        hovermode="closest",
        margin=dict(l=80, r=260, t=16, b=40),
        legend=dict(
            orientation="v",
            x=1.03,
            y=1,
            traceorder="normal",
            font=dict(size=14),
            itemclick=False,
            itemdoubleclick=False,
        ),
    )
    fig.update_xaxes(
        tickvals=[0, 1], ticktext=CASES, range=[-0.5, 1.8], tickfont_size=19
    )
    fig.update_yaxes(range=[-1580, 740], dtick=500)
    return fig


def pulse_value(case, end=DEFAULT_END, *, start=WINDOW_START, reference=REFERENCE_YEAR):
    # Use the configuration-first ensemble result, never a ratio of medians.
    return results.cohort_co2_pulse_equivalent(
        case, METRIC, int(start), int(end), reference_year=int(reference)
    )


def removal_requirements(case):
    """Net tonnes stored needed for a −1 t score in each assessment.

    All source scores are kg-equivalent per net tonne stored after transport
    loss. This inversion gives physical net storage, not gross captured CO₂ or
    forest uptake. GWP100 uses the current (NPi, 2025) and prospective
    (PkBudg1000, 2030) static snapshots; pulse equivalence uses the temporal
    cohort and the presentation's default window.
    """
    scores = {
        "current_static": static_score(case, "SSP2-NPi", 2025),
        "prospective_static": static_score(case, "SSP2-PkBudg1000", 2030),
        "pulse": pulse_value(case),
    }
    if any(score >= 0 for score in scores.values()):
        raise ValueError("A negative target requires negative per-tonne scores")
    return {metric: -1000.0 / score for metric, score in scores.items()}


def frame(figure, *, ytitle, xtitle="Calendar year", legend=True):
    figure.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=14, color="#17232c"),
        margin=dict(l=65, r=18, t=42 if legend else 18, b=48),
        autosize=True,
        showlegend=legend,
        legend=dict(orientation="h", y=1.14, x=0, font=dict(size=13)),
        hovermode="x unified",
        hoverlabel=dict(font_size=15),
    )
    figure.update_xaxes(title_text=xtitle, showgrid=False, zeroline=False)
    figure.update_yaxes(
        title_text=ytitle,
        gridcolor="#e4eaed",
        zeroline=True,
        zerolinecolor="#8b9ca4",
        zerolinewidth=1,
    )
    return figure


@lru_cache(maxsize=1)
def scenario_context_rows():
    with (Path(__file__).parent / "data/scenario_context.csv").open(
        newline=""
    ) as stream:
        return tuple(csv.DictReader(stream))


def scenario_context_figure(indicator="GMST", region="World", pathway=PATHWAYS[1]):
    if indicator not in ("GMST", "CO2", "Population") or region not in ("World", "ENC"):
        raise ValueError("Unknown scenario indicator or region")
    if indicator == "GMST" and region != "World":
        raise ValueError("GMST is a global indicator")
    scale, unit = {
        ("GMST", "World"): (1, "°C above 1850–1900"),
        ("CO2", "World"): (1e-9, "Gt CO₂ / year"),
        ("CO2", "ENC"): (1e-6, "Mt CO₂ / year"),
        ("Population", "World"): (1e-3, "billion people"),
        ("Population", "ENC"): (1, "million people"),
    }[indicator, region]
    hover_unit = {
        "GMST": "°C",
        "CO2": "Gt/yr" if region == "World" else "Mt/yr",
        "Population": "bn" if region == "World" else "M",
    }[indicator]
    fig = go.Figure()
    for scenario, colour in zip(PATHWAYS, ("#6f818a", "#008a82"), strict=True):
        rows = sorted(
            (
                row
                for row in scenario_context_rows()
                if row["indicator"] == indicator
                and row["region"] == region
                and row["pathway"] == scenario
            ),
            key=lambda row: int(row["year"]),
        )
        fig.add_scatter(
            x=[int(row["year"]) for row in rows],
            y=[float(row["value"]) * scale for row in rows],
            name=scenario.removeprefix("SSP2-"),
            mode="lines+markers",
            line=dict(
                color=colour,
                width=3 if scenario == pathway else 2,
                dash="solid" if scenario == pathway else "dot",
            ),
            marker=dict(size=4),
            opacity=1 if scenario == pathway else 0.65,
            hovertemplate=(
                f"%{{y:,.2f}} {hover_unit}"
                f"<extra>{scenario.removeprefix('SSP2-')}</extra>"
            ),
            connectgaps=False,
        )
    frame(fig, ytitle=None, xtitle=None)
    fig.update_layout(
        title=dict(text=unit, x=0.02, y=0.98, font=dict(size=11)),
        margin=dict(l=35, r=8, t=27, b=58),
        legend=dict(
            x=0,
            y=-0.25,
            orientation="h",
            font=dict(size=10),
            itemclick=False,
            itemdoubleclick=False,
        ),
        meta=dict(indicator=indicator, region=region, pathway=pathway, unit=unit),
    )
    fig.update_xaxes(
        range=[2018, 2102],
        tickvals=[2020, 2050, 2100],
        tickfont_size=11,
        fixedrange=True,
    )
    fig.update_yaxes(tickfont_size=11, nticks=4, fixedrange=True, rangemode="tozero")
    return fig


def scenario_context_note(indicator, region):
    if indicator == "GMST":
        return "GMST is global · MAGICC7 median."
    if indicator == "Population":
        return "Both pathways use the same SSP2 population."
    if region == "ENC":
        return "Net CO₂ emissions. NPi: no 2100 value in the source."
    return "Annual net CO₂ emissions."


@lru_cache(maxsize=1)
def sector_mix_rows():
    """Read ENC market shares extracted from the original scenario packages."""
    with (Path(__file__).parent / "data/sector_mixes.csv").open(newline="") as stream:
        return tuple(csv.DictReader(stream))


def sector_mix(sector, pathway, year):
    shares = {
        row["category"]: float(row["share"])
        for row in sector_mix_rows()
        if row["sector"] == sector
        and row["pathway"] == pathway
        and int(row["year"]) == year
    }
    if not shares:
        raise LookupError(f"No sector mix for {sector}, {pathway}, {year}.")
    return shares


def mix_figure(sector, pathway=PATHWAYS[1]):
    """Display the actual market shares, grouping only consistently tiny routes."""
    snapshots = {
        (path, year): sector_mix(sector, path, year)
        for path in PATHWAYS
        for year in MIX_YEARS
    }
    categories = list(dict.fromkeys(cat for row in snapshots.values() for cat in row))
    major = [
        cat
        for cat in categories
        if cat != "Other"
        and max(row.get(cat, 0.0) for row in snapshots.values()) >= 0.01
    ]
    minor = [cat for cat in categories if cat not in major]
    fig = go.Figure()
    for category in major + (
        ["Other"]
        if any(
            sum(row.get(cat, 0.0) for cat in minor) > 0 for row in snapshots.values()
        )
        else []
    ):
        values = [
            (
                sum(snapshots[pathway, year].get(cat, 0.0) for cat in minor)
                if category == "Other"
                else snapshots[pathway, year].get(category, 0.0)
            )
            for year in MIX_YEARS
        ]
        fig.add_bar(
            x=[str(year) for year in MIX_YEARS],
            y=values,
            name=category,
            marker_color=MIX_COLOURS[category],
            width=0.6,
            text=[f"{v:.0%}" if v >= 0.15 else "" for v in values],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(
                size=13,
                color="white" if category not in ("Solar", "Other") else "#17232c",
            ),
            hovertemplate=f"{sector} · {pathway}<br>%{{x}}: %{{y:.1%}}<extra>{category}</extra>",
        )
    frame(fig, ytitle=None, xtitle=None)
    fig.update_layout(
        barmode="stack",
        hovermode="closest",
        margin=dict(l=40, r=5, t=10, b=110, autoexpand=False),
        legend=dict(
            orientation="h",
            x=0,
            y=-0.06,
            font=dict(size=10),
            entrywidth=0.5,
            entrywidthmode="fraction",
            traceorder="normal",
            itemclick=False,
            itemdoubleclick=False,
        ),
        meta=dict(sector=sector, pathway=pathway),
    )
    fig.update_xaxes(
        type="category",
        tickmode="array",
        tickvals=[str(year) for year in MIX_YEARS],
        tickfont_size=10,
        fixedrange=True,
    )
    fig.update_yaxes(
        range=[0, 1], tickvals=[0, 0.5, 1], tickformat=".0%", fixedrange=True
    )
    return fig


PROSPECTIVE_CATEGORIES = (
    ("Forest regrowth", "#3e7654"),
    ("Direct air capture", "#3292b5"),
    ("Upstream biogenic uptake", "#9bbd8f"),
    ("CHP operating emissions", "#d49a61"),
    ("Biomass supply", "#9b826b"),
    ("Electricity + heat activities", "#e4b543"),
    ("CO₂ transport losses", "#c5685b"),
    ("Other activities", "#8497a3"),
)


def prospective_contributions(case, pathway, year):
    """Group signed activity attributions consistently across static snapshots.

    The explicit foreground-step decomposition is only available for 2025;
    use the closing activity tables for every year here, not cohort results.
    Keep opposite signs separate within each displayed category.
    """
    grouped = {
        (label, sign): 0.0 for label, _ in PROSPECTIVE_CATEGORIES for sign in (-1, 1)
    }
    biogenic = (
        "supply of forest residue",
        "plywood production",
        "three and five layered board production",
        "treatment of sewage sludge by anaerobic digestion",
        "hardwood forestry",
    )
    for contributor, value in results.static_activity_contributions_per_net_tonne(
        case, pathway, year, BECCS_REFERENCE if case == "BECCS" else "not applicable"
    ):
        name = contributor.lower()
        if "forest carbon regrowth differential" in name:
            label = "Forest regrowth"
        elif "direct air capture system" in name:
            label = "Direct air capture"
        elif "operation of new nordic spruce chp" in name:
            label = "CHP operating emissions"
        elif "carbon dioxide transport extension" in name:
            label = "CO₂ transport losses"
        elif value < 0 and any(item in name for item in biogenic):
            label = "Upstream biogenic uptake"
        elif any(
            item in name
            for item in (
                "supply of forest residue",
                "wood chipping",
                "harvesting, forestry",
            )
        ):
            label = "Biomass supply"
        elif "| electricity" in name or "| heat" in name:
            label = "Electricity + heat activities"
        else:
            label = "Other activities"
        grouped[label, 1 if value >= 0 else -1] += value
    return grouped


def prospective_figure():
    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.08, subplot_titles=CASES
    )
    for col, case in enumerate(CASES, 1):
        for p, pathway in enumerate(PATHWAYS):
            xpos = [i + (-0.19 if p == 0 else 0.19) for i in range(3)]
            snapshots = [
                prospective_contributions(case, pathway, year)
                for year in SNAPSHOT_YEARS
            ]
            customdata = [[case, pathway, year] for year in SNAPSHOT_YEARS]
            for label, colour in PROSPECTIVE_CATEGORIES:
                for sign in (-1, 1):
                    values = [row[label, sign] for row in snapshots]
                    # Give every category exactly one legend entry, even when absent in BECCS.
                    shown = any(
                        trace.name == label and trace.showlegend for trace in fig.data
                    )
                    if not any(values):
                        continue
                    fig.add_bar(
                        x=xpos,
                        y=values,
                        width=0.32,
                        name=label,
                        legendgroup=label,
                        legendrank=[item[0] for item in PROSPECTIVE_CATEGORIES].index(
                            label
                        ),
                        showlegend=not shown,
                        customdata=customdata,
                        marker=dict(
                            color=colour,
                            pattern=dict(shape="/" if p == 0 else "", solidity=0.12),
                        ),
                        hovertemplate="%{customdata[0]} · %{customdata[1]} · %{customdata[2]}<br>%{y:,.1f} kg CO₂-eq<extra>%{fullData.name}</extra>",
                        row=1,
                        col=col,
                    )
            totals = [static_score(case, pathway, year) for year in SNAPSHOT_YEARS]
            fig.add_scatter(
                x=xpos,
                y=totals,
                name="Net GWP100",
                legendgroup="net",
                legendrank=10,
                mode="markers",
                marker=dict(
                    symbol="diamond",
                    size=8,
                    color="white",
                    line=dict(color="#17232c", width=1.5),
                ),
                customdata=customdata,
                showlegend=col == 1 and p == 0,
                hovertemplate="%{customdata[0]} · %{customdata[1]} · %{customdata[2]}<br>%{y:,.1f} kg CO₂-eq<extra>Net GWP100</extra>",
                row=1,
                col=col,
            )
            for x, value in zip(xpos, totals, strict=True):
                fig.add_annotation(
                    x=x,
                    y=value,
                    yshift=17,
                    text=f"<b>{value:,.0f}</b>".replace("-", "−"),
                    showarrow=False,
                    bgcolor="rgba(255,255,255,.95)",
                    borderpad=2,
                    font=dict(size=12, color="#17232c"),
                    row=1,
                    col=col,
                )
    frame(fig, ytitle="kg CO₂-eq / net t stored", xtitle="Background year")
    fig.update_layout(
        barmode="relative",
        hovermode="closest",
        margin=dict(l=75, r=230, t=35, b=48),
        legend=dict(
            orientation="v",
            x=1.02,
            y=1,
            traceorder="normal",
            font=dict(size=12),
            itemclick=False,
            itemdoubleclick=False,
        ),
    )
    fig.update_xaxes(
        tickvals=[0, 1, 2], ticktext=list(SNAPSHOT_YEARS), range=[-0.6, 2.6]
    )
    fig.update_yaxes(range=[-1580, 740], dtick=500)
    fig.update_yaxes(title_text=None, row=1, col=2)
    fig.update_annotations(
        font=dict(size=18, color="#0b3b52"), selector=dict(yref="paper")
    )
    return fig


TEMPORAL_CATEGORIES = (
    ("Uptake", "#3e7654"),
    ("Energy", "#e4b543"),
    ("CO₂ & stack emissions", "#c5685b"),
    ("Materials", "#8873ad"),
    ("Other supply chain", "#8497a3"),
)
BECCS_TEMPORAL_GROUPS = {
    "Forest regrowth": "Uptake",
    "Residual biogenic stack emissions": "CO₂ & stack emissions",
    "Transport losses": "CO₂ & stack emissions",
    "Harvesting and biomass supply": "Energy",
    "Avoided Northern European electricity": "Energy",
    "Avoided Northern European heat": "Energy",
    "Compression and recompression": "Energy",
    "Capture chemicals and operating materials": "Materials",
    "New CHP infrastructure and end-of-life": "Materials",
    "CCS infrastructure and end-of-life": "Materials",
    "Pipeline and geological storage": "Other supply chain",
    "Other CHP and CCS supply-chain GHG emissions": "Other supply chain",
}
# DACCS roots carry reference products; the complete construction and waste
# treatment branches stay with Materials. The bundled transport/storage branch
# cannot be split further using this table and remains in Other supply chain.
DACCS_TEMPORAL_PRODUCTS = {
    "carbon dioxide, captured": "Uptake",
    "electricity, medium voltage": "Energy",
    "diesel, burned in diesel-electric generating set, 10MW": "Energy",
    "carbon dioxide transport extension": "CO₂ & stack emissions",
    "amine-based silica": "Materials",
    "reinforcing steel": "Materials",
    "drawing of pipe, steel": "Materials",
    "direct air capture system": "Materials",
    "polyethylene, low density, granulate": "Materials",
    "sand": "Materials",
    "bitumen seal": "Materials",
    "waste reinforcement steel": "Materials",
    "waste polyethylene": "Materials",
    "waste bitumen": "Materials",
    "carbon dioxide, stored": "Other supply chain",
    "transport, freight, lorry, diesel, unspecified": "Other supply chain",
}


def temporal_contributions(case):
    """Group existing root attributions without treating every credit as uptake.

    Uptake contains only the explicit forest-regrowth and direct-capture roots.
    Energy includes avoided electricity/heat and biomass supply. Upstream
    biogenic uptake and credits stay with their source service or material.
    Energy uses signed elementary-flow scores before root totals are netted.
    The other categories retain signed annual root scores.
    """
    years = temporal_years()
    grouped = {
        (label, sign): dict.fromkeys(years, 0.0)
        for label, _ in TEMPORAL_CATEGORIES
        for sign in (-1, 1)
    }
    for contributor, series in results.cohort_temporal_score_series(case, "per_tonne"):
        if case == "BECCS":
            label = BECCS_TEMPORAL_GROUPS[contributor]
        elif case == "DACCS":
            label = DACCS_TEMPORAL_PRODUCTS[contributor.split(" | ")[1]]
        else:
            raise ValueError(f"Unknown CDR case: {case}")
        if label == "Energy":
            continue
        for year, value in series:
            values = grouped[label, 1 if value >= 0 else -1]
            if year not in values:
                raise ValueError(f"Temporal chart would omit year {year}")
            values[year] += value
    for row in results.energy_flow_rows():
        if row["case"] == case:
            grouped["Energy", int(row["sign"])][int(row["impact_year"])] += float(
                row["score_per_net_tonne_kg_co2eq"]
            )
    return grouped


def temporal_figure(view="stacked"):
    stacked = view != "unstacked"
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"secondary_y": True}, {"secondary_y": True}]],
        shared_yaxes=True,
        horizontal_spacing=0.19,
        subplot_titles=CASES,
    )
    years = list(temporal_years())
    cumulative_colour = "#c62828"
    for col, case in enumerate(CASES, 1):
        contributions = temporal_contributions(case)
        for rank, (label, colour) in enumerate(TEMPORAL_CATEGORIES):
            for sign in (1, -1):
                values = contributions[label, sign]
                if not any(values.values()):
                    continue
                name = (
                    f"Energy ({'+' if sign > 0 else '−'})"
                    if label == "Energy"
                    else label
                )
                negative_energy = label == "Energy" and sign < 0
                shown = any(t.name == name and t.showlegend for t in fig.data)
                fig.add_scatter(
                    x=years,
                    y=[values[y] for y in years],
                    name=name,
                    meta=dict(case=case, category=label, sign=sign),
                    mode="lines",
                    stackgroup=(
                        ("emissions" if sign > 0 else "uptake-and-credits")
                        if stacked
                        else None
                    ),
                    fill=None if stacked else "none",
                    fillcolor="#f4dfae" if negative_energy else colour,
                    fillpattern=(
                        dict(shape="/", fgcolor="#b58730", size=7, solidity=0.15)
                        if negative_energy and stacked
                        else None
                    ),
                    line=dict(
                        color=colour,
                        width=1 if stacked else 2,
                        dash="dash" if negative_energy and not stacked else "solid",
                    ),
                    legendgroup=name,
                    legendrank=rank,
                    showlegend=not shown,
                    hovertemplate=f"{case} · %{{x}}<br>%{{y:.2f}} kg CO₂-eq<extra>{name}</extra>",
                    row=1,
                    col=col,
                    secondary_y=False,
                )
        # Accumulate the entire inventory, even where the initial view hides
        # earlier upstream contributions. Do not reset the balance at 2000.
        cumulative = []
        running_total = 0.0
        for year in years:
            running_total += sum(values[year] for values in contributions.values())
            cumulative.append(running_total)
        fig.add_scatter(
            x=years,
            y=cumulative,
            name="Cumulative GWP100 · accounting sum",
            meta=dict(case=case, category="cumulative"),
            mode="lines",
            line=dict(color=cumulative_colour, width=3),
            legendgroup="cumulative",
            legendrank=len(TEMPORAL_CATEGORIES),
            showlegend=col == 1,
            hovertemplate=f"{case} · through %{{x}}<br>%{{y:,.1f}} kg CO₂-eq / net t stored<extra>Cumulative GWP100</extra>",
            row=1,
            col=col,
            secondary_y=True,
        )
        fig.add_annotation(
            x=0.98,
            xref="x domain" if col == 1 else "x2 domain",
            y=cumulative[-1],
            yref="y2" if col == 1 else "y4",
            text=f"GWP100 total: {cumulative[-1]:,.0f}".replace("-", "−"),
            showarrow=False,
            xanchor="right",
            yanchor="top",
            yshift=-9,
            font=dict(size=12, color=cumulative_colour),
        )
        if case == "BECCS":
            fig.add_annotation(
                x=0.99,
                y=0.99,
                xref="x domain",
                yref="y domain",
                text="Standing-forest reference<br>Removal credited during<br>post-harvest regrowth",
                showarrow=False,
                xanchor="right",
                yanchor="top",
                align="left",
                bgcolor="rgba(255,255,255,.94)",
                bordercolor="#cbded0",
                borderpad=5,
                font=dict(size=12, color=COLOURS[case]),
            )
        fig.add_vrect(
            x0=2030,
            x1=2049,
            fillcolor=COLOURS[case],
            opacity=0.07,
            line_width=0,
            row=1,
            col=col,
        )
    frame(fig, ytitle=None, xtitle=None)
    fig.update_layout(
        meta=dict(view="stacked" if stacked else "unstacked"),
        margin=dict(l=76, r=95, t=36, b=65),
        legend=dict(
            y=-0.1,
            x=0.5,
            xanchor="center",
            yanchor="top",
            traceorder="normal",
            font=dict(size=12),
            itemclick=False,
            itemdoubleclick=False,
        ),
    )
    # Use the same scale for each case, with zero aligned between annual and
    # cumulative axes. Only the annual axes draw grid and zero lines.
    fig.update_yaxes(range=[-70, 30], dtick=20, secondary_y=False)
    fig.update_yaxes(
        title_text="Annual GWP100<br>(kg CO₂-eq / net t stored)",
        title_font_size=12,
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.update_yaxes(
        range=[-1400, 600],
        dtick=400,
        title_text="Cumulative GWP100<br>(kg CO₂-eq / net t stored)",
        title_font=dict(size=12, color=cumulative_colour),
        tickfont=dict(size=12, color=cumulative_colour),
        showticklabels=True,
        showgrid=False,
        zeroline=False,
        secondary_y=True,
    )
    fig.update_xaxes(
        range=[2000, years[-1]],
        tickvals=sorted({2000, 2030, 2060, 2090, regrowth_end(), years[-1]}),
    )
    fig.update_annotations(
        font=dict(size=18, color="#0b3b52"), selector=dict(yref="paper")
    )
    return fig


def forcing_figure(end=2300, reference=False):
    shading, curves = [], []
    for case in CASES:
        series = dict(results.cohort_fair_total_series(case, METRIC, "total"))
        years = sorted(series)
        values = [series[y] * 1e12 for y in years]
        shade_years, shade_values = [], []
        for i, (year, value) in enumerate(zip(years, values, strict=True)):
            # Follow the line exactly where it crosses zero between years.
            if i and values[i - 1] * value < 0:
                fraction = -values[i - 1] / (value - values[i - 1])
                shade_years.append(years[i - 1] + fraction * (year - years[i - 1]))
                shade_values.append(0.0)
            shade_years.append(year)
            shade_values.append(min(value, 0.0))
        rgb = [int(COLOURS[case][i : i + 2], 16) for i in (1, 3, 5)]
        shading.append(
            go.Scatter(
                x=shade_years,
                y=shade_values,
                mode="lines",
                line=dict(width=0),
                fill="tozeroy",
                fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.12)",
                legendgroup=case,
                showlegend=False,
                hoverinfo="skip",
            )
        )
        curves.append(
            go.Scatter(
                x=years,
                y=values,
                name=case,
                legendgroup=case,
                mode="lines",
                line=dict(color=COLOURS[case], width=4),
                hovertemplate="%{x}: %{y:.3f} pW m⁻²<extra>%{fullData.name}</extra>",
            )
        )
    fig = go.Figure(data=shading + curves)
    if reference:
        series = results.co2_reference_pulse_series(METRIC, pulse_year=REFERENCE_YEAR)
        fig.add_scatter(
            x=[y for y, _ in series],
            y=[v * 1000 * 1e12 for _, v in series],
            name="+1 t CO₂ in 2030",
            mode="lines",
            line=dict(color="#c28b24", width=3, dash="dash"),
        )
    fig.add_vrect(x0=2030, x1=2049, line_width=0, fillcolor="#7e929e", opacity=0.10)
    frame(fig, ytitle="Δ forcing · pW m⁻² / net t stored")
    fig.update_xaxes(range=[FAIR_START, int(end)])
    fig.update_yaxes(range=[-1.08, 1.9] if reference else [-1.08, 0.25])
    return fig


def pulse_figure(end=DEFAULT_END, *, start=WINDOW_START, reference=REFERENCE_YEAR):
    fig = go.Figure()
    years = list(range(int(reference) + 5, 2301, 5))
    for case in CASES:
        fig.add_scatter(
            x=years,
            y=[pulse_value(case, y, start=start, reference=reference) for y in years],
            name=case,
            mode="lines+markers",
            marker=dict(size=3),
            line=dict(color=COLOURS[case], width=4),
            hovertemplate="Through %{x}: %{y:,.0f} kg CO₂ pulse-eq<extra>%{fullData.name}</extra>",
        )
        fig.add_scatter(
            x=[int(end)],
            y=[pulse_value(case, end, start=start, reference=reference)],
            mode="markers",
            marker=dict(
                color=COLOURS[case], size=12, line=dict(color="white", width=2)
            ),
            showlegend=False,
            hoverinfo="skip",
        )
    fig.add_vline(x=int(end), line_color="#a3adb3", line_dash="dot")
    frame(
        fig,
        ytitle="kg CO₂ pulse-eq / net t stored",
        xtitle="Assessment window end",
    )
    fig.update_xaxes(range=[min(years[0] - 5, 2280), 2305], nticks=6)
    fig.update_yaxes(rangemode="tozero")
    fig.update_layout(
        meta=dict(start=int(start), reference=int(reference), end=int(end))
    )
    return fig
