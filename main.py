import os
import sys
import numpy as np
import tensorflow as tf
from osgeo import gdal
import osr

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
data_dir = os.path.join(base_dir, 'data')

pop_data = gdal.Open(os.path.join(data_dir, 'TGO14adjv1.tif'))

myarray = np.array(pop_data.GetRasterBand(1).ReadAsArray())
print(myarray.shape)

print(myarray.max())

print(myarray)

myarray[myarray < 0] = 0

print(myarray)

Projection = osr.SpatialReference()
Projection.ImportFromWkt(pop_data.GetProjectionRef())

geoTransform = pop_data.GetGeoTransform()
minx = geoTransform[0]
maxy = geoTransform[3]


print(geoTransform)
print(minx)
print(maxy)

driver = gdal.GetDriverByName('GTiff')

dst_ds = driver.Create('test_tiff.tif', xsize=myarray.shape[1], ysize=myarray.shape[0],
                       bands=1, eType=gdal.GDT_Float32)

dst_ds.SetGeoTransform((
    geoTransform[0],  # x_min
    geoTransform[1],  # pixel width
    geoTransform[2],  # rotation
    geoTransform[3],  # y_max
    geoTransform[4],  # rotation
    geoTransform[5]  # pixel height
    ))

# xmin
# ymax

dst_ds.SetProjection(Projection.ExportToWkt())
dst_ds.GetRasterBand(1).WriteArray(myarray)
dst_ds.FlushCache()  # Write to disk.






