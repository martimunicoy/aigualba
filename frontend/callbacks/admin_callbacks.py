"""
Admin authentication and dashboard callbacks with proper Keycloak authentication
"""
from dash import html, dcc, Input, Output, State, callback, dash_table, ALL, callback_context, no_update
from dash.exceptions import PreventUpdate
import requests
import json
import os
from urllib.parse import urlparse, parse_qs
from utils.auth import keycloak_auth
from utils.admin import admin_sample_manager
from components.admin_dashboard import create_admin_tabs_content, create_sample_edit_modal
from utils.helpers import get_backend_url

def create_auth_error_message(message):
    """Create an error message component for authentication errors"""
    return html.Div([
        html.Div([
            html.I(className="fas fa-exclamation-triangle", style={
                'fontSize': '1.2rem',
                'color': '#e74c3c',
                'marginRight': '0.5rem'
            }),
            html.Span(message, style={
                'color': '#e74c3c',
                'fontWeight': '500'
            })
        ], style={
            'backgroundColor': '#fdf2f2',
            'border': '1px solid #fca5a5',
            'borderRadius': '6px',
            'padding': '1rem',
            'textAlign': 'center'
        })
    ])

def create_auth_info_message(message):
    """Create an info message component"""
    return html.Div([
        html.Div([
            html.I(className="fas fa-info-circle", style={
                'fontSize': '1.2rem',
                'color': '#3498db',
                'marginRight': '0.5rem'
            }),
            html.Span(message, style={
                'color': '#2c3e50',
                'fontWeight': '500'
            })
        ], style={
            'backgroundColor': '#e8f4f8',
            'border': '1px solid #3498db',
            'borderRadius': '6px',
            'padding': '1rem',
            'textAlign': 'center'
        })
    ])



