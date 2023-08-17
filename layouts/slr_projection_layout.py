from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def generate_slr_page(init):

    return html.Div(
        id="sea-level-rise",
        className="app-page hidden-app-page",
        children=html.Div(
            className="container",
            children=dbc.Row(
                class_name="gx-5 gy-4",
                children=[
                    generate_slr_projection_section(init),
                    generate_slr_budget_section(init),
                    generate_slr_table_section(init),
                ],
            ),
        ),
    )


def generate_slr_projection_section(init):

    return dbc.Col(
        id="slr-outer",
        md=12,
        xl=8,
        children=[
            html.H3(
                children=[
                    "Local sea-level rise scenarios",
                    html.Span(
                        dbc.Button(
                            html.I(className="bi bi-info-circle me-2"),
                            color="link",
                            id="scenario-graph-info-button",
                            className="info-button-graph",
                        ),
                    ),
                ],
                className="graph-title",
            ),
            html.H6(
                children=[
                    "Source: ",
                    html.A(
                        "2022 U.S. Interagency Taskforce (ITF) Report",
                        href="https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report-sections.html",
                        target="_blank",
                        style={"text-decoration": "none"},
                    ),
                ],
                className="graph-subtitle",
            ),
            html.Div(
                id="slr-loading-outer",
                children=[
                    dcc.Loading(
                        id="slr-loading",
                        children=dcc.Graph(
                            id="slr-graph",
                            figure=init["graph"],
                            config=dict(displaylogo=False, displayModeBar=True),
                            clear_on_unhover=True,
                        ),
                    )
                ],
            ),
        ],
    )


def generate_slr_budget_section(init):

    return dbc.Col(
        id="slr-budget-outer",
        sm=12,
        md=10,
        lg=6,
        xl=4,
        children=[
            html.H3(
                children=[
                    "Contributions",
                    html.Span(
                        dbc.Button(
                            html.I(className="bi bi-info-circle me-2"),
                            color="link",
                            id="budget-graph-info-button",
                            className="info-button-graph",
                        ),
                    ),
                ],
                className="graph-title",
            ),
            html.H6(
                children=[
                    "In the year ",  # (selected scenario)",
                    html.Span(
                        init["year"],
                        id="slr-budget-year",
                        className="graph-subtitle-option",
                    ),
                    # dcc.Input(
                    #     id="slr-budget-year-input",
                    #     className="app-options-input",
                    #     type="number",
                    #     value=2100,
                    #     debounce=True,
                    # ),
                ],
                className="graph-subtitle",
            ),
            # html.P(
            #     children=[
            #         "Select a year from 2020 to 2100",
            #         # dcc.Input(
            #         #     id="slr-budget-year-input",
            #         #     className="app-options-input",
            #         #     type="number",
            #         #     value=2100,
            #         #     debounce=True,
            #         # ),
            #     ],
            #     className="graph-subtitle",
            # ),
            html.Div(
                id="slr-budget-loading-outer",
                children=[
                    # dcc.Loading(
                    # id="slr-budget-loading",
                    # children=
                    dcc.Graph(
                        id="slr-budget-graph",
                        figure=init["graph"],
                        config=dict(displaylogo=False, displayModeBar=False),
                    ),
                    # )
                ],
            ),
        ],
    )


def generate_slr_table_section(init):

    columns = [
        "Scenario",
        "2050",
        "2100",
        "3ºC GSW",
        "5ºC GSW",
        "VHE/LCP",
    ]

    return dbc.Col(
        id="slr-summary-outer",
        sm=12,
        lg=6,
        xl=12,
        children=[
            html.H3(
                children=[
                    "Scenario likelihoods",
                    # html.Span(
                    #     dbc.Button(
                    #         html.I(className="bi bi-info-circle me-2"),
                    #         color="link",
                    #         id="scenario-table-info-button",
                    #         className="info-button-graph",
                    #     ),
                    # ),
                ],
                className="graph-title",
            ),
            html.P(children="", id="slr-likelihood-statement",),
            html.Div(
                id="slr-likelihood-notes",
                children=[
                    html.Div(
                        children=[
                            "*See ",
                            html.A(
                                "Box 1.1",
                                href="https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1/#h3-9-siblings",
                                target="_blank",
                            ),
                            " in the IPCC AR6 Report for more details about the calibrated language used for likelihood and its relationship to probability.",
                        ],
                    ),
                    html.Div(
                        children=[
                            "**",
                            html.I("Very high greenhouse gas emissions"),
                            " corresponds to the SSP5-8.5 socioeconomic pathway and emissions scenario from the IPCC.",
                        ],
                    ),
                ],
            ),
            html.Div(
                id="slr-summary",
                children=dbc.Row(
                    className="gx-5 gy-4",
                    children=[
                        dbc.Col(
                            lg=12,
                            xl=8,
                            children=[
                                dcc.Markdown(
                                    children=[
                                        "The table below shows specific amounts of *local* sea-level rise and specific probabilities that *global* sea-level rise will meet or exceed the ITF scenarios (adapted from Table 2.4 in the [ITF Report](https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report-sections.html)).",
                                    ],
                                    link_target="_blank",
                                ),
                                dash_table.DataTable(
                                    id="slr-summary-table",
                                    columns=[{"name": y, "id": y} for y in columns],
                                    data=None,
                                    cell_selectable=False,
                                    style_as_list_view=True,
                                    style_cell_conditional=[
                                        {
                                            "if": {"column_id": "Scenario"},
                                            "textAlign": "left",
                                            "paddingLeft": "10px",
                                        },
                                        *[
                                            {
                                                "if": {"column_id": c},
                                                "textAlign": "right",
                                            }
                                            for c in columns[1:]
                                        ],
                                    ],
                                    style_header_conditional=[
                                        {
                                            "if": {"header_index": 0},
                                            "textAlign": "left",
                                            "fontWeight": "bold",
                                        },
                                        *[
                                            {
                                                "if": {"column_id": c},
                                                "textAlign": "right",
                                                "fontWeight": "bold",
                                            }
                                            for c in columns[1:]
                                        ],
                                    ],
                                ),
                            ],
                        ),
                        dbc.Col(
                            lg=12,
                            xl=4,
                            children=[
                                dcc.Markdown(
                                    """
                                ###### Table Columns
                                - **2050** and **2100** show amounts of sea-level rise since 2000 for each scenario by the years 2050 and 2100.
                                - **3ºC GSW** and **5ºC GSW** show the percent chance (or likelihood) that sea-level rise meets or exceeds each scenario for 3ºC and 5ºC of average global surface warming (GSW) by 2100.
                                - **VHE/LCP** shows the percent chance (or likelihood) that sea-level rise meets or exceeds each scenario under Very High Emissions (VHE) when including Low-Confidence Processes (LCP) such as marine ice cliff instability.
                            """,
                                    id="slr-summary-table-description",
                                )
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )

