#!/usr/bin/env python3
"""Create an eleven-page student handout for three IMAGE SSP pathways."""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "structured_data (2, 4, 8).csv"
OUTPUT_FILE = ROOT / "reports" / "IMAGE_SSP1-L_SSP2-M_SSP3-H_student_handout.pdf"

BG = "#F7F6F2"
INK = "#19323C"
MUTED = "#60727A"
GRID = "#D9DFDF"
WHITE = "#FFFFFF"
SSP2 = "#0B7A75"
SSP2_LIGHT = "#D6ECE9"
SSP3 = "#D95D39"
SSP3_LIGHT = "#F5DED6"
SSP1 = "#2E86AB"
SSP1_LIGHT = "#DDEEF5"
ACCENT = "#E9B949"
PURPLE = "#6C5B7B"

SCENARIOS = ["SSP1-L", "SSP2-M", "SSP3-H"]
SCENARIO_COLORS = {"SSP1-L": SSP1, "SSP2-M": SSP2, "SSP3-H": SSP3}
SCENARIO_LIGHT = {"SSP1-L": SSP1_LIGHT, "SSP2-M": SSP2_LIGHT, "SSP3-H": SSP3_LIGHT}
REGION_NAMES = {
    "BRA": "Brazil",
    "CAN": "Canada",
    "CEU": "Central Europe",
    "CHN": "China",
    "EAF": "East Africa",
    "INDIA": "India",
    "INDO": "Indonesia",
    "JAP": "Japan",
    "KOR": "Korea",
    "ME": "Middle East",
    "MEX": "Mexico",
    "NAF": "North Africa",
    "OCE": "Oceania",
    "RCAM": "Rest of Central America",
    "RSAF": "Other sub-Saharan Africa",
    "RSAM": "Rest of South America",
    "RSAS": "Rest of South Asia",
    "RUS": "Russia",
    "SAF": "South Africa",
    "SEAS": "Southeast Asia",
    "STAN": "Central Asia / Caucasus",
    "TUR": "Turkey",
    "UKR": "Ukraine / Belarus / Moldova",
    "USA": "United States",
    "WAF": "West Africa",
    "WEU": "Western Europe",
}


def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_FILE)
    image = data[
        (data["model"].str.lower() == "image")
        & data["scenario"].isin(SCENARIOS)
    ].copy()
    image["year"] = image["year"].astype(int)
    required = {"World", *SCENARIOS}
    present = set(image["region"]) | set(image["scenario"])
    missing = required - present
    if missing:
        raise ValueError(f"Missing expected data labels: {sorted(missing)}")
    return image


def world_series(data: pd.DataFrame, sector: str, variable: str) -> pd.DataFrame:
    out = data[
        (data["region"] == "World")
        & (data["sector"] == sector)
        & (data["variables"] == variable)
        & (data["year"] >= 2020)
    ].pivot_table(index="year", columns="scenario", values="val", aggfunc="first")
    return out.reindex(columns=SCENARIOS).sort_index()


def new_page(title: str, subtitle: str, page: int) -> plt.Figure:
    fig = plt.figure(figsize=(8.27, 11.69), facecolor=BG)
    title_size = 21 if len(title) <= 43 else 18.5 if len(title) <= 52 else 17
    fig.text(0.07, 0.953, title, fontsize=title_size, fontweight="bold", color=INK, va="top")
    fig.text(0.07, 0.918, subtitle, fontsize=9.8, color=MUTED, va="top")
    fig.add_artist(plt.Line2D([0.07, 0.93], [0.895, 0.895], color=GRID, lw=1))
    fig.text(
        0.07,
        0.033,
        "IMAGE SSP1-L, SSP2-M & SSP3-H  •  IAM–LCA student briefing",
        fontsize=7.5,
        color=MUTED,
    )
    fig.text(0.93, 0.033, str(page), fontsize=8, color=MUTED, ha="right")
    return fig


def rounded_box(ax, facecolor=WHITE, edgecolor="none", radius=0.04, lw=1):
    ax.set_axis_off()
    patch = FancyBboxPatch(
        (0, 0),
        1,
        1,
        boxstyle=f"round,pad=0.015,rounding_size={radius}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
        transform=ax.transAxes,
        clip_on=False,
    )
    ax.add_patch(patch)
    return patch


def add_wrapped(
    ax,
    x,
    y,
    text,
    width,
    fontsize=9,
    color=INK,
    weight="normal",
    lineheight=1.35,
    **kwargs,
):
    wrapped = "\n".join(textwrap.wrap(text, width=width, break_long_words=False))
    return ax.text(
        x,
        y,
        wrapped,
        fontsize=fontsize,
        color=color,
        fontweight=weight,
        linespacing=lineheight,
        va="top",
        **kwargs,
    )


def style_plot(ax, title: str, ylabel: str = ""):
    ax.set_facecolor(BG)
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold", color=INK, pad=9)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.set_ylabel(ylabel, fontsize=8, color=MUTED)
    ax.set_xticks([2020, 2040, 2060, 2080, 2100])
    ax.set_xlim(2020, 2100)


def plot_scenario_lines(ax, frame: pd.DataFrame, title: str, ylabel: str):
    style_plot(ax, title, ylabel)
    for scenario in SCENARIOS:
        ax.plot(
            frame.index,
            frame[scenario],
            color=SCENARIO_COLORS[scenario],
            lw=2.6,
            marker="o",
            markersize=3.2,
            markevery=[0, len(frame) - 1],
            zorder=3,
        )
    ax.margins(y=0.12)


def scenario_card(fig, position, scenario, label, narrative, data_points):
    ax = fig.add_axes(position)
    face = SCENARIO_LIGHT[scenario]
    color = SCENARIO_COLORS[scenario]
    rounded_box(ax, facecolor=face, radius=0.035)
    ax.text(0.06, 0.90, scenario, fontsize=19, fontweight="bold", color=color, va="top")
    ax.text(0.06, 0.79, label, fontsize=8.5, fontweight="bold", color=INK, va="top")
    wrap_width = 36 if position[2] < 0.32 else 48
    add_wrapped(ax, 0.06, 0.69, narrative, wrap_width, fontsize=8.5, color=INK)
    y = 0.27
    for heading, value in data_points:
        ax.text(0.06, y, heading.upper(), fontsize=6.8, color=MUTED, fontweight="bold")
        ax.text(0.06, y - 0.072, value, fontsize=11.5, color=color, fontweight="bold")
        y -= 0.145
    return ax


def metric_card(fig, x, title, ssp2_value, ssp3_value, note=""):
    ax = fig.add_axes([x, 0.18, 0.19, 0.16])
    rounded_box(ax, facecolor=WHITE, edgecolor=GRID, radius=0.05)
    ax.text(0.07, 0.86, title.upper(), fontsize=6.8, color=MUTED, fontweight="bold", va="top")
    ax.text(0.07, 0.61, ssp2_value, fontsize=15, fontweight="bold", color=SSP2)
    ax.text(0.07, 0.39, ssp3_value, fontsize=15, fontweight="bold", color=SSP3)
    if note:
        add_wrapped(ax, 0.07, 0.20, note, 24, fontsize=6.5, color=MUTED, lineheight=1.1)


def page_one(data: pd.DataFrame) -> plt.Figure:
    fig = new_page(
        "Three IMAGE futures for IAM–LCA coupling",
        "An eleven-page guide to SSP1-L, SSP2-M and SSP3-H • global results and sector pathways",
        1,
    )
    fig.text(
        0.07,
        0.855,
        "Scenarios are coherent ‘what-if’ worlds—not predictions. They connect assumptions about society, technology and policy to future energy, material and emissions pathways.",
        fontsize=11,
        color=INK,
        va="top",
        wrap=True,
    )

    scenario_card(
        fig,
        [0.06, 0.50, 0.27, 0.29],
        "SSP1-L",
        "Sustainability • low warming",
        "Cooperation, resource efficiency and cleaner technologies advance rapidly. Energy and material demand grow more slowly, while mitigation expands across sectors.",
        [("Transition pattern", "Early and coordinated")],
    )
    scenario_card(
        fig,
        [0.365, 0.50, 0.27, 0.29],
        "SSP2-M",
        "Middle road • medium warming",
        "Historical social, economic and technological patterns broadly continue. Development and cleaner technologies advance, but unevenly and without the deep transformation needed for a low-warming future.",
        [("Transition pattern", "Gradual diversification")],
    )
    scenario_card(
        fig,
        [0.67, 0.50, 0.27, 0.29],
        "SSP3-H",
        "Regional Rivalry • high warming",
        "Countries prioritize security and self-sufficiency. International cooperation weakens, development slows and technology diffuses less evenly, making climate action and adaptation more difficult.",
        [("Transition pattern", "Delayed and uneven")],
    )

    pop = world_series(data, "Population", "population").loc[2100] / 1_000
    gdp = world_series(data, "Gross Domestic Product", "gdp").loc[2100]
    gdp_pc = gdp / (world_series(data, "Population", "population").loc[2100])
    co2 = world_series(data, "Carbon Dioxide emissions", "CO2").loc[2100] / 1e9
    gmst = world_series(data, "GMST increase", "GMST").loc[2100]

    table = fig.add_axes([0.07, 0.16, 0.86, 0.25])
    rounded_box(table, facecolor=WHITE, edgecolor=GRID, radius=0.035)
    table.text(0.04, 0.90, "GLOBAL OUTCOMES IN 2100", fontsize=7, color=MUTED, fontweight="bold")
    xcols = {"SSP1-L": 0.43, "SSP2-M": 0.64, "SSP3-H": 0.84}
    for scenario, xpos in xcols.items():
        table.text(xpos, 0.90, scenario, fontsize=9, color=SCENARIO_COLORS[scenario], fontweight="bold", ha="center")
    metrics = [
        ("Population", lambda s: f"{pop[s]:.1f} bn"),
        ("GDP per person (PPP)", lambda s: f"${gdp_pc[s]:.1f}k"),
        ("Annual CO₂", lambda s: f"{co2[s]:.1f} Gt"),
        ("Warming above 1850–1900", lambda s: f"{gmst[s]:.2f}°C"),
    ]
    for y, (label, formatter) in zip([0.70, 0.52, 0.34, 0.16], metrics):
        table.text(0.04, y, label, fontsize=8, color=INK, va="center")
        for scenario, xpos in xcols.items():
            table.text(xpos, y, formatter(scenario), fontsize=9.2, color=SCENARIO_COLORS[scenario], fontweight="bold", ha="center", va="center")

    fig.text(0.07, 0.105, "How to read the names", fontsize=9.2, fontweight="bold", color=INK)
    fig.text(
        0.07,
        0.078,
        "The SSP number describes socioeconomic conditions; L, M and H identify low-, medium- and high-warming pathway families. These are conditional futures, not forecasts. The technology results are IMAGE-specific: another IAM may translate similar assumptions into different demands, technologies and regional patterns.",
        fontsize=7.4,
        color=MUTED,
        wrap=True,
    )
    return fig


