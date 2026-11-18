"""Schematic bridge from an aggregated LCA to overlapping temporal layers."""

from functools import lru_cache
from html import escape
from urllib.parse import quote

from dash import html


def label(x, y, value, size=19, colour="#173747", weight=500, anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{colour}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'


def icon(kind, x, y, size, colour):
    glyphs = {
        "activities": '<rect x="2" y="10" width="8" height="12" rx="2" fill="currentColor" fill-opacity=".08"/><rect x="22" y="10" width="8" height="12" rx="2" fill="currentColor" fill-opacity=".08"/><path d="M10 16h12m-4-4 4 4-4 4M6 6V3m20 23v3"/>',
        "gases": '<path d="m9 10 6 6m3 3 6 5m-5-9 6-6"/><circle cx="6" cy="7" r="4" fill="currentColor" fill-opacity=".12"/><circle cx="16" cy="17" r="6" fill="currentColor" fill-opacity=".08"/><circle cx="27" cy="6" r="3"/><circle cx="27" cy="27" r="3"/>',
        "economy": '<path d="M3 28h26M6 24V14h5v10m5 0V9h5v15m5 0V4h4v20M3 10l7-6 7 2 9-4m-5 0h5v5"/>',
        "atmosphere": '<path d="M8 25h16a6 6 0 0 0 0-12 9 9 0 0 0-17-2 7 7 0 0 0 1 14Z"/><path d="M5 5Q16-1 27 6m-3-3 4 3-5 2"/>',
        "environment": '<path d="M9 28Q4 12 28 7Q29 25 9 28Z" fill="currentColor" fill-opacity=".08"/><path d="m9 0 13-13" transform="translate(0 28)"/><path d="M5 3Q-1 11 5 16Q11 11 5 3Z"/>',
        "build": '<path d="M6 30h14M10 30V4m0 0L2 11h28L10 4Zm6 7v19M10 16l6 6-6 6M26 11v10"/><rect x="22" y="21" width="8" height="6" rx="1" fill="currentColor" fill-opacity=".13"/>',
        "operate": '<path d="M3 29V13l10 5v-7l10 6V4h6v25H3Z" fill="currentColor" fill-opacity=".09"/><path d="M7 23h3m5 0h3m5 0h3M23 4h6M7 29v-2m16 2v-2"/>',
        "cycle": '<path d="M26 11a11 11 0 0 0-19-3m19-4v7h-7M6 21a11 11 0 0 0 19 3M6 28v-7h7"/><path d="m13 13 6 6m0-6-6 6" stroke-opacity=".6"/>',
        "factory": '<path d="M2 29V14l10 5v-8l10 7V3h7v26H2Z" fill="currentColor" fill-opacity=".09"/><path d="M7 24h3m5 0h3m5 0h3M22 3h7m-4 0V1"/>',
        "wind": '<path d="M16 15v15M11 30h10M16 15 14 4q0-3 3-3l2 2-3 12ZM16 15l10 5q3 2 1 4l-3 1-8-10ZM16 15 6 24q-3 1-4-2l1-3 13-4Z" fill="currentColor" fill-opacity=".06"/><circle cx="16" cy="15" r="2" fill="white"/>',
        "solar": '<path d="m5 14 22 0 3 13H2l3-13Zm-1 6h24M12 14l-1 13m9-13 1 13M11 27v4m10-4v4M8 31h16" fill="currentColor" fill-opacity=".07"/><circle cx="16" cy="5" r="3"/><path d="M16 0v1M9 5H7m16 0h2M11 1l-1-1m11 1 1-1"/>',
    }
    return f'<g transform="translate({x} {y}) scale({size/32})" color="{colour}" fill="none" stroke="{colour}" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round">{glyphs[kind]}</g>'


@lru_cache(maxsize=1)
def visual_uri():
    parts = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 512" role="img">
    <title>Un bilan agrégé devient une chaîne datée, avec des profils de gaz et des contextes qui changent</title>
    <defs>
      <linearGradient id="sum" x2="0" y2="1"><stop stop-color="#176181"/><stop offset="1" stop-color="#0b3b52"/></linearGradient>
      <linearGradient id="context"><stop stop-color="#f1f7f5"/><stop offset="1" stop-color="#e7f1f8"/></linearGradient>
      <marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 7 3.5 0 7Z" fill="#8aa7b2"/></marker>
    </defs><g font-family="Arial,sans-serif">
    <rect x="8" y="8" width="285" height="484" rx="20" fill="#f1f6f8"/>
    ''']
    parts += [label(32, 45, "ACV AGRÉGÉE", 16, "#527780", 750),
              label(32, 84, "Un score lisible", 27, weight=750),
              label(32, 114, "Les dates se superposent", 18, "#527780")]
    for x, gas, colour in ((45, "CO₂", "#3e7654"), (125, "CH₄", "#c29328"), (205, "N₂O", "#8873ad")):
        parts += [f'<rect x="{x-8}" y="160" width="65" height="33" rx="16" fill="white" stroke="{colour}" stroke-opacity=".65"/>',
                  label(x+25, 183, gas, 20, colour, 700, "middle"),
                  f'<path d="M{x+25} 193Q{x+25} 220 150 242" fill="none" stroke="{colour}" stroke-width="2.5" opacity=".55"/>']
    parts += ['<circle cx="150" cy="287" r="65" fill="none" stroke="#c6dce5" stroke-width="1.5" stroke-dasharray="3 7"/>',
              '<circle cx="150" cy="287" r="51" fill="url(#sum)"/>',
              label(150, 301, "Σ", 59, "white", 500, "middle"),
              label(150, 325, "CO₂-eq", 15, "#c1dce8", 600, "middle")]
    for x, case, colour, fill in ((28, "BECCS", "#3e7654", "#e4efe7"), (157, "DACCS", "#3292b5", "#e1eef5")):
        parts += [f'<path d="M150 339L{x+54} 389" stroke="#a0b8c2" fill="none"/>',
                  f'<rect x="{x}" y="389" width="112" height="39" rx="10" fill="{fill}"/>',
                  label(x+56, 416, case, 22, colour, 700, "middle")]
    parts += [label(150, 461, "Un résultat par système", 18, "#527780", 500, "middle"),
              '<path d="M308 246H327V233L354 255L327 277V264H308Z" transform="translate(0 18)" fill="#9bbcc9"/>',
              label(380, 42, "DES FLUX DATÉS, DANS UN MONDE QUI ÉVOLUE", 17, "#008a82", 750)]

    # A common calendar visibly passes through the project, flows and contexts.
    for x in (590, 730, 1035, 1295):
        parts.append(f'<path d="M{x} 67V473" stroke="#d3e2e8" stroke-dasharray="3 6"/>')
    parts += ['<rect x="706" y="66" width="44" height="407" fill="#3292b5" opacity=".045"/>',
              icon("activities", 379, 76, 32, "#a77b31"),
              label(420, 101, "Les activités", 22, weight=750),
              icon("gases", 379, 195, 32, "#3e7654"),
              label(420, 220, "Les flux", 22, weight=750),
              label(420, 245, "Gaz et profils distincts", 17, "#527780")]

    # Event nodes and an operating interval; links carry the timing downstream.
    parts.append('<path d="M604 108H1278" stroke="#9bb5c0" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
    parts += ['<rect x="731" y="88" width="250" height="40" rx="20" fill="#e4f1ee" stroke="#8bbbae"/>',
              icon("operate", 746, 91, 32, "#378d80"),
              '<circle cx="590" cy="108" r="28" fill="#fffbf2" stroke="#c8a865" stroke-width="1.5"/>',
              icon("build", 570, 86, 40, "#a77b31"),
              '<circle cx="1035" cy="108" r="28" fill="#f8f5fc" stroke="#ad9fc2" stroke-width="1.5"/>',
              icon("cycle", 1015, 88, 40, "#8873ad"),
              label(590, 75, "Construire", 19, "#785c24", 650, "middle"),
              label(851, 114, "Exploiter", 20, "#2c6f65", 700, "middle"),
              label(1035, 75, "Fin de vie", 19, "#75608c", 650, "middle"),
              label(1213, 96, "Effets prolongés", 18, "#527780", 600, "middle"),
              '<path d="M590 135V183M856 129V180M1035 134V185" stroke="#b7cbd4" stroke-width="1.5" stroke-dasharray="3 4"/>']

    # Different release and uptake schedules. No quantitative axis or model data.
    parts += ['<g transform="translate(0 16)">',
              '<path d="M566 212H1362" stroke="#b7ccd4" stroke-width="1.2"/>',
              '<path d="M566 212L590 174L614 212H733Q792 162 866 184T981 212H1362" fill="none" stroke="#c66c5c" stroke-width="3"/>',
              '<path d="M566 212L590 174L614 212H733Q792 162 866 184T981 212Z" fill="#c66c5c" opacity=".12"/>',
              '<path d="M566 212H740Q758 185 778 212H1035Q1053 185 1071 212H1362" fill="none" stroke="#c29328" stroke-width="2.8"/>',
              '<path d="M566 212H750Q815 193 889 201T1050 210H1362" fill="none" stroke="#8873ad" stroke-width="2.7" stroke-dasharray="5 4"/>',
              '<path d="M566 212H730Q814 256 901 227T1030 212Q1125 273 1230 250T1355 213" fill="none" stroke="#3e7654" stroke-width="3.5"/>',
              '<path d="M730 212Q814 256 901 227T1030 212Q1125 273 1230 250T1355 213V212Z" fill="#3e7654" opacity=".13"/>',
              label(1163, 184, "Émissions (+)", 18, "#b45f50", 650),
              label(1130, 279, "Absorptions (−)", 18, "#3e7654", 650),
              label(563, 160, "CO₂ · CH₄ · N₂O", 17, "#527780", 500),
              '<path d="M566 299H1362" stroke="#d4e3e9"/>', '</g>']

    # The economy supplies each dated activity; the receiving world evolves too.
    parts += ['<g transform="translate(0 30)">',
              '<rect x="370" y="311" width="1016" height="109" rx="15" fill="url(#context)"/>',
              icon("economy", 382, 324, 27, "#008a82"),
              label(420, 346, "L’économie", 21, weight=750),
              icon("environment", 382, 372, 27, "#8873ad"),
              label(420, 394, "L’environnement", 20, weight=750)]
    # Three supply snapshots with an energy/material mix and short connectors.
    for x, kind, colour, shares in (
        (603, "factory", "#7a8790", (21, 9, 6)),
        (897, "wind", "#378d80", (12, 9, 15)),
        (1200, "solar", "#378d80", (5, 9, 22)),
    ):
        parts.append(f'<rect x="{x-4}" y="313" width="46" height="43" rx="8" fill="white" opacity=".9"/>')
        parts.append(icon(kind, x, 314, 40, colour))
        y = 354
        for h, fill in zip(shares, ("#8e9ba3", "#b5a1c8", "#6cafa1")):
            y -= h
            parts.append(f'<rect x="{x+54}" y="{y}" width="22" height="{h}" rx="2" fill="{fill}"/>')
    parts += ['<path d="M691 341H862M985 341H1167" stroke="#9fb9c4" fill="none" marker-end="url(#arrow)"/>',
              '<path d="M565 362H1370" stroke="#d8e5e9"/>',
              '<path d="M620 388C739 387 873 370 1012 379S1221 399 1368 378" fill="none" stroke="#8873ad" stroke-width="2.7"/>',
              '<path d="M620 388C792 397 1104 392 1368 386" fill="none" stroke="#3292b5" stroke-width="2.7"/>',
              label(815, 409, "Atmosphère · eau · sols · écosystèmes", 16, "#527780", 500),
              '</g>',
              '<path d="M729 343V310" stroke="#008a82" stroke-width="1.5" marker-end="url(#arrow)"/>',
              '<path d="M1102 304V341" stroke="#8873ad" stroke-width="1.5" marker-end="url(#arrow)"/>',
              '<path d="M565 480H1370" stroke="#819da8" stroke-width="1.5" marker-end="url(#arrow)"/>']
    for x, title in ((590, "Avant"), (730, "Mise en service"), (1035, "Années"), (1295, "Décennies")):
        parts += [f'<circle cx="{x}" cy="480" r="3" fill="white" stroke="#819da8" stroke-width="1.4"/>',
                  label(x, 503, title, 17, "#527780", 500, "middle")]
    parts.append('</g></svg>')
    return "data:image/svg+xml," + quote("".join(parts))


def time_bridge():
    return html.Div([
        html.Img(src=visual_uri(), alt="À gauche, les flux BECCS et DACCS sont agrégés. À droite, construction, exploitation et fin de vie sont reliées aux émissions et absorptions datées. L’économie qui fournit ces activités et l’atmosphère et les milieux qui reçoivent les flux évoluent sur le même calendrier.", className="time-bridge-visual"),
        html.Div([
            html.Strong("CO₂ non fossile : quel bilan, à quelle date, dans quel monde ?"),
            html.Span("La question s’étend aux autres impacts environnementaux."),
        ], className="time-bridge-question"),
        html.P("Schéma conceptuel · profils et évolutions illustratifs, sans échelle quantitative.", className="source"),
    ], className="time-bridge")
