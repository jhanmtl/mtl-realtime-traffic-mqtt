import numpy as np
import dash_table
import plotly.graph_objects as go
import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc


class CustomTable:
    def __init__(self, config, card_title, target_card):
        self.config = config
        self.card = target_card
        self.cardheader = dbc.CardHeader(card_title, style={"textAlign": "center",
                                                            "padding": "0px",
                                                            "border": "0px",
                                                            "color": self.config['textcolor'],
                                                            "borderRadius": "0px"
                                                            })
        self.table = None

    def set_data(self, df):
        c = [{"name": i, "id": i} for i in df.columns]
        self.table = dash_table.DataTable(data=df.to_dict('records'),
                                          columns=c,
                                          id="table",
                                          style_cell={"textAlign": "center",
                                                      "border": "0",
                                                      "fontFamily": "Lato",
                                                      "fontSize": "0.65rem",
                                                      "background": self.config['bgcolor']},
                                          cell_selectable=False,
                                          style_cell_conditional=[{'if': {'column_id': c}, 'textAlign': 'left'} for c in
                                                                  ['corner']])
        self.card.children = [self.cardheader, self.table]


class CustomScatter:
    def __init__(self, config, card_title, target_card, stations, default_range=60, freq=60600):
        self.config = config
        self.card = target_card
        self.default_range = default_range
        self.cardheader = dbc.CardHeader(card_title, style={"textAlign": "center",
                                                            "padding": "0px",
                                                            "border": "0px",
                                                            "color": self.config['textcolor'],
                                                            "borderRadius": "0px"
                                                            })
        self.graph = dcc.Graph(className="graphs", id="hist-plot")
        self.slider = None
        self.fig = None

        self.val_primary = None
        self.val_secondary = None

        self.ticks = None
        self.unit = None
        self.time=None

        self.interval= dcc.Interval(
            id="hist-interval",
            interval=freq,
            n_intervals=0
        )

        self.dropdown1 = dcc.Dropdown(
            id='drop-1',
            value="station 1",
            options=[{"label": s, 'value': s} for s in stations],
            clearable=False,
        )

        self.dropdown2 = dcc.Dropdown(
            id='drop-2',
            value="station 2",
            options=[{"label": s, 'value': s} for s in stations],
            clearable=False,
        )

        self.data_select = dbc.Row([
            dbc.Col(self.dropdown1, width={"size": 3, "offset": 4}),
            dbc.Col(self.dropdown2, width={"size": 3})
        ],
            style={"marginTop": 32, "textAlign": "center"}
        )


    def set_primary(self, time,values, unit):
        self.time=time
        self.unit = unit
        self.ticks = np.arange(len(values))
        self.val_primary = values
        self.slider = dcc.RangeSlider(id="hist-slider",
                                      min=self.ticks[0],
                                      max=self.ticks[-1]+1,
                                      value=[self.ticks[-1] - self.default_range, self.ticks[-1]+1],
                                      step=10,
                                      pushable=self.default_range,
                                      )

        self.card.children = [self.cardheader,
                              self.data_select,
                              self.graph,
                              html.Div(self.slider, style={"width": "90%", "margin": "auto", "paddingTop": "32px"}),
                              self.interval
                              ]

    def set_seconary(self, values):
        self.val_secondary = values

    def update_primary(self, values):
        x = np.arange(len(values))
        t = self._min_max_texts(values)
        self.fig = px.scatter(x=x,
                              y=values
                              )
        self.fig.update_layout(margin=self.config["margin"],
                               paper_bgcolor=self.config['bgcolor'],
                               plot_bgcolor=self.config['bgcolor'],
                               showlegend=False,
                               xaxis=dict(tickvals=x,
                                          ticktext=["" for i in range(len(x))],
                                          title="",
                                          color=self.config['textcolor'],
                                          showgrid=False,
                                          zeroline=False,
                                          ),
                               yaxis=dict(showgrid=False,
                                          title="",
                                          visible=False)
                               )
        self.fig.update_traces(textfont_color=self.config["textcolor"],
                               mode="lines+markers+text",
                               line=dict(color=self.config["barcolor"]),
                               marker=dict(color=self.config["capcolor"]),
                               textposition='top center'
                               )

        self.graph.figure = self.fig

    def update_secondary(self, values):
        t = self._min_max_texts(values)
        existing_traces = list(self.fig.data)
        if len(existing_traces) > 1:
            existing_traces.pop(1)

        self.fig.data = existing_traces

        x = np.arange(len(values))
        secondary_fig = go.Scatter(x=x,
                                   y=values,
                                   mode="lines+markers+text",
                                   line=dict(color=self.config['comp-color-dark']),
                                   marker=dict(color=self.config['comp-color-bright']),
                                   textposition='top center',
                                   textfont_color=self.config["textcolor"],
                                   )

        self.fig.add_trace(secondary_fig)

    def _min_max_texts(self, values):
        x = np.arange(len(values))
        t = [""] * len(x)

        max_val = np.max(values)
        max_idx = np.argmax(values)
        t[max_idx] = str(max_val.item()) + " " + self.unit

        min_val = np.min(values)
        min_idx = np.argmin(values)
        t[min_idx] = str(min_val.item()) + " " + self.unit

        return t

    def clear_all(self):
        self.fig.data = ()


