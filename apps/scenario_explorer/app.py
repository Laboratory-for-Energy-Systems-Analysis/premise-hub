from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

import dash
from dash import ALL, Input, Output, State, ctx, dcc, html, no_update
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml
from flask_caching import Cache

APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = APP_ROOT / "data"
REQUESTS_PREFIX = os.getenv("SCENARIO_REQUESTS_PREFIX", "/")
MAX_COMPARISONS = 6
TOP_VARIABLES = 8

with (DATA_DIR / "units.yaml").open(encoding="utf-8") as stream:
    UNITS = yaml.safe_load(stream)
with (DATA_DIR / "ssp_descriptions.yaml").open(encoding="utf-8") as stream:
    SSP_DESCRIPTIONS = yaml.safe_load(stream)
with (DATA_DIR / "rcp_descriptions.yaml").open(encoding="utf-8") as stream:
    RCP_DESCRIPTIONS = yaml.safe_load(stream)
with (DATA_DIR / "datasets.yaml").open(encoding="utf-8") as stream:
    DATASET_ENTRIES = yaml.safe_load(stream)
with (DATA_DIR / "sector_catalog.yaml").open(encoding="utf-8") as stream:
    SECTOR_CATALOG = yaml.safe_load(stream)

DATASETS = {str(entry["id"]): entry for entry in DATASET_ENTRIES}
DEFAULT_DATASET = "2.4.9"
DEFAULT_SECTOR = "GMST increase"
DEFAULT_COMPARISONS = [
    {"model": "image", "scenario": "SSP1-L"},
    {"model": "image", "scenario": "SSP2-M"},
    {"model": "image", "scenario": "SSP3-H"},
]
DEFAULT_PAIR = DEFAULT_COMPARISONS[0]
VIEW_STATE_REVISION = 2

TOPICS = SECTOR_CATALOG["topics"]
TOPIC_BY_ID = {topic["id"]: topic for topic in TOPICS}
SECTOR_TO_TOPIC = {
    sector: topic["id"] for topic in TOPICS for sector in topic["sectors"]
}
SECTOR_BEHAVIOR = SECTOR_CATALOG.get("sector_behavior", {})

PSI_COLORS = [
    "#006b8f",
    "#008a82",
    "#d99614",
    "#c44e52",
    "#7656a8",
    "#0b3b52",
    "#4f8b57",
    "#d46b2c",
]
OTHER_COLOR = "#7b8790"


def dataset_path(dataset_id: str) -> Path:
    try:
        filename = DATASETS[str(dataset_id)]["filename"]
    except KeyError as error:
        raise ValueError(f"Unknown dataset id: {dataset_id}") from error
    path = (DATA_DIR / str(filename)).resolve()
    if path.parent != DATA_DIR.resolve() or not path.is_file():
        raise FileNotFoundError(path)
    return path


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    requests_pathname_prefix=REQUESTS_PREFIX,
    compress=True,
    title="Premise IAM Scenario Explorer",
    update_title=None,
)
load_figure_template("LUX")
server = app.server

cache = Cache(
    server,
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 600,
        "CACHE_THRESHOLD": 3,
    },
)

COLUMN_DTYPES = {
    "region": "category",
    "variables": "category",
    "year": "int32",
    "val": "float64",
    "sector": "category",
    "model": "category",
    "scenario": "category",
    "powertrain": "category",
    "size": "category",
    "region_source": "category",
}


@cache.memoize(timeout=600)
def get_dataset(dataset_id: str) -> pd.DataFrame:
    path = dataset_path(dataset_id)
    print(f"[LOAD] Reading {path.name}")
    frame = pd.read_csv(path, dtype=COLUMN_DTYPES)
    if "region_source" not in frame.columns:
        frame["region_source"] = pd.Categorical(
            ["reported"] * len(frame), categories=["reported", "derived"]
        )
    return frame


def get_all_variables() -> list[str]:
    with (DATA_DIR / "variable_catalog.json").open(encoding="utf-8") as stream:
        return json.load(stream)


def pair_token(model: str, scenario: str) -> str:
    return f"{model}:{scenario}"


def normalize_pairs(value: object) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    if not isinstance(value, list):
        return pairs
    for item in value:
        if not isinstance(item, dict):
            continue
        model = str(item.get("model", "")).strip()
        scenario = str(item.get("scenario", "")).strip()
        if model and scenario and {"model": model, "scenario": scenario} not in pairs:
            pairs.append({"model": model, "scenario": scenario})
    return pairs[:MAX_COMPARISONS]


def default_comparisons_for(
    available: list[dict[str, str]],
) -> list[dict[str, str]]:
    available_tokens = {pair_token(**pair) for pair in available}
    preferred = [
        dict(pair)
        for pair in DEFAULT_COMPARISONS
        if pair_token(**pair) in available_tokens
    ]
    return preferred or available[:1]


def available_pairs(
    frame: pd.DataFrame, sector: str | None = None
) -> list[dict[str, str]]:
    subset = frame
    if sector:
        subset = subset.loc[subset["sector"].eq(sector)]
    values = (
        subset[["model", "scenario"]]
        .drop_duplicates()
        .astype(str)
        .sort_values(["model", "scenario"])
    )
    return values.to_dict("records")


def sectors_for_topic(frame: pd.DataFrame, topic_id: str) -> list[str]:
    available = set(frame["sector"].dropna().unique())
    configured = TOPIC_BY_ID.get(topic_id, {}).get("sectors", [])
    sectors = [sector for sector in configured if sector in available]
    if topic_id == "energy":
        known = set(SECTOR_TO_TOPIC)
        sectors.extend(sorted(available - known))
    return list(dict.fromkeys(sectors))


