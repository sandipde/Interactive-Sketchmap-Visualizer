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

    def bkplot(self,x,y,color='None',radii='None',ps=20,minps=0,alpha=0.8,pw=600,ph=400,palette='Inferno256',style='smapstyle',Hover=True,title='',table=False,table_width=600, table_height=150,add_colorbar=True,**kwargs):
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
        data=self.pd
        COLORS=locals()[palette]
       # TOOLS="resize,crosshair,pan,wheel_zoom,reset,tap,save,box_select,box_zoom,lasso_select"
        TOOLS="pan,reset,tap,save,box_zoom,lasso_select"
        wheel_zoom=WheelZoomTool(dimensions='both')
        if Hover :
             proplist=[]
             for prop in data.columns:
                 if prop not in ["CV1","CV2","Cv1","Cv2","cv1","cv2","colors","radii"]: proplist.append((prop,'@'+prop))
             hover = HoverTool(names=["mycircle"],
                     tooltips=[
                         ("index", "$index"),
                         ("(x,y)", "($x, $y)")
                     ]
                 )
             for prop in proplist:
                  hover.tooltips.append(prop)
             plot=figure(title=title,plot_width=pw,active_scroll=wheel_zoom, plot_height=ph,tools=[TOOLS,hover,wheel_zoom],**kwargs)
        else:
             plot=figure(title=title,plot_width=pw,active_scroll=wheel_zoom, plot_height=ph,tools=[TOOLS],**kwargs)


# selection glyphs and plot styles
        initial_circle = Circle(x='x', y='y')
        selected_circle = Circle(fill_alpha=0.7, fill_color="blue", size=25 ,line_color=None)
        nonselected_circle = Circle(fill_alpha=0.5,fill_color='colors',line_color=None)
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
                    plot.circle(x,y,source=datasrc,size='radii',fill_color='colors', fill_alpha=alpha, line_color=None,name='mycircle',legend=group_item,view=view)
                renderer = plot.select(name="mycircle")
                renderer.selection_glyph = selected_circle
                renderer.nonselection_glyph = nonselected_circle
                plot.legend.location = "top_left"
                plot.legend.orientation = "vertical"
	    else:
                groups = pd.cut(data[color].values, len(COLORS))
                c = [COLORS[xx] for xx in groups.codes]
                data['colors']=c
                datasrc=ColumnDataSource(data)
                plot.circle(x,y,source=datasrc,size='radii',fill_color='colors', fill_alpha=alpha, line_color=None,name="mycircle")
                renderer = plot.select(name="mycircle")
                renderer.selection_glyph = selected_circle
                renderer.nonselection_glyph = nonselected_circle
                color_mapper=LinearColorMapper(palette, low=data[color].min(), high=data[color].max())
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
        if style == 'smapstyle':
             for p in [plot,oplot]:
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
                 p.toolbar.logo=None
