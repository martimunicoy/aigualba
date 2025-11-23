import dash
from dash import html, dcc, Input, Output, State
import sys
import os

# Add current directory to Python path for imports
sys.path.append('/app')

# Import page components
from components.navbar import create_navbar
from pages.home import create_home_page
from pages.about import create_about_page
from pages.browse import create_browse_page
from pages.submit import create_submit_page
from utils.helpers import get_backend_url, fetch_parameters, create_parameter_card, create_data_table

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, assets_folder='assets')

# Get backend URL
BACKEND_URL = get_backend_url()

# Main app layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    create_navbar(),
    html.Div(id='page-content')
], style={'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', 'margin': '0', 'padding': '0', 'backgroundColor': '#f5f5f5'})

# Callback for URL routing
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/about':
        return create_about_page()
    elif pathname == '/browse':
        return create_browse_page()
    elif pathname == '/submit':
        return create_submit_page()
    else:
        return create_home_page()

# Callback for home page live parameters
@app.callback(
    Output('live-parameters', 'children'),
    [Input('interval-home', 'n_intervals')]
)
def update_home_parameters(n):
    data = fetch_parameters(BACKEND_URL)
    if not data:
        return [html.Div("Error carregant dades", style={'color': 'red', 'textAlign': 'center'})]
    
    return [create_parameter_card(param) for param in data]

# Callback for browse page table
@app.callback(
    Output('parameters-table', 'children'),
    [Input('interval-browse', 'n_intervals')]
)
def update_browse_table(n):
    data = fetch_parameters(BACKEND_URL)
    return create_data_table(data)

# Callback for browse page chart (only if plotly is available)
try:
    import plotly.graph_objects as go
    
    @app.callback(
        Output('parameters-chart', 'figure'),
        [Input('interval-browse', 'n_intervals')]
    )
    def update_chart(n):
        try:
            data = fetch_parameters(BACKEND_URL)
            if not data:
                return {"data": [], "layout": {"title": "No hi ha dades disponibles"}}
            
            fig = go.Figure()
            for param in data:
                fig.add_trace(go.Bar(
                    name=param['name'],
                    x=[param['name']],
                    y=[float(param['value'])],
                    text=param['value'],
                    textposition='auto',
                    marker_color='#3498db'
                ))
            
            fig.update_layout(
                title="Paràmetres actuals de qualitat de l'aigua",
                xaxis_title="Paràmetres",
                yaxis_title="Valors",
                showlegend=False,
                height=400,
                template="plotly_white",
                font=dict(family="Segoe UI, Arial, sans-serif")
            )
            return fig
        except Exception as e:
            return {"data": [], "layout": {"title": f"Error carregant gràfic: {e}"}}

except ImportError:
    pass

# Callback for navigation buttons on home page
@app.callback(
    Output('url', 'pathname'),
    [Input('btn-browse', 'n_clicks'), Input('btn-submit', 'n_clicks')],
    [State('url', 'pathname')],
    prevent_initial_call=True
)
def navigate_from_buttons(browse_clicks, submit_clicks, current_path):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    # Only trigger navigation if we're on the home page
    if current_path != '/':
        return dash.no_update
    
    # Only trigger if there's an actual click (not None and greater than 0)
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'btn-browse' and browse_clicks and browse_clicks > 0:
        return '/browse'
    elif button_id == 'btn-submit' and submit_clicks and submit_clicks > 0:
        return '/submit'
    return dash.no_update

if __name__ == "__main__":
    debug_flag = os.getenv("DASH_DEBUG", "")
    is_debug = debug_flag.lower() in ("1", "true", "yes", "on")
    
    # Enable hot reloading and development tools for better development experience
    app.run(
        debug=is_debug,
        host="0.0.0.0",
        port=8050,
        dev_tools_hot_reload=is_debug,
        dev_tools_hot_reload_interval=500,  # Faster reload interval
        dev_tools_hot_reload_max_retry=3,
        dev_tools_ui=is_debug,
        dev_tools_prune_errors=True,
        dev_tools_silence_routes_logging=False if is_debug else True
    )
