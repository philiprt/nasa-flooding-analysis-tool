import pandas as pd
import numpy as np
import json

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc, html

import graphs.analysis as anlyz


def station_levels(station_id, units_toggle=True):

    units = "ft" if units_toggle else "m"

    fname = "./data/levels/" + station_id + ".json"
    with open(fname, "r") as f:
        levels = json.load(f)

    updated = levels["updated"]

    levels = {k: levels[k] for k in levels if levels[k] is not None}

    levels["datums"] = {
        d: levels["datums"][d] for d in levels["datums"] if d in ["msl", "mhhw", "mllw"]
    }

    # extract top ten events before replacing levels variable
    for n in range(len(levels["topten"])):
        levels["topten"][n]["height"] = (
            np.round(levels["topten"][n]["height"] * 3.28084, 2)
            if units == "ft"
            else np.round(levels["topten"][n]["height"], 2)
        )

    topten = [
        {
            "date": ev["date"],
            "height": str(ev["height"]) + " " + units,
            "type": "topten",
        }
        for ev in levels["topten"]
    ]

    # make one dict from all types of levels and convert units if necessary
    levels = {
        lev: levels[lev_type][lev]
        for lev_type in [k for k in levels if k in ["datums", "flood", "extremes"]]
        for lev in levels[lev_type]
        if levels[lev_type][lev] is not None
    }

    levels_names = {
        "minor": "NOAA Minor",
        "moderate": "NOAA Moderate",
        "major": "NOAA Major",
        "nws_minor": "NWS Minor",
        "nws_moderate": "NWS Moderate",
        "nws_major": "NWS Major",
        "100yr": "100-year flood",
        "10yr": "10-year flood",
        "2yr": "2-year flood",
        "1yr": "1-year flood",
        "msl": "Mean Sea Level",
        "mhhw": "Mean Higher High Water",
        "mllw": "Mean Lower Low Water",
    }

    levels = [
        dict(
            value=h,
            label=levels_names[h],
            height=np.round(levels[h] * 3.28084, 2)
            if units == "ft"
            else np.round(levels[h], 2),
            height_key=f"{round(100*levels[h]):0>3}",
        )
        for h in levels
        if levels[h] is not None
    ]

    topten_with_return_periods = []
    mx_ht = 100
    for rp in [
        lev for lev in levels if lev["value"] in ["100yr", "10yr", "2yr", "1yr"]
    ]:

        for tt in topten:
            tt_ht = float(tt["height"].split(" ")[0])
            if (tt_ht >= rp["height"]) and (tt_ht < mx_ht):
                topten_with_return_periods.append(tt)

        topten_with_return_periods.append(
            dict(date=rp["label"], height=f"{rp['height']} {units}", type="return")
        )

        mx_ht = rp["height"]

    # htf_table_data = prjn.loc[[2050, 2075, 2100], :].astype(int)
    # # htf_table_data
    # htf_table_data = pd.DataFrame(
    #     htf_table_data[10].astype(str) + "–" + htf_table_data[50].astype(str)
    # ).T
    # htf_table_data[:] = ["0" if v == "0–0" else v for v in htf_table_data.values[0]]
    # htf_table_data[:] = [
    #     "365" if v == "365–365" else v for v in htf_table_data.values[0]
    # ]
    # htf_table_data = htf_table_data.to_dict("records")

    return levels, topten_with_return_periods, updated


