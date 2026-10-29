"""Shared visual identity for the same four cases throughout the lecture."""

from __future__ import annotations

from html import escape
from urllib.parse import quote

from dash import html
from apps.ccus_webinar.webinar.cover import ICONS
from .carbon import ORIGINS, FOSSIL, NON_FOSSIL

CASES = ("DACCS", "BECCS", "ERW", "Cement + CCS")
CASE = {
    "DACCS": dict(
        colour="#3292b5",
        origin="Atmospheric carbon",
        service="1 t CO₂ physically stored",
        reference="No DAC plant",
        action="Capture air; store CO₂",
        clock="Energy now, capture during operation",
    ),
    "BECCS": dict(
        colour="#3e7654",
        origin="Carbon in biomass",
        service="1 t CO₂ physically stored",
        reference="Standing forest + market energy",
        action="Grow biomass; capture; store",
        clock="Harvest now, regrowth over decades",
    ),
    "ERW": dict(
        colour="#c18a1b",
        origin="Atmospheric carbon",
        service="1.25 t rock deployed",
        reference="No additional rock deployment",
        action="Dissolve rock; build alkalinity",
        clock="Grinding now, uptake after spreading",
    ),
    "Cement + CCS": dict(
        colour="#7656a8",
        origin="Limestone + fuel carbon",
        service="1 t CO₂ stored · CCS − BAU",
        reference="Same clinker without capture",
        action="Capture kiln CO₂; store it",
        clock="Construction first, avoided release during operation",
    ),
}

GLYPHS = dict(ICONS)
GLYPHS.update(
    {
        "people": '<circle cx="32" cy="14" r="8"/><circle cx="12" cy="22" r="6"/><circle cx="52" cy="22" r="6"/><path d="M19 59V41a13 13 0 0 1 26 0v18M3 56V42a9 9 0 0 1 13-8M61 56V42a9 9 0 0 0-13-8M26 59V45m12 14V45"/>',
        "policy": '<circle cx="30" cy="34" r="23"/><circle cx="30" cy="34" r="14"/><circle cx="30" cy="34" r="5" fill="currentColor" fill-opacity=".15"/><path d="M30 34 55 9m-9 1h9v9"/>',
        "investment": '<path d="M7 57h50M12 54V37h9v17m7 0V26h9v28m7 0V14h9v40M10 24 29 14l11 4L55 5m-8 0h8v8"/>',
        "buildings": '<path d="M6 59h52M10 59V24h22v35M32 59V9h22v50M15 30h5m5 0h3M15 39h5m5 0h3M15 48h5m5 0h3M38 18h5m5 0h2M38 28h5m5 0h2M38 38h5m5 0h2M39 59V47h9v12"/>',
        "database": '<ellipse cx="32" cy="12" rx="24" ry="9" fill="currentColor" fill-opacity=".1"/><path d="M8 12v39c0 5 11 10 24 10s24-5 24-10V12M8 25c0 5 11 10 24 10s24-5 24-10M8 38c0 5 11 10 24 10s24-5 24-10"/>',
        "clock": '<circle cx="32" cy="32" r="25"/><path d="M32 13v20l13 8M32 3v5M32 56v5M3 32h5M56 32h5"/>',
        "response": '<path d="M6 8v48h52M9 40q12-29 22-10t27 12"/><path d="M9 40q12-29 22-10t27 12v14H9Z" fill="currentColor" fill-opacity=".12"/>',
    }
)
GLYPHS.update(
    {
        "electric_car": '<path d="M5 43V32l8-4 8-13h23l9 13 6 4v11H5Z" fill="currentColor" fill-opacity=".12"/><path d="M14 28h38M31 16v12"/><circle cx="17" cy="44" r="6" fill="white"/><circle cx="47" cy="44" r="6" fill="white"/><path d="m34 32-6 7h6l-2 7 8-10h-6Z" fill="currentColor" stroke-width="1"/>',
        "battery": '<rect x="12" y="15" width="40" height="38" rx="5" fill="currentColor" fill-opacity=".1"/><path d="M25 9h14v6M22 28h10m-5-5v10M38 28h8M22 42h24"/>',
        "charger": '<rect x="10" y="8" width="28" height="48" rx="5" fill="currentColor" fill-opacity=".1"/><path d="M7 57h35M38 23h7v18a7 7 0 0 0 14 0V22m-5-9v9m7-9v9M51 22h13"/><path d="m26 16-9 15h8l-3 13 12-18h-9Z" fill="currentColor" stroke-width="1"/>',
        "recycling": '<path d="m22 18 9-13 12 19m-1-10 1 10-10-2M48 27l9 15-22 1m9 5-9-5 6-8M29 46H12l10-19m-9 4 9-4 3 10" stroke-width="3"/>',
        "heat": '<path d="M15 54q-10-12 1-24t0-23M33 54q-10-12 1-24t0-23M51 54q-10-12 1-24t0-23"/>',
        "transport": '<path d="M4 17h34v29H4Zm34 10h12l10 12v7H38Z"/><circle cx="16" cy="48" r="7"/><circle cx="48" cy="48" r="7"/>',
    }
)
GLYPHS.update(
    {
        "atmosphere": '<path d="M15 45h32a11 11 0 0 0 2-22 16 16 0 0 0-30-6 14 14 0 0 0-4 28Z" fill="currentColor" fill-opacity=".08"/>',
        "uptake": '<path d="M13 31h36a8 8 0 0 0 0-16 12 12 0 0 0-23-5 11 11 0 0 0-13 21Z" fill="currentColor" fill-opacity=".08"/><path d="M23 35v15m-4-4 4 4 4-4M42 35v15m-4-4 4 4 4-4M4 58q7-6 14 0t14 0t14 0t14 0"/>',
        "forest": '<path d="M12 54h42M22 50V35m22 15V29"/><path d="m22 6-13 19h7L6 40h32L28 25h7Z" fill="currentColor" fill-opacity=".12"/><path d="m44 3-11 18h6l-8 15h27l-9-15h6Z" fill="currentColor" fill-opacity=".16"/>',
        "rock": '<path d="m8 45 5-24 18-11 21 8 8 27-18 10-25-2Z" fill="currentColor" fill-opacity=".15"/><path d="m13 21 22 8 17-11M35 29l7 26M8 45l27-16"/>',
        "ocean": '<path d="M4 20q7-8 14 0t14 0t14 0t14 0M4 37q7-8 14 0t14 0t14 0t14 0M4 54q7-8 14 0t14 0t14 0t14 0"/><path d="M20 2v9m25-9v9" opacity=".5"/>',
        "power": '<path d="M35 3 13 35h17l-3 26 24-36H34Z" fill="currentColor" fill-opacity=".16"/>',
    }
)


