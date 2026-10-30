"""An evidence-to-result workflow with explicit analyst choices and tool roles."""

from dash import html
from .branding import logo, tool_link
from .visuals import icon_svg, svg_uri


def _icon(kind,colour):
    return html.Img(src=svg_uri(icon_svg(kind,colour),64,64,kind),alt="",className="workflow-stage-icon")


def workflow_map():
    decisions = (("Service","What does the system deliver?"),("Reference","What happens without it?"),
                 ("Timing evidence","When do the flows occur?"),("Climate question","Background · window · pulse"))
    marks = [
        _icon("investment","#527b90"),
        html.Div([logo("ecoinvent","workflow-brand"),html.Span("+ IAM scenarios"),
                  html.B("↓"),logo("premise","workflow-brand")],className="workflow-background-marks"),
        logo("trails","workflow-trails-brand"),
        html.Div([html.Strong("FaIR"),_icon("response","#7656a8")],className="workflow-fair-mark"),
        _icon("response","#008a82"),
    ]
    stages = (
        ("01","Frame","Foreground + reference","Specify the service and the system without the intervention.","Study definition","#527b90"),
        ("02","Transform",["ecoinvent · IAMs · ",tool_link("premise")],"Translate scenario pathways into changing life-cycle suppliers.","Future supplier data","#3292b5"),
        ("03","Date + solve",tool_link("trails"),"Route temporal exchanges and solve the year-specific supply chains.","GHG emissions by year","#008a82"),
        ("04","Simulate",tool_link("fair"),"Compare the same climate background with and without the project.","Forcing + temperature","#7656a8"),
        ("05","Interpret","Trajectory + CO₂-pulse-eq","Report the response curve together with a declared comparison window.","A dated climate result","#3e7654"),
    )
    return html.Div([
        html.Div([html.Strong("Analyst choices"),html.Div([
            html.Div([html.Strong(title),html.Span(detail)]) for title,detail in decisions
        ],className="workflow-choice-grid")],className="workflow-choices"),
        html.Div([
            html.Article([
                html.Div([html.Span(n),html.Strong(verb)],className="workflow-stage-heading"),
                html.Div(marks[i],className="workflow-stage-mark"),
                html.H2(tool),html.P(detail),html.Div(output,className="workflow-stage-output"),
            ],className="workflow-stage",style={"--stage-colour":colour})
            for i,(n,verb,tool,detail,output,colour) in enumerate(stages)
        ],className="workflow-stage-grid"),
    ],className="workflow-overview",**{"data-reused-from":"/setac-2026/ · evidence-to-results workflow; existing ecoinvent, premise and TRAILS marks"})
