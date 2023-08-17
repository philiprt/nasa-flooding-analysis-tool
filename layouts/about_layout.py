from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def generate_about_page():

    return html.Div(
        id="about",
        className="app-page hidden-app-page",
        children=[
            html.Div(
                className="container",
                children=[
                    dbc.Row(
                        class_name="g-0 about-row",
                        children=[
                            dbc.Col(
                                id="about-tabs-container",
                                sm=12,
                                md=3,
                                lg=2,
                                children=dcc.Tabs(
                                    id="about-tabs",
                                    value="about-instructions",
                                    vertical=True,
                                    mobile_breakpoint=768,
                                    children=[
                                        dcc.Tab(
                                            label="Instructions",
                                            value="about-instructions",
                                        ),
                                        dcc.Tab(
                                            label="Background",
                                            value="about-background",
                                        ),
                                        dcc.Tab(
                                            label="Methodology",
                                            value="about-methodology",
                                        ),
                                    ],
                                ),
                            ),
                            dbc.Col(
                                id="about-content-container",
                                sm=12,
                                md=9,
                                lg=10,
                                children=[
                                    html.Div(
                                        id="about-instructions",
                                        className="app-page-section hidden-app-page",
                                        children=generate_instructions_content(),
                                    ),
                                    html.Div(
                                        id="about-background",
                                        className="app-page-section hidden-app-page",
                                        children=generate_background_content(),
                                    ),
                                    html.Div(
                                        id="about-methodology",
                                        className="app-page-section hidden-app-page",
                                        children=generate_methodology_content(),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            )
        ],
    )


def generate_instructions_content():

    title_dom = (
        dbc.Row(
            class_name="g-0",
            children=[
                dbc.Col(
                    class_name="about-column",
                    children=[
                        html.H3(
                            children="How to use this tool",
                            className="about-tab-title",
                        ),
                    ],
                ),
            ],
        ),
    )

    about_sections_content = [
        # --------------------------------------------------------------------
        dict(
            title="1. Select a location",
            image="/assets/images/about_location_panel.png",
            content=[
                html.P(
                    [
                        "This tool provides projections and analysis of high-tide flooding days at the locations of ",
                        html.A(
                            "tide gauges",
                            href="https://oceanservice.noaa.gov/facts/tide-gauge.html",
                        ),
                        ". If a tide gauge does not exist at the desired location, analysis from the closest tide gauge can provide useful information.  However, it is important to consider the potential impact of local factors that can differ even over short distances such as ",
                        html.A(
                            "land subsidence",
                            href="https://sealevel.nasa.gov/understanding-sea-level/regional-sea-level/subsidence",
                            target="_blank",
                        ),
                        ".",
                    ]
                ),
                dcc.Markdown(
                    "You can **select a location** in two ways:",
                    className="pre-list-p",
                ),
                dcc.Markdown(
                    [
                        "- Select a location from from the **dropdown menu** displaying the current location name. The locations can be searched by typing in this field.",
                        "- Select a location by **clicking on the map**. Note that the map can be hidden once the desired location is chosen using the switch beneath the location name.",
                    ]
                ),
            ],
        ),
        # --------------------------------------------------------------------
        dict(
            title="2. Select a flooding threshold",
            image="/assets/images/about_threshold_panel.png",
            content=[
                html.P(
                    [
                        'Not every "flooding" threshold corresponds to tangible impacts. Choosing a ',
                        html.B("relevant flooding threshold"),
                        " is essential for understanding and determining the impacts of current and future high-tide flooding. One way to determine a relevant threshold is to look at tide-gauge observations on the ",
                        html.I(
                            dcc.Link("Observed Flooding", href="/observed-flooding",)
                        ),
                        " tab in this tool and determine whether past high sea-level events above various thresholds correspond to the timing and/or frequency of known impacts.",
                    ]
                ),
                dcc.Markdown(
                    "You can **select a threshold** in two ways:",
                    className="pre-list-p",
                ),
                dcc.Markdown(
                    [
                        "- Choose from a list of predetermined [NOAA](https://repository.library.noaa.gov/view/noaa/17403) and [NWS](https://www.weather.gov/aprfc/terminology) flooding thresholds* using the **dropdown menu** displaying the current threshold name.",
                        "- Enter a **custom threshold height** in the box below the threshold name. Custom thresholds will round to the nearest centimeter, which may adjust the entered threshold by a small amount.",
                    ],
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
                        html.Span("December 31, 1999", id="about-how-threshold-update"),
                        ".",
                    ],
                    className="footnote-text",
                ),
            ],
        ),
        # --------------------------------------------------------------------
        dict(
            title="3. Select a sea-level rise scenario",
            image="/assets/images/about_scenario_panel.png",
            content=[
                # html.P(
                #     "The frequency of high-tide flooding is expected to increase in most locations during the 21st century due to sea-level rise. The amount and rate of future sea-level rise determines the evolution of future flooding extent and frequency."
                # ),
                html.P(
                    [
                        "The Flooding Days projections provided in this tool are based on the most recent sea-level rise scenarios from the ",
                        html.A(
                            "2022 U.S. Interagency Task Force (ITF) report",
                            href="https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report-sections.html",
                            target="_blank",
                        ),
                        " and can be viewed on the ",
                        html.I(dcc.Link("Sea-Level Rise", href="/sea-level-rise",)),
                        " tab in this tool. These scenarios use information from the ",
                        html.A(
                            "IPCC 6th Assessment Report",
                            href="https://www.ipcc.ch/assessment-report/ar6/",
                            target="_blank",
                        ),
                        " to produce individual scenarios corresponding to various levels of risk tolerance.",
                    ]
                ),
                dcc.Markdown(
                    [
                        "You can **select one of five ITF scenarios** from the **dropdown menu**.",
                        "- The two highest scenarios correspond to low-probability yet plausible and highly impactful outcomes for applications with low risk tolerance.",
                        "- The graph next to the scenarios shows **contributions** to sea-level rise for the selected scenario during a specific year. ",
                        "   - The graph will show the year closest to the user's cursor when hovering over the scenarios. ",
                        '   - A particular year can be "locked in" by clicking on the scenarios.',
                    ],
                    className="pre-list-p",
                ),
                html.P(
                    [
                        "To fully explore the ITF scenarios, see the ",
                        html.A(
                            "Interagency Sea Level Rise Scenario Tool",
                            href="https://sealevel.nasa.gov/task-force-scenario-tool",
                            target="_blank",
                        ),
                        ". and these ",
                        html.A(
                            "frequently asked questions",
                            href="https://sealevel.nasa.gov/faq/16/what-are-the-scenarios-from-the-sea-level-rise-interagency-task-force-and-how-do-they-compare-to-the/",
                            target="_blank",
                        ),
                        ".",
                    ]
                ),
            ],
        ),
        # --------------------------------------------------------------------
        dict(
            title="4. View projections of flooding days",
            image="/assets/images/about_flood_panel.png",
            content=[
                html.P(
                    [
                        "From the selected combination of location, threshold, and scenario, the ",
                        html.I(dcc.Link("Projected Flooding", href="/sea-level-rise",)),
                        " tab shows the expected number of flooding days per year during the 21st century. The projections are based on the approach of ",
                        html.A(
                            "Thompson et al. (2021)",
                            href="https://www.nature.com/articles/s41558-021-01077-8",
                            target="_blank",
                        ),
                        " but updated to incorporate the 2022 ITF scenarios. See the ",
                        html.I(dcc.Link("Methodology", href="/about/methodology",)),
                        " link on this page for more details.",
                    ]
                ),
                dcc.Markdown(
                    [
                        "- The projections incorporate:",
                        "   - Changes in tides from one year or decade to the next.",
                        "   - A range of possibilities based on unpredictable changes in sea level related to ocean circulation and natural climate fluctuations (El Niño, etc.).",
                        "- The graph next to the flooding days projections shows the breakdown of flooding days by month during a specific year. ",
                        "   - The graph will show the year closest to the user's cursor when hovering over the scenarios. ",
                        '   - A particular year can be "locked in" by clicking on the annual projection.',
                    ],
                    className="pre-list-p",
                ),
            ],
        ),
        # --------------------------------------------------------------------
    ]

    about_sections = [
        dbc.Row(
            class_name="g-0 about-subsection",
            children=[
                dbc.Col(
                    class_name="about-column",
                    xl=6,
                    lg=7,
                    sm=12,
                    children=[
                        html.H4(
                            children=asc["title"], className="about-subsection-title",
                        ),
                        html.P(children=asc["content"], className="common-text",),
                    ],
                ),
                dbc.Col(
                    class_name="about-column",
                    xl=6,
                    lg=5,
                    sm=12,
                    children=[
                        dbc.Stack(
                            [
                                html.Img(
                                    className="about-panel-img mx-auto",
                                    src=asc["image"],
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        )
        for asc in about_sections_content
    ]

    return [*title_dom, *about_sections]


def generate_methodology_content():

    title_dom = (
        dbc.Row(
            class_name="g-0",
            children=[
                dbc.Col(
                    class_name="about-column",
                    children=[
                        html.H3(children="Methodology", className="about-tab-title",),
                        dcc.Markdown(
                            """
                            The methodology used to produce the high-tide flooding projections in this tool follows the process developed by [Thompson et al. (2021)](https://www.nature.com/articles/s41558-021-01077-8). The method has been updated to incorporate the most recent sea-level rise scenarios from the [2022 Interagency Task Force report](https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report-sections.html) and applied to any location within the U.S. and its territories for which there is sufficient tide gauge data.
                            """,
                            className="common-text about-subsection",
                            link_target="_blank",
                        ),
                    ],
                ),
            ],
        ),
    )

    about_sections_content = [
        # --------------------------------------------------------------------
        dict(
            title="A Distribution for Flooding Days",
            image="/assets/images/methods_distributions.png",
            image_caption="""
                **Figure 2:** Hypothetical probability mass distributions for the number of flooding days per year for two scenarios. (top) The highest astronomical tides are far below the flooding threshold, which means the highest probability is that no flooding days occur. (bottom) The highest astronomical tides are near the flooding threshold, which implies high probability of multiple flooding days.
                """,
            content=[
                dcc.Markdown(
                    """
                    The machinery of the projection algorithm is based around the idea that the probability mass distribution governing the number of threshold exceedances in a given year can be parameterized as a function of the height difference between the threshold of interest and the height of the highest tides of the year. For example, if the threshold is far above the height of the highest tides, then the probability of exceedance is low, and one would expect the probability of zero events to be high with small probabilities of multiple events (**Figure&nbsp;2a**). Alternatively, if the threshold is relatively close to the height of the highest tides, one would expect high probabilities of multiple events with lower probabilities of zero and many events (Figure 2b). In practice, the method employs the flexible [beta-binomial probability mass distribution](https://en.wikipedia.org/wiki/Beta-binomial_distribution) to represent the varying shapes of the distribution as the height of the highest tides varies relative to the height of the threshold. The parameters of the beta-binomial distribution are estimated as functions of the difference between threshold and highest tides on a location- and month-specific basis via an analysis of available tide gauge data.
                    """,
                    link_target="_blank",
                ),
            ],
        ),
        # --------------------------------------------------------------------
        dict(
            title="Ensemble Projections",
            image="/assets/images/methods_schematic.png",
            image_caption="""
                **Figure 3:** Schematic illustrating how various ingredients are combined into an probabilistic projections for the number of flooding days above the threshold during each year of the 21st century.
                """,
            content=[
                dcc.Markdown(
                    """
                    Once the parameters of the distribution are established, projections of flooding days requires projections of the highest tides of the month. We define the highest tides of the month as the annual 99th percentile of astronomical tidal variability PLUS monthly mean sea level. The latter acts to change the baseline of the tidal variability similar to **Figure&nbsp;1**. In order to project this quantity, we use three ingredients:

                    * **Ensemble projection of astronomical tidal variability.** The ensemble tidal projections employed here are based on [Gaussian process](https://en.wikipedia.org/wiki/Gaussian_process) representations of periodic and stochastic variations in the amplitude and phase of major tidal constituents. These projections account for co-variability between certain constituents and mean sea level, as well as trends in tidal amplitude related to non-climatic factors.

                    * **Projections of local mean sea level trends and acceleration**. It is essential to use *local* mean sea level projections that incorporate estimates of local and regional vertical land motion, as well as spatial differences in the response of ocean surface height to climate change (e.g., [ice melt fingerprints](https://sealevel.nasa.gov/understanding-sea-level/regional-sea-level/overview)). The high-tide flooding projections in this tool are based on sea-level rise scenarios from the [2022 Interagency Task Force report](https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report-sections.html)

                    * **Ensemble projections of stochastic variability in monthly mean sea level**. These projections are based on [Gaussian process](https://en.wikipedia.org/wiki/Gaussian_process) representations of unpredictable variations in local monthly mean sea level primarily related to atmosphere-ocean dynamics.

                    The schematic in **Figure&nbsp;3** illustrates how these ingredients are combined into an ensemble prediction of the 99th percentile of tidal height for each month during the 21st century. When further combined with a user defined threshold and parameterization of the beta-binomial probability mass distribution tuned using tide gauge data, these components produce a probabilistic estimate for the number of flooding days above the threshold in each month and year.
                    """,
                    link_target="_blank",
                ),
            ],
        ),
        # --------------------------------------------------------------------
    ]

    about_sections = [
        dbc.Row(
            class_name="g-0 about-subsection",
            children=[
                dbc.Col(
                    class_name="about-column",
                    xl=6,
                    lg=7,
                    sm=12,
                    children=[
                        html.H4(
                            children=asc["title"], className="about-subsection-title",
                        ),
                        html.P(children=asc["content"], className="common-text",),
                    ],
                ),
                dbc.Col(
                    class_name="about-column",
                    xl=6,
                    lg=5,
                    sm=12,
                    children=[
                        dbc.Stack(
                            [
                                html.Img(
                                    className="about-panel-img mx-auto",
                                    src=asc["image"],
                                ),
                            ]
                        ),
                        dcc.Markdown(
                            className="about-panel-img-caption",
                            children=asc["image_caption"],
                        ),
                    ],
                ),
            ],
        )
        for asc in about_sections_content
    ]

    return [*title_dom, *about_sections]


def generate_background_content():

    title_dom = (
        dbc.Row(
            class_name="g-0",
            children=[
                dbc.Col(
                    class_name="about-column",
                    children=[
                        html.H3(children="Background", className="about-tab-title",),
                    ],
                ),
            ],
        ),
    )

    about_sections_content = [
        # --------------------------------------------------------------------
        dict(
            title="Factors Affecting High-Tide Flooding",
            content=[
                dcc.Markdown(
                    """
                    [High-tide flooding](https://coast.noaa.gov/states/fast-facts/recurrent-tidal-flooding.html) is—as the name suggests—flooding that occurs at high tide, but it is not necessarily due to the tidal forces of the moon and sun alone. There are a variety of factors that contribute to any given high sea-level event. Some of them have to do with the astronomical forces that generate tides while others do not.

                    Most people are aware that some high tides are higher than others. The [spring-neap cycle](https://oceanservice.noaa.gov/facts/springtide.html), for example, is related to the alignment of the earth, moon, and sun, and causes the height of high tides to get higher and lower roughly twice per month. Most people are also aware that sea level rise will cause the highest tides to get even higher and cause flooding thresholds to be exceeded more often (**Figure&nbsp;1**).

                    However, there are myriad factors across time and space scales that affect how often the ocean height will exceed a given threshold. For example:
                    - Tidal amplitude does not just vary on a quasi-monthly basis due to the spring-neap cycle—it also varies from season to season and year to year. More specifically, there are substantial [4.4- and 18.6-year cycles](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2010JC006645) in the tides with important [implications](https://www.nature.com/articles/s41558-021-01077-8) for the frequency of coastal flooding. 
                    
                    - Changes in ocean circulation and year-to-year variations in climate cause average sea level to rise and fall over periods of months or years, with phenomena such as [El Ni&ntilde;o](https://journals.ametsoc.org/doi/abs/10.1175/1520-0485%281980%29010%3C0557%3AOTSADO%3E2.0.CO%3B2) and [changes in the strength of the Gulf Stream](https://tidesandcurrents.noaa.gov/publications/EastCoastSeaLevelAnomaly_2009.pdf)) being two leading factors along the Pacific and Atlantic coastlines of the U.S., respectively. 
                    
                    - Changes in [storminess](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2021GL096820) or short-term chaotic ocean variability (i.e., ocean "weather" like eddies) can lead to differences in flooding frequency from one month or year to the next.
                    """,
                    link_target="_blank",
                ),
            ],
        ),
        # --------------------------------------------------------------------
        dict(
            title="A Range of Possibilities",
            content=[
                dcc.Markdown(
                    """
                    It is possible for multiple factors such as those listed above to coincide and produce a "cluster" of flooding events. For example, there was a period of [state-wide, repeated coastal flooding in Hawai`i during summer 2017](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2018JC014741), which was related to the combination of seasonally high tides, eddies, El [Niño, and and weak trade winds](https://doi.org/10.1175/JCLI-D-19-0221.1). Similar situations can occur elsewhere, which explains why locations affected by high-tide flooding tend to experience occasional, severe years with many events while other years experience few or none at all.

                    The [methodology](/) used to produce the high-tide flooding projections in this tool takes into account the tendency of flooding events to "cluster" together in occasional—yet inevitable—severe months or years. As a result, the projections provide a range of possibilities for any given year, acknowledging that some years will be worse than others, and it is not possible to know in advance which years those will be. The projections leverage the predictability inherent in certain contributions (e.g., tidal amplitude and climate-change-induced sea level rise) and use statistical methods to account for everything else.
                    """,
                    link_target="_blank",
                ),
            ],
        ),
        # --------------------------------------------------------------------
    ]

    about_sections = [
        dbc.Row(
            class_name="gx-0 gy-5",
            children=[
                dbc.Col(
                    class_name="about-column",
                    # xl=6,
                    lg=7,
                    sm=12,
                    children=[
                        html.Div(
                            [
                                html.H4(
                                    children=asc["title"],
                                    className="about-subsection-title",
                                ),
                                html.P(
                                    children=asc["content"], className="common-text",
                                ),
                            ],
                            className="about-subsection",
                        )
                        for asc in about_sections_content
                    ],
                ),
                dbc.Col(
                    class_name="about-column",
                    # xl=6,
                    lg=5,
                    sm=12,
                    children=[
                        dbc.Stack(
                            [
                                html.Img(
                                    className="about-panel-img mx-auto",
                                    src="/assets/images/methods_effect_of_slr.png",
                                ),
                            ]
                        ),
                        dcc.Markdown(
                            className="about-panel-img-caption",
                            children=[
                                """
    **Figure 1:** Schematic showing the effect of sea level rise on flooding events. For the same flooding threshold, sea level rise will cause the highest ocean levels to get higher and flooding thresholds to be exceeded more often.
                                """
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]

    return [*title_dom, *about_sections]

