"""Signed, closing attribution by root-activity type for the Seoul comparisons."""

from collections import defaultdict
from functools import lru_cache
import hashlib
import json

import numpy as np
import plotly.graph_objects as go
from dash import dcc, html
from apps.setac_2026.figures import prospective_contributions
from . import comparison as base
from .visuals import CASES, CASE
from .cement_basis import cement_scale
from .static_scenarios import SCENARIOS, DEFAULT_SCENARIO, case_result

TYPES = {
    "CO₂ uptake": "#008a82",
    "Biogenic uptake": "#3e7654",
    "Direct / avoided emissions": "#bd7054",
    "Electricity + heat": "#d7aa31",
    "Biomass supply": "#9b826b",
    "Materials + equipment": "#91a4ad",
    "Transport + storage": "#7656a8",
    "Mining + spreading": "#c18a1b",
}

# Slide 15 separates direct carbon mechanisms while upstream effects remain
# assigned to their responsible activity, including a capture-stage heat credit.
TEMPORAL_TYPES = {
    "CO₂ uptake": TYPES["CO₂ uptake"],
    "Biogenic uptake": TYPES["Biogenic uptake"],
    "Avoided fossil CO₂": "#ad603d",
    "Avoided biogenic CO₂": "#85aa72",
    "Other foreground effects": TYPES["Direct / avoided emissions"],
    "Electricity + heat": TYPES["Electricity + heat"],
    "Fuel + biomass supply": TYPES["Biomass supply"],
    "Capture operation + heat credit": "#648e9c",
    "Materials + equipment": TYPES["Materials + equipment"],
    "Transport + storage": TYPES["Transport + storage"],
    "Mining + spreading": TYPES["Mining + spreading"],
}


def temporal_activity_type(name, case):
    typ=activity_type(name,case)
    return {"Direct / avoided emissions":"Other foreground effects",
            "Biomass supply":"Fuel + biomass supply"}.get(typ,typ)

# Slide 5 uses the requested two CO₂ flow names; suppliers keep activity labels.
CURRENT_TYPES = {
    "fossil CO₂": "#ad603d",
    "non-fossil CO₂": "#3e7654",
    "Other direct effects": TYPES["Direct / avoided emissions"],
    **{
        name: TYPES[name]
        for name in (
            "Electricity + heat",
            "Biomass supply",
            "Materials + equipment",
            "Transport + storage",
            "Mining + spreading",
        )
    },
}


@lru_cache(maxsize=2)
def cdr_static_roots(year):
    record = json.loads((base.ROOT / f"data/cdr_static_roots_{year}.json").read_text())
    expected = json.loads(
        (
            base.ROOT.parent / "setac_2026/data/processed/system_inventory_2025.json"
        ).read_text()
    )["basis"]["foreground_sha256"]
    if record["foreground_sha256"] != expected:
        raise ValueError("CDR root attribution no longer matches the foreground")
    for case, data in record["cases"].items():
        total = sum(r["score"] for r in data["foreground"] + data["suppliers"])
        if not np.isclose(total, base.snapshot(case, year), atol=1e-6, rtol=0):
            raise ValueError(f"CDR root attribution does not close: {case} {year}")
    return record


def supplier_type(row):
    """Classify the root supplier, retaining its full upstream life cycle."""
    name = row["activity"].lower()
    product = (row.get("reference_product") or "").lower()
    parent = row.get("foreground_parent", "").lower()
    if "biomass supply from existing spruce forest" in parent:
        return "Biomass supply"
    if product.startswith(
        ("electricity,", "heat,", "diesel, burned in diesel-electric generating set")
    ):
        return "Electricity + heat"
    if product.startswith("transport,") or product == "carbon dioxide, stored":
        return "Transport + storage"
    if any(
        s in name
        for s in (
            "wood chipping",
            "harvesting, forestry",
            "tree seedling",
            "skidding,",
            "forwarding,",
        )
    ):
        return "Biomass supply"
    return "Materials + equipment"


