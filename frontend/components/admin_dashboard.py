"""
Admin dashboard components for sample management
"""
from dash import html, dcc, dash_table
import pandas as pd
from datetime import datetime
from utils.helpers import format_date_catalan

def create_admin_statistics(stats_data):
    """Create admin statistics overview"""
    return html.Div([
        html.H3("Resum General", style={'marginBottom': '1.5rem', 'color': '#2c3e50'}),
        
        # Main statistics cards
        html.Div([
            html.Div([
                html.Span(str(stats_data.get('total_samples', 0)), className='admin-stat-number'),
                html.Span("Total Mostres", className='admin-stat-label')
            ], className='admin-stat-card'),
            
            html.Div([
                html.Span(str(stats_data.get('validated_samples', 0)), className='admin-stat-number'),
                html.Span("Mostres Validades", className='admin-stat-label')
            ], className='admin-stat-card'),
            
            html.Div([
                html.Span(str(stats_data.get('pending_samples', 0)), className='admin-stat-number'),
                html.Span("Pendents de Validar", className='admin-stat-label')
            ], className='admin-stat-card'),
            
            html.Div([
                html.Span(str(stats_data.get('total_visits_30_days', 0)), className='admin-stat-number'),
                html.Span("Visitants únics (30 dies)", className='admin-stat-label')
            ], className='admin-stat-card')
        ], className='admin-stats-grid'),
        
        # Visits chart section
        html.Div([
            html.H4("Visitants únics dels últims 7 dies", style={'marginBottom': '1rem', 'color': '#2c3e50'}),
            html.Div(id='visits-chart-container', children=[
                create_visits_chart(stats_data.get('visits_last_7_days', []))
            ])
        ], style={
            'backgroundColor': 'white',
            'padding': '1.5rem',
            'borderRadius': '8px',
            'border': '1px solid #dee2e6',
            'marginTop': '2rem'
        }),
        
        # Monthly visits chart section
        html.Div([
            html.H4("Visitants únics per mes de l'últim any", style={'marginBottom': '1rem', 'color': '#2c3e50'}),
            html.Div(id='visits-monthly-chart-container', children=[
                create_monthly_visits_chart(stats_data.get('visits_last_year_monthly', []))
            ])
        ], style={
            'backgroundColor': 'white',
            'padding': '1.5rem',
            'borderRadius': '8px',
            'border': '1px solid #dee2e6',
            'marginTop': '2rem'
        }),
        
        # Locations breakdown
        html.Div([
            html.H4("Mostres per ubicació", style={'marginBottom': '1rem', 'color': '#2c3e50'}),
            create_locations_breakdown(stats_data.get('samples_by_location', {}))
        ], style={
            'backgroundColor': 'white',
            'padding': '1.5rem',
            'borderRadius': '8px',
            'border': '1px solid #dee2e6',
            'marginTop': '1rem'
        })
    ])

def create_visits_chart(visits_data):
    """Create a simple visits chart using HTML/CSS"""
    print(f"DEBUG: create_visits_chart called with data: {visits_data}")
    print(f"DEBUG: visits_data type: {type(visits_data)}, empty check: {not visits_data}")
    
    if not visits_data:
        return html.P("No hi ha dades de visitants disponibles.", style={
            'textAlign': 'center',
            'color': '#6c757d',
            'padding': '2rem'
        })
    
    # Find max visits for scaling
    max_visits = max([day['visits'] for day in visits_data], default=1)
    
    # Create bar chart
    chart_bars = []
    for day_data in visits_data:
        height_percent = (day_data['visits'] / max_visits) * 100
        date_label = datetime.strptime(day_data['date'], '%Y-%m-%d').strftime('%d/%m')
        
        chart_bars.append(
            html.Div([
                html.Div(
                    style={
                        'height': f'{height_percent}%',
                        'backgroundColor': '#3498db',
                        'width': '100%',
                        'borderRadius': '4px 4px 0 0',
                        'transition': 'all 0.3s ease'
                    }
                ),
                html.Div(str(day_data['visits']), style={
                    'textAlign': 'center',
                    'fontSize': '0.8rem',
                    'fontWeight': 'bold',
                    'color': '#2c3e50',
                    'marginTop': '4px'
                }),
                html.Div(date_label, style={
                    'textAlign': 'center',
                    'fontSize': '0.7rem',
                    'color': '#7f8c8d',
                    'marginTop': '2px'
                })
            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'justifyContent': 'flex-end',
                'height': '150px',
                'minWidth': '60px',
                'padding': '0 5px'
            })
        )
    
    return html.Div(chart_bars, style={
        'display': 'flex',
        'alignItems': 'flex-end',
        'justifyContent': 'space-around',
        'height': '200px',
        'padding': '1rem',
        'backgroundColor': '#f8f9fa',
        'borderRadius': '4px',
        'border': '1px solid #e9ecef'
    })

def create_monthly_visits_chart(visits_monthly_data):
    """Create a monthly visits chart using HTML/CSS"""
    if not visits_monthly_data:
        return html.P("No hi ha dades de visitants mensuals disponibles.", style={
            'textAlign': 'center',
            'color': '#6c757d',
            'padding': '2rem'
        })
    
    # Find max visits for scaling
    max_visits = max([month['visits'] for month in visits_monthly_data], default=1)
    if max_visits == 0:
        max_visits = 1  # Avoid division by zero
    
    # Create bar chart
    chart_bars = []
    for month_data in visits_monthly_data:
        height_percent = (month_data['visits'] / max_visits) * 100
        month_label = datetime.strptime(month_data['month'], '%Y-%m').strftime('%m/%y')
        
        chart_bars.append(
            html.Div([
                html.Div(
                    style={
                        'height': f'{height_percent}%',
                        'backgroundColor': '#e74c3c',
                        'width': '100%',
                        'borderRadius': '4px 4px 0 0',
                        'transition': 'all 0.3s ease'
                    }
                ),
                html.Div(str(month_data['visits']), style={
                    'textAlign': 'center',
                    'fontSize': '0.8rem',
                    'fontWeight': 'bold',
                    'color': '#2c3e50',
                    'marginTop': '4px'
                }),
                html.Div(month_label, style={
                    'textAlign': 'center',
                    'fontSize': '0.7rem',
                    'color': '#7f8c8d',
                    'marginTop': '2px'
                })
            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'justifyContent': 'flex-end',
                'height': '150px',
                'minWidth': '60px',
                'padding': '0 5px'
            })
        )
    
    return html.Div(chart_bars, style={
        'display': 'flex',
        'alignItems': 'flex-end',
        'justifyContent': 'space-around',
        'height': '200px',
        'padding': '1rem',
        'backgroundColor': '#f8f9fa',
        'borderRadius': '4px',
        'border': '1px solid #e9ecef'
    })

