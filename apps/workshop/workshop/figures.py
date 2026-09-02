from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import ANONYMOUS_ORDER, CORE_SCENARIOS, NARRATIVES
from .data import (
    context_series,
    electricity_mix,
    image_end_use_transformations,
    image_electricity_chain,
    image_energy_layers,
    image_region_mapping,
    image_total_energy_chain,
    iam_region_topologies,
    lcia_contributions,
    lcia_results,
    mechanics_series,
    pathways,
    premise_mapping_counts,
    remind_eu_region_mapping,
    sector_mix,
    steel_mix,
)

NEUTRAL_COLORS = ["#253746", "#526675", "#80909A", "#B0BAC0"]
TECH_COLORS = {
    "Solar": "#F5B642",
    "Wind": "#5C8DCE",
    "Hydro": "#4FA3A5",
    "Nuclear": "#8F6FB3",
    "Geothermal": "#B46A55",
    "Biomass": "#74A65A",
    "Coal": "#383D42",
    "Gas": "#9A7B5B",
    "Oil": "#B85C5C",
    "Storage": "#D5C7E8",
    "Other renewables": "#9AC9A8",
    "Other": "#B8B8B8",
}

SCENARIO_COLORS = {
    "H": "#8F1D1D",
    "HL": "#C44E52",
    "M": "#D99614",
    "ML": "#7E9D42",
    "L": "#008A82",
    "VL": "#006B8F",
    "LN": "#7656A8",
}

SSP_COLORS = {
    "SSP1": "#006B8F",
    "SSP2": "#D99614",
    "SSP3": "#C44E52",
    "SSP4": "#7656A8",
    "SSP5": "#765237",
}

ENERGY_LAYER_COLORS = {
    "Coal": "#383D42",
    "Oil": "#B85C5C",
    "Gas": "#9A7B5B",
    "Biomass": "#74A65A",
    "Nuclear": "#8F6FB3",
    "Non-biomass renewables": "#24A19C",
    "Hydro": "#4FA3A5",
    "Solar": "#F5B642",
    "Wind": "#5C8DCE",
    "Other": "#B8B8B8",
}

END_USE_COLORS = {
    "Battery electric": "#008A82",
    "Fuel cell": "#5C8DCE",
    "Combustion": "#9A7B5B",
    "Conventional kiln": "#6B7075",
    "Efficient kiln": "#D99614",
    "MEA CCS": "#4FA3A5",
    "On-site CCS": "#7656A8",
    "Oxyfuel CCS": "#006B8F",
    "Conventional BF/BOF": "#383D42",
    "Advanced fossil primary": "#9A7B5B",
    "Primary with CCS": "#5C8DCE",
    "Hydrogen + electrowinning": "#008A82",
    "Secondary steel": "#74A65A",
    "Fossil boilers": "#9A7B5B",
    "Electric heating": "#F5B642",
    "District heat": "#C44E52",
    "Bioenergy": "#74A65A",
    "Hydrogen": "#5C8DCE",
}

IAM_MAP_COLORS = [
    "#006B8F",
    "#D99614",
    "#008A82",
    "#7656A8",
    "#C44E52",
    "#5C8DCE",
    "#74A65A",
    "#9A7B5B",
    "#4FA3A5",
    "#B46A55",
    "#253746",
    "#E17C05",
    "#6B9AC4",
    "#B565A7",
    "#52796F",
    "#D1495B",
    "#2A9D8F",
    "#8D6A9F",
    "#E9C46A",
    "#457B9D",
    "#BC6C25",
    "#7A9E9F",
    "#A44A3F",
    "#3D5A80",
    "#81B29A",
    "#F4A261",
    "#6D597A",
    "#264653",
    "#C77DFF",
    "#588157",
    "#E76F51",
    "#577590",
    "#F2CC8F",
]

# Stable semantic colours for the interactive sector snapshot. The set of
# reported technologies changes by year, so assigning colours by the index of
# the currently visible traces makes the same technology change colour as the
# presenter clicks through time.
SECTOR_SNAPSHOT_COLORS = {
    **TECH_COLORS,
    "Battery electric": "#008A82",
    "Fuel cell": "#5C8DCE",
    "Gaseous fuel": "#9A7B5B",
    "Gasoline": "#B85C5C",
    "Conventional kiln": "#6B7075",
    "Efficient kiln": "#D99614",
    "MEA CCS": "#4FA3A5",
    "On-site CCS": "#7656A8",
    "Oxyfuel CCS": "#006B8F",
    "Hydrogen-based primary": "#008A82",
    "Other primary": "#383D42",
    "Primary with CCS": "#5C8DCE",
    "Secondary": "#74A65A",
    "BECCS": "#74A65A",
    "Biofuels with CCS": "#D99614",
    "Direct air capture": "#008A82",
    "Synthetic fuels with CCS": "#7656A8",
    "Other removal": "#B8B8B8",
}

END_USE_GROUP_ORDER = {
    "Passenger cars": ["Combustion", "Fuel cell", "Battery electric"],
    "Cement": [
        "Conventional kiln",
        "Efficient kiln",
        "On-site CCS",
        "MEA CCS",
        "Oxyfuel CCS",
    ],
    "Steel": [
        "Conventional BF/BOF",
        "Advanced fossil primary",
        "Primary with CCS",
        "Hydrogen + electrowinning",
        "Secondary steel",
    ],
    "Space heating": [
        "Fossil boilers",
        "Bioenergy",
        "District heat",
        "Hydrogen",
        "Electric heating",
    ],
}

END_USE_LABELS = {
    "MEA CCS": "MEA carbon capture",
    "On-site CCS": "On-site carbon capture",
    "Oxyfuel CCS": "Oxyfuel carbon capture",
    "Conventional BF/BOF": "Blast furnace / basic oxygen furnace",
    "Advanced fossil primary": "Advanced fossil-based primary steel",
    "Primary with CCS": "Primary steel with carbon capture",
    "Hydrogen + electrowinning": "Hydrogen / electrowinning",
    "Secondary steel": "Recycled steel",
}

STEEL_WEU_ROUTE_ORDER = [
    "Other primary",
    "Primary with CCS",
    "Hydrogen-based primary",
    "Secondary",
]


def _base_layout(fig: go.Figure, title: str, unit: str | None = None) -> go.Figure:
    fig.update_layout(
        title={"text": title, "x": 0, "xanchor": "left", "font": {"size": 24}},
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 16, "color": "#17232C"},
        margin={"l": 66, "r": 28, "t": 70, "b": 58},
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.2, "x": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, title=None)
    fig.update_yaxes(gridcolor="#E4E8EA", zerolinecolor="#9AA6AD", title=unit)
    return fig


def scenario_trajectory(
    sector: str,
    title: str,
    reveal: bool,
    scenarios: list[str] | None = None,
    model: str = "image",
) -> go.Figure:
    scenarios = scenarios or ANONYMOUS_ORDER
    frame = context_series(sector, scenarios, model=model)
    fig = go.Figure()
    unit = frame["display_unit"].iloc[0] if not frame.empty else None
    for index, scenario in enumerate(scenarios):
        data = frame[frame["scenario"] == scenario]
        narrative = NARRATIVES.get(scenario, {})
        label = (
            narrative.get("short_name", scenario)
            if reveal
            else narrative.get("anonymous_id", chr(65 + index))
        )
        color = (
            narrative.get("color", NEUTRAL_COLORS[index % len(NEUTRAL_COLORS)])
            if reveal
            else NEUTRAL_COLORS[index % len(NEUTRAL_COLORS)]
        )
        dash = (
            narrative.get("line_dash", "solid")
            if reveal
            else ["solid", "dash", "dot", "longdash"][index % 4]
        )
        fig.add_trace(
            go.Scatter(
                x=data["year"],
                y=data["display_value"],
                mode="lines",
                name=label,
                line={"width": 4, "color": color, "dash": dash},
                hovertemplate=f"{label}<br>%{{x}}: %{{y:.2f}} {unit}<extra></extra>",
            )
        )
    fig.add_vline(x=2020, line_width=1, line_dash="dot", line_color="#7D8A92")
    return _base_layout(fig, title, unit)


def detective_figure(clue: int, reveal: bool) -> tuple[go.Figure, str]:
    sequence = [
        ("Population", "Clue 1: population"),
        ("Gross Domestic Product", "Clue 2: economic activity"),
        ("Carbon Dioxide emissions", "Clue 3: annual CO₂ emissions"),
        ("GMST increase", "Clue 4: global mean surface temperature"),
        ("Final Energy", "Clue 5: final-energy demand"),
        ("Carbon Dioxide Removal", "Clue 6: reported carbon removal"),
    ]
    sector, title = sequence[min(clue, len(sequence) - 1)]
    return scenario_trajectory(sector, title, reveal), title


def pathway_comparison() -> go.Figure:
    scenarios = ["SSP2-VLHO", "SSP2-M"]
    co2 = context_series("Carbon Dioxide emissions", scenarios)
    gmst = context_series("GMST increase", scenarios)
    fig = make_subplots(
        rows=1, cols=2, subplot_titles=("Annual CO₂", "Warming response")
    )
    for scenario in scenarios:
        narrative = NARRATIVES[scenario]
        for col, frame in [(1, co2), (2, gmst)]:
            data = frame[frame["scenario"] == scenario]
            fig.add_trace(
                go.Scatter(
                    x=data["year"],
                    y=data["display_value"],
                    name=scenario,
                    legendgroup=scenario,
                    showlegend=col == 1,
                    mode="lines",
                    line={
                        "width": 4,
                        "color": narrative["color"],
                        "dash": narrative["line_dash"],
                    },
                ),
                row=1,
                col=col,
            )
    fig.update_yaxes(title_text="Gt CO₂/yr", row=1, col=1, gridcolor="#E4E8EA")
    fig.update_yaxes(title_text="°C above 1850–1900", row=1, col=2, gridcolor="#E4E8EA")
    fig.update_xaxes(showgrid=False)
    fig.update_layout(
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 16, "color": "#17232C"},
        margin={"l": 66, "r": 30, "t": 60, "b": 55},
        legend={"orientation": "h", "y": -0.2},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def electricity_snapshot(year: int = 2060) -> go.Figure:
    scenarios = ["SSP2-VLHO", "SSP2-M"]
    frame = electricity_mix(scenarios, year)
    fig = go.Figure()
    order = [
        "Coal",
        "Gas",
        "Oil",
        "Nuclear",
        "Biomass",
        "Hydro",
        "Wind",
        "Solar",
        "Geothermal",
        "Storage",
        "Other renewables",
        "Other",
    ]
    for technology in order:
        data = frame[frame["technology"] == technology]
        if data.empty:
            continue
        values = {row.scenario: row.share for row in data.itertuples()}
        fig.add_trace(
            go.Bar(
                x=scenarios,
                y=[values.get(scenario, 0) for scenario in scenarios],
                name=technology,
                marker_color=TECH_COLORS[technology],
                hovertemplate=f"{technology}: %{{y:.1%}}<extra></extra>",
            )
        )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(tickformat=".0%", range=[0, 1], title="Share of generation")
    return _base_layout(fig, f"Electricity technology shares in {year}", None)


def cdr_snapshot(year: int = 2060) -> go.Figure:
    scenarios = CORE_SCENARIOS
    frame = context_series("Carbon Dioxide Removal", scenarios)
    data = frame[frame["year"] == year]
    values = {row.scenario: row.display_value for row in data.itertuples()}
    fig = go.Figure()
    for scenario in scenarios:
        present = scenario in values
        fig.add_trace(
            go.Bar(
                x=[scenario],
                y=[values.get(scenario, 0)],
                name=scenario,
                marker_color=(
                    NARRATIVES[scenario]["color"] if present else "rgba(0,0,0,0)"
                ),
                marker_line=(
                    {"color": "#9AA6AD", "width": 2} if not present else {"width": 0}
                ),
                text=[f"{values[scenario]:,.0f}" if present else "missing / validate"],
                textposition="outside",
                hovertemplate=(
                    f"{scenario}: %{{y:,.0f}} Mt CO₂/yr<extra></extra>"
                    if present
                    else f"{scenario}: no row in structured CSV<extra></extra>"
                ),
                showlegend=False,
            )
        )
    fig.update_yaxes(title="Mt CO₂/yr")
    return _base_layout(fig, f"Reported CDR technologies in {year}", None)