def icon_svg(kind, colour, x=0, y=0, size=64):
    if kind == "kiln":
        return f'<g transform="translate({x} {y + size * 0.1}) scale({size / 128})" stroke="{colour}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round">{GLYPHS[kind]}</g>'
    return f'<g transform="translate({x} {y}) scale({size / 64})" stroke="{colour}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round" color="{colour}">{GLYPHS[kind]}</g>'


def svg_uri(body, width=1200, height=420, title="Conceptual system diagram"):
    return "data:image/svg+xml;charset=utf-8," + quote(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title>{body}</svg>'
    )


def label(x, y, value, size=18, colour="#173747", anchor="middle", weight=600):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{colour}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}">{escape(value)}</text>'


def route_uri(case):
    c = CASE[case]["colour"]
    kinds, labels = {
        "DACCS": (("atmosphere", "capture", "storage"), ("Air", "Capture", "Store")),
        "BECCS": (
            ("forest", "capture", "storage"),
            ("Biomass", "Energy + capture", "Store"),
        ),
        "ERW": (
            ("rock", "ocean", "uptake"),
            ("Crush rock", "Dissolve", "Air → ocean"),
        ),
        "Cement + CCS": (
            ("kiln", "capture", "storage"),
            ("Clinker", "Capture", "Store"),
        ),
    }[case]
    b = ""
    for i, (kind, name) in enumerate(zip(kinds, labels)):
        x = 18 + i * 126
        b += f'<rect x="{x}" y="16" width="96" height="100" rx="18" fill="{c}" fill-opacity=".08"/>'
        b += icon_svg(kind, c, x + 16, 26, 64)
        b += label(x + 48, 139, name, 14)
        if i < 2:
            b += f'<path d="M{x + 104} 66h22m-7-6 7 6-7 6" fill="none" stroke="{c}" stroke-width="2.5"/>'
    return svg_uri(b, 390, 158, CASE[case]["action"])


def case_ribbon():
    return html.Div(
        [
            html.Span(
                [html.I(style={"backgroundColor": CASE[c]["colour"]}), c],
                **{"data-case": c},
            )
            for c in CASES
        ],
        className="case-ribbon",
        **{"aria-label": "The four study cases"},
    )


def case_card(case, body=None, detail=None):
    return html.Article(
        [
            html.Div(
                [
                    html.I(style={"backgroundColor": CASE[case]["colour"]}),
                    html.H2(case),
                ],
                className="case-title",
            ),
            html.Img(
                src=route_uri(case), alt=CASE[case]["action"], className="case-route"
            ),
            html.Div(
                body if body is not None else CASE[case]["origin"],
                className="case-main",
            ),
            html.P(
                detail if detail is not None else CASE[case]["clock"],
                className="case-detail",
            ),
        ],
        className="case-card",
        style={"--case-colour": CASE[case]["colour"]},
        **{"data-case": case},
    )


def case_grid(bodies=None, details=None):
    return html.Div(
        [case_card(c, (bodies or {}).get(c), (details or {}).get(c)) for c in CASES],
        className="case-grid",
    )


def supply_network():
    b = '<rect x="380" y="15" width="800" height="380" rx="28" fill="#f0f5f7"/>'
    b += label(770, 57, "One connected background system", 24)
    nodes = [
        (500, 140, "Electricity", "power"),
        (780, 140, "Heat", "heat"),
        (1050, 140, "Materials", "rock"),
        (630, 295, "Transport", "transport"),
        (920, 295, "Equipment", "capture"),
    ]
    for x, y, name, kind in nodes:
        for x2, y2, _, _ in nodes:
            if x < x2:
                b += f'<path d="M{x} {y}L{x2} {y2}" stroke="#c1d3da" stroke-width="2"/>'
    for i, case in enumerate(CASES):
        y = 49 + i * 93
        c = CASE[case]["colour"]
        b += f'<rect x="15" y="{y}" width="270" height="65" rx="14" fill="{c}" fill-opacity=".1" stroke="{c}"/>'
        b += label(150, y + 39, case, 24, c)
        b += f'<path d="M285 {y + 32}C350 {y + 32},350 193,400 193" stroke="{c}" stroke-width="2.4" fill="none"/>'
    for x, y, name, kind in nodes:
        b += f'<circle cx="{x}" cy="{y}" r="46" fill="white" stroke="#bcd0d8"/>'
        b += icon_svg(kind, "#006b8f", x - 24, y - 27, 48)
        b += label(x, y + 72, name, 20)
    return html.Img(
        src=svg_uri(
            b,
            title="The four project foregrounds draw on connected energy, material and equipment suppliers",
        ),
        alt="DACCS, BECCS, ERW and cement CCS linked to a connected background of electricity, heat, materials, transport and equipment.",
        className="full-visual",
    )


def timeline_uri(mode="dated"):
    if mode == "dated":
        return project_clocks_uri()
    b = ""
    xmin, xmax = -5, 110
    left, right = 245, 1170
    xx = lambda age: left + (age - xmin) / (xmax - xmin) * (right - left)
    for tick in (0, 20, 50, 100):
        x = xx(tick)
        b += f'<path d="M{x} 35V388" stroke="#dce4e8" stroke-width="1.4"/>' + label(
            x, 420, f"+{tick} years" if tick else "Start", 17, "#607780"
        )
    for i, c in enumerate(CASES):
        y = 65 + i * 91
        colour = CASE[c]["colour"]
        b += label(18, y + 10, c, 25, colour, "start")
        if mode != "dated":
            x = xx(0)
            b += f'<circle cx="{x}" cy="{y + 2}" r="18" fill="{colour}"/>' + label(
                x + 38, y + 9, "One aggregate score", 19, colour, "start"
            )
            continue
    return svg_uri(
        b,
        1200,
        440,
        "Four project timelines, shown relative to commissioning or spreading",
    )


def project_clocks_uri():
    """Equipment stages and overlapping carbon processes on a relative axis."""
    ink, muted = "#173747", "#607780"
    start, end = 430, 1370

    def xx(age):
        if age <= 30:
            return start + age * 16
        if age < 50:
            return 910 + (age - 30) * 4
        return 990 + (age - 50) * 7.2

    b = '<defs><linearGradient id="weathering-tail"><stop stop-color="#c18a1b" stop-opacity=".3"/><stop offset="1" stop-color="#c18a1b" stop-opacity=".06"/></linearGradient></defs>'
    b += '<rect width="1400" height="550" rx="18" fill="white"/>'
    for age in (0, 10, 20, 30, 50, 100):
        x = xx(age)
        b += f'<path d="M{x} 15V477" stroke="#e4ebef" stroke-width="1.2"/>'

    def bar(x, y, width, text, colour=ink, filled=False, outline=False):
        stroke = ' stroke="#a4b5be" stroke-dasharray="4 3"' if outline else ""
        return (f'<rect x="{x}" y="{y}" width="{width}" height="26" rx="7" fill="{colour if filled else "#e3ebef"}"{stroke}/>'
                + label(x + width / 2, y + 19, text, 20, "white" if filled else ink, weight=500))

    def tail(x, y, text, colour, dashed=False, text_x=1160):
        dash = ' stroke-dasharray="7 5"' if dashed else ""
        return (f'<path d="M{x} {y}H{end}m-10-6 10 6-10 6" stroke="{colour}" stroke-width="3" fill="none"{dash}/>'
                + label(text_x, y - 10, text, 20, colour, weight=500))

    for case, y in zip(CASES, (24, 132, 240, 366)):
        colour = CASE[case]["colour"]
        kind = {"DACCS": "capture", "BECCS": "forest", "ERW": "rock", "Cement + CCS": "kiln"}[case]
        height = 118 if case == "ERW" else 102
        b += f'<g data-case="{escape(case)}">'
        b += f'<rect x="10" y="{y - 10}" width="1380" height="{height}" rx="12" fill="#f4f8fa" fill-opacity=".65"/>'
        b += icon_svg(kind, colour, 25, y + 14, 38)
        b += label(77, y + 42, case, 26, colour, "start")
        duration = 30 if case == "Cement + CCS" else 20
        b += bar(280, y + 8, 136, "Build-up", outline=True)
        upkeep = {"DACCS": "Operate · sorbent", "BECCS": "Operate · upkeep",
                  "ERW": "Grind + spread · annual batches",
                  "Cement + CCS": "Operate · maintain components"}[case]
        b += bar(start, y + 8, xx(duration) - start, upkeep)
        b += bar(xx(duration) + 12, y + 8, 133, "Dismantle", outline=True)
        if case == "ERW":
            b += label(77, y + 69, "20-year supply chain", 19, muted, "start", 400)
            # Each operating batch feeds mineral reaction, then air–sea uptake.
            # Arrow extents are schematic, not a completion date or mass scale.
            for age in (1, 10, 19):
                x = xx(age)
                b += f'<path d="M{x} {y + 35}v12m-4-5 4 5 4-5" stroke="{muted}" stroke-width="1.8" fill="none"/>'
            for x, top, text in ((start, y + 48, "Dissolution + alkalinity transport"),
                                 (start + 24, y + 86, "Atmospheric uptake · delayed")):
                b += f'<path d="M{x} {top}H{end - 18}l18 12-18 12H{x}Z" fill="url(#weathering-tail)" stroke="{colour}" stroke-width="1.2" stroke-opacity=".4"/>'
                b += label(1080, top + 19, text, 21, colour, weight=500)
            for age in (3, 12, 21):
                x = xx(age)
                b += f'<path d="M{x} {y + 73}q0 7 13 12m-6-6 6 6-8 1" stroke="{colour}" stroke-width="1.8" fill="none"/>'
        else:
            action = {"DACCS": "Capture + store", "BECCS": "Harvest + capture", "Cement + CCS": "Capture avoids kiln release"}[case]
            b += bar(start, y + 49, xx(duration) - start, action, colour, True)
            b += tail(xx(duration) + 8, y + 69, "Geological storage", colour)
            if case == "BECCS":
                b += tail(start, y + 96, "Regrowth after each harvest", colour, True, 1090)
        b += '</g>'

    b += f'<path d="M280 485H416" stroke="{muted}" stroke-width="1.5" stroke-dasharray="4 4"/>'
    b += f'<path d="M{start} 485H910M990 485H{end}m-10-6 10 6-10 6" stroke="{muted}" stroke-width="2" fill="none"/>'
    b += '<path d="m943 478-7 14m18-14-7 14" stroke="#607780" stroke-width="2.5"/>'
    b += label(348, 513, "Before", 20, muted, weight=500)
    for age in (0, 10, 20, 30, 50, 100):
        x = xx(age)
        b += f'<path d="M{x} 481v9" stroke="{muted}" stroke-width="1.5"/>'
        b += label(x, 513, "Start" if age == 0 else f"+{age}", 20, muted, weight=500)
    b += label(900, 545, "Years from start · axis break after +30", 19, muted, weight=400)
    return svg_uri(b, 1400, 550, "Build-up before start, twenty- or thirty-year operation, dismantling and overlapping carbon tails")


