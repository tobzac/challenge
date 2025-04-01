#!/usr/bin/env python
# coding: utf-8

# Im ersten Notebook wurde die Daten/Struktur angeschaut, nun sollen die Daten zusammengeführt werden für ein ganzes Jahr.
# Schritte: pro Monat die Datentabellen zusammenführen, dann alle Monate.
# Für die pro Jahr Analyse auch Monatsintervalle beachten.
# 

# In[1]:


# imports für das notebook
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import rcParams
import matplotlib.pyplot as plt
import datetime as dt
import math
# importing re for regular expressions
import re
import os

import analysis_functions


# ## citibikenyc per year
# 
# ### monthly intervalls
# 

# In[2]:


year = 2024
result_map, stations_analysis_list = analysis_functions.analysis_one_year(year, 'intermediate_results/df_geocode_all_stations.csv', 'normal')


# In[3]:


result_map_core, stations_analysis_list_core = analysis_functions.analysis_one_year(year, 'intermediate_results/df_geocode_all_stations.csv', 'core_region')


# In[4]:


# plot
result_map_extended = {}
result_map_extended[year] = result_map
df_bike_trips_year = pd.DataFrame.from_dict(result_map_extended)
df_bike_trips_year["month"] = df_bike_trips_year.index
df_bike_trips_year = df_bike_trips_year.rename(columns={year: 'number of trips'})

rcParams['figure.figsize'] = 11.7,8.27

sns.barplot(data = df_bike_trips_year, x = 'month', y = 'number of trips', color='b').set_title('citibikenyc: number of trips per month in ' + str(year))


# ### all year stats

# In[5]:


# year summary
min_usage = 0

n_total, df_coords_total = analysis_functions.analysis_summary_year(result_map, stations_analysis_list)
print(n_total)
df_coords_total

#restrict to minimal number of usage:
df_coords_total_min_usage = df_coords_total[df_coords_total["usage"] > min_usage]
#restrict to reasonable bounds for plotting
df_coords_total_min_usage = df_coords_total_min_usage[(df_coords_total_min_usage['longitude'] != 0) & (df_coords_total_min_usage['longitude'] < -73.8)]
df_coords_total_min_usage


# In[6]:


sns.set_style("whitegrid")
norm = plt.Normalize(df_coords_total_min_usage['usage'].min(), df_coords_total_min_usage['usage'].max())
sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
sm.set_array([])

fig, ax = plt.subplots()

fig = sns.scatterplot(data=df_coords_total_min_usage, x="longitude", y="latitude", s=15, hue='usage', palette='Reds')
fig.set_title("citibikenyc stations with minimal usage of " + str(min_usage) + " rents/arrivals per year", size=18)

# Remove the legend and add a colorbar
fig.get_legend().remove()
fig.figure.colorbar(sm, ax=ax)
df_coords_total_min_usage


# In[7]:


df_geocode_all_stations = pd.read_csv('intermediate_results/df_geocode_all_stations.csv', index_col=0)
df_geocode_all_stations = df_geocode_all_stations[df_geocode_all_stations.columns.intersection(['neighbourhood', 'borough', 'city'])]

# annotate generated data with neighbourhood and borough
df_coords_total_geo = df_coords_total.join(df_geocode_all_stations)
df_coords_total_geo


# In[8]:


# also restrict citibike data to core region only
# define core region as Manhattan region that is covered by first stations in 2013
# basically Manhattan below Central Park (use Manhattan annotation from geocode AND a linear discrimination lines below central park),
# see notebook 04_reverse_geocode
# and count trip as within region, when start/end of trip is within this region

# determine for each year which stations are in this region
df_coords_total_geo_core = df_coords_total_geo[df_coords_total_geo['borough'] == 'Manhattan']
df_coords_total_geo_core = df_coords_total_geo_core[(df_coords_total_geo_core['latitude'] < (((df_coords_total_geo_core['longitude'] + 73.965)*((40.755 - 40.78)/(-73.965 + 73.99)) ) + 40.755)) & (df_coords_total_geo_core['longitude'] > -74.03)]


#check by plotting
sns.set_style("whitegrid")

fig, ax = plt.subplots()

fig = sns.scatterplot(data=df_coords_total_geo_core, x="longitude", y="latitude", s=15, size='usage', hue='borough', palette='Reds')
fig.set_title("citibikenyc stations restricted in a year ", size=18)

plt.plot([-74.03, -74.03], [40.7, 40.75], linewidth=2)
plt.plot([-73.965, -73.99], [40.755, 40.78], linewidth=2)

#okay


# In[9]:


