"""Actionable reading routes from study design to an ERW case inventory."""

from dash import html
from .layout import PREFIX


def resource_guide():
    routes = (
        ("01","Frame and model your system","Define the system boundaries and the timing question your assessment must answer.",
         "Start modelling your system and its boundaries with Brightway; specify the service, reference, emission dates and climate window.",
         (("Brightway · foreground modelling","https://learn.brightway.dev/en/latest/content/chapters/BW25/BW25_introduction.html"),
          ("Dynamic LCA · Levasseur 2010","https://doi.org/10.1021/es9030003"),
          ("IPCC · emission metrics","https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/#7.6"))),
        ("02","Build future suppliers","Turn an IAM pathway into prospective life-cycle inventory data.",
         "Choose an ecoinvent system model, then run premise’s first scenario example.",
         (("ecoinvent · system models","https://support.ecoinvent.org/system-models"),
          ("premise · first scenario","https://premise.readthedocs.io/en/latest/getting_started/first-scenario.html"))),
        ("03","Calculate the timing effects","Route dated exchanges, then inspect forcing and pulse equivalents.",
         "Start with the TRAILS quickstart; use FaIR’s calibrated ensemble example for climate modelling.",
         (("TRAILS · quickstart","https://trails.readthedocs.io/en/latest/quickstart.html"),
          ("FaIR · calibrated example","https://docs.fairmodel.net/en/latest/examples/calibrated_constrained_ensemble.html"))),
        ("04","Adapt an ERW inventory","Separate the source inventory from site-dependent uptake assumptions.",
         "Open the reviewed workbook, then check grinding, grain size and uptake timing for your site.",
         (("Reviewed inventory + changes",PREFIX+"erw-review"),
          ("Source inventory · Table S1","https://doi.org/10.1021/acs.est.2c08633.s001"),
          ("Marine weathering · Geerts 2025","https://doi.org/10.5194/bg-22-355-2025"))),
    )
    return html.Div([
        html.Div([
            html.Article([
                html.Div([html.Span(number),html.H2(title)],className="resource-route-title"),
                html.P(purpose,className="resource-purpose"),
                html.Div([html.Strong("First step"),html.Span(action)],className="resource-first-step"),
                html.Div([html.A(label,href=url,target="_blank",rel="noopener noreferrer")
                          for label,url in links],className="resource-route-links"),
            ],className="resource-route") for number,title,purpose,action,links in routes
        ],className="resource-route-grid"),
        html.Div([html.Strong("Revisit a worked example"),html.Div([
            html.A(label,href=url,target="_blank",rel="noopener noreferrer") for label,url in (
                ("IAM scenarios","/workshop/"),("CDR + time","/setac-2026/"),
                ("Cement + CCS","/ccus-webinar/"),("Temporal LCA","/lca-time/"))
        ])],className="resource-example-links"),
    ],className="resource-guide")
