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

    prepd = PrepData(config, data_loader)

    start_raster = data_loader.arrays[-1]

    prepd.add_data(start_raster)

    # Create the experiments output dir
    create_dirs([config.output_dir, config.output_pred_dir, config.output_dif_dir, config.output_eval_dir])

    # Create tensorflow session
    sess = tf.Session()

    # Create instance of the model
    model = PopModel(config)

    # Load model if exist
    model.load(sess)

    # Create data generator
    data = DataGenerator(config, prepdata = prepd)

    start_raster = data.prepdata.x_data[0][:,:,0]
    prev_raster = start_raster

    with sess:
        rasters = []

        for k in range(config.num_outputs):
            data.prepdata.output_nr = k
            data.create_data()

            cur_row = 0
            cur_col = 0

            chunk_height = data.prepdata.chunk_height
            chunk_width = data.prepdata.chunk_width

            chunk_rows = data.prepdata.chunk_rows
            chunk_cols = data.prepdata.chunk_cols

            output_raster = np.empty((chunk_rows * chunk_height, chunk_cols * chunk_width))

            # Predicting for each batch
            for i in range(data.batch_num):
                #y_pred = sess.run(model.y, feed_dict={model.x: data.input[0][i]})
                y_pred, y_pred_chunk = sess.run([model.y, model.y_chunk], feed_dict={model.x: data.input[0][i],
                                                                                     model.x_pop_chunk: data.x_chunk_pop[0][i],
                                                                                     model.x_proj: config.pop_proj[k],
                                                                                     model.x_cur_pop: data.prepdata.x_cur_pop[0]})
                y_pred = y_pred.reshape(config.batch_size, chunk_height, chunk_width)


                for j in range(config.batch_size):
                    if chunk_cols == cur_col:  # Change to new row and reset column if it reaches the end
                        cur_row += 1
                        cur_col = 0

                    output_raster[cur_row * chunk_height: (cur_row + 1) * chunk_height, cur_col * chunk_width: (cur_col + 1) * chunk_width] = \
                        y_pred[j, :, :]

                    cur_col += 1



            # Removes null-cells at the start of the array
            output_raster = output_raster[data.prepdata.offset_rows:, data.prepdata.offset_cols:]

            # Makes sure the right amount of null-cells are removed from the end of the array
            if data.prepdata.row_null_cells == 0 and data.prepdata.col_null_cells == 0:
                pass
            elif data.prepdata.row_null_cells == 0:
                output_raster = output_raster[:, :-data.prepdata.col_null_cells]
            elif data.prepdata.col_null_cells == 0:
                output_raster = output_raster[:-data.prepdata.row_null_cells, :]
            else:
                output_raster = output_raster[:-data.prepdata.row_null_cells, :-data.prepdata.col_null_cells]

            # Removes the previous input data and adds the output raster
            data.prepdata.x_data = []

            # Replaces the old population with the predicted one, keeps the other features constant
            new_input = data_loader.arrays[-1]
            new_input[:, :, 0] = output_raster[:new_input.shape[0], :new_input.shape[1]]

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

            data_writer = DataWriter(data_loader.geotif[0], start_raster, prev_raster, output_raster, config)
            data_writer.write_outputs()
            prev_raster = output_raster



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