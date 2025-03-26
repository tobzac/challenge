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


# ## citibikenyc per year
# 
# ### monthly intervalls
# 

# In[2]:


# analysis per month steps

def analysis_per_month(df_month):
    
    #-------------------------
    # get number of bike trips
    # full list used for simple stats like total number of trips etc.
    n_bike_trips = len(df_month.index)
    
    # cleaned list for analyses, where values are needed
    df_month_cleaned = df_month.dropna()
    
    # other stuff
    #-------------------------------------------------------
    # get station list per month and number of stations used
    # get number of occurences of different stations
    n_occurences_start = df_month_cleaned['start_station_name'].value_counts().to_dict()
    n_occurences_end = df_month_cleaned['end_station_name'].value_counts().to_dict()
    n_occurences = {key: n_occurences_start.get(key, 0) + n_occurences_end.get(key, 0) for key in set(n_occurences_start) | set(n_occurences_end)}
    df_n_occurences = pd.DataFrame.from_dict(n_occurences, orient='index').rename(columns={0: 'usage'})

    # iterate through table and form map with coordinates of different stations
    start_station_names_to_coords = pd.Series(list(zip(df_month_cleaned['start_lng'], df_month_cleaned['start_lat'])), index=df_month_cleaned.start_station_name).to_dict()
    end_station_names_to_coords = pd.Series(list(zip(df_month_cleaned['end_lng'], df_month_cleaned['end_lat'])), index=df_month_cleaned.end_station_name).to_dict()

    station_names_to_coords = start_station_names_to_coords
    station_names_to_coords.update(end_station_names_to_coords)
    station_names_to_coords
    #len(station_names_to_coords)
    df_coords = pd.DataFrame.from_dict(station_names_to_coords, orient='index')
    df_coords = df_coords.rename(columns={0: 'longitude', 1: 'latitude'})
    df_coords = df_coords.join(df_n_occurences)
    
    # get median bike trip duration
    
    return n_bike_trips, df_coords


# In[3]:


# summarize number for whole year

def analysis_summary_year(results_map, stations_analysis_list):
    
    #-------------------------------------------
    # sum up all bike trips to get total number:
    s = 0
    for key in results_map:
        s = s + results_map[key]
    
    #-------------------------------------------------------------------
    # make one station list per year and number of stations used per year 
    # is of course approximation, but can then be also used for building up a visualization grid
    # concatenate all dfs from list
    df_all = pd.concat(stations_analysis_list, axis=0)
    
    # sum over index to get usage values for all stations
    only_usage = pd.DataFrame(df_all["usage"].groupby(level=0).sum())
    station_names_to_coords = pd.Series(list(zip(df_all['longitude'], df_all['latitude'])), index = df_all.index).to_dict()
    df_coords = pd.DataFrame.from_dict(station_names_to_coords, orient='index')
    df_coords = df_coords.rename(columns={0: 'longitude', 1: 'latitude'})
    df_coords_year = df_coords.join(only_usage).sort_values('usage', ascending = False)


    return s, df_coords_year


# In[4]:


# specify year for analysis
year = 2022

month_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
#month_list = ["01", "06"]
base_folder_name = str(year)+"-citibike-tripdata"

#results
result_map = {}
stations_analysis_list = []

# read in successively all data for month, then for all months
for month in month_list:
    print("month: " + month)
    #collect all files for the month
    month_folder_name = str(year) + month + "-citibike-tripdata"
    #dataframe for month
    df_list = []
    full_path = "Data/" + base_folder_name + "/" + month_folder_name + "/"
    for filename in os.listdir(full_path):
        if filename.endswith(".csv") and month_folder_name in filename:
            print(filename)
            df_month_partial = pd.read_csv(full_path + filename)
            df_list.append(df_month_partial)
    
    df_month = pd.concat(df_list, axis=0, ignore_index=True)
    
    # perform monthly analysis
    result_n_trips, df_coords_stations = analysis_per_month(df_month)
    result_map[month] = result_n_trips
    stations_analysis_list.append(df_coords_stations)
    
    print("numer of trips: " + str(result_n_trips))
    print("number of stations used: " + str(len(df_coords_stations)))
    
print(result_map)


# In[5]:


# plot
result_map_extended = {}
result_map_extended[2022] = result_map
df_bike_trips_year = pd.DataFrame.from_dict(result_map_extended)
df_bike_trips_year["month"] = df_bike_trips_year.index
df_bike_trips_year = df_bike_trips_year.rename(columns={2022: 'number of trips'})

rcParams['figure.figsize'] = 11.7,8.27

sns.barplot(data = df_bike_trips_year, x = 'month', y = 'number of trips', color='b').set_title('citibikenyc: number of trips per month in ' + str(year))


# ### all year stats

# In[6]:


# year summary
min_usage = 50000

n_total, df_coords_total = analysis_summary_year(result_map, stations_analysis_list)
print(n_total)
df_coords_total

#restrict to minimal number of usage:
df_coords_total_min_usage = df_coords_total[df_coords_total["usage"] > min_usage]
df_coords_total_min_usage


# In[7]:


sns.set_style("whitegrid")
norm = plt.Normalize(df_coords_total_min_usage['usage'].min(), df_coords_total_min_usage['usage'].max())
sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
sm.set_array([])

ax = sns.scatterplot(data=df_coords_total_min_usage, x="longitude", y="latitude", s=15, hue='usage', palette='Reds')
ax.set_title("citibikenyc stations with minimal usage of " + str(min_usage) + " rents/arrivals per year", size=18)

