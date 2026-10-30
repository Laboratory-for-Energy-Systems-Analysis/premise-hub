"""Foreground process maps with source-backed physical flow quantities."""

from dash import html

from .visuals import CASE, CASES, icon_svg, label, svg_uri
from .carbon import ORIGINS, FOSSIL, NON_FOSSIL
from .layout import PREFIX
from .branding import logo_uri, tool_link

FLOW = {
    "carbon": "#00877d",
    "material": "#647988",
    "electricity": "#c47b14",
    "heat": "#c4484b",
    "fossil": ORIGINS[FOSSIL],
    "non_fossil": ORIGINS[NON_FOSSIL],
}


def _arrow(path, kind):
    colour = FLOW[kind]
    dash = (
        ' stroke-dasharray="9 6"'
        if kind == "electricity"
        else ' stroke-dasharray="9 4 2 4"'
        if kind == "heat"
        else ' stroke-dasharray="3 4"'
        if kind == "non_fossil"
        else ""
    )
    return (
        f'<path d="{path}" fill="none" stroke="{colour}" stroke-width="3"'
        f'{dash} marker-end="url(#{kind})" stroke-linejoin="round"/>'
    )


def _tag(x, y, width, lines, kind, *, supplier=False):
    colour = FLOW[kind]
    height = 28 * len(lines) + 22
    body = (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'rx="12" fill="{"#e4eff4" if supplier else "white"}" stroke="{colour}" stroke-opacity=".45"/>'
    )
    return body + "".join(
        label(x + width / 2, y + 30 + i * 28, text, 21, colour)
        for i, text in enumerate(lines)
    )


def process_quantities(case):
    """Selected physical quantities only; never infer mass from an LCIA score."""
    import hashlib
    import json
    from pathlib import Path
    from apps.setac_2026.results import case_inventory

    root = Path(__file__).resolve().parent
    if case not in CASES:
        raise ValueError(case)
    if case in ("DACCS", "BECCS"):
        quantities = case_inventory(case)
        if case == "DACCS":
            quantities["capture_process_electricity_mwh"] = (
                quantities["capture_and_heat_pump_electricity_mwh"]
                - quantities["heat_pump_electricity_mwh"]
            )
        return quantities
    if case == "ERW":
        data = json.loads((root / "data/erw_process_quantities.json").read_text())
        if (
            hashlib.sha256(
                (root / "data/coastal_erw_ei312.xlsx").read_bytes()
            ).hexdigest()
            != data["source_sha256"]
        ):
            raise ValueError("ERW process quantities no longer match the foreground")
        return data["quantities"]
    public = root.parent / "ccus_webinar/data/public"
    bau = json.loads((public / "bau_detail_2025.json").read_text())
    capture = json.loads((public / "capture_details_2025.json").read_text())
    display = json.loads((root / "data/cement_process_display.json").read_text())
    molar = capture["molar_masses"]["CO2"] / capture["molar_masses"]["C"]
    from .cement_basis import cement_scale

    scale = cement_scale(2025)
    # The full stored tonne includes kiln calcination, fuel and recaptured boiler
    # carbon. Derive its total routing from physical capture/retention rates,
    # never from characterized LCIA rows. Non-fossil carbon is the public SI
    # fuel fraction; all remaining captured carbon is fossil/mineral.
    eta = capture["rates"]["capture_fraction"]
    retention = 0.95 * (1 - 0.0144)
    stored = 1000.0
    gross = stored / (eta * retention)
    non_gross = capture["systems"]["CCS"]["non_fossil_fuel"]["inlet_c"] * molar * scale

    def route(inlet):
        captured = inlet * eta
        liquid = captured * 0.05
        transport = (captured - liquid) * 0.0144
        return dict(
            inlet_co2_kg=inlet,
            captured_co2_kg=captured,
            stored_co2_kg=captured - liquid - transport,
            uncaptured_co2_kg=inlet - captured,
            liquefaction_loss_co2_kg=liquid,
            transport_loss_co2_kg=transport,
        )

    total = route(gross)
    return {
        "clinker_t": scale,
        "chalk_kg_approx": bau["limestone_as_chalk_slurry"]["value"] * scale,
        "fuel_gj": bau["kiln_energy"]["value"] * scale,
        "fuel_co2_kg": sum(
            bau["emissions"][k]["value"] for k in ("fuel_fossil", "fuel_non_fossil")
        ) * scale,
        "gross_co2_kg": gross,
        **{k: v for k, v in total.items() if k != "inlet_co2_kg"},
        "known_air_co2_kg": gross - stored,
        "capture_fraction": eta,
        "capture_electricity_label": display["capture_electricity_label"],
        "capture_gas_label": display["capture_gas_label"],
        "origins": {"fossil": route(gross - non_gross), "non_fossil": route(non_gross)},
    }