def iam_mechanics_figure() -> go.Figure:
    frame = mechanics_series()
    series = {
        metric: frame[frame["metric"] == metric].sort_values("year")
        for metric in [
            "annual_investment",
            "hydrogen_output",
            "conversion_efficiency",
        ]
    }
    fig = make_subplots(
        rows=1,
        cols=3,
        horizontal_spacing=0.075,
        subplot_titles=(
            "1 · Annual electrolyser investment",
            "2 · Hydrogen output from electrolysis",
            "3 · Electrolyser efficiency",
        ),
    )

    investment = series["annual_investment"]
    output = series["hydrogen_output"]
    efficiency = series["conversion_efficiency"]
    fig.add_trace(
        go.Bar(
            x=investment["year"],
            y=investment["value"],
            marker={"color": "#D99614", "line": {"color": "#B47800", "width": 1}},
            hovertemplate="%{x}: $%{y:.1f} bn/yr<extra>Investment</extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=output["year"],
            y=output["value"],
            mode="lines+markers",
            line={"width": 4, "color": "#008A82"},
            marker={"size": 7, "color": "#008A82"},
            fill="tozeroy",
            fillcolor="rgba(0, 138, 130, .12)",
            hovertemplate="%{x}: %{y:.2f} EJ/yr<extra>Hydrogen output</extra>",
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=efficiency["year"],
            y=efficiency["value"],
            mode="lines+markers",
            line={"width": 4, "color": "#7656A8"},
            marker={"size": 8, "color": "#7656A8"},
            hovertemplate="%{x}: %{y:.0f}%<extra>Conversion efficiency</extra>",
            showlegend=False,
        ),
        row=1,
        col=3,
    )

    fig.add_annotation(
        x=2035,
        y=float(investment.loc[investment["year"] == 2035, "value"].iloc[0]),
        text="<b>Peak 2035</b><br>$116 bn/yr",
        showarrow=True,
        arrowhead=2,
        ax=48,
        ay=35,
        bgcolor="#FFF7DF",
        bordercolor="#D99614",
        font={"size": 11},
        row=1,
        col=1,
    )
    fig.add_annotation(
        x=2060,
        y=float(output.loc[output["year"] == 2060, "value"].iloc[0]),
        text="<b>2060</b><br>32.1 EJ/yr",
        showarrow=True,
        arrowhead=2,
        ax=-52,
        ay=35,
        bgcolor="#E9F6F3",
        bordercolor="#008A82",
        font={"size": 11},
        row=1,
        col=2,
    )
    fig.add_annotation(
        x=2055,
        y=75,
        text="<b>+14 percentage points</b><br>from 2020",
        showarrow=True,
        arrowhead=2,
        ax=-58,
        ay=35,
        bgcolor="#F4F0FA",
        bordercolor="#7656A8",
        font={"size": 11},
        row=1,
        col=3,
    )

    for col in [1, 2, 3]:
        fig.update_xaxes(
            showgrid=False,
            tickvals=[2020, 2030, 2040, 2050, 2060],
            range=[2018, 2062],
            row=1,
            col=col,
        )
    fig.update_yaxes(
        title="billion US$2017/yr",
        range=[0, 132],
        gridcolor="#E4E8EA",
        row=1,
        col=1,
    )
    fig.update_yaxes(
        title="EJ H₂/yr",
        range=[0, 36],
        gridcolor="#E4E8EA",
        row=1,
        col=2,
    )
    fig.update_yaxes(
        title="%",
        range=[58, 80],
        dtick=5,
        gridcolor="#E4E8EA",
        row=1,
        col=3,
    )
    fig.update_layout(
        template="plotly_white",
        margin={"l": 58, "r": 24, "t": 48, "b": 38},
        font={"family": "Arial, Helvetica, sans-serif", "size": 13, "color": "#17232C"},
        bargap=0.22,
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def energy_accounting_example_figure(
    year: int = 2060, scale_total: float | None = None
) -> go.Figure:
    frame = image_electricity_chain()
    frame = frame[frame["year"].eq(year)]
    if frame.empty:
        raise ValueError(f"No IMAGE electricity-chain data for {year}")
    values = {(row.stage, row.group): float(row.value) for row in frame.itertuples()}
    primary = {
        group: values[("Primary input to electricity", group)]
        for group in ["Fossil", "Biomass", "Nuclear + hydro", "Wind + solar"]
    }
    primary_total = sum(primary.values())
    electricity = values[("Secondary electricity", "Electricity output")]
    conversion_loss = primary_total - electricity
    passenger = values[("Final electricity", "Passenger transport")]
    heating = values[("Final electricity", "Space heating")]
    other_balance = electricity - passenger - heating

    labels = [
        f"Fossil<br><b>{primary['Fossil']:.2f} EJ/yr</b>",
        f"Biomass<br><b>{primary['Biomass']:.2f} EJ/yr</b>",
        f"Nuclear + hydro<br><b>{primary['Nuclear + hydro']:.2f} EJ/yr</b>",
        f"Wind + solar<br><b>{primary['Wind + solar']:.2f} EJ/yr</b>",
        f"Power sector<br><b>{primary_total:.2f} EJ/yr in</b>",
        f"Electricity<br><b>{electricity:.2f} EJ/yr</b>",
        f"Conversion / own use<br><b>{conversion_loss:.2f} EJ/yr</b>",
        f"Passenger transport<br><b>{passenger:.2f} EJ/yr</b>",
        f"Space heating<br><b>{heating:.2f} EJ/yr</b>",
        f"Other uses + balance<br><b>{other_balance:.2f} EJ/yr</b>",
    ]
    sources = [0, 1, 2, 3, 4, 4, 5, 5, 5]
    targets = [4, 4, 4, 4, 5, 6, 7, 8, 9]
    link_values = [
        primary["Fossil"],
        primary["Biomass"],
        primary["Nuclear + hydro"],
        primary["Wind + solar"],
        electricity,
        conversion_loss,
        passenger,
        heating,
        other_balance,
    ]
    link_colors = [
        "rgba(91,74,66,.50)",
        "rgba(116,166,90,.50)",
        "rgba(143,111,179,.46)",
        "rgba(36,161,156,.52)",
        "rgba(0,107,143,.52)",
        "rgba(196,78,82,.35)",
        "rgba(0,138,130,.50)",
        "rgba(217,150,20,.48)",
        "rgba(128,144,154,.40)",
    ]
    node_colors = [
        "#5B4A42",
        "#74A65A",
        "#8F6FB3",
        "#24A19C",
        "#D99614",
        "#006B8F",
        "#C44E52",
        "#008A82",
        "#D99614",
        "#80909A",
    ]
    node_x = [0.01, 0.01, 0.01, 0.01, 0.31, 0.57, 0.57, 0.88, 0.88, 0.88]
    node_y = [0.04, 0.28, 0.54, 0.78, 0.37, 0.25, 0.76, 0.06, 0.36, 0.70]

    if scale_total is not None and scale_total > primary_total:
        # Transparent scale anchors make flow widths comparable across panels.
        labels.extend(["", ""])
        node_colors.extend(["rgba(0,0,0,0)", "rgba(0,0,0,0)"])
        node_x.extend([0.01, 0.31])
        node_y.extend([0.96, 0.96])
        sources.append(10)
        targets.append(11)
        link_values.append(scale_total - primary_total)
        link_colors.append("rgba(0,0,0,0)")

    fig = go.Figure(
        go.Sankey(
            arrangement="snap" if scale_total is not None else "fixed",
            orientation="h",
            valueformat=".2f",
            valuesuffix=" EJ/yr",
            node={
                "pad": 12,
                "thickness": 18,
                "line": {"color": "#FFFFFF", "width": 1.5},
                "label": labels,
                "color": node_colors,
                "x": node_x,
                "y": node_y,
                "hovertemplate": "%{label}<extra></extra>",
            },
            link={
                "source": sources,
                "target": targets,
                "value": link_values,
                "color": link_colors,
                "hovertemplate": "%{source.label} → %{target.label}<br><b>%{value:.2f} EJ/yr</b><extra></extra>",
            },
        )
    )
    fig.update_layout(
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 10, "color": "#17232C"},
        margin={"l": 8, "r": 8, "t": 8, "b": 6},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def total_energy_system_figure(
    year: int = 2060, scale_total: float | None = None
) -> go.Figure:
    frame = image_total_energy_chain()
    frame = frame[frame["year"].eq(year)]
    if frame.empty:
        raise ValueError(f"No IMAGE total-energy-chain data for {year}")
    values = {(row.stage, row.group): float(row.value) for row in frame.itertuples()}
    primary_groups = [
        "Fossil",
        "Biomass",
        "Nuclear + other",
        "Non-biomass renewables",
    ]
    carrier_groups = [
        "Electricity",
        "Liquids",
        "Gases",
        "Solids + biomass",
        "Heat",
        "Hydrogen",
    ]
    final_groups = ["Industry", "Transport", "Buildings", "Other + carbon management"]
    primary = {
        group: values[("Primary energy supply", group)] for group in primary_groups
    }
    flows = frame[frame["stage"].eq("Final energy flow")]
    carriers = {
        group: float(flows.loc[flows["group"].eq(group), "value"].sum())
        for group in carrier_groups
    }
    final = {
        group: float(flows.loc[flows["destination"].eq(group), "value"].sum())
        for group in final_groups
    }
    primary_total = sum(primary.values())
    final_total = sum(final.values())
    accounting_difference = primary_total - final_total
    if accounting_difference < 0:
        raise ValueError(
            f"Final energy exceeds primary energy in {year}: {accounting_difference}"
        )

    final_display = {
        "Industry": "Industry",
        "Transport": "Transport",
        "Buildings": "Buildings",
        "Other + carbon management": "Other + C management",
    }
    node_specs = [
        ("Fossil", primary["Fossil"]),
        ("Biomass", primary["Biomass"]),
        ("Nuclear + other", primary["Nuclear + other"]),
        ("Renewables", primary["Non-biomass renewables"]),
        ("Conversion + direct delivery", primary_total),
        *[
            (
                "Solids / biomass" if group == "Solids + biomass" else group,
                carriers[group],
            )
            for group in carrier_groups
        ],
        ("Primary-to-final difference", accounting_difference),
        *[(final_display[group], final[group]) for group in final_groups],
    ]
    hover_labels = [
        f"{label}<br><b>{amount:.2f} EJ/yr</b>" for label, amount in node_specs
    ]
    labels = []
    for index, (label, amount) in enumerate(node_specs):
        if amount < 2 or (label == "Hydrogen" and amount < 10):
            labels.append("")
        elif 5 <= index <= 10:
            labels.append(label)
        else:
            labels.append(f"{label}<br><b>{amount:.1f}</b>")
    sources = [0, 1, 2, 3]
    targets = [4, 4, 4, 4]
    link_values = [
        primary["Fossil"],
        primary["Biomass"],
        primary["Nuclear + other"],
        primary["Non-biomass renewables"],
    ]
    link_colors = [
        "rgba(91,74,66,.50)",
        "rgba(116,166,90,.50)",
        "rgba(143,111,179,.45)",
        "rgba(36,161,156,.50)",
    ]
    carrier_colors = {
        "Electricity": "rgba(0,107,143,.48)",
        "Liquids": "rgba(184,92,92,.46)",
        "Gases": "rgba(154,123,91,.46)",
        "Solids + biomass": "rgba(116,166,90,.46)",
        "Heat": "rgba(217,150,20,.46)",
        "Hydrogen": "rgba(118,86,168,.46)",
    }
    carrier_node_index = {
        group: 5 + index for index, group in enumerate(carrier_groups)
    }
    final_node_index = {group: 12 + index for index, group in enumerate(final_groups)}
    for group in carrier_groups:
        sources.append(4)
        targets.append(carrier_node_index[group])
        link_values.append(carriers[group])
        link_colors.append(carrier_colors[group])
    sources.append(4)
    targets.append(11)
    link_values.append(accounting_difference)
    link_colors.append("rgba(196,78,82,.30)")
    for group in carrier_groups:
        carrier_rows = flows[flows["group"].eq(group)]
        for destination in final_groups:
            amount = float(
                carrier_rows.loc[
                    carrier_rows["destination"].eq(destination), "value"
                ].sum()
            )
            if amount <= 0:
                continue
            sources.append(carrier_node_index[group])
            targets.append(final_node_index[destination])
            link_values.append(amount)
            link_colors.append(carrier_colors[group].replace(".4", ".28"))
    node_colors = [
        "#5B4A42",
        "#74A65A",
        "#8F6FB3",
        "#24A19C",
        "#D99614",
        "#006B8F",
        "#B85C5C",
        "#9A7B5B",
        "#74A65A",
        "#D99614",
        "#7656A8",
        "#C44E52",
        "#7656A8",
        "#006B8F",
        "#008A82",
        "#80909A",
    ]
    node_x = [
        0.01,
        0.01,
        0.01,
        0.01,
        0.28,
        0.56,
        0.56,
        0.56,
        0.56,
        0.56,
        0.56,
        0.56,
        0.91,
        0.91,
        0.91,
        0.91,
    ]
    node_y = [
        0.02,
        0.30,
        0.56,
        0.76,
        0.35,
        0.02,
        0.19,
        0.36,
        0.53,
        0.68,
        0.80,
        0.90,
        0.02,
        0.28,
        0.52,
        0.76,
    ]
    if scale_total is not None and scale_total > primary_total:
        labels.extend(["", ""])
        hover_labels.extend(["Scale spacer", "Scale spacer"])
        node_colors.extend(["rgba(0,0,0,0)", "rgba(0,0,0,0)"])
        node_x.extend([0.01, 0.28])
        node_y.extend([0.97, 0.97])
        sources.append(16)
        targets.append(17)
        link_values.append(scale_total - primary_total)
        link_colors.append("rgba(0,0,0,0)")

    fig = go.Figure(
        go.Sankey(
            arrangement="snap" if scale_total is not None else "fixed",
            orientation="h",
            valueformat=".2f",
            valuesuffix=" EJ/yr",
            node={
                "pad": 7,
                "thickness": 13,
                "line": {"color": "#FFFFFF", "width": 1.3},
                "label": labels,
                "customdata": hover_labels,
                "color": node_colors,
                "x": node_x,
                "y": node_y,
                "hovertemplate": "%{customdata}<extra></extra>",
            },
            link={
                "source": sources,
                "target": targets,
                "value": link_values,
                "color": link_colors,
                "hovertemplate": "%{source.label} → %{target.label}<br><b>%{value:.2f} EJ/yr</b><extra></extra>",
            },
        )
    )
    fig.update_layout(
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 10, "color": "#17232C"},
        margin={"l": 8, "r": 8, "t": 8, "b": 6},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _stacked_energy_layer_figure(
    layer: str, groups: list[str], title: str
) -> go.Figure:
    frame = image_energy_layers()
    frame = frame[frame["layer"].eq(layer)]
    scenarios = CORE_SCENARIOS
    regions = ["World", "Europe (WEU + CEU)"]
    totals = frame.groupby(
        ["region", "scenario", "year"], as_index=False, observed=True
    )["value"].sum()
    max_totals = totals.groupby("region", observed=True)["value"].max() * 1.05
    fig = make_subplots(
        rows=2,
        cols=4,
        shared_xaxes=True,
        shared_yaxes="rows",
        vertical_spacing=0.18,
        horizontal_spacing=0.035,
        subplot_titles=tuple(scenarios) + ("", "", "", ""),
    )
    for region_index, region in enumerate(regions):
        row = region_index + 1
        for scenario_index, scenario in enumerate(scenarios):
            col = scenario_index + 1
            scenario_frame = frame[
                frame["region"].eq(region) & frame["scenario"].eq(scenario)
            ]
            cumulative: list[float] | None = None
            for group in groups:
                data = scenario_frame[scenario_frame["group"].eq(group)].sort_values(
                    "year"
                )
                if data.empty:
                    continue
                values = data["value"].astype(float).tolist()
                cumulative = (
                    values
                    if cumulative is None
                    else [total + value for total, value in zip(cumulative, values)]
                )
                fig.add_trace(
                    go.Scatter(
                        x=data["year"].astype(int).tolist(),
                        y=cumulative,
                        customdata=values,
                        name=group,
                        legendgroup=group,
                        showlegend=region_index == 0 and scenario_index == 0,
                        mode="lines",
                        line={"color": ENERGY_LAYER_COLORS[group], "width": 0.6},
                        fill="tozeroy" if group == groups[0] else "tonexty",
                        fillcolor=ENERGY_LAYER_COLORS[group],
                        hovertemplate=(
                            f"{region} · {scenario} · {group}"
                            "<br>%{x}: %{customdata:.1f} EJ/yr<extra></extra>"
                        ),
                    ),
                    row=row,
                    col=col,
                )

    fig.update_layout(
        title={"text": title, "x": 0, "xanchor": "left", "font": {"size": 18}},
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 11, "color": "#17232C"},
        margin={"l": 62, "r": 14, "t": 58, "b": 52},
        hovermode="x unified",
        legend={
            "orientation": "h",
            "y": -0.13,
            "x": 0,
            "font": {"size": 10},
            "traceorder": "normal",
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(
        showgrid=False,
        tickvals=[2020, 2060, 2100],
        range=[2018, 2102],
    )
    for row, region in enumerate(regions, 1):
        for col in range(1, 5):
            fig.update_yaxes(
                gridcolor="#E4E8EA",
                range=[0, float(max_totals.loc[region])],
                row=row,
                col=col,
            )
    fig.update_yaxes(title="<b>World</b><br>EJ/yr", row=1, col=1)
    fig.update_yaxes(title="<b>Europe</b><br>EJ/yr", row=2, col=1)
    return fig


def primary_energy_layer_figure() -> go.Figure:
    return _stacked_energy_layer_figure(
        "Primary energy",
        ["Coal", "Oil", "Gas", "Biomass", "Nuclear", "Non-biomass renewables"],
        "Resource inputs by carrier · World and Europe (WEU + CEU)",
    )


def secondary_energy_layer_figure() -> go.Figure:
    return _stacked_energy_layer_figure(
        "Secondary electricity",
        ["Coal", "Gas", "Oil", "Biomass", "Nuclear", "Hydro", "Solar", "Wind", "Other"],
        "Electricity output by technology group · World and Europe (WEU + CEU)",
    )


def final_energy_layer_figure() -> go.Figure:
    frame = image_energy_layers()
    frame = frame[frame["layer"].eq("Final energy")]
    services = [
        "Passenger transport",
        "Freight transport",
        "Iron & steel",
        "Space heating",
    ]
    scenarios = CORE_SCENARIOS
    regions = ["World", "Europe (WEU + CEU)"]
    maxima = frame.groupby(["region", "group"], observed=True)["value"].max() * 1.08
    fig = make_subplots(
        rows=2,
        cols=4,
        shared_xaxes=True,
        vertical_spacing=0.18,
        horizontal_spacing=0.045,
        subplot_titles=tuple(services) + ("", "", "", ""),
    )
    for region_index, region in enumerate(regions):
        row = region_index + 1
        for service_index, service in enumerate(services):
            col = service_index + 1
            for scenario in scenarios:
                data = frame[
                    frame["region"].eq(region)
                    & frame["group"].eq(service)
                    & frame["scenario"].eq(scenario)
                ].sort_values("year")
                fig.add_trace(
                    go.Scatter(
                        x=data["year"],
                        y=data["value"],
                        name=scenario,
                        legendgroup=scenario,
                        showlegend=region_index == 0 and service_index == 0,
                        mode="lines+markers",
                        line={"width": 2.1, "color": NARRATIVES[scenario]["color"]},
                        marker={"size": 3},
                        hovertemplate=(
                            f"{region} · {scenario} · {service}"
                            "<br>%{x}: %{y:.1f} EJ/yr<extra></extra>"
                        ),
                    ),
                    row=row,
                    col=col,
                )

    fig.update_layout(
        title={
            "text": "Selected end-use demands · World and Europe (WEU + CEU)",
            "x": 0,
            "xanchor": "left",
            "font": {"size": 18},
        },
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 11, "color": "#17232C"},
        margin={"l": 62, "r": 14, "t": 58, "b": 48},
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.12, "x": 0, "font": {"size": 10}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(
        showgrid=False,
        tickvals=[2020, 2060, 2100],
        range=[2018, 2102],
    )
    for row, region in enumerate(regions, 1):
        for col, service in enumerate(services, 1):
            fig.update_yaxes(
                gridcolor="#E4E8EA",
                range=[0, float(maxima.loc[(region, service)])],
                showticklabels=True,
                row=row,
                col=col,
            )
    fig.update_yaxes(title="<b>World</b><br>EJ/yr", row=1, col=1)
    fig.update_yaxes(title="<b>Europe</b><br>EJ/yr", row=2, col=1)
    return fig


def end_use_transformation_figure(domain: str) -> go.Figure:
    """Show absolute activity, market shares and specific energy side by side."""

    frame = image_end_use_transformations()
    frame = frame[frame["domain"].eq(domain)]
    mix = frame[frame["metric"].eq("technology mix")].copy()
    totals = mix.groupby("year", observed=True)["value"].transform("sum")
    mix["share"] = mix["value"] / totals.where(totals.ne(0))
    intensity = frame[frame["metric"].eq("specific energy")].sort_values("year")
    chart_settings = {
        "Passenger cars": (
            "Reported activity by powertrain",
            "Powertrain share",
            "Energy / passenger-km",
            1_000_000,
            "million model activity units",
        ),
        "Cement": (
            "Cement output by kiln route",
            "Kiln-route share",
            "Estimated sector energy / tonne",
            1,
            "Mt cement/yr",
        ),
        "Steel": (
            "Reported steel output by route",
            "Steel-route share",
            "Energy / tonne crude steel",
            1,
            "Mt/yr",
        ),
        "Space heating": (
            "Delivered energy by carrier",
            "Carrier share (technology estimate)",
            "Heating energy / person",
            1,
            "EJ/yr",
        ),
    }
    absolute_title, share_title, intensity_title, absolute_scale, absolute_unit = (
        chart_settings[domain]
    )
    fig = make_subplots(
        rows=1,
        cols=3,
        column_widths=[0.34, 0.34, 0.32],
        horizontal_spacing=0.075,
        subplot_titles=(
            f"<b>{absolute_title}</b>",
            f"<b>{share_title}</b>",
            f"<b>{intensity_title}</b>",
        ),
    )
    for group in END_USE_GROUP_ORDER[domain]:
        data = mix[mix["group"].eq(group)].sort_values("year")
        if data.empty:
            continue
        display_group = END_USE_LABELS.get(group, group)
        fig.add_trace(
            go.Scatter(
                x=data["year"],
                y=data["value"] / absolute_scale,
                customdata=data["share"],
                name=display_group,
                legendgroup=group,
                mode="lines",
                line={"width": 0.8, "color": END_USE_COLORS[group]},
                stackgroup="absolute",
                fillcolor=END_USE_COLORS[group],
                hovertemplate=(
                    f"{display_group}<br>%{{x}}: <b>%{{y:.2f}} {absolute_unit}</b>"
                    "<br>%{customdata:.1%} of reported mix<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=data["year"],
                y=data["share"],
                customdata=data["value"],
                name=display_group,
                legendgroup=group,
                showlegend=False,
                mode="lines",
                line={"width": 0.8, "color": END_USE_COLORS[group]},
                stackgroup="technology",
                fillcolor=END_USE_COLORS[group],
                hovertemplate=(
                    f"{display_group}<br>%{{x}}: <b>%{{y:.1%}}</b>"
                    "<br>Reported activity: %{customdata:.2f}<extra></extra>"
                ),
            ),
            row=1,
            col=2,
        )

    intensity_unit = str(intensity["unit"].iloc[0])
    fig.add_trace(
        go.Scatter(
            x=intensity["year"],
            y=intensity["value"],
            name="Specific energy use",
            mode="lines+markers",
            line={"width": 4, "color": "#006B8F"},
            marker={"size": 6, "color": "#FFFFFF", "line": {"width": 2}},
            fill="tozeroy",
            fillcolor="rgba(0,107,143,0.10)",
            showlegend=False,
            hovertemplate=(
                f"%{{x}}: <b>%{{y:.2f}} {intensity_unit}</b><extra></extra>"
            ),
        ),
        row=1,
        col=3,
    )
    for year, position in [(2020, "top right"), (2060, "top center")]:
        point = intensity[intensity["year"].eq(year)]
        if point.empty:
            continue
        value = float(point["value"].iloc[0])
        fig.add_trace(
            go.Scatter(
                x=[year],
                y=[value],
                mode="markers+text",
                text=[f"<b>{value:.2f}</b>"],
                textposition=position,
                marker={"size": 9, "color": "#006B8F"},
                showlegend=False,
                hoverinfo="skip",
                cliponaxis=False,
            ),
            row=1,
            col=3,
        )

    fig.update_layout(
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 11, "color": "#17232C"},
        margin={"l": 54, "r": 22, "t": 46, "b": 58},
        hovermode="x unified",
        legend={
            "orientation": "h",
            "y": -0.16,
            "x": 0,
            "font": {"size": 10},
            "traceorder": "normal",
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(
        showgrid=False,
        tickvals=[2020, 2040, 2060, 2080, 2100],
        range=[2018, 2102],
    )
    fig.update_yaxes(
        title=absolute_unit,
        gridcolor="#E4E8EA",
        rangemode="tozero",
        row=1,
        col=1,
    )
    fig.update_yaxes(
        title="Market share",
        tickformat=".0%",
        range=[0, 1],
        gridcolor="#E4E8EA",
        row=1,
        col=2,
    )
    fig.update_yaxes(
        title=intensity_unit,
        range=[0, float(intensity["value"].max()) * 1.22],
        gridcolor="#E4E8EA",
        row=1,
        col=3,
    )
    return fig


def energy_emissions_change_figure() -> go.Figure:
    years = list(range(2000, 2025))
    energy_twh = [
        110416.40,
        111493.29,
        113894.43,
        117849.60,
        123841.74,
        127936.72,
        131481.20,
        135617.98,
        137229.40,
        135033.22,
        141602.05,
        144913.30,
        147002.42,
        149599.73,
        151239.17,
        152357.62,
        154221.48,
        157625.31,
        161806.12,
        163694.61,
        157993.89,
        166043.50,
        169061.53,
        172238.78,
        176737.10,
    ]
    co2_gt = [
        25.511,
        25.693,
        26.265,
        27.653,
        28.610,
        29.599,
        30.594,
        31.499,
        32.050,
        31.513,
        33.318,
        34.480,
        34.955,
        35.276,
        35.466,
        35.404,
        35.393,
        35.975,
        36.734,
        37.087,
        35.158,
        36.867,
        37.528,
        38.094,
        38.599,
    ]
    energy_index = [100 * value / energy_twh[0] for value in energy_twh]
    co2_index = [100 * value / co2_gt[0] for value in co2_gt]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=years,
            y=energy_index,
            customdata=energy_twh,
            mode="lines",
            name="Primary energy",
            line={"width": 4, "color": "#006B8F"},
            hovertemplate=(
                "Primary energy<br>%{x}: index %{y:.1f}<br>"
                "%{customdata:,.0f} TWh<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=years,
            y=co2_index,
            customdata=co2_gt,
            mode="lines",
            name="Fossil CO₂",
            line={"width": 4, "color": "#C44E52"},
            hovertemplate=(
                "Fossil and industrial CO₂<br>%{x}: index %{y:.1f}<br>"
                "%{customdata:.1f} Gt CO₂<extra></extra>"
            ),
        )
    )
    for start, end, label in [
        (2008.6, 2009.4, "Financial crisis"),
        (2019.6, 2020.4, "Pandemic"),
    ]:
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor="#526675",
            opacity=0.08,
            line_width=0,
            annotation_text=label,
            annotation_position="top left",
            annotation_font={"size": 11, "color": "#5B6A74"},
        )
    fig.add_annotation(
        x=2024,
        y=energy_index[-1],
        text="<b>160</b>",
        showarrow=False,
        xanchor="left",
        xshift=7,
        font={"size": 14, "color": "#006B8F"},
    )
    fig.add_annotation(
        x=2024,
        y=co2_index[-1],
        text="<b>151</b>",
        showarrow=False,
        xanchor="left",
        xshift=7,
        font={"size": 14, "color": "#C44E52"},
    )
    fig.update_xaxes(tickvals=[2000, 2005, 2010, 2015, 2020, 2024], range=[2000, 2026])
    fig.update_yaxes(range=[96, 166], dtick=10)
    fig = _base_layout(
        fig,
        "Energy use and CO₂ emissions both rose, but at different rates",
        "Index · 2000 = 100",
    )
    fig.update_layout(
        legend={"orientation": "h", "y": -0.16, "x": 0.5, "xanchor": "center"}
    )
    return fig


def ghg_sector_figure() -> go.Figure:
    sectors = ["Energy supply", "Industry", "AFOLU", "Transport", "Buildings"]
    emissions = [20.0, 14.0, 13.0, 8.7, 3.3]
    shares = [34, 24, 22, 15, 6]
    colors = ["#006B8F", "#7656A8", "#74A65A", "#D99614", "#5C8DCE"]
    fig = go.Figure(
        go.Bar(
            x=emissions[::-1],
            y=sectors[::-1],
            orientation="h",
            marker_color=colors[::-1],
            text=[f"{share}%" for share in shares[::-1]],
            textposition="outside",
            customdata=shares[::-1],
            hovertemplate="%{y}<br>%{x:.1f} Gt CO₂-eq · %{customdata}%<extra></extra>",
        )
    )
    fig.update_xaxes(title="Gt CO₂-eq in 2019", range=[0, 23])
    fig.update_layout(showlegend=False)
    return _base_layout(fig, "Where direct emissions occur", None)


def ghg_gas_figure() -> go.Figure:
    labels = [
        "CO₂ · fossil + industry",
        "CO₂ · land use",
        "Methane",
        "Nitrous oxide",
        "F-gases",
    ]
    values = [38.0, 6.6, 11.0, 2.7, 1.4]
    colors = ["#006B8F", "#74A65A", "#D99614", "#7656A8", "#C44E52"]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            domain={"x": [0.0, 0.56], "y": [0.0, 1.0]},
            hole=0.56,
            sort=False,
            marker={"colors": colors, "line": {"color": "#FFFFFF", "width": 2}},
            textinfo="percent",
            textposition="inside",
            insidetextorientation="horizontal",
            textfont={"size": 13},
            hovertemplate="%{label}<br>%{value:.1f} Gt CO₂-eq · %{percent}<extra></extra>",
        )
    )
    fig.add_annotation(
        x=0.28,
        y=0.50,
        text="<b>2019</b><br>by gas",
        showarrow=False,
        font={"size": 17, "color": "#0B3B52"},
    )
    fig.update_layout(
        title={
            "text": "What is emitted",
            "x": 0,
            "xanchor": "left",
            "font": {"size": 24},
        },
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 13, "color": "#17232C"},
        margin={"l": 18, "r": 18, "t": 62, "b": 20},
        legend={"x": 0.63, "y": 0.50, "xanchor": "left", "yanchor": "middle"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        uniformtext={"minsize": 10, "mode": "hide"},
    )
    return fig


