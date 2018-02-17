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

    def bkplot(self,x,y,color='None',radii='None',ps=20,minps=0,alpha=0.8,pw=600,ph=400,palette='Inferno256',style='smapstyle',Hover=True,title='',table=False,table_width=600, table_height=150,add_colorbar=True,Periodic_color=False,return_datasrc=False,frac_load=1.0,marker=['circle'],**kwargs):
        from bokeh.layouts import row, widgetbox,column,Spacer
        from bokeh.models import HoverTool,TapTool,FixedTicker,Circle,WheelZoomTool
        from bokeh.models import CustomJS, Slider,Rect,ColorBar,HoverTool,LinearColorMapper, BasicTicker
        from bokeh.plotting import figure
        import bokeh.models.markers as Bokeh_markers
        from bokeh.models import ColumnDataSource, CDSView, IndexFilter
        from bokeh.palettes import all_palettes,Spectral6,Inferno256,Viridis256,Greys256,Magma256,Plasma256
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
        if palette=='cosmo':COLORS=cosmo()
        else: COLORS=locals()[palette]
        if marker[0]=='variable':marker=['circle','diamond','triangle','square','asterisk','cross','inverted_triangle']
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
        mdict={'circle':'Circle','diamond':'Diamond','triangle':'Triangle','square':'Square','asterisk':'Asterisk','cross':'Cross','inverted_triangle':'InvertedTriangle'}
        initial_circle = Circle(x='x', y='y')
        selected_circle = getattr(Bokeh_markers,mdict[marker[0]])(fill_alpha=0.7, fill_color="blue", size=ps*1.5 ,line_color="blue")
        nonselected_circle = getattr(Bokeh_markers,mdict[marker[0]])(fill_alpha=alpha*0.5,fill_color='colors',line_color='colors',line_alpha=alpha*0.5)
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
           getattr(plot,marker[0])(x,y,source=datasrc,size='radii',fill_color='colors', fill_alpha=alpha, line_color='colors',line_alpha=alpha,name="mycircle")
           renderer = plot.select(name="mycircle")
           renderer.selection_glyph = selected_circle
           renderer.nonselection_glyph = nonselected_circle
        else:
            if data[color].dtype=='object' :    # Categorical variable for colors
                grouped=data.groupby(color)
               # COLORS=Spectral[len(grouped)]
                i=0
                nc=len(COLORS)
                istep=int(nc/len(grouped))
                cat_colors=[]
                for group_item in grouped.groups.keys():
                  #  data.loc[grouped.groups[group_item],'colors']=COLORS[i]
                   # print(group_item,COLORS[i])
                    i=min(i+istep,nc-1)
                    cat_colors.append(COLORS[i])
                #colors=[ '#d53e4f', '#3288bd','#fee08b', '#99d594']
                datasrc=ColumnDataSource(data)
                view=[]
               # used_markers=[]
               # marker=['circle','diamond','triangle','square','asterisk','cross','inverted_triangle']
                #while True:
                #    for x in marker: 
                #        used_markers.append(x)
                #    if len(used_markers)>len(grouped): break
                i=0
                #print used_markers
                for group_item in grouped.groups.keys():
                    view.append(CDSView(source=datasrc, filters=[IndexFilter(grouped.groups[group_item])]))
                    cname='mycircle'+str(i)
                    #print used_markers[i]
                    try:mk=marker[i]
                    except:mk=marker[0]
                    getattr(plot,mk)(x,y,source=datasrc,size='radii',fill_color=cat_colors[i],muted_color=cat_colors[i], muted_alpha=0.2, fill_alpha=alpha,line_alpha=alpha, line_color=cat_colors[i],name=cname,legend=group_item,view=view[i])
                    selected_mk = getattr(Bokeh_markers,mdict[mk])(fill_alpha=0.7, fill_color="blue", size=ps*1.5 ,line_color="blue",line_alpha=0.7)
                    nonselected_mk = getattr(Bokeh_markers,mdict[mk])(fill_alpha=alpha*0.5,fill_color=cat_colors[i],line_color=cat_colors[i],line_alpha=alpha*0.5)
                    renderer = plot.select(name=cname)
                    renderer.selection_glyph = selected_mk
                    renderer.nonselection_glyph = nonselected_mk
                    i+=1
                plot.legend.location = "top_left"
                plot.legend.orientation = "vertical"
                plot.legend.click_policy="hide"
	    else:
                if Periodic_color: # if periodic property then generate periodic color palatte
                     blendcolor=interpolate(COLORS[-1],COLORS[0],len(COLORS)/5)
                     COLORS=COLORS+blendcolor
                groups = pd.cut(data[color].values, len(COLORS))
                c = [COLORS[xx] for xx in groups.codes]
                data['colors']=c
                datasrc=ColumnDataSource(data)
                getattr(plot,marker[0])(x,y,source=datasrc,size='radii',fill_color='colors', fill_alpha=alpha, line_color='colors',line_alpha=alpha,name="mycircle")
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

