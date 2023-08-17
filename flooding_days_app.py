import dash
from dash import dcc, html
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

import pandas as pd
import json
from urllib.parse import parse_qs

from graphs.stations_map import create_stations_map
from graphs.observed_flooding import (
    station_levels,
    observed_flooding,
    observed_flooding_text,
)
from graphs.htf_projection import (
    load_projection_data,
    htf_projection,
    htf_analysis_text,
)
from graphs.clim_projection import clim_projection
from graphs.slr_projection import slr_projection, slr_budget
from graphs.pentad_projection import pentad_projection

from layouts.options_layout import (
    generate_app_header,
    generate_options,
    generate_tabs,
    generate_stations_map,
)
from layouts.obs_flood_layout import generate_obs_flood_page
from layouts.slr_projection_layout import generate_slr_page
from layouts.htf_projection_layout import generate_htf_projection_page
from layouts.about_layout import generate_about_page
from layouts.info_modals_layout import generate_intro_modal, generate_info_modal

# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
# SETUP APP
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no",
        }
    ],
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, dbc.themes.YETI],
    suppress_callback_exceptions=True,
)
app.title = "Flooding Days v2"

# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
# INITIALIZE
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

init = dict(station=None, scenario="int", threshold="minor", year="2050",)

fname = "./data/stations.json"
with open(fname, "r") as f:
    stations = pd.DataFrame(json.load(f)).T

graph_init = go.Figure()
graph_init.update_xaxes(visible=False)
graph_init.update_yaxes(visible=False)
graph_init.update_layout(template="none")
init["graph"] = graph_init

options = dict(
    station=[dict(label=stations.name.loc[sid], value=sid) for sid in stations.index],
    scenario=[
        dict(label="Observed Trajectory", value="traj"),
        dict(label="Low", value="low"),
        dict(label="Intermediate Low", value="int_low"),
        dict(label="Intermediate", value="int"),
        dict(label="Intermediate High", value="int_high"),
        dict(label="High", value="high"),
    ],
    threshold=[
        dict(label="NOAA Minor", value="minor"),
        dict(label="NOAA Moderate", value="moderate"),
    ],
)

# Plotly mapbox token
mapbox_access_token = "pk.eyJ1IjoicHQwY2VhbmljIiwiYSI6ImNreGZiZjFjdzE4ZGEyb280N2t2cWplZmMifQ.2l-fZ2_g3WYTsNy2roxscA"

# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
# GENERATE INITIAL DOM
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

# generate dom for layout components
app_header = generate_app_header()
stations_map = generate_stations_map(init)
app_pages = {
    "observed-flooding": {
        "name": "Observed Flooding",
        "dom": generate_obs_flood_page(init),
    },
    "sea-level-rise": {"name": "Sea-Level Rise", "dom": generate_slr_page(init),},
    "projected-flooding": {
        "name": "Projected Flooding",
        "dom": generate_htf_projection_page(init),
    },
    "about": {"name": "About", "dom": generate_about_page(),},
}
app_pages_names = {pg: app_pages[pg]["name"] for pg in app_pages}
app_options = generate_options(options)
app_tabs = generate_tabs(app_pages_names)

about_sections = [
    "about-instructions",
    "about-background",
    "about-methodology",
]

intro_modal = generate_intro_modal()
info_modal_elements = [
    "threshold-picker",
    "scenario-picker",
    "scenario-graph",
    # "scenario-table",
    "budget-graph",
    "observed-graph",
    "projected-graph",
    "climatology-graph",
    "extreme-graph",
]
info_modals = [generate_info_modal(e) for e in info_modal_elements]

# generate app dom
app.layout = html.Div(
    id="app-container",
    children=[
        dcc.Location(id="url", refresh=False),  # represents URL bar
        html.Div(id="app_header", children=app_header,),
        html.Div(id="stations-map", children=stations_map,),
        html.Div(id="sticky-header", children=[app_tabs, app_options]),
        html.Div(
            id="app-page-container",
            children=[app_pages[pg]["dom"] for pg in app_pages],
        ),
        html.Div(id="intro-modal-container", children=intro_modal,),
        html.Div(id="info-modals", children=info_modals,),
        dcc.Store(id="redraw-map-store", data=True,),
        dcc.Store(id="last-map-redraw-was-hidden-store", data="",),
        dcc.Store(id="station-id-store", data=None,),
        dcc.Store(id="thresholds-store", data="",),
        dcc.Store(id="current-threshold-store", data="",),
        dcc.Store(id="slr-scenarios-data-store", data="",),
        dcc.Store(id="slr-budget-data-store", data=None,),
        dcc.Store(id="slr-budget-year-store", data=init["year"],),
        dcc.Store(id="clim-prjn-data-store", data="",),
        dcc.Store(id="clim-year-store", data=init["year"],),
    ],
)

