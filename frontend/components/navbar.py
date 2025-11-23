from dash import html

def create_navbar():
    """Create the navigation bar component"""
    return html.Nav([
        html.Div([
            html.Div([
                html.A("AiGualba", href="/", 
                       style={
                           'color': '#ecf0f1', 
                           'fontSize': '1.5rem', 
                           'fontWeight': 'bold', 
                           'textDecoration': 'none'
                       }),
            ]),
            html.Div([
                html.Ul([
                    html.Li([html.A("Explora les dades", href="/browse", id="nav-browse", 
                                   style={
                                       'color': '#ecf0f1', 
                                       'textDecoration': 'none', 
                                       'fontWeight': '500',
                                       'padding': '0.5rem 1rem',
                                       'borderRadius': '4px',
                                       'transition': 'background-color 0.3s'
                                   })]),
                    html.Li([html.A("Aporta noves dades", href="/submit", id="nav-submit", 
                                   style={
                                       'color': '#ecf0f1', 
                                       'textDecoration': 'none', 
                                       'fontWeight': '500',
                                       'padding': '0.5rem 1rem',
                                       'borderRadius': '4px',
                                       'transition': 'background-color 0.3s'
                                   })]),
                    html.Li([html.A("Qui som", href="/about", id="nav-about", 
                                   style={
                                       'color': '#ecf0f1', 
                                       'textDecoration': 'none', 
                                       'fontWeight': '500',
                                       'padding': '0.5rem 1rem',
                                       'borderRadius': '4px',
                                       'transition': 'background-color 0.3s'
                                   })]),
                ], style={
                    'listStyle': 'none', 
                    'display': 'flex', 
                    'margin': '0', 
                    'padding': '0', 
                    'gap': '1rem'
                })
            ])
        ], style={
            'maxWidth': '1200px', 
            'margin': '0 auto', 
            'display': 'flex', 
            'justifyContent': 'space-between', 
            'alignItems': 'center', 
            'padding': '0 2rem'
        })
    ], style={
        'backgroundColor': '#2c3e50', 
        'padding': '1rem 0', 
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'position': 'sticky',
        'top': '0',
        'zIndex': '1000'
    })