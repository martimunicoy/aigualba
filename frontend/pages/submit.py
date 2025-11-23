from dash import html, dcc

def create_submit_page():
    """Create the submit data page layout"""
    return html.Div([
        html.Div([
            html.H1("Aporta noves dades", 
                   style={
                       'color': '#2c3e50', 
                       'fontSize': '2.5rem', 
                       'marginBottom': '2rem', 
                       'textAlign': 'center'
                   }),
            
            html.Div([
                html.Div([
                    html.H3("Formulari de mesures de qualitat de l'aigua", 
                           style={'color': '#2c3e50', 'marginBottom': '2rem', 'textAlign': 'center'}),
                    
                    html.Div([
                        html.Label("Tipus de paràmetre:", 
                                  style={'display': 'block', 'marginBottom': '0.5rem', 'fontWeight': '600', 'color': '#2c3e50'}),
                        dcc.Dropdown(
                            id="parameter-name",
                            options=[
                                {"label": "Nivell de pH", "value": "pH"},
                                {"label": "Temperatura (°C)", "value": "Temperature"},
                                {"label": "Turbiditat (NTU)", "value": "Turbidity"},
                                {"label": "Oxigen dissolt (mg/L)", "value": "Dissolved_Oxygen"},
                                {"label": "Clor (mg/L)", "value": "Chlorine"}
                            ],
                            placeholder="Selecciona el tipus de paràmetre",
                            style={'marginBottom': '1rem'}
                        )
                    ], style={'marginBottom': '1.5rem'}),
                    
                    html.Div([
                        html.Label("Valor mesurat:", 
                                  style={'display': 'block', 'marginBottom': '0.5rem', 'fontWeight': '600', 'color': '#2c3e50'}),
                        dcc.Input(
                            id="parameter-value",
                            type="number",
                            placeholder="Introdueix el valor mesurat",
                            style={'width': '100%', 'padding': '0.75rem', 'border': '2px solid #ecf0f1', 'borderRadius': '6px', 'fontSize': '1rem'}
                        )
                    ], style={'marginBottom': '1.5rem'}),
                    
                    html.Div([
                        html.Label("Ubicació (opcional):", 
                                  style={'display': 'block', 'marginBottom': '0.5rem', 'fontWeight': '600', 'color': '#2c3e50'}),
                        dcc.Input(
                            id="parameter-location",
                            type="text",
                            placeholder="ex. Pantà A, Estació de bombeig 2",
                            style={'width': '100%', 'padding': '0.75rem', 'border': '2px solid #ecf0f1', 'borderRadius': '6px', 'fontSize': '1rem'}
                        )
                    ], style={'marginBottom': '1.5rem'}),
                    
                    html.Div([
                        html.Label("Observacions (opcional):", 
                                  style={'display': 'block', 'marginBottom': '0.5rem', 'fontWeight': '600', 'color': '#2c3e50'}),
                        dcc.Textarea(
                            id="parameter-notes",
                            placeholder="Observacions addicionals o comentaris",
                            style={
                                'width': '100%', 
                                'padding': '0.75rem', 
                                'border': '2px solid #ecf0f1', 
                                'borderRadius': '6px', 
                                'fontSize': '1rem',
                                'minHeight': '100px',
                                'resize': 'vertical'
                            }
                        )
                    ], style={'marginBottom': '2rem'}),
                    
                    html.Div([
                        html.Button("Enviar dades", 
                                   id="submit-button", 
                                   style={
                                       'backgroundColor': '#e74c3c', 
                                       'color': 'white', 
                                       'border': 'none', 
                                       'padding': '12px 32px', 
                                       'borderRadius': '6px', 
                                       'fontSize': '1.1rem', 
                                       'cursor': 'pointer',
                                       'width': '100%',
                                       'transition': 'background-color 0.3s'
                                   }),
                        html.Div(id="submit-status", style={'marginTop': '1rem', 'textAlign': 'center'})
                    ])
                    
                ], style={
                    'backgroundColor': 'white', 
                    'padding': '3rem', 
                    'borderRadius': '10px', 
                    'boxShadow': '0 4px 20px rgba(0,0,0,0.1)', 
                    'maxWidth': '600px', 
                    'margin': '0 auto'
                }),
                
                # Information section
                html.Div([
                    html.H4("Com contribuir amb dades de qualitat", style={'color': '#2c3e50', 'marginBottom': '1rem'}),
                    html.Ul([
                        html.Li("Assegura't que les mesures siguin precises i recents"),
                        html.Li("Utilitza equips calibrats per obtenir lectures fiables"),
                        html.Li("Inclou la ubicació exacta per facilitar el seguiment"),
                        html.Li("Reporta qualsevol anomalia o circumstància especial"),
                        html.Li("Les dades seran verificades abans de ser publicades")
                    ], style={'lineHeight': '1.8'})
                ], style={
                    'backgroundColor': '#e3f2fd', 
                    'padding': '2rem', 
                    'borderRadius': '10px', 
                    'marginTop': '2rem',
                    'border': '1px solid #90caf9'
                })
            ])
        ], style={
            'maxWidth': '1000px', 
            'margin': '0 auto', 
            'padding': '2rem'
        })
    ], style={'backgroundColor': '#f8f9fa', 'minHeight': '80vh'})