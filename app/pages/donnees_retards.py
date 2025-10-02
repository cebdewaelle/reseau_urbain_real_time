import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import os
import pandas as pd


BASEDIR_OUT = "./data/out/"
nomfic_export = os.path.join(BASEDIR_OUT, "current_data.csv")

df = pd.read_csv(nomfic_export, delimiter=";")
# Crée le DataFrame filtré pour cette page
df_filtered = df[df["delay"] > 0]

dash.register_page(__name__)

# Liste des routes uniques pour le premier dropdown
route_options = [{"label": i, "value": i} for i in df_filtered["route_id"].unique()]


colnames = {
    "trip_id": "Trip",
    "route_id": "Route id",
    "stop_id": "Stop id",
    "realtime_arrival": "Heure d'arrivée",
    "planned_arrival": "Heure prévue",
    "delay": "Retard (en s)",
    "route_long_name": "Route",
    "stop_name": "Stop",
}

columns = [
    {
        "name": colnames.get(col_id, col_id),
        "id": col_id,
        "sortable": True if col_id == "delay" else False,
    }
    for col_id in df.columns
]


non_sortable_column_ids = [col["id"] for col in columns if col.pop("sortable") is False]

table_css = [
    {
        "selector": f'th[data-dash-column="{col}"] span.column-header--sort',
        "rule": "display: none",
    }
    for col in non_sortable_column_ids
]


layout = (
    html.Div(
        [
            html.H1("Tableau des données de retard"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Sélectionnez une route :"),
                            dcc.Dropdown(
                                id="retards-route-dropdown",
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
                                id="retards-trip-dropdown",
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
                id="retards-datatable-interactivity",
                # columns=[{"name": i, "id": i} for i in df.columns],
                columns=columns,
                page_size=20,
                css=table_css,
                data=df_filtered.to_dict("records"),
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
                sort_action="native",
            ),
        ],
        className="content",
    ),
)


# Callback pour mettre à jour les options du dropdown 'trip_id' en fonction de 'route_id'
@dash.callback(
    Output("retards-trip-dropdown", "options"), Input("retards-route-dropdown", "value")
)
def set_trips_options(selected_route):
    if not selected_route:
        return []

    filtered_df = df_filtered[df_filtered["route_id"] == selected_route]
    trip_options = filtered_df["trip_id"].unique()
    return [{"label": i, "value": i} for i in trip_options]


# Callback pour mettre à jour la table en fonction de 'trip_id' (et 'route_id')
@dash.callback(
    Output("retards-datatable-interactivity", "data"),
    Input("retards-route-dropdown", "value"),
    Input("retards-trip-dropdown", "value"),
)
def update_table(selected_route, selected_trip):
    dff = df_filtered

    if selected_route:
        dff = dff[dff["route_id"] == selected_route]

    if selected_trip:
        dff = dff[dff["trip_id"] == selected_trip]

    return dff.to_dict("records")