def foreground_contributions(case, year=2025, pathway=DEFAULT_SCENARIO):
    """Direct foreground CO₂, plus signed complete root-supplier contributions."""
    from .carbon import FOSSIL, NON_FOSSIL, UPTAKE
    from .cement_origins import origin

    grouped = defaultdict(float)
    if case in ("DACCS", "BECCS") or (case == "ERW" and year in (2035, 2050)):
        data = (case_result(case, year, pathway) if year in (2035, 2050)
                else cdr_static_roots(year)["cases"][case])
        for row in data["foreground"]:
            name = row["flow"]
            # Fossil/non-fossil methane is NOT a CO₂ flow.
            kind = (
                origin(name)
                if name.lower().startswith(("carbon dioxide,", "co₂,"))
                else None
            )
            typ = (
                "fossil CO₂"
                if kind == FOSSIL
                else "non-fossil CO₂"
                if kind in (NON_FOSSIL, UPTAKE)
                else "Other direct effects"
            )
            value = row["score"]
            grouped[typ, 1 if value >= 0 else -1] += value
        for row in data["suppliers"]:
            value = row["score"]
            kind = activity_type(row["activity"], case) if case == "ERW" else supplier_type(row)
            grouped[kind, 1 if value >= 0 else -1] += value
    elif case == "ERW":
        rows = next(
            r["contributions"] for r in erw_attribution()["static"] if r["year"] == year
        )
        for row in rows:
            value = row["score"]
            direct = row.get("reference_product") == "direct foreground biosphere"
            typ = "non-fossil CO₂" if direct else activity_type(row["activity"], case)
            if typ == "CO₂ uptake":
                raise ValueError("ERW supplier cannot be labelled foreground uptake")
            grouped[typ, 1 if value >= 0 else -1] += value
    else:
        # Released subprocess intensities already keep root providers separate.
        # Only explicit foreground CO₂ entries receive a CO₂ flow label.
        paired = defaultdict(float)
        for row in base.cement_bundle(year, pathway).tables["static_subprocesses"]:
            if row["system"] in ("CCS", "BAU"):
                paired[row["stage"], row["subprocess"]] += row["score"] * cement_scale(year) * (
                    1 if row["system"] == "CCS" else -1
                )
        for (stage, name), value in paired.items():
            kind = origin(name)
            typ = (
                "fossil CO₂"
                if kind == FOSSIL
                else "non-fossil CO₂"
                if kind in (NON_FOSSIL, UPTAKE)
                else cement_type(stage, name)
            )
            if typ == "Direct / avoided emissions":
                typ = "Other direct effects"
            grouped[typ, 1 if value >= 0 else -1] += value
    if not np.isclose(
        sum(grouped.values()), base.snapshot(case, year, pathway), atol=1e-6, rtol=0
    ):
        raise ValueError(f"Foreground + roots do not close: {case} {year}")
    return dict(grouped)


def current_contributions(case):
    return foreground_contributions(case, 2025)


def activity_type(name, case):
    n = name.lower()
    if case == "ERW":
        if "coastal olivine weathering deployment" in n or "atmospheric co" in n:
            return "CO₂ uptake"
        if "electricity" in n:
            return "Electricity + heat"
        if "transport, freight" in n:
            return "Transport + storage"
        if any(
            x in n
            for x in ("spreading", "explosive", "agricultural machinery", "quarry")
        ):
            return "Mining + spreading"
        return "Materials + equipment"
    if any(
        x in n
        for x in ("forest regrowth", "forest carbon regrowth", "upstream biogenic")
    ):
        return "Biogenic uptake"
    if "captured and stored" in n or n == "direct air capture":
        return "CO₂ uptake"
    if "residual biogenic stack" in n or "chp operating" in n:
        return "Direct / avoided emissions"
    if any(x in n for x in ("electricity", "heat activities", "european heat")):
        return "Electricity + heat"
    if any(
        x in n
        for x in (
            "transport losses",
            "co₂ transport",
            "carbon dioxide transport",
            "compression",
            "pipeline",
            "geological storage",
            "carbon dioxide, stored",
        )
    ):
        return "Transport + storage"
    if any(x in n for x in ("biomass", "harvesting")):
        return "Biomass supply"
    return "Materials + equipment"


