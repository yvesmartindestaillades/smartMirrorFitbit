import json
import pandas as pd
import plotly.express as px


def display_sleep_data(sleep_data):

    if sleep_data['sleep'] == []:
        print('No sleep data for this day.')
        return
    # Get the summary data
    stages = sleep_data['summary']['stages']
    totalMinutesAsleep = sleep_data['summary']['totalMinutesAsleep']
    totalTimeInBed = sleep_data['summary']['totalTimeInBed']
    efficiency = sleep_data['sleep'][0]['efficiency']
    date = sleep_data['sleep'][0]['dateOfSleep']
    
    # Get the data per minute
    data_per_minute = pd.DataFrame(sleep_data['sleep'][0]['minuteData'])
    px.line(data_per_minute, x='dateTime', y='value').show()
    
if __name__=='__main__':
    display_sleep_data(json.load(open('sleep.json')))