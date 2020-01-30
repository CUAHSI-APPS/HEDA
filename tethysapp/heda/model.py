# Put your persistent store models in this file

#import os
#import uuid
import json
from .app import Heda as app
from .api_access import fetch_data, extract_values #extract_tag

#from plotly import graph_objs as go
#from tethys_gizmos.gizmo_options import PlotlyView

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime

#import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker
import numpy as np

import csv
import copy 

import pandas as pd
from .hysteresis_metrics import hysteresisMetrics


import os


# Import standard libs
from datetime import datetime
from suds.client import Client
import matplotlib.pyplot as plt
from .nbutils import install_and_import, TimeSeries
from pandas import Grouper
import pandas


#this is a comment for syncing12

Base = declarative_base()


#import numpy as np
def dummy():
    return True

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
        #self.latitude = si.geoLocation.geogLocation.latitude
        #self.longitude = si.geoLocation.geogLocation.longitude
        #self.elevation = si.elevation_m
        #self.elev_datum = si.verticalDatum
        
        # variable 
        v = self.get_values_object.timeSeries[0].variable
        self.variable_name = v.variableName
        self.variable_datatype = v.dataType
        
        # values
        self.data = []
        for val in self.get_values_object.timeSeries[0].values[0].value:
            value_dt  = val._dateTime
            vC = float(val.value)
            self.data.append(dict(date=value_dt,
                                  val=vC
                                  ))
            
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
                        

def add_new_data_cuahsi(site_code, start, end, concentration_param,network):
    
    
    #debug variables
    #variable_code = '63680'
    #network='NWISUV'
    #site_code = 'NWISUV:01362500'
    #site_code = network+':'+site_code
    #st = datetime(2019, 6, 4)
    #et = datetime(2019,6,4)


    # define the web service info
    st = datetime.strptime(start, '%Y-%m-%d')
    et = datetime.strptime(end, '%Y-%m-%d')
    site_code = network+':'+site_code
   
    wsdl = 'http://hydroportal.cuahsi.org/'+network.lower()+'/cuahsi_1_1.asmx?WSDL'
    #wsdl = f'http://hydroportal.cuahsi.org/{network.lower()}/cuahsi_1_1.asmx?WSDL'
    #print(wsdl)
    
    discharge_pram = '00060'
    
    # collect TMAX for Everett
    client = Client(wsdl)
    
    
    
    concentration_return = client.service.GetValuesObject(site_code, concentration_param, st, et, '')
    concentration_obj = TimeSeries(concentration_return)
    
    flow_return = client.service.GetValuesObject(site_code, discharge_pram, st, et, '')
    flow_obj = TimeSeries(flow_return)
    
    
    flow = []
    concentration = []
    
    
    conc_dates = []
    flow_dates = []
    
    
    for d_point in concentration_obj.data:
        concentration.append(d_point['val'])
        conc_dates.append(d_point['date'])
        
        
    for d_point in flow_obj.data:
        flow.append(d_point['val'])
        flow_dates.append(d_point['date'])
    
    #print error of missing values
    if len(flow) != len(concentration):
        print('Flow values returned : '+str(len(flow)))
        print('Concentration values returned : '+str(len(concentration)))
        print('Warning: Number of flow and concentration values returned not equal.')
        
    
    
    flow_final =[]
    concentration_final = []
    date_time_final = []
    
    flow_counter = 0
    concentration_counter = 0
    while flow_counter<len(flow_dates) and concentration_counter<len(conc_dates):
        if conc_dates[concentration_counter] == flow_dates[flow_counter]:
            flow_final.append(flow[flow_counter])
            concentration_final.append(concentration[concentration_counter])
            date_time_final.append(flow_dates[flow_counter])
            
            #date_time_final.append(datetime.strptime(flow_dates[flow_counter][0:-10],"%Y-%m-%d %H:%M:%S"))
            concentration_counter = concentration_counter + 1
            flow_counter = flow_counter + 1
            
        
        #missing flow value
        elif conc_dates[concentration_counter] < flow_dates[flow_counter]:
            concentration_counter = concentration_counter + 1
            
        #missing concentration value
        elif flow_dates[flow_counter] < conc_dates[concentration_counter]:
            concentration_counter = concentration_counter + 1
            
         
                
    return flow_final,concentration_final,date_time_final                
        