@lru_cache(maxsize=1)
def erw_attribution():
    record = json.loads((base.ROOT / "data/erw_contributions.json").read_text())
    if (
        record["foreground_sha256"]
        != hashlib.sha256(
            (base.ROOT / "data/coastal_erw_ei312.xlsx").read_bytes()
        ).hexdigest()
    ):
        raise ValueError("ERW attribution no longer matches its foreground")
    if record["package_sha256"] != base.erw_results()["package_sha256"]:
        raise ValueError("ERW attribution no longer matches the comparison package")
    return record


def cement_type(stage, subprocess=""):
    if stage == "clinker" or "Captured calcination" in subprocess:
        return "Direct / avoided emissions"
    if (
        stage == "heat_recovery"
        or "electricity" in subprocess.lower()
        or "heat production" in subprocess.lower()
        or subprocess.lower().startswith("heat,")
    ):
        return "Electricity + heat"
    if stage == "storage":
        return "Transport + storage"
    return "Materials + equipment"


def static_contributions(case, year):
    """Keep opposite signs within a type separate; no absolute-value netting."""
    grouped = defaultdict(float)
    if case in ("DACCS", "BECCS"):
        pathway = "SSP2-NPi" if year == 2025 else base.FUTURE
        for (name, sign), value in prospective_contributions(
            case, pathway, year
        ).items():
            grouped[activity_type(name, case), sign] += value
    elif case == "ERW":
        rows = next(
            s["contributions"] for s in erw_attribution()["static"] if s["year"] == year
        )
        for row in rows:
            v = row["score"]
            grouped[activity_type(row["activity"], case), 1 if v >= 0 else -1] += v
    else:
        # Difference matching subprocesses before grouping: shared clinker-service
        # burdens cancel, and every remaining sign belongs to CCS minus BAU.
        paired = defaultdict(float)
        for row in base.cement_bundle(year).tables["static_subprocesses"]:
            if row["system"] in ("CCS", "BAU"):
                paired[row["stage"], row["subprocess"]] += row["score"] * cement_scale(year) * (
                    1 if row["system"] == "CCS" else -1
                )
        for (stage, name), v in paired.items():
            grouped[cement_type(stage, name), 1 if v >= 0 else -1] += v
    if not np.isclose(
        sum(grouped.values()), base.snapshot(case, year), atol=1e-6, rtol=0
    ):
        raise ValueError(f"Static attribution does not close: {case} {year}")
    return dict(grouped)


@lru_cache(maxsize=4)
def temporal_contributions(case):
    """Responsible-root series, grouped by type and sign at each event year."""
    roots = []
    if case in ("DACCS", "BECCS"):
        roots = [
            (temporal_activity_type(name, case), name, [(y - 2030, v) for y, v in series])
            for name, series in base.results.cohort_temporal_score_series(
                case, "per_tonne"
            )
            if not (case=="DACCS" and temporal_activity_type(name,case)=="Electricity + heat")
        ]
        if case=="DACCS":
            from .daccs_energy import signed_energy
            record=signed_energy()
            for sign in ("positive","negative"):
                roots.append(("Electricity + heat",
                    "market group for electricity, medium voltage | electricity, medium voltage | ENC",
                    [(p["year"]-2030,p[sign]) for p in record["annual"]]))
    elif case == "ERW":
        roots = [
            (
                temporal_activity_type(r["activity"], case),
                r["activity"],
                [(p["age"], p["score"]) for p in r["series"]],
            )
            for r in base.campaign_results()["temporal_roots"]
        ]
    else:
        # This released table has alternative stage and flow decompositions.
        # Use only responsible foreground stages, never add the two views.
        paired = defaultdict(float)
        for r in base.cement_bundle().tables["temporal_contributions"]:
            if r["grouping"] == "stage" and r["system"] in ("CCS", "BAU"):
                paired[r["stage"], int(float(r["year"])) - 2035] += r["score"] * cement_scale() * (
                    1 if r["system"] == "CCS" else -1
                )
        by_stage = defaultdict(list)
        for (stage, age), v in paired.items():
            if stage != "clinker":
                by_stage[stage].append((age, v))
        roots = [
            ({"capture":"Capture operation + heat credit",
              "kiln_fuels":"Fuel + biomass supply"}.get(stage,cement_type(stage)),stage,series)
            for stage,series in by_stage.items()
        ]
        from .cement_temporal_foreground import kiln_co2_differences
        direct=kiln_co2_differences()
        for typ in ("Avoided fossil CO₂","Avoided biogenic CO₂"):
            roots.append((typ,"Direct kiln CO₂ · CCS minus BAU",
                          [(year-2035,parts[typ]) for year,parts in direct.items()]))
        roots.append(("Other foreground effects","Remaining clinker-root effects",
            [(age,value-sum(direct.get(age+2035,{}).values()))
             for (stage,age),value in paired.items() if stage=="clinker"]))
    grouped = defaultdict(lambda: defaultdict(float))
    labels = defaultdict(set)
    for typ, name, series in roots:
        labels[typ].add(name)
        for age, v in series:
            grouped[typ, 1 if v >= 0 else -1][age] += v
    expected = dict(base.annual_scores(case))
    actual = defaultdict(float)
    for series in grouped.values():
        for age, v in series.items():
            actual[age] += v
    if any(
        abs(actual[y] - expected.get(y, 0)) > 1e-3
        for y in actual.keys() | expected.keys()
    ):
        raise ValueError(f"Temporal attribution does not close: {case}")
    return dict(grouped), {t: sorted(names) for t, names in labels.items()}


