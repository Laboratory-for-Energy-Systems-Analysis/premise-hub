"""Alternative, closing CO₂-flow view; never added to root attribution.

Static source: explicit named foreground CO₂ subprocesses, remaining effects
left unassigned. Temporal source: released full-system elementary-flow view.
Their attribution scopes differ; the net totals are unchanged in both views.
"""

from collections import defaultdict
from functools import lru_cache
import numpy as np
from .carbon import FOSSIL, NON_FOSSIL, UPTAKE, OTHER, ORIGINS
from .cement_basis import cement_scale


def origin(name):
    n = name.lower()
    if "non-fossil" in n or "soil or biomass stock" in n:
        return NON_FOSSIL
    if "calcination" in n or n in ("co₂, fossil", "carbon dioxide, fossil"):
        return FOSSIL
    if "historical uptake" in n or n == "carbon dioxide, in air":
        return UPTAKE
    return OTHER


@lru_cache(maxsize=2)
def static_origins(year):
    from .comparison import cement_bundle, snapshot

    paired = defaultdict(float)
    for row in cement_bundle(year).tables["static_subprocesses"]:
        if row["system"] in ("CCS", "BAU"):
            paired[row["stage"], row["subprocess"]] += row["score"] * cement_scale(year) * (
                1 if row["system"] == "CCS" else -1
            )
    groups = defaultdict(float)
    for (_, name), value in paired.items():
        groups[origin(name), 1 if value >= 0 else -1] += value
    if not np.isclose(
        sum(groups.values()), snapshot("Cement + CCS", year), atol=1e-6, rtol=0
    ):
        raise ValueError("Cement static origin view does not close")
    return dict(groups)


@lru_cache(maxsize=1)
def temporal_origins():
    from .comparison import cement_bundle, annual_scores

    paired = defaultdict(float)
    for row in cement_bundle().tables["temporal_contributions"]:
        if row["grouping"] == "flow" and row["system"] in ("CCS", "BAU"):
            paired[row["contributor"], int(float(row["year"])) - 2035] += row[
                "score"
            ] * (1 if row["system"] == "CCS" else -1) * cement_scale()
    groups = defaultdict(lambda: defaultdict(float))
    actual = defaultdict(float)
    for (name, year), value in paired.items():
        groups[origin(name), 1 if value >= 0 else -1][year] += value
        actual[year] += value
    expected = dict(annual_scores("Cement + CCS"))
    if any(
        abs(actual[y] - expected.get(y, 0)) > 1e-6
        for y in actual.keys() | expected.keys()
    ):
        raise ValueError("Cement temporal origin view does not close annually")
    return dict(groups)


def with_origins(
    fig,
    *,
    years=None,
    mode="annual",
    end=170,
    activities=True,
    default_view="origins",
    co2_terms=False,
):
    """Switch between independent decompositions with an explicit initial view."""
    from .comparison import snapshot

    if default_view not in ("origins", "activities"):
        raise ValueError(default_view)
    root_count = len(fig.data)
    for trace in fig.data:
        trace.visible = False
        trace.showlegend = False
    if years:
        x = [str(y) for y in years]
        snapshots = [static_origins(y) for y in years]
        groups = {
            key: [s.get(key, 0) for s in snapshots]
            for key in {k for s in snapshots for k in s}
        }
        totals = [snapshot("Cement + CCS", y) for y in years]
    else:
        from .comparison import annual_scores

        source = temporal_origins()
        net = dict(annual_scores("Cement + CCS"))
        x = list(range(min(min(v) for v in source.values()), max(end, max(net)) + 1))
        groups = {key: [series.get(y, 0) for y in x] for key, series in source.items()}
        totals = [net.get(y, 0) for y in x]
        if mode == "cumulative":
            groups = {key: np.cumsum(v).tolist() for key, v in groups.items()}
            totals = np.cumsum(totals).tolist()
    palette = ORIGINS
    if co2_terms:
        renamed = defaultdict(lambda: [0.0] * len(x))
        for (name, sign), values in groups.items():
            display = (
                "fossil CO₂"
                if name == FOSSIL
                else "non-fossil CO₂"
                if name in (NON_FOSSIL, UPTAKE)
                else name
            )
            renamed[display, sign] = [
                a + b for a, b in zip(renamed[display, sign], values)
            ]
        groups = dict(renamed)
        palette = {
            "fossil CO₂": ORIGINS[FOSSIL],
            "non-fossil CO₂": ORIGINS[NON_FOSSIL],
            OTHER: ORIGINS[OTHER],
        }
    for name, colour in palette.items():
        shown = False
        for sign in (1, -1):
            values = groups.get((name, sign), [0] * len(x))
            if not any(abs(v) > 1e-10 for v in values):
                continue
            common = dict(
                x=x,
                y=values,
                name=name,
                legendgroup=name,
                showlegend=not shown,
                hovertemplate=f"{name}<br>%{{x}}<br>%{{y:,.2f}} kg CO₂-eq<extra></extra>",
            )
            if years or mode == "annual":
                fig.add_bar(
                    **common,
                    marker=dict(
                        color=colour,
                        pattern=dict(
                            shape="." if name in (NON_FOSSIL, "non-fossil CO₂") else ""
                        ),
                    ),
                )
            else:
                fig.add_scatter(
                    **common,
                    mode="lines",
                    line=dict(
                        color=colour,
                        width=0.6,
                        dash="dot" if name == NON_FOSSIL else "solid",
                    ),
                    fillcolor=colour,
                    stackgroup="origin-positive" if sign > 0 else "origin-negative",
                )
            shown = True
    fig.add_scatter(
        x=x,
        y=totals,
        name="Net GWP100",
        showlegend=True,
        mode="markers" if years else "lines",
        marker=dict(symbol="diamond", size=9, color="#173747"),
        line=dict(color="#173747", width=2.2),
        hovertemplate="Net · %{x}<br>%{y:,.2f} kg CO₂-eq<extra></extra>",
    )
    count = len(fig.data)
    activity_visibility = [True] * root_count + [False] * (count - root_count)
    origin_visibility = [False] * root_count + [True] * (count - root_count)
    if default_view == "activities":
        for trace, visible in zip(fig.data, activity_visibility):
            trace.visible = visible
    fig.update_layout(
        barmode="relative",
        showlegend=False,
        legend=dict(
            orientation="h", x=0, y=-0.24, font=dict(size=10.5), tracegroupgap=0
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0,
                y=1.02,
                xanchor="left",
                yanchor="bottom",
                active=0 if default_view == "origins" else 1,
                font=dict(size=11),
                pad=dict(t=0, b=0, l=0, r=0),
                buttons=[
                    dict(
                        label="CO₂ origins",
                        method="update",
                        args=[dict(visible=origin_visibility), dict(showlegend=False)],
                    ),
                    dict(
                        label="Activities" if activities else "Net only",
                        method="update",
                        args=[
                            dict(visible=activity_visibility),
                            dict(showlegend=False),
                        ],
                    ),
                ],
            )
        ],
        margin=dict(l=52, r=12, t=40, b=48, autoexpand=False),
        meta={
            **dict(fig.layout.meta or {}),
            "origin_view": True,
            "origin_scope": "named foreground CO₂ + unassigned remainder"
            if years
            else "full-system elementary-flow CO₂",
            "default_view": "CO₂ origins"
            if default_view == "origins"
            else "Activities"
            if activities
            else "Net only",
        },
    )
    return fig
