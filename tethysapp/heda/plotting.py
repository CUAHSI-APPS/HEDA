



class MyAxes3D(axes3d.Axes3D):

    def __init__(self, baseObject, sides_to_draw):
        self.__class__ = type(baseObject.__class__.__name__,
                              (self.__class__, baseObject.__class__),
                              {})
        self.__dict__ = baseObject.__dict__
        self.sides_to_draw = list(sides_to_draw)
        self.mouse_init()

    def set_some_features_visibility(self, visible):
        for t in self.w_zaxis.get_ticklines() + self.w_zaxis.get_ticklabels():
            t.set_visible(visible)
        self.w_zaxis.line.set_visible(visible)
        self.w_zaxis.pane.set_visible(visible)
        self.w_zaxis.label.set_visible(visible)
        
        
            

    def draw(self, renderer):
        # set visibility of some features False 
        self.set_some_features_visibility(False)
        # draw the axes
        super(MyAxes3D, self).draw(renderer)
        # set visibility of some features True. 
        # This could be adapted to set your features to desired visibility, 
        # e.g. storing the previous values and restoring the values
        self.set_some_features_visibility(True)

        zaxis = self.zaxis
        draw_grid_old = zaxis.axes._draw_grid
        # disable draw grid
        zaxis.axes._draw_grid = False

        tmp_planes = zaxis._PLANES

        if 'l' in self.sides_to_draw :
            
            #draw zaxis on the left side
            zaxis._PLANES = (tmp_planes[2], tmp_planes[3],
                             tmp_planes[0], tmp_planes[1],
                             tmp_planes[4], tmp_planes[5])
            zaxis.draw(renderer)
            
            
            
        if 'r' in self.sides_to_draw :
            # draw zaxis on the right side
            zaxis._PLANES = (tmp_planes[3], tmp_planes[2], 
                             tmp_planes[1], tmp_planes[0], 
                             tmp_planes[4], tmp_planes[5])
            zaxis.draw(renderer)

        zaxis._PLANES = tmp_planes

        # disable draw grid
        zaxis.axes._draw_grid = draw_grid_old


def reverse_colourmap(cmap, name = 'my_cmap_r'):
    """
    In: 
    cmap, name 
    Out:
    my_cmap_r

    Explanation:
    t[0] goes from 0 to 1
    row i:   x  y0  y1 -> t[0] t[1] t[2]
                   /
                  /
    row i+1: x  y0  y1 -> t[n] t[1] t[2]

    so the inverse should do the same:
    row i+1: x  y1  y0 -> 1-t[0] t[2] t[1]
                   /
                  /
    row i:   x  y1  y0 -> 1-t[n] t[2] t[1]
    """        
    reverse = []
    k = []   

    for key in cmap._segmentdata:    
        k.append(key)
        channel = cmap._segmentdata[key]
        data = []

        for t in channel:                    
            data.append((1-t[0],t[2],t[1]))            
        reverse.append(sorted(data))    

    LinearL = dict(zip(k,reverse))
    my_cmap_r = mpl.colors.LinearSegmentedColormap(name, LinearL) 
    return my_cmap_r


class HandlerColorLineCollection(HandlerLineCollection):
    def create_artists(self, legend, artist ,xdescent, ydescent,
                        width, height, fontsize,trans):
        x = np.linspace(0,width,self.get_numpoints(legend)+1)
        y = np.zeros(self.get_numpoints(legend)+1)+height/2.-ydescent
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments, cmap=artist.cmap,
                     transform=trans)
        lc.set_array(x)
        lc.set_linewidth(artist.get_linewidth())
        return [lc]

    
