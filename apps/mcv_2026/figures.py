"""French display layer over MCV's regenerated results."""


import plotly.graph_objects as go

from ._source import load

source = load("figures")

CASES = source.CASES
PATHWAYS = source.PATHWAYS
DEFAULT_END = source.DEFAULT_END
REFERENCE_YEAR = source.REFERENCE_YEAR
WINDOW_START = source.WINDOW_START
WINDOW_MIN = source.WINDOW_MIN
pulse_value = source.pulse_value
static_score = source.static_score
regrowth_end = source.regrowth_end
inventory_start = source.inventory_start
removal_requirements = source.removal_requirements

LABELS = {
    "Standing-forest reference<br>Removal credited during<br>post-harvest regrowth": "Référence : forêt sur pied<br>Absorption attribuée<br>à la repousse après récolte",
    "Annual GWP100": "GWP100 annuel",
    "Cumulative GWP100 · accounting sum": "GWP100 cumulé · somme comptable",
    "Cumulative GWP100": "GWP100 cumulé",
    "GWP100 total": "GWP100 total",
    "Forest regrowth": "Repousse forestière",
    "Direct air capture": "Captage dans l’air",
    "Upstream biogenic uptake": "Absorption biogénique en amont",
    "Avoided electricity + heat": "Électricité + chaleur évitées",
    "Residual stack emissions": "Émissions résiduelles",
    "Harvest + biomass supply": "Récolte + biomasse",
    "Electricity + heat supply": "Électricité + chaleur",
    "CO₂ transport losses": "Pertes de CO₂ au transport",
    "Other supply chain": "Autres contributions",
    "CHP operating emissions": "Émissions de cogénération",
    "Biomass supply": "Approvisionnement en biomasse",
    "Electricity + heat activities": "Activités électricité + chaleur",
    "Other activities": "Autres activités",
    "CO₂ & stack emissions": "CO₂ et émissions résiduelles",
    "Materials": "Matériaux",
    "Uptake": "Absorption",
    "Energy": "Énergie",
    "Net GWP100": "GWP100 net",
    "net t stored": "t nette stockée",
    "Calendar year": "",
    "Background year": "Année du système de fond",
    "Assessment window end": "Fin de la fenêtre d’évaluation",
    "Δ forcing": "Δ forçage",
    "Through ": "Jusqu’en ",
    "through ": "jusqu’en ",
    "+1 t CO₂ in 2030": "+1 t CO₂ en 2030",
    "CO₂ pulse-eq": "CO₂-pulse-eq",
    "°C above 1850–1900": "°C par rapport à 1850–1900",
    "Gt CO₂ / year": "Gt CO₂ / an",
    "Mt CO₂ / year": "Mt CO₂ / an",
    "billion people": "milliards d’habitants",
    "million people": "millions d’habitants",
    "District heat": "Chaleur",
    "Electricity": "Électricité",
    "Electric": "Électrique",
    "Cement clinker": "Clinker",
    "Truck transport": "Transport routier",
    "Steel": "Acier",
    "Recovered heat": "Chaleur récupérée",
    "Natural gas": "Gaz naturel",
    "Coal and oil": "Charbon et pétrole",
    "Battery electric": "Électrique à batterie",
    "Diesel truck": "Camion diesel",
    "Compressed gas": "Gaz comprimé",
    "Fuel cell": "Pile à combustible",
    "Scrap EAF": "Four électrique / ferraille",
    "Electrowinning": "Électroextraction",
    "Conventional": "Conventionnel",
    "Biomass": "Biomasse",
    "Hydrogen": "Hydrogène",
    "Nuclear": "Nucléaire",
    "Solar": "Solaire",
    "Wind": "Éolien",
    "Coal": "Charbon",
    "Oil": "Pétrole",
    "Other": "Autres",
}


def french(value):
    for original, translated in sorted(LABELS.items(), key=lambda item: -len(item[0])):
        value = value.replace(original, translated)
    return value


def localize(figure):
    """Translate presentation fields without touching model metadata or arrays."""
    def visit(value, key=""):
        if key == "meta":
            return value
        if isinstance(value, dict):
            return {k: visit(v, k) for k, v in value.items()}
        if isinstance(value, list):
            return [visit(v, key) for v in value]
        if isinstance(value, str) and key in {
            "name", "text", "hovertemplate", "ticktext"
        }:
            return french(value)
        return value

    localized = go.Figure(visit(figure.to_plotly_json()))
    localized.update_layout(separators=", ")
    return localized


def static_figure():
    figure = localize(source.static_figure())
    figure.update_layout(margin_r=280, legend_font_size=12)
    return figure


def prospective_figure():
    figure = localize(source.prospective_figure())
    figure.update_layout(margin_r=265, legend_font_size=11)
    return figure


def temporal_figure(view="stacked"):
    figure = localize(source.temporal_figure(view))
    figure.update_xaxes(
        range=[2000, 2130],
        tickvals=[2000, 2030, 2060, 2090, 2130],
    )
    return figure


def forcing_figure(end=2300):
    return localize(source.forcing_figure(end))


def pulse_figure(end=DEFAULT_END, *, start=WINDOW_START, reference=REFERENCE_YEAR):
    return localize(source.pulse_figure(end, start=start, reference=reference))


def mix_figure(sector, pathway=PATHWAYS[1]):
    return localize(source.mix_figure(sector, pathway))


def scenario_context_figure(indicator="GMST", region="World", pathway=PATHWAYS[1]):
    return localize(source.scenario_context_figure(indicator, region, pathway))


def scenario_context_note(indicator, region):
    if indicator == "GMST":
        return "Température moyenne mondiale · médiane MAGICC7."
    if indicator == "Population":
        return "Même population SSP2 dans les deux scénarios."
    if region == "ENC":
        return "Émissions nettes de CO₂. NPi : pas de valeur source en 2100."
    return "Émissions annuelles nettes de CO₂."
