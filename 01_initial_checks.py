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
from scipy.optimize import curve_fit
import seaborn as sns
from matplotlib import rcParams
import matplotlib.pyplot as plt
import datetime as dt
# importing re for regular expressions
import re


# 
# Ziel dieses notebooks ist es einen Überblick über die Daten zu bekommen (Spalten/Größe), erste plots zu checken.
# Es werden zuerst die Daten der Firma citibikenyc untersucht, anschließend die Unfall Statistik der Stadt NYC.
# Außerdem sollen erste Möglichkeiten zur tiefergehenden Analyse und Korrelation der Daten aus beiden Quellen eruiert werden.
# 
# ## Daten citibikenyc
# ### data from 2020 and later
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

# unter Verwendung von https://wiki.openstreetmap.org/wiki/DE:Genauigkeit_von_Koordinaten
# 1 Längengrad Differenz entspricht auf Breite 40 Grad (NYC): 85118 Meter
# 1 Breitengrad Differenz entspricht 111120 Meter
test_table_bikes["direct_distance"] = np.sqrt(np.power(test_table_bikes["diff_lat"] * 111120, 2.0) + np.power(test_table_bikes["diff_lng"] * 85118, 2.0))


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

#print(n_occurences_start["W 54 St & 11 Ave"])
#print(n_occurences_end["W 54 St & 11 Ave"])
#df_coords


# In[11]:


# Verteilung Ausleih Startzeiten/Endzeiten

start_times = pd.DataFrame(test_table_bikes_cleaned["started_at"])
end_times = pd.DataFrame(test_table_bikes_cleaned["ended_at"])

times = pd.concat([start_times, end_times], axis=1)
times["started_at"] = times["started_at"].dt.hour
times["ended_at"] = times["ended_at"].dt.hour        
times

sns.histplot(data=times, x="started_at", discrete=True).set_title("Distribution of start hour of rent during day")


# klar sichtbar: superposition 2er Verteilungen: einer Arbeits/Berufsverkehr Verteilung, welche um 8 Uhr Morgens und 17 Nachmittags peaked und einer Basis-Verteilung von Ausleihen, welche wahrscheinlich um 14/15 Uhr peaked. Hierdurch könnte man grob den Anteil des reinen Berufsverkehrs/transits in den Ausleihen schätzen. Weg zur Arbeit könnte Versicherungs-technisch besonders relevant sein...

# In[12]:


sns.histplot(data=times, x="ended_at", discrete=True).set_title("Distribution of end hour of rent during day")


# In[13]:


# Verteilung duration
duration = pd.DataFrame(test_table_bikes_cleaned["duration"].dt.total_seconds() / 60)
#remove 50 largest values as some quite large outliers
duration = duration.drop(duration["duration"].sort_values().tail(50).index)
duration

sns.histplot(data=duration, x="duration", bins=200, binrange=(0,100)).set_title("Distribution of rent lengths")


# In[14]:


# Verteilung direct distances End-Startpunkt
sns.histplot(data=test_table_bikes_cleaned, x="direct_distance", bins=200, binrange=(0,10000)).set_title("Distribution of direct distance between start/end point of trip")


# In[15]:


# classical bike vs electric bike
df_types = pd.DataFrame(test_table_bikes_cleaned["rideable_type"].value_counts())
df_types.rename(columns = {"count": "occurence"}, inplace=True)
df_types
sns.barplot(data=df_types, x=df_types.index, y="occurence").set_title("classic or electrical")


# In[16]:


# number of occurence of specific star-end-combinations
test_table_bikes_cleaned['start_end_combo'] = test_table_bikes_cleaned['start_station_name'] + ' - ' + test_table_bikes_cleaned['end_station_name']
test_table_bikes_cleaned.value_counts('start_end_combo')


# ### data before 2020
# columns have different names and also some additional/different columns, e.g. gender and age is new and not present in newer data.

# In[17]:


#test_table_bikes_old = pd.read_csv("Data/2017-citibike-tripdata/1_January/201701-citibike-tripdata.csv_1.csv")
#test_table_bikes_old = pd.read_csv("Data/2013-citibike-tripdata/6_June/201306-citibike-tripdata_1.csv")
#test_table_bikes_old = pd.read_csv("Data/2014-citibike-tripdata/6_June/201406-citibike-tripdata_1.csv")
#test_table_bikes_old = pd.read_csv("Data/2015-citibike-tripdata/6_June/201506-citibike-tripdata_1.csv")
test_table_bikes_old = pd.read_csv("Data/2016-citibike-tripdata/6_June/201606-citibike-tripdata_1.csv")
test_table_bikes_old


