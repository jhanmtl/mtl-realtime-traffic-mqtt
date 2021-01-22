import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import layout_utils
from dash.dependencies import Input, Output, State

import frontend_utils
import callbacks
import pandas as pd
import json
from layout_utils import *

# ================= load configs ==============================================
with open("./assets/bar_config.json", "r") as jfile:
    plot_config = json.load(jfile)

with open("./assets/mapdata.json", "r") as jfile:
    map_config = json.load(jfile)

with open("./assets/slider_config.json", "r") as jfile:
    slider_config = json.load(jfile)

with open("./assets/desc.txt", "r") as tfile:
    desc = tfile.readlines()[0]

cam_link = "http://www1.ville.montreal.qc.ca/Circulation-Cameras/GEN{}.jpeg"

n = 1440
countdown_duration = 60
m_freq = 60600

s_freq = 1010

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
timestamp = db.latest_readings("time")[0]

df = pd.read_csv("../data/detectors-active.csv")
stations = ["station {}".format(i + 1) for i in range(len(df))]
cam_ids = df["id_camera"].values.tolist()
cam_ids = {"station {}".format(i + 1): cam_ids[i] for i in range(len(cam_ids))}
streets = df["corner_st2"].values.tolist()
streets = {"station {}".format(i + 1): streets[i] for i in range(len(streets))}

# ==================== app entry pt ===========================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="mqtt-real", update_title=None)
layout, left_column, right_column = layout_utils.init_layout()

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

# ========================= title stuff ======================================
intro_desc = html.P(
    [
        html.H4("Montreal Real Time Traffic via MQTT",
                style={"textAlign": "center", "textDecoration": "underline", "marginBottom": "16px",
                       "color": "#b0b0b0"}),
        "This project performs realtime IoT data fetching and visualization from 9 thermal and radar sensors embedded "
        "along Rue Notre-Dame by Montreal for its Open Data initiative. ",
        html.Br(),
        html.Br(),
        "Each sensor publishes traffic data in 60 second intervals over the mqtt protocol. "
        "Details about the data source can be found ",
        html.A("here. ",
               href="https://donnees.montreal.ca/ville-de-montreal/circulation-mobilite-temps-reel",
               target="_blank",
               className="hlink"),
        html.Br(),
        html.Br(),
        "Technology involved in building this application include paho-mqtt for data subscription, dash for visualization, and "
        "redis as an in-memory database . See more details at the ",
        html.A("project repo.",
               href="https://github.com/jhanmtl/mtl-realtime-traffic-mqtt",
               target="_blank",
               className="hlink")
    ],
    style={"textAlign": "justify"}
)

title_layout = html.Div([intro_desc],
                        style={"textAlign": "justify", "margin": "16px", "color": "#7a7a7a"})

title_card.children = title_layout

# ======================= camera modal stuff ==================================
camera_text = html.P(["Select to view feed of traffic cameras located at detector locations.",
                      " Note cameras update at 5 minute intervals"
                      ],
                     style={"margin":"16px","textAlign":"justify","color":"#7a7a7a"}
                    )
btn = dbc.Button("view traffic cam", id="open-modal", style={"marginTop":"16px"})
modal = layout_utils.make_modal()
dropdown = dcc.Dropdown(
    id="station-camera-dropdown",
    value="station 1",
    options=[{"label": o, 'value': o} for o in stations],
    clearable=False
)

modal_layout = html.Div([html.Div([dropdown,
                                  modal,
                                   btn
                                   ],style={"textAlign":"center"}),
                         html.Br(),
                         camera_text
                         ],
                        )

camera_card.children = modal_layout

# =======================table stuff ==========================================
table_summary = {
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
map_card.figure = map_fig
map_fig.update_layout(paper_bgcolor="gray", margin=dict(l=0, r=0, b=0, t=0))

# ================== countdown spinner =======================================
spinner = CountdownSpinner(plot_config, "seconds to next update", refresh_card, "pie-graph")

# ================== time stamp stuff ========================================
ts = TimeStamp(plot_config, "readings as of ", timestamp_card)
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

n = len(hist_data[0])

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
    'cam-ids':cam_ids,
    "cam-link":cam_link,
    "streets":streets
}

callbacks.init_callbacks(app, elements)




if __name__ == "__main__":
    app.run_server(debug=True, port=8080, dev_tools_ui=True)
