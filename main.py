import numpy as np
from osgeo import gdal


ds = gdal.Open(r'C:\Users\DKNIBA_la\Aalborg Universitet\Thomas Breilev Lindgreen - 10.Semester - Kandidat\Data\worldpop\Togo 100m Population\TGO10adjv4.tif')
myarray = np.array(ds.GetRasterBand(1).ReadAsArray())
print(myarray.shape)

print(myarray.max())