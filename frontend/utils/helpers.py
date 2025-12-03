import requests
import os
from dash import html, dcc
from datetime import datetime, timedelta
from collections import Counter
from .thresholds import get_threshold, get_percentage_of_range, is_within_safe_range
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

def fetch_pending_samples_count(backend_url):
    """Fetch count of samples pending validation"""
    try:
        resp = requests.get(f"{backend_url}/api/mostres/pending-count", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('pending_count', 0)
        else:
            print(f"Error getting pending count: {resp.status_code} - {resp.text}")
            return 0
    except Exception as e:
        print(f"Error fetching pending count: {e}")
        return 0

def fetch_sample_by_id(backend_url, sample_id):
    """Fetch a specific sample by ID from the backend API"""
    try:
        resp = requests.get(f"{backend_url}/api/mostres/{sample_id}")
        return resp.json()
    except Exception as e:
        print(f"Error fetching sample {sample_id}: {e}")
        return None

def fetch_latest_gualba_sample(backend_url):
    """Fetch the latest sample from Gualba - kept for backwards compatibility"""
    return fetch_latest_sample_by_location(backend_url, "Gualba")

def fetch_latest_sample_by_location(backend_url, location):
    """Fetch the latest sample from a specific location"""
    try:
        samples = fetch_samples(backend_url)
        if not samples:
            return None
        
        # Filter samples by location
        if location:
            location_samples = [s for s in samples if s.get('punt_mostreig', '').lower() == location.lower()]
        else:
            location_samples = samples
        
        if not location_samples:
            return None
            
        # Sort by date descending to get the most recent
        sorted_samples = sorted(location_samples,
                                key=lambda x: x.get('data', ''), 
                                reverse=True)
        return sorted_samples[0] if sorted_samples else None
    except Exception as e:
        print(f"Error fetching latest sample for {location}: {e}")
        return None

def fetch_latest_sample_any_location(backend_url):
    """Fetch the latest sample from any location"""
    try:
        samples = fetch_samples(backend_url)
        if not samples:
            return None
            
        # Sort all samples by date descending to get the most recent
        sorted_samples = sorted(samples,
                                key=lambda x: x.get('data', ''), 
                                reverse=True)
        
        # If there is a tie on date, get the one with more parameters reported
        selected_sample = sorted_samples[0]
        selected_sample_non_null_parameters = sum(1 for v in selected_sample.values() if v not in [None, ''])
        for sample in sorted_samples[1:]:
            if sample == selected_sample:
                continue
            
            if sample.get('data') == selected_sample.get('data'):

                count_next = sum(1 for v in sample.values() if v not in [None, ''])
                if count_next > selected_sample_non_null_parameters:
                    selected_sample = sample
                    selected_sample_non_null_parameters = count_next

        return selected_sample if sorted_samples else None
    except Exception as e:
        print(f"Error fetching latest sample from any location: {e}")
        return None

def calculate_suma_haloacetics(sample):
    """Calculate the sum of the five haloacetic acids"""
    acids = [
        'acid_monocloroacetic',
        'acid_dicloroacetic', 
        'acid_tricloroacetic',
        'acid_monobromoacetic',
        'acid_dibromoacetic'
    ]
    
    total = 0
    has_values = False
    
    for acid in acids:
        value = sample.get(acid)
        if value is not None and value != '':
            try:
                total += float(value)
                has_values = True
            except (ValueError, TypeError):
                continue
    
    return total if has_values else None

def calculate_clor_combinat_residual(sample):
    """Calculate residual combined chlorine (clor total - clor lliure)"""
    clor_total = sample.get('clor_total')
    clor_lliure = sample.get('clor_lliure')
    
    if (clor_total is not None and clor_total != '' and 
        clor_lliure is not None and clor_lliure != ''):
        try:
            total = float(clor_total)
            lliure = float(clor_lliure)
            return total - lliure
        except (ValueError, TypeError):
            return None
    
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
    
    # Check if date and location are provided but no parameters are set
    if sample_data.get('data') and sample_data.get('punt_mostreig'):
        # List of all parameter fields (excluding required basic info)
        parameter_fields = [
            'temperatura', 'ph', 'conductivitat_20c', 'terbolesa', 'color', 'olor', 'sabor',
            'clor_lliure', 'clor_total', 'recompte_escherichia_coli', 'recompte_enterococ',
            'recompte_microorganismes_aerobis_22c', 'recompte_coliformes_totals',
            'acid_monocloroacetic', 'acid_dicloroacetic', 'acid_tricloroacetic',
            'acid_monobromoacetic', 'acid_dibromoacetic'
        ]
        
        # Check if at least one parameter has a value
        has_parameters = False
        for field in parameter_fields:
            value = sample_data.get(field)
            if value is not None and value != '' and str(value).strip() != '':
                has_parameters = True
                break
        
        if not has_parameters:
            errors.append("Has d'introduir almenys un paràmetre per enviar la mostra.")
    
    # Check numeric fields (if provided)
    numeric_fields = ['temperatura', 'clor_lliure', 'clor_total', 'ph', 'terbolesa']
    for field in numeric_fields:
        value = sample_data.get(field)
        if value is not None and value != '':
            try:
                float(value)
            except ValueError:
                errors.append(f"El camp {field.replace('_', ' ')} ha de ser un número")
    
    # Check for potentially unusual values (warnings) using defined thresholds
    from utils.thresholds import get_threshold, WATER_QUALITY_THRESHOLDS
    
    # Check all parameters that have defined thresholds
    for field, value in sample_data.items():
        if value is not None and value != '' and field not in ['data', 'punt_mostreig']:
            try:
                float_val = float(value)
                threshold = get_threshold(field)
                if threshold:
                    min_val = float(threshold['min'])
                    max_val = float(threshold['max'])
                    if float_val < min_val or float_val > max_val:
                        warnings.append(f"{threshold['name']} fora del rang recomanat: {float_val} {threshold['unit']} (rang: {min_val}-{max_val} {threshold['unit']})")
            except ValueError:
                pass  # Already handled as error above
    
    # Check suma_haloacetics if individual haloacetic values are provided
    haloacetic_fields = ['acid_monocloroacetic', 'acid_dicloroacetic', 'acid_tricloroacetic', 
                        'acid_monobromoacetic', 'acid_dibromoacetic']
    haloacetic_values = []
    
    for field in haloacetic_fields:
        value = sample_data.get(field)
        if value is not None and value != '':
            try:
                haloacetic_values.append(float(value))
            except ValueError:
                pass
    
    if haloacetic_values:
        total_haloacetics = sum(haloacetic_values)
        # Use the threshold defined in thresholds.py
        suma_threshold = get_threshold('suma_haloacetics')
        if suma_threshold:
            max_val = float(suma_threshold['max'])
            if total_haloacetics > max_val:
                warnings.append(f"{suma_threshold['name']} elevada: {total_haloacetics:.1f} {suma_threshold['unit']} (límit: {max_val} {suma_threshold['unit']})")
            elif total_haloacetics > max_val * 0.67:  # Warning at 67% of limit
                warnings.append(f"{suma_threshold['name']} moderada: {total_haloacetics:.1f} {suma_threshold['unit']} (límit: {max_val} {suma_threshold['unit']})")
    
    # Additional warnings for parameters not in thresholds.py
    # Temperature (not in thresholds as it's environmental, not regulated)
    if sample_data.get('temperatura'):
        try:
            temp = float(sample_data['temperatura'])
            if temp < 0 or temp > 40:
                warnings.append(f"Temperatura inusual: {temp}°C (rang típic per aigua: 5-25°C)")
        except ValueError:
            pass
    
    # Microbiological parameters (should be zero for safe drinking water)
    micro_params = {
        'recompte_escherichia_coli': ('E. coli', 'NPM/100mL'),
        'recompte_enterococ': ('Enterococ', 'NPM/100mL'), 
        'recompte_coliformes_totals': ('Coliformes totals', 'NMP/100mL'),
        'recompte_microorganismes_aerobis_22c': ('Microorganismes aerobis', 'UFC/mL')
    }
    
    for field, (display_name, unit) in micro_params.items():
        value = sample_data.get(field)
        if value is not None and value != '':
            try:
                float_val = float(value)
                if field == 'recompte_microorganismes_aerobis_22c' and float_val > 100:
                    warnings.append(f"{display_name} elevat: {float_val} {unit} (recomanat: <100 {unit})")
                elif field != 'recompte_microorganismes_aerobis_22c' and float_val > 0:
                    warnings.append(f"{display_name} detectat: {float_val} {unit} (ideal: 0 {unit} per aigua potable)")
            except ValueError:
                pass
    
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

def create_latest_sample_summary(sample, location_name=None):
    """Create a summary card for the latest sample"""
    # Determine location display text
    if location_name and location_name != 'any_location':
        location_text = f" de {location_name}"
    else:
        location_text = " de Gualba"
    
    if not sample:
        return html.Div([
            html.H3(f"Darrera mostra{location_text}", style={'color': '#2c3e50', 'marginBottom': '1rem'}),
            html.P(f"No s'han trobat mostres recents{location_text}", 
                  style={'color': '#6c757d', 'fontStyle': 'italic'})
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '2rem',
            'borderRadius': '10px',
            'border': '1px solid #dee2e6',
            'textAlign': 'center'
        })
    
    # Format date
    date_str = sample.get('data', 'No mesurat')
    if date_str and date_str != 'No mesurat':
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = format_date_catalan(date_obj, 'long')
        except ValueError:
            formatted_date = date_str
    else:
        formatted_date = 'No mesurat'
    
    """
    # Key parameters to display - organized by category
    basic_params = [
        ('Data de recollida', formatted_date),
        ('Punt de mostreig', sample.get('punt_mostreig', 'No mesurat'))
    ]
    
    physical_chemical_params = [
        ('Temperatura', f"{sample.get('temperatura')} °C" if sample.get('temperatura') else 'No mesurat'),
        ('pH', sample.get('ph') if sample.get('ph') else 'No mesurat'),
        ('Conductivitat (20°C)', f"{sample.get('conductivitat_20c')} μS/cm" if sample.get('conductivitat_20c') else 'No mesurat'),
        ('Terbolesa', f"{sample.get('terbolesa')} UNF" if sample.get('terbolesa') else 'No mesurat'),
        ('Color', f"{sample.get('color')} mg/L Pt-Co" if sample.get('color') else 'No mesurat'),
        ('Olor', f"{sample.get('olor')} (índex dilució 25°C)" if sample.get('olor') else 'No mesurat'),
        ('Sabor', f"{sample.get('sabor')} (índex dilució 25°C)" if sample.get('sabor') else 'No mesurat')
    ]
    
    # Calculate derived values
    clor_combinat = calculate_clor_combinat_residual(sample)
    
    chlorine_params = [
        ('Clor lliure', f"{sample.get('clor_lliure')} mg/L" if sample.get('clor_lliure') else 'No mesurat'),
        ('Clor total', f"{sample.get('clor_total')} mg/L" if sample.get('clor_total') else 'No mesurat'),
        ('Clor combinat residual', f"{clor_combinat:.4f} mg/L" if clor_combinat is not None else 'No mesurat')
    ]
    
    microbiological_params = [
        ('E. coli', f"{sample.get('recompte_escherichia_coli')} NPM/100mL" if sample.get('recompte_escherichia_coli') else 'No mesurat'),
        ('Enterococs', f"{sample.get('recompte_enterococ')} NPM/100mL" if sample.get('recompte_enterococ') else 'No mesurat'),
        ('Microorganismes aerobis 22°C', f"{sample.get('recompte_microorganismes_aerobis_22c')} UFC/1mL" if sample.get('recompte_microorganismes_aerobis_22c') else 'No mesurat'),
        ('Coliformes totals', f"{sample.get('recompte_coliformes_totals')} NMP/100mL" if sample.get('recompte_coliformes_totals') else 'No mesurat')
    ]
    
    # Calculate suma haloacetics
    suma_haloacetics = calculate_suma_haloacetics(sample)
    
    chemical_acids_params = [
        ('Àcid monocloroacètic', f"{sample.get('acid_monocloroacetic')} μg/L" if sample.get('acid_monocloroacetic') else 'No mesurat'),
        ('Àcid dicloroacètic', f"{sample.get('acid_dicloroacetic')} μg/L" if sample.get('acid_dicloroacetic') else 'No mesurat'),
        ('Àcid tricloroacètic', f"{sample.get('acid_tricloroacetic')} μg/L" if sample.get('acid_tricloroacetic') else 'No mesurat'),
        ('Àcid monobromoacètic', f"{sample.get('acid_monobromoacetic')} μg/L" if sample.get('acid_monobromoacetic') else 'No mesurat'),
        ('Àcid dibromoacètic', f"{sample.get('acid_dibromoacetic')} μg/L" if sample.get('acid_dibromoacetic') else 'No mesurat'),
        ('Suma 5 haloacètics', f"{suma_haloacetics:.2f} μg/L" if suma_haloacetics is not None else 'No mesurat')
    ]
    
    # Combine all parameters
    key_params = basic_params + physical_chemical_params + chlorine_params + microbiological_params + chemical_acids_params
    """

    # Calculate suma haloacetics
    suma_haloacetics = calculate_suma_haloacetics(sample)

    # Import thresholds for visual ranges
    from .thresholds import get_threshold
    
    def is_parameter_out_of_range(param_key, value):
        """Check if a parameter value is outside the recommended range"""
        if not param_key or value is None:
            return False
        
        threshold = get_threshold(param_key)
        if not threshold:
            return False
        
        min_val = float(threshold['min'])
        max_val = float(threshold['max'])
        
        if min_val > 0:
            # Range-based parameters
            return value < min_val or value > max_val
        else:
            # Threshold-based parameters
            return value > max_val
    
    def create_home_parameter_bar(parameter_key, value):
        """Create a simplified parameter bar for home page display"""
        if value is None:
            return html.Div("No mesurat", style={'textAlign': 'center', 'color': '#6c757d'})
        
        threshold = get_threshold(parameter_key)
        if not threshold:
            return html.Div(f"{value}", style={'textAlign': 'center', 'color': '#2c3e50', 'fontWeight': '500'})
        
        # Calculate position and color
        min_val = float(threshold['min'])
        max_val = float(threshold['max'])
        
        if min_val > 0:
            # Range-based parameters
            if value < min_val or value > max_val:
                dot_color = '#dc3545'  # Red - out of range
                position_percentage = 0 if value < min_val else 100
            else:
                dot_color = '#28a745'  # Green - within range
                position_percentage = ((value - min_val) / (max_val - min_val)) * 100
        else:
            # Threshold-based parameters
            position_percentage = min((value / max_val) * 100, 100)
            if position_percentage < 100:
                dot_color = '#28a745'  # Green
            else:
                dot_color = '#dc3545'  # Red
        
        # Format value display
        if parameter_key == 'ph':
            value_display = f"{value:.1f}"
        elif 'clor' in parameter_key:
            value_display = f"{value:.3f}"
        else:
            value_display = f"{value:.2f}"
        
        return html.Div([
            html.Div([
                html.Span(f"{value_display} {threshold['unit']}", style={'fontSize': '1rem', 'fontWeight': '500', 'color': '#2c3e50'})
            ], style={'textAlign': 'center', 'marginBottom': '8px'}),
            html.Div([
                # Parameter indicator dot
                html.Div(style={
                    'position': 'absolute',
                    'left': f'{position_percentage}%',
                    'top': '50%',
                    'transform': 'translate(-50%, -50%)',
                    'width': '10px',
                    'height': '10px',
                    'backgroundColor': dot_color,
                    'borderRadius': '50%',
                    'border': '2px solid white',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
                    'zIndex': '1'
                })
            ], style={
                'width': '100%',
                'maxWidth': '200px',
                'height': '16px',
                'backgroundColor': '#e9ecef',
                'borderRadius': '8px',
                'border': '1px solid #dee2e6',
                'margin': '0 auto',
                'position': 'relative'
            }),
            html.Div([
                html.Span(f"{threshold['min']}", style={'fontSize': '0.7em', 'color': '#6c757d'}),
                html.Span(f"{threshold['max']}", style={'fontSize': '0.7em', 'color': '#6c757d'})
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'marginTop': '4px',
                'maxWidth': '200px',
                'margin': '4px auto 0 auto'
            })
        ])
    
    # Define parameters with their keys for visual range bars
    key_params_data = [
        ('Data de recollida', formatted_date, None, None),
        ('Punt de mostreig', sample.get('punt_mostreig', 'No mesurat'), None, None),
        ('Temperatura', sample.get('temperatura'), 'temperatura', '°C'),
        ('pH', sample.get('ph'), 'ph', None),
        ('Clor lliure', sample.get('clor_lliure'), 'clor_lliure', None),
        ('Terbolesa', sample.get('terbolesa'), 'terbolesa', None),
        ('Suma 5 haloacètics', suma_haloacetics, 'suma_haloacetics', None)
    ]
    
    # Check if any parameters are out of range
    has_out_of_range = any(is_parameter_out_of_range(param_key, value) for _, value, param_key, _ in key_params_data if param_key)
    
    # Create status message
    if has_out_of_range:
        status_message = html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px', 'fontSize': '1.1rem'}),
                html.Span("ATENCIÓ: Alguns paràmetres estan fora dels valors recomanats", style={'fontWeight': '600'})
            ], style={'color': '#dc3545', 'fontSize': '1rem', 'textAlign': 'center', 'marginBottom': '0.5rem'}),
            html.P([
                "Els paràmetres destacats en vermell superen els límits establerts per la normativa. ",
                "Es recomana contactar amb les autoritats sanitàries locals."
            ], style={'color': '#721c24', 'fontSize': '0.9rem', 'margin': '0', 'textAlign': 'center', 'lineHeight': '1.4'})
        ], style={
            'backgroundColor': '#f8d7da',
            'border': '1px solid #f5c6cb',
            'borderRadius': '6px',
            'padding': '1rem',
            'margin': '1rem 0'
        })
    else:
        status_message = html.Div([
            html.Div([
                html.I(className="fas fa-check-circle", style={'marginRight': '8px', 'fontSize': '1.1rem'}),
                html.Span("Tots els paràmetres dins dels valors recomanats", style={'fontWeight': '600'})
            ], style={'color': '#155724', 'fontSize': '1rem', 'textAlign': 'center', 'marginBottom': '0.5rem'}),
            html.P("La qualitat de l'aigua compleix amb els estàndards establerts per la normativa vigent.",
                  style={'color': '#155724', 'fontSize': '0.9rem', 'margin': '0', 'textAlign': 'center'})
        ], style={
            'backgroundColor': '#d4edda',
            'border': '1px solid #c3e6cb',
            'borderRadius': '6px',
            'padding': '1rem',
            'margin': '1rem 0'
        })
    
    return html.Div([
        html.H3(f"Darrera mostra{location_text}", 
                style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
        
        html.Div([
            html.Div([
                html.Div([
                    html.H5(label, style={'color': '#495057', 'margin': '0 0 0.5rem 0', 'fontSize': '0.9rem', 'textAlign': 'center'}),
                    # Display visual range bar if parameter has thresholds, otherwise show text value
                    (create_home_parameter_bar(param_key, value) if param_key and value is not None and get_threshold(param_key) 
                     else html.P(
                         f"{value} {unit}" if value is not None and unit else (value if value is not None else 'No mesurat'), 
                         style={'color': '#2c3e50', 'margin': '0', 'fontSize': '1.1rem', 'fontWeight': '500', 'textAlign': 'center'}
                     ))
                ], style={
                    'backgroundColor': '#fef2f2' if is_parameter_out_of_range(param_key, value) else 'white',
                    'padding': '1rem',
                    'borderRadius': '6px',
                    'border': '2px solid #dc3545' if is_parameter_out_of_range(param_key, value) else '1px solid #e3e6ea',
                    'minHeight': '120px',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center',
                    'boxShadow': '0 2px 8px rgba(220, 53, 69, 0.15)' if is_parameter_out_of_range(param_key, value) else '0 1px 3px rgba(0,0,0,0.08)',
                    'transition': 'transform 0.2s ease, box-shadow 0.2s ease'
                })
                for label, value, param_key, unit in key_params_data
            ], style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(180px, 1fr))',
                'gap': '1rem',
                'width': '100%',
                'gridAutoRows': 'minmax(80px, auto)'
            }),
            
            # Status message for parameter ranges
            status_message,
            
            html.Div([
                html.Button("Veure detalls complets →",
                          id='home-sample-details-btn',
                          className='btn-standard btn-home-details',
                          style={
                              'backgroundColor': '#3498db', 
                              'color': 'white', 
                              'border': 'none',
                              'padding': '12px 24px', 
                              'borderRadius': '6px', 
                              'fontSize': '1rem', 
                              'cursor': 'pointer',
                              'boxShadow': '0 4px 8px rgba(0,0,0,0.3)',
                              'transition': 'all 0.2s ease'
                          })
            ], style={'textAlign': 'center', 'marginTop': '1.5rem'})
        ])
    ], style={
        'backgroundColor': '#f8f9fa',
        'padding': '2rem',
        'borderRadius': '10px',
        'border': '1px solid #dee2e6',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
        'width': '100%',
        'boxSizing': 'border-box',
        'margin': '0'
    })

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
                href=f"/sample/{sample_id}?ref=browse",
                className='btn-standard btn-details',
                style={
                    'color': 'white',
                    'textDecoration': 'none',
                    'padding': '12px 24px',
                    'backgroundColor': '#3498db',
                    'border': 'none',
                    'borderRadius': '6px',
                    'display': 'inline-block',
                    'fontSize': '1rem',
                    'boxShadow': '0 4px 8px rgba(0,0,0,0.3)',
                    'transition': 'all 0.2s ease',
                    'cursor': 'pointer'
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
                   className='btn-standard',
                   style={
                       'margin': '0 0.5rem', 
                       'padding': '8px 16px', 
                       'backgroundColor': '#6c757d' if current_page <= 1 else '#3498db', 
                       'color': 'white', 
                       'border': 'none', 
                       'borderRadius': '4px',
                       'fontSize': '0.9rem',
                       'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
                       'transition': 'all 0.2s ease',
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
                   className='btn-standard',
                   style={
                       'margin': '0 0.5rem', 
                       'padding': '8px 16px',
                       'backgroundColor': '#6c757d' if current_page >= total_pages else '#3498db', 
                       'color': 'white', 
                       'border': 'none', 
                       'borderRadius': '4px',
                       'fontSize': '0.9rem',
                       'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
                       'transition': 'all 0.2s ease',
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
            html.Div(pagination_controls, className='pagination-controls', style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
            html.Div(page_size_controls, style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginTop': '1rem'})
        ])
    ])

def create_sample_details(sample, referrer="/browse"):
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
    
    # Helper function to format values with specific decimal places
    def format_value(value, decimals):
        if value is None or value == '':
            return None
        try:
            float_val = float(value)
            return f"{float_val:.{decimals}f}"
        except (ValueError, TypeError):
            return value
    
    physical_params = [
        ('Temperatura (°C)', format_value(sample.get('temperatura'), 1)),
        ('pH', format_value(sample.get('ph'), 1)),
        ('Conductivitat a 20°C (μS/cm)', format_value(sample.get('conductivitat_20c'), 0)),
        ('Terbolesa (NTU)', format_value(sample.get('terbolesa'), 1)),
        ('Color', format_value(sample.get('color'), 0)),
        ('Olor', format_value(sample.get('olor'), 0)),
        ('Sabor', format_value(sample.get('sabor'), 0)),
    ]
    
    # Calculate derived values
    clor_combinat_detail = calculate_clor_combinat_residual(sample)
    suma_haloacetics_detail = calculate_suma_haloacetics(sample)
    
    chemical_params = [
        ('Clor Lliure (mg/L)', format_value(sample.get('clor_lliure'), 2)),
        ('Clor Total (mg/L)', format_value(sample.get('clor_total'), 2)),
        ('Clor Combinat Residual (mg/L)', format_value(clor_combinat_detail, 2)),
        ('Àcid Monocloroacètic (μg/L)', format_value(sample.get('acid_monocloroacetic'), 0)),
        ('Àcid Dicloroacètic (μg/L)', format_value(sample.get('acid_dicloroacetic'), 0)),
        ('Àcid Tricloroacètic (μg/L)', format_value(sample.get('acid_tricloroacetic'), 0)),
        ('Àcid Monobromoacètic (μg/L)', format_value(sample.get('acid_monobromoacetic'), 0)),
        ('Àcid Dibromoacètic (μg/L)', format_value(sample.get('acid_dibromoacetic'), 0)),
        ('Suma 5 Haloacètics (μg/L)', format_value(suma_haloacetics_detail, 0)),
    ]
    
    biological_params = [
        ('Escherichia coli (UFC/100mL)', format_value(sample.get('recompte_escherichia_coli'), 0)),
        ('Enterococs (UFC/100mL)', format_value(sample.get('recompte_enterococ'), 0)),
        ('Microorganismes aerobis 22°C (UFC/mL)', format_value(sample.get('recompte_microorganismes_aerobis_22c'), 0)),
        ('Coliformes totals (UFC/100mL)', format_value(sample.get('recompte_coliformes_totals'), 0)),
    ]
    
    def create_parameter_bar(parameter_key, value):
        """Create a progress bar for a parameter showing value within acceptable thresholds"""
        if value is None:
            return html.Div("No mesurat", style={'textAlign': 'right'})
        
        threshold = get_threshold(parameter_key)
        if not threshold:
            # Fallback to simple text display if no threshold defined
            return html.Div(f"{value} {threshold.get('unit', '') if threshold else ''}", style={'textAlign': 'right'})
        
        # Universal range and dot design for all parameters
        is_safe = is_within_safe_range(parameter_key, value)
        
        # Calculate position within the range
        min_val = float(threshold['min'])
        max_val = float(threshold['max'])
        
        # For parameters with minimum threshold > 0, use full range
        # For parameters with minimum = 0, position relative to maximum
        if min_val > 0:
            # Range-based parameters (pH, Clor lliure, Clor total)
            range_width = max_val - min_val
            if value < min_val:
                position_percentage = 0
                dot_color = '#dc3545'  # Red - too low
            elif value > max_val:
                position_percentage = 100
                dot_color = '#dc3545'  # Red - too high
            else:
                position_percentage = ((value - min_val) / range_width) * 100
                dot_color = '#28a745'  # Green - within range
        else:
            # Threshold-based parameters (Suma 5 haloacètics)
            position_percentage = min((value / max_val) * 100, 100)
            if position_percentage < 100:
                dot_color = '#28a745'  # Green - good
            else:
                dot_color = '#dc3545'  # Red - exceeds threshold
        
        # Format value display with specific decimal places
        decimal_rules = {
            'ph': 1,
            'conductivitat_20c': 1,
            'terbolesa': 1,
            'temperatura': 1,
            'color': 0,
            'olor': 0,
            'sabor': 0,
            'acid_monocloroacetic': 0,
            'acid_dicloroacetic': 0,
            'acid_tricloroacetic': 0,
            'acid_monobromoacetic': 0,
            'acid_dibromoacetic': 0,
            'suma_haloacetics': 0,
            'recompte_microorganismes_aerobis_22c': 0,
            'recompte_coliformes_totals': 0,
            'recompte_escherichia_coli': 0,
            'recompte_enterococ': 0,
            'clor_lliure': 2,
            'clor_total': 2,
            'clor_combinat_residual': 2
        }
        
        decimals = decimal_rules.get(parameter_key, 2)  # Default to 2 decimals
        value_display = f"{value:.{decimals}f}"
        
        return html.Div([
            html.Div([
                html.Span(f"{value_display} {threshold['unit']}", style={'fontWeight': 'bold', 'marginRight': '10px'})
            ], style={'marginBottom': '5px', 'textAlign': 'right'}),
            html.Div([
                # Parameter indicator dot
                html.Div(style={
                    'position': 'absolute',
                    'left': f'{position_percentage}%',
                    'top': '50%',
                    'transform': 'translate(-50%, -50%)',
                    'width': '12px',
                    'height': '12px',
                    'backgroundColor': dot_color,
                    'borderRadius': '50%',
                    'border': '2px solid white',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
                    'zIndex': '1'
                })
            ], style={
                'width': '100%',
                'maxWidth': '300px',
                'height': '20px',
                'backgroundColor': '#e9ecef',
                'borderRadius': '10px',
                'border': '1px solid #dee2e6',
                'marginLeft': 'auto',
                'position': 'relative'
            }),
            html.Div([
                html.Span(f"{threshold['min']}", style={'fontSize': '0.8em', 'color': '#6c757d'}),
                html.Span(f"{threshold['max']}", style={'fontSize': '0.8em', 'color': '#6c757d'})
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'marginTop': '2px',
                'maxWidth': '300px',
                'marginLeft': 'auto'
            })
        ])

    def create_param_section(title, params, special_params=None):
        param_items = []
        for label, value in params:
            # Check if this is a special parameter that needs custom rendering
            if special_params and label in special_params:
                param_items.append(
                    html.Tr([
                        html.Td(label.replace(' (μg/L)', ''), style={'fontWeight': 'bold', 'padding': '0.5rem', 'borderBottom': '1px solid #dee2e6', 'textAlign': 'left', 'verticalAlign': 'top', 'width': '50%'}),
                        html.Td(special_params[label], style={'padding': '0.5rem', 'borderBottom': '1px solid #dee2e6', 'verticalAlign': 'top', 'width': '50%'})
                    ])
                )
            else:
                if value is not None and value != '':
                    display_value = str(value)
                else:
                    display_value = 'No mesurat'
                
                param_items.append(
                    html.Tr([
                        html.Td(label, style={'fontWeight': 'bold', 'padding': '0.5rem', 'borderBottom': '1px solid #dee2e6', 'textAlign': 'left', 'width': '50%'}),
                        html.Td(display_value, style={'padding': '0.5rem', 'borderBottom': '1px solid #dee2e6', 'textAlign': 'right', 'width': '50%'})
                    ])
                )
        
        return html.Div([
            html.H3(title, style={'color': '#495057', 'borderBottom': '2px solid #007bff', 'paddingBottom': '0.5rem'}),
            html.Table(param_items, style={
                'width': '100%', 
                'marginBottom': '2rem',
                'tableLayout': 'fixed'
            })
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
                create_param_section("Paràmetres Físics", physical_params, {
                    'pH': create_parameter_bar('ph', sample.get('ph')),
                    'Conductivitat a 20°C (μS/cm)': create_parameter_bar('conductivitat_20c', sample.get('conductivitat_20c')),
                    'Terbolesa (NTU)': create_parameter_bar('terbolesa', sample.get('terbolesa')),
                    'Color': create_parameter_bar('color', sample.get('color')),
                    'Olor': create_parameter_bar('olor', sample.get('olor')),
                    'Sabor': create_parameter_bar('sabor', sample.get('sabor'))
                }),
                create_param_section("Paràmetres Químics", chemical_params, {
                    'Clor Lliure (mg/L)': create_parameter_bar('clor_lliure', sample.get('clor_lliure')),
                    'Clor Total (mg/L)': create_parameter_bar('clor_total', sample.get('clor_total')),
                    'Suma 5 Haloacètics (μg/L)': create_parameter_bar('suma_haloacetics', suma_haloacetics_detail)
                }),
                create_param_section("Paràmetres Biològics", biological_params),
                
                # Back link
                html.Div([
                    dcc.Link("← Tornar a la llista" if referrer == "/browse" else "← Tornar", 
                            href=referrer,
                            className='btn-standard btn-home-details',
                            style={
                                'backgroundColor': '#3498db',
                                'color': 'white',
                                'border': 'none',
                                'padding': '12px 24px',
                                'borderRadius': '6px',
                                'fontSize': '1rem',
                                'cursor': 'pointer',
                                'boxShadow': '0 4px 8px rgba(0,0,0,0.3)',
                                'transition': 'all 0.2s ease',
                                'textDecoration': 'none',
                                'display': 'inline-block'
                            })
                ], style={'textAlign': 'center', 'marginTop': '2rem'})
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
            html.P("Distribució de mostres per ubicació no disponible", style={'textAlign': 'center', 'color': '#6c757d'})
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
            html.P("Distribució de mostres per mes no disponible", style={'textAlign': 'center', 'color': '#6c757d'})
        ])
    
    # Calculate date range (last 12 months from start of month)
    today = datetime.now()
    twelve_months_ago = today.replace(day=1) - timedelta(days=365)
        
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
            'text': 'Mostres carregades els últims 12 mesos',
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