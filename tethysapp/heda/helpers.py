from plotly import graph_objs as go
from tethys_gizmos.gizmo_options import PlotlyView
#from tethysapp.heda.app import Heda as app
from .model import get_conc_flow_seg
import numpy as np

import matplotlib.pyplot as plt  


legend_size = 15
tick_size = 15
label_size = 18
label_size_2 = 25
cap_size ='n/a'
cqtcolor= 'g'



def create_hydrograph(event_id, height='520px', width='100%'):
# Build up Plotly plot
    time,flow,concentration,segments=get_conc_flow_seg(event_id)
    
    
    if len(segments)==0:
        d = {}
        d['start'] = 0
        d['end'] = len(flow)
        segments.append(d)
           
    
    event_segments = []    
    
    flow_go = go.Scatter(
            x=np.arange(0,len(flow)),
            y=flow,
            name='Hydrograph',
            mode = 'lines',
            line={'color': 'blue', 'width': 4},
    )
    
    
    
    event_segments.append(flow_go)
    flow = np.asarray(flow)
    
    for segment in segments:
        event_flow = flow[segment['start']:segment['end']]
        event_go = go.Scatter(
            x=np.arange(segment['start'],segment['end']),
            y=event_flow,
            mode = 'lines',
            line={'color': 'red', 'width': 1, 'shape': 'spline'},
            
        
        )
        event_segments.append(event_go)
    

    
    data = event_segments
    
    layout = {
        'title': 'Hydrograph with {0} events'.format(str(len(segments))),
        'xaxis': {'title': 'Time'},
        'yaxis': {'title': 'Flow (cfs)'},
        'showlegend': False
    }
    figure = {'data': data, 'layout': layout}
    #fig = go.Figure(data=data)
    
    
    
    hydrograph_plot = PlotlyView(figure, height='520px', width='100%')
        
    return hydrograph_plot


def cqt_event_plot(event_id, sub_event,height='520px', width='100%'):
# Build up Plotly plot
    time,flow,concentration,segments=get_conc_flow_seg(event_id)
    
    
    if len(segments)==0:
        d = {}
        d['start'] = 0
        d['end'] = len(flow)
        segments.append(d)
           
    if sub_event >=len(segments):
        sub_event = len(segments)-1
    if sub_event <0:
        sub_event = 0
    
    
    event_flow = flow[segments[sub_event]['start']:segments[sub_event]['end']]
    event_concentration = concentration[segments[sub_event]['start']:segments[sub_event]['end']]
   
    trajectory_go = go.Scatter3d(
    x=np.arange(0,len(event_flow)),
    y=event_flow,
    z=event_concentration,
    mode = 'lines',
    name = 'trajectory',
    line=dict(
        width=10,
        color=np.arange(0,len(event_flow)),
        colorscale='Viridis',
    ),
    )
    
    data = [trajectory_go]
    
    
    
    
    layout = dict(
    width=400,
    height=400,
    autosize=False,
    title='Trajectory for event {0}'.format(str(sub_event)),
    scene=dict(
        xaxis=dict(
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=True,
            backgroundcolor='rgb(230, 230,230)',
            title = 'Time (T)'
        ),
        yaxis=dict(
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=True,
            backgroundcolor='rgb(230, 230,230)',
            title = 'Discharge (Q)'
        ),
        zaxis=dict(
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=True,
            backgroundcolor='rgb(230, 230,230)',
            title = 'Concentration (C)'
        ),
        camera=dict(
            up=dict(
                x=0,
                y=0,
                z=1
            ),
            eye=dict(
                x=-1.7428,
                y=1.0707,
                z=0.7100,
            )
        ),
        aspectratio = dict( x=1, y=1, z=1 ),
        aspectmode = 'manual'
    ),
    )


    figure = {'data': data, 'layout': layout}
    
    
    
    
    hydrograph_plot = PlotlyView(figure, height='520px', width='100%')
        
    return hydrograph_plot

    
def cq_event_plot(event_id, sub_event,height='520px', width='100%'):
# Build up Plotly plot
    time,flow,concentration,segments=get_conc_flow_seg(event_id)
    
    
    if len(segments)==0:
        d = {}
        d['start'] = 0
        d['end'] = len(flow)
        segments.append(d)
           
    if sub_event >=len(segments):
        sub_event = len(segments)-1
    if sub_event <0:
        sub_event = 0
    
    
    event_flow = flow[segments[sub_event]['start']:segments[sub_event]['end']]
    event_concentration = concentration[segments[sub_event]['start']:segments[sub_event]['end']]
   
    hysteresis_go = go.Scatter(
        x= event_flow,
        y = event_concentration,
        mode = 'lines',
        name = 'Hysteresis',
        
        
        line=dict(
            width=10,
            color='#1f77b4',
            
    ),
    )
    
    
    data = [hysteresis_go]
    
    layout = dict(
    width=400,
    height=400,
    autosize=False,
    title='Hysteresis for event {0}'.format(str(sub_event)),
    scene=dict(
        xaxis=dict(
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=True,
            backgroundcolor='rgb(230, 230,230)',
            title = 'Time (T)'
        ),
        yaxis=dict(
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=True,
            backgroundcolor='rgb(230, 230,230)',
            title = 'Discharge (Q)'
        ),
        
        aspectratio = dict( x=1, y=1),
        aspectmode = 'manual'
    ),
    )


    figure = {'data': data, 'layout': layout}



    
    hydrograph_plot = PlotlyView(figure, height='520px', width='100%')
        
    return hydrograph_plot
   
def candq_event_plot(event_id, sub_event,height='520px', width='100%'):
# Build up Plotly plot
    time,flow,concentration,segments=get_conc_flow_seg(event_id)
    
    
    if len(segments)==0:
        d = {}
        d['start'] = 0
        d['end'] = len(flow)
        segments.append(d)
           
    if sub_event >=len(segments):
        sub_event = len(segments)-1
    if sub_event <0:
        sub_event = 0
    
    
    event_flow = flow[segments[sub_event]['start']:segments[sub_event]['end']]
    event_concentration = concentration[segments[sub_event]['start']:segments[sub_event]['end']]
   
   
    flow_go = go.Scatter(
        x= np.arange(0,len(event_flow)),
        y = event_flow,
        mode = 'lines',
        name = 'Discharge',
        
        
        line=dict(
            width=5,
            color='#1f77b4',
            
    ),
    )
    
    concentration_go = go.Scatter(
        x= np.arange(0,len(event_flow)),
        y = event_concentration,
        mode = 'lines',
        name = 'concentration',
        yaxis="y2",
        
        
        line=dict(
            width=5,
            color="#ff7f0e",
            
    ),
    )

    data = []
    data.append(flow_go)
    data.append(concentration_go)
    
    layout = dict(
    xaxis=dict(
        domain=[0.3, 0.7]
    ),
    yaxis=dict(
        title="Discharge (Q)",
        titlefont=dict(
            color="#1f77b4"
        ),
        tickfont=dict(
            color="#1f77b4"
        )
    ),
    yaxis2=dict(
        title="Concentration (C)",
        titlefont=dict(
            color="#ff7f0e"
        ),
        tickfont=dict(
            color="#ff7f0e"
        ),
        overlaying="y",
        side="right"
    )
    
    
    )
    
    figure = {'data': data, 'layout': layout}



    
    hydrograph_plot = PlotlyView(figure, height='520px', width='100%')
        
    return hydrograph_plot   