def page_two(data: pd.DataFrame) -> plt.Figure:
    fig = new_page(
        "People, prosperity and climate diverge",
        "The pathways are close in the near term, then separate strongly after mid-century",
        2,
    )

    pop = world_series(data, "Population", "population") / 1_000
    gdp = world_series(data, "Gross Domestic Product", "gdp")
    gdp_pc = gdp / world_series(data, "Population", "population")
    co2 = world_series(data, "Carbon Dioxide emissions", "CO2") / 1e9
    gmst = world_series(data, "GMST increase", "GMST")

    ax1 = fig.add_axes([0.09, 0.57, 0.37, 0.25])
    plot_scenario_lines(ax1, pop, "Population", "billion people")
    ax1.set_ylim(7.5, 14)

    ax2 = fig.add_axes([0.55, 0.57, 0.37, 0.25])
    plot_scenario_lines(ax2, gdp_pc, "GDP per person", "thousand USD (PPP)")
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:.0f}k"))

    ax3 = fig.add_axes([0.09, 0.24, 0.37, 0.25])
    plot_scenario_lines(ax3, co2, "Annual CO₂ emissions", "Gt CO₂ per year")
    ax3.set_ylim(-12, 55)
    ax3.axhline(0, color=MUTED, lw=0.8)
    ax3.annotate(
        "SSP1-L peak\n≈2025",
        xy=(2025, co2.loc[2025, "SSP1-L"]),
        xytext=(2037, 52),
        fontsize=6.7,
        color=SSP1,
        arrowprops={"arrowstyle": "-", "color": SSP1, "lw": 0.8},
        ha="center",
    )
    ax3.annotate(
        "near net zero\n≈2070",
        xy=(2070, co2.loc[2070, "SSP1-L"]),
        xytext=(2080, 9),
        fontsize=6.7,
        color=SSP1,
        arrowprops={"arrowstyle": "-", "color": SSP1, "lw": 0.8},
        ha="center",
    )

    ax4 = fig.add_axes([0.55, 0.24, 0.37, 0.25])
    plot_scenario_lines(ax4, gmst, "Global mean surface temperature", "°C above 1850–1900")
    ax4.axhline(2.0, color=ACCENT, lw=1.2, ls="--", zorder=1)
    ax4.text(2022, 2.04, "2°C", fontsize=7, color="#8B6B11")
    ax4.annotate(
        "SSP1-L peaks near 1.9°C\nthen gradually declines",
        xy=(2060, gmst.loc[2060, "SSP1-L"]),
        xytext=(2071, 1.35),
        fontsize=6.6,
        color=SSP1,
        arrowprops={"arrowstyle": "-", "color": SSP1, "lw": 0.8},
        ha="center",
    )

    handles = [plt.Line2D([0], [0], color=SCENARIO_COLORS[s], lw=3, label=s) for s in SCENARIOS]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.50, 0.865), ncol=2, frameon=False, fontsize=9)

    ax = fig.add_axes([0.07, 0.075, 0.86, 0.105])
    rounded_box(ax, facecolor=WHITE, edgecolor=GRID, radius=0.04)
    ax.text(0.025, 0.77, "THE MAIN DIVERGENCE", fontsize=7, color=MUTED, fontweight="bold")
    add_wrapped(
        ax,
        0.025,
        0.55,
        "SSP1-L peaks early, approaches net-zero CO₂ around 2070 and becomes net-negative thereafter. Because climate responds with a delay, warming peaks near 1.9°C before declining to 1.69°C by 2100. SSP2-M and SSP3-H remain strongly positive-emissions pathways and reach 2.85°C and 3.56°C, respectively.",
        101,
        fontsize=8.6,
        color=INK,
    )
    return fig


def electricity_mix(data: pd.DataFrame) -> pd.DataFrame:
    power = data[
        (data["region"] == "World")
        & (data["sector"] == "Electricity")
        & data["year"].isin([2050, 2100])
    ].copy()

    def category(variable: str) -> str | None:
        if variable.startswith("Coal"):
            return "Coal"
        if variable.startswith(("Gas", "Oil")):
            return "Gas / oil"
        if variable == "Nuclear":
            return "Nuclear"
        if variable == "Hydro":
            return "Hydro"
        if variable.startswith(("Solar", "Wind")):
            return "Solar + wind"
        if variable.startswith("Biomass") or variable == "Geothermal":
            return "Bio + geothermal"
        return None  # storage is excluded to avoid counting generated electricity twice

    power["category"] = power["variables"].map(category)
    power = power.dropna(subset=["category"])
    out = power.pivot_table(
        index=["year", "scenario"], columns="category", values="val", aggfunc="sum", fill_value=0
    )
    order = ["Coal", "Gas / oil", "Nuclear", "Hydro", "Bio + geothermal", "Solar + wind"]
    return out.reindex(columns=order, fill_value=0)


def passenger_bev_share(data: pd.DataFrame) -> pd.DataFrame:
    cars = data[
        (data["region"] == "World")
        & (data["sector"] == "Transport Passenger Cars")
        & (data["year"] >= 2020)
    ].copy()
    totals = cars.groupby(["year", "scenario"])["val"].sum()
    bev = cars[cars["variables"] == "battery electric"].groupby(["year", "scenario"])["val"].sum()
    share = (bev / totals * 100).unstack("scenario").fillna(0)
    return share.reindex(columns=SCENARIOS)


def page_three(data: pd.DataFrame) -> plt.Figure:
    fig = new_page(
        "Technology pathways reshape future LCA",
        "Background inventories respond to deployment, fuel choices and fleet composition—not only total emissions",
        3,
    )

    mix = electricity_mix(data)
    ax = fig.add_axes([0.09, 0.56, 0.83, 0.27])
    categories = list(mix.columns)
    colors = {
        "Coal": "#4B5563",
        "Gas / oil": "#B8895A",
        "Nuclear": PURPLE,
        "Hydro": "#4E91C4",
        "Bio + geothermal": "#70A37F",
        "Solar + wind": ACCENT,
    }
    x = np.arange(len(mix))
    bottom = np.zeros(len(mix))
    for category in categories:
        vals = mix[category].to_numpy()
        ax.bar(x, vals, bottom=bottom, color=colors[category], width=0.66, label=category)
        bottom += vals
    ax.set_xticks(x, [f"{year}\n{scenario}" for year, scenario in mix.index])
    ax.set_ylabel("EJ per year", fontsize=8, color=MUTED)
    ax.set_title("Global electricity generation by technology", loc="left", fontsize=11, fontweight="bold", color=INK)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.legend(ncol=3, frameon=False, fontsize=7.3, loc="upper left")
    ax.text(
        0.99,
        1.01,
        "Battery storage excluded to avoid double counting generation",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.5,
        color=MUTED,
    )

    bev = passenger_bev_share(data)
    ax2 = fig.add_axes([0.09, 0.23, 0.37, 0.23])
    plot_scenario_lines(ax2, bev, "Battery-electric passenger cars", "% of vehicle-km")
    ax2.set_ylim(0, 100)

    heat = pd.DataFrame(
        {
            "Electric heating": world_series(data, "Heat", "heat, buildings, from electric heater").loc[2100],
            "Natural gas heating": world_series(data, "Heat", "heat, buildings, from natural gas").loc[2100],
            "Industrial coal CHP": world_series(data, "Heat", "heat, industrial, from coal CHP").loc[2100],
        }
    )
    ax3 = fig.add_axes([0.55, 0.23, 0.37, 0.23])
    xx = np.arange(len(heat.columns))
    width = 0.24
    for offset, scenario in zip([-width, 0, width], SCENARIOS):
        ax3.bar(xx + offset, heat.loc[scenario], width, color=SCENARIO_COLORS[scenario], label=scenario)
    ax3.set_title("Selected heat supply in 2100", loc="left", fontsize=11, fontweight="bold", color=INK)
    ax3.set_ylabel("EJ per year", fontsize=8, color=MUTED)
    ax3.set_xticks(xx, ["Electric\nheating", "Natural gas\nheating", "Industrial\ncoal CHP"])
    ax3.spines[["top", "right", "left"]].set_visible(False)
    ax3.spines["bottom"].set_color(GRID)
    ax3.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax3.tick_params(colors=MUTED, labelsize=8, length=0)
    ax3.legend(frameon=False, fontsize=7.5)

    ax4 = fig.add_axes([0.07, 0.075, 0.86, 0.09])
    rounded_box(ax4, facecolor=WHITE, edgecolor=GRID, radius=0.04)
    add_wrapped(
        ax4,
        0.025,
        0.76,
        "SSP1-L combines rapid renewable deployment with much faster electrification of cars and heat. SSP2-M diversifies more gradually, while SSP3-H retains stronger fossil dependence outside the power sector. Technology composition—not a single global carbon number—determines the background changes inherited by an LCA model.",
        120,
        fontsize=8.5,
    )
    return fig


