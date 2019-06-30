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
        segments = [0,len(flow)-1]

    flow_go = go.Scatter(
            x=np.arange(0,len(flow)),
            y=flow,
            name='Hydrograph',
            line={'color': 'blue', 'width': 4, 'shape': 'spline'},
    )
    
    #'#0080ff'
    concentration_go = go.Scatter(
            x=np.arange(0,len(concentration)),
            y=concentration,
            name='Sedigraph',
            line={'color': 'orange', 'width': 4, 'shape': 'spline'},
    )
    
    
    
    flow = np.asarray(flow)
    
    segments_go = go.Scatter(
        x= segments,
        y = flow[segments],
        mode = 'markers',
        name = 'Segments',
        line={'color': 'red'},
    )
    
    
    trajectory_go = go.Scatter3d(
    x=flow,
    y=flow,
    z=concentration,
    mode = 'markers',
    name = 'trajectory',
    marker=dict(
        size=12,
        line=dict(
            color='rgba(217, 217, 217, 0.14)',
            width=0.5
        ),
        opacity=0.8
    )
    )
    

    hysteresis_go = go.Scatter(
        x= flow,
        y = concentration,
        mode = 'markers',
        name = 'Segments',
    )
    
    data = [trajectory_go]
    layout = go.Layout(
        margin=dict(
        l=0,
        r=0,
        b=0,
        t=0
    )
    )
    
    #fig = go.Figure(data=data, layout=layout)
    fig = tools.make_subplots(rows=2, cols=1)
    #fig.append_trace(trajectory_go, 1, 1)
    fig.append_trace(flow_go, 1, 1)
    fig.append_trace(segments_go,1,1)
    fig.append_trace(concentration_go, 2, 1)
    #fig.append_trace(hysteresis_go, 1, 2)
    #fig.append_trace(hysteresis_go, 2, 2)
    
    #fig['layout'].update(title='Visualizations')
   
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
