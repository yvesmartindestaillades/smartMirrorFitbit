from get_sleep import StreamData
from display import display_sleep_data
import time
import json
import datetime

if __name__ == '__main__':
    client_id, client_secret = json.load(open('fitbit_keys.json')).values()
    stream_data = StreamData(client_id, client_secret)
    for i in range(1,30):
        sleep_data = stream_data.get_sleep(datetime.date(2023, 3, i))
        display_sleep_data(sleep_data)
        time.sleep(1) # 150 requests per hour max (fitbit API limit)
        