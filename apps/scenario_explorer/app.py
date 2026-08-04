from __future__ import annotations

import json
import os
from pathlib import Path

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import yaml
from flask_caching import Cache

APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = APP_ROOT / "data"
REQUESTS_PREFIX = os.getenv("SCENARIO_REQUESTS_PREFIX", "/")

with (DATA_DIR / "units.yaml").open(encoding="utf-8") as f:
    units = yaml.safe_load(f)
with (DATA_DIR / "ssp_descriptions.yaml").open(encoding="utf-8") as f:
    ssp_descriptions = yaml.safe_load(f)
with (DATA_DIR / "rcp_descriptions.yaml").open(encoding="utf-8") as f:
    rcp_descriptions = yaml.safe_load(f)
with (DATA_DIR / "datasets.yaml").open(encoding="utf-8") as f:
    dataset_entries = yaml.safe_load(f)

DATASETS = {str(entry["id"]): entry for entry in dataset_entries}
DEFAULT_DATASET = "2.4.8"


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
        "CACHE_THRESHOLD": 2,
    },
)

# Load CSV with optimized dtypes
column_dtypes = {
    "region": "category",
    "variables": "category",
    "year": "int32",
    "val": "float32",
    "sector": "category",
    "model": "category",
    "scenario": "category",
    "powertrain": "category",
    "size": "category",
}

@cache.memoize(timeout=600)
def get_dataset(dataset_id: str):
    path = dataset_path(dataset_id)
    print(f"[LOAD] Reading {path.name}")
    return pd.read_csv(path, dtype=column_dtypes)

def get_all_variables():
    with (DATA_DIR / "variable_catalog.json").open(encoding="utf-8") as stream:
        return json.load(stream)

all_variables = get_all_variables()
colors = px.colors.qualitative.Plotly
color_map = {var: colors[i % len(colors)] for i, var in enumerate(all_variables)}

# Layout
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.A("← Premise resources", href="/")
                ], style={"width": "25%", "display": "inline-block", "fontSize": "12px", "textAlign": "left"}),
                html.Div([
                    html.A("Contact", href="mailto:romain.sacchi@psi.ch")
                ], style={"width": "25%", "display": "inline-block", "fontSize": "12px", "textAlign": "center"}),
                html.Div([
                    html.A("Documentation", href="https://premise.readthedocs.io", target="_blank", rel="noopener noreferrer")
                ], style={"width": "25%", "display": "inline-block", "fontSize": "12px", "textAlign": "center"}),
                html.Div([
                    html.A("Premise on GitHub", href="https://github.com/polca/premise", target="_blank", rel="noopener noreferrer")
                ], style={"width": "25%", "display": "inline-block", "fontSize": "12px", "textAlign": "right"}),
            ], style={"marginBottom": "10px"}),

            html.H1("premise scenario explorer", style={"marginBottom": "20px"}),

            html.Div([
                html.Label("Select Premise Version:"),
                dcc.Dropdown(
                    id="dataset-version-dropdown",
                    options=[
                        {"label": entry["label"], "value": str(entry["id"])}
                        for entry in dataset_entries
                    ],
                    value=DEFAULT_DATASET,
                    clearable=False,
                )
            ], style={"width": "32%", "display": "inline-block", "marginBottom": "20px", "marginRight": "1%"}),

            html.Div([
                # Model–scenario
                html.Div([
                    html.Label("Select Model-Scenario Combinations:"),
                    dcc.Dropdown(id="model-scenario-dropdown", multi=True)
                ], style={"width": "32%", "display": "inline-block", "marginRight": "1%"}),

                # Sector
                html.Div([
                    html.Label("Select Sector:"),
                    dcc.Dropdown(id="sector-dropdown")
                ], style={"width": "32%", "display": "inline-block", "marginRight": "1%"}),

                # Regions
                html.Div([
                    html.Label("Select Regions:"),
                    dcc.Dropdown(id="region-dropdown", value=["World"], multi=True)
                ], style={"width": "32%", "display": "inline-block"}),
            ], style={"marginBottom": "10px"}),

            # Put the 100% stacking toggle in its own clean row
            html.Div([
                # Relative view checkbox
                dcc.Checklist(
                    id="stack-mode-checklist",
                    options=[{"label": "Show relative shares (100%)", "value": "relative"}],
                    value=[],
                    style={"fontSize": "12px", "marginBottom": "10px"}
                ),

                # Export displayed data
                html.Button(
                    "Export displayed data",
                    id="export-displayed-btn",
                    n_clicks=0,
                    style={
                        "display": "block",
                        "width": "100%",
                        "marginBottom": "8px"
                    }
                ),

                # Export EVERYTHING
                html.Button(
                    "Export full dataset",
                    id="export-all-btn",
                    n_clicks=0,
                    style={
                        "display": "block",
                        "width": "100%"
                    }
                ),
            ], style={
                "width": "200px",  # or match the dropdown width
                "marginBottom": "20px",
            })
        ])
    ], style={"background": "#e9e9e9", "padding": "20px", "borderRadius": "5px", "marginBottom": "20px"}),

    dcc.Store(id="data-store"),
    dcc.Download(id="download-data"),
    html.Div(id="graphs-container")
])

