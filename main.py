import os
import sys
import numpy as np
import tensorflow as tf
from osgeo import gdal
import osr

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
data_dir = os.path.join(base_dir, 'data')

pop_data = gdal.Open(os.path.join(data_dir, 'TGO14adjv1.tif'))

myarray = np.array(pop_data.GetRasterBand(1).ReadAsArray())
print(myarray.shape)

print(myarray.max())

print(myarray)

myarray[myarray < 0] = 0

