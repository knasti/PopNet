# ----- merging tif files with ancillary data, creating more bands -----
# imports
import os
import subprocess
import gdal
# --- paths to files ---
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

# iterating through tif files
for raster in os.listdir(postgres_import_data_path):
    if raster.endswith(".tif"):
        name = raster.split(".tif")[0]
        raster = os.path.join(postgres_import_data_path, raster)


        # test: merging all ghs files into one multiband raster
        gdal_merge = r'C:\Users\thoma\Anaconda3\envs\kandidat\Scripts'
        outfile = postgres_import_data_path + "\{0}_merged.tif".format(name)
        # water layer path
        water_path = temp_folder_path +"\denmark_watercover.tif"
        # distance path
        dist_path = temp_folder_path +"\denmark_road.tif"
        # file1 = postgres_import_data_path + "\GHS_POP_1975_Denmark.tif"
        # file2 = postgres_import_data_path + "\GHS_POP_1990_Denmark.tif"
        # file3 = postgres_import_data_path + "\GHS_POP_2000_Denmark.tif"
        # file4 = postgres_import_data_path + "\GHS_POP_2015_Denmark.tif"

        cmd_tif_merge = "python {0}\gdal_merge.py -o {1} -separate {2} {3} {4}".format(gdal_merge, outfile, raster, water_path, dist_path)
        subprocess.call(cmd_tif_merge, shell=False)