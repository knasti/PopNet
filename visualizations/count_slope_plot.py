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
    geotif_2030 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2030.tif')
    geotif_2040 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2040.tif')
    geotif_2050 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2050.tif')
    geotif_2060 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2060.tif')
    geotif_2070 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2070.tif')
    geotif_2080 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2080.tif')
    geotif_2090 = gdal.Open(r'C:\Users\Niels\Documents\GitHub\PopNet\experiments\france\final\pred_2090.tif')
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

np_slope = np.array(geotif_2015.GetRasterBand(4).ReadAsArray()).flatten()
np_2015 = np.array(geotif_2015.GetRasterBand(1).ReadAsArray()).flatten()
np_2020 = np.array(geotif_2020.GetRasterBand(1).ReadAsArray()).flatten()
np_2030 = np.array(geotif_2030.GetRasterBand(1).ReadAsArray()).flatten()
np_2040 = np.array(geotif_2040.GetRasterBand(1).ReadAsArray()).flatten()
np_2050 = np.array(geotif_2050.GetRasterBand(1).ReadAsArray()).flatten()
np_2060 = np.array(geotif_2060.GetRasterBand(1).ReadAsArray()).flatten()
np_2070 = np.array(geotif_2070.GetRasterBand(1).ReadAsArray()).flatten()
np_2080 = np.array(geotif_2080.GetRasterBand(1).ReadAsArray()).flatten()
np_2090 = np.array(geotif_2090.GetRasterBand(1).ReadAsArray()).flatten()
np_2100 = np.array(geotif_2100.GetRasterBand(1).ReadAsArray()).flatten()

# np_2020_fin = np.array(geotif_2020_fin.GetRasterBand(1).ReadAsArray()).flatten()
# np_2050_fin = np.array(geotif_2050_fin.GetRasterBand(1).ReadAsArray()).flatten()
# np_2100_fin = np.array(geotif_2100_fin.GetRasterBand(1).ReadAsArray()).flatten()

# Without zeros


slope = np.concatenate((np_slope, np_slope))
population = np.concatenate((np_2015, np_2020))
year = np.concatenate((np.full(np_2015.shape, '2015'), np.full(np_2020.shape, '2020')))
#scenario = np.concatenate((np.full(np_2020.shape, 'With lake'), np.full(np_2050.shape, 'With lake')))

slope = np.concatenate((slope, np_slope))
population = np.concatenate((population, np_2030))
year = np.concatenate((year, np.full(np_2030.shape, '2030')))

slope = np.concatenate((slope, np_slope))
population = np.concatenate((population, np_2040))
year = np.concatenate((year, np.full(np_2040.shape, '2040')))
slope = np.concatenate((slope, np_slope))
population = np.concatenate((population, np_2050))
year = np.concatenate((year, np.full(np_2050.shape, '2050')))
slope = np.concatenate((slope, np_slope))
population = np.concatenate((population, np_2060))
year = np.concatenate((year, np.full(np_2060.shape, '2060')))
slope = np.concatenate((slope, np_slope))
population = np.concatenate((population, np_2070))
year = np.concatenate((year, np.full(np_2070.shape, '2070')))
slope = np.concatenate((slope, np_slope))
population = np.concatenate((population, np_2080))
year = np.concatenate((year, np.full(np_2080.shape, '2080')))
slope = np.concatenate((slope, np_slope))
population = np.concatenate((population, np_2090))
year = np.concatenate((year, np.full(np_2090.shape, '2090')))
slope = np.concatenate((slope, np_slope))
population = np.concatenate((population, np_2100))
year = np.concatenate((year, np.full(np_2100.shape, '2100')))
# scenario = np.concatenate((scenario, np.full(np_2100.shape, 'With lake')))


# population = np.concatenate((population, np_2020_fin))
# year = np.concatenate((year, np.full(np_2020_fin.shape, '2020')))
# scenario = np.concatenate((scenario, np.full(np_2100_fin.shape, 'Original')))
#
# population = np.concatenate((population, np_2050_fin))
# year = np.concatenate((year, np.full(np_2050_fin.shape, '2050')))
# scenario = np.concatenate((scenario, np.full(np_2050_fin.shape, 'Original')))
#
# population = np.concatenate((population, np_2100_fin))
# year = np.concatenate((year, np.full(np_2100_fin.shape, '2100')))
# scenario = np.concatenate((scenario, np.full(np_2100_fin.shape, 'Original')))

