from osgeo import gdal
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


country = 'france'
if country == 'france':
    geotif_2015 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\data\france\2015.tif')
    geotif_2020 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2020.tif')
    # geotif_2030 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2030.tif')
    # geotif_2040 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2040.tif')
    geotif_2050 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2050.tif')
    # geotif_2060 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2060.tif')
    # geotif_2070 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2070.tif')
    # geotif_2080 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2080.tif')
    # geotif_2090 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2090.tif')
    geotif_2100 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2100.tif')
elif country == 'denmark':
    geotif_2015 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\data\denmark\2015.tif')
    geotif_2020_lake = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\lake\outputs\bbox\bbox_pred_2020.tif')
    geotif_2050_lake = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\lake\outputs\bbox\bbox_pred_2050.tif')
    geotif_2100_lake = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\lake\outputs\bbox\bbox_pred_2100.tif')

    geotif_2020_fin = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\outputs\bbox\bbox_pred_2020.tif')
    geotif_2050_fin = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\outputs\bbox\bbox_pred_2050.tif')
    geotif_2100_fin = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\outputs\bbox\bbox_pred_2100.tif')
    # geotif_2030 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2030.tif')
    # geotif_2040 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2040.tif')
    geotif_2050 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2050.tif')
    # geotif_2060 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2060.tif')
    # geotif_2070 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2070.tif')
    # geotif_2080 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2080.tif')
    # geotif_2090 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2090.tif')
    geotif_2100 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2100.tif')

# np_2015 = np.array(geotif_2015.GetRasterBand(1).ReadAsArray()).flatten()
np_2020_lake = np.array(geotif_2020_lake.GetRasterBand(1).ReadAsArray()).flatten()
# np_2030 = np.array(geotif_2030.GetRasterBand(1).ReadAsArray()).flatten()
# np_2040 = np.array(geotif_2040.GetRasterBand(1).ReadAsArray()).flatten()
np_2050_lake = np.array(geotif_2050_lake.GetRasterBand(1).ReadAsArray()).flatten()
# np_2060 = np.array(geotif_2060.GetRasterBand(1).ReadAsArray()).flatten()
# np_2070 = np.array(geotif_2070.GetRasterBand(1).ReadAsArray()).flatten()
# np_2080 = np.array(geotif_2080.GetRasterBand(1).ReadAsArray()).flatten()
# np_2090 = np.array(geotif_2090.GetRasterBand(1).ReadAsArray()).flatten()
np_2100_lake = np.array(geotif_2100_lake.GetRasterBand(1).ReadAsArray()).flatten()

np_2020_fin = np.array(geotif_2020_fin.GetRasterBand(1).ReadAsArray()).flatten()
np_2050_fin = np.array(geotif_2050_fin.GetRasterBand(1).ReadAsArray()).flatten()
np_2100_fin = np.array(geotif_2100_fin.GetRasterBand(1).ReadAsArray()).flatten()

# Without zeros



population = np.concatenate((np_2020_lake, np_2050_lake))
year = np.concatenate((np.full(np_2020_lake.shape, '2015'), np.full(np_2050_lake.shape, '2050')))
scenario = np.concatenate((np.full(np_2020_lake.shape, 'With lake'), np.full(np_2050_lake.shape, 'With lake')))
# population = np.concatenate((population, np_2040))
# year = np.concatenate((year, np.full(np_2040.shape, '2040')))
# population = np.concatenate((population, np_2050))
# year = np.concatenate((year, np.full(np_2050.shape, '2050')))
# population = np.concatenate((population, np_2060))
# year = np.concatenate((year, np.full(np_2060.shape, '2060')))
# population = np.concatenate((population, np_2070))
# year = np.concatenate((year, np.full(np_2070.shape, '2070')))
# population = np.concatenate((population, np_2080))
# year = np.concatenate((year, np.full(np_2080.shape, '2080')))
# population = np.concatenate((population, np_2090))
# year = np.concatenate((year, np.full(np_2090.shape, '2090')))
population = np.concatenate((population, np_2100_lake))
year = np.concatenate((year, np.full(np_2100_lake.shape, '2100')))
scenario = np.concatenate((scenario, np.full(np_2100_lake.shape, 'With lake')))


population = np.concatenate((population, np_2020_fin))
year = np.concatenate((year, np.full(np_2020_fin.shape, '2020')))
scenario = np.concatenate((scenario, np.full(np_2100_fin.shape, 'Original')))

population = np.concatenate((population, np_2050_fin))
year = np.concatenate((year, np.full(np_2050_fin.shape, '2050')))
scenario = np.concatenate((scenario, np.full(np_2050_fin.shape, 'Original')))

population = np.concatenate((population, np_2100_fin))
year = np.concatenate((year, np.full(np_2100_fin.shape, '2100')))
scenario = np.concatenate((scenario, np.full(np_2100_fin.shape, 'Original')))

df = pd.DataFrame({'Population': population, 'Year': year})
df['Categories'] = df['Population']

df = df[df['Population'] > 1]

df.loc[(df.Categories > 0) & (df.Categories < 51), 'Categories'] = 1
df.loc[(df.Categories > 51) & (df.Categories < 101), 'Categories'] = 2
df.loc[(df.Categories > 101) & (df.Categories < 251), 'Categories'] = 3
df.loc[(df.Categories > 251) & (df.Categories < 500), 'Categories'] = 4
df.loc[df.Categories > 500, 'Categories'] = 5

df.loc[df.Categories == 1, 'Categories'] = '1 - 50'
df.loc[df.Categories == 2, 'Categories'] = '51 - 100'
df.loc[df.Categories == 3, 'Categories'] = '101 - 250'
df.loc[df.Categories == 4, 'Categories'] = '251 - 500'
df.loc[df.Categories == 5, 'Categories'] = '500+'


sns.set(style='whitegrid')
# sns.set_palette(sns.color_palette('husl', 6))
fig = plt.figure()
ax = sns.countplot(x="Categories", hue="Year", data=df, order=['1 - 50', '51 - 100', '101 - 250', '251 - 500', '500+'], palette='Set1')
ax.set_xlabel('Population intervals')
ax.set_ylabel('No. of cells')
ax.set_title('Population Development - France', fontsize=16)
plt.savefig('count_plot.png', bbox_inches='tight')
plt.show()

