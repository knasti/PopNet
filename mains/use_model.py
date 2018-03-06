import tensorflow as tf
import os
from osgeo import gdal
import osr
import sys
import numpy as np

from data_loader.data_generator import DataGenerator, PrepData, PrepTrainTest
from data_loader.data_loader import DataLoader
from data_loader.data_writer import DataWriter
from models.pop_model import PopModel
from trainers.pop_trainer import PopTrainer
from utils.config import process_config
from utils.dirs import create_dirs
from utils.logger import Logger
from utils.utils import get_args

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
data_dir = os.path.relpath('..\\data', base_dir)
config_dir = os.path.relpath('..\\configs', base_dir)

def main():
    # capture the config path from the run arguments
    # then process the json configration file
    # try:
    args = get_args()
    if args.config != 'None':
        config = process_config(args.config)
    else:
        config = process_config(os.path.join(config_dir, 'example.json'))

    data_loader = DataLoader(data_dir)
    data_loader.load_directory('.tif')
    data_loader.create_np_arrays()

    preptt = PrepTrainTest(data_loader.arrays[0], data_loader.arrays[1], config.batch_size, config.chunk_height, config.chunk_width)
    prepd = PrepData(data_loader.arrays[0], data_loader.arrays[1], config.batch_size, config.chunk_height, config.chunk_width)

    # create the experiments output dir
    create_dirs([config.output_dir])

    # create tensorflow session
    sess = tf.Session()
    # create instance of the model you want
    model = PopModel(config)
    #load model if exist
    model.load(sess)
    # create your data generator
    data = DataGenerator(config, preptt, prepd)

    data.create_data()

    with sess:
        # Restore the model
        cur_row = 0
        cur_col = 0

        chunk_height = data.prepdata.chunk_height
        chunk_width = data.prepdata.chunk_width

        chunk_rows = data.prepdata.chunk_rows
        chunk_cols = data.prepdata.chunk_cols

        final_raster = np.empty((chunk_rows * chunk_height, chunk_cols * chunk_width))
        for i in range(data.batch_num):
            y_pred = sess.run(model.y, feed_dict={model.x: data.input[i]})
            y_pred = y_pred.reshape(config.batch_size, chunk_height, chunk_width)

            for j in range(config.batch_size):
                if chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
                    cur_row += 1
                    cur_col = 0

                final_raster[cur_row * chunk_height: (cur_row + 1) * chunk_height, cur_col * chunk_width: (cur_col + 1) * chunk_width] = \
                    y_pred[j, :, :]

                cur_col += 1

    # Calculating back to population
    # norm_sum = np.sum(final_raster)
    # final_pop = np.sum(pop_arr_14)
    #
    # final_raster = (final_raster / norm_sum) * final_pop

    print(np.max(final_raster))
    print(np.min(final_raster))
    print(final_raster.shape)

    data_writer = DataWriter(data_loader.geotif[0], final_raster, config.output_dir)
    data_writer.write_geotif()


    # # Picking up values reference values needed to export to geotif
    # Projection = osr.SpatialReference()
    # Projection.ImportFromWkt(pop_data_14.GetProjectionRef())
    #
    # geoTransform = pop_data_14.GetGeoTransform()
    #
    # driver = gdal.GetDriverByName('GTiff')
    #
    # dst_ds = driver.Create('test_tiff_3.tif', xsize=final_raster.shape[1], ysize=final_raster.shape[0],
    #                        bands=1, eType=gdal.GDT_Float32)
    #
    # dst_ds.SetGeoTransform((
    #     geoTransform[0],  # x_min
    #     geoTransform[1],  # pixel width
    #     geoTransform[2],  # rotation
    #     geoTransform[3],  # y_max
    #     geoTransform[4],  # rotation
    #     geoTransform[5]  # pixel height
    # ))
    #
    # dst_ds.SetProjection(Projection.ExportToWkt())
    # dst_ds.GetRasterBand(1).WriteArray(final_raster)
    # dst_ds.FlushCache()  # Write to disk.
    #


if __name__ == '__main__':
    main()