# elements to hide on load
hidden_if_no_station = [
    "threshold-select-column",
    "scenario-select-column",
    "observed-flooding",
    "sea-level-rise",
    "projected-flooding",
]
visible_if_no_station = [
    "get-started-column",
]

# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
# DEFINE CALLBACKS
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# URL/TABS/OPTIONS CALLBACK


# @app.callback(
#     Output("about-content", "children"), Input("about-tabs", "value"),
# )
# def about_tab_content(active_tab_id):
#     return generate_about_tab_content(active_tab_id)


@app.callback(
    # ---------------------------------------------------------------------------------
    Output("url", "pathname"),
    Output("url", "search"),
    Output("app-tabs", "value"),
    Output("app-options-container", "style"),
    Output("show-map-toggle", "value"),
    Output("stations-map-collapse", "is_open"),
    Output("redraw-map-store", "data"),
    Output("units-toggle", "value"),
    Output("yoi-toggle", "value"),
    Output("station-select", "value"),
    Output("station-id-store", "data"),
    Output("coops-station-id", "children"),
    Output("coops-station-link", "href"),
    Output("scenario-select", "value"),
    Output("scenario-select", "options"),
    Output("scenario-select-container", "className"),
    Output("scenario-select", "disabled"),
    Output("scenario-picker-info-button", "disabled"),
    Output("slr-scenarios-data-store", "data"),
    Output("slr-budget-data-store", "data"),
    Output("threshold-select", "value"),
    Output("threshold-select", "options"),
    Output("threshold-float", "value"),
    Output("threshold-units", "children"),
    Output("threshold-select-container", "className"),
    Output("threshold-select", "disabled"),
    Output("threshold-picker-info-button", "disabled"),
    Output("threshold-float", "disabled"),
    Output("thresholds-store", "data"),
    Output("current-threshold-store", "data"),
    Output("topten-table", "data"),
    *[Output(pg, "className") for pg in app_pages],
    *[Output(pg, "className") for pg in about_sections],
    Output("about-tabs", "value"),
    Output("about-how-threshold-update", "children"),
    Output("threshold-picker-modal-updated", "children"),
    *[Output(e, "style") for e in hidden_if_no_station],
    *[Output(e, "style") for e in visible_if_no_station],
    # ---------------------------------------------------------------------------------
    Input("url", "pathname"),
    Input("url", "search"),
    Input("app-tabs", "value"),
    Input("about-tabs", "value"),
    Input("stations-map-graph", "selectedData"),
    Input("station-select", "value"),
    Input("units-toggle", "value"),
    Input("yoi-toggle", "value"),
    Input("show-map-toggle", "value"),
    Input("scenario-select", "value"),
    Input("threshold-select", "value"),
    Input("threshold-float", "value"),
    # ---------------------------------------------------------------------------------
    State("thresholds-store", "data"),
    State("current-threshold-store", "data"),
    State("station-id-store", "data"),
    State("last-map-redraw-was-hidden-store", "data"),
)
def update_page(
    url_path,
    url_query,
    tab_select,
    about_tab_select,
    map_station_select,
    drp_station_select,
    units_toggle,
    yoi_toggle,
    show_map_toggle,
    scenario_select,
    threshold_select,
    threshold_float,
    thresholds_store,
    current_threshold_store,
    station_id_store,
    last_map_redraw_was_hidden,
):

    # ---------------------------------------------------------------------------------

    trigger = dash.callback_context.triggered[0]["prop_id"]
    parsed_queries = parse_qs(url_query[1:])

    threshold_key = None
    threshold_units = "ft" if units_toggle else "m"

    show_map = None

    # ---------------------------------------------------------------------------------
    # URL INPUT

    if trigger == "url.pathname":
        # logic for handling changes in the url bar

        url_page = "projected-flooding" if url_path[1:] == "" else url_path[1:]
        if url_page[:5] == "about":
            about_tab_select = f"about-{url_page[6:]}"
            url_page = url_page[:5]

        station_id = (
            parsed_queries["station-id"][0]
            if "station-id" in parsed_queries
            else drp_station_select
        )

        show_map_query = parsed_queries["map"][0] if "map" in parsed_queries else None
        show_map_toggle = (
            (False if show_map_query == "hide" else True)
            if show_map_query is not None
            else show_map_toggle
        )

        show_map = False if url_page == "about" else True

        units_query = parsed_queries["units"][0] if "units" in parsed_queries else None
        units_toggle = (
            (False if units_query == "meters" else True)
            if units_query is not None
            else units_toggle
        )

        scenario_query = (
            parsed_queries["scenario"][0] if "scenario" in parsed_queries else None
        )
        possible_scenario_queries = [
            s["value"].replace("_", "-") for s in options["scenario"]
        ]
        scenario_query = (
            scenario_query if scenario_query in possible_scenario_queries else None
        )
        scenario_select = (
            scenario_query.replace("-", "_")
            if scenario_query is not None
            else scenario_select
        )

        threshold_query = (
            parsed_queries["threshold"][0] if "threshold" in parsed_queries else None
        )
        if threshold_query is not None:
            threshold_query_valid = (
                threshold_query.isnumeric()
                & (len(threshold_query) == 3)
                & (int(threshold_query) <= 300)
            )
            threshold_key = threshold_query if threshold_query_valid else None
        else:
            threshold_key = None

        yoi_query = parsed_queries["yoi"][0] if "yoi" in parsed_queries else None
        yoi_toggle = (
            (False if yoi_query == "hide" else True)
            if yoi_query is not None
            else yoi_toggle
        )

        # thresholds_store, _ = station_levels(station_id)
        # possible_threshold_queries = [
        #     d["value"]
        #     for d in thresholds_store
        #     if d["value"] not in ["mhhw", "msl", "mllw"]
        # ]
        # threshold_query = (
        #     threshold_query if threshold_query in possible_threshold_queries else None
        # )
        # threshold_select = (
        #     threshold_query.replace("-", "_")
        #     if threshold_query is not None
        #     else threshold_select
        # )

    else:

        url_page = tab_select
        station_id = (
            map_station_select["points"][0]["customdata"]["id"]
            if trigger == "stations-map-graph.selectedData"
            else drp_station_select
        )
        show_map_query = None
        units_query = None
        scenario_query = None
        threshold_query = None
        yoi_query = None

    # --------------------------------------------------------------------
    # HIDE/SHOW ELEMENTS IF NO STATION IS SELECTED

    hidden_no_sta = [
        dict(display="none") if station_id is None else dict()
        for e in hidden_if_no_station
    ]
    visible_no_sta = [
        dict(display="none") if station_id is not None else dict()
        for e in visible_if_no_station
    ]

    # ---------------------------------------------------------------------------------
    # TAB UPDATE

    if trigger in ["app-tabs.value", "about-tabs.value"] or url_page != tab_select:

        # display correct app page based on url
        app_page_classes_base = "app-page"
        app_page_classes = {
            pg: app_page_classes_base + " current-app-page"
            if pg == url_page
            else app_page_classes_base + " hidden-app-page"
            for pg in app_pages
        }

        if url_page == "about":

            options_show = dict(display="none")
            show_map = False

            scenario_select_class = dash.dash.no_update
            scenario_select_disabled = dash.dash.no_update
            threshold_select_class = dash.dash.no_update
            threshold_select_disabled = dash.dash.no_update

            # display correct about page based on url
            about_page_classes_base = "app-page-section"
            about_page_classes = {
                pg: about_page_classes_base + " current-app-page"
                if pg == about_tab_select
                else about_page_classes_base + " hidden-app-page"
                for pg in about_sections
            }

        else:

            options_show = dict(display="block")
            show_map = show_map_toggle
            about_content = dash.dash.no_update

            # disable irrelevant options
            option_class_base = "selection-container"
            scenario_select_class = (
                option_class_base + " irrelevant-option"
                if url_page in ["observed-flooding"]
                else option_class_base
            )
            scenario_select_disabled = (
                True if url_page in ["observed-flooding"] else False
            )
            threshold_select_class = (
                option_class_base + " irrelevant-option"
                if url_page in ["sea-level-rise"]
                else option_class_base
            )
            threshold_select_disabled = (
                True if url_page in ["sea-level-rise"] else False
            )

            about_page_classes = {pg: dash.dash.no_update for pg in about_sections}

    else:

        options_show = dash.dash.no_update
        show_map = show_map_toggle if show_map is None else show_map
        scenario_select_class = dash.dash.no_update
        scenario_select_disabled = dash.dash.no_update
        threshold_select_class = dash.dash.no_update
        threshold_select_disabled = dash.dash.no_update
        app_page_classes = {pg: dash.dash.no_update for pg in app_pages}
        about_page_classes = {pg: dash.dash.no_update for pg in about_sections}

    # ---------------------------------------------------------------------------------
    # REMAKE GRAPHS FOR STATION/UNITS UPDATE

    # get current station id
    current_station_id = station_id_store
    coops_station_link = (
        f"https://co-ops.nos.noaa.gov/stationhome.html?id={station_id_store}"
    )

    # update threshold options
    if station_id is not None and (
        station_id != current_station_id or trigger == "units-toggle.value"
    ):

        # update station id
        station_id_store = station_id
        coops_station_link = (
            f"https://co-ops.nos.noaa.gov/stationhome.html?id={station_id_store}"
        )

        # update threshold options
        thresholds_store, topten_table, thresholds_updated = station_levels(
            station_id, units_toggle
        )
        threshold_options = [
            {k: d[k] for k in d if k not in ["height", "height_key"]}
            for d in thresholds_store
            if d["value"] not in ["mhhw", "msl", "mllw"]
        ]
        threshold_options += [{"value": "custom", "label": "Custom"}]

        # change threshold to default threshold if current threshold not an option
        if threshold_select not in [t["value"] for t in threshold_options]:
            for h in thresholds_store:
                if h["value"] == init["threshold"]:
                    threshold_key = h["height_key"]
                    break

        # load SLR scenarios
        filename = f"./data/slr_scenarios/{station_id_store}.json"
        with open(filename, "r") as fo:
            slr_scn = json.load(fo)

        # check if station has selected scenario; if not return to default
        scenario_select = (
            scenario_select if scenario_select in slr_scn["names"] else init["scenario"]
        )
        scenario_options = [
            s for s in options["scenario"] if s["value"] in slr_scn["names"]
        ]

        # make json strings for storing SLR scenario info
        slr_scenarios_data_store = json.dumps(
            {s: slr_scn[s] for s in slr_scn if s != "contributions"}
        )
        slr_budget_data_store = json.dumps(
            {s: slr_scn[s] for s in ["contributions", "names"]}
        )

    else:

        station_id_store = dash.dash.no_update
        units_toggle = dash.dash.no_update
        thresholds = dash.dash.no_update
        topten_table = dash.dash.no_update
        threshold_options = dash.dash.no_update
        scenario_options = dash.dash.no_update
        slr_scenarios_data_store = dash.dash.no_update
        slr_budget_data_store = dash.dash.no_update
        thresholds_updated = dash.dash.no_update

    # update stations map, but not if user selecting stations from the map
    if (
        station_id != current_station_id
        and trigger != "stations-map-graph.selectedData"
    ) or (show_map_toggle and last_map_redraw_was_hidden):
        redraw_map_store = True
    else:
        redraw_map_store = dash.dash.no_update

    # ---------------------------------------------------------------------------------
    # THRESHOLD SELECTION LOGIC

    if station_id is not None:

        if trigger == "threshold-select.value" or threshold_key is None:
            for h in thresholds_store:
                if h["value"] == threshold_select:
                    threshold_key = h["height_key"]
                    break

        if trigger == "threshold-float.value" or threshold_key is None:
            threshold_float = float(threshold_float)
            threshold_m = (
                round(threshold_float / 3.281, 2)
                if units_toggle
                else round(threshold_float, 2)
            )
            threshold_m = max(threshold_m, 0.0)
            threshold_m = min(threshold_m, 3.0)
            threshold_key = "{:03}".format(int(100 * threshold_m))

        threshold_name = None
        for h in thresholds_store:
            if (h["height_key"] == threshold_key) & (
                h["value"] not in ["msl", "mllw", "mhhw"]
            ):
                threshold_select = h["value"]
                threshold_name = h["label"]
                break
        threshold_select = "custom" if threshold_name is None else threshold_select

        current_threshold_store = {
            "key": threshold_key,
            "name": threshold_name if threshold_name is not None else "Custom",
            "m": round(float(threshold_key) / 100, 2),
            "ft": round(3.281 * float(threshold_key) / 100, 2),
        }

        threshold_float = current_threshold_store[threshold_units]

    else:

        threshold_select = dash.dash.no_update
        threshold_float = dash.dash.no_update

    # ---------------------------------------------------------------------------------
    # CONSTRUCT UPDATED URL

    url_path = "/" + url_page
    url_path = (
        url_path + "/" + about_tab_select[6:] if url_page == "about" else url_path
    )
    url_queries = {
        "station-id": station_id,
        "map": ("hide" if not show_map_toggle else "show")
        if show_map_query is not None or not show_map_toggle
        else None,
        "units": ("meters" if not units_toggle else "feet")
        if units_query is not None or not units_toggle
        else None,
        "scenario": scenario_select.replace("_", "-")
        if scenario_query is not None or (scenario_select != "int")
        else None,
        "threshold": threshold_key
        if threshold_query is not None or (threshold_select != "minor")
        else None,
        "yoi": ("hide" if not yoi_toggle else "show")
        if yoi_query is not None or yoi_toggle
        else None,
    }
    order_queries = [
        *[q for q in url_queries if q in parsed_queries],
        *[q for q in url_queries if q not in parsed_queries],
    ]
    url_queries = "?" + "&".join(
        [q + "=" + url_queries[q] for q in order_queries if url_queries[q] is not None]
    )

    # ---------------------------------------------------------------------------------
    # SUPPRESS UPDATES TO OPTIONS/GRAPHS IN SOME CASES
    # can't do this earlier, because values are needed for updating url

    # suppress updates if hiding/showing stations map or switching tabs
    if trigger in ["show-map-toggle.value", "app-tabs.value"]:
        station_id_store = dash.dash.no_update
        units_toggle = dash.dash.no_update
        scenario_select = dash.dash.no_update
        threshold_select = dash.dash.no_update

    # ---------------------------------------------------------------------------------
    # RETURN OUTPUTS
    return (
        url_path,
        url_queries,
        url_page,
        options_show,
        show_map_toggle,
        show_map,  # for stations-map-collapse.is_open; same value as toggle
        redraw_map_store,
        units_toggle,
        yoi_toggle,
        station_id,
        station_id_store,
        station_id_store,
        coops_station_link,
        scenario_select,
        scenario_options,
        scenario_select_class,
        scenario_select_disabled,
        scenario_select_disabled,  # for the info button
        slr_scenarios_data_store,
        slr_budget_data_store,
        threshold_select,
        threshold_options,
        threshold_float,
        threshold_units,
        threshold_select_class,
        threshold_select_disabled,
        threshold_select_disabled,  # for the info button
        threshold_select_disabled,  # for the threshold custom input
        thresholds_store,
        current_threshold_store,
        topten_table,
        *[app_page_classes[pg] for pg in app_pages],
        *[about_page_classes[pg] for pg in about_sections],
        about_tab_select,
        thresholds_updated,
        thresholds_updated,
        *hidden_no_sta,
        *visible_no_sta,
    )