## then count only on those stations for each year
test_table_bikes = pd.read_csv("Data/2020-citibike-tripdata/202001-citibike-tripdata/202001-citibike-tripdata_1.csv")
test_table_bikes


# In[10]:


# check restriction to subset of stations in df_coords_total_geo_core data frame
test_table_bikes_restricted = test_table_bikes[(test_table_bikes['start_station_name'].isin(df_coords_total_geo_core.index)) | (test_table_bikes['end_station_name'].isin(df_coords_total_geo_core.index))]
#test_table_bikes_restricted = (test_table_bikes['start_station_name'].isin(df_coords_total_geo_core.index)) | (test_table_bikes['end_station_name'].isin(df_coords_total_geo_core.index))
#test_table_bikes_restricted = (test_table_bikes['start_station_name'].isin(['E 1 St & 1 Ave'])) | (test_table_bikes['end_station_name'].isin(['E 1 St & 1 Ave']))
test_table_bikes_restricted


# In[11]:


df_coords_total_geo_core


# In[12]:


df_coords_total_geo_core.loc[['University Pl & E 14 St']]


# In[13]:


n_total_core, df_coords_total_core = analysis_functions.analysis_summary_year(result_map_core, stations_analysis_list_core)
print(n_total_core)
df_coords_total_core

#restrict to minimal number of usage:
df_coords_total_min_usage_core = df_coords_total_core[df_coords_total_core["usage"] > min_usage]
#restrict to reasonable bounds for plotting
df_coords_total_min_usage_core = df_coords_total_min_usage_core[(df_coords_total_min_usage_core['longitude'] != 0) & (df_coords_total_min_usage_core['longitude'] < -73.8)]
df_coords_total_min_usage_core


# In[14]:


sns.set_style("whitegrid")
norm = plt.Normalize(df_coords_total_min_usage_core['usage'].min(), df_coords_total_min_usage_core['usage'].max())
sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
sm.set_array([])

fig, ax = plt.subplots()

fig = sns.scatterplot(data=df_coords_total_min_usage_core, x="longitude", y="latitude", s=15, hue='usage', palette='Reds')
fig.set_title("citibikenyc stations with minimal usage of " + str(min_usage) + " rents/arrivals per year in core region", size=18)

# Remove the legend and add a colorbar
fig.get_legend().remove()
fig.figure.colorbar(sm, ax=ax)
df_coords_total_min_usage_core


# ## NYC accidents per year
# 
# ### monthly intervalls

# In[15]:


#Einlesen der Unfall Daten von NYC
table_accidents = pd.read_csv("Data/Motor_Vehicle_Collisions_-_Crashes_20250319.csv")

table_accidents


# In[16]:


# restrict to year of interest
table_accidents["CRASH DATE"]= pd.to_datetime(table_accidents["CRASH DATE"])

table_accidents_year = table_accidents[table_accidents["CRASH DATE"].dt.year == year]
table_accidents_year


# In[17]:


sum = 0
results_accidents = {}
for month in range(1,13):
    print("month: "+ str(month))
    table_accidents_month = table_accidents_year[table_accidents_year["CRASH DATE"].dt.month == month]
    sum = sum + len(table_accidents_month)
    print("number of accidents: " + str(len(table_accidents_month)))
    
    if len(results_accidents.keys()) == 0:
        results_accidents["NUMBER OF PERSONS INJURED"] = {}
        results_accidents["NUMBER OF PERSONS KILLED"] = {}
        results_accidents["NUMBER OF PEDESTRIANS INJURED"] = {}
        results_accidents["NUMBER OF PEDESTRIANS KILLED"] = {}
        results_accidents["NUMBER OF CYCLIST INJURED"] = {}
        results_accidents["NUMBER OF CYCLIST KILLED"] = {}
        results_accidents["NUMBER OF MOTORIST INJURED"] = {}
        results_accidents["NUMBER OF MOTORIST KILLED"] = {}
    
    results_accidents["NUMBER OF PERSONS INJURED"][month] = table_accidents_month["NUMBER OF PERSONS INJURED"].sum(skipna = True)
    results_accidents["NUMBER OF PERSONS KILLED"][month] = table_accidents_month["NUMBER OF PERSONS KILLED"].sum(skipna = True)
    results_accidents["NUMBER OF PEDESTRIANS INJURED"][month] = table_accidents_month["NUMBER OF PEDESTRIANS INJURED"].sum(skipna = True)
    results_accidents["NUMBER OF PEDESTRIANS KILLED"][month] = table_accidents_month["NUMBER OF PEDESTRIANS KILLED"].sum(skipna = True)
    results_accidents["NUMBER OF CYCLIST INJURED"][month] = table_accidents_month["NUMBER OF CYCLIST INJURED"].sum(skipna = True)
    results_accidents["NUMBER OF CYCLIST KILLED"][month] = table_accidents_month["NUMBER OF CYCLIST KILLED"].sum(skipna = True)
    results_accidents["NUMBER OF MOTORIST INJURED"][month] = table_accidents_month["NUMBER OF MOTORIST INJURED"].sum(skipna = True)
    results_accidents["NUMBER OF MOTORIST KILLED"][month] = table_accidents_month["NUMBER OF MOTORIST KILLED"].sum(skipna = True)
    
