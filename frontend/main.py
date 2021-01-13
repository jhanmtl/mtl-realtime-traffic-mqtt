import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import layout_utils
from dash.dependencies import Input, Output

import frontend_utils
import pandas as pd
import numpy as np
import json
from layout_utils import CustomBar, CustomTable, CustomScatter

with open("./assets/bar_config.json", "r") as jfile:
    plot_config = json.load(jfile)

df = pd.read_csv("../data/detectors-active.csv")

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])
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
refresh_card=right_column.get_subpanel_by_id("stat-3").children

header=dbc.CardHeader("seconds to refresh",style={"textAlign":"center"})

pstyle={
    "color":"red"
}

refresh_card.children=[header,
                       dbc.Row(dbc.Col(dbc.Progress(id="countdown-progress",barClassName="pbar",style={"background":plot_config['barcolor'],"margin":"auto"})),style={"height":"50%","width":"85%","textAlign":"center","margin":"auto"}),
                       dbc.Row(dbc.Col(html.P(id="countdown-text")),style={"width":"75%","textAlign":"center","margin":"auto"}),
                       dcc.Interval(id="countdown-timer-id",interval=1000,n_intervals=0)]

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

@app.callback([Output("countdown-progress","value"),
               Output("countdown-text","children")],
              Input("countdown-timer-id","n_intervals"))
def update_countdown(n):
    time_remaining=60-n%60

    progress=int(100-100*(60-n%60)/60)
    return progress, str(time_remaining)+" s"


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

    print(n1, n2, n3)
    return speedbar.fig, countbar.fig, gapbar.fig


if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