def ghg_region_figure() -> go.Figure:
    """2019 production-based GHG shares from IPCC AR6 WGIII Figure SPM.2."""
    regions = [
        "Eastern Asia",
        "North America",
        "Latin America & Caribbean",
        "Africa",
        "SE Asia & Pacific",
        "Southern Asia",
        "Europe",
        "E. Europe & W-Central Asia",
        "Middle East",
        "Australia, Japan & NZ",
        "International transport",
    ]
    shares = [27, 12, 10, 9, 9, 8, 8, 6, 5, 3, 2]
    colors = ["#006B8F"] + ["#5BAEA8"] * 4 + ["#BFDAD8"] * 5 + ["#D99614"]
    fig = go.Figure(
        go.Bar(
            x=shares[::-1],
            y=regions[::-1],
            orientation="h",
            marker_color=colors[::-1],
            text=[f"{value}%" for value in shares[::-1]],
            textposition="outside",
            hovertemplate="%{y}<br>%{x}% of 2019 GHG emissions<extra></extra>",
        )
    )
    fig = _base_layout(fig, "Where emissions are produced", "Share of 2019 GHG")
    fig.update_xaxes(range=[0, 30], ticksuffix="%", dtick=10)
    fig.update_yaxes(title=None, tickfont={"size": 10})
    fig.update_layout(
        showlegend=False,
        margin={"l": 148, "r": 24, "t": 62, "b": 42},
    )
    return fig