print(sum)
print(results_accidents)


# In[18]:


df_accidents_year = pd.DataFrame.from_dict(results_accidents)
df_accidents_year["CHECK"] = df_accidents_year["NUMBER OF PEDESTRIANS INJURED"] + df_accidents_year["NUMBER OF CYCLIST INJURED"] + df_accidents_year["NUMBER OF MOTORIST INJURED"]
df_accidents_year["month"] = df_bike_trips_year.index
df_accidents_year_long = pd.melt(df_accidents_year, id_vars=['month'], value_vars=['NUMBER OF PERSONS INJURED', 'NUMBER OF PERSONS KILLED', \
                                                      'NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED', \
                                                      'NUMBER OF CYCLIST INJURED', 'NUMBER OF CYCLIST KILLED', \
                                                      'NUMBER OF MOTORIST INJURED', 'NUMBER OF MOTORIST KILLED'], ignore_index=False).reset_index(drop=True)

df_accidents_year_long['value'] = df_accidents_year_long['value'].astype(int)
df_accidents_year_long = df_accidents_year_long.sort_values(by=['month', 'variable'])
df_accidents_year_long


# In[19]:


rcParams['figure.figsize'] = 15,10


# In[20]:


# injured plot
df_accidents_year_long_injured = df_accidents_year_long[df_accidents_year_long["variable"].str.contains("INJURED")]
df_accidents_year_long_injured

sns.barplot(data = df_accidents_year_long_injured, x = 'month', y='value', hue='variable').set_title('NYC accident injuries per month in 2023')


# In[21]:


# killed plot
df_accidents_year_long_killed = df_accidents_year_long[df_accidents_year_long["variable"].str.contains("KILLED")]
df_accidents_year_long_killed

sns.barplot(data = df_accidents_year_long_killed, x = 'month', y='value', hue='variable').set_title('NYC accident deaths per month in 2023')


# In[22]:


# cyclists only (as relevant for citibikenyc, injured and killed)
df_cyclists_injured = df_accidents_year_long_injured[(df_accidents_year_long_injured["variable"] == "NUMBER OF CYCLIST INJURED")].reset_index(drop=True)
df_cyclists_killed = df_accidents_year_long_killed[df_accidents_year_long_killed["variable"] == "NUMBER OF CYCLIST KILLED"].reset_index(drop=True)
df_cyclists = df_cyclists_killed.merge(df_cyclists_injured, on="month")
df_cyclists = df_cyclists.rename(columns={'value_x' : 'killed', 'value_y' : 'injured'})
df_cyclists

df_cyclists = pd.DataFrame(pd.melt(df_cyclists, id_vars=['month'], value_vars=['killed', 'injured']))
df_cyclists.sort_values('month', inplace = True)
df_cyclists


# In[23]:


g = sns.FacetGrid(df_cyclists, col="variable", sharey=False)
g.map(sns.scatterplot, "month", "value", s=100, alpha=.5)


# ### per year

# In[24]:


accidents_coords = table_accidents_year[["LATITUDE", "LONGITUDE"]]
print(len(accidents_coords))
#remove NaNs
accidents_coords_cleaned = accidents_coords.dropna()
print(len(accidents_coords_cleaned))

# also remove Lat/LONG=0 
accidents_coords_cleaned = accidents_coords_cleaned[accidents_coords_cleaned["LATITUDE"] != 0]
accidents_coords_cleaned.rename(columns={'LONGITUDE': 'longitude', 'LATITUDE': 'latitude'}, inplace = True)
accidents_coords_cleaned


# In[25]:


# make map with injuries/deaths per year

sns.set_style("whitegrid")
sns.scatterplot(data=accidents_coords_cleaned, x="longitude", y="latitude", s=2, color = 'blue').set_title("Accidents "+ str(year), size=20)


# In[26]:


