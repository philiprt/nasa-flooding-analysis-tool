import pickle

import numpy as np
import pandas as pd


def color_palette():

    # Wong (2011), Nature
    return [
        "#0072B2",
        "#56B4E9",
        "#CC79A7",
        "#009E73",
        "#F0E442",
        "#D55E00",
        "#E69F00",
    ]

    # # red, yellow, blue
    # return [
    #     "#d73027",
    #     "#fc8d59",
    #     "#fee090",
    #     "#ffffbf",
    #     "#e0f3f8",
    #     "#91bfdb",
    #     "#4575b4",
    # ]

    # # yellow, green, blue
    # return [
    #     "#ffffcc",
    #     "#c7e9b4",
    #     "#7fcdbb",
    #     "#41b6c4",
    #     "#1d91c0",
    #     "#225ea8",
    #     "#0c2c84",
    # ]

    # # Tol bright
    # return [
    #     "#228833",
    #     "#66ccee",
    #     "#4477aa",
    #     "#ccbb44",
    #     "#ee6677",
    #     "#aa3377",
    #     "#bbbbbb",
    # ]

    # # Tol vibrant
    # return [
    #     "#0077bb",
    #     "#33bbee",
    #     "#009988",
    #     "#ccbb44",
    #     "#cc3311",
    #     "#ee3377",
    #     "#bbbbbb",
    # ]