def timeline(mode="dated"):
    return html.Img(
        src=timeline_uri(mode),
        alt=(
            "Four equipment and carbon clocks share a bottom relative-year axis, with a scale break after year thirty. Build-up precedes start and dismantling follows operation; these equipment stages are schematic and add no unquantified inventory. ERW grinding and spreading operate for twenty years in annual batches, each feeding dissolution and alkalinity transport followed by delayed atmospheric uptake. Connecting arrows show these overlapping stages and open-ended tails rather than a completion date. Geological storage and BECCS regrowth continue beyond operation."
            if mode == "dated"
            else "All four project histories collapse into one aggregate score in static accounting."
        ),
        className="full-visual",
    )


def lens_visual(lens):
    filename = {
        "current": "lens-conventional.svg",
        "prospective": "lens-prospective.svg",
        "dated": "lens-time-explicit.svg",
    }[lens]
    return filename


def _arrow(x1, y1, x2, y2, colour, dashed=False):
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{colour}" stroke-width="2.5" fill="none"{dash}/><path d="m{x2 - 8} {y2 - 5} 8 5-8 5" stroke="{colour}" stroke-width="2.5" fill="none"/>'


def carbon_atlas():
    b = (
        label(488, 24, "CARBON SOURCE", 16, "#607780")
        + label(775, 24, "INTERVENTION", 16, "#607780")
        + label(1080, 24, "DESTINATION", 16, "#607780")
    )
    entries = [
        (
            "atmosphere",
            "Air",
            "capture",
            "Direct air capture",
            "storage",
            "Geological storage",
        ),
        (
            "forest",
            "Biomass",
            "capture",
            "Energy + capture",
            "storage",
            "Geological storage",
        ),
        (
            "atmosphere",
            "Air",
            "uptake",
            "Alkalinity enables uptake",
            "ocean",
            "Dissolved ocean carbon",
        ),
        (
            "kiln",
            "Limestone + fuels",
            "capture",
            "Kiln capture",
            "storage",
            "Geological storage",
        ),
    ]
    supply_and_time = [
        ("Electricity + heat", "Build → capture during operation"),
        ("Biomass + displaced energy", "Harvest → regrowth over decades"),
        ("Grinding electricity + haulage", "Deploy → dissolve → atmospheric uptake"),
        ("Kiln fuels + capture utilities", "Build → capture + avoided release"),
    ]
    for i, (case, entry) in enumerate(zip(CASES, entries)):
        y = 48 + i * 120
        c = CASE[case]["colour"]
        b += f'<rect x="0" y="{y}" width="1200" height="112" rx="14" fill="{c}" fill-opacity=".055"/>'
        b += f'<rect x="0" y="{y}" width="5" height="112" rx="2" fill="{c}"/>'
        b += label(20, y + 31, case, 25, c, "start") + label(
            20, y + 59, CASE[case]["service"], 17, "#173747", "start"
        )
        b += label(
            20, y + 83, "vs " + CASE[case]["reference"], 13, "#607780", "start", 400
        )
        for j in range(3):
            x = [488, 775, 1080][j]
            b += icon_svg(entry[j * 2], c, x - 25, y + 7, 48)
            if case == "Cement + CCS" and j == 0:
                b += label(x, y + 70, "Limestone + fossil fuels", 15, ORIGINS[FOSSIL])
                b += label(x, y + 89, "Non-fossil fuels", 15, ORIGINS[NON_FOSSIL])
            else:
                b += label(x, y + 77, entry[j * 2 + 1], 17, "#173747")
            if j < 2:
                if case == "Cement + CCS":
                    b += _arrow(
                        x + 62,
                        y + 23,
                        [488, 775, 1080][j + 1] - 66,
                        y + 23,
                        ORIGINS[FOSSIL],
                    )
                    b += _arrow(
                        x + 62,
                        y + 39,
                        [488, 775, 1080][j + 1] - 66,
                        y + 39,
                        ORIGINS[NON_FOSSIL],
                        dashed=True,
                    )
                else:
                    b += _arrow(x + 62, y + 30, [488, 775, 1080][j + 1] - 66, y + 30, c)
        supply, timing = supply_and_time[i]
        b += label(
            420, y + 102, "Supply system: " + supply, 14, "#607780", "start", 400
        )
        b += label(790, y + 102, "Timing: " + timing, 14, c, "start", 400)
    return html.Img(
        src=svg_uri(
            b,
            1200,
            534,
            "Four carbon routes linking changing suppliers with dated carbon flows",
        ),
        alt="Four carbon routes: air capture, biomass capture, alkalinity-enabled ocean uptake, and kiln capture. Each has its own service and no-project reference, with the relevant suppliers and carbon timing identified.",
        className="full-visual carbon-atlas",
    )


