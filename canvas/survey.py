import json
import datetime
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dash_table, dcc, callback, Output, Input
from util import colors

    
    
    
def display_depression_question(id, question):
    
    return html.Div([
        html.H2(question, style={'color': colors['text']}),
        dcc.Slider(
            id=id,
            min=0,
            max=3,
            step=1,
            value=0,
            marks={
                0: 'Not at all',
                1: 'Several days',
                2: 'More than half the days',
                3: 'Nearly every day'
            }
        ),
        html.Div(id=id+'-output')
    ])