df = pd.DataFrame({'Population': population, 'Year': year, 'Slope': slope})
df['Categories'] = df['Slope']



df = df[df['Population'] > 1]

slopes = []



sum_2015_01 = df[(df['Slope'] >= 0) & (df['Slope'] < 1) & (df['Year'] == '2015')]['Population'].mean()
slopes.append({'Slope': '0 - 1', 'Year': 2015, 'Population': sum_2015_01})
sum_2015_15 = df[(df['Slope'] >= 1) & (df['Slope'] < 5) & (df['Year'] == '2015')]['Population'].mean()
slopes.append({'Slope': '1 - 5', 'Year': 2015, 'Population': sum_2015_15})
sum_2015_510 = df[(df['Slope'] >= 5) & (df['Slope'] < 10) & (df['Year'] == '2015')]['Population'].mean()
slopes.append({'Slope': '5 - 10', 'Year': 2015, 'Population': sum_2015_510})
sum_2015_10 = df[(df['Slope'] >= 10) & (df['Year'] == '2015')]['Population'].mean()
slopes.append({'Slope': '10+', 'Year': 2015, 'Population': sum_2015_10})

sum_2020_01 = df[(df['Slope'] >= 0) & (df['Slope'] < 1) & (df['Year'] == '2020')]['Population'].mean()
slopes.append({'Slope': '0 - 1', 'Year': 2020, 'Population': sum_2020_01})
sum_2020_15 = df[(df['Slope'] >= 1) & (df['Slope'] < 5) & (df['Year'] == '2020')]['Population'].mean()
slopes.append({'Slope': '1 - 5', 'Year': 2020, 'Population': sum_2020_15})
sum_2020_510 = df[(df['Slope'] >= 5) & (df['Slope'] < 10) & (df['Year'] == '2020')]['Population'].mean()
slopes.append({'Slope': '5 - 10', 'Year': 2020, 'Population': sum_2020_510})
sum_2020_10 = df[(df['Slope'] >= 10) & (df['Year'] == '2020')]['Population'].mean()
slopes.append({'Slope': '10+', 'Year': 2020, 'Population': sum_2020_10})

sum_2030_01 = df[(df['Slope'] >= 0) & (df['Slope'] < 1) & (df['Year'] == '2030')]['Population'].mean()
slopes.append({'Slope': '0 - 1', 'Year': 2030, 'Population': sum_2030_01})
sum_2030_15 = df[(df['Slope'] >= 1) & (df['Slope'] < 5) & (df['Year'] == '2030')]['Population'].mean()
slopes.append({'Slope': '1 - 5', 'Year': 2030, 'Population': sum_2030_15})
sum_2030_510 = df[(df['Slope'] >= 5) & (df['Slope'] < 10) & (df['Year'] == '2030')]['Population'].mean()
slopes.append({'Slope': '5 - 10', 'Year': 2030, 'Population': sum_2030_510})
sum_2030_10 = df[(df['Slope'] >= 10) & (df['Year'] == '2030')]['Population'].mean()
slopes.append({'Slope': '10+', 'Year': 2030, 'Population': sum_2030_10})

sum_2040_01 = df[(df['Slope'] >= 0) & (df['Slope'] < 1) & (df['Year'] == '2040')]['Population'].mean()
slopes.append({'Slope': '0 - 1', 'Year': 2040, 'Population': sum_2040_01})
sum_2040_15 = df[(df['Slope'] >= 1) & (df['Slope'] < 5) & (df['Year'] == '2040')]['Population'].mean()
slopes.append({'Slope': '1 - 5', 'Year': 2040, 'Population': sum_2040_15})
sum_2040_510 = df[(df['Slope'] >= 5) & (df['Slope'] < 10) & (df['Year'] == '2040')]['Population'].mean()
slopes.append({'Slope': '5 - 10', 'Year': 2040, 'Population': sum_2040_510})
sum_2040_10 = df[(df['Slope'] >= 10) & (df['Year'] == '2040')]['Population'].mean()
slopes.append({'Slope': '10+', 'Year': 2040, 'Population': sum_2040_10})

