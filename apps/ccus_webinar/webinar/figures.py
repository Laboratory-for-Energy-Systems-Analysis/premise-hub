from __future__ import annotations

from collections import defaultdict
from itertools import accumulate

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .model import CAMPAIGN_TONNES, SYSTEMS
from .plot_style import static_style, temporal_style

INK = "#17313b"
MUTED = "#627780"
GRID = "rgba(65,91,102,.14)"
PAPER = "rgba(0,0,0,0)"
PLOT = "#f5f8f8"
RED = "#c44e52"
BAU_LINE = "#536a73"

STAGE_COLORS = {
    "clinker": "#b85f43",
    "raw_materials": "#8d9ba1",
    "kiln_fuels": "#d59324",
    "heat_recovery": "#2f8f83",
    "capture": "#397b9e",
    "storage": "#315b91",
    "hydrogen": "#755aa6",
    "methanol": "#4da2b4",
    "synthetic_fuel": "#6f9c48",
    "infrastructure": "#9a7b62",
    "other": "#9aa8ad",
}

STAGE_LABELS = {
    "clinker": "Clinker",
    "raw_materials": "Raw materials",
    "kiln_fuels": "Kiln fuels",
    "heat_recovery": "Heat balance",
    "capture": "Capture",
    "storage": "Storage chain",
    "hydrogen": "Hydrogen",
    "methanol": "Methanol",
    "synthetic_fuel": "Methanol-to-X",
    "infrastructure": "Infrastructure",
    "other": "Other",
}

FLOW_COLORS = {
    "Carbon dioxide, fossil": "#b85f43",
    "Carbon dioxide, non-fossil": "#3c8c62",
    "Methane, fossil": "#755aa6",
    "Methane, non-fossil": "#9b78be",
    "Dinitrogen monoxide": "#d59324",
    "Nitrogen oxides": "#397b9e",
    "Sulfur dioxide": "#8d9ba1",
    "Carbon monoxide, fossil": "#7a6a58",
    "Carbon monoxide, non-fossil": "#56a3a6",
    "other_flows": "#9aa8ad",
}

FLOW_LABELS = {
    "Carbon dioxide, fossil": "CO₂ · fossil",
    "Carbon dioxide, non-fossil": "CO₂ · non-fossil",
    "Methane, fossil": "CH₄ · fossil",
    "Methane, non-fossil": "CH₄ · non-fossil",
    "Dinitrogen monoxide": "N₂O",
    "Nitrogen oxides": "NOₓ",
    "Sulfur dioxide": "SO₂",
    "Carbon monoxide, fossil": "CO · fossil",
    "Carbon monoxide, non-fossil": "CO · non-fossil",
    "other_flows": "Other flows",
}


def _contributor_label(name):
    return STAGE_LABELS.get(name, FLOW_LABELS.get(name, name.replace("_", " ")))


def _contributor_color(value: str) -> str:
    carbon_colors = {'Kiln CO₂ · fossil':'#bc7056','Kiln CO₂ · non-fossil':'#78ab60',
        'CO₂ to storage · fossil':'#426a9c','CO₂ to storage · non-fossil':'#269f9a',
        'CO₂ to utilisation · non-fossil':'#755aa6',
        'Captured CO₂ · fossil':'#426a9c','Captured CO₂ · non-fossil':'#269f9a',
        'Storage CO₂ losses':'#dca44a','Conversion CO₂ release':'#a98aca','Fuel CO₂ release (+1 y)':'#dc8391'}
    if value in carbon_colors:
        return carbon_colors[value]
    return STAGE_COLORS.get(value, FLOW_COLORS.get(value, STAGE_COLORS["other"]))


def _base_layout(height: int, margin: dict | None = None) -> dict:
    return {
        "height": height,
        "margin": margin or {"l": 62, "r": 24, "t": 34, "b": 44},
        "paper_bgcolor": PAPER,
        "plot_bgcolor": PLOT,
        "font": {"family": "Arial, Helvetica, sans-serif", "color": INK, "size": 11},
        "hoverlabel": {"font": {"size": 12}},
    }


def _table(bundle, *names: str) -> tuple[dict, ...]:
    for name in names:
        rows = bundle.tables.get(name, ())
        if rows:
            return rows
    return ()


def status_figure(bundle, message: str | None = None, height: int = 390) -> go.Figure:
    detail = message or getattr(
        bundle, "message", "Approved results are not available."
    )
    withdrawn = bundle.status == "invalidated"
    if withdrawn:
        detail = "Carbon routing, hydrogen and product end-of-life are under review.<br>The ranking and any claim of carbon neutrality have not been verified."
    fig = go.Figure()
    fig.add_shape(
        type="rect",
        x0=0.08,
        x1=0.92,
        y0=0.21,
        y1=0.79,
        line={"color": "#b9c9ce", "width": 1.2},
        fillcolor="#f4f8f8",
    )
    fig.add_annotation(
        x=0.5,
        y=0.59,
        text="<b>Climate results withdrawn after the carbon audit</b>" if withdrawn else "<b>Recalculation required</b>",
        showarrow=False,
        font={"size": 20, "color": INK},
    )
    fig.add_annotation(
        x=0.5,
        y=0.40,
        text=detail,
        showarrow=False,
        font={"size": 11, "color": MUTED},
        align="center",
    )
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[0, 1])
    fig.update_layout(**_base_layout(height), showlegend=False)
    return fig


def _float(row: dict, key: str) -> float:
    return float(row.get(key, 0) or 0)


def _normalization_factor(normalization: str) -> float:
    return CAMPAIGN_TONNES if normalization == "absolute" else 1.0


