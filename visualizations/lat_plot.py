from osgeo import gdal, osr
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from scipy.interpolate import spline

country = 'france'
if country == 'france':
    ds_2015 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\data\france\2015.tif')
    ds_2020 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2020.tif')
    ds_2100 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2100.tif')

if country == 'denmark':
    ds_2015 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\data\denmark\2015.tif')
    ds_2020 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2020.tif')
    ds_2100 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2100.tif')


old_cs = osr.SpatialReference()
old_cs.ImportFromWkt(ds_2020.GetProjectionRef())

# create the new coordinate system
wgs84_wkt = """
GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.01745329251994328,
        AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4326"]]"""
new_cs = osr.SpatialReference()
new_cs.ImportFromWkt(wgs84_wkt)

# create a transform object to convert between coordinate systems
transform = osr.CoordinateTransformation(old_cs,new_cs)

#get the point to transform, pixel (0,0) in this case
width = ds_2020.RasterXSize
height = ds_2020.RasterYSize
gt = ds_2020.GetGeoTransform()

minx = gt[0]
miny = gt[3] + width*gt[4] + height*gt[5]
maxx = gt[0] + width*gt[1] + height*gt[2]
maxy = gt[3]

latlong_min = transform.TransformPoint(minx,miny)
latlong_max = transform.TransformPoint(maxx,maxy)

lon_min = latlong_min[0]
lon_max = latlong_max[0]
lat_min = latlong_min[1]
lat_max = latlong_max[1]

lon_dif = lon_max - lon_min
lat_dif = lat_max - lat_min

np_2015 = np.array(ds_2015.GetRasterBand(1).ReadAsArray())
np_2020 = np.array(ds_2020.GetRasterBand(1).ReadAsArray())
np_2100 = np.array(ds_2100.GetRasterBand(1).ReadAsArray())

no_rows = np_2020.shape[0]
no_cols = np_2020.shape[1]
cell_lon_change = lon_dif / no_cols
cell_lat_change = lat_dif / no_rows

np_2020_lat = np.zeros(no_rows)
np_2020_latpop = np.zeros(no_rows)
np_dif_lat = np.zeros(no_rows)

for i in range(no_rows):
    np_2020_lat[i] = lat_max - i * cell_lat_change
    np_2020_latpop[i] = np.sum(np_2020[i,:])
    np_dif_lat[i] = np.sum(np_2100[i,:]) - np.sum(np_2015[i,:])

np_2020_lon = np.zeros(no_cols)
np_2015_lonpop = np.zeros(no_cols)
np_2020_lonpop = np.zeros(no_cols)
np_2100_lonpop = np.zeros(no_cols)
np_dif_lon = np.zeros(no_cols)


print(cell_lat_change)
print(cell_lon_change)
for i in range(no_cols):
    print(i)
    print(np.shape(np_2020_lonpop))
    print(np.shape(np_2020))
    np_2020_lon[i] = lon_min + i * cell_lon_change
    np_2015_lonpop[i] = np.sum(np_2015[:,i])
    np_2020_lonpop[i] = np.sum(np_2020[:,i])
    np_2100_lonpop[i] = np.sum(np_2100[:,i])
    np_dif_lon[i] = np.sum(np_2100[:,i]) - np.sum(np_2015[:,i])


# df = pd.DataFrame({'Population': np_2020_latpop, 'Latitude': np_2020_lat})
# df.plot()

# x_smooth_2020 = np.linspace(np_2020_latpop.min(), np_2020_latpop.max(), 300)
# y_smooth_2020 = spline(np_2020_latpop, np_2020_lat, x_smooth_2020)
#
#
# sns.set(style='whitegrid')
# fig = plt.figure()
# plt.plot(x_smooth_2020, y_smooth_2020, linewidth=0.5)
# plt.xlabel('Population')
# plt.ylabel('Degrees latitude')
# plt.savefig('lat_2020_plot.png', bbox_inches='tight')
# plt.show()
# plt.clf()
# plt.close()
sns.set(style='whitegrid')
fig = plt.figure()
plt.plot(np_dif_lat, np_2020_lat, linewidth=0.5)
plt.xlabel('Difference in population between 2015 and 2100')
plt.ylabel('Degrees latitude')
plt.title('Latitude population development - France', fontsize=16)
plt.savefig('lat_dif_plot.png', bbox_inches='tight')
plt.show()
plt.clf()
plt.close()

fig = plt.figure()
plt.plot(np_2020_lon, np_dif_lon, linewidth=0.5)
plt.ylabel('Difference in population between 2015 and 2100')
plt.xlabel('Degrees longitude')
plt.title('Longitude population development - Denmark', fontsize=16)
plt.savefig('lon_dif_plot.png', bbox_inches='tight')
plt.show()
plt.clf()
plt.close()

# fig = plt.figure()
# plt.plot(np_2020_lon, np_2015_lonpop, linewidth=0.5)
# plt.ylabel('Population 2015')
# plt.xlabel('Degrees longitude')
# plt.title('Longitude population development - Denmark', fontsize=16)
# plt.savefig('lon_2015_plot.png', bbox_inches='tight')
# plt.show()
# plt.clf()
# plt.close()

fig = plt.figure()
ax1 = fig.add_axes([0,0,1,1])
ax2 = fig.add_axes([0.13,0.48,0.4,0.4])
ax1.plot(np_2020_lon, np_2015_lonpop, linewidth=0.5, label='2015')
ax1.plot(np_2020_lon, np_2100_lonpop, linewidth=0.5, label='2100')
ax1.legend(fontsize=12)
ax1.set_title('Longitude population 2015 and 2100 - Denmark', fontsize=16)
ax1.set_xlabel('Degrees longitude')
ax1.set_ylabel('Population')


ax2.plot(np_2020_lon[(np_2020_lon > 9.5) & (np_2020_lon < 10.5)], np_2015_lonpop[(np_2020_lon > 9.5) & (np_2020_lon < 10.5)], linewidth=0.5, label='2015')
ax2.plot(np_2020_lon[(np_2020_lon > 9.5) & (np_2020_lon < 10.5)], np_2100_lonpop[(np_2020_lon > 9.5) & (np_2020_lon < 10.5)], linewidth=0.5, label='2100')

ax2.set_xlabel('Degrees longitude')
ax2.set_ylabel('Population')
# ax2.set_xlabel('Degrees longitude')
# ax2.set_ylabel('Population')

# plot_2015 = plt.plot(np_2020_lon, np_2015_lonpop, linewidth=0.5, label='2015')
# plot_2100 = plt.plot(np_2020_lon, np_2100_lonpop, linewidth=0.5, label='2100')

# plt.ylabel('Population')
# plt.xlabel('Degrees longitude')

plt.savefig('lon_2100_plot.png', bbox_inches='tight')
plt.show()
plt.clf()
plt.close()