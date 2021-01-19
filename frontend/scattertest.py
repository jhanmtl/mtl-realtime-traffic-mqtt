import dash
import dash_html_components as html
import dash_core_components as dcc
import numpy as np
import json
from layout_utils import CustomScatter, CustomSlider
import string
import frontend_utils
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

with open("./assets/bar_config.json", "r") as jfile:
    plot_config = json.load(jfile)

with open("./assets/slider_config.json", "r") as jfile:
    slider_config = json.load(jfile)

labels = [c for c in string.ascii_lowercase]

x = np.arange(-13, 13)
values = x ** 2
n = len(x)
print(n)

scatter = CustomScatter(plot_config)
slider = CustomSlider()

scatter.set_unit("kmh")
scatter.set_labels(labels)

scatter.set_primary_data(values)
scatter.set_secondary_data(-1 * values)

slider.set_labels(labels)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([scatter.graph, slider.layout])


@app.callback([Output("left-marker", "style"),
               Output("left-marker", "children"),
               Output("right-marker", "style"),
               Output("right-marker", "children"),
               Output("hist-plot", "figure")
               ],
              Input("cust-slider", "value"),
              )
def update_slider_labels(v):
    [idx_left, idx_right] = v
    print(v)

    offset_left = int(100 * (idx_left / n)) - 2
    offset_right = int(100 * (idx_right / n))

    style_left = {"marginLeft": "{}%".format(offset_left)}
    style_left.update(slider_config)

    style_right = {"marginLeft": "{}%".format(offset_right), "paddingTop": "60px"}
    style_right.update(slider_config)

    text_left = slider.labels[idx_left]
    text_right = slider.labels[idx_right]

    scatter.zoom_in(idx_left, idx_right)

    return style_left, str(text_left)+" "+str(idx_left), style_right, str(text_right)+" "+str(idx_right), scatter.base_fig


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
