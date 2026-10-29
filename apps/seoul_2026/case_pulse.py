"""Four real project curves matched to dated, background-consistent CO2 pulses.

This teaching view matches areas of displayed median trajectories. It does not
present ratios of medians as configuration-first ensemble pulse equivalents.
"""

from functools import lru_cache
import hashlib
import json
from pathlib import Path

from dash import dcc, html
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from apps.setac_2026 import results
from . import comparison as compare
from .erw_campaign import campaign_results
from .visuals import CASES, CASE

DEFAULT_WINDOW = (2020, 2030, 2100)
ERW_REFERENCE_SHA256 = "449ad8f97208481d3377fb60c9fea16f3d169e0f2f04b5180b9ca6a482f6f99d"
DATA = Path(__file__).resolve().parent / "data"


@lru_cache(maxsize=1)
def erw_references():
    path = DATA / "erw_reference_pulses.json"
    if hashlib.sha256(path.read_bytes()).hexdigest() != ERW_REFERENCE_SHA256:
        raise ValueError("ERW reference curves differ from the checked calculation")
    data = json.loads(path.read_text())
    campaign = campaign_results()
    if (data["fair_input_hashes"] != campaign["fair_input_hashes"]
            or data["trails_version"] != campaign["trails"]
            or data["scenario"] != "REMIND|SSP2-EU21-PkBudg1000"
            or data["config_count"] != 841
            or set(data["pulses"]) != {str(y) for y in range(2005,2200,5)}):
        raise ValueError("ERW reference background/settings do not match its stored project")
    return data


@lru_cache(maxsize=1)
def released_references():
    """Recover native half-year coordinates and normalize the released +1 t pulse.

    The SETAC CSV rounded reference dates down to integer years. Its 2030 pulse
    is numerically identical to the cement export at native half-year dates,
    after the latter's 1 t reference is divided by 1,000. Check that identity.
    """
    grouped = {}
    for row in compare.cement_bundle().tables["pulse_reference"]:
        if row["metric"] == "radiative_forcing":
            grouped.setdefault(int(row["reference_year"]), []).append(
                (float(row["year"]), float(row["value"])/1000))
    grouped = {year:tuple(sorted(points)) for year,points in grouped.items()}
    native = dict(grouped[2030])
    checked = 0
    for row in results.co2_reference_pulse_rows():
        if row["metric"] != "radiative forcing" or float(row["quantile"]) != 50:
            continue
        if int(row["pulse_year"]) != 2030:
            continue
        year = float(row["response_year"])+.5
        if year in native:
            if not np.isclose(native[year],float(row["value_per_kg_co2_pulse"]),rtol=1e-10,atol=1e-28):
                raise ValueError("SETAC and cement reference pulse conventions no longer agree")
            checked += 1
    if checked < 200:
        raise ValueError("Insufficient overlap to check the released pulse normalization")
    return grouped


def reference_series(case, reference_year):
    if case == "ERW":
        points = erw_references()["pulses"][str(reference_year)]
    else:
        points = released_references()[reference_year]
    return [(float(y),float(v)*1e12) for y,v in points]  # pW/m² per kg CO2


def validate_window(window):
    start, reference_year, end = map(int, window)
    if not (2000 <= start < reference_year < end <= 2200) or any(
            y % 5 for y in (start,reference_year,end)):
        raise ValueError("Choose increasing five-year dates from 2000 to 2200")
    return start, reference_year, end


