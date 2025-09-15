import dash
from dash import Input, Output, State, html, dcc


sidebar = html.Div(
    [
        html.Div(
            [
                html.H2("Boards", className="text-white"),
            ],
            className="sidebar-header",
        ),
        html.Div(
            [
                html.Div(
                    dcc.Link(
                        [
                            html.I(className=page.get("icon", "fas fa-circle")),
                            html.Span(page["name"], className="ms-2"),
                        ],
                        href=page["relative_path"],
                        className="sidebar-link",
                    )
                )
                for page in dash.page_registry.values()
            ],
            className="sidebar-nav",
        ),
    ],
    className="sidebar",
)
