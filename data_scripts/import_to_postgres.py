# ------ IMPORT SCRIPT FOR POSTGRESQL ------
# --Imports--
import psycopg2
import subprocess
import sys,os
#import shapefile
import gdal
import ogr
import osr
from shutil import *

# --settings--
# Specify Country to import
country = 'Denmark'

# --input path to "Project_data" folder (Project_data folder placed in same folder as script)--
# Content and structure of Project_data folder should be:
#Ancillary_data folder
#GADM folder
#GHS folder
#Temp folder - for produced data (created in same folder as this script)

# Get path to script
python_script_dir = os.path.dirname(os.path.abspath(__file__))
#path to ancillary data folder
ancillary_data_folder_path = python_script_dir + "\Project_data\Ancillary_data"
#path to GADM folder
gadm_folder_path = python_script_dir + "\Project_data\GADM"
#path to GHS folder
ghs_folder_path = python_script_dir + "\Project_data\GHS"
#path to temp folder
temp_folder_path = python_script_dir + "\Project_data\Temp"
#path to data folder to import to postgresql
postgres_import_data_path = python_script_dir + "\Project_data\postgres_import_data"

# ---------------------------------------------------------------------------------------------------------------------
# ----- Extracting country from GADM and creating bounding box-----
# select country in GADM and write to new file
input_gadm_dataset = gadm_folder_path + "\gadm28_adm0.shp"
output_country_shp = postgres_import_data_path + "\GADM_{0}.shp".format(country)

sql_statement = "NAME_ENGLI='{0}'".format(country)
country_shp = 'ogr2ogr -where {0} -f "ESRI Shapefile"  {1} {2}'.format(sql_statement, output_country_shp, input_gadm_dataset)
subprocess.call(country_shp, shell=True)

# create bounding box around chosen country
# Get a Layer's Extent
inShapefile = output_country_shp
inDriver = ogr.GetDriverByName("ESRI Shapefile")
inDataSource = inDriver.Open(inShapefile, 0)
inLayer = inDataSource.GetLayer()
extent = inLayer.GetExtent()

# Create a Polygon from the extent tuple
ring = ogr.Geometry(ogr.wkbLinearRing)
ring.AddPoint(extent[0], extent[2])
ring.AddPoint(extent[1], extent[2])
ring.AddPoint(extent[1], extent[3])
ring.AddPoint(extent[0], extent[3])
ring.AddPoint(extent[0], extent[2])
poly = ogr.Geometry(ogr.wkbPolygon)
poly.AddGeometry(ring)

# Save extent to a new Shapefile
outShapefile = postgres_import_data_path + "\{0}_extent.shp".format(country)
outDriver = ogr.GetDriverByName("ESRI Shapefile")

# Remove output shapefile if it already exists
if os.path.exists(outShapefile):
    outDriver.DeleteDataSource(outShapefile)

# Create the output shapefile
outDataSource = outDriver.CreateDataSource(outShapefile)
outLayer = outDataSource.CreateLayer("{0}_extent".format(country), geom_type=ogr.wkbPolygon)

# Add an ID field
idField = ogr.FieldDefn("id", ogr.OFTInteger)
outLayer.CreateField(idField)

# Create the feature and set values
featureDefn = outLayer.GetLayerDefn()
feature = ogr.Feature(featureDefn)
feature.SetGeometry(poly)
feature.SetField("id", 1)
outLayer.CreateFeature(feature)
feature = None

# Save and close DataSource
inDataSource = None
outDataSource = None

# create projection file for extent
driver = ogr.GetDriverByName('ESRI Shapefile')
dataset = driver.Open(output_country_shp)
layer = dataset.GetLayer()
spatialRef = layer.GetSpatialRef()
in_epsg = int(spatialRef.GetAttrValue('Authority', 1))
spatialRef.MorphToESRI()
file = open(postgres_import_data_path + '\{0}_extent.prj'.format(country), 'w')
file.write(spatialRef.ExportToWkt())
file.close()

# ----- recalculating coordinate extent of bbox to match pixels to avoid pixel shift and clipping ghs raster -----
for subdir, dirs, files in os.walk(ghs_folder_path):
    for file in files:
        if file.endswith(".tif"):
            name = file.split(".tif")[0]

            ghs_file_path = os.path.join(subdir, file)
            out_file_path = postgres_import_data_path + "\{0}_{1}.tif".format(name, country)
            country_mask = postgres_import_data_path + "\GADM_{0}.shp".format(country)

            # open raster and get its georeferencing information
            dsr = gdal.Open(ghs_file_path, gdal.GA_ReadOnly)
            gt = dsr.GetGeoTransform()
            srr = osr.SpatialReference()
            srr.ImportFromWkt(dsr.GetProjection())

            # open vector data and get its spatial ref
            dsv = ogr.Open(country_mask)
            lyr = dsv.GetLayer(0)
            srv = lyr.GetSpatialRef()

            # make object that can transorm coordinates
            ctrans = osr.CoordinateTransformation(srv, srr)

            lyr.ResetReading()
            ft = lyr.GetNextFeature()
            while ft:
                # read the geometry and transform it into the raster's SRS
                geom = ft.GetGeometryRef()
                geom.Transform(ctrans)
                # get bounding box for the transformed feature
                minx, maxx, miny, maxy = geom.GetEnvelope()

                # compute the pixel-aligned bounding box (larger than the feature's bbox)
                left = minx - (minx - gt[0]) % gt[1]
                right = maxx + (gt[1] - ((maxx - gt[0]) % gt[1]))
                bottom = miny + (gt[5] - ((miny - gt[3]) % gt[5]))
                top = maxy - (maxy - gt[3]) % gt[5]

                cmd_clip = 'gdalwarp -te {0} {1} {2} {3} -tr {4} {5} -cutline {6} -srcnodata -3.4028234663852886e+38 -dstnodata 0 {7} {8}'.format(
                str(left), str(bottom), str(right), str(top), str(abs(gt[1])), str(abs(gt[5])), country_mask, ghs_file_path, out_file_path)
                subprocess.call(cmd_clip, shell=True)

                ft = lyr.GetNextFeature()
            ds = None

