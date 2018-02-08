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

driver = gdal.GetDriverByName('GTiff')

dst_ds = driver.Create('test_tiff.tif', xsize=myarray.shape[1], ysize=myarray.shape[0],
                       bands=1, eType=gdal.GDT_Float32)

dst_ds.SetGeoTransform((
    5000,  # 0
    100,  # 1
    0,  # 2
    5000,  # 3
    0,  # 4
    -100))

dst_ds.SetProjection(Projection.ExportToWkt())
dst_ds.GetRasterBand(1).WriteArray(myarray)
dst_ds.FlushCache()  # Write to disk.






