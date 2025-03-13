import dash
from dash import dcc, html, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import io
import plotly.express as px

# ✅ Register the Forecasting Page
dash.register_page(__name__, path="/forecast")

# 📌 Load dataset
file_path = os.path.join(os.getcwd(), "prediction_patients.xlsx")
df = pd.read_excel(file_path)

# Set the first column as the index (Unit Codes)
df.set_index(df.columns[0], inplace=True)

# Transpose the DataFrame to move dates from headers to rows
df = df.T.reset_index()

# Rename columns: First column is 'Date', others are 'Unit Codes'
df = df.rename(columns={"index": "Date"})

# ✅ Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# ✅ Reshape DataFrame to long format (Unit Code as a column)
df_melted = df.melt(id_vars=["Date"], var_name="UnitCode", value_name="Patient Forecast")

# ✅ Get unique unit codes for dropdown
unit_codes = df_melted["UnitCode"].unique()

print(df_melted)

# ✅ Define Forecasting Page Layout
layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row([
            dbc.Col([
                html.H1("Forecasting Tool", className="text-center"),
                html.P("Select a Unit Code to see forecasting results."),
            ], width=12)
        ]),

        # ✅ Dropdown for Unit Code Selection
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="unit-code-dropdown",
                    options=[{"label": code, "value": code} for code in unit_codes],
                    value=unit_codes[0],  # Default selection
                    clearable=False,
                    searchable=True,
                    placeholder="Select Unit Code",
                    style={"width": "100%"}
                )
            ], width=6)
        ], className="mt-3"),

        # ✅ Buttons for download & display
        dbc.Row([
            dbc.Col(
                dbc.Button("Download Excel", id="download-excel-btn", color="primary", style={"width": "100%"}),
                width=3
            ),
            dbc.Col(
                dbc.Button("Display Plot", id="display-plot-btn", color="secondary", style={"width": "100%"}),
                width=3
            ),
        ], className="mt-3"),
        
        # ✅ Add space
        html.Br(),
        html.Br(),

        # ✅ Graph placeholder (Initially Hidden)
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="forecast-graph", style={"display": "none"})
            ], width=12)
        ]),

        # ✅ Download Component
        dcc.Download(id="download-excel")
    ],
    style={"backgroundColor": "#e3f2fd", "minHeight": "100vh", "padding": "20px"}
)

# 📌 Callbacks for updating the forecast graph
@dash.callback(
    Output("forecast-graph", "figure"),
    Output("forecast-graph", "style"),
    Input("display-plot-btn", "n_clicks"),
    State("unit-code-dropdown", "value"),
    prevent_initial_call=True
)
def display_plot(n_clicks, selected_unit):
    # ✅ Filter data based on selected unit code
    filtered_df = df_melted[df_melted["UnitCode"] == selected_unit]

    # ✅ Create a Forecasting Plot
    fig = px.line(
        filtered_df, x="Date", y=["Patient Forecast"],
        title=f"Forecasted Patient Volume for {selected_unit}",
        labels={"value": "Number of Patients", "variable": "Type"},
        color_discrete_map={"Patient Forecast": "blue"}
    )

    return fig, {"width": "100%", "display": "block"}  # Make the plot visible

@dash.callback(
    Output("download-excel", "data"),
    Input("download-excel-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_excel(n_clicks):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_melted.to_excel(writer, sheet_name="Forecast", index=False)
    output.seek(0)
    return dcc.send_bytes(output.getvalue(), filename="forecast_data.xlsx")
