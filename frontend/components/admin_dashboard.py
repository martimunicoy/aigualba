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
                html.Span(f"{len(stats_data.get('samples_by_location', {}))}", className='admin-stat-number'),
                html.Span("Ubicacions Actives", className='admin-stat-label')
            ], className='admin-stat-card')
        ], className='admin-stats-grid')
    ])

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



def create_admin_tabs_content(active_tab='samples', samples_data=None, stats_data=None):
    """Create the content for admin tabs"""
    if active_tab == 'samples':
        if samples_data is None:
            samples_data = []
        return create_samples_management_table(samples_data)
    elif active_tab == 'stats':
        if stats_data is None:
            stats_data = {}
        return create_admin_statistics(stats_data)
    else:
        return html.Div("Tab no trobada")