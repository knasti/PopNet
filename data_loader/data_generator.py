import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from data_loader.data_writer import DataWriter
import os
from random import randint

class DataGenerator():
    def __init__(self, config, preptraintest = None, prepdata = None):
        self.i = 0
        self.tot_i = 0
        self.i_train = 0
        self.tot_i_train = 0
        self.i_test = 0
        self.tot_i_test = 0
        self.pair_no = 0
        self.config = config
        self.preptraintest = preptraintest
        self.prepdata = prepdata

    def create_traintest_data(self):
        self.preptraintest.create_chunks()
        # self.preptraintest.input_to_tif()
        self.preptraintest.create_train_test_split()
        # self.preptraintest.normalize_data()
        self.train_data, self.train_labels, self.train_label_pop, self.num_train_batches, self.list_num_train_batches = self.preptraintest.train_batches()
        self.test_data, self.test_labels, self.test_label_pop, self.num_test_batches, self.list_num_test_batches = self.preptraintest.test_batches()

    def create_data(self):
        self.prepdata.create_chunks()
        # self.prepdata.input_to_tif()
        # self.prepdata.normalize_data()
        self.input, self.x_chunk_pop, self.batch_num, self.list_batch_num = self.prepdata.create_batches()

    def next_train_batch(self):
        train_id = self.i_train
        pair_no = self.pair_no  # determines which pair we are on (1975-1990 (0), 1990-2000 (1) or 2000-2010 (2))

        self.i_train += 1  # Will always be 1 larger than train_id, from here
        self.tot_i_train +=1  # Determines when to reset both train id and pair no (when finished with one epoch)

        # Batches in the current pair
        if self.i_train == self.list_num_train_batches[self.pair_no]:
            self.i_train = 0
            self.pair_no += 1

        # Total amount of batches
        if self.tot_i_train == self.num_train_batches:
            self.i_train = 0
            self.tot_i_train = 0
            self.pair_no = 0

        yield self.train_data[pair_no][train_id], self.train_labels[pair_no][train_id], self.preptraintest.x_proj[pair_no], self.train_label_pop[pair_no][train_id], self.preptraintest.x_cur_pop[pair_no]

    def next_big_train_batch(self):
        batch_nr = self.i_train
        self.num_train_batches = len(self.preptraintest.x_data)
        self.i_train += 1

        if self.i_train == self.num_train_batches:
            self.i_train = 0

        yield self.preptraintest.x_data[batch_nr], self.preptraintest.y_true[batch_nr], self.preptraintest.x_proj[batch_nr]

    def next_test_batch(self):
        test_id = self.i_test
        pair_no = self.pair_no  # determines which pair we are on (1975-1990 (0), 1990-2000 (1) or 2000-2010 (2))

        self.i_test += 1
        self.tot_i_test += 1

        if self.i_test == self.list_num_test_batches[pair_no]:
            self.i_test = 0
            self.pair_no += 1

        if self.tot_i_test == self.num_test_batches:
            self.i_test = 0
            self.tot_i_test = 0
            self.pair_no = 0

        yield self.test_data[pair_no][test_id], self.test_labels[pair_no][test_id], self.preptraintest.x_proj[pair_no], self.test_label_pop[pair_no][test_id], self.preptraintest.x_cur_pop[pair_no]

    def next_batch(self):
        id = self.i
        self.i += 1

        if id > self.list_batch_num[self.pair_no]:
            self.pair_no += 1
        pair_no = self.pair_no  # which pair are we on (1975-1990 (0), 1990-2000 (1) or 2000-2010 (2))

        if self.batch_num == self.i:
            self.i = 0
            self.pair_no = 0

        yield self.input[pair_no][id]


