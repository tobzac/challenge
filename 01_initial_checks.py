#!/usr/bin/env python
# coding: utf-8

# # Data Science Challenge
# 
# Wie beschrieben in dem file 24_09-Data_Science_Challenge.pdf sollen die öffentlich verfügbaren Daten der Firma citibikenyc (https://citibikenyc.com/) untersucht werden zusammen mit den Unfall Statistiken des NYPD.
# Ziel ist es eine Analyse zu machen, sodass die Firma ihre Daten sinnvoll nutzen kann um z.B. eine Kooperation mit einer Versicherung einzugehen. Es kann auch versucht werden, die Zusammenarbeit für die Versicherung ebenfalls mit Auffinden zusätzlicher Vorteile (ausgenommen dem Vorteil eines zusätzlichen Kunden) schmackhaft zu machen.

# In[1]:


# imports für das notebook
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import rcParams
# importing re for regular expressions
import re


# 
# Ziel dieses notebooks ist es einen Überblick über die Daten zu bekommen (Spalten/Größe), erste plots zu checken.
# Es werden zuerst die Daten der Firma citibikenyc untersucht, anschließend die Unfall Statistik der Stadt NYC.
# Außerdem sollen erste Möglichkeiten zur tiefergehenden Analyse und Korrelation der Daten aus beiden Quellen eruiert werden.
# 
# ## Daten citibikenyc
# 
# Download der kompletten Daten für 2023 von https://s3.amazonaws.com/tripdata/index.html.
# Es werden der Einfachheit hier nur die Daten von Januar 2023 betrachtet.

# In[2]:


#Einlesen der Daten von citibikenyc

test_table_bikes = pd.read_csv("Data/2023-citibike-tripdata/202301-citibike-tripdata/202301-citibike-tripdata_1.csv")

test_table_bikes


# In[3]:


# Überblick über mögliche Spalteneinträge
for column in ["rideable_type", "start_station_name", "start_station_id", "end_station_name", "end_station_id", "member_casual"]:
    print(column+": "+str(test_table_bikes[column].unique())+" "+str(len(test_table_bikes[column].unique())))

#check für nan und Entfernen der Zeilen
print(test_table_bikes[test_table_bikes.isnull().any(axis=1)])
print(len(test_table_bikes[test_table_bikes.isnull().any(axis=1)]))
test_table_bikes.dropna(inplace = True)
print(test_table_bikes[test_table_bikes.isnull().any(axis=1)])


# In[4]:


# Konvertierung aller station_ids in strings
test_table_bikes.start_station_id = test_table_bikes.start_station_id.astype(str)
test_table_bikes.end_station_id = test_table_bikes.end_station_id.astype(str)


# In[5]:


# Neue Spalten "duration", "diff_lat", "diff_lng", "direct_distance"
# Konvertierung von length/latitude DIfferenzen in Entfernungen in Meilen

test_table_bikes.dtypes

test_table_bikes["ended_at"] = pd.to_datetime(test_table_bikes["ended_at"])
test_table_bikes["started_at"] = pd.to_datetime(test_table_bikes["started_at"])

test_table_bikes["duration"] = test_table_bikes["ended_at"] - test_table_bikes["started_at"]
test_table_bikes["diff_lat"] = test_table_bikes["end_lat"] - test_table_bikes["start_lat"]
test_table_bikes["diff_lng"] = test_table_bikes["end_lng"] - test_table_bikes["start_lng"]
#test_table["direct_distance"] = 

test_table_bikes


# Check der Stationen: IDs und Namen, Verteilung, Vorkommen im Datenset

# In[6]:


# Überblick über die Stationen
# 1. a) mittels station_ids "5626.13" (Zahl + dot + Zahl):
station_id_full_start_unique = test_table_bikes.start_station_id.unique()
print("StationID full unique start: "+str(len(station_id_full_start_unique)))
station_id_full_end_unique = test_table_bikes.end_station_id.unique()
print("StationID full unique end: "+str(len(station_id_full_end_unique)))
station_id_full = pd.concat([pd.DataFrame(station_id_full_start_unique), pd.DataFrame(station_id_full_end_unique)]).reset_index()
station_id_full_unique = station_id_full[0].unique()
print("StationID full unique: "+str(len(station_id_full_unique)))

# 1. b) mittels station_ids "5626" (Zahl ohne (dot + Zahl)):
station_id_start_unique = test_table_bikes.start_station_id.astype("string").str.split(".", n=1, expand=True)[0].unique()
print("StationID part unique start: "+str(len(station_id_start_unique)))
station_id_end_unique = test_table_bikes.end_station_id.astype("string").str.split(".", n=1, expand=True)[0].unique()
print("StationID part unique end: "+str(len(station_id_end_unique)))
station_id = pd.concat([pd.DataFrame(station_id_start_unique), pd.DataFrame(station_id_end_unique)]).reset_index()
station_id_unique = station_id[0].unique()
print("StationID part unique: "+str(len(station_id_unique)))

# 2. mittels station_name
station_name_start_unique = test_table_bikes.start_station_name.unique()
print("Station name unique start: "+str(len(station_name_start_unique)))
station_name_end_unique = test_table_bikes.end_station_name.unique()
print("Station name unique end: "+str(len(station_name_end_unique)))
station_name = pd.concat([pd.DataFrame(station_name_start_unique), pd.DataFrame(station_name_end_unique)]).reset_index()
station_name_unique = station_name[0].unique()
print("Station name unique: "+str(len(station_name_unique)))


