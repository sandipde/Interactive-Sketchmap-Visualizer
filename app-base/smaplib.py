#from bokeh.io import output_notebook
from bokeh.layouts import layout,row
#output_notebook()
import numpy as np
import pandas as pd

class smap:
    import numpy as np
    import pandas as pd 
    from bokeh.palettes import Spectral6
    from bokeh.palettes import Spectral6,Inferno256,Viridis256,Greys256,Magma256,Plasma256
    def __init__(self, name='smapdata'):
        self.name = name
        self.data = []    # creates a new empty list 
        self.columns = []
        self.pd=pd.DataFrame(self.data,columns=self.columns)
        
    def add_data(self,data,columns=[]):
        self.data=data
        ncol=len(data[0])
        self.columns=columns
        self.check_columns()
        self.pd=pd.DataFrame(self.data,columns=self.columns)
        
    def read_data(self,filename):
        self.data=np.loadtxt(filename)
        self.get_columns(filename)
        self.pd=pd.DataFrame(self.data,columns=self.columns)
        
    def read(self,filename,sep='\s+',**kwargs):
        self.pd=pd.read_csv(filename,sep=sep,**kwargs)
        self.data=self.pd.values
        self.columns=self.pd.columns
        
    def write(self,filename='',sep='\t',**kwargs):
        if (filename==''):filename=self.name+'-COLVAR.dat'
        self.pd.to_csv(filename,sep='\t',index=False) 

    def read_properties(self,propfile,sep='\s+',**kwargs):
        prop=pd.read_csv(propfile,sep=sep,**kwargs)
        if (len(prop) != len(self.data)): 
            print ("data length and property length mismtch")
            pass
        df=self.pd
        self.pd=pd.concat([df,prop],axis=1)
        self.data=self.pd.values
        self.columns=self.pd.columns
        
    def get_columns(self,file):
        with open(file) as f:
            last_pos = f.tell()
            li=f.readline().strip()
            if li.startswith("#"):
                self.columns=li.split()[1:]

            else:
                pcount=len(li.split())
                for i in range(pcount):
                    self.columns.append["prop_"+str(i+1)]
        self.check_columns()
        
    def check_columns(self):
        ncol=len(self.data[0])
        if (len(self.columns)< ncol):
            pcount=len(self.columns)
            for i in range(pcount,ncol):
                self.columns.append("col_"+str(i+1))
        self.columns=self.columns[:ncol]

    def normalize(self,v):
    	norm=np.linalg.norm(v)
    	if norm==0: 
    	   return v
    	v=v/norm
    	return v-min(v)

    def bkplot(self,x,y,color='None',radii='None',ps=20,minps=0,alpha=0.8,pw=600,ph=400,palette='Inferno256',style='smapstyle',Hover=True,title='',table=False,table_width=600, table_height=150,add_colorbar=True,Periodic_color=False,return_datasrc=False,frac_load=1.0,**kwargs):
        from bokeh.layouts import row, widgetbox,column,Spacer
        from bokeh.models import HoverTool,TapTool,FixedTicker,Circle,WheelZoomTool
        from bokeh.models import CustomJS, Slider,Rect,ColorBar,HoverTool,LinearColorMapper, BasicTicker
        from bokeh.plotting import figure
        from bokeh.models import ColumnDataSource, CDSView, IndexFilter
        from bokeh.palettes import Spectral6,Inferno256,Viridis256,Greys256,Magma256,Plasma256
        from bokeh.palettes import Spectral,Inferno,Viridis,Greys,Magma,Plasma
        from bokeh.models import LogColorMapper, LogTicker, ColorBar,BasicTicker,LinearColorMapper
        from bokeh.models.widgets import DataTable,TableColumn,NumberFormatter,Div
        import pandas as pd
#        if (title==''): title=self.name
        fulldata=self.pd
        idx=np.arange(len(fulldata))
        fulldata['id']=idx 
        nload=int(frac_load*len(fulldata))
        np.random.shuffle(idx)
        idload=np.sort(idx[0:nload])
        data=self.pd.iloc[idload].copy()
        COLORS=locals()[palette]
       # TOOLS="resize,crosshair,pan,wheel_zoom,reset,tap,save,box_select,box_zoom,lasso_select"
        TOOLS="pan,reset,tap,save,box_zoom,lasso_select"
        wheel_zoom=WheelZoomTool(dimensions='both')
        if Hover :
             proplist=[]
             for prop in data.columns:
                 if prop not in ["CV1","CV2","Cv1","Cv2","cv1","cv2","colors","radii","id"]: proplist.append((prop,'@'+prop))
             hover = HoverTool(names=["mycircle"],
                     tooltips=[
                         ("id", '@id')
                     ]
                 )
             for prop in proplist:
                  hover.tooltips.append(prop)
             plot=figure(title=title,plot_width=pw,active_scroll=wheel_zoom, plot_height=ph,tools=[TOOLS,hover,wheel_zoom],**kwargs)
        else:
             plot=figure(title=title,plot_width=pw,active_scroll=wheel_zoom, plot_height=ph,tools=[TOOLS],**kwargs)