def add_new_data(sites, start,end,concentration,source,network):
    """
    Persist new dam.
    """
    # Serialize data to json
    try:
        
        
        if source == 'CUAHSI':
            
            discharge, SSC, time = add_new_data_cuahsi(sites, start, end, concentration,network)
        
        
        else:
        
            #'01646500'
            #'USGS:06306300'
            #print('site number provided is '+sites)
            #parameters = {}
            #parameters['format']= 'json'
            #parameters['sites']= 'USGS:06306300'
            #parameters['startDT'] = '2019-06-03'
            #parameters['endDT'] = '2019-06-9'
            
            parameters = {}
            parameters['format']= 'json'
            parameters['sites']= sites
            
            parameters['startDT'] = start
            parameters['endDT'] = end
            
            
            
            parameter_retrieve = '00060,'+str(concentration)
            #discharge 00060
            #tributry 63680
            #parameters['parameterCd']='00060,63680'
            print(parameter_retrieve)
            parameters['parameterCd'] = parameter_retrieve
            
            parameters['siteStatus']='all'
            
            
            
            
            Host =  'https://waterservices.usgs.gov/nwis/iv/'
            
            response = fetch_data(Host,parameters)
            
            if not response:
                return False
            
            if response.status_code != 200:
                return False
                
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
                
        trajectory_points = []
        for i in range(0,len(discharge)):
            try:
                date_time = time[i]
                flow = discharge[i]
                concentration = SSC[i]
            
                trajectory_points.append(TrajectoryPoint(index = i, time=date_time, flow=flow,concentration=concentration))
                
            except ValueError:
                continue
            
            
            
            
        
        #Create new event record
        #new_data_id = uuid.uuid4()
        new_event = Event(
            #id = str(new_data_id),
            siteNumber=sites,
            siteName = 'n/a',
            startDate = start,
            endDate = end
        
        )
        trajectory = Trajectory()
        new_event.trajectory = trajectory
        trajectory.points = trajectory_points
        
        # Get connection/session to database
        Session = app.get_persistent_store_database('tethys_super', as_sessionmaker=True)
        session = Session()

        # Add the new dam record to the session
        session.add(new_event)
        session.flush()
        event_id = new_event.id
        
        if event_id > 40:
            #delete one event for every event added after 40
            session.delete(session.query(Event).get(int(event_id-30)))
            
        # Commit the session and close the connection
        session.commit()
        session.close()
        
        print('Event id for new event added is '+str(event_id))
        
        return event_id
        
    except Exception as e:
        # Careful not to hide error. At the very least log it to the console
        print(e)
        return False

        

# SQLAlchemy ORM definition for the dams table
class Event(Base):
    """
    SQLAlchemy Event DB Model
    """
    __tablename__ = 'events'

    # Columns
    id = Column(Integer, primary_key=True)
    siteNumber = Column(String)
    siteName = Column(String)
    startDate = Column(String)   
    endDate = Column(String)  
    
    # Relationships
    trajectory= relationship('Trajectory', back_populates='event', uselist=False)
    #segments= relationship('Segment', back_populates='event', uselist=False)
       
                
def init_primary_db(engine, first_time):
    """
    Initializer for the primary database.
    """
    # Create all the tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    # Add data
    #print(first_time)
    if True:
        # Make session
        Session = sessionmaker(bind=engine)
        session = Session()



        Event1 = Event(
            siteNumber='USGS:06306300',
            siteName = 'test',
            startDate = '2019-06-03',
            endDate = '2019-06-9'
        
        )
        
        trajectory_points = []
        trajectory_points.append(TrajectoryPoint(index = 0, time=datetime.strptime('2000-01-01 00:00:00',"%Y-%m-%d %H:%M:%S"), flow=0,concentration=0))
        
        trajectory = Trajectory()
        Event1.trajectory = trajectory
        trajectory.points = trajectory_points
        
        segment_points = []
        segment_points.append(Segments(start = 0,end = 0))
        
        trajectory.segments = segment_points
        # Add the dams to the session, commit, and close
        session.add(Event1)
        session.flush()
        print('this is event auto id '+str(Event1.id))
        
        session.commit()
        session.close()                                
                
                

    


