"""Closing summary of the same native-service results shown in the lecture."""

from functools import lru_cache
from dash import html
from . import comparison as compare
from .case_pulse import case_window_figure, DEFAULT_WINDOW
from .visuals import CASES, CASE
from .processes import process_quantities


@lru_cache(maxsize=1)
def summary_rows():
    rows = []
    for case in CASES:
        pulse = case_window_figure(case,DEFAULT_WINDOW).layout.meta["equivalent_kg"]
        quantities = process_quantities(case)
        gross_capture_t = (
            quantities["gross_capture_t_co2"] if case in ("DACCS", "BECCS")
            else quantities["eventual_uptake_kg"] / 1000 if case == "ERW"
            else quantities["captured_co2_kg"] / 1000
        )
        # Linear scaling of the existing signed curve-area match, including the
        # physical capture-to-storage ratio. Positive responses cannot match removal.
        scale = -1000 / pulse if pulse < 0 else None
        rows.append(dict(case=case,current=compare.snapshot(case,2025),
                         prospective=compare.snapshot(case,2035),
                         time_explicit=sum(value for age,value in compare.annual_scores(case)),
                         pulse=pulse,gross_capture_per_service_t=gross_capture_t,
                         removal_match_scale=scale,
                         gross_required_t=gross_capture_t * scale if scale is not None else None))
    return tuple(rows)


def _score(value):
    return f"{value:+,.0f}".replace("-","−")


def score_table():
    return html.Div([
        html.H3("Life-cycle scores for the four options"),
        html.P("Native inventories and climate backgrounds · 1 t stored, or eventual ERW uptake potential",
               className="closing-score-service"),
        html.Table([
            html.Thead([
                html.Tr([html.Th("Option",rowSpan=2,scope="col"),
                         html.Th("GWP100 · kg CO₂-eq",colSpan=3,scope="colgroup"),
                         html.Th(["CO₂-pulse-eq",html.Span("kg · curve match"),
                                  html.Span("2020–2100 · ref. 2030")],rowSpan=2,scope="col"),
                         html.Th(["Gross CO₂ needed",html.Span("t captured / ERW uptake"),
                                  html.Span("Match −1 t in 2030"),
                                  html.Span("RF area · 2020–2100")],rowSpan=2,scope="col",
                                 className="closing-gross-heading")]),
                html.Tr([html.Th("Current 2025",scope="col"),html.Th("Future 2035",scope="col"),
                         html.Th(["Time-explicit",html.Span("Operation period",className="closing-operation-label")],scope="col")]),
            ]),
            html.Tbody([
                html.Tr([html.Th(row["case"],scope="row",style={"color":CASE[row["case"]]["colour"]}),
                         html.Td(_score(row["current"])),html.Td(_score(row["prospective"])),
                         html.Td([_score(row["time_explicit"]),html.Span(
                             "2035–2064" if row["case"]=="Cement + CCS" else "2030–2049",
                             className="closing-operation-period")]),
                         html.Td("≈ "+_score(row["pulse"]),className="closing-pulse-score"),
                         html.Td("Cannot match" if row["gross_required_t"] is None else
                                 f"≈ {row['gross_required_t']:.2f}",className="closing-gross-score")])
                for row in summary_rows()
            ]),
        ],**{"aria-label":"GWP100, illustrative CO2 pulse equivalents and gross CO2 capture or uptake needed to match one tonne removed in 2030 over 2020–2100"}),
        html.Ul([
            html.Li([html.Strong("Prospective LCA")," captures changing production conditions."]),
            html.Li([html.Strong("Time-explicit LCA")," reveals when emissions and climate benefits occur."]),
            html.Li([html.Strong("CO₂-pulse-eq")," summarizes an effect over a declared window; keep the trajectory alongside it."]),
        ],className="closing-score-takeaways"),
    ],className="closing-removal-frame seoul-closing-scores")
