"""Public-SI BAU illustration, without private workbook quantities or links."""

import json
from pathlib import Path
from urllib.parse import quote

from dash import html

from .diagrams import COLORS, _arrow, _svg, _text
from .overview import ORIGINS, _icon

DETAIL = json.loads(
    (
        Path(__file__).resolve().parents[1] / "data/public/bau_detail_2025.json"
    ).read_text()
)


def _utility_icon(kind, x, y, size=54):
    glyphs = {
        "equipment": (
            '<path d="m14 7 8 8-7 7-8-8a14 14 0 0 0 17 18l22 22a6 6 0 0 0 9-9L33 23A14 14 0 0 0 14 7Z" fill="#e5edf1"/>'
            '<circle cx="50" cy="49" r="2"/>'
            '<path d="m5 54 13-13 6 6-13 13H5Z" fill="#c2d2d9"/>'
        ),
        "electricity": (
            '<path d="M9 56h46M16 56 27 7h10l11 49M20 39h24M24 22h16M15 22h34M12 13h40"/>'
            '<path d="m25 25 15 14-20 13m19-27L24 39l21 13M14 13v7m36-7v7M16 22v7m32-7v7"/>'
        ),
        "boiler": (
            '<rect x="8" y="15" width="43" height="40" rx="7" fill="#fff4d9"/>'
            '<path d="M40 15V5h14v7h-6v3M4 27h4m43 15h9"/>'
            '<circle cx="20" cy="25" r="4"/><path d="m20 25 2-2"/>'
            '<path d="M30 28c-3 10-11 12-8 19 4 7 18 3 15-5l-3-6-3 6c-3-4 2-7-1-14Z" fill="#edbd64"/>'
        ),
    }
    tone = "material" if kind == "equipment" else "energy"
    return (
        f'<g data-icon="{kind}" transform="translate({x} {y}) scale({size/64})" '
        f'color="{COLORS[tone]}" stroke="currentColor" stroke-width="2" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round">'
        + glyphs[kind]
        + "</g>"
    )


def _box(x, y, w, h, *, background=False):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" '
        f'fill="{"#fff9ed" if background else "white"}" stroke="#c8d7dc"/>'
    )


