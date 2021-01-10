import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc


class LeftColumn:
    def __init__(self):
        aux_panel = dbc.Row("tbd", className="top-left-pane", id="aux")
        speed_panel = dbc.Row(dcc.Graph(id="vspeed-graph", className="graphs"), className="speed-plot", id="vspeed")
        count_panel = dbc.Row(dcc.Graph(id="vcount-graph", className="graphs"), className="count-plot", id="vcount")
        time_panel = dbc.Row(dcc.Graph(id="vgaptime-graph", className="graphs"), className="time-plot", id="vgap")
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
        stat1 = dbc.Col("stat 1", className="stat-col", id="stat-1")
        stat2 = dbc.Col("stat 2", className="stat-col", id="stat-2")
        stat3 = dbc.Row("stat 3", className="substat-row", id="stat-3")
        stat4 = dbc.Row("stat 4", className="substat-row", id="stat-4")
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
        self.layout = dbc.Col("map", className="map-col", id="map-pane")

    def get_layout(self):
        return self.layout


class HistoricPlot:
    def __init__(self):
        self.layout = dbc.Row("plot", className="historic-plot", id="hist-pane")

    def get_layout(self):
        return self.layout


class TitlePane:
    def __init__(self):
        self.layout = dbc.Row("title text", className="title-row", id="title-pane")

    def get_layout(self):
        return self.layout


class DropDown:
    def __init__(self):
        self.layout = dbc.Row("title text", className="drop-down-row", id="drop-pane")

    def get_layout(self):
        return self.layout
