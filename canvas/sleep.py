import json
import datetime
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dash_table, dcc, callback, Output, Input

def display_sleep_canvas(sleep_data):

    # Get the summary data
    totalMinutesAsleep = sleep_data['summary']['totalMinutesAsleep']
    totalTimeInBed = sleep_data['summary']['totalTimeInBed']
    efficiency = sleep_data['sleep'][0]['efficiency']
    date = sleep_data['sleep'][0]['dateOfSleep']

    canvas = html.Div(
        className='col',
        children=[
            # Sleep graph
            dcc.Graph(
                id='sleep-graph',
                figure=sleep_graph(sleep_data),
                style={'width': '6in', 'height': '5in', 'display': 'inline-block'},
            ),
        ]
        )


    return canvas


def sleep_graph(sleep_data):
    stages = sleep_data['summary']['stages']
    if stages is None:
        return go.Figure(data=[go.Bar(x=[0], y=[0])], layout=go.Layout(title='No sleep data for this day.'))
    df = pd.DataFrame(stages, index=[0])/60
    return go.Figure(
            data=[
                go.Bar(
                    x=df.values[0],
                    y=df.columns,
                    orientation='h',
                    marker=dict(
                        color=['blue', 'orange',
                                'green', 'red']
                    ),
                    textposition='auto',
                )
            ],
            layout=go.Layout(
                title='Sleep Stages',
                xaxis=dict(
                    title='Time (hours)',
                    range=[0, max(5, max(df.values[0])+0.3)],
                ),
                yaxis=dict(
                    title='Stages',
                    titlefont=dict(
                        size=20
                    ),
                    tickfont=dict(
                        size=14
                    ),
                    automargin=True
                )
            )
        )
    
    
