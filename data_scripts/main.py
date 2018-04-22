# ------ Main Script for data preparation ------------------------------------------------------------------------------
# Imports
import subprocess
import os
import gdal
import ogr
import osr
from postgres_queries import run_queries
from rast_to_vec_grid import rasttovecgrid
from postgres_to_shp import psqltoshp
from postgres_to_shp import shptoraster

# ----- ATTENSION ------------------------------------------------------------------------------------------------------
#Before running this script and database named raster_batabase scould be created in postgres with a postgis extension.
#Furthermore, the Project_data folder, containing the data and a Temp folder containing a Data_from_postgres folder scould
# be created. and the scripts should be placed in the same folder as the Project_data and Temp folder.

# ----- Specify country to extract data from ---------------------------------------------------------------------------
country = 'Denmark'

# ----- Different paths ------------------------------------------------------------------------------------------------
# Get path to script
python_script_dir = os.path.dirname(os.path.abspath(__file__))
#path to ancillary data folder
ancillary_data_folder_path = python_script_dir + "\Project_data\Ancillary_data"
#path to GADM folder
gadm_folder_path = python_script_dir + "\Project_data\GADM"
#path to GHS folder
ghs_folder_path = python_script_dir + "\Project_data\GHS"
#path to temp folder
temp_folder_path = python_script_dir + "\Temp"
#path to data folder to import to postgresql
save_data_path_from_postgres = python_script_dir + "\Temp\Data_from_postgres"
#path to data folder to import to postgresql
finished_data_path = python_script_dir + "\Finished_data"
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'C:\Users\thoma\Anaconda3\envs\kandidat\Scripts'

# ---------------------------------------------------------------------------------------------------------------------
# ----- Extracting country from GADM and creating bounding box -----

# select country in GADM and write to new file
input_gadm_dataset = gadm_folder_path + "\gadm28_adm0.shp"
output_country_shp = temp_folder_path + "\GADM_{0}.shp".format(country)
sql_statement = "NAME_ENGLI='{0}'".format(country)
country_shp = 'ogr2ogr -where {0} -f "ESRI Shapefile"  {1} {2} -lco ENCODING=UTF-8'\
    .format(sql_statement, output_country_shp, input_gadm_dataset)
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
outShapefile = temp_folder_path + "\extent_{0}.shp".format(country)
outDriver = ogr.GetDriverByName("ESRI Shapefile")

# Remove output shapefile if it already exists
if os.path.exists(outShapefile):
    outDriver.DeleteDataSource(outShapefile)

# Create the output shapefile
outDataSource = outDriver.CreateDataSource(outShapefile)
outLayer = outDataSource.CreateLayer("extent_{0}".format(country), geom_type=ogr.wkbPolygon)

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
file = open(temp_folder_path + '\extent_{0}.prj'.format(country), 'w')
file.write(spatialRef.ExportToWkt())
file.close()


# # ----- Recalculating coordinate extent of bbox to match ghs pixels and clipping ghs raster layers -------------------
for subdir, dirs, files in os.walk(ghs_folder_path):
    for file in files:
        if file.endswith(".tif"):
            name = file.split(".tif")[0]

            ghs_file_path = os.path.join(subdir, file)
            out_file_path = temp_folder_path + "\{0}_{1}.tif".format(name, country)
            country_mask = temp_folder_path + "\GADM_{0}.shp".format(country)

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

                cmd_clip = 'gdalwarp -te {0} {1} {2} {3} -tr {4} {5} -cutline {6} -srcnodata -3.4028234663852886e+38 \
                            -dstnodata 0 {7} {8}'.format(
                str(left), str(bottom), str(right), str(top), str(abs(gt[1])), str(abs(gt[5])),
                country_mask, ghs_file_path, out_file_path)
                subprocess.call(cmd_clip, shell=True)

                ft = lyr.GetNextFeature()
            ds = None


# ----- Clipping slope, altering resolution to match ghs pop and recalculating slope values ----------------------------
#Getting extent of ghs pop raster
data = gdal.Open(temp_folder_path + "\GHS_POP_1975_{0}.tif".format(country))
wkt = data.GetProjection()
geoTransform = data.GetGeoTransform()
minx = geoTransform[0]
maxy = geoTransform[3]
maxx = minx + geoTransform[1] * data.RasterXSize
miny = maxy + geoTransform[5] * data.RasterYSize
#print(minx, miny, maxx, maxy)
data = None