class Trajectory(Base):
    """
    SQLAlchemy Hydrograph DB Model
    """
    __tablename__ = 'trajectories'

    # Columns
    id = Column(Integer, primary_key=True)
    event_id = Column(ForeignKey('events.id'))

    # Relationships
    event = relationship('Event', back_populates='trajectory')
    points = relationship('TrajectoryPoint', back_populates='trajectory')
    segments = relationship('Segments',back_populates = 'trajectory')


class TrajectoryPoint(Base):
    """
    SQLAlchemy Hydrograph Point DB Model
    """
    __tablename__ = 'trajectory_points'

    # Columns
    id = Column(Integer, primary_key=True)
    trajectory_id = Column(ForeignKey('trajectories.id'))
    index = Column(Integer)
    time = Column(DateTime)  #: 15 minute interval number
    flow = Column(Float)  #: cfs
    concentration = Column(Float) #: mg/l

    # Relationships
    trajectory = relationship('Trajectory', back_populates='points')
    
  
  
def get_events(event_id):
    """
    Get all persisted dams.
    """
    #print('event id for access is '+str(event_id))
    # Get connection/session to database
    Session = app.get_persistent_store_database('tethys_super', as_sessionmaker=True)
    session = Session()
    event = session.query(Event).get(int(event_id))
    print(event)
    # Query for all dam records
    #events = session.query(Event).all()
    session.close()

    return event
    
    
def get_conc_flow_seg(event_id):
    """
    Get all persisted dams.
    """
    #print('event id for access is '+str(event_id))
    # Get connection/session to database
    Session = app.get_persistent_store_database('tethys_super', as_sessionmaker=True)
    session = Session()
    event = session.query(Event).get(int(event_id))
    
    trajectory = event.trajectory
    time = []
    flow = []
    concentration = []
    
    for point in trajectory.points:
        flow.append(point.flow)
        concentration.append(point.concentration)
        time.append(point.time)
    
    segments = []
    for segment in trajectory.segments:
        d={}
        d['start'] = segment.start
        d['end'] = segment.end
        #segments.append(segment.start)
        #segments.append(segment.end)
        segments.append(d)
    
    
    # Query for all dam records
    #events = session.query(Event).all()
    session.close()
    
    return time,flow,concentration,segments
    

#def fetch_data(site_name, event_id):
#    """
#    fetch data from hydroshare server
#    """
      
 
class Segments(Base):
    """
    SQLAlchemy Hydrograph DB Model
    """
    __tablename__ = 'segments'

    # Columns
    id = Column(Integer, primary_key=True)
    trajectory_id = Column(ForeignKey('trajectories.id'))
    start = Column(Integer)  
    end = Column(Integer) 
    startTime = Column(String)
    endTime = Column(String)
    duration = Column(String)
    PeakQ = Column(Float)
    baseflow = Column(Float)
    timetoPeakQ = Column(String)
    FI = Column(Float)
    QRecess  = Column(Float)
    SSCRecess = Column(Float)
    PeakConc = Column(Float)
    TimetoPeakConc= Column(String)
    DiffPeakQPeakC = Column(String)
    HI = Column(Float)
    
    #statistics for segment
    
    

    # Relationships
    trajectory = relationship('Trajectory', back_populates='segments')
    

    