def render_static_comparison(
    lens: str, pathway: str, grouping: str, bundle
) -> go.Figure:
    totals = _table(bundle, "static_totals", "static_results")
    contributions = _table(bundle, "static_contributions", "contributions")
    if not totals:
        return status_figure(bundle)
    row_pathways = {pathway}
    if lens == "current_static":
        row_pathways |= {"current", "SSP2-NPi"}
    selected = [
        r for r in totals if r.get("lens") == lens and r.get("pathway") in row_pathways
    ]
    by_system = {r.get("system"): r for r in selected}
    if any(system not in by_system for system in SYSTEMS):
        return status_figure(
            bundle, f"The {lens.replace('_', ' ')} comparison is not complete."
        )
    contrib = [
        r
        for r in contributions
        if r.get("lens") == lens
        and r.get("pathway") in row_pathways
        and r.get("grouping", "stage")
        in {grouping, "stage" if grouping == "stage" else grouping}
    ]
    key_name = "contributor" if any("contributor" in r for r in contrib) else "stage"
    values = defaultdict(float)
    for row in contrib:
        values[(row.get("system"), row.get(key_name, "other"))] += _float(row, "score")
    if grouping == "flow":
        importance = defaultdict(float)
        for (_system, contributor), value in values.items():
            importance[contributor] += abs(value)
        retained = {
            contributor
            for contributor, _value in sorted(
                importance.items(), key=lambda item: item[1], reverse=True
            )[:7]
        }
        compact = defaultdict(float)
        for (system, contributor), value in values.items():
            compact[
                (system, contributor if contributor in retained else "other_flows")
            ] += value
        values = compact
    categories = sorted(
        {key for _system, key in values},
        key=lambda value: (
            list(STAGE_COLORS).index(value) if value in STAGE_COLORS else 99
        ),
    )
    fig = go.Figure()
    for category in categories:
        row_values = [values[(system, category)] for system in SYSTEMS]
        if not any(abs(value) > 1e-12 for value in row_values):
            continue
        fig.add_trace(
            go.Bar(
                name=_contributor_label(category),
                x=row_values,
                y=list(SYSTEMS),
                orientation="h",
                marker_color=_contributor_color(category),
                hovertemplate="%{y}<br>%{x:,.1f} kg CO2-eq/t<extra>%{fullData.name}</extra>",
            )
        )
    net = [_float(by_system[system], "score") for system in SYSTEMS]
    if not categories:
        fig.add_trace(
            go.Bar(
                x=net,
                y=list(SYSTEMS),
                orientation="h",
                marker_color=["#8d9ba1", "#397b9e", "#6f9c48"],
                showlegend=False,
            )
        )
    fig.add_trace(
        go.Scatter(
            x=net,
            y=list(SYSTEMS),
            mode="markers+text",
            marker={"size": 11, "color": INK, "line": {"color": "white", "width": 2}},
            text=[f"{value:,.0f}" for value in net],
            textposition=[
                "middle right" if value >= 0 else "middle left" for value in net
            ],
            showlegend=False,
            hovertemplate="%{y}<br>Net %{x:,.1f} kg CO2-eq/t<extra></extra>",
        )
    )
    fig.add_vline(x=0, line={"color": INK, "width": 1.3})
    fig.update_layout(
        **_base_layout(420, {"l": 82, "r": 60, "t": 16, "b": 70}),
        barmode="relative",
        xaxis={
            "title": "credits / storage  ←  kg CO₂-eq per tonne clinker  →  burdens",
            "gridcolor": GRID,
            "zeroline": False,
        },
        yaxis={
            "autorange": "reversed",
            "gridcolor": "rgba(0,0,0,0)",
            "categoryorder": "array",
            "categoryarray": list(SYSTEMS),
        },
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.20,
            "font": {"size": 9},
        },
        hovermode="closest",
    )
    # One scale across both snapshot years, pathways and contribution groupings.
    envelopes = defaultdict(lambda: [0.0, 0.0])
    for row in contributions:
        if row.get("lens") not in {"current_static", "prospective_static"}:
            continue
        value = _float(row, "score")
        key = (
            row.get("lens"),
            row.get("pathway"),
            row.get("system"),
            row.get("grouping", "stage"),
        )
        envelopes[key][int(value >= 0)] += value
    extent = (
        max(
            [abs(v) for bounds in envelopes.values() for v in bounds]
            + [abs(_float(r, "score")) for r in totals]
        )
        or 1
    )
    fig.update_xaxes(range=[-extent * 1.15, extent * 1.15])
    if lens == "prospective_static":
        # Keep the new number separate from a nearby prior-year diamond.
        for trace in fig.data:
            if trace.type == "scatter" and trace.mode == "markers+text":
                trace.textposition = "top center"
        baseline = {
            r.get("system"): _float(r, "score")
            for r in totals
            if r.get("lens") == "current_static"
            and r.get("pathway") in {"SSP2-NPi", "current"}
        }
        if set(baseline) == set(SYSTEMS):
            fig.add_trace(
                go.Scatter(
                    x=[baseline[s] for s in SYSTEMS],
                    y=list(SYSTEMS),
                    mode="markers",
                    name="2025 net",
                    marker={
                        "symbol": "diamond-open",
                        "size": 13,
                        "color": "#7d929d",
                        "line": {"width": 2},
                    },
                    hovertemplate="2025 net: %{x:,.0f} kg CO₂-eq/t<extra>%{y}</extra>",
                )
            )
            for system, value in zip(SYSTEMS, net):
                fig.add_annotation(
                    x=extent * 1.12,
                    y=system,
                    text=f"Δ {value-baseline[system]:+,.0f}",
                    showarrow=False,
                    xanchor="right",
                    font={"size": 14, "color": INK},
                )
    return static_style(fig)


