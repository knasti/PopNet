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
        config = process_config(os.path.join(config_dir, 'config.json'))

    data_loader = DataLoader(data_dir)
    data_loader.load_directory('.tif')
    data_loader.create_np_arrays()
    data_loader.create_data_label_pairs()

    preptt = PrepTrainTest(config.batch_size, config.chunk_height, config.chunk_width)
    prepd = PrepData(config.batch_size, config.chunk_height, config.chunk_width)

    for i in range(len(data_loader.data_label_pairs)):
        x_data = data_loader.data_label_pairs[i][0]
        y_true = data_loader.data_label_pairs[i][1]

        preptt.add_data(x_data, y_true)
        prepd.add_data(x_data, y_true)


    # Create the experiments dirs
    create_dirs([config.summary_dir, config.checkpoint_dir])

    # Create tensorflow session
    sess = tf.Session()

    # Create instance of the model you want
    model = PopModel(config)

    # Load model if exist
    model.load(sess)

    # Create Tensorboard logger
    logger = Logger(sess, config)

    # Create your data generator
    data = DataGenerator(config, preptt, prepd)

    data.create_traintest_data()
    data.create_data()



    # Create trainer and path all previous components to it
    trainer = PopTrainer(sess, model, data, config, logger)

    # Train model
    trainer.train()

    # Test model



if __name__ == '__main__':
    main()