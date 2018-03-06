import numpy as np
import numpy as np
import os
import sys
from osgeo import gdal
import osr

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
data_dir = os.path.relpath('..\\data', base_dir)
config_dir = os.path.relpath('..\\configs', base_dir)


# Loads the geotiff
pop_data_10 = gdal.Open(os.path.join(data_dir, '2010.tif'))

# Store the values of the geotif into a np.array
pop_arr_10 = np.array(pop_data_10.GetRasterBand(1).ReadAsArray())
pop_arr_10 = np.delete(pop_arr_10, -1, axis=1)  # Shape not the same as pop data from 14 and 15

print(pop_arr_10.shape)

Projection = osr.SpatialReference()
Projection.ImportFromWkt(pop_data_10.GetProjectionRef())

geoTransform = pop_data_10.GetGeoTransform()

driver = gdal.GetDriverByName('GTiff')

dst_ds = driver.Create('2010.tif', xsize=pop_arr_10.shape[1], ysize=pop_arr_10.shape[0],
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
dst_ds.GetRasterBand(1).WriteArray(pop_arr_10)
dst_ds.FlushCache()  # Write to disk.