def _temporal_rows(bundle, system: str, pathway: str) -> list[dict]:
    rows = _table(bundle, "temporal_totals", "annual_results")
    return sorted(
        (r for r in rows if r.get("system") == system and r.get("pathway") == pathway),
        key=lambda r: int(float(r.get("year", 0))),
    )


def _temporal_contrib(bundle, system: str, pathway: str, grouping: str) -> list[dict]:
    rows = _table(bundle, "temporal_contributions", "contributions")
    return [
        r
        for r in rows
        if r.get("lens") in {None, "time_explicit"}
        and r.get("system") == system
        and r.get("pathway") == pathway
        and r.get("grouping", "stage")
        in {grouping, "stage" if grouping == "stage" else grouping}
    ]


def render_temporal_gwp(
    pathway: str, grouping: str, area_mode: str, normalization: str, bundle
) -> go.Figure:
    if not _table(bundle, "temporal_totals", "annual_results"):
        return status_figure(bundle,
            getattr(bundle, "payloads", {}).get("temporal_preview_error")
            or "Fresh time-explicit results are not available yet. Earlier temporal calculations are excluded.",
            height=520)
    factor = _normalization_factor(normalization)
    gwp_unit = "kg CO₂-eq/t" if normalization == "per_tonne" else "kg CO₂-eq · campaign"
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.055,
        subplot_titles=["BAU / reference", "CCS", "CCUS"],
        specs=[[{"secondary_y": True}]] * 3,
    )
    global_years: set[int] = set()
    annual_extent = 0.0
    cumulative_extent = 0.0
    prepared = {}
    for system in SYSTEMS:
        totals = _temporal_rows(bundle, system, pathway)
        if not totals:
            return status_figure(
                bundle, f"Time-explicit results are missing for {system}.", 520
            )
        total_by_year = {
            int(float(r["year"])): _float(r, "score") * factor for r in totals
        }
        # TRAILS can retain a much wider, zero-padded coordinate horizon.
        # Fit the inventory view to dated contributions, not empty padding.
        active_years = {year for year, value in total_by_year.items() if value != 0}
        global_years.update(active_years or total_by_year)
        contributions = _temporal_contrib(bundle, system, pathway, grouping)
        key_name = (
            "contributor" if any("contributor" in r for r in contributions) else "stage"
        )
        by_contributor = defaultdict(lambda: defaultdict(float))
        for row in contributions:
            by_contributor[row.get(key_name, "other")][int(float(row["year"]))] += (
                _float(row, "score") * factor
            )
        prepared[system] = (total_by_year, by_contributor)
    from .temporal_carbon_presentation import load_carbon_display, split_carbon
    carbon_display = load_carbon_display(bundle, public=True)
    if carbon_display:
        for system, (_, by_contributor) in prepared.items():
            split_carbon(by_contributor,system=system,grouping=grouping,factor=factor,payload=carbon_display)
    if grouping == "flow":
        importance = defaultdict(float)
        for _totals, by_contributor in prepared.values():
            for contributor, yearly in by_contributor.items():
                importance[contributor] += sum(abs(value) for value in yearly.values())
        retained = {
            contributor
            for contributor, _value in sorted(
                importance.items(), key=lambda item: item[1], reverse=True
            )[:7]
        }
        retained.update(c for _, contributors in prepared.values() for c in contributors if 'CO₂' in c)
        for system, (total_by_year, by_contributor) in tuple(prepared.items()):
            compact = defaultdict(lambda: defaultdict(float))
            for contributor, yearly in by_contributor.items():
                label = contributor if contributor in retained else "other_flows"
                for year, value in yearly.items():
                    compact[label][year] += value
            prepared[system] = (total_by_year, compact)
    years = list(range(min(global_years), max(global_years) + 1))
    # Keep numerical residuals in the plotted data, but not as misleading
    # legend categories. Evaluate significance per tonne in either scale mode.
    legend_magnitude = defaultdict(float)
    for _, contributors in prepared.values():
        for contributor, yearly in contributors.items():
            legend_magnitude[contributor] += sum(abs(v) for v in yearly.values()) / factor
    carbon_detail_labels = {
        "clinker": "Other kiln emissions",
        "capture": "Capture utilities & materials",
        "storage": "Storage utilities & transport",
        "methanol": "Methanol · other burdens",
        "synthetic_fuel": "MTX utilities & fuel credits",
        "Carbon dioxide, fossil": "Other CO₂ · fossil",
        "Carbon dioxide, non-fossil": "Other CO₂ · non-fossil",
    } if carbon_display else {}
    if carbon_display and not carbon_display['releases']:
        # Losses and fuel releases remain within their original stage totals.
        for stage in ('capture', 'storage', 'methanol', 'synthetic_fuel'):
            carbon_detail_labels.pop(stage, None)
    legend_seen = set()
    for panel, system in enumerate(SYSTEMS, start=1):
        total_by_year, by_contributor = prepared[system]
        # Signed stacks can exceed the net annual score by a large margin.
        for year in years:
            signed_values = [v.get(year, 0.0) for v in by_contributor.values()]
            annual_extent = max(annual_extent,
                sum(max(v, 0) for v in signed_values),
                abs(sum(min(v, 0) for v in signed_values)))
        if by_contributor:
            for contributor, yearly in sorted(by_contributor.items()):
                values = [yearly.get(year, 0.0) for year in years]
                color = _contributor_color(contributor)
                label = carbon_detail_labels.get(contributor, _contributor_label(contributor))
                show_in_legend = legend_magnitude[contributor] >= 0.001
                if area_mode == "stacked":
                    for sign, signed in (
                        ("positive", [max(v, 0) for v in values]),
                        ("negative", [min(v, 0) for v in values]),
                    ):
                        if any(signed):
                            fig.add_trace(
                                go.Scatter(
                                    x=years,
                                    y=signed,
                                    mode="lines",
                                    line={"color": color, "width": 0.8},
                                    fillcolor=color,
                                    opacity=0.68,
                                    stackgroup=f"{system}-{sign}",
                                    name=label,
                                    legendgroup=label,
                                    showlegend=show_in_legend and label not in legend_seen,
                                    hovertemplate="%{x}<br>%{y:,.0f} " + gwp_unit + "<extra>%{fullData.name}</extra>",
                                ),
                                row=panel,
                                col=1,
                                secondary_y=False,
                            )
                            legend_seen.add(label)
                elif any(values):
                    fig.add_trace(
                        go.Scatter(
                            x=years,
                            y=values,
                            mode="lines",
                            line={"color": color, "width": 1},
                            fill="tozeroy",
                            fillcolor=color,
                            opacity=0.18,
                            name=label,
                            legendgroup=label,
                            showlegend=show_in_legend and label not in legend_seen,
                            hovertemplate="%{x}<br>%{y:,.0f} " + gwp_unit + "<extra>%{fullData.name}</extra>",
                        ),
                        row=panel,
                        col=1,
                        secondary_y=False,
                    )
                    legend_seen.add(label)
        else:
            values = [total_by_year.get(year, 0.0) for year in years]
            for label, color, signed in (
                ("Annual burden", "#b85f43", [max(v, 0) for v in values]),
                ("Annual credit", "#397b9e", [min(v, 0) for v in values]),
            ):
                fig.add_trace(
                    go.Scatter(
                        x=years,
                        y=signed,
                        mode="lines",
                        line={"color": color, "width": 1},
                        fill="tozeroy",
                        fillcolor=color,
                        opacity=0.55,
                        name=label,
                        showlegend=panel == 1,
                    ),
                    row=panel,
                    col=1,
                    secondary_y=False,
                )
        annual = [total_by_year.get(year, 0.0) for year in years]
        cumulative = list(accumulate(annual))
        annual_extent = max(annual_extent, *(abs(v) for v in annual))
        cumulative_extent = max(cumulative_extent, *(abs(v) for v in cumulative))
        fig.add_trace(
            go.Scatter(
                x=years,
                y=cumulative,
                mode="lines",
                line={"color": RED, "width": 4},
                name="Cumulative GWP100",
                showlegend=panel == 1,
                hovertemplate="%{x}<br>%{y:,.0f} " + gwp_unit + "<extra>Cumulative GWP100</extra>",
            ),
            row=panel,
            col=1,
            secondary_y=True,
        )
        fig.add_hline(
            y=0, line={"color": INK, "width": 0.8}, row=panel, col=1, secondary_y=False
        )
        fig.update_yaxes(
            range=(
                [-annual_extent * 1.08, annual_extent * 1.08] if annual_extent else None
            ),
            title_text=f"Annual {gwp_unit}" if panel == 2 else None,
            gridcolor=GRID,
            row=panel,
            col=1,
            secondary_y=False,
        )
        fig.update_yaxes(
            range=(
                [-cumulative_extent * 1.08, cumulative_extent * 1.08]
                if cumulative_extent
                else None
            ),
            title_text=f"Cumulative {gwp_unit}" if panel == 2 else None,
            showgrid=False,
            tickfont={"color": RED},
            row=panel,
            col=1,
            secondary_y=True,
        )
    # Apply the final global extents to every panel so the three systems are
    # compared on identical axes, even when an early panel has a smaller range.
    for panel in range(1, 4):
        fig.update_yaxes(
            range=(
                [-annual_extent * 1.08, annual_extent * 1.08] if annual_extent else None
            ),
            title_text=f"Annual {gwp_unit}" if panel == 2 else None,
            gridcolor=GRID,
            row=panel,
            col=1,
            secondary_y=False,
        )
        fig.update_yaxes(
            range=(
                [-cumulative_extent * 1.08, cumulative_extent * 1.08]
                if cumulative_extent
                else None
            ),
            title_text=f"Cumulative {gwp_unit}" if panel == 2 else None,
            showgrid=False,
            tickfont={"color": RED},
            row=panel,
            col=1,
            secondary_y=True,
        )
    fig.add_vrect(
        x0=2035,
        x1=2064.8,
        fillcolor="rgba(8,126,164,.055)",
        line_width=0,
        row="all",
        col=1,
    )
    fig.update_xaxes(
        title_text="Calendar year" if True else None, gridcolor=GRID, row=3, col=1
    )
    fig.update_layout(
        **_base_layout(560, {"l": 68, "r": 70, "t": 42, "b": 62}),
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.10,
            "font": {"size": 9},
        },
        hovermode="x unified",
    )
    # Display window only: retain earlier events in the cumulative calculation.
    fig.update_xaxes(range=[2006, max(global_years)])
    fig = temporal_style(fig, kind="gwp", unit=gwp_unit, area_mode=area_mode)
    # The shared style rebuilds legend visibility, so apply the residual filter
    # afterward as well. The traces and their numerical values stay intact.
    negligible_labels = {
        carbon_detail_labels.get(name, _contributor_label(name))
        for name, magnitude in legend_magnitude.items() if magnitude < 0.001
    }
    for trace in fig.data:
        if trace.name in negligible_labels:
            trace.showlegend = False
    from .plot_style import compact_gwp_legend
    compact_gwp_legend(fig, grouping=grouping,
                       negligible_labels=negligible_labels, unit=gwp_unit)
    # Retain paired annual/cumulative axes but place the scenarios side by side.
    for panel in range(3):
        left, right = panel*.35, panel*.35+.30
        xkey = 'xaxis'+(str(panel+1) if panel else '')
        ykey = 'yaxis'+(str(panel*2+1) if panel else '')
        fig.layout[xkey].update(domain=[left,right],showticklabels=True,
            title_text='Calendar year',dtick=25)
        fig.layout[ykey].update(domain=[0,1],title_text=f'Annual {gwp_unit}' if panel==0 else None)
        fig.layout[f'yaxis{panel*2+2}'].update(
            title_text=f'Cumulative {gwp_unit}' if panel==2 else None)
        fig.layout.annotations[panel].update(x=left,y=1.07,xanchor='left')
        fig.layout.annotations[panel+3].update(x=right,y=1.01,xanchor='right')
    fig.update_layout(legend_y=1.17,margin=dict(l=65,r=80,t=100,b=45))
    return fig


