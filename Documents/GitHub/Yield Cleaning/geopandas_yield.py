
import geopandas as gpd

shp_path = r"C:\Users\lmlev\Dropbox\Classes\Spring 2019\GIS 5541\Projects\soy_yield.shp"

shp = gpd.read_file(shp_path, driver='ESRI Shapefile')

# Print column names
print(list(shp))

# Plot with matplotlib
shp.plot()

# Clip shp file with shp boundary



# Selection shp where shp's attribute "Swth_Wdth_" == 35
new_shp = shp[shp['Swth_Wdth_'] == 35]

# Selection of shp where 'Moisture__' > 0
new2 = new_shp[new_shp['Moisture__'] > 0]

# Selection of shp where 
new3 = new2[new2['Yld_Vol_Dr'] > 0]


# Find standard deviation of yield data, and value of 3 SDs 

import fiona
import pprint as pp

# Load in the shapefile for 2018 yield using Fiona 
fh = fiona.open(r"C:\Users\lmlev\Dropbox\Classes\Spring 2019\GIS 5541\Projects\soy_yield.shp")

# Loop over all the features to find the average Yield 
average = 0 
count = 0 
yldsum = 0
for f in fh:
    yld = f['properties']['Yld_Vol_Dr']
    yldsum += yld
    count += 1
    average = yldsum / count 
print("Yield average", average)


# Write to new file
new3.to_file(r'C:\Users\lmlev\Dropbox\Classes\Spring 2019\GIS 5541\Projects\new3')
