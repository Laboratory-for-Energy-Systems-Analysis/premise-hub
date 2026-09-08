"""Three aligned stage bars with signed sub-process contributions."""

from collections import defaultdict
from hashlib import sha256
from math import ceil, floor
from urllib.parse import quote

from dash import html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .runtime_parameters import ELECTRICITY_OPTIONS, FUEL_SHARES, SYSTEMS
from .figures import STAGE_LABELS, status_figure


def carbon_balance_panel(bundle):
    data = bundle.payloads.get("static_carbon_balance")
    if not data:
        return html.P("The verified physical carbon balance is not available for this result.")
    from ..lca_model.carbon_balance import validate_carbon_balance

    validate_carbon_balance(data)
    u, g, s, r = (f'{data[k]:.0f}' for k in ("uptake", "generated", "stored", "released"))
    description = (
        f"CCS non-fossil carbon: {u} kg CO₂ absorbed from the atmosphere into biomass, "
        f"{g} generated at the kiln, {s} permanently stored and {r} released. "
        "Quantities per tonne clinker. Arrows show routing, not proportional widths."
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 88">
      <defs><marker id="a" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="none" stroke="#607986"/></marker></defs>
      <g fill="none" stroke="#607986" stroke-width="2" marker-end="url(#a)">
        <path d="M135 44H186"/><path d="M352 44H403"/><path d="M570 44H621"/>
        <path d="M788 44H818V21H850"/><path d="M818 44V67H850"/>
      </g>
      <g stroke="#d7e1e4" fill="white">
        <rect x="1" y="17" width="134" height="54" rx="9"/>
        <rect x="188" y="17" width="164" height="54" rx="9" fill="#eef5e8"/>
        <rect x="405" y="17" width="165" height="54" rx="9"/>
        <rect x="623" y="17" width="165" height="54" rx="9" fill="#edf3f6"/>
        <rect x="852" y="2" width="267" height="36" rx="8" fill="#fcf2ed"/>
        <rect x="852" y="50" width="267" height="36" rx="8" fill="#eaf4ef"/>
      </g>
      <g font-family="Arial, sans-serif" text-anchor="middle" fill="#173d50" font-size="18">
        <text x="68" y="50">Atmosphere</text>
        <text x="270" y="39">Biomass</text><text x="270" y="60" font-size="16">{u} absorbed</text>
        <text x="488" y="39">Kiln</text><text x="488" y="60" font-size="16">{g} generated</text>
        <text x="705" y="39">Capture + storage</text><text x="705" y="60" font-size="15">Including losses</text>
        <text x="985" y="26">{r} released to atmosphere</text>
        <text x="985" y="74" fill="#276d5b">{s} permanently stored</text>
      </g></svg>'''
    return html.Div([
        html.Div([
            html.Strong("CCS · Non-fossil carbon balance"),
            html.Span("2025 · kg CO₂/t clinker"),
        ], className="carbon-balance-heading"),
        html.Img(src="data:image/svg+xml," + quote(svg), alt=description, className="carbon-balance-diagram"),
        html.Div([
            html.Strong(f"In the bars: −{u} uptake + {g} generated − {s} stored = −{s} net"),
            html.Span(f"Physically: −{u} uptake + {r} released = −{s} net"),
        ], className="carbon-accounting-bridge"),
        html.Small("Storage corrects gross kiln emissions, not a second uptake. Carbon only here; charts retain energy and supply-chain impacts."),
    ], className="carbon-balance-panel")

# Presentation order only; the calculation graph and exported scores are unchanged.
STAGES = (
    "raw_materials",
    "kiln_fuels",
    "clinker",
    "heat_recovery",
    "capture",
    "storage",
    "hydrogen",
    "methanol",
    "synthetic_fuel",
)
PALETTE = (
    "#427f9d",
    "#829b42",
    "#c9913b",
    "#91639d",
    "#458d80",
    "#b7664f",
    "#7b8795",
    "#bd788d",
    "#50765e",
    "#6d8eae",
)
COLORS = {
    "Limestone calcination": "#b85f43",
    "Fossil kiln-fuel combustion": "#d99c64",
    "Non-fossil kiln-fuel combustion": "#819b47",
    "Fossil CO₂ stored": "#315b91",
    "Non-fossil CO₂ stored": "#397d6e",
    "Avoided jet-fuel production": "#267c9d",
    "Avoided fossil jet-fuel combustion": "#2e8977",
    "Synthetic jet-fuel combustion": "#ba8543",
    "Residual carbon oxidation": "#bb675c",
    "Conversion electricity": "#8b6caf",
    "Avoided diesel production": "#537b4c",
    "Avoided naphtha production": "#82984f",
}


def color_for(label):
    if label.startswith("Captured "):
        return "#397d6e" if "non-fossil" in label else "#315b91"
    return COLORS.get(
        label, PALETTE[int(sha256(label.encode()).hexdigest()[:8], 16) % len(PALETTE)]
    )


def whole_score(value):
    return f"{value:+,.0f}" if round(value) else "0"


def stage_rows(bundle, lens="current_static", pathway="SSP2-NPi"):
    return [
        r
        for r in bundle.tables.get("static_subprocesses", ())
        if r["lens"] == lens and r["pathway"] == pathway
    ]


def sensitivity_cell(bundle, electricity="ENC market", fuel_share=30):
    """Return one precomputed grid cell; never interpolate a result."""
    grid = bundle.payloads.get("current_static_sensitivity", {})
    electricity = electricity if electricity in ELECTRICITY_OPTIONS else "ENC market"
    try:
        fuel_share = int(fuel_share)
    except (TypeError, ValueError):
        fuel_share = 30
    if fuel_share not in FUEL_SHARES:
        return None
    return next(
        (
            cell
            for cell in grid.get("cells", ())
            if cell["electricity"] == electricity and cell["fuel_share"] == fuel_share
        ),
        None,
    )


def sensitivity_selection(bundle, electricity="ENC market", fuel_share=30):
    if bundle.status == "invalidated":
        return "Sensitivity results withdrawn pending the engineering corrections."
    cell = sensitivity_cell(bundle, electricity, fuel_share)
    if not cell:
        return "Sensitivity grid unavailable. The fourth panel remains the 2025 baseline."
    ranking = sorted(cell["totals"], key=cell["totals"].get)
    source = {"ENC market": "REMIND-EU market", "photovoltaic": "PV"}.get(
        cell["electricity"], cell["electricity"]
    )
    return (
        f"Calculated: {source} · {cell['fuel_share']}% non-fossil · "
        f"{ranking[0]} lowest ({cell['totals'][ranking[0]]:,.0f} kg CO₂-eq/t)."
    )


def sensitivity_takeaway(bundle, electricity="ENC market", fuel_share=30):
    if bundle.status == "invalidated":
        return "The previous ranking is withdrawn. Carbon, hydrogen and end-of-life checks must pass before recalculation."
    cell = sensitivity_cell(bundle, electricity, fuel_share)
    if not cell:
        return "The selected sensitivity combination has not been calculated."
    ranking = sorted(cell["totals"], key=cell["totals"].get)
    source = {"ENC market": "REMIND-EU market", "photovoltaic": "PV"}.get(
        cell["electricity"], cell["electricity"]
    )
    return (
        f"At {source} and {cell['fuel_share']}% non-fossil kiln energy: "
        f"{' < '.join(ranking)}."
    )


def render_stage_comparison(
    bundle, selected="synthetic_fuel", lens="current_static", pathway="SSP2-NPi",
    prototype=False, electricity="ENC market", fuel_share=30,
):
    rows = stage_rows(bundle, lens, pathway)
    if not rows:
        return status_figure(bundle, "The sub-process breakdown is being calculated.")
    signed = defaultdict(float)
    for r in rows:
        signed[(r["system"], r["stage"], r["sign"])] += float(r["score"])
    cell = sensitivity_cell(bundle, electricity, fuel_share) if prototype else None
    overview_rows = cell["contributions"] if cell else rows
    overview_totals = cell["totals"] if cell else None
    if prototype:
        # The overview stacks all stages together, retaining burdens and credits
        # separately. Include its envelope in the common scale, not just nets.
        for r in overview_rows:
            signed[(r["system"], "overview", r["sign"])] += float(r["score"])
    low = min([0, *[v for (*_, sign), v in signed.items() if sign == "negative"]])
    high = max([0, *[v for (*_, sign), v in signed.items() if sign == "positive"]])
    bounds = [floor(low / 100) * 100 - 50, ceil(high / 100) * 100 + 50]
    fig = make_subplots(rows=1, cols=4 if prototype else 3, shared_yaxes=True,
                        horizontal_spacing=0.045 if prototype else 0.065)
    totals = {
        s: sum(float(r["score"]) for r in rows if r["system"] == s) for s in SYSTEMS
    }
    for panel, system in enumerate(SYSTEMS, 1):
        local = [r for r in rows if r["system"] == system]
        for label, sign in sorted({(r["subprocess"], r["sign"]) for r in local}):
            values = [
                sum(
                    float(r["score"])
                    for r in local
                    if r["subprocess"] == label
                    and r["sign"] == sign
                    and r["stage"] == stage
                )
                for stage in STAGES
            ]
            if not any(values):
                continue
            fig.add_trace(
                go.Bar(
                    x=list(range(len(STAGES))),
                    y=values,
                    name=label,
                    marker_color=color_for(label),
                    marker_line_width=0,
                    legendgroup=label,
                    showlegend=False,
                    customdata=list(STAGES),
                    hovertext=[f"{system} · {STAGE_LABELS[stage]}" for stage in STAGES],
                    hovertemplate="<b>%{fullData.name}</b><br>%{hovertext}<br>%{y:+,.0f} kg CO₂-eq/t clinker<extra></extra>",
                ),
                row=1,
                col=panel,
            )
        axis = "yaxis" + (str(panel) if panel > 1 else "")
        top = fig.layout[axis].domain[1]
        x_domain = fig.layout["xaxis" + (str(panel) if panel > 1 else "")].domain
        fig.add_annotation(
            x=x_domain[0],
            y=top,
            xref="paper",
            yref="paper",
            xanchor="left",
            yanchor="bottom",
            yshift=5,
            text=f"<b>{system}</b>" + (" · reference" if prototype and system == "BAU" else " · no investment" if system == "BAU" else ""),
            showarrow=False,
            font_size=12 if prototype else 13,
        )
        fig.add_annotation(
            x=x_domain[1],
            y=top,
            xref="paper",
            yref="paper",
            xanchor="right",
            yanchor="bottom",
            yshift=5,
            text=f"GWP100 <b>{totals[system]:,.0f}</b>" + ("" if prototype else " kg CO₂-eq/t"),
            showarrow=False,
            font_size=13,
        )
        fig.update_yaxes(
            range=bounds,
            dtick=500,
            tickfont_size=11,
            gridcolor="#dce5e8",
            zeroline=True,
            zerolinecolor="#647b86",
            zerolinewidth=1.2,
            showticklabels=True,
            row=1,
            col=panel,
        )
        fig.update_xaxes(
            range=[-0.6, 8.6], tickvals=list(range(len(STAGES))),
            ticktext=[{"clinker":"Kiln CO₂", "raw_materials":"Materials", "kiln_fuels":"Kiln fuels",
                       "heat_recovery":"Heat", "storage":"Storage", "hydrogen":"H₂", "synthetic_fuel":"Fuel conversion"}.get(s, STAGE_LABELS[s]) for s in STAGES], showticklabels=True,
            tickangle=-45, tickfont_size=12, showgrid=False, fixedrange=False,
            row=1, col=panel,
        )
        fig.add_vrect(
            x0=STAGES.index(selected) - 0.42, x1=STAGES.index(selected) + 0.42,
            fillcolor="#e7ecdc", opacity=0.5, line_width=0, layer="below", row=1, col=panel,
        )
    if prototype:
        for label, sign in sorted({(r["subprocess"], r["sign"]) for r in overview_rows}):
            local = [r for r in overview_rows if r["subprocess"] == label and r["sign"] == sign]
            values = [sum(float(r["score"]) for r in local if r["system"] == s) for s in SYSTEMS]
            fig.add_trace(go.Bar(
                x=list(SYSTEMS), y=values, name=label, marker_color=color_for(label),
                showlegend=False, customdata=[None] * 3,
                hovertemplate="<b>%{fullData.name}</b><br>%{x} · sensitivity<br>%{y:+,.0f} kg CO₂-eq/t clinker<extra></extra>",
            ), row=1, col=4)
        fig.add_trace(go.Scatter(
            x=list(SYSTEMS), y=[overview_totals[s] if overview_totals else totals[s] for s in SYSTEMS], mode="markers+text",
            text=[f"{(overview_totals or totals)[s]:,.0f}" for s in SYSTEMS], textposition="top center",
            marker=dict(symbol="diamond", color="#17313b", size=8, line=dict(color="white", width=1)),
            name="Net total", showlegend=False, hoverinfo="none",
        ), row=1, col=4)
        fig.update_yaxes(range=bounds, dtick=500, tickfont_size=11, gridcolor="#dce5e8",
                         zerolinecolor="#647b86", showticklabels=True, row=1, col=4)
        fig.update_xaxes(tickfont_size=12, showgrid=False, row=1, col=4)
        source_label = {"ENC market": "REMIND-EU market", "photovoltaic": "PV"}.get(electricity, electricity)
        fig.add_annotation(x=fig.layout.xaxis4.domain[0], y=1, xref="paper", yref="paper",
                           text=f"<b>Sensitivity · {source_label} · {fuel_share}%</b>", showarrow=False,
                           xanchor="left", yanchor="bottom", yshift=5, font_size=12)
        fig.add_annotation(x=sum(fig.layout.xaxis4.domain)/2, y=0, xref="paper", yref="paper",
                           text=("Selected sensitivity case · ◆ total" if cell else
                                 "2025 baseline only · sensitivity grid unavailable"),
                           showarrow=False, yanchor="top", yshift=-31,
                           font=dict(size=11, color="#90631c"), bgcolor="#fff5e2", borderpad=5)
    baseline_share = bundle.payloads.get("current_static_sensitivity", {}).get("baseline_non_fossil_energy_percent")
    baseline_label = f" · {baseline_share:.1f}% non-fossil fuel energy" if baseline_share is not None else " · original fuel blend"
    fig.add_annotation(x=0, y=1, yshift=34, yanchor="bottom", xref="paper", yref="paper", xanchor="left",
                       text="Fixed baseline panels"+baseline_label, showarrow=False,
                       font=dict(size=12, color="#52727e"))
    fig.update_yaxes(
        title=dict(text="kg CO₂-eq / t clinker", font=dict(size=11), standoff=5),
        automargin=True,
    )
    fig.update_layout(
        height=465,
        autosize=True,
        barmode="relative",
        bargap=0.25,
        margin=dict(l=68, r=16, t=55, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f3f6f7",
        font=dict(family="Arial, Helvetica, sans-serif", size=12, color="#0b3b52"),
        hovermode="closest",
        hoverlabel=dict(bgcolor="white", bordercolor="#b9cbd3",
                        font=dict(size=12, color="#173d50"), namelength=-1),
        dragmode="zoom",
        uirevision=selected,
        meta={"scenario_totals": totals, "sensitivity_totals": overview_totals,
              "shared_y_range": bounds, "sensitivity_prototype": prototype},
    )
    return fig


def compact_subprocess_key(bundle, selected="synthetic_fuel", lens="current_static", pathway="SSP2-NPi"):
    labels = sorted({r["subprocess"] for r in stage_rows(bundle, lens, pathway)
                     if r["stage"] == selected and abs(float(r["score"])) > 1e-9})
    return html.Div([html.Span([html.I(style={"backgroundColor": color_for(label)}), label])
                     for label in labels], className="static-compact-legend")


def subprocess_key(bundle, selected="synthetic_fuel"):
    rows = [r for r in stage_rows(bundle) if r["stage"] == selected]
    if not rows:
        return html.P("Sub-process results pending.")
    labels = sorted(
        {r["subprocess"] for r in rows if abs(float(r["score"])) > 1e-9},
        key=lambda label: -max(
            abs(float(r["score"])) for r in rows if r["subprocess"] == label
        ),
    )
    return html.Div(
        [
            html.Div(
                [html.Span("Sub-process"), *[html.B(s) for s in SYSTEMS]],
                className="subprocess-key-row subprocess-key-head",
            ),
            *[
                html.Div(
                    [
                        html.Span(
                            [html.I(style={"backgroundColor": color_for(label)}), label]
                        ),
                        *[
                            html.Span(
                                (
                                    whole_score(
                                        sum(
                                            float(r["score"])
                                            for r in rows
                                            if r["subprocess"] == label
                                            and r["system"] == system
                                        )
                                    )
                                    if any(
                                        r["system"] == system
                                        and r["subprocess"] == label
                                        for r in rows
                                    )
                                    else "–"
                                ),
                                **{"data-system": system},
                            )
                            for system in SYSTEMS
                        ],
                    ],
                    className="subprocess-key-row",
                )
                for label in labels
            ],
        ],
        className="subprocess-key-table",
    )
