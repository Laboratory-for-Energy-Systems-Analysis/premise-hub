"""French adaptation of Seoul slide 15 and its verified temporal graph viewer."""

from functools import lru_cache
from pathlib import Path

from dash import dcc, html

from apps.seoul_2026.routing import (
    _workflow as source_workflow,
    shallow_route_json,
    verified_route_path,
)

CASES = {"DACCS": "daccs", "BECCS": "beccs"}
SOURCE = Path(__file__).resolve().parents[1] / "seoul_2026"

WORKFLOW_TEXT = {
    "IAM scenarios": "Scénarios IAM",
    "Pathway + future years": "Trajectoire et années futures",
    "3.12 · cut-off inventories": "Inventaires 3.12 · cut-off",
    ": scenario-updated LCA data": " : données ACV prospectives",
    "Transform suppliers · export scenario years": "Transformer les fournisseurs · exporter les années",
    "Scenario data package": "Paquet de données prospectives",
    "3D stacks: two inventory dimensions + year": "Matrices 3D : deux dimensions d’inventaire + année",
    "+ Encode temporal distributions": "+ Définir les distributions temporelles",
    "Analyst’s foreground: build · operate · regrow / dissolve": "Premier plan : construire · exploiter · repousser",
    ": route in time → solve by year": " : routage temporel → calcul annuel",
    "Interpolate backgrounds · retain the remaining supply chain": "Interpoler les fonds · conserver la chaîne résiduelle",
}


def workflow(prefix):
    component = source_workflow()

    def translate(value):
        if isinstance(value, str):
            return WORKFLOW_TEXT.get(value, value)
        if isinstance(value, (list, tuple)):
            return [translate(child) for child in value]
        if hasattr(value, "children"):
            value.children = translate(value.children)
        if getattr(value, "src", "").endswith("shared/trails-annual-matrices.svg"):
            value.src = prefix + "assets/trails-annual-matrices.svg"
            value.alt = "Matrices annuelles A et B : produits, activités et flux élémentaires."
        return value

    return translate(component)


def routing_lesson(print_mode, prefix):
    href = prefix + "routing/daccs.html"
    if print_mode:
        controls = html.Strong("DACCS · sortie réelle de TRAILS", className="route-print-service")
        viewer = html.Img(src=prefix + "routing/daccs.png", alt="Graphe temporel réel DACCS : unité fonctionnelle au niveau 0 et fournisseurs datés aux niveaux 1 à 3.", className="route-printed-graph")
    else:
        controls = html.Div([
            dcc.RadioItems(id="mcv-route-case", options=list(CASES), value="DACCS", inline=True, className="segmented"),
            html.A("Ouvrir le graphe ↗", href=href, id="mcv-route-open", target="_blank", rel="noopener"),
        ], className="mcv-route-controls")
        viewer = html.Iframe(src=href, id="mcv-route-frame", title="Graphe temporel réel TRAILS", className="route-frame", allow="fullscreen")
    return html.Div([
        html.Section([
            html.H2("01 · Construire le modèle temporel"), workflow(prefix),
        ], className="route-left-pane"),
        html.Section([
            html.Div([
                html.H2("02 · Suivre les échanges datés"),
                html.Span("Sortie réelle TRAILS · unité fonctionnelle au niveau 0"),
            ], className="route-right-heading"),
            controls, viewer,
        ], className="route-right-pane"),
    ], className="routing-split")


@lru_cache(maxsize=1)
def french_graph_template():
    """Reuse the viewer algorithm; translate its interface, keeping raw data intact."""
    template = (SOURCE / "templates/routing_graph.html").read_text()
    translations = {
        'lang="en"': 'lang="fr"',
        "TRAILS temporal graph": "Graphe temporel TRAILS",
        "Maximum routing level": "Niveau maximal de routage",
        "Graph representation": "Représentation du graphe",
        "Supply chain branch": "Branche de fournisseurs",
        ">Levels ": ">Niveaux ",
        "Dated nodes": "Nœuds datés",
        "Activity overview": "Vue par activité",
        ">Fit<": ">Ajuster<",
        "Zoom in": "Agrandir", "Zoom out": "Réduire",
        "All branches": "Toutes les branches",
        "Zoom for more activity names · dashed = negative demand": "Zoomer pour lire les activités · pointillés = demande négative",
        "Loading the TRAILS graph…": "Chargement du graphe TRAILS…",
        "Graph not available": "Graphe indisponible",
        "Level 0 · ": "Niveau 0 · ", "LEVEL 0 · ": "NIVEAU 0 · ",
        "Level ": "Niveau ", " · level ": " · niveau ",
        "Activity demand; coefficients omitted": "Demande d’activité ; coefficients non affichés",
        "Negative demand / substitution branch": "Demande négative / substitution",
        "Supply-chain demand branch": "Demande de fournisseur",
        "Calendar year": "Année",
        "activity groups": "groupes d’activités", "dated nodes": "nœuds datés",
        " links · levels 0–": " liens · niveaux 0–",
        "Calendar replicas grouped for this view": "Répliques annuelles regroupées dans cette vue",
        "Actual TRAILS routing output": "Sortie réelle du routage TRAILS",
        "Loading level 4…": "Chargement du niveau 4…",
        "Level 4 could not load; showing levels 0–3.": "Niveau 4 indisponible ; affichage des niveaux 0–3.",
        "Graph could not load: ": "Chargement impossible : ",
    }
    for original, translated in sorted(translations.items(), key=lambda item: -len(item[0])):
        template = template.replace(original, translated)
    template = template.replace("raw.metadata.functional_unit", "serviceText()")
    template = template.replace(" let loadedDepth=", " function serviceText(){return raw.metadata.functional_unit.replace('CO2 physically stored','CO₂ stockée physiquement');}\n let loadedDepth=")
    return template