sum_2050_01 = df[(df['Slope'] >= 0) & (df['Slope'] < 1) & (df['Year'] == '2050')]['Population'].mean()
slopes.append({'Slope': '0 - 1', 'Year': 2050, 'Population': sum_2050_01})
sum_2050_15 = df[(df['Slope'] >= 1) & (df['Slope'] < 5) & (df['Year'] == '2050')]['Population'].mean()
slopes.append({'Slope': '1 - 5', 'Year': 2050, 'Population': sum_2050_15})
sum_2050_510 = df[(df['Slope'] >= 5) & (df['Slope'] < 10) & (df['Year'] == '2050')]['Population'].mean()
slopes.append({'Slope': '5 - 10', 'Year': 2050, 'Population': sum_2050_510})
sum_2050_10 = df[(df['Slope'] >= 10) & (df['Year'] == '2050')]['Population'].mean()
slopes.append({'Slope': '10+', 'Year': 2050, 'Population': sum_2050_10})

sum_2060_01 = df[(df['Slope'] >= 0) & (df['Slope'] < 1) & (df['Year'] == '2060')]['Population'].mean()
slopes.append({'Slope': '0 - 1', 'Year': 2060, 'Population': sum_2060_01})
sum_2060_15 = df[(df['Slope'] >= 1) & (df['Slope'] < 5) & (df['Year'] == '2060')]['Population'].mean()
slopes.append({'Slope': '1 - 5', 'Year': 2060, 'Population': sum_2060_15})
sum_2060_510 = df[(df['Slope'] >= 5) & (df['Slope'] < 10) & (df['Year'] == '2060')]['Population'].mean()
slopes.append({'Slope': '5 - 10', 'Year': 2060, 'Population': sum_2060_510})
sum_2060_10 = df[(df['Slope'] >= 10) & (df['Year'] == '2060')]['Population'].mean()
slopes.append({'Slope': '10+', 'Year': 2060, 'Population': sum_2060_10})

sum_2070_01 = df[(df['Slope'] >= 0) & (df['Slope'] < 1) & (df['Year'] == '2070')]['Population'].mean()
slopes.append({'Slope': '0 - 1', 'Year': 2070, 'Population': sum_2070_01})
sum_2070_15 = df[(df['Slope'] >= 1) & (df['Slope'] < 5) & (df['Year'] == '2070')]['Population'].mean()
slopes.append({'Slope': '1 - 5', 'Year': 2070, 'Population': sum_2070_15})
sum_2070_510 = df[(df['Slope'] >= 5) & (df['Slope'] < 10) & (df['Year'] == '2070')]['Population'].mean()
slopes.append({'Slope': '5 - 10', 'Year': 2070, 'Population': sum_2070_510})
sum_2070_10 = df[(df['Slope'] >= 10) & (df['Year'] == '2070')]['Population'].mean()
slopes.append({'Slope': '10+', 'Year': 2070, 'Population': sum_2070_10})

sum_2080_01 = df[(df['Slope'] >= 0) & (df['Slope'] < 1) & (df['Year'] == '2080')]['Population'].mean()
slopes.append({'Slope': '0 - 1', 'Year': 2080, 'Population': sum_2080_01})
sum_2080_15 = df[(df['Slope'] >= 1) & (df['Slope'] < 5) & (df['Year'] == '2080')]['Population'].mean()
slopes.append({'Slope': '1 - 5', 'Year': 2080, 'Population': sum_2080_15})
sum_2080_510 = df[(df['Slope'] >= 5) & (df['Slope'] < 10) & (df['Year'] == '2080')]['Population'].mean()
slopes.append({'Slope': '5 - 10', 'Year': 2080, 'Population': sum_2080_510})
sum_2080_10 = df[(df['Slope'] >= 10) & (df['Year'] == '2080')]['Population'].mean()
slopes.append({'Slope': '10+', 'Year': 2080, 'Population': sum_2080_10})

