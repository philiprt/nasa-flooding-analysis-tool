FROM python:3
RUN mkdir /flooding_days
RUN apt-get update && apt-get install -y python3-netcdf4 libhdf5-dev
RUN pip install dash dash_bootstrap_components pandas xarray h5netcdf
WORKDIR /flooding_days
COPY . /flooding_days
EXPOSE 8050
CMD python /flooding_days/flooding_days_app.py