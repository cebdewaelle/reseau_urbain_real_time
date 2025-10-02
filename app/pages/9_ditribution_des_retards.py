import os
import pandas as pd
import numpy as np
from dash import html, dcc
import dash
import plotly.express as px
from dash.dependencies import Input, Output

dash.register_page(__name__)

BASEDIR_OUT = "./data/out/"
nomfic_export = os.path.join(BASEDIR_OUT, "current_data.csv")

# ---------- Lecture des données ----------
df = pd.read_csv(nomfic_export, delimiter=";")

# delay est en secondes → conversion en minutes
df["delay_min"] = df["delay"] / 60.0

# ---------- Layout ----------
layout = html.Div(
    [
        html.H1("Distribution des retards"),
        html.P("Histogramme des retards par bus (en minutes)"),
        dcc.Graph(id="delay-distr"),
    ],
    className="content",
)


# ---------- Callback ----------
@dash.callback(Output("delay-distr", "figure"), Input("delay-distr", "id"))
def update_hist(_):
    # bornes
    bins = [-15, -10, -5, -2, 0, 2, 5, 10, 15, 20, 30, 60]

    # Catégorisation en classes
    df["delay_class"] = pd.cut(df["delay_min"], bins=bins)
    df["delay_class_str"] = df["delay_class"].astype(str)

    # Comptage par classe
    agg = df["delay_class_str"].value_counts().sort_index().reset_index()
    agg.columns = ["delay_class_str", "count"]

    # Histogramme en barres
    fig = px.bar(
        agg,
        x="delay_class_str",
        y="count",
        title="Distribution des retards (minutes)",
        labels={
            "delay_class_str": "Classes de retard (minutes)",
            "count": "Nombre de bus",
        },
        text="count",
    )
    fig.update_traces(textposition="outside")

    return fig
