"""Audience labels for the unchanged REMIND-EU pathways used in this lecture."""

from copy import deepcopy

import plotly.graph_objects as go
from dash import dcc

LABELS = {"SSP2-NPi": "~2.6 °C in 2100", "SSP2-PkBudg1000": "<2 °C in 2100"}
# Stored World/GMST MAGICC7 medians in scenario_context.csv, relative to 1850–1900:
# NPi: 2.56888559381881 °C; PkBudg1000: 1.75596596598054 °C in 2100.


def warming_text(value):
    if not isinstance(value, str):
        return value
    for pathway, label in LABELS.items():
        value = value.replace(pathway, label).replace(pathway.removeprefix("SSP2-"), label)
    return value


def _display_values(value):
    if isinstance(value, (list, tuple)):
        return [_display_values(item) for item in value]
    return warming_text(value)


def warming_figure(figure):
    """Relabel presentation fields; retain numeric arrays and source metadata."""
    data = deepcopy(figure.to_plotly_json() if hasattr(figure, "to_plotly_json") else figure)
    for trace in data.get("data", []):
        for prop in ("name", "text", "hovertext", "hovertemplate", "x", "customdata"):
            if prop in trace:
                trace[prop] = _display_values(trace[prop])
    layout = data.get("layout", {})
    for annotation in layout.get("annotations", []):
        annotation["text"] = warming_text(annotation.get("text", ""))
    for name, axis in layout.items():
        if name.startswith(("xaxis", "yaxis")) and isinstance(axis, dict):
            if "ticktext" in axis:
                axis["ticktext"] = _display_values(axis["ticktext"])
            if isinstance(axis.get("title"), dict) and "text" in axis["title"]:
                axis["title"]["text"] = warming_text(axis["title"]["text"])
    if isinstance(layout.get("title"), dict) and "text" in layout["title"]:
        layout["title"]["text"] = warming_text(layout["title"]["text"])
    return go.Figure(data)


def warming_labels(component):
    """Relabel Seoul audience content without changing form values or link targets."""
    if component is None or isinstance(component, (str, int, float)):
        return warming_text(component)
    if isinstance(component, dcc.Graph):
        component.figure = warming_figure(component.figure)
    options = getattr(component, "options", None)
    if isinstance(options, list):
        component.options = [
            {**option, "label": warming_labels(option["label"])}
            if isinstance(option, dict) and "label" in option else option
            for option in options
        ]
    if hasattr(component, "children"):
        original = component.children
        component.children = ([warming_labels(child) for child in original]
                              if isinstance(original, (list, tuple)) else warming_labels(original))
    return component