# -------------------------------------------------------------------------------------
# STATIONS MAP CALLBACK
# This callback is needed to redraw the map after uncollapsing the map div.


@app.callback(
    Output("stations-map-graph", "figure"),
    Output("last-map-redraw-was-hidden-store", "data"),
    Input("redraw-map-store", "data"),
    State("station-id-store", "data"),
    State("show-map-toggle", "value"),
)
def redraw_stations_map(
    redraw_map_store, station_id_store, show_map_toggle,
):

    last_map_redraw_was_hidden = (
        True if redraw_map_store and not show_map_toggle else False
    )

    if redraw_map_store:
        stations_map = create_stations_map(
            stations, mapbox_access_token, station_select=station_id_store
        )
        return stations_map, last_map_redraw_was_hidden

    else:
        raise PreventUpdate()


# -------------------------------------------------------------------------------------
# EXTREME SL OBSERVATIONS CALLBACK


@app.callback(
    Output("obs-flood-graph", "figure"),
    Output("topten-location", "children"),
    Output("obs-flood-analysis-threshold", "children"),
    Output("obs-flood-analysis-content", "children"),
    Input("station-id-store", "data"),
    Input("thresholds-store", "data"),
    Input("current-threshold-store", "data"),
    Input("units-toggle", "value"),
)
def update_obs_flood_graph(
    station_id_store, thresholds_store, current_threshold_store, units_toggle,
):

    units_toggle = "ft" if units_toggle else "m"

    trigger = dash.callback_context.triggered[0]["prop_id"]
    relevant_triggers = [
        "station-id-store.data",
        "current-threshold-store.data",
        "thresholds-store.data",
        "units-toggle.value",
    ]

    if trigger in relevant_triggers and station_id_store is not None:

        station_name = stations.loc[station_id_store, "name"]
        threshold_name = current_threshold_store["name"]

        obs_flood_graph, obs_flood_analysis = observed_flooding(
            station_id_store,
            current_threshold_store["key"],
            thresholds_store,
            units_toggle,
        )

        obs_flood_text = observed_flooding_text(
            station_name, threshold_name, obs_flood_analysis,
        )

    else:
        raise PreventUpdate()

    return (
        obs_flood_graph,
        station_name,
        threshold_name,
        obs_flood_text,
    )


