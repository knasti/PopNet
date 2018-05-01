# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
from process import process_data

# ATTENSION ------------------------------------------------------------------------------------------------------------
# Before running this script, a database should be created in postgres with a postgis extension and the database
# information entered below. Furthermore, the Project_data folder, containing the data and a Temp folder containing a
# Data_from_postgres folder should be created. The scripts (main, process, import_to_postgres, postgres_to_shp,
# postgres_queries and rast_to_vec_grid) should be placed in the same folder as the Project_data and Temp folder.

# Specify country to extract data from ---------------------------------------------------------------------------------
country = 'Denmark'

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

# Paths for the data / folders in Project_data -------------------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path = python_script_dir + "\Project_data\Ancillary_data"
#path to GADM folder
gadm_folder_path = python_script_dir + "\Project_data\GADM"
#path to GHS folder
ghs_folder_path = python_script_dir + "\Project_data\GHS"

# Paths to storage during the data preparation (AUTOMATICALLY CREATED) -------------------------------------------------
#path to temp folder - will contain temporary files
temp_folder_path = python_script_dir + "\Temp"
#path to data folder to save data from postgresql
save_data_path_from_postgres = python_script_dir + "\Temp\Data_from_postgres"
#path to data folder to store the final tif files
finished_data_path = python_script_dir + "\Finished_data"

# Other Paths to necessary python scripts and functions ----------------------------------------------------------------
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'C:\Users\thoma\Anaconda3\envs\kandidat\Scripts'
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'C:\Users\thoma\Anaconda3\envs\kandidat\lib\site-packages\osgeo'


# Process all data -----------------------------------------------------------------------------------------------------
process_data(country, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase,
             ancillary_data_folder_path, gadm_folder_path, ghs_folder_path,
             temp_folder_path, save_data_path_from_postgres, finished_data_path,
             python_scripts_folder_path, gdal_rasterize_path)