""" Montreal Realtime Traffic Dashboard
This project performs realtime IoT data fetching and visualization from 9 thermal and radar sensors embedded along Rue
Notre-Dame by the City of Montreal for its Open Data initiative. Data details here
(https://donnees.montreal.ca/ville-de-montreal/circulation-mobilite-temps-reel).
Each sensor publishes traffic data regarding vehicle speed, count, and gaptime in 60 second intervals over the mqtt
protocol.

This dashboard pulls its data on each sensor from a locally running redis database, onto which a separate python script
continually records each sensor's new readings at the 60 second intervals that the mqtt message is published by each
sensor. The update frequency of this dashboard is therefore set to be 600ms longer than
that to ensure complete updates. A ~1 second interval for visualizing countdown to next update is also present.

Main information conveyed are the current vehicle speed, count, and gaptime at each dectector location. Historic reading
over 24hrs for each detector is also available in scatter plot form, along with option to compare against a second
detector and the option for switching between reading types.

A bonus feature, not related to mqtt data, is the ability to access live traffic cam feed at the location
of the detectors. Note that these camera feeds update at ~5 minute intervals.

As for Dash:
Certain graphic elements are improved by using dash-bootstrap-components. The staggered layout is implemented with
nested rows and columns based on bootstrap grids.

Native dash core components for plotting such as Scatter and Bar are reassgined to wrapper classes in
../src/layout_utils.py to place the plotting and data update logic in one entity. In most cases it makes the callback
managment for updating the plots much easier. Though whether it is a necessary practice is still tbd.

To run this dashboard, make sure to set ../src on the PYTHONPATH environment variable and launch from temrinal
with 'python dash-app.py'

"""
import dash
import layout_utils
from dash.dependencies import Input, Output, State

import frontend_utils
import callback_utils
import pandas as pd
import json
from layout_utils import *

# configs and parameters
n = 1000
countdown_duration = 60
m_freq = 60600
s_freq = 1010
cam_link = "http://www1.ville.montreal.qc.ca/Circulation-Cameras/GEN{}.jpeg"

with open("./assets/bar_config.json", "r") as jfile:
    plot_config = json.load(jfile)

with open("./assets/mapdata.json", "r") as jfile:
    map_config = json.load(jfile)

with open("./assets/slider_config.json", "r") as jfile:
    slider_config = json.load(jfile)

with open("./assets/desc.txt", "r") as tfile:
    desc = tfile.readlines()[0]

# dash intervals for countdown spinner (1s interval) and update plots with new data from redis (60s interval)
minterval = dcc.Interval(
    id="minute-interval",
    interval=m_freq,
    n_intervals=0
)

sinterval = dcc.Interval(
    id="second-interval",
    interval=s_freq,
    n_intervals=0)

# read detector datasheet
df = pd.read_csv("../data/detectors-active.csv")
stations = ["station {}".format(i + 1) for i in range(len(df))]
cam_ids = df["id_camera"].values.tolist()
cam_ids = {s: i for s, i in zip(stations, cam_ids)}
streets = df["corner_st2"].values.tolist()
streets = {s: st for s, st in zip(stations, streets)}

# connect to redis, uses wrapper class for pyredis's Redis class from frontend_utils
db = frontend_utils.RedisDB()

# get readings
speed_values = db.latest_readings("vehicle-speed")
count_values = db.latest_readings("vehicle-count")
gap_values = db.latest_readings("vehicle-gap-time")
timestamp = db.latest_readings("time")[0]

hist_data = db.n_latest_readings("vehicle-speed", n)
hist_utc = db.n_latest_readings("time", n)[0]
hist_dict = {s: l for s, l in zip(stations, hist_data)}

# create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="mqtt-real", update_title=None)

# init layout (empty cards, but in correct placement) with wrapper classes from layout_utils
layout, left_column, right_column = layout_utils.init_layout()

# get specified cards by name
title_card = right_column.get_subpanel_by_id("title-pane").children
camera_card = right_column.get_subpanel_by_id("stat-2").children.children
map_card = right_column.get_subpanel_by_id('map-pane').children
speed_card = left_column.get_subpanel_by_id("vspeed").children
count_card = left_column.get_subpanel_by_id("vcount").children
gap_card = left_column.get_subpanel_by_id("vgap").children
refresh_card = right_column.get_subpanel_by_id("stat-3").children
timestamp_card = right_column.get_subpanel_by_id('stat-4').children
hist_card = right_column.get_subpanel_by_id("hist-pane").children
table_card = left_column.get_subpanel_by_id("aux").children

# populate cards with texts and/or maps and plots with wrapper definitions or classes from layout_utils

title_card.children = layout_utils.make_title()
spinner = CountdownSpinner(plot_config, "seconds to next update", refresh_card, "pie-graph")
ts = TimeStamp(plot_config, "readings as of ", timestamp_card)
ts.update_time(timestamp)

camera_card.children = layout_utils.make_modal(plot_config, stations)

table = CustomTable(plot_config, "detector metrics summary", table_card)
table_data = frontend_utils.generate_table_data(df, speed_values, count_values, gap_values)
table.set_data(table_data)

map_fig, map_data = layout_utils.init_map(df)
map_card.figure = map_fig
map_fig.update_layout(paper_bgcolor="gray", margin=dict(l=0, r=0, b=0, t=0))

speedbar = CustomBar(plot_config, "speed dectected", speed_card, "speed-live-graph")
countbar = CustomBar(plot_config, "vehicles counted", count_card, "count-live-graph")
gapbar = CustomBar(plot_config, "gap time between vehicles", gap_card, "gap-live-graph")

speedbar.set_data(speed_values, stations, "kmh")
countbar.set_data(count_values, stations, "cars")
gapbar.set_data(gap_values, stations, "s")

# the historic scatter plot is more involved with the choice to choose 2 stations and a data type to compare
# initially start with station1, station2, and vehicle speed
cardheader = layout_utils.make_header("historic data over 24 hrs - use sliders and dropdown to select range and type",
                                      plot_config)

scatter = CustomScatter(plot_config)
slider = CustomSlider()
dropdown = CustomDropdown(stations)

primary_values = hist_dict["station 1"]
secondary_values = hist_dict["station 2"]

scatter.set_unit("kmh")
scatter.set_labels(hist_utc)
scatter.set_primary_data(primary_values)
scatter.set_secondary_data(secondary_values)
slider.set_labels(hist_utc)

hist_card.children = [cardheader, dropdown.layout, scatter.graph, slider.layout]

# assign populated layout to app, along with interval components for updating
app.layout = html.Div([layout, minterval, sinterval])

# current way to pass objects so that they can be used by callback methods in the callback_utils.py module
# probably a better way exists, to be investigated in future
elements = {
    "spinner": spinner,
    "timestamp": ts,
    "slider-config": slider_config,
    "n": n,
    "slider": slider,
    "scatter": scatter,
    "db": db,
    "station": stations,
    "speedbar": speedbar,
    "countbar": countbar,
    "gapbar": gapbar,
    "table": table,
    "countdown-duration": countdown_duration,
    'cam-ids': cam_ids,
    "cam-link": cam_link,
    "streets": streets
}

callback_utils.init_callbacks(app, elements)

if __name__ == "__main__":
    app.run_server(debug=True, port=8080, dev_tools_ui=False)