def balance_ledger():
    entries = [
        (
            "− air uptake",
            "+ energy, materials, losses",
            "Physical removal, after supply-chain burdens",
        ),
        (
            "− regrowth − displaced energy",
            "+ residual release + supply chain",
            "Land and displaced-energy references matter",
        ),
        (
            "− atmospheric uptake",
            "+ grinding, haulage, spreading",
            "Rock deployment creates a potential; uptake takes time",
        ),
        (
            "CCS clinker − BAU clinker",
            "Same clinker service on both sides",
            html.Div(
                [
                    html.Span(
                        "Fossil / mineral: avoided release",
                        style={"color": ORIGINS[FOSSIL]},
                    ),
                    html.Span(
                        "Non-fossil: potential removal",
                        style={"color": ORIGINS[NON_FOSSIL]},
                    ),
                ],
                className="origin-reading",
            ),
        ),
    ]
    return html.Div(
        [
            html.Div(
                [
                    html.Span("INTERVENTION"),
                    html.Span("WHAT ENTERS THE BALANCE?"),
                    html.Span("HOW TO READ IT"),
                ],
                className="ledger-head",
            ),
            *[
                html.Div(
                    [
                        html.Strong(case, style={"color": CASE[case]["colour"]}),
                        html.Div(
                            [
                                html.Span(e[0], className="ledger-credit"),
                                html.Span(e[1], className="ledger-burden"),
                            ]
                        ),
                        html.Div(e[2], className="ledger-reading"),
                    ],
                    className="ledger-row",
                    style={"--case-colour": CASE[case]["colour"]},
                    **{"data-case": case},
                )
                for case, e in zip(CASES, entries)
            ],
            html.Div(
                "Qualitative mechanisms · a negative intervention score does not always mean atmospheric removal",
                className="ledger-footer",
            ),
        ],
        className="balance-ledger",
    )


def discussion_cases(prompts):
    return html.Div(
        [
            html.Div(
                [
                    html.Img(src=route_uri(c), alt=CASE[c]["action"]),
                    html.Strong(c),
                    html.Span(p),
                ],
                style={"--case-colour": CASE[c]["colour"]},
            )
            for c, p in zip(CASES, prompts)
        ],
        className="discussion-cases",
    )


