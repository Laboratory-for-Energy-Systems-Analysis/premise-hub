"""Slide 3's aligned routes, using the cover's industrial icon family.

Carbon origins are visual categories, not proportional flows or new inventory
values. Keep this overview separate from the quantified detailed diagrams.
"""

from urllib.parse import quote

from dash import html

from .cover import ICONS
from .diagrams import COLORS, _arrow, _svg, _text

ORIGINS = (
    ("mineral", "#967052", "Limestone calcination · fossil CO₂"),
    ("fossil", COLORS["fossil"], "Fossil fuel · fossil CO₂"),
    ("non-fossil", COLORS["bio"], "Non-fossil fuel · non-fossil CO₂"),
)

SUPPLY_ICONS = {
    "quarry": (
        '<path d="M3 54h58M4 46h17V35h15V24h25"/>'
        '<path d="M4 46V17h20l12 7v11H21v11Z" fill="#ede2cf"/>'
        '<path d="m8 28 5-4 6 3m-10 9 5 2m28-18 5-6 12 8"/>'
        '<path d="M33 46h19l5 7H30Z" fill="#d8c8aa"/>'
        '<path d="M41 44V32h8l6 9h-9m-2-9 8-8 8 3"/>'
        '<circle cx="36" cy="54" r="3" fill="white"/>'
        '<circle cx="52" cy="54" r="3" fill="white"/>'
    ),
    "fuel": (
        '<path d="M19 7C15 16 6 24 6 33a13 13 0 0 0 26 0C32 24 23 15 19 7Z" '
        'fill="#f0dfe1" stroke="#a64f54"/>'
        '<path d="M12 33q0 8 7 8" stroke="#a64f54"/>'
        '<path d="M33 46C27 27 42 16 60 15c-1 20-8 34-27 31Z" '
        'fill="#dfece0" stroke="#3e7654"/>'
        '<path d="m30 54 22-29m-14 17 11-1m-6-6 1-9" stroke="#3e7654"/>'
    ),
    "ship": (
        '<path d="M4 36h55L49 49H16Z" fill="#dceaf2"/>'
        '<path d="M9 36V18h12v18m-8-18V9h4v9M25 36V25h25v11"/>'
        '<rect x="25" y="25" width="11" height="11" rx="5" fill="#edf5f8"/>'
        '<rect x="39" y="25" width="11" height="11" rx="5" fill="#edf5f8"/>'
        '<path d="M12 23h6m-6 6h6M4 54q7-4 14 0t14 0t14 0t13 0"/>'
    ),
    "heat": (
        '<rect x="8" y="13" width="48" height="38" rx="5" fill="#fff4d9"/>'
        '<path d="M18 44V21m9 23V21m10 23V21m9 23V21M3 24h5m48 16h5"/>'
        '<path d="M18 7v6m28 38v6"/>'
    ),
}


def _icon(kind, x, y, size=48, tone="material"):
    glyph = SUPPLY_ICONS[kind] if kind in SUPPLY_ICONS else ICONS[kind]
    return (
        f'<g data-icon="{kind}" transform="translate({x} {y}) scale({size / 64})" '
        f'color="{COLORS[tone]}" stroke="currentColor" stroke-width="2" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round">' + glyph + "</g>"
    )


def _carbon(path, origin, destination):
    key, color, _ = ORIGINS[origin]
    return (
        f'<path data-origin="{key}" data-destination="{destination}" d="{path}" '
        f'fill="none" stroke="{color}" stroke-width="3" '
        f'stroke-linejoin="round" marker-end="url(#origin-{key})"/>'
    )


