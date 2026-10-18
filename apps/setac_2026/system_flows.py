"""Condensed flow diagram using lca_time artwork and reviewed inventory values."""

from functools import lru_cache
from pathlib import Path
import xml.etree.ElementTree as ET

from .results import case_inventory

NS = "http://www.w3.org/2000/svg"
SOURCE = Path(__file__).resolve().parents[1] / "lca_time/assets/case-pathways.svg"
ET.register_namespace("", NS)


@lru_cache(maxsize=1)
def system_flow_svg():
    """Retain both routes and icons, replacing small notes with physical flows."""
    beccs, daccs = (case_inventory(case) for case in ("BECCS", "DACCS"))
    source = SOURCE.read_text()
    # Replace the overview's reference inset and generic DAC energy tag with
    # quantified flow callouts. The reference is stated below the slide figure.
    for start, end in (
        ("<!-- Greenfield BECCS reference arm -->", "<!-- Solid-sorbent DAC node -->"),
        (
            "<!-- DACCS energy input -->",
            "<!-- Shared transport and geological storage -->",
        ),
    ):
        before, rest = source.split(start, 1)
        _, after = rest.split(end, 1)
        source = before + end + after
    root = ET.fromstring(source)
    root.set("viewBox", "0 0 1400 460")
    root.find(f"{{{NS}}}title").text = "BECCS and DACCS: material, energy and CO₂ flows"
    root.find(f"{{{NS}}}desc").text = (
        "Selected physical flows per net tonne of atmospheric CO₂ stored. "
        "Both routes capture 1.029 tonnes and lose 0.029 tonnes in transport. "
        "BECCS consumes wood chips and capture inputs and exports useful energy. "
        "DACCS consumes sorbent and electricity for capture and heat-pump heat."
    )
    replacements = {
        "Norway spruce": f"{beccs['forest_co2_uptake_t']:.3f} t CO₂ uptake",
        "Wood chips": f"{beccs['spruce_woodchips_t_dry']:.3f} t wood chips",
        "forest supply": f"{beccs['biomass_fuel_energy_gj']:.2f} GJ biomass fuel",
        "CO₂ capture": f"{beccs['host_flue_gas_capture_rate']:.0%} CO₂ capture",
        "post-combustion": f"{beccs['gross_capture_t_co2']:.3f} t captured",
        "low-temperature regeneration": f"{daccs['atmospheric_co2_uptake_t']:.3f} t CO₂ captured from air",
        "transport to storage": f"{beccs['pipeline_distance_km']:,} km · {beccs['pipeline_loss_fraction']:.1%} loss",
        "SHARED DESTINATION": f"{beccs['gross_storage_t_co2']:.3f} t CO₂ STORED",
    }
    found = set()
    for element in root.iter(f"{{{NS}}}text"):
        if element.text in replacements:
            found.add(element.text)
            element.text = replacements[element.text]
            if element.get("class") == "node-title":
                element.set("style", "font-size:15px")
    if found != set(replacements):
        raise ValueError(
            f"Source diagram changed: missing labels {set(replacements) - found}"
        )

    # Keep the DACCS stream visible around the added BECCS input callout.
    for element in root.iter(f"{{{NS}}}path"):
        if element.get("d") == "M885 289 C983 289 991 199 1054 184":
            element.set("d", "M885 289 C1015 289 1034 225 1042 202 Q1048 190 1054 184")

    # The connectors stay behind their callout boxes; all values come from the
    # source inventory rather than a second, hard-coded inventory bundle.
    additions = f"""<g xmlns="{NS}">
      <defs>
        <marker id="setac-energy" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L8 4L0 8Z" fill="#d18a12"/></marker>
        <marker id="setac-material" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L8 4L0 8Z" fill="#6f7f87"/></marker>
        <style>
          .flow-card-title {{ font:700 16px Arial,sans-serif; fill:#0b3b52; text-anchor:middle; }}
          .flow-card-value {{ font:700 16px Arial,sans-serif; fill:#344b57; text-anchor:middle; }}
          .flow-card-note {{ font:14px Arial,sans-serif; fill:#53636c; text-anchor:middle; }}
          .flow-input {{ fill:none; stroke-width:2.5; stroke-linejoin:round; }}
        </style>
      </defs>
      <path d="M925 76H1000V38H1034" class="flow-input" stroke="#c44e52" marker-end="url(#arrow-red)"/>
      <rect x="1035" y="12" width="345" height="48" rx="11" fill="#fbeef0" stroke="#dfb8bb"/>
      <text x="1207" y="31" class="flow-card-title">Residual BECCS stack CO₂</text>
      <text x="1207" y="50" class="flow-card-note">{beccs['capture_loss_co2_t']:.3f} t to atmosphere</text>

      <path d="M675 151V160H450V167" class="flow-input" stroke="#d18a12" marker-end="url(#setac-energy)"/>
      <rect x="245" y="168" width="420" height="51" rx="11" fill="#fff8e7" stroke="#ead49e"/>
      <text x="455" y="188" class="flow-card-title">CHP exports → market substitution</text>
      <text x="455" y="208" class="flow-card-value">{beccs['electricity_coproduct_mwh']:.3f} MWh electricity + {beccs['net_heat_coproduct_gj']:.3f} GJ heat</text>

      <path d="M855 168V153" class="flow-input" stroke="#6f7f87" marker-end="url(#setac-material)"/>
      <rect x="685" y="168" width="340" height="51" rx="11" fill="#f1f5f6" stroke="#c9d6da"/>
      <text x="855" y="188" class="flow-card-value">{beccs['internal_capture_heat_gj']:.3f} GJ CHP heat · {beccs['capture_chemicals_kg']:.3f} kg chemicals</text>
      <text x="855" y="208" class="flow-card-note">+ {beccs['cooling_water_m3']:.1f} m³ cooling water</text>

      <path d="M385 358V334" class="flow-input" stroke="#d18a12" marker-end="url(#setac-energy)"/>
      <rect x="245" y="359" width="405" height="86" rx="12" fill="#fff8e7" stroke="#ead49e"/>
      <text x="447" y="380" class="flow-card-title">{daccs['capture_and_heat_pump_electricity_mwh']:.3f} MWh capture electricity</text>
      <text x="447" y="403" class="flow-card-note">{daccs['capture_and_heat_pump_electricity_mwh'] - daccs['heat_pump_electricity_mwh']:.3f} MWh process + {daccs['heat_pump_electricity_mwh']:.3f} MWh heat pump</text>
      <text x="447" y="428" class="flow-card-value">→ {daccs['delivered_low_temperature_heat_gj']:.3f} GJ heat · COP {daccs['heat_pump_cop']:.0f}</text>

      <path d="M775 358V344H500V334" class="flow-input" stroke="#6f7f87" marker-end="url(#setac-material)"/>
      <rect x="665" y="359" width="235" height="86" rx="12" fill="#f1f5f6" stroke="#c9d6da"/>
      <text x="782" y="389" class="flow-card-title">{daccs['sorbent_kg']:.3f} kg sorbent</text>
      <text x="782" y="414" class="flow-card-note">make-up to capture plant</text>

      <path d="M1140 238V353" class="flow-input" stroke="#008a82" stroke-dasharray="5 4"/>
      <rect x="970" y="354" width="410" height="91" rx="12" fill="#edf8f7" stroke="#9ecdc6"/>
      <text x="1175" y="375" class="flow-card-title">Both routes · transport + storage</text>
      <text x="1175" y="400" class="flow-card-value">{beccs['gross_capture_t_co2']:.3f} t captured − {beccs['transport_loss_co2_t']:.3f} t lost</text>
      <text x="1175" y="426" class="flow-card-note">{beccs['gross_storage_t_co2']:.3f} t stored · {beccs['compression_storage_electricity_mwh']:.3f} MWh electricity</text>
    </g>"""
    root.append(ET.fromstring(additions))
    return ET.tostring(root, encoding="unicode")
