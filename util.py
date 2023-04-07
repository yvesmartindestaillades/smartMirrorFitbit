
import datetime

colors = {
    'background': '#111111',
    'text': '#FFFFFF'
}

# a function returns the time 24h ago
def last24h_interval(date = datetime.datetime.now()):
    start_date = date - datetime.timedelta(days=1)
    end_date = date
    start_time = start_date.strftime('%H:%M')
    end_time = end_date.strftime('%H:%M')
    return {'start_date': start_date, 'end_date': end_date, 'start_time': start_time, 'end_time': end_time}



