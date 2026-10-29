"""Discussion bridge from dated GWP contributions to climate response."""

from math import exp

from dash import html

from .visuals import label, svg_uri


def hint_diagram(kind):
    """Timelines for emission dates, removal, gas persistence and backgrounds."""
    width, height = 420, 160
    colour, muted = "#173747", "#527780"
    early, late, endpoint = "#be861c", "#3292b5", "#b55044"
    b = '<rect width="420" height="160" fill="#f1f7f8"/>'

    def axis(left, right, y, ticks):
        s = f'<path d="M{left} {y}H{right}" fill="none" stroke="#7a929e" stroke-width="1.5"/>'
        for px, text in ticks:
            s += f'<path d="M{px} {y-3}v7" stroke="#7a929e"/>'
            s += label(px, y+22, text, 17, endpoint if text == "2100" else muted,
                       "end" if px == right else "middle")
        return s

    def pulse(x, y, tip, stroke):
        direction = 1 if tip < y else -1
        return (f'<path d="M{x} {y}V{tip}m-6 {direction*7} 6 {-direction*7} 6 {direction*7}" '
                f'fill="none" stroke="{stroke}" stroke-width="3" stroke-linejoin="round"/>')

    if kind == "dated":
        def x(year):
            return 66 + (year-2030)*2.2
        b += label(220,20,"Each +1 t CO₂ → +1,000 kg CO₂-eq",18,colour)
        b += f'<rect x="66" y="35" width="{x(2100)-66}" height="91" rx="5" fill="#deece6"/>'
        for year,y,stroke in ((2030,50,early),(2080,93,late)):
            b += label(42,y+19,str(year),17,muted,"end")
            b += f'<rect x="{x(year)}" y="{y}" width="220" height="22" rx="5" fill="{stroke}" opacity=".18"/>'
            b += label(x(year)+110,y+17,"100-year window",17,colour)
            b += label(x(year+100),y-6,str(year+100),16,muted)
            b += pulse(x(year),y+22,y-11,stroke)
        b += f'<path d="M{x(2100)} 33V126" stroke="{endpoint}" stroke-width="2" stroke-dasharray="4 4"/>'
        b += label(x(2100),33,"Target",14,endpoint)
        b += axis(66,396,133,((66,"2030"),(x(2100),"2100"),(396,"2180")))
        alt = ("Two alternative positive one-tonne CO2 pulses, in 2030 or 2080. Each scores "
               "+1,000 kg CO2-eq under fixed GWP100, but the accounting windows are 2030 to "
               "2130 and 2080 to 2180. The green 2030 to 2100 calendar period and red 2100 "
               "target contrast with those moving windows. Do equal scores describe effects "
               "before that common endpoint? Arrows are emissions; bars are accounting horizons, not lifetimes.")
    elif kind == "removal":
        b += label(16,20,"t CO₂",16,muted,"start")
        b += label(226, 20, "Both total 0 kg CO₂-eq", 20, colour)
        for y, name in ((60,"Now"),(108,"Later")):
            b += label(16,y+6,name,18,muted,"start")
            b += f'<path d="M92 {y}H386" stroke="#b8ccd5" stroke-width="1.3"/>'
        b += '<rect x="104" y="94" width="238" height="26" rx="4" fill="#f0dfb8"/>'
        b += label(220,113,"50-year gap",18,"#906313")
        b += pulse(97,60,33,early) + pulse(111,60,84,late)
        b += label(76,36,"+1",16,early) + label(133,82,"−1",16,late)
        b += pulse(104,108,81,early) + pulse(342,108,132,late)
        b += label(80,89,"+1",16,early) + label(365,129,"−1",16,late)
        b += axis(92,386,136,((104,"2030"),(342,"2080")))
        alt = ("Alternative CO2 pulse pairs in tonnes: +1 and minus 1 in 2030, or +1 in "
               "2030 and minus 1 in 2080. Both aggregate to zero kg CO2-eq with fixed CO2 "
               "GWP100 factors. The shaded fifty-year gap shows delayed removal, not a "
               "calculated forcing or temperature effect. Does the equal total hide climate history?")
    elif kind == "gases":
        # Illustrative shapes normalized to equal 0–100-year forcing areas.
        # These are not fitted gas impulse responses or temperature curves.
        def co2(t):
            return .28 + .30*exp(-t/45) + .42*exp(-t/4)
        def ch4(t):
            return exp(-t/12)
        co2_area = .28*100 + .30*45*(1-exp(-100/45)) + .42*4*(1-exp(-100/4))
        ch4_scale = co2_area / (12*(1-exp(-100/12)))
        def x(t):
            return 50 + t*348/150
        def path(points):
            return "M" + " L".join(f"{px:.2f} {py:.2f}" for px,py in points)
        b += label(226,20,"Same GWP100 · different pulse masses",17,colour)
        b += '<text x="17" y="79" transform="rotate(-90 17 79)" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#527780">Forcing · schematic</text>'
        b += f'<rect x="50" y="33" width="{x(100)-50}" height="93" fill="#e5eff2"/>'
        b += '<path d="M50 33V126" stroke="#7a929e" stroke-width="1.5"/>'
        for f,scale,stroke in ((co2,1,late),(ch4,ch4_scale,early)):
            points = [(x(t),126-22*scale*f(t)) for t in range(151)]
            b += f'<path d="{path(points[:101])} L{x(100)} 126H50Z" fill="{stroke}" opacity=".2"/>'
            b += f'<path d="{path(points)}" fill="none" stroke="{stroke}" stroke-width="2.8"/>'
        b += f'<path d="M{x(100)} 33V126" stroke="#a4b9c2" stroke-dasharray="4 4"/>'
        b += label(x(100),44,"100 y",15,muted)
        b += label(84,77,"CH₄",19,early)
        b += label(225,108,"CO₂",19,late)
        b += axis(50,398,126,((50,"2030"),(x(50),"2080"),(x(100),"2130"),(398,"2180")))
        alt = ("Two simultaneous gas pulses in 2030, scaled to the same GWP100 score, "
               "not equal emitted masses. Illustrative methane-like and CO2-like forcing "
               "curves have equal shaded areas over 2030 to 2130 but different time profiles: "
               "a stronger early methane effect fades, while CO2 leaves a persistent tail. "
               "Curves are schematic, not calibrated gas impulse responses, temperature "
               "trajectories or technology results. What timing information does equal CO2-eq hide?")
    elif kind == "background":
        b += label(220,20,"Concentrations · indexed, schematic",17,colour)
        b += '<path d="M62 91H348M62 34V91" stroke="#b8ccd5" fill="none"/>'
        for d, stroke, gas, y in (
            ("M62 66C140 64 217 38 338 38", "#7656a8", "CO₂", 43),
            ("M62 66C164 65 225 74 338 84", early, "CH₄", 89),
            ("M62 66C160 65 244 55 338 54", late, "N₂O", 62),
        ):
            b += f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="2.8"/>'
            b += label(355,y,gas,18,stroke,"start")
        b += '<path d="M62 120H338" stroke="#b55044" stroke-width="2.5" stroke-dasharray="6 4"/>'
        b += label(220,113,"Fixed CH₄ / N₂O GWP100?",18,endpoint)
        b += axis(62,398,136,((62,"2030"),(338,"2080")))
        alt = ("Schematic changes in background CO2, methane and nitrous oxide concentrations "
               "between 2030 and 2080 contrast with a flat line for fixed methane and nitrous "
               "oxide GWP100 factors. Curves are illustrative normalized paths, not forecasts "
               "or concentrations on a common physical scale. Background concentrations affect "
               "marginal radiative efficiencies, including the CO2 reference; lifetimes and "
               "carbon-cycle feedbacks may also change. Can fixed-reference factors describe "
               "a scenario-specific evolving atmosphere? No direction or size of GWP change is implied.")
    else:
        raise ValueError(f"Unknown discussion diagram: {kind}")
    return svg_uri(b,width,height,alt), alt


