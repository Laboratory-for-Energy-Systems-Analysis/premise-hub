"""Presenter introduction, with user-confirmed role, projects and interests."""

import base64
import json
import math
from functools import lru_cache
from pathlib import Path

from dash import html

from .branding import logo
from .visuals import icon_svg, svg_uri, label

PROJECTS = (
    ("premise", "Future LCA databases", "https://github.com/polca/premise", "premise"),
    ("TRAILS", "Time-explicit LCA", "https://github.com/Laboratory-for-Energy-Systems-Analysis/trails", "trails"),
    ("carculator", "Vehicle life-cycle models", "https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator", "electric_car"),
    ("EDGES", "Context-aware impact assessment", "https://github.com/Laboratory-for-Energy-Systems-Analysis/edges", "edges"),
)
PUBLICATIONS = (
    ("premise: databases for prospective LCA", "Renewable & Sustainable Energy Reviews · 2022",
     "https://doi.org/10.1016/j.rser.2022.112311"),
    ("How to make climate-neutral aviation fly", "Nature Communications · 2023",
     "https://doi.org/10.1038/s41467-023-39749-y"),
    ("Electrification of passenger cars: when, where and how?", "Renewable & Sustainable Energy Reviews · 2022",
     "https://doi.org/10.1016/j.rser.2022.112475"),
)


@lru_cache(maxsize=1)
def portrait_uri():
    raw = (Path(__file__).parent / "assets/romain-sacchi-portrait.png").read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def _link(children, href, **kwargs):
    return html.A(children, href=href, target="_blank", rel="noopener noreferrer", **kwargs)


@lru_cache(maxsize=1)
def swiss_map_uri():
    """Natural Earth outline; approximate campus location at country scale."""
    rings = json.loads((Path(__file__).parent / "data/switzerland_outline.geojson").read_text())["geometry"]["coordinates"]
    points = [point for ring in rings for point in ring]
    west, east = min(p[0] for p in points), max(p[0] for p in points)
    south, north = min(p[1] for p in points), max(p[1] for p in points)
    cosine = math.cos(math.radians(47))
    scale = min(320 / ((east-west)*cosine),180 / (north-south))

    def project(lon, lat):
        return 20+(lon-west)*cosine*scale, 38+(north-lat)*scale

    paths = " ".join("M" + "L".join(f"{x:.1f} {y:.1f}" for x,y in
                                      (project(*p) for p in ring)) + "Z" for ring in rings)
    px,py = project(8.23,47.54)
    body = ('<rect x="0" y="0" width="360" height="235" rx="14" fill="#f0f6f8"/>'
            + label(18,27,"Switzerland",20,anchor="start",weight=700)
            + f'<path d="{paths}" fill="#cfe3e9" stroke="#719eae" stroke-width="1.6"/>'
            + f'<circle cx="{px:.1f}" cy="{py:.1f}" r="12" fill="#bb5932" fill-opacity=".15"/>'
            + f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#bb5932" stroke="white" stroke-width="2"/>'
            + f'<path d="M{px+6:.1f} {py:.1f}l17 -18h35" fill="none" stroke="#bb5932" stroke-width="1.7"/>'
            + label(px+64,py-20,"PSI",22,"#a64526",anchor="start",weight=750)
            + label(px+64,py+1,"Villigen",16,"#526e7b",anchor="start",weight=500))
    for lon,lat,name,dx,dy in ((7.5886,47.5596,"Basel",-10,-9),(8.5417,47.3769,"Zürich",9,16)):
        x,y = project(lon,lat)
        body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8" fill="#527b90"/>'
        body += label(x+dx,y+dy,name,14,"#526e7b",anchor="end" if dx<0 else "start",weight=500)
    return svg_uri(body,360,235,"Switzerland with PSI marked near Villigen, between Basel and Zürich")


def introduction():
    interests = (
        ("power", "Industrial ecology", "Future energy & mobility systems", "#008a82"),
        ("response", "Time & climate", "Prospective + dynamic LCA", "#3292b5"),
        ("database", "Open science", "Transparent, usable modelling tools", "#7656a8"),
    )
    return html.Div([
        html.Div([
            html.Img(src=portrait_uri(), alt="Portrait of Romain Sacchi", className="bio-portrait"),
            html.Div([
                html.Strong("Scientist", className="bio-role"),
                html.P("Technology Assessment Group"),
                html.P("Laboratory for Energy Systems Analysis"),
                html.Strong("Paul Scherrer Institut · Switzerland", className="bio-institute"),
                _link("PSI profile ↗", "https://www.psi.ch/en/ta/people/romain-sacchi"),
            ],className="bio-affiliation"),
            _link(html.Img(src=swiss_map_uri(),alt="Map of Switzerland locating PSI at Villigen, between Basel and Zürich",
                           className="bio-swiss-map"),"https://www.psi.ch/en/about/how-to-find-us",
                  className="bio-location"),
        ],className="bio-person"),
        html.Section([
            html.H2("Path to PSI"),
            html.Ol([
                html.Li([html.Time(year,dateTime=year),html.Strong(title),html.Span(detail)])
                for year,title,detail in (
                    ("2012","MSc","Environmental Sciences · Aalborg University"),
                    ("2018","Industrial PhD","Industrial Ecology · Aalborg University"),
                    ("2019","Joined PSI","Technology Assessment Group"),
                )
            ]),
        ],className="bio-timeline"),
        html.Div([
            html.Section([
                html.H2("Research interests"),
                html.Div([
                    html.Article([
                        html.Img(src=svg_uri(icon_svg(kind,colour),64,64,title),alt=""),
                        html.Strong(title), html.Span(detail),
                    ],style={"--interest-colour":colour})
                    for kind,title,detail,colour in interests
                ],className="bio-interest-grid"),
            ]),
            html.Section([
                html.Div([html.H2("Open-source projects"),
                          _link("github.com/romainsacchi ↗","https://github.com/romainsacchi")],
                         className="bio-section-heading"),
                html.Div([
                    _link([
                        logo(mark,"bio-project-mark") if mark in ("premise","trails","edges") else
                        html.Img(src=svg_uri(icon_svg(mark,"#527b90"),64,64,name),alt="",className="bio-project-mark"),
                        html.Div([html.Strong(name),html.Span(detail)]),
                        html.B("↗",**{"aria-hidden":"true"}),
                    ],href,className="bio-project") for name,detail,href,mark in PROJECTS
                ],className="bio-project-grid"),
            ]),
            html.Section([
                html.Div([html.H2("Selected publications"),
                          _link("Full record · ORCID ↗","https://orcid.org/0000-0003-1440-0905")],
                         className="bio-section-heading"),
                html.Div([
                    _link([html.Span(venue),html.Strong(title),html.B("Read paper ↗")],
                          href,className="bio-publication")
                    for title,venue,href in PUBLICATIONS
                ],className="bio-publication-grid"),
            ]),
        ],className="bio-work"),
    ],className="speaker-bio")