# table
        if table:
             tcolumns=[]
             for prop in data.columns:
                if prop not in ["CV1","CV2","Cv1","Cv2","cv1","cv2","colors"]: #,"radii"]: 
                  if data[prop].dtype == 'object': tcolumns.append(TableColumn(field=prop ,title=prop))
                  if data[prop].dtype == 'float64': tcolumns.append(TableColumn(field=prop ,title=prop,formatter=NumberFormatter(format='0.00')))
                  if data[prop].dtype == 'int64': tcolumns.append(TableColumn(field=prop ,title=prop,formatter=NumberFormatter(format='0')))
             data_table = DataTable(source=datasrc, fit_columns=True, scroll_to_selection=True,columns=tcolumns,name="Property Table", width=table_width, height=table_height)
             div = Div(text="""<h6><b> Property Table </b> </h6> <br>""",
width=600, height=10)
             return plot,oplot,column(widgetbox(div),Spacer(height=10),widgetbox(data_table))
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

    def cosmo_color():
  
       colors=["#ddf0fe", "#dcf0fe", "#dcf0fe", "#dbf0fe", "#dbf0fe", "#dbeffe", \
       "#daeffe", "#daeffe", "#d9effe", "#d9effe", "#d8eefe", "#d8eefe", \
       "#d7eefe", "#d7eefe", "#d6edfe", "#d6edfe", "#d5edfe", "#d5edfe", \
       "#d4edfe", "#d4ecfe", "#d3ecfe", "#d3ecfe", "#d2ecfe", "#d2ebfe", \
       "#d1ebfe", "#d1ebfe", "#d0ebfe", "#d0eafe", "#d0eafe", "#cfeafe", \
       "#cfeafe", "#cee9fe", "#cee9fd", "#cde9fd", "#cce9fd", "#cce9fd", \
       "#cbe8fd", "#cbe8fd", "#cae8fd", "#cae8fd", "#c9e7fd", "#c9e7fd", \
       "#c8e7fd", "#c8e7fd", "#c7e6fd", "#c7e6fd", "#c6e6fd", "#c6e6fd", \
       "#c5e5fd", "#c5e5fd", "#c4e5fd", "#c4e5fd", "#c3e4fd", "#c3e4fd", \
       "#c2e4fd", "#c2e3fd", "#c1e3fd", "#c0e3fd", "#c0e3fd", "#bfe2fd", \
       "#bfe2fd", "#bee2fd", "#bee2fd", "#bde1fd", "#bde1fd", "#bce1fd", \
       "#bce1fd", "#bbe0fd", "#bae0fd", "#bae0fd", "#b9dffd", "#b9dffd", \
       "#b8dffd", "#b8dffd", "#b7defd", "#b7defd", "#b6defd", "#b5defd", \
       "#b5ddfc", "#b4ddfc", "#b4ddfc", "#b3dcfc", "#b3dcfc", "#b2dcfc", \
       "#b2dcfc", "#b1dbfc", "#b0dbfc", "#b0dbfc", "#afdbfc", "#afdafc", \
       "#aedafc", "#aedafc", "#add9fc", "#acd9fc", "#acd9fc", "#abd9fc", \
       "#abd8fc", "#aad8fc", "#a9d8fc", "#a9d7fc", "#a8d7fc", "#a8d7fc", \
       "#a7d7fc", "#a7d6fc", "#a6d6fc", "#a5d6fc", "#a5d5fc", "#a4d5fc", \
       "#a4d5fc", "#a3d4fc", "#a2d4fc", "#a2d4fc", "#a1d4fc", "#a1d3fc", \
       "#a0d3fc", "#9fd3fc", "#9fd2fc", "#9ed2fc", "#9ed2fb", "#9dd2fb", \
       "#9cd1fb", "#9cd1fb", "#9bd1fb", "#9bd0fb", "#9ad0fb", "#99d0fb", \
       "#99cffb", "#98cffb", "#98cffb", "#97cffb", "#96cefb", "#96cefb", \
       "#95cefb", "#95cdfb", "#94cdfb", "#93cdfb", "#93ccfb", "#92ccfb", \
       "#92ccfb", "#91cbfb", "#90cbfb", "#90cbfb", "#8fcbfb", "#8fcafb", \
       "#8ecafb", "#8dcafb", "#8dc9fb", "#8cc9fb", "#8bc9fb", "#8bc8fb", \
       "#8ac8fb", "#8ac8fb", "#89c7fb", "#88c7fb", "#88c7fa", "#88c6fa", \
       "#87c6fa", "#87c6fa", "#87c5fa", "#86c5fa", "#86c5fa", "#86c4fa", \
       "#85c4fa", "#85c4fa", "#85c3f9", "#84c3f9", "#84c2f9", "#84c2f9", \
       "#83c2f9", "#83c1f9", "#83c1f9", "#82c1f9", "#82c0f9", "#82c0f8", \
       "#82bff8", "#81bff8", "#81bff8", "#81bef8", "#80bef8", "#80bef8", \
       "#80bdf8", "#7fbdf8", "#7fbdf7", "#7fbcf7", "#7ebcf7", "#7ebbf7", \
       "#7ebbf7", "#7dbbf7", "#7dbaf7", "#7dbaf7", "#7dbaf7", "#7cb9f6", \
       "#7cb9f6", "#7cb8f6", "#7bb8f6", "#7bb8f6", "#7bb7f6", "#7bb7f6", \
       "#7ab6f6", "#7ab6f5", "#7ab6f5", "#79b5f5", "#79b5f5", "#79b5f5", \
       "#78b4f5", "#78b4f5", "#78b3f5", "#78b3f5", "#77b3f4", "#77b2f4", \
       "#77b2f4", "#76b2f4", "#76b1f4", "#76b1f4", "#76b0f4", "#75b0f4", \
       "#75b0f3", "#75aff3", "#74aff3", "#74aef3", "#74aef3", "#74aef3", \
       "#73adf3", "#73adf3", "#73adf2", "#73acf2", "#72acf2", "#72abf2", \
       "#72abf2", "#71abf2", "#71aaf2", "#71aaf2", "#71a9f1", "#70a9f1", \
       "#70a9f1", "#70a8f1", "#70a8f1", "#6fa7f1", "#6fa7f1", "#6fa7f1", \
       "#6fa6f0", "#6ea6f0", "#6ea5f0", "#6ea5f0", "#6ea5f0", "#6da4f0", \
       "#6da4f0", "#6da4f0", "#6da3ef", "#6ca3ef", "#6ca2ef", "#6ca2ef", \
       "#6ca2ef", "#6ba1ef", "#6ba1ef", "#6ba0ee", "#6ba0ee", "#6aa0ee", \
       "#6a9fee", "#6a9fee", "#6a9eee", "#699eee", "#699eee", "#699ded", \
       "#699ded", "#689ced", "#689ced", "#689ced", "#689bed", "#679bed", \
       "#679aec", "#679aec", "#679aec", "#6699ec", "#6699ec", "#6698ec", \
       "#6698ec", "#6598ec", "#6597eb", "#6597eb", "#6596eb", "#6596eb", \
       "#6496eb", "#6495eb", "#6495eb", "#6494ea", "#6394ea", "#6394ea", \
       "#6393ea", "#6393ea", "#6392ea", "#6292ea", "#6292e9", "#6291e9", \
       "#6291e9", "#6191e9", "#6190e9", "#6190e9", "#618fe9", "#618fe8", \
       "#608fe8", "#608ee8", "#608ee8", "#608de8", "#5f8de8", "#5f8de8", \
       "#5f8ce8", "#5f8ce7", "#5f8be7", "#5e8be7", "#5e8be7", "#5e8ae7", \
       "#5e8ae7", "#5e89e7", "#5d89e6", "#5d89e6", "#5d88e6", "#5d88e6", \
       "#5d87e6", "#5c87e6", "#5c87e6", "#5c86e5", "#5c86e5", "#5c85e5", \
       "#5b85e5", "#5b85e5", "#5b84e5", "#5b84e5", "#5b83e4", "#5a83e4", \
       "#5a83e4", "#5a82e4", "#5a82e4", "#5a81e4", "#5981e4", "#5981e3", \
       "#5980e3", "#5980e3", "#597fe3", "#587fe3", "#587fe3", "#587ee3", \
       "#587ee2", "#587de2", "#577de2", "#577de2", "#577ce2", "#577ce2", \
       "#577be2", "#577be1", "#567be1", "#567ae1", "#567ae1", "#5679e1", \
       "#5679e1", "#5579e1", "#5578e0", "#5578e0", "#5577e0", "#5577e0", \
       "#5577e0", "#5476e0", "#5476df", "#5475df", "#5475df", "#5475df", \
       "#5474df", "#5374df", "#5373df", "#5373de", "#5373de", "#5372de", \
       "#5272de", "#5271de", "#5271de", "#5271de", "#5270dd", "#5270dd", \
       "#5170dd", "#516fdd", "#516fdd", "#516edd", "#516edd", "#516edc", \
       "#506ddc", "#506ddc", "#506cdc", "#506cdc", "#506cdc", "#506bdc", \
       "#506bdb", "#4f6adb", "#4f6adb", "#4f6adb", "#4f69db", "#4f69db", \
       "#4f68da", "#4e68da", "#4e68da", "#4e67da", "#4e67da", "#4e67da", \
       "#4e66da", "#4d66d9", "#4d65d9", "#4d65d9", "#4d65d9", "#4d64d9", \
       "#4d64d9", "#4d63d9", "#4c63d8", "#4c63d8", "#4c62d8", "#4c62d8", \
       "#4c61d8", "#4c61d8", "#4c61d7", "#4c60d7", "#4c60d7", "#4c60d7", \
       "#4c5fd6", "#4c5fd6", "#4b5fd6", "#4b5ed6", "#4b5ed6", "#4b5ed5", \
       "#4b5ed5", "#4b5dd5", "#4b5dd5", "#4b5dd4", "#4b5cd4", "#4b5cd4", \
       "#4b5cd4", "#4b5bd3", "#4b5bd3", "#4b5bd3", "#4b5ad3", "#4b5ad3", \
       "#4b5ad2", "#4b59d2", "#4b59d2", "#4b59d2", "#4b58d1", "#4b58d1", \
       "#4b58d1", "#4b57d1", "#4b57d0", "#4b57d0", "#4b56d0", "#4b56d0", \
       "#4b56d0", "#4b55cf", "#4b55cf", "#4b55cf", "#4b54cf", "#4b54ce", \
       "#4b54ce", "#4b54ce", "#4a53ce", "#4a53cd", "#4a53cd", "#4a52cd", \
       "#4a52cd", "#4a52cd", "#4a51cc", "#4a51cc", "#4a51cc", "#4a50cc", \
       "#4a50cb", "#4a50cb", "#4a4fcb", "#4a4fcb", "#4a4fca", "#4a4eca", \
       "#4a4eca", "#4a4eca", "#4a4ec9", "#4a4dc9", "#4a4dc9", "#4a4dc9", \
       "#4a4cc9", "#4a4cc8", "#4a4cc8", "#4a4bc8", "#4a4bc8", "#4a4bc7", \
       "#4a4ac7", "#4a4ac7", "#4a4ac7", "#4a4ac6", "#4a49c6", "#4a49c6", \
       "#4a49c6", "#4a48c5", "#4a48c5", "#4a48c5", "#4a47c5", "#4a47c5", \
       "#4a47c4", "#4a46c4", "#4a46c4", "#4a46c4", "#4a46c3", "#4a45c3", \
       "#4a45c3", "#4a45c3", "#4a44c2", "#4a44c2", "#4a44c2", "#4a43c2", \
       "#4a43c1", "#4a43c1", "#4a43c1", "#4a42c1", "#4a42c0", "#4a42c0", \
       "#4a41c0", "#4a41c0", "#4a41c0", "#4a40bf", "#4a40bf", "#4b40bf", \
       "#4b40bf", "#4b3fbe", "#4b3fbe", "#4b3fbe", "#4b3ebe", "#4b3ebd", \
       "#4b3ebd", "#4b3ebd", "#4b3dbd", "#4b3dbc", "#4b3dbc", "#4b3cbc", \
       "#4b3cbc", "#4b3cbb", "#4b3bbb", "#4b3bbb", "#4b3bbb", "#4b3bba", \
       "#4b3aba", "#4b3aba", "#4b3aba", "#4b39ba", "#4b39b9", "#4b39b9", \
       "#4b39b9", "#4b38b9", "#4b38b8", "#4b38b8", "#4b37b8", "#4b37b8", \
       "#4b37b7", "#4b37b7", "#4b36b7", "#4b36b7", "#4b36b6", "#4b35b6", \
       "#4b35b6", "#4c35b6", "#4c35b5", "#4c34b5", "#4c34b5", "#4c34b5", \
       "#4c33b4", "#4c33b4", "#4c33b4", "#4c33b4", "#4c32b3", "#4c32b3", \
       "#4c32b3", "#4c32b3", "#4c31b3", "#4c31b2", "#4c31b2", "#4c30b2", \
       "#4c30b2", "#4c30b1", "#4c30b1", "#4c2fb1", "#4c2fb1", "#4c2fb0", \
       "#4d2eb0", "#4d2eb0", "#4d2eb0", "#4d2eaf", "#4d2daf", "#4d2daf", \
       "#4d2daf", "#4d2dae", "#4d2cae", "#4d2cae", "#4d2cae", "#4d2cad", \
       "#4d2bad", "#4d2bad", "#4d2bad", "#4d2aac", "#4d2aac", "#4d2aac", \
       "#4d2aac", "#4e29ab", "#4e29ab", "#4e29ab", "#4e29ab", "#4e28aa", \
       "#4e28aa", "#4e28aa", "#4e28aa", "#4e27a9", "#4e27a9", "#4e27a9", \
       "#4e27a9", "#4e26a8", "#4e26a8", "#4e26a8", "#4f26a8", "#4f25a7", \
       "#4f25a7", "#4f25a7", "#4f25a7", "#4f24a6", "#4f24a6", "#4f24a6", \
       "#4f24a6", "#4f23a5", "#4f23a5", "#4f23a5", "#4f23a5", "#4f22a4", \
       "#5022a4", "#5022a4", "#5022a4", "#5021a3", "#5021a3", "#5021a3", \
       "#5021a3", "#5020a2", "#5020a2", "#5020a2", "#5020a1", "#501fa1", \
       "#511fa1", "#511fa1", "#511fa0", "#511ea0", "#511ea0", "#511ea0", \
       "#511e9f", "#511d9f", "#511d9f", "#511d9f", "#511d9e", "#521d9e", \
       "#521c9e", "#521c9e", "#521c9d", "#521c9d", "#521b9d", "#521b9d", \
       "#521b9c", "#521b9c", "#521a9c", "#531a9b", "#531a9b", "#531a9b", \
       "#531a9b", "#53199a", "#53199a", "#53199a", "#53199a", "#531999", \
       "#531899", "#541899", "#541899", "#541898", "#541798", "#541798", \
       "#541797", "#541797", "#541797", "#551697", "#551696", "#551696", \
       "#551696", "#551696", "#551595", "#551595", "#551595", "#551594", \
       "#551594", "#551594", "#551593", "#551593", "#551593", "#551592", \
       "#551592", "#551592", "#551591", "#551591", "#551591", "#551590", \
       "#551590", "#551590", "#55158f", "#55158f", "#55158f", "#55158e", \
       "#55158e", "#55158e", "#55158d", "#55158d", "#54158c", "#54158c", \
       "#54158c", "#54158b", "#54158b", "#54158b", "#54158a", "#54158a", \
       "#54158a", "#541589", "#541589", "#541589", "#541588", "#541588", \
       "#541588", "#541587", "#541587", "#541586", "#541586", "#541586", \
       "#541585", "#541585", "#541585", "#541584", "#541584", "#541584", \
       "#541583", "#541583", "#541583", "#551582", "#551582", "#551581", \
       "#551581", "#551581", "#551580", "#551580", "#551580", "#55157f", \
       "#55167f", "#55167e", "#55167e", "#55167e", "#55167d", "#55167d", \
       "#55167d", "#55167c", "#55167c", "#55167b", "#55167b", "#55167b", \
       "#56167a", "#56167a", "#56167a", "#561679", "#561679", "#561678", \
       "#561778", "#561778", "#561777", "#561777", "#561777", "#561776", \
       "#571776", "#571775", "#571775", "#571775", "#571774", "#571774", \
       "#571773", "#571873", "#571873", "#581872", "#581872", "#581871", \
       "#581871", "#581871", "#581870", "#581870", "#59186f", "#59196f", \
       "#59196f", "#59196e", "#59196e", "#59196d", "#5a196d", "#5a196d", \
       "#5a196c", "#5a196c", "#5a1a6b", "#5a1a6b", "#5b1a6b", "#5b1a6a", \
       "#5b1a6a", "#5b1a69", "#5b1a69", "#5c1b68", "#5c1b68", "#5c1b68", \
       "#5c1b67", "#5c1b67", "#5d1b66", "#5d1b66", "#5d1c66", "#5d1c65", \
       "#5d1c65", "#5e1c64", "#5e1c64", "#5e1c63", "#5e1d63", "#5f1d63", \
       "#5f1d62", "#5f1d62", "#5f1d61", "#601d61", "#601e60", "#601e60", \
       "#611e5f", "#611e5f", "#611e5f", "#611f5e", "#621f5e", "#621f5d", \
       "#621f5d", "#631f5c", "#63205c", "#63205b", "#64205b", "#64205b", \
       "#64205a", "#65215a", "#652159", "#652159", "#662158", "#662258", \
       "#662257", "#672257", "#672256", "#682356", "#682356", "#682355", \
       "#692355", "#692454", "#6a2454", "#6a2453", "#6a2453", "#6b2552", \
       "#6b2552", "#6c2551", "#6c2651", "#6d2650", "#6d2650", "#6d264f", \
       "#6e274f", "#6e274e", "#6f274e", "#6f284d", "#70284d", "#70284c", \
       "#71294c", "#71294c", "#72294b", "#72294b", "#732a4a", "#732a4a", \
       "#742b49", "#742b49", "#752b48", "#762c48", "#762c47", "#772c47", \
       "#772d46", "#782d46", "#782d45", "#792e45", "#7a2e44", "#7a2f43", \
       "#7b2f43", "#7b2f42", "#7c3042", "#7d3041", "#7d3041", "#7e3140", \
       "#7f3140", "#7f323f", "#80323f", "#81333e", "#81333e", "#82333d", \
       "#83343d", "#84343c", "#84353c", "#85353b", "#86363b", "#86363a", \
       "#87373a", "#883739", "#893838", "#8a3838", "#8a3937", "#8b3937", \
       "#8c3a36", "#8d3a36", "#8e3b35", "#8e3b35", "#8f3c34", "#903c34", \
       "#913d33", "#923d32", "#933e32", "#943e31", "#943f31", "#953f30", \
       "#964030", "#97412f", "#98412e", "#99422e", "#9a422d", "#9b432d", \
       "#9c442c", "#9d442c", "#9e452b", "#9f452a", "#a0462a", "#a14729", \
       "#a24729", "#a34828", "#a44928", "#a54927", "#a64a26", "#a74b26", \
       "#a94b25", "#aa4c25", "#ab4d24", "#ac4d23", "#ad4e23", "#ae4f22", \
       "#af4f22", "#b15021", "#b25120", "#b35220", "#b4521f", "#b5531f", \
       "#b7541e", "#b8551d", "#b9551d", "#bb561c", "#bc571c", "#bd581b", \
       "#be591a", "#c0591a", "#c15a19", "#c25b18", "#c45c18", "#c55d17", \
       "#c75e17", "#c85e16", "#c95f15", "#cb6015", "#cc6114", "#ce6213", \
       "#cf6313", "#d16412", "#d26511", "#d46611", "#d56610", "#d767f", \
       "#d968f", "#da69e", "#dc6ae", "#dd6bd", "#df6cc", "#e16dc", "#e26eb", \
       "#e46fa", "#e670a", "#e7719", "#e9728", "#eb738", "#ed747", "#ee756", \
       "#f0776", "#f2785", "#f4794", "#f67a3", "#f77b3", "#f97c2", "#fb7d1", \
       "#fd7e1", "#ff800"]
       colors.reverse()
       return colors