def coastal_scene():
    b = """<defs><linearGradient id="water" x2="0" y2="1"><stop stop-color="#e5f4f5"/><stop offset="1" stop-color="#c7e1e8"/></linearGradient></defs>
    <rect width="1200" height="450" rx="22" fill="#f3f8fa"/>
    <path d="M0 230Q110 155 240 214L380 315L470 450H0Z" fill="#d8c9a8"/>
    <path d="M260 240Q280 225 300 240T340 240T380 240T420 240T460 240T500 240T540 240T580 240T620 240T660 240T700 240T740 240T780 240T820 240T860 240T900 240T940 240T980 240T1020 240T1060 240T1100 240T1140 240T1180 240H1200V450H470L380 315Z" fill="url(#water)"/>
    <path d="M0 236Q110 160 240 219L380 320L470 450" stroke="#bba579" stroke-width="4" fill="none"/>
    <path d="M260 240Q280 225 300 240T340 240T380 240T420 240T460 240T500 240T540 240T580 240T620 240T660 240T700 240T740 240T780 240T820 240T860 240T900 240T940 240T980 240T1020 240T1060 240T1100 240T1140 240T1180 240" stroke="#4999b0" stroke-width="2" fill="none"/>
    """
    b += (
        icon_svg("rock", "#c18a1b", 120, 149, 64)
        + icon_svg("rock", "#c18a1b", 257, 245, 43)
        + icon_svg("rock", "#c18a1b", 301, 277, 30)
    )
    b += icon_svg("atmosphere", "#3292b5", 813, 95, 96)
    b += label(860, 85, "Atmospheric CO₂", 22, "#3292b5")
    for x in (825, 890):
        b += f'<path d="M{x} 186v112m-8-10 8 10 8-10" stroke="#3292b5" stroke-width="3.5" fill="none"/>'
    b += f'<path d="M357 299C490 340 581 330 724 335m-12-9 12 9-12 6" stroke="#c18a1b" stroke-width="4" stroke-dasharray="8 6" fill="none"/>'
    b += label(540, 376, "Alkalinity transport + mixing", 20, "#856011")
    b += label(933, 348, "Dissolved inorganic carbon", 21, "#24617a")
    for x, y in ((330, 330), (353, 350), (377, 370), (400, 392)):
        b += f'<circle cx="{x}" cy="{y}" r="4" fill="#c18a1b" opacity=".5"/>'
    steps = [
        (24, 28, "01", "Deploy + grind", "Energy and transport occur first."),
        (
            400,
            28,
            "02",
            "Dissolve + transport",
            "Mineralogy, grain size and site matter.",
        ),
        (
            788,
            390,
            "03",
            "Air–sea uptake",
            "Chemical change precedes atmospheric uptake.",
        ),
    ]
    # Third caption sits in the water; its process arrow is separate from rock transport.
    for x, y, num, title, detail in steps:
        b += label(x, y + 15, num, 18, "#c18a1b", "start") + label(
            x + 40, y + 15, title, 23, "#173747", "start"
        )
        b += label(x, y + 43, detail, 15, "#607780", "start", 400)
    return html.Img(
        src=svg_uri(
            b,
            1200,
            450,
            "Coastal ERW has separate deployment, dissolution and atmospheric uptake clocks",
        ),
        alt="Conceptual coastal cross-section: rock is deployed, dissolution adds alkalinity that is transported and mixed, and atmospheric carbon enters through air–sea exchange. Separate clocks determine realized uptake.",
        className="full-visual coastal-scene",
    )


def lens_map():
    entries = [
        (
            "01",
            "Current static",
            "What drives the result today?",
            "One present-day production system",
            "Snapshot hotspots",
        ),
        (
            "02",
            "Prospective static",
            "What if the supply system changes?",
            "One conditional future production system",
            "Future burdens + credits",
        ),
        (
            "03",
            "Time-explicit + climate",
            "When does the benefit arrive?",
            "Dated exchanges in changing systems",
            "Trajectory + declared climate metric",
        ),
    ]
    return html.Div(
        [
            html.Div(
                [
                    html.Span("SERVICE + REFERENCE FIRST"),
                    html.Strong("Then choose the question that matters."),
                ],
                className="lens-intro",
            ),
            html.Div(
                [
                    html.Article(
                        [
                            html.Span(n, className="lens-number"),
                            html.H2(name),
                            html.Strong(question),
                            html.Div(scope, className="lens-scope"),
                            html.Div(outcome, className="lens-outcome"),
                        ]
                    )
                    for n, name, question, scope, outcome in entries
                ],
                className="lens-columns",
            ),
            html.Div(
                "Dated GWP100 pulses locate the inventory. Climate responses and fixed-window CO₂-pulse-eq evaluate its timing.",
                className="lens-footer",
            ),
        ],
        className="lens-map",
    )


