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


class Detector:
    def __init__(self, det_id, db):
        self.det_id = det_id
        self.db = db

        data = json.loads(db.get(self.det_id))
        self.vspeed = data['vehicle-speed']
        self.vtime = data['vehicle-gap-time']
        self.vcount = data['vehicle-count']
        self.utf = data['time']

    def get_id(self):
        return self.det_id

    def get_utf(self):
        return self.utf

    def get_latest_speed(self):
        return self.vspeed[-1]

    def get_latest_count(self):
        return self.vcount[-1]

    def get_latest_gaptime(self):
        return self.vtime[-1]


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
                            style=style
                            )
    fig.update_mapboxes(
        bearing=bearing,
    )

    fig.update_traces(marker=dict(size=msize,
                                  color=mcolor
                                  ))
    fig.update_layout(margin=dict(l=16, r=16, t=16, b=16))

    return fig, mdata
