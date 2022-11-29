#!/usr/bin/env python
# coding: utf-8

# In[80]:


#get_ipython().run_line_magic('matplotlib', 'inline')

import os
import sys
import pandas
import datetime
import copy
import shutil

#import matplotlib.pyplot as plt
#import matplotlib.colors as colors 
#plt.style.use('seaborn-whitegrid')

import numpy as np 
import clawpack.clawutil as clawutil
import clawpack.geoclaw.units as units

from clawpack.geoclaw.surge.storm import Storm

import requests
from bs4 import BeautifulSoup


# In[198]:


storms2download = {}

# Link to noaa archive with year and link to data files 
noaa_archive_url = 'http://ftp.nhc.noaa.gov/atcf/archive/'

# Set path to directory where we download atcf files 
# and the directory where we process them to geoclaw files 
atcf_data = os.path.join(os.getcwd(), 'atcf_data')
geoclaw_data = os.path.join(os.getcwd(), 'geoclaw_data')

# Create directories where we download atcf files
# and store the files in geoclaw format if those
# directories do not exist 
if not os.path.exists(atcf_data): 
    os.mkdir(atcf_data) 

if not os.path.exists(geoclaw_data): 
    os.mkdir(geoclaw_data) 


# Download files from NOAA archive
# A set of years that we want to grab data for is given. 
# Then we search through the noaa_archive_url html to see 
# if it contains those specific years. If so, then we check 
# to see if we already have that file in geoclaw format. 
# If we do, we do not download the file and move on to the next one. 

for year in range(2008, 2020): 
    
    # Get html data and determine all hyperlinked content on the 
    # archive with the specific years 
    year_url = os.path.join(noaa_archive_url, str(year))
    response = requests.get(year_url)
    soup = BeautifulSoup(response.content)
    links = soup.find_all('a')
    
    # Run through links to check files are there. We then 
    # check if that file has already been downloaded and transformed
    # to geoclaw. If it has we ignore that download and move to the 
    # next one that has not been downloaded. 
    for l in links: 
        s = l.get('href')
        if s.startswith('bal'): 
            s_file_name = s.split('.dat.gz')[0]
            print(s_file_name)
            if os.path.exists(path=os.path.join(geoclaw_data, '%s.storm' %s_file_name)): 
                print('File already downloaded and processed to geoclaw format. Located at %s' 
                      %os.path.join(geoclaw_data,'%s.storm' %s_file_name))
                continue 
            else: 
                data_url = os.path.join(year_url, s)
                clawutil.data.get_remote_file(url=data_url, output_dir=atcf_data, force=False, verbose=True)
            
    if year == 2008: 
        break 

    
# Sort the files in the atcf_data directory by extension. 
# All files with ext '.dat' will be listed first. Then all 
# files with ext '.dat.gz' will be listed last 
atcf_files = os.listdir(atcf_data)
atcf_files = sorted(os.listdir(atcf_data), key= lambda file: os.path.splitext(file)[1] )
  
# Run through files in the list and stop once we reach the 
# .gz file extension 
for file in atcf_files:
    file_name_tuple = os.path.splitext(file)
    if file_name_tuple[1] == '.gz': 
        print('All %s files written in geoclaw file format. \n', 
              'Processing "%s" finished. Now deleting %s directory'
             %('.dat', atcf_data))
        break 
    else: 
        if os.path.exists(os.path.join(geoclaw_data, '%s.storm' %file_name_tuple[0])): 
            print('File already exists located at %s' 
                  %os.path.join(geoclaw_data, '%s.storm' %file_name_tuple[0])) 
            continue
        else: 
            storm = Storm(path=os.path.join(atcf_data, file), file_format='ATCF')
            storm.write(path=os.path.join(geoclaw_data, '%s.storm' %file_name_tuple[0]), 
                        file_format='geoclaw')
            
shutil.rmtree(path=atcf_data)


# In[ ]:




