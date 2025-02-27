from plotly import graph_objs as go
from plotly import tools
from plotly.subplots import make_subplots
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
           
    
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    
    
    
    
    
    #add all the flow
    fig.add_trace(go.Scatter(
            x=time,
            y=flow,
            name='Hydrograph',
            mode = 'lines',
            line={'color': 'blue', 'width': 1},
    ),
    secondary_y=False,
    )
    
    
    fig.add_trace(go.Scatter(
            x=time,
            y=concentration,
            name='Concentration graph',
            mode = 'lines',
            line={'color': 'orange', 'width': 1},
            
    ),
    secondary_y=True,
    )
    
    
    
    flow = np.asarray(flow)
    event_counter = 1
    
    for segment in segments:
        event_flow = flow[segment['start']:segment['end']]
        event_time = time[segment['start']:segment['end']]
        #event_concentration = concentration[segment['start']:concentration['end']]
        
        fig.add_trace(go.Scatter(
            x=event_time,
            y=event_flow,
            mode = 'lines',
            line={'color': 'red', 'width': 4, 'shape': 'spline'},
            name="", 
            
        
        ),
        secondary_y=False,
        )
        
        
        event_counter = event_counter + 1
    
    

    
    
   #this is a comment for syncing
    
    if event_id != '1':
        title = 'Number of events segmented: {0} '.format(str(len(segments)))
    else:
        title = 'Hydrograph to validate segmentation'
    
    
    fig.update_layout(
    xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        ),
        showlegend=False,
        title_text=title,
    
    )
    
    # Set x-axis title
    fig.update_xaxes(title_text="Time")

    # Set y-axes titles
    fig.update_yaxes(title_text="Flow (cfs)", secondary_y=False)
    fig.update_yaxes(title_text="Concentration", showgrid = False, secondary_y=True)

    
    
    
    
    
    
    

    
    
    hydrograph_plot = PlotlyView(fig, height='520px', width='100%')
        
    return hydrograph_plot





def create_hydrograph_old(event_id, height='520px', width='100%'):
# Build up Plotly plot
    print(event_id)
    time,flow,concentration,segments=get_conc_flow_seg(event_id)
    
    
    if len(segments)==0:
        d = {}
        d['start'] = 0
        d['end'] = len(flow)
        segments.append(d)
           
    
    event_segments = []    
    
    flow_go = go.Scatter(
            x=time,
            y=flow,
            name='Hydrograph',
            mode = 'lines',
            line={'color': 'blue', 'width': 1},
            
    )
    
    
   
    
    event_segments.append(flow_go)
    flow = np.asarray(flow)
    
    for segment in segments:
        event_flow = flow[segment['start']:segment['end']]
        event_time = time[segment['start']:segment['end']]
        event_go = go.Scatter(
            x=event_time,
            y=event_flow,
            mode = 'lines',
            line={'color': 'red', 'width': 4, 'shape': 'spline'},
            
        
        )
        event_segments.append(event_go)
    

    
    data = event_segments
    if event_id != '1':
        title = 'Hydrograph with {0} events'.format(str(len(segments)))
    else:
        title = 'Hydrograph to validate segmentation'
    
    layout = {
        'title': title,
        'xaxis': {'title': 'Time'},
        'yaxis': {'title': 'Flow (cfs)'},
        'showlegend': False,
        'xaxis_range':[time[0],time[-1]],
        
        'xaxis':go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
        
        
    }
    figure = {'data': data, 'layout': layout}
    

    
    
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
    event_time = time[segments[sub_event]['start']:segments[sub_event]['end']]
   
    trajectory_go = go.Scatter3d(
    x=event_time,
    y=event_flow,
    z=event_concentration,
    mode = 'lines',
    name = 'Trajectory',
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
    
    
    
    
    hydrograph_plot = PlotlyView(figure, height='200px', width='100%')
        
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

    
    
    
    hydrograph_plot = PlotlyView(figure, height='200px', width='100%')
        
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
    
    
def cqt_cq_event_plot(event_id, sub_event,height='800px', width='100%'):
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
    event_time = time[segments[sub_event]['start']:segments[sub_event]['end']]
   
    # Initialize figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        #Scott, column width and row with as you pointed out are ratio, we have two columns and two rows.. 
        column_widths=[0.6, 0.4],
        row_heights=[0.4, 0.6],
        #Scott - horizontal spacing, is used to remove the gap between C-Q and 3-D plot..
        horizontal_spacing = 0.05,
        specs=[[{"type": "xy","secondary_y": True,"colspan":2}, None],
            [{"type": "scatter"}, {"type": "scatter3d"}]])
            
    
    
                
       
    # Add traces
    fig.add_trace(
        go.Scatter(x=event_time, y=event_flow, name="Discharge (Q)", line=dict(
                        width=4,
                        color='blue',
            
                        ),
                        ),
        row=1, col=1,
        secondary_y=False,
        
        
    )
    fig.add_trace(
        go.Scatter(x=event_time, y=event_concentration, name="Concentration (C)",line=dict(
                        width=4,
                        color='orange',
            
                        ),),
        row=1, col=1,
        secondary_y=True,
    
    
    )
    
    
    # Add scattergeo globe map of volcano locations
    fig.add_trace(
            go.Scatter(
                x= event_flow,
                y = event_concentration,
                mode = 'lines+markers',
                name = 'Hysteresis',
                fill='toself',
                
                line=dict(
                        width=6,
                        color='#1f77b4',
            
                        ),
                marker=dict(
                size=10,
                color=np.arange(0,len(event_flow)),
                colorscale='Viridis',
            )
                        
                    
                   
            
            ),
            row=2, col=1
                )
    
    # Add 3d surface of volcano
    fig.add_trace(
        go.Scatter3d(
            x=event_time,
            y=event_flow,
            z=event_concentration,
            mode = 'lines',
            name = 'trajectory',
            line=dict(
                width=10,
                color=np.arange(0,len(event_flow)),
                colorscale='Viridis',
            )
            
    
        ),
        row=2, col=2
    )
    #Scott - height 800 and width 950. I am using these to adjust height and width. I think if you want height to be greater or small, i would also change the height in line "PlotlyView(fig, height='800px', width='100%')" to match.  
    fig['layout'].update(height=800, width=950)
                                                  
    # Set theme, margin, and annotation in layout
    fig.update_layout(
        template="plotly_dark", #ggplot2, plotly_dark, seaborn, plotly, plotly_white, presentation, xgridoff
        margin=dict(r=10, t=25, b=40, l=60),
        autosize=True,
        #automargin=True,
        annotations=[
            go.layout.Annotation(
                text="Source: CAUHSI - HEDA Tool",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0,
                y=0)
        ],
        scene1 = dict(
                    xaxis_title='Time',
                    yaxis_title='Discharge',
                    zaxis_title='Concentration'),
        #showlegend=False,
        #Scott - I moved the legend to top because it was messing with space utilization of figure. 
        #orientation "h" makes it a horizontal legend.
        legend_orientation="h",
        #location coordinates of legend.
        legend=dict(x=-.1, y=1.1),
        
    )
    
    
    fig.update_yaxes(title_text="Concentration", row=2, col=1)
    fig.update_xaxes(title_text="Discharge", row=2, col=1)
    
    
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_yaxes(title_text="Discharge", row=1, col=1,secondary_y = False)
    fig.update_yaxes(title_text="Concentration", row=1, col=1,secondary_y = True)
    
    

    
    
    hydrograph_plot = PlotlyView(fig, height='800px', width='100%')
    return hydrograph_plot
   