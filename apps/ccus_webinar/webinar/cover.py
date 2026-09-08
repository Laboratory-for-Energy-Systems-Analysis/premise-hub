"""Title-slide route illustrations: consistent industrial icons, no result data."""

from urllib.parse import quote

from .diagrams import COLORS, _arrow, _svg, _text

# Larger, purpose-drawn glyphs for the cover. Keep detailed-slide geometry intact.
ICONS = {
    "kiln": (
        # A long, slightly inclined drum, not a short concrete-mixer barrel.
        '<g data-part="foundations"><path d="M15 72h101" stroke-width="2.5"/>'
        '<path d="m38 61-4 11h22l-4-11Zm45-7-4 18h22l-4-18Z" '
        'fill="currentColor" fill-opacity=".16"/>'
        '<circle cx="42" cy="59" r="4" fill="white"/>'
        '<circle cx="51" cy="58" r="4" fill="white"/>'
        '<circle cx="86" cy="52" r="4" fill="white"/>'
        '<circle cx="95" cy="51" r="4" fill="white"/></g>'
        '<g data-part="rotating-drum" transform="rotate(-8 62 39)">'
        '<path d="M23 27h78v24H23Z" fill="#e6eef1"/>'
        '<path d="M27 32h70" stroke="white" stroke-width="3"/>'
        '<ellipse cx="101" cy="39" rx="4" ry="12" fill="#e6eef1"/>'
        '<rect x="41" y="25" width="7" height="28" rx="2" fill="#c2d2d9"/>'
        '<rect x="86" y="25" width="7" height="28" rx="2" fill="#c2d2d9"/>'
        '<ellipse cx="23" cy="39" rx="5" ry="12" fill="#f9f5ed"/>'
        '<ellipse cx="23" cy="39" rx="2.5" ry="7" fill="#edbb67" stroke="#bf7c20" stroke-width="1.5"/>'
        '</g><g data-part="burner" stroke="#bf7c20">'
        '<path d="M5 47h21" stroke-width="3"/>'
        '<path d="m27 43 14-2-5 5 9 1-17 5Z" fill="#e9ae4c" stroke-width="1.2"/></g>'
        '<g data-part="feed-chute"><path d="M105 10h15l-4 12h-7Z" fill="#e6eef1"/>'
        '<path d="M112 22v8h-7"/></g>'
        '<path d="M55 17a11 7 0 0 1 21-2m-1-5 1 5-5 1" stroke-width="1.7"/>'
    ),
    "capture": (
        '<rect x="10" y="9" width="17" height="42" rx="8" fill="currentColor" fill-opacity=".10"/>'
        '<rect x="38" y="17" width="16" height="34" rx="8" fill="currentColor" fill-opacity=".10"/>'
        '<path d="M10 22h17m-17 9h17m-17 9h17M27 17h6v25h5M27 46h11M6 54h52M18 4v5m28 2v6"/>'
        '<path d="M14 47V16m-3 4 3-4 3 4" stroke-width="1.5" opacity=".6"/>'
    ),
    "storage": (
        '<path d="M4 15q7-4 14 0t14 0t14 0t14 0"/>'
        '<path d="M5 28h19m14 0h21M5 36h19m14 0h21" opacity=".5"/>'
        '<path d="M31 5v38m-5-6 5 6 5-6M26 8h10"/>'
        '<path d="M8 49q22-14 46 0q-24 13-46 0Z" fill="currentColor" fill-opacity=".18"/>'
        '<path d="M15 49q17-6 32 0" opacity=".6"/>'
    ),
    "atmosphere": (
        '<path d="M15 45h32a11 11 0 0 0 2-22 16 16 0 0 0-30-6 14 14 0 0 0-4 28Z" fill="currentColor" fill-opacity=".08"/>'
        '<path d="M23 37V25m-4 4 4-4 4 4M38 37V25m-4 4 4-4 4 4"/>'
        '<path d="M23 54v-4m15 4v-4" opacity=".5"/>'
    ),
    "jet": (
        '<path d="M7 28l18-1L39 7h5l-7 20 15 2 6-7h3l-3 10 3 10h-3l-6-7-15 2 7 20h-5L25 36 7 35Z" fill="currentColor" fill-opacity=".12"/>'
        '<path d="M3 25h8M2 39h9" opacity=".5"/>'
    ),
}


def _icon(kind, x, y, size, tone):
    if kind == "kiln":
        # The kiln has a landscape silhouette; its anchor remains identical in
        # all three routes while the other icons retain their square viewport.
        return (
            f'<g transform="translate({x} {y})" color="#526e7c" '
            'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round" fill="none">' + ICONS[kind] + "</g>"
        )
    return (
        f'<g transform="translate({x} {y}) scale({size / 64})" '
        f'color="{COLORS[tone]}" stroke="currentColor" stroke-width="2.2" '
        'stroke-linecap="round" stroke-linejoin="round" fill="none">'
        + ICONS[kind]
        + "</g>"
    )


def route_uri(system):
    """Keep kiln, capture and destination on the same coordinates across cards."""
    b = _icon("kiln", 6, 23, 84, "material")
    b += _text(70, 139, "Rotary kiln", "node-title", "middle")
    if system == "BAU":
        b += _arrow("M148 69H490", "fossil")
        b += _text(302, 54, "Direct CO₂ emissions", "node-title", "middle")
        b += _icon("atmosphere", 502, 26, 84, "fossil")
        b += _text(546, 139, "Atmosphere", "node-title", "middle")
    else:
        b += _arrow("M148 69H229", "carbon")
        b += _icon("capture", 242, 27, 84, "carbon")
        b += _text(284, 139, "CO₂ capture", "node-title", "middle")
        if system == "CCS":
            b += _arrow("M340 69H490", "storage")
            b += _icon("storage", 502, 26, 84, "storage")
            b += _text(546, 139, "North Sea storage", "node-title", "middle")
        else:
            b += _arrow("M340 69H404V34H477", "storage")
            b += _arrow("M404 69V110H477", "bio")
            b += _icon("storage", 487, 1, 64, "storage")
            b += _text(565, 27, "North Sea storage", "node-title")
            b += _text(565, 49, "Fossil carbon", "note")
            b += _icon("jet", 487, 78, 64, "bio")
            b += _text(565, 106, "Jet fuel", "node-title")
            b += _text(565, 128, "Non-fossil carbon", "note")
    return "data:image/svg+xml;charset=utf-8," + quote(
        _svg(b, 720, 152, f"{system}: cement production and carbon destinations")
    )