def pulse_equivalence_map():
    # Schematics deliberately avoid assigning uncalculated pulse-equivalent scores
    # to cases with different native cohort dates and source backgrounds.
    b = ""
    for i, c in enumerate(CASES):
        y = 42 + i * 68
        colour = CASE[c]["colour"]
        b += label(5, y + 8, c, 22, colour, "start")
        b += f'<path d="M202 {y + 15}H385M202 {y - 22}V{y + 27}" stroke="#c4d5dc" fill="none"/>'
        paths = [
            "M205 60Q225 39 245 60T285 70T330 76T381 77",
            "M205 128Q240 100 268 128T317 145T381 151",
            "M205 196Q230 165 247 196T300 216T381 219",
            "M205 264Q224 246 250 264T300 285T381 287",
        ]
        b += f'<path d="{paths[i]}" transform="translate(0 -18)" stroke="{colour}" stroke-width="3" fill="none"/>'
        b += _arrow(403, y, 460, y, colour)
    b += '<rect x="478" y="14" width="290" height="290" rx="20" fill="#eaf4f3"/>'
    b += label(623, 47, "ONE CALENDAR WINDOW", 18, "#008a82")
    b += '<path d="M508 120H737M508 91V207M737 91V207" stroke="#87aaa8" stroke-width="1.6" stroke-dasharray="5 4"/><path d="M508 120Q550 61 580 120T655 168T737 174V120Z" fill="#008a82" fill-opacity=".17"/><path d="M508 120Q550 61 580 120T655 168T737 174" stroke="#008a82" stroke-width="3" fill="none"/>'
    b += label(508, 232, "Start", 17, "#607780") + label(737, 232, "End", 17, "#607780")
    b += label(623, 276, "Signed area = integrated forcing", 16, "#173747")
    b += _arrow(784, 154, 832, 154, "#008a82")
    b += '<rect x="850" y="14" width="340" height="290" rx="20" fill="#f0f4f8"/>'
    b += label(1020, 47, "DATED REFERENCE PULSE", 18, "#3292b5")
    b += '<path d="M880 172H1160M925 172V81m-6 9 6-9 6 9M925 81Q985 117 1060 127T1160 136" stroke="#3292b5" stroke-width="3" fill="none"/>'
    b += label(1020, 211, "What signed mass of CO₂", 21, "#173747") + label(
        1020, 240, "matches that area?", 21, "#173747"
    )
    b += label(1020, 278, "Same background + same window", 16, "#607780")
    b += label(5, 342, "GWP100: 100 years after EACH event", 22, "#a4563f", "start")
    b += label(5, 378, "Pulse-eq: one declared calendar window", 22, "#008a82", "start")

    return html.Img(
        src=svg_uri(
            b,
            1200,
            400,
            "Conceptual fixed-window CO2 pulse equivalence for the four project responses",
        ),
        alt="Concept: integrate each dated project response over one common calendar window and compare it with the signed integrated forcing per kilogram of a CO2 pulse at a declared reference date. Schematics are not calculated four-case equivalent scores.",
        className="full-visual pulse-equivalence-map",
    )


def workflow_map():
    b = label(
        600, 30, "FOUR PROJECTS · ONE REPRODUCIBLE CHAIN OF EVIDENCE", 19, "#607780"
    )
    xs = [108, 354, 600, 846, 1092]
    steps = [
        (
            "01",
            "Define",
            "Your foreground",
            "Service + counterfactual",
            "Evidence + uptake profile",
            "rock",
        ),
        (
            "02",
            "Supply",
            "ecoinvent + IAMs",
            "Linked unit processes",
            "Conditional trajectories",
            "power",
        ),
        (
            "03",
            "Transform",
            "premise",
            "Scenario signals become",
            "future inventory coefficients",
            "capture",
        ),
        (
            "04",
            "Date",
            "TRAILS",
            "Route dated exchanges",
            "through changing suppliers",
            "clock",
        ),
        (
            "05",
            "Assess",
            "FaIR",
            "Forcing + temperature",
            "Window + CO₂-pulse-eq",
            "response",
        ),
    ]
    for i, (num, verb, tool, line1, line2, kind) in enumerate(steps):
        x = xs[i]
        b += f'<circle cx="{x}" cy="118" r="43" fill="#edf5f6" stroke="#c1d7de" stroke-width="1.5"/>'
        b += icon_svg(kind, "#006b8f", x - 25, 91, 50)
        b += label(x, 193, num + " · " + verb, 23, "#173747")
        b += label(x, 224, tool, 22, "#008a82")
        if i == 4:
            b += label(x, 248, "+ declared climate metric", 15, "#607780")
        if i < 4:
            b += _arrow(x + 66, 118, xs[i + 1] - 66, 118, "#91a8b1")
        b += label(x, 365, line1, 17, "#173747") + label(x, 392, line2, 17, "#607780")
    for i, c in enumerate(CASES):
        y = 270 + i * 12
        col = CASE[c]["colour"]
        b += f'<path d="M20 {y}H1180" stroke="{col}" stroke-width="3" opacity=".65"/>'
        for x in xs:
            b += f'<circle cx="{x}" cy="{y}" r="5" fill="{col}"/>'
    b += '<rect x="18" y="435" width="1164" height="49" rx="13" fill="#edf5f2"/>'
    b += label(
        600,
        466,
        "Analyst inputs: service · reference · timing evidence · climate window",
        20,
        "#008a82",
    )
    return html.Img(
        src=svg_uri(
            b,
            1200,
            500,
            "Evidence-to-result workflow and analyst decisions for all four technologies",
        ),
        alt="Five stages: define the foreground and reference; obtain ecoinvent data and IAM scenarios; use premise for future backgrounds; TRAILS for dated inventories; FaIR and a declared climate metric for interpretation. The analyst supplies timing evidence and the assessment window.",
        className="full-visual workflow-map",
    )


