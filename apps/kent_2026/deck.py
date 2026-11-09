from __future__ import annotations

import os
import math

from dash import dcc, html
from apps.seoul_2026.bio import introduction as presenter_introduction

from . import results
from .figures import (
    annual_stage_figure,
    cumulative_figure,
    decision_matrix_figure,
    decision_slices_figure,
    heatmap_figure,
    indicator_conflict_figure,
    option_figure,
    fuel_replacement_figure,
    mobility_electricity_figure,
    scenario_bars,
    passenger_modes_figure,
)

TITLE = "Keep It or Replace It? Car Replacement Decisions in a Changing Energy System"
UPLOAD_NAME = "Kent_Seminar_Keep_or_Replace_Romain_Sacchi"

SLIDES = [
    dict(title=TITLE, phase="Kent Seminar · 12 November 2026", seconds=75, cue="Frame the talk as a mobility-service question, not an argument for one drivetrain.", notes="Open with the title. The aim is not to prescribe one universal replacement date. It is to show why a defensible answer depends on the vehicle, the service required, the energy system, and the indicator."),
    dict(title="Romain Sacchi", phase="About me", seconds=60, cue="Briefly introduce your PSI role, research interests and the open-source tools that lead into this presentation.", notes="Scientist in the Technology Assessment Group, Laboratory for Energy Systems Analysis, Paul Scherrer Institut. Locate PSI near Villigen on the Switzerland map. Briefly connect industrial ecology, future energy and mobility systems, time-explicit LCA and open science to the car-replacement examples that follow. Mention premise, TRAILS, carculator and EDGES as open-source projects, then transition to mobility LCA."),
    dict(title="Beyond the lifetime score: when do mobility impacts occur?", phase="Functional unit · system boundary · life-cycle stages", seconds=110, cue="Start from the mobility service, then follow the vehicle, energy and infrastructure needed to provide it.", notes="The functional unit is one vehicle-kilometre. Passenger-car LCA normally covers vehicle and battery production, fuel or electricity supply, driving emissions, maintenance, road wear and end-of-life. A conventional lifetime result is useful, but collapsing those stages into one accounting year removes the chronology: it cannot distinguish a production pulse today from operation under future energy systems."),
    dict(title="carculator turns vehicle choices into transparent inventories", phase="Open source · parameterized vehicles · calendar-year impacts", seconds=120, cue="Introduce carculator as the engine behind the examples: specifications, inventories, prospective backgrounds, impact assessment and annual event timing.", notes="The current local checkouts identify carculator 1.9.7 and premise 2.6.0. The initial release was in 2022. The broader carculator suite covers passenger cars, two-wheelers, buses and trucks. carculator derives component masses, energy consumption and direct emissions; links vehicle, fuel, electricity, maintenance and end-of-life inventories; and connects emission factors to IAM-backed prospective LCA databases generated with premise. It calculates midpoint indicators and can distribute exposed life-cycle exchanges over calendar years. The deck uses precomputed results rather than calculating in the browser."),
    dict(title="Inside carculator: from the road to the inventory", phase="Driving cycle · vehicle physics · electricity supply · impact assessment", seconds=120, cue="Follow the four panels: road demand becomes wheel demand, then tank or battery demand, then a linked inventory and midpoint results.", notes="The driving cycle supplies second-by-second speed and acceleration. Longitudinal physics resolves inertia, rolling resistance, aerodynamic drag and road gradient before powertrain losses. Energy supply can vary by region, year and scenario. For the displayed BEV, the GECO US charging mix is interpolated and re-solved for every operating calendar year rather than freezing the 2025 mix for the vehicle lifetime. Those flows are linked to vehicle, battery, fuel, electricity, maintenance and end-of-life inventories, then characterized across EF 3.1 midpoint indicators. The lower-right chart is the actual EF 3.1 climate-change profile for the displayed 2025 US medium BEV. Components are produced in 2023, assembly occurs in 2024, and first use begins in 2025. Stacked annual impacts use the left axis in t CO2-eq/year, the cumulative curve uses the right axis in t CO2-eq and reaches 37.3 t at end-of-life in 2042, and the operational inset makes the smaller maintenance contributions visible."),
    dict(title="Technology comparisons change with vehicle family and energy supply", phase="2025 United States · EF 3.1 climate change", seconds=150, cue="Read the four family cards first, then use the lower panels to separate the effects of electricity carbon intensity and occupancy.", notes="The top row compares representative 2025 two-wheelers, passenger cars, city buses and 40-tonne trucks. Passenger modes are normalized per passenger-kilometre; trucks are per tonne-kilometre. FCEVs in the top row use natural-gas SMR hydrogen, while the lower-left sensitivity explicitly uses electrolytic hydrogen. The sensitivity varies a custom wind-to-coal electricity supply and marks the 2025 US lifetime-average charging mix. The lower-right panel puts motorcycle, passenger-car and city-bus options on a common passenger-kilometre basis; occupancy is therefore part of the result. Bus HVAC uses a representative 15 degree Celsius ambient temperature."),
    dict(title="Now narrow the question: keep the car or replace it?", phase="One owner · one mobility service · two futures", seconds=120, cue="Use the 2026 fork to move from broad technology comparisons to the owner-level counterfactual at the heart of the talk.", notes="Once a car already exists, its manufacture is sunk but remains part of the historical owner timeline. The current car is a generic 2020 medium gasoline car and replacement occurs after 2026. The transferred car's later use and end-of-life leave the modeled owner's boundary. Both paths provide 12,000 kilometres per year through 2060, with a common 200,000-kilometre vehicle lifetime and no battery replacement. The comparison is therefore between two complete owner futures, not between two isolated vehicle scores."),
    dict(title="Same service, different calendar-year pulses", phase="Keep above · replace below · EF 3.1 climate change", seconds=120, cue="Read the pathways in parallel: identical mobility service, different vehicle-production schedules and operating profiles.", notes="The upper panel keeps the original gasoline car to its 200,000-kilometre retirement, then introduces BEV successors in 2036 and 2053. The lower panel transfers the original car after 2026 and introduces BEVs in 2027, 2043 and 2060. Both panels include the shared 2018 component-production and 2019 assembly history, provide 12,000 kilometres per year through 2060, and use identical axes. This is calendar assignment of carculator inventory impacts, not atmospheric dynamic LCA."),
    dict(title="When does replacement pay back?", phase="256 precomputed cases · EF 3.1 climate change + particulate matter", seconds=150, cue="Move one assumption at a time, then switch indicators: the crossing and even the preferred pathway can change.", notes="The four sliders select among 256 audited or explicitly interpolated cases. Lifetime and annual mileage affect vehicle turnover. The energy-system choice combines the REMIND background with the corresponding calendar-year GECO charging mix: SSP2-NPi plus Reference, an interpolated midpoint, SSP2-PkBudg1000 plus NDC/LTS, and SSP2-PkBudg650 plus 1.5°C. Petrol, E20, E50 and E85 compare the reference blend with first-generation corn-starch ethanol. The indicator switch contrasts EF 3.1 climate change with particulate matter formation, whose unit is disease incidence. Under the baseline, climate replacement crosses in 2034 and ends 6.7 tonnes CO2-equivalent lower, while particulate-matter impact is higher for replacement by 0.595 × 10⁻³ disease incidences."),
    dict(title="Replacement is robust in some regimes—and conditional in others", phase="Decision frontier · annual driving × charging carbon intensity", seconds=160, cue="Lead with the default 2026 conclusion: at 12,000 kilometres per year, replacement is lower across the tested electricity range; at 5,000 kilometres, the answer crosses from replacement to keeping as charging becomes more carbon intensive.", notes="The matrix reports REPLACE minus KEEP in tonnes CO2-equivalent. Negative values favor replacement, positive values favor keeping, and differences within plus or minus 2 tonnes are labeled close calls. Under the default 2026 decision, 200,000-kilometre lifetime and 2040 evaluation year, the typical 12,000-kilometre case favors replacement by about 12 to 26 tonnes across the tested charging intensities. At 5,000 kilometres per year, very clean electricity supports replacement while carbon-intensive electricity supports keeping. The replacement-year control shows that timing changes the frontier; grey cells mean the current car has already reached its assumed lifetime, so replacement is no longer a discretionary early swap."),
    dict(key="thanks", title="Thank you", phase="Questions + discussion", seconds=120, cue="Close on the conditional answer, leave the decision drivers and contact details visible, and invite questions.", notes="The closing slide reuses the two-column conclusion and contact composition from the Seoul presentation. Recap that dated life-cycle events make the replacement question explicit; vehicle use, lifetime, energy pathways, indicators and evaluation horizons can change the outcome. Do not include project or funding acknowledgements."),
]

