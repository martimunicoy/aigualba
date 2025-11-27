import requests
import os
from dash import html, dcc
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
        print(f"Fetching samples from: {backend_url}/api/mostres")
        resp = requests.get(f"{backend_url}/api/mostres", timeout=10)
        print(f"Response status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Retrieved {len(data)} samples")
            return data
        else:
            print(f"Error response: {resp.status_code} - {resp.text}")
            return []
    except Exception as e:
        print(f"Error fetching samples: {e}")
        import traceback
        traceback.print_exc()
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
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return {"success": True, "data": response.json()}
    except Exception as e:
        print(f"Error submitting data: {e}")
        return {"success": False, "error": str(e)}

def validate_sample_data(sample_data):
    """Validate sample data before submission"""
    errors = []
    
    # Check required fields
    required_fields = ['data', 'punt_mostreig']
    for field in required_fields:
        if not sample_data.get(field):
            errors.append(f"El camp {field.replace('_', ' ')} és obligatori")
    
    # Check numeric fields (if provided)
    numeric_fields = ['temperatura', 'clor_lliure', 'clor_total', 'ph', 'terbolesa']
    for field in numeric_fields:
        value = sample_data.get(field)
        if value is not None and value != '':
            try:
                float(value)
            except ValueError:
                errors.append(f"El camp {field.replace('_', ' ')} ha de ser un número")
    
    return errors

def create_parameter_card(parameter):
    """Create a parameter card component"""
    return html.Div([
        html.H3(parameter.get('nom', 'Parameter'), className='parameter-title'),
        html.P(parameter.get('descripcio', 'No description'), className='parameter-description'),
        html.Div([
            html.Span(f"Unitat: {parameter.get('unitat', 'N/A')}", className='parameter-unit'),
            html.Span(f"Valor límit: {parameter.get('valor_limit', 'N/A')}", className='parameter-limit')
        ], className='parameter-info')
    ], className='parameter-card')

def create_data_table(data):
    """Create a data table component"""
    if not data:
        return html.Div("No data available", className='no-data')
    
    # Create table header
    header = html.Tr([html.Th(key) for key in data[0].keys()])
    
    # Create table rows
    rows = []
    for item in data:
        row = html.Tr([html.Td(str(value)) for value in item.values()])
        rows.append(row)
    
    return html.Table([
        html.Thead(header),
        html.Tbody(rows)
    ], className='data-table')

def create_samples_table(samples, current_page=1, page_size=10, sort_column='data', sort_order='desc'):
    """Create a paginated and sortable samples table"""
    print(f"create_samples_table called with: sort_column={sort_column}, sort_order={sort_order}, page={current_page}, size={page_size}")
    
    # Handle None values
    if sort_column is None:
        sort_column = 'data'
    if sort_order is None:
        sort_order = 'desc'
    if current_page is None:
        current_page = 1
    if page_size is None:
        page_size = 10
        
    if not samples:
        return html.Div([
            html.P("No s'han trobat mostres.", 
                  style={'textAlign': 'center', 'color': '#6c757d', 'fontSize': '1.1rem', 'padding': '3rem'})
        ])
    
    # Sort samples
    reverse_order = sort_order == 'desc'
    try:
        if sort_column == 'data':
            sorted_samples = sorted(samples, key=lambda x: x.get('data', ''), reverse=reverse_order)
        elif sort_column == 'id':
            sorted_samples = sorted(samples, key=lambda x: x.get('id', 0), reverse=reverse_order)
        elif sort_column == 'punt_mostreig':
            sorted_samples = sorted(samples, key=lambda x: x.get('punt_mostreig', ''), reverse=reverse_order)
        else:
            sorted_samples = samples
    except Exception as e:
        print(f"Error sorting samples: {e}")
        sorted_samples = samples
    
    # Calculate pagination
    total_samples = len(sorted_samples)
    total_pages = max(1, (total_samples + page_size - 1) // page_size)
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    page_samples = sorted_samples[start_idx:end_idx]
    
    # Create table header with sorting controls
    def create_sort_header(column, label):
        current_sort_icon = ""
        if sort_column == column:
            current_sort_icon = " ↑" if sort_order == 'asc' else " ↓"
        
        return html.Th([
            html.Button(
                f"{label}{current_sort_icon}",
                id=f'sort-{column}',
                style={
                    'background': 'none',
                    'border': 'none',
                    'cursor': 'pointer',
                    'color': '#007bff',
                    'fontWeight': 'bold',
                    'fontSize': '0.95rem',
                    'padding': '0.75rem',
                    'width': '100%',
                    'textAlign': 'center'
                }
            )
        ], style={'textAlign': 'center', 'padding': '0.75rem', 'border': '1px solid #dee2e6', 'backgroundColor': '#f8f9fa'})
    
    table_header = html.Thead([
        html.Tr([
            create_sort_header('id', 'ID'),
            create_sort_header('data', 'Data'),
            create_sort_header('punt_mostreig', 'Punt de Mostreig'),
            html.Th("Accions", style={
                'textAlign': 'center', 
                'fontWeight': 'bold',
                'padding': '0.75rem',
                'border': '1px solid #dee2e6',
                'backgroundColor': '#f8f9fa',
                'color': '#495057'
            })
        ], style={'backgroundColor': '#f8f9fa'})
    ], style={'backgroundColor': '#f8f9fa'})
    
    # Create table rows
    table_rows = []
    for sample in page_samples:
        # Format date if available
        date_str = sample.get('data', 'N/A')
        if date_str and date_str != 'N/A':
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d/%m/%Y')
            except ValueError:
                formatted_date = date_str
        else:
            formatted_date = 'N/A'
        
        # Create detail link
        sample_id = sample.get('id')
        if sample_id:
            detail_link = dcc.Link(
                "Veure Detalls",
                href=f"/browse/sample/{sample_id}",
                style={
                    'color': '#007bff',
                    'textDecoration': 'none',
                    'padding': '0.5rem 1rem',
                    'backgroundColor': '#f8f9fa',
                    'border': '1px solid #007bff',
                    'borderRadius': '4px',
                    'display': 'inline-block',
                    'fontSize': '0.9rem'
                }
            )
        else:
            detail_link = html.Span("N/A", style={'color': '#6c757d'})
        
        # Create table row with improved styling
        cell_style = {
            'textAlign': 'center',
            'padding': '0.75rem',
            'border': '1px solid #dee2e6',
            'backgroundColor': '#ffffff'
        }
        
        row = html.Tr([
            html.Td(str(sample.get('id', 'N/A')), style=cell_style),
            html.Td(formatted_date, style=cell_style),
            html.Td(sample.get('punt_mostreig', 'N/A'), style=cell_style),
            html.Td(detail_link, style=cell_style)
        ], style={'backgroundColor': '#ffffff', 'transition': 'background-color 0.2s'})
        table_rows.append(row)
    
    table_body = html.Tbody(table_rows)
    
    # Create pagination controls
    pagination_controls = []
    
    # Previous button
    if current_page > 1:
        pagination_controls.append(
            html.Button("← Anterior", id='prev-page', 
                       style={'margin': '0 0.5rem', 'padding': '0.5rem 1rem', 
                             'backgroundColor': '#007bff', 'color': 'white', 'border': 'none', 'borderRadius': '4px'})
        )
    
    # Page info
    pagination_controls.append(
        html.Span(f"Pàgina {current_page} de {total_pages} ({total_samples} mostres)",
                 style={'margin': '0 1rem', 'fontSize': '0.9rem', 'color': '#6c757d'})
    )
    
    # Next button
    if current_page < total_pages:
        pagination_controls.append(
            html.Button("Següent →", id='next-page',
                       style={'margin': '0 0.5rem', 'padding': '0.5rem 1rem',
                             'backgroundColor': '#007bff', 'color': 'white', 'border': 'none', 'borderRadius': '4px'})
        )
    
    # Page size selector
    page_size_controls = [
        html.Label("Mostres per pàgina: ", style={'margin': '0 0.5rem', 'fontSize': '0.9rem'}),
        dcc.Dropdown(
            id='page-size-dropdown',
            options=[
                {'label': '5', 'value': 5},
                {'label': '10', 'value': 10},
                {'label': '20', 'value': 20},
                {'label': '50', 'value': 50}
            ],
            value=page_size,
            style={'width': '80px', 'display': 'inline-block'}
        )
    ]
    
    return html.Div([
        # Table container with improved styling
        html.Div([
            html.Table([table_header, table_body], className='samples-table',
                      style={
                          'width': '100%', 
                          'borderCollapse': 'collapse', 
                          'backgroundColor': '#ffffff',
                          'border': '1px solid #dee2e6',
                          'borderRadius': '8px',
                          'overflow': 'hidden',
                          'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                      })
        ], style={
            'marginBottom': '2rem',
            'borderRadius': '8px',
            'overflow': 'hidden'
        }),
        
        # Controls
        html.Div([
            html.Div(pagination_controls, style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
            html.Div(page_size_controls, style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginTop': '1rem'})
        ])
    ])

def create_sample_details(sample):
    """Create a detailed view of a sample"""
    if not sample:
        return html.Div([
            html.H2("Error", style={'color': '#e74c3c'}),
            html.P("No s'han pogut carregar els detalls de la mostra.")
        ])
    
    # Format date
    date_str = sample.get('data', 'N/A')
    if date_str and date_str != 'N/A':
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d de %B del %Y')
        except ValueError:
            formatted_date = date_str
    else:
        formatted_date = 'N/A'
    
    # Organize parameters into sections
    basic_info = [
        ('ID de la Mostra', sample.get('id', 'N/A')),
        ('Data de Recollida', formatted_date),
        ('Punt de Mostreig', sample.get('punt_mostreig', 'N/A')),
    ]
    
    physical_params = [
        ('Temperatura (°C)', sample.get('temperatura')),
        ('pH', sample.get('ph')),
        ('Conductivitat a 20°C (μS/cm)', sample.get('conductivitat_20c')),
        ('Terbolesa (NTU)', sample.get('terbolesa')),
        ('Color', sample.get('color')),
        ('Olor', sample.get('olor')),
        ('Sabor', sample.get('sabor')),
    ]
    
    chemical_params = [
        ('Clor Lliure (mg/L)', sample.get('clor_lliure')),
        ('Clor Total (mg/L)', sample.get('clor_total')),
        ('Àcid Monocloroacètic (μg/L)', sample.get('acid_monocloroacetic')),
        ('Àcid Dicloroacètic (μg/L)', sample.get('acid_dicloroacetic')),
        ('Àcid Tricloroacètic (μg/L)', sample.get('acid_tricloroacetic')),
        ('Àcid Monobromoacètic (μg/L)', sample.get('acid_monobromoacetic')),
        ('Àcid Dibromoacètic (μg/L)', sample.get('acid_dibromoacetic')),
    ]
    
    biological_params = [
        ('Escherichia coli (UFC/100mL)', sample.get('recompte_escherichia_coli')),
        ('Enterococs (UFC/100mL)', sample.get('recompte_enterococ')),
        ('Microorganismes aerobis 22°C (UFC/mL)', sample.get('recompte_microorganismes_aerobis_22c')),
        ('Coliformes totals (UFC/100mL)', sample.get('recompte_coliformes_totals')),
    ]
    
    def create_param_section(title, params):
        param_items = []
        for label, value in params:
            if value is not None and value != '':
                display_value = str(value)
            else:
                display_value = 'No mesurat'
            
            param_items.append(
                html.Tr([
                    html.Td(label, style={'fontWeight': 'bold', 'padding': '0.5rem', 'borderBottom': '1px solid #dee2e6'}),
                    html.Td(display_value, style={'padding': '0.5rem', 'borderBottom': '1px solid #dee2e6'})
                ])
            )
        
        return html.Div([
            html.H3(title, style={'color': '#495057', 'borderBottom': '2px solid #007bff', 'paddingBottom': '0.5rem'}),
            html.Table(param_items, style={'width': '100%', 'marginBottom': '2rem'})
        ])
    
    return html.Div([
        # Header
        html.Div([
            html.H1(f"Detalls de la Mostra #{sample.get('id', 'N/A')}", 
                   style={'color': '#2c3e50', 'marginBottom': '0.5rem'}),
            html.P(f"Recollida el {formatted_date} a {sample.get('punt_mostreig', 'ubicació desconeguda')}", 
                  style={'color': '#6c757d', 'fontSize': '1.1rem', 'marginBottom': '2rem'})
        ], style={'textAlign': 'center', 'marginBottom': '3rem'}),
        
        # Parameter sections
        create_param_section("Informació Bàsica", basic_info),
        create_param_section("Paràmetres Físics", physical_params),
        create_param_section("Paràmetres Químics", chemical_params),
        create_param_section("Paràmetres Biològics", biological_params),
        
        # Back link
        html.Div([
            dcc.Link("← Tornar a la llista", href="/browse", 
                    style={'color': '#007bff', 'textDecoration': 'none', 'fontSize': '1.1rem'})
        ], style={'textAlign': 'center', 'marginTop': '3rem'})
    ])