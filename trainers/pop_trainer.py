from base.base_train import BaseTrain
from tqdm import tqdm
import numpy as np



class PopTrainer(BaseTrain):
    def __init__(self, sess, model, data, config, logger):
        super(PopTrainer, self).__init__(sess, model, data, config, logger)

    def train_epoch(self):
        num_batches = tqdm(range(len(self.data.preptraintest.x_data))) # self.data.num_train_batches
        pop_losses = []
        root_losses = []
        losses = []

        for i in num_batches:
            pop_loss, root_loss, loss = self.train_step()
            pop_losses.append(pop_loss)
            root_losses.append(root_loss)
            losses.append(loss)
        pop_loss = np.mean(pop_losses)
        root_loss = np.mean(root_losses)
        loss = np.mean(losses)

        cur_it = self.model.global_step_tensor.eval(self.sess)
        print('im train cur_it {}'.format(cur_it))
        summaries_dict = {}
        summaries_dict['pop_loss'] = pop_loss
        summaries_dict['root_loss'] = root_loss
        summaries_dict['loss'] = loss

        self.logger.summarize(cur_it, summaries_dict=summaries_dict)
        self.model.save(self.sess)


    def train_step(self):
        batch_x, batch_y, x_proj = next(self.data.next_big_train_batch())
        # batch_x, batch_y, x_proj = next(self.data.next_train_batch())
        #print(self.model.y_sum)
        feed_dict = {self.model.x: batch_x, self.model.y_true: batch_y, self.model.x_proj: x_proj, self.model.is_training: True}
        pop_loss, root_loss, _, loss = self.sess.run([self.model.pop_total_err, self.model.root_mean_square_err, self.model.train_step, self.model.loss_func],
                                     feed_dict=feed_dict)

        print('im pop error: {}'.format(pop_loss))
        print('im root error: {}'.format(root_loss))

        return pop_loss, root_loss, loss

    def test_epoch(self):
        num_batches = tqdm(range(self.data.num_test_batches))
        losses=[]

        for _ in num_batches:
            loss = self.test_step()
            losses.append(loss)

        loss=np.mean(losses)

        cur_it = self.model.global_step_tensor.eval(self.sess)
        print('im test cur_it {}'.format(cur_it))
        summaries_dict = {}
        summaries_dict['loss'] = loss

        self.logger.summarize(cur_it, summerizer="test", summaries_dict=summaries_dict)

    def test_step(self):
        batch_x, batch_y = next(self.data.next_test_batch())
        feed_dict = {self.model.x: batch_x, self.model.y_true: batch_y, self.model.is_training: False}
        _, loss = self.sess.run([self.model.train_step, self.model.root_mean_square_err],
                                     feed_dict=feed_dict)
        return loss

