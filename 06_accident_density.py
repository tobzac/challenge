#!/usr/bin/env python
# coding: utf-8

# ## accident density
# accident density map per year. overlayed with citibike stations.
# 

# In[70]:


import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import rcParams
import matplotlib.pyplot as plt


# In[3]:


#Einlesen der Unfall Daten von NYC
table_accidents = pd.read_csv("Data/Motor_Vehicle_Collisions_-_Crashes_20250319.csv")

table_accidents


# In[107]:


year = 2022

table_accidents["CRASH DATE"]= pd.to_datetime(table_accidents["CRASH DATE"])
table_accidents_year = table_accidents[table_accidents["CRASH DATE"].dt.year == year]
table_accidents_year


# In[108]:


# remove latitude zero rows and nan
table_accidents_year = table_accidents_year[table_accidents_year['LATITUDE'] > 0]
table_accidents_year


# In[109]:


def roundPartial (value, resolution):
    return round (value / resolution) * resolution


# In[110]:


# define a grid by rounding and then count accidents in it...
table_accidents_year['LATITUDE ROUNDED'] = np.round(table_accidents_year.LATITUDE.apply(lambda x: roundPartial(float(x), 0.005)), 3)
table_accidents_year['LONGITUDE ROUNDED'] = np.round(table_accidents_year.LONGITUDE.apply(lambda x: roundPartial(float(x), 0.005)), 3)
table_accidents_year['LOCATION ROUNDED'] = table_accidents_year['LATITUDE ROUNDED'].astype(str) + ' ' + table_accidents_year['LONGITUDE ROUNDED'].astype(str) 
table_accidents_year


# In[111]:


rcParams['figure.figsize'] = 11.7,8.27


# In[112]:


# all accidents
all_accidents = pd.DataFrame(table_accidents_year['LOCATION ROUNDED'].value_counts())
all_accidents['location'] = all_accidents.index
all_accidents[['latitude', 'longitude']] = all_accidents.location.str.split(' ', n= 1, expand=True)
all_accidents['latitude'] = all_accidents['latitude'].astype(float)
all_accidents['longitude'] = all_accidents['longitude'].astype(float)
all_accidents

#sns.kdeplot(data=all_accidents, x="longitude", y="latitude", cmap="Reds", fill=True, bw_adjust=0.6)
#sns.scatterplot(data=all_accidents, x="longitude", y="latitude", hue="count", s=3)
#sns.scatterplot(data=table_accidents_year, x="LONGITUDE", y="LATITUDE", s=2)

sns.set_style("whitegrid")
norm = plt.Normalize(all_accidents['count'].min(), all_accidents['count'].max())
sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
sm.set_array([])

fig, ax = plt.subplots()

fig = sns.scatterplot(data=all_accidents, x="longitude", y="latitude", s=22, hue='count', marker='s', palette='Reds')
fig.set_title("accident density in year: " + str(year), size=18)

# Remove the legend and add a colorbar
fig.get_legend().remove()
fig.figure.colorbar(sm, ax=ax)


# In[113]:


# only cyclists involved

