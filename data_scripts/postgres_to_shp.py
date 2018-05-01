import os
import subprocess

def psqltoshp(country, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, save_data_path):
    os.environ['PATH'] = pgpath
    os.environ['PGHOST'] = pghost
    os.environ['PGPORT'] = pgport
    os.environ['PGUSER'] = pguser
    os.environ['PGPASSWORD'] = pgpassword
    os.environ['PGDATABASE'] = pgdatabase

    # exporting water cover from postgres
    # print("---------- Exporting water cover from postgres ----------")
    # path = save_data_path + "\{0}_water_cover.shp".format(country)
    # cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres raster_database "SELECT id, water_cover, geom FROM {1}_cover_analysis"'.format(path, country)
    # subprocess.call(cmd, shell=True)

    # # exporting roads
    print("---------- Exporting roads from postgres ----------")
    path = save_data_path + "\{0}_roads.shp".format(country)
    cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres raster_database "SELECT id, rdist, geom FROM {1}_cover_analysis"'.format(path, country)
    subprocess.call(cmd, shell=True)
    #
    # # exporting corine 1990
    # print("---------- Exporting corine 1990 from postgres ----------")
    # path = save_data_path + "\{0}_corine1990.shp".format(country)
    # cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres raster_database "SELECT id, corine_cover90, geom FROM {1}_cover_analysis"'.format(path, country)
    # subprocess.call(cmd, shell=True)
    #
    # # exporting corine 2012
    # print("---------- Exporting corine 2012 from postgres ----------")
    # path = save_data_path + "\{0}_corine2012.shp".format(country)
    # cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres raster_database "SELECT id, corine_cover, geom FROM {1}_cover_analysis"'.format(path, country)
    # subprocess.call(cmd, shell=True)



def shptoraster(country, gdal_rasterize_path, xmin, xmax, ymin, ymax, xres, yres, save_data_path):
    # Dette virker højest sansynligt ikke og skal laves om og testes. Vi skal finde en god løsning mht at lave raster
    # Rasterizing water_cover layer
    # print("Rasterizing water_cover layer")
    # src_file = save_data_path +"\{0}_water_cover.shp".format(country)
    # dst_file = save_data_path +"\{0}_water_cover.tif".format(country)
    # cmd = '{0}\gdal_rasterize.exe -a WATER_COVE -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
    #     .format(gdal_rasterize_path, xmin, ymin, xmax, ymax, xres, yres, src_file, dst_file)
    # subprocess.call(cmd, shell=True)

    # Rasterizing roads layer
    print("Rasterizing roads layer")
    src_file = save_data_path + "\{0}_roads.shp".format(country)
    dst_file = save_data_path + "\{0}_roads.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -a RDIST -te {1} {2} {3} {4} -tr {5} {6} {7} {8}' \
        .format(gdal_rasterize_path, xmin, ymin, xmax, ymax, xres, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)
    #
    # # Rasterizing corine 1990 layer
    # print("Rasterizing corine 1990 layer")
    # src_file = save_data_path + "\{0}_corine1990.shp".format(country)
    # dst_file = save_data_path + "\{0}_corine1990.tif".format(country)
    # cmd = '{0}\gdal_rasterize.exe -a CORINE_COV -te {1} {2} {3} {4} -tr {5} {6} {7} {8}' \
    #     .format(gdal_rasterize_path, xmin, ymin, xmax, ymax, xres, yres, src_file, dst_file)
    # subprocess.call(cmd, shell=True)
    #
    # # Rasterizing corine 2012 layer
    # print("Rasterizing corine 2012 layer")
    # src_file = save_data_path + "\{0}_corine2012.shp".format(country)
    # dst_file = save_data_path + "\{0}_corine2012.tif".format(country)
    # cmd = '{0}\gdal_rasterize.exe -a CORINE_COV -te {1} {2} {3} {4} -tr {5} {6} {7} {8}' \
    #     .format(gdal_rasterize_path, xmin, ymin, xmax, ymax, xres, yres, src_file, dst_file)
    # subprocess.call(cmd, shell=True)

