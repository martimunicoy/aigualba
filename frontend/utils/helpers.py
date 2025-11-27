import requests
import os
from dash import html, dcc
from datetime import datetime, timedelta
from collections import Counter
try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def get_backend_url():
    """Get the backend URL from environment variables"""
    return os.getenv("BACKEND_URL", "http://localhost:8000")

def format_date_catalan(date_obj, format_type='short'):
    """Format date in Catalan language"""
    catalan_months = {
        1: 'gener', 2: 'febrer', 3: 'març', 4: 'abril', 5: 'maig', 6: 'juny',
        7: 'juliol', 8: 'agost', 9: 'setembre', 10: 'octubre', 11: 'novembre', 12: 'desembre'
    }
    
    catalan_months_abbr = {
        1: 'gen', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
        7: 'jul', 8: 'ago', 9: 'set', 10: 'oct', 11: 'nov', 12: 'des'
    }
    
    if format_type == 'short':
        # Format: dd/mm/yyyy (numerical format doesn't need translation)
        return date_obj.strftime('%d/%m/%Y')
    elif format_type == 'long':
        # Format: dd de month del yyyy
        day = date_obj.day
        month = catalan_months[date_obj.month]
        year = date_obj.year
        return f"{day} de {month} del {year}"
    elif format_type == 'abbr':
        # Format: abbr yyyy (for charts)
        month_abbr = catalan_months_abbr[date_obj.month]
        year = date_obj.year
        return f"{month_abbr} {year}"
    else:
        return date_obj.strftime('%d/%m/%Y')

def filter_samples_by_criteria(samples, date_from=None, date_to=None, location=None):
    """Filter samples by date range and/or location"""
    if not samples:
        return []
    
    filtered_samples = samples.copy()
    
    # Filter by date range
    if date_from or date_to:
        date_filtered = []
        for sample in filtered_samples:
            sample_date_str = sample.get('data')
            if sample_date_str:
                try:
                    sample_date = datetime.strptime(sample_date_str, '%Y-%m-%d')
                    
                    # Check date_from constraint
                    if date_from:
                        filter_date_from = datetime.strptime(date_from, '%Y-%m-%d')
                        if sample_date < filter_date_from:
                            continue
                    
                    # Check date_to constraint
                    if date_to:
                        filter_date_to = datetime.strptime(date_to, '%Y-%m-%d')
                        if sample_date > filter_date_to:
                            continue
                    
                    date_filtered.append(sample)
                except ValueError:
                    # Keep samples with invalid dates
                    date_filtered.append(sample)
            else:
                # Keep samples without dates
                date_filtered.append(sample)
        
        filtered_samples = date_filtered
    
    # Filter by location
    if location and location != 'all':
        location_filtered = []
        for sample in filtered_samples:
            sample_location = sample.get('punt_mostreig', '')
            if sample_location == location:
                location_filtered.append(sample)
        filtered_samples = location_filtered
    
    return filtered_samples

