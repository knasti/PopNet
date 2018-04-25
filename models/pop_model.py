from base.base_model import BaseModel
import tensorflow as tf
import numpy as np


class PopModel(BaseModel):
    def __init__(self, config):
        super(PopModel, self).__init__(config)
        # call the build_model and init_saver functions.
        self.build_model()
        self.init_saver()


    def build_model(self):
        # Network placeholders
        self.is_training = tf.placeholder(tf.bool)

        self.x = tf.placeholder(tf.float32, shape=[self.config.batch_size, self.config.chunk_height, self.config.chunk_width, self.config.num_features + 1], name='x')
        self.x_pop_chunk = tf.placeholder(tf.float32, shape=self.config.batch_size, name='x_pop_chunk')  # sum of population in chunks
        self.x_cur_pop = tf.placeholder(tf.float32, name='x_cur_pop')  # sum of all population in current year
        self.x_proj = tf.placeholder(tf.float32, name='x_proj')  # projection of population in year to come
        self.y_true = tf.placeholder(tf.float32, shape=[self.config.batch_size, self.config.chunk_height, self.config.chunk_width, 1], name='y_true')

        # Network architecture
        conv1 = tf.layers.conv2d(
            inputs=self.x,
            filters=6,
            kernel_size=[7, 7], # [filter height, filter width]
            strides=(1, 1),
            padding="same",
            activation=tf.nn.relu,
            name='convolution_1')

        norm1 = tf.nn.local_response_normalization(
            conv1,
            depth_radius=5,
            bias=1,
            alpha=1,
            beta=0.5,
            name='normalization_1')

        # pool1 = tf.nn.max_pool(conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],

        conv2 = tf.layers.conv2d(
            inputs=conv1,
            filters=6,
            kernel_size=[5, 5],
            strides=(1, 1),
            padding="same",
            activation=tf.nn.relu,
            name='convolution_2')

        norm2 = tf.nn.local_response_normalization(
            conv2,
            depth_radius=5,
            bias=1,
            alpha=1,
            beta=0.5,
            name='normalization_2')

        dense1 = tf.layers.dense(inputs=conv2, units=32, activation=tf.nn.relu, name='dense_1')

        # dropout = tf.layers.dropout(dense1, rate=self.config.dropout, training=self.is_training)

        self.y = tf.layers.dense(inputs=dense1, units=1, name='y')

        self.y_chunk = tf.abs(tf.subtract(tf.reduce_sum(self.y, axis=0), tf.multiply(self.x_proj, tf.divide(self.x_pop_chunk, self.x_cur_pop))))

        # y_sum = tf.Variable(0)
        #
        # y_sum = tf.add(y_sum, tf.cast(tf.reduce_sum(self.y), tf.int32))
        #
        # y_sum = tf.Variable(y_sum,)

        # self.y_sum = tf.Print(self.y_sum, [self.y_sum], message="This is y_sum: ")
        #
        # b = tf.add(self.y_sum, self.y_sum)

        def absolute_mean_err():
            return tf.reduce_mean(tf.abs(tf.subtract(self.y_true, self.y)))
        def neg_value_err():
            return 10000.0


        with tf.name_scope("pop_tot_loss"):
            #self.pop_total_err = tf.abs(tf.subtract(self.x_proj, tf.reduce_sum(self.y)))
            #self.pop_total_err = tf.div(tf.abs(tf.subtract(self.x_proj, tf.reduce_sum(self.y))), tf.cast(tf.size(self.y), tf.float32)) # 573440)
            #label_pop = tf.divide(self.y_pop, self.x_proj)
            #pred_pop = tf.divide(tf.reduce_sum(self.y, axis=0), self.x_proj)
            #self.pop_total_err = tf.reduce_mean(tf.abs(tf.subtract(self.y_pop, tf.reduce_sum(self.y, axis=0))))
            #chunk_pred = tf.reduce_sum(self.y, axis=0)
            chunk_height = tf.cast(self.config.chunk_height, dtype='float32')
            chunk_width = tf.cast(self.config.chunk_width, dtype='float32')
            #chunk_y = tf.divide(tf.multiply(self.x_proj, tf.divide(self.x_pop_chunk, self.x_cur_pop)), tf.multiply(chunk_height, chunk_width))
            self.pop_total_err = tf.divide(self.y_chunk, tf.multiply(chunk_height, chunk_width))
        with tf.name_scope("pop_cell_loss"):
            #self.root_mean_square_err = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(self.y_true, self.y))))
            self.mean_absolute_err = tf.reduce_mean(tf.abs(tf.subtract(self.y_true, self.y)))
            #self.mean_absolute_err = tf.cond(tf.greater_equal(tf.reduce_mean(self.y), 0), absolute_mean_err, neg_value_err)
            # mean_absolute_err = tf.get_variable("mean_absolute_err", constraint = lambda x: tf.clip_by_value(x, 0, np.infty))
            # self.mean_absolute_err = mean_absolute_err

            # self.mean_absolute_err = tf.reduce_mean(tf.abs(tf.subtract(self.y_true, self.y)))

        with tf.name_scope("loss"):
            # Cost function
            # pop_total_err = tf.div(tf.abs(tf.subtract(self.x_proj, tf.reduce_sum(self.y))), tf.size(self.y))

            # MANGLER AT DIVIDE POP_TOTAL_ERR med antallet af celler
            # TensorFlow function for root mean square error

            self.loss_func = tf.add(tf.multiply(0.5, self.mean_absolute_err), tf.multiply(0.5, self.pop_total_err))

            # Initializing the optimizer, that will optimize the root mean square error through backpropagation, and thus learn
            self.train_step = tf.train.AdamOptimizer(self.config.learning_rate).minimize(self.loss_func,
                                                                                   global_step=self.global_step_tensor)

        with tf.name_scope("y_sum"):
            # tf.Print(self.y_sum, [self.y_sum])
            # a = tf.add(self.y_sum, self.y_sum)

            self.y_sum += tf.reduce_sum(self.y)

    def init_saver(self):
        #here you initalize the tensorflow saver that will be used in saving the checkpoints.
        self.saver = tf.train.Saver(max_to_keep=self.config.max_to_keep)