sum_2090_01 = df[(df['Slope'] >= 0) & (df['Slope'] < 1) & (df['Year'] == '2090')]['Population'].mean()
slopes.append({'Slope': '0 - 1', 'Year': 2090, 'Population': sum_2090_01})
sum_2090_15 = df[(df['Slope'] >= 1) & (df['Slope'] < 5) & (df['Year'] == '2090')]['Population'].mean()
slopes.append({'Slope': '1 - 5', 'Year': 2090, 'Population': sum_2090_15})
sum_2090_510 = df[(df['Slope'] >= 5) & (df['Slope'] < 10) & (df['Year'] == '2090')]['Population'].mean()
slopes.append({'Slope': '5 - 10', 'Year': 2090, 'Population': sum_2090_510})
sum_2090_10 = df[(df['Slope'] >= 10) & (df['Year'] == '2090')]['Population'].mean()
slopes.append({'Slope': '10+', 'Year': 2090, 'Population': sum_2090_10})

sum_2100_01 = df[(df['Slope'] >= 0) & (df['Slope'] < 1) & (df['Year'] == '2100')]['Population'].mean()
slopes.append({'Slope': '0 - 1', 'Year': 2100, 'Population': sum_2100_01})
sum_2100_15 = df[(df['Slope'] >= 1) & (df['Slope'] < 5) & (df['Year'] == '2100')]['Population'].mean()
slopes.append({'Slope': '1 - 5', 'Year': 2100, 'Population': sum_2100_15})
sum_2100_510 = df[(df['Slope'] >= 5) & (df['Slope'] < 10) & (df['Year'] == '2100')]['Population'].mean()
slopes.append({'Slope': '5 - 10', 'Year': 2100, 'Population': sum_2100_510})
sum_2100_10 = df[(df['Slope'] >= 10) & (df['Year'] == '2100')]['Population'].mean()
slopes.append({'Slope': '10+', 'Year': 2100, 'Population': sum_2100_10})

df = pd.DataFrame(slopes)

sns.set(style='whitegrid')
fig = plt.figure()
ax = fig.add_axes([0.2, 0.2, 0.7, 0.7])
ax.plot(df[df['Slope'] == '0 - 1']['Year'], df[df['Slope'] == '0 - 1']['Population'], label='0$^\circ$ - 1$^\circ$')
ax.plot(df[df['Slope'] == '1 - 5']['Year'], df[df['Slope'] == '1 - 5']['Population'], label='1$^\circ$ - 5$^\circ$')
ax.plot(df[df['Slope'] == '5 - 10']['Year'], df[df['Slope'] == '5 - 10']['Population'], label='5$^\circ$ - 10$^\circ$')
ax.plot(df[df['Slope'] == '10+']['Year'], df[df['Slope'] == '10+']['Population'], label='10$^\circ$+')
ax.set_xlim(2010, 2105)
ax.set_ylim(0, 80)
ax.legend()
ax.set_xlabel('Year')
ax.set_ylabel('Average population pr. cell')
ax.set_title('Population of Slope - France', fontsize=16)
plt.savefig('slope_line_plot.png', bbox_inches='tight')
plt.show()
plt.clf()
plt.close()

# df.loc[(df.Slope >= 0) & (df.Slope < 1), 'Slope'] = 0
# df.loc[(df.Slope >= 1) & (df.Slope < 5), 'Slope'] = 1
# df.loc[(df.Slope >= 5) & (df.Slope <= 10), 'Slope'] = 2
# #df.loc[(df.Categories > 251) & (df.Categories < 500), 'Categories'] = 4
# df.loc[df.Slope > 10, 'Slope'] = 3
#
# df.loc[df.Slope == 0, 'Slope'] = '0 - 1'
# df.loc[df.Slope == 1, 'Slope'] = '1 - 5'
# df.loc[df.Slope == 2, 'Slope'] = '5 - 10'
# df.loc[df.Slope == 3, 'Slope'] = '10+'
#df.loc[df.Categories == 5, 'Categories'] = '500+'


# sns.set(style='whitegrid')
# # sns.set_palette(sns.color_palette('husl', 6))
# fig = plt.figure()
# # ax = sns.countplot(x="Categories", hue="Year", data=df, order=['0 - 1', '1 - 5', '5 - 10', '10+'], palette='Set1')
# ax = sns.violinplot(x="Year", y="Population", hue="Slope", data=df, palette='Set1', jitter=True, cut=0)
# ax.set_xlabel('Year')
# ax.set_ylabel('Population')
# ax.set_title('Population and Slope - France', fontsize=16)
# plt.savefig('slope_plot.png', bbox_inches='tight')
# plt.show()

