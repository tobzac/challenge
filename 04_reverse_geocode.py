#!/usr/bin/env python
# coding: utf-8

# In[1]:


# generate info for station locations from reverse geocode
# basically taken from https://towardsdatascience.com/reverse-geocoding-with-nyc-bike-share-data-cdef427987f8/


# In[2]:


from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd


# In[3]:


geolocator = Nominatim(user_agent="citibikedata_analysis")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1, max_retries=2)


# In[4]:


# check
reverse("40.741740, -73.994156").raw['address']


# In[5]:


reverse("40.717548, -73.994156").raw['address']


# In[6]:


reverse("40.793367, -73.923956").raw['address']


# In[10]:


# import unique station names with coords
all_years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

imported_df_coords_per_year = {}
stations_analysis_list_all = []
for year in all_years:
    df = pd.read_csv('intermediate_results/df_coords_stations_' + str(year) + '.csv', index_col="Unnamed: 0")
    imported_df_coords_per_year[year] = df
    stations_analysis_list_all.append(df)

# make a single data frame with unique entries
df_all = pd.concat(stations_analysis_list_all, axis=0)
print(len(df_all))

# sum over index to get usage values for all stations
only_usage = pd.DataFrame(df_all["usage"].groupby(level=0).sum())
station_names_to_coords = dict(pd.Series(list(zip(df_all['longitude'], df_all['latitude'])),
                               index=df_all.index).to_dict())
df_coords = pd.DataFrame.from_dict(station_names_to_coords, orient='index')
df_coords = df_coords.rename(columns={0: 'longitude', 1: 'latitude'})
df_coords_all = df_coords.join(only_usage).sort_values('usage', ascending=False)
df_only_coords_all = df_coords_all.drop('usage', axis=1)

print(len(df_only_coords_all))
df_only_coords_all_cleaned = df_only_coords_all[df_only_coords_all['longitude'] != 0]
print(len(df_only_coords_all_cleaned))
df_only_coords_all_cleaned


# In[8]:


# call reverse function on those 
locations=[]
for index, row in df_only_coords_all_cleaned.iterrows():
    locations.append(reverse("{}, {}".format(row['latitude'],
    row['longitude'])).raw['address'])
df_geocode = pd.DataFrame(locations)
df_geocode.index = df_only_coords_all_cleaned.index

#save out to file
df_geocode.to_csv('intermediate_results/df_geocode_all_stations.csv', index=True)

df_geocode


# In[ ]:




