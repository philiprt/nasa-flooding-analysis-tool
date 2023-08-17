from dash import html, dcc

# import dash_daq as daq
import dash_bootstrap_components as dbc


def generate_intro_modal():

    # title_text = "Flooding Analysis Tool"

    body_text = [
        html.Div(
            className="container",
            children=[
                dbc.Row(
                    [
                        dbc.Col(lg=1, md=0),
                        dbc.Col(
                            className="intro-modal-logo intro-modal-nasa-logo",
                            lg=5,
                            md=12,
                            children=html.Div(
                                html.A(
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
                                                    id="intro-modal-nasa-logo-text",
                                                ),
                                                # html.Div(
                                                #     "Observations From Space",
                                                #     id="nasa-logo-text-bottom",
                                                # ),
                                            ]
                                        ),
                                    ],
                                    href="https://sealevel.nasa.gov/",
                                    target="_blank",
                                ),
                                className="intro-modal-logo-flex",
                            ),
                        ),
                        dbc.Col(
                            className="intro-modal-logo intro-modal-uhslc-logo",
                            lg=5,
                            md=12,
                            children=html.Div(
                                html.A(
                                    html.Img(src="/assets/images/logo_uhslc.png"),
                                    href="https://uhslc.soest.hawaii.edu",
                                    target="_blank",
                                ),
                                className="intro-modal-logo-flex",
                            ),
                        ),
                        dbc.Col(lg=1, md=0),
                    ],
                ),
            ],
        ),
        html.H1("Flooding Analysis Tool", id="intro-modal-title"),
        dcc.Markdown(
            """
            High-tide flooding is an increasingly frequent occurrence in coastal areas around the United States. The *NASA Flooding Analysis Tool* was developed to facilitate decision-relevant assessments of how sea-level rise and other factors will affect the frequency of high-tide flooding across the United States. Users can:
            - View sea-level observations and assess past high-tide flooding frequency.
            - View future changes in high-tide flooding frequency under the [Interagency Sea-Level Rise Scenarios](https://sealevel.nasa.gov/task-force-scenario-tool).
            - View statistics and inflection points that support decision making.

            The Flooding Analysis Tool was developed with funding from the [NASA Sea Level Change Team](https://sealevel.nasa.gov/science-team/overview) by scientists at the [University of Hawaii Sea Level Center](https://uhslc.soest.hawaii.edu) and is based on the methods of [Thompson et al. (2021)](https://www.nature.com/articles/s41558-021-01077-8).
            """,
            link_target="_blank",
            id="intro-modal-text",
        ),
        dcc.Markdown(
            """
                - **Tip:** You can skip the landing page and return to the tool for specific locations and options by copying or bookmarking the web address associated with the desired configuration. 
                - **Note:** The previous version of this tool based on on the sea-level rise scenarios from [Sweet et al. (2017)](https://tidesandcurrents.noaa.gov/publications/techrpt83_Global_and_Regional_SLR_Scenarios_for_the_US_final.pdf.) remains online at [https://sealevel.nasa.gov/flooding-days-projection/](https://sealevel.nasa.gov/flooding-days-projection/)

                """,
            link_target="_blank",
            className="modal-highlight",
        ),
    ]

    return dbc.Modal(
        [
            # dbc.ModalHeader(dbc.ModalTitle(title_text)),
            dbc.ModalBody(body_text),
            dbc.ModalFooter(
                children=[
                    dbc.Button(
                        "Instructions",
                        id="intro-modal-instructions-link",
                        className="intro-modal-button",
                        href="/about/instructions",
                        n_clicks=0,
                    ),
                    dbc.Button(
                        "Get started",
                        id="intro-modal-close",
                        className="intro-modal-button ms-auto",
                        n_clicks=0,
                    ),
                ]
            ),
        ],
        id=f"intro-modal",
        className="modal common-text",
        is_open=False,
        centered=True,
        size="lg",
        scrollable=True,
    )


def generate_info_modal(element):

    # --------------------------------------------------------------------

    if element == "threshold-picker":

        title_text = "Flooding Thresholds"

        body_text = [
            dcc.Markdown(
                """
                - Select a **flooding threshold**\* predetermined by [NOAA](https://repository.library.noaa.gov/view/noaa/17403) or [NWS](https://www.weather.gov/aprfc/terminology) using the dropdown menu, or enter a custom threshold\*\* in the text box.

                - The thresholds are provided as heights above [mean higher high water](https://tidesandcurrents.noaa.gov/datum_options.html#MHHW) (MHHW), which is approximately the average height of the highest tide per day.
                """,
                link_target="_blank",
                className="modal-highlight",
            ),
            dcc.Markdown(
                """ 
                **Note:** The term **"flooding"** as used in this tool corresponds to any water level above a threshold, but this water level may or may not correspond to tangible impacts. Choosing a **locally relevant flooding threshold** from the provided options is essential for understanding and determining the impacts of current and future high-tide flooding.
                """,
                link_target="_blank",
            ),
            html.P(
                [
                    "*Predetermined threshold heights were obtained from the ",
                    html.A(
                        "CO-OPS API For Data Retrieval",
                        href="https://api.tidesandcurrents.noaa.gov/api/prod/",
                        target="_blank",
                    ),
                    " and were last updated in this tool on ",
                    html.Span("December 31, 1999", id="threshold-picker-modal-updated"),
                    ".",
                ],
                className="footnote-text",
            ),
            html.P(
                [
                    "**Custom thresholds will round to the nearest centimeter, which may adjust the entered threshold by a small amount.",
                ],
                className="footnote-text",
            ),
        ]

    # --------------------------------------------------------------------

    elif element in ["scenario-picker", "scenario-graph"]:

        title_text = "Sea-Level Rise Scenarios"

        body_text = [
            dcc.Markdown(
                """
                - Select a **sea-level rise scenario** from the [2022 U.S. Interagency Task Force (ITF) report](https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report-sections.html).
                """,
                link_target="_blank",
                className="modal-highlight",
            ),
            dcc.Markdown(
                """
                The scenarios are defined by specific amounts of *global* mean sea-level (GMSL) rise by 2100. However, *local* mean sea-level rise for each scenario, which differs from the global average, is what is shown in this tool (and what is used to produce the location-specific high-tide flooding projections). The scenario names and corresponding amounts of GMSL rise by 2100 are:
                - **Low** (0.3 m or 1.0 ft)
                - **Intermediate Low** (0.5 m or 1.6 ft)
                - **Intermediate** (1.0 m or 3.3 ft)
                - **Intermediate High** (1.5 m or 4.9 ft)
                - **High** (2.0 m or 6.6 ft)
                """,
                link_target="_blank",
                className="pre-list-p",
            ),
            dcc.Markdown(
                """    
                **Note:** The two highest scenarios (*High* and *Intermediate High*) correspond to more sea-level rise than is expected from most climate models. However, while there is a low probability of these scenarios occurring based on current understanding, they are **physically plausible** and correspond to **high-impact** outcomes that are relevant for applications with low risk tolerance.
                """,
                link_target="_blank",
            ),
            dcc.Markdown(
                """
                To learn more:
                - Read the [ITF report](https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report-sections.html) and its [application guide](https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report-sections.html#application-guide).
                - Explore the scenarios with the [Interagency Sea Level Rise Scenario Tool](https://sealevel.nasa.gov/task-force-scenario-tool).
                """,
                link_target="_blank",
                className="pre-list-p",
            ),
        ]

    # --------------------------------------------------------------------

    # elif element in "scenario-table":

    #     title_text = "Scenarios, emissions, and warming"
    #     body_text = "This is the content of the modal."

    # --------------------------------------------------------------------

    elif element == "budget-graph":

        title_text = "Contributions To Future Sea-Level Rise"

        body_text = [
            dcc.Markdown(
                """
                Mouse over the sea-level rise scenarios graph to see the contributions to local sea-level change for the selected scenario and year closest to the cursor.
                
                Click a specific year in the graph of ITF scenarios to "lock in" a specific year in the contributions graph.
                """,
                link_target="_blank",
                className="modal-highlight",
            ),
            dcc.Markdown(
                """
                Multiple processes contribute to long-term sea-level change—some related to climate, such as ice melt and ocean warming, and others unrelated to climate, such as land subsidence and water storage. The relative importance of these processes varies from one location and time to another, and understanding how these processes vary is essential for projecting future sea-level rise and impacts. 

                For more information, see the discussion of contributions to regional sea-level change on NASA's [Understanding Sea Level](https://sealevel.nasa.gov/understanding-sea-level/regional-sea-level/overview) page.
                """,
                link_target="_blank",
                # className="pre-list-p",
            ),
        ]

    # --------------------------------------------------------------------

    elif element == "observed-graph":

        title_text = "Observations From Tide Gauges"

        body_text = [
            dcc.Markdown(
                """
                - **Blue lines** show the highest and lowest hourly water levels from a [NOAA tide gauge](https://oceanservice.noaa.gov/facts/tide-gauge.html) at the selected location.

                - The **black horizontal line** marks the height of the currently selected flooding threshold.

                - **Orange markers** denote observed flooding days.

                - **Blue bars** (bottom) show the number of flooding days in each year*.

                - The water level data and thresholds are provided as heights relative to [mean higher high water](https://tidesandcurrents.noaa.gov/datum_options.html#MHHW) (MHHW), which is approximately the average height of the highest tide per day.
                """,
                link_target="_blank",
                className="modal-highlight",
            ),
            dcc.Markdown(
                """
                A **flooding day** is defined as a day during which at least one hourly average water level exceeds the selected flooding threshold.

                **Note:** The term **"flooding"** as used in this tool corresponds to any water level above a threshold, but this water level may or may not correspond to tangible impacts. Choosing a **locally relevant flooding threshold** from the provided options is essential for understanding and determining the impacts of current and future high-tide flooding.
                """,
                link_target="_blank",
            ),
            html.P(
                [
                    "*Years are defined as meterological years (May–April) to avoid splitting storm seasons into separate years. The year shown corresponds to the year of January during the meteorological year.",
                ],
                className="footnote-text",
            ),
        ]

    # --------------------------------------------------------------------

    elif element == "projected-graph":

        title_text = "Projections of Flooding Days"

        body_text = [
            dcc.Markdown(
                """
                - The **blue line** shows the **expected number** (or 50th percentile from the projection ensemble) of flooding days in future years for the specific **threshold** and **scenario** selected.

                - The **blue shading** shows the ***likely* and *very likely* ranges**\* that account for unpredictable contributions to high-tide flooding, such as changes in sea level or storminess from one year or decade to the next due to natural climate fluctuations.

                """,
                link_target="_blank",
                className="modal-highlight",
            ),
            html.P(
                [
                    "See the ",
                    dcc.Link("Methodology", href="/about/methodology"),
                    " page for a description of how these projections were created.",
                ],
            ),
            dcc.Markdown(
                """
                A **flooding day** is defined as a day during which at least one hourly average water level exceeds the selected flooding threshold.

                **Note:** The term **"flooding"** as used in this tool corresponds to any water level above a threshold, but this water level may or may not correspond to tangible impacts. Choosing a **locally relevant flooding threshold** from the provided options is essential for understanding and determining the impacts of current and future high-tide flooding.
                """,
                link_target="_blank",
            ),
            html.P(
                [
                    "*See ",
                    html.A(
                        "Box 1.1",
                        href="https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1/#h3-9-siblings",
                        target="_blank",
                    ),
                    " in the IPCC AR6 Report for more details about the calibrated language used for likelihood and its relationship to probability.",
                ],
                className="footnote-text",
            ),
        ]

    # --------------------------------------------------------------------

    elif element == "climatology-graph":

        title_text = "Monthly Breakdown of Flooding Days"

        body_text = [
            dcc.Markdown(
                """
                - Mouse over the *Flooding Days* projection graph to see the monthly breakdown of flooding days for the selected scenario and year closest to the cursor.
                
                - Click a specific year in the *Flooding Days* projection graph to "lock in" a specific year in the monthly graph.
                """,
                link_target="_blank",
                className="modal-highlight",
            ),
            dcc.Markdown(
                """
                The likelihood of flooding days changes throughout the year due to seasonal changes in tides and sea level. As a result, flooding days in many locations will tend to be **concentrated during particular months or seasons**. 

                At locations where the seasonality is particularly pronounced, the effect is **important to consider when interpreting annual projections** of flooding days. For example, a projection of 25 flooding days in one year may contain a single month with 12 flooding days or a single season with 20 days.
                """,
                link_target="_blank",
                # className="pre-list-p",
            ),
        ]

    # --------------------------------------------------------------------

    elif element == "extreme-graph":

        title_text = "Extreme Months"

        body_text = [
            dcc.Markdown(
                """
                - The **blue circles** represent the **average number of flooding days per month** during future five-year periods for the specific **threshold** and **scenario** selected.

                - The **red circles** represent the number of **flooding days during the *most severe* month ** of each five-year period.

                - The **vertical lines** span the **likely range**\* for each value.

                """,
                link_target="_blank",
                className="modal-highlight",
            ),
            dcc.Markdown(
                """
                Coastal engineers do not design structures based on average sea level—rather they design structures to withstand extreme events that may only occur once every decade or century. Similarly, coastal communities should be prepared for extreme months when many high-tide flooding events cluster together during a single **extreme month**. This graph demonstrates the difference between average numbers of flooding days and the most extreme month during each five-year period.
                """
            ),
            html.P(
                [
                    "This analysis is made possible by (and is unique to) the ensemble projections of flooding days produced by ",
                    html.A(
                        "Thompson et al. (2021)",
                        href="https://www.nature.com/articles/s41558-021-01077-8",
                        target="_blank",
                    ),
                    ". See the ",
                    dcc.Link("Methodology", href="/about/methodology"),
                    " page for an overview of how these projections were created.",
                ],
            ),
            html.P(
                [
                    "*See ",
                    html.A(
                        "Box 1.1",
                        href="https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1/#h3-9-siblings",
                        target="_blank",
                    ),
                    " in the IPCC AR6 Report for more details about the calibrated language used for likelihood and its relationship to probability.",
                ],
                className="footnote-text",
            ),
        ]

    # --------------------------------------------------------------------

    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title_text)),
            dbc.ModalBody(body_text),
            # dbc.ModalFooter(
            #     dbc.Button("Close", id="close", className="ms-auto", n_clicks=0)
            # ),
        ],
        id=f"{element}-info-modal",
        className="modal common-text",
        is_open=False,
        centered=True,
    )

