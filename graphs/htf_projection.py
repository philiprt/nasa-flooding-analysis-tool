import numpy as np
import pandas as pd
import plotly.graph_objects as go
import graphs.analysis as anlyz
import os
import json

from dash import dcc, html
import dash_bootstrap_components as dbc


def load_projection_data(station, scenario, threshold):

    filename = f"./data/ensemble_calcs/{station['id']}/{scenario}/{threshold}.json"

    if not os.path.exists(filename):
        return None, None, None, None

    with open(filename, "r") as f:
        analysis = json.load(f)

    meta = {
        **station,
        **{"threshold": threshold, "scenario": scenario, "steps": analysis["yoi"]},
    }

    p = analysis["annual_percentiles"]
    prjn = pd.DataFrame(p["percentiles"], index=p["years"])
    prjn.columns = [int(c) for c in prjn.columns]

    clim = analysis["monthly_percentiles"]

    pent_quantities = {
        "pent_avg": "pentad_mean_month_percentiles",
        "pent_mxssn": "pentad_max_season_percentiles",
        "pent_mxmo": "pentad_max_month_percentiles",
    }
    pent = dict()
    for q in pent_quantities:
        p = analysis[pent_quantities[q]]
        pent[q] = pd.DataFrame(p["percentiles"], index=p["pentads"])
        pent[q].columns = [int(c) for c in pent[q].columns]

    prob = dict(
        annual=dict(
            at_least=pd.DataFrame(
                analysis["annual_probabilities"]["prob_at_least_n"],
                index=analysis["annual_probabilities"]["years"],
            ),
            first_yr=pd.DataFrame(
                analysis["annual_probabilities"]["prob_first_year"],
                index=analysis["annual_probabilities"]["years"],
            ),
        ),
        amonthly=dict(
            at_least=pd.DataFrame(
                analysis["monthly_probabilities"]["prob_at_least_n"],
                index=analysis["monthly_probabilities"]["years"],
            ),
            first_yr=pd.DataFrame(
                analysis["monthly_probabilities"]["prob_first_year"],
                index=analysis["monthly_probabilities"]["years"],
            ),
        ),
    )

    return meta, prjn, clim, pent, prob


def htf_projection(meta, prjn, yoi_toggle):

    if prjn is None:
        fig = go.Figure()
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        fig.update_layout(template="none")
        fig.add_annotation(
            {
                "x": 0.5,
                "y": 0.5,
                "text": "No projection for this flooding threshold",
                "xref": "paper",
                "yref": "paper",
                "xanchor": "center",
                "yanchor": "middle",
                # "bgcolor": "white",
                # "borderpad": 2,
                "showarrow": False,
            }
        )
        return fig, None

    yr_max = (
        int(np.round((meta["steps"][-1] + 3) / 5) * 5)
        if meta["steps"] is not None
        else prjn.loc[prjn[50] <= 330].index.values[-1]
    )
    yr_max = yr_max if yr_max <= prjn.index[-1] else prjn.index[-1]
    yr_lims = [2020, yr_max]

    # vertical axis limits
    xd_max = min([prjn.loc[yr_max, 90] * 1.1, 370])
    xd_min = -xd_max * 0.25 / 13  # match height of zero line in climatology figure
    xd_lims = [xd_min, xd_max]

    col = anlyz.color_palette()
    fig = go.Figure()

    leg = True
    traces = projection_traces(prjn, meta, col, leg, yoi_toggle)
    for trc in traces:
        fig.add_trace(trc)

    # annotations = projection_annotations(prjn, meta)

    fig.update_yaxes(title_text="Flooding days per year", side="right", range=xd_lims)
    fig.update_xaxes(range=yr_lims)

    fig.update_layout(
        # width=800,
        # height=525,
        template="none",
        margin=dict(l=60, r=10, b=42, t=30, pad=0),
        font=dict(size=14),
        xaxis=dict(layer="below traces",),
        yaxis=dict(layer="below traces", side="left",),
        hovermode="x",
        #     hoverlabel_align="left",
        legend=dict(
            x=0.02, y=1, traceorder="reversed", itemclick=False, itemdoubleclick=False,
        ),
        legend_tracegroupgap=100,
        # title=dict(
        #     text="Projected High-Tide-Flooding Days",
        #     x=0.035,
        #     y=0.97,
        #     font=dict(size=24),
        # ),
        # annotations=annotations,
        modebar=dict(
            remove=["toImage", "lasso", "select", "zoomIn", "zoomOut"],
            orientation="h",
            color="#333333",
            bgcolor=None,
        ),
    )

    return fig, yr_lims