def plot_event(discharge,concentration):
    fig = plt.figure(figsize=(9,12))#
    
    #l = ['sedimentFlow','streamFlow','streamFlow']
    for c in range(0,4):
        cmap_r = reverse_colourmap(cm.YlGnBu)
        if c<3:
            



            if c==0: 
                #axarr = plt.subplot2grid((7, 7), (0, 0), colspan=3)
                axarr= fig.add_subplot(1, 3, c+1,aspect='equal')#
                x = np.linspace(0,1,len(concentration))
                y = concentration
                plt.plot(x,y,linewidth=2.0,linestyle = '-.',color = 'orange',label = 'SSC') #($mg/l$)
        
                axarr.set_ylabel('Concentration', fontsize = label_size,labelpad=0)#ssc
                
                axarr.tick_params(axis='both', which='major', labelsize=tick_size)
                
                
                
            if c ==1:
                axarr2 = axarr.twinx()  # instantiate a second axes that shares the same x-axis  
                color = 'tab:blue'
                
                axarr2.set_ylabel('Discharge', color=color,fontsize = label_size,labelpad=3)  # we already handled the x-label with ax1
                y = discharge
                x = np.linspace(0,1,len(concentration))
                axarr2.plot(x,y,linewidth=2.0,linestyle = '-.',color = color,label = 'SSC') #($mg/l$)
                axarr2.tick_params(axis='y', labelcolor=color)
    
                
                plt.minorticks_on()
                plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

                
                
            if c ==2:
                
                axarr= fig.add_subplot(1, 3, c,aspect='equal')
                    
                x = discharge
                y = concentration
                
                t = np.arange(len(x))
                
                plt.scatter(x,y,c=t,cmap=cmap_r,s = 10)
                axarr.xaxis.label.set_color('navy')
                axarr.yaxis.label.set_color('navy')
                axarr.set_xlabel('Q', fontsize = label_size_2,labelpad=-15)#ssc
                axarr.set_ylabel('SSC',fontsize = label_size_2,labelpad=-10)
                axarr.tick_params(axis='both', which='major', labelsize=tick_size,color='navy', labelcolor='navy')
                
                points = np.array([x, y]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)

                #lc = LineCollection(segments, cmap=plt.get_cmap('YlGnBu'),norm=plt.Normalize(0, 10), linewidth=10)
                lc = LineCollection(segments, cmap=cmap_r,norm=plt.Normalize(0, 10), linewidth=4.0)
                
                
                lc.set_array(t)



                
                axarr.legend([lc], ["time ->"],handler_map={lc: HandlerColorLineCollection(numpoints=100)}, framealpha=0.5,fontsize= legend_size,loc = 'upper left')
                
                plt.minorticks_on()
                
                
                

                
                for spine in axarr.spines.values():
                    spine.set_edgecolor('navy')
                
        
        if c ==3:
            
            axarr= fig.add_subplot(1, 3, c, projection='3d',aspect='equal')
            axarr = fig.add_axes(MyAxes3D(axarr, 'r'))

            
            x = concentration
            z = discharge
            y = np.linspace(0,1,len(x))
            
            
            t = np.arange(len(x))
    
            
            axarr.scatter(x,y,z, c=t,cmap=cmap_r, s = 10)
            
            axarr.set_xlabel('SSC', fontsize = label_size_2,labelpad=-10,rotation=-15,color = cqtcolor)#ssc
            axarr.set_ylabel('T',fontsize = label_size_2,labelpad=-10,rotation=40,color = cqtcolor)
            axarr.set_zlabel('Q',fontsize = label_size_2,labelpad=-10,color = cqtcolor)
            
            
            axarr.tick_params(axis='z', which='major', labelsize=tick_size,pad=0,labelcolor=cqtcolor)
            axarr.tick_params(axis='y', which='major', labelsize=tick_size,pad=-5,labelcolor=cqtcolor)
            axarr.tick_params(axis='x', which='major', labelsize=tick_size,pad=-5,labelcolor=cqtcolor)

            
            
            axarr.set_xlim([1, 0])
            axarr.set_ylim([0, 1])
            axarr.set_zlim([0, 1])
            
            
            points = np.array([x, z]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            lc = LineCollection(segments, cmap=cmap_r,norm=plt.Normalize(0, 10), linewidth=4)
            lc.set_array(t)



                
            axarr.legend([lc], ["time ->"],handler_map={lc: HandlerColorLineCollection(numpoints=100)}, framealpha=0.5,fontsize= legend_size,loc = 'upper left')
            #axarr.dist = 13
            axarr.view_init(elev=20)
            
            

            
            
            axarr.minorticks_on()
            
            
            axarr.grid(which='major', color='#999999', linestyle='-', alpha=0.5)
            
            axarr.dist = 7.5
            plt.yticks(rotation=45)
        
           
            
            axarr.w_xaxis.line.set_color(cqtcolor)
            axarr.w_yaxis.line.set_color(cqtcolor)
            axarr.w_zaxis.line.set_color(cqtcolor)
            
            
    
    
    
    
    return fig