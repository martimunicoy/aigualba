from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

def create_visualize_page():
    """Create the data visualization page layout"""
    return html.Div([
        html.Div([
            html.H1("Visualitza les mostres", 
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
                    html.Li("Selecciona el paràmetre que vols visualitzar des del menú desplegable"),
                    html.Li("Escull el punt de mostreig per filtrar les dades"),
                    html.Li("Veu l'evolució temporal del paràmetre seleccionat"),
                    html.Li("Interactua amb el gràfic per fer zoom, veure valors específics i més")
                ], style={'fontSize': '1rem', 'lineHeight': '1.6', 'color': '#34495e'})
            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),

            # Controls section
            html.Div([
                html.H3("Controls", 
                       style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                
                html.Div([
                    # Parameter selector
                    html.Div([
                        html.Label("Selecciona el paràmetre:", 
                                 style={'fontWeight': 'bold', 'marginBottom': '0.5rem', 'display': 'block', 'color': '#495057'}),
                        dcc.Dropdown(
                            id='parameter-selector',
                            options=[
                                {'label': 'pH', 'value': 'ph'},
                                {'label': 'Temperatura (°C)', 'value': 'temperatura'},
                                {'label': 'Conductivitat 20°C (μS/cm)', 'value': 'conductivitat_20c'},
                                {'label': 'Terbolesa (UNF)', 'value': 'terbolesa'},
                                {'label': 'Color (mg/L Pt-Co)', 'value': 'color'},
                                {'label': 'Olor (índex dilució 25°C)', 'value': 'olor'},
                                {'label': 'Sabor (índex dilució 25°C)', 'value': 'sabor'},
                                {'label': 'Clor lliure (mg/L)', 'value': 'clor_lliure'},
                                {'label': 'Clor total (mg/L)', 'value': 'clor_total'},
                                {'label': 'Clor combinat residual (mg/L)', 'value': 'clor_combinat_residual'},
                                {'label': 'E. coli (NPM/100mL)', 'value': 'recompte_escherichia_coli'},
                                {'label': 'Enterococs (NPM/100mL)', 'value': 'recompte_enterococ'},
                                {'label': 'Microorganismes aerobis 22°C (UFC/1mL)', 'value': 'recompte_microorganismes_aerobis_22c'},
                                {'label': 'Coliformes totals (NMP/100mL)', 'value': 'recompte_coliformes_totals'},
                                {'label': 'Àcid monocloroacètic (μg/L)', 'value': 'acid_monocloroacetic'},
                                {'label': 'Àcid dicloroacètic (μg/L)', 'value': 'acid_dicloroacetic'},
                                {'label': 'Àcid tricloroacètic (μg/L)', 'value': 'acid_tricloroacetic'},
                                {'label': 'Àcid monobromoacètic (μg/L)', 'value': 'acid_monobromoacetic'},
                                {'label': 'Àcid dibromoacètic (μg/L)', 'value': 'acid_dibromoacetic'},
                                {'label': 'Suma 5 haloacètics (μg/L)', 'value': 'suma_haloacetics'}
                            ],
                            value=None,
                            placeholder="Selecciona un paràmetre...",
                            style={'fontSize': '1rem'}
                        )
                    ], className='visualize-control-item', style={'flex': '1', 'marginRight': '1rem'}),
                    
                    # Location selector
                    html.Div([
                        html.Label("Punt de mostreig:", 
                                 style={'fontWeight': 'bold', 'marginBottom': '0.5rem', 'display': 'block', 'color': '#495057'}),
                        dcc.Dropdown(
                            id='location-selector',
                            value='all',
                            placeholder="Selecciona un punt de mostreig...",
                            style={'fontSize': '1rem'}
                        )
                    ], className='visualize-control-item', style={'flex': '1'})
                ], className='visualize-controls-flex', style={'display': 'flex', 'gap': '1rem', 'marginBottom': '1rem'})
            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),

            # Chart section
            html.Div([
                html.H3(id="chart-title", 
                       style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                
                # Loading component
                dcc.Loading(
                    id="loading-chart",
                    children=[
                        dcc.Graph(
                            id='time-series-chart',
                            config={
                                'displayModeBar': True,
                                'displaylogo': False,
                                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
                            },
                            style={'height': '500px'}
                        )
                    ],
                    type="default"
                ),
                
                # Chart info
                html.Div(id="chart-info", style={'marginTop': '1rem'})
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

def get_parameter_label(parameter_key):
    """Get the human-readable label for a parameter"""
    parameter_labels = {
        'ph': 'pH',
        'temperatura': 'Temperatura (°C)',
        'conductivitat_20c': 'Conductivitat 20°C (μS/cm)',
        'terbolesa': 'Terbolesa (UNF)',
        'color': 'Color (mg/L Pt-Co)',
        'olor': 'Olor (índex dilució 25°C)',
        'sabor': 'Sabor (índex dilució 25°C)',
        'clor_lliure': 'Clor lliure (mg/L)',
        'clor_total': 'Clor total (mg/L)',
        'recompte_escherichia_coli': 'E. coli (NPM/100mL)',
        'recompte_enterococ': 'Enterococs (NPM/100mL)',
        'recompte_microorganismes_aerobis_22c': 'Microorganismes aerobis 22°C (UFC/1mL)',
        'recompte_coliformes_totals': 'Coliformes totals (NMP/100mL)',
        'acid_monocloroacetic': 'Àcid monocloroacètic (μg/L)',
        'acid_dicloroacetic': 'Àcid dicloroacètic (μg/L)',
        'acid_tricloroacetic': 'Àcid tricloroacètic (μg/L)',
        'acid_monobromoacetic': 'Àcid monobromoacètic (μg/L)',
        'acid_dibromoacetic': 'Àcid dibromoacètic (μg/L)',
        'suma_haloacetics': 'Suma 5 haloacètics (μg/L)',
        'clor_combinat_residual': 'Clor combinat residual (mg/L)'
    }
    return parameter_labels.get(parameter_key, parameter_key)