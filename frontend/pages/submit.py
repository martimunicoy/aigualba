from dash import html, dcc
from datetime import date


def create_input_field(field_id, label_text, field_type="number", placeholder="", min_val=None, max_val=None, step=None):
    """Create a standardized input field with label in row format"""
    input_props = {
        'id': field_id,
        'type': field_type,
        'placeholder': placeholder,
        'className': 'form-input-aligned'
    }
    
    if field_type == "number":
        if min_val is not None:
            input_props['min'] = min_val
        if max_val is not None:
            input_props['max'] = max_val
        if step is not None:
            input_props['step'] = step
    
    return html.Div([
        html.Label(label_text, className='form-label-aligned'),
        dcc.Input(**input_props)
    ], className='form-row-aligned')


def create_section(title, fields):
    """Create a form section with title and fields"""
    return html.Div([
        html.H3(title, className='submit-section-title'),
        html.Div(fields, className='submit-fields-container')
    ], className='submit-form-section')


def create_submit_page():
    """Create the submit data page layout with improved styling matching home.py"""
    return html.Div([
        # Hero-style header section
        html.Div([
            html.H1("Nova mostra d'aigua", className='submit-hero-title'),
            html.P("Aporta noves dades de qualitat de l'aigua del municipi de Gualba", 
                   className='submit-hero-subtitle'),
        ], className='submit-hero-section'),
        
        # Instructions section at the beginning
        html.Div([
            html.H3("Instruccions per a la recollida de mostres", className='instructions-title'),
            html.Div([
                html.Ul([
                    html.Li("Assegura't que les mesures siguin precises i recents"),
                    html.Li("Utilitza equips calibrats per obtenir lectures fiables"),
                    html.Li("Els camps marcats amb * són obligatoris"),
                    html.Li("El clor combinat es calcula automàticament"),
                    html.Li("Els paràmetres microbiològics haurien de ser propers a zero per a aigua potable"),
                    html.Li("Tots els paràmetres són opcionals excepte la data i punt de mostreig")
                ], className='instructions-list')
            ])
        ], className='instructions-section'),
        
        # Main form container
        html.Div([
            # Validation messages
            html.Div(id="validation-alert", className='validation-alert', style={'display': 'none'}),
            html.Div(id="submit-sample-status", className='submit-status', style={'display': 'none'}),
            
            # Basic information section
            create_section("Informació bàsica", [
                html.Div([
                    html.Label("Data de la mostra *", className='form-label-aligned'),
                    dcc.DatePickerSingle(
                        id='sample-date',
                        date=date.today(),
                        display_format='DD/MM/YYYY',
                        className='form-input-aligned',
                        style={'border': '0', 'padding': '0'}
                    )
                ], className='form-row-aligned'),
                html.Div([
                    html.Label("Punt de mostreig *", className='form-label-aligned'),
                    dcc.Input(
                        id="punt-mostreig",
                        type="text",
                        placeholder="ex. Dipòsit principal, Xarxa distribució zona A",
                        className='form-input-aligned'
                    )
                ], className='form-row-aligned')
            ]),
            
            # Physical and chemical parameters
            create_section("Paràmetres físics i químics", [
                create_input_field("temperatura", "Temperatura (°C)", placeholder="ex. 20.5", min_val=-5, max_val=60, step=0.1),
                create_input_field("ph", "pH", placeholder="ex. 7.2", min_val=0, max_val=14, step=0.1),
                create_input_field("conductivitat-20c", "Conductivitat a 20°C (μS/cm)", placeholder="ex. 250", min_val=0, max_val=10000, step=1),
                create_input_field("terbolesa", "Terbolesa (UNF)", placeholder="ex. 0.5", min_val=0, step=0.01),
                create_input_field("color", "Color (mg/l Pt-Co)", placeholder="ex. 5", min_val=0, step=0.1),
                create_input_field("olor", "Olor (índex dilució a 25°C)", placeholder="ex. 2", min_val=0, step=1),
                create_input_field("sabor", "Sabor (índex dilució a 25°C)", placeholder="ex. 2", min_val=0, step=1)
            ]),
            
            # Chlorine parameters
            create_section("Paràmetres de clor", [
                create_input_field("clor-lliure", "Clor lliure (mg Cl₂/l)", placeholder="ex. 0.5", min_val=0, max_val=50, step=0.01),
                create_input_field("clor-total", "Clor total (mg Cl₂/l)", placeholder="ex. 0.8", min_val=0, max_val=50, step=0.01)
            ]),
            html.P("Nota: El clor combinat es calcula automàticament com a clor total menys clor lliure.", 
                   className='section-note'),

            # Microbiological parameters
            create_section("Paràmetres microbiològics", [
                create_input_field("recompte-escherichia-coli", "E. coli (NPM/100 ml)", placeholder="ex. 0", min_val=0, step=0.01),
                create_input_field("recompte-enterococ", "Enterococ (NPM/100 ml)", placeholder="ex. 0", min_val=0, step=0.01),
                create_input_field("recompte-microorganismes-aerobis-22c", "Microorganismes aeròbics a 22°C (ufc/1 ml)", placeholder="ex. 100", min_val=0, step=1),
                create_input_field("recompte-coliformes-totals", "Coliformes Totals (NMP/100 ml)", placeholder="ex. 0", min_val=0, step=0.01)
            ]),
            
            # Acid parameters
            create_section("Àcids haloacètics", [
                create_input_field("acid-monocloroacetic", "Àcid monocloroacètic (μg/l)", placeholder="ex. 1.0", min_val=0, step=0.01),
                create_input_field("acid-dicloroacetic", "Àcid dicloroacètic (μg/l)", placeholder="ex. 2.0", min_val=0, step=0.01),
                create_input_field("acid-tricloroacetic", "Àcid tricloroacètic (μg/l)", placeholder="ex. 1.5", min_val=0, step=0.01),
                create_input_field("acid-monobromoacetic", "Àcid monobromoacètic (μg/l)", placeholder="ex. 0.5", min_val=0, step=0.01),
                create_input_field("acid-dibromoacetic", "Àcid dibromoacètic (μg/l)", placeholder="ex. 0.3", min_val=0, step=0.01)
            ]),
            html.P("Nota: La suma dels 5 àcids haloacètics es calcula automàticament a partir dels valors introduïts.",
                   className='section-note'),

            # Submit button
            html.Div([
                html.Button("Enviar mostra", id="submit-sample-button", className='hero-btn-primary submit-btn')
            ], className='submit-button-section')
            
        ], className='submit-main-container')
    ], className='submit-page-container')