def _origin_tag(x, y, width, title, fossil, non_fossil):
    body = f'<rect x="{x}" y="{y}" width="{width}" height="100" rx="12" fill="white" stroke="#91a4ad" stroke-opacity=".45"/>'
    body += label(x + width / 2, y + 26, title, 20)
    body += label(
        x + width / 2, y + 55, f"Fossil: {fossil:.1f} kg CO₂", 20, FLOW["fossil"]
    )
    body += label(
        x + width / 2,
        y + 83,
        f"Non-fossil: {non_fossil:.1f} kg CO₂",
        20,
        FLOW["non_fossil"],
    )
    return body


def process_uri(case):
    """Amounts label connectors; fixed-width arrows do not encode magnitude."""
    q = process_quantities(case)
    colour = CASE[case]["colour"]
    nodes = {
        "DACCS": [
            ("atmosphere", "Ambient air", "Atmospheric CO₂"),
            ("capture", "Solid-sorbent DAC", "Low-temperature TVSA"),
            ("capture", "Conditioning", "Dry + compress CO₂"),
            ("transport", "CO₂ transport", "Pipeline"),
            ("storage", "Geological storage", "Inject + retain CO₂"),
        ],
        "BECCS": [
            ("forest", "Forest + harvest", "Carbon in wood"),
            ("heat", "Biomass CHP", "Electricity + heat"),
            ("capture", "Flue-gas capture", "90% capture"),
            ("transport", "CO₂ transport", "Pipeline"),
            ("storage", "Geological storage", "Inject + retain CO₂"),
        ],
        "ERW": [
            ("rock", "Rock extraction", "Olivine-rich rock"),
            ("power", "Crush + grind", "Increase surface area"),
            ("transport", "Haul + spread", "Coastal deployment"),
            ("ocean", "Rock dissolution", "Release alkalinity"),
            ("uptake", "Ocean carbon", "Dissolved inorganic C"),
        ],
        "Cement + CCS": [
            ("rock", "Raw materials", "Chalk + other inputs"),
            ("kiln", "Kiln + gas boiler", "Clinker + flue gas"),
            ("capture", "Flue-gas capture", "90% capture"),
            ("transport", "Condition + ship", "Liquefy + transport"),
            ("storage", "Geological storage", "North Sea gas field"),
        ],
    }[case]
    if case == "DACCS":
        amounts = [(f"{q['gross_capture_t_co2']:.3f} t", "CO₂")] * 3 + [
            (f"{q['gross_storage_t_co2']:.3f} t", "CO₂")
        ]
    elif case == "BECCS":
        amounts = [
            (f"{q['spruce_woodchips_t_dry']:.3f} t", "dry wood"),
            (f"{q['gross_flue_gas_co2_t']:.3f} t", "CO₂"),
            (f"{q['gross_capture_t_co2']:.3f} t", "CO₂"),
            (f"{q['gross_storage_t_co2']:.3f} t", "CO₂"),
        ]
    elif case == "ERW":
        amounts = [("1.25 t", "rock")] * 3 + [("", "Alkalinity")]
    else:
        amounts = [
            (f"≈{q['chalk_kg_approx'] / 1000:.1f} t", "chalk"),
            (f"{q['gross_co2_kg']:.0f} kg", "CO₂"),
            (f"{q['captured_co2_kg']:.0f} kg", "CO₂"),
            (f"{q['stored_co2_kg']:.0f} kg", "CO₂"),
        ]
    body = "<defs>"
    for kind, c in FLOW.items():
        body += f'<marker id="{kind}" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L10 5L0 10Z" fill="{c}"/></marker>'
    body += (
        '</defs><rect x="0" y="0" width="1400" height="620" rx="20" fill="#f5f8fa"/>'
    )

    for i, (amount, unit) in enumerate(amounts):
        kind = "material" if case == "ERW" or (i == 0 and case != "DACCS") else "carbon"
        x = 210 + i * 280
        if case == "Cement + CCS" and i > 0:
            field = ("inlet_co2_kg", "captured_co2_kg", "stored_co2_kg")[i - 1]
            for kind, y in (("fossil", 262), ("non_fossil", 320)):
                body += _arrow(f"M{x} {y}H{x + 87}", kind)
                body += label(
                    x + 45,
                    y - 14,
                    f"{q['origins'][kind][field]:.0f} kg",
                    20,
                    FLOW[kind],
                )
            continue
        body += _arrow(f"M{x} 280H{x + 87}", kind)
        body += label(x + 45, 242, amount, 21, FLOW[kind])
        body += label(x + 45, 264, unit, 17, FLOW[kind])

    if case == "DACCS":
        body += _tag(
            15,
            20,
            225,
            [
                f"Heat pump · COP {q['heat_pump_cop']:.0f}",
                f"{q['heat_pump_electricity_mwh']:.3f} MWh electricity",
            ],
            "electricity",
        )
        body += _arrow("M125 98V175H350V210", "heat")
        body += label(235, 160, f"{q['delivered_low_temperature_heat_gj']:.2f} GJ capture heat", 20, FLOW["heat"])
        body += _tag(
            280, 20, 330,
            ["Air capture electricity", f"{q['capture_process_electricity_mwh']:.3f} MWh process"],
            "electricity", supplier=True,
        )
        body += _arrow("M445 98V210", "electricity")
        body += _tag(
            820,
            20,
            555,
            [
                "Compression, transport + injection",
                f"{q['compression_storage_electricity_mwh'] * 1000:.0f} kWh electricity · total",
            ],
            "electricity",
            supplier=True,
        )
        for x in (685, 965, 1245):
            body += _arrow(f"M1100 98V155H{x}V210", "electricity")
        body += _tag(210, 410, 405, [f"{q['sorbent_kg']:.2f} kg sorbent"], "material", supplier=True)
        body += _arrow("M405 410V355", "material")
        body += _tag(
            760,
            410,
            510,
            [
                f"{q['transport_loss_co2_t'] * 1000:.1f} kg CO₂ → air",
                f"{q['pipeline_distance_km']:,} km pipeline · {q['pipeline_loss_fraction']:.1%} loss",
            ],
            "carbon",
        )
        body += _arrow("M965 355V410", "carbon")
    elif case == "BECCS":
        body += _tag(
            15,
            20,
            235,
            ["Atmospheric uptake", f"{q['forest_co2_uptake_t']:.3f} t CO₂"],
            "carbon",
        )
        body += _arrow("M125 98V210", "carbon")
        body += _tag(
            500,
            20,
            325,
            [
                f"{q['capture_chemicals_kg']:.3f} kg chemicals",
                f"{q['cooling_water_m3']:.1f} m³ cooling water",
            ],
            "material",
            supplier=True,
        )
        body += _arrow("M710 98V210", "material")
        body += _tag(
            880,
            20,
            495,
            [
                "Compression, transport + injection",
                f"{q['compression_storage_electricity_mwh'] * 1000:.0f} kWh electricity · total",
            ],
            "electricity",
            supplier=True,
        )
        for x in (685, 965, 1245):
            body += _arrow(f"M1125 98V140H{x}V210", "electricity")
        body += _arrow("M385 210V175H660V210", "heat")
        body += label(
            485,
            165,
            f"{q['internal_capture_heat_gj']:.2f} GJ CHP heat",
            20,
            FLOW["heat"],
        )
        body += _tag(
            20,
            410,
            215,
            [
                "Electricity export",
                f"{q['electricity_coproduct_mwh'] * 1000:.0f} kWh",
            ],
            "electricity",
        )
        body += _arrow("M375 355V385H130V410", "electricity")
        body += _tag(260, 410, 215, ["Heat export", f"{q['net_heat_coproduct_gj']:.3f} GJ"], "heat")
        body += _arrow("M425 355V390H365V410", "heat")
        body += _tag(
            505,
            410,
            395,
            ["Uncaptured stack CO₂", f"{q['capture_loss_co2_t'] * 1000:.1f} kg → air"],
            "carbon",
        )
        body += _arrow("M685 355V410", "carbon")
        body += _tag(
            945,
            410,
            430,
            [
                "Transport losses",
                f"{q['transport_loss_co2_t'] * 1000:.1f} kg CO₂ → air",
            ],
            "carbon",
        )
        body += _arrow("M965 355V410", "carbon")
        body += label(
            250,
            382,
            f"Wood fuel: {q['biomass_fuel_energy_gj']:.2f} GJ",
            19,
            FLOW["material"],
        )
    elif case == "ERW":
        body += _tag(
            20,
            20,
            360,
            [
                "Deployment electricity",
                f"{q['electricity_kwh']:.1f} kWh electricity",
            ],
            "electricity",
            supplier=True,
        )
        for x in (125, 405, 685):
            body += _arrow(f"M210 98V155H{x}V210", "electricity")
        body += _tag(410, 20, 335, ["Machinery diesel", f"{q['direct_diesel_mj']:.1f} MJ fuel"], "material", supplier=True)
        body += _arrow("M575 98V180H685V210", "material")
        body += _tag(
            1040,
            20,
            335,
            [
                "Eventual gross potential",
                f"{q['eventual_uptake_kg'] / 1000:.2f} t atmospheric CO₂",
            ],
            "carbon",
        )
        body += _arrow("M1245 98V210", "carbon")
        body += label(1225, 170, "Air–sea exchange", 20, FLOW["carbon"], anchor="end")
        body += _tag(
            345,
            410,
            490,
            [f"{q['truck_tkm']:.1f} t·km freight · {q['water_m3']:.3f} m³ water"],
            "material",
            supplier=True,
        )
        body += _arrow("M685 410V355", "material")
        body += _tag(
            880,
            410,
            495,
            [
                "Potential Ni mobilization",
                f"≤ {q['nickel_upper_bound_kg']:.2f} kg · upper bound",
            ],
            "material",
        )
        body += _arrow("M965 355V410", "material")
    else:
        body += _tag(
            245,
            20,
            255,
            ["Kiln fuels", f"{q['fuel_gj']:.2f} GJ fuel"],
            "material",
            supplier=True,
        )
        body += _arrow("M405 98V210", "material")
        body += _tag(
            505,
            20,
            355,
            [
                "Capture electricity",
                q["capture_electricity_label"],
            ],
            "electricity",
            supplier=True,
        )
        body += _arrow("M720 98V210", "electricity")
        body += _tag(15, 20, 225, ["Capture gas boiler", q["capture_gas_label"], "Fossil CO₂ recaptured"], "material")
        body += _arrow("M125 126V154H620V210", "heat")
        body += label(240, 145, "Boiler heat", 19, FLOW["heat"])
        body += _arrow("M385 210V183H660V210", "heat")
        body += label(500, 172, "Recovered kiln heat", 19, FLOW["heat"])
        body += _tag(
            880,
            20,
            495,
            ["Storage-chain losses", "5% liquefaction → 1.44% transport"],
            "material",
        )
        body += _tag(20, 410, 430, ["Associated product", f"{q['clinker_t']:.3f} t grey clinker"], "material")
        body += _arrow("M405 355V385H230V410", "material")
        fossil, non = q["origins"]["fossil"], q["origins"]["non_fossil"]
        body += _origin_tag(
            505,
            410,
            395,
            "Uncaptured kiln + boiler CO₂",
            fossil["uncaptured_co2_kg"],
            non["uncaptured_co2_kg"],
        )
        body += _origin_tag(
            945,
            410,
            430,
            "Conditioning + transport losses",
            fossil["liquefaction_loss_co2_kg"] + fossil["transport_loss_co2_kg"],
            non["liquefaction_loss_co2_kg"] + non["transport_loss_co2_kg"],
        )
        for x in (685, 965):
            body += _arrow(f"M{x - 7} 355V410", "fossil")
            body += _arrow(f"M{x + 7} 355V410", "non_fossil")

    atmosphere_x, atmosphere_w = (505, 870) if case != "ERW" else (20, 295)
    body += (
        f'<rect x="{atmosphere_x}" y="550" width="{atmosphere_w}" height="52" '
        'rx="24" fill="#e5eff3" stroke="#91a4ad"/>'
    )
    body += label(atmosphere_x + atmosphere_w / 2, 584, "Atmosphere", 23, FLOW["carbon"])
    if case == "DACCS":
        body += _arrow("M1015 488V550", "carbon")
    elif case == "BECCS":
        body += _arrow("M702 488V550", "carbon")
        body += _arrow("M1160 488V550", "carbon")
    elif case == "ERW":
        body += _tag(20, 410, 295, ["Diesel exhaust", "CO₂ · unquantified"], "carbon")
        body += _arrow("M620 355V380H167V410", "carbon")
        body += _arrow("M167 488V550", "carbon")
    else:
        for x in (702, 1160):
            body += _arrow(f"M{x - 7} 510V550", "fossil")
            body += _arrow(f"M{x + 7} 510V550", "non_fossil")

    # This badge is a data-source key, not a physical flow or an LCA credit.
    bg_x = 360 if case == "ERW" else 20
    body += f'<rect x="{bg_x}" y="535" width="450" height="72" rx="12" fill="#e4eff4" stroke="#a5bfcc"/>'
    body += icon_svg("database", "#527b90", bg_x + 17, 543, 36)
    body += f'<image href="{logo_uri("ecoinvent")}" x="{bg_x + 78}" y="546" width="155" height="26"/>'
    body += label(bg_x + 331, 566, "background", 21, "#375d70")
    body += label(bg_x + 225, 598, "Shaded inputs link to database unit processes", 18, "#435d6a", weight=400)

    for i, (kind, title, subtitle) in enumerate(nodes):
        x = 20 + i * 280
        body += f'<rect x="{x}" y="210" width="190" height="145" rx="16" fill="white" stroke="{colour}" stroke-width="1.5"/>'
        body += icon_svg(kind, colour, x + 68, 220, 54)
        body += label(x + 95, 308, title, 20, colour)
        body += label(x + 95, 337, subtitle, 16, "#435d6a", weight=400)
    return svg_uri(
        body, 1400, 620, f"{case}: main physical flows and amounts per native service"
    )


