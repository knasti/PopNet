import numpy as np
import os
from osgeo import gdal

class DataLoader():

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.files = []
        self.arrays = []
        self.geotif = []

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
            array = np.array(pop_data.GetRasterBand(1).ReadAsArray())
            # Null-values (neg-values) are replaced with zeros
            array[array < 0] = 0
            self.arrays.append(array)

