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
nomfic_export = os.path.join(BASEDIR_OUT, f"delays_routes_{today_str}.csv")

df = pd.read_csv(nomfic_export, delimiter=";")

df["execution_date"] = pd.to_datetime(df["execution_date"], format="%H:%M:%S").dt.time

df["execution_datetime"] = pd.to_datetime(
    today_str_tirets + " " + df["execution_date"].astype(str),
    format="%Y-%m-%d %H:%M:%S",
)

# On ne garde que le dernier relevé
last_exec = df["execution_datetime"].max()
df_last = df[df["execution_datetime"] == last_exec]


dash.register_page(__name__)

fig = px.bar(
    df_last,
    x="route_id",
    y="delai_moyen",
    text="delai_moyen",
    title="Délai moyen par route (dernier relevé)",
)

fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig.update_layout(yaxis_title="Délai moyen (seondes)", xaxis_title="Route")

layout = html.Div(
    [
        html.H1("Suivi des délais moyens par route (dernier relevé)"),
        dcc.Graph(figure=fig, style={"height": "80vh"}),
    ]
)
