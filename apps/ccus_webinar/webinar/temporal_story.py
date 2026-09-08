"""Visual timing narrative. No changes to inventories or temporal assumptions."""
import json
import hashlib
from pathlib import Path
from dash import dcc, html
import plotly.graph_objects as go
from .editorial import artwork
from .diagrams import _icon, _text, _arrow, _svg
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def candidate_profiles():
    path=ROOT/'data/public/uptake_profiles.json'
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != path.with_suffix('.sha256').read_text().strip():
        raise ValueError('Candidate uptake artifact changed')
    candidate=json.loads(raw)
    return candidate['profiles']


def timeline_art():
    x = lambda year: 320 + (year-2035)/30*890
    b = ''
    for i, (system, description) in enumerate((('BAU', 'Keep the existing kiln'),
        ('CCS', 'Capture and store both carbon origins'), ('CCUS', 'Store fossil carbon. Reuse non-fossil carbon.'))):
        y = 64+i*85
        b += f'<rect x="0" y="{y}" width="1400" height="77" rx="12" fill="{["#f3f6f7","#eef5f8","#edf6f2"][i]}"/>'
        b += _icon('kiln', 12, y+16, 46)
        b += _text(65, y+40, system, 'node-title')
        b += _icon('atmosphere', 151, y+2, 33, 'bio')
        b += _arrow(f'M168 {y+30}v24H292L320 {y+41}', 'bio')
        b += _text(226, y+46, 'Uptake', 'note', 'middle')
    b += '<rect x="314" y="54" width="12" height="257" rx="6" fill="#d6a742" fill-opacity=".2"/>'
    b += _text(320, 18, '2035', 'node-title', 'middle')
    b += _text(320, 40, 'Investment starts', 'note', 'middle')
    b += _text(205, 18, 'From the atmosphere', 'note', 'middle')
    b += _text(205, 40, 'Before fuel use', 'note', 'middle')
    b += _text(760, 18, '30 operating years · same clinker demand', 'node-title', 'middle')
    for year in (2040,2045,2050,2055,2060,2065):
        b += _text(x(year), 40, str(year), 'note', 'middle')
        b += f'<path d="M{x(year)} 57V308" stroke="#b9ccd1" stroke-dasharray="2 6" opacity=".6"/>'
    for i in range(3):
        y = 105+i*85
        b += f'<path d="M{x(2035)} {y}H{x(2064)}" stroke="#008a82" stroke-width="6"/>'
        for year in range(2035,2065):
            b += f'<circle cx="{x(year)}" cy="{y}" r="3.5" fill="#008a82"/>'
        if i:
            b += f'<path d="M320 {y-11}l11 11-11 11-11-11Z" fill="#d6a742"/>'
            b += _icon('capture', 340, y-32, 31)
            b += _arrow(f'M{x(2035)} {y}v19H1340', 'storage')
            b += _icon('storage', 1344, y-1, 38, 'storage')
            b += _text(930, y+15, 'Fossil + non-fossil CO₂' if i == 1 else 'Fossil CO₂', 'note', 'middle')
            b += _text(1278, y+12, 'Permanent', 'note', 'middle')
            for year in (2045,2055):
                b += _arrow(f'M{x(year)} {y}v-23', 'fossil')
            if i == 1:
                b += _text(840, y-24, 'To air: uncaptured CO₂ + storage-chain losses', 'note', 'middle')
        else:
            for year in (2040,2050,2060):
                b += _arrow(f'M{x(year)} {y}v-23', 'fossil')
            b += _text(930, y-21, 'Kiln CO₂ to air', 'note', 'middle')
            b += _icon('atmosphere', 1290, y-27, 45, 'fossil')
        if i == 2:
            # Extra CCUS equipment fits above the timeline, beside capture.
            b += '<g><title>Additional CCUS activities: hydrogen production, methanol synthesis and conversion to fuels</title>'
            for kind, left in (('hydrogen', 380), ('methanol', 414), ('jet', 448)):
                b += _icon(kind, left, y-32, 31, 'bio')
            b += _text(490, y-24, 'H₂ · methanol · fuels', 'note')
            b += '</g>'
            for year in (2045,2055):
                b += f'<circle cx="{x(year)}" cy="{y}" r="7" fill="white" stroke="#d6a742" stroke-width="3"/>'
            b += _text(800, y-24, 'Uncaptured CO₂ + residuals + losses', 'note', 'middle')
            b += _text(1040, y-24, 'Fuel CO₂ to air (+1 yr)', 'note', 'middle')
            b += _arrow(f'M{x(2060)} {y}v-20', 'bio')
    b += _text(320, 330, '◆ Initial equipment', 'note')
    b += _text(600, 330, '○ Electrolyser stack replacement (10 yr)', 'note')
    b += _text(975, 330, '● Annual operation · 2035–2064', 'note')
    return artwork(b, 'Three investment timelines. BAU emits kiln carbon to air. CCS stores fossil and non-fossil carbon. CCUS stores fossil carbon and converts non-fossil carbon to fuels used one year later. Investment starts in 2035.', height=345)


