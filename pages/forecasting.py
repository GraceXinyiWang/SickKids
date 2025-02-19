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
file_path = os.path.join(os.getcwd(), "Inpatient_Events_In_Hospital.xlsx")
df = pd.read_excel(file_path)

# ✅ Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# ✅ Count the number of patients per day
daily_volume = df.groupby('Date').size().reset_index(name='PatientVolume')

# ✅ Add a forecasted column (Basic Example: Increase by 5%)
daily_volume['ForecastedVolume'] = daily_volume['PatientVolume'] * 1.05

# ✅ Create a Forecasting Plot (Initially Empty)
fig_forecast = px.line(title="Forecasted Patient Volume (Click 'Display Plot')")

# ✅ Define Forecasting Page Layout
layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row([
            dbc.Col([
                html.H1("Forecasting Tool", className="text-center"),
                html.P("This is where forecasting models and visualizations will go."),
            ], width=12)
        ]),

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

        # ✅ Graph placeholder (Initially Hidden)
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="forecast-graph", figure=fig_forecast, style={"display": "none"})  
            ], width=12)
        ]),

        # ✅ Download Component
        dcc.Download(id="download-excel")
    ],
    style={"backgroundColor": "#e3f2fd", "minHeight": "100vh", "padding": "20px"}
)

# 📌 Callbacks for buttons
@dash.callback(
    Output("forecast-graph", "figure"),
    Output("forecast-graph", "style"),
    Input("display-plot-btn", "n_clicks"),
    prevent_initial_call=True
)
def display_plot(n_clicks):
    # ✅ Create a Forecasting Plot with Real Data
    fig = px.line(
        daily_volume, x="Date", y=["PatientVolume", "ForecastedVolume"],
        title="Forecasted Patient Volume",
        labels={"value": "Number of Patients", "variable": "Type"},
        color_discrete_map={"PatientVolume": "blue", "ForecastedVolume": "red"}
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
        daily_volume.to_excel(writer, sheet_name="Forecast", index=False)
    output.seek(0)
    return dcc.send_bytes(output.getvalue(), filename="forecast_data.xlsx")