# Admin authentication callback
@callback(
    [Output('login-form', 'style'),
     Output('admin-dashboard', 'style'),
     Output('admin-username', 'children'),
     Output('admin-auth-state', 'data'),
     Output('admin-user-info', 'data'),
     Output('admin-auth-error', 'children'),
     Output('admin-auth-error', 'style')],
    [Input('admin-url', 'pathname'),
     Input('admin-url', 'search'),
     Input('login-btn', 'n_clicks'),
     Input('logout-btn', 'n_clicks'),
     Input('login-username', 'n_submit'),
     Input('login-password', 'n_submit')],
    [State('admin-auth-state', 'data'),
     State('admin-user-info', 'data'),
     State('login-username', 'value'),
     State('login-password', 'value')]
)
def handle_admin_auth(pathname, search, login_clicks, logout_clicks, username_submit, password_submit, auth_state, user_info, username, password):
    """Handle admin authentication flow with proper access control"""
    ctx = callback_context
    
    if not ctx.triggered:
        # Check existing authentication state and validate token
        if auth_state and auth_state.get('authenticated') and user_info:
            token = auth_state.get('token')
            if token:
                try:
                    # Validate existing token
                    if keycloak_auth.validate_token(token):
                        # Token is still valid
                        return (
                            {'display': 'none'},  # hide login form
                            {'display': 'block'},  # show dashboard
                            user_info.get('preferred_username', user_info.get('username', 'Admin')),
                            auth_state,
                            user_info,
                            '',
                            {'display': 'none'}
                        )
                    else:
                        # Token expired or invalid, clear session
                        return (
                            {'display': 'block'},  # show login form
                            {'display': 'none'},   # hide dashboard
                            '',
                            {'authenticated': False, 'token': None, 'error': 'Session expired'},
                            None,
                            create_auth_error_message('Session expired. Please login again.'),
                            {'display': 'block'}
                        )
                except Exception as e:
                    # Token validation error, clear session
                    return (
                        {'display': 'block'},  # show login form
                        {'display': 'none'},   # hide dashboard
                        '',
                        {'authenticated': False, 'token': None, 'error': f'Session validation error: {str(e)}'},
                        None,
                        create_auth_error_message(f'Session validation error: {str(e)}'),
                        {'display': 'block'}
                    )
        
        # Default: show login form
        return (
            {'display': 'block'},  # show login form
            {'display': 'none'},   # hide dashboard
            '',
            {'authenticated': False, 'token': None},
            None,
            '',
            {'display': 'none'}
        )
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle logout
    if trigger_id == 'logout-btn' and logout_clicks:
        return (
            {'display': 'block'},  # show login form
            {'display': 'none'},   # hide dashboard
            '',
            {'authenticated': False, 'token': None},
            None,
            '',
            {'display': 'none'}
        )
    
    # Handle login redirect (button click or Enter key press)
    if (trigger_id == 'login-btn' and login_clicks) or \
       (trigger_id == 'login-username' and username_submit) or \
       (trigger_id == 'login-password' and password_submit):
        # Validate form inputs
        if not username or not password:
            return (
                {'display': 'block'},  # keep showing login form
                {'display': 'none'},   # hide dashboard
                '',
                {'authenticated': False, 'token': None, 'error': 'Missing credentials'},
                None,
                create_auth_error_message('Si us plau, introdueix el nom d\'usuari i la contrasenya.'),
                {'display': 'block'}
            )
        
        try:
            # Try to get token using provided credentials
            admin_token = keycloak_auth.get_admin_token(username, password)
            if admin_token:
                user_info = keycloak_auth.get_user_info(admin_token['access_token'])
                if user_info and keycloak_auth.has_admin_role(user_info):
                    return (
                        {'display': 'none'},  # hide login form
                        {'display': 'block'},  # show dashboard
                        user_info.get('preferred_username', 'admin'),
                        {'authenticated': True, 'token': admin_token['access_token']},
                        user_info,
                        '',
                        {'display': 'none'}
                    )
                else:
                    return (
                        {'display': 'block'},  # keep showing login form
                        {'display': 'none'},   # hide dashboard
                        '',
                        {'authenticated': False, 'token': None, 'error': 'No admin role'},
                        None,
                        create_auth_error_message('Aquest usuari no té permisos d\'administrador.'),
                        {'display': 'block'}
                    )
            else:
                return (
                    {'display': 'block'},  # keep showing login form
                    {'display': 'none'},   # hide dashboard
                    '',
                    {'authenticated': False, 'token': None, 'error': 'Token failed'},
                    None,
                    create_auth_error_message('Credencials incorrectes. Si us plau, comprova el nom d\'usuari i la contrasenya.'),
                    {'display': 'block'}
                )
        except Exception as e:
            return (
                {'display': 'block'},  # keep showing login form
                {'display': 'none'},   # hide dashboard
                '',
                {'authenticated': False, 'token': None, 'error': f'Auth error: {str(e)}'},
                None,
                create_auth_error_message(f'Error d\'autenticació: {str(e)}'),
                {'display': 'block'}
            )
    
    # Check if coming back from Keycloak with auth code
    if search and 'code=' in search:
        # Parse authorization code
        query_params = parse_qs(search[1:])  # Remove the '?' 
        code = query_params.get('code', [None])[0]
        
        if code:
            try:
                # Exchange code for token with actual Keycloak
                token_data = keycloak_auth.exchange_code_for_token(code)
                
                if token_data and token_data.get('access_token'):
                    # Validate token and get user info
                    user_info = keycloak_auth.get_user_info(token_data['access_token'])
                    
                    if user_info and keycloak_auth.has_admin_role(user_info):
                        return (
                            {'display': 'none'},  # hide login form
                            {'display': 'block'},  # show dashboard
                            user_info.get('preferred_username', 'Admin'),
                            {'authenticated': True, 'token': token_data['access_token']},
                            user_info,
                            '',
                            {'display': 'none'}
                        )
                    else:
                        # User doesn't have admin role
                        return (
                            {'display': 'block'},  # show login form
                            {'display': 'none'},   # hide dashboard
                            '',
                            {'authenticated': False, 'token': None, 'error': 'Access denied: Admin role required'},
                            None,
                            create_auth_error_message('Access denied: You need admin privileges to access this panel.'),
                            {'display': 'block'}
                        )
                else:
                    # Token exchange failed
                    return (
                        {'display': 'block'},  # show login form
                        {'display': 'none'},   # hide dashboard
                        '',
                        {'authenticated': False, 'token': None, 'error': 'Authentication failed'},
                        None,
                        create_auth_error_message('Authentication failed. Please check your credentials.'),
                        {'display': 'block'}
                    )
            except Exception as e:
                return (
                    {'display': 'block'},  # show login form
                    {'display': 'none'},   # hide dashboard
                    '',
                    {'authenticated': False, 'token': None, 'error': f'Auth error: {str(e)}'},
                    None,
                    create_auth_error_message(f'Authentication error: {str(e)}'),
                    {'display': 'block'}
                )
    
    # Default: show login form
    return (
        {'display': 'block'},  # show login form
        {'display': 'none'},   # hide dashboard
        '',
        {'authenticated': False, 'token': None},
        None,
        '',
        {'display': 'none'}
    )

# Tab switching callback
@callback(
    [Output('tab-samples', 'className'),
     Output('tab-stats', 'className'),
     Output('tab-logs', 'className'),
     Output('admin-active-tab', 'data'),
     Output('admin-tab-content', 'children')],
    [Input('tab-samples', 'n_clicks'),
     Input('tab-stats', 'n_clicks'),
     Input('tab-logs', 'n_clicks')],
    [State('admin-samples-data', 'data'),
     State('admin-stats-data', 'data'),
     State('admin-logs-data', 'data'),
     State('admin-auth-state', 'data')]
)
def switch_admin_tabs(samples_clicks, stats_clicks, logs_clicks, samples_data, stats_data, logs_data, auth_state):
    """Handle admin tab switching - requires authentication"""
    # Check authentication first
    if not auth_state or not auth_state.get('authenticated'):
        raise PreventUpdate
    
    ctx = callback_context
    
    if not ctx.triggered:
        # Default to samples tab - ensure we have data
        if not samples_data:
            samples_data = []
        if not stats_data:
            stats_data = {}
        if not logs_data:
            logs_data = []
        return (
            'admin-tab active-tab', 'admin-tab', 'admin-tab',
            'samples',
            create_admin_tabs_content('samples', samples_data, stats_data, logs_data)
        )
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'tab-samples':
        return (
            'admin-tab active-tab', 'admin-tab', 'admin-tab',
            'samples',
            create_admin_tabs_content('samples', samples_data, stats_data, logs_data)
        )
    elif trigger_id == 'tab-stats':
        return (
            'admin-tab', 'admin-tab active-tab', 'admin-tab',
            'stats',
            create_admin_tabs_content('stats', samples_data, stats_data, logs_data)
        )
    elif trigger_id == 'tab-logs':
        return (
            'admin-tab', 'admin-tab', 'admin-tab active-tab',
            'logs',
            create_admin_tabs_content('logs', samples_data, stats_data, logs_data)
        )
    
    raise PreventUpdate

# Load admin data callback
@callback(
    [Output('admin-samples-data', 'data'),
     Output('admin-stats-data', 'data'),
     Output('admin-logs-data', 'data')],
    [Input('admin-active-tab', 'data'),
     Input('admin-auth-state', 'data')],
    prevent_initial_call=True
)
def load_admin_data(active_tab, auth_state):
    """Load admin data when tab is activated or user authenticates"""
    # Check authentication first
    if not auth_state or not auth_state.get('authenticated'):
        raise PreventUpdate
    
    # Validate token
    token = auth_state.get('token')
    if not token or not keycloak_auth.validate_token(token):
        raise PreventUpdate
    
    # Fetch real data from backend API
    backend_url = get_backend_url()
    samples_data = []
    stats_data = {}
    
    try:
        # Fetch all samples (including unvalidated) from admin endpoint
        response = requests.get(f"{backend_url}/api/mostres/admin/all")
        if response.status_code == 200:
            samples_data = response.json()
        else:
            print(f"Error fetching admin samples: {response.status_code}")
            
        # Fetch statistics including visits from admin statistics endpoint
        token = auth_state.get('token')
        if token:
            headers = {'Authorization': f'Bearer admin-{token}'}
            stats_response = requests.get(f"{backend_url}/api/admin/statistics", headers=headers)
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print(f"DEBUG: Got stats data from backend: {stats_data}")
                print(f"DEBUG: Visits data in stats: {stats_data.get('visits_last_7_days', 'NOT FOUND')}")
            else:
                print(f"Error fetching admin statistics: {stats_response.status_code}")
                # Fallback to calculate basic statistics from samples data
                total_samples = len(samples_data)
                validated_samples = sum(1 for sample in samples_data if sample.get('validated', False))
                pending_samples = total_samples - validated_samples
                
                # Group by location
                locations = {}
                for sample in samples_data:
                    location = sample.get('punt_mostreig', 'Unknown')
                    locations[location] = locations.get(location, 0) + 1
                
                stats_data = {
                    'total_samples': total_samples,
                    'validated_samples': validated_samples,
                    'pending_samples': pending_samples,
                    'samples_by_location': locations
                }
        
    except Exception as e:
        print(f"Error loading admin data: {e}")
        # Fallback to empty data
        samples_data = []
        stats_data = {
            'total_samples': 0,
            'validated_samples': 0,
            'pending_samples': 0,
            'samples_by_location': {}
        }
    
    # Fetch logs data if logs tab is active
    logs_data = []
    if active_tab == 'logs':
        try:
            # Get logs from backend API
            token = auth_state.get('token')
            if token:
                headers = {'Authorization': f'Bearer admin-{token}'}
                response = requests.get(f"{backend_url}/api/admin/logs", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    all_logs_data = response.json()
                    logs_data = []
                    
                    # Format logs from all services
                    for service_name, service_logs in all_logs_data.get('services', {}).items():
                        logs_data.append(f"=== {service_name.upper()} SERVICE LOGS ===")
                        
                        if service_logs.get('error'):
                            logs_data.extend(service_logs.get('logs', []))
                        else:
                            service_log_lines = service_logs.get('logs', [])
                            # Add only the last 25 lines per service to avoid overwhelming display
                            recent_logs = service_log_lines[-25:] if len(service_log_lines) > 25 else service_log_lines
                            logs_data.extend(recent_logs)
                        
                        logs_data.append("")  # Empty line separator
                
                else:
                    logs_data = [f"Error fetching logs: HTTP {response.status_code}"]
            else:
                logs_data = ["Authentication required to view logs"]
                
        except Exception as e:
            print(f"Error fetching logs: {e}")
            logs_data = [f'Error fetching logs: {str(e)}']
    
    return samples_data, stats_data, logs_data

# Sample management callbacks
@callback(
    [Output('admin-status-message', 'children'),
     Output('delete-confirmation-modal', 'style'),
     Output('delete-confirmation-text', 'children')],
    [Input('bulk-validate-btn', 'n_clicks'),
     Input('bulk-unvalidate-btn', 'n_clicks'),
     Input('bulk-delete-btn', 'n_clicks')],
    [State('admin-samples-table', 'selected_rows'),
     State('admin-samples-table', 'data'),
     State('admin-auth-state', 'data')]
)
def handle_bulk_operations(validate_clicks, unvalidate_clicks, delete_clicks, selected_rows, table_data, auth_state):
    """Handle bulk operations on samples - requires authentication and admin role"""
    # Check authentication first
    if not auth_state or not auth_state.get('authenticated'):
        raise PreventUpdate
    
    # Validate token
    token = auth_state.get('token')
    if not token or not keycloak_auth.validate_token(token):
        return (
            html.Div([
                html.P("Session expired. Please login again.", 
                       style={'color': '#e74c3c', 'margin': '0'})
            ], style={
                'backgroundColor': '#fdf2f2',
                'padding': '1rem',
                'borderRadius': '4px',
                'border': '1px solid #fca5a5'
            }),
            {'display': 'none'},  # Hide modal
            ""  # Empty confirmation text
        )
    
    ctx = callback_context
    if not ctx.triggered or not selected_rows:
        raise PreventUpdate
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    selected_sample_ids = [table_data[i]['id'] for i in selected_rows]
    backend_url = get_backend_url()
    
    if trigger_id == 'bulk-validate-btn':
        # Validate selected samples via API
        success_count = 0
        failed_count = 0
        
        for sample_id in selected_sample_ids:
            try:
                response = requests.post(f"{backend_url}/api/mostres/{sample_id}/validate")
                if response.status_code == 200:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Error validating sample {sample_id}: {e}")
                failed_count += 1
        
        if failed_count > 0:
            return (
                html.Div([
                    html.P(f"S'han validat {success_count} mostres. {failed_count} han fallat.", 
                           style={'color': '#856404', 'margin': '0'})
                ], style={
                    'backgroundColor': '#fff3cd',
                    'padding': '1rem',
                    'borderRadius': '4px',
                    'border': '1px solid #ffeaa7'
                }),
                {'display': 'none'},  # Hide modal
                ""  # Empty confirmation text
            )
        else:
            return (
                html.Div([
                    html.P(f"S'han validat {success_count} mostres correctament.", 
                           style={'color': '#28a745', 'margin': '0'})
                ], style={
                    'backgroundColor': '#d4edda',
                    'padding': '1rem',
                    'borderRadius': '4px',
                    'border': '1px solid #c3e6cb'
                }),
                {'display': 'none'},  # Hide modal
                ""  # Empty confirmation text
            )
            
    elif trigger_id == 'bulk-unvalidate-btn':
        # Invalidate selected samples via API
        success_count = 0
        failed_count = 0
        
        for sample_id in selected_sample_ids:
            try:
                response = requests.post(f"{backend_url}/api/mostres/{sample_id}/invalidate")
                if response.status_code == 200:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Error invalidating sample {sample_id}: {e}")
                failed_count += 1
        
        if failed_count > 0:
            return (
                html.Div([
                    html.P(f"S'han marcat com a pendents {success_count} mostres. {failed_count} han fallat.", 
                           style={'color': '#856404', 'margin': '0'})
                ], style={
                    'backgroundColor': '#fff3cd',
                    'padding': '1rem',
                    'borderRadius': '4px',
                    'border': '1px solid #ffeaa7'
                }),
                {'display': 'none'},  # Hide modal
                ""  # Empty confirmation text
            )
        else:
            return (
                html.Div([
                    html.P(f"S'han marcat com a pendents {success_count} mostres correctament.", 
                           style={'color': '#856404', 'margin': '0'})
                ], style={
                    'backgroundColor': '#fff3cd',
                    'padding': '1rem',
                    'borderRadius': '4px',
                    'border': '1px solid #ffeaa7'
                }),
                {'display': 'none'},  # Hide modal
                ""  # Empty confirmation text
            )
            
    elif trigger_id == 'bulk-delete-btn':
        # Show confirmation modal for deletion
        confirmation_text = f"Esteu segur que voleu eliminar {len(selected_sample_ids)} mostres? Aquesta acció no es pot desfer."
        return (
            html.Div(),  # Empty status message
            {'display': 'block'},  # Show modal
            confirmation_text
        )
    
    # Default case - no modal, empty status
    return html.Div(), {'display': 'none'}, ""

# Clear login form callback
@callback(
    [Output('login-username', 'value'),
     Output('login-password', 'value')],
    [Input('admin-auth-state', 'data')],
    prevent_initial_call=True
)
def clear_login_form(auth_state):
    """Clear login form when authentication state changes"""
    if auth_state and auth_state.get('authenticated'):
        # Clear form on successful login
        return '', ''
    elif auth_state and auth_state.get('error'):
        # Clear password on error, keep username
        return no_update, ''
    
    return no_update, no_update

# Initialize admin tab content on login
@callback(
    Output('admin-tab-content', 'children', allow_duplicate=True),
    [Input('admin-samples-data', 'data'),
     Input('admin-stats-data', 'data')],
    [State('admin-active-tab', 'data'),
     State('admin-auth-state', 'data')],
    prevent_initial_call=True
)
def update_tab_content_on_data_load(samples_data, stats_data, active_tab, auth_state):
    """Update tab content when data is loaded"""
    if not auth_state or not auth_state.get('authenticated'):
        raise PreventUpdate
    
    # Default to samples tab if no active tab is set
    if not active_tab:
        active_tab = 'samples'
    
    return create_admin_tabs_content(active_tab, samples_data, stats_data)

# Manual refresh callback - only works when button is rendered
@callback(
    [Output('admin-samples-data', 'data', allow_duplicate=True),
     Output('admin-stats-data', 'data', allow_duplicate=True)],
    [Input('refresh-samples-btn', 'n_clicks')],
    [State('admin-auth-state', 'data')],
    prevent_initial_call=True
)
def manual_refresh_data(refresh_clicks, auth_state):
    """Handle manual refresh button clicks"""
    if not refresh_clicks or not auth_state or not auth_state.get('authenticated'):
        raise PreventUpdate
    
    # Fetch fresh data from backend
    backend_url = get_backend_url()
    samples_data = []
    stats_data = {}
    
    try:
        response = requests.get(f"{backend_url}/api/mostres/admin/all")
        if response.status_code == 200:
            samples_data = response.json()
            
            # Calculate fresh statistics
            total_samples = len(samples_data)
            validated_samples = sum(1 for sample in samples_data if sample.get('validated', False))
            pending_samples = total_samples - validated_samples
            
            locations = {}
            for sample in samples_data:
                location = sample.get('punt_mostreig', 'Unknown')
                locations[location] = locations.get(location, 0) + 1
            
            stats_data = {
                'total_samples': total_samples,
                'validated_samples': validated_samples,
                'pending_samples': pending_samples,
                'samples_by_location': locations
            }
    except Exception as e:
        print(f"Error refreshing data: {e}")
        raise PreventUpdate
    
    return samples_data, stats_data

# Auto-refresh after bulk operations
@callback(
    [Output('admin-samples-data', 'data', allow_duplicate=True),
     Output('admin-stats-data', 'data', allow_duplicate=True)],
    [Input('bulk-validate-btn', 'n_clicks'),
     Input('bulk-unvalidate-btn', 'n_clicks')],
    [State('admin-samples-table', 'selected_rows'),
     State('admin-auth-state', 'data')],
    prevent_initial_call=True
)
def auto_refresh_after_operations(validate_clicks, unvalidate_clicks, selected_rows, auth_state):
    """Auto-refresh data after bulk operations"""
    ctx = callback_context
    if not ctx.triggered or not selected_rows or not auth_state or not auth_state.get('authenticated'):
        raise PreventUpdate
    
    # Fetch fresh data from backend
    backend_url = get_backend_url()
    samples_data = []
    stats_data = {}
    
    try:
        response = requests.get(f"{backend_url}/api/mostres/admin/all")
        if response.status_code == 200:
            samples_data = response.json()
            
            # Calculate fresh statistics
            total_samples = len(samples_data)
            validated_samples = sum(1 for sample in samples_data if sample.get('validated', False))
            pending_samples = total_samples - validated_samples
            
            locations = {}
            for sample in samples_data:
                location = sample.get('punt_mostreig', 'Unknown')
                locations[location] = locations.get(location, 0) + 1
            
            stats_data = {
                'total_samples': total_samples,
                'validated_samples': validated_samples,
                'pending_samples': pending_samples,
                'samples_by_location': locations
            }
    except Exception as e:
        print(f"Error refreshing data: {e}")
        raise PreventUpdate
    
    return samples_data, stats_data


# Delete confirmation callbacks
@callback(
    [Output('delete-confirmation-modal', 'style', allow_duplicate=True),
     Output('admin-status-message', 'children', allow_duplicate=True)],
    [Input('confirm-delete-btn', 'n_clicks'),
     Input('cancel-delete-btn', 'n_clicks')],
    [State('admin-samples-table', 'selected_rows'),
     State('admin-samples-table', 'data'),
     State('admin-auth-state', 'data')],
    prevent_initial_call=True
)
def handle_delete_confirmation(confirm_clicks, cancel_clicks, selected_rows, table_data, auth_state):
    """Handle delete confirmation modal actions"""
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'cancel-delete-btn':
        # Close modal without action
        return {'display': 'none'}, html.Div()
    
    elif trigger_id == 'confirm-delete-btn':
        if not selected_rows or not auth_state or not auth_state.get('authenticated'):
            return {'display': 'none'}, html.Div()
        
        # Perform actual deletion
        selected_sample_ids = [table_data[i]['id'] for i in selected_rows]
        backend_url = get_backend_url()
        success_count = 0
        failed_count = 0
        
        # Get authentication token
        token = auth_state.get('token')
        headers = {'Authorization': f'Bearer admin-{token}'} if token else {}
        
        for sample_id in selected_sample_ids:
            try:
                # Use the correct admin endpoint with authentication
                response = requests.delete(
                    f"{backend_url}/api/admin/samples/{sample_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    success_count += 1
                else:
                    print(f"Delete failed for sample {sample_id}: {response.status_code} - {response.text}")
                    failed_count += 1
            except Exception as e:
                print(f"Error deleting sample {sample_id}: {e}")
                failed_count += 1
        
        # Close modal and show result
        if failed_count > 0:
            status_message = html.Div([
                html.P(f"S'han eliminat {success_count} mostres. {failed_count} han fallat.", 
                       style={'color': '#856404', 'margin': '0'})
            ], style={
                'backgroundColor': '#fff3cd',
                'padding': '1rem',
                'borderRadius': '4px',
                'border': '1px solid #ffeaa7'
            })
        else:
            status_message = html.Div([
                html.P(f"S'han eliminat {success_count} mostres correctament.", 
                       style={'color': '#721c24', 'margin': '0'})
            ], style={
                'backgroundColor': '#f8d7da',
                'padding': '1rem',
                'borderRadius': '4px',
                'border': '1px solid #f5c6cb'
            })
        
        return {'display': 'none'}, status_message
    
    raise PreventUpdate

# Select/Unselect all callback
@callback(
    [Output('admin-samples-table', 'selected_rows'),
     Output('select-all-btn', 'children')],
    [Input('select-all-btn', 'n_clicks')],
    [State('admin-samples-table', 'selected_rows'),
     State('admin-samples-table', 'data'),
     State('admin-samples-table', 'derived_virtual_data')],
    prevent_initial_call=True
)
def toggle_select_all(n_clicks, current_selected, table_data, filtered_data):
    """Toggle select/unselect all currently visible (filtered) rows"""
    if not n_clicks or not table_data:
        raise PreventUpdate
    
    # Use filtered data if available (when filtering is active), otherwise use all data
    visible_data = filtered_data if filtered_data is not None else table_data
    
    if not visible_data:
        raise PreventUpdate
    
    # Get the indices of visible rows in the original data
    visible_indices = []
    for visible_row in visible_data:
        # Find the index of this row in the original table_data
        for i, original_row in enumerate(table_data):
            if original_row['id'] == visible_row['id']:
                visible_indices.append(i)
                break
    
    # Check if all visible rows are currently selected
    visible_selected = [i for i in current_selected if i in visible_indices]
    all_visible_selected = len(visible_selected) == len(visible_indices)
    
    if all_visible_selected:
        # Unselect all visible rows (keep selection of non-visible rows)
        new_selected = [i for i in current_selected if i not in visible_indices]
        button_content = [
            html.I(className="fas fa-square", style={'marginRight': '8px'}),
            "Seleccionar Tot"
        ]
    else:
        # Select all visible rows (add to existing selection)
        new_selected = list(set(current_selected + visible_indices))
        button_content = [
            html.I(className="fas fa-check-square", style={'marginRight': '8px'}),
            "Deseleccionar Tot"
        ]
    
    return new_selected, button_content

# Logs management callbacks
@callback(
    Output('admin-logs-data', 'data', allow_duplicate=True),
    [Input('refresh-logs-btn', 'n_clicks')],
    [State('admin-auth-state', 'data')],
    prevent_initial_call=True
)
def refresh_logs(n_clicks, auth_state):
    """Refresh logs data"""
    if not n_clicks or not auth_state or not auth_state.get('authenticated'):
        raise PreventUpdate
    
    try:
        import datetime
        import requests
        from utils.helpers import get_backend_url
        
        backend_url = get_backend_url()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get logs from backend API
        token = auth_state.get('token')
        if token:
            headers = {'Authorization': f'Bearer admin-{token}'}
            response = requests.get(f"{backend_url}/api/admin/logs", headers=headers, timeout=15)
            
            if response.status_code == 200:
                all_logs_data = response.json()
                logs_data = [f"[{current_time}] INFO: Logs refreshed successfully"]
                
                # Format logs from all services
                for service_name, service_logs in all_logs_data.get('services', {}).items():
                    logs_data.append(f"\n=== {service_name.upper()} SERVICE LOGS ===")
                    
                    if service_logs.get('error'):
                        logs_data.extend(service_logs.get('logs', []))
                    else:
                        service_log_lines = service_logs.get('logs', [])
                        # Add only the last 30 lines per service
                        recent_logs = service_log_lines[-30:] if len(service_log_lines) > 30 else service_log_lines
                        logs_data.extend(recent_logs)
                    
                    logs_data.append("")  # Empty line separator
                
            else:
                logs_data = [
                    f"[{current_time}] ERROR: Failed to fetch logs from backend",
                    f"[{current_time}] ERROR: HTTP {response.status_code}: {response.text}"
                ]
        else:
            logs_data = [f"[{current_time}] ERROR: No authentication token available"]
            
    except Exception as e:
        import datetime
        print(f"Error refreshing logs: {e}")
        logs_data = [f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] ERROR: {str(e)}']
    
    return logs_data

@callback(
    Output('logs-content', 'children'),
    [Input('admin-logs-data', 'data'),
     Input('log-level-filter', 'value'),
     Input('service-filter', 'value')],
    prevent_initial_call=True
)
def update_logs_content(logs_data, log_level_filter, service_filter):
    """Update logs content based on filters"""
    if not logs_data:
        return [html.P("No hi ha logs disponibles.", style={
            'textAlign': 'center',
            'color': '#6c757d',
            'padding': '2rem'
        })]
    
    filtered_logs = logs_data
    
    # Apply service filter if not 'all'
    if service_filter and service_filter != 'all':
        in_service_section = False
        service_filtered_logs = []
        
        for log_line in logs_data:
            # Check if we're entering the desired service section
            if f"=== {service_filter} SERVICE LOGS ===" in log_line:
                in_service_section = True
                service_filtered_logs.append(log_line)
                continue
            
            # Check if we're entering a different service section
            if "=== " in log_line and " SERVICE LOGS ===" in log_line and service_filter not in log_line:
                in_service_section = False
                continue
            
            # Add log lines that belong to the selected service
            if in_service_section:
                service_filtered_logs.append(log_line)
        
        filtered_logs = service_filtered_logs
    
    # Apply log level filter if not 'all'
    if log_level_filter and log_level_filter != 'all':
        filtered_logs = [log for log in filtered_logs if log_level_filter in log or "===" in log]
    
    # Take only the last 150 lines for performance
    display_logs = filtered_logs[-150:] if len(filtered_logs) > 150 else filtered_logs
    
    if not display_logs:
        return [html.P(f"No s'han trobat logs amb el nivell '{log_level_filter}'.", style={
            'textAlign': 'center',
            'color': '#6c757d',
            'padding': '2rem'
        })]
    
    # Style different log levels
    styled_logs = []
    for log_line in display_logs:
        style = {
            'margin': '0',
            'padding': '2px 0',
            'fontFamily': 'Monaco, Menlo, "Ubuntu Mono", monospace',
            'fontSize': '0.85rem',
            'lineHeight': '1.4'
        }
        
        # Color code different log levels
        if 'ERROR' in log_line:
            style['color'] = '#ff6b6b'
        elif 'WARNING' in log_line:
            style['color'] = '#ffd93d'
        elif 'INFO' in log_line:
            style['color'] = '#74c0fc'
        else:
            style['color'] = '#e2e8f0'
        
        styled_logs.append(html.Div(log_line, style=style))
    
    return [html.Div(styled_logs, style={
        'backgroundColor': '#2d3748',
        'padding': '1rem',
        'borderRadius': '4px',
        'maxHeight': '600px',
        'overflowY': 'auto',
        'whiteSpace': 'pre-wrap',
        'wordWrap': 'break-word'
    })]

@callback(
    [Output('admin-logs-data', 'data', allow_duplicate=True),
     Output('admin-status-message', 'children', allow_duplicate=True)],
    [Input('clear-logs-btn', 'n_clicks')],
    [State('admin-auth-state', 'data')],
    prevent_initial_call=True
)
def clear_logs(n_clicks, auth_state):
    """Clear logs (this is just a UI clear, actual logs remain in containers)"""
    if not n_clicks or not auth_state or not auth_state.get('authenticated'):
        raise PreventUpdate
    
    return [], html.Div([
        html.P("Logs nets de la visualització.", 
               style={'color': '#28a745', 'margin': '0'})
    ], style={
        'backgroundColor': '#d4edda',
        'padding': '1rem',
        'borderRadius': '4px',
        'border': '1px solid #c3e6cb'
    })