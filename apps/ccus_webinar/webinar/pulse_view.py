"""Two linked views of precomputed FaIR outputs, following lca_time slide 20."""
from dash import html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .model import SYSTEMS

COLORS = {'BAU': '#b85f43', 'CCS': '#397b9e', 'CCUS': '#3e7654'}


def endpoint_cards(figure):
    meta = figure.layout.meta or {}
    values = {r['system']: r for r in meta.get('readouts', [])}
    return [html.Div([
        html.Small('BAU / reference' if system == 'BAU' else system),
        html.Strong(f"{values[system]['y'][-1]:,.0f}" if system in values else 'Pending'),
        html.Span(values[system]['unit'] if system in values else 'Recalculation in progress'),
    ], className='pulse-endpoint', style={'borderLeftColor': COLORS[system]}) for system in SYSTEMS]


def pulse_selection(selection):
    try:
        if len(selection) != 3:
            raise ValueError('Three dates required')
        values = [int(round(float(v)/5)*5) for v in selection]
        start = max(1995, min(2190, values[0]))
        reference = max(start+5, min(2195, values[1]))
        end = max(reference+5, min(2200, values[2]))
        return start, reference, end
    except (TypeError, ValueError, OverflowError):
        return 2025, 2035, 2100


def pulse_figure(metric, normalization, start, end, uncertainty, bundle, reference_year=2035):
    from .figures import _normalization_factor, status_figure
    rows = bundle.tables.get('pulse_equivalence', ())
    rows = [r for r in rows if int(r.get('reference_year',2035)) == reference_year
            and int(r['window_start']) == start]
    if not rows:
        figure = status_figure(bundle, f'Results for a {reference_year} reference pulse and a window starting in {start} are not yet available.', 470)
        figure.update_layout(meta={'readouts':[], 'window':[start,end], 'reference_year':reference_year})
        return figure
    factor = _normalization_factor(normalization)
    temperature = metric == 'temperature'
    response_metric = 'temperature' if temperature else 'radiative_forcing'
    equivalent_metric = 'integrated_temperature' if temperature else 'integrated_rf'
    scale = 1e9 if temperature else 1e12
    unit = ('n°C' if temperature else 'pW/m²') + ('/t' if normalization == 'per_tonne' else ' · campaign')
    pulse_unit = 'kg CO₂ pulse-eq/t' if normalization == 'per_tonne' else 'kg CO₂ pulse-eq · campaign'
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=.19,
                        subplot_titles=('Temperature response' if temperature else 'Radiative forcing',
                                        'Equivalent pulse at the reference year, by window end'))
    readouts = []
    for system in SYSTEMS:
        color = COLORS[system]
        for panel, source, key, xkey, multiplier in (
            (1, bundle.tables.get('fair_responses', ()), response_metric, 'year', factor*scale),
            (2, rows, equivalent_metric, 'window_end', factor),
        ):
            aliases = {key, 'radiative forcing' if key == 'radiative_forcing' else 'temperature change' if key == 'temperature' else key}
            selected = [r for r in source if r['system'] == system and r['metric'] in aliases
                        and r.get('pathway', 'SSP2-PkBudg1000') == 'SSP2-PkBudg1000'
                        and (panel == 1 or int(r['window_start']) == start)]
            def series(q):
                return sorted((r for r in selected if r['statistic'] in ({'q50','median'} if q == 'q50' else {q})), key=lambda r: float(r[xkey]))
            median = series('q50')
            if not median:
                continue
            x = [float(r[xkey]) for r in median]
            y = [float(r['value'])*multiplier for r in median]
            if uncertainty and panel == 1:
                for q, fill in [('q2.5', None), ('q97.5', 'tonexty')]:
                    band = series(q)
                    fig.add_trace(go.Scatter(x=[float(r[xkey]) for r in band],
                        y=[float(r['value'])*multiplier for r in band], mode='lines',
                        line={'width': 0}, fill=fill, fillcolor='rgba(90,110,125,.12)',
                        legendgroup=system, showlegend=False, hoverinfo='skip', name='FaIR ensemble'), row=panel, col=1)
            if panel == 2:
                errors = None
                if uncertainty:
                    lower = {float(r[xkey]):float(r['value'])*multiplier for r in series('q2.5')}
                    upper = {float(r[xkey]):float(r['value'])*multiplier for r in series('q97.5')}
                    errors = dict(type='data', symmetric=False,
                        array=[upper[t]-v for t,v in zip(x,y)],
                        arrayminus=[v-lower[t] for t,v in zip(x,y)],
                        color=color, thickness=1, width=2)
                fig.add_trace(go.Bar(x=x, y=y, name='CO₂-pulse equivalent',
                    legendgroup=system, offsetgroup=system, showlegend=False,
                    marker={'color':color, 'opacity':[1 if t == end else .65 for t in x],
                            'line':{'color':color,'width':[1.5 if t == end else 0 for t in x]}},
                    error_y=errors,
                    hovertemplate=system+f'<br>Equivalent pulse in {reference_year}'
                        +f'<br>Integration window: {start}–'+'%{x:.0f}'
                        +'<br>%{y:,.0f} '+pulse_unit+'<extra></extra>'), row=2, col=1)
            else:
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=system if panel == 1 else 'CO₂-pulse equivalent',
                legendgroup=system, showlegend=panel == 1, line={'color': color, 'width': 2.8},
                fill='tozeroy' if panel == 1 else None,
                fillcolor={'BAU':'rgba(184,95,67,.10)','CCS':'rgba(57,123,158,.14)','CCUS':'rgba(62,118,84,.14)'}[system],
                hovertemplate=system+'<br>'+('Year' if panel == 1 else 'Window closes')+
                    ' %{x}<br>%{y:,.3f} '+unit+'<extra></extra>' if panel == 1 else
                    system+'<br>Window closes %{x}<br>%{y:,.0f} '+pulse_unit+'<extra></extra>'), row=panel, col=1)
            if panel == 2:
                chosen = next((v for t,v in zip(x,y) if t == end), None)
                if chosen is not None:
                    readouts.append({'system':system,'y':[chosen],'unit':pulse_unit})
    reference = [r for r in bundle.tables.get('pulse_reference', ()) if r['metric'] == response_metric
                 and int(r.get('reference_year',2035)) == reference_year]
    if reference:
        fig.add_trace(go.Scatter(x=[r['year'] for r in reference],
            y=[r['value']*scale*factor for r in reference], name=f'+1 t CO₂ pulse · {reference_year}',
            mode='lines', line={'color':'#d18a12','dash':'dash','width':2},
            hovertemplate='Reference +1 t CO₂ · %{x}<br>%{y:.3f} '+unit+'<extra></extra>'),row=1,col=1)
    for panel in (1,2):
        fig.add_vrect(x0=start,x1=end,fillcolor='rgba(57,123,158,.08)',line_width=0,layer='below',row=panel,col=1)
        fig.add_vline(x=end,line={'color':'#536a73','dash':'dot','width':1.5},row=panel,col=1)
        fig.add_vline(x=reference_year,line={'color':'#d18a12','dash':'dash','width':1},row=panel,col=1)
        fig.add_hline(y=0,line={'color':'#738994','width':1},row=panel,col=1)
    fig.update_xaxes(range=[min(2000,start),2203],dtick=50,gridcolor='#dce5e8',showticklabels=True)
    fig.update_xaxes(title_text='Comparison window end year',row=2,col=1)
    fig.update_yaxes(title_text=unit,gridcolor='#dce5e8',zeroline=False,row=1,col=1)
    fig.update_yaxes(title_text=pulse_unit,gridcolor='#dce5e8',zeroline=False,row=2,col=1)
    for annotation in fig.layout.annotations:
        annotation.update(x=0,xanchor='left',font={'size':13,'color':'#17313b'})
    fig.update_layout(autosize=True,margin={'l':85,'r':20,'t':48,'b':45},paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#f2f6f7',font={'family':'Arial','size':11,'color':'#17313b'},hovermode='x unified',
        barmode='group', bargap=.25, bargroupgap=.08,
        legend={'orientation':'h','x':.4,'y':1.15,'font':{'size':11}},
        meta={'readouts':readouts,'window':[start,end],'reference_year':reference_year},
        uirevision=f'pulse-{metric}-{normalization}-{start}-{reference_year}-{end}-{uncertainty}')
    return fig
