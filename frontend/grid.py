import dash
import dash_html_components as html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


row = html.Div(
    dbc.Row(
        [
            dbc.Col([
                        dbc.Row("tbd",className="top-left-pane"),
                        dbc.Row("speed plot",className="speed-plot"),
                        dbc.Row("count plot",className="count-plot"),
                        dbc.Row("time plot",className="time-plot")
                    ],
                    width=4, className="full-vh-cols"),
            dbc.Col(
                [
                    dbc.Row(
                            [
                                dbc.Col([
                                            dbc.Row("title text", className="title-row"),
                                            dbc.Row([
                                                        dbc.Col("stat 1",className="stat-col"),
                                                        dbc.Col("stat 2",className="stat-col"),
                                                        dbc.Col([
                                                                    dbc.Row("stat 3",className="substat-row"),
                                                                    dbc.Row("stat 4",className="substat-row")
                                                                ],
                                                                className="stat-col"),
                                                    ],
                                                    className="key-stat-row"),
                                            dbc.Row("dropdow select boxes", className="drop-down-row")
                                        ],
                                        className="title-key-stat-col"),
                                dbc.Col("map",className="map-col")
                            ],
                            className="title-stat-map-row"),
                    dbc.Row("historic plot",className="historic-plot")
                ],
                className='full-vh-cols')
        ],
        style={"margin": "0", "height": "100%"}),
    style={"height": "100vh", "padding": "16px"})

app.layout = row

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
