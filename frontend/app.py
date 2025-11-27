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
from utils.helpers import (get_backend_url, fetch_parameters, create_parameter_card, create_data_table, 
                           submit_sample_data, validate_sample_data, fetch_samples, create_samples_table, create_sample_details)

def create_sample_detail_page(sample_id):
    """Create a sample detail page for a specific sample ID"""
    # Try to get individual sample first, fall back to list if endpoint doesn't exist
    try:
        import requests
        response = requests.get(f"{BACKEND_URL}/api/mostres/{sample_id}")
        if response.status_code == 200:
            sample_data = response.json()
        else:
            # Fallback to searching through all samples
            samples = fetch_samples(BACKEND_URL)
            sample_data = None
            for sample in samples:
                if str(sample.get('id')) == str(sample_id):
                    sample_data = sample
                    break
    except:
        # Fallback to searching through all samples
        samples = fetch_samples(BACKEND_URL)
        sample_data = None
        for sample in samples:
            if str(sample.get('id')) == str(sample_id):
                sample_data = sample
                break
    
    return html.Div([
        html.Div([
            create_sample_details(sample_data)
        ], style={
            'maxWidth': '1200px', 
            'margin': '0 auto', 
            'padding': '2rem'
        })
    ], style={'backgroundColor': '#f8f9fa', 'minHeight': '80vh'})

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
    elif pathname and pathname.startswith('/browse/sample/'):
        # Handle sample detail pages like /browse/sample/123
        try:
            sample_id = pathname.split('/')[-1]
            return create_sample_detail_page(sample_id)
        except Exception as e:
            print(f"Error loading sample detail: {e}")
            return create_browse_page()
    elif pathname and pathname.startswith('/browse/') and len(pathname.split('/')) > 2:
        # Fallback for old URL format /browse/123
        try:
            sample_id = pathname.split('/')[-1]
            return create_sample_detail_page(sample_id)
        except Exception as e:
            print(f"Error loading sample detail: {e}")
            return create_browse_page()
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

# Callback for browse page samples table
@app.callback(
    Output('samples-table', 'children'),
    [Input('interval-browse', 'n_intervals'),
     Input('table-current-page', 'data'),
     Input('table-page-size', 'data'),
     Input('table-sort-column', 'data'),
     Input('table-sort-order', 'data')]
)
def update_samples_table(n, current_page, page_size, sort_column, sort_order):
    data = fetch_samples(BACKEND_URL)
    return create_samples_table(data, current_page, page_size, sort_column, sort_order)

# Callback for table sorting
@app.callback(
    [Output('table-current-page', 'data', allow_duplicate=True),
     Output('table-sort-column', 'data'),
     Output('table-sort-order', 'data')],
    [Input('sort-id', 'n_clicks'),
     Input('sort-data', 'n_clicks'),
     Input('sort-punt_mostreig', 'n_clicks')],
    [State('table-sort-column', 'data'),
     State('table-sort-order', 'data')],
    prevent_initial_call=True
)
def handle_sorting(sort_id_clicks, sort_data_clicks, sort_punt_clicks, current_sort_column, current_sort_order):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id.startswith('sort-'):
        new_column = button_id.replace('sort-', '')
        if new_column == current_sort_column:
            # Toggle sort order
            new_order = 'asc' if current_sort_order == 'desc' else 'desc'
        else:
            # New column, default to desc
            new_order = 'desc'
        return 1, new_column, new_order  # Reset to page 1 when sorting
    
    return dash.no_update, dash.no_update, dash.no_update

# Callback for pagination navigation
@app.callback(
    Output('table-current-page', 'data', allow_duplicate=True),
    [Input('pagination-prev', 'n_clicks'),
     Input('pagination-next', 'n_clicks'),
     Input('page-input', 'value')],
    [State('table-current-page', 'data')],
    prevent_initial_call=True
)
def handle_pagination(prev_clicks, next_clicks, page_input, current_page):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'pagination-prev' and prev_clicks:
        return max(1, current_page - 1)
    elif button_id == 'pagination-next' and next_clicks:
        return current_page + 1  # Table will handle max bounds
    elif button_id == 'page-input' and page_input:
        try:
            page_num = int(page_input)
            return max(1, page_num)  # Ensure at least page 1
        except (ValueError, TypeError):
            return current_page
    
    return dash.no_update

@app.callback(
    [Output('table-page-size', 'data'),
     Output('table-current-page', 'data', allow_duplicate=True)],
    [Input('page-size-dropdown', 'value')],
    prevent_initial_call=True
)
def update_page_size(page_size):
    return page_size, 1  # Reset to page 1 when changing page size

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