# Remove the legend and add a colorbar
ax.get_legend().remove()
ax.figure.colorbar(sm)
df_coords_total_min_usage


# ## NYC accidents per year
# 
# ### monthly intervalls

# In[8]:


#Einlesen der Unfall Daten von NYC
table_accidents = pd.read_csv("Data/Motor_Vehicle_Collisions_-_Crashes_20250319.csv")

table_accidents


# In[9]:


# restrict to year of interest
table_accidents["CRASH DATE"]= pd.to_datetime(table_accidents["CRASH DATE"])

table_accidents_year = table_accidents[table_accidents["CRASH DATE"].dt.year == year]
table_accidents_year


# In[10]:


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


# In[11]:


df_accidents_year = pd.DataFrame.from_dict(results_accidents)
df_accidents_year["CHECK"] = df_accidents_year["NUMBER OF PEDESTRIANS INJURED"] + df_accidents_year["NUMBER OF CYCLIST INJURED"] + df_accidents_year["NUMBER OF MOTORIST INJURED"]
df_accidents_year["month"] = df_bike_trips_year.index
df_accidents_year_long = pd.melt(df_accidents_year, id_vars=['month'], value_vars=['NUMBER OF PERSONS INJURED', 'NUMBER OF PERSONS KILLED',                                                       'NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED',                                                       'NUMBER OF CYCLIST INJURED', 'NUMBER OF CYCLIST KILLED',                                                       'NUMBER OF MOTORIST INJURED', 'NUMBER OF MOTORIST KILLED'], ignore_index=False).reset_index(drop=True)

df_accidents_year_long['value'] = df_accidents_year_long['value'].astype(int)
df_accidents_year_long = df_accidents_year_long.sort_values(by=['month', 'variable'])
df_accidents_year_long


# In[12]:


rcParams['figure.figsize'] = 15,10


# In[13]:


# injured plot
df_accidents_year_long_injured = df_accidents_year_long[df_accidents_year_long["variable"].str.contains("INJURED")]
df_accidents_year_long_injured

sns.barplot(data = df_accidents_year_long_injured, x = 'month', y='value', hue='variable').set_title('NYC accident injuries per month in 2023')


# In[14]:


# killed plot
df_accidents_year_long_killed = df_accidents_year_long[df_accidents_year_long["variable"].str.contains("KILLED")]
df_accidents_year_long_killed

sns.barplot(data = df_accidents_year_long_killed, x = 'month', y='value', hue='variable').set_title('NYC accident deaths per month in 2023')


# In[15]:


# cyclists only (as relevant for citibikenyc, injured and killed)
df_cyclists_injured = df_accidents_year_long_injured[(df_accidents_year_long_injured["variable"] == "NUMBER OF CYCLIST INJURED")].reset_index(drop=True)
df_cyclists_killed = df_accidents_year_long_killed[df_accidents_year_long_killed["variable"] == "NUMBER OF CYCLIST KILLED"].reset_index(drop=True)
df_cyclists = df_cyclists_killed.merge(df_cyclists_injured, on="month")
df_cyclists = df_cyclists.rename(columns={'value_x' : 'killed', 'value_y' : 'injured'})
df_cyclists

df_cyclists = pd.DataFrame(pd.melt(df_cyclists, id_vars=['month'], value_vars=['killed', 'injured']))
df_cyclists.sort_values('month', inplace = True)
df_cyclists


# In[16]:


g = sns.FacetGrid(df_cyclists, col="variable", sharey=False)
g.map(sns.scatterplot, "month", "value", s=100, alpha=.5)


# ### per year

# In[17]:


accidents_coords = table_accidents_year[["LATITUDE", "LONGITUDE"]]
print(len(accidents_coords))
#remove NaNs
accidents_coords_cleaned = accidents_coords.dropna()
print(len(accidents_coords_cleaned))

# also remove Lat/LONG=0 
accidents_coords_cleaned = accidents_coords_cleaned[accidents_coords_cleaned["LATITUDE"] != 0]
accidents_coords_cleaned.rename(columns={'LONGITUDE': 'longitude', 'LATITUDE': 'latitude'}, inplace = True)
accidents_coords_cleaned


# In[18]:


# make map with injuries/deaths per year

sns.set_style("whitegrid")
sns.scatterplot(data=accidents_coords_cleaned, x="longitude", y="latitude", s=2, color = 'blue').set_title("Accidents "+ str(year), size=20)


# In[19]:


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


# In[20]:


sns.set_style("whitegrid")
sns.scatterplot(data=accidents_coords_cyclists_cleaned, x="longitude", y="latitude", s=2, color = 'blue').set_title("Cyclist accidents "+ str(year), size=20)


# In[21]:


# now restrict to areas near much used citibike stations (for rent/arrival)
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
    for index2, row2 in df_coords_total_min_usage.iterrows():
        distance = math.sqrt(math.pow((row['LONGITUDE'] - row2['longitude']) * 85118, 2.0) + math.pow((row['LATITUDE'] - row2['latitude']) * 111120, 2.0))
        if distance < 1000:
            close_enough = True
            break
    if close_enough:
        accidents_coords_cyclists.loc[index, "in_region"] = 1

        
accidents_coords_cyclists[accidents_coords_cyclists["in_region"] == 1]


# In[22]:


accidents_coords_cyclists_region = accidents_coords_cyclists[accidents_coords_cyclists["in_region"] == 1]

sns.set_style("whitegrid")
sns.scatterplot(data=accidents_coords_cyclists_region, x="LONGITUDE", y="LATITUDE", s=2, color = 'blue').set_title("Cyclist accidents "+ str(year), size=20)

