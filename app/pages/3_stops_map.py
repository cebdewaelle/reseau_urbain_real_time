import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import os
import plotly.express as px
import pandas as pd
from datetime import datetime
import pytz


gtfs_tz = pytz.timezone("Europe/Paris")
now_local = datetime.now(gtfs_tz)
today_str = now_local.strftime("%Y%m%d")
today_str_tirets = now_local.strftime("%Y-%m-%d")

BASEDIR_OUT = "./data/out/"
nomfic_export = os.path.join(BASEDIR_OUT, "current_data.csv")

df = pd.read_csv(nomfic_export, delimiter=";")

dash.register_page(__name__)

fig = px.scatter_map(
    df,
    lat="stop_lat",
    lon="stop_lon",
    color="route_id",
    text="stop_name",
    color_continuous_scale=px.colors.cyclical.IceFire,
    zoom=10,
)


layout = (
    html.Div(
        [
            html.H1("Carte des arrêts"),
            dcc.Graph(figure=fig),
        ],
        className="content",
    ),
)
