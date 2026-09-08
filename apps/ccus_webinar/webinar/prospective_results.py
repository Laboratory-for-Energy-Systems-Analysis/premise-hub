"""Explicit local diagnostic preview of newly calculated prospective grids."""
from collections import defaultdict
import json
import os
from pathlib import Path

import plotly.graph_objects as go

from ..lca_model.results import ResultBundle, file_sha256
from .carbon_presentation import gross_kiln_transfer_view
from .static_stages import render_stage_comparison, sensitivity_cell, STAGES

APP = Path(__file__).resolve().parents[1]
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
    background = {}
    try:
        if (os.environ.get("CCUS_WEBINAR_DIAGNOSTIC_PREVIEW") != "mtx-gas-heat"
                or os.environ.get("CCUS_WEBINAR_SHOW_CANDIDATE_RESULTS") != "1"):
            raise ValueError("Prospective diagnostic preview is not enabled")
        from ..lca_model.prospective_grid import validate_grid_payload
        from ..lca_model.pipeline import METHOD
        if year not in YEARS or pathway not in PATHWAYS:
            raise ValueError("Unsupported year or pathway")
        folder = APP / f"generated/results/prospective_diagnostic/{year}/{pathway}"
        manifest = json.loads((folder / "manifest.json").read_text())
        if not manifest.get("diagnostic_only") or not manifest.get("publication_hold"):
            raise ValueError("Missing diagnostic review status")
        if file_sha256(folder / "grid.json") != manifest["output_sha256"]:
            raise ValueError("Prospective grid changed")
        for name, digest in manifest["input_hashes"].items():
            path = (APP / name).resolve()
            if not path.is_relative_to(APP.resolve()) or file_sha256(path) != digest:
                raise ValueError(f"Changed prospective calculation input: {name}")
        for check in ("exact_links", "matrix_coefficients", "forward_adjoint_all_roots", "complete_grid_and_contributions"):
            if manifest["checks"].get(check) != "passed":
                raise ValueError(f"Missing calculation check: {check}")
        grid = json.loads((folder / "grid.json").read_text())
        if grid["year"] != year or grid["pathway"] != pathway or grid["method"] != METHOD:
            raise ValueError("Unexpected prospective result identity")
        validate_grid_payload(grid)
        for row in [*grid["baseline_contributions"], *(r for c in grid["cells"] for r in c["contributions"])]:
            if row.get("stage") == "synthetic_fuel" and row.get("subprocess") == "heat production, natural gas, at industrial furnace low-NOx >100kW":
                row["subprocess"] = "MTX gas-boiler heat"
        grid["baseline_contributions"] = gross_kiln_transfer_view(grid["baseline_contributions"])
        for cell in grid["cells"]:
            cell["contributions"] = gross_kiln_transfer_view(cell["contributions"])
        grid["presentation_decomposition"] = "gross kiln CO2 and equal captured transfers"
        context = dict(lens="prospective_static", pathway=pathway, year=year)
        details = tuple({**r, **context} for r in grid["baseline_contributions"])
        totals = tuple(dict(**context, system=s, score=v) for s,v in grid["baseline_scores"].items())
        return ResultBundle("candidate", f"prospective-{year}-{pathway}",
            "Diagnostic results: engineering review remains open", manifest,
            {"static_subprocesses":details, "static_totals":totals},
            payloads={"current_static_sensitivity":grid})
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ResultBundle("invalidated", "prospective-unavailable", str(exc), {}, background)


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
