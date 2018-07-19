from osgeo import gdal
import numpy as np
import osr


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

# gammel tif (trækker den gamle fra den nye)
path_tiff_1 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\data\france\2000.tif')
# ny tif
path_tiff_2 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\data\france\2015.tif')
# dir du vil gemme i
dir = r'C:\Users\Niels\Documents\GitHub\PopNet\visualizations\filename.tif'

np_tiff_1 = np.array(path_tiff_1.GetRasterBand(1).ReadAsArray())
print(np.shape(np_tiff_1))

np_tiff_2 = np.array(path_tiff_2.GetRasterBand(1).ReadAsArray())
dif_tif = np_tiff_2 - np_tiff_1

print(type(path_tiff_1))
print(type(dif_tif))

write_tif_to_disk(dir, dif_tif, path_tiff_1)


