# import dash
# from dash import html, dcc, dash_table
# from dash.dependencies import Input, Output
# import os
# import pandas as pd


# dash.register_page(__name__)


# BASEDIR_OUT = "./data/out/"
# nomfic_export = os.path.join(BASEDIR_OUT, "current_data.csv")

# df = pd.read_csv(nomfic_export, delimiter=";")

# dash.register_page(__name__)

# # Liste des routes uniques pour le premier dropdown
# route_options = [{"label": i, "value": i} for i in df["route_id"].unique()]


# layout = (
#     html.Div(
#         [
#             html.H1("Graphe des données de retard"),
#             html.Div(
#                 [
#                     html.Div(
#                         [
#                             html.Label("Sélectionnez une route :"),
#                             dcc.Dropdown(
#                                 id="route-dropdown-8",
#                                 options=route_options,
#                                 value=None,
#                                 placeholder="Sélectionnez une route",
#                             ),
#                         ],
#                         style={"width": "48%", "display": "inline-block"},
#                     ),
#                     html.Div(
#                         [
#                             html.Label("Sélectionnez un trip :"),
#                             dcc.Dropdown(
#                                 id="trip-dropdown-8",
#                                 value=None,
#                                 placeholder="Sélectionnez un trip",
#                             ),
#                         ],
#                         style={
#                             "width": "48%",
#                             "display": "inline-block",
#                             "float": "right",
#                         },
#                     ),
#                 ]
#             ),
#             html.Hr(),
#         ],
#         className="content",
#     ),
# )


# # Callback pour mettre à jour les options du dropdown 'trip_id' en fonction de 'route_id'
# @dash.callback(Output("trip-dropdown-8", "options"), Input("route-dropdown-8", "value"))
# def set_trips_options_fr(selected_route):
#     if not selected_route:
#         return []

#     filtered_df = df[df["route_id"] == selected_route]
#     trip_options = filtered_df["trip_id"].unique()
#     return [{"label": i, "value": i} for i in trip_options]


# # Callback pour mettre à jour la table en fonction de 'trip_id' (et 'route_id')
# @dash.callback(
#     Output("datatable", "data"),
#     Input("route-dropdown-8", "value"),
#     Input("trip-dropdown-8", "value"),
# )
# def update_graph(selected_route, selected_trip):
#     dff = df

#     if selected_route:
#         dff = dff[dff["route_id"] == selected_route]

#     if selected_trip:
#         dff = dff[dff["trip_id"] == selected_trip]

#     return dff.to_dict("records")


import os
import pandas as pd
import numpy as np
from dash import html, dcc, dash_table, callback_context
from dash.dependencies import Input, Output
import plotly.express as px
import dash

dash.register_page(__name__)

BASEDIR_OUT = "./data/out/"
nomfic_export = os.path.join(BASEDIR_OUT, "current_data.csv")

# ---------- Lecture + préparation ----------
# lire le CSV (délimiteur ;)
df = pd.read_csv(nomfic_export, delimiter=";")

# colonnes datetime parsing (elles ont offset +02:00 dans le CSV)
for col in ["realtime_arrival", "planned_arrival"]:
    df[col] = pd.to_datetime(df[col], utc=True)  # parse en tz-aware (converti en UTC)
# si tu veux garder l'affichage en timezone Europe/Paris, tu peux:
# df["realtime_arrival_paris"] = df["realtime_arrival"].dt.tz_convert("Europe/Paris")

# assure tri correct par trip et stop_sequence
df = df.sort_values(["route_id", "trip_id", "stop_sequence"]).reset_index(drop=True)

# convertir stop_sequence en int si nécessaire
df["stop_sequence"] = df["stop_sequence"].astype(int)

# ---------- Calcul du temps de parcours par tronçon ----------
# On crée des colonnes qui représentent le temps (en secondes) entre deux arrêts successifs
# pour chaque trip_id : scheduled_travel_s, actual_travel_s

# shift au niveau du même trip
df["planned_prev"] = df.groupby("trip_id")["planned_arrival"].shift(1)
df["realtime_prev"] = df.groupby("trip_id")["realtime_arrival"].shift(1)
df["stop_prev"] = df.groupby("trip_id")["stop_id"].shift(1)
df["stop_name_prev"] = df.groupby("trip_id")["stop_name"].shift(1)
df["stop_seq_prev"] = df.groupby("trip_id")["stop_sequence"].shift(1)

# calculs en secondes (na pour le premier arrêt d'un trip)
df["scheduled_travel_s"] = (
    df["planned_arrival"] - df["planned_prev"]
).dt.total_seconds()
df["actual_travel_s"] = (
    df["realtime_arrival"] - df["realtime_prev"]
).dt.total_seconds()

# tronçon id (ex: "from_stopid-to_stopid" ou basé sur stop_sequence)
df["segment_id"] = df.apply(
    lambda r: (
        f"{int(r['stop_seq_prev'])}->{int(r['stop_sequence'])}"
        if pd.notnull(r["stop_seq_prev"])
        else np.nan
    ),
    axis=1,
)

# écart actual - scheduled (positif = plus lent que prévu)
df["delta_s"] = df["actual_travel_s"] - df["scheduled_travel_s"]

# on peut nettoyer les valeurs négatives absurdes ou temps nuls si besoin (optionnel)
# ex: ignorer segments où scheduled_travel_s <= 0 or actual_travel_s <= 0
df.loc[
    (df["scheduled_travel_s"] <= 0) | (df["actual_travel_s"] <= 0),
    ["scheduled_travel_s", "actual_travel_s", "delta_s"],
] = np.nan