BACKUPS = [
    dict(title="Backup · Modeling contract", phase="Owner boundary and sequence logic", seconds=0, cue="Use when questions concern resale, end-of-life, or equal service.", notes="Replacement occurs after the selected year. Later impacts of the transferred original car are excluded. Every new owner vehicle is modeled through its events that occur by 2060. If a mileage threshold is reached partway through a year, the successor supplies the remaining kilometres in the same annual bin; use and maintenance are prorated and foreground end-of-life follows actual final use."),
    dict(title="Backup · EF 3.1 midpoint coverage", phase="All 25 categories calculated", seconds=0, cue="The core selects climate and PM; the complete category list is retained here.", notes="All EF midpoint categories are calculated by the precomputation. Only climate and PM are used in the core narrative."),
    dict(title="Backup · Model years and horizons", phase="Interpolation and endpoint handling", seconds=0, cue="Distinguish vehicle specification interpolation from calendar-year characterization.", notes="Vehicle specifications are interpolated between native years 2020, 2025, 2030, 2040 and 2050. For later cohorts, endpoint-only vehicle and background inputs are held where necessary and documented in the manifest."),
    dict(title="Backup · Reproducibility", phase="Local source checkouts · hashed artifacts", seconds=0, cue="Show commits, dirty-state disclosure and the runtime boundary.", notes="The generator records source commits and dirty flags without modifying either development checkout. The browser reads only the hashed JSON bundle."),
]
ALL_SLIDES = SLIDES + BACKUPS
CORE_COUNT = len(SLIDES)


def graph(figure, identifier=None, animate=False):
    props = dict(figure=figure, config={"displayModeBar": False, "responsive": True}, responsive=True, className="chart", animate=animate)
    if identifier:
        props["id"] = identifier
    if identifier == "interactive-map":
        props["animate"] = True
        props["animation_options"] = {"frame": {"duration": 450}, "transition": {"duration": 350}}
    return dcc.Graph(**props)


def pill(text):
    return html.Span(text, className="pill")


def metric(value, label, detail=""):
    return html.Div([html.Strong(value), html.Span(label), html.Small(detail)], className="metric-card")


def title_block(slide, number):
    del number
    return html.Div(
        [html.Div(slide["phase"], className="slide-eyebrow"), html.H1(slide["title"])],
        className="slide-heading",
    )


def shared_image(filename, alt, class_name=""):
    prefix = os.getenv("KENT_2026_REQUESTS_PREFIX", "/")
    return html.Img(src=prefix + "shared/" + filename, alt=alt, className=class_name)


def asset_image(filename, alt, class_name=""):
    prefix = os.getenv("KENT_2026_REQUESTS_PREFIX", "/")
    return html.Img(src=prefix + "assets/" + filename, alt=alt, className=class_name)


def baseline_case():
    return results.ownership_case()


