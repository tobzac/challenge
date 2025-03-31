#!/usr/bin/env python
# coding: utf-8

# In[1]:


# generate info for station locations from reverse geocode
# basically taken from https://towardsdatascience.com/reverse-geocoding-with-nyc-bike-share-data-cdef427987f8/


# In[120]:


from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# In[19]:


geolocator = Nominatim(user_agent="citibikedata_analysis")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1, max_retries=2)


# In[28]:


# check e.g. Lincoln Park	-74.078406	40.724605	-73.994156	40.741740   -74.078900	40.711130	-73.994539	40.735439
reverse("40.735439, -73.994539").raw['address']


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


# In[93]:


# read in geocode data
df_geocode_all_stations = pd.read_csv('intermediate_results/df_geocode_all_stations.csv', index_col=0)
df_geocode_all_stations = df_geocode_all_stations[df_geocode_all_stations.columns.intersection(['neighbourhood', 'borough', 'city'])]

# annotate generated data with neighbourhood and borough
all_years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
imported_df_coords_per_year = {}
for year in all_years:
    df = pd.read_csv('intermediate_results/df_coords_stations_' + str(year) + '.csv', index_col=0)
    df = df.join(df_geocode_all_stations)
    imported_df_coords_per_year[year] = df

imported_df_coords_per_year[2015]


# In[71]:


# what neighbourhoods
imported_df_coords_per_year[2015][imported_df_coords_per_year[2015]['borough'] == 'Manhattan'].neighbourhood.unique()


# In[119]:


min_usage = 0

df_coords_total_min_usage = imported_df_coords_per_year[2019]
df_coords_total_min_usage = df_coords_total_min_usage[df_coords_total_min_usage['longitude'] != 0]
df_coords_total_min_usage = df_coords_total_min_usage[df_coords_total_min_usage['usage'] > min_usage]
# now restrict to regions under central park, which basically present from 2013 on...
# function: y = (40.755 - 40.78)/(-73.965 + 73.99) * (x + 73.965) + 40.755 
# and vertical line at longitude -74.03
df_coords_total_min_usage = df_coords_total_min_usage[df_coords_total_min_usage['borough'] == 'Manhattan']
#df_coords_total_min_usage = df_coords_total_min_usage[(df_coords_total_min_usage['latitude'] < (((df_coords_total_min_usage['longitude'] + 73.965)*((40.755 - 40.78)/(-73.965 + 73.99)) ) + 40.755)) & (df_coords_total_min_usage['longitude'] > -74.03)]

sns.set_style("whitegrid")
#norm = plt.Normalize(df_coords_total_min_usage['usage'].min(), df_coords_total_min_usage['usage'].max())
#sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
#sm.set_array([])

fig, ax = plt.subplots()

#fig = sns.scatterplot(data=df_coords_total_min_usage, x="longitude", y="latitude", s=15, hue='usage', palette='Reds')
fig = sns.scatterplot(data=df_coords_total_min_usage, x="longitude", y="latitude", s=15, size='usage', hue='borough', palette='Reds')
fig.set_title("citibikenyc stations with minimal usage of " + str(min_usage) + " rents/arrivals per year", size=18)

# Remove the legend and add a colorbar
#fig.get_legend().remove()
#fig.figure.colorbar(sm, ax=ax)
df_coords_total_min_usage

plt.plot([-74.03, -74.03], [40.7, 40.75], linewidth=2)
plt.plot([-73.965, -73.99], [40.755, 40.78], linewidth=2)
#plt.ylim(40.65, 40.80)


# In[95]:


imported_df_coords_per_year[2019][imported_df_coords_per_year[2019]['borough'] == 'Manhattan']

