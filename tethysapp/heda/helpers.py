from plotly import graph_objs as go
from tethys_gizmos.gizmo_options import PlotlyView
#from tethysapp.heda.app import Heda as app
from .model import get_events, get_conc_flow_seg
import numpy as np
from plotly import tools
import matplotlib.pyplot as plt  



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


def plot_event(event_id, sub_event,height='520px', width='100%'):
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
            x=event_flow,
            y=event_concentration,
            mode = 'lines',
            line={'color': 'red', 'width': 1, 'shape': 'spline'},
            
        
        )
        
    concentration_go = go.Scatter(
            x=np.arange(segments[sub_event]['start'],segments[sub_event]['end']),
            y=event_concentration,
            mode = 'lines',
            line={'color': 'orange', 'width': 1, 'shape': 'spline'},
            
        
        )
    flow_go = go.Scatter(
            x=np.arange(segments[sub_event]['start'],segments[sub_event]['end']),
            y=event_flow,
            mode = 'lines',
            line={'color': 'blue', 'width': 1, 'shape': 'spline'},
            
        
        )
    
    
    
    fig = tools.make_subplots(rows=3, cols=1)
    fig.append_trace(hysteresis_go, 1, 1)
    fig.append_trace(flow_go, 2, 1)
    fig.append_trace(concentration_go,3,1)
    

    
    
    
    
    
    hydrograph_plot = PlotlyView(fig, height='520px', width='100%')
    
    # Compute the x and y coordinates for points on a sine curve 
    figure = plt.figure()
    x = np.arange(0, 3 * np.pi, 0.1) 
    y = np.sin(x) 
    

    # Plot the points using matplotlib 
    plt.plot(x, y) 
    
    # Converting to Plotly's Figure object..
    plotly_fig = tools.mpl_to_plotly(figure)


    hydrograph_plot = PlotlyView(plotly_fig, height=height, width=width)
        
    return hydrograph_plot 