def legend(net="line", *, co2_terms=False, include_net=True, cumulative=False, temporal=False):
    entries=[]
    for name,colour in (TEMPORAL_TYPES if temporal else CURRENT_TYPES if co2_terms else TYPES).items():
        if temporal and name=="Electricity + heat":
            entries.extend([
                html.Span([html.I(style={"backgroundColor":colour}),"Electricity + heat (+)"]),
                html.Span([html.I(style={"backgroundColor":"#fff4d1",
                    "backgroundImage":"repeating-linear-gradient(135deg, transparent 0 3px, #b18a1d 3px 4px)"}),"Electricity + heat (−)"]),
            ])
        else:
            entries.append(html.Span([html.I(style={"backgroundColor":colour}),name]))
    if temporal:
        entries.append(html.Span([html.I(style={"backgroundColor":"rgba(198,62,62,.18)"}),
                                  "ERW timing scenarios"]))
    return html.Div(
        entries
        + ([
            html.Span(
                [
                    html.B("◆") if net == "diamond" else html.I(className="net-line"),
                    "Net GWP100",
                ],
                className="net-legend",
            )
        ] if include_net else [])
        + ([html.Span([
            html.I(className="net-line", style={"backgroundColor":"#c63e3e","height":"4px"}),
            "Cumulative GWP100 · right axis",
        ],className="net-legend")] if cumulative else []),
        className="activity-legend",
        **{"aria-label": "Root activity type colours"},
    )


