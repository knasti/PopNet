import os
import sys
import numpy as np
import tensorflow as tf
from osgeo import gdal
import osr
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

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


def create_chunks(x_data, y_true):
    chunk_height = 32  # cells
    chunk_width = 32  # cells

    # INPUT DATA
    # Takes the number of rows MOD the chunk height to determine if we need to add extra rows (padding)
    rest_rows = x_data.shape[0] % chunk_height
    if rest_rows != 0:
        # Adds rows until the input data matches with the chunk height
        x_data = np.r_[x_data, np.zeros((chunk_height - rest_rows, x_data.shape[1]))]

    # Takes the number of cols MOD the chunk width to determine if we need to add extra columns (padding)
    rest_cols = x_data.shape[1] % chunk_width
    if rest_rows != 0:
        # Adds columns until the input data matches with the chunk width
        x_data = np.c_[x_data, np.zeros((x_data.shape[0], chunk_height - rest_cols))]

    # LABEL (should give the same result as above)
    # Takes the number of rows MOD the chunk height to determine if we need to add extra rows (padding)
    rest_rows = y_true.shape[0] % chunk_height
    if rest_rows != 0:
        # Adds rows until the input data matches with the chunk height
        y_true = np.r_[y_true, np.zeros((chunk_height - rest_rows, y_true.shape[1]))]

    # Takes the number of cols MOD the chunk width to determine if we need to add extra columns (padding)
    rest_cols = y_true.shape[1] % chunk_width
    if rest_rows != 0:
        # Adds columns until the input data matches with the chunk width
        y_true = np.c_[y_true, np.zeros((y_true.shape[0], chunk_height - rest_cols))]

    chunk_rows = int(x_data.shape[0] / chunk_height)
    chunk_cols = int(x_data.shape[1] / chunk_width)
    no_chunks = int(chunk_rows * chunk_cols)

    # [number of chunks, chunk height, chunk width, number of features]
    x_data = x_data.reshape((no_chunks, chunk_height, chunk_width, 1))
    y_true = y_true.reshape((no_chunks, chunk_height, chunk_width, 1))

    # Creating train test split
    x_train, x_test, y_train, y_test = train_test_split(x_data, y_true, test_size=0.3, random_state=101)

    x_train_shape = x_train.shape
    x_test_shape = x_test.shape
    y_train_shape = y_train.shape
    y_test_shape = y_test.shape

    # Normalizing the data with scikit-learn, needs to be in a 2D-array
    scaler = MinMaxScaler()
    x_train = scaler.fit_transform(x_train.reshape(x_train.shape[0] * x_train.shape[1] * x_train.shape[2], 1))
    x_test = scaler.fit_transform(x_test.reshape(x_test.shape[0] * x_test.shape[1] * x_test.shape[2], 1))

    y_train = scaler.fit_transform(y_train.reshape(y_train.shape[0] * y_train.shape[1] * y_train.shape[2], 1))
    y_test = scaler.fit_transform(y_test.reshape(y_test.shape[0] * y_test.shape[1] * y_test.shape[2], 1))

    x_train = x_train.reshape(x_train_shape[0], x_train_shape[1], x_train_shape[2], x_train_shape[3])
    x_test = x_test.reshape(x_test_shape[0], x_test_shape[1], x_test_shape[2], x_test_shape[3])
    y_train = y_train.reshape(y_train_shape[0], y_train_shape[1], y_train_shape[2], y_train_shape[3])
    y_test = y_test.reshape(y_test_shape[0], y_test_shape[1], y_test_shape[2], y_test_shape[3])

    print(x_train.shape)
    print(x_test.shape)
    print(y_train.shape)
    print(y_test.shape)

    # return x_data, y_true


create_chunks(pop_arr_10, pop_arr_14)


# Train Test Split randomly with scikit-learn
# if np.sum(x_data) = np.sum(x_data_original) + pop_dif_yearX_yearY)
# x_data = pop_arr_10
# y_true = pop_arr_14



# Create batches
# 1 batch = 100x100 cells
# batch_size = 64
# num_batches = int(round(min(x_train.shape) / batch_size))  # will always round down / floor
#
# for i in range(num_batches):
#     x_train
#     y_train
# print(num_batches)

# def next_batch(batch_size):
#     num_batches =
#     x = self.training_images[self.i:self.i + batch_size].reshape(100, 32, 32, 3)
#     y = self.training_labels[self.i:self.i + batch_size]
#     self.i = (self.i + batch_size) % len(self.training_images)



print(x_train.shape)
print(min(x_train.shape))
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






