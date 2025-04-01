#!/usr/bin/env python
# coding: utf-8

# ## commuter analysis
# Do commuter analysis for a year, hard to completely automate, as fit to distribution is a bit fragile and might have to be tuned by hand.
# Eventually collect analysis for many years and plot results.
# Perform same steps as done in notebook 01_initial_checks, for simplicity only use start times for this analysis.

# In[316]:


import os
import pandas as pd
import numpy as np
import datetime as dt
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import seaborn as sns


# ### per year

# #### citibike data

# In[286]:


year = 2024
# for now only full analysis, nto for core_region


# In[287]:


#read in start times for a certain year for each month
time_data_list_year = []

base_folder_name = str(year) + "-citibike-tripdata"
month_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
numbers_2_name = {"01": "1_January", "02": "2_February", "03": "3_March", "04": "4_April",
                 "05": "5_May", "06": "6_June", "07": "7_July", "08": "8_August",
                 "09": "9_September", "10": "10_October", "11": "11_November", "12": "12_December"}

# read in successively all data for month, then for all months
for month in month_list:
    print("month: " + month)

    # get used folder/filename
    month_folder_name_new = str(year) + month + "-citibike-tripdata"

    # set path to csv files depending on year
    full_path = ""
    if year in [2020, 2021, 2022, 2023, 2024]:
        full_path = "Data/" + base_folder_name + "/" + month_folder_name_new + "/"
    elif year in [2013, 2014, 2015, 2016, 2017, 2018, 2019]:
        full_path = "Data/" + base_folder_name + "/" + numbers_2_name[month] + "/"

    # collect all files for the month
    df_list = []
    for filename in os.listdir(full_path):
        if filename.endswith(".csv") and month_folder_name_new in filename:
            print(filename)
            df_month_start_time_partial = pd.read_csv(full_path + filename)

            # special treatment and renaming of columns if year before 2020
            if year in [2013, 2014, 2015, 2016, 2017, 2018, 2019]:
                if 'User Type' in df_month_start_time_partial.columns:
                    df_month_start_time_partial = df_month_start_time_partial.drop(['Birth Year', 'Gender', 'User Type'], axis=1)
                    df_month_start_time_partial = df_month_start_time_partial.rename(
                        columns={'Start Time': 'started_at', 'Stop Time': 'ended_at',
                                 'Start Station ID': 'start_station_id', 'Start Station Name': 'start_station_name',
                                 'Start Station Latitude': 'start_lat', 'Start Station Longitude': 'start_lng',
                                 'End Station ID': 'end_station_id', 'End Station Name': 'end_station_name',
                                 'End Station Latitude': 'end_lat', 'End Station Longitude': 'end_lng'})
                elif 'usertype' in df_month_start_time_partial.columns:
                    df_month_start_time_partial = df_month_start_time_partial.drop(['birth year', 'gender', 'usertype'], axis=1)
                    df_month_start_time_partial = df_month_start_time_partial.rename(
                        columns={'starttime': 'started_at', 'stoptime': 'ended_at',
                                 'start station id': 'start_station_id', 'start station name': 'start_station_name',
                                 'start station latitude': 'start_lat', 'start station longitude': 'start_lng',
                                 'end station id': 'end_station_id', 'end station name': 'end_station_name',
                                 'end station latitude': 'end_lat', 'end station longitude': 'end_lng'})

            #if "-" in df_month_start_time_partial['started_at'].loc[[0]]:
                
            df_month_start_time_partial = pd.DataFrame(df_month_start_time_partial['started_at'])
            df_list.append(df_month_start_time_partial)

    print(df_list)
    if len(df_list) > 0:
        df_month_start_time = pd.concat(df_list, axis=0, ignore_index=True)
    else:
        df_month_start_time = pd.DataFrame()
        print("no data for month: " + month)

    time_data_list_year.append(df_month_start_time)


# In[288]:


# do count values for each month separately and then join the results
# otherwise tables get too large
time_series_workday_list = []
time_series_weekend_list = []

