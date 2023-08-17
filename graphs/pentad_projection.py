import plotly.graph_objects as go
import plotly.subplots as psb
import graphs.analysis as anlyz


def pentad_projection(meta, pent, yr_lims):

    yr_lims[1] = max([2055, yr_lims[1]])

    if pent is None:
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
        return fig

    colors = anlyz.color_palette()
    colors = [colors[n] for n in [1, 6, 5]]

    fig = go.Figure()

    annotations = []
    shapes = []
    # for yr in pent["pent_avg"].index:

    avg = pent["pent_avg"]
    mxsn = pent["pent_mxssn"]
    mxmo = pent["pent_mxmo"]

    # shade alternating 5 year periods
    shapes.extend([pentad_shading(y5) for y5 in avg.index[avg.index % 10 == 5]])

    # add data traces
    showlegend = True
    trace_inputs = [
        dict(q=avg, dx=2, c=colors[0], leg=showlegend, nm="5-year average"),
        # dict(
        #     q=mxsn,
        #     dx=2.5,
        #     c=colors[1],
        #     leg=showlegend,
        #     nm="5-year peak season (3-month period)",
        # ),
        dict(q=mxmo, dx=3, c=colors[2], leg=showlegend, nm="5-year extreme month",),
    ]
    traces = [pentad_trace(trc) for trc in trace_inputs]
    for trc in traces:
        fig.add_trace(trc)

    # create annotations for station and threshold in each subplot
    # annotations.extend(pentad_annotations(stn_meta[n], r, c, vspace))

    # determine optimal legend location
    last_yr = [y for y in avg.index if y < yr_lims[1]][-1]
    leg_lower_right = True if avg.loc[last_yr, 50] > 15 else False

    yaxis_format = dict(
        layer="below traces", range=[-1, 32], zeroline=True, side="left"
    )
    fig.update_yaxes(patch=yaxis_format, title_text="Flooding days per month")
    fig.update_xaxes(
        range=yr_lims,
        tickvals=[2012.5 + 5 * v for v in range(18)],
        ticktext=[
            #                 str(2030 + 5 * v) + "–" + str((5 * v + 4) % 10)
            "'" + str(10 + 5 * v) + "–'" + str(10 + 5 * v + 4)
            for v in range(18)
        ],
        showgrid=False,
    )

    fig.update_layout(
        # width=800,
        # height=525,
        paper_bgcolor="#f8f9fa",
        margin=dict(l=60, r=10, b=60, t=35, pad=0),
        font=dict(size=14),
        template="none",
        shapes=shapes,
        hovermode="closest",
        # hoverlabel_align="left",
        legend=dict(
            orientation="v",
            xanchor="right" if leg_lower_right else "left",
            x=0.98 if leg_lower_right else 0.02,
            yanchor="bottom" if leg_lower_right else "top",
            y=0.04 if leg_lower_right else 0.98,
            itemclick=False,
            itemdoubleclick=False,
            bgcolor="rgba(0, 0, 0, 0)",
        ),
        modebar=dict(
            remove=["toImage", "lasso", "select", "zoomIn", "zoomOut"],
            orientation="h",
            color="#333333",
            bgcolor=None,
        ),
    )

    return fig


def pentad_trace(trace_input):

    q = trace_input["q"]

    return dict(
        type="scatter",
        name=trace_input["nm"],
        x=q.index + trace_input["dx"],
        y=(q[50].values * 10).round() / 10,
        error_y=dict(
            array=(q[83] - q[50]).values,
            arrayminus=(q[50] - q[17]).values,
            thickness=3,
            width=0,
            #             color="rgba" + trace_input["c"][3:-1] + ", 0.8)",
            color=trace_input["c"],
        ),
        mode="markers",
        marker=dict(
            # symbol="line-ew",
            color=trace_input["c"],
            opacity=1.0,
            size=13,
            line=dict(color="black", width=0.5),
        ),
        showlegend=trace_input["leg"],
        hovertemplate="%{y:.0f}",
    )


def pentad_shading(y5):
    return dict(
        type="rect",
        x0=y5,
        x1=y5 + 5,
        y0=-2,
        y1=32,
        layer="below",
        fillcolor="#f8f9fa",
        line=dict(color="black", width=0),
    )


def pentad_annotations(meta, r, c, vspace):

    x = 2029

    dy = 0.025
    y = 1 + dy if r == 1 else (1 - vspace) / 2 + dy

    Lnm = len(meta["name"])
    xspc = " " * (20 - Lnm)

    cmmn = {
        "x": x,
        "xref": "x" + str(c),
        "yref": "paper",
        "xanchor": "left",
        "yanchor": "top",
        "bgcolor": "white",
        "borderpad": 3,
        "showarrow": False,
    }
    annotations = [
        {
            **{
                "y": y - 0.055,
                "text": "Threshold: NOAA " + meta["threshold"].capitalize() + " ",
            },
            **cmmn,
        },
        {
            **{
                "y": y,
                "text": "<b>" + meta["name"] + "<b>" + xspc,  # ,
                "font": dict(size=16),
            },
            **cmmn,
        },
    ]
    if (r == 1) & (c == 1):
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
                    "y": y + 0.098,
                    "text": scenario_strings[meta["scenario"]] + " SLR Scenario",
                    "font": dict(size=14),
                    "bgcolor": None,
                },
            },
        )

    return annotations
