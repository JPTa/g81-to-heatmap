import datetime
import numpy as np
import re
import matplotlib
import matplotlib.image as mpimg

# Tell matplotlib to not worry about DISPLAY
matplotlib.use('Agg')

# Import pyplot as plt for ease of use
import matplotlib.pyplot as plt

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
  0.13750  0.14009  0.14148  0.14167  0.14065  0.13843  0.1350
 """

# Define your regex rules here depending on how
# your raw output looks. Ultimately, you want to
# arrive at several lines of comma separated
# float values, so split() works well later.
#g81_output_parsed = re.sub(r"^[ ]+", "", g81_output_raw.strip())
g81_output_parsed = re.sub(r"\n[ ]+", "\n", g81_output_raw.strip())
#g81_output_parsed = re.sub(r"[ ]+", ",", g81_output_parsed)

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

sheet_margin_front = 20
sheet_margin_back = 12
sheet_left_x = 0
sheet_right_x = sheet_left_x + x_size
sheet_front_y = -(sheet_margin_front)
sheet_back_y = sheet_front_y + y_size + sheet_margin_front + sheet_margin_back

left_probe_bed_position = 37 - ZERO_REF_X
front_probe_bed_position = 18.4 - ZERO_REF_Y
right_probe_bed_position = 245 - ZERO_REF_X
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
fig = plt.figure(dpi=96, figsize=(10, 8.3))
ax = plt.gca()

for x in x_vals:
  for y in y_vals:
    plt.plot(x, y, '.', color='k')
for x in [0, 3, 6]:
  for y in [0, 3, 6]:
    plt.plot(x_vals[x], y_vals[y], 'o', color='m')

contour = plt.contourf(x_vals, y_vals[::-1], z_vals, alpha=.75, antialiased=True)
img = mpimg.imread('Heatbed-MK52.png')
#img = mpimg.imread('mk52_steel_sheet.png')
plt.imshow(img, extent=[sheet_left_x, sheet_right_x, sheet_front_y, sheet_back_y], interpolation="lanczos")
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

plt.colorbar(contour, label="Level (mm) Variance: " + str(round(z_vals.max() - z_vals.min(), 3)))

# Save our graph as an image in the current directory.
fig.savefig('g81_heatmap.png', bbox_inches="tight")