def observed_flooding(station_id, threshold_key, levels, units):

    col = anlyz.color_palette()
    # fcol = [anlyz.fill_color(c, 0.25) for c in col if c[0] == "#"]

    # load station daily min/max data
    fname = f"./data/day_min_max/{station_id}.csv"
    dy = pd.read_csv(fname, index_col=0, parse_dates=True)

    blank = dy["max"].isna() | dy["min"].isna()
    dy.loc[blank, :] = None

    dy = (dy * 3.28084).round(3) if units == "ft" else dy
    obs_max = dy["max"].max()

    dy = dy.dropna()

    first_obs = dy.index[0].strftime("%Y-%m-%d")
    last_obs = dy.index[-1].strftime("%Y-%m-%d")
    record_length = (dy.index[-1] - dy.index[0]).days / 365.25  # years

    # split data into chunks at missing data; this is necessary for filling the area
    # between min and max in the plot and preventing filling through missing data.
    tdiff = dy.index[1:] - dy.index[:-1]
    splits = np.hstack([[0], np.where(tdiff.days.values > 1)[0] + 1, -1])
    dy_splits = [dy.iloc[i1:i2] for i1, i2 in zip(splits[:-1], splits[1:])]

    # reorganize levels info
    thresholds = {h["value"]: h["height"] for h in levels}
    threshold_names = {h["value"]: h["label"] for h in levels}

    # convert
    this_threshold = [
        lev["value"] for lev in levels if lev["height_key"] == threshold_key
    ]
    if len(this_threshold) == 0:
        this_threshold = "custom"
        thrsh_ht = int(threshold_key) / 100
        thresholds[this_threshold] = (
            round(thrsh_ht * 3.28084, 2) if units == "ft" else thrsh_ht
        )
        threshold_names[this_threshold] = this_threshold.title()
    else:
        this_threshold = this_threshold[0]

    # load the observed flooding counts
    fname = f"./data/htf_observed/{station_id}/{threshold_key}.json"
    with open(fname, "r") as f:
        htfo = json.load(f)

    # create figure
    black = "#222"
    gray = "#aaa"

    fig = go.Figure()
    fig = make_subplots(
        rows=2,
        cols=1,
        start_cell="top-left",
        row_heights=[5, 2],
        shared_xaxes=True,
        vertical_spacing=0.125,
    )

    traces = []
    for n, dys in enumerate(dy_splits):
        traces.extend(
            [
                {
                    "x": dys.index.values,
                    "y": dys["min"].values,
                    "type": "scatter",
                    "mode": "lines",
                    "fill": "tozeroy",
                    "fillcolor": "rgba(1, 1, 1, 0)",
                    "showlegend": False,
                    "line": {"color": col[1], "width": 1},
                    "hoverinfo": "none",
                },
                {
                    "x": dys.index.values,
                    "y": dys["max"].values,
                    "type": "scatter",
                    "mode": "lines",
                    "line": {"color": col[1], "width": 1},
                    "fill": "tonexty",
                    "fillcolor": col[1],
                    "showlegend": True if n == 0 else False,
                    "name": "Observed daily range (min to max)",
                    "hoverinfo": "none",
                    "legendgroup": "1",
                },
            ]
        )

    floods = dy["max"].loc[dy["max"] > thresholds[this_threshold]]
    traces.extend(
        [
            {
                "x": floods.index.values,
                "y": floods.values,
                "type": "scatter",
                "showlegend": True,
                "name": "Flooding day",  # (daily max exceeds the "
                # + threshold_names[this_threshold]
                # + " threshold)",
                "mode": "markers",
                "marker": {
                    "color": col[5],
                    "size": 9,
                    "line": dict(width=1, color="#000"),
                },
                "customdata": floods.index.strftime("%Y-%m-%d").to_list(),
                "hovertemplate": "%{y:0.2f} " + units + "<extra>%{customdata}</extra>",
                "legendgroup": "1",
            },
        ]
    )

    for trc in traces:
        fig.add_trace(trc, row=1, col=1)

    thrsh_labels = []
    thrsh_levels = []

    # loop over thresholds, but placing current threshold at the end of the list to
    # plot its marker on top
    defined_thrsh_list = [
        thrsh
        for thrsh in thresholds
        if thrsh not in [this_threshold, "mllw", "msl", "mhhw"]
    ]
    for thrsh in [
        *[thrsh for thrsh in thresholds if thrsh not in [this_threshold, "mllw"]],
        *[this_threshold],
    ]:

        color = black if thrsh in [this_threshold, "msl", "mhhw"] else gray
        lw = 2 if thrsh == this_threshold else (1 if thrsh in ["msl", "mhhw"] else 0)
        dash = "dash" if thrsh == "mhhw" else ("dot" if thrsh == "msl" else None)
        fig.add_hline(
            y=thresholds[thrsh],
            line={"color": color, "width": lw, "dash": dash},
            layer="below" if thrsh == this_threshold else "above",
            row=1,
            col=1,
        )
        if thrsh == this_threshold:
            fig.add_trace(
                dict(
                    x=dy.index.values[[0, -1]],
                    y=[thresholds[thrsh], thresholds[thrsh]],
                    mode="lines",
                    line={"color": black, "width": lw},
                    name="Selected threshold",
                    showlegend=True if thrsh == this_threshold else False,
                    hoverinfo="none",
                    legendgroup="2",
                )
            )
        static_labels = []  # [this_threshold, "msl", "mhhw"]
        if thrsh in static_labels:
            thrsh_labels.append(
                {
                    "x": 1.01,
                    "y": thresholds[thrsh],
                    "text": "<b>"
                    + threshold_names[thrsh]
                    + " ("
                    + str(thresholds[thrsh])
                    + " "
                    + units
                    + ")</b>"
                    if thrsh == this_threshold
                    else threshold_names[thrsh]
                    + " ("
                    + str(thresholds[thrsh])
                    + " "
                    + units
                    + ")",
                    "font": {"color": black if thrsh == this_threshold else "#777"},
                    "xref": "paper",
                    "yref": "y1",
                    "xanchor": "left",
                    "yanchor": "middle",
                    "borderpad": 2,
                    "showarrow": False,
                }
            )
        thrsh_levels.append(thresholds[thrsh])
        if thrsh not in ["msl", "mhhw"]:
            trace_base = {
                "x": [1],
                "y": [thresholds[thrsh]],
                "xaxis": "x3",
                "type": "scatter",
                "showlegend": True if thrsh == defined_thrsh_list[0] else False,
                "name": "Defined threshold",
                "mode": "markers",
                "marker": {
                    "symbol": "triangle-left",
                    "color": black if thrsh == this_threshold else gray,
                    "size": 10,
                },
                "cliponaxis": False,
                "legendgroup": "2",
            }
            trace_hover = (
                {"hoverinfo": "none"}
                if thrsh in static_labels
                else {
                    "hovertemplate": "%{y} "
                    + units
                    + "<extra>"
                    + threshold_names[thrsh]
                    + "</extra>"
                }
            )
            fig.add_trace({**trace_base, **trace_hover})
        else:
            fig.add_annotation(
                x=1.02,
                y=thresholds[thrsh],
                xref="paper",
                yref="y",
                text=thrsh.upper(),
                font=dict(size=12, color="#000"),
                showarrow=False,
                align="right",
                bordercolor="#000",
                borderwidth=1,
                borderpad=4,
                bgcolor="#fff",
                opacity=1.0,
            )

    fig.update_layout(annotations=thrsh_labels)

    units_full = "feet" if units == "ft" else "meters"
    fig.update_yaxes(
        title_text=units_full + " above MHHW",
        side="right",
        range=[
            # 1.25 * thresholds["mllw"],
            1.1 * thresholds["msl"],
            max(
                [
                    1.05 * thresholds[this_threshold],
                    1.05 * obs_max,
                    1.05 * thresholds["moderate"] if "moderate" in thresholds else 0,
                    1.05 * thresholds["nws_moderate"]
                    if "nws_moderate" in thresholds
                    else 0,
                ]
            ),
        ],
        row=1,
        col=1,
    )

    htfo_time = [pd.Timestamp(str(y - 1) + "-11-01") for y in htfo["annual"]["years"]]
    traces = [
        {
            "x": htfo_time,
            "y": htfo["annual"]["counts"],
            "type": "bar",
            "marker": {"color": col[0]},
            "name": "Annual counts of flooding days (bottom panel)",
            "customdata": [
                "05/" + str(d.year) + "–04/" + str(d.year + 1) for d in htfo_time
            ],
            "hovertemplate": "%{y} days <extra>%{customdata}</extra>",
            "legendgroup": "3",
        },
    ]

    for trc in traces:
        fig.add_trace(
            trc, row=2, col=1,
        )

    max_count = max([c for c in htfo["annual"]["counts"] if c is not None])
    fig.update_yaxes(
        title_text="days",
        side="right",
        range=[-0.05 - 0.05 * max_count, max_count + 1],
        row=2,
        col=1,
    )

    time_lims = [
        str(max([1900, dy_splits[0]["max"].index.year[0]])),
        dy.index[-1] + 0.015 * (dy.index[-1] - dy.index[0]),
        # f"{dy['max'].index.year[-1] + 1}-12-31",
    ]
    fig.update_xaxes(range=time_lims)

    fig.update_layout(
        template="none",
        height=600,
        margin=dict(l=70, r=30, b=30, t=30, pad=0),
        font=dict(size=14),
        xaxis=dict(layer="below traces", zeroline=False, matches="x2",),
        xaxis3=dict(
            layer="below traces",
            zeroline=False,
            overlaying="x",
            range=[0, 1.005],
            fixedrange=True,
            visible=False,
        ),
        yaxis=dict(layer="below traces", side="left", zeroline=False,),
        xaxis2=dict(showgrid=True,),
        yaxis2=dict(layer="below traces", side="left", fixedrange=True,),
        legend=dict(
            xanchor="center",
            x=0.5,
            yanchor="middle",
            y=0.375,
            bgcolor="rgba(255, 255, 255, 1)",
            bordercolor="#000",
            borderwidth=1,
            itemclick=False,
            itemdoubleclick=False,
            orientation="h",
        ),
        modebar=dict(
            remove=["toImage", "lasso", "select", "zoomIn", "zoomOut"],
            orientation="h",
            color="#333333",
            bgcolor=None,
        ),
    )

    # --------------------------------------------------------------------
    # --------------------------------------------------------------------

    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    climatology = pd.DataFrame(
        {"mo_number": range(len(months)), "total": htfo["climatology"]}, index=months
    )
    climatology["percent"] = (
        (100 * climatology.total / climatology.total.sum()).astype(int)
        if climatology.total.sum() > 0
        else 0
    )
    climatology = climatology.sort_values(by="total")

    ann_max_count = max([c for c in htfo["annual"]["counts"] if c is not None])
    ann_max_years = [
        y
        for y, c in zip(htfo["annual"]["years"], htfo["annual"]["counts"])
        if c == ann_max_count
    ]

    mo_counts = pd.DataFrame(htfo["monthly"], index=range(1, 13)).T.stack().astype(int)
    mo_max_count = mo_counts.max()
    mo_counts = mo_counts.loc[mo_counts == mo_max_count] if mo_max_count > 0 else None
    mo_max_months = (
        [f"{months[dt[1]-1]} {dt[0]}" for dt, _ in mo_counts.iteritems()]
        if mo_max_count > 0
        else None
    )

    flood_analysis = dict(
        first_obs=first_obs,
        last_obs=last_obs,
        record_length=int(np.round(record_length)),
        flood_counts=dict(overall=floods.index.size,),
        floods_per_year=dict(overall=np.round(floods.index.size / record_length, 1),),
        climatology=climatology,
        max_counts=dict(
            annual=dict(count=ann_max_count, years=ann_max_years),
            monthly=dict(count=mo_max_count, months=mo_max_months),
        ),
    )

    if htfo["long_term"] is not None:
        flood_analysis = {
            **flood_analysis,
            **dict(
                analyze_long_term=True,
                period1="–".join([f"{y}" for y in htfo["long_term"]["first_10_span"]]),
                period2="–".join([f"{y}" for y in htfo["long_term"]["last_10_span"]]),
                msl_change=htfo["long_term"]["msl_change"],
                units=units,
                f10_htf=htfo["long_term"]["f10_htf"],
                f10_htf_pyr=htfo["long_term"]["f10_htf_pyr"],
                l10_htf=htfo["long_term"]["l10_htf"],
                l10_htf_pyr=htfo["long_term"]["l10_htf_pyr"],
                htf_pyr_change=htfo["long_term"]["htf_pyr_change"],
                htf_pyr_diff_prob=htfo["long_term"]["htf_pyr_diff_prob"],
            ),
        }
    else:
        flood_analysis = {
            **flood_analysis,
            **dict(analyze_long_term=False,),
        }

    return fig, flood_analysis


