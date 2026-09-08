"""Editable SVG diagrams following lca_time's illustrated system boundaries.

Geometry is presentation code; quantities are passed from the engineering
artifact. Solid arrows are physical flows, dashed arrows are substitutions.
"""

from html import escape
from urllib.parse import quote

COLORS = {
    "ink": "#0b3b52",
    "material": "#738994",
    "energy": "#d18a12",
    "carbon": "#008a82",
    "fossil": "#c44e52",
    "storage": "#4193b8",
    "bio": "#3e7654",
    "time": "#7656a8",
}

# The same rounded linework and lightly filled silhouettes as lca_time's
# system-boundary-beccs.svg; purpose-built glyphs for the cement value chain.
GLYPHS = {
    "truck": '<path d="M5 15h31v29H5Z" fill="currentColor" fill-opacity=".12"/><path d="M36 25h13l9 11v8H36M40 29h7l6 8H40ZM5 44h5m12 0h19m12 0h5"/><circle cx="16" cy="45" r="6"/><circle cx="47" cy="45" r="6"/>',
    "steel": '<path d="M10 9h42v8H36v28h16v8H10v-8h16V17H10Z" fill="currentColor" fill-opacity=".14"/><path d="M15 13h32M15 49h32M31 20v21"/>',
    "kiln": '<path d="M6 48V28l14 7V24l14 9V18h10v30Z" fill="currentColor" fill-opacity=".12"/><path d="M34 18V7h10v11M11 41h4m9 0h4m9 0h3M44 34h11v14H44"/><path d="M11 52h44"/>',
    "capture": '<rect x="10" y="10" width="16" height="39" rx="7" fill="currentColor" fill-opacity=".12"/><rect x="36" y="17" width="16" height="32" rx="7"/><path d="M10 23h16m-16 9h16m-16 9h16M26 16h10v12M36 41H26M6 49h50M43 7v10"/>',
    "ship": '<path d="M5 36h52l-9 13H15Z" fill="currentColor" fill-opacity=".15"/><path d="M12 36V23h25v13m0-6h12v6M17 23v-8h12v8m-6-8V7M5 53q7-5 14 0t14 0t14 0t12 0"/><rect x="17" y="27" width="6" height="5"/><rect x="27" y="27" width="6" height="5"/>',
    "storage": '<path d="M4 20q7-4 14 0t14 0t14 0t14 0M31 8v34m-6-29h12M5 34h19m14 0h20M5 44h19m14 0h20"/><path d="M12 50q20-12 40 0q-20 12-40 0Z" fill="currentColor" fill-opacity=".18"/><path d="m26 36 5 6 5-6"/>',
    "atmosphere": '<path d="M16 43h29a10 10 0 0 0 1-20 15 15 0 0 0-28-6 13 13 0 0 0-2 26Z" fill="currentColor" fill-opacity=".10"/><path d="M23 36V25m-4 4 4-4 4 4M36 36V25m-4 4 4-4 4 4"/>',
    "heat": '<path d="M13 45c-12-12 12-17 0-30M30 45c-12-12 12-17 0-30M47 45c-12-12 12-17 0-30M6 52h49"/>',
    "power": '<path d="m35 5-24 29h16l-4 22 27-33H34Z" fill="currentColor" fill-opacity=".15"/>',
    "hydrogen": '<rect x="12" y="10" width="36" height="43" rx="6" fill="currentColor" fill-opacity=".10"/><path d="M20 18v26m9-26v26m10-26v26M7 26h5m36 10h7M21 6v4m18-4v4"/>',
    "methanol": '<path d="M23 8h16m-12 0v15L12 47q-3 6 5 6h30q8 0 5-6L35 23V8M19 37h26" fill="currentColor" fill-opacity=".1"/><circle cx="29" cy="44" r="2"/><circle cx="37" cy="48" r="2"/>',
    "jet": '<path d="m6 28 19-1 13-20h6l-7 20 15 2 6-7h3l-3 10 3 10h-3l-6-7-15 2 7 20h-6L25 36 6 35Z" fill="currentColor" fill-opacity=".16"/>',
    "split": '<path d="M5 31h19q8 0 8-8V13h23M32 31v15h23"/><path d="m49 7 7 6-7 6m0 21 7 6-7 6"/>',
    "resources": '<path d="m5 49 16-24 8 12L41 13l17 36Z" fill="currentColor" fill-opacity=".13"/><path d="m16 33 5 5 5-5m9-8 6 5 6-5M8 54h46"/>',
    "fuel": '<path d="M15 47V25l14-7 16 7v22Z" fill="currentColor" fill-opacity=".12"/><path d="M29 18V8m-8 5 8 5 8-5M10 52h40m-29-9 8-17 8 17Z"/>',
    "clock": '<circle cx="31" cy="31" r="24" fill="currentColor" fill-opacity=".08"/><path d="M31 13v18l13 9M31 7v3m24 21h-3M31 55v-3M7 31h3"/>',
    "calendar": '<rect x="8" y="13" width="46" height="42" rx="5" fill="currentColor" fill-opacity=".08"/><path d="M8 25h46M19 7v12M43 7v12m-28 17h8m8 0h8m-24 11h8m8 0h8"/>',
    "globe": '<circle cx="31" cy="31" r="24"/><ellipse cx="31" cy="31" rx="12" ry="24"/><path d="M7 31h48M12 17h38M12 45h38"/>',
    "response": '<path d="M7 8v46h49M9 45q13-1 17-18t15-4 15-10"/><path d="M10 49q12-1 18-12t13-6 15-5" opacity=".35"/>',
    "pulse": '<path d="M6 50h50M31 50V9m-7 8 7-8 7 8"/><path d="M34 16q4 25 22 30" stroke-dasharray="3 4"/>',
}

