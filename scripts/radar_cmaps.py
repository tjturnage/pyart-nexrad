# -*- coding: utf-8 -*-
"""
Creates radar cmaps for matplotlib
https://matplotlib.org/3.1.0/tutorials/colors/colormap-manipulation.html
Assumption: You'll import the created cmaps into wdss_create_netcdfs.py
author: thomas.turnage@noaa.gov
Last updated: 05 May 2020
------------------------------------------------
"""

import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.colors import ListedColormap
import sys
# from metpy.plots import colortables


def make_cmap(colors, position=None, bit=False):
    """
    Creates colormaps (cmaps) for different products.

    Information on cmap with matplotlib
    https://matplotlib.org/3.1.0/tutorials/colors/colormap-manipulation.html

    Parameters
    ----------
       colors : list of tuples containing RGB values. Tuples must be either:
                - arithmetic (zero to one) - ex. (0.5, 1, 0.75)
                - 8-bit                    - ex. (127, 256, 192)
     position : ordered list of floats
                None: default, returns cmap with equally spaced colors
                If a list is provided, it must have:
                  - 0 at the beginning and 1 at the end
                  - values in ascending order
                  - a number of elements equal to the number of tuples in
                    colors
          bit : boolean
                False : default, assumes arithmetic tuple format
                True  : set to this if using 8-bit tuple format
    Returns
    -------
         cmap

    """
    import numpy as np
    bit_rgb = np.linspace(0, 1, 256)
    if position is None:
        position = np.linspace(0, 1, len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red': [], 'green': [], 'blue': []}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap', cdict, 256)
    return cmap


plts = {}
cmaps = {}

one_ramp = [0, 1]
two_ramp = [0, 0.5, 1]

# -------- Begin creating custom color maps --------

# --- Reflectivity

colors = [(0, 0, 0), (130, 130, 130), (95, 189, 207), (57, 201, 105),
          (57, 201, 105), (0, 40, 0), (9, 94, 9), (255, 207, 0),
          (255, 207, 0), (255, 207, 0), (255, 133, 0), (255, 0, 0),
          (89, 0, 0), (255, 245, 255), (225, 11, 227), (164, 0, 247),
          (99, 0, 214), (5, 221, 224), (58, 103, 181), (255, 255, 255)]
position = [0, 45/110, 46/110, 50/110, 51/110, 65/110, 66/110, 70/110,
            71/110, 80/110, 81/110, 90/110, 91/110, 100/110, 101/110,
            105/110, 106/110, 107/110, 109/110, 1]

cmaps['dkc_z'] = {'colors': colors, 'position': position, 'min': -30,
                  'max': 80}

colors = [(0, 0, 0), (130, 130, 130), (95, 189, 207), (57, 201, 105),
          (57, 201, 105), (0, 40, 0), (9, 94, 9), (255, 207, 0),
          (255, 207, 0),
          (255, 133, 0), (255, 0, 0), (89, 0, 0), (255, 245, 255),
          (225, 11, 227), (164, 0, 247), (99, 0, 214), (5, 221, 224),
          (58, 103, 181), (255, 255, 255)]

# This version of wdtd z fades to white instead of black
# colors=[(255, 255, 255), (130, 130, 130), (95, 189, 207), (57, 201, 105),
#        (57, 201, 105), (0, 40, 0), (9, 94, 9), (255, 207, 0),
#        (255, 207, 0),
#        (255, 133, 0), (255, 0, 0), (89, 0, 0), (255, 245, 255),
#        (225, 11, 227), (164, 0, 247), (99, 0, 214), (5, 221, 224),
#        (58, 103, 181), (255, 255, 255)]
position = [0.0, 0.407, 0.409, 0.452, 0.454, 0.587, 0.590, 0.632, 0.636, 0.722,
            0.727, 0.812, 0.818, 0.902, 0.909, 0.947, 0.954, 0.992, 1.0]
cmaps['wdtd_z'] = {'colors': colors, 'position': position, 'min': -30,
                   'max': 80}

colors = [(255, 255, 255), (255, 255, 255), (200, 200, 200), (155, 155, 155),
          (90, 90, 90)]
# colors=[(255, 255, 255), (130, 130, 130), (95, 189, 207), (57, 201, 105),
#          (57, 201, 105), (0,40, 0), (9,94,9), (255, 207, 0), (255, 207, 0),
#          (255, 133, 0), (255, 0, 0), (89, 0, 0), (255, 245, 255),
#          (225, 11, 227), (164, 0, 247), (99, 0, 214), (5, 221, 224),
#          (58, 103, 181), (255, 255, 255)]
position = [0.0, 45/110, 75/110, 90/110, 1]
cmaps['wdtd_bw'] = {'colors': colors, 'position': position, 'min': -30,
                    'max': 80}

# --- Velocity