def uptake_figure():
    profiles = candidate_profiles()
    low=2035+min(min(p['offsets']) for p in profiles)-1
    years = list(range(low,2036))
    fig = go.Figure()
    colors = ['#397fa5','#956ab1','#cf7651','#bd9b2f','#378f85','#729b52']
    labels = ['RDF','Paper sludge','Sewage sludge','Meat & bone meal','Wood board','Wood chips']
    totals = {}
    for p,color,label in zip(profiles,colors,labels):
        if p['fuel'] == 'wood chips':
            continue  # Wood-chip uptake and dates are retained in its supplier.
        weights = dict(zip(p['offsets'],p['weights']))
        lhv = p['lhv_mj_per_kg']
        total = 1000/lhv*p['kg_co2_per_kg_fuel']*p['biogenic_fraction']
        totals[p['fuel']] = total
        values = [-total*weights.get(y-2035,0) for y in years]
        fig.add_trace(go.Scatter(x=years,y=values,name=label,mode='lines',fill='tozeroy',
            line=dict(color=color,width=2,shape='hv'),fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},.08)',
            customdata=[total]*len(years),
            hovertemplate='<b>%{fullData.name}</b><br>%{x}: %{y:.2f} kg CO₂/GJ<br>Total uptake: %{customdata:.2f} kg CO₂/GJ<extra></extra>'))
    fig.add_vline(x=2035,line_color='#164f61',line_width=2)
    fig.update_layout(margin=dict(l=45,r=12,t=5,b=44),height=150,showlegend=True,
        legend=dict(orientation='h',x=0,y=-.28,font=dict(size=11),traceorder='normal'),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Arial',size=11,color='#355b6c'),
        xaxis=dict(range=[1995,2036],tickvals=[1995,2005,2015,2025,2035],fixedrange=True,showgrid=False),
        yaxis=dict(title=None,rangemode='tozero',nticks=3,fixedrange=True,gridcolor='#dfe9e5',zerolinecolor='#9cb3b9'),
        meta=dict(example_year=2035,status='foreground_profiles_wood_in_background',unit='kg CO2 per GJ of individual fuel, annual uptake',totals=totals))
    return fig


def cohort_art():
    b = _text(22, 26, '2035', 'node-title') + _text(425,26,'2036','node-title')
    b += '<rect x="5" y="40" width="300" height="88" rx="12" fill="#edf4f2"/><rect x="411" y="40" width="244" height="88" rx="12" fill="#fbf2ed"/>'
    b += _icon('capture',15,52,43) + _icon('methanol',72,52,43) + _icon('jet',425,52,50)
    b += _text(132,67,'Capture + fuel production','label') + _text(132,93,'Avoided fuel credited now','note')
    b += _arrow('M312 83H398','time') + _text(355,66,'+1 year','note','middle')
    b += _text(487,70,'Fuel combustion','label') + _text(487,95,'CO₂ reaches the air','note')
    return html.Img(src='data:image/svg+xml;charset=utf-8,'+quote(_svg(b,670,163,'One CCUS cohort: production and credit in 2035, fuel combustion in 2036.')),alt='2035 production and credit, 2036 combustion',className='cohort-art')


def temporal_story():
    return html.Div([
        timeline_art(),
        html.Div([
            html.Div([
                html.Div([html.Strong('When the fuel’s non-fossil carbon was absorbed'),html.Small('2035 · kg CO₂/GJ · Wood chips use supplier timing')],className='uptake-controls'),
                dcc.Graph(id='timing-uptake-chart',figure=uptake_figure(),config={'displayModeBar':False,'responsive':True},responsive=True,style={'height':'150px'}),
                ],className='timing-uptake-panel'),
            html.Div([html.Strong('We assume synthetic fuels are burned one year after production'),cohort_art()],className='timing-cohort-panel'),
        ],className='timing-detail-grid'),
    ],className='temporal-story')
