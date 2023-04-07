import json
import datetime
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dash_table, dcc, callback, Output, Input
from util import colors


def display_medication():
    
    return html.Div([
        dcc.Checklist(
            options=[
                {'label': 'Xanax', 'value': 'item1'},
                {'label': 'Ozempic', 'value': 'item2'},
                {'label': 'Listerine', 'value': 'item3'}
            ],
            value=['item1', 'item2'])
    ])
