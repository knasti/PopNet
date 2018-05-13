from osgeo import gdal
import os
import sys
from utils.config import process_config
from utils.dirs import create_dirs

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

config_dir = os.path.relpath('..\\configs', base_dir)

config = process_config(os.path.join(config_dir, 'config.json'))

data_dir = os.path.relpath('..\\data\\{}'.format(config.exp_name), base_dir)

create_dirs([config.output_bbox_dir])

bbox_dir = config.output_bbox_dir
pred_dir = config.output_pred_dir

# config.output_bbox_dir

#os.path.join(config.output_pred_dir, 'pred_{}.tif'.format(output_nr))
# Input data to BBOX
ds = gdal.Open(os.path.join(data_dir, '2015.tif'))
ds = gdal.Translate(os.path.join(bbox_dir, 'bbox_input.tif'), ds, projWin=config.bbox)
ds = None

# Output data to BBOX
for file in os.listdir(config.output_pred_dir):
    if file.endswith('.tif'):
        ds = gdal.Open(os.path.join(pred_dir, file))
        ds = gdal.Translate(os.path.join(bbox_dir, 'bbox_{}'.format(file)), ds, projWin=config.bbox)
        ds = None
