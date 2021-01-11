import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import layout_utils
import plotly.express as px
import plotly.graph_objects as go

import frontend_utils
import pandas as pd
import numpy as np

gmargin=dict(l=8,r=8,t=8,b=8)

df = pd.read_csv("../data/detectors-active.csv")
map_fig, map_data = frontend_utils.init_map(df)
map_fig.update_layout(paper_bgcolor="gray", margin=dict(l=0,r=0,b=0,t=0))



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
layout, left_column, right_column = layout_utils.init_layout()
right_column.get_subpanel_by_id('map-pane').children.figure=map_fig

cardheader=dbc.CardHeader("vehicle speed",style={"background":"#303030",
                                                 "text-align":"center",
                                                 "padding": 0,
                                                 "border":0})


speed_card=left_column.get_subpanel_by_id("vspeed").children
speed_graph=dcc.Graph(id="speed-graph",className="graphs")

speed_card.children=[cardheader,speed_graph]




places=["Pie-IX","Letourneux","Viau","Dickson","Boussuet","de Boucherville", "Curatteau","des Futailles", "Haig"]
x=np.arange(len(places))
values=np.random.randint(10,40,len(places))
cap=np.ones(len(values))*0.5

fig=px.bar(x=x,y=values)
fig.update_traces(marker_color="#2d4e4f",
                  marker_line_color="#2d4e4f",
                  text=[str(i)+" kmh" for i in values],
                  textposition="inside",
                  textfont_color="white",
                  )

fig2=go.Bar(
    x=x,
    y=cap,
    marker_color="#00a99d",
    marker_line_color="#00a99d"

)

fig.add_trace(fig2)
fig.update_layout(margin=gmargin,
                  xaxis=dict(tickvals=x,ticktext=["station "+str(i+1) for i in x],title=None,color="white"),
                  yaxis=dict(visible=False),
                  paper_bgcolor="#303030",
                  plot_bgcolor="#303030",
                  barmode="relative",
                  showlegend=False,
                  bargap=0.02
                  )

speed_graph.figure=fig

app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
