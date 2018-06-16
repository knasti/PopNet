from osgeo import gdal
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

geotif_2020 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2020.tif')
# geotif_2030 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2030.tif')
# geotif_2040 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2040.tif')
geotif_2050 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2050.tif')
# geotif_2060 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2060.tif')
# geotif_2070 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2070.tif')
# geotif_2080 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2080.tif')
# geotif_2090 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2090.tif')
geotif_2100 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2100.tif')

np_2020 = np.array(geotif_2020.GetRasterBand(1).ReadAsArray()).flatten()
# np_2030 = np.array(geotif_2030.GetRasterBand(1).ReadAsArray()).flatten()
# np_2040 = np.array(geotif_2040.GetRasterBand(1).ReadAsArray()).flatten()
np_2050 = np.array(geotif_2050.GetRasterBand(1).ReadAsArray()).flatten()
# np_2060 = np.array(geotif_2060.GetRasterBand(1).ReadAsArray()).flatten()
# np_2070 = np.array(geotif_2070.GetRasterBand(1).ReadAsArray()).flatten()
# np_2080 = np.array(geotif_2080.GetRasterBand(1).ReadAsArray()).flatten()
# np_2090 = np.array(geotif_2090.GetRasterBand(1).ReadAsArray()).flatten()
np_2100 = np.array(geotif_2100.GetRasterBand(1).ReadAsArray()).flatten()

# Without zeros



population = np.concatenate((np_2020, np_2050))
year = np.concatenate((np.full(np_2020.shape, '2020'), np.full(np_2050.shape, '2050')))
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
population = np.concatenate((population, np_2100))
year = np.concatenate((year, np.full(np_2100.shape, '2100')))

df = pd.DataFrame({'Population': population, 'Year': year})
df['Categories'] = df['Population']

df = df[df['Population'] > 1]

df.loc[(df.Categories > 0) & (df.Categories < 51), 'Categories'] = 1
df.loc[(df.Categories > 51) & (df.Categories < 101), 'Categories'] = 2
df.loc[(df.Categories > 101) & (df.Categories < 251), 'Categories'] = 3
df.loc[(df.Categories > 251) & (df.Categories < 500), 'Categories'] = 4
df.loc[df.Categories > 500, 'Categories'] = 5

df.loc[df.Categories == 1, 'Categories'] = '0 - 50'
df.loc[df.Categories == 2, 'Categories'] = '51 - 100'
df.loc[df.Categories == 3, 'Categories'] = '101 - 250'
df.loc[df.Categories == 4, 'Categories'] = '251 - 500'
df.loc[df.Categories == 5, 'Categories'] = '500+'


sns.set(style='whitegrid')
fig = plt.figure()
ax = sns.countplot(x="Categories", hue="Year", data=df, order=['0 - 50', '51 - 100', '101 - 250', '251 - 500', '500+'])
ax.set_xlabel('Population intervals')
ax.set_ylabel('No. of cells')
plt.savefig('count_plot.png', bbox_inches='tight')
plt.show()

