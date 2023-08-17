import plotly.graph_objects as go
import graphs.analysis as anlyz


def clim_projection(clim, year):

    if clim is None or clim == "no projection" or str(year) not in clim:
        fig = go.Figure()
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        fig.update_layout(template="none")
        return fig

    clim = clim[str(year)]

    col = anlyz.color_palette()
    col = [col[n] for n in [1, 5]]

    fig = go.Figure()

    # mo_labels = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    mo_labels = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    leg = False
    traces = projection_traces(clim, year, col, leg)
    # annotations, shapes = projection_annotations(
    #     prjn, stn_meta[n], r, vspace, sph, col
    # )
    for trc in traces:
        fig.add_trace(trc)
    # for ann in annotations:
    #     fig.add_annotation(ann)
    # for shp in shapes:
    #     fig.add_shape(shp)

    fig.update_xaxes(
        title_text="Flooding days per month",
        range=[-2, 32],  # max(clim["90"]) + 2],
        titlefont=dict(size=15),
    )
    fig.update_yaxes(
        range=[-0.25, 13.0],
        tickmode="array",
        tickvals=[m for m in range(1, 13)],
        ticktext=mo_labels,
        side="right",
    )

    fig.update_layout(
        template="none",
        margin=dict(l=10, r=30, b=41, t=30, pad=0),
        font=dict(size=14),
        yaxis=dict(layer="below traces",),
        xaxis=dict(layer="below traces", zeroline=False,),
        hovermode="y",
        # legend=False,
        # legend=dict(
        #     orientation="h",
        #     x=0.03,
        #     y=0.95,
        #     itemclick=False,
        #     itemdoubleclick=False,
        # ),
        # title=dict(
        #     text="Projected HTF Annual Cycles",
        #     x=0.07,
        #     y=0.975,
        #     font=dict(size=24),
        # ),
    )

    return fig


def projection_traces(clim, year, col, leg):

    fcol = [anlyz.fill_color(c, 0.6) for c in col if c[0] == "#"]
    fcol2 = [anlyz.fill_color(c, 0.25) for c in col if c[0] == "#"]
    n = 0

    mo = [m for m in range(1, 13)]

    bar_height = 0.35

    prjn_traces = []
    for m, xd5, xd17, xd50, xd83, xd95 in zip(
        mo, clim["5"], clim["17"], clim["50"], clim["83"], clim["95"]
    ):
        prjn_traces.extend(
            [
                {
                    "y": [m - bar_height, m + bar_height],
                    "x": [xd5, xd5],
                    "type": "scatter",
                    "mode": "lines",
                    "fill": "none",
                    "showlegend": False,
                    "line": {"color": fcol2[0], "width": 0},
                    "hoverinfo": "none",
                },
                {
                    "y": [m - bar_height, m + bar_height],
                    "x": [xd17, xd17],
                    "type": "scatter",
                    "mode": "lines",
                    "fill": "tonextx",
                    "showlegend": False,
                    "line": {"color": fcol2[0], "width": 0},
                    "fillcolor": fcol2[0],
                    "hoverinfo": "none",
                },
                {
                    "y": [m - bar_height, m + bar_height],
                    "x": [xd17, xd17],
                    "type": "scatter",
                    "mode": "lines",
                    "fill": "none",
                    "showlegend": False,
                    "line": {"color": fcol[0], "width": 0},
                    "hoverinfo": "none",
                },
                {
                    "y": [m - bar_height, m + bar_height],
                    "x": [xd83, xd83],
                    "type": "scatter",
                    "mode": "lines",
                    "fill": "tonextx",
                    "showlegend": False,
                    "line": {"color": fcol[0], "width": 0},
                    "fillcolor": fcol[0],
                    "hoverinfo": "none",
                },
                {
                    "y": [m - bar_height, m + bar_height],
                    "x": [xd83, xd83],
                    "type": "scatter",
                    "mode": "lines",
                    "fill": "none",
                    "showlegend": False,
                    "line": {"color": fcol2[0], "width": 0},
                    "hoverinfo": "none",
                },
                {
                    "y": [m - bar_height, m + bar_height],
                    "x": [xd95, xd95],
                    "type": "scatter",
                    "mode": "lines",
                    "fill": "tonextx",
                    "showlegend": False,
                    "line": {"color": fcol2[0], "width": 0},
                    "fillcolor": fcol2[0],
                    "hoverinfo": "none",
                },
                {
                    "y": [m - bar_height, m + bar_height],
                    "x": [xd50, xd50],
                    "type": "scatter",
                    "mode": "lines",
                    "fill": "none",
                    "showlegend": False,
                    "line": {"color": "#0072B2", "width": 3},
                    "hoverinfo": "none",
                },
            ]
        )

    prjn_traces.extend(
        [
            {
                "y": [m - 0.7 * bar_height for m in mo],
                "x": clim["5"],
                "type": "scatter",
                "mode": "lines",
                "fill": "none",
                "showlegend": False,
                "line": {"color": fcol2[0], "width": 0},
                "hoverinfo": "x",
            },
            {
                "y": [m - 0.35 * bar_height for m in mo],
                "x": clim["17"],
                "type": "scatter",
                "mode": "lines",
                "fill": "none",
                "showlegend": False,
                "line": {"color": fcol[0], "width": 0},
                "hoverinfo": "x",
            },
            {
                "y": mo,
                "x": clim["50"],
                "type": "scatter",
                "mode": "lines",
                "fill": "none",
                "name": str(year) if leg else None,
                "showlegend": False,
                "line": {"color": "#0072B2", "width": 0},
                "hoverinfo": "x",
            },
            {
                "y": [m + 0.35 * bar_height for m in mo],
                "x": clim["83"],
                "type": "scatter",
                "mode": "lines",
                "fill": "none",
                "showlegend": False,
                "line": {"color": fcol[0], "width": 0},
                "hoverinfo": "x",
            },
            {
                "y": [m + 0.7 * bar_height for m in mo],
                "x": clim["95"],
                "type": "scatter",
                "mode": "lines",
                "fill": "none",
                "showlegend": False,
                "line": {"color": fcol2[0], "width": 0},
                "hoverinfo": "x",
            },
        ]
    )

    return prjn_traces


def projection_annotations(prjn, meta, r, vspace, sph, col):

    x = 1.0

    dy = 0.032
    y = 1 - (r - 1) * (vspace + sph)

    cmmn = {
        "x": x,
        "xref": "paper",
        "yref": "paper",
        "xanchor": "left",
        "yanchor": "top",
        "borderpad": 5,
        "showarrow": False,
    }
    annotations = [
        {
            **{
                "y": y - dy,
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
    for n, yr in enumerate(meta["steps"][1:]):
        txt = str(yr)
        if n == 0:
            txt += " (YOI)"
        annotations.append(
            {**cmmn, **{"x": x + 0.125, "y": y - (n + 2) * dy, "text": txt,},}
        )

    if r == 1:
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
                    "x": -0.07,
                    "y": 1.065,
                    "text": scenario_strings[meta["scenario"]] + " SLR Scenario",
                    "font": dict(size=14),
                    "bgcolor": None,
                },
            },
        )

    cmmn = {
        "xref": "paper",
        "yref": "paper",
        "type": "line",
        "x0": 1.02,
        "x1": 1.12,
    }
    shapes = []
    for n, yr in enumerate(meta["steps"][1:]):
        yshp = y - (n + 2) * dy - 0.02
        shapes.append(
            {**cmmn, **{"y0": yshp, "y1": yshp, "line": dict(color=col[n], width=3),},}
        )

    return annotations, shapes
