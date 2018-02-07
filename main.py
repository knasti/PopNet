import os
import sys
import numpy as np
from osgeo import gdal

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
data_dir = os.path.join(base_dir, 'data')

ds = gdal.Open(os.path.join(data_dir, 'TGO14adjv1.tif'))

myarray = np.array(ds.GetRasterBand(1).ReadAsArray())
print(myarray.shape)

print(myarray.max())