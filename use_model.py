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


# Store the values of the geotif into a np.array
pop_arr_10 = np.array(pop_data_10.GetRasterBand(1).ReadAsArray())
pop_arr_10 = np.delete(pop_arr_10, -1, axis=1) # Shape not the same as pop data from 14 and 15

pop_arr_14 = np.array(pop_data_14.GetRasterBand(1).ReadAsArray())

# Null-values (neg-values) are replaced with zeros
pop_arr_10[pop_arr_10 < 0] = 0
pop_arr_14[pop_arr_14 < 0] = 0

batch_size = 16

poph_1 = PopHelper(pop_arr_10, pop_arr_14, batch_size)

poph_1.create_chunks()
poph_1.normalize_data(train_test=False)

x_data, batch_num = poph_1.create_batches()




x = tf.placeholder(tf.float32,shape=[None, 32 * 32 * 1])
y_true = tf.placeholder(tf.float32,shape=[None, 32 * 32 * 1])

W = tf.Variable(tf.zeros([32 * 32 * 1, 32 * 32 * 1]))

b = tf.Variable(tf.zeros([32 * 32 * 1]))

# Create the Graph
y = tf.matmul(x,W) + b

saver = tf.train.Saver()

with tf.Session() as sess:
    # Restore the model
    saver.restore(sess, 'models/test_model.ckpt')
    cur_row = 0
    cur_col = 0
    final_raster = np.random.random((poph_1.no_chunks * poph_1.chunk_height, poph_1.no_chunks * poph_1.chunk_width))
    for i in range(batch_num):
        sess.run(y, feed_dict={x: x_data[i]})
        y.reshape(batch_size, poph_1.chunk_height, poph_1.chunk_width)

        for j in range(batch_size):
            if poph_1.chunk_cols % (i * batch_size) == 0:  # Change to new row
                cur_row += 1
            final_raster[cur_row * poph_1.chunk_height: (cur_row + 1) * poph_1.chunk_height, cur_col * poph_1.chunk_width: (cur_col + 1) * poph_1.chunk_width] = \
                y[j,:,:]

    print(final_raster)
    print(final_raster.shape)