# selection glyphs and plot styles
        initial_circle = Circle(x='x', y='y')
        selected_circle = Circle(fill_alpha=0.7, fill_color="blue", size=ps*1.5 ,line_color=None)
        nonselected_circle = Circle(fill_alpha=alpha*0.5,fill_color='colors',line_color=None)
# set up variable point size
        if radii == 'None':
            r=[ps for i in range(len(data))]
            data['radii']=r
        else:
            if data[radii].dtype=='object' :    # Categorical variable for radii
                grouped=data.groupby(radii)
                i=0
                r=np.zeros(len(data))
                for group_item in grouped.groups.keys():
                    r[grouped.groups[group_item].tolist()]=i**2
                    i=i+2
            else:
                r=[val for val in data[radii]]
            rn=self.normalize(r)
            rad=[minps+ps*np.sqrt(val) for val in rn ]
            data['radii']=rad

# setup variable point color             
        if color == 'None':
           c = ["#31AADE" for i in range(len(data))]
           data['colors']=c
           datasrc=ColumnDataSource(data)
           plot.circle(x,y,source=datasrc,size='radii',fill_color='colors', fill_alpha=alpha, line_color=None,name="mycircle")
           renderer = plot.select(name="mycircle")
           renderer.selection_glyph = selected_circle
           renderer.nonselection_glyph = nonselected_circle
        else:
            if data[color].dtype=='object' :    # Categorical variable for colors
                grouped=data.groupby(color)
                COLORS=Spectral[len(grouped)]
                i=0
                for group_item in grouped.groups.keys():
                    data.loc[grouped.groups[group_item],'colors']=COLORS[i]
                    i+=1
                #colors=[ '#d53e4f', '#3288bd','#fee08b', '#99d594']
                datasrc=ColumnDataSource(data)
                for  group_item in grouped.groups.keys():
                    view = CDSView(source=datasrc, filters=[IndexFilter(grouped.groups[group_item])])
                    plot.circle(x,y,source=datasrc,size='radii',fill_color='colors',muted_color='colors', muted_alpha=0.2, fill_alpha=alpha, line_color=None,name='mycircle',legend=group_item,view=view)
                renderer = plot.select(name="mycircle")
                renderer.selection_glyph = selected_circle
                renderer.nonselection_glyph = nonselected_circle
                plot.legend.location = "top_left"
                plot.legend.orientation = "vertical"
                plot.legend.click_policy="mute"
	    else:
                if Periodic_color: # if periodic property then generate periodic color palatte
                     blendcolor=interpolate(COLORS[-1],COLORS[0],len(COLORS)/5)
                     COLORS=COLORS+blendcolor
                groups = pd.cut(data[color].values, len(COLORS))
                c = [COLORS[xx] for xx in groups.codes]
                data['colors']=c
                datasrc=ColumnDataSource(data)
                plot.circle(x,y,source=datasrc,size='radii',fill_color='colors', fill_alpha=alpha, line_color=None,name="mycircle")
                renderer = plot.select(name="mycircle")
                renderer.selection_glyph = selected_circle
                renderer.nonselection_glyph = nonselected_circle
                color_mapper=LinearColorMapper(COLORS, low=data[color].min(), high=data[color].max())
                colorbar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker(),label_standoff=4, border_line_color=None, location=(0,0),orientation="vertical")
                colorbar.background_fill_alpha = 0
                colorbar.border_line_alpha = 0
                if add_colorbar:
                   plot.add_layout(colorbar, 'left')
# Overview plot           
        oplot=figure(title='',plot_width=200, plot_height=200,toolbar_location=None)
        oplot.circle(x,y,source=datasrc,size=4, fill_alpha=0.6, line_color=None,name="mycircle")
        orenderer = oplot.select(name="mycircle")
        orenderer.selection_glyph = selected_circle
       # orenderer.nonselection_glyph = nonselected_circle
        rectsource = ColumnDataSource({'xs': [], 'ys': [], 'wd': [], 'ht': []})
        jscode="""
                var data = source.data;
                var start = range.start;
                var end = range.end;
                data['%s'] = [start + (end - start) / 2];
                data['%s'] = [end - start];
                source.change.emit();
             """
        plot.x_range.callback = CustomJS(
               args=dict(source=rectsource, range=plot.x_range), code=jscode % ('xs', 'wd'))
        plot.y_range.callback = CustomJS(
               args=dict(source=rectsource, range=plot.y_range), code=jscode % ('ys', 'ht'))
        rect = Rect(x='xs', y='ys', width='wd', height='ht', fill_alpha=0.1,
                   line_color='black', fill_color='red')
        oplot.add_glyph(rectsource, rect)
   
