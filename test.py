import numpy as np

x = np.random.random((16,32,32,1))
W_1 = np.random.random((16,32,32,1))
W_2 = np.random.random((1,16,32,32))

x_1 = np.random.random((16,32,32,1))
W_3 = np.random.random((32 * 32 * 1, 32 * 32 * 1))
b_3 = np.random.random((32 * 32 * 1))

x_1 = x_1.reshape(x_1.shape[0], x_1.shape[1] * x_1.shape[2] * x_1.shape[3])  # [batch_size, flattened_array]


np.add(x,W_1)
# test_result = np.matmul(x,W_2)


matrix_res = np.matmul(x_1,W_3)
matrix_add = np.add(matrix_res,b_3)


print(matrix_add.shape)