def overview_svg(system):
    if system not in ("BAU", "CCS", "CCUS"):
        raise ValueError(f"Unknown system: {system}")
    b = (
        "<defs>"
        + "".join(
            f'<marker id="origin-{key}" markerWidth="7" markerHeight="7" '
            'refX="6" refY="3.5" orient="auto" markerUnits="userSpaceOnUse">'
            f'<path d="M0 0 7 3.5 0 7Z" fill="{color}"/></marker>'
            for key, color, _ in ORIGINS
        )
        + "</defs>"
    )
    b += _text(18, 48, "BAU / reference" if system == "BAU" else system, "title")
    for y, line in zip(
        (72, 90),
        {
            "BAU": ("No capture", "investment"),
            "CCS": ("Capture and", "store CO₂"),
            "CCUS": ("Store fossil CO₂", "Reuse non-fossil CO₂"),
        }[system],
    ):
        b += _text(18, y, line, "note")

    b += '<rect x="178" y="6" width="216" height="134" rx="12" fill="#faf5eb"/>'
    b += '<rect x="414" y="6" width="972" height="134" rx="12" fill="#f4f8fa" stroke="#b9cbd3" stroke-dasharray="5 5"/>'
    b += _text(192, 24, "UPSTREAM SUPPLIERS", "boundary")
    b += _text(428, 24, "PLANT PROCESSES · FOREGROUND", "boundary")
    b += _icon("quarry", 188, 31, 42) + _text(241, 55, "Limestone quarry", "label")
    b += _icon("fuel", 188, 85, 42) + _text(241, 103, "Fuel supply", "label")
    b += _text(241, 122, "Fossil + non-fossil", "note")
    b += _arrow("M384 51H426", "material")
    b += _arrow("M384 106H405V80H426", "energy")
    # The 128-wide cover kiln retains its long drum, rings, rollers and burner.
    b += _icon("kiln", 433, 27, 48)
    b += _text(484, 99, "Rotary kiln", "label", "middle")
    b += _text(484, 116, "1 t clinker", "note", "middle")
    for origin, y in enumerate((56, 65, 74)):
        b += _carbon(
            f"M543 {y}H685", origin, "atmosphere" if system == "BAU" else "capture"
        )
    b += _text(613, 43, "CO₂", "label", "middle")

    if system == "BAU":
        b += _icon("atmosphere", 701, 32, 62, "fossil")
        b += _text(778, 65, "Atmosphere", "node-title")
        b += _text(778, 85, "All three CO₂ sources", "note")
        b += _arrow("M484 121V130H992", "energy")
        b += _text(718, 119, "Recovered heat", "note", "middle")
    else:
        b += _icon("capture", 700, 32, 62, "carbon")
        b += _text(774, 64, "CO₂ capture", "node-title")
        b += _text(774, 84, "All three CO₂ sources", "note")
        b += _arrow("M484 121V130H731V103", "energy")
        b += _text(615, 119, "Heat to capture", "note", "middle")
        b += _arrow("M752 105V130H992", "energy")
        if system == "CCS":
            for origin, y in enumerate((56, 65, 74)):
                b += _carbon(f"M902 {y}H944", origin, "transport")
                b += _carbon(f"M1020 {y}H1070", origin, "storage")
            b += _icon("ship", 950, 32, 60, "storage")
            b += _text(980, 109, "Transport", "note", "middle")
            b += _icon("storage", 1080, 32, 62, "storage")
            b += _text(1155, 62, "North Sea storage", "node-title")
            b += _text(1155, 83, "All captured CO₂", "note")
        else:
            for origin, y in enumerate((56, 65)):
                b += _carbon(
                    f"M902 {y}H{932 + origin*9}V{32 + origin*9}H974",
                    origin,
                    "transport",
                )
                b += _carbon(f"M1030 {32 + origin*9}H1070", origin, "storage")
            b += _icon("ship", 979, 12, 47, "storage")
            b += _icon("storage", 1080, 7, 51, "storage")
            b += _text(1148, 31, "North Sea storage", "node-title")
            b += _text(1148, 50, "Captured fossil CO₂", "note")
            b += _carbon("M902 74H949V91H1070", 2, "methanol-to-jet")
            b += _icon("jet", 1080, 68, 46, "bio")
            b += _text(1148, 90, "Fuel production", "node-title")
            b += _text(1148, 110, "Captured non-fossil CO₂", "note")

    b += _icon("heat", 998, 116, 24, "energy")
    b += _text(
        1034, 135, "Exported heat" if system == "BAU" else "Surplus heat", "note"
    )
    b += _arrow("M1127 130H1170", "energy", dashed=True)
    b += _text(1182, 135, "Displaced heat supply", "note")
    return _svg(
        b,
        1400,
        146,
        f"{system}: quarry and fuels to clinker, with three CO₂ origins and their destinations",
    )


def three_system_overview():
    return html.Div(
        [
            html.Div(
                [html.Strong("CO₂ generated by the kiln")]
                + [
                    html.Span(
                        [
                            html.I(
                                style={"backgroundColor": color},
                                **{"aria-hidden": "true"},
                            ),
                            label,
                        ]
                    )
                    for _, color, label in ORIGINS
                ],
                className="overview-carbon-key",
            ),
            html.Div(
                [
                    html.Figure(
                        html.Img(
                            src="data:image/svg+xml;charset=utf-8,"
                            + quote(overview_svg(system)),
                            alt=f"{system}: limestone quarry and fossil and non-fossil fuel supply feed a rotary kiln. "
                            + {
                                "BAU": "All three CO₂ origins reach the atmosphere. Recovered heat is exported.",
                                "CCS": "Captured CO₂ from all three origins is transported to North Sea storage. Heat feeds capture and surplus is exported.",
                                "CCUS": "Captured fossil CO₂ from limestone calcination and fuels is stored in the North Sea. Captured non-fossil CO₂ feeds methanol-to-jet. Heat feeds capture and surplus is exported.",
                            }[system],
                            className="system-svg",
                        ),
                        className=f"overview-route overview-route-{system.lower()}",
                    )
                    for system in ("BAU", "CCS", "CCUS")
                ],
                className="overview-routes",
            ),
        ],
        className="three-system-overview",
    )
