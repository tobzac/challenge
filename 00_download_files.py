#!/usr/bin/env python
# coding: utf-8

# ### download files

# In[1]:


#import collection of functions for analysis
import analysis_functions


# In[2]:


# download now full batch of csv files for analysis 
# up to now single downloaded files/folders were investigated.


# In[4]:


#zip_folder_list = ["2023-citibike-tripdata.zip", "2022-citibike-tripdata.zip", \
#                   "2021-citibike-tripdata.zip", "2020-citibike-tripdata.zip", \
#                   "2019-citibike-tripdata.zip", "2018-citibike-tripdata.zip", \
#                   "2017-citibike-tripdata.zip", "2016-citibike-tripdata.zip", \
#                   "2015-citibike-tripdata.zip", "2014-citibike-tripdata.zip", \
#                   "2013-citibike-tripdata.zip"]
zip_folder_list = ["2014-citibike-tripdata.zip",                    "2013-citibike-tripdata.zip"]
for zip_folder_name in zip_folder_list:
    print(zip_folder_name)
    analysis_functions.download_url('https://s3.amazonaws.com/tripdata/' + zip_folder_name, 'Data/downloads/' + zip_folder_name.split(".")[0])
    


# In[5]:


# data needs still to be processed and unzipped further... later stored in Data folder...

