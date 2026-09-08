"""Read-only presentation of precomputed, exact-identity background scores."""
import csv
import hashlib
import json
import math
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .background_identity import indicator_identity

APP = Path(__file__).resolve().parents[1]
YEARS = (2020, 2025, 2030, 2035, 2040, 2050)
PATHWAYS = ("SSP2-NPi", "SSP2-PkBudg1000")
METHOD = ("IPCC 2021 (incl. biogenic CO2) no LT - climate change: total "
          "(incl. biogenic CO2) no LT - global warming potential (GWP100) no LT")
UNITS = {"kilowatt hour": "kWh", "megajoule": "MJ", "kilogram": "kg",
         "ton kilometer": "t·km", "tonne kilometer": "t·km"}


def load_scores(root=APP):
    path = root / "generated/results/background_gwp_six_years.json"
    portable = root / "data/runtime/background_gwp_six_years.json"
    if portable.exists():
        path = portable
    try:
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != path.with_suffix(".sha256").read_text().strip():
            return []
        artifact = json.loads(payload)
        mixes = root / "data/processed/scenario_sector_mixes.csv"
        if (artifact["method"] != METHOD or artifact["ei_version"] != "3.12"
                or artifact["year_policy"] != "exact package anchors"
                or artifact["mix_source_sha256"] != hashlib.sha256(mixes.read_bytes()).hexdigest()):
            return []
        packages = {r["pathway"]: r["sha256"] for r in json.loads(
            (root / "data/public/source_manifest.json").read_text())["trails_packages"]}
        with mixes.open(newline="") as stream:
            identities = {(r["pathway"], r["sector"], *indicator_identity(r))
                          for r in csv.DictReader(stream)}
        rows = artifact["rows"]
        keys = set()
        for r in rows:
            key = (r["pathway"], r["sector"], r["year"])
            identity = tuple(r[k] for k in ("pathway", "sector", "activity_name",
                                           "reference_product", "activity_unit", "location"))
            if (key in keys or r["year"] not in YEARS or identity not in identities
                    or r["package_sha256"] != packages.get(r["pathway"])
                    or not math.isfinite(float(r["score"]))):
                return []
            keys.add(key)
        return rows
    except (OSError, ValueError, KeyError, TypeError):
        return []


def available(sector, rows):
    return {(r["pathway"], r["year"]) for r in rows if r["sector"] == sector} == {
        (p, y) for p in PATHWAYS for y in YEARS}


def gwp_figure(sector, rows):
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=.13, subplot_titles=PATHWAYS)
    selected = [r for r in rows if r["sector"] == sector]
    if not available(sector, rows):
        fig.add_annotation(text="Matching GWP scores are not yet available", x=.5, y=.5,
                           xref="paper", yref="paper", showarrow=False)
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return fig
    unit = "kg CO₂-eq / " + UNITS.get(selected[0]["activity_unit"], selected[0]["activity_unit"])
    values = [float(r["score"]) for r in selected]
    lower, upper = min(0, min(values)), max(0, max(values))
    span = max(upper-lower, .001)
    limits = [lower - (.12*span if lower < 0 else 0), upper+.2*span]
    for col, pathway in enumerate(PATHWAYS, 1):
        points = sorted((r for r in selected if r["pathway"] == pathway), key=lambda r:r["year"])
        fig.add_trace(go.Bar(x=list(range(len(YEARS))), y=[float(r["score"]) for r in points],
            marker_color="#6f818a" if col == 1 else "#008a82", name=pathway,
            texttemplate="%{y:.3f}", textposition="outside", textfont=dict(size=10), cliponaxis=False,
            customdata=[[r["year"], r["activity_name"], r["location"], unit] for r in points],
            hovertemplate="<b>%{fullData.name} · %{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]}<br>%{y:.3f} %{customdata[3]}<extra></extra>"),row=1,col=col)
        focus = YEARS.index(2035)
        fig.add_vrect(x0=focus-.42, x1=focus+.42, fillcolor="#e5eee9",opacity=.6,line_width=0,layer="below",row=1,col=col)
        fig.update_xaxes(tickvals=list(range(len(YEARS))),ticktext=["<b>2035</b>" if y == 2035 else str(y) for y in YEARS],tickfont=dict(size=11),range=[-.6,len(YEARS)-.4],fixedrange=True,row=1,col=col)
        fig.update_yaxes(range=limits,nticks=5,tickformat=".3f",gridcolor="#e0e8ea",zerolinecolor="#9baeb8",fixedrange=True,row=1,col=col)
    fig.update_layout(autosize=True,bargap=.48,showlegend=False,
        margin=dict(l=45,r=10,t=58,b=35),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial",size=13,color="#214659"),
        meta={"sector":sector,"metric":"gwp","unit":unit,"years":list(YEARS)})
    fig.add_annotation(text=unit,x=0,y=1.22,xref="paper",yref="paper",xanchor="left",showarrow=False,font=dict(size=12))
    return fig
