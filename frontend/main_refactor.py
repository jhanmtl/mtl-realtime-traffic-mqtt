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
from layout_utils import CustomBar, CustomTable, CustomScatter, CountdownSpinner, CustomSlider, CustomDropdown

# ================= load configs ==============================================
with open("./assets/bar_config.json", "r") as jfile:
    plot_config = json.load(jfile)

with open("./assets/slider_config.json", "r") as jfile:
    slider_config = json.load(jfile)

n = 400

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
hist_data = db.n_latest_readings("vehicle-speed", n)
hist_utc = db.n_latest_readings("time", n)[0]
hist_dict = {s: l for s, l in zip(stations, hist_data)}

primary_values = hist_dict["station 1"]
secondary_values = hist_dict["station 2"]

scatter = CustomScatter(plot_config)
slider = CustomSlider()
dropdown = CustomDropdown(stations)

cardheader = dbc.CardHeader("historic data over 24 hrs - use sliders and dropdown to select range and type",
                            style={"textAlign": "center",
                                   "padding": "0px",
                                   "border": "0px",
                                   "color": plot_config['textcolor'],
                                   "borderRadius": "0px"
                                   })

scatter.set_unit("kmh")
scatter.set_labels(hist_utc)

scatter.set_primary_data(primary_values)
scatter.set_secondary_data(secondary_values)

slider.set_labels(hist_utc)

hist_card.children = [cardheader, dropdown.layout, scatter.graph, slider.layout]

minterval = dcc.Interval(
    id="minute-interval",
    interval=60600,
    n_intervals=0
)

app.layout = html.Div([layout, minterval])


@app.callback(Output("pie-graph", "figure"),
              Input("countdown-timer-id", "n_intervals"))
def update_countdown(n):
    time_elapsed = n % 60
    time_remaining = 60 - time_elapsed
    spinner.increment(time_elapsed, time_remaining)
    return spinner.fig


def slide_zoom_in(slider_values):
    [idx_left, idx_right] = slider_values

    offset_left = int(100 * (idx_left / n))
    offset_right = int(100 * (idx_right / n)) - 7

    style_left = {"marginLeft": "{}%".format(offset_left), "marginTop": "10px"}
    style_left.update(slider_config)

    style_right = {"marginLeft": "{}%".format(offset_right), "marginTop": "75px"}
    style_right.update(slider_config)

    text_left = slider.labels[idx_left]
    text_right = slider.labels[idx_right]

    text_left=text_left.split("T")[-1]
    text_right=text_right.split("T")[-1]

    scatter.zoom_in(idx_left, idx_right)

    return [scatter.base_fig, idx_left, idx_right, style_left, text_left, style_right,
            text_right]


@app.callback(
    [Output("left-marker", "style"),
     Output("left-marker", "children"),
     Output("right-marker", "style"),
     Output("right-marker", "children")],
    [Input('cust-slider', 'value'),
     Input('minute-interval', 'n_intervals')]
)
def update_slider(slider_values, n_intervals):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]["prop_id"]
    if "interval" in trigger:
        new_hist_utc = db.n_latest_readings("time", n)[0]
        slider.set_labels(new_hist_utc)

    zoom_slide_updates = slide_zoom_in(slider_values)
    return zoom_slide_updates[3:]


@app.callback(
    [Output("hist-plot", "figure"),
     Output('speed-live-graph', "figure"),
     Output('count-live-graph', "figure"),
     Output("gap-live-graph", "figure")
     ],
    [Input("cust-slider", "value"),
     Input("minute-interval", "n_intervals"),
     Input("drop-1", "value"),
     Input("drop-2", "value"),
     Input("drop-0", "value")
     ]
)
def update_plots(slider_values, _, selection_1, selection_2, selection_0):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]["prop_id"]
    zoom_slide_updates = slide_zoom_in(slider_values)

    if selection_0 == "speed":
        datatype = "vehicle-speed"
        unit = "kmh"
    elif selection_0 == "count":
        datatype = "vehicle-count"
        unit = "cars"
    else:
        datatype = "vehicle-gap-time"
        unit = "seconds"

    if "drop" in trigger:

        new_times_utc = db.n_latest_readings("time", n + 1)[0]

        new_data = db.n_latest_readings(datatype, n + 1)
        new_timestamp = new_times_utc[-1]

        old_timestamp = scatter.labels[-1]

        if new_timestamp != old_timestamp:
            new_times_utc = new_times_utc[:-1]
            new_hist_dict = {s: l[:-1] for s, l in zip(stations, new_data)}
        else:
            new_times_utc = new_times_utc[1:]
            new_hist_dict = {s: l[1:] for s, l in zip(stations, new_data)}

        new_primary_values = new_hist_dict[selection_1]
        new_secondary_values = new_hist_dict[selection_2]

        scatter.update_primary_data(new_primary_values)
        scatter.update_secondary_data(new_secondary_values)
        scatter.set_labels(new_times_utc)
        scatter.set_unit(unit)

        scatter.zoom_in(zoom_slide_updates[1], zoom_slide_updates[2])

    if "interval" in trigger:
        new_times_utc = db.n_latest_readings("time", n)[0]
        new_data = db.n_latest_readings(datatype, n)
        new_hist_dict = {s: l for s, l in zip(stations, new_data)}

        new_speed_values = db.latest_readings("vehicle-speed")
        new_count_values = db.latest_readings("vehicle-count")
        new_gap_values = db.latest_readings("vehicle-gap-time")

        speedbar.set_data(new_speed_values, stations, "kmh")
        countbar.set_data(new_count_values, stations, "cars")
        gapbar.set_data(new_gap_values, stations, "s")

        new_primary_values = new_hist_dict[selection_1]
        new_secondary_values = new_hist_dict[selection_2]

        scatter.update_primary_data(new_primary_values)
        scatter.update_secondary_data(new_secondary_values)
        scatter.set_labels(new_times_utc)
        scatter.set_unit(unit)

        scatter.zoom_in(zoom_slide_updates[1], zoom_slide_updates[2])

    return [scatter.base_fig, speedbar.fig, countbar.fig, gapbar.fig]


if __name__ == "__main__":
    app.run_server(debug=True, port=8080, dev_tools_ui=False)
