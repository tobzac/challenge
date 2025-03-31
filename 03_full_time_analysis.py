#!/usr/bin/env python
# coding: utf-8

# ## citibike data over full time frame

# In[30]:


import analysis_functions
import pickle
import pandas as pd
import seaborn as sns
from matplotlib import rcParams
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import math


# loop over years. save results into files to save regeneration of these results...

# In[2]:


all_years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

result_map_per_year = {}
result_map_per_year_core = {}
df_coords_per_year = {}
df_coords_per_year_core = {}
number_unique_stations_per_year = {}
number_unique_stations_per_year_core = {}

geo_code_data_file_name = 'intermediate_results/df_geocode_all_stations.csv'


# In[3]:


# loop over all years
# different format of input csvs has to be taken into account...

#for year in [2020, 2021, 2022, 2023, 2024]:
for year in all_years:
    print("year: " + str(year))

    result_map, stations_analysis_list = analysis_functions.analysis_one_year(year, geo_code_data_file_name, 'normal')
    n_total, df_coords_total = analysis_functions.analysis_summary_year(result_map, stations_analysis_list)

    result_map_core, stations_analysis_list_core = analysis_functions.analysis_one_year(year, geo_code_data_file_name, 'core_region')
    n_total_core, df_coords_total_core = analysis_functions.analysis_summary_year(result_map_core, stations_analysis_list_core)
    
    # store results per year
    result_map_per_year[year] = result_map
    result_map_per_year_core[year] = result_map_core
    df_coords_per_year[year] = df_coords_total
    df_coords_per_year_core[year] = df_coords_total_core
    number_unique_stations_per_year[year] = len(df_coords_total)
    number_unique_stations_per_year_core[year] = len(df_coords_total_core)


# In[15]:


# store data to file, as it takes long to generate
# write out dataframes/maps total counts
for year in all_years:
    # write out station coords data frame
    df_coords_per_year[year].to_csv('intermediate_results/df_coords_stations_' + str(year) + '.csv', index=True)

    # write out dictionaries into pickle files
    with open('intermediate_results/result_map_' + str(year) + '.pickle', 'wb') as handle:
        pickle.dump(result_map_per_year[year], handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('intermediate_results/number_unique_stations_' + str(year) + '.pickle', 'wb') as handle:
        pickle.dump(number_unique_stations_per_year[year], handle, protocol=pickle.HIGHEST_PROTOCOL)

#write out geocode restricted core data as well:
for year in all_years:
    # write out station coords data frame
    df_coords_per_year_core[year].to_csv('intermediate_results/df_coords_stations_core_' + str(year) + '.csv', index=True)

    # write out dictionaries into pickle files
    with open('intermediate_results/result_map_core_' + str(year) + '.pickle', 'wb') as handle:
        pickle.dump(result_map_per_year_core[year], handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('intermediate_results/number_unique_stations_core_' + str(year) + '.pickle', 'wb') as handle:
        pickle.dump(number_unique_stations_per_year_core[year], handle, protocol=pickle.HIGHEST_PROTOCOL)


# In[16]:


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
        
imported_number_unique_stations_per_year = {}
for year in all_years:
    with open('intermediate_results/number_unique_stations_' + str(year) + '.pickle', 'rb') as handle:
        b = pickle.load(handle)
        imported_number_unique_stations_per_year[year] = b

print(imported_number_unique_stations_per_year)

#--------------------------------------------------------------
#import pre-generated pickle files/ csv files from core region:
imported_df_coords_per_year_core = {}
for year in all_years:
    df = pd.read_csv('intermediate_results/df_coords_stations_core_' + str(year) + '.csv', index_col="Unnamed: 0")
    imported_df_coords_per_year_core[year] = df

# read in dictionaries from pickle files
imported_result_map_per_year_core = {}
for year in all_years:
    with open('intermediate_results/result_map_core_' + str(year) + '.pickle', 'rb') as handle:
        b = pickle.load(handle)
        imported_result_map_per_year_core[year] = b

print(imported_result_map_per_year_core)
        
imported_number_unique_stations_per_year_core = {}
for year in all_years:
    with open('intermediate_results/number_unique_stations_core_' + str(year) + '.pickle', 'rb') as handle:
        b = pickle.load(handle)
        imported_number_unique_stations_per_year_core[year] = b

print(imported_number_unique_stations_per_year_core)


# In[17]:


imported_df_coords_per_year[2024]


# In[20]:


# plot overall trips over years
df_trips = pd.DataFrame.from_dict(imported_result_map_per_year)
df_trips['month'] = df_trips.index
df_trips = df_trips.sort_values('month')
df_trips
df_trips = df_trips.melt(id_vars=['month'], value_vars=all_years)
df_trips['date'] = df_trips['variable'].astype(str) + "-" + df_trips['month'].astype(str)
df_trips = df_trips.rename(columns={"value": "number of trips"})
df_trips

rcParams['figure.figsize'] = 11.7,8.27

g = sns.lineplot(data=df_trips, x='date', y='number of trips')
g.tick_params(axis='x', labelrotation=90)

g.xaxis.set_major_locator(ticker.MultipleLocator(12))
g.set_title('all citibike trips')


# In[23]:


# plot number of used stations over years
imported_number_unique_stations_per_year
df_stations = pd.DataFrame.from_dict(imported_number_unique_stations_per_year, orient='index')
df_stations['year'] = df_stations.index
df_stations = df_stations.rename(columns={0: 'number of unique used stations'})
df_stations

g = sns.lineplot(data=df_stations, x='year', y='number of unique used stations')
g.set_title('Number of unique used stations')


# In[18]:


# plot overall trips in core region over years
df_trips = pd.DataFrame.from_dict(imported_result_map_per_year_core)
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
g.set_title('citibike trips restricted to core region')


# In[22]:


# plot number of used stations over years
imported_number_unique_stations_per_year_core
df_stations = pd.DataFrame.from_dict(imported_number_unique_stations_per_year_core, orient='index')
df_stations['year'] = df_stations.index
df_stations = df_stations.rename(columns={0: 'number of unique used stations'})
df_stations

g = sns.lineplot(data=df_stations, x='year', y='number of unique used stations')
g.set_title('Number of unique used stations in core region')


# ## NYC accidents data full time frame
# 
# as seen in  previous notebook, this data has to be restricted to areas, where citibikenyc is present to perhaps get some correlation between the 2...

# ### no restrictions
# using all NYC cyclist accidents, also over regions, where there is not citibike rental service available

# In[28]:


table_accidents = pd.read_csv("Data/Motor_Vehicle_Collisions_-_Crashes_20250319.csv")
table_accidents["CRASH DATE"]= pd.to_datetime(table_accidents["CRASH DATE"])


# In[9]:


# total without any restriction

injuries_cyclists = {}
injuries_cyclists_year = {}
deaths_cyclists = {}
deaths_cyclists_year = {}
for year in all_years:
    table_accidents_year = table_accidents[table_accidents["CRASH DATE"].dt.year == year]

    injuries_cyclists_year[year] = table_accidents_year["NUMBER OF CYCLIST INJURED"].sum(skipna = True)
    deaths_cyclists_year[year] = table_accidents_year["NUMBER OF CYCLIST KILLED"].sum(skipna = True)
    
    injuries_cyclists[year] = {}
    deaths_cyclists[year] = {}
    for month in range(1,13):
        table_accidents_month = table_accidents_year[table_accidents_year["CRASH DATE"].dt.month == month]
        injuries_cyclists[year][month] = table_accidents_month["NUMBER OF CYCLIST INJURED"].sum(skipna = True)
        deaths_cyclists[year][month] = table_accidents_month["NUMBER OF CYCLIST KILLED"].sum(skipna = True)
        
print(injuries_cyclists)
print(deaths_cyclists)


# In[10]:


# plot
df_injuries = pd.DataFrame.from_dict(injuries_cyclists)
df_injuries['month'] = df_injuries.index
df_injuries = df_injuries.melt(id_vars=['month'], value_vars=all_years)
df_injuries['date'] = df_injuries['variable'].astype(str) + "-" + df_injuries['month'].astype(str)
df_injuries = df_injuries.rename(columns={'value': 'number of injuries'})
df_injuries

g = sns.lineplot(data=df_injuries, x='date', y='number of injuries')

g.tick_params(axis='x', labelrotation=90)

g.xaxis.set_major_locator(ticker.MultipleLocator(12))
g.set_title('cyclist injuries all NYC')


# In[11]:


# for year sums
df_injuries = pd.DataFrame.from_dict(injuries_cyclists_year, orient='index')
df_injuries = df_injuries.rename(columns={0: 'number of injuries'})
df_injuries['year'] = df_injuries.index
df_injuries

g = sns.lineplot(data=df_injuries, x='year', y='number of injuries')
g.set_title('cyclist injuries all NYC')


# In[12]:


df_deaths = pd.DataFrame.from_dict(deaths_cyclists_year, orient='index')
df_deaths = df_deaths.rename(columns={0: 'number of deaths'})
df_deaths['year'] = df_deaths.index
df_deaths

g = sns.lineplot(data=df_deaths, x='year', y='number of deaths')
g.set_title('cyclist deaths all NYC')


# ### restrict to core region
# only take into account accidents which are at a minimal distance to the core region of citibikenyc, which is defined to be Manhattan below Central Park

# In[33]:


# with restriction to core region
max_distance = 500

injuries_cyclists_core = {}
injuries_cyclists_year_core = {}
deaths_cyclists_core = {}
deaths_cyclists_year_core = {}
for year in all_years:

    print("year: "+ str(year))
    table_accidents_year = table_accidents[table_accidents["CRASH DATE"].dt.year == year]
    
    accidents_coords_cyclists = table_accidents_year[(table_accidents_year["NUMBER OF CYCLIST INJURED"] > 0) | (table_accidents_year["NUMBER OF CYCLIST KILLED"] > 0)]
    accidents_coords_cyclists["in_core_region"] = 0
    accidents_coords_cyclists_cleaned = accidents_coords_cyclists[accidents_coords_cyclists["LATITUDE"] != 0]
    
    count = 0
    for index, row in accidents_coords_cyclists_cleaned.iterrows():
        #print(row['c1'], row['c2'])
        if (count%100) == 0:
            print(count)
        count = count + 1
        close_enough = False
        for index2, row2 in imported_df_coords_per_year_core[year].iterrows():
            distance = math.sqrt(math.pow((row['LONGITUDE'] - row2['longitude']) * 85118, 2.0) + math.pow((row['LATITUDE'] - row2['latitude']) * 111120, 2.0))
            if distance < max_distance:
                close_enough = True 
                break
        if close_enough:
            accidents_coords_cyclists_cleaned.loc[index, "in_core_region"] = 1

    accidents_coords_cyclists_core = accidents_coords_cyclists_cleaned[accidents_coords_cyclists_cleaned["in_core_region"] == 1]

    injuries_cyclists_year_core[year] = accidents_coords_cyclists_core["NUMBER OF CYCLIST INJURED"].sum(skipna = True)
    deaths_cyclists_year_core[year] = accidents_coords_cyclists_core["NUMBER OF CYCLIST KILLED"].sum(skipna = True)
    
    injuries_cyclists_core[year] = {}
    deaths_cyclists_core[year] = {}
    for month in range(1,13):
        table_accidents_month = accidents_coords_cyclists_core[accidents_coords_cyclists_core["CRASH DATE"].dt.month == month]
        injuries_cyclists_core[year][month] = table_accidents_month["NUMBER OF CYCLIST INJURED"].sum(skipna = True)
        deaths_cyclists_core[year][month] = table_accidents_month["NUMBER OF CYCLIST KILLED"].sum(skipna = True)
        
print(injuries_cyclists_core)
print(deaths_cyclists_core)


# In[34]:


imported_df_coords_per_year_core[2022]


# In[36]:


# store data to file, as it takes also long to generate
# write out dataframes/maps total counts
for year in all_years:

    # write out dictionaries into pickle files
    with open('intermediate_results/injuries_cyclists_core_' + str(year) + '.pickle', 'wb') as handle:
        pickle.dump(injuries_cyclists_year_core[year], handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('intermediate_results/deaths_cyclists_core_' + str(year) + '.pickle', 'wb') as handle:
        pickle.dump(deaths_cyclists_year_core[year], handle, protocol=pickle.HIGHEST_PROTOCOL)

# write out total year sums:
with open('intermediate_results/injuries_cyclists_core.pickle', 'wb') as handle:
    pickle.dump(injuries_cyclists_core, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('intermediate_results/deaths_cyclists_core.pickle', 'wb') as handle:
    pickle.dump(deaths_cyclists_core, handle, protocol=pickle.HIGHEST_PROTOCOL)


# In[37]:


# read in stored files for restricted injury/death numbers
imported_injuries_cyclists_per_year_core = {}
for year in all_years:
    with open('intermediate_results/injuries_cyclists_core_' + str(year) + '.pickle', 'rb') as handle:
        b = pickle.load(handle)
        imported_injuries_cyclists_per_year_core[year] = b

# read in dictionaries from pickle files
imported_deaths_cyclists_per_year_core = {}
for year in all_years:
    with open('intermediate_results/deaths_cyclists_core_' + str(year) + '.pickle', 'rb') as handle:
        b = pickle.load(handle)
        imported_deaths_cyclists_per_year_core[year] = b

imported_injuries_cyclists_core = {}
with open('intermediate_results/injuries_cyclists_core.pickle', 'rb') as handle:
        b = pickle.load(handle)
        imported_injuries_cyclists_core = b

imported_deaths_cyclists_core = {}
with open('intermediate_results/deaths_cyclists_core.pickle', 'rb') as handle:
        b = pickle.load(handle)
        imported_deaths_cyclists_core = b
        


# In[38]:


print(imported_injuries_cyclists_core)
print(injuries_cyclists_core)


# In[39]:


# plot
df_injuries_core = pd.DataFrame.from_dict(imported_injuries_cyclists_core)
df_injuries_core['month'] = df_injuries_core.index
df_injuries_core = df_injuries_core.melt(id_vars=['month'], value_vars=all_years)
df_injuries_core['date'] = df_injuries_core['variable'].astype(str) + "-" + df_injuries_core['month'].astype(str)
df_injuries_core = df_injuries_core.rename(columns={'value': 'number of injuries'})
df_injuries_core

g = sns.lineplot(data=df_injuries_core, x='date', y='number of injuries')

g.tick_params(axis='x', labelrotation=90)

g.xaxis.set_major_locator(ticker.MultipleLocator(12))
g.set_title('cyclist injuries restricted to core region in NYC')


# In[40]:


# for year sums
df_injuries_core = pd.DataFrame.from_dict(imported_injuries_cyclists_per_year_core, orient='index')
df_injuries_core = df_injuries_core.rename(columns={0: 'number of injuries'})
df_injuries_core['year'] = df_injuries_core.index
df_injuries_core

g = sns.lineplot(data=df_injuries_core, x='year', y='number of injuries')
g.set_title('cyclist injuries restricted to core region in NYC')


# In[41]:


df_deaths_core = pd.DataFrame.from_dict(imported_deaths_cyclists_per_year_core, orient='index')
df_deaths_core = df_deaths_core.rename(columns={0: 'number of deaths'})
df_deaths_core['year'] = df_deaths_core.index
df_deaths_core

g = sns.lineplot(data=df_deaths_core, x='year', y='number of deaths')
g.set_title('cyclist deaths restricted to core region in NYC')

