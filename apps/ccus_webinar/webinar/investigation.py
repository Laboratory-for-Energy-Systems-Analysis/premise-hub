"""Conceptual route through the investigation, with no illustrative LCA scores."""

from urllib.parse import quote

from dash import html

from .diagrams import _icon, _svg, _text
from .overview import _icon as process_icon


def stage_artwork(stage):
    b = "<style>.year{font-size:27px;font-weight:700}.caption{font-size:16px;fill:#52727e}</style>"
    if stage in ("current", "future"):
        future = stage == "future"
        color = "#4193b8" if future else "#008a82"
        b += f'<rect x="57" y="15" width="108" height="91" rx="12" fill="white" stroke="{color}" stroke-width="2"/>'
        b += f'<path d="M57 40H165M80 6V25M142 6V25" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
        b += _text(111, 79, "2035" if future else "2025", "year", "middle")
        b += process_icon("kiln", 14, 106, 32)
        b += _icon(
            "globe" if future else "power",
            149,
            104,
            48,
            "storage" if future else "energy",
        )
        b += '<path d="M79 126H140" fill="none" stroke="#9bafb8" stroke-width="2"/>'
        b += _text(
            111,
            180,
            "Future system" if future else "Today's system",
            "caption",
            "middle",
        )
    elif stage == "dated":
        b += '<path d="M18 112H206" stroke="#a7b6bf" stroke-width="2"/>'
        for x, y, color in (
            (38, 141, "#3e7654"),
            (99, 53, "#d18a12"),
            (139, 78, "#008a82"),
            (183, 57, "#c44e52"),
        ):
            b += f'<path d="M{x} 112V{y}" stroke="{color}" stroke-width="3"/><circle cx="{x}" cy="{y}" r="7" fill="{color}"/>'
        b += _text(38, 162, "Uptake", "caption", "middle")
        b += _text(126, 32, "Production", "label", "middle")
        b += _text(190, 162, "Use", "caption", "middle")
        b += '<path d="M98 43H154" stroke="#d18a12" stroke-width="2"/>'
    elif stage == "response":
        b += _icon("globe", 71, 7, 73, "time")
        b += '<path d="M19 86V152H205" fill="none" stroke="#a7b6bf" stroke-width="2"/>'
        b += '<path d="M24 143C58 142 61 105 97 102S159 119 200 89" fill="none" stroke="#7656a8" stroke-width="4" stroke-linecap="round"/>'
        b += _text(112, 176, "Forcing / temperature", "caption", "middle")
    elif stage == "pulse":
        b += '<rect x="53" y="20" width="127" height="125" rx="8" fill="#e9e3f2"/>'
        b += '<path d="M53 18V148M180 18V148" stroke="#7656a8" stroke-width="2" stroke-dasharray="4 5"/>'
        b += '<path d="M20 140H207M84 140V48m-7 10 7-10 7 10" fill="none" stroke="#7656a8" stroke-width="3" stroke-linecap="round"/>'
        b += '<path d="M86 51Q112 112 173 122" fill="none" stroke="#008a82" stroke-width="3"/>'
        b += _text(112, 176, "Reference pulse + time window", "caption", "middle")
    else:
        raise ValueError(stage)
    return "data:image/svg+xml;charset=utf-8," + quote(
        _svg(
            b, 224, 190, f"Schematic {stage} assessment concept, not calculated results"
        )
    )


def investigation_map():
    stages = (
        ("current", "Current (static) LCA", "What are the benefits today?", "GWP100"),
        (
            "future",
            "Prospective (static) LCA",
            "Do the benefits hold in 2035?",
            "GWP100",
        ),
        (
            "dated",
            "Time-explicit LCA",
            "When do emissions occur?",
            "Annual + cumulative GWP100",
        ),
        (
            "response",
            "Climate response",
            "When do benefits appear?",
            "Radiative forcing / temperature",
        ),
        (
            "pulse",
            "CO₂-pulse equivalence",
            "How much does the time window matter?",
            "Equivalent reference pulse",
        ),
    )
    return html.Div(
        [
            html.Div(
                [
                    html.Span("THREE INVENTORY APPROACHES", className="investigation-phase-system"),
                    html.Span(
                        "THEN CALCULATE THE CLIMATE RESPONSE →",
                        className="investigation-phase-time",
                    ),
                ],
                className="investigation-phases",
            ),
            html.Div(
                [
                    html.Section(
                        [
                            html.Div(
                                [html.Small(f"0{i + 1}"), html.H2(title)],
                                className="investigation-card-heading",
                            ),
                            html.Img(
                                src=stage_artwork(key),
                                alt=f"Schematic: {question}",
                                className="investigation-art",
                            ),
                            html.Strong(question, className="investigation-prompt"),
                            html.Span(metric, className="investigation-metric"),
                        ],
                        className=f"investigation-card investigation-{key}",
                    )
                    for i, (key, title, question, metric) in enumerate(stages)
                ],
                className="investigation-cards",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Invest in carbon capture?"),
                            html.Span(
                                "Compare climate impacts with and without capture."
                            ),
                        ],
                        className="investigation-anchor-copy",
                    ),
                    *[
                        html.Div(
                            [
                                html.Img(
                                    src="data:image/svg+xml;charset=utf-8,"
                                    + quote(
                                        _svg(
                                            process_icon("kiln", 0, 10, 30)
                                            + (
                                                process_icon(kind, 70, 10, 40)
                                                if kind
                                                else ""
                                            ),
                                            114,
                                            62,
                                            f"{label} investment option",
                                        )
                                    ),
                                    alt="",
                                ),
                                html.Strong(label),
                            ],
                            className="investigation-option",
                        )
                        for label, kind in (
                            ("BAU / no investment", None),
                            ("Invest in CCS", "storage"),
                            ("Invest in CCUS", "jet"),
                        )
                    ],
                ],
                className="investigation-anchor",
            ),
        ],
        className="investigation-map",
    )
