import numpy as np
import os
from osgeo import gdal

class DataLoader():

    def __init__(self, data_dir, config):
        self.data_dir = data_dir
        self.no_features = sum(config.feature_list)
        self.feature_list = config.feature_list
        self.files = []
        self.arrays = []
        self.geotif = []
        self.data_label_pairs = []

    def load_directory(self, ext):
        for file in os.listdir(self.data_dir):
            if file.endswith(ext):
                # Stores the file without extension
                self.files.append(os.path.splitext(file)[0])

                print(os.path.join(self.data_dir, file))

        # Turning all the string-values into integers
        self.files = [int(file) for file in self.files]

        # Sorts the file in ascending order based on the year
        self.files = sorted(self.files, key=int)

        # Turns the integers back into string values with extensions
        self.files = [str(file) + ext for file in self.files]

    def create_np_arrays(self):
        for file in self.files:
            pop_data = gdal.Open(os.path.join(self.data_dir, file))
            self.geotif.append(pop_data)
            arrays = []
            for i in range(len(self.feature_list)):
                if self.feature_list[i] == 1:
                    if i == 0:  # Makes sure outliers are dealt with
                        pop_array = np.array(pop_data.GetRasterBand(i + 1).ReadAsArray())
                        pop_array[pop_array > 10000] = 10
                        arrays.append(pop_array)
                    else:
                        arrays.append(np.array(pop_data.GetRasterBand(i + 1).ReadAsArray()))

            # arrays[0][arrays[0] > 10000] = arrays[0] / 1000
            array = np.stack(arrays, axis=2)  # stacks the array on top of each other, adding a 3rd dimension (axis = 2)
            print('Min value pop: {}'.format(np.amin(arrays[0])))
            print('Max value pop: {}'.format(np.amax(arrays[0])))
            print('Min value water: {}'.format(np.amin(arrays[1])))
            print('Max value water: {}'.format(np.amax(arrays[1])))
            print('Min value road: {}'.format(np.amin(arrays[2])))
            print('Max value road: {}'.format(np.amax(arrays[2])))

            # Null-values (neg-values) are replaced with zeros
            # array[array < 0] = 0
            self.arrays.append(array)

        # for i in range(len(arrays)):
        #
        #     pop_difference = np.sum(arrays[i + 1][0]) - np.sum(arrays[i][0])
        #     print('im pop dif {}'.format(pop_difference))


    def create_data_label_pairs(self):
        # Runs through all the files found
        for i in range(len(self.arrays)):
            try:
                # Pairs the adjacent arrays (0-1, 1-2, 2-3 etc. where (data-label)) in a new pair-list
                self.data_label_pairs.append([self.arrays[i], self.arrays[i + 1]])
            except:
                break
