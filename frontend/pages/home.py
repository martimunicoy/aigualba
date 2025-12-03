from dash import html, dcc
import requests
import os

def create_home_page():
    """Create the home page layout"""
    return html.Div([
        # Hero Section with Image and Overlay Content
        html.Div([
            # Background Image
            html.Img(src='/assets/images/3c7ac384742589.5d66896467ca0.jpg', 
                     alt='Photography by Rafael Aguilera Moyano',
                     className='hero-image',
                     style={
                         'width': '100vw', 
                         'maxWidth': '1200px',
                         'height': '500px', 
                         'objectFit': 'cover', 
                         'display': 'block',
                         'position': 'absolute',
                         'top': '0',
                         'left': '50%',
                         'transform': 'translateX(-50%)',
                         'zIndex': '1',
                         'borderRadius': '10px'
                     }),
            
            # Overlay Content
            html.Div([
                # Welcome Title
                html.H1([
                    "Benvingut a ",
                    html.Span("AiGua", style={'color': '#3498db'}),
                    "lba!"
                ], className='hero-title', style={
                            'fontSize': '3.5rem', 
                            'marginBottom': '2rem', 
                            'fontWeight': '300',
                            'textAlign': 'center',
                            'color': 'white',
                            'textShadow': '2px 2px 4px rgba(0,0,0,0.7)'
                        }),
                
                # Logo
                html.Div([
                    html.Img(src='/assets/images/logo3.png', 
                             alt='AiGua-lba Logo',
                             className='hero-logo',
                             style={
                                 'height': '80px',
                                 'width': 'auto',
                                 'filter': 'drop-shadow(2px 2px 4px rgba(0,0,0,0.3))'
                             })
                ], style={
                    'textAlign': 'center',
                    'margin': '0 0 0.5rem 0'
                }),
                
                # Description
                html.P("Monitoritza i segueix els paràmetres del sistema públic d'aigua del municipi de Gualba", 
                       className='hero-description',
                       style={
                           'fontSize': '1.2rem', 
                           'marginBottom': '2rem', 
                           'textAlign': 'center',
                           'maxWidth': '800px',
                           'margin': '0 auto 2rem auto',
                           'color': 'white',
                           'textShadow': '1px 1px 2px rgba(0,0,0,0.7)'
                       }),
                
                # Buttons
                html.Div([
                    html.Button("Explora les dades", 
                               id="btn-browse",
                               className="hero-btn-primary",
                               style={
                                   'backgroundColor': '#e74c3c', 
                                   'color': 'white', 
                                   'border': 'none', 
                                   'padding': '12px 24px', 
                                   'borderRadius': '6px', 
                                   'fontSize': '1rem', 
                                   'cursor': 'pointer',
                                   'marginRight': '20px',
                                   'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'
                               }),
                    html.Button("Aporta noves dades", 
                               id="btn-submit",
                               className="hero-btn-secondary",
                               style={
                                   'backgroundColor': '#3498db', 
                                   'color': 'white', 
                                   'border': 'none', 
                                   'padding': '12px 24px', 
                                   'borderRadius': '6px', 
                                   'fontSize': '1rem', 
                                   'cursor': 'pointer',
                                   'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'
                               })
                ], className='hero-buttons', style={'textAlign': 'center'})
            ], className='hero-overlay', style={
                'position': 'absolute',
                'top': '0',
                'left': '50%',
                'transform': 'translateX(-50%)',
                'zIndex': '2',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'alignItems': 'center',
                'width': '100vw',
                'maxWidth': '1200px',
                'height': '500px',
                'borderRadius': '10px',
                'background': 'rgba(0,0,0,0.3)'  # Dark overlay for better text readability
            }),
            
            # Photo credit - positioned over the image
            html.Div([
                html.P("Foto: Rafael Aguilera Moyano", 
                       className='photo-credit',
                       style={
                           'fontSize': '0.8rem', 
                           'opacity': '0.8',
                           'textAlign': 'right',
                           'fontStyle': 'italic',
                           'color': 'white',
                           'textShadow': '1px 1px 2px rgba(0,0,0,0.7)',
                           'margin': '0',
                           'padding': '0 20px 10px 0'
                       })
            ], style={
                'position': 'absolute',
                'bottom': '0',
                'right': '0',
                'left': '0',
                'zIndex': '3',
                'maxWidth': '1200px',
                'width': '100vw',
                'margin': '0 auto',
                'transform': 'translateX(0)'
            })
        ], className='hero-section', style={
            'position': 'relative',
            'height': '500px',
            'marginBottom': '3rem'
        }),

        # Information Section
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Què monitoritgem?", style={
                        'color': '#2c3e50',
                        'fontSize': '1.8rem',
                        'marginBottom': '1rem',
                        'textAlign': 'center'
                    }),
                    html.P("Seguim els paràmetres clau de la qualitat de l'aigua per garantir un subministrament segur i de qualitat.", style={
                        'fontSize': '1rem',
                        'color': '#7f8c8d',
                        'textAlign': 'center',
                        'marginBottom': '1.5rem',
                        'lineHeight': '1.6'
                    }),
                    html.Ul([
                        html.Li("Nivell de pH."),
                        html.Li("Temperatura."),
                        html.Li("Controls de sabor, olor i color."),
                        html.Li("Conductivitat i terbolesa."),
                        html.Li("Paràmetres biològics."),
                        html.Li("Concentració de clor."),
                        html.Li("Concentració d'àcids haloacètics.")
                    ], style={
                        'fontSize': '0.95rem',
                        'color': '#34495e',
                        'lineHeight': '1.8',
                        'paddingLeft': '1.5rem'
                    })
                ], style={
                    'flex': '1',
                    'minWidth': '300px',
                    'padding': '2rem'
                }),
                
                html.Div([
                    html.H3("Com participar?", style={
                        'color': '#2c3e50',
                        'fontSize': '1.8rem',
                        'marginBottom': '1rem',
                        'textAlign': 'center'
                    }),
                    html.P("La participació ciutadana és clau per mantenir un control exhaustiu de la qualitat de l'aigua.", style={
                        'fontSize': '1rem',
                        'color': '#7f8c8d',
                        'textAlign': 'center',
                        'marginBottom': '1.5rem',
                        'lineHeight': '1.6'
                    }),
                    html.Ul([
                        html.Li("Consulta les últimes mostres d'aigua recollides."),
                        html.Li("Explora les dades històriques i les tendències de qualitat."),
                        html.Li("Comprova que els paràmetres compleixen els estàndards de seguretat."),
                        html.Li("Col·labora aportant noves mostres d'aigua."),
                        html.Li(["Reporta incidències o anomalies. ",
                                 html.Span("Pròximament", style={'color': '#e67e22', 'fontStyle': 'italic'})
                        ]),
                        html.Li(["Rep notificacions al teu correu electrònic. ",
                                 html.Span("Pròximament", style={'color': '#e67e22', 'fontStyle': 'italic'})
                        ])
                    ], style={
                        'fontSize': '0.95rem',
                        'color': '#34495e',
                        'lineHeight': '1.8',
                        'paddingLeft': '1.5rem'
                    })
                ], style={
                    'flex': '1',
                    'minWidth': '300px',
                    'padding': '2rem'
                })
            ], style={
                'display': 'flex',
                'gap': '2rem',
                'flexWrap': 'wrap',
                'maxWidth': '1000px',
                'margin': '0 auto',
                'padding': '0 2rem'
            }, className='info-section')
        ], style={
            'backgroundColor': 'white',
            'margin': '2rem auto',
            'borderRadius': '10px',
            'boxShadow': '0 4px 15px rgba(0,0,0,0.1)',
            'maxWidth': '1200px'
        }),

        # Live Data Section
        html.Div([
            html.H2("Consulta la darrera mostra", 
                   style={
                       'color': '#2c3e50', 
                       'fontSize': '2rem', 
                       'marginBottom': '1rem', 
                       'textAlign': 'center'
                   }),
            
            # Location selector
            html.Div([
                html.Label("Selecciona ubicació:", 
                          style={'fontWeight': 'bold', 'marginBottom': '0.5rem', 'display': 'block', 'color': '#495057'}),
                dcc.Dropdown(
                    id='home-location-selector',
                    placeholder='Carregant ubicacions...',
                    value=None,  # Will be set to first available location
                    style={'marginBottom': '1rem'}
                )
            ], style={
                'maxWidth': '400px',
                'margin': '0 auto 2rem auto',
                'padding': '0 2rem'
            }),
            
            dcc.Interval(id='interval-home', interval=30*1000, n_intervals=0),
            dcc.Store(id='current-sample-id', data=None),
            dcc.Store(id='selected-location', data=None),
            html.Div(id='live-parameters', style={
                'width': '100%', 
                'margin': '0 auto',
                'padding': '0 2rem',
                'boxSizing': 'border-box'
            })
        ], style={
            'backgroundColor': 'white', 
            'margin': '2rem auto', 
            'padding': '3rem 0', 
            'borderRadius': '10px', 
            'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 
            'maxWidth': '1200px'
        }),

        # Mailing List Subscription Section
        # TODO: Temporarily disabled - uncomment to reactivate
        
        # Active subscription form (commented out)
        # html.Div([
        #     html.Div([
        #         html.H2("Mantén-te informat", 
        #                style={
        #                    'color': '#2c3e50', 
        #                    'fontSize': '2rem', 
        #                    'marginBottom': '1rem', 
        #                    'textAlign': 'center'
        #                }),
        #         
        #         html.P([
        #             "Subscriu-te a la nostra llista de correu per rebre notificacions sobre noves mostres, ",
        #             "alertes de qualitat de l'aigua i actualitzacions del sistema de monitorització."
        #         ], style={
        #             'fontSize': '1.1rem', 
        #             'lineHeight': '1.6', 
        #             'color': '#34495e',
        #             'textAlign': 'center',
        #             'marginBottom': '2rem',
        #             'maxWidth': '600px',
        #             'margin': '0 auto 2rem auto'
        #         }),
        #         
        #         html.Div([
        #             html.Div([
        #                 dcc.Input(
        #                     id='email-input',
        #                     type='email',
        #                     placeholder='Introdueix el teu correu electrònic',
        #                     style={
        #                         'padding': '12px 16px',
        #                         'fontSize': '1rem',
        #                         'border': '2px solid #e0e0e0',
        #                         'borderRadius': '6px 0 0 6px',
        #                         'width': '300px',
        #                         'boxSizing': 'border-box',
        #                         'outline': 'none',
        #                         'transition': 'border-color 0.3s ease'
        #                     }
        #                 ),
        #                 html.Button(
        #                     "Subscriure's",
        #                     id='subscribe-btn',
        #                     className='btn-standard btn-subscribe',
        #                     style={
        #                         'backgroundColor': '#27ae60',
        #                         'color': 'white',
        #                         'border': 'none',
        #                         'padding': '12px 24px',
        #                         'borderRadius': '0 6px 6px 0',
        #                         'fontSize': '1rem',
        #                         'cursor': 'pointer',
        #                         'boxShadow': '0 4px 8px rgba(0,0,0,0.3)',
        #                         'transition': 'all 0.2s ease',
        #                         'marginLeft': '-1px'
        #                     }
        #                 )
        #             ], style={
        #                 'display': 'flex',
        #                 'justifyContent': 'center',
        #                 'marginBottom': '1rem'
        #             }),
        #             
        #             html.Div(id='subscription-status', style={
        #                 'textAlign': 'center',
        #                 'marginTop': '1rem',
        #                 'display': 'none'
        #             }),
        #             
        #             # Hidden store to track subscription state
        #             dcc.Store(id='subscription-state', data={'confirmed': False, 'email': ''}),
        #             
        #             html.P([
        #                 "✓ Notificacions de noves mostres",
        #                 html.Br(),
        #                 "✓ Alertes de qualitat de l'aigua",
        #                 html.Br(),
        #                 "✓ Informes mensuals de qualitat",
        #                 html.Br(),
        #                 "✓ Pots cancel·lar la subscripció en qualsevol moment"
        #             ], style={
        #                 'fontSize': '0.9rem',
        #                 'color': '#7f8c8d',
        #                 'textAlign': 'center',
        #                 'lineHeight': '1.8',
        #                 'marginTop': '1.5rem'
        #             })
        #         ])
        #     ], style={
        #         'maxWidth': '600px',
        #         'margin': '0 auto',
        #         'padding': '0 2rem'
        #     })
        # ], style={
        #     'backgroundColor': 'white', 
        #     'margin': '2rem auto', 
        #     'padding': '3rem 0', 
        #     'borderRadius': '10px', 
        #     'boxShadow': '0 4px 20px rgba(0,0,0,0.1)', 
        #     'maxWidth': '1200px',
        #     'width': '100vw'
        # }),
        
        # Temporary "Coming Soon" message (remove when reactivating subscription)
        html.Div([
            html.Div([
                html.H2("Mantén-te informat", 
                       style={
                           'color': '#2c3e50', 
                           'fontSize': '2rem', 
                           'marginBottom': '1rem', 
                           'textAlign': 'center'
                       }),
                
                html.P([
                    "La subscripció a la nostra llista de correu estarà disponible properament. ",
                    "Torneu aviat per rebre notificacions sobre noves mostres, alertes de qualitat de l'aigua ",
                    "i actualitzacions del sistema de monitorització."
                ], style={
                    'fontSize': '1.1rem', 
                    'lineHeight': '1.6', 
                    'color': '#34495e',
                    'textAlign': 'center',
                    'marginBottom': '2rem',
                    'maxWidth': '600px',
                    'margin': '0 auto 2rem auto'
                }),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-clock", style={
                            'fontSize': '3rem',
                            'color': '#f39c12',
                            'marginBottom': '1rem'
                        }),
                        html.H3("Funcionalitat en desenvolupament", style={
                            'color': '#f39c12',
                            'fontSize': '1.4rem',
                            'marginBottom': '1rem'
                        }),
                        html.P("Estem treballant per oferir-vos aquesta funcionalitat aviat.", style={
                            'color': '#7f8c8d',
                            'fontSize': '1rem'
                        })
                    ], style={
                        'textAlign': 'center',
                        'padding': '2rem',
                        'backgroundColor': '#fff9e6',
                        'border': '2px dashed #f39c12',
                        'borderRadius': '8px',
                        'maxWidth': '400px',
                        'margin': '0 auto'
                    }),
                    
                    html.P([
                        "✓ Notificacions de noves mostres",
                        html.Br(),
                        "✓ Alertes de qualitat de l'aigua",
                        html.Br(),
                        "✓ Informes mensuals de qualitat",
                        html.Br(),
                        "✓ Sistema fàcil de cancel·lació"
                    ], style={
                        'fontSize': '0.9rem',
                        'color': '#7f8c8d',
                        'textAlign': 'center',
                        'lineHeight': '1.8',
                        'marginTop': '1.5rem'
                    })
                ])
            ], style={
                'maxWidth': '600px',
                'margin': '0 auto',
                'padding': '0 2rem'
            })
        ], style={
            'backgroundColor': 'white', 
            'margin': '2rem auto', 
            'padding': '3rem 0', 
            'borderRadius': '10px', 
            'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 
            'maxWidth': '1200px'
        })
    ])