# Callback: update dropdowns
@app.callback(
    Output("model-scenario-dropdown", "options"),
    Output("model-scenario-dropdown", "value"),
    Output("sector-dropdown", "options"),
    Output("sector-dropdown", "value"),
    Input("dataset-version-dropdown", "value"),
)
def update_dropdowns(selected_file):
    df = get_dataset(selected_file)
    model_scenarios = df.drop_duplicates(subset=["model", "scenario"]).copy()
    model_scenarios["combined"] = model_scenarios["model"].astype(str) + " - " + model_scenarios["scenario"].astype(str)
    model_options = model_scenarios["combined"].tolist()

    sectors = sorted(df["sector"].unique())
    sectors = [
        "GMST increase", "Carbon Dioxide emissions", "Population", "Gross Domestic Product"
    ] + [s for s in sectors if s not in ("GMST increase", "Carbon Dioxide emissions", "Population", "Gross Domestic Product")]

    return (
        [{"label": s, "value": s} for s in model_options],
        [model_options[0]],
        [{"label": s, "value": s} for s in sectors],
        sectors[0],
    )

# Callback: update regions
@app.callback(
    Output("region-dropdown", "options"),
    Output("region-dropdown", "value"),
    Input("sector-dropdown", "value"),
    Input("model-scenario-dropdown", "value"),
    State("dataset-version-dropdown", "value"),
    State("region-dropdown", "value"),
)
def update_region_options(selected_sector, selected_combinations, selected_file, current_regions):
    # If nothing is selected yet, don't touch the dropdown
    if not selected_sector or not selected_combinations:
        raise PreventUpdate

    df = get_dataset(selected_file)

    # Filter by sector first
    df = df[df["sector"] == selected_sector]

    # Build the same "model - scenario" combined string as in the first callback
    df = df.copy()  # avoid SettingWithCopy warnings
    df["combined"] = df["model"].astype(str) + " - " + df["scenario"].astype(str)

    # Keep only rows that match one of the selected model-scenario combos
    df = df[df["combined"].isin(selected_combinations)]

    regions = sorted(df["region"].unique())
    options = [{"label": r, "value": r} for r in regions]

    # Default to World on first load; otherwise keep current valid selections.
    if not current_regions:
        next_regions = ["World"] if "World" in regions else ([regions[0]] if regions else [])
    else:
        next_regions = [r for r in current_regions if r in regions]
        if not next_regions:
            next_regions = ["World"] if "World" in regions else ([regions[0]] if regions else [])

    return options, next_regions


