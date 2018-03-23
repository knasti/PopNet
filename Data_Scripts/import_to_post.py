import psycopg2
import subprocess
import sys,os
#import shapefile
#import fiona
import gdal
import ogr
import osr
from shutil import *

gdal.UseExceptions()

# ------ IMPORT SCRIPT FOR POSTGRESQL ------

# Specify Country to import
country = "Denmark"

# Specify Reference System
refsys = 54009

#Set no data value for the rasters
no_data_value = "0"

#Delete TEMP folder when import is finished (yes/no)
del_temp = "no"

# ----input path to "Project_data" folder (Project_data folder placed in same folder as script)----
# Content and structure of Project_data folder should be:
#Ancillary_data folder
#GADM folder
#GHS folder
#Temp folder - for produced data (created in same folder as this script)

# Get path to script
python_script_dir = os.path.dirname(os.path.abspath(__file__))
#Path to data folder
data_folder_path = python_script_dir + "\Project_data"
#path to temp folder
temp_folder_path = python_script_dir + "\Temp"

# ---------------------------------------------------------------------------------------------------------------------
# -----Converting all data to the same reference system-----
# Converting shapefiles:
# Iterating through folders and files in project_data folder
for subdir, dirs, files in os.walk(data_folder_path):
    for file in files:
        # if file.endswith(".shp"):
        #     name = file.split(".shp")[0]
        #     file_path = os.path.join(subdir, file)
        #     print(name)
        #     print(file_path)
        #
        #     driver = ogr.GetDriverByName('ESRI Shapefile')
        #     dataset = driver.Open(file_path)
        #
        #     # from Layer
        #     layer = dataset.GetLayer()
        #     spatialRef = layer.GetSpatialRef()
        #     print(spatialRef)
        #     # Get layer epsg number
        #
        #     in_epsg = int(spatialRef.GetAttrValue('Authority', 1))
        #     print(in_epsg)
        #     out_epsg = refsys
        #     in_shp = file_path
        #     out_shp = temp_folder_path
        #
        #     driver = ogr.GetDriverByName('ESRI Shapefile')
        #
        #     # input SpatialReference
        #     inSpatialRef = osr.SpatialReference()
        #     inSpatialRef.ImportFromEPSG(in_epsg)
        #
        #     # output SpatialReference
        #     outSpatialRef = osr.SpatialReference()
        #     outSpatialRef.ImportFromEPSG(out_epsg)
        #
        #     # create the CoordinateTransformation
        #     coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        #
        #     # get the input layer
        #     inDataSet = driver.Open(in_shp)
        #     inLayer = inDataSet.GetLayer()
        #
        #     # create the output layer
        #     if os.path.exists(out_shp):
        #         driver.DeleteDataSource(out_shp)
        #     outDataSet = driver.CreateDataSource(out_shp)
        #     outLayer = outDataSet.CreateLayer(name, geom_type=ogr.wkbMultiPolygon)
        #
        #     # add fields
        #     inLayerDefn = inLayer.GetLayerDefn()
        #     for i in range(0, inLayerDefn.GetFieldCount()):
        #         fieldDefn = inLayerDefn.GetFieldDefn(i)
        #         outLayer.CreateField(fieldDefn)
        #
        #     # get the output layer's feature definition
        #     outLayerDefn = outLayer.GetLayerDefn()
        #
        #     # loop through the input features
        #     inFeature = inLayer.GetNextFeature()
        #     while inFeature:
        #         # get the input geometry
        #         geom = inFeature.GetGeometryRef()
        #         # reproject the geometry
        #         geom.Transform(coordTrans)
        #         # create a new feature
        #         outFeature = ogr.Feature(outLayerDefn)
        #         # set the geometry and attribute
        #         outFeature.SetGeometry(geom)
        #         for i in range(0, outLayerDefn.GetFieldCount()):
        #             outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        #         # add the feature to the shapefile
        #         outLayer.CreateFeature(outFeature)
        #         # dereference the features and get the next input feature
        #         outFeature = None
        #         inFeature = inLayer.GetNextFeature()
        #
        #     # Save and close the shapefiles
        #     inDataSet = None
        #     outDataSet = None
        #     print("Done")
        #
        #     # create the prj projection file
        #     outSpatialRef.MorphToESRI()
        #     file = open(temp_folder_path + '\\' + name + '.prj', 'w')
        #     file.write(outSpatialRef.ExportToWkt())
        #     file.close()

            # Converting Raster files
        if file.endswith(".tif"):
            name = file.split(".tif")[0]
            file_path = os.path.join(subdir, file)
            out_file_path = os.path.join(temp_folder_path, name) + ".tif"
            print(name)
            print(file_path)
            print(out_file_path)

            rasterdata = gdal.Open(file_path)
            proj = osr.SpatialReference(wkt=rasterdata.GetProjection())

            if proj.GetAttrValue('PROJCS', 0) == "World_Mollweide" and 54009 == refsys:
                copyfile(file_path, out_file_path)
            elif proj.GetAttrValue('PROJCS', 0) == "World_Mollweide" and 54009 != refsys:
                gdal.Warp(out_file_path, file_path, dstSRS='EPSG:{0}'.format(refsys))
            elif int(proj.GetAttrValue('AUTHORITY', 1)) == refsys:
                copyfile(file_path, out_file_path)
            else:
                #in_epsg = proj.GetAttrValue('AUTHORITY', 1)
                gdal.Warp(out_file_path, file_path, dstSRS='EPSG:{0}'.format(refsys))





