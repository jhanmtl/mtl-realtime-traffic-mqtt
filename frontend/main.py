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

with open("./assets/bar_config.json", "r") as jfile:
    plot_config = json.load(jfile)

df = pd.read_csv("../data/detectors-active.csv")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
layout, left_column, right_column = layout_utils.init_layout()

map_fig, map_data = frontend_utils.init_map(df)
right_column.get_subpanel_by_id('map-pane').children.figure = map_fig
map_fig.update_layout(paper_bgcolor="gray", margin=dict(l=0, r=0, b=0, t=0))

db = frontend_utils.RedisDB()
stations = ["station {}".format(i + 1) for i in range(len(df))]

speed_values = db.latest_readings("vehicle-speed")
count_values = db.latest_readings("vehicle-count")
gap_values = db.latest_readings("vehicle-gap-time")

summary = {
    "station": (np.arange(len(stations)) + 1).tolist(),
    "speed (kmh)": speed_values,
    "count (cars)": count_values,
    "gap time (s)": gap_values
}

summary = pd.DataFrame.from_dict(summary)
summary["corner"] = df["corner_st2"]
summary = summary[["station", "corner", "speed (kmh)", "count (cars)", "gap time (s)"]]

speed_card = left_column.get_subpanel_by_id("vspeed").children
count_card = left_column.get_subpanel_by_id("vcount").children
gap_card = left_column.get_subpanel_by_id("vgap").children

refresh_card = right_column.get_subpanel_by_id("stat-3").children

spinner = CountdownSpinner(plot_config, "seconds to next update", refresh_card, "pie-graph")

speedbar = CustomBar(plot_config, "speed dectected", speed_card, "speed-live-graph")
countbar = CustomBar(plot_config, "vehicles counted", count_card, "count-live-graph")
gapbar = CustomBar(plot_config, "gap time between vehicles", gap_card, "gap-live-graph")

speedbar.set_data(speed_values, stations, "kmh")
countbar.set_data(count_values, stations, "cars")
gapbar.set_data(gap_values, stations, "s")

aux_card = left_column.get_subpanel_by_id("aux").children
table = CustomTable(plot_config, "detector metrics summary", aux_card)
table.set_data(summary)

n = 720
hist_card = right_column.get_subpanel_by_id("hist-pane").children
hist_speed = db.n_latest_readings("vehicle-speed", n)
hist_utc = db.n_latest_readings("time", n)[0]
stations = ["station {}".format(i + 1) for i in range(len(db.keys))]
hist_speed_dict = {s: l for s, l in zip(stations, hist_speed)}
hist_speed_dict["utc"] = hist_utc
hist_speed_df = pd.DataFrame.from_dict(hist_speed_dict)

# hist_speed_df=pd.DataFrame.from_dict(hist_speed_dict)
# print(hist_speed_df)
# scatter_value = np.random.randint(10, 70, 60)
# scatter_x = np.arange(len(scatter_value))
#
# hist_graph = CustomScatter(plot_config, "historical data", hist_card)
# hist_graph.set_data(scatter_value, "kmh")

unit="kmh"
y = hist_speed_df["station 1"].values
x = np.arange(len(y)).tolist()
t = [""]*len(x)

max_val=np.max(y)
max_idx=np.argmax(y)
t[max_idx]=str(max_val.item())+" "+unit

min_val=np.min(y)
min_idx=np.argmin(y)
t[min_idx]=str(min_val.item())+" "+unit

graph = dcc.Graph(className="graphs",id="hist-plot")

fig = px.scatter(x=x, y=y, text=t)
fig.update_layout(margin=plot_config["margin"],
                  paper_bgcolor=plot_config['bgcolor'],
                  plot_bgcolor=plot_config['bgcolor'],
                  showlegend=False,
                  xaxis=dict(tickvals=x,
                             ticktext=["" for i in range(len(x))],
                             title="",
                             color=plot_config['textcolor'],
                             showgrid=False,
                             zeroline=False,
                             ),
                  yaxis=dict(showgrid=False,
                             title="",
                             visible=False)
                  )

fig.update_traces(textfont_color=plot_config["textcolor"],
                  mode="lines+markers+text",
                  line=dict(color=plot_config["barcolor"]),
                  marker=dict(color=plot_config["capcolor"]),
                  textposition='top center'
                  )


slider=dcc.RangeSlider(
    id="time-slider",
    min=x[0],
    max=x[-1],
    value=[600,700],
    marks={i:str(i) for i in x[0::50]},
    step=10,
    pushable=50,
)


graph.figure = fig
hist_card.children = [slider,graph]

app.layout = layout

# @app.callback(Output("hist-plot","figure"),
#               Input("time-slider","value"))
# def update_hist_graph(value_range):
#     val=hist_speed_df["station 1"].values.tolist()
#     val=val[value_range[0]:value_range[1]]
#     fig.update_traces(x=np.arange(len(val)),y=val)
#     return fig


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
     Output("gap-live-graph", "figure")
     ],
    [Input('speed-live-graph-interval', 'n_intervals'),
     Input('count-live-graph-interval', 'n_intervals'),
     Input('gap-live-graph-interval', 'n_intervals')]
)
def update_live(n1, n2, n3):
    speed_values = db.latest_readings("vehicle-speed")
    count_values = db.latest_readings("vehicle-count")
    gap_values = db.latest_readings("vehicle-gap-time")

    speedbar.set_data(speed_values, stations, "kmh")
    countbar.set_data(count_values, stations, "cars")
    gapbar.set_data(gap_values, stations, "s")

    return speedbar.fig, countbar.fig, gapbar.fig


if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
