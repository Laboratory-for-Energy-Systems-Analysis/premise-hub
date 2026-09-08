"""Evidence-led presentation components; never calculates or changes LCA results."""

from collections import defaultdict
import csv
import json
from pathlib import Path
from urllib.parse import quote

from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .diagrams import _svg, _text, _icon, _arrow, _node, icon_uri

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = {
    "contract": "data/model_contract.json",
    "quantities": "data/runtime/system_flows_2025.json",
    "bau-public": "data/public/bau_detail_2025.json",
    "capture-public": "data/public/capture_details_2025.json",
    "utilities": "data/runtime/direct_utilities_2025.json",
    "lifetimes": "data/assumptions/component_lifetimes.json",
    "heat-pump": "data/assumptions/industrial_heat_pump.json",
    "jet-yield": "data/assumptions/methanol_to_jet.json",
    "uptake": "data/assumptions/non_fossil_uptake_profiles.json",
    "uptake-revised": "data/assumptions/non_fossil_uptake_candidate.json",
}


def read_json(relative):
    path = ROOT / relative
    return json.loads(path.read_text()) if path.is_file() else {}


def link(text, resource):
    return html.A(
        text + " ↗",
        href="evidence/" + resource,
        target="_blank",
        className="source-link",
    )


def table(headers, rows, cls="evidence-table"):
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(x) for x in headers])),
            html.Tbody([html.Tr([html.Td(x) for x in row]) for row in rows]),
        ],
        className=cls,
    )


def artwork(body, title, height=450):
    return html.Img(
        src="data:image/svg+xml;charset=utf-8,"
        + quote(_svg(body, 1400, height, title)),
        alt=title,
        className="explanation-svg",
    )


def chronology_rows():
    contract = read_json(EVIDENCE["contract"])
    components = read_json(EVIDENCE["lifetimes"])
    profiles = read_json(EVIDENCE["uptake"])["profiles"]
    rows = []
    for fuel in profiles:
        # These are cohort-wide uptake windows, not one pre-project block.
        rows.append(
            (
                fuel["fuel"],
                2035 + min(fuel["offsets"]),
                2064 + max(fuel["offsets"]),
                "bio",
                [],
            )
        )
    rows += [
        ("Construction", 2035, 2035, "material", [2035]),
        ("Operation / production", 2035, 2064, "carbon", []),
        ("Fuel use (+1 year)", 2036, 2065, "fossil", []),
        ("End of life", 2065, 2065, "material", [2065]),
    ]
    return rows