def static_figure(case, years=(2025, 2050), *, default_view="origins", co2_terms=False,
                  pathway=DEFAULT_SCENARIO, show_scenarios=False):
    if not co2_terms and (show_scenarios or pathway != DEFAULT_SCENARIO or 2035 in years):
        raise ValueError("Use the foreground CO₂ / complete root-supplier view for scenario extensions")
    fig = go.Figure()
    snapshots = (
        [foreground_contributions(case, y, pathway) for y in years]
        if co2_terms
        else [static_contributions(case, y) for y in years]
    )
    x_values = list(range(len(years))) if show_scenarios else [str(y) for y in years]
    for typ, colour in (CURRENT_TYPES if co2_terms else TYPES).items():
        for sign in (1, -1):
            values = [s.get((typ, sign), 0) for s in snapshots]
            if not any(values):
                continue
            fig.add_bar(
                x=x_values,
                y=values,
                name=typ,
                legendgroup=typ,
                marker_color=colour,
                customdata=[[case, y, "Current reference" if y == 2025 else pathway] for y in years],
                hovertemplate="%{customdata[0]} · %{customdata[1]}<br>%{customdata[2]}<br>%{y:,.2f} kg CO₂-eq<extra>%{fullData.name}</extra>",
            )
    totals = [base.snapshot(case, y, pathway) for y in years]
    scenario_scores = {}
    if show_scenarios:
        for p, colour, symbol, offset in (
            ("SSP2-NPi", "#6f818a", "diamond-open", -.10),
            (DEFAULT_SCENARIO, "#008a82", "diamond", .10),
        ):
            points = [(i, y) for i, y in enumerate(years) if y != 2025]
            values = [base.snapshot(case, y, p) for _, y in points]
            scenario_scores[p] = dict(zip((y for _, y in points), values))
            fig.add_scatter(
                x=[i + offset for i, _ in points], y=values,
                customdata=[[y, p] for _, y in points],
                name=p.removeprefix("SSP2-") + " net", mode="markers",
                marker=dict(symbol=symbol, size=10, color=colour,
                            line=dict(color=colour if symbol.endswith("open") else "white", width=1.6)),
                hovertemplate="%{customdata[0]} · %{customdata[1]}<br>Net: %{y:,.2f} kg CO₂-eq<extra></extra>",
            )
        reference = [(i, y) for i, y in enumerate(years) if y == 2025]
        if reference:
            fig.add_scatter(x=[i for i, _ in reference],
                y=[base.snapshot(case, y) for _, y in reference],
                mode="markers", name="2025 reference net",
                marker=dict(symbol="diamond", size=9, color="#173747", line=dict(color="white", width=1.5)),
                hovertemplate="2025 current reference<br>Net: %{y:,.2f} kg CO₂-eq<extra></extra>")
        fig.update_xaxes(tickvals=list(range(len(years))), ticktext=[str(y) for y in years],
                         range=[-.5, len(years) - .5], type="linear")
    else:
        fig.add_scatter(x=x_values, y=totals, name="Net GWP100", mode="markers",
            marker=dict(symbol="diamond", size=9, color="#173747", line=dict(color="white", width=1.5)))
    base.style(fig, ytitle="kg CO₂-eq")
    fig.update_layout(
        barmode="relative",
        meta=dict(
            case=case,
            years=list(years),
            attribution="foreground CO₂ + complete root supply chains"
            if co2_terms
            else "signed root activity type",
            co2_terms=co2_terms,
            net_scores=totals,
            bars_pathway=pathway if show_scenarios else None,
            scenario_net_scores=scenario_scores,
            native_service=CASE[case]["service"],
        ),
    )
    fig.update_yaxes(
        range=[-1250, 350] if co2_terms else [-1600, 750],
        dtick=250 if co2_terms else 500,
    )
    if case == "Cement + CCS" and not co2_terms:
        from .cement_origins import with_origins

        return with_origins(fig, years=years, default_view=default_view)
    return fig


def static_panels(years=(2025, 2050), *, default_view="origins", co2_terms=False,
                  pathway=DEFAULT_SCENARIO, show_scenarios=False, live=False):
    current_context = {
        "DACCS": "Northern Europe · " + "/".join(str(y) for y in years),
        "BECCS": "Northern Europe · " + "/".join(str(y) for y in years),
        "ERW": "European coastal model · " + "/".join(str(y) for y in years),
        "Cement + CCS": "Aalborg, Denmark · "
        + "/".join(str(y) for y in years),
    }
    return html.Div(
        [
            html.Article(
                [
                    base.case_heading(
                        c,
                        current_context[c]
                        if co2_terms
                        else "CCS − BAU · foreground CO₂"
                        if c == "Cement + CCS"
                        else None,
                        co2_terms=co2_terms,
                    ),
                    base.graph(
                        static_figure(
                            c, years, default_view=default_view, co2_terms=co2_terms,
                            pathway=pathway, show_scenarios=show_scenarios,
                        ),
                        f"future-case-{CASES.index(c)}" if live else None,
                    ),
                    html.Div(
                        (f"{years[-1]}: " if show_scenarios else "") + base.number(base.snapshot(c, years[-1], pathway)),
                        className="panel-score",
                        **({"id": f"future-score-{CASES.index(c)}"} if live else {}),
                    ),
                    html.P(f"{years[-1]} net · ◆ net score", className="panel-note"),
                ],
                className="comparison-panel",
                style={"--case-colour": CASE[c]["colour"]},
                **{"data-case": c},
            )
            for c in CASES
        ],
        className="comparison-grid",
        **{
            "data-comparison": "current-contributions"
            if len(years) == 1
            else "prospective-contributions"
        },
    )


