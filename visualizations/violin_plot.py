from osgeo import gdal
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

country = 'denmark'

if country == 'france':
    geotif_2015 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\data\france\2015.tif')
    geotif_2020 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2020.tif')
    geotif_2030 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2030.tif')
    geotif_2040 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2040.tif')
    geotif_2050 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2050.tif')
    geotif_2060 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2060.tif')
    geotif_2070 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2070.tif')
    geotif_2080 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2080.tif')
    geotif_2090 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2090.tif')
    geotif_2100 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2100.tif')
if country == 'denmark':
    # geotif_2015 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\data\denmark\2015.tif')
    # geotif_2020_fr = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_fr\bbox_pred_2020.tif')
    # geotif_2030_fr = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_fr\bbox_pred_2030.tif')
    # geotif_2040_fr = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_fr\bbox_pred_2040.tif')
    # geotif_2050_fr = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_fr\bbox_pred_2050.tif')
    # geotif_2060_fr = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_fr\bbox_pred_2060.tif')
    # geotif_2070_fr = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_fr\bbox_pred_2070.tif')
    # geotif_2080_fr = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_fr\bbox_pred_2080.tif')
    # geotif_2090_fr = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_fr\bbox_pred_2090.tif')
    # geotif_2100_fr = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_fr\bbox_pred_2100.tif')
    #
    # geotif_2020_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_dk\bbox_pred_2020.tif')
    # geotif_2030_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_dk\bbox_pred_2030.tif')
    # geotif_2040_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_dk\bbox_pred_2040.tif')
    # geotif_2050_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_dk\bbox_pred_2050.tif')
    # geotif_2060_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_dk\bbox_pred_2060.tif')
    # geotif_2070_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_dk\bbox_pred_2070.tif')
    # geotif_2080_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_dk\bbox_pred_2080.tif')
    # geotif_2090_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_dk\bbox_pred_2090.tif')
    # geotif_2100_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\france_model\outputs\comparison_dk\bbox_pred_2100.tif')
    geotif_2015 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\data\denmark\2015.tif')
    geotif_2020_lake = gdal.Open(
        r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\road\outputs\bbox\bbox_pred_2020.tif')
    geotif_2050_lake = gdal.Open(
        r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\road\outputs\bbox\bbox_pred_2050.tif')
    geotif_2100_lake = gdal.Open(
        r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\road\outputs\bbox\bbox_pred_2100.tif')

    geotif_2020_fin = gdal.Open(
        r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\outputs\bbox\bbox_pred_2020.tif')
    geotif_2050_fin = gdal.Open(
        r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\outputs\bbox\bbox_pred_2050.tif')
    geotif_2100_fin = gdal.Open(
        r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\outputs\bbox\bbox_pred_2100.tif')
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

    # geotif_2020_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2020.tif')
    # geotif_2030_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2030.tif')
    # geotif_2040_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2040.tif')
    # geotif_2050_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2050.tif')
    # geotif_2060_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2060.tif')
    # geotif_2070_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2070.tif')
    # geotif_2080_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2080.tif')
    # geotif_2090_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2090.tif')
    # geotif_2100_dk = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\denmark\final\pred_2100.tif')

# np_2015_fr = np.array(geotif_2015_fr.GetRasterBand(1).ReadAsArray()).flatten()
# np_2020_fr = np.array(geotif_2020_fr.GetRasterBand(1).ReadAsArray()).flatten()
# np_2030_fr = np.array(geotif_2030_fr.GetRasterBand(1).ReadAsArray()).flatten()
# np_2040_fr = np.array(geotif_2040_fr.GetRasterBand(1).ReadAsArray()).flatten()
# np_2050_fr = np.array(geotif_2050_fr.GetRasterBand(1).ReadAsArray()).flatten()
# np_2060_fr = np.array(geotif_2060_fr.GetRasterBand(1).ReadAsArray()).flatten()
# np_2070_fr = np.array(geotif_2070_fr.GetRasterBand(1).ReadAsArray()).flatten()
# np_2080_fr = np.array(geotif_2080_fr.GetRasterBand(1).ReadAsArray()).flatten()
# np_2090_fr = np.array(geotif_2090_fr.GetRasterBand(1).ReadAsArray()).flatten()
# np_2100_fr = np.array(geotif_2100_fr.GetRasterBand(1).ReadAsArray()).flatten()

# np_2020_dk = np.array(geotif_2020_dk.GetRasterBand(1).ReadAsArray()).flatten()
# np_2030_dk = np.array(geotif_2030_dk.GetRasterBand(1).ReadAsArray()).flatten()
# np_2040_dk = np.array(geotif_2040_dk.GetRasterBand(1).ReadAsArray()).flatten()
# np_2050_dk = np.array(geotif_2050_dk.GetRasterBand(1).ReadAsArray()).flatten()
# np_2060_dk = np.array(geotif_2060_dk.GetRasterBand(1).ReadAsArray()).flatten()
# np_2070_dk = np.array(geotif_2070_dk.GetRasterBand(1).ReadAsArray()).flatten()
# np_2080_dk = np.array(geotif_2080_dk.GetRasterBand(1).ReadAsArray()).flatten()
# np_2090_dk = np.array(geotif_2090_dk.GetRasterBand(1).ReadAsArray()).flatten()
# np_2100_dk = np.array(geotif_2100_dk.GetRasterBand(1).ReadAsArray()).flatten()

# print(np.max(np_2015))
# print(np.max(np_2020))
# print(np.max(np_2030))
# print(np.max(np_2040))
# print(np.max(np_2050))
# print(np.max(np_2060))
# print(np.max(np_2070))
# print(np.max(np_2080))
# print(np.max(np_2090))
# print(np.max(np_2100))

# population = np.concatenate((np_2020_fr, np_2030_fr))
# year = np.concatenate((np.full(np_2020_fr.shape, '2020'), np.full(np_2030_fr.shape, '2030')))
# country = np.concatenate((np.full(np_2020_fr.shape, 'France'), np.full(np_2030_fr.shape, 'France')))
#
# population = np.concatenate((population, np_2040_fr))
# year = np.concatenate((year, np.full(np_2040_fr.shape, '2040')))
# country = np.concatenate((country, np.full(np_2040_fr.shape, 'France')))
#
# population = np.concatenate((population, np_2050_fr))
# year = np.concatenate((year, np.full(np_2050_fr.shape, '2050')))
# country = np.concatenate((country, np.full(np_2050_fr.shape, 'France')))
#
# population = np.concatenate((population, np_2060_fr))
# year = np.concatenate((year, np.full(np_2060_fr.shape, '2060')))
# country = np.concatenate((country, np.full(np_2060_fr.shape, 'France')))
#
# population = np.concatenate((population, np_2070_fr))
# year = np.concatenate((year, np.full(np_2070_fr.shape, '2070')))
# country = np.concatenate((country, np.full(np_2070_fr.shape, 'France')))
#
# population = np.concatenate((population, np_2080_fr))
# year = np.concatenate((year, np.full(np_2080_fr.shape, '2080')))
# country = np.concatenate((country, np.full(np_2080_fr.shape, 'France')))
#
# population = np.concatenate((population, np_2090_fr))
# year = np.concatenate((year, np.full(np_2090_fr.shape, '2090')))
# country = np.concatenate((country, np.full(np_2090_fr.shape, 'France')))
#
# population = np.concatenate((population, np_2100_fr))
# year = np.concatenate((year, np.full(np_2100_fr.shape, '2100')))
# country = np.concatenate((country, np.full(np_2100_fr.shape, 'France')))
#
# population = np.concatenate((population, np_2020_dk))
# year = np.concatenate((year, np.full(np_2020_dk.shape, '2020')))
# country = np.concatenate((country, np.full(np_2020_dk.shape, 'Denmark')))
#
# population = np.concatenate((population, np_2030_dk))
# year = np.concatenate((year, np.full(np_2030_dk.shape, '2030')))
# country = np.concatenate((country, np.full(np_2030_dk.shape, 'Denmark')))
#
# population = np.concatenate((population, np_2040_dk))
# year = np.concatenate((year, np.full(np_2040_dk.shape, '2040')))
# country = np.concatenate((country, np.full(np_2040_dk.shape, 'Denmark')))
#
# population = np.concatenate((population, np_2050_dk))
# year = np.concatenate((year, np.full(np_2050_dk.shape, '2050')))
# country = np.concatenate((country, np.full(np_2050_dk.shape, 'Denmark')))
#
# population = np.concatenate((population, np_2060_dk))
# year = np.concatenate((year, np.full(np_2060_dk.shape, '2060')))
# country = np.concatenate((country, np.full(np_2060_dk.shape, 'Denmark')))
#
# population = np.concatenate((population, np_2070_dk))
# year = np.concatenate((year, np.full(np_2070_dk.shape, '2070')))
# country = np.concatenate((country, np.full(np_2070_dk.shape, 'Denmark')))
#
# population = np.concatenate((population, np_2080_dk))
# year = np.concatenate((year, np.full(np_2080_dk.shape, '2080')))
# country = np.concatenate((country, np.full(np_2080_dk.shape, 'Denmark')))
#
# population = np.concatenate((population, np_2090_dk))
# year = np.concatenate((year, np.full(np_2090_dk.shape, '2090')))
# country = np.concatenate((country, np.full(np_2090_dk.shape, 'Denmark')))
#
# population = np.concatenate((population, np_2100_dk))
# year = np.concatenate((year, np.full(np_2100_dk.shape, '2100')))
# country = np.concatenate((country, np.full(np_2100_dk.shape, 'Denmark')))
#
# print(population.shape)
# print(year.shape)

population = np.concatenate((np_2020_lake, np_2050_lake))
year = np.concatenate((np.full(np_2020_lake.shape, '2020'), np.full(np_2050_lake.shape, '2050')))
scenario = np.concatenate((np.full(np_2020_lake.shape, 'With road'), np.full(np_2050_lake.shape, 'With road')))
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
scenario = np.concatenate((scenario, np.full(np_2100_lake.shape, 'With road')))

population = np.concatenate((population, np_2020_fin))
year = np.concatenate((year, np.full(np_2020_fin.shape, '2020')))
scenario = np.concatenate((scenario, np.full(np_2100_fin.shape, 'Original')))

population = np.concatenate((population, np_2050_fin))
year = np.concatenate((year, np.full(np_2050_fin.shape, '2050')))
scenario = np.concatenate((scenario, np.full(np_2050_fin.shape, 'Original')))

population = np.concatenate((population, np_2100_fin))
year = np.concatenate((year, np.full(np_2100_fin.shape, '2100')))
scenario = np.concatenate((scenario, np.full(np_2100_fin.shape, 'Original')))

df = pd.DataFrame({'Population': population, 'Year': year, 'Scenario': scenario})
df['Categories'] = df['Population']



# df = df[df['Population'] > 1]


sns.set(style='whitegrid')
fig = plt.figure()
ax = sns.violinplot(x=df["Year"], y=df["Population"], hue=df["Scenario"], palette='Set1', cut=0, split=True, legend=False)
ax.set_title('Population Distribution - Road Scenario', fontsize=16)
plt.legend(loc='upper left')
# ax.set_ylim(10, np.max(population) + 100)
plt.savefig('violin_plot.png', bbox_inches='tight')
plt.show()
plt.clf()
plt.close()