def concept(stage):
    if stage in {'fair', 'pulse'}:
        from .climate_concepts import climate_concept
        return climate_concept(stage)
    b = ""
    if stage == "primer":
        for x, title, kind in (
            (45, "Product system", "kiln"),
            (525, "Inventory", "atmosphere"),
            (1045, "Climate indicator", "response"),
        ):
            b += _icon(kind, x, 38, 75, "carbon") + _text(x, 146, title, "title")
        b += _text(45, 205, "One tonne of clinker", "label")
        b += _text(45, 247, "Suppliers + kiln + displaced products", "label")
        b += _arrow("M415 230H495", "material")
        for i, label in enumerate(
            (
                "Fossil CO₂ emitted",
                "Non-fossil CO₂ uptake / release",
                "CH₄, N₂O and other flows",
            )
        ):
            b += _text(525, 200 + i * 47, label, "label")
        b += _arrow("M920 230H1015", "time")
        b += _text(1045, 205, "GWP100", "title")
        b += _text(1045, 247, "kg CO₂-equivalent", "label")
        b += _text(
            700,
            354,
            "A characterization factor converts each flow into CO₂-equivalents. Add these contributions with their signs.",
            "label",
            "middle",
        )
        b += _text(
            700,
            405,
            "The result expresses climate impact in CO₂-equivalents. It is not the actual mass of CO₂ emitted.",
            "label",
            "middle",
        )
    elif stage == "current":
        b += _text(60, 38, "ONE LIFE CYCLE", "title") + _text(
            820, 38, "ONE INVENTORY LEDGER", "title"
        )
        for i, (label, kind, date) in enumerate(
            (
                ("Historical uptake", "fuel", "Before fuel use"),
                ("Build and replace", "resources", "Across the project"),
                ("Operate and use fuel", "jet", "Across operating years"),
            )
        ):
            y = 70 + i * 96
            b += _node(60, y, 430, label, kind, "carbon", date)
            b += _arrow(f"M490 {y+36}H650V210H790", "material")
        b += '<rect x="790" y="75" width="550" height="286" rx="15" fill="#eff5f6" stroke="#abc3ce"/>'
        for i, text in enumerate(
            (
                "2025 foreground + 2025 background",
                "CO₂, CH₄, N₂O … and resource uptake",
                "Emissions and credits are characterized",
                "One net GWP100 score per tonne clinker",
            )
        ):
            b += _text(824, 128 + i * 57, text, "label")
        b += _text(
            700,
            409,
            "Dates are not preserved in the result; physical events do not all occur in 2025.",
            "label",
            "middle",
        )
    elif stage == "trails":
        low, high = 1995, 2065
        xx = lambda year: 330 + (year - low) / (high - low) * 990
        for year in (1995, 2015, 2035, 2050, 2065):
            x = xx(year)
            b += f'<path d="M{x} 40V376" stroke="#d7e2e6"/>' + _text(
                x, 28, year, "label", "middle"
            )
        for i, (name, start, end, tone, points) in enumerate(chronology_rows()):
            y = 58 + i * 31
            b += _text(18, y + 6, name, "label")
            color = {
                "bio": "#3e7654",
                "carbon": "#008a82",
                "fossil": "#c44e52",
                "material": "#738994",
            }[tone]
            b += f'<path d="M{xx(start)} {y}H{xx(end)}" stroke="{color}" stroke-width="9" stroke-linecap="round"/>'
            for point in points:
                b += f'<circle cx="{xx(point)}" cy="{y}" r="7" fill="{color}"/>'
        b += _text(
            18,
            403,
            "Example: 2040 production → 2040 suppliers and fuel credit → synthetic combustion in 2041",
            "label",
        )
        b += _text(
            18,
            434,
            "Uptake periods include fuel used in all operating years. Appendix D shows equipment replacement dates.",
            "note",
        )
    elif stage == "fair":
        labels = (
            ("Dated greenhouse gases", "CO₂ · CH₄ · N₂O …", "atmosphere"),
            ("Radiative forcing", "Change in Earth's energy balance", "response"),
            (
                "Temperature response",
                "Climate-system inertia changes the shape",
                "globe",
            ),
        )
        for i, (title, subtitle, icon) in enumerate(labels):
            x = 30 + i * 475
            b += _icon(icon, x, 28, 60, "time") + _text(x + 75, 60, title, "title")
            b += _text(x, 107, subtitle, "label")
            b += f'<path d="M{x+10} 160V325H{x+410}" stroke="#8ca4af" fill="none"/>'
            if i == 0:
                for offset, height in ((70, 70), (130, 140), (200, 90), (270, 35)):
                    b += _arrow(f"M{x+offset} 325V{325-height}", "carbon")
            else:
                path = f"M{x+10} 325C{x+70} 320 {x+90} {150 if i==1 else 270} {x+180} {175 if i==1 else 205}S{x+300} {250 if i==1 else 190} {x+410} {265 if i==1 else 195}"
                b += f'<path d="{path}" fill="none" stroke="#c44e52" stroke-width="5"/>'
            if i < 2:
                b += _arrow(f"M{x+422} 228H{x+460}", "time")
        b += _text(
            700,
            386,
            "The same dated inventory can have a different GWP score, forcing profile and temperature profile.",
            "label",
            "middle",
        )
        b += _text(
            700,
            426,
            "Schematic profiles, not case results · TRAILS retains species and dates; FaIR calculates the response.",
            "note",
            "middle",
        )
    else:
        for i, label in enumerate(
            ("System response", "Scaled 2035 CO₂-pulse response")
        ):
            x = 45 + i * 720
            b += _text(x, 38, label, "title")
            b += f'<rect x="{x+55}" y="75" width="505" height="235" fill="#f0eaf8"/>'
            b += f'<path d="M{x+25} 85V310H{x+600}" stroke="#78909b" fill="none"/>'
            if i == 0:
                curve = f"M{x+55} 300C{x+160} 300 {x+160} 170 {x+270} 180S{x+460} 250 {x+560} 230"
            else:
                curve = f"M{x+55} 300H{x+120}V145C{x+210} 165 {x+300} 245 {x+560} 255"
            b += f'<path d="{curve}L{x+560} 310H{x+55}Z" fill="#7656a8" fill-opacity=".17"/>'
            b += f'<path d="{curve}" fill="none" stroke="#7656a8" stroke-width="4"/>'
            b += _text(x + 55, 336, "2025", "label") + _text(
                x + 560, 336, "2100", "label", "end"
            )
            if i:
                b += _text(x + 120, 130, "2035 pulse", "label", "middle")
        b += _text(
            700,
            380,
            "Equivalent pulse = reference mass × (system integrated response ÷ reference integrated response)",
            "label",
            "middle",
        )
        b += _text(
            700,
            412,
            "Match the signed response integral over the same window—not the value at its endpoint.",
            "label",
            "middle",
        )
        b += _text(
            700,
            442,
            "Schematic only · calculated per FaIR configuration, then summarized · forcing and temperature equivalents can differ",
            "note",
            "middle",
        )
    return artwork(
        b,
        {
            "current": "Static inventory without event chronology",
            "trails": "Fuel-specific historical uptake and annual event chronology",
            "fair": "Emissions cause forcing and a delayed temperature response",
            "pulse": "Integrated response equivalence to a dated CO2 pulse",
            "primer": "Inventory flows are characterized to a climate indicator",
        }[stage],
    )