def _median_rows(bundle, system: str, pathway: str, metric: str) -> list[dict]:
    aliases = {
        "radiative_forcing": {"radiative forcing", "radiative_forcing"},
        "temperature": {"temperature", "temperature change", "temperature_change"},
    }
    rows = _table(bundle, "fair_responses", "climate_results")
    candidates = [
        r
        for r in rows
        if r.get("system") == system
        and r.get("pathway") == pathway
        and r.get("metric") in aliases[metric]
    ]
    median_labels = {"q50", "median", "q0.5", "50", "50.0"}
    return sorted(
        (r for r in candidates if str(r.get("statistic")) in median_labels),
        key=lambda r: float(r["year"]),
    )


def render_fair_response(
    pathway: str,
    metric: str,
    grouping: str,
    area_mode: str,
    normalization: str,
    uncertainty: bool,
    bundle,
) -> go.Figure:
    if not _table(bundle, "fair_responses", "climate_results"):
        return status_figure(bundle, getattr(bundle, 'payloads', {}).get('fair_preview_error')
            or 'The TRAILS–FaIR climate-response results are not yet available.', height=560)
    factor = _normalization_factor(normalization)
    response_scale = 1e12 if metric == "radiative_forcing" else 1e9
    response_unit = "pW/m²" if metric == "radiative_forcing" else "n°C"
    response_axis_unit = (
        f"{response_unit}/t"
        if normalization == "per_tonne"
        else f"{response_unit} · campaign"
    )
    annual_axis_unit = (
        "kg CO₂-eq/t" if normalization == "per_tonne" else "kg CO₂-eq · campaign"
    )
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.055,
        subplot_titles=["BAU / reference", "CCS", "CCUS"],
        specs=[[{"secondary_y": True}]] * 3,
    )
    response_series = {}
    response_extent = 0.0
    for system in SYSTEMS:
        rows = _median_rows(bundle, system, pathway, metric)
        if not rows:
            return status_figure(
                bundle, f"FaIR {metric.replace('_', ' ')} is missing for {system}.", 560
            )
        response_series[system] = (
            [float(r["year"]) for r in rows],
            [_float(r, "value") * response_scale * factor for r in rows],
        )
        response_extent = max(
            response_extent, *(abs(v) for v in response_series[system][1])
        )
    response_start = min(
        (
            int(year)
            for years, values in response_series.values()
            for year, value in zip(years, values, strict=True)
            if abs(value) > max(response_extent * 1e-9, 1e-12)
        ),
        default=int(min(response_series["BAU"][0])),
    )
    contribution_series = {}
    for system in SYSTEMS:
        contributions = _temporal_contrib(bundle, system, pathway, grouping)
        key_name = (
            "contributor"
            if any("contributor" in row for row in contributions)
            else "stage"
        )
        by_contributor = defaultdict(lambda: defaultdict(float))
        for row in contributions:
            by_contributor[row.get(key_name, "other")][int(float(row["year"]))] += (
                _float(row, "score") * factor
            )
        contribution_series[system] = by_contributor
    from .temporal_carbon_presentation import load_carbon_display, split_carbon
    carbon_display = load_carbon_display(bundle)
    if carbon_display:
        for system, contributors in contribution_series.items():
            split_carbon(contributors, system=system, grouping=grouping,
                         factor=factor, payload=carbon_display)
    if grouping == "flow":
        importance = defaultdict(float)
        for by_contributor in contribution_series.values():
            for contributor, yearly in by_contributor.items():
                importance[contributor] += sum(abs(value) for value in yearly.values())
        retained = {
            contributor
            for contributor, _value in sorted(
                importance.items(), key=lambda item: item[1], reverse=True
            )[:7]
        }
        retained.update(c for contributors in contribution_series.values()
                        for c in contributors if 'CO₂' in c)
        for system, by_contributor in tuple(contribution_series.items()):
            compact = defaultdict(lambda: defaultdict(float))
            for contributor, yearly in by_contributor.items():
                label = contributor if contributor in retained else "other_flows"
                for year, value in yearly.items():
                    compact[label][year] += value
            contribution_series[system] = compact
    bau_years, bau_values = response_series["BAU"]
    annual_extent = 0.0
    for panel, system in enumerate(SYSTEMS, start=1):
        by_contributor = contribution_series[system]
        if by_contributor:
            years = list(
                range(
                    min(y for values in by_contributor.values() for y in values),
                    max(y for values in by_contributor.values() for y in values) + 1,
                )
            )
            for contributor, yearly in sorted(by_contributor.items()):
                values = [yearly.get(year, 0.0) for year in years]
                annual_extent = max(annual_extent, *(abs(v) for v in values))
                color = _contributor_color(contributor)
                label = _contributor_label(contributor)
                if area_mode == "stacked":
                    for sign, signed in (
                        ("positive", [max(v, 0) for v in values]),
                        ("negative", [min(v, 0) for v in values]),
                    ):
                        if any(signed):
                            fig.add_trace(
                                go.Scatter(
                                    x=years,
                                    y=signed,
                                    mode="lines",
                                    line={"color": color, "width": 0.6},
                                    fillcolor=color,
                                    opacity=0.35,
                                    stackgroup=f"fair-{system}-{sign}",
                                    name=label,
                                    legendgroup=label,
                                    showlegend=panel == 1 and sign == "positive",
                                    hovertemplate="%{x}<br>%{y:,.3g}<extra>%{fullData.name}</extra>",
                                ),
                                row=panel,
                                col=1,
                                secondary_y=False,
                            )
                elif any(values):
                    fig.add_trace(
                        go.Scatter(
                            x=years,
                            y=values,
                            mode="lines",
                            line={"color": color, "width": 0.8},
                            fill="tozeroy",
                            fillcolor=color,
                            opacity=0.13,
                            name=label,
                            legendgroup=label,
                            showlegend=panel == 1,
                        ),
                        row=panel,
                        col=1,
                        secondary_y=False,
                    )
        years, values = response_series[system]
        if system != "BAU":
            fig.add_trace(
                go.Scatter(
                    x=bau_years,
                    y=bau_values,
                    mode="lines",
                    line={"color": BAU_LINE, "width": 1.6, "dash": "dash"},
                    opacity=0.52,
                    name="BAU benchmark",
                    legendgroup="bau-benchmark",
                    showlegend=panel == 2,
                    hoverinfo="skip",
                ),
                row=panel,
                col=1,
                secondary_y=True,
            )
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=values,
                    mode="lines",
                    line={"color": "#6f5aa6", "width": 3.8},
                    fill="tonexty",
                    fillcolor="rgba(69,145,132,.08)",
                    name="Median response",
                    legendgroup="median",
                    showlegend=panel == 1,
                    hovertemplate=f"%{{x:.0f}}<br>%{{y:.3g}} {response_unit}<extra>{system}</extra>",
                ),
                row=panel,
                col=1,
                secondary_y=True,
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=values,
                    mode="lines",
                    line={"color": "#6f5aa6", "width": 3.8},
                    name="Median response",
                    legendgroup="median",
                    showlegend=True,
                    hovertemplate=f"%{{x:.0f}}<br>%{{y:.3g}} {response_unit}<extra>{system}</extra>",
                ),
                row=panel,
                col=1,
                secondary_y=True,
            )
        if uncertainty:
            all_rows = _table(bundle, "fair_responses", "climate_results")
            aliases = {
                "radiative_forcing": {"radiative forcing", "radiative_forcing"},
                "temperature": {
                    "temperature",
                    "temperature change",
                    "temperature_change",
                },
            }[metric]
            relevant = [
                r
                for r in all_rows
                if r.get("system") == system
                and r.get("pathway") == pathway
                and r.get("metric") in aliases
            ]
            for lower_label, upper_label in (("q2.5", "q97.5"),):
                lower = sorted(
                    (r for r in relevant if r.get("statistic") == lower_label),
                    key=lambda r: float(r["year"]),
                )
                upper = sorted(
                    (r for r in relevant if r.get("statistic") == upper_label),
                    key=lambda r: float(r["year"]),
                )
                if lower and len(lower) == len(upper):
                    bx = [float(r["year"]) for r in lower]
                    fig.add_trace(
                        go.Scatter(
                            x=bx,
                            y=[
                                _float(r, "value") * response_scale * factor
                                for r in lower
                            ],
                            mode="lines",
                            line={"width": 0},
                            showlegend=False,
                            hoverinfo="skip",
                        ),
                        row=panel,
                        col=1,
                        secondary_y=True,
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=bx,
                            y=[
                                _float(r, "value") * response_scale * factor
                                for r in upper
                            ],
                            mode="lines",
                            line={"width": 0},
                            fill="tonexty",
                            fillcolor="rgba(84,100,110,.16)",
                            name="FaIR 2.5–97.5%",
                            showlegend=panel == 1,
                            hoverinfo="skip",
                        ),
                        row=panel,
                        col=1,
                        secondary_y=True,
                    )
        fig.add_hline(
            y=0, line={"color": INK, "width": 0.7}, row=panel, col=1, secondary_y=True
        )
        fig.update_yaxes(
            range=(
                [-annual_extent * 1.1, annual_extent * 1.1] if annual_extent else None
            ),
            title_text=f"Annual GWP100 ({annual_axis_unit})" if panel == 2 else None,
            gridcolor=GRID,
            row=panel,
            col=1,
            secondary_y=False,
        )
        fig.update_yaxes(
            range=(
                [-response_extent * 1.1, response_extent * 1.1]
                if response_extent
                else None
            ),
            title_text=response_axis_unit if panel == 2 else None,
            showgrid=False,
            row=panel,
            col=1,
            secondary_y=True,
        )
    for panel in range(1, 4):
        fig.update_yaxes(
            range=(
                [-annual_extent * 1.1, annual_extent * 1.1] if annual_extent else None
            ),
            title_text=f"Annual GWP100 ({annual_axis_unit})" if panel == 2 else None,
            gridcolor=GRID,
            row=panel,
            col=1,
            secondary_y=False,
        )
        fig.update_yaxes(
            range=(
                [-response_extent * 1.1, response_extent * 1.1]
                if response_extent
                else None
            ),
            title_text=response_axis_unit if panel == 2 else None,
            showgrid=False,
            row=panel,
            col=1,
            secondary_y=True,
        )
    fig.update_xaxes(
        title_text="Climate-response year",
        gridcolor=GRID,
        range=[2000, 2200],
        row=3,
        col=1,
    )
    fig.update_layout(
        **_base_layout(570, {"l": 72, "r": 70, "t": 44, "b": 66}),
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.10,
            "font": {"size": 9},
        },
        hovermode="x unified",
    )
    fig = temporal_style(
        fig, kind="fair", unit=response_axis_unit, area_mode=area_mode
    )
    from .plot_style import compact_gwp_legend
    magnitude = defaultdict(float)
    for contributors in contribution_series.values():
        for name, values in contributors.items():
            magnitude[_contributor_label(name)] += sum(abs(v) for v in values.values()) / factor
    compact_gwp_legend(fig, grouping=grouping,
        negligible_labels={name for name, value in magnitude.items() if value < .001},
        unit=annual_axis_unit)
    for trace in fig.data:
        if trace.name == 'Median response':
            trace.legendrank = 100
            trace.hoverinfo = None
            trace.hovertemplate = '%{x:.0f}<br>%{y:.3g} ' + response_axis_unit + '<extra>Climate response</extra>'
    for panel in range(3):
        left, right = panel * .35, panel * .35 + .30
        xkey = 'xaxis' + (str(panel+1) if panel else '')
        ykey = 'yaxis' + (str(panel*2+1) if panel else '')
        fig.layout[xkey].update(domain=[left,right], showticklabels=True,
            title_text='Calendar year', range=[2000,2200], dtick=50)
        fig.layout[ykey].update(domain=[0,1],
            title_text=f'Annual {annual_axis_unit}' if panel == 0 else None)
        fig.layout[f'yaxis{panel*2+2}'].update(
            title_text=response_axis_unit if panel == 2 else None)
        fig.layout.annotations[panel].update(x=left,y=1.07,xanchor='left')
        fig.layout.annotations[panel+3].update(x=right,y=1.01,xanchor='right')
    fig.update_layout(height=560, legend_y=1.17, margin=dict(l=65,r=80,t=100,b=45))
    fig.layout.meta['reset_axes'] = {key:list(fig.layout[key].range) if fig.layout[key].range else None
        for key in fig.layout if key.startswith(('xaxis','yaxis'))}
    return fig


