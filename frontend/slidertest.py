import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

slider_dispstyle = {
    "color": "white",
    "display": "inline-block",
    "position": "absolute",
    "marginTop":"16px"
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
slider = dcc.RangeSlider(id="hist-slider",
                         min=0,
                         max=100,
                         value=[20, 60],
                         pushable=10,
                         updatemode="drag"
                         )

app.layout = html.Div([
    html.Div(children="value text", id="left-marker"),
    html.Div(children="value text", id="right-marker"),
    slider
], style={"marginTop": 64, "position": "relative", "width": "75%"})


@app.callback([Output("left-marker", "style"),
               Output("left-marker", "children"),
               Output("right-marker", "style"),
               Output("right-marker", "children")
               ],
              Input("hist-slider", "value"),
              )
def cb(v):
    [value_left, value_right] = v
    print(value_left, value_right)

    style_left = {"marginLeft": "{}%".format(value_left)}
    style_left.update(slider_dispstyle)

    style_right={"marginLeft":"{}%".format(value_right-1)}
    style_right.update(slider_dispstyle)



    return style_left, value_left, style_right, value_right


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
