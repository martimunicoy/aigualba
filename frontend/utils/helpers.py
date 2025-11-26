import requests
import os
from dash import html
from datetime import datetime

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

def submit_sample_data(backend_url, sample_data):
    """Submit sample data to the backend API"""
    try:
        response = requests.post(f"{backend_url}/api/mostres", json=sample_data)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

def validate_sample_data(data):
    """Validate sample data and return validation messages"""
    errors = []
    warnings = []
    
    # Required fields validation
    if not data.get('data'):
        errors.append("La data és obligatòria")
    
    if not data.get('punt_mostreig') or data.get('punt_mostreig').strip() == '':
        errors.append("El punt de mostreig és obligatori")
    
    # Chlorine validation
    clor_lliure = data.get('clor_lliure')
    clor_total = data.get('clor_total')
    
    if clor_lliure is not None and clor_total is not None:
        if clor_lliure > clor_total:
            errors.append("El clor lliure no pot ser superior al clor total")
        if clor_total > 0 and clor_lliure >= 0:
            clor_combinat = clor_total - clor_lliure
            if clor_combinat < 0:
                warnings.append("Els valors de clor semblen inconsistents")
    
    # pH validation
    ph = data.get('ph')
    if ph is not None:
        if ph < 6.5 or ph > 9.5:
            warnings.append("El pH està fora del rang recomanat per aigua potable (6.5-9.5)")
    
    # Microbiological parameters warnings
    e_coli = data.get('recompte_escherichia_coli')
    if e_coli is not None and e_coli > 0:
        warnings.append("La presència d'E. coli indica possible contaminació fecal")
    
    enterococ = data.get('recompte_enterococ')
    if enterococ is not None and enterococ > 0:
        warnings.append("La presència d'Enterococ indica possible contaminació")
    
    coliformes = data.get('recompte_coliformes_totals')
    if coliformes is not None and coliformes > 0:
        warnings.append("La presència de coliformes totals pot indicar contaminació")
    
    # Temperature validation
    temperatura = data.get('temperatura')
    if temperatura is not None:
        if temperatura < 5 or temperatura > 35:
            warnings.append(f"La temperatura ({temperatura}°C) està fora del rang típic per aigua de consum")
    
    return {"errors": errors, "warnings": warnings}

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