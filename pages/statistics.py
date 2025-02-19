import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import os
import plotly.express as px

# ✅ Register the Statistics Dashboard
dash.register_page(__name__, path="/")

# 📌 Load dataset
file_path = os.path.join(os.getcwd(), "Inpatient_Events_In_Hospital.xlsx")
df = pd.read_excel(file_path)

# ✅ Convert Date column to datetime and filter relevant years
df['Date'] = pd.to_datetime(df['Date'])
df = df[(df['Date'].dt.year >= 2022) & (df['Date'].dt.year <= 2024)]

# ✅ Combine Unit Codes
df['UnitCode'] = df['UnitCode'].replace(['6A', '6B'], '6AB')
df['UnitCode'] = df['UnitCode'].replace(['7B', '7C', '7D'], '7BCD')

# ✅ Patient Volume Calculation
daily_volume = df.groupby('Date').size().reset_index(name='PatientVolume')
daily_volume['DayOfWeek'] = daily_volume['Date'].dt.day_name()
daily_volume['Month'] = daily_volume['Date'].dt.month_name()

# ✅ Extract hospital unit-wise patient counts
unit_counts = df.groupby('UnitCode').size().reset_index(name='PatientCount')
unit_counts = unit_counts.sort_values(by='PatientCount', ascending=False).head(10)

# ✅ Find today's and yesterday's patient count
latest_date = df['Date'].max()
previous_date = df[df['Date'] < latest_date]['Date'].max()
patients_today = df[df['Date'] == latest_date].shape[0]
patients_yesterday = df[df['Date'] == previous_date].shape[0]

# ✅ Calculate percentage change
if patients_yesterday > 0:
    patient_change_percent = ((patients_today - patients_yesterday) / patients_yesterday) * 100
else:
    patient_change_percent = 0

trend_icon = "📈" if patient_change_percent > 0 else "📉"
trend_text = f"{trend_icon} {patient_change_percent:.2f}% (over the last day)"
trend_class = "text-success" if patient_change_percent > 0 else "text-danger"

# ✅ Patient Summary Card
patient_summary = dbc.Card(
    dbc.CardBody([
        html.H4("Number of Patients Today", className="card-title"),
        html.H1(f"{patients_today}", className="display-4"),
        html.P(trend_text, className=trend_class),
    ]), className="mb-4 shadow-sm",
    style={
        "backgroundColor": "rgba(255, 255, 255, 0.5)",  
        "boxShadow": "2px 2px 10px rgba(0, 0, 0, 0.1)",  
        "borderRadius": "15px",  
    }
)

# ✅ **Get patient count per unit for today and yesterday**
latest_counts = df[df['Date'] == latest_date].groupby('UnitCode').size().reset_index(name='TodayCount')
previous_counts = df[df['Date'] == previous_date].groupby('UnitCode').size().reset_index(name='YesterdayCount')

# ✅ **Merge today and yesterday's counts**
unit_changes = latest_counts.merge(previous_counts, on="UnitCode", how="left").fillna(0)

# ✅ **Calculate percentage change**
unit_changes['PercentageChange'] = ((unit_changes['TodayCount'] - unit_changes['YesterdayCount']) / unit_changes['YesterdayCount']) * 100

# ✅ **Sort and select the top 3 units for display**
top_units = unit_changes.sort_values(by='TodayCount', ascending=False).head(3)

# ✅ **Assign trend colors**
unit_cards = dbc.Row([
    dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H5(top_units.iloc[i]["UnitCode"], className="card-title"),
                html.H2(f"{top_units.iloc[i]['TodayCount']:.0f}"),
                html.P(
                    f"{'🟢 +' if top_units.iloc[i]['PercentageChange'] > 0 else '🔴 '}{top_units.iloc[i]['PercentageChange']:.2f}%",
                    style={"color": "green" if top_units.iloc[i]['PercentageChange'] > 0 else "red", "font-weight": "bold"}
                )
            ]), style={
                "backgroundColor": "rgba(255, 255, 255, 0.5)",  
                "boxShadow": "2px 2px 10px rgba(0, 0, 0, 0.1)",  
                "borderRadius": "15px",  
            }
        ), width=4
    ) for i in range(len(top_units))
], className="mb-4")

# 📊 Create Charts
fig_units = px.bar(
    unit_counts, x="PatientCount", y="UnitCode", orientation="h",
    title="Top 10 Units for In-Hospital Patients (2022-2024)",
    labels={"UnitCode": "Hospital Unit", "PatientCount": "Patient Count"},
    color="PatientCount", color_continuous_scale="Viridis"
)

fig_day = px.box(
    daily_volume, x="DayOfWeek", y="PatientVolume",
    title="Patient Volume by Day of the Week (2022-2024)",
    labels={"DayOfWeek": "Day of the Week", "PatientVolume": "Number of Patients"},
    boxmode="group"
)

fig_month = px.box(
    daily_volume, x="Month", y="PatientVolume",
    title="Patient Volume by Month (2022-2024)",
    labels={"Month": "Month", "PatientVolume": "Number of Patients"},
    category_orders={"Month": [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]}, boxmode="group"
)

# 📌 **Final Page Layout (Fixed Layout: 2 Rows, 2 Columns)**
layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row([
            # ✅ First row, first column (Summary + Unit Cards)
            dbc.Col([
                patient_summary,
                unit_cards,
            ], width=4, style={"margin-left": "40px", "margin-top": "30px","flex":"1"}),

            # ✅ First row, second column (Box Plot for Days)
            dbc.Col([
                dcc.Graph(figure=fig_day, style={"width": "100%"}),
            ], width=6),
        ]),
        
        dbc.Row([
            # ✅ Second row, first column (Top 10 Units - Bar Chart)
            dbc.Col([
                html.Br(),
                dcc.Graph(figure=fig_units, style={"width": "100%"}),
            ], width=4, style={"margin-left": "40px", "margin-top": "30px","flex":"1"}),

            # ✅ Second row, second column (Box Plot for Months)
            dbc.Col([
                html.Br(),
                dcc.Graph(figure=fig_month, style={"width": "100%"}),
            ], width=6),
        ]),
    ],
    style={"backgroundColor": "#e3f2fd", "minHeight": "100vh", "padding": "20px"}
)
