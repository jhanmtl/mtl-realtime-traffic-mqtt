import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import layout_utils
import plotly.express as px

import frontend_utils
import pandas as pd
import numpy as np

# df = pd.read_csv("../data/detectors-active.csv")
# map_fig, map_data = frontend_utils.init_map(df)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

left_column = layout_utils.LeftColumn()
right_column = layout_utils.RightColumn()

layout = html.Div(dbc.Row([left_column.get_layout(), right_column.get_layout()], className="container-row"),
                  className="base-div")

map=right_column.get_subpanel_by_id("map-pane")
print(map)
map.children="new map"
print(map)

app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
