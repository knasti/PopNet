import os
import subprocess

def psqltoshp(country, save_data_path):
    os.environ['PATH'] = r';C:\Program Files\PostgreSQL\9.5\bin'
    os.environ['PGHOST'] = 'localhost'
    os.environ['PGPORT'] = '5432'
    os.environ['PGUSER'] = 'postgres'
    os.environ['PGPASSWORD'] = 'postgres'
    os.environ['PGDATABASE'] = 'raster_database'

    # exporting water cover from postgres
    print("Exporting water cover from postgres")
    path = save_data_path + "\water_cover_{0}.shp".format(country)
    cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres raster_database "SELECT id, water_cover, geom FROM denmark_water_cover"'.format(path)
    subprocess.call(cmd, shell=True)

    # exporting roads
    print("Exporting roads from postgres")
    path = save_data_path + "\{0}_roads.shp".format(country)
    cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres raster_database "SELECT id, rdist, geom FROM denmark_water_cover"'.format(path)
    subprocess.call(cmd, shell=True)

    # exporting corine 2012
    print("Exporting corine 2012 from postgres")
    path = save_data_path + "\corine2012_{0}.shp".format(country)
    cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres raster_database "SELECT id, corine_cover, geom FROM denmark_water_cover"'.format(path)
    subprocess.call(cmd, shell=True)

    # exporting corine 1990
    print("Exporting corine 1990 from postgres")
    path = save_data_path + "\corine1990_{0}.shp".format(country)
    cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres raster_database "SELECT id, corine_cover90, geom FROM denmark_water_cover"'.format(path)
    subprocess.call(cmd, shell=True)

def shptoraster(country, gdal_rasterize_path, band_nr, xmin, xmax, ymin, ymax, xras, yres, save_data_path, dst_file):

    # Dette virker højest sansynligt ikke og skal laves om og testes. Vi skal finde en god løsning mht at lave raster

    # Rasterizing water_cover layer
    print("Rasterizing water_cover layer")
    src_file = save_data_path +"\water_cover_{0}.shp".format(country)
    dst_file = save_data_path +"\water_cover_{0}.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -b {1} -te {2} {3} {4} {5} -tr {6} {7} {8} {9}'\
        .format(gdal_rasterize_path, band_nr, xmin, xmax, ymin, ymax, xras, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)

    # Rasterizing roads layer
    print("Rasterizing roads layer")
    src_file = save_data_path + "\{0}_roads.shp".format(country)
    dst_file = save_data_path + "\{0}_roads.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -b {1} -te {2} {3} {4} {5} -tr {6} {7} {8} {9}' \
        .format(gdal_rasterize_path, band_nr, xmin, xmax, ymin, ymax, xras, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)

    # Rasterizing corine 2012 layer
    print("Rasterizing corine 2012 layer")
    src_file = save_data_path + "\corine2012_{0}.shp".format(country)
    dst_file = save_data_path + "\corine2012_{0}.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -b {1} -te {2} {3} {4} {5} -tr {6} {7} {8} {9}' \
        .format(gdal_rasterize_path, band_nr, xmin, xmax, ymin, ymax, xras, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)

    # Rasterizing corine 1990 layer
    print("Rasterizing corine 1990 layer")
    src_file = save_data_path + "\corine1990_{0}.shp".format(country)
    dst_file = save_data_path + "\corine1990_{0}{0}.tif".format(country)
    cmd = '{0}\gdal_rasterize.exe -b {1} -te {2} {3} {4} {5} -tr {6} {7} {8} {9}' \
        .format(gdal_rasterize_path, band_nr, xmin, xmax, ymin, ymax, xras, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)