# In[7]:


# Check Zusammenhang station name und station id
names_ids_stations = list(zip(test_table_bikes.start_station_name, test_table_bikes.start_station_id))
names_ids_stations_unique = set(names_ids_stations)
names_ids_stations_unique

names_2_ids = {}
for t in names_ids_stations_unique:
    if t[0] in names_2_ids.keys():
        names_2_ids[t[0]].append(t[1])
    else:
        names_2_ids[t[0]] = [t[1]]

count = 0
for key in names_2_ids.keys():
    if len(names_2_ids[key]) > 1:
        count = count + 1
        print(str(count) + ": " + key + " " + str(names_2_ids[key]))


# In[8]:


# Bereinigen der station IDs sodass '5332.1' = '5332.10'

test_table_bikes_cleaned = test_table_bikes.copy()

test_table_bikes_cleaned.start_station_id = test_table_bikes_cleaned.start_station_id.apply(lambda string : string if re.match(r'.*[a-zA-Z].*', string) else str("{:.2f}".format(float(string))))
test_table_bikes_cleaned.end_station_id = test_table_bikes_cleaned.end_station_id.apply(lambda string : string if re.match(r'.*[a-zA-Z].*', string) else str("{:.2f}".format(float(string))))


# In[9]:



# Nun noch einmal Check Station IDs/Namen:
# Überblick über die Stationen
# 1. a) mittels station_ids "5626.13" (Zahl + dot + Zahl):
station_id_full_start_unique = test_table_bikes_cleaned.start_station_id.unique()
print("StationID full unique start: "+str(len(station_id_full_start_unique)))
station_id_full_end_unique = test_table_bikes_cleaned.end_station_id.unique()
print("StationID full unique end: "+str(len(station_id_full_end_unique)))
station_id_full = pd.concat([pd.DataFrame(station_id_full_start_unique), pd.DataFrame(station_id_full_end_unique)]).reset_index()
station_id_full_unique = station_id_full[0].unique()
print("StationID full unique: "+str(len(station_id_full_unique)))

# 2. mittels station_name
station_name_start_unique = test_table_bikes_cleaned.start_station_name.unique()
print("Station name unique start: "+str(len(station_name_start_unique)))
station_name_end_unique = test_table_bikes_cleaned.end_station_name.unique()
print("Station name unique end: "+str(len(station_name_end_unique)))
station_name = pd.concat([pd.DataFrame(station_name_start_unique), pd.DataFrame(station_name_end_unique)]).reset_index()
station_name_unique = station_name[0].unique()
print("Station name unique: "+str(len(station_name_unique)))


# plots

# In[10]:


# erste plots
#Verteilung der Stationen (alle start/end lat/lng)
#get number of occurences of different stations
n_occurences_start = test_table_bikes_cleaned['start_station_name'].value_counts().to_dict()
n_occurences_end = test_table_bikes_cleaned['end_station_name'].value_counts().to_dict()
n_occurences = {key: n_occurences_start.get(key, 0) + n_occurences_end.get(key, 0) for key in set(n_occurences_start) | set(n_occurences_end)}
df_n_occurences = pd.DataFrame.from_dict(n_occurences, orient='index').rename(columns={0: 'usage'})


# iterate through table and form map with coordinates of different stations
start_station_names_to_coords = pd.Series(list(zip(test_table_bikes_cleaned['start_lng'], test_table_bikes_cleaned['start_lat'])), index=test_table_bikes_cleaned.start_station_name).to_dict()
end_station_names_to_coords = pd.Series(list(zip(test_table_bikes_cleaned['end_lng'], test_table_bikes_cleaned['end_lat'])), index=test_table_bikes_cleaned.end_station_name).to_dict()

station_names_to_coords = start_station_names_to_coords
station_names_to_coords.update(end_station_names_to_coords)
station_names_to_coords
#len(station_names_to_coords)
df_coords = pd.DataFrame.from_dict(station_names_to_coords, orient='index')
df_coords = df_coords.rename(columns={0: 'longitude', 1: 'latitude'})
df_coords = df_coords.join(df_n_occurences)

# figure size in inches
rcParams['figure.figsize'] = 11.7,8.27
sns.set_style("whitegrid")
sns.scatterplot(data=df_coords, x="longitude", y="latitude", s=12, hue='usage').set_title("citibikenyc stations", size=20)
df_coords


# In[11]:


# plots stations


# In[12]:


# Verteilung Ausleih Startzeiten/Endzeiten


# In[13]:


# Verteilung distances End-Startpunkt


# In[14]:


# Verteilung Ausleihzeiten


# ## Unfall Statistik NYC
# 
# Download als csv Datei von https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data
# 

# In[ ]:


#Einlesen der Unfall Daten von NYC
table_accidents = pd.read_csv("Data/Motor_Vehicle_Collisions_-_Crashes_20250319.csv")

table_accidents.dtypes


# In[ ]:


crash_dates = list(table_accidents["CRASH DATE"].unique())
print(crash_dates)


# In[ ]:




