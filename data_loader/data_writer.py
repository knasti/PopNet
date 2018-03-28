import numpy as np
import os
import osr
from osgeo import gdal

class DataWriter():

    def __init__(self, geotif, raster, config):
        self.geotif = geotif
        self.raster = raster
        self.config = config
        self.output_dir = config.output_dir



    def write_geotif(self):
        # Finds the number of outputs
        output_nr = 0
        for file in os.listdir(self.output_dir):
            if file.endswith(".tif"):
                output_nr += 1

        output = os.path.join(self.output_dir, 'output_{}.tif'.format(output_nr))

        # Picking up values reference values needed to export to geotif
        projection = osr.SpatialReference()
        projection.ImportFromWkt(self.geotif.GetProjectionRef())

        # Grab the geotransformation values
        geo_transform = self.geotif.GetGeoTransform()

        driver = gdal.GetDriverByName('GTiff')

        dst_ds = driver.Create(output, xsize=self.raster.shape[1], ysize=self.raster.shape[0],
                               bands=1, eType=gdal.GDT_Float32)

        dst_ds.SetGeoTransform((
            geo_transform[0],  # x_min
            geo_transform[1],  # pixel width
            geo_transform[2],  # rotation
            geo_transform[3],  # y_max
            geo_transform[4],  # rotation
            geo_transform[5]  # pixel height
        ))

        dst_ds.SetProjection(projection.ExportToWkt())
        dst_ds.GetRasterBand(1).WriteArray(self.raster)
        dst_ds.FlushCache()  # Write to disk.