def paired_dots(ax, frame: pd.DataFrame, regions, title: str, xlabel: str, show_labels=True):
    values = frame.loc[regions]
    y = np.arange(len(regions))
    ax.hlines(y, values["SSP2-M"], values["SSP3-H"], color=GRID, lw=2, zorder=1)
    ax.scatter(values["SSP2-M"], y, s=31, color=SSP2, zorder=3)
    ax.scatter(values["SSP3-H"], y, s=31, color=SSP3, zorder=3)
    ax.set_yticks(y, [REGION_NAMES.get(r, r) if show_labels else "" for r in regions])
    ax.invert_yaxis()
    ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=INK, pad=8)
    ax.set_xlabel(xlabel, fontsize=7.5, color=MUTED)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    ax.tick_params(colors=MUTED, labelsize=7.2, length=0)


def regional_power_metrics(data: pd.DataFrame, year=2100):
    regional = data[(data["region"] != "World") & (data["year"] == year)]
    power = regional[(regional["sector"] == "Electricity") & (regional["variables"] != "Storage, Battery")].copy()
    power["non_fossil"] = ~power["variables"].str.startswith(("Coal", "Gas", "Oil"))
    total = power.groupby(["region", "scenario"])["val"].sum().unstack()
    low = power[power["non_fossil"]].groupby(["region", "scenario"])["val"].sum().unstack()
    population = regional[
        (regional["sector"] == "Population") & (regional["variables"] == "population")
    ].pivot(index="region", columns="scenario", values="val")
    per_person = total * 277.777778 / population  # EJ and million people -> MWh/person
    low_share = low / total * 100
    return per_person, low_share


def page_four(data: pd.DataFrame) -> plt.Figure:
    fig = new_page(
        "The transition is geographically uneven",
        "Regional scale, development and technology mixes interact differently in each pathway",
        4,
    )

    regional = data[(data["region"] != "World") & (data["year"] == 2100)]
    co2 = regional[
        (regional["sector"] == "Carbon Dioxide emissions") & (regional["variables"] == "CO2")
    ].pivot(index="region", columns="scenario", values="val") / 1e9
    regions = co2.max(axis=1).nlargest(8).index.tolist()

    ax = fig.add_axes([0.18, 0.57, 0.74, 0.25])
    y = np.arange(len(regions))
    bar_h = 0.34
    ax.barh(y - bar_h / 2, co2.loc[regions, "SSP2-M"], bar_h, color=SSP2, label="SSP2-M")
    ax.barh(y + bar_h / 2, co2.loc[regions, "SSP3-H"], bar_h, color=SSP3, label="SSP3-H")
    ax.set_yticks(y, [REGION_NAMES.get(r, r) for r in regions])
    ax.invert_yaxis()
    ax.set_title("Largest regional CO₂ emitters in 2100", loc="left", fontsize=11, fontweight="bold", color=INK)
    ax.set_xlabel("Gt CO₂ per year", fontsize=8, color=MUTED)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    ax.tick_params(colors=MUTED, labelsize=7.8, length=0)
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")

    electricity_pc, low_share = regional_power_metrics(data)
    ax2 = fig.add_axes([0.18, 0.25, 0.34, 0.21])
    paired_dots(ax2, electricity_pc, regions, "Electricity generation per person", "MWh per person, 2100")
    ax2.set_xlim(0, max(20, electricity_pc.loc[regions].to_numpy().max() * 1.12))

    ax3 = fig.add_axes([0.61, 0.25, 0.31, 0.21])
    paired_dots(ax3, low_share, regions, "Non-fossil electricity share", "% of generation, same regions", show_labels=False)
    ax3.set_xlim(0, 105)
    ax3.text(0.98, 0.98, "same regional order", transform=ax3.transAxes, fontsize=6.2, color=MUTED, ha="right", va="top")

    handles = [
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=SSP2, markeredgecolor=SSP2, label="SSP2-M"),
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=SSP3, markeredgecolor=SSP3, label="SSP3-H"),
    ]
    fig.legend(handles=handles, loc="center", bbox_to_anchor=(0.54, 0.205), ncol=2, frameon=False, fontsize=7.5)

    note = fig.add_axes([0.07, 0.075, 0.86, 0.09])
    rounded_box(note, facecolor=WHITE, edgecolor=GRID, radius=0.04)
    add_wrapped(
        note,
        0.025,
        0.77,
        "SSP3-H is not higher in every region: India and the rest of South Asia emit less than in SSP2-M because activity and electricity generation per person are also much lower. Meanwhile China, the United States and Western Europe emit substantially more. A high non-fossil electricity share can coexist with high total CO₂ when transport, heat, industry and the scale of activity are included.",
        116,
        fontsize=8.2,
    )
    fig.text(
        0.07,
        0.058,
        "IMAGE uses 26 socioeconomic regions; regional averages mask disparities between and within countries.",
        fontsize=6.8,
        color=MUTED,
    )
    return fig


def industrial_shares(data: pd.DataFrame, sector: str) -> pd.DataFrame:
    values = data[
        (data["region"] == "World")
        & (data["sector"] == sector)
        & data["year"].isin([2050, 2100])
    ].copy()
    if sector == "Steel":
        mapping = {
            "primary - BF/BOF": "BF/BOF",
            "primary - TGR BF/BOF": "TGR BF/BOF",
            "primary - DRI": "DRI",
            "secondary": "Secondary",
            "primary - BF/BOF CCS": "CCS routes",
            "primary - DRI CCS": "CCS routes",
            "primary - TGR BF/BOF CCS": "CCS routes",
            "primary - H-DRI": "H-DRI + electrowinning",
            "primary - Electrowinning": "H-DRI + electrowinning",
        }
        order = ["BF/BOF", "TGR BF/BOF", "DRI", "Secondary", "H-DRI + electrowinning", "CCS routes"]
    else:
        mapping = {
            "cement, dry feed rotary kiln": "Conventional kiln",
            "cement, dry feed rotary kiln, efficient": "Efficient kiln",
            "cement, dry feed rotary kiln, efficient, with MEA CCS": "Efficient + CCS",
            "cement, dry feed rotary kiln, efficient, with on-site CCS": "Efficient + CCS",
            "cement, dry feed rotary kiln, efficient, with oxyfuel CCS": "Efficient + CCS",
        }
        order = ["Conventional kiln", "Efficient kiln", "Efficient + CCS"]
    values["route"] = values["variables"].map(mapping)
    grouped = values.groupby(["year", "scenario", "route"])["val"].sum().unstack(fill_value=0)
    shares = grouped.div(grouped.sum(axis=1), axis=0) * 100
    return shares.reindex(columns=order, fill_value=0)


def plot_share_bars(ax, shares: pd.DataFrame, colors, title: str):
    x = np.arange(len(shares))
    bottom = np.zeros(len(shares))
    for category in shares.columns:
        vals = shares[category].to_numpy()
        ax.bar(x, vals, bottom=bottom, color=colors[category], width=0.70, label=category)
        bottom += vals
    ax.set_xticks(x, [f"{year}\n{scenario}" for year, scenario in shares.index])
    ax.set_ylim(0, 100)
    ax.set_ylabel("share of production (%)", fontsize=7.2, color=MUTED)
    ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=INK)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.tick_params(colors=MUTED, labelsize=7, length=0)
    ax.legend(frameon=False, fontsize=6.4, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.18))


def top_industry_share(data: pd.DataFrame, sector: str, selector) -> tuple[pd.DataFrame, list[str]]:
    values = data[(data["region"] != "World") & (data["year"] == 2100) & (data["sector"] == sector)].copy()
    totals = values.groupby(["region", "scenario"])["val"].sum().unstack(fill_value=0)
    regions = totals.max(axis=1).nlargest(6).index.tolist()
    selected = values[selector(values["variables"])].groupby(["region", "scenario"])["val"].sum().unstack(fill_value=0)
    shares = selected.reindex(totals.index, fill_value=0) / totals * 100
    return shares, regions


def page_five(data: pd.DataFrame) -> plt.Figure:
    fig = new_page(
        "Steel and cement change mostly without CCS",
        "Route shifts are stronger in SSP2-M, while regional deployment remains highly uneven",
        5,
    )

    steel = industrial_shares(data, "Steel")
    cement = industrial_shares(data, "Cement")
    steel_colors = {
        "BF/BOF": "#4B5563",
        "TGR BF/BOF": "#8A8175",
        "DRI": "#4E91C4",
        "Secondary": "#70A37F",
        "CCS routes": PURPLE,
    }
    cement_colors = {
        "Conventional kiln": "#B8895A",
        "Efficient kiln": ACCENT,
        "Efficient + CCS": PURPLE,
    }
    ax1 = fig.add_axes([0.08, 0.58, 0.40, 0.24])
    plot_share_bars(ax1, steel, steel_colors, "Global steel production routes")

    ax2 = fig.add_axes([0.56, 0.58, 0.36, 0.24])
    plot_share_bars(ax2, cement, cement_colors, "Global cement kiln routes")

    steel_region, steel_regions = top_industry_share(data, "Steel", lambda s: s.eq("secondary"))
    cement_region, cement_regions = top_industry_share(data, "Cement", lambda s: s.str.contains("efficient"))
    ax3 = fig.add_axes([0.16, 0.25, 0.33, 0.20])
    paired_dots(ax3, steel_region, steel_regions, "Secondary steel in 2100", "% of regional steel production")
    ax3.set_xlim(0, 60)

    ax4 = fig.add_axes([0.64, 0.25, 0.28, 0.20])
    paired_dots(ax4, cement_region, cement_regions, "Efficient cement kilns in 2100", "% of regional cement production")
    ax4.set_xlim(0, 55)
    ax4.tick_params(axis="y", labelsize=6.5)

    handles = [
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=SSP2, markeredgecolor=SSP2, label="SSP2-M"),
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=SSP3, markeredgecolor=SSP3, label="SSP3-H"),
    ]
    fig.legend(handles=handles, loc="center", bbox_to_anchor=(0.53, 0.192), ncol=2, frameon=False, fontsize=7.5)

    note = fig.add_axes([0.07, 0.068, 0.86, 0.092])
    rounded_box(note, facecolor=WHITE, edgecolor=GRID, radius=0.04)
    add_wrapped(
        note,
        0.025,
        0.76,
        "By 2100, SSP2-M reaches 37% secondary steel, 21% DRI and 28% efficient cement kilns; SSP3-H retains larger shares of conventional blast furnaces and kilns. Explicit CCS remains tiny: about 0.03% of steel and 0.4% of cement in SSP2-M, and effectively zero in SSP3-H. DRI is not automatically low-carbon: its performance depends on the reductant and energy supply. Route choice and recycling—not CCS—drive most modeled change.",
        116,
        fontsize=7.8,
    )
    fig.text(
        0.07,
        0.054,
        "Sources: local IMAGE scenario extract; units.yaml; IMAGE 26-region definitions (SSP Model Documentation). Values rounded.",
        fontsize=6.2,
        color=MUTED,
    )
    return fig


