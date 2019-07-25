import numpy as np
import json
import requests 
from datetime import datetime

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
        print('retrieving data')
        r = requests.get(url = URL, params = parameters) 
        print(r)
        return r
    except requests.exceptions.RequestException as e:
        print(e)
        print('Except of request entered')
        
  
       
            
                      
parameters = {}
parameters['format']= 'json'
parameters['sites']= '01362500'
parameters['startDT'] = '2019-06-04'
parameters['endDT'] = '2019-06-4'
        
parameters['parameterCd']='00060,63680'
parameters['siteStatus']='all'
        
Host =  'https://waterservices.usgs.gov/nwis/iv/'
        
response = fetch_data(Host,parameters)
        
        
        
if response.status_code != 200:
    print(response.status_code)
else:
            
    y = json.loads(response.text)
            
    
        
    
    discharge_json = y['value']['timeSeries'][0]['values']
    SSC_json = y['value']['timeSeries'][1]['values']
        
        
    discharge = extract_values(discharge_json, 'value')
    SSC = extract_values(SSC_json, 'value')
    time = extract_values(SSC_json, 'dateTime')
    for i in range(0,len(time)):
        time[i] = time[i].replace('T',' ')
        datetime_object = datetime.strptime(time[i][0:-10],"%Y-%m-%d %H:%M:%S")
        time[i] = datetime_object
            
            
    