# only plot cyclist accidents
accidents_coords_cyclists = table_accidents_year[(table_accidents_year["NUMBER OF CYCLIST INJURED"] >0) | (table_accidents_year["NUMBER OF CYCLIST KILLED"] > 0)]
print(accidents_coords_cyclists["BOROUGH"].unique())
#accidents_coords_cyclists = accidents_coords_cyclists[(accidents_coords_cyclists["BOROUGH"] == "MANHATTAN")]# |\
#(accidents_coords_cyclists["BOROUGH"] == "BRONX") | (accidents_coords_cyclists["BOROUGH"] == "BROOKLYN") |\
#(accidents_coords_cyclists["BOROUGH"] == "QUEENS") | (accidents_coords_cyclists["BOROUGH"] == "STATEN ISLAND")]
accidents_coords_cyclists = accidents_coords_cyclists[["LATITUDE", "LONGITUDE"]]
accidents_coords_cyclists_cleaned = accidents_coords_cyclists[accidents_coords_cyclists["LATITUDE"] != 0]
accidents_coords_cyclists_cleaned.rename(columns={'LONGITUDE': 'longitude', 'LATITUDE': 'latitude'}, inplace = True)
accidents_coords_cyclists_cleaned


# In[27]:


sns.set_style("whitegrid")
sns.scatterplot(data=accidents_coords_cyclists_cleaned, x="longitude", y="latitude", s=2, color = 'blue').set_title("Cyclist accidents "+ str(year), size=20)


# In[28]:


# now restrict to areas near much used citibike stations (for rent/arrival) in core region
# go through accidents and pick
accidents_coords_cyclists["in_region"] = 0

# loop explicitly over tables as tables are not too large
count = 0
for index, row in accidents_coords_cyclists.iterrows():
    #print(row['c1'], row['c2'])
    if (count%100) == 0:
        print(count)
    count = count + 1
    close_enough = False
    for index2, row2 in df_coords_total_geo_core.iterrows():
        distance = math.sqrt(math.pow((row['LONGITUDE'] - row2['longitude']) * 85118, 2.0) + math.pow((row['LATITUDE'] - row2['latitude']) * 111120, 2.0))
        if distance < 500:
            close_enough = True 
            break
    if close_enough:
        accidents_coords_cyclists.loc[index, "in_region"] = 1

        
accidents_coords_cyclists[accidents_coords_cyclists["in_region"] == 1]


# In[29]:


accidents_coords_cyclists_region = accidents_coords_cyclists[accidents_coords_cyclists["in_region"] == 1]

sns.set_style("whitegrid")
sns.scatterplot(data=accidents_coords_cyclists_region, x="LONGITUDE", y="LATITUDE", s=2, color = 'blue').set_title("Cyclist accidents "+ str(year), size=20)


# In[30]:


table_accidents_year = table_accidents[table_accidents["CRASH DATE"].dt.year == year]
table_accidents_year


# In[31]:


# check crash times/occurences for weekends/weekdays
table_accidents_year['CRASH DATE'] = pd.to_datetime(table_accidents_year['CRASH DATE'])
table_accidents_year['hour'] = pd.to_datetime(table_accidents_year['CRASH TIME'], format='%H:%M').dt.strftime("%H").astype(int)
table_accidents_year['day'] = table_accidents_year['CRASH DATE'].dt.weekday
table_accidents_year['workday'] = table_accidents_year['day'].isin([0, 1, 2, 3, 4]).astype(int)
table_accidents_year_workday = table_accidents_year[table_accidents_year['workday'] == 1]
table_accidents_year_weekend = table_accidents_year[table_accidents_year['workday'] == 0]

# restrict to cyclists involved
table_accidents_cyclist_year_workday = table_accidents_year_workday[(table_accidents_year_workday["NUMBER OF CYCLIST INJURED"] > 0) | (table_accidents_year_workday["NUMBER OF CYCLIST KILLED"] > 0)]
table_accidents_cyclist_year_weekend = table_accidents_year_weekend[(table_accidents_year_weekend["NUMBER OF CYCLIST INJURED"] > 0) | (table_accidents_year_weekend["NUMBER OF CYCLIST KILLED"] > 0)]

table_accidents_cyclist_year_workday[table_accidents_cyclist_year_workday['hour'] == 6]
#table_accidents_cyclist_year_weekend


# In[32]:


times_workday = table_accidents_cyclist_year_workday[['hour', 'day']]
#times_workday.sort_values('hour')
times_workday
sns.histplot(data=times_workday, x="hour", discrete=True).set_title("Distribution of times of bicycle accidents during workdays (Monday-Friday)")


# In[33]:


times_weekend = table_accidents_cyclist_year_weekend[['hour', 'day']]
#times_workday.sort_values('hour')
times_weekend
sns.histplot(data=times_weekend, x="hour", discrete=True).set_title("Distribution of times of bicycle accidents during weekends (Saturday-Sunday)")