DESCRIPTIONS = {
    "DACCS": "Low-temperature solid-sorbent DAC uses temperature-vacuum swing adsorption. Per net tonne stored, air capture takes 12.24 GJ of heat from a COP-3 heat pump using 1.134 MWh electricity, plus 0.720 MWh direct capture electricity. Conditioning, transport and injection require another 139 kWh in total. Sorbent replacement and transport CO₂ losses are separate streams.",
    "BECCS": "Atmospheric CO₂ enters growing forest; harvested wood fuels combined heat and power. Flue-gas CO₂ is captured, transported and stored. CHP supplies capture heat and exports useful energy; capture chemicals, water and residual CO₂ are shown.",
    "ERW": "Olivine-rich rock is extracted, ground, hauled and spread on the coast. The dated case operates in 2030–2049 with twenty annual batches sharing the same total rock demand. Dissolution releases alkalinity; air–sea exchange draws atmospheric CO₂ into dissolved ocean carbon and can continue after operation ends.",
    "Cement + CCS": "Limestone and fuel feed a clinker kiln. Flue-gas CO₂ is captured, conditioned, transported and stored, using additional materials and energy. The basis is one tonne of CO₂ physically stored, with 1.135 tonnes of associated clinker in 2025 and full calcination, fuel and boiler carbon included. Uncaptured CO₂ and storage-chain losses go to the atmosphere; capture mainly avoids release of mineral and fossil carbon.",
}