def discussion(print_mode=False):
    hints = (
        ("01", "Same score, different assessment window?", "dated"),
        ("02", "Zero total, same climate history?", "removal"),
        ("03", "Same CO₂-eq, different persistence?", "gases"),
        ("04", "Same factors in a changing atmosphere?", "background"),
    )
    def card(number, question, kind):
        src, alt = hint_diagram(kind)
        return html.Div([
            html.H3([html.Span(number), html.Strong(question)]),
            html.Img(src=src, alt=alt, className="gwp-hint-timeline"),
        ], className="gwp-pause-hint")

    return html.Div([
        html.Div([
            html.Span("THINK · COMPARE · DISCUSS",className="discussion-label"),
            html.Div([
                html.A("IPCC AR6 §7.6",href="https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/#7.6",target="_blank",rel="noopener"),
                html.A("Levasseur et al. (2010)",href="https://doi.org/10.1021/es9030003",target="_blank",rel="noopener"),
                html.A("Reisinger et al. (2011)",href="https://doi.org/10.1088/1748-9326/6/2/024020",target="_blank",rel="noopener"),
            ],className="gwp-pause-references"),
        ],className="gwp-pause-heading"),
        html.Div("Do dated GWP100 scores answer our climate question?",className="gwp-pause-question"),
        html.Div([
            card(number,question,kind)
            for number,question,kind in hints
        ],className="gwp-pause-hints"),
    ],className="gwp-pause")