colors = [(0, 0, 0), (12, 250, 250), (221, 181, 243), (238, 186, 248),
          (5, 8, 255), (14, 22, 255), (158, 238, 220), (119, 244, 154),
          (146, 240, 199), (3, 239, 0), (0, 48, 0), (87, 124, 85),
          (109, 131, 107), (138, 110, 124), (132, 62, 71), (93, 2, 3),
          (253, 30, 46), (253, 155, 156), (252, 202, 137), (255, 255, 0),
          (238, 143, 56), (238, 143, 56), (248, 246, 245), (248, 246, 245),
          (63, 18, 13), (63, 18, 13)]
position = [0.0, 0.001, 0.1187, 0.125, 0.2437, 0.25, 0.3093, 0.3125, 0.3520,
            0.3541, 0.4531, 0.4583, 0.4979, 0.5, 0.5395, 0.5416, 0.6406,
            0.6458, 0.6854, 0.6875, 0.7468, 0.75, 0.8687, 0.875, 0.9937, 1.0]
cmaps['wdtd_v'] = {'colors': colors, 'position': position, 'min': -120,
                   'max': 120}
cmaps['rankine'] = {'colors': colors, 'position': position, 'min': -3,
                    'max': 3}

colors = [(0, 0, 0), (50, 65, 120), (55, 70, 130), (75, 90, 155),
          (100, 120, 180), (125, 140, 200), (175, 200, 250),
          (50, 115, 70), (75, 135, 90), (105, 160, 110),
          (130, 180, 135), (165, 205, 160), (225, 225, 225),
          (215, 190, 180), (190, 150, 130), (160, 120, 95),
          (135, 85, 55), (105, 45, 10), (240, 160, 140),
          (220, 120, 105), (195, 80, 70), (165, 60, 62),
          (135, 55, 55), (105, 35, 45)]
position = [0.0, 0.00001, 0.05, 0.1, 0.15, 0.2, 0.25, 0.255, 0.3, 0.35, 0.4,
            0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.745, 0.75, 0.8, 0.85, 0.9,
            0.95, 1.0]
cmaps['dkc_v'] = {'colors': colors, 'position': position, 'min': -100,
                  'max': 100}

z = cmaps['wdtd_z']
v = cmaps['wdtd_v']

vel_max = 100
vels_array = np.linspace(-vel_max, vel_max, 11)
vticks = np.ndarray.tolist(vels_array)

ref_cmap = make_cmap(z['colors'], position=z['position'], bit=True)
plt.register_cmap(cmap=ref_cmap)
plts['ReflectivityQC'] = {'cmap': ref_cmap, 'vmn': z['min'], 'vmx': z['max'],
                          'title': 'Reflectivity',
                          'cbticks': [0, 15, 30, 50, 60], 'cblabel': 'dBZ'}
plts['Ref'] = plts['ReflectivityQC']

vel_cmap = make_cmap(v['colors'], position=v['position'], bit=True)
plt.register_cmap(cmap=vel_cmap)
plts['Velocity'] = {'cmap': vel_cmap, 'vmn': v['min'], 'vmx': v['max'],
                    'title': 'Velocity', 'cbticks': vticks, 'cblabel': 'kts'}
plts['Vel'] = plts['Velocity']
plts['SRV'] = {'cmap': vel_cmap, 'vmn': v['min'], 'vmx': v['max'],
               'title': 'SR Velocity', 'cbticks': vticks, 'cblabel': 'kts'}


# --- Spectrum Width
sw_colors = [(0, 0, 0), (220, 220, 255), (180, 180, 240), (50, 50, 150),
             (255, 255, 0), (255, 150, 0), (255, 0, 0), (255, 255, 255)]
sw_position = [0, 1/40, 5/40, 0.25, 15/40, 0.5, 0.75, 1]
sw_cmap = make_cmap(sw_colors, position=sw_position, bit=True)
plt.register_cmap(cmap=sw_cmap)
plts['SpectrumWidth'] = {'cmap': sw_cmap, 'vmn': 0, 'vmx': 40,
                         'title': 'Spectrum Width',
                         'cbticks': [0, 10, 15, 20, 25, 40], 'cblabel': 'kts'}

# --- CC
cc_colors = [(175, 175, 175), (255, 225, 200), (100, 50, 50), (175, 150, 120),
             (255, 255, 75), (35, 100, 35), (100, 255, 100), (175, 175, 175)]
cc_position = [0, 10/105, 50/105, 70/105, 90/105, 96/105, 100/105, 1]
cc_cmap = make_cmap(cc_colors, position=cc_position, bit=True)
plt.register_cmap(cmap=cc_cmap)
plts['RhoHV'] = {'cmap': cc_cmap, 'vmn': 0.00, 'vmx': 1.05,
                 'title': 'Correlation Coefficient',
                 'cbticks': [0.4, 0.6, 0.8, 0.9, 1.0], 'cblabel': ' '}
