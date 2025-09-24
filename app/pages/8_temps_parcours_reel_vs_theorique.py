import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import os
import pandas as pd


dash.register_page(__name__)


layout = (
    html.Div(
        [
            html.H1("Temps de parcours réel vs théoriques"),
            html.Hr(),
        ],
        className="content",
    ),
)
