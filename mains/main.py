import tensorflow as tf
import os
from osgeo import gdal
import osr
import sys
import numpy as np

from data_loader.data_generator import DataGenerator, PrepData, PrepTrainTest
from data_loader.data_loader import DataLoader
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

    # Create Tensorboard logger
    logger = Logger(sess, config)

    # Create trainer and path all previous components to it
    trainer = PopTrainer(sess, model, data, config, logger)

    # Train model
    trainer.train()


if __name__ == '__main__':
    main()