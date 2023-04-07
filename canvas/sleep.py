import json
import datetime
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dash_table, dcc, callback, Output, Input
from util import colors

def display_sleep_canvas(sleep_data):

    # Get the summary data
    totalMinutesAsleep = sleep_data['summary']['totalMinutesAsleep']
    totalTimeInBed = sleep_data['summary']['totalTimeInBed']
    efficiency = sleep_data['sleep'][0]['efficiency']
    date = sleep_data['sleep'][0]['dateOfSleep']

    canvas = html.Div(
        className='col',
        title = 'Sleep',
        style={'font-weight': 'bold', 'color': colors['text']},
        children=[
            # Sleep graph
            html.H1('Sleep', style={'color': colors['text']}),
            dcc.Graph(
                id='sleep-graph',
                figure=sleep_graph(sleep_data),
                style={'width': '6in', 'height': '5in', 'display': 'inline-block', 'color': colors['background']},
            ),
        ]
        )


    return canvas


def sleep_graph(sleep_data):
    if 'stages' not in sleep_data['summary']:
        return go.Figure(data=[go.Bar(x=[0], y=[0])], layout=go.Layout(title='No sleep data for this day.', paper_bgcolor=colors['background'], plot_bgcolor=colors['background'], font=dict(color=colors['text'])))
    stages = sleep_data['summary']['stages']
    df = pd.DataFrame(stages, index=[0])/60
    fig = go.Figure(
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
                    # background color
                    marker_color=colors['text'],
                    # make the background black
                    # text color
                    textfont=dict(
                        color=colors['text']
                    )
                )
            ],
            layout=go.Layout(
                title='Sleep score: {}            Sleep duration: {}h'.format(sleep_data['sleep'][0]['efficiency'], round(sleep_data['summary']['totalMinutesAsleep']/60, 2)),
                # background color
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                # text color
                font=dict(color=colors['text']),
                xaxis=dict(
                    title='Time (hours)',
                    range=[0, max(5.03, max(df.values[0])+0.3)],
                    titlefont=dict(
                        size=20
                    ),
                    tickfont=dict(
                        size=18
                    ),
                ),
                yaxis=dict(
                    title='Stages',
                    titlefont=dict(
                        size=20
                    ),
                    tickfont=dict(
                        size=18
                    ),
                    automargin=True
                )
            )
        )


    return fig