def inventory_sources(case):
    """Public source lineage of the adapted foreground illustrated on each map."""
    storage = [
        ("Koornneef et al. (2008)", "https://doi.org/10.1016/j.ijggc.2008.06.008"),
        ("Terlouw et al. (2021)", "https://doi.org/10.1021/acs.est.1c03263"),
    ]
    inventory = {
        "DACCS": [
            ("Deutz & Bardow (2021)", "https://doi.org/10.1038/s41560-020-00771-9"),
            ("Qiu et al. (2022)", "https://doi.org/10.1038/s41467-022-31146-1"),
        ],
        "BECCS": [
            ("ecoinvent 3.12 · forest + CHP", "https://support.ecoinvent.org/ecoinvent-version-3.12"),
            ("Volkart et al. (2013) · capture", "https://doi.org/10.1016/j.ijggc.2013.03.003"),
        ],
        "ERW": [
            ("Foteinis et al. (2023)", "https://doi.org/10.1021/acs.est.2c08633"),
            ("Supporting inventory · Table S1", "https://doi.org/10.1021/acs.est.2c08633.s001"),
            ("Reviewed ecoinvent 3.12 adaptation", PREFIX + "erw-review"),
        ],
        "Cement + CCS": [
            ("Gallego Dávila et al. (2023) · SI.2", "https://doi.org/10.1016/j.jclepro.2023.138935"),
            ("Reviewed cement webinar adaptation", "/ccus-webinar/"),
        ],
    }[case]
    groups = [("Adapted inventory", inventory)]
    if case in ("DACCS", "BECCS"):
        groups.append(("CO₂ transport / storage", storage))
    return html.Div(
        [
            html.Span([
                html.Strong(title + ": "),
                *[item for i, (name, url) in enumerate(links)
                  for item in ([" · ", html.A(name, href=url, target="_blank", rel="noopener noreferrer")]
                               if i else [html.A(name, href=url, target="_blank", rel="noopener noreferrer")])],
            ])
            for title, links in groups
        ], className="process-sources", **{"aria-label": f"{case} inventory sources"},
    )