def snapshot_card(fig, x, title, ssp2_value, ssp3_value, unit_note=""):
    ax = fig.add_axes([x, 0.73, 0.19, 0.12])
    rounded_box(ax, facecolor=WHITE, edgecolor=GRID, radius=0.05)
    ax.text(0.07, 0.85, title.upper(), fontsize=6.5, color=MUTED, fontweight="bold", va="top")
    ax.text(0.07, 0.59, ssp2_value, fontsize=13.5, color=SSP2, fontweight="bold", va="top")
    ax.text(0.07, 0.35, ssp3_value, fontsize=13.5, color=SSP3, fontweight="bold", va="top")
    if unit_note:
        ax.text(0.07, 0.10, unit_note, fontsize=6.0, color=MUTED, va="bottom")


def page_six(data: pd.DataFrame) -> plt.Figure:
    fig = new_page(
        "2050: the divergence already matters",
        "A mid-century scorecard aligned with common prospective-LCA time horizons",
        6,
    )

    population = world_series(data, "Population", "population").loc[2050]
    gdp_pc = (
        world_series(data, "Gross Domestic Product", "gdp").loc[2050]
        / population
    )
    co2 = world_series(data, "Carbon Dioxide emissions", "CO2").loc[2050] / 1e9
    gmst = world_series(data, "GMST increase", "GMST").loc[2050]
    snapshot_card(fig, 0.07, "Population", f"{population['SSP2-M']/1000:.2f} bn", f"{population['SSP3-H']/1000:.2f} bn", "global, 2050")
    snapshot_card(fig, 0.285, "GDP per person", f"${gdp_pc['SSP2-M']:.1f}k", f"${gdp_pc['SSP3-H']:.1f}k", "PPP-based")
    snapshot_card(fig, 0.50, "Annual CO₂", f"{co2['SSP2-M']:.1f} Gt", f"{co2['SSP3-H']:.1f} Gt", "CO₂ only")
    snapshot_card(fig, 0.715, "Warming", f"{gmst['SSP2-M']:.2f}°C", f"{gmst['SSP3-H']:.2f}°C", "above 1850–1900")

    current = data[(data["region"] == "World") & (data["year"] == 2050)]
    power = current[
        (current["sector"] == "Electricity") & (current["variables"] != "Storage, Battery")
    ].groupby("scenario")["val"].sum()
    solar_wind = current[
        (current["sector"] == "Electricity") & current["variables"].str.startswith(("Solar", "Wind"))
    ].groupby("scenario")["val"].sum()
    bev = passenger_bev_share(data).loc[2050]
    electric_heat = world_series(data, "Heat", "heat, buildings, from electric heater").loc[2050]
    fossil_liquid = world_series(data, "Fuels", "liquid fossil fuels").loc[2050]
    steel = industrial_shares(data, "Steel").loc[(2050, slice(None)), "Secondary"]
    steel.index = steel.index.droplevel("year")
    cement = industrial_shares(data, "Cement").loc[(2050, slice(None)), ["Efficient kiln", "Efficient + CCS"]].sum(axis=1)
    cement.index = cement.index.droplevel("year")

    rows = [
        ("Total electricity generation", "EJ/yr", power, "SSP2-M is 16% higher"),
        ("Solar and wind generation", "EJ/yr", solar_wind, "34% more in SSP2-M"),
        ("Battery-electric car activity", "% vehicle-km", bev, "Tenfold scenario gap"),
        ("Electric building heat", "EJ/yr", electric_heat, "Almost four times higher"),
        ("Liquid fossil-fuel production", "EJ/yr", fossil_liquid, "18% higher in SSP3-H"),
        ("Secondary steel", "% production", steel, "Routes remain fairly close"),
        ("Efficient cement kilns", "% production", cement, "Only a modest gap by 2050"),
    ]

    table = fig.add_axes([0.07, 0.22, 0.86, 0.44])
    rounded_box(table, facecolor=WHITE, edgecolor=GRID, radius=0.025)
    columns = [0.035, 0.43, 0.56, 0.69, 0.81]
    headers = ["INDICATOR", "UNIT", "SSP2-M", "SSP3-H", "MID-CENTURY SIGNAL"]
    for xpos, header in zip(columns, headers):
        table.text(xpos, 0.94, header, fontsize=6.5, color=MUTED, fontweight="bold", va="center")
    table.add_line(plt.Line2D([0.025, 0.975], [0.885, 0.885], transform=table.transAxes, color=GRID, lw=1))
    row_y = np.linspace(0.81, 0.13, len(rows))
    for i, (label, unit, values, signal) in enumerate(rows):
        if i % 2:
            table.add_patch(
                FancyBboxPatch(
                    (0.02, row_y[i] - 0.047),
                    0.96,
                    0.093,
                    boxstyle="round,pad=0,rounding_size=0.01",
                    facecolor="#F1F3F1",
                    edgecolor="none",
                    transform=table.transAxes,
                )
            )
        if unit.startswith("%"):
            value_fmt = lambda v: f"{v:.1f}%"
        else:
            value_fmt = lambda v: f"{v:.1f}"
        table.text(columns[0], row_y[i], label, fontsize=7.6, color=INK, va="center")
        table.text(columns[1], row_y[i], unit, fontsize=6.8, color=MUTED, va="center")
        table.text(columns[2], row_y[i], value_fmt(values["SSP2-M"]), fontsize=8.2, color=SSP2, fontweight="bold", va="center")
        table.text(columns[3], row_y[i], value_fmt(values["SSP3-H"]), fontsize=8.2, color=SSP3, fontweight="bold", va="center")
        table.text(columns[4], row_y[i], signal, fontsize=6.6, color=INK, va="center")

    note = fig.add_axes([0.07, 0.075, 0.86, 0.09])
    rounded_box(note, facecolor="#FFF4D6", edgecolor=ACCENT, radius=0.04)
    add_wrapped(
        note,
        0.025,
        0.77,
        "For a 2050 LCA, the scenarios already imply very different suppliers and energy carriers. The clearest gaps are in electrification and fossil-liquid demand; steel and cement route shares are still relatively similar and only separate strongly later in the century. Mid-century databases should therefore not be treated as interchangeable versions of the same background.",
        116,
        fontsize=8.2,
    )
    return fig


def transport_final_energy_shares(data: pd.DataFrame, mode: str) -> pd.DataFrame:
    values = data[
        (data["region"] == "World")
        & (data["sector"] == "Final Energy")
        & data["year"].isin([2050, 2100])
        & data["variables"].str.startswith(f"Transport - {mode}")
    ].copy()
    values["carrier"] = values["variables"].str.extract(
        r" - (Biofuel|Elec|H2|Liquid fossil|Nat Gas)$"
    )[0]
    grouped = values.dropna(subset=["carrier"]).groupby(
        ["year", "scenario", "carrier"]
    )["val"].sum().unstack(fill_value=0)
    order = ["Liquid fossil", "Nat Gas", "Biofuel", "H2", "Elec"]
    shares = grouped.div(grouped.sum(axis=1), axis=0) * 100
    return shares.reindex(columns=order, fill_value=0)


def liquid_road_fuels(data: pd.DataFrame) -> pd.DataFrame:
    values = data[
        (data["region"] == "World")
        & data["sector"].isin(["Diesel", "Gasoline"])
        & data["year"].isin([2050, 2100])
        & ~data["variables"].str.startswith("Industry - ")
    ].copy()
    values["fuel"] = np.where(
        values["variables"].isin(["diesel", "gasoline"]),
        "Fossil diesel + gasoline",
        "Bio / synthetic substitutes",
    )
    return values.groupby(["year", "scenario", "fuel"])["val"].sum().unstack(fill_value=0)


def hydrogen_mix(data: pd.DataFrame) -> pd.DataFrame:
    values = data[
        (data["region"] == "World")
        & (data["sector"] == "Hydrogen")
        & data["year"].isin([2050, 2100])
    ].copy()
    mapping = {
        "from natural gas": "Natural gas",
        "from coal": "Coal",
        "from biomass": "Biomass",
        "from electrolysis": "Electrolysis",
        "from electrolysis, from onshore wind": "Electrolysis",
    }
    values["route"] = values["variables"].map(mapping)
    return values.groupby(["year", "scenario", "route"])["val"].sum().unstack(fill_value=0)


