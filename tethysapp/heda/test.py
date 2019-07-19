#'#0080ff'
    concentration_go = go.Scatter(
            x=np.arange(0,len(concentration)),
            y=concentration,
            name='Sedigraph',
            line={'color': 'orange', 'width': 4, 'shape': 'spline'},
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
    
    
    #fig = tools.make_subplots(rows=2, cols=1)
    #fig.append_trace(trajectory_go, 1, 1)
    #fig.append_trace(flow_go, 1, 1)
    #fig.append_trace(segments_go,1,1)
    #fig.append_trace(concentration_go, 2, 1)
    #fig.append_trace(hysteresis_go, 1, 2)
    #fig.append_trace(hysteresis_go, 2, 2)