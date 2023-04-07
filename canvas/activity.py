import json
import datetime
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dash_table, dcc, callback, Output, Input
from util import colors


[
  {
    "activityId": 90013,
    "calories": -1,
    "description": "Walking less than 2 mph, strolling very slowly",
    "distance": 1.61,
    "duration": 1178000,
    "name": "Walk"
  },
  {
    "activityId": 1071,
    "calories": 0,
    "description": "",
    "distance": 0,
    "duration": 973000,
    "name": "Outdoor Bike"
  }
]
      

def display_activity(activity_data):
    # Get the summary data
    canvas = html.Div(
        className='col',
        children=[
             dcc.Markdown(
                    children= activities_to_md(activity_data),
                    id='activity-list'
                ),
        ]
    )

    return canvas


def activities_to_md(activity_data):
    return '# Your last moves\n\n' +'\n\n'.join(['## {} \n\nType: {}\nCalories: {}\n\nDuration: {}\n\n'.format(activity['name'], activity['description'], activity['calories'], activity['duration']) for activity in activity_data])