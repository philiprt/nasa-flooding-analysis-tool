import plotly.graph_objects as go
import numpy as np
import pandas as pd
import xarray as xr
import json

import graphs.analysis as anlyz


def slr_projection(slr, scn_focus="int", units="ft"):

    units_long = "feet" if units == "ft" else "meters"
    uf = 3.28084 if units == "ft" else 1.0

    # reorder to trajectory last to plot on top
    slr["names"] = {
        s: slr["names"][s]
        for s in [s for s in slr["names"] if s != "traj"]
        + [s for s in slr["names"] if s == "traj"]
    }

    scn_nm = {
        s: slr["names"][s] + " (current selection)"
        if s == scn_focus
        else slr["names"][s]
        for s in slr["names"]
    }

    yr_max = 2100
    yr_lims = [1970, yr_max]

    # vertical axis limits
    slr_min = min(slr["observations"]["values"]) * uf
    slr_max = slr["scenarios"]["values"]["high"]["50"][-1] * uf
    pad = 0.05 * slr_max
    slr_lims = [slr_min - pad, slr_max + pad]

    col = anlyz.color_palette()
    col = [col[c] for c in [1, 0, 5, 6, 4]] + ["#000"]

    lw = [5 if s == scn_focus else (3 if s == "traj" else 2) for s in scn_nm]

    fig = go.Figure()

    n = [n for n, scn in enumerate(scn_nm) if scn == scn_focus][0]
    fill_color = anlyz.fill_color(col[n], 0.2)
    years_key = "traj" if scn_focus == "traj" else "scenarios"
    fig.add_trace(
        {
            "x": slr["scenarios"]["years"][years_key],
            "y": [
                round(v * uf, 3) for v in slr["scenarios"]["values"][scn_focus]["17"]
            ],
            "type": "scatter",
            "fill": "none",
            "showlegend": False,
            "line": {"color": fill_color, "width": 0},
            "hoverinfo": "none",
        }
    )
    fig.add_trace(
        {
            "x": slr["scenarios"]["years"][years_key],
            "y": [
                round(v * uf, 3) for v in slr["scenarios"]["values"][scn_focus]["83"]
            ],
            "type": "scatter",
            "fill": "tonexty",
            "fillcolor": fill_color,
            "showlegend": False,
            "mode": "none",
            "hoverinfo": "none",
        },
    )
    for n, scn in enumerate(scn_nm):
        years_key = "traj" if scn == "traj" else "scenarios"
        fig.add_trace(
            {
                "x": slr["scenarios"]["years"][years_key],
                "y": [round(v * uf, 3) for v in slr["scenarios"]["values"][scn]["50"]],
                "type": "scatter",
                "name": scn_nm[scn],
                "showlegend": True,
                "line": {
                    "color": col[n],
                    "width": lw[n],
                    "dash": "dot" if scn == "traj" else None,
                },
                # "hoverinfo": "y",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            }
        )

    obs = (
        pd.Series(
            [round(v * uf, 3) for v in slr["observations"]["values"]],
            index=slr["observations"]["years"],
        )
        .interpolate()
        .dropna()
    )
    fig.add_trace(
        {
            "x": obs.index,
            "y": obs.values,
            "type": "scatter",
            "mode": "lines",
            # "name": "Observed",
            "showlegend": False,
            "line": {"color": "#888", "width": 2,},
            "hoverinfo": "none",
            # "hovertemplate": "%{y:.2f}<extra></extra>",
        },
    )
    fig.add_trace(
        go.Scatter(
            {
                "x": slr["observations"]["years"],
                "y": [round(v * uf, 3) for v in slr["observations"]["values"]],
                "mode": "markers",
                "name": "Observed",
                "showlegend": True,
                "marker": {"size": 7, "color": "#888",},
                # "line": {"color": "#888", "width": 3,},
                "hovertemplate": "%{y:.2f}<extra></extra>",
            }
        )
    )

    fig.update_yaxes(
        title_text="Sea-level rise (" + units_long + ")", side="right", range=slr_lims,
    )
    fig.update_xaxes(range=yr_lims)

    fig.update_layout(
        template="none",
        margin=dict(l=60, r=10, b=42, t=25, pad=0),
        font=dict(size=14),
        xaxis=dict(layer="below traces",),
        yaxis=dict(layer="below traces", side="left",),
        hovermode="x",
        #     hoverlabel_align="left",
        legend=dict(
            x=0.02, y=1, traceorder="reversed", itemclick=False, itemdoubleclick=False,
        ),
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

    return fig


def slr_budget(slr, year_focus=2100, scn_focus="int", units="ft", single_scn=True):

    year_focus = 2050 if (year_focus > 2050) & (scn_focus == "traj") else year_focus

    units_long = "feet" if units == "ft" else "meters"
    uf = uf = 3.28084 if units == "ft" else 1.0

    scenarios = slr["names"]
    if single_scn:
        scenarios = [s for s in scenarios if s == scn_focus]

    col = [
        "#D55E00",
        "#ADE1FF",
        "#56B4E9",
        "#0072B2",
        "#F0E442",
        "#009E73",
        "#CC79A7",
        "#685044",
        "#E69F00",
    ]

    fig = go.Figure()

    xc = [slr["names"][s] for s in scenarios]  # xaxis labels

    # highlight selected scenario if showing mulitple scenarios in budget graph
    if not single_scn:
        if scn_focus in scenarios:
            for n, s in enumerate(scenarios):
                if s != scn_focus:
                    fig.add_vrect(
                        x0=n - 0.5,
                        x1=n + 0.5,
                        line_width=0,
                        fillcolor="gray",
                        opacity=0.06,
                        layer="below",
                    )
    else:
        if scn_focus == "traj":
            fig.add_annotation(
                text=f"Unavailable",
                font=dict(size=18),
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )

    for n, c in enumerate(slr["contributions"][str(year_focus)]):
        if c != "Total":
            fig.add_trace(
                go.Bar(
                    x=xc,
                    y=[
                        round(v * uf, 3)
                        for v in [
                            slr["contributions"][str(year_focus)][c][k]
                            for k, s in enumerate(slr["names"])
                            if s in scenarios and s != "traj"
                        ]
                    ],
                    name=c,
                    marker=dict(color=col[n], opacity=0.9),
                    width=0.5,
                    hovertemplate="%{y:.2f}<extra></extra>",
                )
            )
        # else:
        #     fig.add_trace(
        #         go.Scatter(
        #             x=xc,
        #             y=[
        #                 round(v * uf, 3)
        #                 for v in slr["contributions"][str(year_focus)][c]
        #             ],
        #             name=c,
        #             mode="markers",
        #             marker=dict(color="black", size=13),
        #             hovertemplate="%{y:.2f}<extra></extra>",
        #         )

        #     )

    # fig.add_annotation(
    #     text=f"<b>{year_focus}</b>",
    #     font=dict(size=32),
    #     xref="paper",
    #     yref="paper",
    #     x=0.05,
    #     y=0.94,
    #     showarrow=False,
    # )

    fig.update_xaxes(title_text=f"ITF Scenario", titlefont=dict(size=14))
    fig.update_yaxes(title_text=f"Sea-level rise ({units_long})",)
    fig.update_layout(
        template="none",
        margin=dict(l=60, r=10, b=45, t=25, pad=7),
        font=dict(size=14),
        barmode="relative",
        hovermode="x",
        hoverlabel=dict(font=dict(size=14),),
        legend=dict(traceorder="reversed", itemclick=False, itemdoubleclick=False,),
        modebar=dict(
            remove=["toImage", "lasso", "select", "zoomIn", "zoomOut"],
            orientation="h",
            color="#333333",
            bgcolor=None,
        ),
    )

    return fig


def slr_scenario_table(scn_focus="int"):
    sat_tbl = {
        "Global Mean Surface Air Temperature": [
            "1.5ºC",
            "2.0ºC",
            "3.0ºC",
            "4.0ºC",
            "5.0ºC",
        ],
        "Closest IPCC Emissions Scenario(s)": [
            "Low (SSP1-2.6)",
            "Low to Intermediate (SSP1-2.6 to SSP2-4.5)",
            "Intermediate",
        ],
    }