def case_window_figure(case, window=DEFAULT_WINDOW):
    start, reference_year, end = validate_window(window)
    anchor = 2035 if case == "Cement + CCS" else 2030
    project = [(age+anchor,value) for age,value in compare.forcing_series(case)]
    reference = reference_series(case,reference_year)
    system_area = compare.integrated_forcing(project,start,end)
    unit_area = compare.integrated_forcing(reference,start,end)
    if not np.isfinite(unit_area) or unit_area <= 0:
        raise ValueError("Reference pulse must have a positive integrated response")
    equivalent = system_area/unit_area
    scaled = [(year,value*equivalent) for year,value in reference]
    colour = CASE[case]["colour"]
    rgb = ",".join(str(int(colour[i:i+2],16)) for i in (1,3,5))
    fig = go.Figure()
    fig.add_scatter(x=[y for y,v in project],y=[v for y,v in project],mode="lines",
                    line=dict(color=colour,width=3),fill="tozeroy",fillcolor=f"rgba({rgb},.16)",
                    name="Project response",hovertemplate="%{x:.1f}<br>Project: %{y:.3f} pW/m²<extra></extra>")
    fig.add_scatter(x=[y for y,v in scaled],y=[v for y,v in scaled],mode="lines",
                    line=dict(color="#173747",width=2.3,dash="dash"),name="Area-matched CO₂ pulse",
                    hovertemplate="%{x:.1f}<br>Matched pulse: %{y:.3f} pW/m²<extra></extra>")
    fig.add_vline(x=reference_year,line_dash="dot",line_color="#829ba7",line_width=1)
    compare.style(fig,ytitle="ΔRF · pW/m²")
    visible = [v for series in (project,scaled) for y,v in series if start <= y <= end]
    low,high = min(visible+[0]),max(visible+[0])
    pad = max((high-low)*.15,.04)
    fig.update_yaxes(range=[low-pad,high+pad])
    ticks = sorted({start,end}|{y for y in range(2000,2201,50) if start < y < end})
    fig.update_xaxes(range=[start,end],title="Calendar year",tickvals=ticks,
                     ticktext=[str(y) for y in ticks],tickfont=dict(size=11))
    fig.update_layout(margin=dict(l=48,r=25,t=8,b=42),meta=dict(
        case=case,project_start=anchor,native_service=CASE[case]["service"],
        window_start=start,reference_year=reference_year,window_end=end,
        system_area=system_area,reference_area_per_kg=unit_area,
        matched_reference_area=compare.integrated_forcing(scaled,start,end),
        area_unit="pW·year/m²",equivalent_kg=equivalent,
        equivalent_basis="ratio of displayed median response areas; not an ensemble quantile",
        background="REMIND|SSP2-EU21-PkBudg1000" if case=="ERW" else "REMIND|SSP2-PkBudg1000",
        status="illustrative area match of stored case and reference curves",
    ))
    return fig


def window_readout(figure):
    meta = figure.layout.meta
    return [html.Span("Area-matched reference pulse"),
            html.Strong(f"≈ {meta['equivalent_kg']:+,.0f}".replace("-","−")),
            html.Small("kg CO₂-pulse-eq"),
            html.Span(f"Both areas: {meta['system_area']:+,.2f} pW·year/m²".replace("-","−"),
                      className="case-pulse-area")]


def explorer(print_mode=False):
    control = html.Div("Start 2020 · CO₂ pulse 2030 · end 2100",className="print-selection") if print_mode else html.Div([
        html.Div([html.Span("1 · Window start"),html.Span("2 · Reference pulse"),html.Span("3 · Window end")],className="window-labels"),
        dcc.RangeSlider(id="equivalence-window",min=2000,max=2200,step=5,value=list(DEFAULT_WINDOW),
                        allowCross=False,pushable=5,marks={y:str(y) for y in (2000,2050,2100,2150,2200)},
                        tooltip={"placement":"bottom","always_visible":False}),
    ],className="window-control")
    panels=[]
    for i,case in enumerate(CASES):
        fig=case_window_figure(case)
        panels.append(html.Article([
            compare.case_heading(case,"2035 · CCS − BAU" if case=="Cement + CCS" else
                                 "2030–2049 campaign" if case=="ERW" else "2030 cohort",
                                 combined=True,show_origin_key=False),
            html.Div(window_readout(fig),className="case-pulse-readout",
                     **({"id":f"case-equivalence-readout-{i}"} if not print_mode else {})),
            compare.graph(fig,None if print_mode else f"case-equivalence-{i}"),
        ],className="comparison-panel",style={"--case-colour":CASE[case]["colour"]},**{"data-case":case}))
    return html.Div([
        html.Div([html.Strong("Match each project’s signed area with a dated CO₂ pulse"),
                  html.Span("Illustrative curve matches · native climate background for each case")],className="case-pulse-message"),
        control,
        html.Div([html.Span([html.I(className="case-pulse-project-key"),"Project response"]),
                  html.Span([html.I(className="case-pulse-reference-key"),"Area-matched CO₂ pulse"]),
                  html.Output("2020–2100 · pulse 2030",**({} if print_mode else
                              {"id":"case-equivalence-window-summary"}))],className="case-pulse-legend"),
        html.Div(panels,className="comparison-grid",**{"data-comparison":"case-pulse-equivalence"}),
    ],className="method-page case-equivalence-explorer")