# Industrial silhouettes, rather than a generic factory or laboratory flask.
GLYPHS["kiln"] = (
    '<path d="M7 34 46 21l8 17-39 13Z" fill="currentColor" fill-opacity=".13"/><path d="m17 31 8 17m13-25 8 18M12 51v5m30-14v14M6 56h49M7 34V14h10v16M46 21V8h9v30"/>'
)
GLYPHS["methanol"] = (
    '<rect x="17" y="10" width="29" height="42" rx="12" fill="currentColor" fill-opacity=".12"/><path d="M17 24h29M17 39h29M6 17h11m29 27h11M31 4v6m-10 42v7m20-7v7M6 12v10m51 17v10"/>'
)


def _icon(kind, x, y, size=48, tone="carbon"):
    return (
        f'<g transform="translate({x} {y}) scale({size / 64})" '
        f'color="{COLORS[tone]}" stroke="currentColor" stroke-width="2.4" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round">'
        f'{GLYPHS.get(kind, GLYPHS["clock"])}</g>'
    )


def _text(x, y, value, cls="label", anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{escape(str(value))}</text>'


def _node(x, y, w, title, kind, tone="carbon", note="", h=72):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" ' f'fill="white" stroke="{COLORS[tone]}" stroke-opacity=".45" stroke-width="1.4"/>' + _icon(
        kind, x + 10, y + (h - 48) / 2, 48, tone
    ) + _text(
        x + 66, y + h / 2 - (2 if note else -5), title, "node-title"
    ) + (
        _text(x + 66, y + h / 2 + 18, note, "note") if note else ""
    )


def _arrow(points, tone="carbon", label="", at=None, dashed=False):
    return (
        f'<path d="{points}" fill="none" stroke="{COLORS[tone]}" stroke-width="2.8" '
        f'marker-end="url(#{tone})" stroke-linejoin="round" '
        + ('stroke-dasharray="7 5" ' if dashed else "")
        + "/>"
        + (_text(*at, label, "flow", "middle") if label and at else "")
    )


def _svg(body, width, height, title):
    markers = "".join(
        f'<marker id="{key}" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 9 4.5 0 9Z" fill="{color}"/></marker>'
        for key, color in COLORS.items()
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">'
        f"<title>{escape(title)}</title><defs>{markers}<style>"
        "text{font-family:Arial,Helvetica,sans-serif;fill:#0b3b52}.label{font-size:14px;font-weight:700}"
        ".node-title{font-size:16px;font-weight:700}.note{font-size:13px;fill:#5b6a74}"
        ".flow{font-size:12px;font-weight:700;paint-order:stroke;stroke:white;stroke-width:5px;stroke-linejoin:round}"
        ".boundary{font-size:11px;font-weight:700;letter-spacing:1px;fill:#5b6a74}"
        ".title{font-size:21px;font-weight:700}.quantity{font-size:21px;font-weight:700}"
        "</style></defs>" + body + "</svg>"
    )


def icon_uri(kind: str, tone="carbon") -> str:
    return "data:image/svg+xml;charset=utf-8," + quote(
        _svg(_icon(kind, 0, 0, 64, tone), 64, 64, kind)
    )