def carbon_budget_figure() -> go.Figure:
    targets = ["1.5°C · 50% likelihood", "2°C · 67% likelihood"]
    emitted = [2400, 2400]
    remaining = [500, 1150]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=targets,
            x=emitted,
            orientation="h",
            name="Emitted 1850–2019",
            marker_color="#526675",
            text=["2,400", "2,400"],
            textposition="inside",
            hovertemplate="Historical cumulative CO₂: %{x:,.0f} Gt<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=targets,
            x=remaining,
            orientation="h",
            name="AR6 remaining budget from 2020",
            marker_color="#008A82",
            text=["500", "1,150"],
            textposition="inside",
            hovertemplate="Remaining from 2020: %{x:,.0f} Gt CO₂<extra></extra>",
        )
    )
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title="Cumulative CO₂ · Gt")
    return _base_layout(fig, "A temperature limit is a cumulative constraint", None)


def same_net_zero_date_figure() -> go.Figure:
    """Teaching example: the area under an emissions pathway is what accumulates."""
    years = list(range(2020, 2051))
    steady = [40 * (2050 - year) / 30 for year in years]
    delayed = [40 if year <= 2030 else 40 * (2050 - year) / 20 for year in years]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=years,
            y=steady,
            mode="lines",
            name="Steady decline · 600 Gt",
            line={"width": 4, "color": "#008A82"},
            fill="tozeroy",
            fillcolor="rgba(0, 138, 130, 0.14)",
            hovertemplate="Steady decline<br>%{x}: %{y:.1f} Gt CO₂/yr<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=years,
            y=delayed,
            mode="lines",
            name="10-year delay · 800 Gt",
            line={"width": 4, "color": "#C44E52", "dash": "dash"},
            fill="tozeroy",
            fillcolor="rgba(196, 78, 82, 0.10)",
            hovertemplate="Delayed action<br>%{x}: %{y:.1f} Gt CO₂/yr<extra></extra>",
        )
    )
    fig.add_annotation(
        x=2040,
        y=29,
        text="<b>+200 Gt CO₂</b><br>despite the same 2050 endpoint",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#C44E52",
        ax=-25,
        ay=-52,
        font={"size": 13, "color": "#8F1D1D"},
        bgcolor="rgba(255,255,255,.88)",
        borderpad=4,
    )
    fig.add_annotation(
        x=2020,
        y=43.5,
        text="Schematic teaching calculation",
        showarrow=False,
        xanchor="left",
        font={"size": 11, "color": "#5B6A74"},
    )
    fig = _base_layout(
        fig,
        "Same net-zero date, different cumulative CO₂",
        "Annual emissions · Gt CO₂/yr",
    )
    fig.update_xaxes(tickvals=[2020, 2030, 2040, 2050])
    fig.update_yaxes(range=[0, 46])
    fig.update_layout(
        title={"x": 0.08, "xanchor": "left"},
        legend={"orientation": "h", "y": -0.23, "x": 0.5, "xanchor": "center"},
        hovermode="x unified",
    )
    return fig


