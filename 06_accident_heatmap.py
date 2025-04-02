#!/usr/bin/env python
# coding: utf-8

# ## accident heatmap
# accident heat map per year. overlayed with citibike stations.
# 

# In[1]:


import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import rcParams
import matplotlib.pyplot as plt


# In[2]:


#Einlesen der Unfall Daten von NYC
table_accidents = pd.read_csv("Data/Motor_Vehicle_Collisions_-_Crashes_20250319.csv")

table_accidents


# In[3]:


year = 2024

table_accidents["CRASH DATE"]= pd.to_datetime(table_accidents["CRASH DATE"])
table_accidents_year = table_accidents[table_accidents["CRASH DATE"].dt.year == year]
table_accidents_year


# In[4]:


# remove latitude zero rows and nan
table_accidents_year = table_accidents_year[table_accidents_year['LATITUDE'] > 0]
table_accidents_year


# In[5]:


def roundPartial (value, resolution):
    return round (value / resolution) * resolution


# In[6]:


# define a grid by rounding and then count accidents in it...
table_accidents_year['LATITUDE ROUNDED'] = np.round(table_accidents_year.LATITUDE.apply(lambda x: roundPartial(float(x), 0.005)), 3)
table_accidents_year['LONGITUDE ROUNDED'] = np.round(table_accidents_year.LONGITUDE.apply(lambda x: roundPartial(float(x), 0.005)), 3)
table_accidents_year['LOCATION ROUNDED'] = table_accidents_year['LATITUDE ROUNDED'].astype(str) + ' ' + table_accidents_year['LONGITUDE ROUNDED'].astype(str) 
table_accidents_year


# In[7]:


rcParams['figure.figsize'] = 11.7,8.27


# ### all accidents
# cars, bicycles etc., using whole table for a year.

# In[8]:


# all accidents
all_accidents = pd.DataFrame(table_accidents_year['LOCATION ROUNDED'].value_counts())
all_accidents['location'] = all_accidents.index
all_accidents[['latitude', 'longitude']] = all_accidents.location.str.split(' ', n= 1, expand=True)
all_accidents['latitude'] = all_accidents['latitude'].astype(float)
all_accidents['longitude'] = all_accidents['longitude'].astype(float)
all_accidents

sns.set_style("whitegrid")
norm = plt.Normalize(all_accidents['count'].min(), all_accidents['count'].max())
sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
sm.set_array([])

fig, ax = plt.subplots()

fig = sns.scatterplot(data=all_accidents, x="longitude", y="latitude", s=22, hue='count', marker='s', palette='Reds')
fig.set_title("accident heat map in year: " + str(year), size=18)

# Remove the legend and add a colorbar
fig.get_legend().remove()
fig.figure.colorbar(sm, ax=ax)


# ### only bicycle accidents
# #### single year

# In[9]:


# only cyclists involved
table_accidents_bicycles_year = table_accidents[table_accidents["CRASH DATE"].dt.year == year]
table_accidents_bicycles_year = table_accidents_bicycles_year[table_accidents_bicycles_year['LATITUDE'] > 0]
table_accidents_bicycles_year = table_accidents_bicycles_year[(table_accidents_bicycles_year["NUMBER OF CYCLIST INJURED"] > 0) | (table_accidents_bicycles_year["NUMBER OF CYCLIST KILLED"] > 0)]

table_accidents_bicycles_year['LATITUDE ROUNDED'] = np.round(table_accidents_bicycles_year.LATITUDE.apply(lambda x: roundPartial(float(x), 0.005)), 3)
table_accidents_bicycles_year['LONGITUDE ROUNDED'] = np.round(table_accidents_bicycles_year.LONGITUDE.apply(lambda x: roundPartial(float(x), 0.005)), 3)
table_accidents_bicycles_year['LOCATION ROUNDED'] = table_accidents_bicycles_year['LATITUDE ROUNDED'].astype(str) + ' ' + table_accidents_bicycles_year['LONGITUDE ROUNDED'].astype(str) 

table_deaths_bicycles_year = table_accidents_bicycles_year[(table_accidents_bicycles_year["NUMBER OF CYCLIST KILLED"] > 0)]
table_deaths_bicycles_year['LONGITUDE'] = table_deaths_bicycles_year['LONGITUDE'].astype(float)
table_deaths_bicycles_year['LATITUDE'] = table_deaths_bicycles_year['LATITUDE'].astype(float)

table_accidents_bicycles_year
table_deaths_bicycles_year


# In[10]:


bicycle_accidents = pd.DataFrame(table_accidents_bicycles_year['LOCATION ROUNDED'].value_counts())
bicycle_accidents['location'] = bicycle_accidents.index
bicycle_accidents[['latitude', 'longitude']] = bicycle_accidents.location.str.split(' ', n= 1, expand=True)
bicycle_accidents['latitude'] = bicycle_accidents['latitude'].astype(float)
bicycle_accidents['longitude'] = bicycle_accidents['longitude'].astype(float)
bicycle_accidents

sns.set_style("whitegrid")
norm = plt.Normalize(bicycle_accidents['count'].min(), bicycle_accidents['count'].max())
sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
sm.set_array([])

fig, ax = plt.subplots()

fig = sns.scatterplot(data=bicycle_accidents, x="longitude", y="latitude", s=22, hue='count', marker='s', palette='Reds')
fig.set_title("bicycle accident heat map in year: " + str(year), size=18)

# Remove the legend and add a colorbar
fig.get_legend().remove()
fig.figure.colorbar(sm, ax=ax)

