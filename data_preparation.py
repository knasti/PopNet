import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

class PrepData():
    def __init__(self, x_data, y_true, batch_size, chunk_height=32, chunk_width=32):
        self.x_data = x_data
        self.y_true = y_true
        self.batch_size = batch_size
        self.chunk_height = chunk_height
        self.chunk_width = chunk_width
        self.chunk_rows = None
        self.chunk_cols = None
        self.no_chunks = None

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

        print(self.x_data.shape)

        cur_row = 0
        cur_col = 0

        to_be_x_data = np.empty((self.no_chunks, self.chunk_height, self.chunk_width))
        to_be_y_true = np.empty((self.no_chunks, self.chunk_height, self.chunk_width))

        for i in range(self.no_chunks):
            if self.chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
                cur_row += 1
                cur_col = 0

            x_chunk = self.x_data[cur_row * self.chunk_height: (cur_row + 1) * self.chunk_height,
                      cur_col * self.chunk_width: (cur_col + 1) * self.chunk_width]
            y_chunk = self.y_true[cur_row * self.chunk_height: (cur_row + 1) * self.chunk_height,
                      cur_col * self.chunk_width: (cur_col + 1) * self.chunk_width]

            to_be_x_data[i, :, :] = x_chunk
            to_be_y_true[i, :, :] = y_chunk

            cur_col += 1
        to_be_x_data.reshape((self.no_chunks, self.chunk_height, self.chunk_width, 1))
        to_be_y_true.reshape((self.no_chunks, self.chunk_height, self.chunk_width, 1))
        self.x_data = to_be_x_data
        self.y_true = to_be_y_true

        # [number of chunks, chunk height, chunk width, number of features]



    def normalize_data(self):
        # Normalizing the data with scikit-learn, needs to be in a 2D-array
        scaler = MinMaxScaler()

        x_data = scaler.fit_transform(self.x_data.reshape(self.no_chunks * self.chunk_height * self.chunk_width, 1))
        self.x_data = x_data.reshape(self.no_chunks, self.chunk_height, self.chunk_width, 1)  # LAST ENTRY IS NUMBER OF FEATURES


    def create_batches(self):
        batch_num = self.no_chunks // self.batch_size
        x = []
        for i in range(batch_num):
            print(self.x_data.shape)
            x.append(self.x_data[i * self.batch_size: (i + 1) * self.batch_size, :, :, :])

        return x, batch_num

class PrepTrainTest():
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
        self.chunk_rows = None
        self.chunk_cols = None
        self.no_chunks = None

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

        cur_row = 0
        cur_col = 0

        to_be_x_data = np.empty((self.no_chunks, self.chunk_height, self.chunk_width))
        to_be_y_true = np.empty((self.no_chunks, self.chunk_height, self.chunk_width))

        for i in range(self.no_chunks):
            if self.chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
                cur_row += 1
                cur_col = 0

            x_chunk = self.x_data[cur_row * self.chunk_height: (cur_row + 1) * self.chunk_height,
                      cur_col * self.chunk_width: (cur_col + 1) * self.chunk_width]
            y_chunk = self.y_true[cur_row * self.chunk_height: (cur_row + 1) * self.chunk_height,
                      cur_col * self.chunk_width: (cur_col + 1) * self.chunk_width]

            to_be_x_data[i, :, :] = x_chunk
            to_be_y_true[i, :, :] = y_chunk

            cur_col += 1
        to_be_x_data.reshape((self.no_chunks, self.chunk_height, self.chunk_width, 1))
        to_be_y_true.reshape((self.no_chunks, self.chunk_height, self.chunk_width, 1))
        self.x_data = to_be_x_data
        self.y_true = to_be_y_true

    def create_train_test_split(self):
        # Creating train test split
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x_data, self.y_true, test_size=0.3, random_state=101)

        # Stores the shapes to restore them after the normalization
        self.no_train_chunks = self.x_train.shape[0]
        self.no_test_chunks = self.x_test.shape[0]

    def normalize_data(self):
        # Normalizing the data with scikit-learn, needs to be in a 2D-array
        scaler = MinMaxScaler()

        x_train = scaler.fit_transform(self.x_train.reshape(self.no_train_chunks * self.chunk_height * self.chunk_width, 1))
        x_test = scaler.fit_transform(self.x_test.reshape(self.no_test_chunks * self.chunk_height * self.chunk_width, 1))

        y_train = scaler.fit_transform(self.y_train.reshape(self.no_train_chunks * self.chunk_height * self.chunk_width, 1))
        y_test = scaler.fit_transform(self.y_test.reshape(self.no_test_chunks * self.chunk_height * self.chunk_width, 1))

        # Reshaping the 2D-array back into a 4D-array
        self.x_train = x_train.reshape(self.no_train_chunks, self.chunk_height, self.chunk_width, 1)
        self.x_test = x_test.reshape(self.no_test_chunks, self.chunk_height, self.chunk_width, 1)
        self.y_train = y_train.reshape(self.no_train_chunks, self.chunk_height, self.chunk_width, 1)
        self.y_test = y_test.reshape(self.no_test_chunks, self.chunk_height, self.chunk_width, 1)

    def train_batches(self):
        num_train_batch = self.no_train_chunks // self.batch_size
        x = []
        y = []

        for i in range(num_train_batch):
            x.append(self.x_train[i * self.batch_size:(i + 1) * self.batch_size, :, :, :])
            y.append(self.y_train[i * self.batch_size:(i + 1) * self.batch_size, :, :, :])

        return x, y, num_train_batch

    def test_batches(self):
        num_test_batch = self.no_test_chunks // self.batch_size
        x = []
        y = []

        for i in range(num_test_batch):
            x.append(self.x_test[i * self.batch_size: (i + 1) * self.batch_size, :, :, :])
            y.append(self.y_test[i * self.batch_size: (i + 1) * self.batch_size, :, :, :])

        return x, y, num_test_batch

