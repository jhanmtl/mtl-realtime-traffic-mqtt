import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import layout_utils
from dash.dependencies import Input, Output
import plotly.express as px
from plotly import graph_objects as go

import frontend_utils
import pandas as pd
import numpy as np
import json
from layout_utils import CustomBar, CustomTable, CustomScatter, CountdownSpinner


# ================= load configs ==============================================
with open("./assets/bar_config.json", "r") as jfile:
    plot_config = json.load(jfile)

with open("./assets/slider_config.json", "r") as jfile:
    slider_config = json.load(jfile)

n = 20

# ================= instantiate db, fetch data =================================
db = frontend_utils.RedisDB()
speed_values = db.latest_readings("vehicle-speed")
count_values = db.latest_readings("vehicle-count")
gap_values = db.latest_readings("vehicle-gap-time")

df = pd.read_csv("../data/detectors-active.csv")
stations = ["station {}".format(i + 1) for i in range(len(df))]

# ==================== app entry pt ===========================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
layout, left_column, right_column = layout_utils.init_layout()

speed_card = left_column.get_subpanel_by_id("vspeed").children
count_card = left_column.get_subpanel_by_id("vcount").children
gap_card = left_column.get_subpanel_by_id("vgap").children
refresh_card = right_column.get_subpanel_by_id("stat-3").children
hist_card = right_column.get_subpanel_by_id("hist-pane").children


# ================== map stuff ================================================
map_fig, map_data = frontend_utils.init_map(df)
right_column.get_subpanel_by_id('map-pane').children.figure = map_fig
map_fig.update_layout(paper_bgcolor="gray", margin=dict(l=0, r=0, b=0, t=0))

# ================== countdown spinner =======================================
spinner = CountdownSpinner(plot_config, "seconds to next update", refresh_card, "pie-graph")

# ================== bar plots ===============================================
speedbar = CustomBar(plot_config, "speed dectected", speed_card, "speed-live-graph")
countbar = CustomBar(plot_config, "vehicles counted", count_card, "count-live-graph")
gapbar = CustomBar(plot_config, "gap time between vehicles", gap_card, "gap-live-graph")

speedbar.set_data(speed_values, stations, "kmh")
countbar.set_data(count_values, stations, "cars")
gapbar.set_data(gap_values, stations, "s")

# =================== hist scatter plot =====================================
hist_speed = db.n_latest_readings("vehicle-speed", n)
hist_utc = db.n_latest_readings("time", n)[0]
hist_dict = {s: l for s, l in zip(stations, hist_speed)}
hplot = CustomScatter(plot_config, "historic data over last 24 hrs - use slider to adjust range", hist_card, stations)

values1 = hist_dict["station 1"]
values2 = hist_dict["station 2"]

hplot.set_primary(hist_utc, values1, "kmh")
hplot.set_seconary(values2)

hplot.update_primary(hist_utc, values1)
hplot.update_secondary(hist_utc, values2)

app.layout = layout


@app.callback([Output("left-marker", "style"),
               Output("left-marker", "children"),
               Output("right-marker", "style"),
               Output("right-marker", "children")
               ],
              Input("hist-slider", "value"),
              )
def update_slider_labels(v):
    global hist_utc

    [value_left, value_right] = v
    # print(v)

    marginLeft = int(100 * (value_left / n))
    marginRight = int(100 * (value_right / n))

    style_left = {"marginLeft": "{}%".format(marginLeft)}
    style_left.update(slider_config)

    style_right = {"marginLeft": "{}%".format(marginRight - 4), "paddingTop": "60px"}
    style_right.update(slider_config)

    time_left = hist_utc[value_left - 1]
    time_right = hist_utc[value_right - 1]

    # print(time_left, time_right)

    leftday, lefttime = frontend_utils.date_convert(time_left)
    rightday, righttime = frontend_utils.date_convert(time_right)

    text_left = html.P([
        leftday,
        html.Br(),
        lefttime
    ])

    text_right = html.P([
        rightday,
        html.Br(),
        righttime
    ])

    return style_left, text_left, style_right, text_right


@app.callback(Output("pie-graph", "figure"),
              Input("countdown-timer-id", "n_intervals"))
def update_countdown(n):
    time_elapsed = n % 60
    time_remaining = 60 - time_elapsed
    spinner.increment(time_elapsed, time_remaining)
    return spinner.fig


@app.callback(
    [Output('speed-live-graph', "figure"),
     Output('count-live-graph', "figure"),
     Output("gap-live-graph", "figure"),
     Output("hist-plot", "figure")
     ],
    [Input('speed-live-graph-interval', 'n_intervals'),
     Input('count-live-graph-interval', 'n_intervals'),
     Input('gap-live-graph-interval', 'n_intervals'),
     Input('hist-interval', 'n_intervals'),
     Input('hist-slider', 'value'),
     Input("drop-1", "value"),
     Input("drop-2", "value")
     ]
)
def update_live(n1, n2, n3, n4, value_range, selection_1, selection_2):
    global hist_speed
    global hist_utc

    hist_speed = db.n_latest_readings("vehicle-speed", n)
    hist_utc = db.n_latest_readings("time", n)[0]

    hist_speed_dict = {s: l for s, l in zip(stations, hist_speed)}
    values1 = hist_speed_dict[selection_1]
    values2 = hist_speed_dict[selection_2]
    [i, j] = value_range

    ctx = dash.callback_context

    update_all = False

    if ctx.triggered:
        if len(ctx.triggered) > 1:
            update_all = True

    if update_all:
        speed_values = db.latest_readings("vehicle-speed")
        count_values = db.latest_readings("vehicle-count")
        gap_values = db.latest_readings("vehicle-gap-time")

        speedbar.set_data(speed_values, stations, "kmh")
        countbar.set_data(count_values, stations, "cars")
        gapbar.set_data(gap_values, stations, "s")

        hplot.set_primary(hist_utc, values1, "kmh")
        hplot.set_seconary(values2)

    windowed_primary = hplot.val_primary[i:j]
    windowed_secondary = hplot.val_secondary[i:j]
    windowed_time = hplot.time[i:j]

    hplot.update_primary(windowed_time, windowed_primary)
    hplot.update_secondary(windowed_time, windowed_secondary)

    return speedbar.fig, countbar.fig, gapbar.fig, hplot.fig


if __name__ == "__main__":
    app.run_server(debug=True, port=8080, dev_tools_ui=False)