# plot style 
        plot.toolbar.logo=None
        oplot.toolbar.logo=None
        if style == 'smapstyle':plist=[plot,oplot]
        else: plist=[oplot]
        for p in plist:
                 p.xgrid.grid_line_color = None
                 p.ygrid.grid_line_color = None
                 p.xaxis[0].ticker=FixedTicker(ticks=[])
                 p.yaxis[0].ticker=FixedTicker(ticks=[])
                 p.outline_line_width = 0
                 p.outline_line_alpha = 0
                 p.background_fill_alpha = 0
                 p.border_fill_alpha = 0
                 p.xaxis.axis_line_width = 0
                 p.xaxis.axis_line_color = "white"
                 p.yaxis.axis_line_width = 0
                 p.yaxis.axis_line_color = "white"
                 p.yaxis.axis_line_alpha = 0
# table
        if table:
             tcolumns=[TableColumn(field='id' ,title='id',formatter=NumberFormatter(format='0'))]
             for prop in data.columns:
                if prop not in ["CV1","CV2","Cv1","Cv2","cv1","cv2","colors",'id',"radii"]: 
                  if data[prop].dtype == 'object': tcolumns.append(TableColumn(field=prop ,title=prop))
                  if data[prop].dtype == 'float64': tcolumns.append(TableColumn(field=prop ,title=prop,formatter=NumberFormatter(format='0.00')))
                  if data[prop].dtype == 'int64': tcolumns.append(TableColumn(field=prop ,title=prop,formatter=NumberFormatter(format='0')))
             data_table = DataTable(source=datasrc, fit_columns=True, scroll_to_selection=True,columns=tcolumns,name="Property Table", width=table_width, height=table_height)
             div = Div(text="""<h6><b> Property Table </b> </h6> <br>""",
width=600, height=10)
             if return_datasrc: return plot,oplot,column(widgetbox(div),Spacer(height=10),widgetbox(data_table)),datasrc
             else: return plot,oplot,column(widgetbox(div),Spacer(height=10),widgetbox(data_table))
        else:
             return plot,oplot