class PrepData():
    def __init__(self, config, data_loader):
        self.x_data = []
        self.x_cur_pop = []
        self.x_proj = config.pop_proj
        self.batch_size = config.batch_size
        self.chunk_height = config.chunk_height
        self.chunk_width = config.chunk_width
        self.no_features = sum(config.feature_list)
        self.output_nr = None
        self.chunk_rows = None
        self.chunk_cols = None
        self.no_chunks = None
        self.data_loader = data_loader
        self.config = config
        self.input_counter = 2010

    def create_chunks(self):
        # Runs through all of the data / label pairs
        self.offset_rows = randint(0, round(self.chunk_height / 2))
        self.offset_cols = randint(0, round(self.chunk_width / 2))
        self.row_null_cells = 0
        self.col_null_cells = 0

        for i in range(len(self.x_data)):
            # Adding extra null cells in the beginning to offset the chunks
            row_addition_list = []
            for j in range(len(self.config.feature_list)):
                if self.config.feature_list[j] == 1:
                    row_addition_feature = np.full((self.offset_rows, self.x_data[i].shape[1], 1), self.config.feature_values[j])
                    row_addition_list.append(row_addition_feature)
            row_additions = np.concatenate(row_addition_list, axis=2)
            self.x_data[i] = np.concatenate((row_additions, self.x_data[i]), axis=0)

            col_addition_list = []
            for j in range(len(self.config.feature_list)):
                if self.config.feature_list[j] == 1:
                    col_addition_feature = np.full((self.x_data[i].shape[0], self.offset_cols, 1), self.config.feature_values[j])
                    col_addition_list.append(col_addition_feature)
            col_additions = np.concatenate(col_addition_list, axis=2)
            self.x_data[i] = np.concatenate((col_additions, self.x_data[i]), axis=1)

            # INPUT DATA
            # Takes the number of rows MOD the chunk height to determine if we need to add extra rows (padding)
            rest_rows = self.x_data[i].shape[0] % self.chunk_height
            if rest_rows != 0:
                # Adds rows until the input data matches with the chunk height
                null_cells_list = []
                self.row_null_cells = self.chunk_height - rest_rows
                for j in range(len(self.config.feature_list)):
                    if self.config.feature_list[j] == 1:
                        null_cell_feature = np.full((self.row_null_cells, self.x_data[i].shape[1], 1), self.config.feature_values[j])
                        null_cells_list.append(null_cell_feature)

                null_cells = np.concatenate(null_cells_list, axis=2)
                self.x_data[i] = np.concatenate((self.x_data[i], null_cells), axis=0)
                # self.x_data[i] = np.concatenate((self.x_data[i], np.zeros((self.chunk_height - rest_rows, self.x_data[i].shape[1], self.no_features))), axis=0)
            # Takes the number of cols MOD the chunk width to determine if we need to add extra columns (padding)
            rest_cols = self.x_data[i].shape[1] % self.chunk_width
            if rest_cols != 0:
                # Adds columns until the input data matches with the chunk width
                null_cells_list = []
                self.col_null_cells = self.chunk_width - rest_cols
                for j in range(len(self.config.feature_list)):
                    if self.config.feature_list[j] == 1:
                        null_cell_feature = np.full((self.x_data[i].shape[0], self.col_null_cells, 1), self.config.feature_values[j])
                        null_cells_list.append(null_cell_feature)

                null_cells = np.concatenate(null_cells_list, axis=2)
                self.x_data[i] = np.concatenate((self.x_data[i], null_cells), axis=1)
                # self.x_data[i] = np.concatenate((self.x_data[i], np.zeros((self.x_data[i].shape[0], self.chunk_width - rest_cols, self.no_features))), axis=1)

            self.chunk_rows = int(self.x_data[i].shape[0] / self.chunk_height)
            self.chunk_cols = int(self.x_data[i].shape[1] / self.chunk_width)
            self.no_chunks = int(self.chunk_rows * self.chunk_cols)

            cur_row = 0
            cur_col = 0

            to_be_x_data = np.empty((self.no_chunks, self.chunk_height, self.chunk_width, self.no_features))

            for j in range(self.no_chunks):
                if self.chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
                    cur_row += 1
                    cur_col = 0

                x_chunk = self.x_data[i][cur_row * self.chunk_height: (cur_row + 1) * self.chunk_height,
                          cur_col * self.chunk_width: (cur_col + 1) * self.chunk_width, :]

                to_be_x_data[j, :, :, :] = x_chunk

                cur_col += 1

            to_be_x_data = to_be_x_data.reshape((self.no_chunks, self.chunk_height, self.chunk_width, self.no_features))

            self.x_data[i] = to_be_x_data

        # [number of chunks, chunk height, chunk width, number of features]

    def normalize_data(self):
        # Normalizing the data with scikit-learn, needs to be in a 2D-array
        for i in range(len(self.x_data)):
            scaler = MinMaxScaler()

            x_data = scaler.fit_transform(self.x_data[i].reshape(self.no_chunks * self.chunk_height * self.chunk_width, self.no_features))
            self.x_data[i] = x_data[i].reshape(self.no_chunks, self.chunk_height, self.chunk_width, self.no_features)  # LAST ENTRY IS NUMBER OF FEATURES

    def create_batches(self):
        x = []
        x_chunk_pop = []
        batch_num_list = []
        total_batch_num = 0
        for i in range(len(self.x_data)):
            # Create empty lists for x / y data
            x.append([])
            x_chunk_pop.append([])

            batch_num = self.no_chunks // self.batch_size
            batch_num_list.append(batch_num)
            total_batch_num += batch_num

            for j in range(batch_num):
                x[i].append(self.x_data[i][j * self.batch_size: (j + 1) * self.batch_size, :, :, :])
                batch_pop_sum = []
                batch_pop_sum_array = np.empty([self.batch_size, self.chunk_height, self.chunk_width, 1])
                for k in range(self.batch_size):
                    batch_pop_sum.append(np.sum(self.x_data[i][j * self.batch_size + k, :, :, 0]))
                    batch_pop_sum_array[k,:,:,:] = self.x_proj[self.output_nr] * (batch_pop_sum[k] / self.x_cur_pop[i]) # np.full((self.chunk_height, self.chunk_width, 1), batch_pop_sum[k])

                x[i][j] = np.concatenate((x[i][j][:,:,:,:], batch_pop_sum_array), axis=3)
                x_chunk_pop[i].append(batch_pop_sum)

        return x, x_chunk_pop, total_batch_num, batch_num_list


    # def create_big_batches(self):
    #     x = []
    #
    #     for i in range(len(self.x_data)):
    #         x[i].append
    #
    #     return self.x, self.x_proj


    def add_data(self, x_data):
        self.x_data.append(x_data)
        self.x_cur_pop.append(np.sum(x_data[:, :, 0]))

    def input_to_tif(self):
        raster = np.empty((self.chunk_rows * self.chunk_height, self.chunk_cols * self.chunk_width, self.no_features))
        datawriter = DataWriter(self.data_loader.geotif[0])

        for x_datum in self.x_data:
            cur_row = 0
            cur_col = 0
            x_datum
            for j in range(self.no_chunks):
                if self.chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
                    cur_row += 1
                    cur_col = 0
                raster[
                    cur_row
                    * self.chunk_height : (cur_row + 1)
                    * self.chunk_height,
                    cur_col * self.chunk_width : (cur_col + 1) * self.chunk_width,
                    :,
                ] = x_datum[j]


                cur_col += 1

            for j in range(self.no_features):
                input_dir = os.path.join(self.config.input_dir, 'input_{}_{}.tif'.format(self.input_counter, j + 1))
                input = raster[:, :, j]
                datawriter.write_tif_to_disk(input_dir, input)
        self.input_counter += 10

