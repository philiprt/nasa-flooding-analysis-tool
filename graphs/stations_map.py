import plotly.graph_objs as go


def create_stations_map(stations, mapbox_access_token, station_select=None):

    if station_select is not None:
        slct_idx = stations.index.get_loc(station_select)
        clat = stations.loc[station_select].lat
        clon = stations.loc[station_select].lon
        zm = 6
    else:
        clat = 32
        clon = 210
        zm = 1.7
        slct_idx = None

    m = go.Figure(
        go.Scattermapbox(
            lat=stations.lat.tolist(),
            lon=stations.lon.tolist(),
            mode="markers",
            marker=dict(color="#0072B2", size=12),
            opacity=0.8,
            line=dict(width=2),
            selectedpoints=[slct_idx],
            selected=dict(marker=dict(color="#D55E00", size=18)),
            customdata=[dict(id=s, name=stations.name.loc[s]) for s in stations.index],
            hovertemplate="%{text}<extra></extra>",
            text=stations.name.to_list(),
        )
    )

    m.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=0, b=0, pad=0),
        modebar=dict(
            remove=["pan", "toImage", "lasso", "select"],
            orientation="v",
            color="#333333",
            bgcolor=None,
        ),
        clickmode="event+select",
        hovermode="closest",
        showlegend=False,
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(lat=clat, lon=clon),
            pitch=0,
            zoom=zm,
            style="mapbox://styles/mapbox/light-v10",
        ),
    )

    return m