def future_comparison(print_mode=False):
    control = (
        html.Strong("Future bars: PkBudg1000 (default)") if print_mode
        else html.Div([
            html.Strong("Future bars"),
            dcc.RadioItems(id="future-pathway", value=DEFAULT_SCENARIO,
                options=[{"label": "PkBudg1000 (default)", "value": DEFAULT_SCENARIO},
                         {"label": "NPi", "value": "SSP2-NPi"}],
                inline=True, className="segmented future-pathway-picker"),
        ], className="future-bars-control")
    )
    return html.Div([
        html.Div([
            control,
            html.Div([
                html.Span([html.B("◇", style={"color": "#6f818a"}), "NPi net"]),
                html.Span([html.B("◆", style={"color": "#008a82"}), "PkBudg1000 net"]),
                html.Span([html.B("◆", style={"color": "#173747"}), "2025 reference"]),
            ], className="future-net-key", **{"aria-label": "Diamond markers show net scores for both future scenarios"}),
        ], className="future-scenario-controls"),
        static_panels(years=(2025, 2035, 2050), default_view="activities", co2_terms=True,
                      pathway=DEFAULT_SCENARIO, show_scenarios=True, live=not print_mode),
        legend(co2_terms=True, include_net=False),
    ], className="future-comparison")


@lru_cache(maxsize=1)
def temporal_axis_ranges():
    """Shared annual bounds and the presenter's cumulative −1000 limit."""
    annual_low = annual_high = 0.0
    for case in CASES:
        grouped, _ = temporal_contributions(case)
        positive, negative = defaultdict(float), defaultdict(float)
        for (_, sign), series in grouped.items():
            target = positive if sign > 0 else negative
            for year, value in series.items():
                if -5 <= year <= 100:
                    target[year] += value
        annual_low = min(annual_low,min(negative.values(),default=0))
        annual_high = max(annual_high,max(positive.values(),default=0))
    def rounded_range(low, high, step):
        # One third of the plot is above zero on both axes. Round outward
        # after padding so shared scales never hide a signed contribution.
        extent = float(np.ceil(max(-low,2*high)*1.08/step)*step) or step
        return (-extent,extent/2)
    return (rounded_range(annual_low,annual_high,10),(-1000.0,500.0))


