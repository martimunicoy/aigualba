import dash
from dash import html, dcc, Input, Output, State, ALL
import sys
import os
import requests
import csv
import io
from datetime import datetime

# Add current directory to Python path for imports
sys.path.append('/app')

# Import page components
from components.navbar import create_navbar
from pages.home import create_home_page
from pages.about import create_about_page
from pages.browse import create_browse_page
from pages.submit import create_submit_page
from pages.visualize import create_visualize_page
from pages.admin import layout as admin_layout
# Import admin callbacks to register them
import callbacks.admin_callbacks
from utils.helpers import (get_backend_url, fetch_parameters, create_parameter_card, create_data_table, 
                           submit_sample_data, validate_sample_data, fetch_samples, create_samples_table, create_sample_details,
                           create_data_visualizations, filter_samples_by_criteria, get_unique_locations, 
                           fetch_latest_gualba_sample, create_latest_sample_summary, fetch_latest_sample_by_location,
                           fetch_latest_sample_any_location, fetch_pending_samples_count)

# Get backend URL
BACKEND_URL = get_backend_url()

def track_visit(page_name, request=None):
    """Track a visit to a page with unique IP tracking"""
    try:
        # Get IP address and user agent
        ip_address = ''
        user_agent = ''
        
        # Since we're in a Dash callback context, try to access Flask request
        try:
            # Access the underlying Flask app request context
            from dash import ctx
            if hasattr(ctx, 'request') and ctx.request:
                # Try to get real IP considering proxy headers
                headers = getattr(ctx.request, 'headers', {})
                environ = getattr(ctx.request, 'environ', {})
                
                # Check for forwarded IP headers first (from nginx proxy)
                x_forwarded = headers.get('X-Forwarded-For', '')
                x_real = headers.get('X-Real-IP', '')
                remote_addr = environ.get('REMOTE_ADDR', '')
                
                if x_forwarded:
                    ip_address = x_forwarded.split(',')[0].strip()
                elif x_real:
                    ip_address = x_real
                else:
                    ip_address = remote_addr
                    
                user_agent = headers.get('User-Agent', '')
        except Exception:
            # If we can't get request context, generate a session-based identifier
            # This ensures some level of uniqueness for tracking
            pass
            
        visit_data = {
            'page': page_name,
            'user_agent': user_agent,
            'ip_address': ip_address or 'unknown'  # Ensure we have some identifier
        }
        
        response = requests.post(f"{BACKEND_URL}/api/admin/visits", json=visit_data, timeout=5)
        if response.status_code == 200:
            print(f"Visit tracked: {page_name} from {ip_address or 'unknown IP'}")
        else:
            print(f"Failed to track visit: {response.status_code}")
    except Exception as e:
        print(f"Error tracking visit: {e}")

