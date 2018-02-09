import os
import sys
import numpy as np
import tensorflow as tf
from osgeo import gdal
import osr
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
data_dir = os.path.join(base_dir, 'data')

# Loads the geotiff
pop_data_10 = gdal.Open(os.path.join(data_dir, 'TGO10v4.tif'))
pop_data_14 = gdal.Open(os.path.join(data_dir, 'TGO14adjv1.tif'))
pop_data_15 = gdal.Open(os.path.join(data_dir, 'TGO15adjv4.tif'))

# Store the values of the geotif into a np.array
pop_arr_10 = np.array(pop_data_10.GetRasterBand(1).ReadAsArray())
pop_arr_10 = np.delete(pop_arr_10, -1, axis=1) # Shape not the same as pop data from 14 and 15

pop_arr_14 = np.array(pop_data_14.GetRasterBand(1).ReadAsArray())
pop_arr_15 = np.array(pop_data_15.GetRasterBand(1).ReadAsArray())

# Null-values (neg-values) are replaced with zeros
pop_arr_10[pop_arr_10 < 0] = 0
pop_arr_14[pop_arr_14 < 0] = 0
pop_arr_15[pop_arr_15 < 0] = 0

print(pop_arr_10.shape)
print(pop_arr_14.shape)
print(pop_arr_15.shape)

pop_dif_10_14_mat = pop_arr_14 - pop_arr_10
pop_dif_10_14 = np.sum(pop_dif_10_14_mat)

pop_dif_14_15_mat = pop_arr_15 - pop_arr_14
pop_dif_14_15 = np.sum(pop_dif_14_15_mat)

print(pop_dif_10_14)
print(pop_dif_14_15)

# Shows the np.array
plt.imshow(pop_arr_10)
plt.show()

# Train Test Split
# if np.sum(x_data) = np.sum(x_data_original) + pop_dif_yearX_yearY)
x_data = pop_arr_10
y_true = pop_arr_14
x_train, x_test, y_train, y_test = train_test_split(x_data,y_true, test_size=0.3, random_state = 101)

print(x_train.shape)
print(x_test.shape)
print(y_train.shape)
print(y_test.shape)


# Picking up values reference values needed to export to geotif
Projection = osr.SpatialReference()
Projection.ImportFromWkt(pop_data_14.GetProjectionRef())

geoTransform = pop_data_14.GetGeoTransform()

driver = gdal.GetDriverByName('GTiff')

dst_ds = driver.Create('test_tiff.tif', xsize=pop_arr_14.shape[1], ysize=pop_arr_14.shape[0],
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
dst_ds.GetRasterBand(1).WriteArray(pop_arr_14)
dst_ds.FlushCache()  # Write to disk.






