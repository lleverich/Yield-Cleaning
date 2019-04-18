#!/usr/bin/env python
# coding: utf-8

# In[28]:


import geopandas as gpd

shp_path = r"C:\Users\lmlev\Dropbox\Classes\Spring 2019\GIS 5541\Projects\soy_yield.shp"

shp = gpd.read_file(shp_path, driver='ESRI Shapefile')


# In[29]:


# Print column names
print(list(shp))
shp.bounds


# In[123]:


shp.plot(cmap = 'rainbow', column = "Yld_Vol_Dr")


# In[52]:


# Import the boundaries 
bound_path = r"C:\Users\lmlev\Dropbox\Classes\Spring 2019\GIS 5541\Projects\soy_bounds.shp"
bound = gpd.read_file(bounds_path, driver='ESRI Shapefile')

type(bound)
bound.head()


# In[53]:


# Clip the soy_yield by the bounds 

shp_mask = shp.within(bound.loc[0, 'geometry'])
shp2 = shp.loc[shp_mask]

shp2.bounds

shp2.plot(cmap = 'rainbow', column = "Yld_Vol_Dr")


# In[74]:


# Filter by attributes in the table

# Selection shp where shp's attribute "Swth_Wdth_" == 35 and make a new shapefile 
new_shp = shp2[shp2['Swth_Wdth_'] == 35]

# Selection of shp where 'Moisture__' > 0 
new2 = new_shp[new_shp['Moisture__'] > 0]

# Selection of shp where yield is not zero
new3 = new2[new2['Yld_Vol_Dr'] > 0]

new3.head()
new3.bounds


# In[82]:


import pprint
pprint.pprint(new3.keys())


# In[102]:


# Find standard deviation of yield data, and value of 3 SDs 
mean = new3.loc[:,'Yld_Vol_Dr'].mean()

stdev = new3.loc[:,'Yld_Vol_Dr'].std()

new3.hist('Yld_Vol_Dr')

CI_high = mean + (3 * stdev)
CI_low = mean - (3 * stdev)
mean
CI_low


# In[108]:


# Clean yield outside of one standard deviation 

new4 = new3[new3['Yld_Vol_Dr'] > CI_low]
new5 = new4[new4['Yld_Vol_Dr'] < CI_high]

new5.plot()


# In[122]:


import matplotlib.pyplot as plt

# create figure and axes for Matplotlib
fig, ax = plt.subplots(1, figsize=(20, 6))

# Plot with matplotlib ploting the yield values 
new5.plot(cmap = "rainbow", column = "Yld_Vol_Dr", ax=ax)
# plt.axis(aspect='equal')
plt.xlabel('longitude')
plt.ylabel('latitude') 

# Turn off axis
ax.axis('off')
ax.set_title('Yield Map of Soybean Production', fontdict={'fontsize': '15', 'fontweight' : '3'})

# set the range for the choropleth
vmin, vmax = 10, 75

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap='rainbow', norm=plt.Normalize(vmin=vmin, vmax=vmax))
# empty array for the data range
sm._A = []
# add the colorbar to the figure
cbar = fig.colorbar(sm)

# # set a variable that will call whatever column we want to visualise on the map
# variable = ‘pop_density_per_hectare’
# # set the range for the choropleth
# vmin, vmax = 120, 220
# # create figure and axes for Matplotlib
# fig, ax = plt.subplots(1, figsize=(10, 6))


# ## Find the SD, Avg, and Median

# In[126]:


final_mean = new5.loc[:,'Yld_Vol_Dr'].mean()

final_stdev = new5.loc[:,'Yld_Vol_Dr'].std()

final_median = new5.loc[:,'Yld_Vol_Dr'].median()

print(final_mean, final_stdev, final_median)

new3.hist('Yld_Vol_Dr')


# ## Scrap Code

# In[ ]:


# Find standard deviation of yield data, and value of 3 SDs 
import fiona
import pprint as pp

# Load in the shapefile for 2018 yield using Fiona 
fh = fiona.open(r"C:\Users\lmlev\Dropbox\Classes\Spring 2019\GIS 5541\Projects\new3\new3.shp")

Loop over all the features to find the average Yield 
average = 0 
count = 0 
yldsum = 0
for points in new3:
    yld = points['properties']['Yld_Vol_Dr']
    yldsum += yld
    count += 1
    average = yldsum / count 
print("Yield average", average)


# Write to new file
new3.to_file(r'C:\Users\lmlev\Dropbox\Classes\Spring 2019\GIS 5541\Projects\new3')