def temporal_figure(case):
    """Annual signed areas with a cumulative net on an aligned secondary axis."""
    grouped, labels = temporal_contributions(case)
    net = base.annual_scores(case)
    years = sorted(set(y for y, _ in net) | {y for s in grouped.values() for y in s})
    years = list(range(int(min(years)), max(170, int(max(years))) + 1))
    start_year = 2035 if case == "Cement + CCS" else 2030
    calendar_years = [start_year+y for y in years]
    fig = go.Figure()
    for typ, colour in TEMPORAL_TYPES.items():
        for sign in (1, -1):
            values = [grouped.get((typ, sign), {}).get(y, 0) for y in years]
            if not any(values):
                continue
            energy=typ=="Electricity + heat"
            negative_energy=energy and sign<0
            name=(f"{typ} ({'+' if sign>0 else '−'})" if energy else typ)
            fig.add_scatter(
                x=years, y=values, customdata=calendar_years,
                name=name, legendgroup=name, mode="lines",
                line=dict(color=colour, width=0.6, shape="linear"),
                fillcolor=colour,
                fillpattern=(dict(shape="/",fgcolor="#b18a1d",bgcolor="#fff4d1",
                                  fillmode="replace",size=6,solidity=.2) if negative_energy else None),
                stackgroup="positive" if sign > 0 else "negative",
                meta=dict(activity_type=typ,sign=sign),
                hovertemplate=f"{name}<br>%{{customdata}} · age %{{x:g}}<br>%{{y:,.2f}} kg CO₂-eq / year<extra></extra>",
            )
    values = dict(net)
    totals = [values.get(y, 0) for y in years]
    cumulative = np.cumsum(totals).tolist()
    timing_scenarios=((10,1),(30,5),(100,5))
    if case=="ERW":
        curves=[]
        for duration,lag in timing_scenarios:
            scenario=dict(base.annual_scores(case,duration,lag,1))
            curves.append(np.cumsum([scenario.get(y,0) for y in years]))
        lower,upper=np.min(curves,axis=0),np.max(curves,axis=0)
        for values,name,fill in ((lower,"ERW timing minimum",None),
                                 (upper,"ERW timing maximum","tonexty")):
            fig.add_scatter(x=years,y=values.tolist(),customdata=calendar_years,
                name=name,mode="lines",yaxis="y2",line=dict(width=0),
                fill=fill,fillcolor="rgba(198,62,62,.16)",
                meta=dict(display_role="timing-scenario-envelope"),
                hovertemplate="Illustrative ERW timing bound<br>%{customdata}: %{y:,.1f} kg CO₂-eq<extra></extra>")
    fig.add_scatter(
        x=years, y=cumulative, customdata=calendar_years,
        name="Cumulative GWP100", mode="lines", yaxis="y2",
        line=dict(color="#c63e3e", width=4.5),
        hovertemplate="Cumulative net · %{customdata} (age %{x:g})<br>%{y:,.2f} kg CO₂-eq<extra></extra>",
    )
    base.style(fig, ytitle="kg CO₂-eq / year")
    annual_range, cumulative_range = temporal_axis_ranges()
    fig.update_yaxes(range=annual_range,dtick=20,
                     title_font=dict(size=12),tickfont=dict(size=11))
    fig.update_xaxes(range=[-5,100], title="Calendar year",
        tickvals=[0,50,100],
        ticktext=[str(start_year),str(start_year+50),str(start_year+100)],
        ticklabeloverflow="allow", automargin=True,
        title_font=dict(size=12),tickfont=dict(size=11))
    fig.update_layout(
        margin=dict(l=52,r=64,t=22,b=54),
        yaxis2=dict(overlaying="y",side="right",anchor="x",
            range=cumulative_range,dtick=500,
            title=dict(text="Cumulative kg CO₂-eq",font=dict(color="#c63e3e",size=12),standoff=5),
            tickfont=dict(color="#c63e3e",size=11),tickformat=",.0f",nticks=4,
            showgrid=False,zeroline=False),
        meta=dict(case=case,mode="annual",cumulative_overlay=True,
            start_year=start_year,attribution="responsible root activity type",
            timing_envelope=(dict(scenarios=[dict(dissolution_years=d,lag_scale_years=l)
                for d,l in timing_scenarios],interpretation="illustrative scenario range, not a confidence interval",
                upstream="held fixed",realization=1) if case=="ERW" else None),
            normalization_tonnes=1,normalization_scope="whole operating lifetime",
            normalization_basis=("eventual gross atmospheric uptake potential, modelled"
                                 if case == "ERW" else "physical CO2 stored after losses"),
            root_labels=labels,complete_sum=sum(v for _,v in net),
            pre_window_total=sum(v for y,v in net if y < -5)),
    )
    return fig


def temporal_panels(live=False):
    return html.Div(
        [
            html.Article(
                [
                    base.case_heading(
                        c,
                        "2030–2049 · illustrative 10 y / 1 y"
                        if c == "ERW"
                        else "2035 · CCS − BAU · all CO₂"
                        if c == "Cement + CCS"
                        else "2030 cohort",
                        show_origin_key=False,
                        service=("1 t eventual uptake · modelled" if c == "ERW"
                                 else "1 t CO₂ stored · whole project"),
                    ),
                    base.graph(
                        temporal_figure(c), f"four-time-{i}" if live else None
                    ),
                    html.P(
                        "Foreground stage roots · CCS − BAU"
                        if c == "Cement + CCS"
                        else "Responsible root activity types",
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
        **{"data-comparison": "temporal-contributions"},
    )