class Distance_matrix:
    import numpy as np
    import pandas as pd 

    
    def __init__(self, name='distance-matrix'):
        self.name = name
        self.data = []    # creates a new empty list 
        self.filename=''
        self.colvar=[]
    def read(self,filename):
        self.filename=filename
        self.data=np.loadtxt(filename)
        
    def plot(self,width=12,height=9,**kwargs):
        import seaborn as sns; sns.set(style="ticks", color_codes=True)
        import matplotlib.pyplot as plt
        f, ax = plt.subplots(figsize=(width, height))
        title='Distance Matrix for: '+self.name
        ax.set(title=title)
        sns.heatmap(self.data,square=True,**kwargs)
        plt.show()
    
    def histogram(self,width=8,height=6,**kwargs):
        import seaborn as sns; sns.set(style="ticks", color_codes=True)
        import matplotlib.pyplot as plt
        f, ax = plt.subplots(figsize=(width, height))
        title='Histogram for: '+self.name
        ax.set(title=title)
        sns.distplot(self.data.flatten(),**kwargs)
        plt.show()

    def histogram_with_sigmoid(self,sigma=0.3,aa=6.0,bb=6.0,Interactive=True):
        n,m = self.data.shape
        a = self.data.copy()
        rangea = (np.amin(a),np.amax(a))
        nbin = int((rangea[1]- rangea[0])/2e-3)
        hist, bins = np.histogram(a, bins=nbin)
        width = 0.7 * (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / 2
        b = np.true_divide(hist, np.amax(hist))
        # print 'Max of the distribution is at x={:.3f}'.format(center[np.argmax(b)])
        #  print 'A good sigma could be at sigma={:.3f}'.format(0.8*center[np.argmax(b)])

        if Interactive is True:
           histogram=self.plot_hist_sigmoid_interactive(center,b,sigma,aa,bb)
        else:
           fig, ax1 = plt.subplots(1)
           ax1.bar(center, b, align='center', width=width,color='#006D9C',linewidth=0)
           ax1.grid()
           plt.show()
        return histogram

    def plot_hist_sigmoid_interactive(self,center,hist,sigma,a,b):
        from bokeh.layouts import row, widgetbox,column
        from bokeh.models import CustomJS, Slider,ColorBar,HoverTool,LinearColorMapper, BasicTicker
        from bokeh.plotting import figure, ColumnDataSource,show,reset_output,output_file
        from bokeh.models.widgets import Select
        import matplotlib.pylab as plt
        from bokeh.io import output_notebook
        from bokeh.palettes import Spectral6,Inferno256,Viridis256,Greys256,Magma256,Plasma256
        from bokeh.models import LogColorMapper, LogTicker, ColorBar,BasicTicker,LinearColorMapper
        output_notebook()
        from bokeh.embed import notebook_div
        from bokeh.palettes import Spectral6,Inferno256,Viridis256,Greys256,Magma256,Plasma256
        from bokeh.models import LogColorMapper, LogTicker, ColorBar,BasicTicker,LinearColorMapper
        plot = figure(y_range=(0,1), plot_width=400, plot_height=200)
        plot.line(x=center,y=hist,line_color='#EF1735',line_width=2)
        #   a=6.;b=3.;sigma=0.5;
        x = np.linspace(0, 1, 500)
        y = 1.-np.power(1.+(np.power(2.,(a/b))-1.)*np.power(x/sigma,a),(-b/a))

        datasource = ColumnDataSource(data=dict(xs=x, ys=y))

        plot.line('xs', 'ys', source=datasource, line_width=2, line_alpha=0.8)

        callback = CustomJS(args=dict(source=datasource), code="""
           var data = source.data;
           var a = a.value;
           var b = b.value;
           var sigma = sigma.value;
           x = data['xs']
           y = data['ys']
           for (i = 0; i < x.length; i++) {
               y[i] = 1.-Math.pow(1.+(Math.pow(2.,(a/b))-1.)*Math.pow(x[i]/sigma,a),(-b/a));
           }
           source.change.emit();
        """)

        a_slider = Slider(start=1., end=20., value=a, step=1.,title="a", callback=callback)
        callback.args["a"] = a_slider

        b_slider = Slider(start=1., end=20., value=b, step=1.,title="b", callback=callback)
        callback.args["b"] = b_slider

        sigma_slider = Slider(start=0.001, end=1., value=sigma, step=.001,title="sigma", callback=callback)
        callback.args["sigma"] = sigma_slider


        layout = row(plot,widgetbox(a_slider, b_slider, sigma_slider))
        # layout = widgetbox(a_slider, b_slider, sigma_slider)
        #output_file("slider.html", title="sl/home/de/bin/sketch-map.shider.py example")
        return layout
        #   show(layout,notebook_handle=True);

        
    def smap(self,sigma,a,b):
        simfile=self.filename
        sim=self.data
        n=len(sim)
        prefix=simfile+"smap-"+str(sigma)+'-'+str(a)+''+str(b)
        get_ipython().system(u'./sketch-map.sh $n $simfile $prefix $sigma $a $b >log')
        get_ipython().system(u'rm -f $prefix*.gmds_* $prefix*.imds $prefix*.ismap global.*')
        cv=np.loadtxt(prefix+'.gmds')
        self.colvar=cv

import string
def interpolate_tuple( startcolor, goalcolor, steps ):
    """
    Take two RGB color sets and mix them over a specified number of steps.  Return the list
    """
    # white

    R = startcolor[0]
    G = startcolor[1]
    B = startcolor[2]

    targetR = goalcolor[0]
    targetG = goalcolor[1]
    targetB = goalcolor[2]

    DiffR = targetR - R
    DiffG = targetG - G
    DiffB = targetB - B

    buffer = []

    for i in range(0, steps +1):
        iR = R + (DiffR * i / steps)
        iG = G + (DiffG * i / steps)
        iB = B + (DiffB * i / steps)

        hR = string.replace(hex(iR), "0x", "")
        hG = string.replace(hex(iG), "0x", "")
        hB = string.replace(hex(iB), "0x", "")

        if len(hR) == 1:
            hR = "0" + hR
        if len(hB) == 1:
            hB = "0" + hB

        if len(hG) == 1:
            hG = "0" + hG

        color = string.upper("#"+hR+hG+hB)
        buffer.append(color)

    return buffer

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def interpolate( startcolor, goalcolor, steps ):
    """
    wrapper for interpolate_tuple that accepts colors as html ("#CCCCC" and such)
    """
    start_tuple = hex_to_rgb(startcolor)
    goal_tuple = hex_to_rgb(goalcolor)

    return interpolate_tuple(start_tuple, goal_tuple, steps)



def printchart(startcolor, endcolor, steps):

    colors = interpolate(startcolor, endcolor, steps)

    for color in colors:
        print color
