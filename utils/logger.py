import tensorflow as tf
import os


class Logger():
    def __init__(self, sess,config):
        self.sess = sess
        self.config = config
        self.summary_placeholders = {}
        self.summary_ops = {}
        self.train_summary_writer = tf.summary.FileWriter(os.path.join(self.config.summary_dir, "train"),
                                                          self.sess.graph)
        self.test_summary_writer = tf.summary.FileWriter(os.path.join(self.config.summary_dir, "test"))

    # it can summarize scalers and images.
    def summarize(self, step, summerizer="train", scope="", summaries_dict=None):
        """
        :param step: the step of the summary
        :param summerizer: use the train summary writer or the test one
        :param scope: variable scope
        :param summaries_dict: the dict of the summaries values (tag,value)
        :return:
        """
        summary_writer = self.train_summary_writer if summerizer == "train" else self.test_summary_writer
        with tf.variable_scope(scope):

            if summaries_dict is not None:
                summary_list = []
                for tag, value in summaries_dict.items():
                    if tag not in self.summary_ops:
                        if len(value.shape) <=1:
                            self.summary_placeholders[tag] = tf.placeholder('float32', value.shape, name=tag)
                        else :
                            self.summary_placeholders[tag] = tf.placeholder('float32', [None] + list(value.shape[1:]),name=tag)
                        if len(value.shape) <= 1:
                            self.summary_ops[tag] = tf.summary.scalar(tag, self.summary_placeholders[tag])
                        else:
                            self.summary_ops[tag] = tf.summary.image(tag, self.summary_placeholders[tag])

                    summary_list.append(self.sess.run(self.summary_ops[tag], {self.summary_placeholders[tag]: value}))

                for summary in summary_list:
                    summary_writer.add_summary(summary, step)
                summary_writer.flush()

    def log_config(self):
        # Saves the configurations for the current sub_experiment
        with open(os.path.join("../experiments", self.config.exp_name, self.config.sub_exp, "config.txt"), "a") as f:
            f.write('Experiment: ' + self.config.exp_name)
            f.write('\n')
            f.write('Sub experiment: ' + self.config.sub_exp)
            f.write('\n')
            f.write('Number of epochs: ' + str(self.config.num_epochs))
            f.write('\n')
            f.write('Learning rate: ' + str(self.config.learning_rate))
            f.write('\n')
            f.write('Batch size: ' + str(self.config.batch_size))
            f.write('\n')
            f.write('Max to keep: ' + str(self.config.max_to_keep))
            f.write('\n')
            f.write('Chunk height: ' + str(self.config.chunk_height))
            f.write('\n')
            f.write('Chunk width: ' + str(self.config.chunk_width))
            f.write('\n')