def roadmap():
    stages = (
        ("2025 snapshot", "calendar"),
        ("2035 snapshot", "globe"),
        ("Dated GWP100", "clock"),
        ("Climate response", "response"),
        ("CO₂-pulse equivalent", "pulse"),
    )
    return html.Div(
        [
            html.Div(
                [
                    html.Img(src=icon_uri(kind, "time")),
                    html.Small(f"0{i+1}"),
                    html.Strong(label),
                ],
                className="investigation-stop",
            )
            for i, (label, kind) in enumerate(stages)
        ],
        className="investigation-roadmap",
    )


def quantity_table(flows):
    keys = (
        "Kiln energy",
        "Direct CO₂",
        "Fossil share",
        "Heat exported",
        "CO₂ captured",
        "CO₂ stored",
        "Surplus heat",
        "Fossil CO₂ stored",
        "Non-fossil CO₂ to fuel",
        "Synthetic jet fuel",
    )
    values = {system: {r["label"]: r for r in rows} for system, rows in flows.items()}
    rows = []
    for key in keys:
        entries = [values.get(s, {}).get(key) for s in ("BAU", "CCS", "CCUS")]
        unit = next((e["unit"] for e in entries if e), "")
        rows.append(
            [
                "Fossil CO₂" if key == "Fossil share" else key,
                unit,
                *[
                    (
                        (
                            f"{e['value']:,.0f}"
                            if e["unit"].startswith("kg")
                            else f"{e['value']:.2f}"
                        )
                        if e
                        else "—"
                    )
                    for e in entries
                ],
            ]
        )
    utilities = read_json(EVIDENCE["utilities"])
    utility_rows = [
        (
            label,
            *[
                f"{utilities['systems'][system][key]:,.1f}"
                for system in ("BAU", "CCS", "CCUS")
            ],
        )
        for label, key in (
            ("All direct operations", "direct_electricity_kwh"),
            ("Capture", "capture_electricity_kwh"),
            ("H₂ production + compression", "hydrogen_stage_electricity_kwh"),
            ("Storage chain", "storage_electricity_kwh"),
        )
    ]
    return html.Div(
        [
            html.Div(
                [
                    table(
                        ("2025 quantity / t clinker", "Unit", "BAU", "CCS", "CCUS"),
                        rows,
                    ),
                    html.Div(
                        [
                            html.H2("Operating electricity"),
                            table(
                                ("kWh / t clinker", "BAU", "CCS", "CCUS"), utility_rows
                            ),
                            html.P(
                                "The listed stages are part of the total. Electricity used by suppliers is excluded. Hydrogen production is included within the process model.",
                                className="evidence-note",
                            ),
                            link("Source and quantities included", "utilities"),
                        ],
                        className="utility-evidence",
                    ),
                ],
                className="quantity-columns",
            ),
            html.P(
                [
                    "— = not reported, not zero. Full-system quantities include calcination and capture-boiler carbon, which are outside the fuel-carbon diagrams on slides 4–6. ",
                    link("Source quantities", "quantities"),
                ],
                className="evidence-note",
            ),
        ],
        className="evidence-layout",
    )


