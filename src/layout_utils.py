import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

def init_layout():
    left_column = LeftColumn()
    right_column = RightColumn()

    layout = html.Div(dbc.Row([
        left_column.get_layout(),
        right_column.get_layout()
    ], className="container-row"),
        className="base-div")

    return layout, left_column, right_column

class LeftColumn:
    def __init__(self):
        aux_panel = dbc.Row(card(), className="top-left-pane", id="aux")
        speed_panel = dbc.Row(card(), className="speed-plot", id="vspeed")
        count_panel = dbc.Row(card(), className="count-plot", id="vcount")
        time_panel = dbc.Row(card(), className="time-plot", id="vgap")
        self.subpanels = [aux_panel, speed_panel, count_panel, time_panel]
        self.layout = dbc.Col(self.subpanels, width=4,
                              className="full-vh-cols")

    def get_layout(self):
        return self.layout

    def get_subpanel_by_id(self, pid):
        for sub in self.subpanels:
            if sub.id == pid:
                return sub
        else:
            raise Exception("No panel by that id")


class RightColumn:
    def __init__(self):
        title = TitlePane()
        stat1 = dbc.Col(dbc.Row(card(),className="wrap-div"), className="stat-col", id="stat-1",style={"padding":0})
        stat2 = dbc.Col(dbc.Row(card(),className="wrap-div"), className="stat-col", id="stat-2",style={"padding":0})
        stat3 = dbc.Row(card(), className="substat-row", id="stat-3")
        stat4 = dbc.Row(card(), className="substat-row", id="stat-4")
        drop = DropDown()
        mapp = MapPane()
        hist = HistoricPlot()
        self.subpanels = [title.get_layout(), stat1, stat2, stat3, stat4, drop.get_layout(), mapp.get_layout(), hist.get_layout()]

        self.layout = dbc.Col([
            dbc.Row([
                dbc.Col([
                    title.get_layout(),
                    dbc.Row([
                        stat1,
                        stat2,
                        dbc.Col([
                            stat3,
                            stat4
                        ], className="stat-col"),
                    ], className="key-stat-row"),

                    drop.get_layout()
                ], className="title-key-stat-col"),
                mapp.get_layout(),
            ], className="title-stat-map-row"),
            hist.get_layout()
        ],
            className='full-vh-cols')

    def get_layout(self):
        return self.layout

    def get_subpanel_by_id(self, pid):
        for sub in self.subpanels:
            if sub.id == pid:
                return sub
        else:
            raise Exception("No panel by that id")


class MapPane:
    def __init__(self):
        self.layout = dbc.Col(dcc.Graph(id="scatter_map",className="graphs"), className="map-col", id="map-pane")

    def get_layout(self):
        return self.layout


class HistoricPlot:
    def __init__(self):
        self.layout = dbc.Row(card(), className="historic-plot", id="hist-pane")

    def get_layout(self):
        return self.layout


class TitlePane:
    def __init__(self):
        self.layout = dbc.Row(card(), className="title-row", id="title-pane")

    def get_layout(self):
        return self.layout


class DropDown:
    def __init__(self):
        self.layout = dbc.Row(card(), className="drop-down-row", id="drop-pane")

    def get_layout(self):
        return self.layout

def card():
    return dbc.Card(className="card")