def segmentation(event_id,fc,PKThreshold,ReRa,BSLOPE,ESLOPE,SC,MINDUR,dyslp):
    try:
        # Assign points to hydrograph
        
        Session = app.get_persistent_store_database('tethys_super', as_sessionmaker=True)
        session = Session()
        event = session.query(Event).get(int(event_id))
        
        
        
        
        
        
        # Overwrite old hydrograph
        
    
        # Create new hydrograph if not assigned already
        
        segments = []
        
        event.trajectory.segments = copy.deepcopy(segments)
        
        # Remove old points if any
        
        for segment in event.trajectory.segments:
            session.delete(segment)
        
    
        
        
        time,flow,concentration,segments=get_conc_flow_seg(event_id)
        
        stormflow,baseflow = separatebaseflow(flow,fc,4)
        
        runoffEvents, nRunoffEvent = extractrunoff(stormflow, PKThreshold, ReRa, BSLOPE=0.001, ESLOPE = 0.0001, SC=4,MINDUR = 0, dyslp = 0.001)
        
        segments = []
        for i in range(0,nRunoffEvent):
            event_indexes = runoffEvents[i][:,0]

            event_flow = flow[int(event_indexes[0]):int(event_indexes[-1])]
            event_concentration = concentration[int(event_indexes[0]):int(event_indexes[-1])]
            event_time = time[int(event_indexes[0]):int(event_indexes[-1])]
            start_index = event_indexes[0]
            end_index = event_indexes[-1]
    
            
            #seg = create_segment(event_flow,event_concentration,event_time,start_index,end_index)
            print(start_index)
            
            
            seg = Segments(start = start_index,
            end = end_index, 
            duration = '-1' ,
            PeakQ=0,
            baseflow = 0,
            timetoPeakQ='n/a',
            QRecess = 0,
            PeakConc=0,
            TimetoPeakConc = 'n/a',
            DiffPeakQPeakC = 'n/a',
            startTime = str(event_time[0]), 
            endTime = str(event_time[-1]),
            HI = -999)
    
    

    
            
            segments.append(seg)
        
        
        
        
        
        
        
       
        event.trajectory.segments = segments
        
        
        
        
        # Persist to database
        session.commit()
        session.close()
    
    
        
    
        return True
    
    
    except Exception as e:
        # Careful not to hide error. At the very least log it to the console
        print(e)
        print('in exception')
        return False
        
        

def update_segmentation(event_id): 
    event_id = int(event_id)
    try:
        # Assign points to hydrograph
        
        Session = app.get_persistent_store_database('tethys_super', as_sessionmaker=True)
        session = Session()
        event = session.query(Event).get(int(event_id))
        
        
        
        
        
        event_time,flow,concentration,segments=get_conc_flow_seg(event_id)
        
        
        segmentation_updated = []
        for i in range(0,len(segments)):
            print('this many segments' +str(len(segments)))
            #metrics = retrieve_metrics(event_id,i)
            start_index = segments[i]['start']
            end_index = segments[i]['end']
            print(start_index)
            print(end_index)
            
            seg = create_segment(flow[start_index:end_index],concentration[start_index:end_index],event_time[start_index:end_index],start_index,end_index)
            
            segmentation_updated.append(seg)
            
            
        segments_dummy = []
        
        event.trajectory.segments = copy.deepcopy(segments_dummy)
        
        # Remove old points if any
        
        for segment in event.trajectory.segments:
            session.delete(segment)
            
        
        event.trajectory.segments = segmentation_updated

        # Persist to database
        session.commit()
        session.close()
        
        return True
    
    
    except Exception as e:
        # Careful not to hide error. At the very least log it to the console
        print(e)
        print('in exception')
        return False 
          


        
    
def create_segment(event_flow,event_concentration,event_time,start_index,end_index):
    
    print(len(event_time))
    print(len(event_flow))
    print(len(event_concentration))
    duration = event_time[-1] - event_time[0]
    startTime = str(event_time[0])
    endTime = str(event_time[-1])
    PeakQ = max(event_flow)
    baseflow = event_flow[0]
    timetoPeakQ = event_time[np.argmax(event_flow)] - event_time[0]
    #FI = 
    QRecess=  event_flow[-1] - event_flow[0]
    #SSCRecess
    PeakConc = max(event_concentration)
    TimetoPeakConc = event_time[np.argmax(event_concentration)] - event_time[0]
    
    

    DiffPeakQPeakC = TimetoPeakConc - timetoPeakQ
    days_to_hours = DiffPeakQPeakC.days * 24
    diff_btw_two_times = (DiffPeakQPeakC.seconds) / 3600
    overall_hours = days_to_hours + diff_btw_two_times
    
    DiffPeakQPeakC = str(overall_hours)
    
    duration = str(duration)
    timetoPeakQ = str(timetoPeakQ)
    TimetoPeakConc = str(TimetoPeakConc)
    DiffPeakQPeakC = str(DiffPeakQPeakC)
    
    #HI function takes normalized values
    event_flow_norm = np.asarray(event_flow)
    event_concentration_norm = np.asarray(event_concentration)
    
    if (max(event_flow_norm ) - min(event_flow_norm )) !=0:
        event_flow_norm = (event_flow_norm  - min(event_flow_norm )) / (max(event_flow_norm ) - min(event_flow_norm )) 
    
    if (max(event_concentration_norm ) - min(event_concentration_norm ))  !=0:
        event_concentration_norm= (event_concentration_norm  - min(event_concentration_norm )) / (max(event_concentration_norm ) - min(event_concentration_norm )) 
    
    event_flow_norm = np.asarray(event_flow_norm)
    event_concentration_norm = np.asarray(event_concentration_norm)
    
    
    discharge_df = pd.DataFrame({'valuedatetime': event_time, 'datavalue': event_flow_norm})
    response_df = pd.DataFrame({'valuedatetime': event_time, 'datavalue': event_concentration_norm})
    
    
    
    
    
    timespacing = event_time[1]-event_time[0]
    timespacing = timespacing.total_seconds()
    timespacing = int(timespacing/60)
    
    
    try:
        hystdict = hysteresisMetrics(discharge_df,response_df, timespacing, timespacing, debug=False, interpall=True,
                       discharge_time_spacing_units='minutes', response_time_spacing_units='minutes', )
        H_Ind = hystdict["HI_mean_with_Interp"]
    except Exception as e:
        H_Ind = 0
        
    
   
    
    
    
    seg = Segments(start = start_index,end = end_index, duration = duration,PeakQ=PeakQ,baseflow = baseflow,timetoPeakQ=timetoPeakQ,QRecess = QRecess,PeakConc=PeakConc,TimetoPeakConc = TimetoPeakConc,DiffPeakQPeakC = DiffPeakQPeakC,startTime = startTime, endTime = endTime,HI = H_Ind)
    
    return seg
            

    
