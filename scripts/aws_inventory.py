# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 18:30:54 2020

@author: Eric
"""
# Here we use Amazon AWS to download and process the desired radar data
import s3fs
import numpy as np
from datetime import datetime
from datetime import timedelta
import math
import re
from re import search
import os
import pathlib
import sys
import matplotlib.pyplot as plt
import pyart
import cartopy.crs as ccrs


shape_path = 'C:/data/GIS/counties/counties_central_conus/counties_central_conus.shp'

#prods = ['cross_correlation_ratio', 'spectrum_width', 'reflectivity',
#         'differential_reflectivity', 'differential_phase', 'velocity']

prods = ['reflectivity', 'velocity']


try:
    os.listdir('/usr')
    scripts_dir = '/data/scripts'
    sys.path.append(os.path.join(scripts_dir,'resources'))
except:
    scripts_dir = 'C:/data/scripts'
    sys.path.append(os.path.join(scripts_dir,'resources'))

from reference_data import set_paths
data_dir,image_dir,archive_dir,gis_dir,py_call,placefile_dir = set_paths()

from custom_cmaps import plts
#from gis_layers import pyart_gis_layers
#shape_mini = pyart_gis_layers()

class Nexrad():

    def __init__(self, site, start_datetime, end_datetime):
        self.site = site
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.YYYY = self.start_datetime.year # strftime("%Y")
        self.mm = self.start_datetime.month # strftime("%m")
        self.dd = self.start_datetime.day # strftime("%d")
        self.date_str = f'{self.YYYY:.0f}{self.mm:02.0f}{self.dd:02.0f}'
        self.image_dest_dir = os.path.join(image_dir,self.date_str,self.site)
        self.download_dir = os.path.join(data_dir,self.date_str,self.site,'raw')

    def daterange(self):
        span = self.end_datetime - self.start_datetime
        day_span = math.ceil(float(span.total_seconds()) / (3600*24))

        if self.start_datetime.hour > self.end_datetime.hour:
            day_span += 1

        for n in range(day_span):
            yield self.start_datetime + timedelta(n)

    def aws_files(self):
        """
        Returns
        -------
        aws_file_list : list
            a list of aws filepaths that meet the search criteria
        """

        aws_file_list = []
        fs = s3fs.S3FileSystem(anon=True)
        fs.ls('s3://noaa-nexrad-level2/')

        for single_date in self.daterange():

            YYYY = single_date.year # strftime("%Y")
            mm = single_date.month # strftime("%m")
            dd = single_date.day # strftime("%d")

            # example AWS bucket directory  : 'noaa-nexrad-level2/2018/07/19/KDMX/'
            bucket_dir_str = f'noaa-nexrad-level2/{YYYY:.0f}/{mm:02.0f}/{dd:02.0f}/{self.site}/'
            #print(bucket_dir_str)
            # list available files in bucket
            # sample filename :  KDMX20180719_221153_V06
            files = np.array(fs.ls(bucket_dir_str))

            for f in range(0, len(files)):
                #print(files[f])
                filename = files[f].split('/')[-1]  # this extracts filename only after last '/'

                # searching for YYYYMMDD_HHmmss string in filename
                p = re.compile('[0-9]{8}_[0-9]{6}')
                m = p.search(filename)

                try:
                    file_datetime = datetime.strptime(m.group(0), '%Y%m%d_%H%M%S')

                    if (file_datetime >= self.start_datetime and
                        file_datetime <= self.end_datetime):

                        aws_file_list.append(files[f])
                        #print('aws file ... ' + str(files[f]))

                        #try:
                        #    yield files[f]
                        #except GeneratorExit:
                        #    print("Need to do some clean up.")
                        #    pass
                        

                except:
                    pass

        return aws_file_list

    def download_files(self,plot=True):
        """
        First ensures a download directory is created using YYYY,mm,dd
        from start_datetime. Example: {data_dir}/YYYYmmdd/radar/raw
        
        Second, downloads files to this directory
        """
        download_list = []
        download_dir = os.path.join(data_dir,self.download_dir)
        print('\ndownload directory  ....  ' + str(download_dir) + '\n')
        os.makedirs(download_dir,exist_ok=True)
        fs = s3fs.S3FileSystem(anon=True)
        fs.ls('s3://noaa-nexrad-level2/')
        for f in range(0, len(self.aws_files())):
            filepath = self.aws_files()[f]

            #print('downloading ... ' + str(filepath))
            filename = filepath.split('/')[-1]
            #print('filename ... ' + str(filename))
            test_path = os.path.join(download_dir,filename)
            test_file = pathlib.Path(test_path)
            download_list.append(test_path)

            if test_file.exists ():
                print(filename + '  ....  already exists ')
                pass
            else:
                print(filename + '  ....  downloading ')
                fs.get(filepath,test_path)
                print(test_path)

            if plot:
                self.plot_ref(test_path)

        return download_list



    def get_places(self,xmin,xmax,ymin,ymax):
    
        src = 'C:/data/GIS/places/places_conus.csv'
            
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



    def nexrad_location(self,filepath,dx=1,dy=1):
        radar = pyart.io.read_nexrad_archive(self.download_files()[0])
        self.nexrad_lon = radar.longitude['data'][0]
        self.nexrad_lat = radar.latitude['data'][0]
        
        xmin = self.nexrad_lon - dx
        xmax = self.nexrad_lon + dx
        ymin = self.nexrad_lat - dy
        ymax = self.nexrad_lat + dy
        locations = self.get_places(xmin, xmax, ymin, ymax)
        return locations


    def extract_sweeps(self,orig_list,cut):
        sweep_list = [int(round(x*10)) for x in orig_list]
        cut_list = []
        found_cut = False
        for t in range (0,len(sweep_list)):

            if sweep_list[t] == cut and found_cut is False:

                cut_list.append(t)       
                found_cut = True
            elif sweep_list[t] == cut and found_cut is True:
                found_cut = False

        return cut_list

    def format_name(self,title_str):
        #'KILX 0.5 Deg. 2019-06-16T03:01:10.802000Z \nEquivalent reflectivity factor'
        az_start = radar.sweep_start_ray_index['data'][s]
        delta_secs = int(round(radar.time['data'][az_start]))
        new_time = dt_obj + timedelta(seconds=delta_secs)
        temp_title = display.generate_title('reflectivity',s)
        #title_parts = temp_title.split(' ')
        #el = title_parts[1]
        #new_title = "{} {} Degrees Reflectivity\n".format(title_parts[0],el)

        time_title = datetime.strftime(new_time, '%a %b %d, %Y\n%I:%M %p UTC')
        title = new_title + time_title        

    def plot_ref(self,filepath,dx=1,dy=1):
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
        from gis_layers import pyart_gis_layers
        shape_mini = pyart_gis_layers()
        os.makedirs(self.image_dest_dir,exist_ok=True)     
        # create datetime object from filename
        p = re.compile('[0-9]{8}_[0-9]{6}')
        
        m = p.search(filepath)        

        print(m.group(0))
        dt_obj = datetime.strptime(m.group(0),'%Y%m%d_%H%M%S')
        # convert datetime object from UTC to local time
        local_dt_obj = dt_obj# - time_shift
        # create string for title based on new datetime object
        title = datetime.strftime(local_dt_obj, '%a %b %d, %Y\n%I:%M %p EDT')

        #filename = filepath.split('\\')[-1]
        radar = pyart.io.read_nexrad_archive(filepath)
        display = pyart.graph.RadarMapDisplay(radar)

        angles = list(radar.fixed_angle['data'])
        these_sweeps = self.extract_sweeps(angles,5)

            
        rda_lon = radar.longitude['data'][0]
        rda_lat = radar.latitude['data'][0]
        xmin = rda_lon - dx
        xmax = rda_lon + dx
        ymin = rda_lat - dy
        ymax = rda_lat + dy

        for s in these_sweeps:

            locations = self.get_places(xmin, xmax, ymin, ymax)
            fig = plt.figure(figsize=(6,6))
            title = display.generate_title('reflectivity',1)
            #title = 'hi'
            projection = ccrs.LambertConformal(central_latitude=rda_lat,central_longitude=rda_lon)
            display.plot_ppi_map('reflectivity', int(s), vmin=-30, vmax=80,cmap=plts['Ref']['cmap'],
                                  title=title, title_flag=True,
                                  colorbar_flag = True,colorbar_label = plts['Ref']['cblabel'],
                                  min_lon=xmin, max_lon=xmax, min_lat=ymin, max_lat=ymax,
                                  resolution='50m', projection=projection, shapefile=shape_path,
                                  shapefile_kwargs = {'facecolor':'none', 'edgecolor':'gray', 'linewidth':0.7},
                                  lat_lines=[0],lon_lines=[0], # moves lat/lon lines off to the side
                                  fig=fig,  lat_0=rda_lat, lon_0=rda_lon)
    
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
            for p in range(0,len(locations)):
                place = locations[p][0]
                lat = float(locations[p][2])
                lon = float(locations[p][1])        
                plt.plot(lon,lat, 'o', color='black',transform=ccrs.PlateCarree(),zorder=10)
                plt.text(lon,lat,place,horizontalalignment='center',verticalalignment='top',transform=ccrs.PlateCarree())
    
            fname_dt = datetime.strftime(new_time, '%Y%m%d_%H%M%S')
            #fname = "{}_{}.png".format(fname_dt,el)
            fname = "{}_ref.png".format(fname_dt)
            image_dst_path = os.path.join(self.image_dest_dir,fname)
            plt.savefig(image_dst_path,format='png',bbox_inches="tight", dpi=150)
            print('  Image saved at  ' + image_dst_path)
            plt.close()

        return

#------------------------------------------------------------------------------
# Testing the class

radarId = 'KILX'
start_date = datetime(2019, 6, 16, 3, 0)
end_date = datetime(2019, 6, 16, 3, 20)

example = Nexrad(radarId, start_date, end_date)
down = example.download_files()
hi = down[0]
print(down[0])

#filelist = NexradFileList(radarId, start_date, end_date).aws_file_list()





