# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 18:30:14 2020

@author: eric.lenning

*** Copy this file to configlocal.py on your system. ***

In the variables below, enter the valid pathnames for your system.

You may only need to change the first entry.

"""
import os

project_dir = os.path.join("C:/Users/eric.lenning/Python")

resources_dir = os.path.join(project_dir, "resources")

root_dir = os.path.join(project_dir, "pyart")

scripts_dir = os.path.join(root_dir, "scripts")

data_dir = os.path.join(root_dir, "data")

images_dir = os.path.join(root_dir, "images")

gis_dir = os.path.join(root_dir, "GIS")

archive_dir = os.path.join(root_dir, "archive")

placefile_dir = os.path.join(root_dir, "placefiles")

py_call = None