def system_svg(system: str, flows, *, compact=False) -> str:
    values = {f["label"]: f for f in flows}

    def qty(label, fallback=""):
        if label not in values:
            return fallback
        item = values[label]
        number = (
            f'{item["value"]:,.0f}'
            if item["unit"].startswith("kg")
            else f'{item["value"]:.2f}'
        )
        return f'{number} {item["unit"]}'

    if compact:
        b = _text(18, 30, system, "title")
        descriptions = {
            "BAU": "No capture investment",
            "CCS": "Store both carbon origins",
            "CCUS": "Store fossil · reuse non-fossil",
        }
        b += _text(18, 51, descriptions[system], "note")
        b += _node(240, 12, 205, "Cement kiln", "kiln", "material", "1 tonne clinker")
        if system == "BAU":
            b += _arrow("M445 48H510", "fossil") + _node(
                510,
                12,
                265,
                "Atmosphere",
                "atmosphere",
                "fossil",
                "Fossil + non-fossil CO₂",
            )
            b += _node(
                940,
                12,
                300,
                "Exported heat",
                "heat",
                "energy",
                "Displaces conventional heat",
            )
            b += _arrow("M342 84V103H910V48H940", "energy")
        else:
            b += _arrow("M445 48H510") + _node(
                510, 12, 225, "CO₂ capture", "capture", "carbon"
            )
            b += _arrow("M735 48H815")
            b += _arrow("M342 84V106H622V84", "energy")
            b += _text(385, 142, "Recovered heat → capture first", "note")
            b += _arrow("M622 106V128H1250V130H1290", "energy", dashed=True)
            b += _text(910, 151, "Surplus → displaced heat", "note")
            if system == "CCS":
                b += _node(815, 12, 230, "Transport", "ship", "storage")
                b += _arrow("M1045 48H1110", "storage") + _node(
                    1110, 12, 255, "North Sea storage", "storage", "storage"
                )
            else:
                b += _arrow("M815 48V23H870", "storage") + _node(
                    870, 0, 280, "North Sea storage", "storage", "storage", h=52
                )
                b += _arrow("M815 48V90H870", "bio") + _node(
                    870, 64, 280, "Methanol-to-jet", "jet", "bio", h=52
                )
                b += _text(1175, 32, "Fossil carbon", "note") + _text(
                    1175, 96, "Non-fossil carbon", "note"
                )
        return _svg(b, 1400, 160, f"{system} clinker investment route")

    b = '<rect x="8" y="7" width="1384" height="414" rx="16" fill="#fbfdfd" stroke="#aebfc7" stroke-dasharray="9 6"/>'
    b += _text(28, 29, "COMPLETE PRODUCT SYSTEM", "boundary") + _text(
        1370, 29, "2025 · per tonne clinker", "boundary", "end"
    )
    b += '<rect x="24" y="43" width="1352" height="92" rx="12" fill="#fff8e9" stroke="#e3c884"/>'
    b += _text(40, 63, "BACKGROUND · UPSTREAM SUPPLY & DISPLACED PRODUCTS", "boundary")
    b += _node(
        40,
        73,
        260,
        "Materials / kiln fuel",
        "resources",
        "material",
        "Fuel: " + qty("Kiln energy"),
        h=51,
    )
    b += _node(
        392,
        73,
        265,
        "Energy suppliers",
        "power",
        "energy",
        "2025: electricity + gas boiler",
        h=51,
    )
    b += _node(
        734,
        73,
        270,
        "Displaced heat supply",
        "heat",
        "energy",
        "Gas-boiler heat displaced",
        h=51,
    )
    if system == "CCUS":
        b += _node(
            1070,
            73,
            280,
            "Conventional jet fuel",
            "jet",
            "energy",
            "Production + combustion",
            h=51,
        )
    else:
        b += _node(
            1070,
            73,
            280,
            "Equipment & services",
            "resources",
            "material",
            "Infrastructure · replacements",
            h=51,
        )
    b += '<rect x="24" y="153" width="1352" height="248" rx="12" fill="#f3f8fa" stroke="#9fbfc9" stroke-dasharray="7 5"/>'
    b += _text(40, 176, "FOREGROUND · PHYSICAL PROCESS CHAIN", "boundary")
    b += _node(50, 217, 210, "Cement kiln", "kiln", "material", "1 t clinker output")
    b += _arrow("M170 124V217", "material")
    # Shared supply bracket: utilities and equipment feed the physical chain.
    if system != "CCUS":
        b += _arrow("M1200 124V151H1351V188", "material")
        b += _text(1338, 179, "Shared inputs", "note", "end")
    if system == "BAU":
        b += _arrow("M520 124V192H210V217", "energy")
        b += _node(
            443,
            206,
            360,
            "Atmosphere",
            "atmosphere",
            "fossil",
            qty("Direct CO₂") + " direct CO₂",
            h=92,
        )
        b += _arrow("M260 253H443", "fossil", "Fossil + non-fossil", (352, 241))
        b += _node(
            935,
            206,
            352,
            "Useful heat",
            "heat",
            "energy",
            qty("Heat exported") + " exported",
            h=92,
        )
        b += _arrow("M155 289V360H910V251H935", "energy", "Heat recovery", (520, 383))
        b += _arrow(
            "M1080 206V146H876V124", "energy", "Avoided heat", (1080, 141), dashed=True
        )
        b += _text(1370, 389, "No capture unit · no storage investment", "note", "end")
        fossil = float(values.get("Fossil share", {}).get("value", 0))
        total = float(values.get("Direct CO₂", {}).get("value", 0))
        if total:
            b += _text(
                458,
                323,
                f"Fossil: {fossil:,.0f} kg · non-fossil: {total-fossil:,.0f} kg",
                "label",
            )
    elif system == "CCS":
        b += _node(
            372,
            217,
            237,
            "CO₂ capture",
            "capture",
            "carbon",
            qty("CO₂ captured") + " captured",
        )
        b += _node(
            745, 217, 251, "Condition & ship", "ship", "storage", "Both carbon origins"
        )
        b += _node(
            1100,
            217,
            251,
            "North Sea storage",
            "storage",
            "storage",
            qty("CO₂ stored") + " injected",
        )
        b += (
            _arrow("M260 253H372", "carbon")
            + _arrow("M609 253H745", "storage")
            + _arrow("M996 253H1100", "storage")
        )
        b += _arrow("M526 124V217", "energy", "Capture utilities", (587, 179))
        b += _arrow(
            "M155 289V329H486V289",
            "energy",
            "Recovered heat → capture first",
            (324, 346),
        )
        b += _arrow(
            "M486 329H1040V146H868V124",
            "energy",
            qty("Surplus heat") + " surplus → export",
            (797, 346),
            dashed=True,
        )
        b += _text(1100, 336, "Uncaptured CO₂ and transport losses", "note")
        b += _text(1100, 354, "remain atmospheric emissions.", "note")
        captured = float(values.get("CO₂ captured", {}).get("value", 0))
        stored = float(values.get("CO₂ stored", {}).get("value", 0))
        b += _text(
            700,
            388,
            f"{captured:,.0f} kg captured − {captured-stored:,.0f} kg conditioning / transport loss = {stored:,.0f} kg injected",
            "label",
            "middle",
        )
    else:
        b = b.replace('height="414"', 'height="484"').replace(
            'height="248"', 'height="318"'
        )
        b += _node(
            343, 220, 219, "CO₂ capture", "capture", "carbon", "Both carbon origins"
        )
        b += _arrow("M540 292V332", "fossil")
        b += _text(537, 350, "Uncaptured CO₂ → air", "note", "middle")
        b += _text(820, 264, "Chain losses → air", "note", "middle")
        b += _node(700, 179, 242, "Condition & ship", "ship", "storage", "Fossil CO₂")
        b += _node(
            1088,
            179,
            268,
            "North Sea storage",
            "storage",
            "storage",
            qty("Fossil CO₂ stored"),
        )
        b += _node(
            700,
            275,
            242,
            "Electrolyzer / H₂",
            "hydrogen",
            "energy",
            "Electricity → hydrogen",
            h=60,
        )
        b += _node(
            700,
            380,
            242,
            "Methanol synthesis",
            "methanol",
            "bio",
            qty("Non-fossil CO₂ to fuel") + " CO₂ feed",
            h=64,
        )
        b += _node(
            1088,
            380,
            268,
            "Methanol-to-jet",
            "jet",
            "bio",
            qty("Synthetic jet fuel") + " jet fuel",
            h=64,
        )
        b += _arrow("M260 253H343") + _arrow(
            "M562 256H626V215H700", "storage", "Fossil", (647, 204)
        )
        b += _arrow("M626 256V412H700", "bio", "Non-fossil", (641, 366))
        b += _arrow("M942 215H1088", "storage", "Same-year storage", (1016, 203))
        b += _arrow("M942 412H1088", "bio", "Single fuel output", (1016, 399))
        b += _arrow("M505 124V220", "energy")
        b += _arrow("M654 99H679V305H700", "energy")
        b += _arrow("M820 335V380", "energy", "H₂", (843, 363))
        b += _arrow(
            "M1340 380H1362V124",
            "energy",
            "Avoided fossil jet",
            (1250, 361),
            dashed=True,
        )
        b += _arrow(
            "M155 289V465H451V292",
            "energy",
            "Recovered heat → capture first",
            (310, 457),
        )
        b += _arrow(
            "M451 465H660V147H868V124",
            "energy",
            "Surplus export",
            (787, 144),
            dashed=True,
        )
        b += _arrow("M1220 444V464", "fossil")
        b += _text(1075, 483, "Atmosphere: non-fossil combustion +1 year", "note")
    return _svg(
        b,
        1400,
        500 if system == "CCUS" else 430,
        f"{system}: foreground and background boundaries with carbon, material, energy and avoided flows",
    )


def diagram_uri(system: str, flows, *, compact=False) -> str:
    return "data:image/svg+xml;charset=utf-8," + quote(
        system_svg(system, flows, compact=compact)
    )