def separatebaseflow(hy,fc,Pass =4): 
    
    #Separate streamflow into baseflow and stormflow.
    #[stormflow, baseflow] = separatebaseflow(hy, filter, pass) separates 
    #streamflow (hy) into baselfow and stormflow using digital filter method. 
    #fc = filter coefficient, 
    #pass = # times of filter passing through hy
#
    #Note: This function adpots the agorithm from a R package of EcoHydRology.
    #However, the initial status of baseflow has been improved. 
    

    n = len(hy)
    TV = np.arange(0,len(hy))
    bf = np.empty(n)
    bf[:] = np.nan
    
    bf_p = hy #baseflow from the previous pass, initial is the streamflow

    for j in range(1,Pass+1):
        #set forward and backward pass
        if j% 2 == 1:
            sidx = 0
            eidx = n 
            incr = 1
        else:
            sidx = n-1
            eidx = 1 
            incr = -1 
        
        #set the inital value for baseflow
        bf[sidx] = bf_p[sidx]
        
        for i in range(sidx + incr,eidx,incr):         
            tmp = fc*bf[i-incr] + (1-fc)*(bf_p[i]+bf_p[i-incr])/2
            #print(tmp)
            #print(bf_p[i])
            bf[i] = np.nanmin([tmp, bf_p[i]])     
        
        bf_p = bf
  
    
   
    sf = hy - bf #% stormflow
    
    #sf = np.concatenate((TV,sf))
    #sf = np.concatenate((TV,bf))
    #TV = [TV, bf] 

       
    return sf,bf

def findTP(LINE):
    #Identify Turning Points for a Line
   
#   [TP] = findTP(LINE) returns an two-column array of turning points,
#   where the 1st column is the index of turning point in LINE, and the 2nd
#   column is the label for peak and valley (peak = 1, valley = 0).  
#
#   Note: LINE is supposed to be a vector (one column). 
#   This function replaces the 'findinflect.m'

    FOD = np.diff(LINE) #first order derivative
    sDiff = np.diff(np.sign(FOD)) #sign difference 
    idx = np.nonzero(sDiff) #find the index of the turning points

    #Turning Points (TP):
    #1st column is the index of turing point in the orginal data (LINE)
    #2nd the label for peak and valley


    TP_1 = np.asarray(idx)+1
    TP_2 = sDiff[idx]
    
    TP = np.column_stack((TP_1[0],TP_2))
    
    TP[TP[:, 1] > 0, 1] = 0 #mark local min (valley) with 0
    TP[TP[:, 1] < 0, 1] = 1 #mark local max (peak) with 1



    return TP



def smoothcurve(X,Pass):
    
