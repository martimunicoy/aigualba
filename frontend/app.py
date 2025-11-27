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
from utils.helpers import get_backend_url, fetch_parameters, create_parameter_card, create_data_table, submit_sample_data, validate_sample_data

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

# Mobile menu toggle callback
@app.callback(
    [Output('nav-menu', 'className'),
     Output('mobile-menu-toggle', 'className')],
    [Input('mobile-menu-toggle', 'n_clicks')],
    [State('nav-menu', 'className'),
     State('mobile-menu-toggle', 'className')],
    prevent_initial_call=True
)
def toggle_mobile_menu(n_clicks, nav_menu_class, toggle_class):
    if n_clicks is None:
        return 'nav-menu', 'mobile-menu-toggle'
    
    # Toggle the active class
    if nav_menu_class and 'active' in nav_menu_class:
        return 'nav-menu', 'mobile-menu-toggle'
    else:
        return 'nav-menu active', 'mobile-menu-toggle active'

# Callback for sample submission
@app.callback(
    [Output('submit-sample-status', 'children'),
     Output('submit-sample-status', 'className')],
    [Input('submit-sample-button', 'n_clicks')],
    [State('sample-date', 'date'),
     State('punt-mostreig', 'value'),
     State('temperatura', 'value'),
     State('ph', 'value'),
     State('conductivitat-20c', 'value'),
     State('terbolesa', 'value'),
     State('color', 'value'),
     State('olor', 'value'),
     State('sabor', 'value'),
     State('clor-lliure', 'value'),
     State('clor-total', 'value'),
     State('recompte-escherichia-coli', 'value'),
     State('recompte-enterococ', 'value'),
     State('recompte-microorganismes-aerobis-22c', 'value'),
     State('recompte-coliformes-totals', 'value'),
     State('acid-monocloroacetic', 'value'),
     State('acid-dicloroacetic', 'value'),
     State('acid-tricloroacetic', 'value'),
     State('acid-monobromoacetic', 'value'),
     State('acid-dibromoacetic', 'value')],
    prevent_initial_call=True
)
def handle_sample_submission(n_clicks, sample_date, punt_mostreig, temperatura, ph, conductivitat_20c,
                           terbolesa, color, olor, sabor, clor_lliure, clor_total,
                           recompte_escherichia_coli, recompte_enterococ, recompte_microorganismes_aerobis_22c,
                           recompte_coliformes_totals, acid_monocloroacetic, acid_dicloroacetic,
                           acid_tricloroacetic, acid_monobromoacetic, acid_dibromoacetic):
    if not n_clicks or n_clicks == 0:
        return dash.no_update, dash.no_update
    
    # Prepare sample data
    sample_data = {
        'data': sample_date,
        'punt_mostreig': punt_mostreig,
        'temperatura': temperatura,
        'ph': ph,
        'conductivitat_20c': conductivitat_20c,
        'terbolesa': terbolesa,
        'color': color,
        'olor': olor,
        'sabor': sabor,
        'clor_lliure': clor_lliure,
        'clor_total': clor_total,
        'recompte_escherichia_coli': recompte_escherichia_coli,
        'recompte_enterococ': recompte_enterococ,
        'recompte_microorganismes_aerobis_22c': recompte_microorganismes_aerobis_22c,
        'recompte_coliformes_totals': recompte_coliformes_totals,
        'acid_monocloroacetic': acid_monocloroacetic,
        'acid_dicloroacetic': acid_dicloroacetic,
        'acid_tricloroacetic': acid_tricloroacetic,
        'acid_monobromoacetic': acid_monobromoacetic,
        'acid_dibromoacetic': acid_dibromoacetic
    }
    
    # Validate data
    validation = validate_sample_data(sample_data)
    
    # Create validation alert
    validation_alert = []
    if validation['errors']:
        validation_alert.append(
            html.Div([
                html.Ul([html.Li(error) for error in validation['errors']])
            ], className='validation-error')
        )
    
    if validation['warnings']:
        validation_alert.append(
            html.Div([
                html.H5("Avisos:", style={'marginBottom': '0.5rem'}),
                html.Ul([html.Li(warning) for warning in validation['warnings']])
            ], className='validation-warning')
        )
    
    # If there are validation errors, don't submit
    if validation['errors']:
        # Combine error message with validation alerts in submit-status
        error_content = [
            html.Div("Si us plau, corregeix els errors de validació abans d'enviar.", 
                    style={'color': '#d32f2f', 'fontWeight': '600', 'marginBottom': '1rem'})
        ]
        if validation_alert:
            error_content.extend(validation_alert)
        
        return (
            html.Div(error_content),
            "submit-status show error"
        )
    
    # Submit data
    result = submit_sample_data(BACKEND_URL, sample_data)
    
    if result['success']:
        # Safely get ID from result data
        sample_id = "N/A"
        if result.get('data') and isinstance(result['data'], dict):
            sample_id = str(result['data'].get('id', 'N/A'))
        
        success_message = html.Div([
            html.H3("✓ Mostra enviada correctament!", style={'color': '#2e7d32', 'marginBottom': '0.5rem', 'marginTop': '0'}),
            html.P(f"ID de la mostra: {sample_id}", style={'margin': '0'})
        ], style={
            'backgroundColor': '#e8f5e8',
            'border': '1px solid #4caf50',
            'borderRadius': '6px',
            'padding': '1rem',
            'color': '#2e7d32'
        })
        # Include validation warnings with success message if present
        success_content = [success_message]
        if validation_alert:
            success_content.extend(validation_alert)
        
        return (
            html.Div(success_content),
            "submit-status show success"
        )
    else:
        error_message = html.Div([
            html.H5("Error en enviar la mostra", style={'color': '#d32f2f', 'marginBottom': '0.5rem'}),
            html.P(f"Detall: {result['error']}", style={'margin': '0'})
        ], style={
            'backgroundColor': '#ffebee',
            'border': '1px solid #f44336',
            'borderRadius': '6px',
            'padding': '1rem',
            'color': '#d32f2f'
        })
        # Include validation warnings with error message if present  
        error_content = [error_message]
        if validation_alert:
            error_content.extend(validation_alert)
        
        return (
            html.Div(error_content),
            "submit-status show error"
        )

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
