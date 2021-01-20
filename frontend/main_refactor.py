import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import layout_utils


import frontend_utils
import callbacks
import pandas as pd
import json
from layout_utils import *

# ================= load configs ==============================================
with open("./assets/bar_config.json", "r") as jfile:
    plot_config = json.load(jfile)

with open("./assets/slider_config.json", "r") as jfile:
    slider_config = json.load(jfile)

mode="real"

if mode=="real":
    n = 400
    countdown_duration=60
    m_freq=60600
else:
    n=4800
    countdown_duration=10
    m_freq=10100

s_freq=1010

minterval = dcc.Interval(
    id="minute-interval",
    interval=m_freq,
    n_intervals=0
)

sinterval = dcc.Interval(
    id="second-interval",
    interval=s_freq,
    n_intervals=0)

# ================= instantiate db, fetch data =================================
db = frontend_utils.RedisDB()
speed_values = db.latest_readings("vehicle-speed")
count_values = db.latest_readings("vehicle-count")
gap_values = db.latest_readings("vehicle-gap-time")
timestamp=db.latest_readings("time")[0]

df = pd.read_csv("../data/detectors-active.csv")
stations = ["station {}".format(i + 1) for i in range(len(df))]

# ==================== app entry pt ===========================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="mqtt dash", update_title=None)
layout, left_column, right_column = layout_utils.init_layout()

speed_card = left_column.get_subpanel_by_id("vspeed").children
count_card = left_column.get_subpanel_by_id("vcount").children
gap_card = left_column.get_subpanel_by_id("vgap").children
refresh_card = right_column.get_subpanel_by_id("stat-3").children
timestamp_card=right_column.get_subpanel_by_id('stat-4').children
hist_card = right_column.get_subpanel_by_id("hist-pane").children
table_card=left_column.get_subpanel_by_id("aux").children

# =======================table stuff ==========================================
table_summary={
    "station": (np.arange(len(stations)) + 1).tolist(),
    "speed (kmh)": speed_values,
    "count (cars)": count_values,
    "gap time (s)": gap_values
}
table_summary = pd.DataFrame.from_dict(table_summary)
table_summary["corner"] = df["corner_st2"]
table_summary = table_summary[["station", "corner", "speed (kmh)", "count (cars)", "gap time (s)"]]

table = CustomTable(plot_config, "detector metrics summary", table_card)
table.set_data(table_summary)

# ================== map stuff ================================================
map_fig, map_data = frontend_utils.init_map(df)
right_column.get_subpanel_by_id('map-pane').children.figure = map_fig
map_fig.update_layout(paper_bgcolor="gray", margin=dict(l=0, r=0, b=0, t=0))

# ================== countdown spinner =======================================
spinner = CountdownSpinner(plot_config, "seconds to next update", refresh_card, "pie-graph")

# ================== time stamp stuff ========================================
ts=TimeStamp(plot_config,"readings as of ", timestamp_card)
ts.update_time(timestamp)
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

app.layout = html.Div([layout, minterval, sinterval])

elements={
    "spinner":spinner,
    "timestamp":ts,
    "slider-config":slider_config,
    "n":n,
    "slider":slider,
    "scatter":scatter,
    "db":db,
    "station":stations,
    "speedbar":speedbar,
    "countbar":countbar,
    "gapbar":gapbar,
    "table":table,
    "countdown-duration":countdown_duration
}

callbacks.init_callbacks(app,elements)



if __name__ == "__main__":
    app.run_server(debug=True, port=8080, dev_tools_ui=True)
