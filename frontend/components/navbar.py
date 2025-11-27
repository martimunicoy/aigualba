from dash import html

def create_navbar():
    """Create the navigation bar component"""
    return html.Nav([
        html.Div([
            html.Div([
                html.A([
                    html.Img(src='/assets/images/logo2.png', 
                             alt='AiGua-lba Logo',
                             className='navbar-logo'),
                    html.Span([
                        html.Span("AiGua", style={'color': '#3498db'}),
                        "lba"
                    ], className='navbar-brand-text')
                ], href="/", className='navbar-brand-link'),
            ], className='navbar-brand-container'),
            html.Div([
                # Mobile menu button
                html.Button([
                    html.Span(className='hamburger-line'),
                    html.Span(className='hamburger-line'),
                    html.Span(className='hamburger-line')
                ], className='mobile-menu-toggle', id='mobile-menu-toggle'),
                
                # Navigation menu
                html.Ul([
                    html.Li([html.A("Explora les dades", href="/browse", id="nav-browse", 
                                   className='nav-link')]),
                    html.Li([html.A("Aporta noves dades", href="/submit", id="nav-submit", 
                                   className='nav-link')]),
                    html.Li([html.A("Qui som", href="/about", id="nav-about", 
                                   className='nav-link')]),
                ], className='nav-menu', id='nav-menu')
            ], className='navbar-nav')
        ], className='navbar-container')
    ], className='navbar')