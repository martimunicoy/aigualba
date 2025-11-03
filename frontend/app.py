import dash
from dash import html, dcc
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Public Water System Parameters"),
    dcc.Interval(id='interval', interval=10*1000, n_intervals=0),
    html.Div(id='parameters-table')
])

@app.callback(
    dash.dependencies.Output('parameters-table', 'children'),
    [dash.dependencies.Input('interval', 'n_intervals')]
)
def update_table(n):
    try:
        resp = requests.get(f"{BACKEND_URL}/api/parameters")
        data = resp.json()
        return html.Table([
            html.Tr([html.Th("Name"), html.Th("Value"), html.Th("Updated At")])
        ] + [
            html.Tr([html.Td(p['name']), html.Td(p['value']), html.Td(p['updated_at'])]) for p in data
        ])
    except Exception as e:
        return html.Div(f"Error fetching data: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