def create_locations_breakdown(locations_data):
    """Create locations breakdown display"""
    if not locations_data:
        return html.P("No hi ha dades d'ubicacions disponibles.", style={
            'textAlign': 'center',
            'color': '#6c757d',
            'padding': '1rem'
        })
    
    total_samples = sum(locations_data.values())
    location_items = []
    
    for location, count in sorted(locations_data.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_samples * 100) if total_samples > 0 else 0
        
        location_items.append(
            html.Div([
                html.Div([
                    html.Span(location, style={'fontWeight': 'bold', 'color': '#2c3e50'}),
                    html.Span(f"{count} mostres ({percentage:.1f}%)", style={'color': '#7f8c8d', 'fontSize': '0.9rem'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '8px'}),
                html.Div(style={
                    'height': '8px',
                    'backgroundColor': '#e9ecef',
                    'borderRadius': '4px',
                    'overflow': 'hidden'
                }, children=[
                    html.Div(style={
                        'height': '100%',
                        'width': f'{percentage}%',
                        'backgroundColor': '#28a745',
                        'borderRadius': '4px',
                        'transition': 'width 0.3s ease'
                    })
                ])
            ], style={'marginBottom': '1rem'})
        )
    
    return html.Div(location_items)

def create_samples_management_table(samples):
    """Create samples management table"""
    if not samples:
        return html.Div([
            html.P("No s'han trobat mostres.", style={'textAlign': 'center', 'color': '#6c757d', 'padding': '2rem'})
        ])
    
    # Convert samples to DataFrame for easier manipulation
    df = pd.DataFrame(samples)
    
    # Format sample date (data)
    if 'data' in df.columns:
        df['data'] = df['data'].apply(lambda x: format_date_catalan(datetime.strptime(x, '%Y-%m-%d'), 'short') if x else 'N/A')
    
    # Format submit date (created_at)
    if 'created_at' in df.columns:
        df['submit_date'] = df['created_at'].apply(lambda x: 
            format_date_catalan(datetime.fromisoformat(x.replace('Z', '+00:00')), 'short') if x else 'N/A'
        )
    else:
        df['submit_date'] = 'N/A'
    
    # Format validation status
    if 'validated' in df.columns:
        df['estat'] = df['validated'].apply(lambda x: 'Validada' if x else 'Pendent')
    else:
        df['estat'] = 'N/A'
    
    # Select only the requested columns
    display_columns = ['id', 'data', 'punt_mostreig', 'submit_date', 'estat']
    available_columns = [col for col in display_columns if col in df.columns]
    
    return html.Div([
        html.Div([
            html.H3("Gestió de Mostres", style={'marginBottom': '1rem', 'color': '#2c3e50'}),
            html.Div([
                html.Button(
                    [
                        html.I(className="fas fa-check-square", style={'marginRight': '8px'}),
                        "Seleccionar Tot"
                    ],
                    id='select-all-btn',
                    className='btn-standard admin-action-btn',
                    style={
                        'backgroundColor': '#6c757d',
                        'color': 'white',
                        'marginRight': '0.5rem'
                    }
                ),
                html.Button(
                    "Validar Seleccionades",
                    id='bulk-validate-btn',
                    className='btn-standard admin-action-btn btn-validate',
                    style={'marginRight': '0.5rem'}
                ),
                html.Button(
                    "Marcar Pendents",
                    id='bulk-unvalidate-btn', 
                    className='btn-standard admin-action-btn',
                    style={'backgroundColor': '#ffc107', 'color': 'white', 'marginRight': '0.5rem'}
                ),
                html.Button(
                    "Eliminar Seleccionades",
                    id='bulk-delete-btn',
                    className='btn-standard admin-action-btn btn-delete',
                    style={'marginRight': '0.5rem'}
                ),
                html.Button(
                    [
                        html.I(className="fas fa-sync-alt", style={'marginRight': '8px'}),
                        "Actualitzar"
                    ],
                    id='refresh-samples-btn',
                    className='btn-standard admin-action-btn',
                    style={
                        'backgroundColor': '#17a2b8',
                        'color': 'white'
                    }
                )
            ], style={'marginBottom': '1rem', 'display': 'flex', 'alignItems': 'center'}),
            
            # Samples table
            dash_table.DataTable(
                id='admin-samples-table',
                data=df[available_columns].to_dict('records'),
                columns=[
                    {'name': 'ID', 'id': 'id', 'type': 'numeric'},
                    {'name': 'Data', 'id': 'data'},
                    {'name': 'Punt de Mostreig', 'id': 'punt_mostreig'},
                    {'name': 'Data Enviament', 'id': 'submit_date'},
                    {'name': 'Estat', 'id': 'estat'}
                ],
                row_selectable='multi',
                selected_rows=[],
                sort_action='native',
                sort_mode='multi',
                filter_action='native',
                page_action='native',
                page_size=25,
                style_table={
                    'overflowX': 'auto',
                    'backgroundColor': 'white',
                    'border': '1px solid #dee2e6',
                    'borderRadius': '8px'
                },
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'border': '1px solid #dee2e6'
                },
                style_data={
                    'textAlign': 'center',
                    'border': '1px solid #dee2e6'
                },
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{estat} = Validada'},
                        'backgroundColor': '#d4edda',
                        'color': '#155724'
                    },
                    {
                        'if': {'filter_query': '{estat} = Pendent'},
                        'backgroundColor': '#fff3cd',
                        'color': '#856404'
                    }
                ],
                style_cell={
                    'fontSize': '0.9rem',
                    'padding': '12px',
                    'fontFamily': 'system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif'
                }
            )
        ], className='admin-samples-table'),
        
        # Delete confirmation modal
        html.Div([
            html.Div([
                html.Div([
                    html.H4("Confirmar Eliminació", style={'marginBottom': '1rem', 'color': '#721c24'}),
                    html.P(id='delete-confirmation-text', style={'marginBottom': '1.5rem'}),
                    html.Div([
                        html.Button(
                            "Eliminar",
                            id='confirm-delete-btn',
                            className='btn-standard',
                            style={'backgroundColor': '#dc3545', 'color': 'white', 'marginRight': '0.5rem'}
                        ),
                        html.Button(
                            "Cancel·lar",
                            id='cancel-delete-btn',
                            className='btn-standard',
                            style={'backgroundColor': '#6c757d', 'color': 'white'}
                        )
                    ], style={'textAlign': 'right'})
                ], style={
                    'backgroundColor': 'white',
                    'padding': '2rem',
                    'borderRadius': '8px',
                    'position': 'relative',
                    'maxWidth': '500px',
                    'margin': '0 auto',
                    'border': '2px solid #f5c6cb'
                })
            ], style={
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'width': '100%',
                'height': '100%',
                'backgroundColor': 'rgba(0,0,0,0.5)',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'zIndex': '9999'
            })
        ], id='delete-confirmation-modal', style={'display': 'none'})
    ])