def method_figure():
    """Explain the mapping with the four real default curves, on paired scales."""
    fig=make_subplots(rows=4,cols=2,horizontal_spacing=.32,vertical_spacing=.08)
    for row,case in enumerate(CASES,1):
        source=case_window_figure(case)
        meta=source.layout.meta
        colour=CASE[case]["colour"]
        project=go.Scatter(source.data[0]);project.showlegend=False
        pulse=go.Scatter(source.data[1]);pulse.showlegend=False
        pulse.fill="tozeroy";pulse.fillcolor=project.fillcolor
        fig.add_trace(project,row=row,col=1);fig.add_trace(pulse,row=row,col=2)
        for col in (1,2):
            fig.update_yaxes(range=source.layout.yaxis.range,showticklabels=False,
                             showgrid=False,zeroline=True,zerolinecolor="#aec5cf",row=row,col=col)
            fig.update_xaxes(range=[DEFAULT_WINDOW[0],DEFAULT_WINDOW[2]],showticklabels=row==4,
                             tickvals=[2020,2050,2100],tickfont=dict(size=12),showgrid=False,
                             title_text="Calendar year" if row==4 else None,row=row,col=col)
            fig.add_vline(x=2030,line_dash="dot",line_color="#9bb2bf",line_width=1,row=row,col=col)
        axis=fig.layout["yaxis" if row==1 else f"yaxis{2*row-1}"]
        low,high=axis.domain;middle=(low+high)/2
        fig.add_annotation(x=-.012,y=middle,xref="paper",yref="paper",text=case,
                           xanchor="right",yanchor="middle",showarrow=False,font=dict(size=18,color=colour))
        area_text=f"{meta['system_area']:+.2f}".replace("-","−")
        mass_text=f"{meta['equivalent_kg']:+,.0f}".replace("-","−")
        fig.add_annotation(x=.5,y=middle,xref="paper",yref="paper",yanchor="middle",showarrow=False,
                           text=f"{area_text}<br><span style='font-size:13px'>pW·year/m²</span>",
                           bgcolor="#edf5f4",borderpad=7,font=dict(size=21,color=colour))
        fig.add_annotation(x=.99,y=high+.015,xref="paper",yref="paper",xanchor="right",yanchor="bottom",showarrow=False,
                           text=f"≈ {mass_text} kg CO₂-pulse-eq",
                           font=dict(size=15,color=colour))
        for x in (.42,.65):
            fig.add_annotation(x=x,y=middle,ax=-65,ay=0,xref="paper",yref="paper",
                               axref="pixel",ayref="pixel",text="",showarrow=True,
                               arrowhead=3,arrowwidth=1.7,arrowcolor="#6f929f")
    compare.style(fig)
    for x,title in ((.17,"1 · Dated project response"),(.5,"2 · Signed area"),(.83,"3 · Scale a dated CO₂ pulse")):
        fig.add_annotation(x=x,y=1.12,xref="paper",yref="paper",text=title,showarrow=False,
                           font=dict(size=17,color="#173747"))
    fig.update_layout(margin=dict(l=155,r=25,t=56,b=40),
                       meta=dict(kind="four-case-method",case_order=list(CASES),window=list(DEFAULT_WINDOW)))
    return fig


def method_overview(print_mode=False):
    return html.Div([
        html.Div([html.Strong("Equal signed areas, different trajectories"),
                  html.Span("Within each row: same background, calendar window and vertical scale.")],className="case-method-heading"),
        html.Div([html.Span("Window 2020–2100"),html.Span("CO₂ reference pulse in 2030"),
                  html.Span("Illustrative matches of displayed curves")],className="case-method-settings"),
        html.Div(compare.graph(method_figure()),className="case-method-graphic"),
    ],className="case-equivalence-method")
