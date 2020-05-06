# -*- coding: utf-8 -*-
"""
Downloads WSR-88D Archive level 2 files using AWS
Plots reflectivity using pyart and then saves images

Prequisites:

    shape_path  :  A path to the shapefile you want to plot
         plts   :  Dictionary of colormaps (cmaps) and information about how
                   to plot ( e.g., value range, colorbar settings, etc.)

"""

import sys
import os
import configlocal as cfg
from aws_catalog import NexradLevel2
import matplotlib.pyplot as plt
import pyart
import cartopy.crs as ccrs
from metpy.plots import USCOUNTIES
from radar_cmaps import plts
from datetime import datetime, timedelta

sys.path.append(os.path.join(cfg.resources_dir))

data_dir = cfg.data_dir

image_dir = cfg.images_dir

placefile_dir = cfg.placefile_dir

archive_dir = cfg.archive_dir

gis_dir = cfg.gis_dir

py_call = cfg.py_call


def get_places(xmin, xmax, ymin, ymax):

    src = os.path.join(cfg.gis_dir, "places_conus.csv")

    places = []
    with open(src) as fp:
        content = fp.read().splitlines()
        for line in content:
            test = line.split(',')
            place = test[0]
            lat = test[-2][:6]
            lon = test[-1][:7]
            try:
                float(lon)
                if float(lon) > xmin and float(lon) < xmax:
                    if float(lat) > ymin and float(lat) < ymax:
                        places.append([place, lon, lat])
            except Exception:
                pass

    return places


def pyart_plot_reflectivity(filepath, filename, dx=1, dy=1):
    """

    Parameters
    ----------
    filepath : str
        full local path to Archive 2 radar file
    filename : str
        just the filename instead of the full path
    dx : float, optional
        Number of degrees longitude on each side of the radar location to plot.
        The default is 1.
    dy : float, optional
        Number of degrees latitude on each side of the radar location to plot.
        The default is 1.

    Dependencies
    ----------
    shapefile  : str
        shape_path - full local path to shapefile to add.
                     This needs to be staged in advance.

         cmap  : str
                 plts dictionary that needs to be imported.
                 Can also just use default cmap by removing vmin,vmax, cmap
                 arguments below

    Returns
    -------
    Nothing. Just exits after creating and saving plot.

    """
    # create datetime object from filename
    dt_obj = datetime.strptime(filename[4:19], '%Y%m%d_%H%M%S')
    # convert datetime object from UTC to local time
    local_dt_obj = dt_obj - time_shift
    # create string for title based on new datetime object
    title = datetime.strftime(local_dt_obj, '%a %b %d, %Y\n%I:%M %p EDT')
    radar = pyart.io.read_nexrad_archive(filepath)
    display = pyart.graph.RadarMapDisplay(radar)
    rda_lon = radar.longitude['data'][0]
    rda_lat = radar.latitude['data'][0]
    xmin = rda_lon - dx
    xmax = rda_lon + dx
    ymin = rda_lat - dy
    ymax = rda_lat + dy

    locations = get_places(xmin, xmax, ymin, ymax)

    fig = plt.figure(figsize=(6, 6))
    projection = ccrs.LambertConformal(central_latitude=rda_lat,
                                       central_longitude=rda_lon)
    display.plot_ppi_map('reflectivity', 0, vmin=-30, vmax=80,
                         cmap=plts['Ref']['cmap'],
                         title=title, title_flag=True,
                         colorbar_flag=True,
                         colorbar_label=plts['Ref']['cblabel'],
                         min_lon=xmin, max_lon=xmax, min_lat=ymin,
                         max_lat=ymax,
                         resolution='50m', projection=projection,
                         # shapefile=shape_path,
                         shapefile_kwargs={'facecolor': 'none',
                                           'edgecolor': 'gray',
                                           'linewidth': 0.7},
                         lat_lines=[0], lon_lines=[0],  # omit lat/lon lines
                         fig=fig, lat_0=rda_lat, lon_0=rda_lon)

    ax = display.ax
    ax.add_feature(USCOUNTIES.with_scale('5m'), edgecolor='gray',
                   linewidth=0.7)

    for p in range(0, len(locations)):
        place = locations[p][0]
        lat = float(locations[p][2])
        lon = float(locations[p][1])
        plt.plot(lon, lat, 'o', color='black', transform=ccrs.PlateCarree(),
                 zorder=10)
        plt.text(lon, lat, place, horizontalalignment='center',
                 verticalalignment='top', transform=ccrs.PlateCarree())

    image_dst_path = os.path.join(this_image_dir, filename + '.png')

    plt.savefig(image_dst_path, format='png', bbox_inches="tight", dpi=150)
    print('  Image saved at  ' + image_dst_path)
    plt.close()

    return None


# ##########################################
# Need this pre-staged in directory of your choice
# can be anything, not just counties

# TODO: Maybe nove to a central config location.  For now, put in gis_dir.
# shape_path =
# 'C:/data/GIS/counties/counties_central_conus/counties_central_conus.shp'
shape_path = os.path.join(gis_dir, 'c_02ap19', 'c_02ap19.shp')


# TODO: Move this to an external location, and eventually provide via a GUI.
# Define radar, date, hours in which to acquire files and plot data
###########################################
radar = 'KGRR'
start_date = datetime(2015, 4, 10, 23, 50)
end_date = datetime(2015, 4, 11, 0, 5)
###########################################

# Go to AWS or other location and get list of available files for date range
nexradlist = NexradLevel2(radar, start_date, end_date)
filelist = nexradlist.filelist()

# Assuming we'll do central time for Chicago
# my klunky way of subtracting 6 hours from UTC, to get local time
# This of course changes with transition between standard and daylight time.
# Been meaning to include more robust handling of this, but since I'm focused
# more on research, UTC has always been sufficient
# maybe this is a good project for someone else :)

time_shift = timedelta(hours=5)

# create a string of format YYYYmmdd based on inputs above
# (example: '20190719')
# then, use this string to create sub-directory in image directory
# to save images
YYYY = start_date.year
mm = start_date.month
dd = start_date.day
ymd_str = f'{YYYY:.0f}{mm:02.0f}{dd:02.0f}'
this_image_dir = os.path.join(image_dir, ymd_str, 'radar')
os.makedirs(this_image_dir, exist_ok=True)

this_data_dir = os.path.join(data_dir, ymd_str, radar, 'raw')

radar_files_already_downloaded = nexradlist.download(filelist, this_data_dir)

# Eventually most of this can go away since downloads now occur elsewhere.
if radar_files_already_downloaded is False:
    print("Data files not found or some were missing.")


else:
    # this_data_dir = 'C:/data/20190720/radar' # where arc2 files are
    files = os.listdir(this_data_dir)
    for file in files:
        if 'V06' in file:
            full_filepath = os.path.join(this_data_dir, file)
            print('  Beginning plot of ' + full_filepath)
            locations = pyart_plot_reflectivity(full_filepath, file)
