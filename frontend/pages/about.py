from dash import html

def create_about_page():
    """Create the about page layout"""
    return html.Div([
        html.Div([
            html.H1([
                "Qui som - ",
                html.Span("AiGua", style={'color': '#3498db'}),
                "lba"
            ], style={
                       'color': '#2c3e50', 
                       'fontSize': '2.5rem', 
                       'marginBottom': '2rem', 
                       'textAlign': 'center'
                   }),
            
            # Purpose section
            html.Div([
                html.H3("El projecte", style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                html.P([html.Span("AiGua", style={'color': '#3498db'}),
                        "lba és una iniciativa ciutadana liderada per veïns de Gualba amb la finalitat "
                        "de posar a disposició de tothom les dades de qualitat de l'aigua al municipi. ",
                        "El nostre sistema proporciona una plataforma oberta per a la seva "
                        "recollida, visualització i anàlisi, promovent la "
                        "transparència i la participació comunitària."
                ], style={'fontSize': '1rem', 'lineHeight': '1.6', 'color': '#34495e'})
            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),
            
            # Objectives section
            html.Div([
                html.H3("El nostre propòsit", style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                html.Ul([
                    html.Li("Facilitar l'accés obert a les dades de qualitat de l'aigua."),
                    html.Li("Promoure la participació ciutadana en la monitorització de l'aigua de Gualba."),
                    html.Li("Proporcionar eines pel control, la detecció i avís de possibles problemes de qualitat."),
                    html.Li("Reduir les inquietuds veïnals relacionades amb la qualitat i el servei municipal de l'aigua.")
                ], style={'fontSize': '1rem', 'lineHeight': '1.6', 'color': '#34495e'})

            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),
            
            # Transparency section
            html.Div([
                html.H3("Compromís amb la transparència", style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                html.P([
                    "Creiem en la transparència total de les dades de qualitat de l'aigua. ",
                    "Totes les mesures són públiques i accessibles per a la ciutadania, ",
                    "promovent una gestió participativa i responsable dels recursos hídrics del nostre municipi."
                ], style={'fontSize': '1rem', 'lineHeight': '1.6', 'fontStyle': 'italic', 'color': '#34495e', 'textAlign': 'center'})
            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),

            # Contact section
            html.Div([
                html.H3("Contacte", style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                html.P([
                    "Per a més informació o per unir-te al projecte, contacta'ns a ",
                    html.A("contacte@aigualba.com", href="mailto:contacte@aigualba.com")
                ], style={'fontSize': '1rem', 'lineHeight': '1.6', 'color': '#34495e', 'textAlign': 'center'})
            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),
                
        ], style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '2rem',
            'backgroundColor': '#f8f9fa',
            'minHeight': 'calc(100vh - 100px)'
        })
    ])