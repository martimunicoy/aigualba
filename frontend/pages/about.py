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
            
            html.Div([
                html.Div([
                    html.H3("El nostre propòsit", style={'color': '#2c3e50', 'marginBottom': '1rem'}),
                    html.P([
                        "AiGualba és una iniciativa ciutadana per monitoritzar i garantir la qualitat de l'aigua ",
                        "al municipi de Gualba. El nostre sistema proporciona monitorització en temps real ",
                        "i anàlisi de dades històriques dels indicadors essencials de qualitat de l'aigua."
                    ], style={'fontSize': '1.1rem', 'lineHeight': '1.6', 'marginBottom': '2rem'}),
                ]),
                
                html.Div([
                    html.H3("Característiques principals:", style={'color': '#2c3e50', 'marginTop': '2rem'}),
                    html.Ul([
                        html.Li("Monitorització en temps real de la qualitat de l'aigua"),
                        html.Li("Visualització de dades històriques i tendències"),
                        html.Li("Participació ciutadana i col·laboració comunitària"),
                        html.Li("Alertes automàtiques per incidències en els umballs de qualitat"),
                        html.Li("Informes i analítiques integrals")
                    ], style={'fontSize': '1.1rem', 'lineHeight': '1.8'})
                ]),
                
                html.Div([
                    html.H3("Paràmetres que monitoritzem:", style={'color': '#2c3e50', 'marginTop': '2rem'}),
                    html.Div([
                        html.Div([
                            html.H4("pH", style={'color': '#3498db', 'marginBottom': '0.5rem'}),
                            html.P("Nivells d'acidesa/alcalinitat per garantir l'equilibri químic adequat")
                        ], style={'backgroundColor': '#f8f9fa', 'padding': '1.5rem', 'borderRadius': '8px', 'margin': '1rem 0'}),
                        
                        html.Div([
                            html.H4("Temperatura", style={'color': '#3498db', 'marginBottom': '0.5rem'}),
                            html.P("Control de la temperatura per detectar anomalies en el sistema")
                        ], style={'backgroundColor': '#f8f9fa', 'padding': '1.5rem', 'borderRadius': '8px', 'margin': '1rem 0'}),
                        
                        html.Div([
                            html.H4("Turbiditat", style={'color': '#3498db', 'marginBottom': '0.5rem'}),
                            html.P("Mesura de la claredat de l'aigua per avaluar la presència de partícules")
                        ], style={'backgroundColor': '#f8f9fa', 'padding': '1.5rem', 'borderRadius': '8px', 'margin': '1rem 0'}),
                    ])
                ]),
                
                html.Div([
                    html.H3("Compromís amb la transparència", style={'color': '#2c3e50', 'marginTop': '3rem'}),
                    html.P([
                        "Creiem en la transparència total de les dades de qualitat de l'aigua. ",
                        "Totes les mesures són públiques i accessibles per a la ciutadania, ",
                        "promovent una gestió participativa i responsable dels recursos hídrics del nostre municipi."
                    ], style={'fontSize': '1.1rem', 'lineHeight': '1.6', 'fontStyle': 'italic', 'color': '#7f8c8d'})
                ]),
                
            ], style={
                'fontSize': '1.1rem', 
                'lineHeight': '1.6', 
                'color': '#34495e',
                'maxWidth': '800px',
                'margin': '0 auto'
            })
        ], style={
            'maxWidth': '1200px', 
            'margin': '0 auto', 
            'padding': '3rem 2rem'
        })
    ], style={'backgroundColor': '#f8f9fa', 'minHeight': '80vh'})