"""Four fixed cases, with explicit native services and source contracts.

Panels compare changes within cases. Cement's intervention is CCS minus BAU
for equal clinker output, normalized to one tonne physically stored. Source assumptions are not
silently harmonized and no cross-technology ranking is inferred.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from dash import dcc, html
from apps.setac_2026 import results
from apps.setac_2026.figures import static_score
from apps.ccus_webinar.webinar.release import load_release_bundle
from .visuals import CASES, CASE
from .erw import campaign_profile
from .erw_campaign import campaign_results
from .carbon import origin_key
from .cement_basis import cement_scale

ROOT = Path(__file__).resolve().parent
FUTURE = "SSP2-PkBudg1000"


@lru_cache(maxsize=1)
def erw_results():
    data = json.loads((ROOT / "data/erw_comparison.json").read_text())
    if (
        hashlib.sha256(
            (ROOT / "data/coastal_erw_temporalized.xlsx").read_bytes()
        ).hexdigest()
        != data["foreground_sha256"]
    ):
        raise ValueError("ERW calculation no longer matches the foreground workbook")
    if (
        data.get("ei312_foreground_sha256")
        and hashlib.sha256(
            (ROOT / "data/coastal_erw_ei312.xlsx").read_bytes()
        ).hexdigest()
        != data["ei312_foreground_sha256"]
    ):
        raise ValueError(
            "ERW calculation no longer matches the linked ecoinvent 3.12 foreground"
        )
    return data


def cement_bundle(year=2025, pathway=FUTURE):
    if pathway not in ("SSP2-NPi", FUTURE):
        raise ValueError("Unsupported cement scenario")
    bundle = load_release_bundle("main" if year == 2025 else f"{year}-{pathway}")
    if bundle is None or not bundle.approved:
        raise ValueError("Reviewed cement results unavailable")
    return bundle


def cement_scores(year=2025, pathway=FUTURE):
    bundle = cement_bundle(year, pathway)
    rows = {r["system"]: float(r["score"]) for r in bundle.tables["static_totals"]}
    factor = cement_scale(year)
    return rows["CCS"] * factor, rows["BAU"] * factor


def snapshot(case, year=2025, pathway=FUTURE):
    if case in ("DACCS", "BECCS", "ERW") and year in (2035, 2050):
        from .static_scenarios import case_result

        return case_result(case, year, pathway)["total"]
    if case in ("DACCS", "BECCS"):
        return static_score(case, "SSP2-NPi" if year == 2025 else pathway, year)
    if case == "ERW":
        return next(
            r["net_kg_co2eq"] for r in erw_results()["snapshots"] if r["year"] == year
        )
    ccs, bau = cement_scores(year, pathway)
    return ccs - bau


def number(value):
    return f"{value:,.0f}".replace("-", "−")


def graph(figure, identifier=None):
    return dcc.Graph(
        figure=figure,
        config={"displayModeBar": False, "responsive": True},
        responsive=True,
        className="comparison-chart",
        **({"id": identifier} if identifier else {}),
    )


def style(figure, *, ytitle="", title="", height=None):
    figure.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f7fafb",
        font=dict(family="Arial", size=14, color="#173747"),
        margin=dict(l=52, r=12, t=40, b=48),
        showlegend=False,
        height=height,
        title=dict(text=title, font=dict(size=14)),
        yaxis_title=ytitle,
        hoverlabel=dict(font=dict(size=14)),
    )
    figure.update_xaxes(showgrid=False, zeroline=False)
    figure.update_yaxes(gridcolor="#e0e8eb", zeroline=True, zerolinecolor="#8fa5b0")
    return figure


def static_figure(case, future=False):
    years = [2025, 2050] if future else [2025]
    vals = [snapshot(case, y) for y in years]
    fig = go.Figure()
    for i, (year, value) in enumerate(zip(years, vals)):
        fig.add_bar(
            x=[str(year)],
            y=[value],
            marker_color=CASE[case]["colour"],
            opacity=0.4 if future and i == 0 else 1,
            text=[number(value)],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"{case} · {year}<br>%{{y:,.1f}} kg CO₂-eq<br>{CASE[case]['service']}<extra></extra>",
        )
    fig.update_yaxes(range=[-1200, 150], dtick=500)
    style(fig, ytitle="kg CO₂-eq")
    fig.update_layout(
        meta=dict(
            case=case,
            years=years,
            source=(
                "reviewed inherited results"
                if case != "ERW"
                else "new linked static calculation"
            ),
            native_service=CASE[case]["service"],
        )
    )
    if case == "Cement + CCS":
        from .cement_origins import with_origins

        return with_origins(fig, years=years, activities=False)
    return fig


def case_heading(
    case, context=None, *, combined=False, co2_terms=False, show_origin_key=True,
    service=None,
):
    return html.Div(
        [
            html.Span(case, className="panel-case-name"),
            html.Small(service or CASE[case]["service"]),
            html.Div(context, className="panel-context") if context else None,
            origin_key(combined=combined, co2_terms=co2_terms)
            if case == "Cement + CCS" and show_origin_key
            else None,
        ],
        className="comparison-heading",
    )


def static_panels(future=False):
    panels = []
    for case in CASES:
        year = 2050 if future else 2025
        note = {
            "DACCS": "Air capture, energy supply and geological storage",
            "BECCS": "Standing-forest and displaced-energy reference",
            "ERW": "Corrected foreground linked to ecoinvent 3.12",
            "Cement + CCS": "CCS minus the same clinker without capture",
        }[case]
        current = snapshot(case, 2025)
        val = snapshot(case, year)
        extra = (
            f"{number(val - current)} kg CO₂-eq change from 2025" if future else note
        )
        panels.append(
            html.Article(
                [
                    case_heading(
                        case,
                        "CCS − BAU · foreground CO₂"
                        if case == "Cement + CCS"
                        else None,
                    ),
                    graph(static_figure(case, future)),
                    html.Div(number(val), className="panel-score"),
                    html.Div(extra, className="panel-reading"),
                    html.P(note, className="panel-note") if future else None,
                ],
                className="comparison-panel",
                style={"--case-colour": CASE[case]["colour"]},
                **{"data-case": case},
            )
        )
    return html.Div(
        panels,
        className="comparison-grid",
        **{"data-comparison": "prospective" if future else "current"},
    )


def annual_scores(case, duration=10, lag=1, realization=1):
    values = defaultdict(float)
    if case in ("DACCS", "BECCS"):
        for _, series in results.cohort_temporal_score_series(case, "per_tonne"):
            for year, value in series:
                values[year - 2030] += value
    elif case == "ERW":
        data = campaign_results()
        # A fixed-depth-one routed inventory is retained when available. The
        # live control isolates foreground uptake by holding its background
        # contribution fixed, rather than recalculating LCIA in Dash.
        baseline = data["temporal"]
        default = campaign_profile(10, 1, 1)
        revised = campaign_profile(duration, lag, realization)
        for r in baseline:
            values[int(r["age"])] += r["score"]
        for age, old, new in zip(
            default["age"], default["uptake_kg"], revised["uptake_kg"]
        ):
            values[int(age)] += old - new
    else:
        bundle = cement_bundle()
        for r in bundle.tables["temporal_totals"]:
            if r["system"] in ("BAU", "CCS"):
                values[int(float(r["year"])) - 2035] += (
                    1 if r["system"] == "CCS" else -1
                ) * float(r["score"]) * cement_scale()
    return tuple(sorted(values.items()))


def temporal_figure(
    case, mode="cumulative", duration=10, lag=1, realization=1, end=110
):
    series = annual_scores(case, duration, lag, realization)
    ages = np.asarray([p[0] for p in series])
    values = np.asarray([p[1] for p in series])
    if mode == "cumulative":
        values = np.cumsum(values)
    fig = go.Figure(
        go.Scatter(
            x=ages.tolist(),
            y=values.tolist(),
            mode="lines",
            line=dict(color=CASE[case]["colour"], width=3),
            fill="tozeroy" if mode == "cumulative" else None,
            hovertemplate=f"{case}<br>Project age: %{{x:g}} years<br>%{{y:,.1f}} kg CO₂-eq<extra></extra>",
        )
    )
    style(
        fig,
        ytitle="Cumulative kg CO₂-eq" if mode == "cumulative" else "kg CO₂-eq / year",
    )
    fig.update_xaxes(range=[-5, end], title="Years since project start")
    fig.update_layout(
        meta=dict(
            case=case,
            mode=mode,
            native_service=CASE[case]["service"],
            complete_sum=float(sum(p[1] for p in series)),
            pre_window_total=float(sum(v for y, v in series if y < -5)),
            duration=duration if case == "ERW" else None,
            lag=lag if case == "ERW" else None,
            efficiency=realization if case == "ERW" else None,
        )
    )
    return fig


def time_panels(
    mode="cumulative", duration=10, lag=1, realization=1, end=110, live=False
):
    return html.Div(
        [
            html.Article(
                [
                    case_heading(
                        c,
                        "2035 · CCS − BAU · all CO₂"
                        if c == "Cement + CCS"
                        else "2030–2049 supply campaign"
                        if c == "ERW"
                        else "2030 cohort",
                        show_origin_key=False,
                    ),
                    graph(
                        temporal_figure(c, mode, duration, lag, realization, end),
                        f"four-time-{i}" if live else None,
                    ),
                    html.P(
                        (
                            "2030 cohort"
                            if c in ("DACCS", "BECCS")
                            else (
                                "2030–2049 supply campaign · uptake sensitivity"
                                if c == "ERW"
                                else "2035 cohort · CCS minus BAU"
                            )
                        ),
                        className="panel-note",
                    ),
                ],
                className="comparison-panel",
                style={"--case-colour": CASE[c]["colour"]},
                **{"data-case": c},
            )
            for i, c in enumerate(CASES)
        ],
        className="comparison-grid",
        **{"data-comparison": "time-explicit"},
    )


def forcing_series(case):
    if case in ("DACCS", "BECCS"):
        return [
            (float(y) - 2030, float(v) * 1e12)
            for y, v in results.cohort_fair_total_series(
                case, "radiative forcing", "total"
            )
        ]
    if case == "ERW":
        data = campaign_results()
        return [
            (r["year"] - 2030, r["value"] * 1e12)
            for r in data["fair"]["radiative_forcing"]
        ]
    rows = cement_bundle().tables["fair_responses"]
    by_system = {}
    for system in ("BAU", "CCS"):
        by_system[system] = {
            float(r["year"]): float(r["value"])
            for r in rows
            if r["system"] == system
            and r["metric"] == "radiative_forcing"
            and r["statistic"] in ("q50", "median", "p50")
        }
    if not by_system["CCS"]:
        raise ValueError("Median cement forcing response missing")
    return [
        (y - 2035, (v - by_system["BAU"][y]) * 1e12 * cement_scale())
        for y, v in sorted(by_system["CCS"].items())
    ]


RESPONSE_WINDOW = (2030, 2050)


def response_window(window):
    try:
        start, end = map(float, window)
    except (TypeError, ValueError):
        return RESPONSE_WINDOW
    if not (np.isfinite(start) and np.isfinite(end) and 2030 <= start < end <= 2200):
        return RESPONSE_WINDOW
    return start, end


def integrated_forcing(series, start, end):
    """Signed trapezoidal area, interpolating the exact calendar boundaries."""
    points = np.asarray(sorted(series), dtype=float)
    years, values = points[:, 0], points[:, 1]
    if not (years[0] <= start < end <= years[-1]):
        raise ValueError("Stored forcing does not cover the selected calendar window")
    inside = (years > start) & (years < end)
    x = np.concatenate(([start], years[inside], [end]))
    y = np.concatenate(([np.interp(start, years, values)], values[inside],
                        [np.interp(end, years, values)]))
    integrate = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return float(integrate(y, x))


def forcing_figure(case, window=RESPONSE_WINDOW):
    s = forcing_series(case)
    anchor = 2035 if case == "Cement + CCS" else 2030
    calendar = [(age + anchor, value) for age, value in s]
    start, end = response_window(window)
    area = integrated_forcing(calendar, start, end)
    colour = CASE[case]["colour"]
    rgb = ",".join(str(int(colour[i:i+2], 16)) for i in (1, 3, 5))
    fig = go.Figure(
        go.Scatter(
            x=[p[0] for p in calendar],
            y=[p[1] for p in calendar],
            line=dict(color=colour, width=3),
            fill="tozeroy", fillcolor=f"rgba({rgb},.14)",
            hovertemplate=f"{case}<br>Year %{{x:.1f}}<br>%{{y:.3g}} pW/m²<extra></extra>",
        )
    )
    style(fig, ytitle="ΔRF · pW/m²")
    ticks = sorted({start, end} | {y for y in range(2050, 2201, 50) if start < y < end})
    fig.update_xaxes(range=[start, end], title="Calendar year", tickvals=ticks,
                     ticktext=[f"{y:g}" for y in ticks], tickfont=dict(size=11),
                     title_font=dict(size=14))
    extent = max(abs(v) for age, v in s if -5 <= age <= 170) or 1
    fig.update_yaxes(range=[-extent * 1.12, extent * 0.28],
                     title_font=dict(size=14), tickfont=dict(size=11))
    fig.update_layout(margin=dict(l=44,r=20,t=4,b=32),meta=dict(
        case=case, native_service=CASE[case]["service"], project_start=anchor,
        window_start=start, window_end=end, integrated_forcing=area,
        integrated_forcing_unit="pW·year/m²", area_basis="signed area of displayed stored curve",
    ))
    return fig


def forcing_area_readout(figure):
    meta = figure.layout.meta
    value = meta["integrated_forcing"]
    return [html.Span("Integrated forcing"),
            html.Strong(f"{value:+,.2f}".replace("-", "−")),
            html.Small("pW·year/m²")]


def forcing_panels(live=False):
    return html.Div(
        [
            html.Article(
                [
                    case_heading(
                        c,
                        "2030–2049 · illustrative 10 y / 1 y"
                        if c == "ERW"
                        else "2035 · CCS − BAU"
                        if c == "Cement + CCS"
                        else "2030 cohort",
                        combined=True,
                    ),
                    html.Div(forcing_area_readout(forcing_figure(c)),className="forcing-area",
                             **({"id":f"four-forcing-area-{i}"} if live else {})),
                    graph(forcing_figure(c), f"four-forcing-{i}" if live else None),
                    html.P(
                        (
                            "Fast illustrative reference: 10-year dissolution + 1-year lag"
                            if c == "ERW"
                            else (
                                "CCS response minus BAU response"
                                if c == "Cement + CCS"
                                else "Complete cohort · stored FaIR response"
                            )
                        ),
                        className="panel-note",
                    ),
                ],
                className="comparison-panel",
                style={"--case-colour": CASE[c]["colour"]},
                **{"data-case": c},
            )
            for i, c in enumerate(CASES)
        ],
        className="comparison-grid",
        **{"data-comparison": "climate-response"},
    )


def pulse_timing_figure(delay=0):
    from apps.lca_time.workshop import results as pulse_results

    first = dict(
        pulse_results.co2_reference_pulse_series("radiative forcing", 50, 2030)
    )
    second = dict(
        pulse_results.co2_reference_pulse_series("radiative forcing", 50, 2030 + delay)
    )
    years = sorted(set(first) & set(second))
    fig = go.Figure()
    values = [1000 * (first[y] - second[y]) * 1e12 for y in years]
    fig.add_scatter(
        x=years,
        y=values,
        mode="lines",
        line=dict(color="#173747", width=3.5),
        name="Climate response of the two CO₂ pulses",
        showlegend=False,
        hovertemplate="%{x}<br>%{y:.3f} pW/m²<extra></extra>",
    )
    fig.add_scatter(
        x=years,
        y=[max(v, 0) for v in values],
        mode="lines",
        line=dict(width=0),
        fill="tozeroy",
        fillcolor="rgba(193,138,27,.2)",
        hoverinfo="skip",
        name="Warming influence",
        showlegend=True,
    )
    fig.add_scatter(
        x=years,
        y=[min(v, 0) for v in values],
        mode="lines",
        line=dict(width=0),
        fill="tozeroy",
        fillcolor="rgba(0,138,130,.15)",
        hoverinfo="skip",
        name="Cooling influence",
        showlegend=True,
    )
    fig.add_vline(x=2030, line_color="#b75c43", line_width=2)
    if delay:
        fig.add_vline(
            x=2030 + delay, line_color="#008a82", line_width=2, line_dash="dash"
        )
    style(fig, ytitle="Change in radiative forcing · pW/m²")
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", x=0, y=1.12, font=dict(size=14)),
        margin=dict(l=52, r=12, t=45, b=48),
    )
    fig.update_xaxes(
        range=[2025, 2150],
        title="Calendar year",
        tickvals=[2030, 2050, 2080, 2100, 2150],
    )
    fig.update_yaxes(range=[-0.8, 1.5])
    fig.add_annotation(
        x=2030,
        y=1.38,
        text="+1 t emitted",
        showarrow=False,
        xanchor="left",
        font=dict(size=15, color="#b75c43"),
    )
    fig.add_annotation(
        x=2030 + delay,
        y=1.13,
        text="−1 t removed",
        showarrow=False,
        xanchor="left",
        font=dict(size=15, color="#008a82"),
    )
    if delay:
        fig.add_annotation(
            x=2030 + delay / 2,
            y=0.38,
            text="Forcing while we wait",
            showarrow=False,
            font=dict(size=15, color="#856011"),
        )
    # A teaching illustration using the stored median marginal pulse curves.
    # This is deliberately not labelled as a configuration-level ensemble result.
    window = np.array([y for y in years if 2020 <= y <= 2100], dtype=float)
    reference = np.array([first[int(y)] for y in window])
    net = np.array([1000 * (first[int(y)] - second[int(y)]) for y in window])
    integrate = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    equivalent = float(integrate(net, window) / integrate(reference, window))
    fig.update_layout(
        meta=dict(
            status="illustrative marginal pulse superposition",
            delay=delay,
            equivalent_kg=equivalent,
            window_start=2020,
            window_end=2100,
            reference_year=2030,
            equivalent_basis="ratio of median response areas; not an ensemble quantile",
        )
    )
    return fig


def evidence_note():
    return html.Div(
        "Native services and references remain visible. DACCS/BECCS: Northern Europe; cement: Aalborg; ERW: European foreground. Source packages and cohort dates differ. Read the change within each case.",
        className="evidence-note",
    )


def method_matrix():
    header = html.Tr(
        [
            html.Th("Case / service"),
            html.Th("Current static · 2025"),
            html.Th("Prospective static · 2050"),
            html.Th("Time-explicit · complete inventory"),
        ]
    )
    rows = []
    for c in CASES:
        rows.append(
            html.Tr(
                [
                    html.Th(
                        [html.Strong(c), html.Small(CASE[c]["service"])],
                        style={"borderLeftColor": CASE[c]["colour"]},
                    ),
                    html.Td(number(snapshot(c, 2025))),
                    html.Td(number(snapshot(c, 2050))),
                    html.Td(
                        [
                            number(sum(v for _, v in annual_scores(c))),
                            html.Small("Different lifetime/cohort treatment"),
                        ]
                    ),
                ],
                **{"data-case": c},
            )
        )
    return html.Table(
        [html.Thead(header), html.Tbody(rows)], className="four-method-table"
    )
