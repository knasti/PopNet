import numpy as np
import os
from osgeo import gdal

class DataLoader():

    def __init__(self, data_dir, config):
        self.data_dir = data_dir
        self.no_features = config.num_features
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
            for i in range(self.no_features):
                arrays.append(np.array(pop_data.GetRasterBand(i + 1).ReadAsArray()))

            array = np.stack(arrays, axis=2)  # stacks the array on top of each other, adding a 3rd dimension (axis = 2)
            # Null-values (neg-values) are replaced with zeros
            array[array < 0] = 0
            self.arrays.append(array)

    def create_data_label_pairs(self):
        # Runs through all the files found
        for i in range(len(self.arrays)):
            try:
                # Pairs the adjacent arrays (0-1, 1-2, 2-3 etc. where (data-label)) in a new pair-list
                self.data_label_pairs.append([self.arrays[i], self.arrays[i + 1]])
            except:
                break