class CustomBar:
    def __init__(self, config, card_title, target_card, graph_id, update_freq=60600):
        self.config = config
        self.card = target_card
        self.cardheader = dbc.CardHeader(card_title, style={"textAlign": "center",
                                                            "padding": "0px",
                                                            "border": "0px",
                                                            "color": self.config['textcolor'],
                                                            "borderRadius": "0px"
                                                            })
        self.graph = dcc.Graph(className="graphs", id=graph_id)
        self.interval = dcc.Interval(
            id=graph_id + "-interval",
            interval=update_freq,
            n_intervals=0
        )
        self.card.children = [self.cardheader, self.graph, self.interval]
        self.fig = None

    def set_data(self, values, names, unit):
        x = np.arange(len(values))
        cap = np.ones(len(values)) * self.config['capsize']*np.max(values)
        ticktext = [str(i) + " " + unit for i in values]
        self.fig = px.bar(x=x, y=values)
        self.fig.update_traces(marker_color=self.config['barcolor'],
                               marker_line_color=self.config['barcolor'],
                               text=ticktext,
                               textposition="inside",
                               textfont_color=self.config["textcolor"],
                               )

        capfig = go.Bar(
            x=x,
            y=cap,
            marker_color=self.config['capcolor'],
            marker_line_color=self.config['capcolor']
        )

        self.fig.add_trace(capfig)

        self.fig.update_layout(margin=self.config["margin"],
                               xaxis=dict(tickvals=x,
                                          ticktext=names,
                                          title=None,
                                          color=self.config['textcolor']),
                               yaxis=dict(visible=False),
                               paper_bgcolor=self.config['bgcolor'],
                               plot_bgcolor=self.config['bgcolor'],
                               barmode="relative",
                               showlegend=False,
                               bargap=0.02
                               )

        self.graph.figure = self.fig


class CountdownSpinner:
    def __init__(self, config, card_title, target_card, graph_id, update_freq=1010):
        self.config = config
        self.card = target_card
        self.cardheader = dbc.CardHeader(card_title, style={"textAlign": "center",
                                                            "padding": "0px",
                                                            "border": "0px",
                                                            "color": self.config['textcolor'],
                                                            "borderRadius": "0px"
                                                            })
        self.fig = px.pie(values=[30, 30],
                          color_discrete_sequence=[self.config["capcolor"], self.config["barcolor"]]
                          )

        self.fig.update_traces(textinfo="none",
                               hole=0.95,
                               sort=False,
                               hoverinfo="skip",
                               hovertemplate=None
                               )

        self.fig.update_layout(margin=self.config["margin"],
                               paper_bgcolor=self.config['bgcolor'],
                               plot_bgcolor=self.config['bgcolor'],
                               showlegend=False,
                               annotations=[dict(text="",
                                                 font_color=self.config["textcolor"],
                                                 font_size=16, x=0.5, y=0.5,
                                                 showarrow=False)]
                               )

        self.graph = dcc.Graph(className="graphs", id=graph_id)
        self.graph.figure = self.fig
        self.interval = dcc.Interval(id="countdown-timer-id", interval=update_freq, n_intervals=0)
        self.card.children = [self.cardheader, self.graph, self.interval]

    def increment(self, time_elapsed, time_remaining):
        self.fig.update_traces(
            values=[time_elapsed, time_remaining]
        )
        self.fig.update_layout(annotations=[dict(text=str(time_remaining),
                                                 font_color=self.config["textcolor"],
                                                 font_size=16, x=0.5, y=0.5, showarrow=False)]
                               )


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
        stat1 = dbc.Col(dbc.Row(card(), className="wrap-div"), className="stat-col", id="stat-1", style={"padding": 0})
        stat2 = dbc.Col(dbc.Row(card(), className="wrap-div"), className="stat-col", id="stat-2", style={"padding": 0})
        stat3 = dbc.Row(card(), className="substat-row", id="stat-3")
        stat4 = dbc.Row(card(), className="substat-row", id="stat-4")
        drop = DropDown()
        mapp = MapPane()
        hist = HistoricPlot()
        self.subpanels = [title.get_layout(), stat1, stat2, stat3, stat4, drop.get_layout(), mapp.get_layout(),
                          hist.get_layout()]

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

                    # drop.get_layout()
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
        self.layout = dbc.Col(dcc.Graph(id="scatter_map", className="graphs"), className="map-col", id="map-pane")

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