def plot_stacked(ax, frame: pd.DataFrame, colors, title: str, ylabel: str, legend_cols=2):
    x = np.arange(len(frame))
    bottom = np.zeros(len(frame))
    for category in frame.columns:
        values = frame[category].to_numpy()
        ax.bar(x, values, bottom=bottom, color=colors[category], width=0.70, label=category)
        bottom += values
    ax.set_xticks(x, [f"{year}\n{scenario}" for year, scenario in frame.index])
    ax.set_title(title, loc="left", fontsize=10.2, fontweight="bold", color=INK)
    ax.set_ylabel(ylabel, fontsize=7.2, color=MUTED)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.tick_params(colors=MUTED, labelsize=7, length=0)
    ax.legend(frameon=False, fontsize=6.1, ncol=legend_cols, loc="upper center", bbox_to_anchor=(0.5, -0.19))


def page_seven(data: pd.DataFrame) -> plt.Figure:
    fig = new_page(
        "Beyond electricity, fossil dependence persists",
        "Transport fuels and hydrogen reveal slower parts of the transition",
        7,
    )
    carrier_colors = {
        "Liquid fossil": "#4B5563",
        "Nat Gas": "#B8895A",
        "Biofuel": "#70A37F",
        "H2": "#4E91C4",
        "Elec": ACCENT,
    }
    passenger = transport_final_energy_shares(data, "Pass")
    freight = transport_final_energy_shares(data, "Freight")
    ax1 = fig.add_axes([0.08, 0.61, 0.40, 0.21])
    plot_stacked(ax1, passenger, carrier_colors, "Passenger-transport final energy", "% of final energy", legend_cols=3)
    ax1.set_ylim(0, 100)
    ax2 = fig.add_axes([0.55, 0.61, 0.37, 0.21])
    plot_stacked(ax2, freight, carrier_colors, "Freight-transport final energy", "% of final energy", legend_cols=3)
    ax2.set_ylim(0, 100)

    liquids = liquid_road_fuels(data)
    liquid_colors = {
        "Fossil diesel + gasoline": "#4B5563",
        "Bio / synthetic substitutes": "#70A37F",
    }
    ax3 = fig.add_axes([0.08, 0.29, 0.40, 0.20])
    plot_stacked(ax3, liquids, liquid_colors, "Selected road-liquid production", "EJ per year", legend_cols=1)

    hydrogen = hydrogen_mix(data).reindex(columns=["Natural gas", "Coal", "Biomass", "Electrolysis"], fill_value=0)
    hydrogen_colors = {
        "Natural gas": "#B8895A",
        "Coal": "#4B5563",
        "Biomass": "#70A37F",
        "Electrolysis": "#4E91C4",
    }
    ax4 = fig.add_axes([0.55, 0.29, 0.37, 0.20])
    plot_stacked(ax4, hydrogen, hydrogen_colors, "Hydrogen production routes", "EJ per year", legend_cols=2)

    note = fig.add_axes([0.07, 0.075, 0.86, 0.10])
    rounded_box(note, facecolor=WHITE, edgecolor=GRID, radius=0.04)
    add_wrapped(
        note,
        0.025,
        0.78,
        "In SSP2-M, electricity reaches 36% of passenger-transport and 50% of freight final energy by 2100, yet liquid fossil fuels still supply 56% and 43%, respectively. SSP3-H remains much more fossil-dependent: 82% for passenger transport and 70% for freight. Hydrogen expands late but is still dominated by natural gas in both pathways; electrolysis grows without becoming the main source. Bio-based and synthetic road liquids remain small.",
        116,
        fontsize=8.1,
    )
    fig.text(
        0.07,
        0.057,
        "Transport charts show final-energy shares, not vehicle activity or life-cycle impacts. ‘Selected road liquids’ excludes chemical-industry methanol rows.",
        fontsize=6.2,
        color=MUTED,
    )
    return fig


def global_2050_page(data: pd.DataFrame) -> plt.Figure:
    fig = new_page(
        "2050: three materially different backgrounds",
        "A global mid-century scorecard aligned with common prospective-LCA time horizons",
        4,
    )
    pop = world_series(data, "Population", "population").loc[2050]
    gdp_pc = world_series(data, "Gross Domestic Product", "gdp").loc[2050] / pop
    co2 = world_series(data, "Carbon Dioxide emissions", "CO2").loc[2050] / 1e9
    gmst = world_series(data, "GMST increase", "GMST").loc[2050]
    cards = [
        ("Population", pop / 1000, "bn"),
        ("GDP per person", gdp_pc, "$k"),
        ("Annual CO₂", co2, "Gt"),
        ("Warming", gmst, "°C"),
    ]
    for x, (title, values, unit) in zip([0.07, 0.285, 0.50, 0.715], cards):
        ax = fig.add_axes([x, 0.72, 0.19, 0.13])
        rounded_box(ax, facecolor=WHITE, edgecolor=GRID, radius=0.05)
        ax.text(0.07, 0.87, title.upper(), fontsize=6.4, color=MUTED, fontweight="bold", va="top")
        for y, scenario in zip([0.64, 0.42, 0.20], SCENARIOS):
            value = values[scenario]
            if unit == "$k": label = f"${value:.1f}k"
            elif unit == "°C": label = f"{value:.2f}°C"
            else: label = f"{value:.1f} {unit}"
            ax.text(0.07, y, scenario, fontsize=6.2, color=SCENARIO_COLORS[scenario], fontweight="bold", va="center")
            ax.text(0.94, y, label, fontsize=10.0, color=SCENARIO_COLORS[scenario], fontweight="bold", ha="right", va="center")

    current = data[(data["region"] == "World") & (data["year"] == 2050)]
    power = current[(current["sector"] == "Electricity") & (current["variables"] != "Storage, Battery")].groupby("scenario")["val"].sum()
    power_nf = current[(current["sector"] == "Electricity") & (current["variables"] != "Storage, Battery") & ~current["variables"].str.startswith(("Coal", "Gas", "Oil"))].groupby("scenario")["val"].sum() / power * 100
    heat = current[current["sector"] == "Heat"]
    heat_total = heat.groupby("scenario")["val"].sum()
    heat_elec = heat[heat["variables"].str.contains("electric heater|heat pump", case=False)].groupby("scenario")["val"].sum() / heat_total * 100
    bev = passenger_bev_share(data).loc[2050]
    cement = industrial_shares(data, "Cement").loc[(2050, slice(None)), ["Efficient kiln", "Efficient + CCS"]].sum(axis=1)
    cement.index = cement.index.droplevel("year")
    steel = industrial_shares(data, "Steel").loc[(2050, slice(None)), "Secondary"]
    steel.index = steel.index.droplevel("year")
    transport = transport_final_energy_shares(data, "Pass").loc[(2050, slice(None)), "Liquid fossil"]
    transport.index = transport.index.droplevel("year")
    rows = [
        ("Electricity generation", "EJ/yr", power),
        ("Non-fossil electricity", "% generation", power_nf),
        ("Electric and heat-pump heat", "% heat supply", heat_elec),
        ("Battery-electric car activity", "% vehicle-km", bev),
        ("Efficient or CCS cement kilns", "% production", cement),
        ("Secondary steel", "% production", steel),
        ("Liquid fossil passenger energy", "% final energy", transport),
    ]
    table = fig.add_axes([0.07, 0.20, 0.86, 0.44])
    rounded_box(table, facecolor=WHITE, edgecolor=GRID, radius=0.025)
    xcols = [0.035, 0.43, 0.57, 0.71, 0.85]
    for x, label in zip(xcols, ["INDICATOR", "UNIT", *SCENARIOS]):
        color = SCENARIO_COLORS.get(label, MUTED)
        table.text(x, 0.94, label, fontsize=6.6, color=color, fontweight="bold", ha="center" if label in SCENARIOS else "left")
    table.add_line(plt.Line2D([0.025, 0.975], [0.88, 0.88], transform=table.transAxes, color=GRID, lw=1))
    for i, (label, unit, values) in enumerate(rows):
        y = 0.80 - i * 0.105
        if i % 2:
            table.add_patch(FancyBboxPatch((0.02, y - 0.043), 0.96, 0.086, boxstyle="round,pad=0,rounding_size=0.01", facecolor="#F1F3F1", edgecolor="none", transform=table.transAxes))
        table.text(xcols[0], y, label, fontsize=7.4, color=INK, va="center")
        table.text(xcols[1], y, unit, fontsize=6.6, color=MUTED, va="center")
        for scenario, xpos in zip(SCENARIOS, xcols[2:]):
            suffix = "%" if unit.startswith("%") else ""
            table.text(xpos, y, f"{values[scenario]:.1f}{suffix}", fontsize=8.2, color=SCENARIO_COLORS[scenario], fontweight="bold", ha="center", va="center")
    fig.text(0.07, 0.13, "By 2050, SSP1-L is already a distinct technological world—not merely a lower-emissions version of SSP2-M. The largest differences are visible in electrification, industrial routes and fossil-fuel dependence.", fontsize=8.5, color=INK, wrap=True)
    return fig


