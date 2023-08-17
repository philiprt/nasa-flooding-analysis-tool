from dash import html, dcc, dash_table
import dash_daq as daq
import dash_bootstrap_components as dbc


def generate_app_header():
    return html.Div(
        id="app-header-full-width",
        children=[
            html.Div(className="app-header-bookend"),
            html.Div(
                id="app-header",
                className="container",
                children=[
                    dbc.Row(
                        className="gy-3",
                        align="center",
                        children=[
                            dbc.Col(
                                lg=5,
                                xs=7,
                                children=html.Div(
                                    id="app-header-title",
                                    children=[
                                        html.Span(
                                            id="app-header-title-logo",
                                            children=html.A(
                                                html.Img(
                                                    src="/assets/images/logo_nslct_no_text.png"
                                                ),
                                                href="https://sealevel.nasa.gov/science-team/overview",
                                                target="_blank",
                                            ),
                                        ),
                                        html.Span(
                                            children=[
                                                html.Span(
                                                    "NASA Sea Level Change Team",
                                                    id="app-header-subtitle-text",
                                                ),
                                                html.Div(
                                                    "Flooding Analysis Tool",
                                                    id="app-header-title-text",
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ),
                            dbc.Col(
                                id="app-header-logos-text",
                                lg=7,
                                xs=5,
                                children=dbc.Stack(
                                    [
                                        html.Div(
                                            className="app-header-logo app-header-nasa-logo ms-auto",  # mx-auto",
                                            children=html.A(
                                                children=[
                                                    html.Div(
                                                        html.Img(
                                                            src="/assets/images/logo_nasa.png"
                                                        ),
                                                    ),
                                                    html.Div(
                                                        children=[
                                                            html.Div(
                                                                "SEA LEVEL CHANGE",
                                                                id="nasa-logo-text-top",
                                                            ),
                                                            # html.Div(
                                                            #     "Observations From Space",
                                                            #     id="nasa-logo-text-bottom",
                                                            # ),
                                                        ]
                                                    ),
                                                ],
                                                href="https://sealevel.nasa.gov",
                                                target="_blank",
                                            ),
                                        ),
                                        html.Div(
                                            className="app-header-logo app-header-uhslc-logo",
                                            children=html.A(
                                                html.Img(
                                                    src="/assets/images/logo_uhslc.png"
                                                ),
                                                href="https://uhslc.soest.hawaii.edu",
                                                target="_blank",
                                            ),
                                        ),
                                    ],
                                    direction="horizontal",
                                    gap=3,
                                ),
                            ),
                            dbc.Col(
                                id="app-header-logos-compact",
                                lg=7,
                                xs=5,
                                children=dbc.Stack(
                                    [
                                        html.Div(
                                            className="app-header-nasa-logo ms-auto",
                                            children=html.A(
                                                html.Img(
                                                    src="/assets/images/logo_nasa.png"
                                                ),
                                                href="https://sealevel.nasa.gov",
                                                target="_blank",
                                            ),
                                        ),
                                        html.Div(
                                            className="app-header-uhslc-logo",
                                            children=html.A(
                                                html.Img(
                                                    src="/assets/images/logo_uhslc_compact.png"
                                                ),
                                                href="https://uhslc.soest.hawaii.edu",
                                                target="_blank",
                                            ),
                                        ),
                                    ],
                                    direction="horizontal",
                                    gap=1,
                                ),
                            ),
                        ],
                    ),
                    # html.Div(
                    #     className="app-header-title",
                    #     children=html.H2("Pacific Islands Flooding"),
                    # ),
                    # html.Div(
                    #     className="app-header-logo",
                    #     children=html.A(
                    #         html.Img(src="/assets/images/uhslc_logo.png"),
                    #         href="https://uhslc.soest.hawaii.edu",
                    #         target="_blank",
                    #     ),
                    # ),
                    # html.Div(
                    #     className="app-header-logo",
                    #     children=html.A(
                    #         html.Img(src="/assets/images/picasc_logo.png"),
                    #         href="https://pi-casc.soest.hawaii.edu",
                    #         target="_blank",
                    #     ),
                    # ),
                    # html.Div(style=dict(clear="both")),
                ],
            ),
            html.Div(className="app-header-bookend"),
        ],
    )


def generate_stations_map(init):
    return dbc.Collapse(
        id="stations-map-collapse",
        is_open=False,
        children=dcc.Graph(
            id="stations-map-graph",
            figure=init["graph"],
            config=dict(displaylogo=False, displayModeBar=True),
        ),
    )


def generate_tabs(app_pages_names):
    return html.Div(
        id="app-tabs-full-width",
        children=[
            html.Div(className="app-tabs-bookend"),
            html.Div(
                id="app-tabs-container",
                className="container",
                children=[
                    dbc.Row(
                        className="g-0",
                        children=[
                            dbc.Col(
                                width=12,
                                children=[
                                    dcc.Tabs(
                                        id="app-tabs",
                                        value="",
                                        mobile_breakpoint=768,
                                        children=[
                                            dcc.Tab(
                                                label=app_pages_names[pg], value=pg,
                                            )
                                            for pg in app_pages_names
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(className="app-tabs-bookend"),
        ],
    )


def generate_options(options):
    return html.Div(
        id="app-options-container",
        className="container",
        style=dict(display="none"),
        children=[
            dbc.Row(
                id="app-options-row",
                class_name="g-5",
                justify="between",
                children=[
                    dbc.Col(
                        children=generate_station_selector(options), xl=6, md=12, xs=12,
                    ),
                    dbc.Col(
                        id="threshold-select-column",
                        children=generate_threshold_selector(options),
                        xl=3,
                        md=6,
                        xs=12,
                    ),
                    dbc.Col(
                        id="scenario-select-column",
                        children=generate_scenario_selector(options),
                        xl=3,
                        md=6,
                        xs=12,
                    ),
                    dbc.Col(
                        id="get-started-column",
                        children=generate_get_started(),
                        xl=6,
                        md=12,
                        xs=12,
                    ),
                    # dbc.Col(
                    #     children=generate_threshold_knob(options),
                    #     xl=1,
                    #     md=2,
                    #     xs=3,
                    # ),
                ],
            ),
        ],
    )


def generate_get_started():

    return html.Div(
        id="get-started-container",
        children=html.Div(
            id="get-started-content",
            children=[
                html.H3("Select a location to begin."),
                dcc.Markdown(
                    "Choose by clicking on the map or by selecting from the *Location* menu."
                ),
            ],
        ),
    )


def generate_station_selector(options):

    return html.Div(
        id="station-select-container",
        children=[
            html.Div(
                id="station-select-title-container",
                children=[
                    html.H6(
                        "Location:",
                        id="station-select-title",
                        className="app-options-title",
                    ),
                ],
            ),
            dcc.Dropdown(
                id="station-select",
                className="app-options-dropdown",
                options=options["station"],
                value=None,
                clearable=False,
                placeholder="Location",
            ),
            html.Div(
                id="options-toggles",
                children=[
                    html.Div(
                        id="show-map-toggle-container",
                        children=[
                            html.H6(
                                "Show map",
                                id="show-map-toggle-label",
                                className="app-options-title",
                            ),
                            dbc.Switch(id="show-map-toggle", value=True,),
                        ],
                    ),
                    html.Div(
                        id="units-toggle-container",
                        children=[
                            html.H6(
                                "Feet",
                                className="app-options-title units-toggle-label",
                            ),
                            dbc.Switch(id="units-toggle", value=True,),
                            html.H6(
                                "Meters",
                                className="app-options-title units-toggle-label",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def generate_scenario_selector(options):

    return html.Div(
        id="scenario-select-container",
        className="selection-container",
        children=[
            html.Div(
                [
                    html.H6("U.S. Interagency scenario:", style={"float": "left"}),
                    html.Span(
                        dbc.Button(
                            html.I(className="bi bi-info-circle me-2"),
                            color="link",
                            id="scenario-picker-info-button",
                            className="info-button-picker",
                        ),
                        style={"float": "right"},
                    ),
                    html.Div(style={"clear": "both"}),
                ],
                className="app-options-title",
            ),
            dcc.Dropdown(
                id="scenario-select",
                className="app-options-dropdown",
                options=options["scenario"],
                value="int",
                clearable=False,
            ),
            html.Div(
                id="app-options-scenario",
                className="app-options-info",
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "Sea-level rise by ", style={"float": "left"},
                                    ),
                                    html.Span(
                                        "????",
                                        id="app-options-slr-year",
                                        style={"float": "left"},
                                    ),
                                ],
                                className="app-options-title",
                            ),
                            html.Div(
                                "Relative to 2000", className="app-options-detail",
                            ),
                        ],
                        style={"float": "left"},
                    ),
                    html.Div(
                        [
                            html.Span(
                                "?.?? m",
                                id="app-options-scenario-text",
                                style={"float": "right", "margin": "7px 9px 0px 3px",},
                            ),
                        ],
                        style={"float": "right"},
                    ),
                    html.Div(style={"clear": "both"}),
                ],
            ),
        ],
    )


def generate_threshold_selector(options):

    return html.Div(
        id="threshold-select-container",
        className="selection-container",
        style={"display": "flex"},
        children=[
            html.Div(
                id="threshold-dropdown-container",
                children=[
                    html.Div(
                        [
                            html.H6("Flooding threshold:", style={"float": "left"}),
                            html.Span(
                                dbc.Button(
                                    html.I(className="bi bi-info-circle me-2"),
                                    color="link",
                                    id="threshold-picker-info-button",
                                    className="info-button-picker",
                                ),
                                style={"float": "right"},
                            ),
                            html.Div(style={"clear": "both"}),
                        ],
                        id="threshold-dropdown-title",
                        className="app-options-title",
                    ),
                    dcc.Dropdown(
                        id="threshold-select",
                        className="app-options-dropdown",
                        options=options["threshold"],
                        value="minor",
                        clearable=False,
                    ),
                    html.Div(
                        id="app-options-threshold",
                        className="app-options-info",
                        children=[
                            html.Div(
                                [
                                    html.Div(
                                        "Threshold elevation",
                                        className="app-options-title",
                                    ),
                                    html.Div(
                                        "Above MHHW", className="app-options-detail",
                                    ),
                                ],
                                style={"float": "left"},
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "",
                                        id="threshold-units",
                                        style={
                                            "float": "right",
                                            "margin": "7px 9px 0px 3px",
                                        },
                                    ),
                                    dcc.Input(
                                        id="threshold-float",
                                        type="number",
                                        step=0.01,
                                        value=None,
                                        debounce=True,
                                        # size=65,
                                        style={
                                            "float": "right",
                                            "width": "65px",
                                            "margin-top": "4px",
                                        },
                                    ),
                                ],
                                style={"float": "right"},
                            ),
                            html.Div(style={"clear": "both"}),
                        ],
                    ),
                ],
            ),
            # html.Div(
            #     id="threshold-knob-container",
            #     children=[
            #         daq.Knob(
            #             id="threshold-knob",
            #             size=70,
            #             value=0,
            #             max=10,
            #             scale={
            #                 # "interval": 0.01 * 3.28084,
            #                 # "custom": {0: "0 ft", 3: "3 ft", 7: "7 ft", 10: "10 ft"},
            #                 "custom": {
            #                     tck: f"{tck} ft" if tck in [0, 10] else ""
            #                     for tck in range(11)
            #                 },
            #             },
            #         ),
            #     ],
            # ),
        ],
    )


def generate_threshold_knob(options):

    return html.Div(
        id="threshold-knob-container",
        className="selection-container",
        children=[
            daq.Knob(
                id="threshold-knob",
                size=0,
                value=0,
                max=10,
                scale={"start": 0, "labelInterval": 5, "interval": 0.01 * 3.28084},
            ),
        ],
    )