def assumptions():
    contract = read_json(EVIDENCE["contract"])
    hp = read_json(EVIDENCE["heat-pump"])
    jet = read_json(EVIDENCE["jet-yield"])
    from .temporal_story import candidate_profiles
    fuels = candidate_profiles()
    uptake = html.Div([
        html.Div([html.Strong(f['fuel'] + ': '),
                  '15-year growth + 1-year delay' if f['column'] in (57, 60) else
                  f"{abs(min(f['offsets']))}-year historical window" ])
        for f in fuels
    ], className="uptake-assumption-list")
    rows = [
        (
            "Capture / storage",
            "Capture of fossil and non-fossil CO₂. Permanent storage in the North Sea.",
            link("Model assumptions", "contract"),
            "Central assumption",
        ),
        (
            "Heat supply and credits",
            html.Div([
                html.Div("Capture: recovered kiln heat plus the boiler supply."),
                html.Div("Fuel conversion: separate natural-gas boiler."),
                html.Div(f"Export credit: gas boiler in 2025, industrial heat pump in future cases (COP {hp['coefficient_of_performance']})."),
            ]),
            link("Heat-pump assumption", "heat-pump"),
            "Heat used internally is not also credited as an export.",
        ),
        (
            "Hydrogen",
            "PEM: 55 kWh/kg H₂ in 2025 → 50 in 2050",
            link("Annual plant inputs", "contract"),
            "Interpolated between years. Held constant after 2050.",
        ),
        (
            "Methanol-to-X",
            f"{jet['carbon_yield_to_jet_fraction']:.0%} of methanol carbon to jet, plus diesel and naphtha. Substitution, no allocation.",
            link("Yield sources", "jet-yield"),
            "Webinar assumption, not a measured plant yield",
        ),
        (
            "Fuel credit / use",
            "Avoided fossil production and combustion credited when fuel is produced. Synthetic fuel burns a year later.",
            link("Timing assumptions", "contract"),
            "Substitution",
        ),
        (
            "Historical uptake",
            uptake,
            link("Revised profiles and sources", "uptake-revised"),
            "Assumed historical profiles, not measured fuel histories. No credit for future regrowth.",
        ),
        (
            "Uncertainty",
            "FaIR climate-model ensemble only",
            link("Scope", "contract"),
            "Does not cover LCI or scenario uncertainty",
        ),
    ]
    return table(("Assumption", "Value / schedule", "Evidence", "Interpretation"), rows)


def lifetime_calendar():
    data = read_json(EVIDENCE["lifetimes"])
    b = ""
    x = lambda y: 420 + (y - 2035) / 30 * 920
    for year in (2035, 2040, 2045, 2050, 2055, 2060, 2065):
        b += (
            _text(x(year), 32, year, "label", "middle")
            + f'<path d="M{x(year)} 48V338" stroke="#d4e0e5"/>'
        )
    for i, row in enumerate(data["components"]):
        y = 70 + i * 40
        name = row["component"]
        status = (
            " (equipment burden excluded)"
            if row["column"] == 68
            else " (existing site)" if row["column"] == 100 else ""
        )
        b += _text(16, y + 5, name + status, "label")
        if row["column"] == 100:
            b += _text(440, y + 5, "Existing site: no new drilling scheduled", "note")
        years = (
            []
            if row["column"] == 100
            else list(range(row["first_year"], 2065, row["lifetime_years"]))
        )
        for year in years:
            b += f'<circle cx="{x(year)}" cy="{y}" r="7" fill="{"white" if row["column"]==68 else "#008a82"}" stroke="#008a82" stroke-width="2"/>'
    b += _text(
        18,
        384,
        "● Quantified construction / replacement     ○ Schedule assumption; equipment quantities are not included",
        "label",
    )
    b += _text(
        18,
        417,
        "Not included: separate capture and fuel-conversion plant construction, and heat-pump equipment.",
        "label",
    )
    return html.Div(
        [
            artwork(b, "Actual component-specific replacement calendar"),
            link("Lifetimes, sources and excluded equipment", "lifetimes"),
        ],
        className="evidence-layout",
    )


