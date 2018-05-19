from osgeo import gdal, osr
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

ds = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2020.tif')
width = ds.RasterXSize
height = ds.RasterYSize

old_cs = osr.SpatialReference()
old_cs.ImportFromWkt(ds.GetProjectionRef())

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
width = ds.RasterXSize
height = ds.RasterYSize
gt = ds.GetGeoTransform()

minx = gt[0]
miny = gt[3] + width*gt[4] + height*gt[5]
maxx = gt[0] + width*gt[1] + height*gt[2]
maxy = gt[3]

latlong_min = transform.TransformPoint(minx,miny)
latlong_max = transform.TransformPoint(maxx,maxy)

lat_min = latlong_min[1]
lat_max = latlong_max[1]

lat_dif = lat_max - lat_min


np_2020 = np.array(ds.GetRasterBand(1).ReadAsArray())
no_rows = np_2020.shape[0]
cell_lat_change = lat_dif / no_rows

np_2020_lat = np.zeros(no_rows)
np_2020_latpop = np.zeros(no_rows)
for i in range(no_rows):
    np_2020_lat[i] = lat_max - i * cell_lat_change
    np_2020_latpop[i] = np.sum(np_2020[i][:])

# df = pd.DataFrame({'Population': np_2020_latpop, 'Latitude': np_2020_lat})
# df.plot()

sns.set(style='whitegrid')
fig = plt.figure()
plt.plot(np_2020_latpop, np_2020_lat, linewidth=0.5)

plt.xlabel('Population')
plt.ylabel('Degrees latitude')
plt.savefig('lat_plot.png', bbox_inches='tight')
plt.show()