import numpy as np
import os
from osgeo import gdal
import osr


dir = r'C:\Users\Niels\Desktop\monte_carlo'

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def write_tif_to_disk(dir, raster, geotif):
    # Picking up values reference values needed to export to geotif
    projection = osr.SpatialReference()
    projection.ImportFromWkt(geotif.GetProjectionRef())

    # Grab the geotransformation values
    geo_transform = geotif.GetGeoTransform()

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

sub_dirs = get_immediate_subdirectories(dir)

pred_2020 = []
pred_2030 = []
pred_2040 = []
pred_2050 = []
pred_2060 = []
pred_2070 = []
pred_2080 = []
pred_2090 = []
pred_2100 = []

for sub_dir in sub_dirs:
    path = os.path.join(dir, sub_dir)
    for file in os.listdir(path):
        pop_data = gdal.Open(os.path.join(path, file))
        pop_array = np.array(pop_data.GetRasterBand(1).ReadAsArray())
        if file == 'pred_2020.tif':
            if type(pred_2020) is np.ndarray:
                pred_2020 += pop_array
            else:
                pred_2020 = pop_array
            print(np.max(pop_array))

        elif file == 'pred_2030.tif':
            if type(pred_2030) is np.ndarray:
                pred_2030 += pop_array
            else:
                pred_2030 = pop_array

        elif file == 'pred_2040.tif':
            if type(pred_2040) is np.ndarray:
                pred_2040 += pop_array
            else:
                pred_2040 = pop_array

        elif file == 'pred_2050.tif':
            if type(pred_2050) is np.ndarray:
                pred_2050 += pop_array
            else:
                pred_2050 = pop_array

        elif file == 'pred_2060.tif':
            if type(pred_2060) is np.ndarray:
                pred_2060 += pop_array
            else:
                pred_2060 = pop_array

        elif file == 'pred_2070.tif':
            if type(pred_2070) is np.ndarray:
                pred_2070 += pop_array
            else:
                pred_2070 = pop_array

        elif file == 'pred_2080.tif':
            if type(pred_2080) is np.ndarray:
                pred_2080 += pop_array
            else:
                pred_2080 = pop_array

        elif file == 'pred_2090.tif':
            if type(pred_2090) is np.ndarray:
                pred_2090 += pop_array
            else:
                pred_2090 = pop_array

        else:
            if type(pred_2100) is np.ndarray:
                pred_2100 += pop_array
            else:
                pred_2100 = pop_array


pred_2020 = pred_2020 / len(sub_dirs)
pred_2030 = pred_2030 / len(sub_dirs)
pred_2040 = pred_2040 / len(sub_dirs)
pred_2050 = pred_2050 / len(sub_dirs)
pred_2060 = pred_2060 / len(sub_dirs)
pred_2070 = pred_2070 / len(sub_dirs)
pred_2080 = pred_2080 / len(sub_dirs)
pred_2090 = pred_2090 / len(sub_dirs)
pred_2100 = pred_2100 / len(sub_dirs)

pred_list = [pred_2020, pred_2030, pred_2040, pred_2050, pred_2060, pred_2070, pred_2080, pred_2090, pred_2100]

for i, pred in enumerate(pred_list):
    print_dir = os.path.join(dir, 'pred_{}.tif'.format(i))
    write_tif_to_disk(print_dir, pred, pop_data)


# for sub_dir in os.walk(dir):
#     print(sub_dir[0])

