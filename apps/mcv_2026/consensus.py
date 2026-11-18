"""Closing contribution to the session's standards and biogenic-carbon debate."""

from dash import html

from apps.setac_2026.results import cohort_temporal_total

from .figures import CASES, DEFAULT_END, REFERENCE_YEAR, WINDOW_START, pulse_value

ISO_URL = "https://www.iso.org/standard/71206.html"
GHG_URL = "https://ghgprotocol.org/sites/default/files/2026-11/ISB-Meeting24-Minutes-Day1-20260921.pdf"
PEF_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=intcom%3AC%282021%299332"
DISCUSSION_QUESTION = "La déclaration des flux datés pourrait-elle devenir un socle commun pour comparer les bilans de carbone biogénique ?"


def link(label, url):
    return html.A(label, href=url, target="_blank", rel="noopener noreferrer")


def score_table():
    rows = (
        ("GWP100", "kg CO₂-eq", [cohort_temporal_total(case, "per_tonne") for case in CASES]),
        ("CO₂-pulse-eq", f"kg CO₂-pulse-eq · {WINDOW_START}–{DEFAULT_END} · impulsion {REFERENCE_YEAR}",
         [pulse_value(case) for case in CASES]),
    )
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Par tonne nette de CO₂ stockée", scope="col"),
            *[html.Th(case, scope="col") for case in CASES],
        ])),
        html.Tbody([
            html.Tr([
                html.Th([indicator, html.Span(details)], scope="row"),
                *[html.Td(f"{score:.0f}".replace("-", "−"),
                          className="consensus-lower-score" if score == min(scores) else "")
                  for score in scores],
            ])
            for indicator, details, scores in rows
        ]),
    ], className="consensus-scores")


def closing(funding):
    questions = (
        ("Que comptabiliser ?", "Quantités de carbone et scénario forestier sans projet"),
        ("Quand ont lieu les flux ?", "Dates des absorptions et des émissions"),
        ("Quel effet évaluer ?", "GWP100 et analyse climatique complémentaire"),
    )
    return html.Div([
        html.Div([
            html.Div([
                html.Article([
                    html.H3("ISO 14067 / GHG Protocol"),
                    html.P("Travaux conjoints sur l’empreinte produit, dont les flux biogéniques."),
                    html.Div([link("ISO 14067:2018", ISO_URL), " · ",
                              link("Point d’étape · sept. 2026, p. 4", GHG_URL)], className="consensus-source"),
                ], className="consensus-standard"),
                html.Article([
                    html.H3("PEF · référence 2021"),
                    html.P("Émissions et absorptions comptabilisées sans pondération temporelle."),
                    html.Div(link("Texte de 2021 · §4.4.10", PEF_URL), className="consensus-source"),
                ], className="consensus-standard"),
            ], className="consensus-standards"),
            html.Div([
                html.P([
                    "Pour le même inventaire daté, ",
                    html.Strong("le classement BECCS–DACCS change"),
                    " entre GWP100 et forçage intégré.",
                ], className="consensus-evidence"),
                score_table(),
            ], className="consensus-results"),
            html.Dl([
                html.Div([html.Dt(question), html.Dd(detail)])
                for question, detail in questions
            ], className="consensus-questions"),
            html.Div([
                html.H2(DISCUSSION_QUESTION),
            ], className="consensus-proposal"),
        ], className="consensus-main"),
        html.Div([
            html.H2("Merci"),
            html.P("Romain Sacchi", className="closing-name"),
            html.Address([
                html.P("Laboratoire d’analyse des systèmes énergétiques"),
                html.P("Paul Scherrer Institut (PSI)"),
                html.A("romain.sacchi@psi.ch", href="mailto:romain.sacchi@psi.ch"),
            ]),
            funding,
        ], className="closing-contact"),
    ], className="consensus-layout")
