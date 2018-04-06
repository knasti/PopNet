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
config_dir = os.path.relpath('..\\configs', base_dir)
args = get_args()

if args.config != 'None':
    config = process_config(args.config)
else:
    config = process_config(os.path.join(config_dir, 'config.json'))

data_dir = os.path.relpath('..\\data\\{}'.format(config.exp_name), base_dir)

def main():
    data_loader = DataLoader(data_dir, config)
    data_loader.load_directory('.tif')
    data_loader.create_np_arrays()

    prepd = PrepData(config)

    prepd.add_data(data_loader.arrays[-1])

    # Create the experiments output dir
    create_dirs([config.output_dir])

    # Create tensorflow session
    sess = tf.Session()

    # Create instance of the model
    model = PopModel(config)

    # Load model if exist
    model.load(sess)

    # Create data generator
    data = DataGenerator(config, prepdata = prepd)

    rasters = []

    with sess:
        for i in range(config.num_outputs):
            data.create_data()

            cur_row = 0
            cur_col = 0

            chunk_height = data.prepdata.chunk_height
            chunk_width = data.prepdata.chunk_width

            chunk_rows = data.prepdata.chunk_rows
            chunk_cols = data.prepdata.chunk_cols

            output_raster = np.empty((chunk_rows * chunk_height, chunk_cols * chunk_width))

            y_pred = sess.run(model.y, feed_dict={model.x: data.prepdata.x_data[0], model.x_proj: config.pop_proj[i] * 1000000})
            y_pred = y_pred.reshape(data.prepdata.no_chunks, chunk_height, chunk_width)

            for i in range(data.prepdata.no_chunks):
                if chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
                    cur_row += 1
                    cur_col = 0

                # Puts one chunk in at a time in the output raster
                output_raster[cur_row * chunk_height: (cur_row + 1) * chunk_height, cur_col * chunk_width: (cur_col + 1) * chunk_width] = \
                    y_pred[i, :, :]

                cur_col += 1

            # Predicting for each batch
            # for i in range(data.batch_num):
            #     y_pred = sess.run(model.y, feed_dict={model.x: data.input[0][i]})
            #     y_pred = y_pred.reshape(config.batch_size, chunk_height, chunk_width)
            #
            #
            #     for j in range(config.batch_size):
            #         if chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
            #             cur_row += 1
            #             cur_col = 0
            #
            #         output_raster[cur_row * chunk_height: (cur_row + 1) * chunk_height, cur_col * chunk_width: (cur_col + 1) * chunk_width] = \
            #             y_pred[j, :, :]
            #
            #         cur_col += 1

            # Removes the previous input data and adds the output raster
            data.prepdata.x_data = []

            new_input = data_loader.arrays[-1]
            new_input = np.concatenate((new_input, np.zeros((output_raster.shape[0] - new_input.shape[0], new_input.shape[1], new_input.shape[2]))), axis=0)
            new_input = np.concatenate((new_input, np.zeros((new_input.shape[0], output_raster.shape[1] - new_input.shape[1], new_input.shape[2]))), axis=1)
            new_input[:, :, 0] = output_raster
            data.prepdata.add_data(new_input)
            rasters.append(output_raster)

            print('Min value pop: {}'.format(np.amin(output_raster)))
            print('Max value pop: {}'.format(np.amax(output_raster)))
            print('Sum value pop: {}'.format(np.sum(output_raster)))

    # Calculating back to population
    # norm_sum = np.sum(output_raster)
    # final_pop = np.sum(pop_arr_14)
    #
    # output_raster = (output_raster / norm_sum) * final_pop

            print(np.max(output_raster))
            print(np.min(output_raster))
            print(output_raster.shape)

            data_writer = DataWriter(data_loader.geotif[0], output_raster, config)
            data_writer.write_geotif()


    # # Picking up values reference values needed to export to geotif
    # Projection = osr.SpatialReference()
    # Projection.ImportFromWkt(pop_data_14.GetProjectionRef())
    #
    # geoTransform = pop_data_14.GetGeoTransform()
    #
    # driver = gdal.GetDriverByName('GTiff')
    #
    # dst_ds = driver.Create('test_tiff_3.tif', xsize=output_raster.shape[1], ysize=output_raster.shape[0],
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
    # dst_ds.GetRasterBand(1).WriteArray(output_raster)
    # dst_ds.FlushCache()  # Write to disk.
    #


if __name__ == '__main__':
    main()