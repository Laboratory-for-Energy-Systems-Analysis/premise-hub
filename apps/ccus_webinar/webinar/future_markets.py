"""Scenario snapshots using existing sector-mix data, not new LCA calculations."""
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .diagrams import icon_uri
from .background_gwp import available, load_scores

SECTORS = ("Electricity", "District heat", "Gas", "Steel", "Truck transport", "Cement clinker")
PATHWAYS = ("SSP2-NPi", "SSP2-PkBudg1000")
COLORS = {"Wind": "#36839c", "Solar": "#e5b742", "Hydro": "#80becb",
          "Nuclear": "#989ab5", "Biomass": "#759c68", "Natural gas": "#c19974",
          "Coal and oil": "#6e625d", "Coal": "#605d60", "Oil": "#b47c61",
          "Electric": "#a491c0", "Hydrogen": "#4b9b8b", "Recovered heat": "#81bca5",
          "Other": "#c1cbd0", "Conventional": "#a4b2b9", "CCS": "#347f99",
          "BF–BOF": "#806b60", "BF–BOF + CCS": "#b4997e", "DRI–EAF": "#a3b974",
          "H₂–DRI/EAF": "#438f81", "Scrap EAF": "#70adb7", "Electrowinning": "#a592bc",
          "Diesel truck": "#aa8265", "Battery electric": "#449286",
          "Compressed gas": "#c6af82", "Fuel cell": "#83b3cc",
          "Fossil gas": "#c19974", "Biomethane": "#759c68", "Hydrogen-derived gas": "#4b9b8b"}
CONTEXT = {"Electricity": "Power for capture, electrolysis and synthesis",
           "Gas": "The scenario gas market introduces biomethane into gas-fired electricity and heat",
           "District heat": "The supply displaced by exported surplus heat",
           "Steel": "Materials for plant construction and replacement",
           "Truck transport": "Upstream deliveries of materials and fuels",
           "Cement clinker": "Cement production in the supply database, not the three plants compared here"}


def sector_figure(bundle, sector="Electricity"):
    if sector not in SECTORS:
        sector = "Electricity"
    from .sector_shares import load_sector_shares
    rows = [r for r in load_sector_shares() if r["sector"] == sector]
    if sector == "Gas":
        from .gas_supply import load_gas_shares
        rows = load_gas_shares()
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=.10,
                        subplot_titles=["SSP2-NPi", "SSP2-PkBudg1000"])
    categories = sorted({r["category"] for r in rows})
    years = [2020, 2025, 2030, 2035, 2040, 2050]
    positions = list(range(len(years)))
    for col, pathway in enumerate(PATHWAYS, 1):
        part = [r for r in rows if r["pathway"] == pathway]
        available = {int(r["year"]) for r in part}
        if not set(years).issubset(available):
            fig.add_annotation(text="Data for these years are not available", x=.25 if col == 1 else .8,
                               y=.5, xref="paper", yref="paper", showarrow=False)
            continue
        focus = years.index(2035)
        fig.add_vrect(x0=focus-.42, x1=focus+.42, fillcolor="#e5eee9", opacity=.6,
                      line_width=0, layer="below", row=1, col=col)
        for category in categories:
            values = {int(r["year"]): float(r["share"])*100 for r in part if r["category"] == category}
            fig.add_trace(go.Bar(x=positions, y=[values.get(y,0) for y in years],
                name=category, legendgroup=category, showlegend=col == 1,
                marker=dict(color=COLORS.get(category,"#b2bec4"), line=dict(color="white",width=.7)),
                customdata=[[year,pathway] for year in years],
                hovertemplate="<b>%{fullData.name}</b><br>%{customdata[1]} · %{customdata[0]}<br>%{y:.3f}% " + ("of gas production by energy" if sector == "Gas" else "of supply") + "<extra></extra>"), row=1,col=col)
        fig.update_xaxes(tickvals=positions, ticktext=["<b>2035</b>" if y == 2035 else str(y) for y in years],
                         tickfont=dict(size=11),
                         range=[-.6,len(years)-.4], showgrid=False, fixedrange=True, row=1,col=col)
        fig.update_yaxes(range=[0,100], tickvals=[0,50,100], ticksuffix="%",
                         gridcolor="#e0e8ea", zeroline=False, fixedrange=True, row=1,col=col)
    fig.update_layout(barmode="stack", bargap=.48, autosize=True,
        margin=dict(l=40,r=8,t=35,b=78), paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Arial",size=13,color="#214659"),
        legend=dict(orientation="h", y=-.16, x=.5, xanchor="center", font=dict(size=12)),
        hoverlabel=dict(bgcolor="white",font_size=12),
        meta={"sector":sector,"years":years,"source":"REMIND-EU IAM energy shares" if sector == "Gas" else "premise market shares at exact package anchors"})
    return fig