def projection_traces(prjn, meta, col, leg, yoi_toggle):

    col = [col[n] for n in [1, 5, 4]]
    fcol = [anlyz.fill_color(c, 0.6) for c in col if c[0] == "#"]
    fcol2 = [anlyz.fill_color(c, 0.25) for c in col if c[0] == "#"]

    prjn_traces = [
        {
            "x": prjn.index.values,
            "y": prjn[83].values,
            "type": "scatter",
            "fill": "none",
            "showlegend": False,
            "line": {"color": fcol2[0], "width": 0},
            "hoverinfo": "none",
        },
        {
            "x": prjn.index.values,
            "y": prjn[95].values,
            "type": "scatter",
            "fill": "tonexty",
            "fillcolor": fcol2[0],
            "name": "<i>Very likely</i> range (> 90% probability)",
            "showlegend": True if leg else False,
            "legendgroup": "2",
            "mode": "none",
            "hoverinfo": "y",
        },
        {
            "x": prjn.index.values,
            "y": prjn[5].values,
            "type": "scatter",
            "fill": "none",
            "showlegend": False,
            "line": {"color": fcol2[0], "width": 0},
            "hoverinfo": "y",
        },
        {
            "x": prjn.index.values,
            "y": prjn[17].values,
            "type": "scatter",
            "fill": "tonexty",
            "fillcolor": fcol2[0],
            "showlegend": False,
            "mode": "none",
            "hoverinfo": "none",
        },
        {
            "x": prjn.index.values,
            "y": prjn[17].values,
            "type": "scatter",
            "fill": "none",
            "showlegend": False,
            "line": {"color": fcol[0], "width": 0},
            "hoverinfo": "y",
        },
        {
            "x": prjn.index.values,
            "y": prjn[83].values,
            "type": "scatter",
            "fill": "tonexty",
            "fillcolor": fcol[0],
            "name": "<i>Likely</i> range (> 66% probability)",
            "showlegend": True if leg else False,
            "legendgroup": "1",
            "mode": "none",
            "hoverinfo": "y",
        },
        {
            "x": prjn.index.values,
            "y": prjn[50].values,
            "type": "scatter",
            "name": "50th percentile" if leg else None,
            "showlegend": True if leg else False,
            "legendgroup": "0",
            "line": {"color": "#0072B2", "width": 3},
            "hoverinfo": "y",
        },
        # {
        #     "x": prjn.index.values,
        #     "y": prjn[90].values,
        #     "type": "scatter",
        #     "name": "90th percentile" if leg else None,
        #     "showlegend": True if leg else False,
        #     "line": {"color": col[1], "width": 3},
        #     "hoverinfo": "y",
        # },
    ]

    if meta["steps"] is not None and yoi_toggle:

        annotation_traces = []
        yrs = [y for y in meta["steps"]]
        cmmn = {
            "type": "scatter",
            "mode": "lines",
            "showlegend": False,
            "hoverinfo": "none",
        }

        for n, stp in enumerate(zip(meta["steps"][:-1], meta["steps"][1:])):
            lower = n < (len(meta["steps"]) - 2)
            dash = "dot" if lower else "solid"
            # dash = "solid"
            p12 = [stp[1], stp[0]] if lower else stp
            lcol = col[2] if lower else col[1]
            lcol = "black"

            annotation_traces.append(
                {
                    **{
                        "x": [stp[0], p12[0]],
                        "y": prjn[50].loc[[stp[0], p12[1]]],
                        "line": dict(color=lcol, width=1.5, dash=dash),
                    },
                    **cmmn,
                }
            )
            annotation_traces.append(
                {
                    **{
                        "x": [p12[0], stp[1]],
                        "y": prjn[50].loc[[p12[1], stp[1]]],
                        "line": dict(color=lcol, width=1.5, dash=dash),
                    },
                    **cmmn,
                }
            )

        annotation_traces.append(
            {
                **cmmn,
                **{
                    "x": [yrs[0]],
                    "y": [prjn[50].loc[yrs[0]]],
                    "type": "scatter",
                    "mode": "markers",
                    "showlegend": False,
                    "hoverinfo": "none",
                    "marker": dict(size=10, symbol="circle", line=dict(width=0)),
                    "line": dict(color="black"),
                },
            }
        )

        annotation_traces.append(
            {
                **cmmn,
                **{
                    "x": [yrs[2]],
                    "y": [prjn[50].loc[yrs[2]]],
                    "type": "scatter",
                    "mode": "markers",
                    "showlegend": False,
                    "hoverinfo": "none",
                    "marker": dict(size=10, symbol="circle", line=dict(width=0)),
                    "line": dict(color="black"),
                },
            }
        )

        annotation_traces.append(
            {
                **cmmn,
                **{
                    "x": [yrs[1]],
                    "y": [prjn[50].loc[yrs[1]]],
                    "type": "scatter",
                    "mode": "markers",
                    "name": f"Year of inflection ({yrs[1]})" if leg else None,
                    "showlegend": True if leg else False,
                    "legendgroup": "3",
                    "hoverinfo": "none",
                    "marker": dict(
                        size=12, symbol="circle", line=dict(width=2, color="black")
                    ),
                    "line": dict(color="white"),
                },
            }
        )

        prjn_traces.extend(annotation_traces)

    return prjn_traces