#Smooth Response Data
#
#   [Y] = smoothcurve(X, Pass) smooths the data in the column vector X
#   using a moving average filter. Result is returned in the column vector Y. 
#   The size of the moving average (window) is 3. Pass is the number of
#   filter passing through data. 
    
    if Pass > 0:    
        for n in range(0,Pass):
            for i in range(1,len(X)-1):
                X[i] = (X[i-1] + 2*X[i] + X[i+1])/4;
             
                 
     
    Y = X;
    


    return Y



def extractrunoff(stormflow, MINDIFF, RETURNRATIO, BSLOPE, ESLOPE, SC, MINDUR = 0, dyslp = 0.001):
    #Extract Runoff Events from Stormflow
    #   [RunoffEvent, nEvent] = extractrunoff(stormflow, MINDIFF, RETURNRATIO,
    #   BSLOPE, ESLOPE, SC, MINDUR) returns extracted runoff events in a cell
    #   array (RunoffEvent) and the number of extracted events (nEvent). 
    #   
    #   Explanation of Input Variables
    #   Stormflow: = streamflow - baseflow
    #   MINDIFF: minimum difference between start (or end) and peak of runoff.
    #       It ensures that the extracted runoff events always have (at least)
    #       one distinct peak. 
    #   RETURNRATIO: determine where runoff terminates. In this case, runoff is
    #       considered terminated when declining below a dynamic threshould, A.
    #       A = Fmax (Peak Discharge) * RETURNRATIO.
    #   BSlope and ESlope: Beigining Slope and End Slope. They are threshoulds
    #       of slope, used to cut flat head and end of the runoff event. 
    #   SC: smooth coeffcient. It determine how many passes will apply on
    #       stormflow. More passes result smoother hydrograph. 
    #   MINDUR (optional): minimun duration. It define the minimum duration of selected 
    #       runoff events, so spiky, narrow events will be ignored automatically. 
    #       MINDUR's value represents the number of element, so the minimum
    #       duration is actually equal to MINDUR * TimeInterval. 
    #   dyslp (optional): dynamic slope threshold used to cut the flat head and
    #       end of the runoff event.  


    RETURNCONSTANT = MINDIFF/3

    # Step 1: Hydorgraph Smoothing
    hy = copy.deepcopy(stormflow) 
    hy = smoothcurve(hy, SC) 
    st = []
    ed = []

    #Step 2: Turning Points (TP) Identification and Extraction
    #Identify local max and min (peak and valley)
    TP = findTP(hy) #1st column: index; 2nd column: label (valley = 0, peak = 1)
    TP = TP.astype(int)
    TP_temp = hy[TP[:,0]]
    TP_temp = TP_temp.reshape(len(TP_temp),1)
    TP = np.append(TP,TP_temp,axis = 1)


    #the first element in 'hy' array is considered a 'valley point' no matter what, 
    #if it is at a very low level (< Q_avg/10).

    if TP[0, 1] == 1 and hy[0] < np.mean(hy)/10:
        TP = np.vstack(([1,0,hy[0]],TP))

 
    #the last element in 'hy' array is considered a 'valley point' no matter what, 
    #if it is at a very low level (< Q_avg/10). 
    if TP[-1, 1] == 1 and hy[-1] < np.mean(hy)/10:
        TP = np.vstack((TP,[len(hy), 0, hy[-1]]))

 
    #Remove incomplete event(s) at the beginning and at the end
    
    while TP[0, 1] == 1:
        
        TP = TP[1:, :] 
    while TP[-1, 1] == 1:
        TP = TP[:-1, :]
        


    #Step 3: Identify the Start and End Points of Runoff Event 
    #Get difference between peak and valley
    TP_temp = np.diff(TP[:, 2])
    TP_temp = np.append(TP_temp,0)

    TP_temp = TP_temp.reshape(len(TP_temp), 1)
    TP = np.append(TP, TP_temp, axis=1)

    #Find out start and end points of event flows
    i = 0;
    c = 0; 
    isComplete = 1; 
    nInflect = len(TP)
    
    while i < nInflect -1:
        j = 1;
        d = TP[i, 3] + TP[i+j, 3];
        while d > max(RETURNRATIO * max(abs(TP[i:i+j, 3])), RETURNCONSTANT):
            if i + j < nInflect - 1: 
                j = j + 1 
                d = d + TP[i+j, 3]
            else: 
                isComplete = 0 
                break
             
         
        st.append(i)
        ed.append(i + j)
        i = i + j + 1
        c = c + 1   
 

    
    if isComplete == 0:
        st = np.array(st)
        ed = np.array(ed)
        st = st[0:- 1]
        ed = ed[0:- 1]
 


    #Step 4: Extract Runoff Events and Put Each of Them into a Cell
    nEvent = 0
    runoffEvents = [] 

    for i in range(0,len(st)):

        date = np.arange(TP[st[i], 0]-1, TP[ed[i] + 1, 0])
        event_smooth = hy[int(TP[st[i], 0])-1:int(TP[ed[i]+1, 0])]


        event = stormflow[int(TP[st[i], 0])-1:int(TP[ed[i]+1, 0])]
        
        eventflow = np.column_stack((date,event))
        eventflow = np.column_stack((eventflow,event_smooth))
        
    
        
       
        temp1 = np.diff(eventflow[:, 2]) 
        
        
        
        #Select runoff events whose peak exceeds threshold (minDiff)


        if max(eventflow[:, 1]) - eventflow[0, 1] > MINDIFF and max(eventflow[:, 1]) - eventflow[-1, 1] > MINDIFF:

            ran = max(eventflow[:, 1]) - min(eventflow[:, 1])
            dyslp = dyslp * ran #dynamic slope threhould
            #Shorten runoff event by removing flat head and end
            #Check slope on smoothed flow data



            while len(temp1) > 0 and temp1[0] < min([BSLOPE, dyslp]):
               eventflow = eventflow[1:, :]
               temp1 = temp1[1:];



            while len(temp1) > 0 and temp1[-1] > -min([ESLOPE, dyslp]):
                eventflow = eventflow[0:-1, :]
                temp1 = temp1[0:-1]


            #Check slope on orginal flow data
            if len(temp1) > 0:
                t = eventflow[:, 1]
                t = np.diff(t)
                temp2 = np.diff(eventflow[:, 1])
                t= len(temp2)
                while len(temp2) > 0 and temp2[0] <= min([BSLOPE, dyslp]):
                    eventflow = eventflow[1:, :]
                    temp2 = temp2[1:]



                while len(temp2) > 0 and temp2[-1] >= -min([ESLOPE, dyslp]):
                    eventflow = eventflow[0:-1, :]
                    temp2 = temp2[0:-1]




                    #Select Runoff Events whose duration exceeds threshold (minDur)
                if len(temp2) > MINDUR:
                    nEvent = nEvent + 1;
                    runoffEvents.append(eventflow[:, 0:2])

    
 
    return runoffEvents, nEvent
    
    

    
