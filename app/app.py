import dash
from dash import Dash, Input, Output, State, html, dcc

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
    ],
)

from common.sidebar import sidebar

app.layout = html.Div(
    className="d-flex",
    children=[
        # Le composant dcc.Store est utilisé pour stocker l'état de la sidebar (ouverte/fermée).
        dcc.Store(id="sidebar-state", data="visible"),
        # La barre latérale avec l'ID pour le callback
        html.Div(sidebar, id="sidebar-wrapper", className="sidebar"),
        html.Div(
            [
                # Bouton pour masquer/afficher la barre latérale
                html.Button(
                    id="toggle-button",
                    children=[html.I(className="fas fa-bars")],
                    className="btn btn-primary toggle-button",
                ),
                # Conteneur pour le contenu des pages
                dash.page_container,
            ],
            className="content-container",
        ),
    ],
)


# Callback pour basculer la visibilité de la sidebar
@app.callback(
    Output("sidebar-wrapper", "className"),
    Output("sidebar-state", "data"),
    Input("toggle-button", "n_clicks"),
    State("sidebar-state", "data"),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks, current_state):
    """
    Masque ou affiche la barre latérale en fonction de son état actuel.
    """
    if current_state == "visible":
        new_state = "hidden"
        new_class = "sidebar-hidden"
    else:
        new_state = "visible"
        new_class = "sidebar"
    return new_class, new_state


if __name__ == "__main__":
    app.run(debug=True)
