"""Optional French scenario detail slide, sharing SETAC's audited extracts."""

from dash import dcc, html

from .deck import graph, text
from .figures import PATHWAYS, mix_figure, scenario_context_figure, scenario_context_note


def scenario_slide(print_mode):
    scenario = html.Span("SSP2-PkBudg1000 · Europe du Nord", className="print-setting") if print_mode else dcc.RadioItems(
        id="mix-pathway", options=[{"label": "NPi · politiques en place", "value": PATHWAYS[0]},
            {"label": "PkBudg1000 · budget carbone", "value": PATHWAYS[1]}], value=PATHWAYS[1], inline=True, className="segmented")
    context_controls = html.Div([html.H3("Température mondiale"), html.Span("Monde", className="print-setting")], className="context-controls") if print_mode else html.Div([
        dcc.Dropdown(id="context-indicator", options=[{"label": "Température mondiale", "value": "GMST"}, {"label": "Émissions de CO₂", "value": "CO2"}, {"label": "Population", "value": "Population"}], value="GMST", clearable=False, searchable=False, className="mix-sector-select"),
        dcc.Dropdown(id="context-region", options=[{"label": "Monde", "value": "World"}, {"label": "Europe du Nord", "value": "ENC", "disabled": True}], value="World", clearable=False, searchable=False, className="mix-sector-select")], className="context-controls")
    context = html.Div([context_controls, graph(scenario_context_figure(), None if print_mode else "context-chart"),
        html.P(scenario_context_note("GMST", "World"), className="source context-note", **({} if print_mode else {"id": "context-note"}))], className="chart-stack context-panel")
    material = html.H3("Acier") if print_mode else dcc.Dropdown(id="mix-material-sector", options=[{"label": label, "value": value} for label, value in (("Acier", "Steel"), ("Clinker", "Cement clinker"), ("Transport routier", "Truck transport"))], value="Steel", clearable=False, searchable=False, className="mix-sector-select")
    panels = [html.Div([material if sector == "Steel" else html.H3(label), graph(mix_figure(sector), None if print_mode else identifier)], className="chart-stack mix-panel") for sector, label, identifier in (("Electricity", "Électricité", "mix-electricity"), ("District heat", "Chaleur", "mix-heat"), ("Steel", "Acier", "mix-material"))]
    return html.Div([html.Div([html.Strong("REMIND-EU → premise → mix des fournisseurs futurs"), scenario], className="control-row mix-controls"),
        html.Div([context, html.Div(panels, className="mix-panels")], className="premise-panels"),
        text("Scénarios conditionnels · marchés ENC · parts extraites de 2025 à 2050 par pas de cinq ans. Catégories toujours sous 1 % regroupées dans Autres. Électricité haute tension ; chaleur du marché combiné réseau/industrie.", "source")], className="stack mcv-scenario-stack")
