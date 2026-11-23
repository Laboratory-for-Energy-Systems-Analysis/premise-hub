"""French TRAILS viewer backed by the MCV cohort routing exports."""

from collections import defaultdict, deque
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

from dash import dcc, html

from apps.seoul_2026.routing import _workflow as source_workflow

CASES = {"DACCS": "daccs", "BECCS": "beccs"}
SOURCE = Path(__file__).resolve().parents[1] / "seoul_2026"
DATA = Path(__file__).resolve().parent / "data/routing"
MAX_VIEW_DEPTH = 3
TRANSPORT = (
    "carbon dioxide compression, transport and storage",
    "carbon dioxide transport extension, pipeline 50 to 2000 km, LCSS 2026",
)
COORDINATORS = {
    "daccs": (*TRANSPORT,
        "carbon dioxide removal, DACCS, solid sorbent, low-temperature heat pump, LCSS 2026",
        "carbon dioxide, captured and stored, with a sorbent-based direct air capture system, "
        "100ktCO2, with heat pump heat, and grid electricity",
    ),
    "beccs": (*TRANSPORT,
        "carbon dioxide, captured and stored, at Nordic spruce CHP, post-combustion, LCSS 2026",
        "operation of new Nordic spruce CHP with post-combustion capture, excluding capture equipment, LCSS 2026",
    ),
}
DISPLAY_NAMES = {
    "direct air capture system, sorbent-based, 100ktCO2": "Construction DACCS",
    "market group for electricity, medium voltage": "Électricité consommée",
    "treatment of direct air capture system, sorbent-based, 100ktCO2": "Fin de vie DACCS",
    "market for heat and power co-generation unit, organic Rankine cycle, 1000kW electrical": "Construction de la cogénération",
    "market group for electricity, high voltage": "Électricité de réseau · haute tension",
    "treatment of waste concrete, inert material landfill": "Fin de vie du stockage · béton",
}
SUBSTITUTION_NAMES = {
    "market group for electricity, high voltage": "Électricité évitée",
    "market for heat, district or industrial": "Chaleur évitée",
}
FOREST_DIESEL_CONTEXT = {
    "source": "biomass supply from existing spruce forest, project harvest and future management, LCSS 2026",
    "target": "market for diesel, burned in building machine",
    "label": "Gazole · gestion forestière",
    "note": (
        "Hypothèse du modèle pour la préparation du terrain, l’entretien du peuplement "
        "et les chemins forestiers. Le total est réparti uniformément de l’année de "
        "récolte à 82 ans après. La récolte de 2049 prolonge cette demande jusqu’en 2131."
    ),
}
FRONT_PHASES = [
    {"key": "construction", "label": "Construction · 2027–2029", "first": 2027, "last": 2029},
    {"key": "operation", "label": "Exploitation · 2030–2049", "first": 2030, "last": 2049},
    {"key": "end-of-life", "label": "Fin de vie · 2050", "first": 2050, "last": 2050},
]

WORKFLOW_TEXT = {
    "IAM scenarios": "Scénarios IAM",
    "Pathway + future years": "Trajectoire et années futures",
    "3.12 · cut-off inventories": "Inventaires 3.12 · cut-off",
    ": scenario-updated LCA data": " : données ACV prospectives",
    "Transform suppliers · export scenario years": "Transformer les fournisseurs · exporter les années",
    "Scenario data package": "Paquet de données prospectives",
    "3D stacks: two inventory dimensions + year": "Matrices 3D : deux dimensions d’inventaire + année",
    "+ Encode temporal distributions": "+ Définir les distributions temporelles",
    "Analyst’s foreground: build · operate · regrow / dissolve": "Constructions des fournisseurs par millésime IAM · calendrier du projet",
    ": route in time → solve by year": " : routage temporel → calcul annuel",
    "Interpolate backgrounds · retain the remaining supply chain": "Interpoler les fonds · conserver la chaîne résiduelle",
}


@lru_cache(maxsize=6)
def verified_route_path(slug, suffix):
    if slug not in CASES.values() or suffix not in {"json.gz", "depth3.json.gz", "png"}:
        raise ValueError("Unknown MCV routing asset")
    name = f"{slug}-{suffix}" if suffix.startswith("depth3") else f"{slug}.{suffix}"
    manifest = json.loads((DATA / "manifest.json").read_text())
    path = DATA / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["files"][name]:
        raise ValueError("MCV routing export differs from its manifest")
    return path


@lru_cache(maxsize=4)
def route_json(slug, shallow):
    suffix = "depth3.json.gz" if shallow else "json.gz"
    return gzip.decompress(verified_route_path(slug, suffix).read_bytes())