def render_pulse_equivalence(metric, normalization, window_start, window_end, uncertainty, bundle, reference_year=2035):
    from .pulse_view import pulse_figure
    return pulse_figure(metric, normalization, window_start, window_end, uncertainty, bundle, reference_year)


def render_sensitivity(
    avoided_heat: str,
    operating_electricity: str,
    non_fossil_share: int,
    metric: str,
    bundle,
) -> go.Figure:
    rows = _table(bundle, "sensitivity_results")
    selected = [
        row
        for row in rows
        if row.get("avoided_heat") == avoided_heat
        and row.get("operating_electricity") == operating_electricity
        and int(float(row.get("non_fossil_kiln_share", -1))) == int(non_fossil_share)
        and row.get("metric") == metric
        and row.get("statistic", "median") in {"median", "q50"}
    ]
    if not selected:
        return status_figure(
            bundle, "This sensitivity combination has not been precomputed.", 430
        )
    unit = {
        "cumulative_gwp100": "kg CO₂-eq/t clinker",
        "radiative_forcing": "pW/m²/t clinker",
        "temperature": "n°C/t clinker",
    }.get(metric, "value")
    scale = (
        1e12
        if metric == "radiative_forcing"
        else 1e9 if metric == "temperature" else 1.0
    )
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=["BAU / reference", "CCS", "CCUS"],
    )
    extent = 0.0
    for panel, system in enumerate(SYSTEMS, start=1):
        local = sorted(
            (row for row in selected if row.get("system") == system),
            key=lambda row: float(row["year"]),
        )
        if not local:
            continue
        x = [float(row["year"]) for row in local]
        y = [_float(row, "value") * scale for row in local]
        extent = max(extent, *(abs(value) for value in y))
        color = {"BAU": "#71838a", "CCS": "#397b9e", "CCUS": "#3c8c62"}[system]
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                line={"color": color, "width": 3},
                fill="tozeroy",
                fillcolor=color,
                opacity=0.82,
                showlegend=False,
                hovertemplate=f"%{{x:.0f}}<br>%{{y:,.3g}} {unit}<extra>{system}</extra>",
            ),
            row=panel,
            col=1,
        )
        fig.add_hline(y=0, line={"color": INK, "width": 0.7}, row=panel, col=1)
    for panel in range(1, 4):
        fig.update_yaxes(
            range=[-extent * 1.08, extent * 1.08] if extent else None,
            title_text=unit if panel == 2 else None,
            gridcolor=GRID,
            row=panel,
            col=1,
        )
    fig.update_xaxes(title_text="Calendar year", gridcolor=GRID, row=3, col=1)
    fig.update_layout(
        **_base_layout(445, {"l": 80, "r": 24, "t": 42, "b": 46}), hovermode="x unified"
    )
    return fig