def create_sample_edit_modal():
    """Create modal for editing sample data"""
    return html.Div([
        html.Div([
            html.Div([
                html.H4("Editar Mostra", style={'marginBottom': '1rem'}),
                html.Button("×", id='close-edit-modal', style={
                    'position': 'absolute',
                    'top': '10px',
                    'right': '15px',
                    'background': 'none',
                    'border': 'none',
                    'fontSize': '1.5rem',
                    'cursor': 'pointer'
                }),
                
                html.Div(id='edit-form-content'),
                
                html.Div([
                    html.Button(
                        "Guardar Canvis",
                        id='save-sample-btn',
                        className='btn-standard',
                        style={'backgroundColor': '#28a745', 'color': 'white', 'marginRight': '0.5rem'}
                    ),
                    html.Button(
                        "Cancel·lar",
                        id='cancel-edit-btn',
                        className='btn-standard',
                        style={'backgroundColor': '#6c757d', 'color': 'white'}
                    )
                ], style={'textAlign': 'right', 'marginTop': '1.5rem'})
            ], style={
                'backgroundColor': 'white',
                'padding': '2rem',
                'borderRadius': '8px',
                'position': 'relative',
                'maxWidth': '600px',
                'margin': '0 auto',
                'maxHeight': '80vh',
                'overflowY': 'auto'
            })
        ], style={
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0,0,0,0.5)',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'zIndex': '9999'
        })
    ], id='edit-sample-modal', style={'display': 'none'})



