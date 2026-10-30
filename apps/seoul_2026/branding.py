"""Local, unchanged project marks for the teaching diagrams and offline export."""

import base64
from functools import lru_cache
from pathlib import Path

from dash import html
from .visuals import icon_svg, svg_uri

ROOT = Path(__file__).resolve().parent
ASSETS = {
    "ecoinvent": (ROOT / "assets/ecoinvent-logo.svg", "image/svg+xml"),
    "premise": (ROOT.parent / "workshop/assets/premise-logo-transparent.png", "image/png"),
    "trails": (ROOT.parent / "lca_time/assets/trails-logo.png", "image/png"),
    "edges": (ROOT / "assets/edges-logo.png", "image/png"),
}
TOOL_URLS = {
    "brightway": "https://docs.brightway.dev/en/latest/",
    "premise": "https://premise.readthedocs.io/en/latest/",
    "trails": "https://trails.readthedocs.io/en/latest/",
    "fair": "https://docs.fairmodel.net/en/latest/",
}


def tool_link(name, label=None):
    return html.A(label or {"brightway": "Brightway", "trails": "TRAILS", "fair": "FaIR"}.get(name, name),
                  href=TOOL_URLS[name], target="_blank", rel="noopener noreferrer",
                  className="tool-link")


@lru_cache(maxsize=4)
def logo_uri(name):
    path, mime = ASSETS[name]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def logo(name, class_name):
    return html.Img(src=logo_uri(name), alt=f"{name} logo", className=class_name)


def database_icon():
    return html.Img(src=svg_uri(icon_svg("database", "#527b90"), 64, 64,
                               "Life-cycle inventory database"),
                    alt="Database", className="background-database-icon")
