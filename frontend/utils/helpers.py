import requests
import os
from dash import html

def get_backend_url():
    """Get the backend URL from environment variables"""
    return os.getenv("BACKEND_URL", "http://localhost:8000")

def fetch_parameters(backend_url):
    """Fetch water quality parameters from the backend API"""
    try:
        resp = requests.get(f"{backend_url}/api/parameters")
        return resp.json()
    except Exception as e:
        print(f"Error fetching parameters: {e}")
        return []

def create_parameter_card(param):
    """Create a parameter card component"""
    return html.Div([
        html.H3(param['name'], style={'color': '#2c3e50', 'marginBottom': '1rem'}),
        html.Div(param['value'], style={
            'fontSize': '2rem', 
            'fontWeight': 'bold', 
            'color': '#3498db',
            'marginBottom': '0.5rem'
        }),
        html.P(f"Actualitzat: {param['updated_at'][:19].replace('T', ' ')}", 
               style={'fontSize': '0.9rem', 'color': '#7f8c8d', 'margin': '0'})
    ], style={
        'backgroundColor': '#f8f9fa', 
        'padding': '2rem', 
        'borderRadius': '10px', 
        'textAlign': 'center', 
        'minWidth': '200px', 
        'boxShadow': '0 2px 10px rgba(0,0,0,0.05)',
        'border': '1px solid #ecf0f1',
        'transition': 'transform 0.2s, box-shadow 0.2s'
    })

def create_data_table(data):
    """Create a data table from parameters data"""
    if not data:
        return html.Div("No hi ha dades disponibles", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'fontStyle': 'italic'})
    
    return html.Table([
        html.Thead([
            html.Tr([
                html.Th("Paràmetre", style={'backgroundColor': '#f8f9fa', 'padding': '1rem', 'borderBottom': '2px solid #ecf0f1'}), 
                html.Th("Valor", style={'backgroundColor': '#f8f9fa', 'padding': '1rem', 'borderBottom': '2px solid #ecf0f1'}), 
                html.Th("Última actualització", style={'backgroundColor': '#f8f9fa', 'padding': '1rem', 'borderBottom': '2px solid #ecf0f1'})
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(p['name'], style={'padding': '1rem', 'borderBottom': '1px solid #ecf0f1', 'fontWeight': '500'}), 
                html.Td(p['value'], style={'padding': '1rem', 'borderBottom': '1px solid #ecf0f1', 'color': '#3498db', 'fontWeight': 'bold'}), 
                html.Td(p['updated_at'][:19].replace('T', ' '), style={'padding': '1rem', 'borderBottom': '1px solid #ecf0f1', 'color': '#7f8c8d'})
            ]) for p in data
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'borderRadius': '8px', 'overflow': 'hidden'})