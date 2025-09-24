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


dash.register_page(__name__)


fig = px.line(
    df,
    x="execution_datetime",
    y="delai_moyen",
    color="route_id",
    markers=True,
    title="Évolution des délais moyens par ligne",
    labels={
        "execution_datetime": "Heure d'exécution",
        "delai_moyen": "Délai moyen (secondes)",
    },
)


layout = html.Div(
    [
        html.H1("Suivi des délais moyens par route"),
        dcc.Graph(figure=fig, style={"height": "80vh"}),
    ]
)
