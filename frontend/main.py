import dash
import dash_bootstrap_components as dbc
import layout_utils
from dash.dependencies import Input, Output


import frontend_utils
import pandas as pd
import numpy as np
import json
from layout_utils import CustomBar, CustomTable, CustomScatter

# loads config for styling plots
with open("./assets/bar_config.json", "r") as jfile:
    plot_config = json.load(jfile)

# detector data (lon, lat, id for map plot)
df = pd.read_csv("../data/detectors-active.csv")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
layout, left_column, right_column = layout_utils.init_layout()

# load map, set to corresponding panel in dashboard
map_fig, map_data = frontend_utils.init_map(df)
right_column.get_subpanel_by_id('map-pane').children.figure = map_fig
map_fig.update_layout(paper_bgcolor="gray", margin=dict(l=0, r=0, b=0, t=0))


stations = ["station {}".format(i + 1) for i in range(9)]
speed_values = np.random.randint(10, 40, len(stations))
count_values = np.random.randint(10, 40, len(stations))
gap_values = np.random.randint(10, 40, len(stations))

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
speedbar = CustomBar(plot_config, "speed dectected", speed_card, "speed-live-graph")
speedbar.set_data(speed_values, stations, "kmh")

count_card = left_column.get_subpanel_by_id("vcount").children
countbar = CustomBar(plot_config, "vehicles counted", count_card, "count-live-graph")
countbar.set_data(count_values, stations, "cars")

gap_card = left_column.get_subpanel_by_id("vgap").children
gapbar = CustomBar(plot_config, "gap time between vehicles", gap_card, "gap-live-graph")
gapbar.set_data(gap_values, stations, "s")

aux_card = left_column.get_subpanel_by_id("aux").children
table=CustomTable(plot_config, "detector metrics summary", aux_card)
table.set_data(summary)

scatter_value=np.random.randint(10,70,60)
scatter_x=np.arange(len(scatter_value))
hist_card=right_column.get_subpanel_by_id("hist-pane").children

hist_graph=CustomScatter(plot_config, "historical data", hist_card)
hist_graph.set_data(scatter_value,"kmh")

app.layout = layout


@app.callback(
    [Output('speed-live-graph',"figure"),
     Output('count-live-graph',"figure"),
     Output("gap-live-graph","figure")
     ],
    [Input('speed-live-graph-interval','n_intervals'),
     Input('count-live-graph-interval','n_intervals'),
     Input('gap-live-graph-interval','n_intervals')]
              )
def update_live(n1,n2,n3):
    speed_values = np.random.randint(0, 40, len(stations))
    speedbar.set_data(speed_values, stations, "kmh")

    count_values = np.random.randint(0, 40, len(stations))
    countbar.set_data(count_values, stations, "cars")

    gap_values = np.random.randint(0, 40, len(stations))
    gapbar.set_data(gap_values, stations, "s")

    print(n1, n2, n3)
    return speedbar.fig, countbar.fig, gapbar.fig

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
