import tensorflow as tf
import os
from osgeo import gdal
import osr
import sys
import numpy as np

from data_loader.data_generator import DataGenerator, PrepData, PrepTrainTest
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



    #
    # except:
    #     print("missing or invalid arguments")
    #     exit(0)

    # Loads the geotiff
    pop_data_10 = gdal.Open(os.path.join(data_dir, 'TGO10v4.tif'))
    pop_data_14 = gdal.Open(os.path.join(data_dir, 'TGO14adjv1.tif'))
    pop_data_15 = gdal.Open(os.path.join(data_dir, 'TGO15adjv4.tif'))

    # Store the values of the geotif into a np.array
    pop_arr_10 = np.array(pop_data_10.GetRasterBand(1).ReadAsArray())
    pop_arr_10 = np.delete(pop_arr_10, -1, axis=1)  # Shape not the same as pop data from 14 and 15

    pop_arr_14 = np.array(pop_data_14.GetRasterBand(1).ReadAsArray())
    pop_arr_15 = np.array(pop_data_15.GetRasterBand(1).ReadAsArray())

    # Null-values (neg-values) are replaced with zeros
    pop_arr_10[pop_arr_10 < 0] = 0
    pop_arr_14[pop_arr_14 < 0] = 0
    pop_arr_15[pop_arr_15 < 0] = 0

    preptt = PrepTrainTest(pop_arr_10, pop_arr_14, config.batch_size)
    prepd = PrepData(pop_arr_10, pop_arr_14, config.batch_size)


    # create the experiments dirs
    create_dirs([config.summary_dir, config.checkpoint_dir])
    # create tensorflow session
    sess = tf.Session()
    # create instance of the model you want
    model = PopModel(config)
    #load model if exist
    model.load(sess)
    # create your data generator
    data = DataGenerator(config, preptt, prepd)

    data.create_traintest_data()
    data.create_data()


    print(data.train_data)

    # Create Tensorboard logger
    logger = Logger(sess, config)

    # Create trainer and path all previous components to it
    trainer = PopTrainer(sess, model, data, config, logger)

    # Train model
    trainer.train()


if __name__ == '__main__':
    main()