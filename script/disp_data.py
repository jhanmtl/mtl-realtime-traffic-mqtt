import numpy as np
import redis
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output

db = redis.Redis()
app = dash.Dash(__name__)
app.layout = html.Div(
    html.Div([
        html.H4("speed"),
        dcc.Graph(id="speed-plot"),
        dcc.Interval(
            id='interval-component',
            interval=1000,
            n_intervals=0
        )
    ])
)


@app.callback(Output('speed-plot', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    data = json.loads(db.get("00773"))
    speed = data['vehicle-speed']
    speed=[i for i in speed if i>0]
    xval = np.arange(len(speed))
    fig = px.line(x=xval, y=speed, title="from last {} intervals".format(n))
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
