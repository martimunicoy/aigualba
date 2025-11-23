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
            html.H1("Exploració de dades", 
                   style={
                       'color': '#2c3e50', 
                       'fontSize': '2.5rem', 
                       'marginBottom': '2rem', 
                       'textAlign': 'center'
                   }),
            
            # Real-time data section
            html.Div([
                html.Div([
                    html.H3("Paràmetres en temps real", 
                           style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                    dcc.Interval(id='interval-browse', interval=10*1000, n_intervals=0),
                    html.Div(id='parameters-table', 
                            style={
                                'display': 'flex',
                                'justifyContent': 'center',
                                'alignItems': 'center',
                                'minHeight': '200px'
                            })
                ], style={
                    'backgroundColor': 'white', 
                    'margin': '1rem 0', 
                    'padding': '2rem', 
                    'borderRadius': '10px', 
                    'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
                }),
                
                # Visualization section
                html.Div([
                    html.H3("Visualització de dades", 
                           style={'color': '#2c3e50', 'marginBottom': '1.5rem', 'textAlign': 'center'}),
                    dcc.Graph(id='parameters-chart', style={'height': '400px'}) if HAS_PLOTLY else html.Div([
                        html.P("Gràfics no disponibles - Plotly no instal·lat", 
                              style={'textAlign': 'center', 'color': '#7f8c8d', 'fontStyle': 'italic'})
                    ])
                ], style={
                    'backgroundColor': 'white', 
                    'margin': '1rem 0', 
                    'padding': '2rem', 
                    'borderRadius': '10px', 
                    'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
                })
            ])
        ], style={
            'maxWidth': '1200px', 
            'margin': '0 auto', 
            'padding': '2rem'
        })
    ], style={'backgroundColor': '#f8f9fa', 'minHeight': '80vh'})