def create_sample_detail_page(sample_id, referrer="/browse"):
    """Create a sample detail page for a specific sample ID"""
    sample_data = None
    error_info = []
    
    # First, try to get all samples to see what's available
    all_samples = []
    available_ids = []
    try:
        all_samples = fetch_samples(BACKEND_URL)
        available_ids = [str(s.get('id')) for s in all_samples if s.get('id') is not None]
        error_info.append(f"Available sample IDs: {', '.join(available_ids) if available_ids else 'None'}")
        error_info.append(f"Looking for ID: {sample_id}")
        error_info.append(f"Total samples found: {len(all_samples)}")
        
        # Search through all samples
        for sample in all_samples:
            if str(sample.get('id')) == str(sample_id):
                sample_data = sample
                error_info.append(f"Found sample in list")
                break
        
        if not sample_data and available_ids:
            error_info.append(f"Sample {sample_id} not found in available samples")
            
    except Exception as e:
        error_info.append(f"Error fetching samples: {str(e)}")
    
    # If not found, try individual endpoint as backup
    if not sample_data:
        try:
            response = requests.get(f"{BACKEND_URL}/api/mostres/{sample_id}")
            error_info.append(f"Individual endpoint status: {response.status_code}")
            if response.status_code == 200:
                sample_data = response.json()
                error_info.append(f"Got sample from individual endpoint")
            else:
                error_info.append(f"Individual endpoint error: {response.text}")
        except Exception as e:
            error_info.append(f"Individual endpoint exception: {str(e)}")
    
    if not sample_data:
        return html.Div([
            html.Div([
                html.H2("Error carregant la mostra", style={'color': '#e74c3c', 'textAlign': 'center'}),
                html.P(f"No s'ha pogut carregar la mostra amb ID: {sample_id}", 
                      style={'textAlign': 'center', 'marginBottom': '2rem'}),
                
                # Connection diagnostics
                html.Div([
                    html.H4("Diagnòstic de connexió:", style={'color': '#6c757d', 'marginBottom': '1rem'}),
                    html.Ul([html.Li(info, style={'marginBottom': '0.5rem'}) for info in error_info], 
                           style={'textAlign': 'left', 'color': '#6c757d', 'fontSize': '0.9rem', 'lineHeight': '1.4'})
                ], style={'marginBottom': '2rem', 'padding': '1rem', 'backgroundColor': '#f8f9fa', 'borderRadius': '6px'}),
                
                # Available samples if any
                (html.Div([
                    html.H4("Mostres disponibles:", style={'color': '#28a745', 'marginBottom': '1rem'}),
                    html.Div([
                        html.Div([
                            dcc.Link(f"Mostra {sid}", href=f"/browse/sample/{sid}", 
                                   style={'color': '#fff', 'textDecoration': 'none', 'padding': '0.5rem 1rem', 
                                         'backgroundColor': '#007bff', 'borderRadius': '4px', 'display': 'inline-block'})
                        ], style={'margin': '0.5rem'}) 
                        for sid in available_ids[:5]  # Show first 5 samples
                    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'})
                ], style={'marginBottom': '2rem'}) if available_ids else 
                 html.Div([
                     html.P("No hi ha mostres disponibles a la base de dades", 
                           style={'color': '#dc3545', 'textAlign': 'center', 'fontStyle': 'italic'})
                 ], style={'marginBottom': '2rem'})),
                
                html.Div([
                    dcc.Link("← Tornar a la llista", href="/browse", 
                            style={'color': '#fff', 'textDecoration': 'none', 'fontSize': '1.1rem',
                                  'padding': '0.75rem 1.5rem', 'backgroundColor': '#6c757d', 'borderRadius': '6px'})
                ], style={'textAlign': 'center'})
            ], style={
                'maxWidth': '900px', 
                'margin': '0 auto', 
                'padding': '4rem 2rem',
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            })
        ], style={'backgroundColor': '#f8f9fa', 'minHeight': '80vh', 'paddingTop': '4rem'})
    
    return html.Div([
        html.Div([
            create_sample_details(sample_data, referrer)
        ], style={
            'maxWidth': '1200px', 
            'margin': '0 auto', 
            'padding': '2rem'
        })
    ], style={'backgroundColor': '#f8f9fa', 'minHeight': '80vh'})

# Initialize Dash app

# Custom HTML index string to include all favicon and manifest links
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    assets_folder='assets'
)

# Set custom index string for favicons and manifest
app.index_string = '''
<!DOCTYPE html>
<html lang="ca">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="apple-touch-icon" sizes="180x180" href="/assets/favicon/apple-touch-icon.png">
        <link rel="icon" type="image/x-icon" href="/assets/favicon/favicon.ico">
        <link rel="icon" type="image/x-icon" sizes="16x16" href="/assets/favicon/favicon_16.ico">
        <link rel="icon" type="image/x-icon" sizes="24x24" href="/assets/favicon/favicon_24.ico">
        <link rel="icon" type="image/x-icon" sizes="32x32" href="/assets/favicon/favicon_32.ico">
        <link rel="icon" type="image/x-icon" sizes="48x48" href="/assets/favicon/favicon_48.ico">
        <link rel="icon" type="image/x-icon" sizes="64x64" href="/assets/favicon/favicon_64.ico">
        <link rel="icon" type="image/x-icon" sizes="96x96" href="/assets/favicon/favicon_96.ico">
        <link rel="icon" type="image/x-icon" sizes="128x128" href="/assets/favicon/favicon_128.ico">
        <link rel="icon" type="image/x-icon" sizes="256x256" href="/assets/favicon/favicon_256.ico">
        <link rel="manifest" href="/assets/favicon/site.webmanifest">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Main app layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    create_navbar(),
    html.Div(id='page-content')
], style={'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', 'margin': '0', 'padding': '0', 'backgroundColor': '#f5f5f5'})

# Enable URL routing
app.title = "Aigualba - Qualitat de l'aigua"
app.config.suppress_callback_exceptions = True

# Callback for URL routing
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname'), Input('url', 'search')])
def display_page(pathname, search):
    # Track page visits
    if pathname == '/about':
        track_visit('about')
        return create_about_page()
    elif pathname == '/browse':
        track_visit('browse')
        return create_browse_page()
    elif pathname == '/visualize':
        track_visit('visualize')
        return create_visualize_page()
    elif pathname == '/submit':
        track_visit('submit')
        return create_submit_page()
    elif pathname == '/admin':
        track_visit('admin')
        return admin_layout
    elif pathname and pathname.startswith('/sample/'):
        # Handle direct sample detail pages like /sample/123
        try:
            # Extract sample ID from pathname
            sample_id = pathname.split('/')[-1]
            
            # Extract referrer from search parameters
            referrer = "/"  # default to home
            if search:
                if 'ref=browse' in search:
                    referrer = "/browse"
                elif 'ref=home' in search:
                    referrer = "/"
            
            return create_sample_detail_page(sample_id, referrer=referrer)
        except Exception as e:
            print(f"Error loading sample detail: {e}")
            return html.Div([
                html.H2("Error loading sample"),
                html.P(f"Could not load sample {pathname.split('/')[-1]}"),
                html.A("Return to home", href="/")
            ])
    elif pathname and pathname.startswith('/browse/sample/'):
        # Handle sample detail pages like /browse/sample/123
        try:
            sample_id = pathname.split('/')[-1]
            return create_sample_detail_page(sample_id, referrer="/browse")
        except Exception as e:
            print(f"Error loading sample detail: {e}")
            return html.Div([
                html.H2("Error loading sample"),
                html.P(f"Could not load sample {pathname.split('/')[-1]}"),
                html.A("Return to browse", href="/browse")
            ])
    elif pathname and pathname.startswith('/browse/') and len(pathname.split('/')) > 2:
        # Fallback for old URL format /browse/123
        try:
            sample_id = pathname.split('/')[-1]
            return create_sample_detail_page(sample_id, referrer="/browse")
        except Exception as e:
            print(f"Error loading sample detail: {e}")
            return html.Div([
                html.H2("Error loading sample"),
                html.P(f"Could not load sample {pathname.split('/')[-1]}"),
                html.A("Return to browse", href="/browse")
            ])
    else:
        track_visit('home')
        return create_home_page()

# Callback to populate home location selector
@app.callback(
    [Output('home-location-selector', 'options'),
     Output('home-location-selector', 'value')],
    [Input('interval-home', 'n_intervals')]
)
def populate_home_location_selector(n):
    data = fetch_samples(BACKEND_URL)
    locations = get_unique_locations(data)
    
    # Add 'any location' option at the beginning
    options = [{'label': 'Qualsevol ubicació (més recent)', 'value': 'any_location'}]
    options.extend([{'label': location, 'value': location} for location in locations])
    
    # Set default to 'any location'
    default_value = 'any_location'
    return options, default_value

# Callback for home page live parameters
@app.callback(
    [Output('live-parameters', 'children'),
     Output('current-sample-id', 'data'),
     Output('selected-location', 'data')],
    [Input('home-location-selector', 'value')]
)
def update_home_parameters(selected_location):
    # Fetch the latest sample based on selection
    if selected_location == 'any_location':
        latest_sample = fetch_latest_sample_any_location(BACKEND_URL)
    elif selected_location:
        latest_sample = fetch_latest_sample_by_location(BACKEND_URL, selected_location)
    else:
        # Fallback to any latest sample if no location selected
        latest_sample = fetch_latest_sample_any_location(BACKEND_URL)
    
    if latest_sample:
        sample_id = latest_sample.get('id')
        return create_latest_sample_summary(latest_sample, selected_location), sample_id, selected_location
    else:
        return create_latest_sample_summary(None, selected_location), None, selected_location

# Callback for home page sample details button
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('home-sample-details-btn', 'n_clicks')],
    [State('current-sample-id', 'data')],
    prevent_initial_call=True
)
def navigate_to_home_sample_details(n_clicks, sample_id):
    if n_clicks and sample_id:
        return f'/sample/{sample_id}?ref=home'
    return dash.no_update

# Note: Mail subscription feature temporarily disabled
# To reactivate: uncomment the callbacks below and the form in home.py

# Callback for mailing list subscription
# @app.callback(
#     [Output('subscription-status', 'children'),
#      Output('subscription-status', 'style'),
#      Output('email-input', 'value'),
#      Output('subscription-state', 'data')],
#     [Input('subscribe-btn', 'n_clicks')],
#     [State('email-input', 'value'),
#      State('subscription-state', 'data')],
#     prevent_initial_call=True
# )
# def handle_subscription(n_clicks, email_value, subscription_state):
#     """Handle mailing list subscription with confirmation"""
#     if not n_clicks or not email_value:
#         return dash.no_update, dash.no_update, dash.no_update, dash.no_update
#     
#     # Basic email validation
#     import re
#     email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     
#     if not re.match(email_pattern, email_value):
#         return (
#             html.Div([
#                 html.P("Si us plau, introdueix un correu electrònic vàlid.", 
#                        style={'color': '#e74c3c', 'margin': '0', 'fontWeight': '500'})
#             ]), 
#             {'textAlign': 'center', 'marginTop': '1rem', 'display': 'block'}, 
#             dash.no_update,
#             dash.no_update
#         )
#     
#     # Check if this is the confirmation step
#     if subscription_state.get('confirmed') and subscription_state.get('email') == email_value:
#         # Actually process the subscription
#         try:
#             # TODO: Integrate with actual mailing list service (Mailchimp, ConvertKit, etc.)
#             # Example: requests.post(MAILING_LIST_API_URL, data={'email': email_value})
#             
#             return (
#                 html.Div([
#                     html.P([
#                         html.I(className="fas fa-check-circle", style={'marginRight': '8px', 'color': '#27ae60'}),
#                         "Gràcies! T'has subscrit correctament a la nostra llista de correu."
#                     ], style={'color': '#27ae60', 'margin': '0', 'fontWeight': '500'})
#                 ]), 
#                 {'textAlign': 'center', 'marginTop': '1rem', 'display': 'block'}, 
#                 '',
#                 {'confirmed': False, 'email': ''}
#             )
#             
#         except Exception as e:
#             return (
#                 html.Div([
#                     html.P("Hi ha hagut un error. Si us plau, torna-ho a intentar més tard.", 
#                            style={'color': '#e74c3c', 'margin': '0', 'fontWeight': '500'})
#                 ]), 
#                 {'textAlign': 'center', 'marginTop': '1rem', 'display': 'block'}, 
#                 dash.no_update,
#                 {'confirmed': False, 'email': ''}
#             )
#     else:
#         # Show confirmation message
#         return (
#             html.Div([
#                 html.P([
#                     f"Vols subscriure't amb el correu ",
#                     html.Strong(email_value, style={'color': '#2c3e50'}),
#                     "?"
#                 ], style={'color': '#34495e', 'margin': '0 0 1rem 0', 'fontWeight': '500'}),
#                 html.Div([
#                     html.Button(
#                         "Sí, confirmo",
#                         id='confirm-subscription-btn',
#                         className='btn-standard btn-subscribe',
#                         style={
#                             'backgroundColor': '#27ae60',
#                             'color': 'white',
#                             'border': 'none',
#                             'padding': '8px 16px',
#                             'borderRadius': '4px',
#                             'fontSize': '0.9rem',
#                             'cursor': 'pointer',
#                             'marginRight': '0.5rem',
#                             'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
#                             'transition': 'all 0.2s ease'
#                         }
#                     ),
#                     html.Button(
#                         "Cancel·lar",
#                         id='cancel-subscription-btn',
#                         className='btn-standard',
#                         style={
#                             'backgroundColor': '#95a5a6',
#                             'color': 'white',
#                             'border': 'none',
#                             'padding': '8px 16px',
#                             'borderRadius': '4px',
#                             'fontSize': '0.9rem',
#                             'cursor': 'pointer',
#                             'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
#                             'transition': 'all 0.2s ease'
#                         }
#                     )
#                 ], style={'textAlign': 'center'})
#             ]), 
#             {'textAlign': 'center', 'marginTop': '1rem', 'display': 'block'}, 
#             dash.no_update,
#             {'confirmed': True, 'email': email_value}
#         )


# Callback for subscription confirmation buttons
# @app.callback(
#     [Output('subscription-status', 'children', allow_duplicate=True),
#      Output('subscription-status', 'style', allow_duplicate=True),
#      Output('email-input', 'value', allow_duplicate=True),
#      Output('subscription-state', 'data', allow_duplicate=True)],
#     [Input('confirm-subscription-btn', 'n_clicks'),
#      Input('cancel-subscription-btn', 'n_clicks')],
#     [State('subscription-state', 'data')],
#     prevent_initial_call=True
# )
# def handle_confirmation(confirm_clicks, cancel_clicks, subscription_state):
#     """Handle confirmation or cancellation of subscription"""
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         return dash.no_update, dash.no_update, dash.no_update, dash.no_update
#     
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0]
#     
#     if button_id == 'confirm-subscription-btn':
#         # Process the subscription
#         email_value = subscription_state.get('email', '')
#         try:
#             # TODO: Integrate with actual mailing list service
#             # Example: requests.post(MAILING_LIST_API_URL, data={'email': email_value})
#             
#             return (
#                 html.Div([
#                     html.P([
#                         html.I(className="fas fa-check-circle", style={'marginRight': '8px', 'color': '#27ae60'}),
#                         "Gràcies! T'has subscrit correctament a la nostra llista de correu."
#                     ], style={'color': '#27ae60', 'margin': '0', 'fontWeight': '500'})
#                 ]),
#                 {'textAlign': 'center', 'marginTop': '1rem', 'display': 'block'},
#                 '',
#                 {'confirmed': False, 'email': ''}
#             )
#         except Exception as e:
#             return (
#                 html.Div([
#                     html.P("Hi ha hagut un error. Si us plau, torna-ho a intentar més tard.", 
#                            style={'color': '#e74c3c', 'margin': '0', 'fontWeight': '500'})
#                 ]),
#                 {'textAlign': 'center', 'marginTop': '1rem', 'display': 'block'},
#                 dash.no_update,
#                 {'confirmed': False, 'email': ''}
#             )
#     
#     elif button_id == 'cancel-subscription-btn':
#         # Cancel subscription
#         return (
#             html.Div([]),
#             {'display': 'none'},
#             dash.no_update,
#             {'confirmed': False, 'email': ''}
#         )
#     
#     return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback to populate location filter with unique locations
@app.callback(
    Output('location-filter', 'options'),
    [Input('interval-browse', 'n_intervals')]
)
def populate_location_filter(n):
    data = fetch_samples(BACKEND_URL)
    locations = get_unique_locations(data)
    options = [{'label': 'Totes les ubicacions', 'value': 'all'}]
    options.extend([{'label': location, 'value': location} for location in locations])
    return options

# Callback to filter samples based on filter criteria
@app.callback(
    Output('filtered-samples', 'data'),
    [Input('interval-browse', 'n_intervals'),
     Input('date-filter-from', 'date'),
     Input('date-filter-to', 'date'),
     Input('location-filter', 'value'),
     Input('clear-filters-btn', 'n_clicks')]
)
def filter_samples(n, date_from, date_to, location, clear_clicks):
    ctx = dash.callback_context
    
    # Check if clear button was clicked
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'clear-filters-btn':
            # Return all samples without filters
            data = fetch_samples(BACKEND_URL)
            return data
    
    # Apply filters
    data = fetch_samples(BACKEND_URL)
    filtered_data = filter_samples_by_criteria(data, date_from, date_to, location)
    return filtered_data

# Callback for browse page samples table
@app.callback(
    Output('samples-table', 'children'),
    [Input('filtered-samples', 'data'),
     Input('table-current-page', 'data'),
     Input('table-page-size', 'data'),
     Input('table-sort-column', 'data'),
     Input('table-sort-order', 'data')]
)
def update_samples_table(filtered_data, current_page, page_size, sort_column, sort_order):
    data = filtered_data if filtered_data else []
    
    # Ensure default values are set properly
    if current_page is None:
        current_page = 1
    if page_size is None:
        page_size = 10
    if sort_column is None or sort_column == '':
        sort_column = 'data'
    if sort_order is None or sort_order == '':
        sort_order = 'desc'
        
    print(f"Table update - Page: {current_page}, Size: {page_size}, Sort: {sort_column}, Order: {sort_order}")
    print(f"Filtered data count: {len(data)}")
    return create_samples_table(data, current_page, page_size, sort_column, sort_order)

# Callback for validation status notification on browse page
@app.callback(
    Output('validation-status-notification', 'children'),
    [Input('interval-browse', 'n_intervals')]
)
def update_validation_status_notification(n_intervals):
    """Update the validation status notification banner"""
    try:
        pending_count = fetch_pending_samples_count(BACKEND_URL)
        
        if pending_count > 0:
            if pending_count == 1:
                message_content = [
                    "Hi ha 1 mostra pendent de validació per part dels administradors. Podeu contactar-los a ",
                    html.A("contacte@aigualba.cat", href="mailto:contacte@aigualba.cat", style={'color': '#0c5460', 'textDecoration': 'underline'}),
                    "."
                ]
            else:
                message_content = [
                    f"Hi ha {pending_count} mostres pendents de validació per part dels administradors. Podeu contactar-los a ",
                    html.A("contacte@aigualba.cat", href="mailto:contacte@aigualba.cat", style={'color': '#0c5460', 'textDecoration': 'underline'}),
                    "."
                ]
            
            return html.Div([
                html.Div([
                    html.I(className="fas fa-info-circle", style={'marginRight': '10px', 'fontSize': '1.2rem'}),
                    html.Span(message_content, style={'fontSize': '1rem', 'fontWeight': '500'})
                ], style={
                    'backgroundColor': '#d1ecf1',
                    'border': '1px solid #bee5eb',
                    'borderRadius': '8px',
                    'color': '#0c5460',
                    'padding': '12px 16px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                })
            ])
        else:
            # Return empty div if no pending samples
            return html.Div()
            
    except Exception as e:
        print(f"Error updating validation status notification: {e}")
        return html.Div()

# Callback for validation status notification on visualize page
@app.callback(
    Output('validation-status-notification-visualize', 'children'),
    [Input('url', 'pathname')]
)
def update_validation_status_notification_visualize(pathname):
    """Update the validation status notification banner on visualize page"""
    # Only show notification when on visualize page
    if pathname != '/visualize':
        return html.Div()
    
    try:
        pending_count = fetch_pending_samples_count(BACKEND_URL)
        
        if pending_count > 0:
            if pending_count == 1:
                message_content = [
                    "Hi ha 1 mostra pendent de validació per part dels administradors. Podeu contactar-los a ",
                    html.A("contacte@aigualba.cat", href="mailto:contacte@aigualba.cat", style={'color': '#0c5460', 'textDecoration': 'underline'}),
                    "."
                ]
            else:
                message_content = [
                    f"Hi ha {pending_count} mostres pendents de validació per part dels administradors. Podeu contactar-los a ",
                    html.A("contacte@aigualba.cat", href="mailto:contacte@aigualba.cat", style={'color': '#0c5460', 'textDecoration': 'underline'}),
                    "."
                ]
            
            return html.Div([
                html.Div([
                    html.I(className="fas fa-info-circle", style={'marginRight': '10px', 'fontSize': '1.2rem'}),
                    html.Span(message_content, style={'fontSize': '1rem', 'fontWeight': '500'})
                ], style={
                    'backgroundColor': '#d1ecf1',
                    'border': '1px solid #bee5eb',
                    'borderRadius': '8px',
                    'color': '#0c5460',
                    'padding': '12px 16px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                })
            ])
        else:
            # Return empty div if no pending samples
            return html.Div()
            
    except Exception as e:
        print(f"Error updating validation status notification on visualize page: {e}")
        return html.Div()

# Callback for data visualizations
@app.callback(
    Output('data-visualizations', 'children'),
    [Input('filtered-samples', 'data')]
)
def update_data_visualizations(filtered_data):
    data = filtered_data if filtered_data else []
    return create_data_visualizations(data)

# Callback to clear filters
@app.callback(
    [Output('date-filter-from', 'date'),
     Output('date-filter-to', 'date'),
     Output('location-filter', 'value')],
    [Input('clear-filters-btn', 'n_clicks')],
    prevent_initial_call=True
)
def clear_filters(clear_clicks):
    if clear_clicks:
        return None, None, 'all'
    return dash.no_update, dash.no_update, dash.no_update

# Unified callback for all table state management
@app.callback(
    [Output('table-current-page', 'data'),
     Output('table-page-size', 'data'),
     Output('table-sort-column', 'data'),
     Output('table-sort-order', 'data')],
    [Input('sort-id', 'n_clicks'),
     Input('sort-data', 'n_clicks'),
     Input('sort-punt_mostreig', 'n_clicks'),
     Input('pagination-prev', 'n_clicks'),
     Input('pagination-next', 'n_clicks'),
     Input('page-input', 'value'),
     Input('page-size-dropdown', 'value')],
    [State('table-current-page', 'data'),
     State('table-page-size', 'data'),
     State('table-sort-column', 'data'),
     State('table-sort-order', 'data')],
    prevent_initial_call=True
)
def handle_table_state(sort_id_clicks, sort_data_clicks, sort_punt_clicks,
                      prev_clicks, next_clicks, page_input, page_size_input,
                      current_page, current_page_size, current_sort_column, current_sort_order):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Set defaults to prevent None values - preserve 'data' as default sort column
    if current_page is None:
        current_page = 1
    if current_page_size is None:
        current_page_size = 10
    if current_sort_column is None or current_sort_column == '':
        current_sort_column = 'data'
    if current_sort_order is None or current_sort_order == '':
        current_sort_order = 'desc'
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    triggered_value = ctx.triggered[0]['value']
    
    print(f"Table state update triggered by: {button_id} with value: {triggered_value}")
    print(f"Current state - Page: {current_page}, Size: {current_page_size}, Sort: {current_sort_column} {current_sort_order}")
    
    # Only proceed if this is a real user interaction, not an initial load
    # Check if the triggered value is meaningful (not None and not initial state)
    if triggered_value is None:
        print("Triggered value is None - ignoring to prevent initial state reset")
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    new_page = current_page
    new_page_size = current_page_size
    new_sort_column = current_sort_column
    new_sort_order = current_sort_order
    
    # Handle sorting - only if actual clicks occurred
    if button_id.startswith('sort-') and triggered_value > 0:
        new_column = button_id.replace('sort-', '')
        if new_column == current_sort_column:
            # Toggle sort order
            new_sort_order = 'asc' if current_sort_order == 'desc' else 'desc'
        else:
            # New column, default to desc
            new_sort_column = new_column
            new_sort_order = 'desc'
        new_page = 1  # Reset to page 1 when sorting
        print(f"Sorting changed to: {new_sort_column} {new_sort_order}")
    
    # Handle pagination - only if actual clicks occurred
    elif button_id == 'pagination-prev' and prev_clicks and prev_clicks > 0:
        new_page = max(1, current_page - 1)
        print(f"Moving to previous page: {new_page}")
    elif button_id == 'pagination-next' and next_clicks and next_clicks > 0:
        new_page = current_page + 1  # Table will handle max bounds
        print(f"Moving to next page: {new_page}")
    elif button_id == 'page-input' and page_input:
        try:
            page_num = int(page_input)
            new_page = max(1, page_num)
            print(f"Moving to input page: {new_page}")
        except (ValueError, TypeError):
            pass
    
    # Handle page size change - only if actual selection occurred
    elif button_id == 'page-size-dropdown' and page_size_input and page_size_input != current_page_size:
        new_page_size = page_size_input
        new_page = 1  # Reset to page 1 when changing page size
        print(f"Page size changed to: {new_page_size}")
    
    # If no actual changes were made, don't update anything
    if (new_page == current_page and new_page_size == current_page_size and 
        new_sort_column == current_sort_column and new_sort_order == current_sort_order):
        print("No actual state changes - returning no_update")
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    print(f"New state - Page: {new_page}, Size: {new_page_size}, Sort: {new_sort_column} {new_sort_order}")
    return new_page, new_page_size, new_sort_column, new_sort_order

# Callback for CSV export
@app.callback(
    Output('download-csv', 'data'),
    [Input('export-csv-btn', 'n_clicks')],
    [State('filtered-samples', 'data')],
    prevent_initial_call=True
)
def export_samples_to_csv(export_clicks, filtered_data):
    """Export filtered samples data to CSV file"""
    if not export_clicks:
        return dash.no_update
    
    data = filtered_data if filtered_data else []
    if not data:
        return dash.no_update
    
    # Create CSV content
    output = io.StringIO()
    
    # Define column headers in Catalan and their corresponding keys
    columns = [
        ('ID', 'id'),
        ('Data de recollida', 'data'),
        ('Punt de mostreig', 'punt_mostreig'),
        ('pH', 'ph'),
        ('Temperatura (°C)', 'temperatura'),
        ('Conductivitat 20°C (μS/cm)', 'conductivitat_20c'),
        ('Terbolesa (UNF)', 'terbolesa'),
        ('Color (mg/L Pt-Co)', 'color'),
        ('Olor (índex dilució 25°C)', 'olor'),
        ('Sabor (índex dilució 25°C)', 'sabor'),
        ('Clor lliure (mg/L)', 'clor_lliure'),
        ('Clor total (mg/L)', 'clor_total'),
        ('E. coli (NPM/100mL)', 'recompte_escherichia_coli'),
        ('Enterococs (NPM/100mL)', 'recompte_enterococ'),
        ('Microorganismes aerobis 22°C (UFC/1mL)', 'recompte_microorganismes_aerobis_22c'),
        ('Coliformes totals (NMP/100mL)', 'recompte_coliformes_totals'),
        ('Àcid monocloroacètic (μg/L)', 'acid_monocloroacetic'),
        ('Àcid dicloroacètic (μg/L)', 'acid_dicloroacetic'),
        ('Àcid tricloroacètic (μg/L)', 'acid_tricloroacetic'),
        ('Àcid monobromoacètic (μg/L)', 'acid_monobromoacetic'),
        ('Àcid dibromoacètic (μg/L)', 'acid_dibromoacetic'),
    ]
    
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([header for header, _ in columns])
    
    # Write data rows
    for sample in data:
        row = []
        for _, key in columns:
            value = sample.get(key, '')
            # Handle None values
            if value is None:
                value = ''
            row.append(str(value))
        writer.writerow(row)
    
    # Generate filename with current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    filename = f'mostres_aigua_gualba_{current_date}.csv'
    
    return dict(content=output.getvalue(), filename=filename)

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
                html.Div("Avisos:", style={'marginBottom': '0.5rem'}),
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
        # Safely get information from result data
        sample_id = "N/A"
        api_message = "Mostra enviada correctament!"
        if result.get('data') and isinstance(result['data'], dict):
            sample_id = str(result['data'].get('id', 'N/A'))
            api_message = result['data'].get('message', 'Mostra enviada correctament!')
        
        success_message = html.Div([
            html.H3("✓ Mostra enviada correctament!", style={'color': '#2e7d32', 'marginBottom': '0.5rem', 'marginTop': '0'}),
            html.P(f"ID de la mostra: {sample_id}", style={'margin': '0 0 0.5rem 0'}),
            html.P(api_message, style={'margin': '0', 'fontStyle': 'italic'})
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

# Visualization page callbacks
@app.callback(
    Output('location-selector', 'options'),
    Input('parameter-selector', 'value')
)
def update_location_options(selected_parameter):
    """Update the location selector options with all available locations"""
    try:
        samples = fetch_samples(BACKEND_URL)
        if not samples:
            return [{'label': 'Tots els punts', 'value': 'all'}]
        
        # Get all unique locations regardless of parameter data
        locations = get_unique_locations(samples)
        
        options = [{'label': 'Tots els punts', 'value': 'all'}]
        for location in locations:
            options.append({'label': location, 'value': location})
        
        return options
    except:
        return [{'label': 'Tots els punts', 'value': 'all'}]

@app.callback(
    [Output('time-series-chart', 'figure'),
     Output('chart-title', 'children'),
     Output('chart-info', 'children')],
    [Input('parameter-selector', 'value'),
     Input('location-selector', 'value')]
)
def update_chart(selected_parameter, selected_location):
    """Update the time series chart based on selected parameter and location"""
    try:
        # Import plotly here to handle potential import issues
        import plotly.graph_objects as go
        import plotly.express as px
        from datetime import datetime
        from pages.visualize import get_parameter_label
        from utils.thresholds import get_threshold
        
        # Check if parameter is selected
        if not selected_parameter or not selected_location:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Res a mostrar",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            empty_fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='white'
            )
            return empty_fig, "Selecciona un paràmetre i punt de mostreig de la llista per generar el gràfic", None
        
        # Fetch samples
        samples = fetch_samples(BACKEND_URL)
        if not samples:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No hi ha dades disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            empty_fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='white'
            )
            return empty_fig, "Gràfic de dades", None
        
        # Filter samples based on parameter availability and location
        filtered_samples = []
        for sample in samples:
            # Special handling for calculated fields
            if selected_parameter == 'suma_haloacetics':
                from utils.helpers import calculate_suma_haloacetics
                param_value = calculate_suma_haloacetics(sample)
            elif selected_parameter == 'clor_combinat_residual':
                from utils.helpers import calculate_clor_combinat_residual
                param_value = calculate_clor_combinat_residual(sample)
            else:
                param_value = sample.get(selected_parameter)
            
            # Check if sample has the parameter and it's not None/empty
            if param_value is not None and param_value != '':
                # Check location filter
                if selected_location == 'all' or sample.get('punt_mostreig') == selected_location:
                    # Check if sample has a valid date
                    if sample.get('data'):
                        # Add the calculated value to the sample for later use
                        if selected_parameter in ['suma_haloacetics', 'clor_combinat_residual']:
                            sample_copy = sample.copy()
                            sample_copy[selected_parameter] = param_value
                            filtered_samples.append(sample_copy)
                        else:
                            filtered_samples.append(sample)
        
        if not filtered_samples:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text=f"No hi ha dades disponibles per al paràmetre seleccionat{' i punt de mostreig' if selected_location != 'all' else ''}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            empty_fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='white'
            )
            return empty_fig, get_parameter_label(selected_parameter), None
        
        # Prepare data for plotting
        dates = []
        values = []
        locations = []
        
        for sample in filtered_samples:
            try:
                # Parse date
                date_str = sample.get('data')
                if date_str:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    dates.append(date_obj)
                    values.append(float(sample.get(selected_parameter)))
                    locations.append(sample.get('punt_mostreig', 'Desconegut'))
            except (ValueError, TypeError):
                continue
        
        if not dates:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No es poden processar les dades disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            empty_fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='white'
            )
            return empty_fig, get_parameter_label(selected_parameter), "Error processant les dades"
        
        # Create the figure
        fig = go.Figure()
        
        if selected_location == 'all':
            # Group by location and create separate traces
            location_groups = {}
            for date, value, location in zip(dates, values, locations):
                if location not in location_groups:
                    location_groups[location] = {'dates': [], 'values': []}
                location_groups[location]['dates'].append(date)
                location_groups[location]['values'].append(value)
            
            # Add traces for each location
            colors = px.colors.qualitative.Set2
            for i, (location, data) in enumerate(location_groups.items()):
                color = colors[i % len(colors)]
                fig.add_trace(go.Scatter(
                    x=data['dates'],
                    y=data['values'],
                    mode='lines+markers',
                    name=location,
                    line=dict(color=color, width=2),
                    marker=dict(size=6, color=color),
                    hovertemplate=f'<b>{location}</b><br>' +
                                  'Data: %{x|%d/%m/%Y}<br>' +
                                  f'{get_parameter_label(selected_parameter)}: %{{y}}<br>' +
                                  '<extra></extra>'
                ))
        else:
            # Single location
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name=selected_location,
                line=dict(color='#3498db', width=3),
                marker=dict(size=8, color='#3498db'),
                hovertemplate=f'<b>{selected_location}</b><br>' +
                              'Data: %{x|%d/%m/%Y}<br>' +
                              f'{get_parameter_label(selected_parameter)}: %{{y}}<br>' +
                              '<extra></extra>'
            ))
        
        # Add threshold lines as scatter traces (renders immediately)
        threshold = get_threshold(selected_parameter)
        if threshold and dates:  # Only add if we have data points
            min_val = float(threshold['min'])
            max_val = float(threshold['max'])
            
            # Create x-axis range for threshold lines
            x_min = min(dates)
            x_max = max(dates)
            
            # If only one data point, extend the line to make it visible
            if x_min == x_max:
                from datetime import timedelta
                x_min = x_min - timedelta(days=1)
                x_max = x_max + timedelta(days=1)
            
            threshold_x = [x_min, x_max]
            
            # Add horizontal lines for thresholds as scatter traces
            if min_val > 0:  # Range-based parameter (has meaningful minimum)
                fig.add_trace(go.Scatter(
                    x=threshold_x,
                    y=[min_val, min_val],
                    mode='lines',
                    line=dict(color='red', width=2, dash='dash'),
                    name=f'Límit mínim ({min_val} {threshold["unit"]})',
                    showlegend=False,
                    hovertemplate=f'Límit mínim: {min_val} {threshold["unit"]}<extra></extra>'
                ))
                fig.add_trace(go.Scatter(
                    x=threshold_x,
                    y=[max_val, max_val],
                    mode='lines',
                    line=dict(color='red', width=2, dash='dash'),
                    name=f'Màxim permès ({max_val} {threshold["unit"]})',
                    showlegend=False,
                    hovertemplate=f'Màxim permès: {max_val} {threshold["unit"]}<extra></extra>'
                ))
                
                # Add text annotations for threshold lines
                fig.add_annotation(
                    x=x_max,
                    y=min_val,
                    text=f"Límit mínim: {min_val} {threshold['unit']}",
                    showarrow=False,
                    xanchor="right",
                    yanchor="top",
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="red",
                    borderwidth=1,
                    font=dict(color="red")
                )
                fig.add_annotation(
                    x=x_max,
                    y=max_val,
                    text=f"Límit màxim: {max_val} {threshold['unit']}",
                    showarrow=False,
                    xanchor="right",
                    yanchor="bottom",
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="red",
                    borderwidth=1,
                    font=dict(color="red")
                )
            else:  # Threshold-based parameter (only maximum limit matters)
                fig.add_trace(go.Scatter(
                    x=threshold_x,
                    y=[max_val, max_val],
                    mode='lines',
                    line=dict(color='red', width=2, dash='dash'),
                    name=f'Límit màxim ({max_val} {threshold["unit"]})',
                    showlegend=False,
                    hovertemplate=f'Límit màxim: {max_val} {threshold["unit"]}<extra></extra>'
                ))
                
                # Add text annotation for threshold line
                fig.add_annotation(
                    x=x_max,
                    y=max_val,
                    text=f"Límit màxim: {max_val} {threshold['unit']}",
                    showarrow=False,
                    xanchor="right",
                    yanchor="bottom",
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="red",
                    borderwidth=1,
                    font=dict(color="red")
                )
        
        # Calculate y-axis range to ensure threshold lines are visible
        y_min = min(values) if values else 0
        y_max = max(values) if values else 1
        
        # Extend range to include threshold lines
        if threshold:
            min_val = float(threshold['min'])
            max_val = float(threshold['max'])
            y_min = min(y_min, min_val - abs(min_val) * 0.1)
            y_max = max(y_max, max_val + abs(max_val) * 0.1)
        
        # Add some padding to the range
        y_range = y_max - y_min
        y_padding = y_range * 0.1 if y_range > 0 else 1
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f'Evolució temporal - {get_parameter_label(selected_parameter)}',
                x=0.5,
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title=dict(text='Data', font=dict(size=12, color='#2c3e50')),
                tickfont=dict(size=10, color='#2c3e50'),
                gridcolor='#ecf0f1'
            ),
            yaxis=dict(
                title=dict(text=get_parameter_label(selected_parameter), font=dict(size=12, color='#2c3e50')),
                tickfont=dict(size=10, color='#2c3e50'),
                gridcolor='#ecf0f1',
                range=[y_min - y_padding, y_max + y_padding]
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=60, r=60, t=80, b=60),
            hovermode='x unified'
        )
        
        # Chart info
        total_points = len(values)
        date_range = f"des de {min(dates).strftime('%d/%m/%Y')} fins a {max(dates).strftime('%d/%m/%Y')}" if dates else "No disponible"
        
        info_text = html.Div([
            html.P([
                html.Strong("Punts de dades: "), f"{total_points}",
                html.Br(),
                html.Strong("Període: "), date_range,
                html.Br(),
                html.Strong("Ubicacions: "), f"{len(set(locations))}" if selected_location == 'all' else selected_location
            ], style={'fontSize': '0.9rem', 'color': '#6c757d', 'textAlign': 'center'})
        ])
        
        return fig, get_parameter_label(selected_parameter), info_text
        
    except Exception as e:
        # Error handling
        import traceback
        print(f"Error updating chart: {e}")
        traceback.print_exc()
        
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error carregant les dades: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16, color="red")
        )
        empty_fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white'
        )
        return empty_fig, "Error", "S'ha produït un error carregant les dades"

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
