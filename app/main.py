import pandas as pd
from dash import Dash, dcc, html, dash_table, page_container

from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import os

BASEDIR_OUT = "./data/out/"
nomfic_export = os.path.join(BASEDIR_OUT, "current_data.csv")

df = pd.read_csv(nomfic_export, delimiter=";")

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.MATERIA, dbc.icons.FONT_AWESOME],
)


# sidebar = html.Div(
#     [
#         html.Div(
#             [
#                 html.H2("Auto ML", style={"color": "white"}),
#             ],
#             className="sidebar-header",
#         ),
#         dbc.Nav(
#             [
#                 dbc.NavLink(
#                     [html.I(className="fas fa-home me-2"), html.Span("Dashboard")],
#                     href="/",
#                     active="exact",
#                 ),
#                 dbc.NavLink(
#                     [
#                         html.I(className="fas fa-calendar-alt me-2"),
#                         html.Span("Projects"),
#                     ],
#                     href="/projects",
#                     active="exact",
#                 ),
#                 dbc.NavLink(
#                     [
#                         html.I(className="fas fa-envelope-open-text me-2"),
#                         html.Span("Datasets"),
#                     ],
#                     href="/datasets",
#                     active="exact",
#                 ),
#             ],
#             vertical=True,
#             pills=True,
#         ),
#     ],
#     className="sidebar",
# )


# Liste des routes uniques pour le premier dropdown
route_options = [{"label": i, "value": i} for i in df["route_id"].unique()]


app.layout = html.Div(
    className="container",
    children=[
        html.Div(
            [
                html.Div(
                    [
                        html.H2("Boards", style={"color": "white"}),
                    ],
                    className="sidebar-header",
                ),
                html.Div(
                    [
                        html.A(
                            [
                                html.I(className="fas fa-home me-2"),
                                html.Span("Données Globales"),
                            ],
                            href="/global",
                        ),
                        html.A(
                            [
                                html.I(className="fas fa-calendar-alt me-2"),
                                html.Span("Retards"),
                            ],
                            href="/retards",
                        ),
                        # html.A(
                        #     [
                        #         html.I(className="fas fa-envelope-open-text me-2"),
                        #         html.Span("Datasets"),
                        #     ],
                        #     href="#",
                        # ),
                    ],
                    className="sidebar-nav",
                ),
            ],
            className="sidebar",
        ),
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
                    columns=[{"name": i, "id": i} for i in df.columns],
                    page_size=30,
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
    ],
)


# Callback pour mettre à jour les options du dropdown 'trip_id' en fonction de 'route_id'
@app.callback(Output("trip-dropdown", "options"), Input("route-dropdown", "value"))
def set_trips_options(selected_route):
    if not selected_route:
        return []

    filtered_df = df[df["route_id"] == selected_route]
    trip_options = filtered_df["trip_id"].unique()
    return [{"label": i, "value": i} for i in trip_options]


# Callback pour mettre à jour la table en fonction de 'trip_id' (et 'route_id')
@app.callback(
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


if __name__ == "__main__":
    app.run(debug=True)
