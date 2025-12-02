from dash import html, dcc
from datetime import date


def create_input_field(field_id, label_text, field_type="number", placeholder="", min_val=None, max_val=None, step=None):
    """Create a standardized input field with label in row format"""
    input_props = {
        'id': field_id,
        'type': field_type,
        'placeholder': placeholder,
        'style': {
            'fontSize': '1rem', 
            'padding': '8px', 
            'borderRadius': '4px', 
            'border': '1px solid #ddd',
            'width': '100%',
            'boxSizing': 'border-box'
        }
    }
    
    if field_type == "number":
        if min_val is not None:
            input_props['min'] = min_val
        if max_val is not None:
            input_props['max'] = max_val
        if step is not None:
            input_props['step'] = step
    
    return html.Div([
        html.Label(label_text, 
                  style={'fontWeight': 'bold', 'marginBottom': '0.5rem', 'display': 'block', 'color': '#495057'}),
        dcc.Input(**input_props)
    ], style={'marginBottom': '0', 'minHeight': '80px', 'display': 'flex', 'flexDirection': 'column'})


def create_section(title, fields, note=None):
    """Create a form section with title and fields arranged in responsive columns"""
    return html.Div([
        html.H3(title, 
                style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
        html.Div(fields, className='submit-form-fields', style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(400px, 1fr))',
            'gap': '1rem',
            'gridAutoRows': 'auto'
        }),
        html.P(note, style={'fontSize': '0.9rem', 'color': '#6c757d', 'fontStyle': 'italic', 'textAlign': 'center', 'marginTop': '1rem'}) if note else None
    ], style={
        'backgroundColor': 'white', 
        'margin': '1rem 0', 
        'padding': '2rem', 
        'borderRadius': '10px', 
        'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
    })