def foreground_graph(graph):
    """Fold commissioning-year coordination chains into the functional-unit root."""
    nodes = {node["id"]: node for node in graph["nodes"]}
    root = next(node for node in nodes.values() if node["depth"] == 0)
    outgoing = defaultdict(list)
    for edge in graph["edges"]:
        outgoing[edge["source"]].append(edge)
    coordinators = COORDINATORS[graph["metadata"]["case"]]

    def expand(source, via=()):
        for edge in outgoing[source]:
            node = nodes[edge["target"]]
            if node["year"] == root["year"] and node["name"] in coordinators and not edge["negative"]:
                yield from expand(node["id"], (*via, node["name"]))
            elif via:
                yield {**edge, "source": root["id"], "via": via}
            else:
                yield edge

    outgoing[root["id"]] = list(expand(root["id"]))
    depths = {root["id"]: 0}
    pending = deque(depths)
    edges = []
    while pending:
        source = pending.popleft()
        for edge in outgoing[source]:
            target = edge["target"]
            if target not in depths:
                depths[target] = depths[source] + 1
                pending.append(target)
            edges.append(edge)

    return {
        "metadata": graph["metadata"],
        "nodes": [{**nodes[node_id], "depth": depth} for node_id, depth in depths.items()],
        "edges": edges,
        "loaded_max_depth": max(depths.values()),
    }


def foreground_start(graph):
    nodes = [node for node in graph["nodes"] if node["depth"] <= 1]
    ids = {node["id"] for node in nodes}
    return {**graph, "nodes": nodes, "loaded_max_depth": 1,
            "edges": [e for e in graph["edges"] if e["source"] in ids and e["target"] in ids]}


@lru_cache(maxsize=2)
def foreground_route(slug):
    return foreground_graph(json.loads(route_json(slug, shallow=False)))


@lru_cache(maxsize=4)
def foreground_route_json(slug, shallow):
    graph = foreground_route(slug)
    return json.dumps(foreground_start(graph) if shallow else graph, separators=(",", ":")).encode()


def foreground_template_options(graph):
    return {
        "foreground_layout": True, "initial_depth": 1, "max_depth": min(MAX_VIEW_DEPTH, graph["loaded_max_depth"]),
        "display_names": DISPLAY_NAMES, "substitution_names": SUBSTITUTION_NAMES, "front_phases": FRONT_PHASES,
        "supply_context": FOREST_DIESEL_CONTEXT if graph["metadata"]["case"] == "beccs" else None,
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
        controls = None
        viewer = html.Div([
            html.Img(src=prefix + f"routing/{slug}.png", alt=f"Graphe de routage temporel {case} · échanges du premier plan", className="route-printed-graph")
            for case, slug in CASES.items()
        ], className="route-print-view")
    else:
        controls = html.Div([
            dcc.RadioItems(id="mcv-route-case", options=list(CASES), value="DACCS", inline=True, className="segmented"),
            html.A("Ouvrir le graphe ↗", href=href, id="mcv-route-open", target="_blank", rel="noopener"),
        ], className="mcv-route-controls")
        viewer = html.Iframe(src=href, id="mcv-route-frame", title="Graphe temporel TRAILS", className="route-frame", allow="fullscreen")
    return html.Div([
        html.Section([
            html.H2("01 · Construire le modèle temporel"), workflow(prefix),
        ], className="route-left-pane"),
        html.Section([
            html.Div([
                html.H2("02 · Suivre les échanges datés"),
                html.Span("Échanges du premier plan directement reliés à l’unité fonctionnelle"),
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
        "Coordination activities folded into the root": "Activités de coordination repliées dans la racine",
        "Loading additional levels…": "Chargement des niveaux suivants…",
        "Additional levels could not load.": "Niveaux suivants indisponibles.",
        "Graph could not load: ": "Chargement impossible : ",
    }
    for original, translated in sorted(translations.items(), key=lambda item: -len(item[0])):
        template = template.replace(original, translated)
    template = template.replace("raw.metadata.functional_unit", "serviceText()")
    template = template.replace(" let loadedDepth=", " function serviceText(){return raw.metadata.functional_unit.replace('CO2 physically stored','CO₂ stockée physiquement');}\n let loadedDepth=")
    template = template.replace(
        "daccs:'CO₂ capture and geological storage, solid-sorbent DAC'",
        "daccs:'DACCS · Mise en service'",
    ).replace(
        "beccs:'CO₂ capture and geological storage at biomass CHP'",
        "beccs:'BECCS · Mise en service'",
    )
    return template