# In[18]:


#rename columns so that analysis workflow for newer data also works here:

if 'User Type' in test_table_bikes_old.columns:
    test_table_bikes_old = test_table_bikes_old.drop(['Birth Year', 'Gender', 'User Type'], axis=1)
    test_table_bikes_old = test_table_bikes_old.rename(columns={'Start Time': 'started_at', 'Stop Time': 'ended_at',\
                                                            'Start Station ID': 'start_station_id', 'Start Station Name': 'start_station_name',\
                                                            'Start Station Latitude': 'start_lat', 'Start Station Longitude': 'start_lng',\
                                                            'End Station ID' : 'end_station_id', 'End Station Name': 'end_station_name',\
                                                            'End Station Latitude': 'end_lat', 'End Station Longitude': 'end_lng'})
elif 'usertype' in test_table_bikes_old.columns:
    test_table_bikes_old = test_table_bikes_old.drop(['birth year', 'gender', 'usertype'], axis=1)
    test_table_bikes_old = test_table_bikes_old.rename(columns={'starttime': 'started_at', 'stoptime': 'ended_at',\
                                                            'start station id': 'start_station_id', 'start station name': 'start_station_name',\
                                                            'start station latitude': 'start_lat', 'start station longitude': 'start_lng',\
                                                            'end station id' : 'end_station_id', 'end station name': 'end_station_name',\
                                                            'end station latitude': 'end_lat', 'end station longitude': 'end_lng'})

test_table_bikes_old


# In[19]:


test_table_bikes_old["ended_at"] = pd.to_datetime(test_table_bikes_old["ended_at"], format='%m/%d/%Y %H:%M:%S')
test_table_bikes_old["started_at"] = pd.to_datetime(test_table_bikes_old["started_at"], format='%m/%d/%Y %H:%M:%S')

test_table_bikes_old["duration"] = test_table_bikes_old["ended_at"] - test_table_bikes_old["started_at"]
test_table_bikes_old["diff_lat"] = test_table_bikes_old["end_lat"] - test_table_bikes_old["start_lat"]
test_table_bikes_old["diff_lng"] = test_table_bikes_old["end_lng"] - test_table_bikes_old["start_lng"]

# unter Verwendung von https://wiki.openstreetmap.org/wiki/DE:Genauigkeit_von_Koordinaten
# 1 Längengrad Differenz entspricht auf Breite 40 Grad (NYC): 85118 Meter
# 1 Breitengrad Differenz entspricht 111120 Meter
test_table_bikes_old["direct_distance"] = np.sqrt(np.power(test_table_bikes_old["diff_lat"] * 111120, 2.0) + np.power(test_table_bikes_old["diff_lng"] * 85118, 2.0))

test_table_bikes_old


# In[20]:


print(test_table_bikes_old[test_table_bikes_old.isnull().any(axis=1)])
print(len(test_table_bikes_old[test_table_bikes_old.isnull().any(axis=1)]))
test_table_bikes_old_cleaned = test_table_bikes_old.dropna()
print(test_table_bikes_old_cleaned[test_table_bikes_old_cleaned.isnull().any(axis=1)])


# In[21]:


# erste plots
#Verteilung der Stationen (alle start/end lat/lng)
#get number of occurences of different stations
n_occurences_start = test_table_bikes_old_cleaned['start_station_name'].value_counts().to_dict()
n_occurences_end = test_table_bikes_old_cleaned['end_station_name'].value_counts().to_dict()
n_occurences = {key: n_occurences_start.get(key, 0) + n_occurences_end.get(key, 0) for key in set(n_occurences_start) | set(n_occurences_end)}
df_n_occurences = pd.DataFrame.from_dict(n_occurences, orient='index').rename(columns={0: 'usage'})


# iterate through table and form map with coordinates of different stations
start_station_names_to_coords = pd.Series(list(zip(test_table_bikes_old_cleaned['start_lng'], test_table_bikes_old_cleaned['start_lat'])), index=test_table_bikes_old_cleaned.start_station_name).to_dict()
end_station_names_to_coords = pd.Series(list(zip(test_table_bikes_old_cleaned['end_lng'], test_table_bikes_old_cleaned['end_lat'])), index=test_table_bikes_old_cleaned.end_station_name).to_dict()

