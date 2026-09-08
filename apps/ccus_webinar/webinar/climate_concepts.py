"""Clearly labelled teaching schematics, never substituted for calculated results."""
import math
from dash import html
from .diagrams import _text, _icon, _arrow


def _axes(x, width, unit):
    body = f'<path d="M{x} 140V325H{x+width}" fill="none" stroke="#94a8b1" stroke-width="1.5"/>'
    body += _text(x, 130, unit, 'note')
    for year in (2025, 2035, 2065, 2100):
        px = x + (year-2025)/75*width
        body += f'<path d="M{px} 325v6" stroke="#94a8b1"/>'
        body += _text(px, 353, str(year), 'note', 'middle')
    return body


def _curve(x, width, values, color, fill=False):
    coords = [(x+i/(len(values)-1)*width, 325-v) for i,v in enumerate(values)]
    path = 'M' + 'L'.join(f'{a:.2f},{b:.2f}' for a,b in coords)
    body = ''
    if fill:
        body += f'<path d="{path}L{x+width},325H{x}Z" fill="{color}" opacity=".14"/>'
    return body + f'<path d="{path}" fill="none" stroke="{color}" stroke-width="4"/>'


def climate_concept(stage):
    from .editorial import artwork
    b = ''
    if stage == 'fair':
        cards = [('01','Record when emissions occur','atmosphere','kg of each greenhouse gas'),
                 ('02','Calculate the forcing','response','W/m² · change in Earth’s energy balance'),
                 ('03','Follow the temperature','globe','°C · surface warming')]
        for i,(number,title,icon,unit) in enumerate(cards):
            x = 25+i*465
            b += f'<rect x="{x}" y="12" width="435" height="397" rx="16" fill="#f3f7f8"/>'
            b += _icon(icon,x+20,27,48,'time')
            b += _text(x+82,48,number,'note')+_text(x+82,78,title,'title')
            b += _axes(x+45,345,unit)
            if i == 0:
                px = x+45+345*10/75
                b += _arrow(f'M{px} 325V180','carbon')
                b += _text(x+142,189,'One CO₂ pulse in 2035','label')
                b += _text(x+142,216,'shown for clarity','note')
                note='The inventory records amounts, gases and dates.'
            else:
                vals=[]
                for year in range(2025,2101):
                    dt=year-2035
                    val=0 if dt<0 else (130*(.25+.75*math.exp(-dt/35)) if i==1 else 140*(1-math.exp(-dt/15))*(.7+.3*math.exp(-dt/90)))
                    vals.append(val)
                b += _curve(x+45,345,vals,'#397b9e' if i==1 else '#c44e52',True)
                b += _text(x+125,175,'Forcing persists after the emission' if i==1 else 'Warming builds with a delay','note')
                note='How long gases remain affects the forcing.' if i==1 else 'Ocean heat uptake delays the response.'
            b += _text(x+218,388,note,'note','middle')
            if i<2:
                b += _arrow(f'M{x+438} 227h23','time')
        return artwork(b,'Illustration: a dated CO₂ pulse causes forcing, followed by delayed warming',460)

    # Normalize the illustrative reference curve to exactly the same trapezoid area.
    years=list(range(2025,2101))
    system=[0 if y<2035 else 100*(1-math.exp(-(y-2035)/12))*math.exp(-(y-2035)/95) for y in years]
    reference=[0 if y<2035 else .3+.7*math.exp(-(y-2035)/35) for y in years]
    integral=lambda vals: sum((a+b)/2 for a,b in zip(vals,vals[1:]))
    ratio=integral(system)/integral(reference)
    reference=[v*ratio for v in reference]
    for i,(title,values,color) in enumerate([
        ('The system’s climate effect changes over time',system,'#397b9e'),
        ('One CO₂ pulse produces the same total effect',reference,'#7656a8')]):
        x=30+i*710
        b += f'<rect x="{x}" y="12" width="650" height="394" rx="16" fill="#f3f7f8"/>'
        b += _icon('response' if i==0 else 'pulse',x+22,26,49,'carbon' if i==0 else 'time')
        b += _text(x+88,61,title,'title')
        b += f'<rect x="{x+60}" y="144" width="530" height="181" fill="{color}" opacity=".045"/>'
        b += _axes(x+60,530,'Radiative forcing · illustrative scale')
        b += _curve(x+60,530,values,color,True)
        pulse_x=x+60+530*10/75
        b += f'<path d="M{pulse_x} 148V325" stroke="#d18a12" stroke-dasharray="5 5"/>'
        b += _text(x+320,174,'A · system response' if i==0 else 'B · reference response × scale','label','middle')
        b += _text(x+325,387,'Same window: 2025–2100' if i==0 else 'Pulse in 2035 · find the equivalent CO₂ mass','note','middle')
    b += _text(700,260,'=','title','middle')
    b += _text(700,443,'Illustration: equal integrated response over 2025–2100, not equal curves or values in 2100.','label','middle')
    fraction = html.Span([
        html.Span(['∫',html.Sub('t₀'),html.Sup('t₁'),' ΔX',html.Sub('system'),'(t) dt']),
        html.Span(['∫',html.Sub('t₀'),html.Sup('t₁'),' ΔX',html.Sub('reference'),'(t) dt']),
    ],className='response-fraction')
    formula=html.Div([
        html.Div([html.Span(['m',html.Sub('CO₂-eq'),' = m',html.Sub('reference'),' × ']),fraction],className='response-equation'),
        html.Div(['ΔX = forcing or temperature',html.Br(),
                  'Use the same years and climate-model parameters for both curves.',html.Br(),
                  'Areas below zero count negatively. A negative total gives a negative equivalent mass.'],className='pulse-formula-notes'),
    ],className='pulse-formula')
    return html.Div([artwork(b,'Equal integrated climate response for the system and a scaled reference pulse',460),formula],className='climate-concept')
