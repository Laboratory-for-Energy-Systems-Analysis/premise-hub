from __future__ import annotations
import os
from dash import dcc, html

TITLE = "Why timing matters in life cycle assessment"
UPLOAD_NAME = "SNU_2026_Romain_Sacchi_Time_explicit_LCA"
PREFIX = os.getenv("SEOUL_2026_REQUESTS_PREFIX", "/")


def text(value, cls=""):
    return html.P(value, className=cls)


def callout(value):
    return html.Div(value, className="callout")


def stack(*children):
    return html.Div(list(children), className="stack")


def cards(items, columns=3):
    return html.Div(
        [
            html.Article(
                [
                    html.Span(f"0{i + 1}", className="small-label"),
                    html.H2(title),
                    text(detail),
                ],
                className="snu-card",
            )
            for i, (title, detail) in enumerate(items)
        ],
        className=f"snu-grid cols-{columns}",
    )


def equation(formula, definitions, interpretation):
    return stack(
        html.Div(formula, className="equation", role="math"),
        html.Div(
            [
                html.Div([html.Strong(symbol), html.Span(detail)])
                for symbol, detail in definitions
            ],
            className="equation-key",
        ),
        text(interpretation, "source"),
    )


def sym(base, sub=None, sup=None):
    return html.Span(
        [
            base,
            html.Sub(sub) if sub is not None else None,
            html.Sup(sup) if sup is not None else None,
        ]
    )


def _dated_equations():
    return equation(
        [
            html.Div(
                [
                    sym("Σ", "j"),
                    " ",
                    sym("Σ", "u"),
                    " ",
                    sym("A", "ij"),
                    "(t, u) ",
                    sym("x", "j"),
                    "(u) = ",
                    sym("f", "i"),
                    "(t)",
                ]
            ),
            html.Div(
                [
                    sym("I", "g"),
                    "(t) = ",
                    sym("Σ", "j"),
                    " ",
                    sym("Σ", "u"),
                    " ",
                    sym("B", "gj"),
                    "(t, u) ",
                    sym("x", "j"),
                    "(u)",
                ]
            ),
        ],
        [
            ("t, u", "Exchange-event year and year of activity operation"),
            (
                sym("A", "ij"),
                "Dated product exchanges per unit of activity; balance every product and year",
            ),
            (sym("B", "gj"), "Dated elementary exchanges; retain gas or flow identity"),
        ],
        "General time-indexed inventory formulation. TRAILS implements dated routing plus residual annual solves.",
    )


def _climate_equations():
    return equation(
        [
            html.Div(
                [
                    "Static factors:     S = ",
                    sym("Σ", "t"),
                    " ",
                    sym("Σ", "g"),
                    " ",
                    sym("I", "g"),
                    "(t) · ",
                    sym("GWP", "100,g"),
                ]
            ),
            html.Div(
                [
                    "Dynamic response:     ΔR(τ) ≈ ",
                    sym("Σ", "t ≤ τ"),
                    " ",
                    sym("Σ", "g"),
                    " ",
                    sym("I", "g"),
                    "(t) · ",
                    sym("r", "g"),
                    "(τ, t)",
                ]
            ),
            html.Div(["Common window:     J(H) = ", sym("∫", "t₀", "H"), " ΔR(τ) dτ"]),
        ],
        [
            ("t, τ, H", "Event year, response year and common calendar horizon"),
            (
                sym("r", "g"),
                "Gas-specific marginal response kernel in a defined background state",
            ),
            (
                "ΔR",
                "Forcing or temperature perturbation; FaIR can simulate this directly",
            ),
        ],
        "Equal GWP100 totals need not imply equal interim forcing or equal integrated climate effects.",
    )


def graph(fig, identifier=None):
    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": False, "responsive": True},
        className="chart",
        style={"height": "100%", "minHeight": 0},
        **({"id": identifier} if identifier else {}),
    )


def image(filename, alt):
    return html.Img(src=PREFIX + "shared/" + filename, alt=alt, className="snu-visual")


def _rewrite(component):
    """Reuse figures/layouts without depending on the source deck's mount point."""
    for prop in ("src",):
        value = getattr(component, prop, None)
        if isinstance(value, str):
            if value.startswith(PREFIX + "assets/iam-logos/"):
                # Native model/team marks use this app's local Dash assets.
                # Reused source-deck assets below still go through /shared/.
                pass
            elif "/shared/" in value:
                setattr(
                    component, prop, PREFIX + "shared/" + value.split("/shared/", 1)[1]
                )
            elif value.endswith("system-flows.svg"):
                setattr(component, prop, PREFIX + "system-flows.svg")
            elif "assets/" in value:
                setattr(
                    component, prop, PREFIX + "shared/" + value.split("assets/", 1)[1]
                )
    children = getattr(component, "children", None)
    for child in children if isinstance(children, (list, tuple)) else [children]:
        if child is not None:
            _rewrite(child)
    return component


def _cover():
    return [
        image(
            "cover-iam-trajectories.svg",
            "Conditional pathways of technology and emissions",
        ),
        html.Div(
            [
                html.Div(
                    "Seoul National University · graduate LCA seminar",
                    className="cover-kicker",
                ),
                html.H1(TITLE),
                text(
                    "How does accounting for time change the life cycle assessment of long-lived systems in rapidly changing economies?",
                    "cover-subtitle",
                ),
                html.Div(
                    [
                        html.Strong("Romain Sacchi"),
                        html.Span("Paul Scherrer Institut · 30 October 2026"),
                    ],
                    className="cover-presenter",
                ),
            ],
            className="cover-copy",
        ),
    ]


def _sources():
    from .resources import resource_guide
    return resource_guide()


def _print_safe(component):
    if hasattr(component, "_prop_names") and "id" in component._prop_names:
        component.id = None
    if isinstance(component, html.Button):
        component.disabled = True
    children = getattr(component, "children", None)
    for child in children if isinstance(children, (list, tuple)) else [children]:
        if child is not None:
            _print_safe(child)
    return component