def topic_for_sector(sector: str) -> str:
    return SECTOR_TO_TOPIC.get(sector, "energy")


def sector_supports_relative(sector: str, frame: pd.DataFrame | None = None) -> bool:
    behavior = SECTOR_BEHAVIOR.get(sector, {})
    if behavior.get("relative") is False:
        return False
    if frame is not None and not frame.empty and frame["val"].lt(0).any():
        return False
    return True


def parse_view_query(search: str | None) -> dict[str, object]:
    query = parse_qs((search or "").lstrip("?"), keep_blank_values=False)
    pairs = []
    for encoded in query.get("pair", []):
        if ":" not in encoded:
            continue
        model, scenario = encoded.split(":", 1)
        pairs.append({"model": model, "scenario": scenario})
    return {
        "version": (query.get("version") or [None])[0],
        "sector": (query.get("sector") or [None])[0],
        "pairs": pairs,
        "regions": query.get("region", []),
        "mode": (query.get("mode") or [None])[0],
    }


def serialize_view_state(state: dict[str, object]) -> str:
    values: list[tuple[str, str]] = [
        ("version", str(state["version"])),
        ("sector", str(state["sector"])),
    ]
    for pair in normalize_pairs(state.get("pairs")):
        values.append(("pair", pair_token(pair["model"], pair["scenario"])))
    for region in (
        state.get("regions", []) if isinstance(state.get("regions"), list) else []
    ):
        values.append(("region", str(region)))
    values.append(("mode", str(state.get("mode", "absolute"))))
    return urlencode(values)


def common_regions(
    frame: pd.DataFrame, sector: str, pairs: list[dict[str, str]]
) -> list[str]:
    if not pairs:
        return []
    sector_rows = frame.loc[
        frame["sector"].eq(sector), ["model", "scenario", "region"]
    ]
    region_sets = []
    for pair in pairs:
        subset = sector_rows.loc[
            sector_rows["model"].eq(pair["model"])
            & sector_rows["scenario"].eq(pair["scenario"])
        ]
        region_sets.append(set(subset["region"].dropna().unique()))
    common = set.intersection(*region_sets) if region_sets else set()
    return sorted(common, key=lambda value: (value != "World", value))


def validate_view_state(raw_state: object) -> tuple[dict[str, object], list[str]]:
    raw = raw_state if isinstance(raw_state, dict) else {}
    notes: list[str] = []

    version = str(raw.get("version") or DEFAULT_DATASET)
    if version not in DATASETS:
        version = DEFAULT_DATASET
        notes.append("The requested premise version was unavailable; 2.4.9 was used.")
    frame = get_dataset(version)

    available_sectors = set(frame["sector"].dropna().unique())
    sector = str(raw.get("sector") or DEFAULT_SECTOR)
    if sector not in available_sectors:
        sector = (
            DEFAULT_SECTOR
            if DEFAULT_SECTOR in available_sectors
            else sorted(available_sectors)[0]
        )
        notes.append(
            "The requested sector was unavailable and was replaced with a valid overview."
        )

    valid_pairs = available_pairs(frame, sector)
    valid_tokens = {pair_token(pair["model"], pair["scenario"]) for pair in valid_pairs}
    pairs = [
        pair
        for pair in normalize_pairs(raw.get("pairs"))
        if pair_token(pair["model"], pair["scenario"]) in valid_tokens
    ]
    if not pairs:
        pairs = default_comparisons_for(valid_pairs)
        if raw.get("pairs"):
            notes.append("Unavailable model–scenario comparisons were removed.")
    elif len(normalize_pairs(raw.get("pairs"))) != len(pairs):
        notes.append(
            "Unavailable or duplicate model–scenario comparisons were removed."
        )

    regions = common_regions(frame, sector, pairs)
    requested_regions = (
        raw.get("regions") if isinstance(raw.get("regions"), list) else []
    )
    selected_regions = [
        str(region) for region in requested_regions if str(region) in regions
    ]
    if not selected_regions:
        selected_regions = ["World"] if "World" in regions else regions[:1]
        if requested_regions:
            notes.append("Unavailable regions were removed from the view.")

    mode = str(raw.get("mode") or "absolute")
    selected = filter_frame(frame, sector, pairs, selected_regions)
    if mode not in {"absolute", "relative"}:
        mode = "absolute"
    if mode == "relative" and not sector_supports_relative(sector, selected):
        mode = "absolute"
        notes.append(
            "Relative shares are not valid for this sector; absolute values are shown."
        )

    return {
        "version": version,
        "sector": sector,
        "pairs": pairs,
        "regions": selected_regions,
        "mode": mode,
    }, notes


def filter_frame(
    frame: pd.DataFrame,
    sector: str,
    pairs: list[dict[str, str]],
    regions: list[str] | None = None,
) -> pd.DataFrame:
    subset = frame.loc[frame["sector"].eq(sector)].copy()
    pair_mask = pd.Series(False, index=subset.index)
    for pair in pairs:
        pair_mask |= subset["model"].eq(pair["model"]) & subset["scenario"].eq(
            pair["scenario"]
        )
    subset = subset.loc[pair_mask]
    if regions is not None:
        subset = subset.loc[subset["region"].isin(regions)]
    return subset


def humanize_variable(variable: object) -> str:
    value = str(variable)
    value = re.sub(r"^heat, (buildings|industrial|secondary),\s*", "", value)
    value = value.replace("_", " ").strip(" ,-_")
    special = {
        "CO2": "CO₂",
        "gdp": "GDP",
        "GMST": "GMST",
        "lpg": "LPG",
    }
    if value in special:
        return special[value]
    return value[:1].upper() + value[1:]


