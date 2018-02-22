from base.base_train import BaseTrain
from tqdm import tqdm
import numpy as np


class TemplateTrainer(BaseTrain):
    def __init__(self, sess, model, data, config, logger):
        super(TemplateTrainer, self).__init__(sess, model, data, config, logger)

    def train_epoch(self):
        num_batches = tqdm(range(self.config.num_iter_per_epoch))
        losses=[]

        for i in num_batches:
            loss, acc = self.train_step()
            losses.append(loss)

        loss=np.mean(losses)


        cur_it = self.model.global_step_tensor.eval(self.sess)
        summaries_dict = {}
        summaries_dict['loss'] = loss
        summaries_dict['acc'] = acc
        self.logger.summarize(cur_it, summaries_dict=summaries_dict)
        self.model.save(self.sess)

    def train_step(self):
        batch_x, batch_y = next(self.data.next_batch(self.config.batch_size))
        feed_dict = {self.model.x: batch_x, self.model.y: batch_y, self.model.is_training: True}
        _, loss = self.sess.run([self.model.train_step, self.model.root_mean_square_err],
                                     feed_dict=feed_dict)
        return loss
