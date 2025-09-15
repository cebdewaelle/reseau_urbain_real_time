import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import os
import pandas as pd


BASEDIR_OUT = "./data/out/"
nomfic_export = os.path.join(BASEDIR_OUT, "current_data.csv")

df = pd.read_csv(nomfic_export, delimiter=";")

dash.register_page(__name__, path="/")

# Liste des routes uniques pour le premier dropdown
route_options = [{"label": i, "value": i} for i in df["route_id"].unique()]


colnames = {
    "trip_id": "Trip",
    "route_id": "Route id",
    "stop_id": "Stop id",
    "realtime_arrival": "Heure d'arrivée",
    "planned_arrival": "Heure prévue",
    "delay": "Délai",
    "route_long_name": "Route",
    "stop_name": "Stop",
}

columns = [
    {
        "name": colnames.get(col_id, col_id),
        "id": col_id,
    }
    for col_id in df.columns
]

layout = (
    html.Div(
        [
            html.H1("Tableau des données globales"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Sélectionnez une route :"),
                            dcc.Dropdown(
                                id="route-dropdown",
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
                                id="trip-dropdown",
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
            dash_table.DataTable(
                id="datatable-interactivity",
                columns=columns,
                page_size=20,
                data=df.to_dict("records"),
                page_action="native",
                style_header={
                    "backgroundColor": "rgb(230, 230, 230)",
                    "fontWeight": "bold",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    }
                ],
            ),
        ],
        className="content",
    ),
)


# Callback pour mettre à jour les options du dropdown 'trip_id' en fonction de 'route_id'
@dash.callback(Output("trip-dropdown", "options"), Input("route-dropdown", "value"))
def set_trips_options(selected_route):
    if not selected_route:
        return []

    filtered_df = df[df["route_id"] == selected_route]
    trip_options = filtered_df["trip_id"].unique()
    return [{"label": i, "value": i} for i in trip_options]


# Callback pour mettre à jour la table en fonction de 'trip_id' (et 'route_id')
@dash.callback(
    Output("datatable-interactivity", "data"),
    Input("route-dropdown", "value"),
    Input("trip-dropdown", "value"),
)
def update_table(selected_route, selected_trip):
    if not selected_route:
        # Afficher tout le DataFrame si aucune route n'est sélectionnée
        return df.to_dict("records")

    # Filtrer par route
    dff = df[df["route_id"] == selected_route]

    # Si un trip est sélectionné, filtrer encore plus
    if selected_trip:
        dff = dff[dff["trip_id"] == selected_trip]

    return dff.to_dict("records")