def market_figure(bundle, other=False):
    rows = bundle.tables.get("background_evolution", ())
    if not rows:
        path = ROOT / "data/processed/scenario_sector_mixes.csv"
        rows = tuple(csv.DictReader(path.open())) if path.is_file() else ()
    sectors = sorted({r["sector"] for r in rows})
    selected = (
        [s for s in sectors if s not in ("Electricity", "District heat")]
        if other
        else [s for s in ("Electricity", "District heat") if s in sectors]
    )
    selected = selected[:4] if other else selected
    if not selected:
        return html.Div(
            [
                html.H2("No sector trajectories in the loaded bundle"),
                html.P(
                    "premise can update several sectors. That does not mean their environmental impacts all decrease."
                ),
            ],
            className="evidence-empty",
        )
    pathways = ("SSP2-NPi", "SSP2-PkBudg1000")
    colors = [
        "#397b9e",
        "#4d9564",
        "#d59324",
        "#7656a8",
        "#63acc5",
        "#c44e52",
        "#8d9ba1",
        "#2f8f83",
        "#9a7b62",
    ]
    categories = sorted({r["category"] for r in rows if r["sector"] in selected})
    palette = {c: colors[i % len(colors)] for i, c in enumerate(categories)}
    palette.update(
        {
            "Biomass": "#4d9564",
            "Coal and oil": "#806450",
            "Hydro": "#63acc5",
            "Natural gas": "#b79a68",
            "Nuclear": "#a7aab8",
            "Other": "#adb9be",
            "Solar": "#e3b34f",
            "Wind": "#397b9e",
            "Coal": "#62676b",
            "Electric": "#7656a8",
            "Hydrogen": "#cf81a4",
            "Oil": "#b86e4e",
            "Recovered heat": "#2f8f83",
            "CCS": "#397b9e",
            "Conventional": "#a7aab8",
        }
    )
    fig = make_subplots(
        rows=len(selected),
        cols=2,
        shared_xaxes=True,
        shared_yaxes=True,
        vertical_spacing=0.20 if len(selected) > 1 else 0.1,
        horizontal_spacing=0.09,
        subplot_titles=[f"{s} · {p}" for s in selected for p in pathways],
    )
    seen = set()
    for i, sector in enumerate(selected, 1):
        for j, pathway in enumerate(pathways, 1):
            part = [
                r for r in rows if r["sector"] == sector and r["pathway"] == pathway
            ]
            years = sorted({int(r["year"]) for r in part})
            for cat in sorted({r["category"] for r in part}):
                values = {
                    int(r["year"]): float(r["share"]) * 100
                    for r in part
                    if r["category"] == cat
                }
                fig.add_trace(
                    go.Scatter(
                        x=years,
                        y=[values.get(y, 0) for y in years],
                        name=cat,
                        legendgroup=cat,
                        showlegend=j == 1,
                        legend="legend" if i == 1 else f"legend{i}",
                        mode="lines",
                        stackgroup=f"{i}-{j}",
                        line={"color": palette[cat], "width": 1},
                        hovertemplate="%{x}: %{y:.1f}%<extra>%{fullData.name}</extra>",
                    ),
                    row=i,
                    col=j,
                )
                seen.add(cat)
            fig.add_vline(x=2035, line_dash="dot", line_color="#182e3a", row=i, col=j)
        axis = "yaxis" if i == 1 else f"yaxis{2*i-1}"
        fig.update_layout(**{("legend" if i == 1 else f"legend{i}"): dict(
            orientation="h", x=0, y=fig.layout[axis].domain[0]-.035,
            yanchor="top", font=dict(size=11), tracegroupgap=0)})
    fig.update_yaxes(
        range=[0, 100], ticksuffix="%", tickvals=[0, 50, 100], tickfont={"size": 13},
        title_text="Supply (%)",
    )
    fig.update_xaxes(tickfont={"size": 13}, showgrid=True, gridcolor="#dbe4e8")
    fig.update_layout(
        margin={"l": 52, "r": 18, "t": 44, "b": 85},
        font={"family": "Arial", "size": 13, "color": "#0b3b52"},
        plot_bgcolor="#f3f7f8",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return dcc.Graph(
        figure=fig,
        responsive=True,
        config={"displayModeBar": False},
        className="market-trajectories",
    )


def provenance(bundle):
    manifest = bundle.manifest
    bg = read_json(EVIDENCE["contract"])["background"]
    software = manifest.get("software", {})
    version_rows = []
    for label, key, field, tool in (
        ("Time-explicit calculation", "temporal_diagnostic_manifest", "trails_version", "TRAILS"),
        ("Climate response", "fair_diagnostic_manifest", "fair_version", "FaIR"),
    ):
        recorded = bundle.payloads.get(key, {})
        if recorded.get(field):
            version_rows.append((label, f"{tool} {recorded[field]} · version recorded for this calculation"))
    rows = [
        ("Review status", {"candidate": "Preliminary, awaiting review", "invalidated": "Withdrawn for correction", "stale": "Outdated, needs recalculation"}.get(bundle.status, bundle.status.replace("_", " "))),
        ("Result set", bundle.bundle_id),
        ("Model identifier", html.Abbr((manifest.get("model_hash") or "Not recorded")[:12], title=manifest.get("model_hash") or "Not recorded")),
        (
            "Background",
            f"ecoinvent {bg['ecoinvent_version']} {bg['system_model']} · {bg['iam_model']} · {bg['region']}",
        ),
        ("Method", "IPCC 2021 GWP100 including non-fossil CO₂"),
        (
            "Base result software record",
            (
                json.dumps(software)
                if software
                else "Not recorded in the base manifest. Stage-specific records are shown below when available."
            ),
        ),
        (
            "Scientific review",
            str(
                manifest.get("review", {}).get("reviewer") or "No reviewer recorded"
            ),
        ),
        *version_rows,
    ]
    return html.Div(
        [
            table(("Record", "Data used"), rows),
            link("Model and method scope", "contract"),
        ],
        className="evidence-layout",
    )


def availability(bundle):
    rows = bundle.tables.get("sensitivity_availability", ())
    usable = [
        r
        for r in rows
        if str(r.get("available", "false")).lower() in ("1", "true", "yes")
    ]
    heat = (
        "ENC market",
        "biomass CHP",
        "wind heat pump",
        "coal CHP",
        "natural gas CHP",
    )
    power = ("ENC market", "wind", "photovoltaic", "natural gas", "coal")
    counts = lambda h, e: sum(
        r.get("avoided_heat") == h and r.get("operating_electricity") == e
        for r in usable
    )
    return html.Div(
        [
            html.Strong(f"{len(usable)} / 150 combinations available" if usable else "Dynamic sensitivity results are not yet available"),
            table(
                ("Heat ↓ / electricity →", *power),
                [(h, *[f"{counts(h,e)}/6" for e in power]) for h in heat],
                "availability-table",
            ),
            html.Small(
                "Each cell counts available non-fossil fuel shares. No climate values are inferred for missing combinations."
            ),
        ],
        className="availability-map",
    )
