import json
import datetime
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dash_table, dcc, callback, Output, Input
from util import colors
import plotly.express as px

def display_hr_canvas(intraday_hr):

    # Get the summary data
    restingHeartRate = intraday_hr['activities-heart'][0]['value']['restingHeartRate']
    freqDistribution = intraday_hr['activities-heart'][0]['value']['heartRateZones']

    if 'activities-heart-intraday' not in intraday_hr:
        return go.Figure(data=[go.Bar(x=[0], y=[0])], layout=go.Layout(title='No heart rate data for this day.', paper_bgcolor=colors['background'], plot_bgcolor=colors['background'], font=dict(color=colors['text'])))

    canvas = html.Div(
        className='col',
        title = 'Activity',
        style={'font-weight': 'bold', 'color': colors['text']},
        children = html.Div(
            children=[
                # Heart rate graph
                #html.H2('Heart Rate', style={'color': colors['text']}),
                dcc.Graph(
                    id='hr-graph',
                    figure=hr_linplot(intraday_hr),
                    style={'width': '6in', 'height': '5in',
                           'display': 'inline-block', 'color': colors['background']},
                ),
                #html.H2('Kcal Burned', style={'color': colors['text']}),
                dcc.Graph(
                    id='kcal-graph',
                    figure=hr_kcal(intraday_hr),
                    style={'width': '6in', 'height': '5in',
                           'display': 'inline-block', 'color': colors['background']},
                )],
            #style={'display': 'flex', 'flex-direction': 'column', 'color': colors['background']}
        ))

    return canvas



def hr_linplot(intraday_hr):
    if 'activities-heart-intraday' not in intraday_hr:
        return go.Figure(data=[go.Bar(x=[0], y=[0])], layout=go.Layout(title='No heart rate data for this day.', paper_bgcolor=colors['background'], plot_bgcolor=colors['background'], font=dict(color=colors['text'])))
    df = pd.DataFrame(intraday_hr['activities-heart-intraday']['dataset'])
    df['time'] = pd.to_datetime(df['time'])
    return go.Figure(
            data=[
                go.Scatter(
                    x=df['time'],
                    y=df['value'],
                    mode='lines',
                    marker=dict(
                        color=colors['text']
                    ),
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
                title='Resting heart rate: {}'.format(intraday_hr['activities-heart'][0]['value']['restingHeartRate']),
                # background color
                paper_bgcolor=colors['background'],
                # make the background black
                plot_bgcolor=colors['background'],
                # text color
                font=dict(
                    color=colors['text']
                ),
                xaxis=dict(
                    # text color
                    tickfont=dict(
                        color=colors['text']
                    )
                ),
                yaxis=dict(
                    # text color
                    tickfont=dict(
                        color=colors['text']
                    )
                )
            )
        )
    



def hr_kcal(intraday_hr):
    data = intraday_hr['activities-heart'][0]['value']['heartRateZones']
    df = pd.DataFrame(data).astype({'caloriesOut': 'int32'})
    df.loc[0,'name'] = 'Resting'
    return go.Figure(
            data=[
                # make a piechart with the data
                go.Pie(
                    labels=df['name'],
                    values=df['caloriesOut'],    
                    textinfo='value',  
                    texttemplate='%{label}: %{value} kcal',
                    textfont=dict(
                        color=colors['text'],
                        size=18,
                    ),
                    # amke the legend bigger
                ),               
            ],
            layout=go.Layout(
                title='Total calories burned: {} kcal'.format(df['caloriesOut'].sum()),
                # background color
                paper_bgcolor=colors['background'],
                # make the background black
                plot_bgcolor=colors['background'],
                # text color
                font=dict(
                    color=colors['text']
                ),
                xaxis=dict(
                    # text color
                    tickfont=dict(
                        color=colors['text']

                    )

                ),
                yaxis=dict(
                    # text color
                    tickfont=dict(
                        color=colors['text']
                    )
                )
            )
        )
     
    
    