# input_raster = gdal.Open(filename)
# output_raster = r"C:\path\to\output\raster
# gdal.Warp(output_raster,input_raster,dstSRS='EPSG:4326')


# ----- Extracting country from GADM and create bounding box-----
# select country in GADM and write to new file
# input_gadm_world_shp = r"C:\Users\thoma\Desktop\Kandidat\Data\GADM Administrative Area units\gadm28_levels.shp\gadm28_adm0.shp"
# output_country_shp = r"C:\Users\thoma\Desktop\Kandidat\Data\chosendenmark.shp"
# with fiona.open(input_gadm_world_shp) as input:
#     meta = input.meta
#     with fiona.open(output_country_shp, 'w',**meta) as output:
#         for feature in input:
#             if feature['properties']['NAME_ENGLI'] == country:
#                 output.write(feature)

# Create bounding box around chosen country















# sf = shapefile.Reader(input_shp)
#
# fields = sf.fields[1:]
# field_names = [field[0] for field in fields]
# # construction of a dctionary field_name:value
# for r in sf.shapeRecords():
#     atr = dict(zip(field_names, r.record))
#
#     print(atr)


# Clipping Rasters to bounding box
# for raster in os.listdir(input_path):
#     if raster.endswith(".tif"):
#         name = raster.split(".tif")[0]
#         raster = os.path.join(input_path, raster)
#
#         cmds = 'gdalwarp -cutline path/to/states.shp \
#                 -crop_to_cutline -dstnodata {0} \
#                 {1} \
#                 {2}'.format(no_data_value, raster, country)
#         subprocess.call(cmds, shell=True)




# importing data:
#loop through tif files in dir
# for raster in os.listdir(input_path):
#     if raster.endswith(".tif"):
#         name = raster.split(".tif")[0]
#         raster = os.path.join(input_path, raster)
#
#         #Connect to the PostgreSQL server:
#
#         os.environ['PATH'] = r';C:\Program Files\PostgreSQL\9.5\bin'
#         os.environ['PGHOST'] = 'localhost'
#         os.environ['PGPORT'] = '5432'
#         os.environ['PGUSER'] = 'postgres'
#         os.environ['PGPASSWORD'] = 'postgres'
#         os.environ['PGDATABASE'] = 'raster_database'
#
#         rastername = str(name)
#         rasterlayer = rastername.lower()
#
#         conn = psycopg2.connect(database="raster_database", user="postgres", host="localhost", password="postgres")
#         cursor = conn.cursor()
#
#         # Import each raster through raster2pgsql function (coordinate system epsg code is set to 32633 UTM):
#
#         cmds = 'raster2pgsql -s 54009 -I -t auto "' + raster + '" | psql'
#         subprocess.call(cmds, shell=True)


# Deleting Temp folder
if del_temp == "yes":
    shutil.rmtree(r'temp_folder_path')