def global_industry_page(data: pd.DataFrame) -> plt.Figure:
    fig = new_page(
        "Industry and carbon removal separate SSP1-L",
        "Global production routes and removal deployment through 2100",
        5,
    )
    steel = industrial_shares(data, "Steel")
    cement = industrial_shares(data, "Cement")
    steel_colors = {"BF/BOF": "#4B5563", "TGR BF/BOF": "#8A8175", "DRI": "#4E91C4", "Secondary": "#70A37F", "H-DRI + electrowinning": ACCENT, "CCS routes": PURPLE}
    cement_colors = {"Conventional kiln": "#B8895A", "Efficient kiln": ACCENT, "Efficient + CCS": PURPLE}
    ax1 = fig.add_axes([0.08, 0.57, 0.40, 0.25])
    plot_share_bars(ax1, steel, steel_colors, "Global steel production routes")
    ax2 = fig.add_axes([0.56, 0.57, 0.36, 0.25])
    plot_share_bars(ax2, cement, cement_colors, "Global cement kiln routes")

    ax3 = fig.add_axes([0.09, 0.24, 0.38, 0.20])
    for sector, ls in [("Cement", "-"), ("Steel", "--")]:
        total = data[(data["region"] == "World") & (data["sector"] == sector) & (data["year"] >= 2020)].groupby(["year", "scenario"])["val"].sum().unstack()
        for scenario in SCENARIOS:
            ax3.plot(total.index, total[scenario], color=SCENARIO_COLORS[scenario], ls=ls, lw=2)
    style_plot(ax3, "Material production", "million tonnes per year")
    ax3.set_xlim(2020, 2100)
    ax3.set_xticks([2020, 2040, 2060, 2080, 2100])
    ax3.legend(handles=[plt.Line2D([0], [0], color=INK, lw=2, label="Cement"), plt.Line2D([0], [0], color=INK, lw=2, ls="--", label="Steel")], frameon=False, fontsize=7)

    ax4 = fig.add_axes([0.56, 0.24, 0.36, 0.20])
    cdr = data[(data["region"] == "World") & (data["sector"] == "Carbon Dioxide Removal")].groupby(["year", "scenario"])["val"].sum().unstack().reindex(columns=SCENARIOS).fillna(0) / 1000
    for scenario in SCENARIOS:
        ax4.plot(cdr.index, cdr[scenario], color=SCENARIO_COLORS[scenario], lw=2.5)
    style_plot(ax4, "Annual carbon-dioxide removal", "Gt CO₂ per year")
    ax4.set_xlim(2020, 2100)
    ax4.set_xticks([2020, 2040, 2060, 2080, 2100])
    ax4.legend(SCENARIOS, frameon=False, fontsize=6.7)
    note = fig.add_axes([0.07, 0.075, 0.86, 0.09])
    rounded_box(note, facecolor=WHITE, edgecolor=GRID, radius=0.04)
    add_wrapped(note, 0.025, 0.76, "SSP1-L combines lower material demand with faster adoption of secondary steel, efficient kilns and CCS-equipped routes. CCS prevents some facility emissions from reaching the atmosphere; carbon-dioxide removal (CDR) removes CO₂ already in the atmosphere. They are not interchangeable, and only CDR can directly produce net-negative emissions.", 116, fontsize=7.8, lineheight=1.22)
    fig.text(0.07, 0.060, "BF/BOF = blast furnace/basic oxygen furnace  •  DRI = direct reduced iron", fontsize=5.7, color=MUTED)
    fig.text(0.07, 0.050, "H-DRI = hydrogen-based DRI  •  TGR = top-gas recycling  •  CCS = carbon capture and storage", fontsize=5.7, color=MUTED)
    return fig


def mix_frame(data, sector, categorizer, order):
    values = data[(data["region"] == "World") & (data["sector"] == sector) & (data["year"] <= 2050)].copy()
    values["category"] = values["variables"].map(categorizer)
    values = values.dropna(subset=["category"])
    grouped = values.groupby(["year", "scenario", "category"])["val"].sum().unstack(fill_value=0)
    grouped = grouped.reindex(columns=order, fill_value=0)
    totals = grouped.sum(axis=1)
    shares = grouped.div(totals.replace(0, np.nan), axis=0).fillna(0) * 100
    return shares, totals


def transport_mix_frame(data):
    values = data[(data["region"] == "World") & (data["sector"] == "Final Energy") & (data["year"] <= 2050) & data["variables"].str.startswith("Transport - ")].copy()
    values["category"] = values["variables"].str.extract(r" - (Biofuel|Elec|H2|Liquid fossil|Nat Gas)$")[0]
    values = values.dropna(subset=["category"])
    order = ["Liquid fossil", "Nat Gas", "Biofuel", "H2", "Elec"]
    grouped = values.groupby(["year", "scenario", "category"])["val"].sum().unstack(fill_value=0).reindex(columns=order, fill_value=0)
    totals = grouped.sum(axis=1)
    shares = grouped.div(totals.replace(0, np.nan), axis=0).fillna(0) * 100
    return shares, totals


def total_labels(totals, unit, scale=1, decimals=0):
    return {
        scenario: f"{totals.loc[(2050, scenario)] / scale:.{decimals}f} {unit}"
        for scenario in SCENARIOS
    }


def add_world_benchmark(frame, world_values):
    world = pd.DataFrame(
        [world_values.reindex(SCENARIOS)],
        index=["World"],
        columns=SCENARIOS,
    )
    return pd.concat([world, frame.reindex(columns=SCENARIOS)])


def indexed_series(numerator, denominator, base_year=2005):
    ratio = numerator / denominator.replace(0, np.nan)
    out = ratio.unstack("scenario").reindex(columns=SCENARIOS)
    for scenario in SCENARIOS:
        base = out.loc[base_year, scenario]
        out[scenario] = out[scenario] / base if pd.notna(base) and base != 0 else np.nan
    return out


def triple_dots(ax, frame, regions, title, xlabel):
    y = np.arange(len(regions))
    vals = frame.reindex(regions)
    ax.hlines(y, vals.min(axis=1), vals.max(axis=1), color=GRID, lw=2)
    for offset, scenario in zip([-0.12, 0, 0.12], SCENARIOS):
        ax.scatter(vals[scenario], y + offset, s=25, color=SCENARIO_COLORS[scenario], label=scenario, zorder=3)
    ax.set_yticks(y, [REGION_NAMES.get(r, r) for r in regions])
    ax.invert_yaxis()
    ax.set_title(title, loc="left", fontsize=10, fontweight="bold", color=INK, pad=30)
    ax.text(
        0,
        1.015,
        "World benchmark + six largest regions by sector total",
        transform=ax.transAxes,
        fontsize=6.2,
        color=MUTED,
        va="bottom",
    )
    ax.set_xlabel(xlabel, fontsize=7, color=MUTED)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.tick_params(colors=MUTED, labelsize=6.7, length=0)
    ax.legend(frameon=False, fontsize=6.3, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.34))


def sector_page(fig_title, subtitle, page_no, mix, mix_colors, mix_total_labels, indicator, indicator_title, indicator_ylabel, regional, regions, regional_title, regional_xlabel, takeaway, caveat=""):
    fig = new_page(fig_title, subtitle, page_no)
    fig.text(0.09, 0.855, "GLOBAL TECHNOLOGY MIX, 2005–2050  •  SAME 0–100% SCALE", fontsize=7, color=MUTED, fontweight="bold")
    fig.text(0.91, 0.855, "shaded = 2005–2020", fontsize=6.2, color=MUTED, ha="right")
    for i, scenario in enumerate(SCENARIOS):
        ax = fig.add_axes([0.09 + i * 0.29, 0.635, 0.25, 0.155])
        frame = mix.xs(scenario, level="scenario").sort_index()
        ax.stackplot(frame.index, *[frame[c] for c in frame.columns], colors=[mix_colors[c] for c in frame.columns], linewidth=0)
        ax.axvspan(2005, 2020, color=WHITE, alpha=0.18, zorder=2)
        ax.axvline(2020, color=MUTED, lw=0.8, ls="--", zorder=3)
        ax.set_xlim(2005, 2050); ax.set_ylim(0, 100)
        ax.set_yticks([0, 50, 100]); ax.tick_params(colors=MUTED, labelsize=6.5, length=0)
        ax.set_xticks([2005, 2020, 2050])
        ax.grid(axis="y", color=GRID, lw=0.7)
        ax.set_title(scenario, fontsize=9.5, fontweight="bold", color=SCENARIO_COLORS[scenario], y=1.10, pad=0)
        ax.text(0.5, 1.015, f"2050 total: {mix_total_labels[scenario]}", transform=ax.transAxes, ha="center", va="bottom", fontsize=6.0, color=MUTED)
        if i == 0:
            ax.set_ylabel("% of sector total", fontsize=6.7, color=MUTED)
        else:
            ax.set_yticklabels([])
        ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=mix_colors[c], label=c) for c in mix.columns]
    fig.legend(handles=handles, loc="center", bbox_to_anchor=(0.51, 0.585), ncol=min(4, len(handles)), frameon=False, fontsize=6.4)

    ax1 = fig.add_axes([0.09, 0.245, 0.40, 0.245])
    for scenario in SCENARIOS:
        ax1.plot(indicator.index, indicator[scenario], color=SCENARIO_COLORS[scenario], lw=2.2, label=scenario)
        ax1.scatter([2050], [indicator.loc[2050, scenario]], color=SCENARIO_COLORS[scenario], s=18, zorder=4)
    ax1.axvspan(2005, 2020, color=WHITE, alpha=0.30, zorder=0)
    ax1.axvline(2020, color=MUTED, lw=0.8, ls="--", zorder=1)
    style_plot(ax1, indicator_title, indicator_ylabel)
    ax1.title.set_fontsize(10)
    ax1.set_xlim(2005, 2050); ax1.set_xticks([2005, 2020, 2035, 2050])
    if "%" in indicator_ylabel:
        ax1.set_ylim(0, 100)
        ax1.set_yticks([0, 25, 50, 75, 100])
    elif "index" in indicator_ylabel.lower() or "2005 = 1" in indicator_ylabel:
        ax1.axhline(1, color=MUTED, lw=0.8, ls="--", zorder=1)
    ax1.legend(frameon=False, fontsize=6.5, ncol=3, loc="upper center")
    ax2 = fig.add_axes([0.59, 0.245, 0.33, 0.245])
    triple_dots(ax2, regional, regions, regional_title, regional_xlabel)
    note = fig.add_axes([0.07, 0.072, 0.86, 0.092], zorder=10)
    rounded_box(note, facecolor=WHITE, edgecolor=GRID, radius=0.04)
    add_wrapped(note, 0.025, 0.76, takeaway, 112, fontsize=7.7, lineheight=1.22)
    if caveat:
        fig.text(0.07, 0.055, caveat, fontsize=6.1, color=MUTED)
    return fig


def top_regions(totals, n=6):
    return totals.max(axis=1).nlargest(n).index.tolist()


