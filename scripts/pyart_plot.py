# -*- coding: utf-8 -*-
"""
Downloads WSR-88D Archive level 2 files using AWS
Plots reflectivity using pyart and then saves images

Prequisites:
     set_paths  :  A function called fromresources/reference_data.py that sets paths
                   You may want to override some or all of these
    shape_path  :  A path to the shapefile you want to plot
         plts   :  Dictionary of colormaps (cmaps) and information about how to plot ( e.g., value range, colorbar settings, etc.) 
    
"""

import sys
import os
import configlocal as cfg
from aws_catalog import NexradLevel2

sys.path.append(os.path.join(cfg.resources_dir))

data_dir = cfg.data_dir

image_dir = cfg.images_dir

placefile_dir = cfg.placefile_dir

archive_dir = cfg.archive_dir

gis_dir = cfg.gis_dir

py_call = cfg.py_call

def get_places(xmin,xmax,ymin,ymax):

    src = os.path.join(cfg.gis_dir, "places", "places_conus.csv")
        
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
                        places.append([place,lon,lat])
            except:
                pass
    
    return places

def pyart_plot_reflectivity(filepath,filename,dx=1,dy=1):
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
        shape_path - full local path to shapefile to add. This needs to be staged in advance.

         cmap  : str 
                 plts dictionary that needs to be imported.
                 Can also just use default cmap by removing vmin,vmax, cmap arguments below
        
    Returns
    -------
    Nothing. Just exits after creating and saving plot.

    """
    # create datetime object from filename
    dt_obj = datetime.strptime(filename[4:19],'%Y%m%d_%H%M%S')
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

    ''' Issue #4: Commented out until GIS folder is provided in pyart repo
    locations = get_places(xmin, xmax, ymin, ymax)
    '''
    fig = plt.figure(figsize=(6,6))
    projection = ccrs.LambertConformal(central_latitude=rda_lat,central_longitude=rda_lon)
    display.plot_ppi_map('reflectivity', 0, vmin=-30, vmax=80,cmap=plts['Ref']['cmap'],
                         title=title, title_flag=True,
                         colorbar_flag = True,colorbar_label = plts['Ref']['cblabel'],
                         min_lon=xmin, max_lon=xmax, min_lat=ymin, max_lat=ymax,
                         resolution='50m', projection=projection, shapefile=shape_path,
                         shapefile_kwargs = {'facecolor':'none', 'edgecolor':'gray', 'linewidth':0.7},
                         lat_lines=[0],lon_lines=[0], # moves lat/lon lines off to the side
                         fig=fig,  lat_0=rda_lat, lon_0=rda_lon)

    ''' Issue #4 -- Module gis_layers not provided in pyart repo
    ax = display.ax
    
    for sh in shape_mini:
        if search('inter', str(sh)):
            ax.add_feature(shape_mini[sh], facecolor='none', edgecolor='red', linewidth=0.5)
        elif search('states', str(sh)):
            ax.add_feature(shape_mini[sh], facecolor='none', edgecolor='black', linewidth=1, zorder=10)
        elif search('counties', str(sh)):
            ax.add_feature(shape_mini[sh], facecolor='none', edgecolor='gray', linewidth=0.5)
        else:
            pass
    '''
    
    ''' Issue #4: Commented out until GIS folder is provided in pyart repo
    for p in range(0,len(locations)):
        place = locations[p][0]
        lat = float(locations[p][2])
        lon = float(locations[p][1])        
        plt.plot(lon,lat, 'o', color='black',transform=ccrs.PlateCarree(),zorder=10)
        plt.text(lon,lat,place,horizontalalignment='center',verticalalignment='top',transform=ccrs.PlateCarree())
    '''
    
    image_dst_path = os.path.join(this_image_dir,filename + '.png')

    plt.savefig(image_dst_path,format='png',bbox_inches="tight", dpi=150)
    print('  Image saved at  ' + image_dst_path)
    plt.close()
    
    # Can't return locations until GIS folder added to repo
    return None # locations


import numpy as np
import matplotlib.pyplot as plt
import pyart
import cartopy.crs as ccrs

# Issue #4 -- Module gis_layers not provided in pyart repo
#from gis_layers import pyart_gis_layers
#shape_mini = pyart_gis_layers()

from custom_cmaps import plts
from datetime import datetime, timedelta
from re import search


###########################################
# Need this pre-staged in directory of your choice
# can be anything, not just counties

# TODO: Maybe nove to a central config location.  For now, put in gis_dir.
#shape_path = 'C:/data/GIS/counties/counties_central_conus/counties_central_conus.shp'
shape_path = os.path.join(gis_dir, 'c_02ap19', 'c_02ap19.shp')

# TODO: Move this to an external location, and eventually provide via a GUI.
# Define radar, date, hours in which to acquire files and plot data
###########################################
radar = 'KLOT'
start_date = datetime(2015, 4, 9, 23, 50)
end_date = datetime(2015, 4, 10, 0, 10)
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

# create a string of format YYYYmmdd based on inputs above (example: '20190719')
# then, use this string to create sub-directory in image directory to save images
YYYY = start_date.year
mm = start_date.month
dd = start_date.day
ymd_str = f'{YYYY:.0f}{mm:02.0f}{dd:02.0f}'
this_image_dir = os.path.join(image_dir,ymd_str,'radar')
os.makedirs(this_image_dir, exist_ok = True)

this_data_dir = os.path.join(data_dir,ymd_str,radar,'raw')

radar_files_already_downloaded = nexradlist.download(filelist, this_data_dir)

# Eventually most of this can go away since downloads now occur elsewhere.
if radar_files_already_downloaded is False:
    print("Data files not found or some were missing.")
    
    """
    # sample directory I'd use    : 'C:/data/20180719/KDMX/raw'
    this_data_dir = os.path.join(data_dir,ymd_str,radar,'raw')
    os.makedirs(this_data_dir,exist_ok=True)
    
    
    # Here we use Amazon AWS to download and process the desired radar data
    import s3fs
    fs = s3fs.S3FileSystem(anon=True)
    fs.ls('s3://noaa-nexrad-level2/')
    # example AWS bucket directory  : 'noaa-nexrad-level2/2018/07/19/KDMX/'
    bucket_dir_str = f'noaa-nexrad-level2/{YYYY:.0f}/{mm:02.0f}/{dd:02.0f}/{radar}/'
    
    # list available files in bucket
    # sample filename :  KDMX20180719_221153_V06
    files = np.array(fs.ls(bucket_dir_str))
    
    # sample source filepath  : 'noaa-nexrad-level2/2018/07/19/KDMX/KDMX20180719_221153_V06'
    for f in range(0,len(files)):
        filename = files[f].split('/')[-1]  # this extracts filename only after last '/'
        file_hour = int(filename.split('_')[1][0:2])
        if file_hour >= hr_min and file_hour <= hr_max and 'MD' not in filename:
            print('getting... ' + str(files[f]))
            dst_filepath = os.path.join(this_data_dir,files[f].split('/')[-1])
            fs.get(files[f],dst_filepath)                   # download files to destination dir
            print('  Download complete! Now creating plot.')
            locations = pyart_plot_reflectivity(dst_filepath,filename)  # calls this method to plot each file on the fly
    """

else:
    #this_data_dir = 'C:/data/20190720/radar' # wherever you have the arc2 files stored
    files = os.listdir(this_data_dir)
    for file in files:
        if 'V06' in file:
            full_filepath = os.path.join(this_data_dir,file)
            print('  Beginning plot of ' + full_filepath)
            locations = pyart_plot_reflectivity(full_filepath,file)
