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

def fetch_samples(backend_url):
    """Fetch all samples from the backend API"""
    try:
        resp = requests.get(f"{backend_url}/api/mostres")
        return resp.json()
    except Exception as e:
        print(f"Error fetching samples: {e}")
        return []

def fetch_sample_by_id(backend_url, sample_id):
    """Fetch a specific sample by ID from the backend API"""
    try:
        resp = requests.get(f"{backend_url}/api/mostres/{sample_id}")
        return resp.json()
    except Exception as e:
        print(f"Error fetching sample {sample_id}: {e}")
        return None

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

def create_samples_table(data, current_page=1, page_size=10, sort_column='data', sort_order='desc'):
    """Create an enhanced samples table with pagination, sorting, and ID column"""
    from dash import html, dcc
    import math
    
    if not data:
        return html.Div("No hi ha mostres disponibles", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'fontStyle': 'italic'})
    
    # Sort data
    try:
        if sort_column == 'id':
            data = sorted(data, key=lambda x: int(x.get('id', 0)), reverse=(sort_order == 'desc'))
        elif sort_column == 'data':
            data = sorted(data, key=lambda x: str(x.get('data', '')), reverse=(sort_order == 'desc'))
        elif sort_column == 'punt_mostreig':
            data = sorted(data, key=lambda x: str(x.get('punt_mostreig', '')), reverse=(sort_order == 'desc'))
    except:
        pass  # Keep original order if sorting fails
    
    # Calculate pagination
    total_items = len(data)
    total_pages = max(1, math.ceil(total_items / page_size))
    # Ensure current_page is within bounds
    current_page = max(1, min(current_page, total_pages))
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_data = data[start_idx:end_idx]
    
    # Create sort indicator function
    def get_sort_indicator(column):
        if sort_column == column:
            return " ↓" if sort_order == 'desc' else " ↑"
        return ""
    
    # Create table header with sortable columns
    header_style = {
        'padding': '1rem', 
        'textAlign': 'left', 
        'backgroundColor': '#f8f9fa', 
        'borderBottom': '2px solid #dee2e6',
        'cursor': 'pointer',
        'userSelect': 'none',
        'transition': 'background-color 0.2s'
    }
    
    table_header = html.Thead([
        html.Tr([
            html.Th([
                "ID" + get_sort_indicator('id')
            ], id='sort-id', style={**header_style, 'width': '80px'}, className='sortable-header'),
            html.Th([
                "Data de mostreig" + get_sort_indicator('data')
            ], id='sort-data', style=header_style, className='sortable-header'),
            html.Th([
                "Punt de mostreig" + get_sort_indicator('punt_mostreig')
            ], id='sort-punt_mostreig', style=header_style, className='sortable-header'),
            html.Th("Detalls", style={**header_style, 'textAlign': 'center', 'cursor': 'default'})
        ])
    ])
    
    # Create table rows
    table_rows = []
    for sample in paginated_data:
        sample_id = sample.get('id', 'N/A')
        date_str = sample.get('data', 'N/A')
        location = sample.get('punt_mostreig', 'N/A')
        
        # Format the date if it's available
        if date_str != 'N/A' and 'T' in str(date_str):
            try:
                date_str = str(date_str).split('T')[0]
            except:
                pass
        
        row = html.Tr([
            html.Td(str(sample_id), style={'padding': '1rem', 'borderBottom': '1px solid #dee2e6', 'fontWeight': '500'}),
            html.Td(date_str, style={'padding': '1rem', 'borderBottom': '1px solid #dee2e6'}),
            html.Td(location, style={'padding': '1rem', 'borderBottom': '1px solid #dee2e6'}),
            html.Td([
                dcc.Link("Veure detalls", href=f"/browse/sample/{sample_id}", 
                        style={'color': '#3498db', 'textDecoration': 'none', 'fontWeight': '500'})
            ], style={'padding': '1rem', 'textAlign': 'center', 'borderBottom': '1px solid #dee2e6'})
        ], style={
            'cursor': 'pointer',
            'transition': 'background-color 0.2s',
        }, className='sample-row')
        
        table_rows.append(row)
    
    table_body = html.Tbody(table_rows)
    
    # Pagination controls
    pagination_controls = []
    if total_pages > 1:
        # Previous button
        if current_page > 1:
            pagination_controls.append(
                html.Button("← Anterior", id="pagination-prev", 
                          className="pagination-btn", 
                          **{'data-page': current_page - 1},
                          style={'marginRight': '0.5rem'})
            )
        
        # Page input for direct navigation
        pagination_controls.append(
            html.Div([
                html.Span("Pàgina "),
                dcc.Input(
                    id='page-input',
                    type='number',
                    value=current_page,
                    min=1,
                    max=total_pages,
                    style={
                        'width': '60px',
                        'textAlign': 'center',
                        'margin': '0 0.5rem',
                        'padding': '0.25rem',
                        'border': '1px solid #dee2e6',
                        'borderRadius': '4px'
                    }
                ),
                html.Span(f" de {total_pages}")
            ], style={'display': 'flex', 'alignItems': 'center', 'margin': '0 1rem'})
        )
        
        # Next button
        if current_page < total_pages:
            pagination_controls.append(
                html.Button("Següent →", id="pagination-next", 
                          className="pagination-btn", 
                          **{'data-page': current_page + 1},
                          style={'marginLeft': '0.5rem'})
            )
    
    # Table info
    info_text = f"Mostrant {start_idx + 1}-{min(end_idx, total_items)} de {total_items} mostres"
    
    return html.Div([
        # Table info and controls
        html.Div([
            html.Div(info_text, style={'color': '#6c757d', 'fontSize': '0.9rem'}),
            html.Div([
                html.Label("Mostres per pàgina: ", style={'marginRight': '0.5rem'}),
                dcc.Dropdown(
                    id='page-size-dropdown',
                    options=[
                        {'label': '5', 'value': 5},
                        {'label': '10', 'value': 10},
                        {'label': '25', 'value': 25},
                        {'label': '50', 'value': 50}
                    ],
                    value=page_size,
                    style={'width': '80px', 'display': 'inline-block'},
                    clearable=False
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '1rem'}),
        
        # Table
        html.Table([table_header, table_body], style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'backgroundColor': 'white',
            'borderRadius': '8px',
            'overflow': 'hidden',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
        }),
        
        # Pagination
        html.Div(pagination_controls, style={
            'display': 'flex', 
            'justifyContent': 'center', 
            'alignItems': 'center',
            'marginTop': '1.5rem',
            'flexWrap': 'wrap'
        }, id='pagination-container')
        
    ], style={'overflowX': 'auto'}, id='samples-table-container')

def create_sample_details(sample_data):
    """Create a detailed view of a single sample"""
    from dash import html
    
    if not sample_data:
        return html.Div("Mostra no trobada", 
                       style={'textAlign': 'center', 'color': '#e74c3c', 'fontSize': '1.2rem'})
    
    # Create sections for different parameter types
    basic_info = [
        html.Tr([html.Td("Data de mostreig", style={'fontWeight': 'bold', 'padding': '0.5rem'}), 
                html.Td(str(sample_data.get('data', 'N/A')), style={'padding': '0.5rem'})]),
        html.Tr([html.Td("Punt de mostreig", style={'fontWeight': 'bold', 'padding': '0.5rem'}), 
                html.Td(str(sample_data.get('punt_mostreig', 'N/A')), style={'padding': '0.5rem'})])
    ]
    
    # Physical and chemical parameters
    physical_params = []
    param_mapping = {
        'temperatura': 'Temperatura (°C)',
        'ph': 'pH',
        'conductivitat_20c': 'Conductivitat a 20°C (μS/cm)',
        'terbolesa': 'Terbolesa (UNF)',
        'color': 'Color (mg/l Pt-Co)',
        'olor': 'Olor (índex dilució a 25°C)',
        'sabor': 'Sabor (índex dilució a 25°C)',
        'clor_lliure': 'Clor lliure (mg Cl₂/l)',
        'clor_total': 'Clor total (mg Cl₂/l)'
    }
    
    for key, label in param_mapping.items():
        value = sample_data.get(key)
        if value is not None:
            physical_params.append(
                html.Tr([
                    html.Td(label, style={'fontWeight': 'bold', 'padding': '0.5rem'}),
                    html.Td(str(value), style={'padding': '0.5rem'})
                ])
            )
    
    return html.Div([
        html.H2("Detalls de la mostra", style={'color': '#2c3e50', 'marginBottom': '2rem'}),
        
        # Basic information
        html.Div([
            html.H3("Informació bàsica", style={'color': '#34495e', 'marginBottom': '1rem'}),
            html.Table(basic_info, style={'width': '100%', 'borderCollapse': 'collapse'})
        ], style={'backgroundColor': 'white', 'padding': '1.5rem', 'borderRadius': '8px', 
                 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'marginBottom': '2rem'}),
        
        # Physical and chemical parameters
        html.Div([
            html.H3("Paràmetres físics i químics", style={'color': '#34495e', 'marginBottom': '1rem'}),
            html.Table(physical_params, style={'width': '100%', 'borderCollapse': 'collapse'}) if physical_params else html.P("Cap paràmetre físic o químic registrat")
        ], style={'backgroundColor': 'white', 'padding': '1.5rem', 'borderRadius': '8px', 
                 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'marginBottom': '2rem'}),
        
        # Back button
        html.Div([
            dcc.Link("← Tornar a la llista", href="/browse", 
                    style={'color': '#3498db', 'textDecoration': 'none', 'fontSize': '1.1rem'})
        ], style={'textAlign': 'center', 'marginTop': '2rem'})
    ])

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