# --------------------------------------------------------------------
# --------------------------------------------------------------------


def text_list_connector(mo_name, mo_index):
    return (
        " and "
        if (mo_name == mo_index[-1]) and (mo_index.size == 2)
        else (", and " if (mo_name == mo_index[-1]) and (mo_index.size > 2) else ", ")
    )


def format_text_list(L):
    L = [str(e) for e in L]
    if len(L) > 2:
        L[-1] = f"and {L[-1]}"
    return L[0] if len(L) == 1 else (" and ".join(L) if len(L) == 2 else ", ".join(L))


def observed_flooding_text(station_name, threshold_name, obs_flood_analysis):

    obs_flood_text = [
        dcc.Markdown(
            "The graphs above show the occurrence of individual flooding days for the selected threshold (top) and the number of flooding days in each meterological year (May–April, bottom). Note that **flooding days do not tend to be evenly distributed in time**. There may be an overall increase during the record due to sea-level rise. There may also be years or months when many events cluster together due to the confluence of mulitple factors—such as high sea level, higher than normal high tides, and greater storminess."
        ),
    ]

    # --------------------------------------------------------------------
    # overall record blurb

    if obs_flood_analysis["floods_per_year"]["overall"] >= 1:
        occ_cat = "common"  # more than once per year
    elif obs_flood_analysis["floods_per_year"]["overall"] >= 0.1:
        occ_cat = "infrequent"  # more than once per decade
    else:
        occ_cat = "rare"

    if obs_flood_analysis["flood_counts"]["overall"] > 0:
        overall_record_blurb = [
            "##### Over the full record\n",
            f"- Water levels in **{station_name}** exceeded the **{threshold_name}** threshold on **{obs_flood_analysis['flood_counts']['overall']} {'day' if obs_flood_analysis['flood_counts']['overall'] == 1 else 'days'}** during the {obs_flood_analysis['record_length']}-year record of observations ({obs_flood_analysis['first_obs'][:4]}–{obs_flood_analysis['last_obs'][:4]}).\n",
        ]
        if occ_cat == "common":
            overall_record_blurb.append(
                f"- **Flooding days** for this threshold are historically common, occurring on approximately **{int(obs_flood_analysis['floods_per_year']['overall'])} {'day' if obs_flood_analysis['floods_per_year']['overall'] == 1 else 'days'} per year** on average.",
            )
        elif occ_cat == "infrequent":
            overall_record_blurb.append(
                f"- **Flooding days** for this threshold do not occur every year historically, happening on approximately **{int(10 * obs_flood_analysis['floods_per_year']['overall'])} {'day' if int(10 * obs_flood_analysis['floods_per_year']['overall']) == 1 else 'days'} per decade** on average.",
            )
        else:
            overall_record_blurb.append(
                f"- **Flooding days** for this threshold are historically rare, occurring **<1 day per decade** on average.",
            )

        ann_max_count = obs_flood_analysis["max_counts"]["annual"]["count"]
        if ann_max_count >= 3:
            ann_max_years_str = format_text_list(
                obs_flood_analysis["max_counts"]["annual"]["years"]
            )
            ann_max_text = f"- The **maximum** number of flooding days for this threshold during a single year was **{ann_max_count} days** during {ann_max_years_str}*.\n"

            overall_record_blurb.append(ann_max_text)

    else:
        overall_record_blurb = [
            f"- Water levels for **{station_name}** have *never* exceeded the **{threshold_name}** threshold.\n",
            f"- A table of the highest recorded water levels can be found in the *Extreme water levels* section on this page.",
        ]

    obs_flood_text.append(
        html.Div(
            className="analysis-highlight",
            children=[
                dcc.Markdown(children=overall_record_blurb),
                html.Div(
                    "*Years of January in May–April meteorological years",
                    style={"font-size": 11, "margin-top": "15px"},
                )
                if (obs_flood_analysis["flood_counts"]["overall"] > 0)
                and (ann_max_count >= 3)
                else "",
            ],
        ),
    )

    # if no observed flooding days, no need for remaining analysis
    if obs_flood_analysis["flood_counts"]["overall"] == 0:
        return obs_flood_text

    # --------------------------------------------------------------------
    # long-term change blurb

    if obs_flood_analysis["analyze_long_term"]:

        mslc = obs_flood_analysis["msl_change"]
        units = obs_flood_analysis["units"]
        mslc = np.round(mslc * 3.28084, 2) if units == "ft" else mslc
        units_full = "feet" if units == "ft" else "meters"
        msl_tendency = (
            "**did not change** relative to "
            if mslc == 0
            else f" was **{abs(mslc)} {units_full} {'higher' if mslc > 0 else 'lower'}** than "
        )
        msl_change_text = f"- **Average sea level** in {station_name} during {obs_flood_analysis['period2']} {msl_tendency} {obs_flood_analysis['period1']}\*.\n"

        htfc = obs_flood_analysis["htf_pyr_change"]
        f10_htf = obs_flood_analysis["f10_htf"]
        l10_htf = obs_flood_analysis["l10_htf"]
        htf_tendency = (
            f"**did not change** from {obs_flood_analysis['period1']} to {obs_flood_analysis['period2']}\*{', because no flooding days were observed during either period' if (f10_htf == 0) and (l10_htf == 0) else ''}"
            if htfc == 0
            else f"**{'increased' if htfc > 0 else 'decreased'}** from **{f10_htf} days** during {obs_flood_analysis['period1']} to **{l10_htf} days** during {obs_flood_analysis['period2']}\*"
        )
        htf_change_text = f"- **Flooding days** for the {threshold_name} threshold in {station_name} {htf_tendency}."

        long_term_change_blurb = [
            "##### Long-term change\n",
            f"Sustained sea-level change contributes to changes in the frequency of flooding days over time.\n",
            msl_change_text,
            htf_change_text,
        ]

        if htfc != 0:
            prb = obs_flood_analysis["htf_pyr_diff_prob"]
            lkhd_prb = {
                1: "virtually certain (99–100% chance)",
                10: "very likely (90–100% chance)",
                33: "likely (67–100% chance)",
                67: "about as likely as not (33–67% chance)",
                90: "unlikely (0–33% chance)",
                99: "very unlikely (0–10% chance)",
                100: "exceptionally unlikely (0–1% chance)",
            }
            lkhd_prb = [lkhd_prb[p] for p in lkhd_prb if prb < p][0]

            long_term_change_blurb.append(
                f"\n- It is **{lkhd_prb}**\*\* that the {'increase' if mslc > 0 else 'decrease'} in average sea level contributed to the {'increase' if htfc > 0 else 'decrease'} in flooding days."
            )

        obs_flood_text.extend(
            [
                # dcc.Markdown(
                #     f"Long-term sea-level change contributes to changes in the frequency of flooding days over time."
                # ),
                html.Div(
                    className="analysis-highlight",
                    children=[
                        dcc.Markdown(children=long_term_change_blurb),
                        html.Div(
                            "*Years of January in May–April meteorological years",
                            style={"font-size": 11, "margin-top": "15px"},
                        ),
                        html.Div(
                            children=[
                                "**See ",
                                html.A(
                                    "Box 1.1",
                                    href="https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1/#h3-9-siblings",
                                    target="_blank",
                                ),
                                " in the IPCC AR6 Report for more details about the calibrated language used for likelihood and its relationship to probability. In this case, probabilities were calculated by comparing the observed change in flooding days to differences in flooding days between many random pairs of decades with the difference in average sea level removed.",
                            ],
                            style={"font-size": 11, "margin-top": "5px"},
                        )
                        if htfc != 0
                        else "",
                    ],
                ),
            ]
        )

    # --------------------------------------------------------------------
    # seasonality blurb

    clm = obs_flood_analysis["climatology"]

    if clm.total.sum() < 12:
        mo_most = clm.loc[clm.total > 0].sort_values(
            by=["total", "mo_number"], ascending=[False, True]
        )
    else:

        mo_most = clm.loc[clm.total >= clm.iloc[-3].total].sort_values(
            by=["total", "mo_number"], ascending=False
        )
        mo_most = mo_most.loc[mo_most.total > 1]
    mo_most_text = ""
    for m, d in mo_most.iterrows():
        mo_most_text += text_list_connector(m, mo_most.index)
        if clm.total.sum() >= 25:
            mo_most_text += f"**{m}** ({d['percent']}%"
            mo_most_text += " of observed occurrences" if m == mo_most.index[0] else ""
        else:
            mo_most_text += f"**{m}** ({d['total']} "
            mo_most_text += "day" if d["total"] == 1 else "days"
        mo_most_text += ")"
    mo_most_text = f"- **Flooding days** for the {threshold_name} threshold at {station_name} **occurred {'most frequently' if clm.total.sum() >= 12 else ''}** during {mo_most_text[2:]}.\n"

    seasonality_blurb = [
        "##### By month\n",
        f"Some months experience flooding days more frequently due to seasonality in sea level, tides, and storminess.\n",
        mo_most_text,
    ]

    if clm.total.sum() >= 12:
        clm = clm.sort_values(by="total", ascending=False)
        mo_least = clm.loc[clm.total <= clm.iloc[-3].total].sort_values(
            by=["total", "mo_number"], ascending=True
        )
        mo_least_text = ""
        if mo_least.total.iloc[0] == 0:
            mo_least = mo_least.loc[mo_least.total == 0]
            for m, d in mo_least.iterrows():
                mo_least_text += text_list_connector(m, mo_least.index)
                mo_least_text += f"**{m}**"
            mo_least_text = f"- **Flooding days** for this threshold have ***never* occurred** during {mo_least_text[2:]}.\n"
        else:
            for m, d in mo_least.iterrows():
                mo_least_text += text_list_connector(m, mo_least.index)
                if clm.total.sum() >= 25:
                    mo_least_text += f"**{m}** ({d['percent']}%"
                    mo_least_text += (
                        " of observed occurrences" if m == mo_least.index[0] else ""
                    )
                else:
                    mo_least_text += f"**{m}** ({d['total']} "
                    mo_least_text += "day" if d["total"] == 1 else "days"
                mo_least_text += ")"
            mo_least_text = f"- The **fewest flooding days** for this flooding threshold occured during {mo_least_text[2:]}.\n"
    else:
        mo_least_text = "- **Flooding days** for this threshold have ***never* occurred** during other months."

    seasonality_blurb.append(mo_least_text)

    mo_max_count = obs_flood_analysis["max_counts"]["monthly"]["count"]
    if mo_max_count >= 3:

        mo_max_months_str = format_text_list(
            obs_flood_analysis["max_counts"]["monthly"]["months"]
        )
        mo_max_text = f"- The **maximum** number of flooding days for this threshold during a single month was **{mo_max_count} days** during {mo_max_months_str}.\n"

        seasonality_blurb.append(mo_max_text)

    obs_flood_text.extend(
        [
            # dcc.Markdown(
            #     f"Some months experience flooding days more frequently due to seasonality in sea level, tides, and storminess."
            # ),
            html.Div(
                className="analysis-highlight",
                children=[dcc.Markdown(children=seasonality_blurb),],
            ),
        ]
    )

    # --------------------------------------------------------------------

    return obs_flood_text
