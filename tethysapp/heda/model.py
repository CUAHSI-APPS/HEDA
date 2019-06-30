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



#import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


#import numpy as np
def dummy():
    return True

def add_new_data(sites, start,end):
    """
    Persist new dam.
    """
    # Serialize data to json
    try:
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
        
        #discharge 00060
        #tributry 63680
        parameters['parameterCd']='00060,00065'
        parameters['siteStatus']='all'
        
        Host =  'https://waterservices.usgs.gov/nwis/iv/'
        
        response = fetch_data(Host,parameters)
        
        
        
        if response.status_code != 200:
            return False
            
        else:
            
            y = json.loads(response.text)
            
    
    
    
            discharge_json = y['value']['timeSeries'][0]['values']
            SSC_json = y['value']['timeSeries'][1]['values']
        
        
            discharge = extract_values(discharge_json, 'value')
            SSC = extract_values(SSC_json, 'value')
        
            
            trajectory_points = []
            for i in range(0,len(discharge)):
                try:
                    time = i
                    flow = discharge[i]
                    concentration = SSC[i]
                    trajectory_points.append(TrajectoryPoint(time=time, flow=flow,concentration=concentration))
                except ValueError:
                    continue
            
            # Create new event record
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
        trajectory_points.append(TrajectoryPoint(time=0, flow=0,concentration=0))
        
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
    time = Column(Integer)  #: 15 minute interval number
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
        segments.append(segment.start)
        segments.append(segment.end)
    
    
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
    
    

    # Relationships
    trajectory = relationship('Trajectory', back_populates='segments')
    

    
    


def segmentation(event_id,parameter1,parameter2):
    try:
        # Assign points to hydrograph
        
        Session = app.get_persistent_store_database('tethys_super', as_sessionmaker=True)
        session = Session()
        event = session.query(Event).get(int(event_id))
        
        
        
        
        
        
        
        # Overwrite old hydrograph
        segments = event.trajectory.segments
    
        # Create new hydrograph if not assigned already
        if not segments:
            segments = []
            #segments.append(Segments(start = 0, end = 0))
            event.trajectory.segments = segments
    
        # Remove old points if any
        for segment in event.trajectory.segments:
            session.delete(segment)
    
        trajectory = event.trajectory
        time = []
        
        
        for point in trajectory.points:
            time.append(point.time)
            
        segments = []
        
        segments.append(Segments(start = 0,end = int(len(time)/2)))
        segments.append(Segments(start = int(len(time)/2), end = len(time)-1))
        event.trajectory.segments = segments
        
        
        # Persist to database
        session.commit()
        session.close()
    
    
        
    
        return True
    
    
    except Exception as e:
        # Careful not to hide error. At the very least log it to the console
        print(e)
        return False

'''
        new_data_id = uuid.uuid4()
        data_dict = {
            'id': str(new_data_id),
            'site': sites,
            'start': start,
            'end': end,
            'discharge':discharge,
            'SSC': SSC
            
            
        }
        data_json = json.dumps(data_dict)

        # Write to file in app_workspace/dams/{{uuid}}.json
        # Make dams dir if it doesn't exist
        app_workspace = app.get_app_workspace()
        data_dir = os.path.join(app_workspace.path, 'data')
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        # Name of the file is its id
        file_name = str(new_data_id) + '.json'
        file_path = os.path.join(data_dir, file_name)

        # Write json
        with open(file_path, 'w') as f:
            f.write(data_json)
        
        
        hydrograph =create_hydrograph(discharge)
        status = 'OK'
        return hydrograph,status
        
        '''