# -------------------------------------------------------------------------------------
# EXTREME SL PROJECTIONS CALLBACK


@app.callback(
    Output("htf-graph", "figure"),
    Output("htf-graph-title-scenario", "children"),
    Output("htf-graph-title-threshold", "children"),
    Output("clim-prjn-data-store", "data"),
    Output("pent-graph", "figure"),
    Output("pent-graph-title-scenario", "children"),
    Output("pent-graph-title-threshold", "children"),
    Output("htf-chronic-content", "children"),
    Output("htf-yoi-content", "children"),
    Output("xtrm-analysis-content", "children"),
    Output("htf-yoi-analysis", "style"),
    Input("station-id-store", "data"),
    Input("scenario-select", "value"),
    Input("current-threshold-store", "data"),
    Input("units-toggle", "value"),
    Input("yoi-toggle", "value"),
    State("thresholds-store", "data"),
    prevent_initial_call=True,
)
def update_htf_graph(
    station_id_store,
    scenario_select,
    current_threshold_store,
    units_toggle,
    yoi_toggle,
    thresholds,
):

    units_toggle = "ft" if units_toggle else "m"

    trigger = dash.callback_context.triggered[0]["prop_id"]
    relevant_triggers = [
        "station-id-store.data",
        "scenario-select.value",
        "threshold-select.value",
        "units-toggle.value",
        "yoi-toggle.value",
    ]

    if trigger in relevant_triggers and station_id_store is not None:

        meta, prjn, clim, pent, prob = load_projection_data(
            stations.loc[station_id_store],
            scenario_select,
            current_threshold_store["key"],
        )

        meta["steps_xd"] = (
            [prjn[50].loc[s] for s in meta["steps"]]
            if meta["steps"] is not None
            else None
        )

        display_yoi = {"display": "block" if meta["steps"] is not None else "none"}

        htf_graph, yr_lims = htf_projection(meta, prjn, yoi_toggle)
        pent_graph = pentad_projection(meta, pent, yr_lims)
        htf_content, xtrm_content = htf_analysis_text(meta, prob, prjn, pent)

        scenario_name = [
            scn["label"]
            for scn in options["scenario"]
            if scn["value"] == scenario_select
        ][0]

    else:
        raise PreventUpdate()

    return (
        htf_graph,
        scenario_name,
        current_threshold_store["name"],
        clim,
        pent_graph,
        scenario_name,
        current_threshold_store["name"],
        htf_content["chronic"],
        htf_content["yoi"],
        xtrm_content,
        display_yoi,
    )  # htf_table_data


