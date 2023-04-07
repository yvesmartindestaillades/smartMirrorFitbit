import json
import datetime
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dash_table, dcc, callback, Output, Input
from util import colors

def display_list_devices(devices_data):
    # Get the summary data
    canvas = html.Div(
        title='Devices',
        className='col',
        children=[
             dcc.Markdown(
                    children= devices_to_md(devices_data),
                    id='devices-list'
                ),
        ]
    )

    return canvas


def devices_to_md(devices):
    return '# Devices\n\n' +'\n\n'.join(['## {} \n\nType: {}\nBattery: {}\n\nLast Sync: {}\n\n'.format(device['deviceVersion'], device['type'], device['battery'], device['lastSyncTime']) for device in devices])
