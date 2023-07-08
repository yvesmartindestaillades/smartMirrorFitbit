import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import json
import threading
import time, datetime

from dash import Dash, html

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from canvas.sleep import *
from canvas.hr import *
from canvas.devices import *
from canvas.medication import *
from canvas.activity import *
from canvas.survey import *
from fitbit_connect import *
from firebase import *
from facial_recognition import FacialRecognition
from threading import Thread 
from server import Server
from scheduler import Scheduler

from dash import Dash, html, dash_table, dcc, callback, Output, Input
from util import colors

def build_app(stream, server):
    app = dash.Dash(server = server)

    app.layout = html.Div(
        style={'backgroundColor': colors['background'], 'color': colors['text']},
        children=[
        # header
        
        html.Div([
            html.P(id='placeholder1'),
            html.P(id='placeholder2'),
            html.P(id='placeholder3'),
            html.P(id='placeholder4'),
            html.P(id='placeholder5'),
            html.P(id='placeholder6'),
            html.P(id='placeholder7'),
            html.P(id='placeholder8'),
            #html.H1(children='Hello {}!     '.format(stream.get_name(), style={'color': colors['text'], 'display': 'inline-block',})),
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
                display_hr_canvas(stream.get_hr_canvas( datetime.datetime.now())),
            ], style={'display': 'flex', 'flex-direction': 'column'}),
            # placeholder that takes up the rest of the free space
            html.Div(className='col', children=[
                display_sleep_canvas(stream.get_sleep_canvas(datetime.datetime.now())),
                display_list_devices(stream.get_devices_canvas()),
                display_medication(),
               # display_activity(stream.get_activity_recent()),
                html.H1("Over the last 2 weeks, how often have you been bothered by the following problems?", style={'color': colors['text']}),
               display_depression_question('depression-question-1', 'Little interest or pleasure in doing things'),
                display_depression_question('depression-question-2', 'Feeling down, depressed, or hopeless'),
            ], style={'display': 'flex', 'flex-direction': 'column'}),
        ], style={'display': 'flex', 'flex-direction': 'row'}),
        ])

    # register callbacks
    register_callbacks(app, stream)

    return app


# callbacks
def register_callbacks(dashapp, stream):

    @dashapp.callback(
        Output('sleep-graph', 'figure'),
        [Input('date-picker', 'date')]
    )
    def update_sleep_graph(date):
        data= stream.get_sleep_canvas(datetime.datetime.fromisoformat(date))
        firebase.set(data, 'sleep', date)
        return sleep_graph(data)

    @dashapp.callback(
        Output('hr-graph', 'figure'),
        [Input('date-picker', 'date')]
    )
    def update_hr_linplot(date):
        data= stream.get_hr_canvas(datetime.datetime.fromisoformat(date))
        firebase.set(data, 'hr', date)
        return hr_linplot(data)

    @dashapp.callback(
        Output('kcal-graph', 'figure'),
        [Input('date-picker', 'date')]
    )
    def update_hr_kcal(date):
        data = stream.get_hr_canvas(datetime.datetime.fromisoformat(date))
        firebase.set(data, 'hr', date)
        return hr_kcal(data)

    @dashapp.callback(
        Output('devices-list', 'children'),
        [Input('date-picker', 'date')]
    )
    def update_device_list(options):
        data = stream.get_devices_canvas()
        firebase.set(data, 'devices')
        return devices_to_md(data)

    @dashapp.callback(
        [Output('medication-list', 'value'), Output('medication-list', 'options')],
        [Input('date-picker', 'date')]
    )
    def read_medication_list(date):
        options = firebase.read('medication/options', date) if firebase.exists('medication/options', date) else ['vitamin C', 'creatin', 'ashwaganda', 'collagen', 'proteins']
        value = firebase.read('medication/value', date) if firebase.exists('medication/value', date) else []
        return value, options

    @dashapp.callback(
        Output('placeholder3', 'n_clicks'), 
        [Input('medication-list', 'value')],
        [dash.dependencies.State('date-picker', 'date'), dash.dependencies.State('medication-list', 'options')])
    def push_medication(value, date, options):
        firebase.set(options, 'medication/options', date)
        firebase.set(value, 'medication/value', date)
        return 1
    
    @dashapp.callback(
        Output('placeholder7', 'n_clicks'),
        [Input('depression-question-1', 'value'), Input('depression-question-2', 'value')],
        [dash.dependencies.State('date-picker', 'date')])
    def push_depression(value1, value2, date):
        firebase.set(value1, 'depression_1', date)
        firebase.set(value2, 'depression_2', date)
        return 1
    
    @dashapp.callback(
        [Output('depression-question-1', 'value'), Output('depression-question-2', 'value')],
        [Input('date-picker', 'date')])
    def pull_depression(date):
        data1 = firebase.read('depression_1', date) if firebase.exists('depression_1', date) else 0
        data2 = firebase.read('depression_2', date) if firebase.exists('depression_2', date) else 0
        return data1, data2
       

if __name__=='__main__':
    # Authenticate with Fitbit
    # Start the app

    authentificate = 0
    keys = json.load(open('credentials/yves_martin/fitbit_keys.json'))
    if authentificate:
        print('Authenticating with Fitbit...')
        oauth_server = OAuth2Server(*keys.values())
        #dump tokens to file
        json.dump(oauth_server.get_tokens(), open('credentials/yves_martin/fitbit_tokens.json', 'w'))

    # Start the stream
    print('Starting stream...')
    stream = StreamData(*keys.values(),\
                        *json.load(open('credentials/yves_martin/fitbit_tokens.json')))
    
    face_rec = FacialRecognition()
    
    server = Server()
    scheduler = Scheduler(server)
    
    app = build_app(
            stream=stream,
            server=server,
        )
    
    @scheduler.task('interval', id='update_data', seconds=2)
    def facial_rec_job(app=app, facial_rec=face_rec):
        facial_rec.run()
        # if facial_rec.user_switched and facial_rec.user is not None:
        #     firebase.user = facial_rec.user
            # p = os.path.join(os.abspath(os.path.dirname(__file__)), 'credentials', firebase.user)
            # keys = json.load(open(join(p, 'fitbit_keys.json')))
            # oauth_server = OAuth2Server(*keys.values())
            # json.dump(oauth_server.get_tokens(), open('credentials/fitbit_tokens.json', 'w'))
            # stream.__init__(*keys.values(), *json.load(open('credentials/fitbit_tokens.json')))
    
    
  
    app.run_server(host='127.0.0.1',
                port=8030,
                debug=True,
                )

    print('done')


