import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


class PopHelper():

    def __init__(self, x_data, y_true, batch_size, chunk_height=32, chunk_width=32):
        self.x_data = x_data
        self.y_true = y_true
        self.batch_size = batch_size
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.chunk_height = chunk_height
        self.chunk_width = chunk_width
        self.no_train_chunks = None
        self.no_test_chunks = None
        self.no_chunks = None
        self.chunk_rows = None
        self.chunk_cols = None


    def create_chunks(self):
        # INPUT DATA
        # Takes the number of rows MOD the chunk height to determine if we need to add extra rows (padding)
        rest_rows = self.x_data.shape[0] % self.chunk_height
        if rest_rows != 0:
            # Adds rows until the input data matches with the chunk height
            self.x_data = np.r_[self.x_data, np.zeros((self.chunk_height - rest_rows, self.x_data.shape[1]))]

        # Takes the number of cols MOD the chunk width to determine if we need to add extra columns (padding)
        rest_cols = self.x_data.shape[1] % self.chunk_width
        if rest_rows != 0:
            # Adds columns until the input data matches with the chunk width
            self.x_data = np.c_[self.x_data, np.zeros((self.x_data.shape[0], self.chunk_height - rest_cols))]

        # LABEL (should give the same result as above)
        # Takes the number of rows MOD the chunk height to determine if we need to add extra rows (padding)
        rest_rows = self.y_true.shape[0] % self.chunk_height
        if rest_rows != 0:
            # Adds rows until the input data matches with the chunk height
            self.y_true = np.r_[self.y_true, np.zeros((self.chunk_height - rest_rows, self.y_true.shape[1]))]

        # Takes the number of cols MOD the chunk width to determine if we need to add extra columns (padding)
        rest_cols = self.y_true.shape[1] % self.chunk_width
        if rest_rows != 0:
            # Adds columns until the input data matches with the chunk width
            self.y_true = np.c_[self.y_true, np.zeros((self.y_true.shape[0], self.chunk_height - rest_cols))]

        self.chunk_rows = int(self.x_data.shape[0] / self.chunk_height)
        self.chunk_cols = int(self.x_data.shape[1] / self.chunk_width)
        self.no_chunks = int(self.chunk_rows * self.chunk_cols)

        # [number of chunks, chunk height, chunk width, number of features]
        self.x_data = self.x_data.reshape((self.no_chunks, self.chunk_height, self.chunk_width, 1))
        self.y_true = self.y_true.reshape((self.no_chunks, self.chunk_height, self.chunk_width, 1))

    def create_train_test_split(self):
        # Creating train test split
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x_data, self.y_true, test_size=0.3, random_state=101)

        # Stores the shapes to restore them after the normalization
        self.no_train_chunks = self.x_train.shape[0]
        self.no_test_chunks = self.x_test.shape[0]

    def normalize_data(self, train_test=True):
        # Normalizing the data with scikit-learn, needs to be in a 2D-array
        scaler = MinMaxScaler()
        if train_test:
            x_train = scaler.fit_transform(self.x_train.reshape(self.no_train_chunks * self.chunk_height * self.chunk_width, 1))
            x_test = scaler.fit_transform(self.x_test.reshape(self.no_test_chunks * self.chunk_height * self.chunk_width, 1))

            y_train = scaler.fit_transform(self.y_train.reshape(self.no_train_chunks * self.chunk_height * self.chunk_width, 1))
            y_test = scaler.fit_transform(self.y_test.reshape(self.no_test_chunks * self.chunk_height * self.chunk_width, 1))

            self.x_train = x_train.reshape(self.no_train_chunks, self.chunk_height, self.chunk_width, 1)  # LAST ENTRY IS NUMBER OF FEATURES
            self.x_test = x_test.reshape(self.no_test_chunks, self.chunk_height, self.chunk_width, 1)
            self.y_train = y_train.reshape(self.no_train_chunks, self.chunk_height, self.chunk_width, 1)
            self.y_test = y_test.reshape(self.no_test_chunks, self.chunk_height, self.chunk_width, 1)

        if not train_test:
            x_data = scaler.fit_transform(self.x_data.reshape(self.no_chunks * self.chunk_height * self.chunk_width, 1))
            self.x_data = x_data.reshape(self.no_chunks, self.chunk_height, self.chunk_width, 1)  # LAST ENTRY IS NUMBER OF FEATURES

    def train_batches(self):
        num_train_batch = self.no_train_chunks // self.batch_size
        x = []
        y = []

        for i in range(num_train_batch):
            x.append(self.x_train[i * self.batch_size:(i + 1) * self.batch_size, :, :, :])
            y.append(self.y_train[i * self.batch_size:(i + 1) * self.batch_size, :, :, :])

            # Flattening the np.array
            x[i] = x[i].reshape(x[i].shape[0], x[i].shape[1] * x[i].shape[2] * x[i].shape[3])
            y[i] = y[i].reshape(y[i].shape[0], y[i].shape[1] * y[i].shape[2] * y[i].shape[3])

        return x, y, num_train_batch

    def test_batches(self):
        num_test_batch = self.no_test_chunks // self.batch_size
        x = []
        y = []

        for i in range(num_test_batch):
            x.append(self.x_test[i * self.batch_size:(i + 1) * self.batch_size, :, :, :])
            y.append(self.y_test[i * self.batch_size:(i + 1) * self.batch_size, :, :, :])

            # Flattening the np.array
            x[i] = x[i].reshape(x[i].shape[0], x[i].shape[1] * x[i].shape[2] * x[i].shape[3])
            y[i] = y[i].reshape(y[i].shape[0], y[i].shape[1] * y[i].shape[2] * y[i].shape[3])

        return x, y, num_test_batch

    def create_batches(self):
        batch_num = self.no_chunks // self.batch_size
        x = []
        for i in range(batch_num):
            x.append(self.x_data[i * self.batch_size: (i + 1) * self.batch_size, :, :, :])
            if i == 9:
                print('whjat')
            # Flattening the np.array
            x[i] = x[i].reshape(x[i].shape[0], x[i].shape[1] * x[i].shape[2] * x[i].shape[3])

        return x, batch_num