def flow_legend():
    entries = [
        ("electricity", "Electricity", "kWh or MWh"),
        ("heat", "Heat", "GJ of delivered heat"),
        ("material", "Materials + fuels", "kg, t, m³ · fuel energy in MJ/GJ"),
        ("carbon", "CO₂", "kg or t · capture, storage, release"),
    ]
    return html.Div(
        [html.Div(
            [html.Span([html.I(className=kind), html.Strong(name)]), html.Small(units),
             *([html.Div([
                 html.Span([html.I(className="fossil"), "Fossil CO₂"]),
                 html.Span([html.I(className="non_fossil"), "Non-fossil CO₂"]),
             ], className="process-co2-origins")] if kind == "carbon" else [])],
            className=f"process-flow-key flow-key-{kind}",
        ) for kind, name, units in entries], className="process-legend",
        **{"aria-label": "Flow colours and physical units"},
    )


def process_carousel(selected_case=None):
    """Screen: accessible case tabs. PDF: a single case per expanded page."""
    selected_case = selected_case or CASES[0]
    if selected_case not in CASES:
        raise ValueError(selected_case)
    selected = CASES.index(selected_case)
    return html.Div(
        [
            html.Div(
                [
                    html.Button(
                        case,
                        role="tab",
                        **{
                            "data-process-select": str(i),
                            "aria-selected": str(i == selected).lower(),
                            "aria-label": f"Show {case} process diagram",
                            "tabIndex": 0 if i == selected else -1,
                        },
                        style={"--case-colour": CASE[case]["colour"]},
                    )
                    for i, case in enumerate(CASES)
                ],
                className="process-tabs",
                role="tablist",
                **{"aria-label": "Technology process diagrams"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong(case),
                                    *([html.Span("Low-temperature solid-sorbent DAC · TVSA", className="process-technology")]
                                      if case == "DACCS" else []),
                                    html.Span(
                                        CASE[case]["service"]
                                        + (
                                            " · 2025 · includes calcination + fuel + boiler CO₂"
                                            if case == "Cement + CCS"
                                            else ""
                                        )
                                    ),
                                ],
                                className="process-heading",
                            ),
                            html.Img(
                                src=process_uri(case),
                                alt=DESCRIPTIONS[case] + " Shaded supplier inputs link to unit processes in the ecoinvent 3.12 cut-off background; foreground design, carbon routing and timing remain analyst-defined.",
                                className="process-diagram",
                            ),
                            inventory_sources(case),
                        ],
                        className="process-panel",
                        role="tabpanel",
                        hidden=i != selected,
                        style={"--case-colour": CASE[case]["colour"]},
                        **{
                            "data-process-panel": str(i),
                            "aria-label": f"{case} process flows",
                        },
                    )
                    for i, case in enumerate(CASES)
                ],
            ),
            html.Div(
                ["Foreground systems modelled with ", tool_link("brightway"),
                 " · linked to ecoinvent background suppliers"],
                className="foreground-modelling",
            ),
            html.Div(
                [
                    flow_legend(),
                    html.Div(
                        [
                            html.Button(
                                "←",
                                **{
                                    "data-process-step": "-1",
                                    "aria-label": "Previous technology",
                                },
                            ),
                            html.Span(
                                f"{selected + 1} / 4",
                                className="process-position",
                                role="status",
                            ),
                            html.Button(
                                "→",
                                **{
                                    "data-process-step": "1",
                                    "aria-label": "Next technology",
                                },
                            ),
                        ],
                        className="process-flip",
                    ),
                ],
                className="process-toolbar",
            ),
        ],
        className="process-carousel",
        **{"data-process-index": str(selected)},
    )