# -------------------------------------------------------------------------------------
# EXTREME SL CLIMATOLOGY PROJECTIONS CALLBACK


@app.callback(
    [
        Output("clim-graph", "figure"),
        Output("clim-year", "children"),
        Output("clim-year-store", "data"),
    ],
    [
        Input("htf-graph", "hoverData"),
        Input("htf-graph", "clickData"),
        Input("clim-prjn-data-store", "data"),
    ],
    [State("clim-year-store", "data"),],
)
def update_clim_graph(prjn_hover, prjn_click, clim_json, clim_year_store):

    trigger = dash.callback_context.triggered[0]["prop_id"]

    if trigger == "htf-graph.hoverData":  # , "clim-prjn-data-store.data"]:
        if prjn_hover is not None:
            clim_year = prjn_hover["points"][0]["x"]
        else:
            clim_year = clim_year_store
    elif trigger == "htf-graph.clickData":
        clim_year = prjn_click["points"][0]["x"]
        clim_year_store = clim_year
    else:
        clim_year = clim_year_store

    return clim_projection(clim_json, clim_year), clim_year, clim_year_store


# -------------------------------------------------------------------------------------
# SLR PROJECTIONS CALLBACK


@app.callback(
    [
        Output("slr-graph", "figure"),
        Output("app-options-slr-year", "children"),
        Output("app-options-scenario-text", "children"),
        Output("slr-summary-table", "data"),
        Output("slr-likelihood-statement", "children"),
    ],
    [
        Input("station-id-store", "data"),
        Input("scenario-select", "value"),
        Input("units-toggle", "value"),
        Input("slr-scenarios-data-store", "data"),
    ],
)
def update_slr_graph(
    station_id_store, scenario_select, units_toggle, slr_scenarios_json,
):

    trigger = dash.callback_context.triggered[0]["prop_id"]
    relevant_triggers = [
        "scenario-select.value",
        "units-toggle.value",
        "station-id-store.data",
    ]

    if trigger in relevant_triggers and station_id_store is not None:

        units_toggle = "ft" if units_toggle else "m"
        slr = json.loads(slr_scenarios_json)

        slr_graph = slr_projection(slr, scn_focus=scenario_select, units=units_toggle)

        scn_fullname = slr["names"][scenario_select]

        slr_year = 2100 if scenario_select != "traj" else 2050

        years_key = "traj" if scenario_select == "traj" else "scenarios"
        slr_by_year = [
            v
            for y, v in zip(
                slr["scenarios"]["years"][years_key],
                slr["scenarios"]["values"][scenario_select]["50"],
            )
            if y == slr_year
        ][0]
        slr_by_year = slr_by_year * 3.28084 if units_toggle == "ft" else slr_by_year
        slr_by_year = str(int(100 * slr_by_year) / 100) + " " + units_toggle

        slr_table_data = pd.DataFrame(
            {
                s: slr["scenarios"]["values"][s]["50"]
                for s in slr["names"]
                if s != "traj"
            },
            index=slr["scenarios"]["years"]["scenarios"],
        )
        if "traj" in slr["names"]:
            slr_table_data["traj"] = pd.Series(
                slr["scenarios"]["values"]["traj"]["50"],
                index=slr["scenarios"]["years"]["traj"],
            )

        slr_table_data = (slr_table_data.loc[[2050, 2075, 2100], :].T).round(2)
        slr_table_data = (
            slr_table_data.astype(str).replace("nan", "–") + " " + units_toggle
        )
        slr_table_data["Scenario"] = [slr["names"][s] for s in slr_table_data.index]
        slr_table_data["id"] = [s for s in slr_table_data.index]
        slr_table_data = slr_table_data.loc[:, ["id", "Scenario", 2050, 2100]]

        scn_index = ["low", "int_low", "int", "int_high", "high", "traj"]
        prb_table = pd.DataFrame(
            {
                "3ºC GSW": [">99%", "82%", "5%", "<1%", "<1%", "-%"],
                "5ºC GSW": [">99%", "97%", "10%", "1%", "<1%", "-%"],
                "VHE/LCP": [">99%", "96%", "49%", "20%", "8%", "-%"],
            },
            index=scn_index,
        )

        for c in prb_table.columns:
            slr_table_data[c] = prb_table.loc[slr_table_data.index, c]

        slr_table_data = slr_table_data.to_dict("records")

        # options_slr_table_data = slr_table_data.loc[
        #     slr_table_data.index == scenario_select, [2050, 2100]
        # ]

        # options_slr_table_data = options_slr_table_data.to_dict("records")

        lkhd_table = pd.DataFrame(
            {
                "3ºC GSW": [
                    "virtually certain",
                    "likely",
                    "very unlikely",
                    "exceptionally unlikely",
                    "exceptionally unlikely",
                    "N/A",
                ],
                "5ºC GSW": [
                    "virtually certain",
                    "very likely",
                    "very unlikely",
                    "exceptionally unlikely",
                    "exceptionally unlikely",
                    "N/A",
                ],
                "VHE/LCP": [
                    "virtually certain",
                    "very likely",
                    "about as likely as not",
                    "unlikely",
                    "very unlikely",
                    "N/A",
                ],
            },
            index=scn_index,
        )

        lkhd_prb = {
            "virtually certain": "99–100% chance",
            "very likely": "90–100% chance",
            "likely": "66–100% chance",
            "about as likely as not": "33–66% chance",
            "unlikely": "0–33% chance",
            "very unlikely": "0–10% chance",
            "exceptionally unlikely": "0–1% chance",
        }

        if scenario_select == "traj":
            slr_likelihood = "Likelihoods are not evaluated for Observed Trajectories."
        else:
            l3deg = lkhd_table.loc[scenario_select, "3ºC GSW"]
            l5deg = lkhd_table.loc[scenario_select, "5ºC GSW"]
            lmici = lkhd_table.loc[scenario_select, "VHE/LCP"]
            slr_likelihood = [
                dcc.Markdown(
                    [
                        f"The [2022 U.S. Interagency Task Force (ITF) report](https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-tech-report-sections.html) provides the likelihood that *global* mean sea level will meet or exceed the ITF scenarios given various levels of global warming/emissions from [IPCC AR6 ](https://www.ipcc.ch/assessment-report/ar6/) climate models. Note that the likelihood of *local* mean sea level meeting or exceeding a given *local* scenario may differ slightly from the global likelihoods, but the global likelihoods provide a general sense of how likely the scenarios are under various future conditions. The likelihood that *global* sea-level rise will meet or exceed the selected **{scn_fullname} Scenario** by 2100 is ... ",
                    ],
                    link_target="_blank",
                ),
                dcc.Markdown(
                    id="slr-likelihood-bullets",
                    children=[
                        f"- ***{l3deg.capitalize()}*** for 3ºC of global average surface warming ({lkhd_prb[l3deg]})\*",
                        f"- ***{l5deg.capitalize()}*** for 5ºC of global average surface warming ({lkhd_prb[l3deg]})\*",
                        f"- ***{lmici.capitalize()}*** for very high greenhouse gas emissions** when including the potential for marine ice cliff instability ({lkhd_prb[lmici]})\*",
                    ],
                ),
            ]

        return (
            slr_graph,
            slr_year,
            slr_by_year,
            slr_table_data,
            slr_likelihood,
        )

    else:
        raise PreventUpdate()


