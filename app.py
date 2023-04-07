import dash
import dash_html_components as html
import dash_core_components as dcc
import json
from fitbit_connect import StreamData
import threading
import time, datetime

from dash import Dash, html
from fitbit_connect import StreamData, OAuth2Server

from canvas.sleep import *
from canvas.hr import *
from canvas.devices import *
from canvas.medication import *
from canvas.activity import *

from dash import Dash, html, dash_table, dcc, callback, Output, Input
from util import colors

def build_app():
    app = dash.Dash(__name__)

    app.layout = html.Div(
        style={'backgroundColor': colors['background'], 'color': colors['text']},
        children=[
        # header
        html.Div([
            html.H1(children='Hello {}!     '.format(stream.get_name(), style={
                    'color': colors['text'], 'display': 'inline-block',
                    # center the title
                   # 'margin': '0px 0px 0px 0px'
                    
                    
                    })),
            # insert a date picker with arrows to change the date
            dcc.DatePickerSingle(
                id='date-picker',
                min_date_allowed=datetime.date.fromisoformat(
                    '2021-01-01'),
                max_date_allowed=datetime.date.today(),
                initial_visible_month=datetime.date.today(),
                date=datetime.date.today(),
                display_format='MMM Do, YY',
                style={'width': '3in', 'height': '0.5in', 'display': 'inline-block',
                        'backgroundColor': colors['background'], 'color': colors['background'],
                        'borderColor': colors['background'],
                        'margin': '0px 0px 0px 0px'
                        },
            )], style={'display': 'flex', 'flex-direction': 'row'}),
        
        html.Div(className='row', children=[
            html.Div(className='col', children=[
                dcc.Markdown('''# Activity'''),
                display_hr_canvas(stream.get_hr( datetime.datetime.now())),
            ], style={'display': 'flex', 'flex-direction': 'column'}),
            # placeholder that takes up the rest of the free space
            html.Div(className='col', children=[
                display_sleep_canvas(stream.get_sleep(datetime.datetime.now())),
                display_list_devices(stream.get_devices()),
                display_medication(),
                display_activity(stream.get_activity_recent()),
            ], style={'display': 'flex', 'flex-direction': 'column'}),
        ], style={'display': 'flex', 'flex-direction': 'row'}),
        ])
    return app


# callbacks

@callback(
    Output('sleep-graph', 'figure'),
    [Input('date-picker', 'date')]
)
def update_sleep_graph(date):
    return sleep_graph(stream.get_sleep_canvas(datetime.datetime.fromisoformat(date)))

@callback(
    Output('hr-graph', 'figure'),
    [Input('date-picker', 'date')]
)
def update_hr_linplot(date):
    return hr_linplot(stream.get_hr_canvas(datetime.datetime.fromisoformat(date)))

@callback(
    Output('kcal-graph', 'figure'),
    [Input('date-picker', 'date')]
)
def update_hr_kcal(date):
    return hr_kcal(stream.get_hr_canvas(datetime.datetime.fromisoformat(date)))

@callback(
    Output('devices-list', 'children'),
    [Input('date-picker', 'date')]
)
def update_device_list(options):
    return devices_to_md(stream.get_devices())

if __name__=='__main__':
    # Authenticate with Fitbit
    # Start the app
        
    authentificate = 0
    keys = json.load(open('credentials/fitbit_keys_main.json'))
    if authentificate:
        print('Authenticating with Fitbit...')
        oauth_server = OAuth2Server(*keys.values())
        #dump tokens to file
        json.dump(oauth_server.get_tokens(), open('credentials/fitbit_tokens.json', 'w'))

    # Start the stream
    print('Starting stream...')
    stream = StreamData(*keys.values(),\
                        *json.load(open('credentials/fitbit_tokens.json')))
    
    app = build_app()
    app.run_server(host='127.0.0.1',
                   port=8030,
                   debug=True,
                   use_reloader = not authentificate,
                   )
    
    print('done')