def integration_matrix_figure() -> go.Figure:
    levers = [
        "Service demand",
        "Efficiency",
        "Electrification",
        "Low-carbon supply",
        "Fuels & feedstocks",
        "Land & removals",
    ]
    systems = ["Power", "Transport", "Industry", "Buildings", "AFOLU"]
    matrix = [
        [1, 2, 1, 3, 1, 1],
        [3, 2, 3, 2, 3, 0],
        [3, 2, 2, 2, 3, 1],
        [3, 3, 3, 2, 1, 0],
        [2, 2, 1, 1, 2, 3],
    ]
    meanings = {
        0: "Limited",
        1: "Supporting",
        2: "Material",
        3: "Central",
    }
    text = [[meanings[value] for value in row] for row in matrix]
    fig = go.Figure(
        go.Heatmap(
            z=matrix,
            x=levers,
            y=systems,
            customdata=text,
            hovertemplate=(
                "System: %{y}<br>Option: %{x}<br>Direct role: %{customdata}"
                "<extra></extra>"
            ),
            colorscale=[
                [0.0, "#EDF1F3"],
                [0.33, "#BFDAD8"],
                [0.66, "#5BAEA8"],
                [1.0, "#006B8F"],
            ],
            zmin=0,
            zmax=3,
            showscale=False,
            xgap=5,
            ygap=5,
        )
    )
    fig.update_layout(
        template="plotly_white",
        margin={"l": 90, "r": 20, "t": 55, "b": 95},
        font={"family": "Arial", "size": 14},
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(tickangle=-25, side="bottom")
    return fig


def sector_mitigation_potential_figure() -> go.Figure:
    """Put two IPCC potential assessments in the context of 2019 footprints."""
    sectors = ["Industry", "Transport", "Buildings"]
    current = [20.0, 8.7, 9.4]
    potential_2030 = [5.4, 3.8, 2.0]
    potential_2050 = [4.4, 4.6, 6.8]
    remaining_2030 = [
        total - reduction for total, reduction in zip(current, potential_2030)
    ]
    remaining_after_both = [
        total - reduction_2030 - reduction_2050
        for total, reduction_2030, reduction_2050 in zip(
            current, potential_2030, potential_2050
        )
    ]
    positions = [0, 1, 2]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=positions,
            y=current,
            width=0.58,
            name="2019 sector footprint",
            showlegend=False,
            marker_color="#D9E0E4",
            marker_line={"color": "#B5C0C6", "width": 1.2},
            customdata=sectors,
            hovertemplate=(
                "%{customdata}<br>2019 footprint: %{y:.1f} Gt CO₂-eq/yr"
                "<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Bar(
            x=[position - 0.14 for position in positions],
            y=potential_2030,
            base=remaining_2030,
            width=0.27,
            name="2030 economic potential",
            showlegend=False,
            marker_color="#006B8F",
            text=[f"{value:.1f}" for value in potential_2030],
            textposition="inside",
            textfont={"color": "#FFFFFF", "size": 10},
            customdata=list(zip(sectors, current)),
            hovertemplate=(
                "%{customdata[0]}<br>2019 footprint: %{customdata[1]:.1f} Gt CO₂-eq/yr"
                "<br>2030 economic potential: %{y:.1f} Gt CO₂-eq/yr"
                "<br>Assessed options below USD100/t CO₂-eq<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Bar(
            x=[position + 0.14 for position in positions],
            y=potential_2050,
            base=remaining_after_both,
            width=0.27,
            name="Additional 2050 demand-side potential",
            showlegend=False,
            marker_color="#D99614",
            text=[f"{value:.1f}" for value in potential_2050],
            textposition="inside",
            textfont={"color": "#17232C", "size": 10},
            customdata=list(zip(sectors, current, potential_2030)),
            hovertemplate=(
                "%{customdata[0]}<br>2019 footprint: %{customdata[1]:.1f} Gt CO₂-eq/yr"
                "<br>2030 economic potential: %{customdata[2]:.1f} Gt CO₂-eq/yr"
                "<br>Additional 2050 demand-side potential: %{y:.1f} Gt CO₂-eq/yr"
                "<br>Technical potential versus stated-policies baselines"
                "<extra></extra>"
            ),
        )
    )
    for position, total in zip(positions, current):
        fig.add_annotation(
            x=position,
            y=total + 0.75,
            text=f"2019: <b>{total:.1f}</b>",
            showarrow=False,
            font={"size": 10, "color": "#5B6A74"},
        )
    fig.update_layout(
        template="plotly_white",
        title={
            "text": (
                "<b>One footprint, cumulative reduction potential</b><br>"
                "<sup>Blue descends from 2019; yellow continues from the blue endpoint</sup>"
            ),
            "x": 0,
            "xanchor": "left",
            "font": {"size": 17},
        },
        font={"family": "Arial, Helvetica, sans-serif", "size": 11, "color": "#17232C"},
        margin={"l": 48, "r": 16, "t": 66, "b": 46},
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="overlay",
    )
    fig.update_xaxes(
        showgrid=False,
        tickvals=positions,
        ticktext=sectors,
        range=[-0.55, 2.55],
    )
    fig.update_yaxes(
        title="Gt CO₂-eq/yr",
        range=[0, 22.5],
        gridcolor="#E4E8EA",
        dtick=5,
    )
    return fig


def model_coverage_figure() -> go.Figure:
    frame = premise_mapping_counts()
    sectors = [
        "Electricity",
        "Final energy",
        "Fuels",
        "Cement",
        "Steel",
        "Passenger cars",
        "Road freight",
        "Heat",
    ]
    sector_labels = {
        "Electricity": "Electricity",
        "Final energy": "Final<br>energy",
        "Fuels": "Fuels",
        "Cement": "Cement",
        "Steel": "Steel",
        "Passenger cars": "Passenger<br>cars",
        "Road freight": "Road<br>freight",
        "Heat": "Heat",
    }
    models = ["image", "message", "remind", "remind-eu", "tiam-ucl", "gcam"]
    model_labels = {
        "image": "IMAGE",
        "message": "MESSAGE",
        "remind": "REMIND",
        "remind-eu": "REMIND-EU",
        "tiam-ucl": "TIAM-UCL",
        "gcam": "GCAM",
    }
    matrix: list[list[int]] = []
    for model in models:
        subset = frame[frame["model"].eq(model)].set_index("sector")
        row: list[int] = []
        for sector in sectors:
            row.append(int(subset.loc[sector, "mapped_variable_count"]))
        matrix.append(row)
    fig = go.Figure(
        go.Heatmap(
            z=matrix,
            x=[sector_labels[sector] for sector in sectors],
            y=[model_labels[model] for model in models],
            customdata=matrix,
            hovertemplate=(
                "%{y}<br>%{x}: <b>%{customdata} distinct mapped variables</b>"
                "<extra></extra>"
            ),
            colorscale=[
                [0.0, "#F2F5F6"],
                [0.12, "#D5E8E5"],
                [0.35, "#8DC8C0"],
                [0.65, "#2C9991"],
                [1.0, "#075E60"],
            ],
            zmin=0,
            zmax=315,
            colorbar={
                "title": {
                    "text": "Mapped<br>variables",
                    "side": "right",
                    "font": {"size": 10},
                },
                "tickvals": [0, 50, 100, 200, 300],
                "thickness": 12,
                "len": 0.82,
                "outlinewidth": 0,
                "tickfont": {"size": 10},
            },
            xgap=3,
            ygap=3,
        )
    )
    for row_index, model in enumerate(models):
        for column_index, sector in enumerate(sectors):
            count = matrix[row_index][column_index]
            fig.add_annotation(
                x=sector_labels[sector],
                y=model_labels[model],
                text=f"<b>{count}</b>",
                showarrow=False,
                font={
                    "family": "Arial, Helvetica, sans-serif",
                    "size": 12,
                    "color": "#FFFFFF" if count >= 105 else "#17232C",
                },
            )
    fig.update_layout(
        template="plotly_white",
        margin={"l": 86, "r": 76, "t": 8, "b": 58},
        font={
            "family": "Arial, Helvetica, sans-serif",
            "size": 12,
            "color": "#17232C",
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(side="bottom", tickfont={"size": 11}, fixedrange=True)
    fig.update_yaxes(
        autorange="reversed",
        tickfont={"size": 11, "color": "#253746"},
        fixedrange=True,
    )
    return fig


def premise_mapping_counts_figure() -> go.Figure:
    frame = premise_mapping_counts()
    sectors = [
        "Electricity",
        "Final energy",
        "Fuels",
        "Cement",
        "Steel",
        "Passenger cars",
        "Road freight",
        "Heat",
    ]
    sector_labels = {
        "Electricity": "Electricity",
        "Final energy": "Final<br>energy",
        "Fuels": "Fuels",
        "Cement": "Cement",
        "Steel": "Steel",
        "Passenger cars": "Passenger<br>cars",
        "Road freight": "Road<br>freight",
        "Heat": "Heat",
    }
    model_settings = {
        "image": ("IMAGE", "#006B8F"),
        "message": ("MESSAGE", "#D99614"),
        "remind": ("REMIND", "#C44E52"),
        "remind-eu": ("REMIND-EU", "#7656A8"),
        "tiam-ucl": ("TIAM-UCL", "#008A82"),
        "gcam": ("GCAM", "#526675"),
    }
    maxima = frame.groupby("sector", observed=True)["mapped_variable_count"].max()
    fig = go.Figure()
    for model, (label, color) in model_settings.items():
        subset = frame[frame["model"].eq(model)].set_index("sector")
        counts = [
            int(subset.loc[sector, "mapped_variable_count"]) for sector in sectors
        ]
        text = [
            str(count) if count == int(maxima.loc[sector]) and count > 0 else ""
            for sector, count in zip(sectors, counts)
        ]
        fig.add_trace(
            go.Bar(
                x=[sector_labels[sector] for sector in sectors],
                y=counts,
                name=label,
                marker_color=color,
                text=text,
                textposition="outside",
                textfont={"size": 10, "color": "#17232C"},
                cliponaxis=False,
                customdata=[sector for sector in sectors],
                hovertemplate=(
                    f"{label}<br>%{{customdata}}: "
                    "<b>%{y} distinct mapped variables</b><extra></extra>"
                ),
            )
        )
    fig.update_layout(
        template="plotly_white",
        barmode="group",
        bargap=0.16,
        bargroupgap=0.04,
        font={"family": "Arial, Helvetica, sans-serif", "size": 11, "color": "#17232C"},
        margin={"l": 58, "r": 18, "t": 18, "b": 74},
        legend={
            "orientation": "h",
            "y": -0.22,
            "x": 0,
            "font": {"size": 11},
        },
        hovermode="closest",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, title=None)
    fig.update_yaxes(
        title="Distinct mapped variables",
        range=[0, 345],
        dtick=50,
        gridcolor="#E4E8EA",
        zerolinecolor="#9AA6AD",
    )
    return fig


def ssp_baseline_comparison_figure(metric: str) -> go.Figure:
    years = [2010, 2030, 2050, 2070, 2100]
    series = {
        "population": {
            "SSP1": [6.9, 8.2, 8.5, 8.0, 6.9],
            "SSP2": [6.9, 8.5, 9.2, 9.6, 9.0],
            "SSP3": [6.9, 8.7, 10.0, 11.2, 12.6],
            "SSP4": [6.9, 8.5, 9.3, 9.6, 9.3],
            "SSP5": [6.9, 8.3, 8.6, 8.3, 7.4],
        },
        "gdp": {
            "SSP1": [100, 165, 285, 450, 700],
            "SSP2": [100, 150, 240, 380, 600],
            "SSP3": [100, 135, 190, 270, 400],
            "SSP4": [100, 145, 225, 335, 500],
            "SSP5": [100, 175, 330, 610, 1000],
        },
        "fossil": {
            "SSP1": [100, 105, 102, 98, 90],
            "SSP2": [100, 125, 150, 170, 190],
            "SSP3": [100, 130, 165, 210, 250],
            "SSP4": [100, 115, 120, 115, 105],
            "SSP5": [100, 150, 220, 315, 420],
        },
    }
    titles = {
        "population": ("Population", "billion people"),
        "gdp": ("Global GDP", "index · 2010 = 100"),
        "fossil": ("Primary fossil energy", "index · 2010 = 100"),
    }
    if metric not in series:
        raise ValueError(f"Unknown SSP comparison metric: {metric}")
    fig = go.Figure()
    for ssp, values in series[metric].items():
        fig.add_trace(
            go.Scatter(
                x=years,
                y=values,
                mode="lines+markers",
                name=ssp,
                line={"width": 3, "color": SSP_COLORS[ssp]},
                marker={"size": 5},
                hovertemplate=f"{ssp}<br>%{{x}}: %{{y:.1f}}<extra></extra>",
            )
        )
    title_text, unit = titles[metric]
    fig.update_layout(
        title={"text": title_text, "x": 0, "font": {"size": 16}},
        template="plotly_white",
        margin={"l": 46, "r": 10, "t": 54, "b": 34},
        font={"family": "Arial", "size": 10, "color": "#17232C"},
        legend={
            "orientation": "h",
            "x": 0,
            "y": 1.06,
            "font": {"size": 8},
        },
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(
        showgrid=False,
        tickmode="array",
        tickvals=[2010, 2050, 2100],
        range=[2010, 2100],
    )
    fig.update_yaxes(
        title={"text": unit, "font": {"size": 9}},
        gridcolor="#E4E8EA",
        rangemode="tozero",
    )
    return fig


def rcp_forcing_trajectory_figure(compact: bool = False) -> go.Figure:
    years = [2000, 2020, 2040, 2060, 2080, 2100]
    pathways = {
        "RCP8.5": ([1.6, 2.2, 3.5, 5.1, 6.8, 8.5], "#8F3034"),
        "RCP6.0": ([1.6, 2.2, 2.8, 3.6, 4.8, 6.0], "#B66B2D"),
        "RCP4.5": ([1.6, 2.2, 2.9, 3.6, 4.2, 4.5], "#9A8928"),
        "RCP2.6": ([1.6, 2.2, 2.8, 2.6, 2.5, 2.6], "#008A82"),
        "SSP1-1.9": ([1.6, 2.2, 2.85, 2.55, 2.2, 1.9], "#006B8F"),
    }
    fig = go.Figure()
    for name, (values, color) in pathways.items():
        fig.add_trace(
            go.Scatter(
                x=years,
                y=values,
                mode="lines",
                name=name,
                line={
                    "width": 2.6 if compact else 4,
                    "color": color,
                    "dash": "dash" if name == "SSP1-1.9" else "solid",
                },
                hovertemplate=f"{name}<br>%{{x}}: %{{y:.1f}} W/m²<extra></extra>",
            )
        )
    if compact:
        fig.update_layout(
            template="plotly_white",
            margin={"l": 38, "r": 8, "t": 25, "b": 28},
            font={"family": "Arial", "size": 9, "color": "#17232C"},
            legend={
                "orientation": "h",
                "x": 0,
                "y": 1.16,
                "font": {"size": 8},
            },
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(
            showgrid=False,
            tickmode="array",
            tickvals=[2000, 2050, 2100],
            range=[2000, 2100],
        )
        fig.update_yaxes(
            title={"text": "W/m²", "font": {"size": 8}},
            range=[1, 9],
            dtick=2,
            gridcolor="#E4E8EA",
            zeroline=False,
        )
        return fig
    return _base_layout(
        fig,
        "Representative Concentration Pathways",
        "Radiative forcing (W/m²)",
    )


def rcp_gmst_trajectory_figure(compact: bool = False) -> go.Figure:
    years = [2000, 2020, 2040, 2060, 2080, 2100]
    pathways = {
        "RCP8.5": ([0.8, 1.2, 1.65, 2.25, 3.15, 4.3], "#8F3034"),
        "RCP6.0": ([0.8, 1.2, 1.55, 1.90, 2.35, 2.8], "#B66B2D"),
        "RCP4.5": ([0.8, 1.2, 1.55, 1.85, 2.15, 2.4], "#9A8928"),
        "RCP2.6": ([0.8, 1.2, 1.50, 1.65, 1.65, 1.6], "#008A82"),
        "SSP1-1.9": ([0.8, 1.2, 1.60, 1.55, 1.45, 1.4], "#006B8F"),
    }
    fig = go.Figure()
    for name, (values, color) in pathways.items():
        fig.add_trace(
            go.Scatter(
                x=years,
                y=values,
                mode="lines",
                name=name,
                line={
                    "width": 2.6 if compact else 4,
                    "color": color,
                    "dash": "dash" if name == "SSP1-1.9" else "solid",
                },
                hovertemplate=f"{name}<br>%{{x}}: %{{y:.2f}} °C<extra></extra>",
            )
        )
    if compact:
        fig.update_layout(
            template="plotly_white",
            margin={"l": 38, "r": 8, "t": 25, "b": 28},
            font={"family": "Arial", "size": 9, "color": "#17232C"},
            legend={"orientation": "h", "x": 0, "y": 1.16, "font": {"size": 8}},
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(
            showgrid=False, tickvals=[2000, 2050, 2100], range=[2000, 2100]
        )
        fig.update_yaxes(
            title={"text": "°C", "font": {"size": 8}},
            range=[0.5, 4.7],
            dtick=1,
            gridcolor="#E4E8EA",
            zeroline=False,
        )
        return fig
    return _base_layout(fig, "RCP temperature response", "GMST above 1850–1900 (°C)")


def cmip7_family_figure(compact: bool = False) -> go.Figure:
    years = list(range(2025, 2101, 5))
    anchors = {
        "H": [52, 76],
        "HL": [52, 0],
        "M": [52, 35],
        "ML": [52, 0],
        "L": [52, -2],
        "VL": [52, -5],
        "LN": [52, -18],
    }
    fig = go.Figure()
    for index, (name, (start, end)) in enumerate(anchors.items()):
        values = []
        for year in years:
            t = (year - 2025) / 75
            if name == "HL" and t < 0.45:
                value = start + 30 * (t / 0.45)
            elif name == "HL":
                value = 82 * (1 - (t - 0.45) / 0.55)
            elif name == "LN":
                value = (
                    start + (20 - start) * min(t / 0.45, 1)
                    if t < 0.45
                    else 20 + (end - 20) * ((t - 0.45) / 0.55)
                )
            else:
                curve = t ** (0.75 + index * 0.08)
                value = start + (end - start) * curve
            values.append(value)
        fig.add_trace(
            go.Scatter(
                x=years,
                y=values,
                mode="lines",
                name=name,
                line={"width": 2.4 if compact else 4, "color": SCENARIO_COLORS[name]},
                hovertemplate=f"{name}<br>%{{x}}: %{{y:.0f}} Gt CO₂-eq/yr<extra></extra>",
            )
        )
    fig.add_hline(y=0, line_dash="dot", line_color="#7D8A92")
    if compact:
        fig.update_layout(
            template="plotly_white",
            margin={"l": 38, "r": 8, "t": 25, "b": 28},
            font={"family": "Arial", "size": 9, "color": "#17232C"},
            legend={
                "orientation": "h",
                "x": 0,
                "y": 1.16,
                "font": {"size": 8},
            },
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(
            showgrid=False,
            tickmode="array",
            tickvals=[2025, 2050, 2075, 2100],
            range=[2025, 2100],
        )
        fig.update_yaxes(
            title={"text": "Gt CO₂-eq/yr", "font": {"size": 8}},
            range=[-22, 86],
            dtick=25,
            gridcolor="#E4E8EA",
            zerolinecolor="#7D8A92",
        )
        return fig
    fig = _base_layout(
        fig,
        "CMIP7 families are named for emission trends",
        "Illustrative GHG emissions (Gt CO₂-eq/yr)",
    )
    fig.add_annotation(
        x=2088, y=-14, text="net-negative", showarrow=False, font={"color": "#7656A8"}
    )
    return fig


def cmip7_gmst_trajectory_figure(compact: bool = False) -> go.Figure:
    years = [2025, 2040, 2060, 2080, 2100]
    trajectories = {
        "H": [1.45, 1.70, 2.25, 3.00, 3.80],
        "HL": [1.45, 1.70, 2.30, 2.85, 2.75],
        "M": [1.45, 1.68, 2.15, 2.55, 2.85],
        "ML": [1.45, 1.65, 2.03, 2.24, 2.35],
        "L": [1.45, 1.62, 1.88, 2.00, 2.00],
        "VL": [1.45, 1.58, 1.66, 1.60, 1.52],
        "LN": [1.45, 1.60, 1.78, 1.70, 1.55],
    }
    fig = go.Figure()
    for name, values in trajectories.items():
        fig.add_trace(
            go.Scatter(
                x=years,
                y=values,
                mode="lines",
                name=name,
                line={"width": 2.4 if compact else 4, "color": SCENARIO_COLORS[name]},
                hovertemplate=f"{name}<br>%{{x}}: %{{y:.2f}} °C<extra></extra>",
            )
        )
    fig.add_hline(y=1.5, line_dash="dot", line_color="#7D8A92")
    if compact:
        fig.update_layout(
            template="plotly_white",
            margin={"l": 38, "r": 8, "t": 25, "b": 28},
            font={"family": "Arial", "size": 9, "color": "#17232C"},
            legend={"orientation": "h", "x": 0, "y": 1.16, "font": {"size": 8}},
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(
            showgrid=False, tickvals=[2025, 2050, 2075, 2100], range=[2025, 2100]
        )
        fig.update_yaxes(
            title={"text": "°C", "font": {"size": 8}},
            range=[1.25, 4.1],
            dtick=0.5,
            gridcolor="#E4E8EA",
            zeroline=False,
        )
        return fig
    return _base_layout(fig, "CMIP7 temperature response", "GMST above 1850–1900 (°C)")


def sector_snapshot(sector: str, year: int = 2060, mode: str = "share") -> go.Figure:
    scenarios = CORE_SCENARIOS
    frame = sector_mix(sector, scenarios, year)
    fig = go.Figure()
    palette = [
        "#383D42",
        "#9A7B5B",
        "#D99614",
        "#5C8DCE",
        "#008A82",
        "#7656A8",
        "#74A65A",
        "#C44E52",
        "#A6A6A6",
    ]
    for technology in sorted(frame["technology"].unique()):
        data = frame[frame["technology"] == technology]
        values = {row.scenario: row for row in data.itertuples()}
        y = [
            (
                (values[s].share if mode == "share" else values[s].display_value)
                if s in values
                else 0
            )
            for s in scenarios
        ]
        fig.add_trace(
            go.Bar(
                x=scenarios,
                y=y,
                name=technology,
                marker_color=SECTOR_SNAPSHOT_COLORS.get(
                    technology,
                    palette[
                        sum(
                            (position + 1) * ord(character)
                            for position, character in enumerate(technology)
                        )
                        % len(palette)
                    ],
                ),
                uid=f"{sector}-{technology}",
                hovertemplate=f"{technology}: %{{y:.2f}}<extra></extra>",
            )
        )
    fig.update_layout(barmode="stack", uirevision=f"sector-snapshot-{sector}-{mode}")
    if mode == "share":
        fig.update_yaxes(tickformat=".0%", range=[0, 1], title="Technology share")
    title = {
        "Transport Passenger Cars": "Passenger-car technologies",
        "Transport Road Freight": "Road-freight technologies",
        "Steel": "Steel production routes",
        "Cement": "Cement kiln routes",
        "Carbon Dioxide Removal": "Reported removal portfolio",
        "Electricity": "Electricity generation mix",
    }.get(sector, sector)
    return _base_layout(
        fig, f"{title} · {year}", None if mode == "share" else "Source display unit"
    )


def sector_total_figure(sector: str) -> go.Figure:
    scenarios = CORE_SCENARIOS
    title = {
        "Electricity": "Total electricity output",
        "Transport Passenger Cars": "Total passenger-car activity",
        "Cement": "Total cement production",
        "Steel": "Total steel production",
    }.get(sector, f"{sector} · absolute pathway")
    return scenario_trajectory(sector, title, True, scenarios=scenarios)


def commodity_gwp_figure(sector: str, mode: str = "share") -> go.Figure:
    specs = {
        "Electricity": {
            "case": "electricity",
            "title": "GWP · 1 kWh CH electricity",
            "unit": "kg CO₂-eq / kWh",
            "absolute_title": "LCA-scaled GWP · World electricity",
            "activity_unit": "EJ/yr",
            "absolute_factor": 1 / 3.6,
        },
        "Transport Passenger Cars": {
            "case": "passenger_cars",
            "title": "GWP · 1 vehicle-km WEU",
            "unit": "kg CO₂-eq / vehicle-km",
            "absolute_title": "Absolute GWP unavailable · passenger cars",
            "activity_unit": "vehicle-km/yr",
            "absolute_factor": None,
        },
        "Cement": {
            "case": "cement",
            "title": "GWP · 1 kg CH cement",
            "unit": "kg CO₂-eq / kg cement",
            "absolute_title": "LCA-scaled GWP · World cement",
            "activity_unit": "Mt/yr",
            "absolute_factor": 1 / 1_000,
        },
        "Steel": {
            "case": "steel",
            "title": "GWP · 1 kg WEU steel",
            "unit": "kg CO₂-eq / kg steel",
            "absolute_title": "LCA-scaled GWP · World steel",
            "activity_unit": "Mt/yr",
            "absolute_factor": 1 / 1_000,
        },
    }
    spec = specs.get(sector, specs["Electricity"])
    absolute = mode == "absolute"
    frame = lcia_results()
    frame = frame.loc[
        frame["model"].eq("image")
        & frame["case"].eq(spec["case"])
        & frame["method_family"].eq("IPCC 2021")
        & frame["scenario"].isin(CORE_SCENARIOS)
    ].copy()
    fig = go.Figure()
    if absolute and spec["absolute_factor"] is None:
        fig.add_annotation(
            x=0.5,
            y=0.61,
            xref="paper",
            yref="paper",
            text="<b>Cannot calculate an absolute total from this extract</b>",
            showarrow=False,
            font={"size": 14, "color": "#713436"},
            bgcolor="#FBEFEF",
            bordercolor="#C44E52",
            borderwidth=1,
            borderpad=8,
        )
        fig.add_annotation(
            x=0.5,
            y=0.38,
            xref="paper",
            yref="paper",
            text=(
                "IMAGE activity: <b>model activity unit</b><br>"
                "LCIA functional unit: <b>vehicle-km</b><br>"
                "Add a documented vehicle-km or occupancy conversion before scaling."
            ),
            showarrow=False,
            align="center",
            font={"size": 10, "color": "#53646D"},
        )
        _base_layout(fig, spec["absolute_title"], None)
        fig.update_layout(
            title={
                "text": spec["absolute_title"],
                "x": 0,
                "xanchor": "left",
                "font": {"size": 18},
            },
            margin={"l": 24, "r": 14, "t": 58, "b": 24},
            showlegend=False,
            uirevision=f"commodity-gwp-{sector}-absolute",
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return fig

    if absolute:
        activity = context_series(sector, CORE_SCENARIOS)
        activity = activity.loc[
            activity["year"].isin(frame["year"].unique()),
            ["scenario", "year", "display_unit", "display_value"],
        ]
        reported_units = set(activity["display_unit"].dropna())
        if reported_units != {spec["activity_unit"]}:
            raise ValueError(
                f"Unexpected {sector} activity unit for absolute GWP: {reported_units}"
            )
        frame = frame.merge(
            activity,
            on=["scenario", "year"],
            how="inner",
            validate="one_to_one",
        )
        frame["plot_value"] = (
            frame["score"] * frame["display_value"] * spec["absolute_factor"]
        )
    else:
        frame["plot_value"] = frame["score"]

    for scenario in CORE_SCENARIOS:
        data = frame.loc[frame["scenario"].eq(scenario)].sort_values("year")
        narrative = NARRATIVES[scenario]
        if absolute:
            customdata = data[
                [
                    "score",
                    "display_value",
                    "display_unit",
                    "functional_unit",
                    "region",
                ]
            ]
            hovertemplate = (
                f"{scenario}<br>%{{x}}: %{{y:.3f}} Gt CO₂-eq/yr"
                f"<br>Intensity: %{{customdata[0]:.3f}} {spec['unit']}"
                "<br>Activity: %{customdata[1]:.2f} %{customdata[2]}"
                "<br>%{customdata[3]} · inventory %{customdata[4]}<extra></extra>"
            )
        else:
            customdata = data[["functional_unit", "region"]]
            hovertemplate = (
                f"{scenario}<br>%{{x}}: %{{y:.3f}} {spec['unit']}"
                "<br>%{customdata[0]} · %{customdata[1]}<extra></extra>"
            )
        fig.add_trace(
            go.Scatter(
                x=data["year"],
                y=data["plot_value"],
                mode="lines+markers",
                name=scenario,
                line={
                    "width": 3,
                    "color": narrative["color"],
                    "dash": narrative["line_dash"],
                },
                marker={
                    "size": 8,
                    "color": narrative["color"],
                    "line": {"width": 1.5, "color": "#FFFFFF"},
                },
                customdata=customdata,
                hovertemplate=hovertemplate,
            )
        )
    baseline = frame.loc[frame["year"].eq(2020), "plot_value"]
    if not baseline.empty:
        fig.add_annotation(
            x=2020,
            y=float(baseline.mean()),
            text="4 baselines overlap",
            showarrow=True,
            arrowhead=2,
            ax=34,
            ay=34,
            font={"size": 9, "color": "#53646D"},
            bgcolor="rgba(255,255,255,.88)",
            bordercolor="#D7E0E4",
            borderpad=3,
        )
    chart_title = spec["absolute_title"] if absolute else spec["title"]
    chart_unit = "Gt CO₂-eq / yr" if absolute else spec["unit"]
    _base_layout(fig, chart_title, chart_unit)
    fig.update_layout(
        title={"text": chart_title, "x": 0, "xanchor": "left", "font": {"size": 18}},
        margin={"l": 58, "r": 14, "t": 58, "b": 62},
        legend={
            "orientation": "h",
            "y": -0.22,
            "x": 0,
            "font": {"size": 10},
            "entrywidth": 74,
            "entrywidthmode": "pixels",
        },
        uirevision=f"commodity-gwp-{sector}-{mode}",
    )
    fig.update_xaxes(tickvals=[2020, 2040, 2060], range=[2017, 2063])
    fig.update_yaxes(zeroline=True, zerolinecolor="#7D8A92", tickformat=".2f")
    return fig


CAPSTONE_CASE_SPECS = {
    "electricity": {
        "label": "Electricity",
        "sector": "Electricity",
        "technology": "low-voltage electricity",
        "signal": "Generation mix",
    },
    "passenger_cars": {
        "label": "Passenger cars",
        "sector": "Transport Passenger Cars",
        "technology": "passenger-car transport market",
        "signal": "Powertrain mix",
    },
    "cement": {
        "label": "Cement",
        "sector": "Cement",
        "technology": "unspecified cement market",
        "signal": "Kiln-route mix",
    },
    "steel": {
        "label": "Steel",
        "sector": "Steel",
        "technology": "low-alloyed steel market",
        "signal": "Production-route mix",
    },
    "dac": {
        "label": "Carbon removal",
        "sector": "Carbon Dioxide Removal",
        "technology": "solvent-based DAC",
        "signal": "Reported removal portfolio",
    },
}

CAPSTONE_INDICATOR_SPECS = {
    "climate": {
        "label": "Climate",
        "method_family": "IPCC 2021",
        "category": None,
    },
    "metals": {
        "label": "Metals",
        "method_family": "EF v3.1",
        "category": "material resources: metals/minerals",
    },
    "land": {
        "label": "Land",
        "method_family": "EF v3.1",
        "category": "land use",
    },
    "water": {
        "label": "Water",
        "method_family": "EF v3.1",
        "category": "water use",
    },
}


def _capstone_result_subset(case_key: str, indicator_key: str):
    case = CAPSTONE_CASE_SPECS.get(case_key, CAPSTONE_CASE_SPECS["steel"])
    indicator = CAPSTONE_INDICATOR_SPECS.get(
        indicator_key, CAPSTONE_INDICATOR_SPECS["climate"]
    )
    frame = lcia_results()
    mask = (
        frame["model"].eq("image")
        & frame["case"].eq(case_key)
        & frame["technology"].eq(case["technology"])
        & frame["method_family"].eq(indicator["method_family"])
        & frame["scenario"].isin(CORE_SCENARIOS)
    )
    if indicator["category"]:
        mask &= frame["category"].eq(indicator["category"])
    return frame.loc[mask].copy()


def capstone_signal_figure(
    case_key: str, year: int, selected_scenario: str = "SSP2-VLHO"
) -> go.Figure:
    case = CAPSTONE_CASE_SPECS.get(case_key, CAPSTONE_CASE_SPECS["steel"])
    if selected_scenario not in CORE_SCENARIOS:
        selected_scenario = "SSP2-VLHO"
    frame = sector_mix(case["sector"], CORE_SCENARIOS, year)
    fig = go.Figure()
    palette = [
        "#383D42",
        "#9A7B5B",
        "#D99614",
        "#5C8DCE",
        "#008A82",
        "#7656A8",
        "#74A65A",
        "#C44E52",
        "#A6A6A6",
    ]
    technologies = sorted(frame["technology"].unique()) if not frame.empty else []
    scenario_opacity = [
        1 if scenario == selected_scenario else 0.3 for scenario in CORE_SCENARIOS
    ]
    for index, technology in enumerate(technologies):
        data = frame.loc[frame["technology"].eq(technology)]
        values = dict(zip(data["scenario"], data["share"]))
        color = SECTOR_SNAPSHOT_COLORS.get(technology, palette[index % len(palette)])
        fig.add_trace(
            go.Bar(
                x=CORE_SCENARIOS,
                y=[values.get(scenario, 0) for scenario in CORE_SCENARIOS],
                name=technology,
                marker={"color": color, "opacity": scenario_opacity},
                hovertemplate=f"{technology}<br>%{{x}}: %{{y:.1%}}<extra></extra>",
            )
        )
    if frame.empty:
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            text="No mix reported for this year",
            showarrow=False,
            font={"size": 14, "color": "#5B6A74"},
        )
    fig.update_layout(
        title={
            "text": f"IAM signal · {case['signal']} · {year}",
            "x": 0,
            "xanchor": "left",
            "font": {"size": 16},
        },
        template="plotly_white",
        barmode="stack",
        font={"family": "Arial, Helvetica, sans-serif", "size": 10, "color": "#17232C"},
        margin={"l": 44, "r": 8, "t": 50, "b": 82},
        legend={
            "orientation": "h",
            "x": 0,
            "y": -0.24,
            "font": {"size": 7},
            "entrywidth": 70,
            "entrywidthmode": "pixels",
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        uirevision=f"capstone-signal-{case_key}-{year}-{selected_scenario}",
    )
    fig.add_annotation(
        x=selected_scenario,
        y=0.97,
        text=f"TRACE · {selected_scenario}",
        showarrow=False,
        yanchor="top",
        font={"size": 8, "color": "#FFFFFF"},
        bgcolor=NARRATIVES[selected_scenario]["color"],
        borderpad=3,
    )
    fig.update_xaxes(showgrid=False, tickangle=-20)
    fig.update_yaxes(
        title="Share of reported mix",
        tickformat=".0%",
        range=[0, 1],
        gridcolor="#E4E8EA",
    )
    return fig


def capstone_lcia_trajectory_figure(
    case_key: str,
    indicator_key: str,
    selected_scenario: str = "SSP2-VLHO",
    selected_year: int = 2060,
) -> go.Figure:
    case = CAPSTONE_CASE_SPECS.get(case_key, CAPSTONE_CASE_SPECS["steel"])
    indicator = CAPSTONE_INDICATOR_SPECS.get(
        indicator_key, CAPSTONE_INDICATOR_SPECS["climate"]
    )
    frame = _capstone_result_subset(case_key, indicator_key)
    if selected_scenario not in CORE_SCENARIOS:
        selected_scenario = "SSP2-VLHO"
    if selected_year not in {2020, 2040, 2060}:
        selected_year = 2060
    unit = str(frame["unit"].iloc[0]) if not frame.empty else "LCIA unit"
    fig = go.Figure()
    trace_order = [
        scenario for scenario in CORE_SCENARIOS if scenario != selected_scenario
    ] + [selected_scenario]
    for scenario in trace_order:
        data = frame.loc[frame["scenario"].eq(scenario)].sort_values("year")
        narrative = NARRATIVES[scenario]
        selected = scenario == selected_scenario
        fig.add_trace(
            go.Scatter(
                x=data["year"],
                y=data["score"],
                mode="lines+markers",
                name=scenario,
                legendrank=CORE_SCENARIOS.index(scenario),
                opacity=1 if selected else 0.24,
                line={
                    "width": 4 if selected else 1.5,
                    "color": narrative["color"],
                    "dash": narrative["line_dash"],
                },
                marker={
                    "size": [
                        13 if selected and int(year) == selected_year else 6
                        for year in data["year"]
                    ],
                    "color": narrative["color"],
                    "line": {
                        "width": 2 if selected else 1,
                        "color": "#FFFFFF",
                    },
                },
                customdata=data[["functional_unit", "region"]],
                hovertemplate=(
                    f"{scenario}<br>%{{x}}: %{{y:.4g}} {unit}"
                    "<br>%{customdata[0]} · %{customdata[1]}<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        title={
            "text": f"Inventory result · {indicator['label']}",
            "x": 0,
            "xanchor": "left",
            "font": {"size": 16},
        },
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 9, "color": "#17232C"},
        margin={"l": 58, "r": 8, "t": 50, "b": 68},
        legend={
            "orientation": "h",
            "x": 0,
            "y": -0.22,
            "font": {"size": 8},
            "entrywidth": 66,
            "entrywidthmode": "pixels",
        },
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        uirevision=(
            f"capstone-lcia-{case_key}-{indicator_key}-"
            f"{selected_scenario}-{selected_year}"
        ),
    )
    fig.add_vline(
        x=selected_year,
        line_width=1.5,
        line_dash="dot",
        line_color=NARRATIVES[selected_scenario]["color"],
    )
    fig.update_xaxes(tickvals=[2020, 2040, 2060], range=[2017, 2063], showgrid=False)
    fig.update_yaxes(title=unit, gridcolor="#E4E8EA", zerolinecolor="#80909A")
    return fig


def _short_contributor_name(name: str) -> str:
    replacements = [
        ("market for electricity, low voltage", "Low-voltage electricity"),
        ("market group for electricity, low voltage", "Low-voltage electricity market"),
        ("three and five layered board production", "Board-production wood chips"),
        ("supply of forest residue", "Forest-residue supply"),
        ("carbon dioxide, captured at", "Captured CO₂ at"),
        ("passenger car production", "Passenger-car production"),
        (
            "pig iron production, top gas recycling-blast furnace",
            "Top-gas-recycling pig iron",
        ),
        (
            "pig iron production, blast furnace, with top gas recycling",
            "BF pig iron + top-gas recycling",
        ),
        ("steel production, electric, low-alloyed", "Electric low-alloyed steel"),
        ("quicklime production, in pieces, loose", "Quicklime production"),
    ]
    lower = name.lower()
    for token, label in replacements:
        if token in lower:
            return label
    return name if len(name) <= 32 else f"{name[:29]}…"


def _capstone_contribution_components(
    case_key: str,
    year: int,
    indicator_key: str,
    selected_scenario: str = "SSP2-VLHO",
    limit: int = 5,
):
    case = CAPSTONE_CASE_SPECS.get(case_key, CAPSTONE_CASE_SPECS["steel"])
    indicator = CAPSTONE_INDICATOR_SPECS.get(
        indicator_key, CAPSTONE_INDICATOR_SPECS["climate"]
    )
    scores = _capstone_result_subset(case_key, indicator_key)
    if selected_scenario not in CORE_SCENARIOS:
        selected_scenario = "SSP2-VLHO"
    score_row = scores.loc[
        scores["scenario"].eq(selected_scenario) & scores["year"].eq(year)
    ]
    contributions = lcia_contributions()
    mask = (
        contributions["model"].eq("image")
        & contributions["case"].eq(case_key)
        & contributions["technology"].eq(case["technology"])
        & contributions["scenario"].eq(selected_scenario)
        & contributions["year"].eq(year)
        & contributions["method_family"].eq(indicator["method_family"])
    )
    if indicator["category"]:
        mask &= contributions["category"].eq(indicator["category"])
    data = contributions.loc[mask].copy()
    if data.empty or score_row.empty:
        return [], [], "LCIA unit", 0.0
    data = (
        data.groupby("contributor_name", as_index=False, observed=True)["contribution"]
        .sum()
        .assign(magnitude=lambda frame: frame["contribution"].abs())
        .sort_values("magnitude", ascending=False)
        .head(limit)
    )
    values = data["contribution"].astype(float).tolist()
    labels = [_short_contributor_name(name) for name in data["contributor_name"]]
    score = float(score_row["score"].iloc[0])
    residual = score - sum(values)
    labels.append("All other activities + remaining difference")
    values.append(residual)
    return labels, values, str(score_row["unit"].iloc[0]), score


def capstone_contribution_figure(
    case_key: str,
    year: int,
    indicator_key: str,
    selected_scenario: str = "SSP2-VLHO",
) -> go.Figure:
    labels, values, unit, score = _capstone_contribution_components(
        case_key, year, indicator_key, selected_scenario
    )
    fig = go.Figure()
    if labels:
        fig.add_trace(
            go.Bar(
                x=values,
                y=labels,
                orientation="h",
                marker_color=[
                    "#008A82" if value < 0 else "#C44E52" for value in values
                ],
                text=[f"{value:+.2g}" for value in values],
                textposition="outside",
                cliponaxis=False,
                hovertemplate=f"%{{y}}<br>%{{x:+.4g}} {unit}<extra></extra>",
            )
        )
        fig.add_vline(x=0, line_color="#80909A", line_width=1)
    else:
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            text="No contribution result",
            showarrow=False,
        )
    fig.update_layout(
        title={
            "text": f"Selected result · {selected_scenario} · {year} · total {score:.3g}",
            "x": 0,
            "xanchor": "left",
            "font": {"size": 16},
        },
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 9, "color": "#17232C"},
        margin={"l": 150, "r": 55, "t": 50, "b": 45},
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        uirevision=(
            f"capstone-contribution-{case_key}-{selected_scenario}-"
            f"{year}-{indicator_key}"
        ),
    )
    fig.update_xaxes(title=unit, gridcolor="#E4E8EA", zerolinecolor="#80909A")
    fig.update_yaxes(autorange="reversed", tickfont={"size": 8})
    return fig


def steel_causal_chain_figure() -> go.Figure:
    years = [2020, 2040, 2060]
    mix_by_year = {
        year: sector_mix("Steel", ["SSP2-VLHO"], year, model="image", region="WEU")
        for year in years
    }
    scores = _capstone_result_subset("steel", "climate")
    labels, values, unit, _ = _capstone_contribution_components(
        "steel", 2060, "climate", limit=5
    )
    fig = make_subplots(
        rows=1,
        cols=3,
        column_widths=[0.33, 0.31, 0.36],
        horizontal_spacing=0.10,
        subplot_titles=(
            "<b>1 · IMAGE WEU route mix · SSP2-VLHO</b>",
            "<b>2 · <i>Premise</i> result · 1 kg WEU steel</b>",
            "<b>3 · WEU 2060 contributors · SSP2-VLHO</b>",
        ),
    )
    for group in STEEL_WEU_ROUTE_ORDER:
        values_by_year = []
        for year in years:
            data = mix_by_year[year]
            group_rows = data.loc[data["technology"].eq(group), "share"]
            values_by_year.append(
                float(group_rows.iloc[0]) if not group_rows.empty else 0
            )
        if not any(values_by_year):
            continue
        fig.add_trace(
            go.Bar(
                x=[str(year) for year in years],
                y=values_by_year,
                name=group,
                legendgroup=f"route-{group}",
                marker_color=SECTOR_SNAPSHOT_COLORS[group],
                hovertemplate=f"{group}<br>%{{x}}: %{{y:.1%}}<extra></extra>",
            ),
            row=1,
            col=1,
        )
    for scenario in CORE_SCENARIOS:
        data = scores.loc[scores["scenario"].eq(scenario)].sort_values("year")
        fig.add_trace(
            go.Scatter(
                x=data["year"],
                y=data["score"],
                mode="lines+markers",
                name=scenario,
                legend="legend2",
                legendgroup=f"scenario-{scenario}",
                line={"width": 3, "color": NARRATIVES[scenario]["color"]},
                marker={"size": 6},
                hovertemplate=f"{scenario}<br>%{{x}}: %{{y:.3f}} kg CO₂-eq/kg<extra></extra>",
            ),
            row=1,
            col=2,
        )
    fig.add_trace(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=["#008A82" if value < 0 else "#C44E52" for value in values],
            text=[f"{value:+.2f}" for value in values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"%{{y}}<br>%{{x:+.4f}} {unit}<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=3,
    )
    fig.update_layout(
        template="plotly_white",
        barmode="stack",
        font={"family": "Arial, Helvetica, sans-serif", "size": 10, "color": "#17232C"},
        margin={"l": 52, "r": 30, "t": 58, "b": 82},
        legend={
            "orientation": "h",
            "x": 0,
            "y": -0.23,
            "font": {"size": 9},
            "entrywidth": 60,
            "entrywidthmode": "pixels",
        },
        legend2={
            "orientation": "h",
            "x": 0.45,
            "y": -0.23,
            "font": {"size": 9},
            "entrywidth": 50,
            "entrywidthmode": "pixels",
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(title="Route share", tickformat=".0%", range=[0, 1], row=1, col=1)
    fig.update_yaxes(title="kg CO₂-eq/kg steel", gridcolor="#E4E8EA", row=1, col=2)
    fig.update_yaxes(autorange="reversed", tickfont={"size": 10}, row=1, col=3)
    fig.update_xaxes(showgrid=False, row=1, col=1)
    fig.update_xaxes(tickvals=years, range=[2017, 2063], showgrid=False, row=1, col=2)
    fig.update_xaxes(
        title=unit, gridcolor="#E4E8EA", zerolinecolor="#80909A", row=1, col=3
    )
    fig.add_vline(x=0, line_color="#80909A", line_width=1, row=1, col=3)
    return fig


def cumulative_cdr_figure() -> go.Figure:
    scenarios = ["SSP1-L", "SSP2-VLHO", "SSP2-M"]
    frame = context_series("Carbon Dioxide Removal", scenarios)
    fig = go.Figure()
    for scenario in scenarios:
        data = frame[frame["scenario"] == scenario].sort_values("year")
        if data.empty:
            continue
        years = data["year"].to_numpy()
        rates = data["display_value"].to_numpy()
        cumulative = [0.0]
        for i in range(1, len(years)):
            cumulative.append(
                cumulative[-1]
                + 0.5 * (rates[i - 1] + rates[i]) * (years[i] - years[i - 1]) / 1_000
            )
        fig.add_trace(
            go.Scatter(
                x=years,
                y=cumulative,
                mode="lines",
                name=scenario,
                line={
                    "width": 4,
                    "color": NARRATIVES[scenario]["color"],
                    "dash": NARRATIVES[scenario]["line_dash"],
                },
            )
        )
    return _base_layout(fig, "Cumulative reported CDR", "Gt CO₂")


def _iam_europe_geography_figure(
    mapping: dict, region_order: list[str], colors: list[str]
) -> go.Figure:
    locations: list[str] = []
    values: list[float] = []
    region_labels: list[str] = []
    for index, region in enumerate(region_order):
        region_locations = mapping["iso3_regions"][region]
        locations.extend(region_locations)
        values.extend([index + 0.5] * len(region_locations))
        region_labels.extend([region] * len(region_locations))

    color_scale: list[list[float | str]] = []
    count = len(colors)
    for index, color in enumerate(colors):
        color_scale.extend([[index / count, color], [(index + 1) / count, color]])

    fig = go.Figure()
    fig.add_trace(
        go.Choropleth(
            locations=locations,
            z=values,
            customdata=region_labels,
            locationmode="ISO-3",
            name=mapping["model"],
            showlegend=False,
            showscale=True,
            colorscale=color_scale,
            zmin=0,
            zmax=count,
            colorbar={
                "tickmode": "array",
                "tickvals": [index + 0.5 for index in range(count)],
                "ticktext": region_order,
                "tickfont": {"size": 8},
                "thickness": 10,
                "len": 0.82,
                "x": 1.0,
                "title": {"text": "IAM<br>region", "font": {"size": 8}},
            },
            marker_line_color="#FFFFFF",
            marker_line_width=0.7,
            hovertemplate="%{location} · %{customdata}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Choropleth(
            locations=["CHE"],
            z=[1],
            locationmode="ISO-3",
            name=f"CH → {mapping['iam_region']}",
            showlegend=False,
            showscale=False,
            colorscale=[[0, "#003B57"], [1, "#003B57"]],
            marker_line_color="#FFFFFF",
            marker_line_width=1.4,
            hovertemplate=(
                f"Switzerland · CH inventory location → {mapping['iam_region']}"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        geo={
            "scope": "europe",
            "projection_type": "natural earth",
            "showframe": False,
            "showcoastlines": False,
            "showland": True,
            "landcolor": "#EEF2F4",
            "showcountries": True,
            "countrycolor": "#FFFFFF",
        },
        margin={"l": 0, "r": 42, "t": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def image_geography_figure() -> go.Figure:
    return _iam_europe_geography_figure(
        image_region_mapping(),
        ["WEU", "CEU", "TUR", "UKR", "RUS"],
        ["#5C8DCE", "#76B7B2", "#D99614", "#C44E52", "#7656A8"],
    )


def iam_world_geography_figure(model: str = "image") -> go.Figure:
    topologies = iam_region_topologies()
    if model not in topologies:
        model = "image"
    mapping = topologies[model]
    regions = list(mapping["regions"])
    colors = IAM_MAP_COLORS[: len(regions)]
    locations: list[str] = []
    values: list[float] = []
    region_labels: list[str] = []
    for index, region in enumerate(regions):
        countries = mapping["regions"][region]
        locations.extend(countries)
        values.extend([index + 0.5] * len(countries))
        region_labels.extend([region] * len(countries))

    color_scale: list[list[float | str]] = []
    count = max(1, len(colors))
    for index, color in enumerate(colors):
        color_scale.extend([[index / count, color], [(index + 1) / count, color]])

    figure = go.Figure(
        go.Choropleth(
            locations=locations,
            z=values,
            customdata=region_labels,
            locationmode="ISO-3",
            colorscale=color_scale,
            zmin=0,
            zmax=count,
            showscale=False,
            marker_line_color="rgba(255,255,255,.72)",
            marker_line_width=0.45,
            hovertemplate=(
                f"{mapping['model']}<br>%{{location}} → %{{customdata}}"
                "<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        geo={
            "projection_type": "natural earth",
            "showframe": False,
            "showcoastlines": True,
            "coastlinecolor": "#D2DADF",
            "showland": True,
            "landcolor": "#E8EDF0",
            "showocean": True,
            "oceancolor": "#F4F8FA",
            "showcountries": True,
            "countrycolor": "#FFFFFF",
            "bgcolor": "rgba(0,0,0,0)",
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        uirevision="iam-spatial-resolution",
    )
    return figure


def remind_eu_geography_figure() -> go.Figure:
    return _iam_europe_geography_figure(
        remind_eu_region_mapping(),
        ["DEU", "ECE", "ECS", "ENC", "ESC", "ESW", "EWN", "FRA", "NEN", "NES", "UKI"],
        [
            "#005A7A",
            "#4E79A7",
            "#76B7B2",
            "#59A14F",
            "#EDC948",
            "#F28E2B",
            "#E15759",
            "#B07AA1",
            "#7656A8",
            "#FF9DA7",
            "#9C755F",
        ],
    )


def controlled_comparison_figure() -> go.Figure:
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Hold MESSAGE + SSP2; vary climate objective",
            "Hold SSP2 + low (~2°C); vary IAM",
        ),
        horizontal_spacing=0.11,
    )
    policy_specs = [
        ("SSP2-VL", "#7656A8", "longdash"),
        ("SSP2-L", "#008A82", "solid"),
        ("SSP2-ML", "#3366A3", "dot"),
        ("SSP2-M", "#D99614", "dash"),
    ]
    for scenario, color, dash in policy_specs:
        data = context_series("Carbon Dioxide emissions", [scenario], model="message")
        warming = context_series("GMST increase", [scenario], model="message")
        peak_warming = float(warming["display_value"].max())
        fig.add_trace(
            go.Scatter(
                x=data["year"],
                y=data["display_value"],
                mode="lines",
                name=scenario,
                legend="legend",
                legendgroup=f"policy-{scenario}",
                showlegend=True,
                line={"width": 4, "color": color, "dash": dash},
                hovertemplate=(
                    f"MESSAGE · {scenario}<br>Peak GMST: {peak_warming:.2f}°C"
                    "<br>%{x}: %{y:.1f} Gt CO₂/yr<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )

    model_specs = [
        ("IMAGE", "image", "SSP2-L", "#008A82", "solid"),
        ("MESSAGE", "message", "SSP2-L", "#3366A3", "dash"),
        ("REMIND", "remind", "SSP2-PkBudg1000", "#C44E52", "dot"),
    ]
    for label, model, scenario, color, dash in model_specs:
        data = context_series("Carbon Dioxide emissions", [scenario], model=model)
        warming = context_series("GMST increase", [scenario], model=model)
        peak_warming = float(warming["display_value"].max())
        fig.add_trace(
            go.Scatter(
                x=data["year"],
                y=data["display_value"],
                mode="lines",
                name=label,
                legend="legend2",
                legendgroup=f"model-{model}",
                showlegend=True,
                line={"width": 4, "color": color, "dash": dash},
                hovertemplate=(
                    f"{label} · {scenario}<br>Peak GMST: {peak_warming:.2f}°C"
                    "<br>%{x}: %{y:.1f} Gt CO₂/yr<extra></extra>"
                ),
            ),
            row=1,
            col=2,
        )
    fig.update_xaxes(showgrid=False, range=[2005, 2100])
    fig.update_yaxes(title_text="Gt CO₂/yr", gridcolor="#E4E8EA", row=1, col=1)
    fig.update_yaxes(gridcolor="#E4E8EA", row=1, col=2)
    fig.add_hline(y=0, line_color="#80909A", line_width=1)
    fig.add_vline(x=2020, line_color="#80909A", line_width=1, line_dash="dot")
    fig.update_layout(
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 14},
        margin={"l": 65, "r": 25, "t": 55, "b": 70},
        legend={
            "orientation": "h",
            "x": 0,
            "y": -0.18,
            "font": {"size": 10},
            "title": {"text": "Climate objective"},
        },
        legend2={
            "orientation": "h",
            "x": 0.55,
            "y": -0.18,
            "font": {"size": 10},
            "title": {"text": "IAM implementation"},
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def cdr_overshoot_summary_figure() -> go.Figure:
    scenarios = CORE_SCENARIOS
    annual = context_series("Carbon Dioxide Removal", scenarios)
    gmst = context_series("GMST increase", scenarios)
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "1 · How fast must removals scale?",
            "2 · How much is deployed by 2100?",
            "3 · Does warming fall after its peak?",
        ),
        horizontal_spacing=0.09,
    )
    cumulative_totals: dict[str, float | None] = {}
    for scenario in scenarios:
        narrative = NARRATIVES[scenario]
        data = annual[annual["scenario"].eq(scenario)].sort_values("year")
        if not data.empty:
            fig.add_trace(
                go.Scatter(
                    x=data["year"],
                    y=data["display_value"] / 1_000,
                    mode="lines+markers",
                    name=scenario,
                    legendgroup=scenario,
                    showlegend=True,
                    line={
                        "width": 3.5,
                        "color": narrative["color"],
                        "dash": narrative["line_dash"],
                    },
                    marker={"size": 5, "color": narrative["color"]},
                    hovertemplate=(
                        f"{scenario}<br>%{{x}}: %{{y:.2f}} Gt CO₂/yr" "<extra></extra>"
                    ),
                ),
                row=1,
                col=1,
            )
            years = [2020, *data["year"].astype(int).tolist()]
            values = [0.0, *data["display_value"].astype(float).tolist()]
            cumulative = 0.0
            for index in range(1, len(years)):
                cumulative += (
                    0.5
                    * (values[index - 1] + values[index])
                    * (years[index] - years[index - 1])
                    / 1_000
                )
            cumulative_totals[scenario] = cumulative
        else:
            cumulative_totals[scenario] = None

    bar_values = [
        cumulative_totals[scenario] if cumulative_totals[scenario] is not None else 0
        for scenario in scenarios
    ]
    bar_labels = [
        (
            "not reported"
            if cumulative_totals[scenario] is None
            else (
                "<0.1"
                if cumulative_totals[scenario] < 0.1
                else f"{cumulative_totals[scenario]:.0f}"
            )
        )
        for scenario in scenarios
    ]
    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=bar_values,
            marker={
                "color": [
                    (
                        NARRATIVES[scenario]["color"]
                        if cumulative_totals[scenario] is not None
                        else "rgba(255,255,255,0)"
                    )
                    for scenario in scenarios
                ],
                "line": {
                    "color": [
                        (
                            NARRATIVES[scenario]["color"]
                            if cumulative_totals[scenario] is not None
                            else "#9AA6AD"
                        )
                        for scenario in scenarios
                    ],
                    "width": [1, 1, 1, 2],
                },
            },
            text=bar_labels,
            textposition="outside",
            cliponaxis=False,
            showlegend=False,
            hovertemplate="%{x}<br>%{text} Gt CO₂ through 2100<extra></extra>",
        ),
        row=1,
        col=2,
    )

    for scenario in scenarios:
        narrative = NARRATIVES[scenario]
        warming = gmst[gmst["scenario"].eq(scenario)].sort_values("year")
        peak_row = warming.loc[warming["display_value"].idxmax()]
        end_row = warming.iloc[-1]
        peak_value = float(peak_row["display_value"])
        end_value = float(end_row["display_value"])
        if int(peak_row["year"]) == 2100:
            x_values = [end_value]
            texts = [f"{end_value:.2f} · rising"]
            symbols = ["circle"]
        else:
            x_values = [peak_value, end_value]
            texts = [f"peak {peak_value:.2f}", f"2100 {end_value:.2f}"]
            symbols = ["circle-open", "circle"]
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=[scenario] * len(x_values),
                mode="lines+markers+text",
                text=texts,
                textposition=["top center", "bottom center"][: len(x_values)],
                textfont={"size": 10, "color": narrative["color"]},
                marker={
                    "size": 10,
                    "symbol": symbols,
                    "color": narrative["color"],
                    "line": {"width": 2, "color": narrative["color"]},
                },
                line={"width": 3, "color": narrative["color"]},
                name=scenario,
                legendgroup=scenario,
                showlegend=False,
                hovertemplate=(
                    f"{scenario}<br>%{{text}} °C above 1850–1900" "<extra></extra>"
                ),
            ),
            row=1,
            col=3,
        )

    fig.add_annotation(
        x=2040,
        y=11.8,
        text="SSP3-H: no reported CDR row",
        showarrow=False,
        bgcolor="#F6E7E8",
        bordercolor="#D9A5A8",
        borderpad=4,
        font={"size": 10, "color": "#713436"},
        row=1,
        col=1,
    )
    fig.add_vline(x=2.0, line_color="#80909A", line_dash="dot", row=1, col=3)
    fig.update_xaxes(showgrid=False, range=[2020, 2100], row=1, col=1)
    fig.update_xaxes(showgrid=False, tickangle=-20, row=1, col=2)
    fig.update_xaxes(
        title_text="°C above 1850–1900",
        range=[1.4, 3.75],
        gridcolor="#E4E8EA",
        row=1,
        col=3,
    )
    fig.update_yaxes(title_text="Gt CO₂/yr", gridcolor="#E4E8EA", row=1, col=1)
    fig.update_yaxes(title_text="Gt CO₂", gridcolor="#E4E8EA", row=1, col=2)
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=list(reversed(scenarios)),
        showgrid=False,
        row=1,
        col=3,
    )
    fig.update_layout(
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 11},
        margin={"l": 58, "r": 30, "t": 58, "b": 68},
        legend={"orientation": "h", "x": 0, "y": -0.18},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def lcia_evidence_figure() -> go.Figure:
    scenarios = CORE_SCENARIOS
    results = lcia_results()
    scores = results[
        results["case"].eq("electricity")
        & results["year"].eq(2060)
        & results["method_family"].eq("IPCC 2021")
    ].set_index("scenario")["score"]
    pathway = pathways()
    activity = (
        pathway[
            pathway["model"].eq("image")
            & pathway["scenario"].isin(scenarios)
            & pathway["sector"].eq("Electricity")
            & pathway["region"].isin(["WEU", "CEU"])
            & pathway["year"].eq(2060)
        ]
        .groupby("scenario", observed=True)["display_value"]
        .sum()
    )
    contributions = lcia_contributions()
    contribution_data = contributions[
        contributions["case"].eq("electricity")
        & contributions["scenario"].eq("SSP2-VLHO")
        & contributions["year"].eq(2060)
        & contributions["method_family"].eq("IPCC 2021")
    ].copy()
    contribution_data = contribution_data.reindex(
        contribution_data["contribution"].abs().sort_values(ascending=False).index
    ).head(5)
    labels = []
    for name in contribution_data["contributor_name"]:
        if "layered board" in name:
            labels.append("Board-production wood chips")
        elif "forest residue" in name:
            labels.append("Forest-residue supply")
        elif "natural gas-fired" in name:
            labels.append("Gas CHP + CCS")
        elif "softwood forestry" in name:
            labels.append("Managed softwood forestry")
        elif "wood-fired" in name:
            labels.append("Wood CHP + CCS")
        else:
            labels.append(name[:30])
    contribution_values = contribution_data["contribution"].tolist()
    residual = float(scores["SSP2-VLHO"] - sum(contribution_values))
    labels.append("All other activities + remaining difference")
    contribution_values.append(residual)
    colors = [NARRATIVES[scenario]["color"] for scenario in scenarios]
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "1 kWh CH low voltage · 2060",
            "WEU + CEU generation · 2060",
            "Main contributors to the SSP2-VLHO result",
        ),
        horizontal_spacing=0.11,
    )
    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=[scores[scenario] for scenario in scenarios],
            marker_color=colors,
            text=[f"{scores[scenario]:+.3f}" for scenario in scenarios],
            textposition="outside",
            hovertemplate="%{x}<br>%{y:.3f} kg CO₂-eq/kWh<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=[activity[scenario] for scenario in scenarios],
            marker_color=colors,
            text=[f"{activity[scenario]:.1f}" for scenario in scenarios],
            textposition="outside",
            hovertemplate="%{x}<br>%{y:.1f} EJ/yr<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Bar(
            x=contribution_values,
            y=labels,
            orientation="h",
            marker_color=[
                "#008A82" if value < 0 else "#C44E52" for value in contribution_values
            ],
            text=[f"{value:+.3f}" for value in contribution_values],
            textposition="outside",
            hovertemplate="%{y}<br>%{x:+.4f} kg CO₂-eq/kWh<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=3,
    )
    fig.add_hline(y=0, line_color="#80909A", line_width=1, row=1, col=1)
    fig.add_vline(x=0, line_color="#80909A", line_width=1, row=1, col=3)
    fig.update_xaxes(tickangle=-22, row=1, col=1)
    fig.update_xaxes(tickangle=-22, row=1, col=2)
    fig.update_xaxes(title_text="kg CO₂-eq/kWh", gridcolor="#E4E8EA", row=1, col=3)
    fig.update_yaxes(title_text="kg CO₂-eq/kWh", gridcolor="#E4E8EA", row=1, col=1)
    fig.update_yaxes(title_text="EJ/yr", gridcolor="#E4E8EA", row=1, col=2)
    fig.update_yaxes(autorange="reversed", tickfont={"size": 10}, row=1, col=3)
    fig.update_layout(
        template="plotly_white",
        font={"family": "Arial, Helvetica, sans-serif", "size": 12},
        margin={"l": 65, "r": 40, "t": 60, "b": 65},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def lcia_comparison_figure() -> go.Figure:
    frame = lcia_results()
    if frame.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Run the documented <i>Premise</i>/Brightway workflow and add the checked results",
            x=0.5,
            y=0.55,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={"size": 22, "color": "#5B6A74"},
            align="center",
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return _base_layout(fig, "Scenario-specific LCIA results", None)
    value_col = "score" if "score" in frame.columns else "value"
    indicator_col = "indicator" if "indicator" in frame.columns else "category"
    figure_data = frame.copy()
    figure_data["indicator_short"] = figure_data["category"].replace(
        {
            "climate change": "Climate",
            "material resources: metals/minerals": "Metals/minerals",
            "land use": "Land",
            "water use": "Water",
        }
    )
    references = figure_data[
        (figure_data["scenario"] == "SSP2-M") & (figure_data["year"] == 2040)
    ][["case", "technology", indicator_col, value_col]].rename(
        columns={value_col: "reference"}
    )
    figure_data = figure_data.merge(
        references, on=["case", "technology", indicator_col], how="left"
    )
    figure_data["relative"] = figure_data[value_col] / figure_data["reference"]
    figure_data["label_full"] = (
        figure_data["scenario"].astype(str) + " · " + figure_data["year"].astype(str)
    )
    figure_data["label"] = (
        figure_data["scenario"].astype(str)
        + "·"
        + figure_data["year"].astype(str).str[-2:]
    )
    panel_specs = [
        ("electricity", None, "ELECTRICITY"),
        ("steel", None, "STEEL"),
        ("dac", "sorbent-based DAC", "DAC · SORBENT"),
        ("dac", "solvent-based DAC", "DAC · SOLVENT"),
    ]
    panel_specs = [spec for spec in panel_specs if spec[0] in set(figure_data["case"])]
    fig = make_subplots(
        rows=1,
        cols=len(panel_specs),
        subplot_titles=tuple(title for _, _, title in panel_specs),
    )
    colors = {
        "Climate": "#008A82",
        "Metals/minerals": "#7656A8",
        "Land": "#74A65A",
        "Water": "#5C8DCE",
    }
    for col, (case, technology, _) in enumerate(panel_specs, start=1):
        case_data = figure_data[figure_data["case"] == case].copy()
        if technology:
            case_data = case_data[case_data["technology"] == technology]
        for indicator in ["Climate", "Metals/minerals", "Land", "Water"]:
            data = case_data[case_data["indicator_short"] == indicator]
            fig.add_trace(
                go.Bar(
                    x=data["label"],
                    y=data["relative"],
                    name=indicator,
                    legendgroup=indicator,
                    showlegend=col == 1,
                    marker_color=colors[indicator],
                    customdata=data["label_full"],
                    hovertemplate=f"{indicator}<br>%{{customdata}}<br>%{{y:.2f}} × SSP2-M 2040<extra></extra>",
                ),
                row=1,
                col=col,
            )
        fig.update_yaxes(
            title_text="Index (SSP2-M 2040 = 1)" if col == 1 else None,
            gridcolor="#E4E8EA",
            row=1,
            col=col,
        )
        fig.update_xaxes(tickangle=-40, row=1, col=col)
    fig.update_layout(
        barmode="group",
        template="plotly_white",
        margin={"l": 65, "r": 20, "t": 75, "b": 125},
        font={"family": "Arial", "size": 13},
        legend={"orientation": "h", "y": -0.38},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def cross_iam_figure() -> go.Figure:
    image = context_series("Carbon Dioxide emissions", ["SSP2-M"], model="image")
    message = context_series("Carbon Dioxide emissions", ["SSP2-M"], model="message")
    fig = go.Figure()
    for label, frame, color, dash in [
        ("IMAGE · SSP2-M", image, "#D99614", "solid"),
        ("MESSAGE · SSP2-M", message, "#3366A3", "dash"),
    ]:
        fig.add_trace(
            go.Scatter(
                x=frame["year"],
                y=frame["display_value"],
                mode="lines",
                name=label,
                line={"width": 4, "color": color, "dash": dash},
            )
        )
    return _base_layout(fig, "A shared label does not produce one pathway", "Gt CO₂/yr")


def steel_snapshot(year: int = 2060) -> go.Figure:
    scenarios = CORE_SCENARIOS
    frame = steel_mix(scenarios, year)
    colors = {
        "Secondary": "#5C8DCE",
        "Primary with CCS": "#7656A8",
        "Hydrogen-based primary": "#008A82",
        "Other primary": "#A6A6A6",
    }
    fig = go.Figure()
    for route in colors:
        data = frame[frame["route"] == route]
        values = {row.scenario: row.share for row in data.itertuples()}
        fig.add_trace(
            go.Bar(
                x=scenarios,
                y=[values.get(scenario, 0) for scenario in scenarios],
                name=route,
                marker_color=colors[route],
                hovertemplate=f"{route}: %{{y:.1%}}<extra></extra>",
            )
        )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(
        tickformat=".0%", range=[0, 1], title="Share of reported steel routes"
    )
    return _base_layout(fig, f"Reported steel production routes in {year}", None)
