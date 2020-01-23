#!/usr/bin/env python3


import sys
import numpy
import pandas
import importlib
import subprocess
from datetime import datetime 

"""
This file contains helper functions for the Collect-HIS-Data.ipynb
"""


def install_and_import(imports):
    """
    Fancy way of importing libraries and automatically installing those that are needed.
    """
    
    caller = sys._getframe(1)
    v = caller.f_locals
    failed = []
    for i in imports:
        try:
            v[i] = importlib.import_module(i)
            print('{check} Loaded {lib}'.format(check=u'\N{check mark}', lib=i))
        except ImportError:
            print('{check} {lib} is not installed'.format(check=u'\N{ballot x}', lib=i))
            failed.append(i)

    if len(failed) > 0:
        failed_str = ' '.join(failed)
        print('\nInstalling {failed} using Anaconda'.format(failed=failed_str))
        cmd = ['conda', 'install', '-y', failed_str]
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            print(stdout_line, flush=True)
        popen.stdout.close()
        return_code = popen.wait()

        # reimport 
        for f in failed:
            try:
                v[i] = importlib.import_module(i)
                print('{check} Loaded {lib}'.format(check=u'\N{check mark}', lib=f))
            except ImportError:
                print('{check} {lib} failed to install again :('.format(check=u'\N{ballot x}', lib=f))

                
                

class TimeSeries(object):
    """
    A class for holding HIS timeseries data 
    """
    def __init__(self, get_values_object):
        """
        get_values_obeject -> WOF SOAP object 
        """
        self.get_values_object = get_values_object
        
        self.parse()
        
    def parse(self):
        # series info
        qo = self.get_values_object.queryInfo
        self.site_code = qo.criteria.locationParam
        self.variable_code = qo.criteria.variableParam
        self.start = datetime.strptime(qo.criteria.timeParam.beginDateTime.split('.')[0], '%Y-%m-%d %H:%M:%S')
        self.end = datetime.strptime(qo.criteria.timeParam.endDateTime.split('.')[0], '%Y-%m-%d %H:%M:%S')
        
        # source info
        si = self.get_values_object.timeSeries[0].sourceInfo
        self.site_name = si.siteName
        self.latitude = si.geoLocation.geogLocation.latitude
        self.longitude = si.geoLocation.geogLocation.longitude
        self.elevation = si.elevation_m
        self.elev_datum = si.verticalDatum
        
        # variable 
        v = self.get_values_object.timeSeries[0].variable
        self.variable_name = v.variableName
        self.variable_datatype = v.dataType
        self.units_name = v.unit.unitName
        self.units_desc = v.unit.unitDescription
        self.units_type = v.unit.unitType
        self.units_abbv = v.unit.unitAbbreviation
        self.nodata = v.noDataValue
        
        # values
        self.data = []
        for val in self.get_values_object.timeSeries[0].values[0].value:
            value_dt  = val._dateTime
            vC = float(val.value)
            if vC != self.nodata:
                vF = vC * (9/5) + 32
            else:
                vC = numpy.NaN
                vF = numpy.NaN
            self.data.append(dict(date=value_dt,
                                  tempC=vC,
                                  tempF=vF))
            
    def asDataFrame(self):
        atts = {k:v for k,v in self.__dict__.items() if k not in ('get_values_object', 'data')}
        #atts.pop('get_values_object')
        #data = atts.pop('data')

        dat = []
        for val in self.data:
            content = {k:v for k,v in atts.items()}
            for k, v in val.items():
                content[k] = v
            dat.append(content)

        df = pandas.DataFrame(dat)
        df = df.set_index(df.date)
        return df
                        
        