def get_unique_locations(samples):
    """Get unique sampling locations from samples"""
    if not samples:
        return []
    
    locations = set()
    for sample in samples:
        location = sample.get('punt_mostreig')
        if location:
            locations.add(location)
    
    return sorted(list(locations))

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
    warnings = []
    
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
    
    # Check for potentially unusual values (warnings)
    if sample_data.get('temperatura'):
        try:
            temp = float(sample_data['temperatura'])
            if temp < 0 or temp > 40:
                warnings.append(f"Temperatura inusual: {temp}°C")
        except ValueError:
            pass  # Already handled as error above
    
    if sample_data.get('ph'):
        try:
            ph_val = float(sample_data['ph'])
            if ph_val < 6.0 or ph_val > 9.0:
                warnings.append(f"Valor de pH fora del rang normal: {ph_val}")
        except ValueError:
            pass  # Already handled as error above
    
    return {'errors': errors, 'warnings': warnings}

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
                formatted_date = format_date_catalan(date_obj, 'short')
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
    
    # Previous button - always render but disable if on first page
    pagination_controls.append(
        html.Button("← Anterior", id='pagination-prev', 
                   disabled=current_page <= 1,
                   style={
                       'margin': '0 0.5rem', 
                       'padding': '0.5rem 1rem', 
                       'backgroundColor': '#6c757d' if current_page <= 1 else '#007bff', 
                       'color': 'white', 
                       'border': 'none', 
                       'borderRadius': '4px',
                       'cursor': 'not-allowed' if current_page <= 1 else 'pointer'
                   })
    )
    
    # Page info
    pagination_controls.append(
        html.Span(f"Pàgina {current_page} de {total_pages} ({total_samples} mostres)",
                 style={'margin': '0 1rem', 'fontSize': '0.9rem', 'color': '#6c757d'})
    )
    
    # Page input for direct navigation
    pagination_controls.append(
        html.Div([
            html.Label("Anar a la pàgina:", style={'fontSize': '0.9rem', 'marginRight': '0.5rem', 'color': '#6c757d'}),
            dcc.Input(
                id='page-input',
                type='number',
                min=1,
                max=total_pages,
                value=current_page,
                style={
                    'width': '60px',
                    'padding': '0.25rem',
                    'border': '1px solid #ced4da',
                    'borderRadius': '4px',
                    'textAlign': 'center'
                }
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'margin': '0 1rem'})
    )
    
    # Next button - always render but disable if on last page
    pagination_controls.append(
        html.Button("Següent →", id='pagination-next',
                   disabled=current_page >= total_pages,
                   style={
                       'margin': '0 0.5rem', 
                       'padding': '0.5rem 1rem',
                       'backgroundColor': '#6c757d' if current_page >= total_pages else '#007bff', 
                       'color': 'white', 
                       'border': 'none', 
                       'borderRadius': '4px',
                       'cursor': 'not-allowed' if current_page >= total_pages else 'pointer'
                   })
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
            formatted_date = format_date_catalan(date_obj, 'long')
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
                    html.Td(label, style={'fontWeight': 'bold', 'padding': '0.5rem', 'borderBottom': '1px solid #dee2e6', 'textAlign': 'left'}),
                    html.Td(display_value, style={'padding': '0.5rem', 'borderBottom': '1px solid #dee2e6', 'textAlign': 'right'})
                ])
            )
        
        return html.Div([
            html.H3(title, style={'color': '#495057', 'borderBottom': '2px solid #007bff', 'paddingBottom': '0.5rem'}),
            html.Table(param_items, style={'width': '100%', 'marginBottom': '2rem'})
        ])
    
    return html.Div([
        html.Div([
            html.Div([
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
            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            })
        ], style={
            'maxWidth': '1200px', 
            'margin': '0 auto', 
            'padding': '2rem'
        })
    ], style={'backgroundColor': '#f8f9fa', 'minHeight': '80vh'})

def create_samples_by_location_chart(samples):
    """Create a bar chart showing samples count by location"""
    if not HAS_PLOTLY or not samples:
        return html.Div([
            html.P("Gràfic no disponible", style={'textAlign': 'center', 'color': '#6c757d'})
        ])
    
    # Count samples by location
    location_counts = Counter()
    for sample in samples:
        location = sample.get('punt_mostreig', 'Ubicació desconeguda')
        location_counts[location] += 1
    
    # Sort alphabetically by location name
    sorted_locations = sorted(location_counts.items())
    locations = [item[0] for item in sorted_locations]
    counts = [item[1] for item in sorted_locations]
    
    if not locations:
        return html.Div([
            html.P("No hi ha dades per mostrar", style={'textAlign': 'center', 'color': '#6c757d'})
        ])
    
    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=locations,
        y=counts,
        name='Mostres per ubicació',
        marker_color="#f59f1f"
    ))
    
    fig.update_layout(
        title={
            'text': 'Distribució de mostres per ubicació',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2c3e50'}
        },
        xaxis_title={'text': 'Punt de mostreig', 'font': {'weight': 'bold'}},
        yaxis_title={'text': 'Nombre de mostres', 'font': {'weight': 'bold'}},
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin={'l': 40, 'r': 40, 't': 60, 'b': 120},
        height=400,
        font={'color': '#495057'},
        xaxis={
            'showline': True,
            'linecolor': '#dee2e6',
            'linewidth': 1
        },
        yaxis={
            'dtick': 1,
            'rangemode': 'tozero',
            'showline': True,
            'linecolor': '#dee2e6',
            'linewidth': 1
        }
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False}
    )