def projection_annotations(prjn, meta):

    x = 2020

    dy = 0.05
    y = 1 + dy

    cmmn = {
        "x": x,
        "xref": "x1",
        "yref": "paper",
        "xanchor": "left",
        "yanchor": "top",
        "bgcolor": "white",
        "borderpad": 2,
        "showarrow": False,
    }
    annotations = [
        {
            **{
                "y": y - 0.055,
                "text": "Threshold: NOAA " + meta["threshold"].capitalize(),
            },
            **cmmn,
        },
        {
            **{
                "y": y,
                "text": "<b>" + meta["name"] + "<b>",  # ,
                "font": dict(size=16),
            },
            **cmmn,
        },
    ]

    if meta["steps"] is not None:

        for n, stp in enumerate(zip(meta["steps"][:-1], meta["steps"][1:])):

            dlt = prjn[50].loc[stp[1]] - prjn[50].loc[stp[0]]
            day_or_days = " day/year" if dlt == 1 else " days/year"
            inc_str = "Δ = " + str(int(dlt)) + day_or_days

            if prjn[50].loc[stp[1]] <= 1:
                step_str = str(stp[0]) + " → " + str(stp[1]) + ": " + "Few events"
            else:
                step_str = str(stp[0]) + " → " + str(stp[1]) + ": " + inc_str
            annotations.append(
                {**{"y": y - 0.01 - (n + 2) * 0.045, "text": step_str}, **cmmn,},
            )

    scenario_strings = {
        "int_low": "NOAA Intermediate Low",
        "int": "NOAA Intermediate",
        "int_high": "NOAA Intermediate High",
        "kopp": "Kopp et al. (2014)",
    }
    annotations.append(
        {
            **cmmn,
            **{
                "y": y + 0.105,
                "text": scenario_strings[meta["scenario"]] + " SLR Scenario",
                "font": dict(size=14),
                "bgcolor": None,
            },
        },
    )

    return annotations


