import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import os
import plotly.express as px
import pandas as pd


BASEDIR_OUT = "./data/out/"
nomfic_export = os.path.join(BASEDIR_OUT, "current_data.csv")

df = pd.read_csv(nomfic_export, delimiter=";")


dash.register_page(__name__)

layout = html.Div(
    [
        html.H1("Retards moyens au cours de la journée"),
        html.Div(f"retard moyen: {df['delay'].mean()}"),
    ]
)


# layout = html.Div(
#     [
#         html.H1("Retards moyens au cours de la journée"),
#         dcc.Graph(id="retards_moyens"),
#         dcc.Checklist(
#             id="checklist",
#             options=None,
#             value=None,
#         ),
#     ]
# )


# @dash.callback(Output("retards_moyens", "figure"), Input("checklist", "value"))
# def update_line_chart(trip_ids):
#     mask = df["delay"].mean()
#     fig = px.line(
#         df[mask],
#         x="time",
#         y="retard moyen",
#         title="Retards moyens",
#     )
#     return fig
