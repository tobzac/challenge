#!/usr/bin/env python
# coding: utf-8

# ## citibike data over full time frame

# In[1]:


import analysis_functions
import pickle
import pandas as pd
import seaborn as sns
from matplotlib import rcParams
import matplotlib.ticker as ticker


# loop over years. save results into files to save regeneration of these results...

# In[2]:


all_years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]


# In[ ]:


# loop over all years
# different format of input csvs has to be taken into account...

result_map_per_year = {}
df_coords_per_year = {}
number_unique_stations_per_year = {}
#for year in [2020, 2021, 2022, 2023, 2024]:
for year in all_years:
    print("year: " + str(year))
    
    result_map, stations_analysis_list = analysis_functions.analysis_one_year(year)
    n_total, df_coords_total = analysis_functions.analysis_summary_year(result_map, stations_analysis_list)
    
    # store results per year
    result_map_per_year[year] = result_map
    df_coords_per_year[year] = df_coords_total
    number_unique_stations_per_year[year] = len(df_coords_total)


# In[10]:


# store data to file, as it takes long to generate
# write out dataframes
for year in all_years:
    df_coords_per_year[year].to_csv('intermediate_results/df_coords_stations_' + str(year) + '.csv', index=True)

# write out dictionaries into pickle files
for year in all_years:
    with open('intermediate_results/result_map_' + str(year) + '.pickle', 'wb') as handle:
        pickle.dump(result_map_per_year[year], handle, protocol=pickle.HIGHEST_PROTOCOL)

for year in all_years:
    with open('intermediate_results/number_unique_stations_' + str(year) + '.pickle', 'wb') as handle:
        pickle.dump(number_unique_stations_per_year[year], handle, protocol=pickle.HIGHEST_PROTOCOL)


# In[11]:


# read in pre-generated pickle files/ csv files:
imported_df_coords_per_year = {}
for year in all_years:
    df = pd.read_csv('intermediate_results/df_coords_stations_' + str(year) + '.csv', index_col="Unnamed: 0")
    imported_df_coords_per_year[year] = df

# read in dictionaries from pickle files
imported_result_map_per_year = {}
for year in all_years:
    with open('intermediate_results/result_map_' + str(year) + '.pickle', 'rb') as handle:
        b = pickle.load(handle)
        imported_result_map_per_year[year] = b

print(imported_result_map_per_year)
print(result_map_per_year)
        
imported_number_unique_stations_per_year = {}
for year in all_years:
    with open('intermediate_results/number_unique_stations_' + str(year) + '.pickle', 'rb') as handle:
        b = pickle.load(handle)
        imported_number_unique_stations_per_year[year] = b

print(imported_number_unique_stations_per_year)
print(number_unique_stations_per_year)


# In[12]:


imported_df_coords_per_year[2017]


# In[13]:


# plot overall trips over years
df_trips = pd.DataFrame.from_dict(imported_result_map_per_year)
df_trips['month'] = df_trips.index
df_trips = df_trips.sort_values('month')
df_trips
df_trips = df_trips.melt(id_vars=['month'], value_vars=all_years)
df_trips['date'] = df_trips['variable'].astype(str) + "-" + df_trips['month'].astype(str)
df_trips = df_trips.rename(columns={"value": "numer of trips"})
df_trips

rcParams['figure.figsize'] = 11.7,8.27

g = sns.lineplot(data=df_trips, x='date', y='numer of trips')
g.tick_params(axis='x', labelrotation=90)

g.xaxis.set_major_locator(ticker.MultipleLocator(12))


# In[15]:


# plot number of used stations over years
imported_number_unique_stations_per_year
df_stations = pd.DataFrame.from_dict(imported_number_unique_stations_per_year, orient='index')
df_stations['year'] = df_stations.index
df_stations = df_stations.rename(columns={0: 'number of unique used stations'})
df_stations

g = sns.lineplot(data=df_stations, x='year', y='number of unique used stations')


# In[ ]:





# ## NYC accidents data full time frame
# 
# as seen in  previous notebook, this data has to be restricted to areas, where citibikenyc is present to perhaps get some correlation between the 2...

# In[ ]:


# accidents per month over the years: restrict to Manhattan region, where citibikenyc is heavily used
# and compare to other region, where citibikenyc is not used as heavily...