def create_samples_by_month_chart(samples):
    """Create a bar chart showing samples count by month for the last 12 months"""
    if not HAS_PLOTLY or not samples:
        return html.Div([
            html.P("Gràfic no disponible", style={'textAlign': 'center', 'color': '#6c757d'})
        ])
    
    # Calculate date range (last 12 months from start of month)
    today = datetime.now()
    twelve_months_ago = today.replace(day=1) - timedelta(days=365)
    
    # Debug: Print sample dates and date range
    print(f"Date range: {twelve_months_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")
    for sample in samples[:3]:  # Print first 3 samples for debugging
        print(f"Sample date: {sample.get('data')}")
    
    # Count samples by month
    monthly_counts = {}
    
    # Initialize all months in the last 12 months with 0
    current_date = twelve_months_ago
    while current_date <= today:
        month_key = current_date.strftime('%Y-%m')
        monthly_counts[month_key] = 0
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Count actual samples (include all samples, not just last 12 months for debugging)
    for sample in samples:
        sample_date_str = sample.get('data')
        if sample_date_str:
            try:
                sample_date = datetime.strptime(sample_date_str, '%Y-%m-%d')
                month_key = sample_date.strftime('%Y-%m')
                # Always count the sample, create month if it doesn't exist
                if month_key not in monthly_counts:
                    monthly_counts[month_key] = 0
                monthly_counts[month_key] += 1
                print(f"Counted sample: {sample_date_str} -> {month_key}")
            except ValueError as e:
                print(f"Error parsing date {sample_date_str}: {e}")
                continue
    
    # Prepare data for plotting - show only months with samples or last 12 months
    if any(count > 0 for count in monthly_counts.values()):
        # Show all months that have samples plus the standard 12-month range
        all_months = sorted(monthly_counts.keys())
    else:
        all_months = sorted(monthly_counts.keys())
    
    months = all_months
    counts = [monthly_counts[month] for month in months]
    
    # Format month labels in Catalan
    month_labels = []
    for month in months:
        try:
            date_obj = datetime.strptime(month, '%Y-%m')
            month_labels.append(format_date_catalan(date_obj, 'abbr'))
        except ValueError:
            month_labels.append(month)
    
    print(f"Final months to display: {months}")
    print(f"Final counts: {counts}")
    
    if not months:
        return html.Div([
            html.P("No hi ha dades per mostrar", style={'textAlign': 'center', 'color': '#6c757d'})
        ])
    
    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=month_labels,
        y=counts,
        name='Mostres per mes',
        marker_color='#28a745'
    ))
    
    fig.update_layout(
        title={
            'text': 'Evolució de mostres durant els últims 12 mesos',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2c3e50'}
        },
        xaxis_title={'text': 'Mes', 'font': {'weight': 'bold'}},
        yaxis_title={'text': 'Nombre de mostres', 'font': {'weight': 'bold'}},
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin={'l': 40, 'r': 40, 't': 60, 'b': 60},
        height=400,
        font={'color': '#495057'},
        xaxis={
            'tickangle': -45,
            'showline': True,
            'linecolor': '#dee2e6',
            'linewidth': 1
        },
        yaxis={
            'dtick': 1,
            'rangemode': 'tozero',
            'showline': True,
            'linecolor': '#dee2e6',
            'linewidth': 1
        }
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False}
    )

def create_data_visualizations(samples):
    """Create a section with data visualization charts"""
    return html.Div([
        # Charts container
        html.Div([
            # Samples by location chart
            html.Div([
                html.H3("Anàlisi visual de les dades", 
                    style={'color': '#2c3e50', 'marginBottom': '2rem', 'textAlign': 'center'}),
                create_samples_by_location_chart(samples),
                create_samples_by_month_chart(samples)
            ], style={
                'backgroundColor': 'white',
                'padding': '1.5rem',
                'borderRadius': '10px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                'marginBottom': '2rem'
            })            
        ])
    ], style={'marginBottom': '2rem'})