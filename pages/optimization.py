import dash
from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import os

# ✅ Register the Optimization Page
dash.register_page(__name__, path="/optimization")

# 📌 Load Data
file_nurse = os.path.join(os.getcwd(), "Prediction_Nurse.xlsx")
file_hppd = os.path.join(os.getcwd(), "Hppd_Prediction_total.xlsx")

# ✅ Load datasets
hppd_file_path = "Hppd_Prediction_total.xlsx"
nurse_file_path = "Prediction_Nurse.xlsx"

df_nurse = pd.read_excel(file_nurse)
df_hppd = pd.read_excel(file_hppd)

# ✅ Transform Data: Convert First Column to 'Date'
df_nurse = df_nurse.rename(columns={df_nurse.columns[0]: "Date"})
df_hppd = df_hppd.rename(columns={df_hppd.columns[0]: "Date"})

df_nurse["Date"] = pd.to_datetime(df_nurse["Date"])
df_hppd["Date"] = pd.to_datetime(df_hppd["Date"])

# ✅ Reshape Data to Long Format
df_nurse_melted = df_nurse.melt(id_vars=["Date"], var_name="UnitCode", value_name="PredictedNurses")
df_hppd_melted = df_hppd.melt(id_vars=["Date"], var_name="UnitCode", value_name="PredictedHPPD")

# ✅ Merge the Two DataFrames on Date & UnitCode
df_merged = pd.merge(df_nurse_melted, df_hppd_melted, on=["Date", "UnitCode"], how="inner")

# ✅ Get Unique Unit Codes for Dropdown
unit_codes = df_merged["UnitCode"].unique()

# ✅ Dash Layout
layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row([
            dbc.Col(html.H1("Optimization Dashboard", className="text-center mb-4"), width=12)
        ]),

        # ✅ Dropdown Selection
        dbc.Row([
            dbc.Col([
                html.Label("Select a Unit Code:", className="fw-bold"),
                dcc.Dropdown(
                    id="unit-dropdown",
                    options=[{"label": unit, "value": unit} for unit in unit_codes],
                    value=unit_codes[0],  # Default to the first unit
                    clearable=False,
                    style={"width": "50%"}
                ),
            ], width=6)
        ], className="mb-4"),

        # ✅ Add Space
        html.Br(),

        # ✅ Buttons for Downloading Files
        dbc.Row([
            dbc.Col(
                dbc.Button("Download HPPD Data", id="download-hppd-btn", color="primary", style={"width": "100%"}),
                width=3
            ),
            dbc.Col(
                dbc.Button("Download Nurse Data", id="download-nurse-btn", color="secondary", style={"width": "100%"}),
                width=3
            ),
        ], className="mb-4"),

        # ✅ First Graph: Predicted Nurses
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="nurses-graph")
            ], width=12)
        ], className="mb-4"),

        # ✅ Second Graph: Predicted HPPD
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="hppd-graph")
            ], width=12)
        ]),
        
        # ✅ Download Components
        dcc.Download(id="download-hppd"),
        dcc.Download(id="download-nurse"),
    ],
    style={"padding": "20px"}
)


# 📌 Callback to Update Graphs Based on Unit Code Selection
@dash.callback(
    [Output("nurses-graph", "figure"), Output("hppd-graph", "figure")],
    [Input("unit-dropdown", "value")]
)
def update_graphs(selected_unit):
    # ✅ Filter Data for Selected Unit
    df_filtered = df_merged[df_merged["UnitCode"] == selected_unit]

    # ✅ Create Line Charts
    fig_nurses = px.line(
        df_filtered, x="Date", y="PredictedNurses",
        title=f"Predicted Nurses for {selected_unit}",
        labels={"PredictedNurses": "Nurses"},
        markers=True
    )

    fig_hppd = px.line(
        df_filtered, x="Date", y="PredictedHPPD",
        title=f"Predicted HPPD for {selected_unit}",
        labels={"PredictedHPPD": "HPPD"},
        markers=True
    )

    return fig_nurses, fig_hppd

# ✅ Callbacks to Handle Downloads
@dash.callback(
    Output("download-hppd", "data"),
    Input("download-hppd-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_hppd(n_clicks):
    return dcc.send_file(hppd_file_path)

@dash.callback(
    Output("download-nurse", "data"),
    Input("download-nurse-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_nurse(n_clicks):
    return dcc.send_file(nurse_file_path)