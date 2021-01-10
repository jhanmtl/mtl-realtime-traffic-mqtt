import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import layout_utils
import plotly.express as px

import frontend_utils
import pandas as pd
import numpy as np

df = pd.read_csv("../data/detectors-active.csv")
map_fig, map_data = frontend_utils.init_map(df)
map_fig.update_layout(paper_bgcolor="gray", margin=dict(l=0,r=0,b=0,t=0))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
layout, left_column, right_column = layout_utils.init_layout()
right_column.get_subpanel_by_id('map-pane').children.figure=map_fig

app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=False, port=8080)
