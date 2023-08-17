from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def generate_obs_flood_page(init):

    return html.Div(
        id="observed-flooding",
        className="app-page hidden-app-page",
        children=[
            html.Div(
                id="obs-flood-section",
                className="app-page-section container",
                children=generate_obs_flood_section(init),
            ),
            html.Div(
                id="attribution-section",
                className="app-page-section container",
                children=generate_attribution_section(init),
            ),
        ],
    )


def generate_obs_flood_section(init):

    return [
        html.H3(
            children=[
                "Observed flooding days",
                html.Span(
                    dbc.Button(
                        html.I(className="bi bi-info-circle me-2"),
                        color="link",
                        id="observed-graph-info-button",
                        className="info-button-graph",
                    ),
                ),
            ],
            className="graph-title",
        ),
        html.H6(
            children=[
                "Data source: ",
                html.A(
                    id="coops-station-link",
                    children=[
                        "NOAA CO-OPS Station ",
                        html.Span(children="", id="coops-station-id"),
                    ],
                    href="",
                    target="_blank",
                ),
            ],
            className="graph-subtitle",
        ),
        html.Div(
            id="obs-flood-loading-outer",
            children=[
                dcc.Loading(
                    id="obs-flood-loading",
                    children=dcc.Graph(
                        id="obs-flood-graph",
                        figure=init["graph"],
                        config=dict(displaylogo=False, displayModeBar=True),
                    ),
                )
            ],
        ),
    ]


def generate_attribution_section(init):

    return [
        # dbc.Row(
        #     class_name="g-0",
        #     children=[
        #         dbc.Col(
        #             width=12,
        #             children=[
        #                 html.H3(
        #                     children=[
        #                         "Attribution",
        #                         # html.I(
        #                         #     className="bi bi-info-circle me-2",
        #                         #     style={
        #                         #         "margin-left": "20px",
        #                         #         "font-size": "0.7em",
        #                         #     },
        #                         # ),
        #                     ],
        #                     className="graph-title",
        #                 ),
        #                 html.P(
        #                     children="What caused the observed floods?",
        #                     className="graph-subtitle",
        #                 ),
        #             ],
        #         ),
        #     ],
        # ),
        dbc.Row(
            class_name="gx-5 gy-4",
            justify="between",
            children=[
                dbc.Col(
                    xs=12,
                    lg=7,
                    children=html.Div(
                        id="obs-flood-analysis-container",
                        className="analysis-section",
                        children=[
                            html.H3(children="Analysis", className="sidebar-title",),
                            html.H6(
                                children=[
                                    "For the ",
                                    html.B(
                                        children="", id="obs-flood-analysis-threshold"
                                    ),
                                    " threshold (current selection)",
                                ],
                                className="analysis-subtitle",
                            ),
                            html.Div(
                                id="obs-flood-analysis-content",
                                className="common-text analysis-content",
                                children=[],
                            ),
                        ],
                    ),
                ),
                dbc.Col(
                    xs=12,
                    lg=5,
                    children=html.Div(
                        className="sidebar",
                        children=[
                            html.H3(
                                children="Extreme water levels",
                                className="sidebar-title",
                            ),
                            # html.P(
                            #     children="What caused the observed floods?",
                            #     className="graph-subtitle",
                            # ),
                            html.P(
                                id="extremes-sidebar-text",
                                children=generate_extremes_content_text(),
                                className="sidebar-text",
                            ),
                            html.H5(
                                className="graph-title",
                                children=[
                                    html.Span(
                                        "Ten highest events for ",
                                        style={
                                            "float": "left",
                                            "padding-right": "0.25em",
                                        },
                                    ),
                                    html.Span(
                                        id="topten-location", style={"float": "left"},
                                    ),
                                    html.Div(style={"clear": "both"}),
                                ],
                            ),
                            html.H6(
                                "With comparison to extreme return periods",
                                # className="graph-subtitle",
                                style={"margin-top": "4px"},
                            ),
                            html.Div(
                                id="topten-table-container",
                                children=dash_table.DataTable(
                                    id="topten-table",
                                    columns=[
                                        {"name": "Date or Return Period", "id": "date"},
                                        {"name": "Height*", "id": "height"},
                                    ],
                                    data=None,
                                    cell_selectable=False,
                                    style_as_list_view=True,
                                    style_cell={"textAlign": "left"},
                                    style_header={"background-color": "#E7EBEF"},
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "#F3F5F7",
                                        },
                                        {
                                            "if": {"filter_query": "{type} = return"},
                                            "fontWeight": "bold",
                                        },
                                    ],
                                ),
                            ),
                            html.Div(
                                "*Above mean higher high water (MHHW)",
                                className="table-footnote",
                            ),
                        ],
                    ),
                ),
            ],
        ),
    ]


def generate_extremes_content_text():

    return (
        html.P(
            style={"margin-top": "10px"},
            children=[
                "The table below shows:",
                html.Ol(
                    children=[
                        html.Li(
                            children="Dates and observed water levels for the 10 most extreme events recorded at the selected location. Note that a single event might last multiple days, but the table below shows only one peak water level per event."
                        ),
                        html.Li(
                            children=[
                                "Heights associated with specific ",
                                html.A(
                                    # html.B("return periods"),
                                    "return periods",
                                    href="https://en.wikipedia.org/wiki/Return_period",
                                    target="_blank",
                                    # style={"text-decoration": "none"},
                                ),
                                ". The water level associated with a 10-year return period, for example, is the water level expected to be reached just once every 10 years on average.",
                            ]
                        ),
                    ],
                ),
                "At present, the water levels associated with these events are rare, but sea-level rise will cause these events to occur more frequently in the future. To see how the frequency will change, select a flooding threshold above similar to the events below, and use the ",
                html.I(dcc.Link("Sea-Level Rise", href="/sea-level-rise",)),
                " and ",
                html.I(dcc.Link("Projected Flooding", href="/projected-flooding",)),
                " tabs to generate projections of future occurrences.",
                # html.Ol(
                #     children=[
                #         html.Li(
                #             "Select a flooding threshold above associated with a specific return period (from the dropdown) or customize for a specific event."
                #         ),
                #         html.Li(
                #             [
                #                 "Select a sea-level rise scenario on the ",
                #                 html.I("Sea-Level Rise"),
                #                 " tab above.",
                #             ]
                #         ),
                #         html.Li(
                #             [
                #                 "View projected frequency of occurence on the ",
                #                 html.I("Projected Flooding"),
                #                 " tab above.",
                #             ]
                #         ),
                #     ],
                # ),
            ],
        ),
    )


def generate_attribution_content_text():

    return (
        dcc.Markdown(
            """
        ##### Ideas/thoughts for this section:
        * Results from Sida's paper
            * General attribution for all flooding events; need to think about whether what is presented should change depending on threshold.
            * Individual attribution for the largest events
                * NOAA provides the 10 highest daily max water levels from their API (see table to the right)
                * We can start with providing attribution for these largest events.
        * Results from Chris's AR paper
            * Process attribution (longshore/onshore winds, atmopsheric pressure, precipitiation, etc.) can be extended to all stations and times.
            * This could be coupled to Sida's analysis, and processes could also be decomposed into timescales using a similar methodology.
            * It would be cool to add maps of altimetry SSH, pressure, wind, precip to this page for the largest events.
                * Using NASA-MERRA for the atmospheric components would be a good way to tie in NASA data.
        * Is it equally or more useful from a practitioner's perspective to understand the causes of an individual event or to understand the causes for why one year/season experienced an unusual number of events?
        """,
            style={"margin-top": "25px"},
        ),
    )