# -------------------------------------------------------------------------------------
# SLR BUDGET GRAPH CALLBACK


@app.callback(
    [
        Output("slr-budget-graph", "figure"),
        Output("slr-budget-year", "children"),
        Output("slr-budget-year-store", "data"),
    ],
    [
        Input("slr-graph", "hoverData"),
        Input("slr-graph", "clickData"),
        Input("slr-budget-data-store", "data"),
        # Input("slr-budget-year-input", "value"),
        Input("scenario-select", "value"),
        Input("units-toggle", "value"),
        State("slr-budget-year-store", "data"),
    ],
)
def update_slr_budget_graph(
    slr_hover,
    slr_click,
    budget_json,
    # budget_year_input,
    scenario_select,
    units_toggle,
    budget_year_store,
):

    if budget_json is not None:

        units_toggle = "ft" if units_toggle else "m"
        trigger = dash.callback_context.triggered[0]["prop_id"]

        if trigger == "slr-graph.hoverData":
            if slr_hover is not None:
                budget_year = slr_hover["points"][0]["x"]
            else:
                budget_year = budget_year_store
        elif trigger == "slr-graph.clickData":
            budget_year = slr_click["points"][0]["x"]
            budget_year_store = budget_year
        else:
            budget_year = budget_year_store
            budget_year_store = budget_year

        budget_year = int(budget_year)
        budget_year = (
            2020
            if budget_year < 2020
            else (2100 if budget_year > 2100 else budget_year)
        )

        budget_dict = json.loads(budget_json)

        slr_budget_graph = slr_budget(
            budget_dict,
            year_focus=budget_year,
            scn_focus=scenario_select,
            units=units_toggle,
            single_scn=True,
        )

        return slr_budget_graph, budget_year, budget_year_store

    else:

        raise PreventUpdate()


