from plotly import graph_objs as go
from tethys_gizmos.gizmo_options import PlotlyView
#from tethysapp.heda.app import Heda as app
from .model import get_events, get_conc_flow_seg
import numpy as np
from plotly import tools

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
    layout = go.Layout(
    xaxis = go.layout.XAxis(
        tickmode = 'linear',
       
    ),
        margin=dict(
        l=0,
        r=0,
        b=0,
        t=0
    )
    
    )
    
    fig = go.Figure(data=data, layout=layout)
    
    
    fig['layout'].update(title='Visualizations')
   
    #data = [flow_go,segments_go]
    #layout = {
    #        'title': 'title',
    #        'xaxis': {'title': 'Time (hr)'},
    #        'yaxis': {'title': 'Flow (cfs)'},
    #}
    
    #figure = {'data': data, 'layout': layout}
    hydrograph_plot = PlotlyView(fig, height='520px', width='100%')
        
    return hydrograph_plot
'''    
def create_hydrograph(event_id, height='520px', width='100%'):
    # Build up Plotly plot


    """
    Generates a plotly view of a hydrograph.
    """
    # Get objects from database
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()
    hydrograph = session.query(event_id).get(int(event_id))
    time = []
    flow = []
    for hydro_point in hydrograph.points:
        time.append(hydro_point.time)
        flow.append(hydro_point.flow)
    
    # Build up Plotly plot
    hydrograph_go = go.Scatter(
        x=time,
        y=flow,
        name='Hydrograph for {0}'.format(event_id),
        line={'color': '#0080ff', 'width': 4, 'shape': 'spline'},
    )
    data = [hydrograph_go]
    layout = {
        'title': 'Hydrograph for {0}'.format(event_id),
        'xaxis': {'title': 'Time (hr)'},
        'yaxis': {'title': 'Flow (cfs)'},
    }
    figure = {'data': data, 'layout': layout}
    hydrograph_plot = PlotlyView(figure, height=height, width=width)
    session.close()
    return hydrograph_plot
    #test change

'''        