def future_markets(bundle):
    gwp_rows = load_scores()
    def card(number, title, body, tags, logo, label, href):
        return html.Div([html.A(html.Img(src=logo,alt=label),href=href,target="_blank",rel="noopener noreferrer",className="future-logo"),html.Div([
            html.Small(number), html.H3(title), html.P(body)])],className="future-method-card")
    return html.Div([
        html.Div([
            card("01 · IAM SCENARIOS", "REMIND-EU models future energy systems",
                 "It links energy demand, the economy and climate policy.",
                 ["SSP2-NPi", "SSP2-PkBudg1000"], "assets/pik-logo.png", "Potsdam Institute for Climate Impact Research (PIK)", "https://www.pik-potsdam.de/en"),
            html.Div("→",className="future-arrow"),
            card("02 · PROSPECTIVE INVENTORIES", "premise updates supply-chain inventories",
                 "It applies future technology mixes and efficiencies to ecoinvent.",
                 ["Technology mixes", "Process efficiency"], "assets/premise-logo.png", "premise", "https://premise.readthedocs.io/"),
            html.Div([
                html.Img(src="assets/enc-europe.svg", alt="Europe map highlighting Denmark, Sweden, Finland, Åland and the Faroe Islands"),
                html.Div([html.Small("NORTHERN EUROPE"),html.H3("ENC"),
                          html.P("Denmark · Sweden · Finland"),
                          html.P("Åland (AX) · Faroe Islands (FO)"),
                          html.Small("REMIND-EU definition")]),
            ],className="future-region-card"),
        ],className="future-methods"),
        html.Div([
          html.Div([
            html.Div([html.Strong("SSP2 with two climate-policy scenarios"),
                      html.Span("Global · 2020–2100")],className="future-chart-heading"),
            html.Div([html.Span("Population (both pathways)",className="shared"),
                      html.Span("NPi · implemented policies",className="npi"),
                      html.Span("PkBudg1000 · 1000 Gt CO₂ budget",className="budget")],className="future-global-legend"),
            html.Img(src="assets/ssp2-global-trends.svg",alt="Global REMIND-EU SSP2 trajectories: population levels off near 10 billion by 2100, GDP rises in both pathways, while global CO2 emissions diverge between NPi and PkBudg1000.",className="future-global-chart"),
            html.A("REMIND-EU scenario data · model documentation ↗",href="https://rse.pik-potsdam.de/doc/remind/",target="_blank",rel="noopener noreferrer",className="future-global-source"),
          ],className="future-global-card"),
          html.Div([
            html.Div([html.Strong("How supply and emissions change"),
                dcc.RadioItems(id="future-metric", options=[
                    {"label":"Supply shares", "value":"shares"},
                    {"label":"GWP per unit", "value":"gwp", "disabled":not available("Electricity", gwp_rows)}],
                    value="shares", inline=True, className="future-metric-toggle")],className="future-chart-heading"),
            dcc.RadioItems(id="future-sector", options=[{"label":html.Span([
                html.Img(src=icon_uri({"Electricity":"power","District heat":"heat","Gas":"fuel","Steel":"steel","Truck transport":"truck","Cement clinker":"kiln"}[s]),alt=""),html.Span(s)
            ],className="future-sector-option"),"value":s} for s in SECTORS],
                           value="Electricity",inline=True,className="future-sector-tabs"),
            html.Div(CONTEXT["Electricity"],id="future-sector-context",className="future-sector-context"),
            dcc.Graph(id="future-sector-chart",figure=sector_figure(bundle),responsive=True,
                      config={"displayModeBar":False},className="future-sector-chart"),
            html.Div(id="future-metric-note",className="future-metric-note"),
          ],className="future-chart-card"),
        ],className="future-analysis-grid"),
    ],className="future-markets-layout")