def kent_thank_you():
    """Kent adaptation of the Seoul two-column conclusion/contact slide."""
    drivers = (
        ("Vehicle", "Age, size, powertrain and the replacement option"),
        ("Service", "Annual distance, lifetime mileage and occupancy"),
        ("Energy", "Calendar-year electricity and fuel pathways"),
        ("Assessment", "Indicator, counterfactual and evaluation horizon"),
    )
    return html.Div([
        html.Div([
            html.Div([
                html.H3("What conditions the answer?"),
                html.Div([
                    html.Div([html.Strong(label), html.Span(detail)])
                    for label, detail in drivers
                ], className="closing-driver-grid"),
            ], className="closing-driver-frame"),
            html.Ul([
                html.Li([html.Strong("Put impacts on a timeline:"), " making a car happens first; driving and maintenance come later."]),
                html.Li([html.Strong("Compare like with like:"), " both choices must provide the same amount of travel over the same years."]),
                html.Li([html.Strong("Change the assumptions:"), " how far you drive, how long cars last, the energy supply and the indicator can change the result."]),
                html.Li([html.Strong("There is no single answer:"), " replacing the car can be better in some cases, while keeping it can be better in others."]),
            ], className="closing-takeaways"),
        ], className="closing-summary"),
        html.Div([
            html.Div([
                html.Span("University of Kent · 12 November 2026", className="small-label"),
                html.H3("Questions and discussion"),
                html.P("Whether replacing a car reduces impacts depends on how much it is driven, what replaces it, and how its energy is produced."),
            ], className="closing-outlook"),
            html.H2("Thank you"),
            html.P("Romain Sacchi", className="closing-name"),
            html.Address([
                html.P("Laboratory for Energy Systems Analysis"),
                html.P("Paul Scherrer Institute (PSI)"),
                html.A("romain.sacchi@psi.ch", href="mailto:romain.sacchi@psi.ch"),
            ]),
        ], className="closing-contact"),
    ], className="closing-layout")


def landscape_summary(lifetime_km=200_000, horizon=2040):
    counts = results.landscape_state(lifetime_km, horizon)["counts"]
    return [
        html.Span([html.B(f'{counts["keep"]:,}'), " clear KEEP"]),
        html.Span([html.B(f'{counts["replace"]:,}'), " clear REPLACE"]),
        html.Span([html.B(f'{counts["ties_hidden"]:,}'), " near ties hidden"]),
        html.Span([html.B(f'{counts["invalid"]:,}'), " invalid excluded"]),
    ]


def landscape_insights(decision_year=2026, lifetime_km=200_000, horizon=2040):
    """Translate the selected decision slice into three audience-facing claims."""
    points = [
        point for point in results.landscape_state(lifetime_km, horizon)["points"]
        if point["decision_year"] == decision_year
    ]
    by_mileage = {
        annual: [point for point in points if point["annual_km"] == annual]
        for annual in (5_000, 8_000, 12_000, 20_000)
    }
    typical = by_mileage[12_000]
    typical_negative = [abs(point["delta_t"]) for point in typical if point["outcome"] == "replace"]
    if len(typical_negative) == len(typical):
        typical_value = f"{min(typical_negative):.0f}–{max(typical_negative):.0f} t lower"
        typical_copy = "REPLACE across every tested charging intensity"
    else:
        typical_value = "Outcome crosses the frontier"
        typical_copy = "electricity and timing affect the typical-use case"

    low = by_mileage[5_000]
    low_replace = [point["intensity"] for point in low if point["outcome"] == "replace"]
    low_keep = [point["intensity"] for point in low if point["outcome"] == "keep"]
    if low_replace and low_keep:
        low_value = "Electricity decides"
        low_copy = f"REPLACE at {max(low_replace)} g; KEEP from {min(low_keep)} g CO₂-eq/kWh"
    elif low_replace:
        low_value = "Robust REPLACE"
        low_copy = "REPLACE is lower across the tested electricity range"
    elif low_keep:
        low_value = "Robust KEEP"
        low_copy = "KEEP is lower across the tested electricity range"
    else:
        low_value = "Close calls"
        low_copy = "all tested electricity cases are close calls"

    cards = (
        ("Typical use · 12,000 km/y", typical_value, typical_copy, "replace"),
        ("Low use · 5,000 km/y", low_value, low_copy, "conditional"),
    )
    insight_cards = [
        html.Div([
            html.Span(label), html.Strong(value), html.P(copy),
        ], className=f"landscape-insight landscape-insight-{tone}")
        for label, value, copy, tone in cards
    ]
    trend_panel = html.Div([
        html.Strong("How the controls move the frontier"),
        html.Ul([
            html.Li([html.B("Replacement year: "), "later swaps generally weaken REPLACE—and may follow natural retirement."]),
            html.Li([html.B("Vehicle lifetime: "), "turnover changes, so the effect is non-linear."]),
            html.Li([html.B("Evaluation year: "), "a longer horizon adds both use savings and new vehicles."]),
        ]),
    ], className="landscape-trend-panel")
    return insight_cards + [trend_panel]


def vehicle_spec_strip():
    vehicles = results.vehicle_specs()["vehicles"]
    return html.Div([
        html.Div([
            html.Strong(vehicle["label"]),
            html.Div([
                html.Span([html.B(f'{vehicle["mass_kg"]:,}'), " kg"]),
                html.Span([html.B(f'{vehicle["ttw_efficiency_pct"]}%'), " TTW η"]),
                html.Span([html.B(f'{vehicle["range_km"]}'), " km range"]),
                html.Span([html.B(f'{vehicle["battery_kwh"]}'), " kWh"] if vehicle["battery_kwh"] else "no traction battery"),
            ], className="vehicle-spec-values"),
        ], className="vehicle-spec-card")
        for vehicle in vehicles
    ], className="vehicle-spec-strip", **{"aria-label": "Selected carculator model outputs for the compared vehicles"})