# # ----- Change coordinate system of slope tif -----
# # reproject bounding box to match slope tif
# original = postgres_import_data_path + "\GADM_{0}.shp".format(country)
# new = temp_folder_path + "\{0}_mask_srs3035.shp".format(country)
# cmd_srs_bbox = 'ogr2ogr -f "ESRI Shapefile" -t_srs EPSG:3035 {0} {1}'.format(new, original)
# subprocess.call(cmd_srs_bbox, shell=True)
#
# # clipping slope tif
# country_mask = postgres_import_data_path + "\GADM_{0}.shp".format(country)
# in_tif = ancillary_data_folder_path + "\Copernicus\Slope\eudem_slop_3035_europe.tif"
# out_tif = temp_folder_path + "\{}_slope_extent_srs3035.tif".format(country)
# cmd_clip = "gdalwarp -cutline {0} -crop_to_cutline {1} {2}".format(country_mask, in_tif, out_tif)
# subprocess.call(cmd_clip, shell=True)
#
# # reprojecting slope to srs 54009
# in_tif = temp_folder_path + "\{}_slope_extent_srs3035.tif".format(country)
# out_tif = postgres_import_data_path + "\{0}_slope.tif".format(country)
# cmd_srs_change = "gdalwarp -s_srs EPSG:3035 -t_srs EPSG:54009 {0} {1}".format(in_tif, out_tif)
# subprocess.call(cmd_srs_change, shell=True)
#
# ----- clipping lakes layer -----
clip_poly = postgres_import_data_path + "\GADM_{0}.shp".format(country)
in_shp = ancillary_data_folder_path + "\lakes.shp"
out_shp = postgres_import_data_path + "\lakes.shp"
cmd_shp_clip = "ogr2ogr -clipsrc {0} {1} {2}".format(clip_poly, out_shp, in_shp)
subprocess.call(cmd_shp_clip, shell=True)

# ----- importing tif and shp files to postgres: -----
#loop through raster files in dir
for raster in os.listdir(postgres_import_data_path):
    if raster.endswith(".tif"):
        name = raster.split(".tif")[0]
        raster = os.path.join(postgres_import_data_path, raster)

        #Connect to the PostgreSQL server:

        os.environ['PATH'] = r';C:\Program Files\PostgreSQL\9.5\bin'
        os.environ['PGHOST'] = 'localhost'
        os.environ['PGPORT'] = '5432'
        os.environ['PGUSER'] = 'postgres'
        os.environ['PGPASSWORD'] = 'postgres'
        os.environ['PGDATABASE'] = 'raster_database'

        rastername = str(name)
        rasterlayer = rastername.lower()

        conn = psycopg2.connect(database="raster_database", user="postgres", host="localhost", password="postgres")
        cursor = conn.cursor()

        # Import each raster through raster2pgsql function

        cmds = 'raster2pgsql -s 54009 -I -t auto "' + raster + '" | psql'
        subprocess.call(cmds, shell=True)

# loop through shapefiles files in dir
for shapefile in os.listdir(postgres_import_data_path):
    if shapefile.endswith(".shp"):
        name = shapefile.split(".shp")[0]
        shapefile = os.path.join(postgres_import_data_path, shapefile)

        #Connect to the PostgreSQL server:

        os.environ['PATH'] = r';C:\Program Files\PostgreSQL\9.5\bin'
        os.environ['PGHOST'] = 'localhost'
        os.environ['PGPORT'] = '5432'
        os.environ['PGUSER'] = 'postgres'
        os.environ['PGPASSWORD'] = 'postgres'
        os.environ['PGDATABASE'] = 'raster_database'

        schema ="public"
        table = name
        database ='raster_database'

        shapefile_name = str(name)
        shapefile_layer = shapefile_name.lower()

        conn = psycopg2.connect(database="raster_database", user="postgres", host="localhost", password="postgres")
        cursor = conn.cursor()

        # Import each shp through shp2pgs ql function:

        cmds = 'shp2pgsql -I -s 54009 {0} {1}.{2} | psql -U postgres -d {3}'.format(shapefile, schema, table, database)
        subprocess.call(cmds, shell=True)

# # test: merging all ghs files into one multiband raster
# gdal_merge = r'C:\Users\thoma\Anaconda3\envs\kandidat\Scripts'
# outfile = postgres_import_data_path + "\MERGED_POP_Denmark.tif"
# file1 = postgres_import_data_path + "\GHS_POP_1975_Denmark.tif"
# file2 = postgres_import_data_path + "\GHS_POP_1990_Denmark.tif"
# file3 = postgres_import_data_path + "\GHS_POP_2000_Denmark.tif"
# file4 = postgres_import_data_path + "\GHS_POP_2015_Denmark.tif"
# cmd_tif_merge = "python {0}\gdal_merge.py -o {1} -separate {2} {3} {4} {5}".format(gdal_merge, outfile, file1, file2, file3, file4)
# subprocess.call(cmd_tif_merge, shell=False)