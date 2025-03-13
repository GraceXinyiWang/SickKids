import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

# ✅ Initialize Dash app with multi-page support
app = dash.Dash(
    __name__,
    use_pages=True,  # ✅ Enables multi-page navigation
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,  # ✅ Avoids errors when switching pages
)

# ✅ Sidebar Navigation (Logo + Menu)
sidebar = html.Div(
    [
        html.Img(
            src="/assets/sickkids-logo-header.webp",
            style={"width": "150px", "margin-bottom": "10px"}
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Statistics Dashboard", href="/", active="exact"),
                dbc.NavLink("Forecasting Tool", href="/forecast", active="exact"),
                dbc.NavLink("Optimization Tool", href="/optimization", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style={
        "width": "15rem",
        "position": "fixed",
        "height": "100vh",
        "padding": "2rem",
        "backgroundColor": "rgba(255, 255, 255, 0.85)",  # ✅ Semi-transparent sidebar
        "boxShadow": "2px 0px 10px rgba(0, 0, 0, 0.1)",  # ✅ Soft shadow effect
        "backdropFilter": "blur(8px)",  # ✅ Optional: Adds a blur effect
    },
)

# ✅ Main Layout (Loads the correct page dynamically)
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            [
                dbc.Col(sidebar, width=2),  # Sidebar stays fixed
                dbc.Col(dash.page_container, width=10),  # ✅ Dynamically loads each page
            ]
        )
    ],
    style={"backgroundColor": "#e3f2fd", "minHeight": "100vh", "padding": "20px"},  # ✅ Light Blue Background
)

# ✅ Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
