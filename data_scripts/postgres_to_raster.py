import os
import shutil
import subprocess
import gdal

def psqltoshp(country, pghost, pguser, pgpassword, pgdatabase, save_data_path):

    # exporting water cover from postgres
    print("Exporting water cover from postgres")
    path = save_data_path + "\{0}_water_cover.shp".format(country)
    cmd = 'ogr2ogr -f "ESRI Shapefile" {0} PG:"host={1} user={2} dbname={3} password={4}" \
        -sql "SELECT id, water_cover, geom FROM {5}_cover_analysis"'.format(path, pghost, pguser, pgdatabase,
                                                                            pgpassword, country)
    subprocess.call(cmd, shell=True)

    # exporting roads from postgres
    print("Exporting roads from postgres")
    path = save_data_path + "\{0}_roads.shp".format(country)
    cmd = 'ogr2ogr -f "ESRI Shapefile" {0} PG:"host={1} user={2} dbname={3} password={4}" \
        -sql "SELECT id, rdist, geom FROM {5}_cover_analysis"'.format(path, pghost, pguser, pgdatabase,
                                                                      pgpassword, country)
    subprocess.call(cmd, shell=True)

    # exporting corine 1990 from postgres
    print("Exporting corine 1990 from postgres")
    path = save_data_path + "\{0}_corine1990.shp".format(country)
    cmd = 'ogr2ogr -f "ESRI Shapefile" {0} PG:"host={1} user={2} dbname={3} password={4}" \
            -sql "SELECT id, corine_cover90, geom FROM {5}_cover_analysis"'.format(path, pghost, pguser, pgdatabase,
                                                                                   pgpassword, country)
    subprocess.call(cmd, shell=True)

    # exporting corine 2012 from postgres
    print("Exporting corine 2012 from postgres")
    path = save_data_path + "\{0}_corine2012.shp".format(country)
    cmd = 'ogr2ogr -f "ESRI Shapefile" {0} PG:"host={1} user={2} dbname={3} password={4}" \
                -sql "SELECT id, corine_cover, geom FROM {5}_cover_analysis"'.format(path, pghost, pguser, pgdatabase,
                                                                                     pgpassword, country)
    subprocess.call(cmd, shell=True)

    # exporting train stations from postgres
    print("Exporting train stations from postgres")
    path = save_data_path + "\{0}_train_stations.shp".format(country)
    cmd = 'ogr2ogr -f "ESRI Shapefile" {0} PG:"host={1} user={2} dbname={3} password={4}" \
                -sql "SELECT id, station, geom FROM {5}_cover_analysis"'.format(path, pghost, pguser, pgdatabase,
                                                                                     pgpassword, country)
    subprocess.call(cmd, shell=True)

    # exporting municipality from postgres
    print("Exporting municipality information from postgres")
    path = save_data_path + "\{0}_municipality.shp".format(country)
    cmd = 'ogr2ogr -f "ESRI Shapefile" {0} PG:"host={1} user={2} dbname={3} password={4}" \
                -sql "SELECT id, municipality, geom FROM {5}_cover_analysis"'.format(path, pghost, pguser, pgdatabase,
                                                                                     pgpassword, country)
    subprocess.call(cmd, shell=True)

def shptoraster(country, gdal_rasterize_path, xres, yres, save_data_path, merge_folder_path):
    # Getting extent of ghs pop raster
    data = gdal.Open(merge_folder_path + "\GHS_POP_1975_{0}.tif".format(country))
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None

    # Rasterizing water_cover layer
    print("Rasterizing water_cover layer")
    src_file = save_data_path +"\{0}_water_cover.shp".format(country)
    dst_file = merge_folder_path +"\{0}_water_cover.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -a WATER_COVE -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
        .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)

    # Rasterizing roads layer
    print("Rasterizing roads layer")
    src_file = save_data_path + "\{0}_roads.shp".format(country)
    dst_file = merge_folder_path + "\{0}_roads.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -a RDIST -te {1} {2} {3} {4} -tr {5} {6} {7} {8}' \
        .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)

    # Rasterizing corine 1990 layer
    print("Rasterizing corine 1990 layer")
    src_file = save_data_path + "\{0}_corine1990.shp".format(country)
    dst_file = merge_folder_path + "\{0}_corine1990.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -a CORINE_COV -te {1} {2} {3} {4} -tr {5} {6} {7} {8}' \
        .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)

    # Rasterizing corine 2012 layer
    print("Rasterizing corine 2012 layer")
    src_file = save_data_path + "\{0}_corine2012.shp".format(country)
    dst_file = merge_folder_path + "\{0}_corine2012.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -a CORINE_COV -te {1} {2} {3} {4} -tr {5} {6} {7} {8}' \
        .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)

    # Rasterizing train stations
    print("Rasterizing train stations layer")
    src_file = save_data_path + "\{0}_train_stations.shp".format(country)
    dst_file = merge_folder_path + "\{0}_train_stations.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -a station -te {1} {2} {3} {4} -tr {5} {6} {7} {8}' \
        .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)

    # Rasterizing train stations
    print("Rasterizing municipality information layer")
    src_file = save_data_path + "\{0}_municipality.shp".format(country)
    dst_file = merge_folder_path + "\{0}_municipality.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -a municipali -te {1} {2} {3} {4} -tr {5} {6} {7} {8}' \
        .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)

    # #Deleting temp folder
    # print("Deleting temp folder and content")
    # shutil.rmtree(save_data_path, ignore_errors=True)