for i, time_data in enumerate(time_data_list_year): 
    df = time_data
    df[['date', 'time']] = df['started_at'].str.split(' ', n=1, expand=True)
    df.time = df.time.apply(lambda string : string.split(':')[0]).astype(int)
    df.date = pd.to_datetime(df.date)
    df['day'] = df['date'].dt.weekday
    df
    
    start_times_workday = df[df['day'].isin([0, 1, 2, 3, 4])]
    start_times_weekend = df[df['day'].isin([5,6])]
    
    time_series_workday = pd.DataFrame(start_times_workday['time'].value_counts()).sort_values(['time'])
    time_series_workday = time_series_workday.rename(columns={'count': 'count'+str(i)})
    time_series_weekend = pd.DataFrame(start_times_weekend['time'].value_counts()).sort_values(['time'])
    time_series_weekend = time_series_weekend.rename(columns={'count': 'count'+str(i)})

    time_series_workday_list.append(time_series_workday)
    time_series_weekend_list.append(time_series_weekend)
    #print(time_series_workday)
    #print(time_series_weekend)
    count = i + 1


# In[289]:


# merge df into one and create sum column
time_series_workday_year = pd.concat(time_series_workday_list, axis=1)
time_series_weekend_year = pd.concat(time_series_weekend_list, axis=1)

column_names = []
for i in range(0,12):
   column_names.append('count'+str(i))

time_series_workday_year['total'] = time_series_workday_year[column_names].sum(axis=1)
time_series_weekend_year['total'] = time_series_weekend_year[column_names].sum(axis=1)

time_series_workday_year
#time_series_weekend_year


# In[290]:


x, y = (list(time_series_workday_year.index), list(time_series_workday_year['total']))
print(x)
print(y)

plt.plot(x,y)
plt.title('workday start rent time distribution for year '+ str(year))
plt.show()
print(time_series_workday_year['total'].sum())


# In[291]:


x, y = (list(time_series_weekend_year.index), list(time_series_weekend_year['total']))
print(x)
print(y)

plt.plot(x,y)
plt.title('weekend start rent time distribution for year '+ str(year))
plt.show()
print(time_series_weekend_year['total'].sum())


# In[292]:


# write out to save time as it takes time to generate them
time_series_workday_year.to_csv("intermediate_results/time_series_workday_year_"+ str(year)+".txt")
time_series_weekend_year.to_csv("intermediate_results/time_series_weekend_year_"+ str(year)+".txt")


# In[293]:


#symmetrize for fitting
print(time_series_workday_year['total'].min())
print(time_series_workday_year['total'].idxmin())
time_series_workday_year.head(time_series_workday_year['total'].idxmin())

time_series = pd.concat([time_series_workday_year.tail(len(time_series_workday_year)-time_series_workday_year['total'].idxmin()), time_series_workday_year.head(time_series_workday_year['total'].idxmin())])
time_series = time_series.reset_index()
time_series = time_series[['time', 'total']]
time_series


# In[294]:


x, y = (list(time_series.index), list(time_series['total']))
print(x)
print(y)


# In[295]:


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
guess = [5, 2000000, 2, 12, 1000000, 4, 15, 2000000, 2]

popt, pcov = curve_fit(func, x, y, p0=guess, maxfev = 2000)
print(popt)
fit = func(x, *popt)

plt.plot(x, y)
plt.plot(x, fit , 'r-')
plt.title('Fit of 3 Gaussians to workday start rent time distribution for year '+str(year))
plt.show()


# In[296]:


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


# In[297]:


#write also out to file
with open("intermediate_results/commuter_results_"+str(year)+".txt", "w") as f:
    #header:
    f.write("sum of all weekend trips\tsum of all workday trips\tpercentage commuters workday\n")
    #values:
    f.write(str(time_series_weekend_year['total'].sum())+"\t"+str(time_series_workday_year['total'].sum())+"\t"+str(area_commuters/area_all)+"\n")


# In[325]:


# read in commuter results
results = {}
for year in [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]:
    with open("intermediate_results/commuter_results_"+str(year)+".txt", "r") as f:
        for line in f:
            if not line.startswith("sum"):
                entries = line.split("\t")
                sum_weekend_trips = entries[0]
                sum_workday_trips = entries[1]
                percentage_commuters_workday = entries[2]

    if 'weekend_trips' in results.keys():
        results['weekend_trips'].append(int(sum_weekend_trips)) 
        results['workday_trips'].append(int(sum_workday_trips))
        results['perc_commuters_workdays'].append(float(percentage_commuters_workday))
        results['year'].append(year)
    else:
        results['weekend_trips'] = [int(sum_weekend_trips)]
        results['workday_trips'] = [int(sum_workday_trips)]
        results['perc_commuters_workdays'] = [float(percentage_commuters_workday)]
        results['year'] = [year]

df_result = pd.DataFrame.from_dict(results)
df_result['commuters_workdays'] = df_result['workday_trips'] * df_result['perc_commuters_workdays']
df_result


# In[326]:


# plot commuter percentage over years and workday/weekend ratio
sns.lineplot(data=df_result, x='year', y='perc_commuters_workdays')
plt.ylim(0,1)


# In[328]:


# plot commuter percentage over years and workday/weekend ratio
sns.lineplot(data=df_result, x='year', y='commuters_workdays')


# #### NYC accidents data

# In[299]:


#Einlesen der Unfall Daten von NYC
table_accidents = pd.read_csv("Data/Motor_Vehicle_Collisions_-_Crashes_20250319.csv")
table_accidents


# In[300]:


# restrict to year of interest
table_accidents["CRASH DATE"]= pd.to_datetime(table_accidents["CRASH DATE"])

table_accidents_year = table_accidents[table_accidents["CRASH DATE"].dt.year == year]
table_accidents_year


# In[301]:


table_accidents_year['hour'] = pd.to_datetime(table_accidents_year['CRASH TIME'], format='%H:%M').dt.strftime("%H").astype(int)
table_accidents_year['day'] = table_accidents_year['CRASH DATE'].dt.weekday
table_accidents_year['workday'] = table_accidents_year['day'].isin([0, 1, 2, 3, 4]).astype(int)
table_accidents_year_workday = table_accidents_year[table_accidents_year['day'].isin([0, 1, 2, 3, 4])]
table_accidents_year_weekend = table_accidents_year[table_accidents_year['day'].isin([5,6])]

# restrict to cyclists involved
table_accidents_cyclist_year_workday = table_accidents_year_workday[(table_accidents_year_workday["NUMBER OF CYCLIST INJURED"] > 0) | (table_accidents_year_workday["NUMBER OF CYCLIST KILLED"] > 0)]
table_accidents_cyclist_year_weekend = table_accidents_year_weekend[(table_accidents_year_weekend["NUMBER OF CYCLIST INJURED"] > 0) | (table_accidents_year_weekend["NUMBER OF CYCLIST KILLED"] > 0)]

table_accidents_cyclist_year_workday
table_accidents_cyclist_year_weekend


# In[302]:


accidents_time_series_workday = pd.DataFrame(table_accidents_cyclist_year_workday['hour'].value_counts()).sort_values(['hour'])
accidents_time_series_weekend = pd.DataFrame(table_accidents_cyclist_year_weekend['hour'].value_counts()).sort_values(['hour'])
accidents_time_series_workday


# In[303]:


x, y = (list(accidents_time_series_workday.index), list(accidents_time_series_workday['count']))
print(x)
print(y)

plt.plot(x,y)
plt.title('workday accident distribution for year '+ str(year))
plt.show()
print(accidents_time_series_workday['count'].sum())


# In[304]:


x, y = (list(accidents_time_series_weekend.index), list(accidents_time_series_weekend['count']))
print(x)
print(y)

plt.plot(x,y)
plt.title('weekend accident distribution for year '+ str(year))
plt.show()
print(accidents_time_series_weekend['count'].sum())


# In[305]:


#symmetrize for fitting
print(accidents_time_series_workday['count'].min())
print(accidents_time_series_workday['count'].idxmin())
accidents_time_series_workday.head(accidents_time_series_workday['count'].idxmin())

time_series = pd.concat([accidents_time_series_workday.tail(len(accidents_time_series_workday)-accidents_time_series_workday['count'].idxmin()), accidents_time_series_workday.head(accidents_time_series_workday['count'].idxmin())])
time_series = time_series.reset_index()
time_series


# In[306]:


x, y = (list(time_series.index), list(time_series['count']))
print(x)
print(y)


# In[307]:


# guessed centers are 8-3=5, 15-3=12, 18-3=15
guess = [5, 200, 2, 11, 100, 4, 15, 200, 2]

popt, pcov = curve_fit(func, x, y, p0=guess, maxfev = 2000)
print(popt)
fit = func(x, *popt)

plt.plot(x, y)
plt.plot(x, fit , 'r-')
plt.title('Fit of 3 Gaussians to workday accident time distribution for year '+str(year))
plt.show()


# In[308]:


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


# In[309]:


#write also out to file
with open("intermediate_results/accident_commuter_results_"+str(year)+".txt", "w") as f:
    #header:
    f.write("sum of all weekend accidents\tsum of all workday accidents\tpercentage commuters workday accidents\n")
    #values:
    f.write(str(accidents_time_series_weekend['count'].sum())+"\t"+str(accidents_time_series_workday['count'].sum())+"\t"+str(area_commuters/area_all)+"\n")


# In[ ]:


# also read in and plot

