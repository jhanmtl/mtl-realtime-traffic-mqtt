import numpy as np
import dash_table
import plotly.graph_objects as go
import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import frontend_utils
import pandas as pd


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
        self.table_div=html.Div(id="table-div")
        self.df=None

    def set_data(self, df=None):
        if df is not None:
            self.df=df
        c = [{"name": i, "id": i} for i in self.df.columns]
        self.table = dash_table.DataTable(data=self.df.to_dict('records'),
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
        self.table_div.children=self.table
        self.card.children = [self.cardheader, self.table_div]

    def refresh(self):
        self.set_data()



class CustomDropdown:
    def __init__(self, options):
        self.options = options

        self.dropdown0 = dcc.Dropdown(
            id='drop-0',
            value="speed",
            options=[{"label": o, 'value': o} for o in ["speed", "count", "gap time"]],
            clearable=False,
        )

        self.dropdown1 = dcc.Dropdown(
            id='drop-1',
            value="station 1",
            options=[{"label": o, 'value': o} for o in self.options],
            clearable=False,
        )
        self.dropdown2 = dcc.Dropdown(
            id='drop-2',
            value="station 2",
            options=[{"label": o, 'value': o} for o in self.options],
            clearable=False,
        )

        self.layout = dbc.Row([
            dbc.Col(self.dropdown1, width={"size": 3, "offset": 2}),
            dbc.Col(self.dropdown2, width={"size": 3}),
            dbc.Col(self.dropdown0, width={"size": 2})
        ],
            style={"marginTop": 32, "textAlign": "center"}
        )


class CustomSlider:
    def __init__(self, default_range=120, min_gap=60, cid="cust-slider"):
        self.default_range = default_range
        self.min_gap = min_gap
        self.id = cid

        self.layout = None
        self.slider = None
        self.handle_left = None
        self.handle_right = None
        self.labels = None

    def set_labels(self, labels):
        self.labels = labels
        x = np.arange(len(labels))
        self.slider = dcc.RangeSlider(id=self.id,
                                      min=x[0],
                                      max=x[-1],
                                      value=[x[-1] - self.default_range + 1, x[-1]],
                                      step=1,
                                      pushable=self.min_gap,
                                      updatemode="drag"
                                      )

        self.handle_left = html.Div(children="val", id="left-marker")
        self.handle_right = html.Div(children="val", id="right-marker")

        self.layout = html.Div([
            self.handle_left,
            self.handle_right,
            self.slider
        ], style={"position": "relative", "width": "85%", "marginLeft": "11.5%", "marginBottom": "32px"})


class CustomScatter:
    def __init__(self, config):
        self.config = config

        self.unit = None
        self.labels = None

        self.graph = dcc.Graph(className="graphs", id="hist-plot")
        self.base_fig = go.Figure()
        self.base_fig.update_layout(
            margin=self.config["margin"],
            paper_bgcolor=self.config['bgcolor'],
            plot_bgcolor=self.config['bgcolor'],
            showlegend=False,
            xaxis=dict(title="",
                       color=self.config['textcolor'],
                       tickvals=[None],
                       ticktext=[""],
                       showgrid=False,
                       zeroline=False,
                       ),
            yaxis=dict(showgrid=False,
                       visible=True,
                       tickfont={"color": "#7a7a7a"},
                       rangemode="tozero",
                       zeroline=False,

                       ),
            font_color="#7a7a7a"
        )

        self.primary_data = None
        self.secondary_data = None

        self.primary_fig = None
        self.secondary_fig = None

        self.graph.figure = self.base_fig

    def set_unit(self, unit):
        self.unit = unit
        self.base_fig.update_layout(
            title=dict(
                text=self.unit,
                x=0.0,
                y=1.0,
                xanchor="left",
                yanchor="top"
            )
        )

    def set_labels(self, labels):
        self.labels = labels

    def set_primary_data(self, primary_data):
        x = np.arange(len(primary_data))
        self.primary_data = primary_data
        self.primary_fig = self._make_fig(x, self.primary_data, self.labels, "barcolor", "capcolor")
        self.base_fig.add_trace(self.primary_fig)

    def set_secondary_data(self, secondary_data):
        x = np.arange(len(secondary_data))
        self.secondary_data = secondary_data
        self.secondary_fig = self._make_fig(x, self.secondary_data, self.labels, "comp-color-dark", "comp-color-bright")
        self.base_fig.add_trace(self.secondary_fig)

    def update_primary_data(self, new_primary_data):
        self.primary_data = new_primary_data
        self.base_fig.data = self.base_fig.data[:1]
        self.set_primary_data(self.primary_data)

    def update_secondary_data(self, new_secondary_data):
        self.secondary_data = new_secondary_data
        self.base_fig.data = self.base_fig.data[1:]
        self.set_secondary_data(self.secondary_data)

    def zoom_in(self, start, end):
        end += 1
        windowed_primary = self.primary_data[start:end]
        windowed_secondary = self.secondary_data[start:end]
        windowed_label = self.labels[start:end]
        windowed_x = np.arange(len(windowed_label))

        self.primary_fig = self._make_fig(windowed_x, windowed_primary, windowed_label, "barcolor", "capcolor")
        self.secondary_fig = self._make_fig(windowed_x, windowed_secondary, windowed_label, "comp-color-dark",
                                            "comp-color-bright")

        self.base_fig.data = []
        self.base_fig.add_trace(self.primary_fig)
        self.base_fig.add_trace(self.secondary_fig)

    def restore(self):
        self.base_fig.data = []
        self.set_primary_data(self.primary_data)
        self.set_secondary_data(self.secondary_data)

    def _make_fig(self, x, y, label, linecolor_key, markercolor_key):
        fig = go.Scatter(
            x=x,
            y=y,
            textfont_color=self.config["textcolor"],
            mode="lines+markers+text",
            line=dict(color=self.config[linecolor_key]),
            marker=dict(color=self.config[markercolor_key]),
            textposition='top center',
            customdata=label,
            hovertemplate='Time: %{customdata}<br>Reading: %{y} ' + self.unit,
            name=""
        )

        return fig


class CustomBar:
    def __init__(self, config, card_title, target_card, graph_id):
        self.config = config
        self.card = target_card
        self.cardheader = dbc.CardHeader(card_title, style={"textAlign": "center",
                                                            "padding": "0px",
                                                            "border": "0px",
                                                            "color": self.config['textcolor'],
                                                            "borderRadius": "0px"
                                                            })
        self.graph = dcc.Graph(className="graphs", id=graph_id)
        self.card.children = [self.cardheader, self.graph]
        self.fig = None

    def set_data(self, values, names, unit):
        x = np.arange(len(values))
        cap = np.ones(len(values)) * self.config['capsize'] * np.max(values)
        threshold = 0.2 * np.max(values)
        inside_ticktext = [str(i) + " " + unit if i > threshold else "" for i in values]
        outside_ticktext = [str(i) + " " + unit if i <= threshold else "" for i in values]

        self.fig = px.bar(x=x, y=values)
        self.fig.update_traces(marker_color=self.config['barcolor'],
                               marker_line_color=self.config['barcolor'],
                               text=inside_ticktext,
                               textposition="outside",
                               textfont_color=self.config["textcolor"],
                               )

        capfig = go.Bar(
            x=x,
            y=cap,
            marker_color=self.config['capcolor'],
            marker_line_color=self.config['capcolor'],
            text=outside_ticktext,
            textposition="outside",
            textfont_color=self.config['textcolor']
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
    def __init__(self, config, card_title, target_card, graph_id):
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
        self.card.children = [self.cardheader, self.graph]

    def increment(self, time_elapsed, time_remaining):
        self.fig.update_traces(
            values=[time_elapsed, time_remaining]
        )
        self.fig.update_layout(annotations=[dict(text=str(time_remaining),
                                                 font_color=self.config["textcolor"],
                                                 font_size=16, x=0.5, y=0.5, showarrow=False)]
                               )

class TimeStamp:
    def __init__(self, config, card_title, target_card):
        self.config = config
        self.card = target_card
        self.cardheader = dbc.CardHeader(card_title, style={"textAlign": "center",
                                                            "padding": "0px",
                                                            "border": "0px",
                                                            "color": self.config['textcolor'],
                                                            "borderRadius": "0px"
                                                            })
        self.stamp=""
        self.text=html.H4(children=self.stamp,id="timestamp-text", style={"textAlign":"center", "height":"100%"})
        self.card.children = [self.cardheader, html.Div(self.text, style={"margin":"auto"})]

    def update_time(self,newstamp):
        newstamp = frontend_utils.date_convert(newstamp)
        newstamp = newstamp.strftime("%H:%M:%S")
        self.stamp=newstamp



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
