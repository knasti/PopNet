# This script imports data to postgres
import os
import ogr
import subprocess


def import_to_postgres(country, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, temp_folder_path, ancillary_data_folder_path):
    # ----- Importing data to postgres -------------------------------------------------------------------------------------
    # Importing corine layers by quering data inside country extent
    # Tranforming gadm country layer to srs 3035
    inshp = temp_folder_path + "\GADM_{0}.shp".format(country)
    outshp = temp_folder_path + "\GADM_{0}_3035.shp".format(country)
    cmd = 'ogr2ogr -f "ESRI Shapefile" -t_srs EPSG:3035 {0} {1}'.format(outshp, inshp)
    subprocess.call(cmd, shell=True)

    # Get a Layer's Extent
    inShapefile = temp_folder_path + "\GADM_{0}_3035.shp".format(country)
    inD = ogr.GetDriverByName("ESRI Shapefile")
    inData = inD.Open(inShapefile, 0)
    inLa = inData.GetLayer()
    extent = inLa.GetExtent()
    xmin = extent[0]
    ymin = extent[2]
    xmax = extent[1]
    ymax = extent[3]

    # Loading corine 2012 into postgres
    clc12path = ancillary_data_folder_path + "\corine\clc12_Version_18_5a_sqLite\clc12_Version_18_5.sqlite"
    cmds = 'ogr2ogr -lco GEOMETRY_NAME=geom -lco SCHEMA=public -f "PostgreSQL" \
    PG:"host=localhost port=5432 user=postgres dbname=raster_database password=postgres" \
    -a_srs "EPSG:3035" {0} -sql "SELECT * FROM clc12_Version_18_5 \
    WHERE code_12 = 124 OR code_12 = 121 OR code_12 = 311 OR code_12 = 312 OR code_12 = 313" \
    -spat {1} {2} {3} {4} -nln corine'.format(clc12path, xmin, ymin, xmax, ymax)
    subprocess.call(cmds, shell=True)

    # Loading corine 1990 into postgres
    clc90path = ancillary_data_folder_path + "\corine\clc90_Version_18_5_sqLite\clc90_Version_18_5.sqlite"
    cmds = 'ogr2ogr -lco GEOMETRY_NAME=geom -lco SCHEMA=public -f "PostgreSQL" \
    PG:"host=localhost port=5432 user=postgres dbname=raster_database password=postgres" \
    -a_srs "EPSG:3035" {0} -sql "SELECT * FROM clc90_Version_18_5 \
    WHERE code_90 = 124 OR code_90 = 121 OR code_90 = 311 OR code_90 = 312 OR code_90 = 313" \
    -spat {1} {2} {3} {4} -nln corine90'.format(clc90path, xmin, ymin, xmax, ymax)
    subprocess.call(cmds, shell=True)

    # Setting environment for psql
    os.environ['PATH'] = pgpath
    os.environ['PGHOST'] = pghost
    os.environ['PGPORT'] = pgport
    os.environ['PGUSER'] = pguser
    os.environ['PGPASSWORD'] = pgpassword
    os.environ['PGDATABASE'] = pgdatabase

    # Loading vector grid into postgresql
    gridpath = temp_folder_path + "\{0}_2015vector.shp".format(country)
    cmds = 'ogr2ogr --config PG_USE_COPY YES -gt 65536 -f PGDump /vsistdout/ \
    {0} -a_srs "EPSG:54009" -lco GEOMETRY_NAME=geom -lco SCHEMA=public -lco \
    CREATE_SCHEMA=OFF -lco SPATIAL_INDEX=OFF | psql'.format(gridpath)
    subprocess.call(cmds, shell=True)

    # Loading iteration grid into postgres
    ite_path = temp_folder_path + "\{0}_iteration_grid.shp".format(country)
    cmds = 'shp2pgsql -I -s 54009 {0} public.{1}_iteration_grid | psql'.format(ite_path, country)
    subprocess.call(cmds, shell=True)

    # Loading gadm into postgres
    gadmpath = temp_folder_path + "\GADM_{0}.shp".format(country)
    cmds = 'shp2pgsql -I -s 54009 {0} public.{1}_adm | psql'.format(gadmpath, country)
    subprocess.call(cmds, shell=True)

    # Loading water into postgres
    lakespath = temp_folder_path + "\eu_lakes_{0}.shp".format(country)
    cmds = 'shp2pgsql -I -s 54009 {0} public.eu_lakes_{1} | psql'.format(lakespath, country)
    subprocess.call(cmds, shell=True)

    # Loading groads into postgres
    roadpath = ancillary_data_folder_path + "\groads_europe\gROADS-v1-europe.shp"
    cmds = 'shp2pgsql -I -s 4326 {0} public.groads | psql'.format(roadpath)
    subprocess.call(cmds, shell=True)