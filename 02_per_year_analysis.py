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
import datetime as dt
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
    # get number of bike trips
    n_bike_trips = len(df_month.index)
    
    # other stuff
    # get number of stations used
    # get median bike trip duration
    
    
    return n_bike_trips


# In[3]:


# summarize number for whole year

def analysis_summary_year(results_map):
    # sum up all bike trips to get total number:
    sum = 0
    for key in results_map:
        sum = sum + results_map[key]
        
    return sum


# In[4]:


# specify year for analysis
year = 2023

month_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
#month_list = ["01", "06"]
base_folder_name = str(year)+"-citibike-tripdata"

#results
result_map = {}

# read in successively all data for month, then for all months
for month in month_list:
    print(month)
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
    result = analysis_per_month(df_month)
    result_map[month] = result
    
    print("month: " + month)
    print(result)
    
print(result_map)


# In[5]:


# plot
result_map_extended = {}
result_map_extended[2023] = result_map
df_bike_trips_year = pd.DataFrame.from_dict(result_map_extended)
df_bike_trips_year["month"] = df_bike_trips_year.index
df_bike_trips_year = df_bike_trips_year.rename(columns={2023: 'number of trips'})

sns.barplot(data = df_bike_trips_year, x = 'month', y = 'number of trips', color='b').set_title('citibikenyc: number of trips per month in 2023')


# ### all year stats

# In[6]:


# year summary
analysis_summary_year(result_map)


# ## NYC accidents per year
# 
# ### monthly intervalls

# In[7]:


#Einlesen der Unfall Daten von NYC
table_accidents = pd.read_csv("Data/Motor_Vehicle_Collisions_-_Crashes_20250319.csv")

table_accidents


# In[8]:


# restrict to year of interest
table_accidents["CRASH DATE"]= pd.to_datetime(table_accidents["CRASH DATE"])

table_accidents_year = table_accidents[table_accidents["CRASH DATE"].dt.year == year]
table_accidents_year


# In[9]:


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


# In[14]:


df_accidents_year = pd.DataFrame.from_dict(results_accidents)
df_accidents_year["CHECK"] = df_accidents_year["NUMBER OF PEDESTRIANS INJURED"] + df_accidents_year["NUMBER OF CYCLIST INJURED"] + df_accidents_year["NUMBER OF MOTORIST INJURED"]
df_accidents_year["month"] = df_bike_trips_year.index
df_accidents_year_long = pd.melt(df_accidents_year, id_vars=['month'], value_vars=['NUMBER OF PERSONS INJURED', 'NUMBER OF PERSONS KILLED',                                                       'NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED',                                                       'NUMBER OF CYCLIST INJURED', 'NUMBER OF CYCLIST KILLED',                                                       'NUMBER OF MOTORIST INJURED', 'NUMBER OF MOTORIST KILLED'], ignore_index=False).reset_index(drop=True)

df_accidents_year_long['value'] = df_accidents_year_long['value'].astype(int)
df_accidents_year_long = df_accidents_year_long.sort_values(by=['month', 'variable'])
df_accidents_year_long


# In[15]:


rcParams['figure.figsize'] = 15,10


# In[16]:


# injured plot
df_accidents_year_long_injured = df_accidents_year_long[df_accidents_year_long["variable"].str.contains("INJURED")]
df_accidents_year_long_injured

sns.barplot(data = df_accidents_year_long_injured, x = 'month', y='value', hue='variable').set_title('NYC accident injuries per month in 2023')


# In[17]:


# killed plot
df_accidents_year_long_killed = df_accidents_year_long[df_accidents_year_long["variable"].str.contains("KILLED")]
df_accidents_year_long_killed

sns.barplot(data = df_accidents_year_long_killed, x = 'month', y='value', hue='variable').set_title('NYC accident deaths per month in 2023')

