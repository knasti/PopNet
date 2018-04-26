import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import osr
from osgeo import gdal

class DataWriter():

    def __init__(self, geotif, start_raster, output_raster, config):
        self.geotif = geotif
        self.start_raster = start_raster
        self.output_raster = output_raster
        self.config = config
        self.output_dir = config.output_dir

    def write_geotif(self):
        # Finds the number of outputs
        output_nr = 0
        for file in os.listdir(self.output_dir):
            if file.endswith(".tif"):
                output_nr += 1

        # Writes the predicted output
        output_tif = os.path.join(self.output_dir, 'output_{}.tif'.format(output_nr))
        output_fig = os.path.join(self.output_dir, 'output_{}.png'.format(output_nr))
        self.heatmap(output_fig, self.output_raster)
        self.write_to_disk(output_tif, self.output_raster)

        # Writes the difference between start point and predicted output
        diff_output_tif = os.path.join(self.output_dir, 'diff_output_{}.tif'.format(output_nr))
        diff_output_fig = os.path.join(self.output_dir, 'diff_output_{}.png'.format(output_nr))
        diff_output_hist = os.path.join(self.output_dir, 'diff_output_hist_{}.png'.format(output_nr))

        start_raster_padded = np.zeros(self.output_raster.shape)
        start_raster_padded[:self.start_raster.shape[0],:self.start_raster.shape[1]] = self.start_raster
        diff_raster = np.subtract(self.output_raster, start_raster_padded)
        self.heatmap(diff_output_fig, diff_raster)
        self.histogram(diff_output_hist, diff_raster)
        self.write_to_disk(diff_output_tif, diff_raster)

    def write_to_disk(self, dir, raster):
        # Picking up values reference values needed to export to geotif
        projection = osr.SpatialReference()
        projection.ImportFromWkt(self.geotif.GetProjectionRef())

        # Grab the geotransformation values
        geo_transform = self.geotif.GetGeoTransform()

        driver = gdal.GetDriverByName('GTiff')

        dst_ds = driver.Create(dir, xsize=raster.shape[1], ysize=raster.shape[0],
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
        dst_ds.GetRasterBand(1).WriteArray(raster)
        dst_ds.FlushCache()  # Write to disk.


    def heatmap(self, dir, raster):
        plt.figure()
        plot = sns.heatmap(raster)
        figure = plot.get_figure()
        figure.savefig(dir)

    def histogram(self, dir, raster):
        plt.figure()
        plot = sns.distplot(raster.ravel(), kde=False)
        figure = plot.get_figure()
        figure.savefig(dir)