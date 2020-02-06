#!/usr/bin/env python
# coding: utf-8

# # Segmenting and Clustering Neighborhoods in Toronto Part 1

# ## Problem 1

# Use the Notebook to build the code to scrape the following Wikipedia page, https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M, in order to obtain the data that is in the table of postal codes and to transform the data into a pandas dataframe.
# 

# To create the above dataframe:
# 
#   * The dataframe will consist of three columns: PostalCode, Borough, and Neighborhood
#   * Only process the cells that have an assigned borough. Ignore cells with a borough that is Not assigned.
#   * More than one neighborhood can exist in one postal code area. For example, in the table on the Wikipedia page, you will notice that M5A is listed twice and has two neighborhoods: Harbourfront and Regent Park. These two rows will be combined into one row with the neighborhoods separated with a comma as shown in row 11 in the above table.
#   * If a cell has a borough but a Not assigned neighborhood, then the neighborhood will be the same as the borough. So for the 9th cell in the table on the Wikipedia page, the value of the Borough and the Neighborhood columns will be Queen's Park.
#   * Clean your Notebook and add Markdown cells to explain your work and any assumptions you are making.
#   * In the last cell of your notebook, use the .shape method to print the number of rows of your dataframe.
#   
# Note: There are different website scraping libraries and packages in Python. For scraping the above table, you can simply use pandas to read the table into a pandas dataframe.
# 
# Another way, which would help to learn for more complicated cases of web scraping is using the BeautifulSoup package. Here is the package's main documentation page: http://beautiful-soup-4.readthedocs.io/en/latest/
# 
# The package is so popular that there is a plethora of tutorials and examples on how to use it. Here is a very good Youtube video on how to use the BeautifulSoup package: https://www.youtube.com/watch?v=ng2o98k983k
# 
# Use pandas, or the BeautifulSoup package, or any other way you are comfortable with to transform the data in the table on the Wikipedia page into the above pandas dataframe.

# In[39]:


get_ipython().system('pip install beautifulsoup4')
get_ipython().system('pip install lxml')
import requests # library to handle requests
import pandas as pd # library for data analsysis
import numpy as np # library to handle data in a vectorized manner
import random # library for random number generation

#!conda install -c conda-forge geopy --yes 
from geopy.geocoders import Nominatim # module to convert an address into latitude and longitude values

# libraries for displaying images
from IPython.display import Image 
from IPython.core.display import HTML 


from IPython.display import display_html
import pandas as pd
import numpy as np
    
# tranforming json file into a pandas dataframe library
from pandas.io.json import json_normalize

get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')
import folium # plotting library
from bs4 import BeautifulSoup
from sklearn.cluster import KMeans
import matplotlib.cm as cm
import matplotlib.colors as colors

print('Folium installed')
print('Libraries imported.')


# In[40]:


List_url = "https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M"
source = requests.get(List_url).text


# In[41]:


soup = BeautifulSoup(source,'xml')


# In[42]:


table = soup.find('table')


# In[43]:


columns_names = ['Postalcode','Borough','Neighborhood']
df = pd.DataFrame(columns = columns_names)


# In[44]:


for tr_cell in table.find_all('tr'):
    row_data = []
    for td_cell in tr_cell.find_all('td'):
        row_data.append(td_cell.text.strip())
    if len(row_data)==3:
        df.loc[len(df)] = row_data


# In[45]:


df.head()


# ### Time to remove rows where Borough is "Not assigned".*

# In[46]:


df = df[df['Borough']!= 'Not assigned']


# In[47]:


df[df['Neighborhood']=='Not assigned'] = df['Borough']
df.head()


# In[48]:


temp_df=df.groupby('Postalcode')['Neighborhood'].apply(lambda x: "%s" % ', '.join(x))
temp_df = temp_df.reset_index(drop=False)
temp_df.rename(columns={'Neighborhood':'Neighborhood_joined'},inplace = True)


# In[49]:


df_merge = pd.merge(df,temp_df, on= 'Postalcode')


# In[50]:


df_merge.drop(['Neighborhood'],axis=1,inplace=True)


# In[51]:


df_merge.rename(columns={'Neighborhood_joined':'Neighborhood'},inplace=True)


# In[52]:


df_merge.head()


# In[53]:


df_merge.shape


# ## Problema 2

# Now that you have built a dataframe of the postal code of each neighborhood along with the borough name and neighborhood name, in order to utilize the Foursquare location data, we need to get the latitude and the longitude coordinates of each neighborhood.
# 
# In an older version of this course, we were leveraging the Google Maps Geocoding API to get the latitude and the longitude coordinates of each neighborhood. However, recently Google started charging for their API: http://geoawesomeness.com/developers-up-in-arms-over-google-maps-api-insane-price-hike/, so we will use the Geocoder Python package instead: https://geocoder.readthedocs.io/index.html.
# 
# The problem with this Package is you have to be persistent sometimes in order to get the geographical coordinates of a given postal code. So you can make a call to get the latitude and longitude coordinates of a given postal code and the result would be None, and then make the call again and you would get the coordinates. So, in order to make sure that you get the coordinates for all of our neighborhoods, you can run a while loop for each postal code. 
# 
# Given that this package can be very unreliable, in case you are not able to get the geographical coordinates of the neighborhoods using the Geocoder package, here is a link to a csv file that has the geographical coordinates of each postal code: http://cocl.us/Geospatial_data
# 
# Important Note: There is a limit on how many times you can call geocoder.google function. It is 2500 times per day. This should be way more than enough for you to get acquainted with the package and to use it to get the geographical coordinates of the neighborhoods in the Toronto.

# In[54]:


lat_lon = pd.read_csv('https://cocl.us/Geospatial_data')
lat_lon.head()


# In[55]:


Latitude = lat_lon['Latitude']
Longitude = lat_lon['Longitude']


# In[57]:


df_merge['Latitude'] = Latitude
df_merge['Longitude'] = Longitude


# In[58]:


df_merge.head()


# ## Problem 3 

# ### Explore the neighborhoods in Toronto

# In[59]:


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

import folium # map rendering library

print('Libraries imported.')


# In[60]:


address = "Toronto, On"

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))


# In[79]:


mapToronto = folium.Map(location = [latitude, longitude], zoom_start = 11)

for lat, long, borough, neighborhood in zip(df_merge['Latitude'], df_merge['Longitude'], df_merge['Borough'], df_merge['Neighborhood']):
    label = neighborhood + " " + borough
    label = folium.Popup(label, parse_html = True)
    
mapToronto


# In[ ]:




