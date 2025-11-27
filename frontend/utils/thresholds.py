# Water quality parameter thresholds according to EU Directive 2020/2184
# and Spanish drinking water regulations (RD 140/2003)

WATER_QUALITY_THRESHOLDS = {
    # Chemical parameters
    'suma_haloacetics': {
        'min': 0,
        'max': 60,  # μg/L - EU legal limit for total haloacetic acids (HAA5)
        'unit': 'μg/L',
        'name': 'Suma 5 Haloacètics'
    },
    
    # Physical parameters
    'ph': {
        'min': 6.5,
        'max': 9.5,  # pH units - EU acceptable range for drinking water
        'unit': 'pH',
        'name': 'pH'
    },
    
    # Chlorine parameters
    'clor_lliure': {
        'min': 0.2,    # Minimum residual chlorine for disinfection
        'max': 1.0,    # mg/L - Maximum recommended free chlorine
        'unit': 'mg/L',
        'name': 'Clor Lliure'
    },
    
    'clor_total': {
        'min': 0.2,    # Minimum total chlorine for effective disinfection
        'max': 2.0,    # mg/L - Maximum total chlorine limit
        'unit': 'mg/L',
        'name': 'Clor Total'
    },
    
    # Physical water quality parameters
    'terbolesa': {
        'min': 0,      # Minimum turbidity (clear water)
        'max': 4.0,    # NTU - EU limit for drinking water turbidity
        'unit': 'NTU',
        'name': 'Terbolesa'
    },
    
    'conductivitat_20c': {
        'min': 0,      # Minimum conductivity
        'max': 2500,   # μS/cm - EU guideline value for conductivity
        'unit': 'μS/cm',
        'name': 'Conductivitat a 20°C'
    },
    
    'color': {
        'min': 0,      # No color (clear water)
        'max': 15,     # mg/L Pt-Co - EU acceptable limit for color
        'unit': 'mg/L Pt-Co',
        'name': 'Color'
    },
    
    'olor': {
        'min': 0,      # No odor
        'max': 3,      # Index dilution at 25°C - EU acceptable limit
        'unit': 'índex dilució',
        'name': 'Olor'
    },
    
    'sabor': {
        'min': 0,      # No taste
        'max': 3,      # Index dilution at 25°C - EU acceptable limit  
        'unit': 'índex dilució',
        'name': 'Sabor'
    }
}

def get_threshold(parameter_key):
    """Get threshold information for a specific parameter"""
    return WATER_QUALITY_THRESHOLDS.get(parameter_key)

def is_within_safe_range(parameter_key, value):
    """Check if a value is within the safe range for a parameter"""
    if value is None:
        return None
    
    threshold = get_threshold(parameter_key)
    if not threshold:
        return None
    
    return threshold['min'] <= value <= threshold['max']

def get_percentage_of_range(parameter_key, value):
    """Calculate what percentage of the acceptable range a value represents"""
    if value is None:
        return None
    
    threshold = get_threshold(parameter_key)
    if not threshold:
        return None
    
    # For pH, calculate distance from optimal center (7.0-8.5 range)
    if parameter_key == 'ph':
        optimal_min = 7.0
        optimal_max = 8.5
        if optimal_min <= value <= optimal_max:
            return 0  # Optimal range
        elif value < optimal_min:
            # Distance from minimum acceptable
            return ((optimal_min - value) / (optimal_min - threshold['min'])) * 100
        else:
            # Distance from maximum acceptable
            return ((value - optimal_max) / (threshold['max'] - optimal_max)) * 100
    
    # For other parameters, calculate percentage of maximum threshold
    return min((value / threshold['max']) * 100, 150)  # Cap at 150% for visualization