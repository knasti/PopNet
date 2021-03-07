import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import osr
import pandas as pd
from osgeo import gdal

class DataWriter():

    def __init__(self, geotif, start_raster=None, prev_raster=None, output_raster=None, config=None):
        self.geotif = geotif
        self.start_raster = start_raster
        self.output_raster = output_raster
        self.prev_raster = prev_raster
        self.config = config


    def write_outputs(self):
        # Finds the number of outputs
        output_nr = 2020 + sum(
            10
            for file in os.listdir(self.config.output_pred_dir)
            if file.endswith(".tif")
        )

        # Writes the predicted output
        output_tif = os.path.join(self.config.output_pred_dir, 'pred_{}.tif'.format(output_nr))
        output_fig = os.path.join(self.config.output_pred_dir, 'pred_heat_{}.png'.format(output_nr))
        output_log = os.path.join(self.config.output_dir, 'log.txt'.format(output_nr))
        self.heatmap(output_fig, self.output_raster)
        self.write_tif_to_disk(output_tif, self.output_raster)
        self.write_log(output_log, output_nr, self.output_raster)

        # Writes the difference between start point and predicted output
        diff_output_tif = os.path.join(self.config.output_dif_dir, 'diff_{}.tif'.format(output_nr))
        diff_output_fig = os.path.join(self.config.output_dif_dir, 'diff_heat_{}.png'.format(output_nr))
        diff_output_hist = os.path.join(self.config.output_dif_dir, 'diff_hist_{}.png'.format(output_nr))

        start_raster_padded = np.zeros(self.output_raster.shape)
        start_raster_padded[:self.start_raster.shape[0],:self.start_raster.shape[1]] = self.start_raster
        diff_raster = np.subtract(self.output_raster, start_raster_padded)
        self.heatmap(diff_output_fig, diff_raster)
        self.histogram(diff_output_hist, diff_raster)
        self.write_tif_to_disk(diff_output_tif, diff_raster)

        # Writes the difference between start point and predicted output
        diff_prev_output_tif = os.path.join(self.config.output_dif_dir, 'diff_prev_{}.tif'.format(output_nr))
        diff_prev_output_fig = os.path.join(self.config.output_dif_dir, 'diff_prev_heat_{}.png'.format(output_nr))
        diff_prev_output_hist = os.path.join(self.config.output_dif_dir, 'diff_prev_hist_{}.png'.format(output_nr))

        prev_raster_padded = np.zeros(self.output_raster.shape)
        prev_raster_padded[:self.prev_raster.shape[0],:self.prev_raster.shape[1]] = self.prev_raster
        prev_diff_raster = np.subtract(self.output_raster, prev_raster_padded)
        self.heatmap(diff_prev_output_fig, prev_diff_raster)
        self.histogram(diff_prev_output_hist, prev_diff_raster)
        self.write_tif_to_disk(diff_prev_output_tif, prev_diff_raster)

    def write_tif_to_disk(self, dir, raster):
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
        plot = sns.heatmap(raster, cmap="YlOrRd_r", yticklabels=False, xticklabels=False)
        figure = plot.get_figure()
        figure.savefig(dir)
        plt.clf()
        plt.close()

    def histogram(self, dir, raster):
        plt.figure()
        plot = sns.distplot(raster.ravel(), kde=False)
        plt.xlabel('Population Difference')
        plt.ylabel('No. of cells')
        figure = plot.get_figure()
        figure.savefig(dir)
        plt.clf()
        plt.close()

    def write_log(self, dir, output_nr, raster):
        with open(dir, 'a') as f:
            f.write('Year {}'.format(output_nr))
            f.write('\n')
            f.write('Min value pop: {}'.format(np.amin(raster)))
            f.write('\n')
            f.write('Max value pop: {}'.format(np.amax(raster)))
            f.write('\n')
            f.write('Sum value pop: {}'.format(np.sum(raster)))
            f.write('\n')
            f.write('\n')