def retrieve_metrics(event_id,sub_event):
    """
    Get data.
    """
    sub_event = int(sub_event)
    Session = app.get_persistent_store_database('tethys_super', as_sessionmaker=True)
    session = Session()
    event = session.query(Event).get(int(event_id))
    
    trajectory = event.trajectory
    time = []
    flow = []
    concentration = []
    
    for point in trajectory.points:
        flow.append(point.flow)
        concentration.append(point.concentration)
        time.append(point.time)
    
    
    metrics = []
    
    for segment in trajectory.segments:
        metrics_dict={}
        metrics_dict['startTime'] = segment.startTime
        metrics_dict['endTime'] = segment.endTime  
        metrics_dict['duration'] = segment.duration
        metrics_dict['PeakQ'] = segment.PeakQ
        metrics_dict['baseflow'] = segment.baseflow
        metrics_dict['Time to peak discharge'] = segment.timetoPeakQ
        metrics_dict['Q recess'] = segment.QRecess
        metrics_dict['Peak concentration'] = segment.PeakConc
        metrics_dict['Time to peak concentration'] = segment.TimetoPeakConc
        metrics_dict['Difference between peak Q and peak C (hrs)'] = segment.DiffPeakQPeakC
        metrics_dict['Hysteresis Index'] = round(segment.HI,3)
        metrics_dict['start index'] = segment.start
        metrics_dict['end index'] = segment.end
    

        
        
        
        metrics.append(metrics_dict)
    
    
    
    session.close()
    
    
    
    
    return  metrics 