def mobility_family_card(family):
    candidates = family["candidates"]
    maximum = max(item["total"] for item in candidates)
    ceiling = max(50, math.ceil(maximum / 50) * 50)
    stage_classes = {
        "vehicle production": "stage-vehicle",
        "energy supply": "stage-energy",
        "direct emissions": "stage-direct",
        "maintenance and road": "stage-maintenance",
        "end of life": "stage-eol",
    }
    return html.Article([
        html.Div([
            asset_image(family["icon"], family["label"], "mobility-family-icon"),
            html.Div([
                html.Strong(family["label"]),
                html.Span(family["model"]),
            ], className="mobility-family-title"),
            html.Small(family["unit"], className="mobility-family-unit"),
            html.Span(className="mobility-family-zoom-icon", **{"aria-hidden": "true"}),
        ], className="mobility-family-header"),
        html.Div([
            html.Div([
                html.Span(f"{ceiling:.0f}"),
                html.Span("0"),
            ], className="mobility-stack-axis", **{"aria-hidden": "true"}),
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Strong(f"{candidate['total']:.0f}", className="mobility-stack-value"),
                            html.Div([
                                html.Span(
                                    className=f"mobility-stack-segment {stage_classes[stage]}",
                                    style={"flexGrow": candidate["contributions"][stage]},
                                    title=f"{stage}: {candidate['contributions'][stage]:.1f} {family['unit']}",
                                )
                                for stage in stage_classes
                                if candidate["contributions"][stage] > 0
                            ], className="mobility-stack-bar"),
                        ], className="mobility-stack-wrap", style={"height": f"{100 * candidate['total'] / ceiling:.1f}%"}),
                    ], className="mobility-stack-well"),
                    html.Span(
                        [html.Span("FCEV"), html.Small("(NG)")] if candidate["label"] == "FCEV (NG)" else candidate["label"],
                        className="mobility-stack-label",
                        title=candidate["detail"],
                    ),
                ], className="mobility-stack-candidate")
                for candidate in candidates
            ], className="mobility-stack-plot"),
        ], className="mobility-family-chart", **{"aria-label": f"Stacked life-cycle climate impacts for {family['label']}"}),
    ],
        className=f"mobility-family-card family-{family['key']}",
        role="button",
        tabIndex=0,
        title=f"Enlarge {family['label'].lower()} comparison",
        **{
            "data-family-zoom": family["key"],
            "data-family-title": family["label"],
            "aria-label": f"Enlarge {family['label'].lower()} life-cycle comparison",
        },
    )


def configuration_fingerprint(state="baseline"):
    configuration = results.map_configuration(state)
    items = (
        ("Current", "2020 medium gasoline"),
        ("Successor", configuration["successor"]),
        ("Lifetime", configuration["lifetime"]),
        ("Decision", "map axis · 2020–35"),
        ("Driving", "map axis · 5–20k km/y"),
        ("Future", configuration["future"]),
        ("Horizon", "2060"),
    )
    return [
        html.Div([html.Span(label), html.Strong(value)], className="fingerprint-token")
        for label, value in items
    ]


def sensitivity_ladder(state="baseline"):
    active = {
        "small_bev": "Successor size", "large_bev": "Successor size",
        "short_life": "Vehicle lifetime", "long_life": "Vehicle lifetime",
        "transition": "Energy-system future", "rapid": "Energy-system future",
    }.get(state)
    ranking = results.sensitivity_ranking()
    maximum = max(item["spread_tonnes"] for item in ranking)
    return [
        html.Div([
            html.Div([html.Strong("WHAT MOVES THE SURFACE?"), html.Span("spread in mean Δ · t CO₂-eq")], className="sensitivity-heading"),
            *[
                html.Div([
                    html.Div([html.Strong(item["factor"]), html.Span(item["range"])], className="sensitivity-label"),
                    html.Div(html.Span(style={"width": f'{100 * item["spread_tonnes"] / maximum:.1f}%'}), className="sensitivity-track"),
                    html.B(f'{item["spread_tonnes"]:.1f}'),
                ], className="sensitivity-row active" if item["factor"] == active else "sensitivity-row")
                for item in ranking
            ],
            html.Small("Ranked across the seven shown result surfaces—not a global sensitivity analysis."),
        ], className="sensitivity-card")
    ]