def summarize_for_chart(
    frame: pd.DataFrame, limit: int = TOP_VARIABLES
) -> pd.DataFrame:
    if frame.empty:
        return frame.assign(display_variable=pd.Series(dtype="string"))
    work = frame.loc[frame["val"].ne(0)].copy()
    ranking = (
        work.assign(_magnitude=work["val"].abs())
        .groupby("variables", observed=True)["_magnitude"]
        .sum()
        .sort_values(ascending=False)
    )
    keep = set(ranking.head(limit).index.astype(str))
    raw_variables = work["variables"].astype(str)
    work["display_variable"] = raw_variables.map(
        lambda value: humanize_variable(value) if value in keep else "Other"
    )
    return (
        work.groupby(
            ["year", "region", "region_source", "display_variable"],
            observed=True,
            as_index=False,
        )["val"]
        .sum()
        .sort_values(["year", "display_variable"])
    )


def chart_kind(sector: str, frame: pd.DataFrame) -> str:
    if SECTOR_BEHAVIOR.get(sector, {}).get("chart") == "indicator":
        return "line"
    return "bar" if frame["year"].nunique() <= 2 else "area"


def is_single_series_comparison(frame: pd.DataFrame) -> bool:
    """Return whether each model–scenario–region contributes one comparable series."""
    if frame.empty:
        return False
    series = frame.loc[
        frame["val"].ne(0), ["model", "scenario", "region", "variables"]
    ].drop_duplicates()
    if series.empty:
        return False
    pair_count = len(series[["model", "scenario"]].drop_duplicates())
    series_per_pair_region = series.groupby(
        ["model", "scenario", "region"], observed=True
    ).size()
    return pair_count > 1 and bool(series_per_pair_region.eq(1).all())


def scenario_details(scenario: str) -> tuple[str, str, str, str]:
    parts = scenario.split("-")
    ssp = SSP_DESCRIPTIONS.get(parts[0] if parts else "", {})
    rcp = RCP_DESCRIPTIONS.get(parts[1] if len(parts) > 1 else "", {})
    return (
        ssp.get("name", ""),
        ssp.get("description", ""),
        rcp.get("name", ""),
        rcp.get("description", ""),
    )


def build_figure(
    raw_frame: pd.DataFrame,
    sector: str,
    mode: str,
    y_range: tuple[float, float] | None = None,
) -> go.Figure:
    plotted = summarize_for_chart(raw_frame)
    if plotted.empty:
        figure = go.Figure()
        figure.add_annotation(text="No data for this selection", showarrow=False)
        return figure

    variable_order = (
        plotted.assign(_magnitude=plotted["val"].abs())
        .groupby("display_variable", observed=True)["_magnitude"]
        .sum()
        .sort_values(ascending=False)
        .index.astype(str)
        .tolist()
    )
    color_map = {
        variable: (
            OTHER_COLOR if variable == "Other" else PSI_COLORS[index % len(PSI_COLORS)]
        )
        for index, variable in enumerate(variable_order)
    }
    facet = "region" if plotted["region"].astype(str).nunique() > 1 else None
    labels = {
        "year": "Year",
        "val": "Value",
        "display_variable": "Technology",
        "region": "Region",
        "region_source": "Region source",
    }
    kind = chart_kind(sector, plotted)
    relative = mode == "relative"
    common = dict(
        data_frame=plotted,
        x="year",
        y="val",
        color="display_variable",
        color_discrete_map=color_map,
        category_orders={"display_variable": variable_order},
        facet_col=facet,
        labels=labels,
        hover_data={"region_source": True},
    )
    if kind == "line":
        figure = px.line(**common, markers=True, line_group="region")
    elif kind == "bar":
        figure = px.bar(**common, barmode="stack")
        if relative:
            figure.update_layout(barnorm="percent")
    else:
        figure = px.area(
            **common,
            line_group="region",
            groupnorm="percent" if relative else None,
        )

    unit = "Share (%)" if relative else UNITS.get(sector, {}).get("label", "Value")
    figure.update_layout(
        autosize=True,
        height=500,
        margin={"l": 58, "r": 18, "t": 110, "b": 62},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        showlegend=True,
        font={"family": "Arial, Helvetica, sans-serif", "color": "#17232c", "size": 12},
        legend={
            "title": {"text": "Technology"},
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "x": 0,
        },
        hoverlabel={"bgcolor": "#ffffff", "font_color": "#17232c"},
        transition_duration=180,
    )
    figure.update_xaxes(showgrid=False, title="Year")
    figure.update_yaxes(
        gridcolor="#e7ecef",
        zerolinecolor="#c6d0d5",
        title=unit,
        rangemode="tozero" if not relative else None,
    )
    if relative:
        figure.update_yaxes(range=[0, 100])
    elif y_range is not None:
        figure.update_yaxes(range=list(y_range))
    figure.for_each_annotation(
        lambda annotation: annotation.update(text=annotation.text.split("=")[-1])
    )
    return figure