station_names_to_coords = start_station_names_to_coords
station_names_to_coords.update(end_station_names_to_coords)
station_names_to_coords
#len(station_names_to_coords)
df_coords = pd.DataFrame.from_dict(station_names_to_coords, orient='index')
df_coords = df_coords.rename(columns={0: 'longitude', 1: 'latitude'})
df_coords = df_coords.join(df_n_occurences)

#remove long/lat == zero cases
df_coords = df_coords[df_coords['latitude'] != 0]

# figure size in inches
rcParams['figure.figsize'] = 11.7,8.27
sns.set_style("whitegrid")
sns.scatterplot(data=df_coords, x="longitude", y="latitude", s=12, hue='usage').set_title("citibikenyc stations", size=20)
df_coords


# In[22]:


# Verteilung Ausleih Startzeiten/Endzeiten

start_times = pd.DataFrame(test_table_bikes_old_cleaned["started_at"])
end_times = pd.DataFrame(test_table_bikes_old_cleaned["ended_at"])

times = pd.concat([start_times, end_times], axis=1)
times["started_at"] = times["started_at"].dt.hour
times["ended_at"] = times["ended_at"].dt.hour        
times

sns.histplot(data=times, x="started_at", discrete = True).set_title("Distribution of start hour of rent during day")


# In[23]:


# Wochentag vs. Wochenende
start_times['day'] = start_times['started_at'].dt.weekday
start_times['workday'] = start_times['day'].isin([0, 1, 2, 3, 4]).astype(int)
start_times_workday = start_times[start_times['workday'] == 1]
start_times_weekend = start_times[start_times['workday'] == 0]

start_times_workday["started_at"] = start_times_workday["started_at"].dt.hour 
start_times_workday

sns.histplot(data=start_times_workday, x="started_at", discrete = True).set_title("Distribution of start hour of rent during work days (Monday-Friday)")


# In[24]:


start_times_weekend["started_at"] = start_times_weekend["started_at"].dt.hour 
start_times_weekend

sns.histplot(data=start_times_weekend, x="started_at", discrete=True).set_title("Distribution of start hour of rent during weekends (Saturday-Sunday)")


# In[25]:


sns.histplot(data=times, x="ended_at", discrete=True).set_title("Distribution of end hour of rent during day")


# ### estimate percentage of commuters in workdays

# In[26]:


#get values
time_series = pd.DataFrame(start_times_workday['started_at'].value_counts()).sort_values(['started_at'])

#symmetrize
print(time_series['count'].min())
print(time_series['count'].idxmin())
time_series.head(time_series['count'].idxmin())

time_series = pd.concat([time_series.tail(len(time_series)-time_series['count'].idxmin()), time_series.head(time_series['count'].idxmin())])
time_series = time_series.reset_index()
time_series


# In[27]:


x, y = (list(time_series.index), list(time_series['count']))
print(x)
print(y)

plt.plot(x,y)
plt.title('symmetrized workday start rent time distribution')
plt.show()


# In[28]:


# fit 3 Gaussians to get estimate on percentage of commuters

def func(x, *params):
    y = np.zeros_like(x)
    #for i in range(0, len(params), 3):
    for i in range(0, len(params), 3):
        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]
        y = y + amp * np.exp( -((x - ctr)/wid)**2)
    return y

def single_func(x, ctr, amp, wid):
    return amp * np.exp( -((x - ctr)/wid)**2)

# guessed centers are 8-3=5, 15-3=12, 18-3=15
guess = [5, 20000, 2, 12, 10000, 4, 15, 20000, 2]

popt, pcov = curve_fit(func, x, y, p0=guess, maxfev = 2000)
print(popt)
fit = func(x, *popt)

plt.plot(x, y)
plt.plot(x, fit , 'r-')
plt.title('Fit of 3 Gaussians to workday start rent time distribution')
plt.show()


# In[29]:


# compute percentage of commute trips
# compute area under all 3 curves with delta t = 1 (hour)
area_all = sum(y)
print(area_all)

# compute area under 1st and last gaussian
ctr_1 = popt[0]
amp_1 = popt[1]
wid_1 = popt[2]
y1 = single_func(x, ctr_1, amp_1, wid_1)

