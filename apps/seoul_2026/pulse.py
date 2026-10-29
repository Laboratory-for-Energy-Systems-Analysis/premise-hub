"""A fixed-inventory pulse-equivalence teaching experiment.

Uses only stored marginal CO2 pulse responses, never the older full-project
results. Ratios of median response areas are labelled as illustrations, not
configuration-first ensemble equivalents for the four technologies.
"""

from dash import dcc, html
import numpy as np
from plotly.subplots import make_subplots

from apps.lca_time.workshop.results import co2_reference_pulse_series
from . import comparison as compare

DEFAULT_WINDOW = (2020, 2030, 2100)


def window_figure(window=DEFAULT_WINDOW):
    start, reference_year, end = map(int, window)
    if not (2000 <= start < reference_year < end <= 2300) or any(y % 5 for y in (start, reference_year, end)):
        raise ValueError("Choose three increasing five-year dates from 2000 to 2300")
    first = dict(co2_reference_pulse_series("radiative forcing", 50, 2030))
    second = dict(co2_reference_pulse_series("radiative forcing", 50, 2080))
    reference = dict(co2_reference_pulse_series("radiative forcing", 50, reference_year))
    years = np.array(sorted(first.keys() & second.keys() & reference.keys()))
    if not set(range(start, end + 1)) <= set(years):
        raise ValueError("Stored pulse responses do not cover the selected window")
    net = np.array([1000 * (first[y] - second[y]) for y in years])
    unit = np.array([reference[y] for y in years])
    mask = (years >= start) & (years <= end)
    integrate = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    numerator = float(integrate(net[mask], years[mask]))
    denominator = float(integrate(unit[mask], years[mask]))
    if denominator <= 0:
        raise ValueError("The reference pulse must have a positive integrated response")
    equivalent = numerator / denominator
    scaled = unit * equivalent
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=.08,
                        subplot_titles=("Response of the fixed pulse pair", f"Equivalent pulse in {reference_year}"))
    for col, values, colour in ((1, net, "#173747"), (2, scaled, "#3292b5")):
        fig.add_scatter(x=years, y=values * 1e12, mode="lines", line=dict(color=colour, width=3),
                        name="Two-pulse response" if col == 1 else "Scaled reference response",
                        hovertemplate="%{x}<br>%{y:.3f} pW/m²<extra></extra>", row=1, col=col)
        for positive, fill in ((True, "rgba(193,138,27,.28)"), (False, "rgba(0,138,130,.22)")):
            fig.add_scatter(x=years[mask], y=np.maximum(values[mask], 0) * 1e12 if positive else np.minimum(values[mask], 0) * 1e12,
                            mode="lines", line=dict(width=0), fill="tozeroy", fillcolor=fill,
                            hoverinfo="skip", showlegend=False, row=1, col=col)
        fig.add_vline(x=start, line_dash="dot", line_color="#829ba7", row=1, col=col)
        fig.add_vline(x=end, line_dash="dot", line_color="#829ba7", row=1, col=col)
    fig.add_vline(x=reference_year, line_dash="dash", line_color="#3292b5", row=1, col=2)
    compare.style(fig, ytitle="Δ forcing · pW/m²")
    fig.update_yaxes(title_text=None, row=1, col=2)
    visible = (years >= min(start, 2020)) & (years <= min(2300, max(end + 10, 2110)))
    low = min(float(net[visible].min()), float(scaled[visible].min()), 0)
    high = max(float(net[visible].max()), float(scaled[visible].max()), 0)
    padding = max((high - low) * .15, .1e-12)
    fig.update_yaxes(range=[(low - padding) * 1e12, (high + padding) * 1e12])
    fig.update_xaxes(range=[min(start, 2020), min(2300, max(end + 10, 2110))], title="Calendar year")
    fig.update_layout(margin=dict(l=60, r=15, t=32, b=38), meta=dict(
        status="illustrative marginal pulse superposition", equivalent_kg=equivalent,
        window_start=start, reference_year=reference_year, window_end=end,
        system_area=numerator, reference_area_per_kg=denominator,
        matched_reference_area=float(integrate(scaled[mask], years[mask])),
        equivalent_basis="ratio of median response areas; not an ensemble quantile",
        fixed_inventory={"2030": 1000, "2080": -1000},
        background="SSP2-PkBudg1000",
    ))
    return fig


def window_readout(figure):
    meta = figure.layout.meta
    value = meta["equivalent_kg"]
    return html.Div(
        [
            html.Div([html.Span("EQUIVALENT REFERENCE PULSE"), html.Strong(f"{value:+,.0f} kg CO₂-pulse-eq")], className="equivalence-score"),
            html.Div([
                html.Strong(f"Window {meta['window_start']}–{meta['window_end']} · pulse {meta['reference_year']}"),
                html.Span("Same signed area; different climate trajectories."),
            ], className="equivalence-reading"),
        ], className="equivalence-readout",
    )


def explorer(print_mode=False):
    fig = window_figure()
    control = html.Div("Start 2020 · reference pulse 2030 · end 2100", className="print-selection") if print_mode else html.Div(
        [html.Div([html.Span("1 · Window start"), html.Span("2 · Reference pulse"), html.Span("3 · Window end")], className="window-labels"),
         dcc.RangeSlider(id="equivalence-window", min=2000, max=2300, step=5,
                         value=list(DEFAULT_WINDOW), allowCross=False, pushable=5,
                         marks={y: str(y) for y in (2000, 2050, 2100, 2200, 2300)},
                         tooltip={"placement": "bottom", "always_visible": False})],
        className="window-control",
    )
    return html.Div(
        [
            html.Div([html.Strong("Fixed example: +1 t CO₂ in 2030, −1 t in 2080"),
                      html.Span("GWP100 stays zero · illustrative median marginal responses · SSP2-PkBudg1000")], className="method-message pulse-example-heading"),
            control,
            compare.graph(fig, None if print_mode else "equivalence-chart"),
            html.Div(window_readout(fig), **({} if print_mode else {"id": "equivalence-readout"})),
        ], className="method-page equivalence-explorer",
        **{"data-reused-from": "/setac-2026/ · pulse window interaction; /lca-time/ · marginal CO2 pulse curves"},
    )