# -------------------------------------------------------------------------------------
# SLR PROJECTIONS TABLE CALLBACK


@app.callback(
    Output("slr-summary-table", "style_data_conditional"),
    Input("scenario-select", "value"),
)
def style_selected_rows(scenario):
    if scenario is None:
        raise PreventUpdate()
    style_conditional = [
        {
            "if": {"filter_query": "{{id}}={}".format(scenario)},
            "backgroundColor": "#D7EDF9",
        }
    ]
    return style_conditional


# -------------------------------------------------------------------------------------
# ABOUT TABS CALLBACK


# @app.callback(
#     Output("about-content", "children"), Input("about-tabs", "value"),
# )
# def about_tab_content(active_tab_id):
#     return generate_about_tab_content(active_tab_id)


# -------------------------------------------------------------------------------------
# INFO MODALS CALLBACKS


@app.callback(
    [Output(f"{e}-info-modal", "is_open") for e in info_modal_elements],
    [Input(f"{e}-info-button", "n_clicks") for e in info_modal_elements],
    [State(f"{e}-info-modal", "is_open") for e in info_modal_elements],
)
def toggle_modal(*inputs):

    trigger = dash.callback_context.triggered[0]["prop_id"]
    elem = trigger[:-21]

    if elem in info_modal_elements:

        ne = info_modal_elements.index(elem)
        n_clicks = inputs[ne]
        is_open = [
            not io if (n == ne) and n_clicks else io
            for n, io in enumerate(inputs[len(info_modal_elements) :])
        ]

        return is_open

    else:
        raise PreventUpdate()


# -------------------------------------------------------------------------------------
# INTRO MODAL CALLBACK


@app.callback(
    Output("intro-modal", "is_open"),
    Input("intro-modal-close", "n_clicks"),
    Input("intro-modal-instructions-link", "n_clicks"),
    Input("station-id-store", "data"),
)
def toggle_modal(close_clicks, instructions_clicks, station_id_store):

    if (close_clicks > 0) or (instructions_clicks > 0) or station_id_store is not None:
        return False
    elif station_id_store is None:
        return True
    else:
        raise PreventUpdate()


# -------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run_server(debug=False, port=8090)
