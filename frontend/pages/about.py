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
                html.H3("El nostre propòsit", style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                html.P([
                    "AiGualba és una iniciativa ciutadana per monitoritzar i garantir la qualitat de l'aigua ",
                    "al municipi de Gualba. El nostre sistema proporciona monitorització en temps real ",
                    "i anàlisi de dades històriques dels indicadors essencials de qualitat de l'aigua."
                ], style={'fontSize': '1rem', 'lineHeight': '1.6', 'color': '#34495e'})
            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),
                
            # Features section
            html.Div([
                html.H3("Característiques principals", style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                html.Ul([
                    html.Li("Monitorització en temps real de la qualitat de l'aigua"),
                    html.Li("Visualització de dades històriques i tendències"),
                    html.Li("Participació ciutadana i col·laboració comunitària"),
                    html.Li("Alertes automàtiques per incidències en els umballs de qualitat"),
                    html.Li("Informes i analítiques integrals")
                ], style={'fontSize': '1rem', 'lineHeight': '1.6', 'color': '#34495e'})
            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),
                
            # Parameters section
            html.Div([
                html.H3("Paràmetres que monitoritzem", style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                html.Div([
                    # Physical-Chemical Parameters
                    html.Div([
                        html.H4("Paràmetres fisicoquímics", style={'color': '#3498db', 'marginBottom': '1rem', 'textAlign': 'center'}),
                        html.Ul([
                            html.Li("pH - Nivells d'acidesa/alcalinitat"),
                            html.Li("Temperatura - Control tèrmic del sistema"),
                            html.Li("Conductivitat 20°C - Mesura de sals dissoltes"),
                            html.Li("Terbolesa - Claredat de l'aigua"),
                            html.Li("Color - Pigmentació de l'aigua"),
                            html.Li("Olor i sabor - Qualitats organolèptiques")
                        ], style={'fontSize': '0.95rem', 'lineHeight': '1.5'})
                    ], style={'backgroundColor': '#f8f9fa', 'padding': '1.5rem', 'borderRadius': '8px', 'margin': '1rem 0'}),
                    
                    # Chemical Parameters  
                    html.Div([
                        html.H4("Paràmetres químics", style={'color': '#3498db', 'marginBottom': '1rem', 'textAlign': 'center'}),
                        html.Ul([
                            html.Li("Clor lliure - Desinfectant residual actiu"),
                            html.Li("Clor total - Capacitat desinfectant total"),
                            html.Li("Clor combinat residual - Clor combinat amb compostos orgànics"),
                            html.Li("Àcids haloacètics - Subproductes de desinfecció"),
                            html.Li("Suma 5 haloacètics - Indicador regulat per la normativa")
                        ], style={'fontSize': '0.95rem', 'lineHeight': '1.5'})
                    ], style={'backgroundColor': '#f8f9fa', 'padding': '1.5rem', 'borderRadius': '8px', 'margin': '1rem 0'}),
                    
                    # Microbiological Parameters
                    html.Div([
                        html.H4("Paràmetres microbiològics", style={'color': '#3498db', 'marginBottom': '1rem', 'textAlign': 'center'}),
                        html.Ul([
                            html.Li("E. coli - Indicador de contaminació fecal"),
                            html.Li("Enterococs - Microorganismes indicadors de qualitat"),
                            html.Li("Coliformes totals - Indicadors de contaminació general"),
                            html.Li("Microorganismes aerobis 22°C - Flora microbiana total")
                        ], style={'fontSize': '0.95rem', 'lineHeight': '1.5'})
                    ], style={'backgroundColor': '#f8f9fa', 'padding': '1.5rem', 'borderRadius': '8px', 'margin': '1rem 0'}),
                ])
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
            })
                
        ], style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '2rem',
            'backgroundColor': '#f8f9fa',
            'minHeight': 'calc(100vh - 100px)'
        })
    ])