# Callback: generate graphs
@app.callback(
    Output("graphs-container", "children"),
    Input("model-scenario-dropdown", "value"),
    Input("sector-dropdown", "value"),
    Input("region-dropdown", "value"),
    Input("stack-mode-checklist", "value"),
    State("dataset-version-dropdown", "value"),
)
def update_graphs(selected_combinations, selected_sector, selected_regions, stack_mode, selected_file):
    # No regions -> keep current graphs until user chooses some
    if not selected_regions:
        raise PreventUpdate

    # No model–scenario -> clear graphs
    if not selected_combinations:
        return []

    df = get_dataset(selected_file)
    df = df[df["sector"] == selected_sector].copy()

    # Compute global max across all selected model-scenario combinations & regions
    global_max = 0

    for combo in selected_combinations:
        model, scenario = combo.split(" - ", 1)
        df_ms = df[(df["model"] == model) & (df["scenario"] == scenario)]

        # Filter to selected regions
        df_ms = df_ms[df_ms["region"].isin(selected_regions)]

        # Compute total value per year (summing all variables)
        totals = df_ms.groupby("year")["val"].sum()

        if not totals.empty:
            global_max = max(global_max, totals.max())

    # Edge case: no data
    if global_max == 0:
        global_max = 1

    stack_relative = bool(stack_mode and "relative" in stack_mode)
    cards = []

    for combo in selected_combinations:
        # combo looks like "model - scenario"
        try:
            model, scenario = combo.split(" - ", 1)
        except ValueError:
            # skip malformed entries just in case
            continue

        temp_df = df[(df["model"] == model) & (df["scenario"] == scenario)]

        # Ensure World rows exist / are non-zero if needed
        for year in temp_df["year"].unique():
            year_mask = (
                (df["model"] == model)
                & (df["scenario"] == scenario)
                & (df["year"] == year)
            )
            year_df = df[year_mask]

            world_mask = year_mask & (df["region"] == "World")
            world_df = df[world_mask]

            if year_df.empty:
                continue

            if world_df.empty or world_df["val"].sum() == 0:
                total_val = year_df[year_df["region"] != "World"]["val"].sum()
                if not world_df.empty:
                    df.loc[world_mask, "val"] = total_val
                else:
                    new_row = {
                        "region": "World",
                        "variables": year_df["variables"].iloc[0],
                        "year": year,
                        "val": total_val,
                        "sector": selected_sector,
                        "model": model,
                        "scenario": scenario,
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Filter for selected regions
        temp_df = df[
            (df["model"] == model)
            & (df["scenario"] == scenario)
            & (df["region"].isin(selected_regions))
        ]
        temp_df = (
            temp_df[temp_df["val"] > 0]
            .sort_values(["year", "variables"])  # <-- sort by year, then variables
        )

        # Choose line vs area + relative stacking
        if "efficiency" in selected_sector.lower():
            fig = px.line(
                temp_df,
                x="year",
                y="val",
                color="variables",
                color_discrete_map=color_map,
                line_group="region",
                facet_col="region",
                labels={
                    "val": "Value",
                    "year": "Year",
                    "variables": "Variables",
                    "region": "Region",
                },
                title=f"Model: {model} | Scenario: {scenario}",
                height=350,
            )
            yaxis_label = units.get(selected_sector, {}).get("label", "Value")

        else:
            if stack_relative:
                fig = px.area(
                    temp_df,
                    x="year",
                    y="val",
                    color="variables",
                    color_discrete_map=color_map,
                    line_group="region",
                    facet_col="region",
                    groupnorm="percent",
                    labels={
                        "val": "Share (%)",
                        "year": "Year",
                        "variables": "Variables",
                        "region": "Region",
                    },
                    title=f"Model: {model} | Scenario: {scenario}",
                    height=350,
                )
                yaxis_label = "Share (%)"
            else:
                fig = px.area(
                    temp_df,
                    x="year",
                    y="val",
                    color="variables",
                    color_discrete_map=color_map,
                    line_group="region",
                    facet_col="region",
                    labels={
                        "val": "Value",
                        "year": "Year",
                        "variables": "Variables",
                        "region": "Region",
                    },
                    title=f"Model: {model} | Scenario: {scenario}",
                    height=350,
                )
                yaxis_label = units.get(selected_sector, {}).get("label", "Value")

        fig.update_layout(yaxis_title=yaxis_label)
        # Force correct Y-axis range depending on mode
        if stack_relative:
            # Relative view → always 0–100%
            fig.update_yaxes(range=[0, 100])
        else:
            # Absolute view → global max across all scenarios
            fig.update_yaxes(range=[0, global_max])

        # SSP / RCP text
        parts = scenario.split("-")
        ssp_key = parts[0] if len(parts) > 0 else ""
        rcp_key = parts[1] if len(parts) > 1 else ""

        ssp_meta = ssp_descriptions.get(ssp_key, {})
        rcp_meta = rcp_descriptions.get(rcp_key, {})

        card = html.Div(
            [
                html.Div(
                    [
                        html.H3(
                            ssp_meta.get("name", ""),
                            style={"fontSize": "10px", "marginBottom": "2px"},
                        ),
                        html.P(
                            ssp_meta.get("description", ""),
                            style={
                                "fontSize": "8px",
                                "marginTop": "0px",
                                "marginBottom": "4px",
                            },
                        ),
                        html.H3(
                            rcp_meta.get("name", ""),
                            style={"fontSize": "10px", "marginBottom": "2px"},
                        ),
                        html.P(
                            rcp_meta.get("description", ""),
                            style={
                                "fontSize": "8px",
                                "marginTop": "0px",
                                "marginBottom": "4px",
                            },
                        ),
                    ],
                    style={"flex": "0 0 auto"},
                ),
                dcc.Graph(
                    figure=fig,
                    config={"displayModeBar": False},
                    style={"flex": "1 1 auto", "height": "340px"},
                ),
            ],
            style={
                "flex": "0 0 50%",
                "maxWidth": "50%",
                "display": "flex",
                "flexDirection": "column",
                "margin": "0 5px",
            },
        )

        cards.append(card)

    # Now group cards into rows of 2 — no chance of duplication
    rows = []
    for i in range(0, len(cards), 2):
        row_cards = cards[i : i + 2]
        rows.append(
            html.Div(
                row_cards,
                style={"display": "flex", "alignItems": "stretch"},
            )
        )

    expl_text = units.get(selected_sector, {}).get("expl_text", "")
    return [html.Div(html.P(expl_text, style={"fontSize": "16px"}))] + rows


@app.callback(
    Output("download-data", "data"),
    Input("export-displayed-btn", "n_clicks"),
    State("model-scenario-dropdown", "value"),
    State("sector-dropdown", "value"),
    State("region-dropdown", "value"),
    State("dataset-version-dropdown", "value"),
    prevent_initial_call=True,
)
def export_displayed(n_clicks, selected_combinations, selected_sector, selected_regions, selected_file):
    # No click or missing filters → no download
    if not n_clicks:
        raise PreventUpdate
    if not selected_combinations or not selected_regions or not selected_sector:
        raise PreventUpdate

    df = get_dataset(selected_file)

    # Same filtering logic as in update_graphs, but with safe string conversion
    df = df[df["sector"] == selected_sector].copy()

    # IMPORTANT: cast to string (model & scenario are categorical)
    df["combined"] = df["model"].astype(str) + " - " + df["scenario"].astype(str)

    df = df[df["combined"].isin(selected_combinations)]
    df = df[df["region"].isin(selected_regions)]

    df = df.drop(columns=[c for c in ["Unnamed: 0", "combined"] if c in df.columns])

    if df.empty:
        # Nothing to export -> don't trigger a useless download
        raise PreventUpdate

    # Return CSV
    return dcc.send_data_frame(df.to_csv, "displayed_data.csv", index=False)

@app.callback(
    Output("download-data", "data", allow_duplicate=True),
    Input("export-all-btn", "n_clicks"),
    State("dataset-version-dropdown", "value"),
    State("model-scenario-dropdown", "value"),
    prevent_initial_call=True,
)
def export_all(n_clicks, selected_file, selected_combinations):
    if not n_clicks:
        raise PreventUpdate

    df = get_dataset(selected_file).copy()

    # Safety check
    if not selected_combinations:
        raise PreventUpdate

    # Build combined key safely (model and scenario are categorical)
    df["combined"] = df["model"].astype(str) + " - " + df["scenario"].astype(str)

    # Filter by the selected model–scenario pairs
    df = df[df["combined"].isin(selected_combinations)]

    # Drop leftover helper columns
    df = df.drop(columns=[c for c in ["Unnamed: 0", "combined"] if c in df.columns])

    return dcc.send_data_frame(df.to_csv, "full_dataset_filtered.csv", index=False)


if __name__ == "__main__":
    app.run(debug=True)
