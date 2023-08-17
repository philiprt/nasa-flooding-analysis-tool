# ---------------------------------------------------------------------------

import numpy as np
import pandas as pd
import pickle
import xarray as xr
import glob
import os
import json
import requests
import datetime

# ---------------------------------------------------------------------------

fname = "../data/stations.pickle"
stations = pd.read_pickle(fname)

# -----------------------------------------------------------------------

# # only do select stations
# select = ["8720030"]
# keep = [n for n in stations.index if stations.loc[n, "id"] in select]
# stations = stations.loc[keep]

# ---------------------------------------------------------------------------

n = 0
Nsta = stations.index.size
for idx, sta in stations.iterrows():

    n += 1

    print(
        "Station "
        + str(sta["id"])
        + ": "
        + sta["name"]
        + " ("
        + str(n)
        + " of "
        + str(Nsta)
        + ")"
    )

    levels = {}

    # -----------------------------------------------------------------------
    # DATUMS

    url = (
        "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/"
        + str(sta["id"])
        + "/datums.json?units=metric"
    )

    # get datums
    rqst = json.loads(requests.get(url).text)
    datums = rqst["datums"]

    msl = [d["value"] for d in datums if d["name"] == "MSL"][0]
    mhhw = [d["value"] for d in datums if d["name"] == "MHHW"][0]
    mllw = [d["value"] for d in datums if d["name"] == "MLLW"][0]
    gt = [d["value"] for d in datums if d["name"] == "GT"][0]  # great diurnal range

    datums = {
        "msl": msl,
        "mllw": mllw,
        "mhhw": mhhw,
        "hat": rqst["HAT"],
        "lat": rqst["LAT"],
    }
    levels["datums"] = {d: np.round(datums[d] - mhhw, 3) for d in datums}
    levels["datums"]["gt"] = gt

    # -----------------------------------------------------------------------
    # FLOODING THRESHOLDS

    url = (
        "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/"
        + str(sta["id"])
        + "/floodlevels.json?units=metric"
    )

    thrsh = json.loads(requests.get(url).text)

    flood = {
        "minor": thrsh["nos_minor"]
        if thrsh["nos_minor"] is not None
        else np.round(1.04 * gt + 0.5 + mllw, 2),
        "moderate": thrsh["nos_moderate"]
        if thrsh["nos_moderate"] is not None
        else np.round(1.03 * gt + 0.8 + mllw, 2),
        "major": thrsh["nos_major"]
        if thrsh["nos_major"] is not None
        else np.round(1.04 * gt + 1.17 + mllw, 2),
        "nws_minor": thrsh["nws_minor"] if "nws_minor" in thrsh else None,
        "nws_moderate": thrsh["nws_moderate"] if "nws_moderate" in thrsh else None,
        "nws_major": thrsh["nws_major"] if "nws_major" in thrsh else None,
    }
    levels["flood"] = {
        f: np.round(flood[f] - mhhw, 3) if flood[f] is not None else None for f in flood
    }

    # -----------------------------------------------------------------------
    # EXTREME LEVELS

    url = (
        "https://api.tidesandcurrents.noaa.gov/dpapi/prod/webapi/product/.json?name=extremewaterlevels&station="
        + str(sta["id"])
        + "&units=metric"
    )

    xtrms = json.loads(requests.get(url).text)["ExtremeWaterLevels"]

    levels["extremes"] = (
        {
            "100yr": xtrms[0]["f1_gtmhhw"],
            "10yr": xtrms[0]["f10_gtmhhw"],
            "2yr": xtrms[0]["f50_gtmhhw"],
            "1yr": xtrms[0]["f99_gtmhhw"],
        }
        if len(xtrms) > 0
        else None
    )

    # -----------------------------------------------------------------------
    # TOP TEN OBSERVED

    url = (
        "https://api.tidesandcurrents.noaa.gov/dpapi/prod/webapi/product/.json?name=toptenwaterlevels&station="
        + str(sta["id"])
        + "&units=metric"
    )

    topten = xtrms = json.loads(requests.get(url).text)["topTenWaterLevels"]

    levels["topten"] = [
        {"date": ev["peakDate"], "height": ev["height"]} for ev in topten
    ]

    # -----------------------------------------------------------------------
    # DATE UPDATED

    levels["updated"] = datetime.date.today().strftime("%B %d, %Y")

    # -----------------------------------------------------------------------

    path = "./levels/"
    os.makedirs(path, exist_ok=True)
    fname = path + str(sta["id"]) + ".json"
    with open(fname, "w") as f:
        json.dump(levels, f)

    # -----------------------------------------------------------------------
