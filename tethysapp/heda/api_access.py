# -*- coding: utf-8 -*-
# importing the requests library 
import requests 
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as Soup
import numpy as np
  
# recursivejson.py

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results
      

def fetch_data(host,parameters):
    

    URL = host
    

    # sending post request and saving response as response object 
    try:
        print('retrieving data from USGS.')
        r = requests.get(url = URL, params = parameters) 
        return r
    except requests.exceptions.RequestException as e:
        print(e)
        print('USGS response not stadard or expected.')
        return False
  


    
    
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
    
    


