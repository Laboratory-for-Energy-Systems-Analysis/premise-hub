"""Adapt the long deck's vector matrix and routing artwork for the short talk."""

from pathlib import Path
import re

APP = Path(__file__).resolve().parents[1]
SOURCE = APP.parent / "lca_time/assets/premise-trails-handoff.svg"


def build():
    source = SOURCE.read_text()
    defs = source.split("<defs>", 1)[1].split("</defs>", 1)[0]
    cube = source.split("<!-- 3D technosphere block: activity × product × year -->", 1)[
        1
    ].split('<text x="785.5"', 1)[0]
    matrix_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 215" role="img" aria-labelledby="title desc">
  <title id="title">Annual technosphere and biosphere matrix stacks</title>
  <desc id="desc">A has activity, product and year dimensions. B has activity, elementary flow and year dimensions. Each slice represents a calendar year's background.</desc>
  <!-- Cube geometry reused from lca_time/assets/premise-trails-handoff.svg. -->
  <defs>{defs}</defs>
  <style>text {{font-family:Arial,Helvetica,sans-serif; fill:#0b3b52}} .name {{font-size:20px;font-weight:700}} .dimension {{font-size:15px;fill:#536c76}}</style>
  <text x="135" y="25" text-anchor="middle" class="name">Technosphere A</text>
  <text x="405" y="25" text-anchor="middle" class="name">Biosphere B</text>
  <g transform="translate(40 65) scale(1.55) translate(-742 -83)">{cube}</g>
  <g transform="translate(310 65) scale(1.55) translate(-742 -83)">{cube}</g>
  <text x="223" y="63" text-anchor="middle" class="dimension">year ↗</text>
  <text x="493" y="63" text-anchor="middle" class="dimension">year ↗</text>
  <text x="135" y="185" text-anchor="middle" class="dimension">activity × product × year</text>
  <text x="405" y="185" text-anchor="middle" class="dimension">activity × flow × year</text>
</svg>"""
    network = source.split('<rect x="580" y="208"', 1)[1].split(
        '<rect x="999" y="308"', 1
    )[0]
    network = '<rect x="580" y="208"' + network
    # Make the graph's depth labels readable at half-slide width. The graph
    # remains the original schematic; these are not new case-study results.
    network = network.replace('x="590"', 'x="570"')
    network = re.sub(r">d([0-3])</text>", r">\1</text>", network)
    network = network.replace('class="label">stopped', 'class="stop">stop')
    routing_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="555 183 580 180" role="img" aria-labelledby="title desc">
  <title id="title">Temporal routing through an activity-year supply graph</title>
  <desc id="desc">Supply-chain depth runs downward and calendar year runs to the right. Exchanges connect activities in different years. Stopped branches remain demands for annual background solves.</desc>
  <!-- Network reused from lca_time/assets/premise-trails-handoff.svg. -->
  <style>text {{font-family:Arial,Helvetica,sans-serif;fill:#536c76}} .label {{font-size:12px;font-weight:700}} .micro {{font-size:11px}} .stop {{font-size:11px;font-weight:700}}</style>
  <text x="570" y="195" font-size="12">depth ↓</text>
  <text x="1120" y="195" text-anchor="end" font-size="12">calendar year →</text>
  {network}
</svg>"""
    for name, content in (
        ("trails-annual-matrices.svg", matrix_svg),
        ("trails-temporal-routing.svg", routing_svg),
    ):
        (APP / "assets" / name).write_text(
            "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
        )


if __name__ == "__main__":
    build()
