# -*- coding: utf-8 -*-
"""Read and download data from AWS inventory.

Initial focus will be on NEXRAD Level 2 radar data but eventually other
data types could be included.

Classes:
    NexradLevel2

Created on Mon May  4 08:36:33 2020

@author: eric.lenning
"""

import sys
import os
import math
from datetime import timedelta
from datetime import datetime
import s3fs
import numpy as np


class NexradLevel2():

    def __init__(this, site, start_datetime, end_datetime):
        this.site = site
        this.start_datetime = start_datetime
        this.end_datetime = end_datetime

    def daterange(this):
        """ Yields list of dates within specified time range. """

        span = this.end_datetime - this.start_datetime

        day_span = math.ceil(float(span.total_seconds()) / (3600*24))

        if this.start_datetime.hour > this.end_datetime.hour:
            day_span += 1

        for n in range(day_span):
            yield this.start_datetime + timedelta(n)

    def filelist(this):
        """ List of files for site within specified time range. """

        fs = s3fs.S3FileSystem(anon=True)
        fs.ls('s3://noaa-nexrad-level2/')

        radarfiles = []

        for single_date in this.daterange():

            YYYY = single_date.year  # strftime("%Y")
            mm = single_date.month  # strftime("%m")
            dd = single_date.day  # strftime("%d")

            # sample bucket dir : 'noaa-nexrad-level2/2018/07/19/KDMX/'
            bucket_dir_str = f'noaa-nexrad-level2/{YYYY:.0f}/{mm:02.0f}/\
                              {dd:02.0f}/{this.site}/'

            # list available files in bucket
            # sample filename :  KDMX20180719_221153_V06
            files = np.array(fs.ls(bucket_dir_str))

            for f in range(0, len(files)):

                filename = files[f].split('/')[-1]  # extracts fname after /

                if 'MDM' not in filename:
                    file_date = filename[4:19]

                    try:
                        file_datetime = datetime.strptime(file_date,
                                                          '%Y%m%d_%H%M%S')

                        if (file_datetime >= this.start_datetime
                            and file_datetime <= this.end_datetime):

                            print(files[f])

                            radarfiles.append(files[f])

                            info = fs.info(files[f])

                            print("size ", info['size'])

                            print(info)

                    except Exception:
                        print("Unexpected error:", sys.exc_info()[0])

        return radarfiles

    def download(this, filelist, raw_data_dir):
        """Download level 2 radar files from AWS.

        Files will be named according to the format on AWS but assumes nothing
        about the destination folder.  this is because different users may
        have different requirements for where data should be stored.

        Args:
            filelist: A list of files in the AWS NEXRAD inventory.
            raw_data_dir: Full pathname of download destination.

        Returns:
            The return value. True for success, False otherwise.
        """

        os.makedirs(raw_data_dir, exist_ok=True)

        fs = s3fs.S3FileSystem(anon=True)

        # https://noaa-nexrad-level2.s3.amazonaws.com/
        #           2015/04/10/KLOT/KLOT20150410_235635_V06.gz
        # sample filename :  KDMX20180719_221153_V06

        # downloaded = []

        download_count = 0

        # sample source filepath
        # 'noaa-nexrad-level2/2018/07/19/KDMX/KDMX20180719_221153_V06'
        for f in range(0, len(filelist)):
            try:
                print('getting... ' + str(filelist[f]))
                dst_filepath = os.path.join(raw_data_dir,
                                            filelist[f].split('/')[-1])

                print('...to ', dst_filepath)

                info = fs.info(filelist[f])

                remote_filesize = info['size']

                try:
                    stat = os.stat(dst_filepath)
                    print(stat)
                    local_filesize = stat.st_size

                    print('remote and local filesize: ',
                          remote_filesize, local_filesize)

                    if local_filesize < remote_filesize:
                        raise Exception('File exists but is too small.')

                    print('Already downloaded.')
                    download_count += 1
                except Exception:
                    fs.get(filelist[f], dst_filepath)  # download to dest dir
                    print('  Download complete!')
                    download_count += 1
                    # downloaded.append(filelist[f])
            except Exception:
                pass

        # Tell caller if you got all the files it wanted.
        if download_count == len(filelist):
            return True
        else:
            return False
