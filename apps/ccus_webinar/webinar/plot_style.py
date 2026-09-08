"""Shared lca_time presentation grammar, independent of the LCA calculations."""

from collections import defaultdict
from math import floor, log10

INK = "#0b3b52"
RED = "#c44e52"
SYSTEMS = ("BAU", "CCS", "CCUS")
LEGEND_ORDER = (
    "Clinker",
    "Raw materials",
    "Kiln fuels",
    "Heat balance",
    "Capture",
    "Storage chain",
    "Hydrogen",
    "Methanol",
    "Methanol-to-X",
    "Infrastructure",
    "Other",
    "Cumulative GWP100",
    "Median response",
    "BAU benchmark",
)


def rgba(color: str, opacity: float) -> str:
    if isinstance(color, str) and color.startswith("#") and len(color) == 7:
        rgb = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
        return f"rgba({rgb[0]},{rgb[1]},{rgb[2]},{opacity})"
    return color


def _ticks(extent):
    target = extent * 0.82
    decade = 10 ** floor(log10(target or 1))
    step = max(value * decade for value in (1, 2, 5, 10) if value * decade <= target)
    return [-step, 0, step]


def temporal_style(figure, *, kind, unit, area_mode="stacked"):
    """Style aligned panels and fit axes to the actual signed stack envelopes.

    A single legend is formed from all three systems, not just the BAU panel.
    The browser gets compact net series for an unobscuring shared readout.
    """
    dual = kind != "pulse"
    seen = set()
    annual_bounds = []
    net_bounds = []
    stacks = defaultdict(lambda: defaultdict(float))
    readouts = []
    for trace in figure.data:
        name = trace.name or ""
        trace.legendrank = LEGEND_ORDER.index(name) if name in LEGEND_ORDER else 20
        axis = trace.yaxis or "y"
        axis_number = int(axis[1:] or 1)
        is_net_axis = not dual or axis_number % 2 == 0
        is_net_line = name in {
            "Cumulative GWP100",
            "Median response",
            "CO₂-pulse equivalent",
        }
        is_area = bool(trace.stackgroup) or (trace.fill == "tozeroy")
        is_benchmark = name == "BAU benchmark"
        values = [float(v) for v in trace.y if v is not None]

        if is_area:
            panel = (axis_number - 1) // 2 if dual else axis_number - 1
            trace.meta = {
                "annual": True,
                "system": SYSTEMS[panel],
                "unit": "kg CO₂-eq" + ("/t" if "/t" in unit else ""),
            }
            color = trace.line.color or "#84929a"
            trace.line.width = 1.1 if area_mode == "stacked" else 1.8
            trace.fillcolor = rgba(color, 0.58 if kind == "gwp" else 0.36)
            trace.opacity = 1
            if area_mode != "stacked":
                trace.fillcolor = rgba(color, 0.23)
            if trace.stackgroup:
                for x, y in zip(trace.x, trace.y, strict=True):
                    stacks[(axis, trace.stackgroup)][float(x)] += float(y or 0)
            else:
                annual_bounds.extend(values)
        if is_net_axis:
            net_bounds.extend(values)
        if is_net_line:
            trace.line.color = RED if dual else "#7656a8"
            trace.line.width = 3.6
            trace.legendgroup = "net-response"
            panel = (axis_number - 1) // 2 if dual else axis_number - 1
            if 0 <= panel < 3:
                readouts.append(
                    {
                        "system": SYSTEMS[panel],
                        "x": list(trace.x),
                        "y": list(trace.y),
                        "unit": unit,
                    }
                )
        if is_area or is_net_line or is_benchmark or "FaIR 2.5" in name:
            group = trace.legendgroup or name
            trace.legendgroup = group
            trace.showlegend = group not in seen
            seen.add(group)
        elif not name:
            trace.showlegend = False
        # The fixed readout below the chart replaces floating popups.
        trace.hovertemplate = None
        trace.hoverinfo = "none"
    for stack in stacks.values():
        annual_bounds.extend(stack.values())
    annual_extent = max((abs(v) for v in annual_bounds), default=1) or 1
    net_extent = max((abs(v) for v in net_bounds), default=1) or 1
    for panel in range(1, 4):
        primary = "yaxis" + (
            str(panel * 2 - 1)
            if dual and panel > 1
            else str(panel) if not dual and panel > 1 else ""
        )
        axis = figure.layout[primary]
        axis.update(
            range=[
                -1.12 * (annual_extent if dual else net_extent),
                1.12 * (annual_extent if dual else net_extent),
            ],
            tickfont={"size": 12, "color": "#60757d"},
            nticks=4,
            gridcolor="#dce5e8",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor="#8da0a9",
            title_font={"size": 12},
            tickvals=_ticks(annual_extent if dual else net_extent),
        )
        if dual:
            figure.layout[f"yaxis{panel*2}"].update(
                range=[-net_extent * 1.12, net_extent * 1.12],
                nticks=4,
                tickfont={"size": 12, "color": RED},
                title_font={"size": 12, "color": RED},
                showgrid=False,
                zeroline=False,
                tickvals=_ticks(net_extent),
                tickformat=".3g" if kind == "fair" else ",.0f",
            )
    for annotation in figure.layout.annotations:
        if annotation.text in {"BAU / reference", "CCS", "CCUS"}:
            annotation.update(
                x=0,
                xanchor="left",
                font={"size": 13, "color": INK},
                text=f"<b>{annotation.text}</b>",
            )
    for item in readouts:
        panel = SYSTEMS.index(item["system"]) + 1
        primary = "yaxis" + (
            str(panel * 2 - 1)
            if dual and panel > 1
            else str(panel) if not dual and panel > 1 else ""
        )
        value = item["y"][-1]
        number = f"{value:,.0f}" if "kg" in unit else f"{value:.3g}"
        figure.add_annotation(
            x=figure.layout.xaxis.domain[1],
            y=figure.layout[primary].domain[1],
            xref="paper",
            yref="paper",
            text=f"<b>{number}</b> {unit}",
            showarrow=False,
            xanchor="right",
            yanchor="bottom",
            yshift=3,
            font={"size": 12, "color": RED if dual else "#7656a8"},
        )
    if dual:
        figure.add_vline(
            x=2035,
            line_dash="dot",
            line_color="#728990",
            line_width=1,
            row="all",
            col=1,
        )
    figure.update_xaxes(
        showgrid=True,
        gridcolor="#dce5e8",
        tickfont={"size": 12},
        title_font={"size": 12},
        zeroline=False,
        showspikes=True,
        spikecolor="#829aa4",
        spikethickness=1,
        spikedash="dot",
        spikemode="across",
    )
    figure.update_layout(
        margin={"l": 85, "r": 110 if dual else 38, "t": 62 if dual else 30, "b": 39},
        plot_bgcolor="#f2f6f7",
        paper_bgcolor="rgba(0,0,0,0)",
        legend={
            "orientation": "h",
            "x": 0,
            "xanchor": "left",
            "y": 1.10,
            "yanchor": "bottom",
            "font": {"size": 12},
            "tracegroupgap": 3,
            "groupclick": "togglegroup",
        },
        showlegend=dual,
        hovermode="closest",
        dragmode="zoom",
        meta={"presentation_kind": kind, "readouts": readouts},
    )
    figure.layout.meta["reset_axes"] = {
        key: list(figure.layout[key].range) if figure.layout[key].range else None
        for key in figure.layout
        if key.startswith(("xaxis", "yaxis"))
    }
    return figure