ctr_3 = popt[6]
amp_3 = popt[7]
wid_3 = popt[8]
y3 = single_func(x, ctr_3, amp_3, wid_3)

area_commuters = sum(y1+y3)
print(area_commuters)

#missing area
ctr_2 = popt[3]
amp_2 = popt[4]
wid_2 = popt[5]
y2 = single_func(x, ctr_2, amp_2, wid_2)

area_missing = sum(y2)
print(area_missing)

# percentage commuters
print(area_commuters/area_all)
print(area_missing/area_all)
print(area_commuters/area_all + area_missing/area_all)


# In[30]:


# Verteilung duration
duration = pd.DataFrame(test_table_bikes_old_cleaned["duration"].dt.total_seconds() / 60)
#remove 50 largest values as some quite large outliers
duration = duration.drop(duration["duration"].sort_values().tail(50).index)
duration

sns.histplot(data=duration, x="duration", bins=200, binrange=(0,100)).set_title("Distribution of rent lengths")


# In[31]:


# Verteilung direct distances End-Startpunkt
sns.histplot(data=test_table_bikes_old_cleaned, x="direct_distance", bins=200, binrange=(0,10000)).set_title("Distribution of direct distance between start/end point of trip")


# In[32]:


# number of occurence of specific star-end-combinations 
test_table_bikes_old_cleaned['start_end_combo'] = test_table_bikes_old_cleaned['start_station_name'] + ' - ' + test_table_bikes_old_cleaned['end_station_name']
test_table_bikes_old_cleaned.value_counts('start_end_combo')


# ## Unfall Statistik NYC
# 
# Download als csv Datei von https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data
# 

# In[33]:


#Einlesen der Unfall Daten von NYC
table_accidents = pd.read_csv("Data/Motor_Vehicle_Collisions_-_Crashes_20250319.csv")

table_accidents.dtypes


# In[34]:


#crash_dates = list(table_accidents["CRASH DATE"].unique())
#print(crash_dates)


# In[35]:


table_accidents


# In[36]:


# check NaNs for injury/death numbers
column_list = ["CRASH DATE", "CRASH_TIME", "NUMBER OF PERSONS INJURED", "NUMBER OF PERSONS KILLED", "NUMBER OF PEDESTRIANS INJURED", "NUMBER OF PEDESTRIANS KILLED",\
               "NUMBER OF CYCLIST INJURED", "NUMBER OF CYCLIST KILLED", "NUMBER OF MOTORIST INJURED", "NUMBER OF MOTORIST KILLED"]
table_injuries_deaths = table_accidents[[c for c in table_accidents.columns if c in column_list]]

print("injury/deaths columns: ")
print("Rows before dropping nans: " + str(len(table_injuries_deaths)))
table_injuries_deaths.dropna(inplace =True)
print("Rows after dropping nans: " + str(len(table_injuries_deaths)))


# In[37]:


# check NaNs for longitude/latitude
table_long_lat = table_accidents[["LATITUDE", "LONGITUDE"]]

print("long/lat columns: ")
print("Rows before dropping nans: " + str(len(table_long_lat)))
table_long_lat.dropna(inplace =True)
print("Rows after dropping nans: " + str(len(table_long_lat)))


# In[38]:


# check NaNs for vehicle 1 info
table_vehicle_1 = table_accidents[["CONTRIBUTING FACTOR VEHICLE 1", "VEHICLE TYPE CODE 1"]]

print("vehicle 1 columns: ")
print("Rows before dropping nans: " + str(len(table_vehicle_1)))
table_vehicle_1.dropna(inplace =True)
print("Rows after dropping nans: " + str(len(table_vehicle_1)))


# In[39]:


#check for cyclist accidents
table_cyclist_accidents = table_accidents[table_accidents['NUMBER OF CYCLIST INJURED'] > 0]

columns_to_check = ['CONTRIBUTING FACTOR VEHICLE 1', 'CONTRIBUTING FACTOR VEHICLE 2', 'CONTRIBUTING FACTOR VEHICLE 3',\
'CONTRIBUTING FACTOR VEHICLE 4', 'CONTRIBUTING FACTOR VEHICLE 5', 'COLLISION_ID',\
'VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3',\
'VEHICLE TYPE CODE 4', 'VEHICLE TYPE CODE 5', 'NUMBER OF CYCLIST INJURED']
table_cyclist_accidents[columns_to_check]

