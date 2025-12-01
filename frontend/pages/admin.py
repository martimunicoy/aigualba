from dash import html, dcc, callback, Input, Output, State
import dash
from utils.auth import keycloak_auth
import urllib.parse as urlparse
from components.admin_dashboard import create_sample_edit_modal

def create_layout():
    """Create the admin page layout with modal"""
    return html.Div([
        # Hidden components for auth state
        dcc.Store(id='admin-auth-state', storage_type='session'),
        dcc.Store(id='admin-user-info', storage_type='session'),
        dcc.Location(id='admin-url', refresh=False),
        
        # Main content container
        html.Div(id='admin-content', children=[
            # Login form (shown when not authenticated)
            html.Div([
                html.Div([
                    html.H1("Administració d'AiGualba", style={
                        'textAlign': 'center',
                        'color': '#2c3e50',
                        'marginBottom': '2rem'
                    }),
                    html.P("Accés restringit només per administradors del sistema.", style={
                        'textAlign': 'center',
                        'color': '#7f8c8d',
                        'marginBottom': '2rem'
                    }),
                    
                    # Login form fields
                    html.Div([
                        html.Label("Nom d'usuari:", style={
                            'display': 'block',
                            'marginBottom': '0.5rem',
                            'fontWeight': 'bold',
                            'color': '#2c3e50'
                        }),
                        dcc.Input(
                            id='login-username',
                            type='text',
                            placeholder='Introdueix el nom d\'usuari',
                            value='',
                            n_submit=0,
                            style={
                                'width': '100%',
                                'padding': '12px',
                                'border': '1px solid #ddd',
                                'borderRadius': '4px',
                                'fontSize': '1rem',
                                'marginBottom': '1rem'
                            }
                        )
                    ], style={'marginBottom': '1rem'}),
                    
                    html.Div([
                        html.Label("Contrasenya:", style={
                            'display': 'block',
                            'marginBottom': '0.5rem',
                            'fontWeight': 'bold',
                            'color': '#2c3e50'
                        }),
                        dcc.Input(
                            id='login-password',
                            type='password',
                            placeholder='Introdueix la contrasenya',
                            value='',
                            n_submit=0,
                            style={
                                'width': '100%',
                                'padding': '12px',
                                'border': '1px solid #ddd',
                                'borderRadius': '4px',
                                'fontSize': '1rem',
                                'marginBottom': '1.5rem'
                            }
                        )
                    ], style={'marginBottom': '1.5rem'}),
                    
                    html.Div([
                        html.Button(
                            [
                                html.I(className="fas fa-sign-in-alt", style={'marginRight': '8px'}),
                                "Iniciar sessió"
                            ],
                            id='login-btn',
                            n_clicks=0,
                            className='btn-standard',
                            style={
                                'display': 'inline-block',
                                'backgroundColor': '#e74c3c',
                                'color': 'white',
                                'border': 'none',
                                'padding': '12px 24px',
                                'borderRadius': '6px',
                                'fontSize': '1rem',
                                'cursor': 'pointer',
                                'boxShadow': '0 4px 8px rgba(0,0,0,0.3)',
                                'transition': 'all 0.2s ease',
                                'width': '100%',
                                'textDecoration': 'none',
                                'textAlign': 'center',
                                'lineHeight': '1.2'
                            }
                        )
                    ], style={'textAlign': 'center'})
                ], style={
                    'backgroundColor': 'white',
                    'padding': '3rem',
                    'borderRadius': '10px',
                    'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
                    'maxWidth': '500px',
                    'margin': '0 auto'
                })
            ], id='login-form', style={'display': 'block'}),
            
            # Admin dashboard (shown when authenticated)
            html.Div([
                html.Div([
                    html.H1("Panell d'Administració", style={
                        'color': '#2c3e50',
                        'marginBottom': '1rem'
                    }),
                    html.Div([
                        html.Span("Benvingut,\u00A0", style={'color': '#7f8c8d'}),
                        html.Span(id='admin-username', style={'fontWeight': 'bold', 'color': '#2c3e50'}),
                        html.Button(
                            [
                                html.I(className="fas fa-sign-out-alt", style={'marginRight': '8px'}),
                                "Tancar sessió"
                            ],
                            id='logout-btn',
                            className='btn-standard',
                            style={
                                'backgroundColor': '#95a5a6',
                                'color': 'white',
                                'border': 'none',
                                'padding': '8px 16px',
                                'borderRadius': '4px',
                                'fontSize': '0.9rem',
                                'cursor': 'pointer',
                                'marginLeft': '2rem',
                                'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
                                'transition': 'all 0.2s ease'
                            }
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '2rem'})
                ], style={'marginBottom': '2rem'}),
                
                # Admin navigation tabs
                html.Div([
                    html.Button("Gestió de Mostres", id='tab-samples', className='admin-tab active-tab'),
                    html.Button("Estadístiques", id='tab-stats', className='admin-tab'),
                    html.Button("Logs del Sistema", id='tab-logs', className='admin-tab')
                ], className='admin-tabs', style={
                    'marginBottom': '2rem',
                    'borderBottom': '2px solid #dee2e6'
                }),
                
                # Tab content
                html.Div(id='admin-tab-content'),
                
                # Hidden components for admin functionality
                dcc.Store(id='admin-active-tab', data='samples'),
                dcc.Store(id='admin-samples-data', data=[]),
                dcc.Store(id='admin-stats-data', data={}),
                dcc.Store(id='admin-logs-data', data=[]),
                
                # Status messages
                html.Div(id='admin-status-message', style={'marginTop': '1rem'})
            ], id='admin-dashboard', style={'display': 'none'}),
            
            # Authentication error message
            html.Div(id='admin-auth-error', style={'display': 'none', 'marginTop': '2rem'})
        ]),
        
        # Add the sample edit modal
        create_sample_edit_modal()
    ], style={
        'backgroundColor': '#f8f9fa',
        'minHeight': '100vh',
        'padding': '2rem'
    })

# Register the layout function
layout = create_layout()