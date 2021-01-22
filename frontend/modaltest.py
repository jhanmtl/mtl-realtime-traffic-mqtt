import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash

modal = html.Div(
    [
        dbc.Button("Open", id="open-centered"),
        dbc.Modal(
            [
                dbc.ModalHeader("Header"),
                dbc.ModalBody(
                    html.Img(srcSet="http://www1.ville.montreal.qc.ca/Circulation-Cameras/GEN31.jpeg")
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close-centered", className="ml-auto"
                    )
                ),
            ],
            id="modal-centered",
            centered=True,
        ),
    ]
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="mqtt-real", update_title=None)
app.layout=modal


@app.callback(
    Output("modal-centered", "is_open"),
    [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

if __name__=="__main__":
    app.run_server(port=8080,debug=True)