class PrepTrainTest():
    def __init__(self, config, data_loader):
        self.batch_size = config.batch_size
        self.chunk_height = config.chunk_height
        self.chunk_width = config.chunk_width
        self.no_features = sum(config.feature_list)
        self.test_size = config.test_size
        self.x_data = []
        self.x_proj = []
        self.x_cur_pop = []
        self.y_true = []
        self.x_train = []
        self.x_test = []
        self.y_train = []
        self.y_test = []
        self.no_train_chunks = []
        self.no_test_chunks = []
        self.chunk_rows = None
        self.chunk_cols = None
        self.no_chunks = None
        self.data_loader = data_loader
        self.config = config

    def create_chunks(self):
        # Runs through all of the data / label pairs
        for i in range(len(self.x_data)):
            # INPUT DATA
            # Takes the number of rows MOD the chunk height to determine if we need to add extra rows (padding)
            rest_rows = self.x_data[i].shape[0] % self.chunk_height
            if rest_rows != 0:
                # Adds rows until the input data matches with the chunk height
                null_cells_list = []
                for j in range(len(self.config.feature_list)):
                    if self.config.feature_list[j] == 1:
                        null_cell_feature = np.full((self.chunk_height - rest_rows, self.x_data[i].shape[1], 1),
                                                    self.config.feature_values[j])
                        null_cells_list.append(null_cell_feature)

                null_cells = np.concatenate(null_cells_list, axis=2)
                self.x_data[i] = np.concatenate((self.x_data[i], null_cells), axis=0)

            # Takes the number of cols MOD the chunk width to determine if we need to add extra columns (padding)
            rest_cols = self.x_data[i].shape[1] % self.chunk_width
            if rest_cols != 0:
                # Adds columns until the input data matches with the chunk width
                null_cells_list = []
                for j in range(len(self.config.feature_list)):
                    if self.config.feature_list[j] == 1:
                        null_cell_feature = np.full((self.x_data[i].shape[0], self.chunk_width - rest_cols, 1), self.config.feature_values[j])
                        null_cells_list.append(null_cell_feature)

                null_cells = np.concatenate(null_cells_list, axis=2)
                self.x_data[i] = np.concatenate((self.x_data[i], null_cells), axis=1)

            # LABEL (should give the same result as above)
            # Takes the number of rows MOD the chunk height to determine if we need to add extra rows (padding)
            rest_rows = self.y_true[i].shape[0] % self.chunk_height
            if rest_rows != 0:
                # Adds rows until the input data matches with the chunk height
                self.y_true[i] = np.concatenate((self.y_true[i], np.zeros((self.chunk_height - rest_rows, self.y_true[i].shape[1]))), axis=0)

            # Takes the number of cols MOD the chunk width to determine if we need to add extra columns (padding)
            rest_cols = self.y_true[i].shape[1] % self.chunk_width
            if rest_cols != 0:
                # Adds columns until the input data matches with the chunk width
                self.y_true[i] = np.concatenate((self.y_true[i], np.zeros((self.y_true[i].shape[0], self.chunk_height - rest_cols))), axis=1)

            self.chunk_rows = int(self.x_data[i].shape[0] / self.chunk_height)
            self.chunk_cols = int(self.x_data[i].shape[1] / self.chunk_width)
            self.no_chunks = int(self.chunk_rows * self.chunk_cols)

            cur_row = 0
            cur_col = 0

            to_be_x_data = np.empty((self.no_chunks, self.chunk_height, self.chunk_width, self.no_features))
            to_be_y_true = np.empty((self.no_chunks, self.chunk_height, self.chunk_width))
            pop_chunk = np.empty(self.no_chunks)
            for j in range(self.no_chunks):
                if self.chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
                    cur_row += 1
                    cur_col = 0

                x_chunk = self.x_data[i][cur_row * self.chunk_height: (cur_row + 1) * self.chunk_height,
                          cur_col * self.chunk_width: (cur_col + 1) * self.chunk_width, :]
                y_chunk = self.y_true[i][cur_row * self.chunk_height: (cur_row + 1) * self.chunk_height,
                          cur_col * self.chunk_width: (cur_col + 1) * self.chunk_width]

                to_be_x_data[j, :, :, :] = x_chunk

                to_be_y_true[j, :, :] = y_chunk
                pop_chunk[j] = np.sum(y_chunk)

                # y_chunk_pop = y_chunk[]


                cur_col += 1
            to_be_x_data = to_be_x_data.reshape((self.no_chunks, self.chunk_height, self.chunk_width, self.no_features))
            to_be_y_true = to_be_y_true.reshape((self.no_chunks, self.chunk_height, self.chunk_width, 1))
            self.x_data[i] = to_be_x_data
            self.y_true[i] = to_be_y_true

    def create_train_test_split(self):
        for i in range(len(self.x_data)):
            # Create lists for train / test data
            self.x_train.append([])
            self.x_test.append([])
            self.y_train.append([])
            self.y_test.append([])
            self.no_train_chunks.append([])
            self.no_test_chunks.append([])

            # Creating train test split
            self.x_train[i], self.x_test[i], self.y_train[i], self.y_test[i] = train_test_split(self.x_data[i], self.y_true[i], test_size=self.test_size, random_state=101)

            # Stores the shapes to restore them (after the normalization)
            self.no_train_chunks[i] = self.x_train[i].shape[0]
            self.no_test_chunks[i] = self.x_test[i].shape[0]

    def normalize_data(self):
        # Normalizing the data with scikit-learn, needs to be in a 2D-array
        for i in range(len(self.x_data)):
            scaler = MinMaxScaler()

            x_train = scaler.fit_transform(self.x_train[i].reshape(self.no_train_chunks[i] * self.chunk_height * self.chunk_width, self.no_features))
            x_test = scaler.fit_transform(self.x_test[i].reshape(self.no_test_chunks[i] * self.chunk_height * self.chunk_width, self.no_features))

            y_train = scaler.fit_transform(self.y_train[i].reshape(self.no_train_chunks[i] * self.chunk_height * self.chunk_width, 1))
            y_test = scaler.fit_transform(self.y_test[i].reshape(self.no_test_chunks[i] * self.chunk_height * self.chunk_width, 1))

            # Reshaping the 2D-array back into a 4D-array
            self.x_train[i] = x_train[i].reshape(self.no_train_chunks[i], self.chunk_height, self.chunk_width, self.no_features)
            self.x_test[i] = x_test[i].reshape(self.no_test_chunks[i], self.chunk_height, self.chunk_width, self.no_features)
            self.y_train[i] = y_train[i].reshape(self.no_train_chunks[i], self.chunk_height, self.chunk_width, 1)
            self.y_test[i] = y_test[i].reshape(self.no_test_chunks[i], self.chunk_height, self.chunk_width, 1)

    def train_batches(self):
        x = []
        y = []
        x_chunk_pop = []
        num_train_batch_list = []
        total_train_batches = 0
        for i in range(len(self.x_data)):
            # Create empty lists for x / y data
            x.append([])
            y.append([])
            x_chunk_pop.append([])
            num_train_batch = self.no_train_chunks[i] // self.batch_size
            num_train_batch_list.append(num_train_batch)
            total_train_batches += num_train_batch

            for j in range(num_train_batch):
                x[i].append(self.x_train[i][j * self.batch_size: (j + 1) * self.batch_size, :, :, :])
                y[i].append(self.y_train[i][j * self.batch_size: (j + 1) * self.batch_size, :, :, :])
                batch_pop_sum = []
                batch_pop_sum_array = np.empty([self.batch_size, self.chunk_height, self.chunk_width, 1])
                for k in range(self.batch_size):
                    batch_pop_sum.append(np.sum(self.x_train[i][j * self.batch_size + k, :, :, 0]))
                    batch_pop_sum_array[k,:,:,:] = self.x_proj[i] * (batch_pop_sum[k] / self.x_cur_pop[i]) # np.full((self.chunk_height, self.chunk_width, 1), batch_pop_sum[k])

                x[i][j] = np.concatenate((x[i][j][:,:,:,:], batch_pop_sum_array), axis=3)
                x_chunk_pop[i].append(batch_pop_sum)

        return x, y, x_chunk_pop, total_train_batches, num_train_batch_list

    def test_batches(self):
        x = []
        y = []
        x_chunk_pop = []
        num_test_batch_list = []
        total_test_batches = 0
        for i in range(len(self.x_data)):
            # Create empty lists for x / y data
            x.append([])
            y.append([])
            x_chunk_pop.append([])
            num_test_batch = self.no_test_chunks[i] // self.batch_size
            num_test_batch_list.append(num_test_batch)
            total_test_batches += num_test_batch

            for j in range(num_test_batch):
                x[i].append(self.x_test[i][j * self.batch_size: (j + 1) * self.batch_size, :, :, :])
                y[i].append(self.y_test[i][j * self.batch_size: (j + 1) * self.batch_size, :, :, :])
                batch_pop_sum = []
                batch_pop_sum_array = np.empty([self.batch_size, self.chunk_height, self.chunk_width, 1])
                for k in range(self.batch_size):
                    batch_pop_sum.append(np.sum(self.x_test[i][j * self.batch_size + k, :, :, 0]))
                    batch_pop_sum_array[k,:,:,:] = self.x_proj[i] * (batch_pop_sum[k] / self.x_cur_pop[i]) # np.full((self.chunk_height, self.chunk_width, 1), batch_pop_sum[k])

                x[i][j] = np.concatenate((x[i][j][:,:,:,:], batch_pop_sum_array), axis=3)
                x_chunk_pop[i].append(batch_pop_sum)

        return x, y, x_chunk_pop, total_test_batches, num_test_batch_list

    def add_data(self, x_data, y_true):
        self.x_data.append(x_data)
        self.y_true.append(y_true)
        self.x_proj.append(np.sum(y_true))
        self.x_cur_pop.append(np.sum(x_data[:,:,0]))

    def input_to_tif(self):
        raster = np.empty((self.chunk_rows * self.chunk_height, self.chunk_cols * self.chunk_width, self.no_features))
        datawriter = DataWriter(self.data_loader.geotif[0])

        for i in range(len(self.x_data)):
            cur_row = 0
            cur_col = 0
            for j in range(self.no_chunks):
                if self.chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
                    cur_row += 1
                    cur_col = 0
                self.x_data[i]
                raster[cur_row * self.chunk_height: (cur_row + 1) * self.chunk_height, cur_col * self.chunk_width: (cur_col + 1) * self.chunk_width, :] = self.x_data[i][j]

                cur_col += 1

            for j in range(self.no_features):
                input_dir = os.path.join(self.config.input_dir, 'input_{}_{}.tif'.format(i + 1, j + 1))
                input = raster[:, :, j]
                datawriter.write_tif_to_disk(input_dir, input)


