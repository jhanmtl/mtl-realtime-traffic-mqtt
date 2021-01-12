import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import layout_utils
import plotly.express as px
import plotly.graph_objects as go

import frontend_utils
import pandas as pd
import numpy as np
import json
from layout_utils import CustomBar

with open("./assets/bar_config.json", "r") as jfile:
    bconfig = json.load(jfile)

df = pd.read_csv("../data/detectors-active.csv")
map_fig, map_data = frontend_utils.init_map(df)
map_fig.update_layout(paper_bgcolor="gray", margin=dict(l=0, r=0, b=0, t=0))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
layout, left_column, right_column = layout_utils.init_layout()
right_column.get_subpanel_by_id('map-pane').children.figure = map_fig

stations = ["station {}".format(i + 1) for i in range(9)]
speed_values = np.random.randint(10, 40, len(stations))
count_values = np.random.randint(10, 40, len(stations))
gap_values = np.random.randint(10, 40, len(stations))

speed_card = left_column.get_subpanel_by_id("vspeed").children
speedbar = CustomBar(bconfig, "speed dectected", speed_card)
speedbar.set_data(speed_values, stations, "kmh")

count_card = left_column.get_subpanel_by_id("vcount").children
countbar = CustomBar(bconfig, "vehicles counted", count_card)
countbar.set_data(count_values, stations, "cars")

gap_card = left_column.get_subpanel_by_id("vgap").children
gapbar = CustomBar(bconfig, "gap time between vehicles", gap_card)
gapbar.set_data(gap_values, stations, "s")

summary={
    "station":(np.arange(len(stations))+1).tolist(),
    "speed (kmh)":speed_values,
    "count (cars)": count_values,
    "gap time (s)":gap_values
}

summary=pd.DataFrame.from_dict(summary)
summary["corner"]=df["corner_st2"]
summary=summary[["station","corner","speed (kmh)","count (cars)","gap time (s)"]]


# summary = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
# print(summary)
c=[{"name": i, "id": i} for i in summary.columns]
table=dash_table.DataTable(data=summary.to_dict('records'),
                           columns=c,
                           id="table",
                           style_cell={"background":"{}".format(bconfig["bgcolor"]),"textAlign":"center","border":"0"},
                           cell_selectable=False,
                            style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'left'
                                    } for c in ['corner']
                                ]
                           )

aux_card=left_column.get_subpanel_by_id("aux").children
cardheader = dbc.CardHeader("detector metrics overview ", style={"textAlign": "center",
                                                    "padding": "0px",
                                                    "border": "0px",
                                                    "color": bconfig['textcolor'],
                                                    "borderRadius": "0px"
                                                    })

aux_card.children=[cardheader,table]

app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
