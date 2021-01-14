import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import layout_utils
from dash.dependencies import Input, Output
import plotly.express as px

import frontend_utils
import pandas as pd
import numpy as np
import json
from layout_utils import CustomBar, CustomTable, CustomScatter, CountdownTimer

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

# ------------------------------ to be refactored into a spinner class -------------------------------------------------
header=dbc.CardHeader("seconds to update",style={"padding":"0","textAlign":"center"})

fig = px.pie(names=["done","todo"],
                 values=[60, 0],
                 color_discrete_sequence=[plot_config["capcolor"], plot_config["barcolor"]],
                 )
fig.update_traces(textinfo="none",
                  hole=0.9,
                  sort=False)

fig.update_layout(margin={"l": 8, "r": 8, "t": 16, "b": 16},
                  paper_bgcolor=plot_config['bgcolor'],
                  plot_bgcolor=plot_config['bgcolor'],
                  showlegend=False,
                  annotations=[dict(text="", font_color="white", font_size=16, x=0.5, y=0.5, showarrow=False)]
                  )

graph = dcc.Graph(id="pie-graph", className="graphs")
graph.figure = fig

interval=dcc.Interval(id="countdown-timer-id",interval=1000,n_intervals=0)
# ------------------------------ to be refactored into a spinner class -------------------------------------------------

refresh_card.children = [header,graph,interval]

speedbar = CustomBar(plot_config, "speed dectected", speed_card, "speed-live-graph")
countbar = CustomBar(plot_config, "vehicles counted", count_card, "count-live-graph")
gapbar = CustomBar(plot_config, "gap time between vehicles", gap_card, "gap-live-graph")

speedbar.set_data(speed_values, stations, "kmh")
countbar.set_data(count_values, stations, "cars")
gapbar.set_data(gap_values, stations, "s")

aux_card = left_column.get_subpanel_by_id("aux").children
table = CustomTable(plot_config, "detector metrics summary", aux_card)
table.set_data(summary)

scatter_value = np.random.randint(10, 70, 60)
scatter_x = np.arange(len(scatter_value))
hist_card = right_column.get_subpanel_by_id("hist-pane").children

hist_graph = CustomScatter(plot_config, "historical data", hist_card)
hist_graph.set_data(scatter_value, "kmh")

app.layout = layout


@app.callback(Output("pie-graph","figure"),
              Input("countdown-timer-id","n_intervals"))

def update_countdown(n):
    time_elapsed=n%60
    time_remaining=60-time_elapsed

    fig = px.pie(names=["done","todo"],
                 values=[time_elapsed, time_remaining],
                 color_discrete_sequence=[plot_config["capcolor"], plot_config["barcolor"]],
                 )
    fig.update_traces(textinfo="none",
                      hole=0.9,
                      sort=False)

    fig.update_layout(margin={"l": 8, "r": 8, "t": 16, "b": 16},
                      paper_bgcolor=plot_config['bgcolor'],
                      plot_bgcolor=plot_config['bgcolor'],
                      showlegend=False,
                      annotations=[dict(text=str(time_remaining), font_color="white", font_size=16, x=0.5, y=0.5, showarrow=False)]
                      )

    return fig


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
