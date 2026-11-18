"""French adaptation of the shared-scenario diagram on Seoul slide 19."""

from functools import lru_cache
from urllib.parse import unquote
import xml.etree.ElementTree as ET

from dash import html

from apps.seoul_2026.methods import fair_handoff as seoul_handoff

from .figures import PATHWAYS

SVG_NS = "http://www.w3.org/2000/svg"
DESCRIPTION = (
    f"Le scénario REMIND-EU {PATHWAYS[1]} alimente deux branches. "
    "Premise en dérive les chaînes d’approvisionnement futures utilisées par TRAILS "
    "pour dater les émissions et les retraits du projet. Le même scénario fournit "
    "directement les émissions de gaz à effet de serre de fond à FaIR. FaIR reçoit "
    "ces deux entrées et compare les simulations avec et sans le projet."
)

LABELS = {
    "IAM scenario": "REMIND-EU",
    "One shared pathway": PATHWAYS[1],
    "Future LCA suppliers": "Fournisseurs futurs",
    "TRAILS inventory": "Inventaire TRAILS",
    "Dated project emissions": "Émissions et retraits datés",
    "Future background GHG emissions": "Émissions futures de GES de fond",
    "From that same IAM scenario": "Du même scénario REMIND-EU",
    "→ Gas concentrations": "→ Concentrations de GES",
    "With project − without project": "Avec projet − sans projet",
    "Climate response": "Réponse climatique",
    "Δ forcing → Δ temperature": "Δ forçage → Δ température",
}


@lru_cache(maxsize=1)
def diagram_svg():
    source = seoul_handoff().children[0].src
    root = ET.fromstring(unquote(source.split(",", 1)[1]))
    root.find(f"{{{SVG_NS}}}title").text = DESCRIPTION
    for label in root.iter(f"{{{SVG_NS}}}text"):
        if label.text in LABELS:
            label.text = LABELS[label.text]
    return ET.tostring(root, encoding="unicode")


def scenario_handoff(prefix):
    return html.Img(src=prefix + "fair-handoff.svg", alt=DESCRIPTION, className="mcv-fair-handoff")