def electricity_sector_page(data):
    def cat(v):
        if v == "Storage, Battery": return None
        if "CCS" in v: return "CCS-equipped"
        if v.startswith(("Coal", "Gas", "Oil")): return "Fossil, no CCS"
        if v.startswith("Biomass"): return "Biomass"
        if v == "Nuclear": return "Nuclear"
        if v == "Hydro": return "Hydro"
        if v.startswith(("Solar", "Wind")): return "Solar + wind"
        return "Other renewable"
    order = ["Fossil, no CCS", "CCS-equipped", "Nuclear", "Hydro", "Biomass", "Other renewable", "Solar + wind"]
    colors = {"Fossil, no CCS":"#4B5563","CCS-equipped":PURPLE,"Nuclear":"#75658C","Hydro":"#4E91C4","Biomass":"#70A37F","Other renewable":"#9BC1A5","Solar + wind":ACCENT}
    mix, mix_totals = mix_frame(data, "Electricity", cat, order)
    indicator = 100 - mix["Fossil, no CCS"].unstack("scenario").reindex(columns=SCENARIOS)
    reg = data[(data["region"] != "World") & (data["sector"] == "Electricity") & (data["year"] == 2050) & (data["variables"] != "Storage, Battery")].copy()
    totals = reg.groupby(["region","scenario"])["val"].sum().unstack(fill_value=0)
    numerator = reg[~reg["variables"].str.startswith(("Coal","Gas","Oil"))].groupby(["region","scenario"])["val"].sum().unstack(fill_value=0)
    numerator = numerator.reindex(index=totals.index, columns=SCENARIOS, fill_value=0)
    nf = numerator / totals.reindex(columns=SCENARIOS) * 100
    regional = add_world_benchmark(nf, indicator.loc[2050])
    regions = ["World", *top_regions(totals)]
    return sector_page("Electricity: rapid divergence after 2020", "Technology mix, generation shift and regional variation", 6, mix, colors, total_labels(mix_totals, "EJ/yr", decimals=0), indicator, "Non-fossil generation share", "% of generation", regional, regions, "Regional non-fossil share in 2050", "% of generation", "By 2050, non-fossil electricity reaches about 85% in SSP1-L, compared with roughly 70% in SSP2-M and 68% in SSP3-H. SSP1-L also activates CCS-equipped power technologies that are absent or negligible in the other pathways.", "Technical power-plant efficiency series are not present in this CSV; technology shares are shown instead.")


def heat_sector_page(data):
    def cat(v):
        s=v.lower()
        if "electric heater" in s or "heat pump" in s: return "Electric + heat pump"
        if "district" in s: return "District heat"
        if "natural gas" in s: return "Natural gas"
        if "coal" in s or "oil" in s: return "Coal + oil"
        if "wood" in s or "biomass" in s: return "Biomass"
        return None
    order=["Coal + oil","Natural gas","District heat","Biomass","Electric + heat pump"]
    colors={"Coal + oil":"#4B5563","Natural gas":"#B8895A","District heat":PURPLE,"Biomass":"#70A37F","Electric + heat pump":ACCENT}
    mix,mix_totals=mix_frame(data,"Heat",cat,order)
    indicator=mix["Electric + heat pump"].unstack("scenario").reindex(columns=SCENARIOS)
    reg=data[(data["region"]!="World")&(data["sector"]=="Heat")&(data["year"]==2050)].copy(); reg["cat"]=reg["variables"].map(cat)
    totals=reg.groupby(["region","scenario"]).val.sum().unstack(fill_value=0)
    numerator=reg[reg["cat"].isin(["Coal + oil","Natural gas"])].groupby(["region","scenario"]).val.sum().unstack(fill_value=0)
    numerator=numerator.reindex(index=totals.index,columns=SCENARIOS,fill_value=0)
    fossil=numerator/totals.reindex(columns=SCENARIOS)*100
    world_fossil=mix[["Coal + oil","Natural gas"]].sum(axis=1).unstack("scenario").reindex(columns=SCENARIOS).loc[2050]
    regional=add_world_benchmark(fossil,world_fossil)
    regions=["World",*top_regions(totals)]
    return sector_page("Heat: electrification competes with fossil boilers", "Building and industrial heat supply from 2005 to 2050",7,mix,colors,total_labels(mix_totals,"EJ/yr",decimals=0),indicator,"Electric and heat-pump share","% of heat supply",regional,regions,"Regional fossil share in 2050","% of heat supply","SSP1-L combines lower heat demand with faster adoption of electric heating and heat pumps. By 2050, fossil sources provide about 40% of heat in SSP1-L, 51% in SSP2-M and 72% in SSP3-H; regional differences remain wider than the global averages suggest.","Technical boiler and heat-pump efficiency series are not present in this CSV; technology shares are shown instead.")


def cement_sector_page(data):
    def cat(v):
        if "CCS" in v: return "Efficient + CCS"
        if "efficient" in v: return "Efficient kiln"
        return "Conventional kiln"
    order=["Conventional kiln","Efficient kiln","Efficient + CCS"]
    colors={"Conventional kiln":"#B8895A","Efficient kiln":ACCENT,"Efficient + CCS":PURPLE}
    mix,mix_totals=mix_frame(data,"Cement",cat,order)
    fe=data[(data["region"]=="World")&(data["sector"]=="Final Energy")&data["variables"].str.startswith("Industry - Cement")&(data["year"]<=2050)].groupby(["year","scenario"]).val.sum()
    prod=data[(data["region"]=="World")&(data["sector"]=="Cement")&(data["year"]<=2050)].groupby(["year","scenario"]).val.sum()
    intensity=indexed_series(fe,prod)
    reg=data[(data["region"]!="World")&(data["sector"]=="Cement")&(data["year"]==2050)].copy(); totals=reg.groupby(["region","scenario"]).val.sum().unstack(fill_value=0)
    numerator=reg[reg["variables"].str.contains("efficient")].groupby(["region","scenario"]).val.sum().unstack(fill_value=0)
    numerator=numerator.reindex(index=totals.index,columns=SCENARIOS,fill_value=0)
    advanced=numerator/totals.reindex(columns=SCENARIOS)*100
    world_advanced=mix[["Efficient kiln","Efficient + CCS"]].sum(axis=1).unstack("scenario").reindex(columns=SCENARIOS).loc[2050]
    regional=add_world_benchmark(advanced,world_advanced)
    regions=["World",*top_regions(totals)]
    return sector_page("Cement: efficient kilns and CCS scale up","Production routes, energy intensity and regional adoption",8,mix,colors,total_labels(mix_totals,"Gt/yr",scale=1000,decimals=2),intensity,"Final energy per tonne (indexed)","2005 = 1; lower is better",regional,regions,"Efficient/CCS kiln share in 2050","% of production","SSP1-L produces substantially less cement and shifts about 41% of 2050 production to efficient or CCS-equipped kilns; explicit CCS supplies roughly 15%. SSP2-M and SSP3-H remain dominated by conventional kilns through mid-century.","Derived sector average: lower energy per tonne does not guarantee lower emissions; kiln route, fuel mix and CCS energy needs also matter.")


def steel_sector_page(data):
    def cat(v):
        if "CCS" in v: return "CCS routes"
        if "H-DRI" in v or "Electrowinning" in v: return "H-DRI + electrowinning"
        if v=="secondary": return "Secondary"
        if "DRI" in v: return "DRI"
        if "TGR" in v: return "TGR BF/BOF"
        return "BF/BOF"
    order=["BF/BOF","TGR BF/BOF","DRI","Secondary","H-DRI + electrowinning","CCS routes"]
    colors={"BF/BOF":"#4B5563","TGR BF/BOF":"#8A8175","DRI":"#4E91C4","Secondary":"#70A37F","H-DRI + electrowinning":ACCENT,"CCS routes":PURPLE}
    mix,mix_totals=mix_frame(data,"Steel",cat,order)
    fe=data[(data["region"]=="World")&(data["sector"]=="Final Energy")&data["variables"].str.startswith("Industry - Steel")&(data["year"]<=2050)].groupby(["year","scenario"]).val.sum()
    prod=data[(data["region"]=="World")&(data["sector"]=="Steel")&(data["year"]<=2050)].groupby(["year","scenario"]).val.sum()
    intensity=indexed_series(fe,prod)
    reg=data[(data["region"]!="World")&(data["sector"]=="Steel")&(data["year"]==2050)].copy(); reg["cat"]=reg["variables"].map(cat); totals=reg.groupby(["region","scenario"]).val.sum().unstack(fill_value=0)
    numerator=reg[reg["cat"].isin(["Secondary","H-DRI + electrowinning","CCS routes"])].groupby(["region","scenario"]).val.sum().unstack(fill_value=0)
    numerator=numerator.reindex(index=totals.index,columns=SCENARIOS,fill_value=0)
    transition=numerator/totals.reindex(columns=SCENARIOS)*100
    world_transition=mix[["Secondary","H-DRI + electrowinning","CCS routes"]].sum(axis=1).unstack("scenario").reindex(columns=SCENARIOS).loc[2050]
    regional=add_world_benchmark(transition,world_transition)
    regions=["World",*top_regions(totals)]
    return sector_page("Steel: recycling leads, advanced routes emerge","Production routes, energy intensity and regional adoption",9,mix,colors,total_labels(mix_totals,"Gt/yr",scale=1000,decimals=2),intensity,"Final energy per tonne (indexed)","2005 = 1; lower is better",regional,regions,"Low-carbon route share in 2050","% of production","SSP1-L reaches about 37% secondary steel by 2050 and begins deploying H-DRI, electrowinning and CCS routes. SSP2-M and SSP3-H retain larger blast-furnace shares. DRI alone is kept separate because its climate performance depends on the reductant and electricity source.","Derived sector average: lower energy per tonne does not guarantee lower emissions; route, reductant, electricity and CCS energy needs also matter.")


