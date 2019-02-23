# This is the raw G81 output from Pronterface,
# Your regex replace rules below will clean it
# and make it ready for conversion to a list of
# float values.
g81_output_raw = """
  0.33000  0.29435  0.25157  0.20167  0.14463  0.08046  0.00917
  0.30509  0.28572  0.25841  0.22315  0.17995  0.12881  0.06972
  0.27731  0.27026  0.25516  0.23204  0.20087  0.16168  0.11444
  0.24667  0.24796  0.24185  0.22833  0.20741  0.17907  0.14333
  0.21315  0.21884  0.21847  0.21204  0.19955  0.18100  0.15639
  0.17676  0.18288  0.18501  0.18315  0.17729  0.16745  0.15361
  0.13750  0.14009  0.14148  0.14167  0.14065  0.13843  0.13500
 """

import re

# Define your regex rules here depending on how
# your raw output looks. Ultimately, you want to
# arrive at several lines of comma separated
# float values, so split() works well later.
g81_output_parsed = re.sub(r"\n[ ]+", "\n", g81_output_raw.strip())

# No need to edit anything below this :)
#
import datetime
import numpy as np
from numpy import radians as rad
import matplotlib
from matplotlib.patches import Arc, RegularPolygon
import matplotlib.image as mpimg

# Tell matplotlib to not worry about DISPLAY
matplotlib.use('Agg')

# Import pyplot as plt for ease of use
import matplotlib.pyplot as plt

# Draw arc arrow
def arcArrow(ax,radius,centX,centY,direction='ccw',color_='black'):
    angle_ = 165

    # Line
    arc = Arc([centX,centY],radius,radius,angle=angle_,
      theta1=205,capstyle='round',linestyle='-',lw=3,color=color_)
    ax.add_patch(arc)

    dir = 1
    if direction == 'cw':
      dir = -1  
    
    # Create the arrow head
    endX=centX+(radius/2)*dir*np.cos(rad(angle_)) #Do trig to determine end position
    endY=centY+(radius/2)*np.sin(rad(angle_))

    ax.add_patch(
      RegularPolygon(
        (endX, endY),
         3,                   # triangle
         radius/5,            # radius
         dir*rad(360+angle_), # orientation
         color=color_
      )
    )
    ax.set_xlim([centX-radius,centY+radius]) and ax.set_ylim([centY-radius,centY+radius]) 

# Calculate how many degrees to turn per distance
def dist2deg(distance):
    screw_pitch = 0.5
    return str(int(round(distance / screw_pitch * 360))) + "°"

# Add adjustment points
def addAdjuster(ax,x,y,z):
  if z < 0:
    z_marker = '_'
    z_mcolor = 'g'
    dir = 'ccw'
  elif z > 0:
    z_marker = '+'
    z_mcolor = 'r'
    dir = 'cw'    
  plt.plot(x, y, z_marker, color=z_mcolor)
  plt.text(x, y-10, dist2deg(z), ha="center", va="center",
    bbox=dict(boxstyle="round", facecolor="white", lw=0.75)
  )  
  arcArrow(ax,15,x,y,dir,z_mcolor)
  
# We're about to convert these strings into floats,
# this list will hold onto those.
g81_list_of_lists = []

# Split our regex corrected output by line, then
# split each line by its commas and convert the
# string values to floats.
for line in g81_output_parsed.splitlines():
    g81_list_of_lists.append([float(i) for i in re.split(r"[ ]+", line)])

g81_xyz_list_of_lists = []
row_count = 0
col_count = 0
x_size = 250
y_size = 210
  
# These values come from mesh_bed_calibration.cpp
ZERO_REF_X = 2
ZERO_REF_Y = 9.4

sheet_margin_front = 24.5
sheet_margin_back = 16.5
sheet_left_x = 0
sheet_right_x = sheet_left_x + x_size
sheet_front_y = -(sheet_margin_front)
sheet_back_y = sheet_front_y + y_size + sheet_margin_front + sheet_margin_back

left_probe_bed_position = 38.5 - ZERO_REF_X
front_probe_bed_position = 18.4 - ZERO_REF_Y
right_probe_bed_position = 243.5 - ZERO_REF_X
back_probe_bed_position = 210.4 - ZERO_REF_Y

x_inc = (right_probe_bed_position - left_probe_bed_position) / 6 
y_inc = (back_probe_bed_position - front_probe_bed_position) / 6
x_vals = np.zeros(7)
y_vals = np.zeros(7)
z_vals = np.zeros(shape=(7,7))

center_z = g81_list_of_lists[3][3];
for col in g81_list_of_lists:
  for val in col:
    x_vals[col_count] = col_count*x_inc + left_probe_bed_position
    y_vals[row_count] = row_count*y_inc + front_probe_bed_position
    z_vals[col_count][row_count] = val - center_z
    row_count = row_count + 1
  col_count = col_count + 1
  row_count = 0
    
# Set figure and gca objects, this will let us
# adjust things about our heatmap image as well
# as adjust axes label locations.
fig = plt.figure(dpi=96, figsize=(10, 8))
ax = plt.gca()

for x in x_vals:
  for y in y_vals:
    plt.plot(x, y, '.', color='k')

# Show bolt adjustment values
# Bolt location Y values inverted
x_points = [16.7, 0, 0, 125.4, 0, 0, 228.8]
y_points =  [210.4, 0, 0, 105.6, 0, 0, 0.8]
output_mm_txt = "\nMeasured distances (in mm):"
output_deg_txt = "\n\nBolt adjustments (in degrees):"
for y in [0, 3, 6]:
  output_mm_txt = output_mm_txt + "\n"
  output_deg_txt = output_deg_txt + "\n" 
  for x in [0, 3, 6]:
    z_val = round(z_vals[y][x], 3)
    output_mm_txt = output_mm_txt + "\t" + str(z_val) 
    output_deg_txt = output_deg_txt + "\t" + dist2deg(z_val)
    if x == 3 and y == 3:
      marker = '*'
      mcolor = 'g'
      msize = 15
    else:
      marker = 'o'
      mcolor = 'b'
      msize = 10
    plt.plot(x_vals[x], y_vals[y], marker, color=mcolor, linewidth=1, markersize=msize)
    if z_val:
      addAdjuster(ax, x_points[x], y_points[y], z_val)
print(output_mm_txt + output_deg_txt)

# Select color theme
cmap_theme = plt.cm.get_cmap("RdBu")
contour = plt.contourf(x_vals, y_vals[::-1], z_vals, alpha=.90, antialiased=True, cmap=cmap_theme)
img = mpimg.imread('Heatbed-MK52.png')
#img = mpimg.imread('mk52_steel_sheet.png')
plt.imshow(img, extent=[sheet_left_x, sheet_right_x, sheet_front_y, sheet_back_y], interpolation="lanczos", cmap=cmap_theme)
ax.set_xlim(left=0, right=x_size)
ax.set_ylim(bottom=0, top=y_size)

# Set various options about the graph image before
# we generate it. Things like labeling the axes and
# colorbar, and setting the X axis label/ticks to
# the top to better match the G81 output.
plt.title("Mesh Level: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
plt.axis('image')
ax.axes.get_xaxis().set_visible(False)
ax.axes.get_yaxis().set_visible(False)

plt.colorbar(contour, label="Bed Level (mm) Maximum variance: " + str(round(z_vals.max() - z_vals.min(), 3)))

# Save our graph as an image in the current directory.
fig.savefig('g81_heatmap.png', bbox_inches="tight")