def create_submit_page():
    """Create the submit data page layout"""
    return html.Div([
        html.Div([
            html.H1("Aporta una nova mostra", 
                   style={
                       'color': '#2c3e50', 
                       'fontSize': '2.5rem', 
                       'marginBottom': '2rem', 
                       'textAlign': 'center'
                   }),
            
            # Instructions section
            html.Div([
                html.H3("Com utilitzar aquesta pàgina", 
                        style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                html.Ul([
                    html.Li("Assegura't que les mesures siguin precises i recents"),
                    html.Li("Utilitza equips calibrats per obtenir lectures fiables"),
                    html.Li("Els camps marcats amb * són obligatoris"),
                    html.Li("Has d'introduir almenys un paràmetre per poder enviar la mostra"),
                    html.Li("El clor combinat es calcula automàticament"),
                    html.Li("Els paràmetres microbiològics haurien de ser propers a zero per a aigua potable")
                ], style={'fontSize': '1rem', 'lineHeight': '1.6', 'color': '#34495e'})
            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),

            # Basic information section
            create_section("Informació bàsica", [
                html.Div([
                    html.Label("Data de la mostra *", 
                              style={'fontWeight': 'bold', 'marginBottom': '0.5rem', 'display': 'block', 'color': '#495057'}),
                    dcc.DatePickerSingle(
                        id='sample-date',
                        placeholder='Selecciona',
                        display_format='DD/MM/YYYY',
                        clearable=True,
                        max_date_allowed=date.today(),
                        style={'fontSize': '1rem'}
                    )
                ], style={'marginBottom': '1rem'}),
                html.Div([
                    html.Label("Punt de mostreig *", 
                              style={'fontWeight': 'bold', 'marginBottom': '0.5rem', 'display': 'block', 'color': '#495057'}),
                    dcc.Dropdown(
                        id="punt-mostreig",
                        options=[
                            {'label': 'Dipòsit Vell Can Figueres', 'value': 'Dipòsit Vell Can Figueres'},
                            {'label': 'Dipòsit Nou Can Figueres', 'value': 'Dipòsit Nou Can Figueres'},
                            {'label': 'Font de la Plaça', 'value': 'Font de la Plaça'},
                            {'label': 'Font Masia Can Figueres', 'value': 'Font Masia Can Figueres'},
                            {'label': 'Dipòsit Royal Park 1', 'value': 'Dipòsit Royal Park 1'},
                            {'label': 'Dipòsit Royal Park 2', 'value': 'Dipòsit Royal Park 2'},
                            {'label': 'Dipòsit Can Pla', 'value': 'Dipòsit Can Pla'}
                        ],
                        placeholder="Selecciona punt de mostreig",
                        clearable=True,
                        style={'fontSize': '1rem'}
                    )
                ], style={'marginBottom': '1rem'})
            ]),
            
            # Physical and chemical parameters
            create_section("Paràmetres físics i químics", [
                create_input_field("temperatura", "Temperatura (°C)", placeholder="ex. 20.5", min_val=-5, max_val=100, step=0.1),
                create_input_field("ph", "pH", placeholder="ex. 7.2", min_val=0, max_val=14, step=0.1),
                create_input_field("conductivitat-20c", "Conductivitat a 20°C (μS/cm)", placeholder="ex. 250", min_val=0, step=1),
                create_input_field("terbolesa", "Terbolesa (UNF)", placeholder="ex. 0.5", min_val=0, step=0.01),
                create_input_field("color", "Color (mg/l Pt-Co)", placeholder="ex. 5", min_val=0, step=0.1),
                create_input_field("olor", "Olor (índex dilució a 25°C)", placeholder="ex. 2", min_val=0, step=1),
                create_input_field("sabor", "Sabor (índex dilució a 25°C)", placeholder="ex. 2", min_val=0, step=1)
            ]),
            
            # Chlorine parameters
            create_section("Paràmetres de clor", [
                create_input_field("clor-lliure", "Clor lliure (mg Cl₂/l)", placeholder="ex. 0.5", min_val=0, step=0.01),
                create_input_field("clor-total", "Clor total (mg Cl₂/l)", placeholder="ex. 0.8", min_val=0, step=0.01),
            ], note="Nota: El clor combinat es calcula automàticament com a clor total menys clor lliure."),

            # Microbiological parameters
            create_section("Paràmetres microbiològics", [
                create_input_field("recompte-escherichia-coli", "E. coli (NPM/100 ml)", placeholder="ex. 0", min_val=0, step=0.01),
                create_input_field("recompte-enterococ", "Enterococ (NPM/100 ml)", placeholder="ex. 0", min_val=0, step=0.01),
                create_input_field("recompte-microorganismes-aerobis-22c", "Microorganismes aeròbics a 22°C (ufc/1 ml)", placeholder="ex. 100", min_val=0, step=1),
                create_input_field("recompte-coliformes-totals", "Coliformes totals (NMP/100 ml)", placeholder="ex. 0", min_val=0, step=0.01)
            ]),
            
            # Acid parameters
            create_section("Àcids haloacètics", [
                create_input_field("acid-monocloroacetic", "Àcid monocloroacètic (μg/l)", placeholder="ex. 1.0", min_val=0, step=0.01),
                create_input_field("acid-dicloroacetic", "Àcid dicloroacètic (μg/l)", placeholder="ex. 2.0", min_val=0, step=0.01),
                create_input_field("acid-tricloroacetic", "Àcid tricloroacètic (μg/l)", placeholder="ex. 1.5", min_val=0, step=0.01),
                create_input_field("acid-monobromoacetic", "Àcid monobromoacètic (μg/l)", placeholder="ex. 0.5", min_val=0, step=0.01),
                create_input_field("acid-dibromoacetic", "Àcid dibromoacètic (μg/l)", placeholder="ex. 0.3", min_val=0, step=0.01)
            ], note="Nota: La suma dels 5 àcids haloacètics es calcula automàticament a partir dels valors introduïts."),
            
            # Form sections
            html.Div([
            # Submit button
            html.Div([
                html.Button("Aporta una nova mostra", 
                          id="submit-sample-button", 
                          className='btn-standard btn-submit',
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
            ], style={'textAlign': 'center'}),
            html.Div(id="submit-sample-status", style={'display': 'none'})

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
            'padding': '2rem',
            'backgroundColor': '#f8f9fa',
            'minHeight': 'calc(100vh - 100px)'
        })
    ])