def render_slide(index, print_mode=False, map_state="baseline", indicator="climate change"):
    slide = ALL_SLIDES[index]
    head = title_block(slide, index + 1 if index < CORE_COUNT else index - CORE_COUNT + 1)
    original_index = index - 1 if index >= 2 else index
    if index == 0:
        body = [
            html.Div([
                html.Div("KENT SEMINAR · 12 NOVEMBER 2026", className="cover-kicker"),
                html.H1(TITLE),
                html.P("A calendar-year life-cycle view of passenger-car replacement decisions", className="cover-subtitle"),
            ], className="cover-copy"),
            shared_image("cover-iam-trajectories.svg", "Illustrative energy-system trajectories", "cover-iam-background"),
            html.Div([html.Strong("Romain Sacchi · Paul Scherrer Institute"), html.Span("One mobility service · two vehicle futures")], className="presenter-line"),
        ]
    elif index == 1:
        prefix = os.getenv("KENT_2026_REQUESTS_PREFIX", "/")
        body = presenter_introduction(prefix + "assets/carculator-logo.svg")
    elif slide.get("key") == "thanks":
        body = kent_thank_you()
    elif original_index == 1:
        body = html.Div([
            html.Div([
                html.Div([
                    html.Span("1", className="principle-number"),
                    html.Div([html.Span("FUNCTIONAL UNIT", className="card-kicker"), html.Strong("1 vehicle-km"), html.P("Compare the same mobility service.")]),
                ], className="mobility-principle accent-blue"),
                html.Div([
                    html.Span("2", className="principle-number"),
                    html.Div([html.Span("SYSTEM BOUNDARY", className="card-kicker"), html.Strong("vehicle + energy supply"), html.P("Production · driving · maintenance · end-of-life")]),
                ], className="mobility-principle accent-teal"),
                html.Div([
                    html.Span("3", className="principle-number"),
                    html.Div([html.Span("TIME PROFILE", className="card-kicker"), html.Strong("date each exchange"), html.P("Separate production pulses from recurring use.")]),
                ], className="mobility-principle accent-amber"),
            ], className="mobility-principles"),
            html.Div([
                asset_image("mobility-life-cycle.svg", "Passenger-car mobility life cycle with dated production, operation, maintenance and end-of-life", "mobility-life-cycle-visual"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("TRADITIONAL LCA", className="card-kicker"),
                            html.Strong("Options compared as aggregate scores"),
                            html.Small("illustrative life-cycle contributions"),
                        ], className="result-panel-heading"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span(className="stack-segment stack-production", style={"height": "15%"}),
                                    html.Span(className="stack-segment stack-use", style={"height": "70%"}),
                                    html.Span(className="stack-segment stack-maintenance", style={"height": "9%"}),
                                    html.Span(className="stack-segment stack-eol", style={"height": "6%"}),
                                ], className="stacked-column stack-gasoline"),
                                html.Span("Gasoline"),
                            ], className="traditional-option"),
                            html.Div([
                                html.Div([
                                    html.Span(className="stack-segment stack-production", style={"height": "48%"}),
                                    html.Span(className="stack-segment stack-use", style={"height": "37%"}),
                                    html.Span(className="stack-segment stack-maintenance", style={"height": "10%"}),
                                    html.Span(className="stack-segment stack-eol", style={"height": "5%"}),
                                ], className="stacked-column stack-bev"),
                                html.Span("BEV"),
                            ], className="traditional-option"),
                            html.Div([
                                html.Div([
                                    html.Span(className="stack-segment stack-production", style={"height": "25%"}),
                                    html.Span(className="stack-segment stack-use", style={"height": "58%"}),
                                    html.Span(className="stack-segment stack-maintenance", style={"height": "11%"}),
                                    html.Span(className="stack-segment stack-eol", style={"height": "6%"}),
                                ], className="stacked-column stack-fcev"),
                                html.Span("FCEV"),
                            ], className="traditional-option"),
                        ], className="traditional-bars", **{"aria-label": "Illustrative stacked life-cycle results comparing gasoline, battery-electric and fuel-cell vehicles"}),
                        html.Div([
                            html.Span("production", className="legend-production"),
                            html.Span("use", className="legend-use"),
                            html.Span("maintenance", className="legend-maintenance"),
                            html.Span("end-of-life", className="legend-eol"),
                        ], className="result-stage-legend"),
                        html.Ul([html.Li("Which option has the lower total?")], className="result-questions"),
                    ], className="traditional-result"),
                    html.Div([
                        html.Div([
                            html.Span("TIME-EXPLICIT LCA", className="card-kicker"),
                            html.Strong("One car · impacts by calendar year"),
                        ], className="result-panel-heading"),
                        html.Div([
                            html.Span(className="time-event time-production"),
                            html.Span(className="time-event time-use"),
                            html.Span(className="time-event time-use"),
                            html.Span(className="time-event time-maintenance"),
                            html.Span(className="time-event time-use"),
                            html.Span(className="time-event time-use"),
                            html.Span(className="time-event time-maintenance"),
                            html.Span(className="time-event time-use"),
                            html.Span(className="time-event time-use"),
                            html.Span(className="time-event time-use"),
                            html.Span(className="time-event time-eol"),
                        ], className="time-explicit-profile", **{"aria-label": "Production impact in 2020, recurring use and maintenance impacts, and end-of-life impact in 2037"}),
                        html.Div([html.Span("2020"), html.Span("2037")], className="impact-years"),
                        html.Ul([
                            html.Li("When do the impacts occur?"),
                            html.Li("Which energy system supplies each year?"),
                        ], className="result-questions"),
                    ], className="time-explicit-result"),
                ], className="result-comparison-lens"),
            ], className="life-cycle-visual-row"),
        ], className="mobility-lca-stack")
    elif original_index == 2:
        body = html.Div([
            html.Div([
                html.Span("OPEN-SOURCE VEHICLE LCA MODEL", className="carculator-kicker"),
                asset_image("carculator-logo.svg", "carculator", "carculator-logo"),
                html.P("A transparent engineering model that turns a generic vehicle specification into an auditable, dated life-cycle inventory.", className="carculator-lead"),
                html.Div([
                    html.Span([html.Strong("carculator 1.9.7"), "current checkout"]),
                    html.Span([html.Strong("2022"), "initial release"]),
                    html.Span([html.Strong("4 vehicle families"), "cars · two-wheelers · buses · trucks"]),
                    html.Span([html.Strong("premise 2.6.0"), "IAM-backed backgrounds"]),
                ], className="carculator-meta"),
                html.Div([
                    html.A([
                        html.Span("SOURCE CODE"),
                        html.Strong("GitHub repository ↗"),
                    ], href="https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator", target="_blank", rel="noopener noreferrer", className="carculator-link carculator-link-code"),
                    html.A([
                        html.Span("TRY CARCULATOR"),
                        html.Strong("Open web interface ↗"),
                    ], href="https://carculator.psi.ch", target="_blank", rel="noopener noreferrer", className="carculator-link carculator-link-web"),
                ], className="carculator-links"),
            ], className="carculator-brandline"),
            asset_image("carculator-model-flow.svg", "Vehicle parameters pass through engineering, inventory, characterization and timing layers to auditable outputs", "carculator-model-flow"),
            html.Div([
                html.Div([
                    html.Span("01", className="proof-index"),
                    html.Div([html.Small("PARAMETERIZED SCOPE"), html.Strong("Generic vehicle model, but can be parametrized"), html.Span("size · powertrain · cohort · region · driving cycle")], className="proof-copy"),
                ], className="proof-card"),
                html.Div([
                    html.Span("02", className="proof-index"),
                    html.Div([html.Small("MECHANISTIC CALCULATION"), html.Strong("A physics model, not a static look-up table"), html.Span("mass · road load · energy conversion · losses")], className="proof-copy"),
                ], className="proof-card"),
                html.Div([
                    html.Span("03", className="proof-index"),
                    html.Div([html.Small("INSPECTABLE INPUTS"), html.Strong("Transparency of input parameter values"), html.Span("defaults · user edits · uncertainty · inventory export")], className="proof-copy"),
                ], className="proof-card"),
            ], className="carculator-proof-row"),
        ], className="carculator-overview")
    elif original_index == 3:
        zoom_tiles = (
            "Actual speed trace",
            "Wheel work and mass composition",
            "Energy loop",
            "Year-specific charging mix",
            "Calendar-year climate profile",
        )
        body = html.Div([
            html.Div([
                asset_image("carculator-capabilities.svg", "Driving cycle, road-load physics, powertrain losses, electricity scenarios and dated inventory impacts in carculator", "capability-visual"),
                *([] if print_mode else [
                    html.Div([
                        html.Button(
                            title,
                            type="button",
                            className="capability-zoom-button",
                            title=f"Enlarge {title.lower()}",
                            **{
                                "data-zoom-tile": str(tile),
                                "data-zoom-title": title,
                                "aria-label": f"Enlarge {title.lower()}",
                            },
                        )
                        for tile, title in enumerate(zoom_tiles, start=1)
                    ], className="capability-zoom-hotspots")
                ]),
            ], className="capability-zoom-stage"),
        ], className="capability-layout")
    elif original_index == 4:
        comparison = results.mobility_comparison()
        bev_spec = comparison["electricity_sensitivity"]["bev_specification"]
        body = html.Div([
            html.Div([
                html.Span([html.I(className="legend-swatch stage-vehicle"), "vehicle production"]),
                html.Span([html.I(className="legend-swatch stage-energy"), "energy supply"]),
                html.Span([html.I(className="legend-swatch stage-direct"), "direct emissions"]),
                html.Span([html.I(className="legend-swatch stage-maintenance"), "maintenance + road"]),
                html.Span([html.I(className="legend-swatch stage-eol"), "end-of-life"]),
            ], className="mobility-stage-legend"),
            html.Div([
                *[mobility_family_card(family) for family in comparison["families"]],
            ], className="mobility-family-row"),
            html.Div([
                html.Section([
                    html.Div([
                        html.Div([
                            html.Span("PASSENGER CARS · SAME SIZE", className="analysis-kicker"),
                            html.Strong("Cleaner electricity reshuffles the ranking"),
                        ]),
                        html.Small("gasoline · synthetic gasoline · BEV · electrolytic H₂"),
                    ], className="mobility-analysis-heading"),
                    html.Div([
                        html.Strong("BEV · 2025"),
                        html.Span([html.B(bev_spec["size"]), " size"]),
                        html.Span([html.B(f'{bev_spec["annual_km"]:,} km/y'), f' · {bev_spec["annual_km"] * results.MILES_PER_KM:,.0f} mi/y']),
                        html.Span([html.B(f'{bev_spec["lifetime_km"]:,} km'), f' · {bev_spec["lifetime_km"] * results.MILES_PER_KM:,.0f} mi']),
                        html.Span([html.B(f'{bev_spec["power_kw"]:.0f} kW'), " motor"]),
                        html.Span([html.B(f'{bev_spec["battery_kwh"]:.0f} kWh'), " battery"]),
                        html.Span([html.B(f'{bev_spec["grid_kwh_per_vkm"]:.3f} kWh/vkm'), " grid input"]),
                    ], className="bev-spec-ribbon", **{"aria-label": "Battery-electric vehicle specification"}),
                    graph(mobility_electricity_figure()),
                ], className="mobility-analysis-card electricity-analysis"),
                html.Section([
                    html.Div([
                        html.Div([
                            html.Span("COMMON MOBILITY SERVICE", className="analysis-kicker"),
                            html.Strong("Passenger transport · one passenger-kilometre"),
                        ]),
                        html.Small("default occupancy · 2025 US energy supply"),
                    ], className="mobility-analysis-heading"),
                    graph(passenger_modes_figure()),
                ], className="mobility-analysis-card passenger-analysis"),
            ], className="mobility-analysis-row"),
        ], className="mobility-comparison-layout")
    elif original_index == 5:
        replacement_specs = results.replacement_vehicle_specs()
        body = html.Div([
            asset_image("replacement-counterfactual.svg", "Keep and replace timelines with a shared history, a 2026 decision and equal service through 2060", "replacement-counterfactual"),
            html.Div([
                html.Div([
                    html.Strong("VEHICLE TECHNOLOGY EVOLVES WITH EACH COHORT"),
                    html.Span("Match cohort colors to cars above · 2050 specifications held after 2050"),
                ], className="replacement-specs-heading"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Strong(str(vehicle["year"])),
                            html.Span(vehicle["label"]),
                        ], className="replacement-spec-card-heading"),
                        html.Div([
                            html.Span([html.B(f'{vehicle["power_kw"]} kW'), html.Small("power")]),
                            html.Span([html.B("—" if vehicle["battery_kwh"] is None else f'{vehicle["battery_kwh"]} kWh'), html.Small("battery")]),
                            html.Span([html.B(f'{vehicle["mass_kg"]:,} kg'), html.Small("curb mass")]),
                            html.Span([html.B(f'{vehicle["energy_value"]:.1f}'), html.Small(vehicle["energy_unit"])]),
                        ], className="replacement-spec-metrics"),
                    ], className=f'replacement-spec-card spec-cohort-{index} {"current-spec" if index == 0 else "future-spec"}')
                    for index, vehicle in enumerate(replacement_specs["vehicles"])
                ], className="replacement-spec-grid"),
            ], className="replacement-specs"),
        ], className="decision-contract")
    elif original_index == 6:
        body = graph(annual_stage_figure())
    elif original_index == 7:
        cumulative_result = results.cumulative_sensitivity()
        controls = html.Div([
            html.Div([
                html.Label([html.Span("Total lifetime"), html.Strong("200k km · 124k mi", id="lifetime-readout")]),
                dcc.Slider(id="cumulative-lifetime", min=0, max=3, step=1, value=1,
                           marks={0: "150k", 1: "200k", 2: "250k", 3: "300k km"}),
            ], className="cumulative-control"),
            html.Div([
                html.Label([html.Span("Annual mileage"), html.Strong("12k km/y · 7.5k mi/y", id="mileage-readout")]),
                dcc.Slider(id="cumulative-mileage", min=0, max=3, step=1, value=2,
                           marks={0: "5k", 1: "8k", 2: "12k", 3: "20k km/y"}),
            ], className="cumulative-control"),
            html.Div([
                html.Label([html.Span("Energy-system pathway"), html.Strong("IAM + GECO")]),
                dcc.Slider(id="cumulative-electricity", min=0, max=3, step=1, value=0,
                           marks={0: "NPi", 1: "Mid", 2: "Pk1000", 3: "Pk650"}),
            ], className="cumulative-control"),
            html.Div([
                html.Label([html.Span("Gasoline blend"), html.Strong("corn ethanol")]),
                dcc.Slider(id="cumulative-fuel", min=0, max=3, step=1, value=0,
                           marks={0: "Petrol", 1: "E20", 2: "E50", 3: "E85"}),
            ], className="cumulative-control"),
        ], className="cumulative-controls")
        body = html.Div([
            *([] if print_mode else [controls]),
            html.Div([
                graph(cumulative_figure(sensitivity=cumulative_result), None if print_mode else "cumulative-interactive"),
                *([] if print_mode else [html.Div([
                    html.Span("EF 3.1 indicator"),
                    dcc.RadioItems(
                        id="cumulative-indicator",
                        options=[
                            {"label": "Climate change", "value": "climate change"},
                            {"label": "Fine particles", "value": "particulate matter formation"},
                        ],
                        value="climate change",
                        inline=True,
                    ),
                ], className="cumulative-indicator-switch")]),
            ], className="cumulative-chart-wrap"),
            html.Div([
                html.Div([html.Strong(str(cumulative_result["break_even_year"])), html.Span("sustained break-even")]),
                html.Div([html.Strong(f'{abs(cumulative_result["delta_2060_t"]):.1f} t CO₂-eq'), html.Span("replacement advantage in 2060")]),
                html.Div([html.Strong("SSP2-NPi + Reference · petrol"), html.Span("IAM background + calendar-year GECO charging mix")]),
            ], className="cumulative-summary", **({} if print_mode else {"id": "cumulative-summary"})),
        ], className="cumulative-layout")
    elif original_index == 8:
        landscape_year = 2026
        landscape_lifetime = 200_000
        landscape_horizon = 2040
        if print_mode:
            toolbar = html.Div([
                html.Div([html.Span("Replacement after"), html.Strong("2026")]),
                html.Div([html.Span("Vehicle lifetime"), html.Strong("200,000 km")]),
                html.Div([html.Span("Evaluation year"), html.Strong("2040")]),
            ], className="landscape-context landscape-context-static")
        else:
            toolbar = html.Div([
                html.Div([
                    html.Span("Replacement year", className="landscape-control-label"),
                    dcc.Slider(
                        id="landscape-year", min=0, max=3, step=1, value=1,
                        marks={0: "2020", 1: "2026", 2: "2030", 3: "2035"},
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ], className="landscape-year-control"),
                html.Div([
                    html.Div([
                        html.Span("Lifetime"),
                        dcc.RadioItems(
                            id="landscape-lifetime",
                            options=[
                                {"label": "150k", "value": 150_000}, {"label": "200k", "value": 200_000},
                                {"label": "250k", "value": 250_000}, {"label": "300k km", "value": 300_000},
                            ], value=landscape_lifetime, inline=True,
                        ),
                    ], className="landscape-selector"),
                    html.Div([
                        html.Span("Through"),
                        dcc.RadioItems(
                            id="landscape-horizon",
                            options=[{"label": str(year), "value": year} for year in (2035, 2040, 2050, 2060)],
                            value=landscape_horizon, inline=True,
                        ),
                    ], className="landscape-selector"),
                ], className="landscape-secondary-controls"),
            ], className="landscape-controls")
        body = html.Div([
            toolbar,
            html.Div([
                graph(
                    decision_matrix_figure(landscape_year, landscape_lifetime, landscape_horizon),
                    None if print_mode else "decision-landscape",
                ),
                html.Div(
                    landscape_insights(landscape_year, landscape_lifetime, landscape_horizon),
                    className="landscape-insights",
                    **({} if print_mode else {"id": "landscape-insights"}),
                ),
            ], className="landscape-main"),
            html.Div([
                html.Span("Teal: REPLACE lower · amber: KEEP lower · white: close call · grey: current car already retired"),
                html.Span("Charging stress test scales annual GECO BEV use impacts; non-use impacts unchanged"),
            ], className="landscape-footnote"),
        ], className="decision-landscape-layout")
    elif original_index == 9:
        if print_mode:
            body = html.Div([
                html.Div(configuration_fingerprint("baseline"), className="configuration-fingerprint"),
                html.Div([
                    graph(heatmap_figure("baseline")),
                    html.Div(sensitivity_ladder("baseline"), className="sensitivity-ladder"),
                ], className="interactive-main"),
                html.P("Curated PDF state: medium BEV · 200,000 km life · SSP2-NPi + reference electricity.", className="source"),
            ], className="interactive-panel")
        else:
            body = html.Div([
                html.Div([
                    dcc.RadioItems(id="map-state", options=[
                        {"label": "Baseline", "value": "baseline"}, {"label": "Small BEV", "value": "small_bev"}, {"label": "Large/SUV BEV", "value": "large_bev"},
                        {"label": "150k km life", "value": "short_life"}, {"label": "250k km life", "value": "long_life"}, {"label": "Transition", "value": "transition"}, {"label": "Rapid transition", "value": "rapid"},
                    ], value=map_state, inline=True, className="state-picker"),
                    html.Div(configuration_fingerprint(map_state), id="config-fingerprint", className="configuration-fingerprint"),
                ], className="interactive-toolbar"),
                html.Div([
                    graph(heatmap_figure(map_state), "interactive-map"),
                    html.Div(sensitivity_ladder(map_state), id="sensitivity-ladder", className="sensitivity-ladder"),
                ], className="interactive-main"),
                html.P("Animated transition between precomputed, auditable result surfaces.", className="source"),
            ], className="interactive-panel")
    elif original_index == 10:
        body = html.Div([graph(indicator_conflict_figure()), html.P("2026 decision · medium BEV successor. Signs are comparable; magnitudes are not. Each bar keeps its own EF 3.1 midpoint unit.", className="source")], className="chart-panel")
    elif original_index == 11:
        body = html.Div([graph(fuel_replacement_figure()), html.P("2026 decision · 12,000 km/y. Synthetic petrol: methanol route with electrolytic H₂ and cement-plant CO₂, energy allocation.", className="source")], className="chart-panel")
    elif original_index == 12:
        body = html.Div([graph(scenario_bars()), html.P("Left: presentation pairings, not formal scenario-equivalence mappings. Right: SSP2-NPi fixed; electricity trajectory changed independently.", className="source")], className="chart-panel")
    elif original_index == 13:
        body = html.Div([
            asset_image("temporal-boundary.svg", "Modeled calendar-year inventory timing contrasted with dynamic climate response and recursive supplier timing that are not claimed", "temporal-boundary-visual"),
            html.Div([html.Strong("Credibility rule"), html.Span("Date what the inventory exposes; do not claim temporal resolution the model does not contain.")], className="credibility-rule"),
        ], className="boundary-visual-layout")
    elif original_index == 14:
        body = html.Div([
            asset_image("decision-dependencies.svg", "Four connected dependencies around the keep-or-replace decision boundary", "decision-dependencies-visual"),
            html.Div([html.Strong("It depends."), html.Span("But the dependency can be made explicit, calculated and audited."), html.A("romain.sacchi@psi.ch", href="mailto:romain.sacchi@psi.ch")], className="closing-line"),
        ], className="closing-visual-layout")
    elif index == CORE_COUNT:
        body = html.Div([html.Div([html.H3("Keep path"), html.Ol([html.Li("Include original events through natural retirement"), html.Li("Fill any final-year mileage remainder with the successor"), html.Li("Repeat until 2060")])], className="method-card"), html.Div([html.H3("Replace path"), html.Ol([html.Li("Include original events only through decision year"), html.Li("Exclude transferred-car later burdens"), html.Li("Add and repeat successors for exactly the same annual service")])], className="method-card")], className="scope-grid")
    elif index == CORE_COUNT + 1:
        categories = results.ef_categories()
        body = html.Div([html.Div([html.Strong(item["category"]), html.Span(item["unit"])], className="category-row") for item in categories], className="category-grid")
    elif index == CORE_COUNT + 2:
        body = html.Div([metric("7", "direct cohort anchors", "2020 · 2025 · 2030 · 2035 · 2040 · 2050 · 2060"), metric("annual", "event resolution", "whole calendar years"), metric("2050", "vehicle/background endpoint", "held where source tables end"), metric("2070", "electricity data horizon", "endpoint held afterward"), html.Div("Vehicle inputs are interpolated to each anchor; between anchors, characterized stage profiles are interpolated by lifecycle-event age. This does not create manufacturer-specific cars.", className="boundary-note")], className="metric-grid")
    else:
        manifest = results.manifest()
        body = html.Div([metric(manifest["carculator"]["commit"][:8], "carculator commit", "dirty checkout disclosed" if manifest["carculator"]["dirty"] else "clean checkout"), metric(manifest["carculator_utils"]["commit"][:8], "carculator_utils commit", "dirty checkout disclosed" if manifest["carculator_utils"]["dirty"] else "clean checkout"), metric(manifest["results_sha256"][:12], "result SHA-256", "full hash in manifest"), metric("JSON only", "browser runtime", "no live LCA calculation"), html.Div("Rebuild command and assumptions are documented in apps/kent_2026/README.md.", className="boundary-note")], className="metric-grid")

    number = index + 1 if index < CORE_COUNT else index - CORE_COUNT + 1
    number_label = f"{number:02d} / {CORE_COUNT:02d}" if index < CORE_COUNT else f"B{number:02d}"
    classes = ["slide", "presentation-slide", "kent-slide", f"kent-slide-{index + 1}"]
    if index == 0:
        classes.append("cover-slide")
        children = body + [html.Span(number_label, className="slide-number")]
    elif slide.get("key") == "thanks":
        classes.append("closing-slide")
        children = [body, html.Span(number_label, className="slide-number")]
    else:
        children = [head, html.Div(body, className="slide-body"), html.Span(number_label, className="slide-number")]
    return html.Section(children, className=" ".join(classes), id=f"slide-{index}", **{"aria-label": slide["title"]})
