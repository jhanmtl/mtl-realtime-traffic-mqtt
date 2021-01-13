import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

import json
import pandas as pd
import numpy as np
import os
import redis


class RedisDB:
    def __init__(self, host="localhost", port=6379, dbid=0):
        self.db = redis.Redis(host=host, port=port, db=dbid)
        self.keys = [k.decode() for k in self.db.keys()]
        self.readings = {}

    def _update(self):
        for k in self.keys:
            self.readings[k] = json.loads(self.db.get(k))

    def latest_reading(self, value_type):
        """

        :param value_type: one of the following strings 'vehicle-gap-time','vehicle-speed','vehicle-count','time'
        :return:
        """
        self._update()
        values = {}
        for detector_id in self.readings:
            values[detector_id] = self.readings[detector_id][value_type][-1]

        return values

    def n_latest_readings(self, value_type, n):
        self._update()
        values = {}
        for detector_id in self.readings:
            complete_readings = self.readings[detector_id][value_type]
            leng = len(complete_readings)
            if leng <= n:
                values[detector_id] = complete_readings
            else:
                values[detector_id] = complete_readings[leng - n:leng]

        return values


def init_map(df):
    curdir = os.path.dirname(__file__)
    basedir = os.path.abspath(os.path.join(curdir, os.pardir))
    creddir = os.path.join(basedir, "frontend/cred")

    with open(os.path.join(creddir, "mpbx.txt"), "r") as f:
        token = f.readline()

    with open("assets/mapdata.json", "r") as f:
        mdata = json.load(f)

    px.set_mapbox_access_token(token)

    init_lat = mdata["init-lat"]
    init_lon = mdata["init-lon"]
    bearing = mdata["bearing"]
    zoom = mdata["zoom"]
    style = mdata["style"]
    mcolor = mdata["marker-color"]
    msize = mdata["marker-size"]

    fig = px.scatter_mapbox(df,
                            lat="latitude",
                            lon="longitude",
                            center={'lat': init_lat, 'lon': init_lon},
                            zoom=zoom,
                            color='id',
                            mapbox_style=style
                            )
    fig.update_mapboxes(
        bearing=bearing,
    )

    fig.update_traces(marker=dict(size=msize,
                                  color=mcolor
                                  ))
    fig.update_layout(margin=dict(l=16, r=16, t=16, b=16))

    return fig, mdata