def upload_trajectory(hydrograph_file):
    """
    Parse hydrograph file and add to database, assigning to appropriate dam.
    """
    # Parse file
    trajectory_points = []
    segments_all = set()
    segment_index = []
    flow_all = []
    concentration_all = []
    time_all = []
    try:
        
        for line in hydrograph_file:
            
            
            sline = line.decode().split(',')
        
            try:
                index = int(sline[0])
                time = sline[1]
                flow = float(sline[2])
                concentration = float(sline[3])
                segment = int(sline[4])
                segment_index.append(segment)
                segments_all.add(segment)
                time = datetime.strptime(time,"%Y-%m-%d %H:%M:%S")
                flow_all.append(flow)
                time_all.append(time)
                concentration_all.append(concentration)
                trajectory_points.append(TrajectoryPoint(index = index, time=time, flow=flow,concentration=concentration))
            except ValueError:
                continue
                print('value error')

        
        if len(trajectory_points) > 0:
            print('length of uploaded trajectory: '+str(len(trajectory_points)))
            #Create new event record
            #new_data_id = uuid.uuid4()
            new_event = Event(
                #id = str(new_data_id),
                siteNumber='manual',
                siteName = 'manual',
                startDate = trajectory_points[0].time,
                endDate = trajectory_points[-1].time
            
            )
            trajectory = Trajectory()
            new_event.trajectory = trajectory
            trajectory.points = trajectory_points
            
            #get index of all unique numbers other than zero in segments_all, add start and end indexes
            #segments.append(Segments(start = event_indexes[0],end = event_indexes[-1]))
            segment_index = np.asarray(segment_index)
            segments = []
            
            for segment in segments_all:
                if segment != 0:
                    ii = np.where(segment_index == segment)[0]
                    #segments.append(Segments(start = int(ii[0]),end = int(ii[-1])))
        
                    start_index = int(ii[0])
                    end_index = int(ii[-1])
                    
                    
                    event_flow = flow_all[start_index:end_index]
                    event_concentration = concentration_all[start_index:end_index]
                    event_time = time_all[start_index:end_index]
    
                    
                    seg = create_segment(event_flow,event_concentration,event_time,start_index,end_index)
                    
                    segments.append(seg)
        
            
            new_event.trajectory.segments = segments
            #trajectory.segments = segments
            # Get connection/session to database
            Session = app.get_persistent_store_database('tethys_super', as_sessionmaker=True)
            session = Session()
    
            # Add the new dam record to the session
            session.add(new_event)
            session.flush()
            event_id = new_event.id
            
            if event_id > 40:
                #delete one event for every event added after 40
                session.delete(session.query(Event).get(int(event_id-30)))
                
            # Commit the session and close the connection
            session.commit()
            session.close()
            
            return event_id
            

    except Exception as e:
        # Careful not to hide error. At the very least log it to the console
        print(e)
        return False

def download_file(event_id): 
    
    try:
        Session = app.get_persistent_store_database('tethys_super', as_sessionmaker=True)
        session = Session()
        event = session.query(Event).get(int(event_id))
        
        
        
        
        
        rows = []
        segment_list = np.zeros(len(event.trajectory.points))
        seg_num = 1
        for segment in event.trajectory.segments:
            segment_list[segment.start:segment.end] = seg_num
            seg_num +=1
        i = 0
        rows = []
        for point in event.trajectory.points:
            d= {}
            d['index'] = point.index
            d['time'] = point.time
            d['flow'] = point.flow
            d['concentration'] = point.concentration
            d['segment'] = int(segment_list[i])
            i = i+1
            rows.append(d)
    
        #close the session
        session.close()
        
        
        
        
        #create a file and return path, and download file
        #fname = str(event_id)+'_file.csv'
        fileDir = os.path.dirname(__file__)
        fname = fileDir + '/public/files/'+str(event_id)+'_file_temp.csv'
        fout = open(fname, 'w')
        csvw = csv.DictWriter(fout, fieldnames = ['index','time','flow','concentration','segment'])
        csvw.writeheader()
        csvw.writerows(rows)
        fout.close()
        
        #clean up old files
       
        if int(event_id) > 40:
            
            fname2 = 'tethysdev/tethysapp-heda/tethysapp/heda/public/files/'+str(int(event_id)-30)+'_file_temp.csv'
            if os.path.exists(fname2):
                print('removing')
                os.remove(fname2)
         
            
        #print(os.getcwd())

        return fname
    except Exception as e:
        # Careful not to hide error. At the very least log it to the console
        print(e)
        return False
    
    