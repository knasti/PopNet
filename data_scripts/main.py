# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
from process import process_data

# ATTENSION ------------------------------------------------------------------------------------------------------------
# Before running this script, a database should be created in postgres and the database information entered below, if
# it's not the same. Furthermore, the Project_data folder, scound be placed in the same folder as the scripts
# (main, process, import_to_postgres, postgres_to_shp, postgres_queries and rast_to_vec_grid)

# Folder strudture:
# scripts
# Project_data

# Specify country to extract data from ---------------------------------------------------------------------------------
country = 'France'

# choose processes to run ----------------------------------------------------------------------------------------------
# Initial preparation of Population raster and slope ("yes" / "no")
init_prep = "yes"
#Import data to postgres? ("yes" / "no")
init_import_to_postgres = "yes"
# Run postgres queries? ("yes" / "no")
init_run_queries = "yes"
# calculate multiple train buffers? (dict{'column_name':biffersize in meters} or one ("yes", buffersize in meters)?
#multiple_train = "yes"
#multiple_train_dict = {'station2':2000, 'station5':5000, 'station10':10000, 'station20':20000}
#one_train_buffer = "yes", 10000

# export data from postgres? ("yes" / "no")
init_export_data = "yes"
# rasterize data from postgres? ("yes" / "no")
init_rasterize_data = "yes"
# Merge data from postgres? ("yes" / "no")
init_merge_data = "yes"

# Specify database information -----------------------------------------------------------------------------------------
# path to postgresql bin folder
pgpath = r';C:\Program Files\PostgreSQL\9.5\bin'
pghost = 'localhost'
pgport = '5432'
pguser = 'postgres'
pgpassword = 'postgres'
pgdatabase = 'raster_database'

# DIFFERENT PATHS ------------------------------------------------------------------------------------------------------
# Get path to main script
python_script_dir = os.path.dirname(os.path.abspath(__file__))

# Paths for the data / folders in the Project_data folder --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path = python_script_dir + "\Project_data\Ancillary_data"
#path to GADM folder
gadm_folder_path = python_script_dir + "\Project_data\GADM"
#path to GHS folder
ghs_folder_path = python_script_dir + "\Project_data\GHS"

# Paths to storage during the data preparation (AUTOMATICALLY CREATED) -------------------------------------------------
#path to temp folder - will contain temporary files
temp_folder_path = python_script_dir + "\Temp"
#Files to be merged folder
merge_folder_path = python_script_dir + "\Tif_to_merge"
#path to data folder to store the final tif files
finished_data_path = python_script_dir + "\Finished_data"

# Other Paths to necessary python scripts and functions ----------------------------------------------------------------
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'C:\Users\thoma\Anaconda3\envs\kandidat\Scripts'
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'C:\Users\thoma\Anaconda3\envs\kandidat\lib\site-packages\osgeo'

# Process all data -----------------------------------------------------------------------------------------------------
process_data(country, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path,
             gadm_folder_path, ghs_folder_path, temp_folder_path, merge_folder_path, finished_data_path,
             python_scripts_folder_path, gdal_rasterize_path, init_prep, init_import_to_postgres, init_run_queries,
             init_export_data, init_rasterize_data, init_merge_data)