import json
import redis
import pytz
import datetime
import numpy as np
import pandas as pd

def generate_table_data(df, speed_values,count_values,gap_values):
    stations=['station {}'.format(i) for i in range(len(speed_values))]
    table_data = {
        "station": (np.arange(len(stations)) + 1).tolist(),
        "speed (kmh)": speed_values,
        "count (cars)": count_values,
        "gap time (s)": gap_values
    }

    table_data = pd.DataFrame.from_dict(table_data)
    table_data["corner"] = df["corner_st2"]
    table_data = table_data[["station", "corner", "speed (kmh)", "count (cars)", "gap time (s)"]]
    return table_data

def date_convert(utc_time_str, target_tz="America/New_York"):
    [date, time] = utc_time_str.split("T")

    date = [int(i) for i in date.split("-")]
    year = date[0]
    month = date[1]
    day = date[2]

    time = [int(i) for i in time.split(":")]
    hour = time[0]
    minute = time[1]
    second = time[2]

    utc_time = datetime.datetime(year, month, day, hour, minute, second)
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    converted = utc_time.astimezone(pytz.timezone(target_tz))

    return converted


class RedisDB:
    def __init__(self, host="localhost", port=6379, dbid=0):
        self.db = redis.Redis(host=host, port=port, db=dbid)
        self.keys = [k.decode() for k in self.db.keys()]
        self.keys.sort()
        self.readings = {}

    def _update(self):
        for k in self.keys:
            self.readings[k] = json.loads(self.db.get(k))

    def latest_readings(self, value_type):
        self._update()
        values = []

        for k in self.keys:
            values.append(self.readings[k][value_type][-1])

        return values

    def n_latest_readings(self, value_type, n):
        self._update()
        values = []
        for k in self.keys:
            complete_readings = self.readings[k][value_type]
            leng = len(complete_readings)
            if leng <= n:
                subreadings = complete_readings
            else:
                subreadings = complete_readings[leng - n:leng]

            values.append(subreadings)

        return values

    def get_earliest_timestamp(self):
        self._update()
        k=self.keys[0]
        ts=self.readings[k]['time'][0]
        return ts