def compact_gwp_legend(figure, *, grouping, negligible_labels, unit):
    """Group legend controls only; retain every numerical layer and hover name."""
    import plotly.graph_objects as go

    groups = {
        "Kiln supply": ("#ac852e", {
            "Raw materials", "Kiln fuels", "Clinker", "Other kiln emissions",
        }),
        "Kiln CO₂": ("#b85f43", {"Kiln CO₂ · fossil", "Kiln CO₂ · non-fossil"}),
        "Captured CO₂": ("#397b9e", {"Captured CO₂ · fossil", "Captured CO₂ · non-fossil"}),
        "CO₂ to storage": ("#397b9e", {"CO₂ to storage · fossil", "CO₂ to storage · non-fossil"}),
        "CO₂ to utilisation": ("#755aa6", {"CO₂ to utilisation · non-fossil"}),
        "Heat balance": ("#2f8f83", {"Heat balance"}),
        "Capture & storage": ("#315b91", {
            "Capture", "Storage chain", "Capture utilities & materials",
            "Storage utilities & transport",
        }),
        "Fuel production & credits": ("#755aa6", {
            "Hydrogen", "Methanol", "Methanol · other burdens", "Methanol-to-X",
            "MTX utilities & fuel credits",
        }),
        "CO₂ releases": ("#dc8391", {
            "Storage CO₂ losses", "Conversion CO₂ release", "Fuel CO₂ release (+1 y)",
        }),
        "Other supply": ("#9aa8ad", {"Infrastructure", "Other"}),
    }
    if grouping == "flow":
        groups = {key: value for key, value in groups.items()
                  if key in {"Kiln CO₂", "Captured CO₂", "CO₂ to storage", "CO₂ to utilisation", "CO₂ releases"}}
        groups.update({
            "Other CO₂": ("#ac852e", set()),
            "Methane": ("#755aa6", set()),
            "Nitrous oxide": ("#2f8f83", set()),
            "Other flows": ("#9aa8ad", set()),
        })
    members = {name: group for group, (_, names) in groups.items() for name in names}
    visible_groups = set()
    for trace in figure.data:
        if trace.name == "Cumulative GWP100":
            trace.legendrank = 100
            continue
        if not (trace.stackgroup or trace.fill == "tozeroy"):
            continue
        group = members.get(trace.name)
        if group is None and grouping == "flow":
            name = trace.name.lower()
            group = ("Other CO₂" if "carbon dioxide" in name or "co₂" in name
                     else "Methane" if "methane" in name or "ch₄" in name
                     else "Nitrous oxide" if "dinitrogen monoxide" in name or "nitrous oxide" in name or "n₂o" in name
                     else "Other flows")
        group = group or "Other supply"
        color = groups[group][0]
        trace.legendgroup = "detail-" + group
        trace.showlegend = False
        trace.line.color = color
        trace.fillcolor = rgba(color, 0.58 if trace.stackgroup else 0.23)
        trace.hoverinfo = None
        trace.hovertemplate = "%{x}<br>%{y:,.0f} " + unit + "<extra>%{fullData.name}</extra>"
        if trace.name.startswith('CO₂ to '):
            trace.hovertemplate = ("%{x}<br>%{y:,.0f} " + unit
                + "<br>Display offset of gross kiln CO₂; not an additional removal."
                + "<br>Losses and later releases remain in their original stages."
                + "<extra>%{fullData.name}</extra>")
        if trace.name not in negligible_labels:
            visible_groups.add(group)
    # Empty proxy traces do not enter stacks, axis fitting, or the net readout.
    for rank, (group, (color, _)) in enumerate(groups.items()):
        if group in visible_groups:
            figure.add_trace(go.Scatter(
                x=[None], y=[None], mode="lines", line={"color": color, "width": 8},
                name="Heat supply & exports" if group == "Heat balance" else group,
                legendgroup="detail-" + group, legendrank=rank,
                showlegend=True, hoverinfo="skip",
            ))
    figure.update_layout(legend_groupclick="togglegroup")
    return figure


def static_style(figure):
    figure.update_layout(
        margin={"l": 90, "r": 60, "t": 74, "b": 52},
        bargap=0.40,
        plot_bgcolor="#f2f6f7",
        font={"family": "Arial, Helvetica, sans-serif", "size": 13, "color": INK},
        legend={
            "orientation": "h",
            "x": 0,
            "xanchor": "left",
            "y": 1.10,
            "yanchor": "bottom",
            "font": {"size": 13},
        },
    )
    for trace in figure.data:
        if trace.type == "bar":
            trace.marker.line.width = 0
            color = trace.marker.color
            trace.marker.color = (
                [rgba(item, 0.70) for item in color]
                if isinstance(color, (list, tuple))
                else rgba(color, 0.70)
            )
        elif trace.mode == "markers+text":
            trace.marker.size = 12
            trace.textfont = {"size": 18, "color": INK}
    figure.update_xaxes(tickfont={"size": 12}, title_font={"size": 13})
    figure.update_yaxes(tickfont={"size": 15})
    return figure
