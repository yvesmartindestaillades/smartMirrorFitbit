import json
import datetime
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dash_table, dcc, callback, Output, Input
from util import colors


def display_medication():

    return html.Div([
        html.H1('Medication', style={'color': colors['text']}),
        dcc.Checklist(
            options=['vitamin C', 'creatin', 'ashwaganda', 'collagen', 'proteins'],
            value=[],
            id='medication-list',
            ),
        html.Div(id='medication-output')
    ])
