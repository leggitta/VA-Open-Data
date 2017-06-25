import json
import os
import pandas as pd
from sqlalchemy import create_engine
from urllib import request


# define urls of interest
base_url = 'https://raw.githubusercontent.com'
patient_2015_url = (
    '%s/vacobrydsk/VHA-Files/master/NEPEC_Overview_PTSD_FY15.json'
    % base_url)
center_2015_url = (
    '%s/vacobrydsk/VHA-Files/master/NEPEC_AnnualDataSheet_PTSD_FY15.json'
    % base_url)
patient_2014_url = (
    '%s/vacobrydsk/VHA-Files/master/NEPEC_Overview_PTSD_FY14.json'
    % base_url)
va_location_url = (
    '%s/department-of-veterans-affairs/' % base_url +
    'VHA-Facilities/master/VAFacilityLocation.json')

# create dataframes from urls
patient_2014 = pd.read_json(patient_2014_url)
patient_2014['Year'] = 2014
patient_2015 = pd.read_json(patient_2015_url)
patient_2015['Year'] = 2015
patient = pd.concat([patient_2014, patient_2015])
center_2015 = pd.read_json(center_2015_url)
with request.urlopen(va_location_url) as url:
    va_location_dict = json.loads(url.read().decode('utf8'))
location_table = pd.DataFrame(va_location_dict['VAFacilityData'])

# save data frames to mysql
engine = create_engine(
    "mysql://%s:%s@localhost/va_open?charset=utf8"
    % (os.getenv('MYSQL_USER'), os.getenv('MYSQL_PASS')))
patient.to_sql(
    'patient', engine, flavor='mysql', if_exists='replace')
center_2015.to_sql(
    'center_2015', engine, flavor='mysql', if_exists='replace')
location_table.to_sql(
    'va_location', engine, flavor='mysql', if_exists='replace')