# Clipping slope and altering resolution
cutlinefile = temp_folder_path + "\GADM_{0}.shp".format(country)
srcfile = ancillary_data_folder_path +"\slope\slope_europe.tif"
dstfile = temp_folder_path + "\slope_250_{0}.tif".format(country)
cmds = 'gdalwarp -s_srs EPSG:54009 -tr 250 250 -te {0} {1} {2} {3} -cutline {4} -srcnodata 255 -dstnodata 0 {5} {6}'\
    .format(minx, miny, maxx, maxy, cutlinefile, srcfile, dstfile)
subprocess.call(cmds, shell=True)

# Recalculate slope raster values of 0 - 250 to real slope value 0 to 90 degrees
outfile = temp_folder_path + "\slope_{0}_finished_vers.tif".format(country)
cmds = 'python {0}\gdal_calc.py -A {1} --outfile={2} --calc="numpy.arcsin((250-(A))/250)*180/numpy.pi" --NoDataValue=0'\
    .format(python_scripts_folder_path, dstfile, outfile)
subprocess.call(cmds, shell=False)


# ----- clipping lakes layer to country --------------------------------------------------------------------------------
clip_poly = temp_folder_path + "\extent_{0}.shp".format(country)
in_shp = ancillary_data_folder_path + "\eu_lakes.shp"
out_shp = temp_folder_path + "\eu_lakes_{0}.shp".format(country)
cmd_shp_clip = "ogr2ogr -clipsrc {0} {1} {2} -nlt geometry".format(clip_poly, out_shp, in_shp)
subprocess.call(cmd_shp_clip, shell=True)

# ----- Creating polygon grid that matches the population grid ---------------------------------------------------------
outpath = temp_folder_path + "\{0}_2015vector.shp".format(country)
rasttovecgrid(outpath, minx, maxx, miny, maxy, 250, 250)

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
os.environ['PATH'] = r';C:\Program Files\PostgreSQL\9.5\bin'
os.environ['PGHOST'] = 'localhost'
os.environ['PGPORT'] = '5432'
os.environ['PGUSER'] = 'postgres'
os.environ['PGPASSWORD'] = 'postgres'
os.environ['PGDATABASE'] = 'raster_database'

# Loading vector grid into postgresql
gridpath = temp_folder_path + "\{0}_2015vector.shp".format(country)
cmds = 'ogr2ogr --config PG_USE_COPY YES -gt 65536 -f PGDump /vsistdout/ \
{0} -a_srs "EPSG:54009" -lco GEOMETRY_NAME=geom -lco SCHEMA=public -lco \
CREATE_SCHEMA=OFF -lco SPATIAL_INDEX=OFF | psql'.format(gridpath)
subprocess.call(cmds, shell=True)

# Loading pop raster 2015 into postgres
poprastpath = temp_folder_path + "\GHS_POP_2015_{0}.tif".format(country)
cmd = 'raster2pgsql -I -C -s 54009 {0} public.{1}_2015 | psql'.format(poprastpath, country)
subprocess.call(cmd, shell=True)

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

#----- Running postgres queries ----------------------------------------------------------------------------------------
run_queries(country)

#----- Export layers from postgres to shp ------------------------------------------------------------------------------
#psqltoshp(country, save_data_path_from_postgres)

#----- Rasterize layers from postgres ----------------------------------------------------------------------------------
#Skal laves når vi har en holdbar løsning mht frankrig
#shptoraster()

#----- Merging all ghs files into one multiband raster -----------------------------------------------------------------
#outfile = temp_folder_path + "\MERGED_POP_Denmark.tif"
#file1 = temp_folder_path + "\GHS_POP_1975_Denmark.tif"
#file2 = temp_folder_path + "\GHS_POP_1990_Denmark.tif"
#file3 = temp_folder_path + "\GHS_POP_2000_Denmark.tif"
#file4 = temp_folder_path + "\GHS_POP_2015_Denmark.tif"
# cmd_tif_merge = "python {0}\gdal_merge.py -o {1} -separate {2} {3} {4} {5}"\
#     .format(python_scripts_folder_path, outfile, file1, file2, file3, file4)
#subprocess.call(cmd_tif_merge, shell=False)