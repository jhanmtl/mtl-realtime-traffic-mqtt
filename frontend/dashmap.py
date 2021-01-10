import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import redis

import json
import pandas as pd
import numpy as np
import os

import frontend_utils

det_ids=['00777', '00970', '00971', '00974', '00774', '00969', '00773', '00966', '00937']
db=redis.Redis()
detectors=[frontend_utils.Detector(each_id,db) for each_id in det_ids]
latest_speed=[i.get_latest_speed() for i in detectors]
latest_count=[i.get_latest_count() for i in detectors]
latest_gaptime=[i.get_latest_gaptime() for i in detectors]
latest_time=[i.get_utf() for i in detectors]

latest_df=pd.DataFrame()
latest_df['speed']=latest_speed
latest_df['count']=latest_count
latest_df['gaptime']=latest_gaptime
latest_df['utf']=latest_time
latest_df['id']=det_ids

df=pd.read_csv("../data/detectors-active.csv")
map, mapdata=frontend_utils.init_map(df)


app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div(
        dcc.Graph(
            figure=map,
            id='map',
            config={'displayModeBar': False, 'scrollZoom': True},
            style={'height': '100vh', 'width': '100%'}
        )
    )
], style={"height": "100vh"})

if __name__ == "__main__":
    app.run_server(port=8080, debug=True)
