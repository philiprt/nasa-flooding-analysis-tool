from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def generate_htf_projection_page(init):

    return html.Div(
        id="projected-flooding",
        className="app-page hidden-app-page",
        children=[
            html.Div(
                id="annual-projection-section",
                className="app-page-section container",
                children=generate_annual_projection_section(init),
            ),
            html.Div(
                id="pentadal-projection-section",
                className="app-page-section container",
                children=generate_pentadal_projection_section(init),
            ),
        ],
    )


def generate_annual_projection_section(init):

    return (
        dbc.Row(
            class_name="gx-5",
            justify="between",
            children=[
                dbc.Col(
                    md=12,
                    lg=9,
                    children=html.Div(
                        id="htf-outer",
                        children=[
                            html.H3(
                                children=[
                                    "Projected Flooding Days",
                                    html.Span(
                                        dbc.Button(
                                            html.I(className="bi bi-info-circle me-2"),
                                            color="link",
                                            id="projected-graph-info-button",
                                            className="info-button-graph",
                                        ),
                                    ),
                                ],
                                className="graph-title",
                            ),
                            html.P(
                                children=[
                                    html.Div(
                                        className="graph-subtitle-float",
                                        children=html.H6(
                                            children=[
                                                "SLR scenario: ",
                                                html.Span(
                                                    id="htf-graph-title-scenario",
                                                    className="graph-subtitle-option",
                                                ),
                                            ],
                                        ),
                                    ),
                                    html.Div(
                                        className="graph-subtitle-float",
                                        children=html.H6(
                                            children=[
                                                "Flooding threshold: ",
                                                html.Span(
                                                    id="htf-graph-title-threshold",
                                                    className="graph-subtitle-option",
                                                ),
                                            ],
                                        ),
                                    ),
                                    html.Div(style=dict(clear="both")),
                                ],
                                className="graph-subtitle",
                            ),
                            dcc.Loading(
                                id="htf-loading",
                                children=dcc.Graph(
                                    id="htf-graph",
                                    figure=init["graph"],
                                    config=dict(displaylogo=False, displayModeBar=True),
                                    clear_on_unhover=True,
                                ),
                            ),
                        ],
                    ),
                ),
                dbc.Col(
                    # sm=12,
                    md=12,
                    lg=3,
                    xl=3,
                    children=html.Div(
                        id="clim-outer",
                        children=[
                            html.H3(
                                children=[
                                    "Monthly",
                                    html.Span(
                                        dbc.Button(
                                            html.I(className="bi bi-info-circle me-2"),
                                            color="link",
                                            id="climatology-graph-info-button",
                                            className="info-button-graph",
                                        ),
                                    ),
                                ],
                                className="graph-title",
                            ),
                            html.P(
                                html.H6(
                                    children=[
                                        "In the year ",
                                        html.Span(
                                            init["year"],
                                            id="clim-year",
                                            className="graph-subtitle-option",
                                        ),
                                    ],
                                ),
                                className="graph-subtitle",
                            ),
                            dcc.Graph(
                                id="clim-graph",
                                figure=init["graph"],
                                config=dict(displaylogo=False, displayModeBar=False),
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )


def generate_pentadal_projection_section(init):

    return (
        dbc.Row(
            class_name="gx-5 gy-4",
            justify="between",
            children=[
                dbc.Col(
                    md=12,
                    xl=6,
                    children=html.Div(
                        id="htf-analysis-section",
                        className="analysis-content common-text",
                        children=[
                            html.H3(children="Analysis", className="sidebar-title"),
                            html.H6(
                                "Interpreting the Flooding Days projections",
                                className="analysis-subtitle",
                            ),
                            dcc.Markdown(
                                "The graphs above show how the **frequency of flooding will evolve** during the 21st century for the selected location, threshold, and scenario. The first graph shows number of flooding days per year, while the second graph shows how the flooding days are distributed within a future year. The *likely* and *very likely* ranges provide a range of possibilities accounting for unpredictable natural fluctuations in sea level and storminess.",
                                style={"margin-top": "1em"},
                            ),
                            html.Div(
                                id="htf-analysis-content",
                                className="analysis-content",
                                children=[
                                    html.Div(
                                        id="htf-chronic-analysis",
                                        className="analysis-highlight",
                                        children=[
                                            dcc.Markdown(
                                                children=[
                                                    "##### Routine and chronic flooding\n",
                                                ]
                                            ),
                                            html.Div(
                                                id="htf-chronic-content", children=[],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        id="htf-yoi-analysis",
                                        className="analysis-highlight",
                                        children=[
                                            dcc.Markdown(
                                                id="htf-yoi-title",
                                                children=[
                                                    "##### Year of inflection (YOI)\n",
                                                ],
                                            ),
                                            html.Div(
                                                id="htf-yoi-toggle-container",
                                                children=[
                                                    dbc.Switch(id="yoi-toggle"),
                                                    html.H6(
                                                        "Show YOI on graph",
                                                        id="yoi-toggle-label",
                                                        className="app-options-title units-toggle-label",
                                                    ),
                                                ],
                                            ),
                                            html.Div("", style={"clear": "both"}),
                                            html.Div(
                                                id="htf-yoi-content", children=[],
                                            ),
                                            html.Div(
                                                children=[
                                                    "Note: This section of the analysis will only appear for combinations of location, threshold, and scenario where it is possible to perform the YOI analysis.",
                                                ],
                                                style={
                                                    "font-size": 11,
                                                    "margin-top": "1.5em",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                dbc.Col(
                    md=12,
                    xl=6,
                    children=html.Div(
                        className="sidebar",
                        children=[
                            html.H3(
                                children=[
                                    "Extreme Months",
                                    html.Span(
                                        dbc.Button(
                                            html.I(className="bi bi-info-circle me-2"),
                                            color="link",
                                            id="extreme-graph-info-button",
                                            className="info-button-graph",
                                        ),
                                    ),
                                ],
                                className="graph-title",
                            ),
                            html.P(
                                children=[
                                    html.Div(
                                        className="graph-subtitle-float",
                                        children=html.H6(
                                            children=[
                                                "SLR scenario: ",
                                                html.Span(
                                                    id="pent-graph-title-scenario",
                                                    className="graph-subtitle-option",
                                                ),
                                            ],
                                        ),
                                    ),
                                    html.Div(
                                        className="graph-subtitle-float",
                                        children=html.H6(
                                            children=[
                                                "Flooding threshold: ",
                                                html.Span(
                                                    id="pent-graph-title-threshold",
                                                    className="graph-subtitle-option",
                                                ),
                                            ],
                                        ),
                                    ),
                                    html.Div(style=dict(clear="both")),
                                ],
                                className="graph-subtitle",
                            ),
                            html.Div(
                                dcc.Loading(
                                    id="pent-loading",
                                    children=dcc.Graph(
                                        id="pent-graph",
                                        figure=init["graph"],
                                        config=dict(
                                            displaylogo=False, displayModeBar=True
                                        ),
                                    ),
                                ),
                            ),
                            html.Div(
                                id="xtrm-analysis-content",
                                className="common-text",
                                children=[],
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )
