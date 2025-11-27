from dash import html, dcc
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def create_browse_page():
    """Create the browse data page layout"""
    return html.Div([
        html.Div([
            html.H1("Mostres d'aigua", 
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
                    html.Li("Navega per totes les mostres d'aigua recollides"),
                    html.Li("Fes clic a 'Veure detalls' per veure la informació completa de cada mostra"),
                    html.Li("Les mostres es mostren ordenades per data de recollida"),
                    html.Li("Utilitza els filtres per trobar mostres específiques")
                ], style={'fontSize': '1rem', 'lineHeight': '1.6', 'color': '#34495e'})
            ], style={
                'backgroundColor': 'white', 
                'margin': '1rem 0', 
                'padding': '2rem', 
                'borderRadius': '10px', 
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),

            # Filters section
            html.Div([
                html.H3("Filtres", 
                       style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                
                html.Div([
                    # Date filter
                    html.Div([
                        html.Label("Filtrar per data:", 
                                 style={'fontWeight': 'bold', 'marginBottom': '0.5rem', 'display': 'block', 'color': '#495057'}),
                        html.Div([
                            html.Label("Des de:", style={'fontSize': '0.9rem', 'color': '#6c757d', 'marginRight': '0.5rem'}),
                            dcc.DatePickerSingle(
                                id='date-filter-from',
                                placeholder='Selecciona data inicial',
                                display_format='DD/MM/YYYY',
                                style={'marginRight': '1rem'}
                            ),
                        ], style={'display': 'inline-block', 'marginRight': '2rem'}),
                        
                        html.Div([
                            html.Label("Fins a:", style={'fontSize': '0.9rem', 'color': '#6c757d', 'marginRight': '0.5rem'}),
                            dcc.DatePickerSingle(
                                id='date-filter-to',
                                placeholder='Selecciona data final',
                                display_format='DD/MM/YYYY'
                            ),
                        ], style={'display': 'inline-block'}),
                    ], style={'marginBottom': '1rem'}),
                    
                    # Location filter
                    html.Div([
                        html.Label("Filtrar per ubicació:", 
                                 style={'fontWeight': 'bold', 'marginBottom': '0.5rem', 'display': 'block', 'color': '#495057'}),
                        dcc.Dropdown(
                            id='location-filter',
                            placeholder='Selecciona una ubicació...',
                            style={'width': '100%', 'marginBottom': '1rem'}
                        ),
                    ], style={'marginBottom': '1rem'}),
                    
                    # Clear filters button
                    html.Div([
                        html.Button(
                            "Netejar filtres",
                            id='clear-filters-btn',
                            style={
                                'backgroundColor': '#6c757d',
                                'color': 'white',
                                'border': 'none',
                                'padding': '0.5rem 1rem',
                                'borderRadius': '4px',
                                'cursor': 'pointer',
                                'fontSize': '0.9rem'
                            }
                        )
                    ], style={'textAlign': 'center'})
                    
                ], style={'display': 'flex', 'flexDirection': 'column', 'gap': '1rem'})
                
            ], style={
                'backgroundColor': 'white',
                'margin': '1rem 0',
                'padding': '2rem',
                'borderRadius': '10px',
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),
            
            # Samples table section
            html.Div([
                html.Div([
                    html.H3("Llista de mostres", 
                           style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                    dcc.Interval(id='interval-browse', interval=30*1000, n_intervals=0),
                    # Hidden stores for table state
                    dcc.Store(id='table-current-page', data=1),
                    dcc.Store(id='table-page-size', data=10),
                    dcc.Store(id='table-sort-column', data='data'),
                    dcc.Store(id='table-sort-order', data='desc'),
                    # Hidden stores for filter state
                    dcc.Store(id='filtered-samples', data=[]),
                    html.Div(id='samples-table', 
                            style={
                                'minHeight': '200px'
                            })
                ], style={
                    'backgroundColor': 'white', 
                    'margin': '1rem 0', 
                    'padding': '2rem', 
                    'borderRadius': '10px', 
                    'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
                }),
                
                # Data visualizations section
                html.Div(id='data-visualizations', style={'marginBottom': '2rem'})
                
            ])
        ], style={
            'maxWidth': '1200px', 
            'margin': '0 auto', 
            'padding': '2rem'
        })
    ], style={'backgroundColor': '#f8f9fa', 'minHeight': '80vh'})