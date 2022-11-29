#!/usr/bin/env python
# coding: utf-8

# In[10]:


import os
import sys
import pandas
import datetime
import copy
import shutil

# to exract all the fine grid topography data from /bathy
import glob
import sys
import datetime
import shutil
import gzip

import numpy as np

from clawpack.geoclaw.surge.storm import Storm
import clawpack.clawutil as clawutil

import matplotlib.pyplot as plt
import matplotlib.colors as colors 
plt.style.use('seaborn-whitegrid')

import numpy as np 
import clawpack.clawutil as clawutil
import clawpack.geoclaw.units as units

from clawpack.geoclaw.surge.storm import Storm

import requests
from bs4 import BeautifulSoup
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

for year in range(2008, 2020): 
    
    # Get html data and determine all hyperlinked content on the 
    # archive with the specific years 
    year_url = os.path.join(noaa_archive_url, str(year))
    response = requests.get(year_url)
    soup = BeautifulSoup(response.content)
    links = soup.find_all('a')
    for l in links:
        #print(l.get('href'))
            s = l.get('href')
            print(s)
            if s.startswith('bal'):
                    # Convert ATCF data to GeoClaw format
                clawutil.data.get_remote_file( "http://ftp.nhc.noaa.gov/atcf/archive/" +str(year)+"/"+str(s),output_dir=os.getcwd())
                atcf_path = os.path.join(os.getcwd(), s)
                # Note that the get_remote_file function does not support gzip files which
                # are not also tar files.  The following code handles this
                with gzip.open(".".join((atcf_path, 'gz')), 'rb') as atcf_file:
                    with open(atcf_path, 'w') as atcf_unzipped_file:
                        atcf_unzipped_file.write(atcf_file.read().decode('ascii'))

                sandy = Storm(path=atcf_path, file_format="ATCF")

                # Calculate landfall time - Need to specify as the file above does not
                # include this info (9/13/2008 ~ 7 UTC)
                sandy.time_offset = datetime.datetime(2012,10,30,0,0)

                sandy.write(s, file_format='geoclaw')