def _ordering(values: dict[str, float]) -> str:
    return " < ".join(sorted(values, key=values.get))


def static_takeaway(lens: str, pathway: str, bundle) -> str:
    rows = [
        row
        for row in _table(bundle, "static_totals", "static_results")
        if row.get("lens") == lens
    ]
    if lens == "current_static":
        rows = [row for row in rows if row.get("pathway") in {"current", "SSP2-NPi"}]
    else:
        rows = [row for row in rows if row.get("pathway") == pathway]
    values = {
        row.get("system"): _float(row, "score")
        for row in rows
        if row.get("system") in SYSTEMS
    }
    if len(values) != len(SYSTEMS):
        return "The ranking will appear once the results have been checked."
    ordering = _ordering(values)
    spread = max(values.values()) - min(values.values())
    if lens == "current_static":
        return f"Lower is better: {ordering}. The spread is {spread:,.0f} kg CO₂-eq/t clinker."

    current_rows = [
        row
        for row in _table(bundle, "static_totals", "static_results")
        if row.get("lens") == "current_static"
        and row.get("pathway") in {"current", "SSP2-NPi"}
    ]
    current = {
        row.get("system"): _float(row, "score")
        for row in current_rows
        if row.get("system") in SYSTEMS
    }
    changes = []
    if len(current) == len(SYSTEMS):
        changes.append(
            "the ranking changes"
            if _ordering(current) != ordering
            else "the ranking is unchanged"
        )
        sign_changes = [
            system
            for system in SYSTEMS
            if (current[system] < 0) != (values[system] < 0)
        ]
        if sign_changes:
            changes.append(f"{', '.join(sign_changes)} crosses zero")
    prefix = "; ".join(changes) if changes else "Lower is better"
    prefix = prefix[:1].upper() + prefix[1:]
    return (
        f"{prefix}. 2035 order: {ordering}; spread {spread:,.0f} kg CO₂-eq/t clinker."
    )