# ---------- Préparer options dropdown ----------
route_options = [{"label": r, "value": r} for r in df["route_id"].unique()]

# ---------- Layout Dash ----------
layout = html.Div(
    [
        html.H1("Analyse temps de parcours — réel vs théorique"),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Sélectionnez une route :"),
                        dcc.Dropdown(
                            id="route-dropdown-8",
                            options=route_options,
                            value=None,
                            placeholder="Sélectionnez une route",
                        ),
                    ],
                    style={"width": "48%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        html.Label("Sélectionnez un trip :"),
                        dcc.Dropdown(
                            id="trip-dropdown-8",
                            value=None,
                            placeholder="Sélectionnez un trip",
                        ),
                    ],
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "float": "right",
                    },
                ),
            ]
        ),
        html.Hr(),
        html.Div(
            [
                dcc.Graph(id="segment-delta-line", style={"height": "420px"}),
                dcc.Graph(id="delta-hist", style={"height": "320px"}),
            ],
            style={"display": "grid", "gridTemplateColumns": "1fr", "gap": "12px"},
        ),
        html.Hr(),
        html.H3("Données filtrées (tronçons)"),
        dash_table.DataTable(
            id="datatable",
            columns=[
                {"name": c, "id": c}
                for c in [
                    "trip_id",
                    "route_id",
                    "segment_id",
                    "stop_seq_prev",
                    "stop_sequence",
                    "stop_name_prev",
                    "stop_name",
                    "scheduled_travel_s",
                    "actual_travel_s",
                    "delta_s",
                ]
            ],
            data=[],
            page_size=15,
            sort_action="native",
            filter_action="native",
            style_table={"overflowX": "auto"},
        ),
    ],
    className="content",
)


# ---------- Callbacks ----------
@dash.callback(Output("trip-dropdown-8", "options"), Input("route-dropdown-8", "value"))
def set_trips_options_fr(selected_route):
    if not selected_route:
        return []
    filtered_df = df[df["route_id"] == selected_route]
    trip_options = filtered_df["trip_id"].unique()
    return [{"label": i, "value": i} for i in trip_options]


@dash.callback(
    Output("datatable", "data"),
    Output("segment-delta-line", "figure"),
    Output("delta-hist", "figure"),
    Input("route-dropdown-8", "value"),
    Input("trip-dropdown-8", "value"),
)
def update_graph(selected_route, selected_trip):
    dff = df.copy()

    if selected_route:
        dff = dff[dff["route_id"] == selected_route]
    if selected_trip:
        dff = dff[dff["trip_id"] == selected_trip]

    # On se limite aux tronçons (dropna sur segment_id)
    segs = dff.dropna(subset=["segment_id"]).copy()

    # Si un trip précis est sélectionné -> on affiche la courbe pour ce trip (delta par tronçon)
    if selected_trip:
        # ordre par stop_sequence
        segs = segs.sort_values("stop_sequence")
        # figure ligne : x=segment_id (ou stop_sequence), y=delta_s (en s)
        fig_line = px.line(
            segs,
            x="segment_id",
            y="delta_s",
            markers=True,
            title=f"Écart (actual - scheduled) par tronçon — trip {selected_trip} (secondes)",
            labels={"delta_s": "delta (s)", "segment_id": "tronçon"},
        )
        # histogramme des deltas pour ce trip
        fig_hist = px.histogram(
            segs,
            x="delta_s",
            nbins=30,
            title=f"Histogramme des écarts (s) — trip {selected_trip}",
            labels={"delta_s": "delta (s)"},
        )
    else:
        # Aucune trip sélectionné : on agrège par route et segment (moyenne)
        # pour repérer où se concentrent les ralentissements sur la ligne
        agg = (
            segs.groupby("segment_id")
            .agg(
                avg_delta_s=("delta_s", "mean"),
                count=("delta_s", "count"),
                avg_scheduled_s=("scheduled_travel_s", "mean"),
                avg_actual_s=("actual_travel_s", "mean"),
            )
            .reset_index()
            .sort_values("segment_id")
        )
        if agg.empty:
            fig_line = px.line(title="Pas de données pour la route sélectionnée")
            fig_hist = px.histogram(title="Pas de données pour la route sélectionnée")
        else:
            fig_line = px.bar(
                agg,
                x="segment_id",
                y="avg_delta_s",
                title=f"Moyenne (actual - scheduled) par tronçon — route {selected_route} (s)",
                labels={"avg_delta_s": "avg delta (s)", "segment_id": "tronçon"},
            )
            # histogramme : distribution globale des deltas pour la route
            fig_hist = px.histogram(
                segs,
                x="delta_s",
                nbins=40,
                title=f"Histogramme des écarts (s) — route {selected_route}",
                labels={"delta_s": "delta (s)"},
            )

    # préparer la table : sélectionner colonnes d'intérêt et dropna
    table_df = segs[
        [
            "trip_id",
            "route_id",
            "segment_id",
            "stop_seq_prev",
            "stop_sequence",
            "stop_name_prev",
            "stop_name",
            "scheduled_travel_s",
            "actual_travel_s",
            "delta_s",
        ]
    ].copy()
    # arrondir colonnes temporelles
    table_df["scheduled_travel_s"] = table_df["scheduled_travel_s"].round(1)
    table_df["actual_travel_s"] = table_df["actual_travel_s"].round(1)
    table_df["delta_s"] = table_df["delta_s"].round(1)

    return table_df.to_dict("records"), fig_line, fig_hist
