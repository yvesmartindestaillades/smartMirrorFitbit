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

from dash import Dash, html, dash_table, dcc, callback, Output, Input


def build_app():
    app = dash.Dash(__name__)

    app.layout = html.Div(children=[
        # title + date picker
        html.Div([
            html.H1(children='Hello {}!'.format(stream.get_name())),
            # insert a date picker with arrows to change the date
            dcc.DatePickerSingle(
                id='date-picker',
                min_date_allowed=datetime.date.fromisoformat('2021-01-01'),
                max_date_allowed=datetime.date.today(),
                initial_visible_month=datetime.date.today(),
                date=datetime.date.today(),
                display_format='MMM Do, YYYY',
                style={'width': '3in', 'height': '1in', 'display': 'inline-block'},
            )]),
        
        # first row
        html.Div(
            className='row', 
            children=[
                display_sleep_canvas(stream.get_sleep(datetime.datetime.now())),
            ]),
    ])
    return app


# callbacks

@callback(
    Output('sleep-graph', 'figure'),
    [Input('date-picker', 'date')
     ]
)
def update_app_data(date):
    return sleep_graph(stream.get_sleep(datetime.datetime.fromisoformat(date)))



if __name__=='__main__':
    # Authenticate with Fitbit
    # Start the app
        
    authentificate = 0
    if authentificate:
        print('Authenticating with Fitbit...')
        oauth_server = OAuth2Server(*json.load(open('credentials/fitbit_keys.json')).values())
        #dump tokens to file
        json.dump(oauth_server.get_tokens(), open('credentials/fitbit_tokens.json', 'w'))

    # Start the stream
    print('Starting stream...')
    stream = StreamData(*json.load(open('credentials/fitbit_keys.json')).values(),\
                        *json.load(open('credentials/fitbit_tokens.json')))
    
    app = build_app()
    app.run_server(host='127.0.0.1',
                   port=8040,
                   debug=True,
                   use_reloader = not authentificate,
                   )
    
    print('done')