fig = sns.scatterplot(data=table_deaths_bicycles_year, x="LONGITUDE", y="LATITUDE", color='blue', legend=False, s=12)


# #### all years

# In[12]:


# bicycles accident heatmap for all years
table_accidents_bicycles_allyears = table_accidents[table_accidents['LATITUDE'] > 0]
table_accidents_bicycles_allyears = table_accidents_bicycles_allyears[(table_accidents_bicycles_allyears["NUMBER OF CYCLIST INJURED"] > 0) | (table_accidents_bicycles_allyears["NUMBER OF CYCLIST KILLED"] > 0)]

table_accidents_bicycles_allyears['LATITUDE ROUNDED'] = np.round(table_accidents_bicycles_allyears.LATITUDE.apply(lambda x: roundPartial(float(x), 0.005)), 3)
table_accidents_bicycles_allyears['LONGITUDE ROUNDED'] = np.round(table_accidents_bicycles_allyears.LONGITUDE.apply(lambda x: roundPartial(float(x), 0.005)), 3)
table_accidents_bicycles_allyears['LOCATION ROUNDED'] = table_accidents_bicycles_allyears['LATITUDE ROUNDED'].astype(str) + ' ' + table_accidents_bicycles_allyears['LONGITUDE ROUNDED'].astype(str) 

table_deaths_bicycles_allyears = table_accidents_bicycles_allyears[(table_accidents_bicycles_allyears["NUMBER OF CYCLIST KILLED"] > 0)]
table_deaths_bicycles_allyears['LONGITUDE'] = table_deaths_bicycles_allyears['LONGITUDE'].astype(float)
table_deaths_bicycles_allyears['LATITUDE'] = table_deaths_bicycles_allyears['LATITUDE'].astype(float)

table_accidents_bicycles_allyears
table_deaths_bicycles_allyears


# In[13]:


bicycle_accidents_all = pd.DataFrame(table_accidents_bicycles_allyears['LOCATION ROUNDED'].value_counts())
bicycle_accidents_all['location'] = bicycle_accidents_all.index
bicycle_accidents_all[['latitude', 'longitude']] = bicycle_accidents_all.location.str.split(' ', n= 1, expand=True)
bicycle_accidents_all['latitude'] = bicycle_accidents_all['latitude'].astype(float)
bicycle_accidents_all['longitude'] = bicycle_accidents_all['longitude'].astype(float)
bicycle_accidents_all

sns.set_style("whitegrid")
norm = plt.Normalize(bicycle_accidents_all['count'].min(), bicycle_accidents_all['count'].max())
sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
sm.set_array([])

fig, ax = plt.subplots()

fig = sns.scatterplot(data=bicycle_accidents_all, x="longitude", y="latitude", s=22, hue='count', marker='s', palette='Reds')
fig.set_title("bicycle accident heat map all years 2012-2025", size=18)

# Remove the legend and add a colorbar
fig.get_legend().remove()
fig.figure.colorbar(sm, ax=ax)

fig = sns.scatterplot(data=table_deaths_bicycles_allyears, x="LONGITUDE", y="LATITUDE", color='blue', legend=False, s=12)


# to compute real total probabilities of an accident when riding a bike, which would be needed for a risk map, one would need overall number of bike rides and estimate it. Not known from 2 tables...

# to compute conditional probabilities of a bike crash, when riding a citibike, one would need to know which of the bike crashes in the NYPD table are citibikenyc crashes. Also not known. so 2 tables cannot be consistently mapped onto each other.

# strategy for accident/health insurance:\
# As data shows there are many yearly citibike rides and thus it is a considerable market for insurance companies. One could take the bicycles accident map as a risk map and push for a included insurance with citibikenyc members for example. One could couple fees of course with number of trips/time spent on bike, so that it would be rather modest.\
# Assuming the bike rental company allows the data to be shared (about the trips), the individual members can be grouped into different risk groups based on which areas they cover with their trips/commutes. If the customer doesn´t allow the data to be shared, group in high risk group to give incentive to share data (assuming this is legal in the US, in Europe due to its data privacy laws it would probably be not). It would also cover insurance only with use of helmet to prevent bad head injuries.\
# Incentivize usage of dedicated bike ways/paths (e.g. in insurance rates) to lower risk of car collisions.\
# Health Insurance would also love to see people doing sports, as obesity is a very common health risk in the US and riding bikes would be very good to counter that (in nprinciple), although people in large cities are probably already more health-aware than people on the countryside.\
# \
# CitibikeNYC strategy:\
# It would want people to be insured, without probably providing the logistics of the service itself (otherwise it would do it already now). Bad for PR if people are not insured, see (https://observer.com/2013/07/citi-bike-floods-streets-with-thousands-of-uninsured-cyclists/), but also high legal risks in sueing-prone US (see https://www.edelmanpclaw.com/bicycle-injuries/citi-bike-injuries/). But given the increasing number of accidents the PR issue becomes worse.\
# It would want to couple insurance with usage of helmet, as bad injuries occur when riding without helmet. And bad injuries are very bad for PR/legal expenses. It would also want people to have their bike trips on more safe dedicated bike paths/ways.\
# Given large percentage of commuters that use citibikenyc, one could also push for extra provisions in insurances for commute on bikes in health insurances (that are usually coupled with jobs). Trips are usually not so long and overall risk is not so high.\
# \
# In total insurance would probably help that people wear helmets, as it is not mandatory (only for minors below 14 years and in some regions perhaps). It would also help citibikenyc with bad PR and some legal expenses due to being sued. But probably for them currently it is still cheaper to pay legal expenses that to provide the extra service of insurance.