def transport_sector_page(data):
    mix,mix_totals=transport_mix_frame(data)
    colors={"Liquid fossil":"#4B5563","Nat Gas":"#B8895A","Biofuel":"#70A37F","H2":"#4E91C4","Elec":ACCENT}
    world=data[(data["region"]=="World")&(data["sector"]=="Transport Passenger Cars")&(data["year"]<=2050)].copy()
    activity=world.groupby(["year","scenario"]).val.sum()
    bev_world=world[world["variables"]=="battery electric"].groupby(["year","scenario"]).val.sum()
    indicator=(bev_world/activity*100).unstack("scenario").reindex(columns=SCENARIOS)
    reg=data[(data["region"]!="World")&(data["sector"]=="Transport Passenger Cars")&(data["year"]==2050)].copy(); totals=reg.groupby(["region","scenario"]).val.sum().unstack(fill_value=0)
    numerator=reg[reg["variables"]=="battery electric"].groupby(["region","scenario"]).val.sum().unstack(fill_value=0)
    numerator=numerator.reindex(index=totals.index,columns=SCENARIOS,fill_value=0)
    bev=numerator/totals.reindex(columns=SCENARIOS)*100
    regional=add_world_benchmark(bev,indicator.loc[2050])
    regions=["World",*top_regions(totals)]
    return sector_page("Transport: electrification moves at three speeds","Energy mix, battery-electric activity and regional uptake",10,mix,colors,total_labels(mix_totals,"EJ/yr",decimals=0),indicator,"Global battery-electric car activity","% of vehicle-km",regional,regions,"Battery-electric activity in 2050","% of vehicle-km","By 2050, electricity supplies 38% of total passenger and freight final energy in SSP1-L, while battery-electric cars provide 52% of passenger-car activity. The measures differ because final energy includes freight and electric cars use less energy per kilometre. SSP2-M and SSP3-H electrify much more slowly.","Vehicle efficiency series are not present in this CSV; activity share is not a fleet-stock, sales or test-cycle-efficiency measure.")


def transport_modes_page(data):
    modes = ["Passenger cars", "Trucks", "Other transport"]
    carriers = ["Liquid fossil", "Nat Gas", "Biofuel", "H2", "Elec"]
    carrier_colors = {
        "Liquid fossil": "#4B5563",
        "Nat Gas": "#B8895A",
        "Biofuel": "#70A37F",
        "H2": "#4E91C4",
        "Elec": ACCENT,
    }
    values = data[
        (data["region"] == "World")
        & (data["sector"] == "Final Energy")
        & (data["year"] <= 2050)
        & data["variables"].str.startswith("Transport - ")
    ].copy()

    def mode(variable):
        if "Pass - Midsize Car" in variable:
            return "Passenger cars"
        if "Freight - Truck" in variable:
            return "Trucks"
        return "Other transport"

    values["mode"] = values["variables"].map(mode)
    values["carrier"] = values["variables"].str.extract(
        r" - (Biofuel|Elec|H2|Liquid fossil|Nat Gas)$"
    )[0]
    values = values.dropna(subset=["carrier"])
    grouped = (
        values.groupby(["year", "scenario", "mode", "carrier"])["val"]
        .sum()
        .unstack(fill_value=0)
        .reindex(columns=carriers, fill_value=0)
    )
    totals = grouped.sum(axis=1)
    shares = grouped.div(totals.replace(0, np.nan), axis=0).fillna(0) * 100
    current = shares.xs(2050, level="year")
    current_totals = totals.xs(2050, level="year").unstack("scenario").reindex(index=modes, columns=SCENARIOS)
    electric_h2 = (
        current[["Elec", "H2"]]
        .sum(axis=1)
        .unstack("scenario")
        .reindex(index=modes, columns=SCENARIOS)
    )

    fig = new_page(
        "Cars, trucks and other transport follow different routes",
        "Final-energy composition and demand in 2050 across the three IMAGE pathways",
        11,
    )
    fig.text(0.09, 0.855, "2050 FINAL-ENERGY MIX  •  SAME 0–100% SCALE", fontsize=7, color=MUTED, fontweight="bold")
    for i, mode_name in enumerate(modes):
        ax = fig.add_axes([0.09 + i * 0.29, 0.61, 0.25, 0.19])
        frame = current.xs(mode_name, level="mode").reindex(SCENARIOS)
        y = np.arange(len(SCENARIOS))
        left = np.zeros(len(SCENARIOS))
        for carrier in carriers:
            values_ = frame[carrier].to_numpy()
            ax.barh(y, values_, left=left, color=carrier_colors[carrier], height=0.62)
            left += values_
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 50, 100])
        ax.set_yticks(y, SCENARIOS if i == 0 else [])
        if i == 0:
            for tick, scenario in zip(ax.get_yticklabels(), SCENARIOS):
                tick.set_color(SCENARIO_COLORS[scenario])
                tick.set_fontweight("bold")
        ax.invert_yaxis()
        ax.grid(axis="x", color=GRID, lw=0.8)
        ax.tick_params(colors=MUTED, labelsize=6.7, length=0)
        ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
        ax.set_title(mode_name, fontsize=9.5, fontweight="bold", color=INK, pad=8)
        ax.set_xlabel("% of mode final energy", fontsize=6.3, color=MUTED)
    handles = [plt.Rectangle((0, 0), 1, 1, color=carrier_colors[c], label=c) for c in carriers]
    fig.legend(handles=handles, loc="center", bbox_to_anchor=(0.51, 0.57), ncol=5, frameon=False, fontsize=6.5)

    ax1 = fig.add_axes([0.09, 0.245, 0.42, 0.235])
    x = np.arange(len(modes))
    width = 0.23
    for offset, scenario in zip([-width, 0, width], SCENARIOS):
        values_ = current_totals[scenario].to_numpy()
        bars = ax1.bar(x + offset, values_, width, color=SCENARIO_COLORS[scenario], label=scenario)
        for bar, value in zip(bars, values_):
            ax1.text(bar.get_x() + bar.get_width() / 2, value + 1.5, f"{value:.0f}", ha="center", va="bottom", fontsize=6, color=SCENARIO_COLORS[scenario])
    ax1.set_title("Absolute final-energy demand in 2050", loc="left", fontsize=10, fontweight="bold", color=INK)
    ax1.set_ylabel("EJ per year", fontsize=7, color=MUTED)
    ax1.set_xticks(x, ["Passenger\ncars", "Trucks", "Other\ntransport"])
    ax1.set_ylim(0, current_totals.max().max() * 1.18)
    ax1.grid(axis="y", color=GRID, lw=0.8)
    ax1.tick_params(colors=MUTED, labelsize=7, length=0)
    ax1.spines[["top", "right", "left"]].set_visible(False)
    ax1.spines["bottom"].set_color(GRID)
    ax1.legend(frameon=False, fontsize=6.5, ncol=3, loc="upper left")

    ax2 = fig.add_axes([0.60, 0.245, 0.32, 0.235])
    y = np.arange(len(modes))
    ax2.hlines(y, electric_h2.min(axis=1), electric_h2.max(axis=1), color=GRID, lw=2)
    for offset, scenario in zip([-0.12, 0, 0.12], SCENARIOS):
        ax2.scatter(electric_h2[scenario], y + offset, s=28, color=SCENARIO_COLORS[scenario], zorder=3)
    ax2.set_yticks(y, modes)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 100)
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.set_title("Electricity + hydrogen share", loc="left", fontsize=10, fontweight="bold", color=INK, pad=18)
    ax2.text(0, 1.015, "2050 final energy", transform=ax2.transAxes, fontsize=6.3, color=MUTED, va="bottom")
    ax2.set_xlabel("% of mode final energy", fontsize=6.7, color=MUTED)
    ax2.grid(axis="x", color=GRID, lw=0.8)
    ax2.tick_params(colors=MUTED, labelsize=6.8, length=0)
    ax2.spines[["top", "right", "left", "bottom"]].set_visible(False)

    note = fig.add_axes([0.07, 0.072, 0.86, 0.092], zorder=10)
    rounded_box(note, facecolor=WHITE, edgecolor=GRID, radius=0.04)
    add_wrapped(
        note,
        0.025,
        0.76,
        "In SSP1-L, electricity and hydrogen supply about 60% of passenger-car final energy and 70% of truck energy by 2050, but only 21% of other transport. Aviation, shipping, rail and buses together remain the largest energy block and still obtain about 70% of their energy from liquid fossil fuels.",
        112,
        fontsize=7.7,
        lineheight=1.22,
    )
    fig.text(0.07, 0.059, "‘Trucks’ combines 18- and 40-tonne road freight; ‘other transport’ combines buses, rail, aviation and shipping.", fontsize=5.9, color=MUTED)
    fig.text(0.07, 0.049, "Shares are final energy—not activity, fleet stock or life-cycle impact.", fontsize=5.9, color=MUTED)
    return fig


def build_report() -> Path:
    data = load_data()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pages = [
        page_one(data),
        page_two(data),
        page_three(data),
        global_2050_page(data),
        global_industry_page(data),
        electricity_sector_page(data),
        heat_sector_page(data),
        cement_sector_page(data),
        steel_sector_page(data),
        transport_sector_page(data),
        transport_modes_page(data),
    ]
    with PdfPages(
        OUTPUT_FILE,
        metadata={
            "Title": "IMAGE SSP1-L, SSP2-M and SSP3-H: an IAM–LCA student briefing",
            "Author": "Generated from PyamDashView scenario data",
            "Subject": "IAM scenarios and prospective life-cycle assessment",
            "Keywords": "IMAGE, SSP1-L, SSP2-M, SSP3-H, IAM, LCA, premise",
        },
    ) as pdf:
        for fig in pages:
            pdf.savefig(fig, facecolor=fig.get_facecolor(), bbox_inches=None)
            plt.close(fig)
    return OUTPUT_FILE


if __name__ == "__main__":
    output = build_report()
    print(output)
