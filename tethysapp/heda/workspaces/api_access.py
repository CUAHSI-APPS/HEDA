# -*- coding: utf-8 -*-
# importing the requests library 
import requests 
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as Soup
import numpy as np
  
  

def fetch_data(host,parameters):
    

    URL = Host
    print(URL)
    

    # sending post request and saving response as response object 
    r = requests.get(url = URL, params = parameters) 
  

    #print(r.url)
    #print(r)
    return r
    
    
    '''
    discharge_values = []
    result = Soup(r.text,'xml')
    for element in result.find_all("wml2:value"):
        discharge_values.append(float(element.text)) 
    
    
    print(discharge_values[0])
    '''
    
def extract_tag(response,tag):
    
    discharge_values = []
    result = Soup(response.text,'xml')
    for element in result.find_all(tag):
        discharge_values.append(float(element.text)) 
    
    
    return discharge_values
    
    
Host =  'https://waterservices.usgs.gov/nwis/iv/'

parameters = {}
parameters['format']= 'waterml,2.0'
parameters['sites']= '01646500'
parameters['startDT'] = '2019-06-03'
parameters['endDT'] = '2019-06-4'
parameters['parameterCd']='00060,00065'
parameters['siteStatus']='all'
response = fetch_data(Host,parameters)

if response.status_code != 200:
    print('Error')
    print(response)
else:
    discharge = extract_tag(response,'wml2:value')