def build_single_series_figure(
    raw_frame: pd.DataFrame,
    sector: str,
    mode: str,
    pairs: list[dict[str, str]],
    y_range: tuple[float, float] | None = None,
) -> go.Figure:
    """Overlay comparable model–scenario time series in a single figure."""
    plotted = (
        raw_frame.loc[raw_frame["val"].ne(0)]
        .groupby(
            ["model", "scenario", "year", "region", "region_source"],
            observed=True,
            as_index=False,
        )["val"]
        .sum()
    )
    if plotted.empty:
        figure = go.Figure()
        figure.add_annotation(text="No data for this selection", showarrow=False)
        return figure

    plotted["comparison"] = (
        plotted["model"].astype(str).str.upper()
        + " · "
        + plotted["scenario"].astype(str)
    )
    comparison_order = [
        f"{pair['model'].upper()} · {pair['scenario']}" for pair in pairs
    ]
    region_count = plotted["region"].astype(str).nunique()
    facet = "region" if region_count > 1 else None
    facet_columns = min(region_count, 3)
    figure_height = max(500, ((region_count + 2) // 3) * 360)
    relative = mode == "relative"
    if relative:
        plotted["val"] = 100.0

    figure = px.line(
        plotted,
        x="year",
        y="val",
        color="comparison",
        markers=True,
        line_group="comparison",
        color_discrete_sequence=PSI_COLORS,
        category_orders={"comparison": comparison_order},
        facet_col=facet,
        facet_col_wrap=facet_columns if facet else 0,
        labels={
            "year": "Year",
            "val": "Value",
            "comparison": "Model · scenario",
            "region": "Region",
            "region_source": "Region source",
        },
        hover_data={
            "model": False,
            "scenario": False,
            "region": True,
            "region_source": True,
        },
    )
    unit = "Share (%)" if relative else UNITS.get(sector, {}).get("label", "Value")
    figure.update_layout(
        autosize=True,
        height=figure_height,
        margin={"l": 58, "r": 18, "t": 110, "b": 62},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        showlegend=True,
        font={"family": "Arial, Helvetica, sans-serif", "color": "#17232c", "size": 12},
        legend={
            "title": {"text": "Model · scenario"},
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "x": 0,
        },
        hoverlabel={"bgcolor": "#ffffff", "font_color": "#17232c"},
        transition_duration=180,
    )
    figure.update_traces(line={"width": 2.5})
    figure.update_xaxes(showgrid=False, title="Year")
    figure.update_yaxes(
        gridcolor="#e7ecef",
        zerolinecolor="#c6d0d5",
        title=unit,
        rangemode="tozero" if not relative else None,
    )
    if relative:
        figure.update_yaxes(range=[0, 100])
    elif y_range is not None:
        figure.update_yaxes(range=list(y_range))
    figure.for_each_annotation(
        lambda annotation: annotation.update(text=annotation.text.split("=")[-1])
    )
    return figure


def _dropdown(label: str, component: dcc.Dropdown, control_id: str) -> html.Div:
    return html.Div(
        [html.Label(label, htmlFor=control_id), component],
        className="control-group",
    )


def build_layout() -> html.Div:
    return html.Div(
        className="explorer-shell",
        children=[
            dcc.Location(id="explorer-url", refresh=False),
            dcc.Store(id="active-view-store"),
            dcc.Store(id="saved-view-store", storage_type="local"),
            dcc.Store(id="comparison-store"),
            dcc.Store(id="url-sync-store"),
            dcc.Download(id="download-data"),
            html.Header(
                className="explorer-header",
                children=[
                    html.A(
                        className="brand-lockup",
                        href="/",
                        children=[
                            html.Img(
                                src="/static/psi-mark.svg",
                                className="psi-mark",
                                alt="PSI",
                            ),
                            html.Span(
                                className="brand-copy",
                                children=[
                                    html.Strong("Paul Scherrer Institute"),
                                    html.Small(
                                        "Laboratory for Energy Systems Analyses"
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Nav(
                        children=[
                            html.A("Premise resources", href="/"),
                            html.A(
                                "Documentation",
                                href="https://premise.readthedocs.io",
                                target="_blank",
                                rel="noopener noreferrer",
                            ),
                            html.A(
                                "GitHub",
                                href="https://github.com/polca/premise",
                                target="_blank",
                                rel="noopener noreferrer",
                            ),
                        ],
                        **{"aria-label": "Resource links"},
                    ),
                ],
            ),
            html.Div(className="psi-accent", **{"aria-hidden": "true"}),
            html.Main(
                className="explorer-main",
                children=[
                    html.Section(
                        className="explorer-intro",
                        children=[
                            html.P("PREMISE IAM DATA", className="eyebrow"),
                            html.H1([html.Em("premise"), " scenario explorer"]),
                            html.P(
                                "Compare the integrated-assessment pathways used to build prospective life-cycle inventories.",
                                className="intro-copy",
                            ),
                        ],
                    ),
                    html.Section(
                        className="filter-card",
                        children=[
                            html.Div(
                                className="primary-controls",
                                children=[
                                    _dropdown(
                                        "Premise version",
                                        dcc.Dropdown(
                                            id="dataset-version-dropdown",
                                            options=[
                                                {
                                                    "label": entry["label"],
                                                    "value": str(entry["id"]),
                                                }
                                                for entry in DATASET_ENTRIES
                                            ],
                                            clearable=False,
                                        ),
                                        "dataset-version-dropdown",
                                    ),
                                    _dropdown(
                                        "Topic",
                                        dcc.Dropdown(
                                            id="topic-dropdown", clearable=False
                                        ),
                                        "topic-dropdown",
                                    ),
                                    _dropdown(
                                        "Sector",
                                        dcc.Dropdown(
                                            id="sector-dropdown", clearable=False
                                        ),
                                        "sector-dropdown",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="comparison-section",
                                children=[
                                    html.Div(
                                        className="section-label-row",
                                        children=[
                                            html.Div(
                                                [
                                                    html.H2("Comparisons"),
                                                    html.P(
                                                        "Add up to six model–scenario pairs."
                                                    ),
                                                ]
                                            ),
                                            html.Span(
                                                id="comparison-count",
                                                className="count-badge",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="comparison-builder",
                                        children=[
                                            _dropdown(
                                                "IAM model",
                                                dcc.Dropdown(
                                                    id="model-dropdown", clearable=False
                                                ),
                                                "model-dropdown",
                                            ),
                                            _dropdown(
                                                "Scenario",
                                                dcc.Dropdown(
                                                    id="scenario-dropdown",
                                                    clearable=False,
                                                ),
                                                "scenario-dropdown",
                                            ),
                                            html.Button(
                                                "Add comparison",
                                                id="add-comparison-btn",
                                                n_clicks=0,
                                                className="button button-primary add-button",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        id="comparison-chips",
                                        className="comparison-chips",
                                    ),
                                    html.P(
                                        id="comparison-message",
                                        className="inline-message",
                                        role="status",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="secondary-controls",
                                children=[
                                    _dropdown(
                                        "Regions",
                                        dcc.Dropdown(id="region-dropdown", multi=True),
                                        "region-dropdown",
                                    ),
                                    html.Div(
                                        className="control-group view-mode-control",
                                        children=[
                                            html.Label("View"),
                                            dcc.RadioItems(
                                                id="view-mode-radio",
                                                options=[
                                                    {
                                                        "label": "Absolute",
                                                        "value": "absolute",
                                                    },
                                                    {
                                                        "label": "Relative shares",
                                                        "value": "relative",
                                                    },
                                                ],
                                                value="absolute",
                                                inline=True,
                                            ),
                                            html.Small(id="view-mode-help"),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="filter-actions",
                                children=[
                                    html.Button(
                                        "Download current view (CSV)",
                                        id="export-displayed-btn",
                                        n_clicks=0,
                                        className="button button-secondary",
                                    ),
                                    html.Button(
                                        "Download selected scenarios (CSV)",
                                        id="export-all-btn",
                                        n_clicks=0,
                                        className="button button-secondary",
                                    ),
                                    html.Div(
                                        className="share-control",
                                        children=[
                                            dcc.Clipboard(
                                                id="share-link-copy",
                                                title="Copy a link to this view",
                                                className="share-clipboard",
                                            ),
                                            html.A(
                                                "Share current view",
                                                id="share-view-link",
                                                className="share-link",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.P(
                                id="initialization-notice",
                                className="state-notice",
                                role="status",
                            ),
                        ],
                        **{"aria-label": "Scenario filters"},
                    ),
                    html.Div(
                        id="explorer-status",
                        className="sr-only",
                        role="status",
                        **{"aria-live": "polite"},
                    ),
                    dcc.Loading(
                        id="graphs-loading",
                        type="circle",
                        color="#008a82",
                        children=html.Div(id="graphs-container"),
                    ),
                ],
            ),
            html.Footer(
                [
                    html.Span(
                        "Paul Scherrer Institute · Laboratory for Energy Systems Analyses"
                    ),
                    html.A("Contact", href="mailto:romain.sacchi@psi.ch"),
                ]
            ),
        ],
    )


app.layout = build_layout


@app.callback(
    Output("active-view-store", "data"),
    Output("initialization-notice", "children"),
    Input("explorer-url", "search"),
    State("saved-view-store", "data"),
)
def initialize_view(search: str | None, _saved_state: object):
    # An explicit URL reproduces a shared view. A clean URL must always use the
    # application defaults rather than selections persisted by an older visit.
    requested = parse_view_query(search) if search else None
    state, notes = validate_view_state(requested)
    return state, " ".join(notes)


@app.callback(
    Output("dataset-version-dropdown", "value"),
    Input("active-view-store", "data"),
)
def apply_initial_version(state: dict[str, object] | None):
    return (state or {}).get("version", DEFAULT_DATASET)


@app.callback(
    Output("topic-dropdown", "options"),
    Output("topic-dropdown", "value"),
    Input("dataset-version-dropdown", "value"),
    State("active-view-store", "data"),
)
def update_topic_options(dataset_id: str, initial_state: dict[str, object] | None):
    frame = get_dataset(dataset_id)
    available = set(frame["sector"].dropna().unique())
    options = [
        {"label": topic["label"], "value": topic["id"]}
        for topic in TOPICS
        if any(sector in available for sector in topic["sectors"])
        or (topic["id"] == "energy" and bool(available - set(SECTOR_TO_TOPIC)))
    ]
    initial_sector = str((initial_state or {}).get("sector", DEFAULT_SECTOR))
    preferred = topic_for_sector(initial_sector)
    values = {option["value"] for option in options}
    return options, preferred if preferred in values else options[0]["value"]


@app.callback(
    Output("sector-dropdown", "options"),
    Output("sector-dropdown", "value"),
    Input("dataset-version-dropdown", "value"),
    Input("topic-dropdown", "value"),
    State("sector-dropdown", "value"),
    State("active-view-store", "data"),
)
def update_sector_options(
    dataset_id: str,
    topic_id: str,
    current_sector: str | None,
    initial_state: dict[str, object] | None,
):
    sectors = sectors_for_topic(get_dataset(dataset_id), topic_id)
    options = [{"label": sector, "value": sector} for sector in sectors]
    initial_sector = str((initial_state or {}).get("sector", DEFAULT_SECTOR))
    if current_sector in sectors:
        selected = current_sector
    elif (
        initial_sector in sectors and (initial_state or {}).get("version") == dataset_id
    ):
        selected = initial_sector
    else:
        selected = DEFAULT_SECTOR if DEFAULT_SECTOR in sectors else sectors[0]
    return options, selected


@app.callback(
    Output("model-dropdown", "options"),
    Output("model-dropdown", "value"),
    Input("dataset-version-dropdown", "value"),
    Input("sector-dropdown", "value"),
    State("model-dropdown", "value"),
)
def update_model_options(dataset_id: str, sector: str, current_model: str | None):
    pairs = available_pairs(get_dataset(dataset_id), sector)
    models = sorted({pair["model"] for pair in pairs})
    options = [{"label": model.upper(), "value": model} for model in models]
    preferred = DEFAULT_PAIR["model"] if DEFAULT_PAIR["model"] in models else models[0]
    return options, current_model if current_model in models else preferred


@app.callback(
    Output("scenario-dropdown", "options"),
    Output("scenario-dropdown", "value"),
    Input("dataset-version-dropdown", "value"),
    Input("sector-dropdown", "value"),
    Input("model-dropdown", "value"),
    State("scenario-dropdown", "value"),
)
def update_scenario_options(
    dataset_id: str, sector: str, model: str, current_scenario: str | None
):
    pairs = available_pairs(get_dataset(dataset_id), sector)
    scenarios = [pair["scenario"] for pair in pairs if pair["model"] == model]
    options = [{"label": scenario, "value": scenario} for scenario in scenarios]
    preferred = (
        DEFAULT_PAIR["scenario"]
        if model == DEFAULT_PAIR["model"] and DEFAULT_PAIR["scenario"] in scenarios
        else scenarios[0]
    )
    return options, current_scenario if current_scenario in scenarios else preferred


@app.callback(
    Output("comparison-store", "data"),
    Output("comparison-message", "children"),
    Input("active-view-store", "data"),
    Input("dataset-version-dropdown", "value"),
    Input("sector-dropdown", "value"),
    Input("add-comparison-btn", "n_clicks"),
    Input({"type": "remove-pair", "token": ALL}, "n_clicks"),
    State("comparison-store", "data"),
    State("model-dropdown", "value"),
    State("scenario-dropdown", "value"),
)
def manage_comparisons(
    initial_state: dict[str, object] | None,
    dataset_id: str,
    sector: str,
    _add_clicks: int,
    _remove_clicks: list[int],
    current_pairs: object,
    model: str,
    scenario: str,
):
    if not dataset_id or not sector:
        raise PreventUpdate
    valid = available_pairs(get_dataset(dataset_id), sector)
    valid_tokens = {pair_token(pair["model"], pair["scenario"]) for pair in valid}
    trigger = ctx.triggered_id

    if trigger == "active-view-store":
        candidates = normalize_pairs((initial_state or {}).get("pairs"))
    else:
        candidates = normalize_pairs(current_pairs)
    candidates = [
        pair
        for pair in candidates
        if pair_token(pair["model"], pair["scenario"]) in valid_tokens
    ]

    message = ""
    if trigger == "add-comparison-btn":
        candidate = {"model": model, "scenario": scenario}
        token = pair_token(model, scenario)
        if token not in valid_tokens:
            message = "This comparison is unavailable for the selected sector."
        elif candidate in candidates:
            message = "That model–scenario pair is already included."
        elif len(candidates) >= MAX_COMPARISONS:
            message = "Remove a comparison before adding another; the limit is six."
        else:
            candidates.append(candidate)
    elif isinstance(trigger, dict) and trigger.get("type") == "remove-pair":
        candidates = [
            pair
            for pair in candidates
            if pair_token(pair["model"], pair["scenario"]) != trigger.get("token")
        ]
    elif not candidates and valid:
        candidates = default_comparisons_for(valid)

    return candidates[:MAX_COMPARISONS], message


@app.callback(
    Output("comparison-chips", "children"),
    Output("comparison-count", "children"),
    Input("comparison-store", "data"),
)
def render_comparison_chips(value: object):
    pairs = normalize_pairs(value)
    chips = [
        html.Span(
            className="comparison-chip",
            children=[
                html.Span(
                    [html.Strong(pair["model"].upper()), f" · {pair['scenario']}"]
                ),
                html.Button(
                    "×",
                    id={"type": "remove-pair", "token": pair_token(**pair)},
                    n_clicks=0,
                    title=f"Remove {pair['model']} {pair['scenario']}",
                    **{"aria-label": f"Remove {pair['model']} {pair['scenario']}"},
                ),
            ],
        )
        for pair in pairs
    ]
    return chips, f"{len(pairs)} / {MAX_COMPARISONS}"


@app.callback(
    Output("region-dropdown", "options"),
    Output("region-dropdown", "value"),
    Input("dataset-version-dropdown", "value"),
    Input("sector-dropdown", "value"),
    Input("comparison-store", "data"),
    State("region-dropdown", "value"),
    State("active-view-store", "data"),
)
def update_region_options(
    dataset_id: str,
    sector: str,
    selected_pairs: object,
    current_regions: list[str] | None,
    initial_state: dict[str, object] | None = None,
):
    frame = get_dataset(dataset_id)
    pairs = normalize_pairs(selected_pairs)
    regions = common_regions(frame, sector, pairs)
    selected_data = filter_frame(frame, sector, pairs)
    derived_world = not selected_data.loc[
        selected_data["region"].eq("World")
        & selected_data["region_source"].eq("derived")
    ].empty
    options = [
        {
            "label": (
                "World (derived for some comparisons)"
                if region == "World" and derived_world
                else region
            ),
            "value": region,
        }
        for region in regions
    ]
    requested = current_regions or []
    if ctx.triggered_id == "comparison-store" and initial_state:
        initial_regions = initial_state.get("regions")
        if isinstance(initial_regions, list):
            requested = initial_regions
    selected = [region for region in requested if region in regions]
    if not selected:
        selected = ["World"] if "World" in regions else regions[:1]
    return options, selected


@app.callback(
    Output("view-mode-radio", "options"),
    Output("view-mode-radio", "value"),
    Output("view-mode-help", "children"),
    Input("dataset-version-dropdown", "value"),
    Input("sector-dropdown", "value"),
    Input("comparison-store", "data"),
    Input("region-dropdown", "value"),
    State("view-mode-radio", "value"),
    State("active-view-store", "data"),
)
def update_view_mode(
    dataset_id: str,
    sector: str,
    selected_pairs: object,
    regions: list[str] | None,
    current_mode: str,
    initial_state: dict[str, object] | None,
):
    selected = filter_frame(
        get_dataset(dataset_id), sector, normalize_pairs(selected_pairs), regions or []
    )
    allowed = sector_supports_relative(sector, selected)
    options = [
        {"label": "Absolute", "value": "absolute"},
        {"label": "Relative shares", "value": "relative", "disabled": not allowed},
    ]
    requested = current_mode
    if initial_state:
        initial_pairs = normalize_pairs(initial_state.get("pairs"))
        initial_regions = initial_state.get("regions")
        initial_matches = (
            initial_state.get("version") == dataset_id
            and initial_state.get("sector") == sector
            and initial_pairs == normalize_pairs(selected_pairs)
            and isinstance(initial_regions, list)
            and initial_regions == (regions or [])
        )
        if initial_matches:
            requested = str(initial_state.get("mode", current_mode))
    value = requested if requested == "relative" and allowed else "absolute"
    help_text = (
        "Compare the contribution mix independently of total volume."
        if allowed
        else "Relative shares are unavailable for indicators, efficiencies, or negative values."
    )
    return options, value, help_text


def _comparison_card(
    frame: pd.DataFrame,
    pair: dict[str, str],
    sector: str,
    mode: str,
    y_range: tuple[float, float] | None,
) -> html.Article:
    model = pair["model"]
    scenario = pair["scenario"]
    subset = frame.loc[
        frame["model"].eq(model) & frame["scenario"].eq(scenario)
    ]
    derived = not subset.loc[
        subset["region_source"].eq("derived") & subset["region"].eq("World")
    ].empty
    ssp_name, ssp_text, rcp_name, rcp_text = scenario_details(scenario)
    details = [
        (
            html.Div([html.Strong(ssp_name), html.P(ssp_text)])
            if ssp_name or ssp_text
            else None
        ),
        (
            html.Div([html.Strong(rcp_name), html.P(rcp_text)])
            if rcp_name or rcp_text
            else None
        ),
    ]
    details = [item for item in details if item is not None]
    filename = re.sub(r"[^a-z0-9]+", "-", f"{model}-{scenario}-{sector}".lower()).strip(
        "-"
    )
    return html.Article(
        className="result-card",
        children=[
            html.Div(
                className="result-card-header",
                children=[
                    html.Div(
                        [
                            html.P(model.upper(), className="model-label"),
                            html.H2(scenario),
                        ]
                    ),
                    html.Div(
                        className="result-badges",
                        children=[
                            (
                                html.Span(
                                    "Derived World", className="badge badge-derived"
                                )
                                if derived
                                else None
                            ),
                            html.Span(
                                UNITS.get(sector, {}).get("label", "Value"),
                                className="badge",
                            ),
                        ],
                    ),
                ],
            ),
            dcc.Graph(
                figure=build_figure(subset, sector, mode, y_range),
                responsive=True,
                style={"height": "500px"},
                config={
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "filename": filename,
                        "format": "png",
                        "scale": 2,
                    },
                },
                className="result-graph",
            ),
            (
                html.Details(
                    className="scenario-details",
                    children=[html.Summary("Scenario details"), *details],
                )
                if details
                else None
            ),
        ],
    )


def _single_series_comparison_card(
    frame: pd.DataFrame,
    pairs: list[dict[str, str]],
    sector: str,
    mode: str,
    y_range: tuple[float, float] | None,
) -> html.Article:
    derived = not frame.loc[
        frame["region_source"].eq("derived") & frame["region"].eq("World")
    ].empty
    region_count = frame["region"].astype(str).nunique()
    figure_height = max(500, ((region_count + 2) // 3) * 360)
    filename = _safe_filename(f"model-scenario-comparison-{sector}")
    return html.Article(
        className="result-card",
        children=[
            html.Div(
                className="result-card-header",
                children=[
                    html.Div(
                        [
                            html.P(
                                "MODEL · SCENARIO COMPARISON", className="model-label"
                            ),
                            html.H2(
                                f"{len(pairs)} pathways · {region_count} "
                                f"{'region' if region_count == 1 else 'regions'}"
                            ),
                        ]
                    ),
                    html.Div(
                        className="result-badges",
                        children=[
                            (
                                html.Span(
                                    "Derived World", className="badge badge-derived"
                                )
                                if derived
                                else None
                            ),
                            html.Span(
                                UNITS.get(sector, {}).get("label", "Value"),
                                className="badge",
                            ),
                        ],
                    ),
                ],
            ),
            dcc.Graph(
                figure=build_single_series_figure(frame, sector, mode, pairs, y_range),
                responsive=True,
                style={"height": f"{figure_height}px"},
                config={
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "filename": filename,
                        "format": "png",
                        "scale": 2,
                    },
                },
                className="result-graph",
            ),
        ],
    )


@app.callback(
    Output("graphs-container", "children"),
    Output("explorer-status", "children"),
    Input("comparison-store", "data"),
    Input("sector-dropdown", "value"),
    Input("region-dropdown", "value"),
    Input("view-mode-radio", "value"),
    Input("dataset-version-dropdown", "value"),
)
def update_graphs(
    selected_pairs: object,
    selected_sector: str,
    selected_regions: list[str] | None,
    mode: str,
    selected_file: str,
):
    pairs = normalize_pairs(selected_pairs)
    if not pairs:
        return (
            html.Div(
                "Add a model–scenario pair to begin comparing pathways.",
                className="empty-state",
            ),
            "No comparisons selected.",
        )
    if not selected_regions:
        return (
            html.Div("Select at least one region.", className="empty-state"),
            "No regions selected.",
        )

    raw = filter_frame(
        get_dataset(selected_file), selected_sector, pairs, selected_regions
    )
    if raw.empty:
        return (
            html.Div("No data match this view.", className="empty-state"),
            "No matching data.",
        )

    y_range = None
    if mode != "relative":
        totals = raw.groupby(["model", "scenario", "region", "year"], observed=True)[
            "val"
        ].sum()
        if not totals.empty:
            minimum = min(0.0, float(totals.min()))
            maximum = max(0.0, float(totals.max()))
            padding = (maximum - minimum) * 0.05 or 1.0
            y_range = (minimum - (padding if minimum < 0 else 0), maximum + padding)

    derived = not raw.loc[
        raw["region_source"].eq("derived") & raw["region"].eq("World")
    ].empty
    context = html.Section(
        className="sector-context",
        children=[
            html.Div(
                [
                    html.P("SELECTED SECTOR", className="eyebrow"),
                    html.H2(selected_sector),
                    html.P(UNITS.get(selected_sector, {}).get("expl_text", "")),
                ]
            ),
            (
                html.Div(
                    className="provenance-note",
                    children=[
                        html.Span("Derived World", className="badge badge-derived"),
                        html.P(
                            "Some World series are sums of non-overlapping IMAGE regions; reported World values are never overwritten."
                        ),
                    ],
                )
                if derived
                else None
            ),
        ],
    )
    combined = is_single_series_comparison(raw)
    if combined:
        cards = [
            _single_series_comparison_card(raw, pairs, selected_sector, mode, y_range)
        ]
    else:
        cards = [
            _comparison_card(raw, pair, selected_sector, mode, y_range)
            for pair in pairs
        ]
    grid_class = "results-grid single-result" if len(cards) == 1 else "results-grid"
    status = (
        f"Rendered {len(pairs)} model–scenario pathways across "
        f"{raw['region'].astype(str).nunique()} regions in one comparison chart."
        if combined
        else f"Rendered {len(cards)} comparison charts."
    )
    return [
        context,
        html.Div(cards, className=grid_class),
    ], status


def _safe_filename(value: str) -> str:
    sanitized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-+", "-", sanitized)


@app.callback(
    Output("download-data", "data"),
    Input("export-displayed-btn", "n_clicks"),
    State("comparison-store", "data"),
    State("sector-dropdown", "value"),
    State("region-dropdown", "value"),
    State("dataset-version-dropdown", "value"),
    prevent_initial_call=True,
)
def export_displayed(
    n_clicks: int,
    selected_pairs: object,
    sector: str,
    regions: list[str],
    dataset_id: str,
):
    if not n_clicks:
        raise PreventUpdate
    frame = filter_frame(
        get_dataset(dataset_id), sector, normalize_pairs(selected_pairs), regions
    )
    if frame.empty:
        raise PreventUpdate
    frame = frame.drop(
        columns=[column for column in ["Unnamed: 0"] if column in frame.columns]
    )
    filename = f"premise-{dataset_id}-{_safe_filename(sector)}-current-view.csv"
    return dcc.send_data_frame(frame.to_csv, filename, index=False)


@app.callback(
    Output("download-data", "data", allow_duplicate=True),
    Input("export-all-btn", "n_clicks"),
    State("comparison-store", "data"),
    State("dataset-version-dropdown", "value"),
    prevent_initial_call=True,
)
def export_selected(n_clicks: int, selected_pairs: object, dataset_id: str):
    if not n_clicks:
        raise PreventUpdate
    pairs = normalize_pairs(selected_pairs)
    frame = get_dataset(dataset_id).copy()
    pair_mask = pd.Series(False, index=frame.index)
    for pair in pairs:
        pair_mask |= frame["model"].eq(pair["model"]) & frame["scenario"].eq(
            pair["scenario"]
        )
    frame = frame.loc[pair_mask]
    frame = frame.drop(
        columns=[column for column in ["Unnamed: 0"] if column in frame.columns]
    )
    if frame.empty:
        raise PreventUpdate
    filename = f"premise-{dataset_id}-selected-scenarios.csv"
    return dcc.send_data_frame(frame.to_csv, filename, index=False)


@app.callback(
    Output("saved-view-store", "data"),
    Output("share-link-copy", "content"),
    Output("share-view-link", "href"),
    Input("dataset-version-dropdown", "value"),
    Input("sector-dropdown", "value"),
    Input("comparison-store", "data"),
    Input("region-dropdown", "value"),
    Input("view-mode-radio", "value"),
    State("explorer-url", "href"),
)
def save_view_state(
    dataset_id: str,
    sector: str,
    selected_pairs: object,
    regions: list[str] | None,
    mode: str,
    current_href: str | None,
):
    if not all([dataset_id, sector, mode]) or regions is None:
        return no_update, no_update, no_update
    state = {
        "revision": VIEW_STATE_REVISION,
        "version": dataset_id,
        "sector": sector,
        "pairs": normalize_pairs(selected_pairs),
        "regions": regions,
        "mode": mode,
    }
    parts = urlsplit(current_href or "")
    share_url = urlunsplit(
        (parts.scheme, parts.netloc, parts.path, serialize_view_state(state), "")
    )
    return state, share_url, share_url


app.clientside_callback(
    """
    function(href) {
        if (!href) {
            return window.dash_clientside.no_update;
        }
        const url = new URL(href, window.location.href);
        window.history.replaceState({}, "", url.pathname + url.search);
        return url.search;
    }
    """,
    Output("url-sync-store", "data"),
    Input("share-view-link", "href"),
    prevent_initial_call=True,
)


if __name__ == "__main__":
    app.run(debug=True)