def create_logs_viewer(logs_data=None):
    """Create logs viewer component"""
    if logs_data is None:
        logs_data = []
    
    return html.Div([
        html.Div([
            html.H3("Logs del Sistema", style={'marginBottom': '1rem', 'color': '#2c3e50'}),
            html.Div([
                html.Button(
                    [
                        html.I(className="fas fa-sync-alt", style={'marginRight': '8px'}),
                        "Actualitzar Logs"
                    ],
                    id='refresh-logs-btn',
                    className='btn-standard admin-action-btn',
                    style={
                        'backgroundColor': '#17a2b8',
                        'color': 'white',
                        'marginRight': '1rem'
                    }
                ),
                html.Button(
                    [
                        html.I(className="fas fa-trash", style={'marginRight': '8px'}),
                        "Netejar Logs"
                    ],
                    id='clear-logs-btn',
                    className='btn-standard admin-action-btn',
                    style={
                        'backgroundColor': '#dc3545',
                        'color': 'white',
                        'marginRight': '1rem'
                    }
                ),
                html.Div([
                    html.Label("Servei:", style={
                        'marginRight': '0.5rem',
                        'color': '#495057',
                        'fontSize': '0.9rem'
                    }),
                    dcc.Dropdown(
                        id='service-filter',
                        options=[
                            {'label': 'Tots els serveis', 'value': 'all'},
                            {'label': 'Backend', 'value': 'BACKEND'},
                            {'label': 'Frontend', 'value': 'FRONTEND'},
                            {'label': 'Base de dades', 'value': 'DATABASE'},
                            {'label': 'Nginx', 'value': 'NGINX'},
                            {'label': 'Keycloak', 'value': 'KEYCLOAK'}
                        ],
                        value='all',
                        style={'minWidth': '150px', 'marginRight': '1rem'}
                    )
                ], style={'display': 'inline-block'}),
                html.Div([
                    html.Label("Nivell de log:", style={
                        'marginRight': '0.5rem',
                        'color': '#495057',
                        'fontSize': '0.9rem'
                    }),
                    dcc.Dropdown(
                        id='log-level-filter',
                        options=[
                            {'label': 'Tots els nivells', 'value': 'all'},
                            {'label': 'ERROR', 'value': 'ERROR'},
                            {'label': 'WARNING', 'value': 'WARNING'},
                            {'label': 'INFO', 'value': 'INFO'},
                            {'label': 'DEBUG', 'value': 'DEBUG'}
                        ],
                        value='all',
                        style={'minWidth': '150px'}
                    )
                ], style={'display': 'inline-block'})
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'marginBottom': '1rem',
                'flexWrap': 'wrap',
                'gap': '1rem'
            })
        ]),
        
        # Logs display area
        html.Div([
            html.Div(
                id='logs-content',
                children=[
                    html.P("Carregant logs...", style={
                        'textAlign': 'center',
                        'color': '#6c757d',
                        'padding': '2rem'
                    })
                ] if not logs_data else [
                    html.Pre('\n'.join(logs_data[-100:]), style={  # Show last 100 lines
                        'backgroundColor': '#2d3748',
                        'color': '#e2e8f0',
                        'padding': '1rem',
                        'borderRadius': '4px',
                        'fontSize': '0.85rem',
                        'fontFamily': 'Monaco, Menlo, "Ubuntu Mono", monospace',
                        'maxHeight': '600px',
                        'overflowY': 'auto',
                        'whiteSpace': 'pre-wrap',
                        'wordWrap': 'break-word'
                    })
                ],
                style={
                    'backgroundColor': 'white',
                    'border': '1px solid #dee2e6',
                    'borderRadius': '8px',
                    'minHeight': '400px'
                }
            )
        ])
    ], style={'padding': '1rem'})

def create_admin_tabs_content(active_tab='samples', samples_data=None, stats_data=None, logs_data=None):
    """Create the content for admin tabs"""
    if active_tab == 'samples':
        if samples_data is None:
            samples_data = []
        return create_samples_management_table(samples_data)
    elif active_tab == 'stats':
        if stats_data is None:
            stats_data = {}
        return create_admin_statistics(stats_data)
    elif active_tab == 'logs':
        return create_logs_viewer(logs_data)
    else:
        return html.Div("Tab no trobada")