def cosmo():
    color=['#ff8000', '#fb7d02', '#f87b04', '#f57906', '#f17708', '#ee750a', '#eb730d', '#e8710f', '#e46f11', '#e16d13', '#de6b15', '#da6918', '#d7671a', '#d4651c', '#d1631e', '#cd6120', '#ca5f23', '#c75d25', '#c45b27', '#c05929', '#bd572b', '#ba552e', '#b65330', '#b35132', '#b04f34', '#ad4d36', '#a94a39', '#a6483b', '#a3463d', '#a0443f', '#9c4241', '#994044', '#963e46', '#923c48', '#8f3a4a', '#8c384c', '#89364f', '#853451', '#823253', '#7f3055', '#7c2e57', '#782c5a', '#752a5c', '#72285e', '#6e2660', '#6b2462', '#682265', '#652067', '#611e69', '#5e1c6b', '#5b1a6d', '#581870', '#571871', '#571972', '#571974', '#561a75', '#561a76', '#561b78', '#561b79', '#551c7a', '#551d7c', '#551d7d', '#551e7f', '#541e80', '#541f81', '#541f83', '#542084', '#532185', '#532187', '#532288', '#53228a', '#52238b', '#52238c', '#52248e', '#52258f', '#512590', '#512692', '#512693', '#512795', '#502796', '#502897', '#502999', '#50299a', '#4f2a9b', '#4f2a9d', '#4f2b9e', '#4f2ba0', '#4e2ca1', '#4e2da2', '#4e2da4', '#4e2ea5', '#4d2ea6', '#4d2fa8', '#4d2fa9', '#4d30ab', '#4c31ac', '#4c31ad', '#4c32af', '#4c32b0', '#4b33b1', '#4b33b3', '#4b34b4', '#4b35b6', '#4b36b6', '#4b37b7', '#4b39b8', '#4c3ab9', '#4c3cba', '#4c3dbb', '#4c3fbc', '#4d40bd', '#4d41bd', '#4d43be', '#4d44bf', '#4e46c0', '#4e47c1', '#4e49c2', '#4e4ac3', '#4f4bc4', '#4f4dc5', '#4f4ec5', '#4f50c6', '#5051c7', '#5053c8', '#5054c9', '#5055ca', '#5157cb', '#5158cc', '#515acc', '#515bcd', '#525dce', '#525ecf', '#525fd0', '#5261d1', '#5362d2', '#5364d3', '#5365d3', '#5367d4', '#5468d5', '#5469d6', '#546bd7', '#546cd8', '#556ed9', '#556fda', '#5571db', '#5572db', '#5673dc', '#5675dd', '#5676de', '#5678df', '#5779e0', '#577be1', '#577ce2', '#587ee3', '#597fe3', '#5a81e3', '#5b82e4', '#5d84e4', '#5e86e5', '#5f87e5', '#6189e6', '#628be6', '#638ce7', '#658ee7', '#668fe8', '#6791e8', '#6993e9', '#6a94e9', '#6b96ea', '#6d98ea', '#6e99eb', '#6f9beb', '#709cec', '#729eec', '#73a0ed', '#74a1ed', '#76a3ee', '#77a5ee', '#78a6ef', '#7aa8ef', '#7ba9f0', '#7cabf0', '#7eadf1', '#7faef1', '#80b0f2', '#82b2f2', '#83b3f3', '#84b5f3', '#85b6f4', '#87b8f4', '#88baf5', '#89bbf5', '#8bbdf6', '#8cbff6', '#8dc0f7', '#8fc2f7', '#90c3f8', '#91c5f8', '#93c7f9', '#94c8f9', '#95cafa', '#97ccfa', '#98cdfb', '#99cffb', '#9bd1fc', '#9cd1fb', '#9ed2fb', '#a0d3fb', '#a2d3fb', '#a3d4fb', '#a5d5fb', '#a7d5fb', '#a9d6fa', '#aad7fa', '#acd8fa', '#aed8fa', '#b0d9fa', '#b1dafa', '#b3dafa', '#b5dbf9', '#b7dcf9', '#b9ddf9', '#baddf9', '#bcdef9', '#bedff9', '#c0dff9', '#c1e0f8', '#c3e1f8', '#c5e1f8', '#c7e2f8', '#c8e3f8', '#cae4f8', '#cce4f8', '#cee5f8', '#cfe6f7', '#d1e6f7', '#d3e7f7', '#d5e8f7', '#d7e9f7', '#d8e9f7', '#daeaf7', '#dcebf6', '#deebf6', '#dfecf6', '#e1edf6', '#e3edf6', '#e5eef6', '#e6eff6', '#e8f0f5', '#eaf0f5', '#ecf1f5', '#edf2f5', '#eff2f5', '#f1f3f5', '#f3f4f5', '#f5f5f5']
    return color
