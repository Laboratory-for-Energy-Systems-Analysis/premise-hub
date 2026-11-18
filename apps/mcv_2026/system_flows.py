"""Adapt the SETAC supply chains for projection in French."""

from functools import lru_cache
import re
import xml.etree.ElementTree as ET

from apps.setac_2026.system_flows import system_flow_svg as source_svg

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
LABELS = {
    "BECCS · NEW CHP + CCS ROUTE": "BECCS · COGÉNÉRATION + CCS",
    "DACCS · ENGINEERED ROUTE": "DACCS · CAPTAGE DANS L’AIR",
    "Atmospheric CO₂": "CO₂ atmosphérique",
    "both pathways start here": "origine des deux voies",
    "Forest": "Forêt",
    "New CHP": "Cogénération",
    "heat + power": "chaleur + électricité",
    "Solid-sorbent DAC": "DAC à sorbant solide",
    "CO₂ conditioning": "Préparation CO₂",
    "drying + compression": "séchage + compression",
    "CO₂ pipeline": "Conduite de CO₂",
    "Geological": "Stockage CO₂",
    "CO₂ storage": "géologique",
    "Residual BECCS stack CO₂": "CO₂ résiduel de BECCS",
    "CHP exports → market substitution": "Énergie exportée → substitution",
    "make-up to capture plant": "appoint de l’installation",
    "Both routes · transport + storage": "Deux voies · transport et stockage",
    "t CO₂ captured from air": "t CO₂ capté dans l’air",
    "t CO₂ uptake": "t CO₂ absorbé",
    "t CO₂ STORED": "t CO₂ STOCKÉ",
    "t wood chips": "t granulés secs",
    "GJ biomass fuel": "GJ de biomasse",
    "CO₂ capture": "captage CO₂",
    "t captured": "t capté",
    "t to atmosphere": "t vers l’atmosphère",
    "MWh capture electricity": "MWh électricité de captage",
    "MWh electricity": "MWh électricité",
    "MWh heat pump": "MWh pompe à chaleur",
    "MWh process": "MWh procédé",
    "GJ CHP heat": "GJ chaleur interne",
    "GJ heat": "GJ chaleur",
    "kg chemicals": "kg produits chimiques",
    "m³ cooling water": "m³ eau de refroidissement",
    "kg sorbent": "kg sorbant",
    "t stored": "t stocké",
    "t lost": "t perdu",
    "% loss": "% pertes",
    "2,000 km": "2 000 km",
}


def space_supply_chains(root):
    """Lower the DACCS lane and reconnect it to the shared nodes."""
    gap = 38
    dac_center = 289 + gap
    lower = f"translate(0 {gap})"
    root.set("viewBox", f"0 0 1400 {460 + gap}")

    children = list(root)
    # The two DACCS process nodes precede the common transport and storage.
    dac_start = next(i for i, child in enumerate(children)
                     if child.tag == f"{{{NS}}}rect" and child.get("y") == "245")
    shared_start = next(i for i, child in enumerate(children)
                        if child.get("d") == "M1054 184 H1064")
    for child in children[dac_start:shared_start]:
        child.set("transform", lower)

    for child in children:
        if child.get("class") == "route-label" and (child.text or "").startswith("DACCS"):
            child.set("transform", lower)
        if child.get("class") != "flow-sky":
            continue
        if child.get("d").startswith("M191 "):
            child.set("d", f"M191 194 C216 194 218 {dac_center} 244 {dac_center}")
        elif child.get("d").startswith("M885 "):
            child.set("d", f"M885 {dac_center} C1015 {dac_center} 1034 225 1042 202 Q1048 190 1054 184")
        else:
            child.set("transform", lower)

    # Keep the two input cards and the common transport summary on one baseline.
    for child in children[-1]:
        path = child.get("d", "")
        if path == "M1140 238V353":
            child.set("d", f"M1140 238V{353 + gap}")
        elif path.startswith(("M385 358", "M775 358")) or int(child.get("y", 0)) >= 354:
            child.set("transform", lower)


@lru_cache(maxsize=1)
def system_flow_svg():
    root = ET.fromstring(source_svg())
    space_supply_chains(root)
    root.find(f"{{{NS}}}title").text = "BECCS et DACCS : flux de matière, d’énergie et de CO₂"
    root.find(f"{{{NS}}}desc").text = "Flux sélectionnés par tonne nette stockée après les pertes au transport, repris de l’inventaire SETAC vérifié."
    for element in root.iter(f"{{{NS}}}text"):
        value = element.text or ""
        for original, translated in sorted(LABELS.items(), key=lambda item: -len(item[0])):
            value = value.replace(original, translated)
        # Display at most two decimals; calculation inputs remain unchanged.
        element.text = re.sub(
            r"\b\d+\.\d+\b",
            lambda match: f"{float(match[0]):.2f}".rstrip("0").rstrip(".").replace(".", ","),
            value,
        )
        # French labels are slightly longer than the original English ones.
        if element.get("class", "").startswith("flow-card"):
            element.set("style", "font-size:13px")
        if value == "Préparation CO₂":
            element.set("style", "font-size:15px")
    return ET.tostring(root, encoding="unicode")
