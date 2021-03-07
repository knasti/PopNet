import tensorflow as tf
import os
import numpy as np


class BaseTrain:
    def __init__(self, sess, model, data, config, logger):
        self.model = model
        self.logger = logger
        self.config = config
        self.sess = sess
        self.data = data
        self.init = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
        self.sess.run(self.init)

    def train(self):
        for cur_epoch in range(self.model.cur_epoch_tensor.eval(self.sess), self.config.num_epochs + 1, 1):
            print('***** EPOCH {} *****'.format(cur_epoch))
            print('Training')
            #print('im y sum {}'.format(self.model.y_sum))
            self.train_epoch()
            # print(self.model.y_sum)
            # self.model.y_sum = 0
            #print('im y sum {}'.format(self.model.y_sum))
            if self.config.test_size > 0:
                print('Testing')
                self.test_epoch()

            self.sess.run(self.model.increment_cur_epoch_tensor)

    def train_epoch(self):
        """
        implement the logic of epoch:
        -loop ever the number of iteration in the config and call the train step
        -add any summaries you want using the summary
        """
        raise NotImplementedError

    def train_step(self):
        """
        implement the logic of the train step
        - run the tensorflow session
        - return any metrics you need to summarize
        """
        raise NotImplementedError

    def test(self):
        for _ in range(self.model.cur_epoch_tensor.eval(self.sess), 1, 1):
            self.test_epoch()
            self.sess.run(self.model.increment_cur_epoch_tensor)

    def test_epoch(self):
        """
        implement the logic of epoch:
        -loop ever the number of iteration in the config and call the test step
        -add any summaries you want using the summary
        """
        raise NotImplementedError

    def test_step(self):
        """
        implement the logic of the train step
        - run the tensorflow session
        - return any metrics you need to summarize
        """
        raise NotImplementedError