def bau_svg(detail=DETAIL):
    b = "<style>.fuel-label{font-size:15px}.fuel-amount{font-size:16px;font-weight:700}</style>"
    b += '<rect x="8" y="8" width="1384" height="472" rx="15" fill="white" stroke="#aebfc7" stroke-dasharray="7 5"/>'
    b += _text(26, 30, "COMPLETE PRODUCT SYSTEM", "boundary")
    b += _text(1372, 30, "2025 illustration · per tonne of clinker", "boundary", "end")
    b += '<rect x="24" y="44" width="360" height="411" rx="12" fill="#faf5eb"/>'
    b += _text(40, 64, "BACKGROUND · MATERIAL & FUEL SUPPLY", "boundary")
    b += _icon("quarry", 43, 76, 55)
    b += _text(111, 99, "Limestone (chalk)", "node-title")
    b += _text(
        111,
        122,
        f'≈ {detail["limestone_as_chalk_slurry"]["value"]:,.0f} kg chalk slurry (rounded)',
        "note",
    )

    b += _icon("fuel", 42, 143, 39)
    b += _text(91, 166, "Kiln fuel mix", "node-title")
    b += _text(
        366, 165, f'{detail["kiln_energy"]["value"]:.2f} GJ', "node-title", "end"
    )
    b += _text(366, 190, "kg / tonne clinker", "note", "end")
    fuels = {f["name"]: f for f in detail["fuels"]}
    rows = [
        ("Refuse-derived fuel (RDF)", ("RDF",)),
        ("Coal", ("Coal",)),
        ("Petroleum coke", ("Petroleum coke",)),
        ("Meat and bone meal", ("Meat and bone meal",)),
        ("Sewage sludge", ("Sewage sludge",)),
        ("Cement-bound wood board", ("Cement-bound wood fiber board",)),
        ("Wood chips", ("Wood chips",)),
        ("Paper sludge", ("Paper sludge",)),
        ("Fuel oil + gas oil", ("Fuel oil", "Gas oil")),
    ]
    shown = {name for _, names in rows for name in names}
    if any(f["value"] > 0 and f["name"] not in shown for f in detail["fuels"]):
        raise ValueError("The BAU fuel panel is missing a positive fuel input")
    for i, (label, names) in enumerate(rows):
        y = 210 + i * 23
        fractions = {fuels[name]["non_fossil_carbon_fraction"] for name in names}
        tone = (
            COLORS["fossil"]
            if fractions == {0.0}
            else COLORS["bio"] if fractions == {1.0} else COLORS["energy"]
        )
        b += f'<circle cx="47" cy="{y-5}" r="4" fill="{tone}"/>'
        b += _text(62, y, label, "fuel-label")
        b += _text(
            366,
            y,
            f'{sum(fuels[name]["value"] for name in names):.1f}',
            "fuel-amount",
            "end",
        )
    b += _text(
        42,
        423,
        f'RDF carbon: {fuels["RDF"]["non_fossil_carbon_fraction"]:.0%} non-fossil',
        "label",
    )
    b += _text(42, 445, "Other raw materials and transport included", "note")

    b += _box(420, 52, 275, 80, background=True)
    b += _utility_icon("equipment", 431, 65, 49)
    b += _text(490, 80, "Equipment & services", "node-title")
    b += _text(490, 103, "Plant infrastructure", "note")
    b += _box(718, 52, 309, 80, background=True)
    b += _utility_icon("electricity", 730, 65, 51)
    b += _text(793, 77, "Electricity supply", "node-title")
    b += _text(793, 99, "Kiln operation", "note")
    b += _text(793, 119, "Heat-recovery pumps", "note")

    b += '<rect x="416" y="163" width="952" height="197" rx="12" fill="#f3f8fa" stroke="#afc7d0" stroke-dasharray="7 5"/>'
    b += _text(1348, 184, "FOREGROUND · CLINKER PRODUCTION", "boundary", "end")
    b += _box(444, 196, 209, 145)
    b += _icon("kiln", 450, 206, 91)
    b += _text(549, 332, "Rotary kiln", "node-title", "middle")
    b += _text(549, 355, "1 tonne clinker", "label", "middle")
    # Every supply arrow terminates on an actual process box.
    b += (
        '<g data-connection="limestone-to-kiln">'
        + _arrow("M384 106H402V235H444", "material")
        + "</g>"
    )
    b += (
        '<g data-connection="fuel-to-kiln">' + _arrow("M384 287H444", "energy") + "</g>"
    )
    b += (
        '<g data-connection="equipment-to-kiln">'
        + _arrow("M552 132V196", "material")
        + "</g>"
    )
    b += (
        '<g data-connection="electricity-to-kiln">'
        + _arrow("M869 132V146H616V196", "energy")
        + "</g>"
    )

    origins = (
        ("calcination_fossil", "Raw-material calcination · fossil CO₂", ORIGINS[0][1]),
        ("fuel_fossil", "Fuel combustion · fossil CO₂", ORIGINS[1][1]),
        ("fuel_non_fossil", "Fuel combustion · non-fossil CO₂", ORIGINS[2][1]),
    )
    for i, (key, label, color) in enumerate(origins):
        y = 225 + 45 * i
        b += f'<g data-emission="{key}">'
        b += f'<path d="M653 {y}H1035" stroke="{color}" stroke-width="3"/><path d="M1033 {y-4}l8 4-8 4Z" fill="{color}"/>'
        b += _text(670, y - 12, label, "label")
        if key in detail["emissions"]:
            b += _text(
                1016,
                y - 12,
                f'{detail["emissions"][key]["value"]:,.0f} kg',
                "node-title",
                "end",
            )
        b += "</g>"
    b += _box(1042, 193, 310, 151)
    b += _icon("atmosphere", 1151, 200, 74, "material")
    b += _text(1197, 304, "Atmosphere", "title", "middle")
    b += _text(1197, 327, "All three kiln CO₂ streams", "note", "middle")

    b += '<rect x="416" y="375" width="605" height="77" rx="12" fill="#f3f8fa"/>'
    b += _text(436, 398, "HEAT RECOVERY", "boundary")
    b += _box(696, 384, 300, 65)
    b += _icon("heat", 708, 390, 50, "energy")
    b += _text(773, 409, "Useful heat", "node-title")
    b += _text(773, 432, "Exported to district heating", "note")
    b += _arrow("M626 341V416H696", "energy")
    b += _box(1064, 384, 290, 65, background=True)
    b += _utility_icon("boiler", 1076, 389, 53)
    b += _text(1141, 408, "Natural gas boiler", "node-title")
    b += _text(1141, 432, "Avoided heat production", "note")
    b += _arrow("M996 416H1064", "energy", dashed=True)
    b += (
        '<g data-connection="electricity-to-heat-recovery">'
        + _arrow("M1027 88H1380V465H840V449", "energy")
        + "</g>"
    )
    b += _text(1222, 478, "Heat-recovery electricity", "note", "middle")
    return _svg(
        b,
        1400,
        487,
        "2025 public-SI illustration: interpolated fuel inputs, rounded chalk supply, connected utilities and three atmospheric CO₂ streams",
    )


def bau_detail():
    return html.Div(
        [
            html.Figure(
                html.Img(
                    src="data:image/svg+xml;charset=utf-8," + quote(bau_svg()),
                    alt="2025 BAU per tonne of clinker. Limestone arrives as chalk slurry. RDF, coal, petroleum coke and smaller waste and oil fractions feed the kiln. Fossil calcination CO₂, fossil fuel CO₂ and non-fossil fuel CO₂ are emitted separately. Electricity supplies the kiln and heat recovery, equipment supplies the kiln, and exported heat displaces a natural gas boiler.",
                    className="system-svg",
                ),
                className="bau-detail-figure",
            ),
            html.Div(
                [
                    html.Strong("Fuel carbon"),
                    html.Span(
                        [html.I(style={"backgroundColor": COLORS["fossil"]}), "Fossil"]
                    ),
                    html.Span(
                        [html.I(style={"backgroundColor": COLORS["bio"]}), "Non-fossil"]
                    ),
                    html.Span(
                        [html.I(style={"backgroundColor": COLORS["energy"]}), "Mixed"]
                    ),
                    html.Span(
                        "Solid arrows: physical flows · Dashed arrow: avoided supply",
                        className="bau-arrow-key",
                    ),
                ],
                className="bau-detail-key",
            ),
            html.P(
                "Fuel inputs and fuel CO₂: 2025 interpolation from published SI.2, using the same fuel trajectory as the calculation model.",
                className="bau-public-basis",
            ),
        ],
        className="bau-detail-layout",
    )
