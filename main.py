import os
import sys
import numpy as np
import tensorflow as tf
from osgeo import gdal
import osr
import matplotlib.pyplot as plt
from data_preparation import PopHelper

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

batch_size = 16

poph = PopHelper(pop_arr_10, pop_arr_14, batch_size)

poph.create_chunks()


x = tf.placeholder(tf.float32,shape=[None, 32 * 32 * 1])
y_true = tf.placeholder(tf.float32,shape=[None, 32 * 32 * 1])

W = tf.Variable(tf.zeros([32 * 32 * 1, 32 * 32 * 1]))

b = tf.Variable(tf.zeros([32 * 32 * 1]))

# Create the Graph
y = tf.matmul(x,W) + b

root_mean_square_err = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(y_true, y))))

optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.5)

train = optimizer.minimize(root_mean_square_err)
init = tf.global_variables_initializer()

train_data, train_labels = poph.train_batches()
test_data, test_labels = poph.test_batches()

with tf.Session() as sess:
    sess.run(init)

    # Train the model for 1000 steps on the training set
    # Using built in batch feeder from mnist for convenience
    steps = 1000
    for i in range(len(train_data)):
        train_data[i] = train_data[i].reshape(train_data[i].shape[0], train_data[i].shape[1] * train_data[i].shape[2] * train_data[i].shape[3])
        train_labels[i] = train_labels[i].reshape(train_labels[i].shape[0], train_labels[i].shape[1] * train_labels[i].shape[2] * train_labels[i].shape[3])
        sess.run(train, feed_dict={x: train_data[i], y_true: train_labels[i]})

        # PRINT OUT A MESSAGE EVERY 100 STEPS
        if i % 100 == 0:
            print('Currently on step {}'.format(i))
            print('Accuracy is:')
            # Test the Train Model
            rmse = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(y_true, y))))

            test_data[i] = test_data[i].reshape(test_data[i].shape[0], test_data[i].shape[1] * test_data[i].shape[2] * test_data[i].shape[3])
            test_labels[i] = test_labels[i].reshape(test_labels[i].shape[0], test_labels[i].shape[1] * test_labels[i].shape[2] * test_labels[i].shape[3])

            print(sess.run(rmse, feed_dict={x: test_data[i], y_true: test_labels[i]}))

            print(rmse)


    # Test the Train Model
    # rmse = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(y_true, y))))
    #
    # acc = tf.reduce_mean(tf.cast(matches, tf.float32))
    #
    # print(sess.run(rmse, feed_dict={x: mnist.test.images, y_true: mnist.test.labels}))

    steps




print(x.shape)
print(y.shape)

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


#
# print(x_train.shape)
# print(min(x_train.shape))
# print(x_test.shape)
# print(y_train.shape)
# print(y_test.shape)


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






