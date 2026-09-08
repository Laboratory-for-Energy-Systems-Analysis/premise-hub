"""Display of reviewed public prospective result grids."""

import plotly.graph_objects as go

from ..lca_model.results import ResultBundle
from .static_stages import render_stage_comparison, sensitivity_cell, STAGES

PATHWAYS = ("SSP2-NPi", "SSP2-PkBudg1000")
YEARS = (2035, 2050)


def reference_segments(values, labels):
    """One bar-width horizontal segment per value, separated by explicit gaps."""
    x, y, names = [], [], []
    for position, (value, label) in enumerate(zip(values, labels)):
        x.extend([position - .375, position + .375, None])
        y.extend([value, value, None])
        names.extend([label, label, None])
    return dict(x=x, y=y, customdata=names, connectgaps=False)


def load_prospective_bundle(year=2035, pathway="SSP2-NPi"):
    from .release import load_release_bundle
    released = load_release_bundle(f'{year}-{pathway}')
    if released is not None:
        return released
    return ResultBundle('stale', 'public-release-missing',
                        'The public prospective result bundle is unavailable.', {}, {})

def prospective_figure(bundle, current, selected, pathway, electricity, share, reference=False):
    fig = render_stage_comparison(bundle, selected, "prospective_static", pathway,
                                 prototype=True, electricity=electricity, fuel_share=share)
    if not fig.data:
        return fig
    fig.layout.meta["year"] = bundle.payloads["current_static_sensitivity"]["year"]
    fig.layout.meta["pathway"] = pathway
    if not reference or current.status == "invalidated":
        return fig
    rows = current.tables.get("static_subprocesses", ())
    cell = sensitivity_cell(current, electricity, share)
    if not rows or not cell:
        return fig
    reference_fig = render_stage_comparison(current, selected, prototype=True,
                                            electricity=electricity, fuel_share=share)
    for panel, system in enumerate(("BAU", "CCS", "CCUS"), 1):
        values = [sum(float(r["score"]) for r in rows if r["system"] == system and r["stage"] == stage) for stage in STAGES]
        fig.add_trace(go.Scatter(**reference_segments(values, STAGES), mode="lines",
            line=dict(color="#c43737",width=2,dash="dash"),
            name="2025 net stage score", showlegend=False,
            hovertemplate="2025 · SSP2-NPi · baseline net stage<br>%{customdata}<br>%{y:,.0f} kg CO₂-eq/t clinker<extra></extra>"),row=1,col=panel)
    # Use numeric category centres so segments span individual bars, not systems.
    systems = ("BAU", "CCS", "CCUS")
    for trace in fig.data:
        if trace.xaxis == "x4":
            trace.hovertext = list(trace.x)
            trace.x = [systems.index(s) for s in trace.x]
            if trace.hovertemplate:
                trace.hovertemplate = trace.hovertemplate.replace("%{x}", "%{hovertext}")
    fig.update_xaxes(type="linear", tickvals=[0,1,2], ticktext=list(systems),
                     range=[-.6,2.6], row=1, col=4)
    fig.add_trace(go.Scatter(**reference_segments([cell["totals"][s] for s in systems], systems),mode="lines",
        line=dict(color="#c43737",width=2,dash="dash"),name="2025 sensitivity",showlegend=False,
        hovertemplate="2025 · SSP2-NPi · selected sensitivity<br>%{customdata}<br>%{y:,.0f} kg CO₂-eq/t clinker<extra></extra>"),row=1,col=4)
    limits = [min(fig.layout.yaxis.range[0], reference_fig.layout.yaxis.range[0]),
              max(fig.layout.yaxis.range[1], reference_fig.layout.yaxis.range[1])]
    fig.update_yaxes(range=limits)
    fig.layout.meta["reference_year"] = 2025
    fig.layout.meta["shared_y_range"] = limits
    return fig
