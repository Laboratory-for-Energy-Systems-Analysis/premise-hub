"""Consistent carbon-origin cues, independent of technology and activity colours."""

from dash import html

FOSSIL = "Fossil / mineral CO₂"
NON_FOSSIL = "Non-fossil CO₂"
UPTAKE = "Atmospheric uptake"
OTHER = "Other effects"
ORIGINS = {
    FOSSIL: "#ad603d",
    NON_FOSSIL: "#3e7654",
    UPTAKE: "#008a82",
    OTHER: "#91a4ad",
}


def origin_key(combined=False, *, co2_terms=False):
    return html.Div(
        [
            html.Span(
                [
                    html.I(style={"backgroundColor": ORIGINS[FOSSIL]}),
                    "fossil CO₂" if co2_terms else "Fossil / mineral",
                ]
            ),
            html.Span(
                [
                    html.I(style={"backgroundColor": ORIGINS[NON_FOSSIL]}),
                    "non-fossil CO₂" if co2_terms else "Non-fossil",
                ]
            ),
            *(
                []
                if combined or co2_terms
                else [
                    html.Span(
                        [
                            html.I(style={"backgroundColor": ORIGINS[UPTAKE]}),
                            "Air uptake",
                        ]
                    ),
                    html.Span(
                        [
                            html.I(style={"backgroundColor": ORIGINS[OTHER]}),
                            "Other effects",
                        ],
                        title="Other greenhouse gases and effects without an origin split",
                    ),
                ]
            ),
            html.B("Combined response") if combined else None,
        ],
        className="cement-origin-key",
        **{"aria-label": "Cement carbon origins"},
    )
