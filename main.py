import os
import sys
import numpy as np
import tensorflow as tf
from osgeo import gdal
import osr

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
data_dir = os.path.join(base_dir, 'data')

# Loads the geotiff
pop_data = gdal.Open(os.path.join(data_dir, 'TGO14adjv1.tif'))

# Store the values of the geotif into a np.array
pop_arr = np.array(pop_data.GetRasterBand(1).ReadAsArray())

# Null-values (neg-values) are replaced with zeros
pop_arr[pop_arr < 0] = 0

# Picking up values reference values needed to export to geotif
Projection = osr.SpatialReference()
Projection.ImportFromWkt(pop_data.GetProjectionRef())

geoTransform = pop_data.GetGeoTransform()

driver = gdal.GetDriverByName('GTiff')

dst_ds = driver.Create('test_tiff.tif', xsize=pop_arr.shape[1], ysize=pop_arr.shape[0],
                       bands=1, eType=gdal.GDT_Float32)

dst_ds.SetGeoTransform((
    geoTransform[0],  # x_min
    geoTransform[1],  # pixel width
    geoTransform[2],  # rotation
    geoTransform[3],  # y_max
    geoTransform[4],  # rotation
    geoTransform[5]  # pixel height
    ))

dst_ds.SetProjection(Projection.ExportToWkt())
dst_ds.GetRasterBand(1).WriteArray(pop_arr)
dst_ds.FlushCache()  # Write to disk.






