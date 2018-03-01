import os
import sys
import numpy as np
import tensorflow as tf
from osgeo import gdal
import osr
import matplotlib.pyplot as plt
from data_preparation import PrepData, PrepTrainTest

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
# plt.imshow(pop_arr_10)
# plt.show()

# Setting up the batch size
batch_size = 16

# Initalizes PopHelper object to create chunks, train & test split and normalizing the data
poph = PrepTrainTest(pop_arr_10, pop_arr_14, batch_size)

poph.create_chunks()
poph.create_train_test_split()
poph.normalize_data()

# Creating placeholders for the input data
x = tf.placeholder(tf.float32,shape=[None, 32, 32, 1])
y_true = tf.placeholder(tf.float32,shape=[None, 32, 32, 1])

# Initializing Xavier weights
W = tf.get_variable("W", shape=[32 * 32 * 1, 32 * 32 * 1], initializer=tf.contrib.layers.xavier_initializer())

# Initializing biases
b = tf.Variable(tf.zeros([32 * 32 * 1]))

# Create the Graph
# y = tf.matmul(x,W) + b

#
# padding = tf.constant([[1, 1,], [1, 1]])  # Same as [2,2] padding
# # 'constant_values' is 0.
# # rank of 't' is 2.
# tf.pad(x, padding, "CONSTANT")

conv1 = tf.layers.conv2d(
    inputs=x,
    filters=32,
    kernel_size=[5, 5],
    padding="same",
    activation=tf.nn.relu)

conv2 = tf.layers.conv2d(
    inputs=conv1,
    filters=48,
    kernel_size=[5, 5],
    padding="same",
    activation=tf.nn.relu)
# MÅSKE VI SKAL BRUGE POOLING FOR AT GÅ FRA 48 I SIDSTE DIMENSION TIL 1?
# conv2_flat = tf.reshape(conv2, [None, 32 * 32 * 48])
dense1 = tf.layers.dense(inputs=conv2, units=1024, activation=tf.nn.relu)

y = tf.layers.dense(inputs=dense1, units=1)


# TensorFlow function for root mean square error
root_mean_square_err = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(y_true, y))))

# Initializing the optimizer, that will optimize the root mean square error through backpropagation, and thus learn
optimizer = tf.train.AdamOptimizer(learning_rate=0.001)

# Tell the optimizer to use root mean square error as the cost function (the function to minimize)
train = optimizer.minimize(root_mean_square_err)

# Initialize all TensorFlow variables
init = tf.global_variables_initializer()

train_data, train_labels, num_train_batches = poph.train_batches()
test_data, test_labels, num_test_batches = poph.test_batches()

saver = tf.train.Saver()

num_epochs = 1
j = 0
counter = 0
x_axis = []
y_axis = []



# with tf.device('/gpu:'+str(GPU_INDEX)):

# Training Session
with tf.Session() as sess:
    sess.run(init)
    # convo_test_1 = sess.run(conv1, feed_dict={x: train_data[0]})
    # convo_test_2 = sess.run(conv2, feed_dict={conv1: convo_test_1})
    # dense_test_3 = sess.run(dense1, feed_dict={conv2: convo_test_2})
    # dense_test_4 = sess.run(dense2, feed_dict={dense1: dense_test_3})
    #
    # print(convo_test_1.shape)
    # print(convo_test_2.shape)
    # print(dense_test_3.shape)
    # print(dense_test_4.shape)
    for epoch in range(num_epochs):
        print('epoch number {}'.format(epoch))
        for i in range(num_train_batches):
            print(train_data)
            sess.run(train, feed_dict={x: train_data[i], y_true: train_labels[i]})
    print('yoyoyo')
    saver.save(sess, 'models/test_model.ckpt')

# plt.plot(x_axis, y_axis)
# plt.title("Root Mean Squared Error")
# plt.xlabel("Iterations")
# plt.ylabel("Error")
# plt.show()

# Test Session
with tf.Session() as sess:
    # Restore the model
    saver.restore(sess, 'models/test_model.ckpt')

    for i in range(num_test_batches):
        rmse = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(y_true, y))))
        err = sess.run(rmse, feed_dict={x: test_data[i], y_true: test_labels[i]})
        print('RMSE')
        print(err)

        print(y.shape)



    # Test the Train Model
    # rmse = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(y_true, y))))
    #
    # acc = tf.reduce_mean(tf.cast(matches, tf.float32))
    #
    # print(sess.run(rmse, feed_dict={x: mnist.test.images, y_true: mnist.test.labels}))


poph_1 = PrepData(pop_arr_10, pop_arr_14, batch_size)

poph_1.create_chunks()
poph_1.normalize_data()

x_data, batch_num = poph_1.create_batches()


# Use model to predict population cells
with tf.Session() as sess:
    # Restore the model
    saver.restore(sess, 'models/test_model.ckpt')
    cur_row = 0
    cur_col = 0
    final_raster = np.empty((poph_1.chunk_rows * poph_1.chunk_height, poph_1.chunk_cols * poph_1.chunk_width))
    for i in range(batch_num):
        y_pred = sess.run(y, feed_dict={x: x_data[i]})
        y_pred = y_pred.reshape(batch_size, poph_1.chunk_height, poph_1.chunk_width)

        for j in range(batch_size):
            if poph_1.chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
                cur_row += 1
                cur_col = 0

            final_raster[cur_row * poph_1.chunk_height: (cur_row + 1) * poph_1.chunk_height,
            cur_col * poph_1.chunk_width: (cur_col + 1) * poph_1.chunk_width] = \
                y_pred[j, :, :]

            cur_col += 1


# Calculating back to population
norm_sum = np.sum(final_raster)
final_pop = np.sum(pop_arr_14)

super_final_rast = (final_raster / norm_sum) * final_pop

print(np.max(super_final_rast))
print(np.min(super_final_rast))
print(super_final_rast.shape)



# Picking up values reference values needed to export to geotif
Projection = osr.SpatialReference()
Projection.ImportFromWkt(pop_data_14.GetProjectionRef())

geoTransform = pop_data_14.GetGeoTransform()

driver = gdal.GetDriverByName('GTiff')

dst_ds = driver.Create('test_tiff_3.tif', xsize=super_final_rast.shape[1], ysize=super_final_rast.shape[0],
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
dst_ds.GetRasterBand(1).WriteArray(super_final_rast)
dst_ds.FlushCache()  # Write to disk.