def fill_color(hex, opacity):
    hex = hex.lstrip("#")
    hlen = len(hex)
    return "rgba" + str(
        tuple(
            [int(hex[i : i + hlen // 3], 16) for i in range(0, hlen, hlen // 3)]
            + [opacity]
        )
    )


def station_string(sta):
    """Create a station-specific string for creating directories and filenames."""

    loc_str = "".join(
        [
            c if c != " " else "_"
            for c in [c for c in sta["name"].lower() if c not in [",", "."]]
        ]
    )
    return loc_str + "_" + str(sta["id"])


def experiment_string(msl_scenario, threshold, time_of_day):
    """Create a string describing an exceedance days experiment."""
    tod_str = "h" + "{:0>2}".format(time_of_day[0]) + "{:0>2}".format(time_of_day[1])
    return msl_scenario + "_" + threshold + "_" + tod_str


def station_list(select=None, exclude=None, sortby="lon"):
    """Return a dataframe where each row contains information about a NOS
    tide station."""

    fname = "../data/stations.pickle"
    stations = pd.read_pickle(fname)

    if select is None:

        # remove stations to skip
        skip = [
            8771013,  # eagle point
        ]
        if exclude is not None:
            if isinstance(exclude, int):
                exclude = [exclude]
            skip += exclude
        stations = stations.loc[
            [n for n in stations.index if stations.loc[n, "noaa id"] not in skip]
        ]

        # priortize certain stations in the order of completion
        first = [1612340, 8443970, 8658120, 8545240, 9414290]
        stations["sort"] = [
            first.index(stations.loc[n, "noaa id"])
            if stations.loc[n, "noaa id"] in first
            else n + len(first)
            for n in stations.index
        ]
        stations = stations.sort_values(by="sort")
        stations.index = range(stations.index.size)

    else:

        if isinstance(select, int):
            select = [select]

        stations = stations.loc[
            [n for n in stations.index if stations.loc[n, "noaa id"] in select]
        ]

    stations.loc[stations["lon"] < 0, "lon"] += 360
    stations.sort_values(sortby, inplace=True)
    stations.index = range(stations.shape[0])

    return stations


def stations_by_reg(stations):

    # organize stations by region and sort to make the ordering intuitive
    stn_by_reg = {}

    stn_by_reg["Pacific Islands"] = stations[stations["lon"] < 230].sort_values(
        by="lon", ascending=True
    )

    stn_by_reg["California"] = stations[
        (stations["lon"] > 230) & (stations["lon"] < 250) & (stations["lat"] <= 43)
    ].sort_values(by="lat", ascending=True)

    stn_by_reg["Oregon & Washington"] = stations[
        (stations["lon"] > 230) & (stations["lon"] < 250) & (stations["lat"] > 43)
    ].sort_values(by="lat", ascending=True)

    stn_by_reg["Gulf of Mexico, West"] = stations[
        (stations["lon"] > 250) & (stations["lon"] < 272)
    ].sort_values(by="lon", ascending=True)

    stn_by_reg["Gulf of Mexico, Florida"] = stations[
        (stations["lon"] > 272) & (stations["lon"] < 278.4)
    ].sort_values(by="lat", ascending=False)

    stn_by_reg["Caribbean"] = stations[stations["lon"] > 292].sort_values(
        by="lon", ascending=True
    )

    stn_by_reg["Atlantic Coast, South"] = stations[
        (stations["lon"] > 278.4) & (stations["lon"] < 282.5)
    ].sort_values(by="lat", ascending=True)

    atl_nrth = stations[
        (stations["lon"] > 282.5) & (stations["lon"] < 292)
    ].sort_values(by="lat", ascending=True)

    atl_nrth_states_1 = ["NC", "VA", "DC", "MD", "DE", "PA"]
    stn_by_reg["Atlantic Coast, North 1"] = pd.concat(
        [
            stn
            for state in [
                [stn[1] for stn in atl_nrth.iterrows() if stn[1]["name"][-2:] == st]
                for st in atl_nrth_states_1
            ]
            for stn in state
        ],
        axis=1,
    ).T

    atl_nrth_states_2 = ["NJ", "NY", "CT", "RI", "MA", "ME"]
    stn_by_reg["Atlantic Coast, North 2"] = pd.concat(
        [
            stn
            for state in [
                [stn[1] for stn in atl_nrth.iterrows() if stn[1]["name"][-2:] == st]
                for st in atl_nrth_states_2
            ]
            for stn in state
        ],
        axis=1,
    ).T

    for reg in stn_by_reg:
        stn_by_reg[reg]["Region"] = reg

    stn_by_reg = pd.concat([stn_by_reg[reg] for reg in stn_by_reg], axis=0)
    stn_by_reg.set_index("name", inplace=True)
    stn_by_reg = stn_by_reg.loc[:, ["noaa id", "Region", "lat", "lon"]]
    stn_by_reg.columns = ["NOAA ID", "Region", "Latitude", "Longitude"]
    stations.index.name = "Name"

    return stn_by_reg


# def analysis_by_reg_subsets(a_by_reg, subsets):

#     analysis = {}

#     for reg in subsets:

#         for s in subsets[reg]:
#             s["steps"] = s["steps"] if "steps" in s.keys() else None

#         analysis[reg] = [
#             [
#                 {**a, **{"steps": s["steps"]}}
#                 for a in a_by_reg[s["threshold"]][reg]
#                 if a["station"]["name"] == s["name"]
#             ][0]
#             for s in subsets[reg]
#         ]

#     return analysis


def yoi_steps(prjn, search_range=None):

    if search_range is not None:
        prjn = prjn.loc[search_range[0] - 10 : search_range[1] + 10]

    deltas = prjn.rolling(21, center=True).apply(
        lambda x: (x[20] - x[10]) - (x[10] - x[0]), raw=True
    )
    multipliers = prjn.rolling(21, center=True).apply(lambda x: x[20] / x[10], raw=True)

    deltas = deltas[(prjn > 1) & (prjn <= 50) & deltas.notna()]
    multipliers = multipliers.loc[deltas.index]
    drnk = deltas.rank()
    mrnk = multipliers.rank()
    avgrnk = (drnk + mrnk) / 2
    try:
        yoi = avgrnk.idxmax()
        return [yoi + d for d in [-10, 0, 10]]
    except:
        return None


def yoi_analysis(analysis, stations, search_range=None, combine_regions=None):

    yoi = []

    for stn in analysis:
        for scn in analysis[stn]:
            for thrsh in analysis[stn][scn]:

                qty = analysis[stn][scn][thrsh]["xdys_ann_ptl"].loc[:, 50]
                steps = yoi_steps(qty, search_range=search_range)

                base = {
                    "Name": stn,
                    "NOAA ID": stations.loc[stn, "NOAA ID"],
                    "Region": stations.loc[stn, "Region"],
                    "Scenario": scn,
                    "Threshold": thrsh,
                }

                if (steps is not None) and ~np.isnan(steps[1]):

                    steps = qty.loc[steps]

                    calc = {
                        "YOI": steps.index[1],
                        "10-year increase": steps.diff().iloc[2],
                        "10-year multiplier": (
                            np.round(100 * steps.iloc[2] / steps.iloc[1]) / 100
                        ),
                    }

                else:

                    calc = {
                        "YOI": None,
                        "10-year increase": None,
                        "10-year multiplier": None,
                    }

                yoi.append({**base, **calc})

    yoi_df = pd.DataFrame(yoi)

    if combine_regions is not None:
        for new_reg in combine_regions:
            for old_reg in combine_regions[new_reg]:
                z = yoi_df["Region"] == old_reg
                yoi_df.loc[z, "Region"] = new_reg

    return yoi_df


def first_month_analysis(count, analysis, stations, combine_regions=None):

    ann_count_lookup = {5: 60, 10: 120, 15: 180}
    ann_count = ann_count_lookup[count]

    P = [25, 50]

    fmo = []

    for stn in analysis:
        for scn in analysis[stn]:
            for thrsh in analysis[stn][scn]:

                a = analysis[stn][scn][thrsh]

                cum_p_fmo = a["prob_mxmo_frst_yr"][count].cumsum().loc[2020:]
                p_first_mo = [(cum_p_fmo > p / 100).idxmax() for p in P]

                calc = {
                    "Year": [
                        p_first_mo[0],
                        p_first_mo[1],
                        a["prob_mxmo"][count].ge(0.5).idxmax(),
                        a["xdys_ann_ptl"][50].ge(ann_count).idxmax(),
                    ],
                    "Quantity": [
                        "P" + str(P[0]),
                        "P" + str(P[1]),
                        "Expected monthly",
                        "Expected annually",
                    ],
                }

                N = len(calc["Year"])
                base = {
                    "Name": [stn] * N,
                    "Region": [stations.loc[stn, "Region"]] * N,
                    "Scenario": [scn] * N,
                    "Threshold": [thrsh] * N,
                }

                fmo.append(pd.DataFrame({**base, **calc}))

    fmo_df = pd.concat(fmo, axis=0, ignore_index=True)

    if combine_regions is not None:
        for new_reg in combine_regions:
            for old_reg in combine_regions[new_reg]:
                z = fmo_df["Region"] == old_reg
                fmo_df.loc[z, "Region"] = new_reg

    return fmo_df


def first_month_by_region(count, a_by_reg, yoi_df):

    ann_count_lookup = {5: 60, 10: 120, 15: 180}
    ann_count = ann_count_lookup[count]

    fmo_by_reg = {}

    for reg in [r for r in a_by_reg["minor"]]:

        fmo_by_reg[reg] = {}

        for mnr, mdt in zip(a_by_reg["minor"][reg], a_by_reg["moderate"][reg]):

            # check that mnr and mdt refer to same station
            if mnr["station"]["name"] != mdt["station"]["name"]:
                raise Exception("Station match failed.")

            thrsh = yoi_df.loc[yoi_df["Name"] == mnr["station"]["name"]][
                "Threshold"
            ].iloc[0]

            if thrsh == "Minor":
                stn = mnr
            elif thrsh == "Moderate":
                stn = mdt

            cum_p_fmo = stn["prob_mxmo_frst_yr"][count].cumsum().loc[2020:]

            prb = [10, 25, 50, 75, 90]

            fmo_by_reg[reg][mnr["station"]["name"]] = {
                "p_first_mo": pd.Series(
                    [(cum_p_fmo > p / 100).idxmax() for p in prb], index=prb
                ),
                "xpctd_mo": stn["prob_mxmo"][count].ge(0.5).idxmax(),
                "xpctd_ann": stn["xdys_ann_ptl"][50].ge(ann_count).idxmax(),
                "threshold": thrsh,
            }

    return fmo_by_reg


def first_month_aggregate_dataframe(fmo_by_reg, combine_regions=None):

    P = [25, 50]

    fmo_df = pd.concat(
        [
            pd.DataFrame(
                {
                    "Name": [loc for n in range(4)],
                    "Region": [reg for n in range(4)],
                    "Threshold": [fmo_by_reg[reg][loc]["threshold"] for n in range(4)],
                    "Year": [
                        fmo_by_reg[reg][loc]["p_first_mo"].loc[P[0]],
                        fmo_by_reg[reg][loc]["p_first_mo"].loc[P[1]],
                        fmo_by_reg[reg][loc]["xpctd_mo"],
                        fmo_by_reg[reg][loc]["xpctd_ann"],
                    ],
                    "Quantity": [
                        "P" + str(P[0]),
                        "P" + str(P[1]),
                        "Expected monthly",
                        "Expected annually",
                    ],
                }
            )
            for reg in fmo_by_reg
            for loc in fmo_by_reg[reg]
        ],
        axis=0,
        ignore_index=True,
    )

    if combine_regions is not None:
        for new_reg in combine_regions:
            for old_reg in combine_regions[new_reg]:
                z = fmo_df["Region"] == old_reg
                fmo_df.loc[z, "Region"] = new_reg

    return fmo_df


def peak_season_analysis(analysis, stations, combine_regions=None):

    pks = []

    for stn in analysis:
        for scn in analysis[stn]:
            for thrsh in analysis[stn][scn]:

                a = analysis[stn][scn][thrsh]

                d = {
                    "average": a["xdys_pent_mn_ptl"][50] / 12,
                    "peak_ssn": a["xdys_pent_mxssn_ptl"][50] / 3,
                    "peak_mo": a["xdys_pent_mxmo_ptl"][50],
                }
                qty = d["peak_mo"] / d["average"]
                #                 qty = (3 * d["peak_ssn"]) / (12 * 5 * d["average"])
                qty.loc[d["average"] < 1] = None
                N = qty.values.size

                calc = {
                    "Year": qty.index.values,
                    "Quantity": qty.values,
                }

                base = {
                    "Name": [stn] * N,
                    "Region": [stations.loc[stn, "Region"]] * N,
                    "Scenario": [scn] * N,
                    "Threshold": [thrsh] * N,
                }

                pks.append(pd.DataFrame({**base, **calc}))

    pks_df = pd.concat(pks, axis=0, ignore_index=True)

    if combine_regions is not None:
        for new_reg in combine_regions:
            for old_reg in combine_regions[new_reg]:
                z = pks_df["Region"] == old_reg
                pks_df.loc[z, "Region"] = new_reg

    return pks_df


def top10_percent_analysis(analysis, stations, combine_regions=None):

    t10 = []

    for stn in analysis:
        for scn in analysis[stn]:
            for thrsh in analysis[stn][scn]:

                a = analysis[stn][scn][thrsh]

                calc = {
                    "Year": a["xdys_pent_top10pct_ptl"].index.values,
                    "Quantity": a["xdys_pent_top10pct_ptl"][50].values,
                    "Total": a["xdys_pent_mn_ptl"][50].values[:-1] * 5,
                }

                N = calc["Year"].size
                base = {
                    "Name": [stn] * N,
                    "Region": [stations.loc[stn, "Region"]] * N,
                    "Scenario": [scn] * N,
                    "Threshold": [thrsh] * N,
                }

                t10.append(pd.DataFrame({**base, **calc}))

    t10_df = pd.concat(t10, axis=0, ignore_index=True)

    if combine_regions is not None:
        for new_reg in combine_regions:
            for old_reg in combine_regions[new_reg]:
                z = t10_df["Region"] == old_reg
                t10_df.loc[z, "Region"] = new_reg

    return t10_df


class ProgressBar:
    def __init__(self, total, description=None):

        self.total = total
        self.decimals = 1
        self.length = 50
        self.fill = ">"
        self.iteration = 0
        self.intervals = np.ceil(np.linspace(1, self.total, self.length))
        self.percent = np.linspace(0, 100, self.length + 1)[1:].astype(int)

        unq, cnt = np.unique(self.intervals, return_counts=True)
        idx = np.array([np.where(self.intervals == u)[0][-1] for u in unq])
        self.intervals = self.intervals[idx]
        self.percent = self.percent[idx]
        self.cumcnt = np.cumsum(cnt)

        if description:
            print(description)
        print("|%s| 0%% complete" % (" " * self.length), end="\r")

    def update(self):

        self.iteration += 1

        if self.iteration in self.intervals:
            prog = np.where(self.intervals == self.iteration)[0][-1]
            pctstr = str(self.percent[prog]) + "%"
            bar = self.fill * self.cumcnt[prog] + " " * (
                self.length - self.cumcnt[prog]
            )
            print("\r|%s| %s complete" % (bar, pctstr), end="\r")
            if self.iteration == self.total:
                print()  # blank line on completion