def temporal_takeaway(pathway: str, bundle) -> str:
    totals = {}
    crossings = {}
    for system in SYSTEMS:
        rows = _temporal_rows(bundle, system, pathway)
        if not rows:
            continue
        running = 0.0
        system_crossings = []
        for row in rows:
            previous = running
            running += _float(row, "score")
            if previous != 0 and (previous < 0 <= running or previous > 0 >= running):
                direction = "turns positive" if previous < 0 else "turns negative"
                system_crossings.append(f"{direction} in {int(float(row['year']))}")
        totals[system] = running
        crossings[system] = system_crossings
    if len(totals) != len(SYSTEMS):
        return "The annual and cumulative results are not yet available."
    negative = [system for system in SYSTEMS if totals[system] < 0]
    sign = (f"{' and '.join(negative)} {'finishes' if len(negative) == 1 else 'finish'} below zero."
            if negative else "No total is below zero.")
    return f"30-year GWP100, lowest first: {_ordering(totals)}. {sign} This covers the evolving plant’s operating life, not just the 2035 snapshot."


def fair_takeaway(pathway: str, metric: str, bundle) -> str:
    values = {}
    series = {}
    for system in SYSTEMS:
        rows = _median_rows(bundle, system, pathway, metric)
        if rows:
            scale = 1e12 if metric == "radiative_forcing" else 1e9
            series[system] = {
                int(float(item["year"])): _float(item, "value") * scale
                for item in rows
                if float(item["year"]) <= 2200.5
            }
            row = max(
                (row for row in rows if float(row["year"]) <= 2200.5),
                key=lambda item: float(item["year"]),
                default=rows[-1],
            )
            values[system] = _float(row, "value") * scale
    if len(values) != len(SYSTEMS):
        return "The climate-response results are not yet available."
    unit = "pW/m²" if metric == "radiative_forcing" else "n°C"
    benefit_years = {}
    for system in ("CCS", "CCUS"):
        common = sorted(set(series.get("BAU", {})) & set(series.get(system, {})))
        gaps = [series["BAU"][year] - series[system][year] for year in common]
        tolerance = max((abs(value) for value in gaps), default=0.0) * 1e-6
        benefit_years[system] = next(
            (
                year
                for year, gap in zip(common, gaps, strict=True)
                if year >= 2035 and gap > tolerance
            ),
            None,
        )
    timing = ". ".join(
        f"{system} first falls below BAU in {year}"
        for system, year in benefit_years.items()
        if year is not None
    )
    timing_text = f" {timing}." if timing else ""
    response = "radiative forcing" if metric == "radiative_forcing" else "temperature response"
    return f"Near 2200, {response} is lowest for {min(values, key=values.get)}. The BAU–CCUS difference is {values['BAU'] - values['CCUS']:.3g} {unit}/t.{timing_text}"


def pulse_takeaway(metric: str, window_start: int, window_end: int, bundle) -> str:
    metric_alias = {
        "forcing": "integrated_rf",
        "temperature": "integrated_temperature",
    }[metric]
    rows = [
        row
        for row in _table(bundle, "pulse_equivalence")
        if row.get("metric") == metric_alias
        and int(row.get("window_start", 0)) == window_start
        and int(row.get("window_end", 0)) == window_end
        and row.get("statistic") in {"median", "q50"}
    ]
    values = {
        row.get("system"): _float(row, "value")
        for row in rows
        if row.get("system") in SYSTEMS
    }
    if len(values) != len(SYSTEMS):
        return "The CO₂-pulse-equivalent results are not yet available."
    return f"Window {window_start}–{window_end} · reference pulse 2035 · {_ordering(values)}. CCUS: {values['CCUS']:,.0f} kg CO₂ pulse-eq per tonne of clinker produced over 30 years."