def temporal_introduction():
    """Set up three reasons to retain time, before the case studies."""
    b = label(380, 26, "AN ELECTRIC CAR OVER ITS LIFE CYCLE", 17, "#607780")
    b += '<path d="M25 180H745m-9-6 9 6-9 6" stroke="#a5bac4" stroke-width="2" fill="none"/>'
    stages = [
        (122, 205, ("Car + battery", "Production"), "Before driving", "#3292b5", ("electric_car", "battery")),
        (380, 270, ("Charging", "Maintenance"), "Years of driving", "#c18a1b", ("electric_car", "charger")),
        (640, 210, ("Vehicle + battery", "Dismantling + recycling"), "After use", "#7656a8", ("recycling",)),
    ]
    for x, w, name, when, colour, kinds in stages:
        b += f'<rect x="{x - w / 2}" y="48" width="{w}" height="112" rx="12" fill="{colour}" fill-opacity=".1" stroke="{colour}" stroke-width="1.5"/>'
        if len(kinds) == 2:
            b += icon_svg(kinds[0], colour, x - 57, 61, 57)
            b += icon_svg(kinds[1], colour, x + 13, 66, 45)
        else:
            b += icon_svg(kinds[0], colour, x - 29, 60, 58)
        b += label(x, 136, name[0], 20, colour)
        b += label(x, 155, name[1], 16, colour)
        b += f'<path d="M{x} 163v17" stroke="{colour}" stroke-width="2"/>'
        b += label(x, 211, when, 17, "#607780")
    b += '<path d="M770 108H858m-12-9 12 9-12 9" stroke="#008a82" stroke-width="4" fill="none"/>'
    b += label(810, 57, "AGGREGATE", 14, "#008a82")
    b += '<rect x="884" y="40" width="306" height="154" rx="18" fill="#edf5f3" stroke="#b7d5cf"/>'
    b += label(1037, 77, "One life-cycle inventory", 22, "#173747")
    b += label(1037, 108, "→ impact score", 21, "#008a82")
    b += label(1037, 145, "Amounts are retained.", 18, "#607780")
    b += label(1037, 172, "Event dates usually are not.", 18, "#607780")
    return html.Div(
        [
            html.P(
                "An electric car is manufactured, charged and maintained for years, then dismantled and recycled—all can enter one total without event dates.",
                className="temporal-intro-lead",
            ),
            html.Img(
                src=svg_uri(
                    b,
                    1200,
                    228,
                    "An electric car's production, charging, maintenance and recycling aggregated into one life-cycle inventory and impact score",
                ),
                alt="Illustrative electric-car life cycle: car and battery production before driving, charging and maintenance during years of driving, then dismantling and recycling after use. The aggregate inventory retains amounts but usually not their event dates; no vehicle lifetime or impact values are assumed.",
                className="temporal-intro-visual",
            ),
            html.Div(
                [
                    html.Article(
                        [
                            html.Span("01 · LONG-LIVED ACTIVITIES"),
                            html.H2("Suppliers change during operation"),
                            html.P(
                                "The electricity used to charge the same car can change over its years of driving."
                            ),
                            html.Div(
                                "Long-lived plants and replacement equipment face the same issue.",
                                className="temporal-intro-example",
                            ),
                            html.A(
                                "Müller et al. (2025)",
                                href="https://doi.org/10.1007/s11367-025-02539-3",
                                target="_blank",
                                rel="noopener noreferrer",
                            ),
                        ]
                    ),
                    html.Article(
                        [
                            html.Span("02 · CLIMATE EFFECTS"),
                            html.H2(
                                "Climate depends on emission dates"
                            ),
                            html.P(
                                "CO₂ emitted now affects the climate before a later removal occurs. A single total hides that history."
                            ),
                            html.Div(
                                "Relevant to forest regrowth, weathering and delayed CO₂ removal.",
                                className="temporal-intro-example",
                            ),
                            html.A(
                                "Levasseur et al. (2010)",
                                href="https://doi.org/10.1021/es9030003",
                                target="_blank",
                                rel="noopener noreferrer",
                            ),
                        ]
                    ),
                    html.Article(
                        [
                            html.Span("03 · DELAYED IMPACTS"),
                            html.H2("Impacts can arise long after disposal"),
                            html.P(
                                "Landfill leachate can release pollutants centuries later, causing potential human-toxicity impacts."
                            ),
                            html.Div(
                                "A short horizon or a ‘no LT’ method can exclude these effects.",
                                className="temporal-intro-example",
                            ),
                            html.Div(
                                [
                                    html.A(
                                        "Turner et al. (2017)",
                                        href="https://doi.org/10.1016/j.wasman.2016.12.005",
                                        target="_blank",
                                        rel="noopener noreferrer",
                                    ),
                                    " · ",
                                    html.A(
                                        "ecoinvent LT guidance",
                                        href="https://support.ecoinvent.org/lcia-results",
                                        target="_blank",
                                        rel="noopener noreferrer",
                                    ),
                                ],
                                className="temporal-intro-card-references",
                            ),
                        ]
                    ),
                ],
                className="temporal-intro-reasons",
            ),
            html.Div(
                [
                    html.Span("Temporal inventory foundations: "),
                    html.A(
                        "Beloin-Saint-Pierre, Heijungs & Blanc (2014)",
                        href="https://doi.org/10.1007/s11367-014-0710-9",
                        target="_blank",
                        rel="noopener noreferrer",
                    ),
                ],
                className="temporal-intro-reference",
            ),
        ],
        className="temporal-intro",
    )