def htf_analysis_text(meta, prob, prjn, pent):

    htf_text = dict()

    # --------------------------------------------------------------------
    # chronic flooding analysis

    chronic_intro = [
        "Sea-level rise will cause routine and chronic flooding at increasing numbers of locations and increasingly higher thresholds."
    ]

    likelihoods = {
        "likely": 66,
        "very likely": 90,
    }

    lkhd = "likely"

    # prob["annual"]["first_yr"] = prob["annual"]["first_yr"].loc[2021:]
    # cprb = prob["annual"]["first_yr"].cumsum()

    pal20 = prob["annual"]["at_least"]["20"]
    if pal20.iloc[0] >= likelihoods[lkhd] / 100:
        rtn_text_end = f"is currently ***{lkhd}***\* on an annual basis"
    elif pal20.iloc[-1] < likelihoods[lkhd] / 100:
        rtn_text_end = f"does not become ***{lkhd}***\* on an annual basis by 2100"
    else:
        rtn_ab = (pal20 >= likelihoods[lkhd] / 100).idxmax()
        # rtn_sy = (cprb["20"] >= 0.25).idxmax()
        # rtn_sy_prb = 100 * cprb["20"].loc[rtn_sy]
        rtn_text_end = (
            f"becomes ***{lkhd}***\* on an annual basis beginning in **{rtn_ab}**"
        )

    pal50 = prob["annual"]["at_least"]["50"]
    if pal50.iloc[0] >= likelihoods[lkhd] / 100:
        cnc_text_end = f"is currently ***{lkhd}***\* on an annual basis"
    elif pal50.iloc[-1] < likelihoods[lkhd] / 100:
        cnc_text_end = f"does not become ***{lkhd}***\* on an annual basis by 2100"
    else:
        cnc_ab = (pal50 >= likelihoods[lkhd] / 100).idxmax()
        cnc_text_end = (
            f"becomes ***{lkhd}***\* on an annual basis beginning in **{cnc_ab}**"
        )

    # prob["annual"]["first_yr"] = prob["annual"]["first_yr"].loc[2021:]

    prb_none = (1 - prob["annual"]["at_least"]).cumprod()
    prb_atleast1 = 1 - prb_none
    cprb = prb_atleast1.loc[
        range(2030, prb_atleast1.index[-1] + 1, 10), ["10", "20", "50", "100"]
    ]
    cprb = cprb.where(cprb >= 0.25).dropna(axis=0, how="all").iloc[:2, :]
    yr_and_cnt = (cprb >= 0.25).iloc[:, ::-1].idxmax(axis=1).drop_duplicates()

    rtn_text = [
        "For the selected threshold and scenario:",
        f"- **Routine flooding** (at least 20 days per year) {rtn_text_end}.",
        f"- **Chronic flooding** (at least 50 days per year) {cnc_text_end}.",
    ]
    rtn_text.extend(
        [
            f"- There is a **{f'{100 * cprb.loc[y, c]:0.0f}' if cprb.loc[y, c] <= 0.99 else '>99'}% chance** of at least **{c} flooding days** during a single year **by {y}**."
            for y, c in yr_and_cnt.iteritems()
        ]
        if len(yr_and_cnt) > 0
        else [
            "- < 25% chance that a single year will experience at least 10 flooding days by 2100."
        ]
    )

    # rtn_text = [
    #     "**Routine flooding** (at least 20 days per year) ...",
    #     f"- Is ***likely***\* to occur on an **annual basis** beginning in **{rtn_ab}**.",
    #     f"- Has a **{rtn_sy_prb: 0.0f}% chance** of occurring during a **single year** by **{rtn_sy}**.",
    # ]

    # cnc_text = [
    #     "**Chronic flooding** (at least 50 days per year) ...",
    #     f"- Is ***likely***\* to occur on an **annual basis** beginning in **{cnc_ab}**.",
    #     f"- Has a **{cnc_sy_prb: 0.0f}% chance** of occurring during a **single year** by **{cnc_sy}**.",
    # ]

    htf_text["chronic"] = [
        html.Div(
            children=[
                dcc.Markdown(children=chronic_intro, style={"margin-bottom": "1em"},),
                dcc.Markdown(children=rtn_text, style={"margin-bottom": "1em"},),
                # dcc.Markdown(children=cnc_text),
                html.Div(
                    children=[
                        # "*",
                        # html.I(lrng.capitalize()),
                        f"*Indicates >66% chance. See ",
                        html.A(
                            "Box 1.1",
                            href="https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1/#h3-9-siblings",
                            target="_blank",
                        ),
                        " in the IPCC AR6 Report for more details about the calibrated language used for likelihood and its relationship to probability. In this case, probabilities were calculated over an ensemble of future possibilities from the ",
                        dcc.Link(
                            "probabilistic projections",
                            href="/about/flooding-projections",
                        ),
                        ".",
                    ],
                    style={"font-size": 11, "margin-top": "10px"},
                ),
            ],
            style={"margin-top": "1em"},
        ),
    ]

    # --------------------------------------------------------------------
    # YOI analysis

    sxd = meta["steps_xd"]

    def change_text(c1, c2):
        dpct = None if c1 == 0 and c2 != 0 else 100 * (c2 - c1) / c1
        if c2 - c1 == 0:
            ctxt = "is **not expected to change**."
        elif dpct is None:
            ctxt = f"is expected to {'increase' if c2 > 0 else 'decrease'} from {c1} days to {c2} days per year on average."
        else:
            txt_end = f"from {c1} days to {c2} days per year on average"
            if dpct < 0:
                ctxt = f"is expected to **decrease by {-dpct: 0.0f}%** {txt_end}."
            else:
                if dpct < 100:
                    ctxt = f"is expected to **increase by {dpct: 0.0f}%** {txt_end}."
                else:
                    if dpct < 175:
                        mtxt = "double" if dpct == 100 else "more than double"
                    elif dpct < 275:
                        mtxt = (
                            "triple"
                            if dpct == 200
                            else ("more than triple" if dpct > 200 else "almost triple")
                        )
                    elif dpct < 375:
                        mtxt = (
                            "quadruple"
                            if dpct == 300
                            else (
                                "more than quadruple"
                                if dpct > 300
                                else "almost quadruple"
                            )
                        )
                    else:
                        fctr = np.floor(dpct / 100)
                        frem = dpct % 100
                        mtxt = (
                            f"increase by a factor of {fctr: 0.0f}"
                            if frem == 0
                            else (
                                f"increase by more than a factor of {fctr: 0.0f}"
                                if frem <= 75
                                else f"increase by almost a factor of {fctr+1: 0.0f}"
                            )
                        )
                    ctxt = f"is expected to **{mtxt}** {txt_end}."
        return ctxt

    if meta["steps"] is None:
        yoi_bullets = [
            "- A YOI was not calculated for the selected location, threshold, and scenario.",
        ]
    else:
        yoi_bullets = [
            "For the selected location, threshold, and scenario:",
            f"- The YOI is **{meta['steps'][1]}**.",
            f"- During the decade **prior to the YOI**, the frequency of flooding {change_text(sxd[0], sxd[1])}",
            f"- During the decade **following the YOI**, the frequency of flooding {change_text(sxd[1], sxd[2])}",
        ]

    htf_text["yoi"] = [
        html.P(
            style={"margin-bottom": "1em"},
            children=[
                "The ",
                html.A(
                    "interaction",
                    href="https://www.jpl.nasa.gov/news/study-projects-a-surge-in-coastal-flooding-starting-in-2030s",
                    target="_blank",
                ),
                " between sea-level rise and natural fluctuations in the height of high tides can lead to abrupt increases in the frequency of flooding. Where applicable, the ",
                html.A(
                    "year of inflection (YOI)",
                    href="https://www.nature.com/articles/s41558-021-01077-8",
                    target="_blank",
                ),
                " marks the onset of a period of rapid change preceded by a period of relatively slower change. The inflection may be more or less pronounced depending on location, threshold, and scenario.",
            ],
        ),
        dcc.Markdown(children=yoi_bullets),
    ]

    # --------------------------------------------------------------------
    # extreme months text

    likelihood_ranges = {
        "likely": (17, 83),
        "very likely": (5, 95),
    }

    lrng = "likely"
    l1, l2 = likelihood_ranges[lrng]

    xtrm_months_intro = [
        "As the frequency of flooding increases, **extreme months will become more severe**. For the selected scenario and threshold, the *Extreme Months* graph above shows:",
    ]
    xtrm_months_blurb = []

    def get_pent_strings(p):

        p_str = f"{p}–{p+4}"

        p_avg_hi = pent["pent_avg"].loc[p, l2]
        p_avg = f"{pent['pent_avg'].loc[p, l1]}–{p_avg_hi}"

        p_mxmo_hi = pent["pent_mxmo"].loc[p, l2]
        p_mxmo = f"{pent['pent_mxmo'].loc[p, l1]}–{p_mxmo_hi}"

        p_blurb = [
            "\n",
            f"- **{p_str}** is ***{lrng}***\* to experience ...",
            f"  - {p_avg if p_avg_hi > 1 else ('1 or fewer' if p_avg_hi == 1 else 0)} flooding days per month on average.\n"
            f"  - **{p_mxmo if p_mxmo_hi > 1 else ('1 or fewer' if p_mxmo_hi == 1 else 0)} flooding days** during the **most extreme** month.",
        ]
        return p_blurb, p_mxmo_hi

    # p1_blurb, _ = get_pent_strings(2030)
    p1_blurb = None
    # p2_blurb, p2_hi = get_pent_strings(2050)
    p2_hi = 0
    p3_blurb, p3_hi = get_pent_strings(2095 if meta["scenario"] != "traj" else 2050)

    # if p2_mxmo_hi <= 2:
    #     p2_mxmo

    if p3_hi < 5:
        p1_blurb = [
            f"- Months experiencing 5 or more flooding days do not become ***{lrng}***\* prior to 2100."
        ]
        p2_blurb = []
    elif (p2_hi < 5) and (p3_hi >= 5):
        # p1_blurb = [
        #     f"- Months experiencing 5 or more flooding days become *{lrng}*\* after 2050."
        # ]
        y = pent["pent_mxmo"].loc[pent["pent_mxmo"][l2] >= 10].index
        if len(y) > 0:
            p2_blurb, p2_hi = get_pent_strings(y[0])
        else:
            p2_blurb = p3_blurb

    if p1_blurb is not None:
        xtrm_months_blurb.extend(p1_blurb)
    xtrm_months_blurb.extend(p2_blurb)

    first_mo_intro = [
        # "\nExtreme months correspond to frequent flooding during brief periods **before** frequent flooding is expected on average. For the selected scenario and threshold, there is a ..."
        "\nFor the selected scenario and threshold, there is a ..."
    ]

    prb_none = (1 - prob["amonthly"]["at_least"]).cumprod()
    prb_atleast1 = 1 - prb_none
    cprb = prb_atleast1.loc[range(2030, prb_atleast1.index[-1] + 1, 10)]
    cprb = cprb.where(cprb >= 0.25).dropna(axis=0, how="all").iloc[:2, :]
    yr_and_cnt = (cprb >= 0.25).iloc[:, ::-1].idxmax(axis=1).drop_duplicates()

    first_mo_blurb = (
        [
            f"- **{f'{100 * cprb.loc[y, c]:0.0f}' if cprb.loc[y, c] <= 0.99 else '>99'}% chance** of at least **{c} flooding days** during a single month **by {y}**."
            for y, c in yr_and_cnt.iteritems()
        ]
        if len(yr_and_cnt) > 0
        else [
            "- < 25% chance that a single month will experience at least 10 flooding days by 2100."
        ]
    )

    xtrm_text = []
    xtrm_text.extend(
        [
            html.Div(
                # className="analysis-highlight",
                children=[
                    dcc.Markdown(children=xtrm_months_intro),
                    dcc.Markdown(
                        children=xtrm_months_blurb, style={"margin-top": "-1em",}
                    ),
                    dcc.Markdown(children=first_mo_intro),
                    dcc.Markdown(
                        children=first_mo_blurb, style={"margin-top": "-1em",}
                    ),
                    html.Div(
                        children=[
                            # "*",
                            # html.I(lrng.capitalize()),
                            f"*Indicates >{np.diff(likelihood_ranges[lrng])[0]}",
                            "% chance that the number is in the given range for the selected scenario and threshold. See ",
                            html.A(
                                "Box 1.1",
                                href="https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-1/#h3-9-siblings",
                                target="_blank",
                            ),
                            " in the IPCC AR6 Report for more details about the calibrated language used for likelihood and its relationship to probability. In this case, probabilities were calculated over an ensemble of future possibilities from the ",
                            dcc.Link(
                                "probabilistic projections",
                                href="/about/flooding-projections",
                            ),
                            ".",
                        ],
                        style={"font-size": 11, "margin-top": "10px"},
                    ),
                ],
                style={"margin-top": "1em"},
            ),
        ]
    )

    # --------------------------------------------------------------------

    return htf_text, xtrm_text
