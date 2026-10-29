"""Keep explanatory footer prose in presenter notes, not audience slides."""

from dash import html

FOOTER_CLASSES = {
    "source",
    "evidence-note",
    "panel-note",
    "panel-reading",
    "pathway-source",
    "ledger-footer",
    "lens-footer",
    "metric-reporting",
    "metric-example",
    "timing-control-caption",
}


def children(component):
    value = getattr(component, "children", None)
    return value if isinstance(value, (list, tuple)) else [value]


def references(component):
    if isinstance(component, html.A):
        yield component
        return
    for child in children(component):
        if child is not None and not isinstance(child, (str, int, float)):
            yield from references(child)


def plain_text(component, skip_links=False):
    if component is None:
        return ""
    if isinstance(component, (str, int, float)):
        return str(component)
    if skip_links and isinstance(component, html.A):
        return ""
    return " ".join(t for c in children(component) if (t := plain_text(c, skip_links)))


def footer_context(component):
    classes = set((getattr(component, "className", "") or "").split())
    if classes & FOOTER_CLASSES:
        value = plain_text(component, skip_links=True).strip(" ·\n")
        if value:
            yield value
        return
    for child in children(component):
        if child is not None and not isinstance(child, (str, int, float)):
            yield from footer_context(child)


def clean_audience_footer(component):
    if component is None or isinstance(component, (str, int, float)):
        return component
    classes = set((getattr(component, "className", "") or "").split())
    if classes & FOOTER_CLASSES:
        links = list(references(component))
        if links:
            component.children = [
                item
                for i, link in enumerate(links)
                for item in ([" · ", link] if i else [link])
            ]
            component.className = "slide-references"
            return component
        if getattr(component, "id", None):
            # The reused scenario callback still writes to this output. Keep its
            # target mounted while suppressing its explanatory caption.
            component.children = ""
            component.className = "callback-note"
            component.style = {
                **(getattr(component, "style", None) or {}),
                "display": "none",
            }
            return component
        return None
    if hasattr(component, "children"):
        original = getattr(component, "children")
        cleaned = [
            v
            for child in children(component)
            if (v := clean_audience_footer(child)) is not None
        ]
        component.children = (
            cleaned
            if isinstance(original, (list, tuple))
            else (cleaned[0] if cleaned else None)
        )
    return component
