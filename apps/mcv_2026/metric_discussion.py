"""French adaptation of Seoul slide 17, retaining its schematic geometry."""

from functools import lru_cache
from urllib.parse import quote, unquote
import xml.etree.ElementTree as ET

from dash import html

from apps.seoul_2026.metric_discussion import hint_diagram as source_diagram

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)

TRANSLATIONS = {
    "Each +1 t CO₂ → +1,000 kg CO₂-eq": "Chaque +1 t CO₂ → +1 000 kg CO₂-eq",
    "100-year window": "Fenêtre de 100 ans",
    "Target": "Cible",
    "Both total 0 kg CO₂-eq": "Deux bilans de 0 kg CO₂-eq",
    "Now": "Immédiat",
    "Later": "Différé",
    "50-year gap": "Décalage de 50 ans",
    "Same GWP100 · different pulse masses": "Même GWP100 · masses différentes",
    "Forcing · schematic": "Forçage · schéma",
    "100 y": "100 ans",
    "Concentrations · indexed, schematic": "Concentrations indexées · schéma",
    "Fixed CH₄ / N₂O GWP100?": "GWP100 CH₄ / N₂O fixes ?",
}

CARDS = (
    ("01", "Même score, fenêtres différentes ?", "dated",
     "Deux émissions alternatives de +1 t CO₂ en 2030 ou 2080 valent chacune +1 000 kg CO₂-eq. "
     "Leurs fenêtres GWP100 vont jusqu’en 2130 ou 2180, tandis que la cible commune est 2100. "
     "Les bandes représentent les horizons de caractérisation, pas la durée de vie du CO₂."),
    ("02", "Bilan nul, même histoire climatique ?", "removal",
     "+1 t et −1 t CO₂ en 2030, ou +1 t en 2030 et −1 t en 2080 : les deux sommes sont nulles. "
     "La zone ombrée indique le délai de 50 ans, pas un forçage calculé. "
     "Ce décalage éclaire la question des émissions et de la repousse biogénique."),
    ("03", "Même CO₂-eq, même persistance ?", "gases",
     "Deux impulsions de gaz en 2030, de masses différentes, sont ajustées à un même GWP100. "
     "Les réponses schématiques de type CH₄ et CO₂ ont la même aire sur 100 ans, mais des profils différents. "
     "Il ne s’agit ni de réponses calibrées, ni de températures, ni de résultats FaIR."),
    ("04", "Facteurs fixes, atmosphère changeante ?", "background",
     "Des concentrations de fond indexées de CO₂, CH₄ et N₂O évoluent entre 2030 et 2080, "
     "face à des facteurs GWP100 fixes. Schéma sans prévision quantitative : "
     "le fond atmosphérique influence la réponse marginale des gaz et celle du CO₂ de référence."),
)


@lru_cache(maxsize=4)
def diagram(kind, description):
    uri, _ = source_diagram(kind)
    root = ET.fromstring(unquote(uri.split(",", 1)[1]))
    for element in root.iter():
        if element.tag in (f"{{{NS}}}title", f"{{{NS}}}desc"):
            element.text = description
        elif element.text in TRANSLATIONS:
            original = element.text
            element.text = TRANSLATIONS[original]
            if original in ("Now", "Later"):
                element.set("font-size", "16")
    return "data:image/svg+xml," + quote(ET.tostring(root, encoding="unicode"))


def discussion():
    references = (
        ("GIEC AR6 §7.6", "https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/#7.6"),
        ("Levasseur et al. (2010)", "https://doi.org/10.1021/es9030003"),
        ("Reisinger et al. (2011)", "https://doi.org/10.1088/1748-9326/6/2/024020"),
    )
    return html.Div([
        html.Div([
            html.Span("QUATRE DIMENSIONS DU TEMPS", className="mcv-gwp-label"),
            html.Div([html.A(label, href=url, target="_blank", rel="noopener")
                      for label, url in references], className="mcv-gwp-references"),
        ], className="mcv-gwp-heading"),
        html.Div([
            html.Article([
                html.H3([html.Span(number), html.Strong(question)]),
                html.Img(src=diagram(kind, description), alt=description),
            ], className="mcv-gwp-card")
            for number, question, kind, description in CARDS
        ], className="mcv-gwp-grid"),
    ], className="mcv-gwp")
