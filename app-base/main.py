# -*- coding: utf-8 -*-
import pandas as pd
import os
import argparse
import sys
import numpy as np
from copy import copy
from bokeh.io import curdoc
from bokeh.layouts import layout,column,row
from bokeh.models.layouts import Row,Column
from bokeh.models import (
    ColumnDataSource, HoverTool, SingleIntervalTicker, Slider, Button, Label,
    CategoricalColorMapper,
)
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import ColumnDataSource, CustomJS, Rect,Spacer
from bokeh.models import HoverTool,TapTool,FixedTicker,Circle
from bokeh.models import BoxSelectTool, LassoSelectTool
from bokeh.plotting import figure
from bokeh.layouts import row, widgetbox
from bokeh.models.widgets import Select,TextInput
#from cosmo import create_plot
from os.path import dirname, join
from smaplib import *
from bokeh.events import ButtonClick
from bokeh.models.widgets import RadioGroup,RadioButtonGroup,CheckboxGroup
from bokeh.models.widgets import DataTable,TableColumn
from bokeh.embed import components
from bokeh.resources import CDN, INLINE
from bokeh.plotting import figure


def main(dfile,pcol,app_name,title='Sketch-map',pointsize=10,jmol_settings=""):
    global cv,controls,selectsrc,columns,button,slider,n,xcol,ycol,ccol,rcol,plt_name,indx,ps,jmolsettings,appname
    appname=app_name
    ps=pointsize
    jmolsettings=jmol_settings
#initialise data
    datafile=join(dirname(__file__), 'data', dfile)
    cv=smap(name=title)
    cv.read(datafile) 
    n=len(cv.data)
    columns=[i for i in cv.columns]

# set up selection options
    tcol=pcol[0]-1
    xcol = Select(title='X-Axis', value=columns[tcol], options=columns,width=50)
    xcol.on_change('value', update)
    tcol=pcol[1]-1
    ycol = Select(title='Y-Axis', value=columns[tcol], options=columns, width=50)
    ycol.on_change('value', update)
    roptions=['None']
    for option in columns: roptions.append(option)
    rcol = Select(title='Size', value='None', options=roptions,width=50)
    rcol.on_change('value', update)
    if (len(pcol)>2 ):
      tcol=pcol[2]-1
      ccol = Select(title='Color', value=columns[tcol], options=roptions,width=50)
    else:    
      ccol = Select(title='Color', value='None', options=roptions,width=50)
    ccol.on_change('value', update)
    plt_name = Select(title='Palette',width=50, value='Inferno256', options=["Magma256","Plasma256","Spectral6","Inferno256","Viridis256","Greys256"])
    plt_name.on_change('value', update)
    xm=widgetbox(xcol,width=210,sizing_mode='fixed')
    ym=widgetbox(ycol,width=210,sizing_mode='fixed')
    cm=widgetbox(ccol,width=210,sizing_mode='fixed')
    rm=widgetbox(rcol,width=210,sizing_mode='fixed')
    pm=widgetbox(plt_name,width=210,sizing_mode='fixed')
    controls = Row(xm, ym, cm,rm, pm, width=1050, sizing_mode='scale_width')

# create plot and slider

    plotpanel=create_plot()
# full layout 
    lay=layout([
        [controls],
        [plotpanel],
    ], sizing_mode='fixed')
    return lay

def create_buttons():
    global button,download_button
# Play button
    button = Button(label='► Play', button_type="success",width=60)
    button.on_click(animate)
    play_widget=widgetbox(button,width=80,height=50,sizing_mode='fixed')
    spacer = Spacer(width=300, height=50)


# Download button 
    download_button1 = Button(label="Download Minimal HTML", button_type="success", width=150 )
    download_button2 = Button(label="Download With Structures", button_type="success", width=150 )
    download_button1.js_on_event(ButtonClick, download_simple())
    download_button2.js_on_event(ButtonClick, download_extended())
    download_widget1=widgetbox(download_button1,width=200,height=50,sizing_mode='fixed')
    download_widget2=widgetbox(download_button2,width=200,height=50,sizing_mode='fixed')
    dpanel=Row(Spacer(width=170),download_widget1,Spacer(width=10),download_widget2,width=600, sizing_mode='fixed')
    return play_widget,dpanel
    
    
def create_plot():
    global cv,selectsrc,columns,button,slider,n,xcol,ycol,ccol,rcol,plt_name,indx,controls,ps,jmolsettings
# Set up main plot
    p1,p2,table=cv.bkplot(xcol.value,ycol.value,ccol.value,radii=rcol.value,palette=plt_name.value,ps=ps,minps=4,alpha=0.6,pw=700,ph=600,Hover=True,toolbar_location="above",table=True,table_height=170)

# Set up mouse selection callbacks


# The following code is very tricky to understand properly. 
# the %s are the function or variable to pass from python depending on the slider callback or mouse callback. 
# One could write 3 seperate callbacks to connect slider,jmol and mouse selection but this way it is more compact ! 
 

    code="""
       var refdata = ref.data;
       var data = source.data;
       var ind = %s ;
       Array.prototype.min = function() {
          return Math.min.apply(null, this);
          };
       var inds =ind%s;
       var xs = refdata['x'][inds];
       var ys = refdata['y'][inds];
       data['xs'] = [xs];
       data['ys'] = [ys];
       data=refdata[inds];
       source.change.emit();
       %s;
       var str = "" + inds;
       var pad = "000000";
       var indx = pad.substring(0, pad.length - str.length) + str;
       var settings= "%s" ; 
       var file= "javascript:Jmol.script(jmolApplet0," + "'set frank off; load  %s/static/xyz/set."+ indx+ ".xyz ;" + settings + "')" ;
       location.href=file;
       localStorage.setItem("indexref",indx);
       document.getElementById("p1").innerHTML = " Selected frame:"+ indx ;
       document.getElementById("info").innerHTML = "Complete Selection: " + ind  ;
       """ 

# Set up Slider
    print jmolsettings
    iold=0  
    selectsrc=ColumnDataSource({'xs': [cv.pd[xcol.value][iold]], 'ys': [cv.pd[ycol.value][iold]]})
    refsrc=ColumnDataSource({'x':cv.pd[xcol.value], 'y':cv.pd[ycol.value]})
    slider = Slider(start=0, end=n-1, value=0, step=1, title="Primary Selection", width=400)
    slider_callback=CustomJS(args=dict(source=selectsrc, ref=refsrc,slider=slider), code=code%("cb_obj.value",".toFixed(0)","",jmolsettings,appname))
    slider.js_on_change('value', slider_callback)
    slider.on_change('value', slider_update)

#set up mouse
    callback=CustomJS(
         args=dict(source=selectsrc, ref=refsrc,slider=slider), code=code%("cb_data.source['selected']['1d'].indices",".min()","slider.set('value', inds)",jmolsettings,appname))
    taptool = p1.select(type=TapTool)
    taptool.callback = callback
    p1.circle('xs', 'ys', source=selectsrc, fill_alpha=0.9, fill_color="blue",line_color='black',line_width=1, size=15,name="selectcircle")

# Draw Selection on Overview Plot
 
    p2.circle('xs', 'ys', source=selectsrc, fill_alpha=0.9, fill_color="blue",line_color='black',line_width=1, size=8,name="mycircle")
    


# layout stuffs 
    spacer1 = Spacer(width=200, height=10)
    spacer2 = Spacer(width=200, height=170)
    indx=0
    xval=cv.pd[xcol.value][indx]
    yval=cv.pd[ycol.value][indx]

#slider
    slider_widget=widgetbox(slider,width=400,height=50,sizing_mode='fixed')
    spacer = Spacer(width=300, height=50)

# create buttons 
    play_widget,download_widget=create_buttons()
    playpanel=Row(play_widget,Spacer(width=30),slider_widget)
    plotpanel=Row(Column(p1,Spacer(height=40),Row(Spacer(width=10,height=40),
                                                     download_widget)),Column(spacer1,p2,spacer2,playpanel,Spacer(height=50),table))
    
    return plotpanel

def download_extended():
    from bokeh.io import output_file,show
    from bokeh.resources import CDN, INLINE
    from bokeh.embed import file_html
    from bokeh.embed import autoload_static
    from bokeh.resources import INLINE
    from jinja2 import Template
    import jinja2
    import os,zipfile
    from shutil import copyfile
    
    global cv,indx,controls,selectsrc,xval,yval,plt_name,xcol,ycol,ccol,rcol,jmolsettings,appname
    title='Sketchmap for '+appname+ ': Colored with '+ ccol.value + ' Point Size Variation: '+rcol.value 
    p1,p2,table=cv.bkplot(xcol.value,ycol.value,ccol.value,radii=rcol.value,palette=plt_name.value,ps=10,minps=4,alpha=0.6,pw=700,ph=600,Hover=True,toolbar_location="above",table=True,table_width=550, table_height=400,title='')
    # Set up mouse selection callbacks


# The following code is very tricky to understand properly. 
# the %s are the function or variable to pass from python depending on the slider callback or mouse callback. 
# One could write 3 seperate callbacks to connect slider,jmol and mouse selection but this way it is more compact ! 
    code="""
       var refdata = ref.data;
       var data = source.data;
       var ind = %s ;
       Array.prototype.min = function() {
          return Math.min.apply(null, this);
          };
       var inds =ind%s;
       var xs = refdata['x'][inds];
       var ys = refdata['y'][inds];
       data['xs'] = [xs];
       data['ys'] = [ys];
       data=refdata[inds];
       source.change.emit();
       %s;
       var str = "" + inds;
       var pad = "000000";
       var indx = pad.substring(0, pad.length - str.length) + str;
       var settings= "%s" ; 
       var file= "javascript:Jmol.script(jmolApplet0," + "'set frank off; load  %s/static/xyz/set."+ indx+ ".xyz ;" + settings + "')" ;
       location.href=file;
       localStorage.setItem("indexref",indx);
       document.getElementById("p1").innerHTML = " Selected frame:"+ indx ;
       
       """ 

# Set up Slider
    print jmolsettings
    iold=0  
    selectsrc=ColumnDataSource({'xs': [cv.pd[xcol.value][iold]], 'ys': [cv.pd[ycol.value][iold]]})
    refsrc=ColumnDataSource({'x':cv.pd[xcol.value], 'y':cv.pd[ycol.value]})
    slider = Slider(start=0, end=n-1, value=0, step=1, title="Primary Selection", width=400)
    slider_callback=CustomJS(args=dict(source=selectsrc, ref=refsrc,slider=slider), code=code%("cb_obj.value",".toFixed(0)","",jmolsettings,appname))
    slider.js_on_change('value', slider_callback)
    slider.on_change('value', slider_update)

#set up mouse
    callback=CustomJS(
         args=dict(source=selectsrc, ref=refsrc,slider=slider), code=code%("cb_data.source['selected']['1d'].indices",".min()","slider.set('value', inds)",jmolsettings,appname))
    taptool = p1.select(type=TapTool)
    taptool.callback = callback
    p1.circle('xs', 'ys', source=selectsrc, fill_alpha=0.9, fill_color="blue",line_color='black',line_width=1, size=15,name="selectcircle")

# Draw Selection on Overview Plot
 
    p2.circle('xs', 'ys', source=selectsrc, fill_alpha=0.9, fill_color="blue",line_color='black',line_width=1, size=8,name="mycircle")
    
#    spacer1 = Spacer(width=200, height=20)
#    spacer2 = Spacer(width=200, height=170)
#    plotpanel=Row(p1,Column(spacer1,p2,spacer2,table))    

    # layout stuffs 
    spacer1 = Spacer(width=200, height=30)
    spacer2 = Spacer(width=200, height=170)
    indx=0
    xval=cv.pd[xcol.value][indx]
    yval=cv.pd[ycol.value][indx]

#slider
    slider_widget=widgetbox(slider,width=400,height=50,sizing_mode='fixed')
    spacer = Spacer(width=300, height=50)

# create buttons 
#    play_widget,download_widget=create_buttons()
    playpanel=Row(Spacer(width=80),slider_widget)
    plotpanel=Row(Column(p1,Spacer(height=40)),Column(spacer1,p2,spacer2,playpanel,Spacer(height=50),table))

       
    # Get JavaScript/HTML resources
    js, tag = autoload_static(plotpanel, INLINE, "")
    js=js.decode("utf-8") 
#    print "jS",js 
#    print "TAG",tag
#    return 
    css=[]
    for f in ["w3"]:
        css.append(appname+"/static/css/"+f+'.css')
    templateLoader = jinja2.FileSystemLoader( searchpath="./")
    templateEnv = jinja2.Environment( loader=templateLoader )
    TEMPLATE_FILE = appname+"/templates/offline-template.html"
    template = templateEnv.get_template( TEMPLATE_FILE )
    html = template.render(js_resources=js,div=tag,jmolsettings=jmolsettings,appname=appname,css_files=css,title=title)
    fbase='sketchmap_'+xcol.value+'-'+ycol.value+'-'+ccol.value+'-'+rcol.value 
    fname=appname+'/static/'+fbase+'.html'
    zname=appname+'/static/'+fbase+'.zip'
 #   fname=fbase+'.html'
    f=open(fname,'w')
    f.write(html.encode("utf-8"))
    f.close()
    
# prepare zip file from template
    if (os.path.isfile(zname)): os.remove(zname)
    copyfile(appname+'/static/static-offline.zip',zname)
    zip = zipfile.ZipFile(zname,'a')
    zip.write(fname,fbase+'.html')
    zip.write(appname+'/static/README','README')
    zip.close()
        
    return CustomJS(code="""
           alert('Extended offline html file might fail to load on your browser. Refer to README file in download for solution. ');
           window.open("%s",title="%s");
           """ % (zname,fbase))
 
def download_simple():
    from bokeh.io import output_file,show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.embed import autoload_static
    from bokeh.resources import INLINE
    from bokeh.resources import Resources
#    from jinja2 import Template
    import jinja2

    global cv,indx,controls,selectsrc,xval,yval,plt_name,xcol,ycol,ccol,rcol
    title='Sketchmap for '+appname+ ': Colored with '+ ccol.value + ' Point Size Variation: '+rcol.value
    p1,p2,table=cv.bkplot(xcol.value,ycol.value,ccol.value,radii=rcol.value,palette=plt_name.value,ps=10,
                              minps=4,alpha=0.6,pw=700,ph=600,Hover=True,toolbar_location="above",table=True,table_width=550, table_height=300,title='')
    spacer1 = Spacer(width=200, height=10)
    spacer2 = Spacer(width=200, height=20)
    plotpanel_static=Row(p1,Column(spacer1,Row(Spacer(width=200),p2),spacer2,table))
    js, tag = autoload_static(plotpanel_static, Resources(mode='inline'), "")
    js=js.decode("utf-8") 
    templateLoader = jinja2.FileSystemLoader( searchpath="./")
    templateEnv = jinja2.Environment( loader=templateLoader )
    TEMPLATE_FILE = appname+"/templates/offline-template-minimal.html"
    template = templateEnv.get_template( TEMPLATE_FILE )
    html = template.render(js_resources=js,div=tag,appname=appname,title=title)
#    html = file_html(plotpanel_static, CDN, "my plot")
    fbase='sketchmap_'+xcol.value+'-'+ycol.value+'-'+ccol.value+'-'+rcol.value
    fname=appname+'/static/'+fbase+'-minimal.html'
    f=open(fname,'w')
    f.write(html.encode("utf-8"))
    f.close()
    return CustomJS(code="""        
           window.open("%s",title="%s");
           """ % (fname,fbase))   

def animate_update():
    global indx,n
    indx = slider.value + 1
    if indx > (n-1):
        indx = 0
    slider.value = indx

def slider_update(attrname, old, new):
    global  cv,indx,selectsrc,xcol,ycol,label
    indx = slider.value
    s = ColumnDataSource(data=dict(xs=[cv.pd[xcol.value][indx]], ys=[cv.pd[ycol.value][indx]]))
    selectsrc.data=s.data 

def animate():
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        curdoc().add_periodic_callback(animate_update, 500)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(animate_update)





def update(attr, old, new):
    global cv,indx,selectsrc,xval,yval,plt_name,xcol,ycol,ccol,rcol,extended
    plotpanel=create_plot()
    slider_widget=widgetbox(slider,width=800,sizing_mode='fixed')
    lay.children[1] = plotpanel




appname=os.path.basename(dirname(__file__))
parser = argparse.ArgumentParser(description="A python script to generate interactive web graphics using bokeh")
parser.add_argument("-smapdata", default='COLVAR',help="The name of the data file to use in data directory")
parser.add_argument("-u",  type=str, default='1:2:3',help="columns of the data file to plot eg. -u 1:2:3:4 to plot 1st column vs 2nd column. color the data using 3rd coloumn and 4th column to varry the point size (optional)")
parser.add_argument("-ps",  type=float, default='10',help="point size")
parser.add_argument("-jmol",  type=str, default=" ",help="optional: parameters to be used for jmol")
#parser.add_argument("-t",  type=str, default='',help="Title of the plot")
args = parser.parse_args()
pcol = map(int,args.u.split(':'))

lay=main(dfile='COLVAR',pcol=pcol,app_name=appname,pointsize=args.ps,jmol_settings=args.jmol)
curdoc().add_root(lay)
curdoc().template_variables["js_files"] = [appname+"/static/jmol/JSmol.min.js"]
css=[]
for f in ["w3","introjs"]:
  css.append(appname+"/static/css/"+f+'.css')
curdoc().template_variables["css_files"] = css
curdoc().template_variables["appname"] = [appname]
curdoc().template_variables["jmolsettings"] = args.jmol
curdoc().title = "Interactive Sketchmap Visualizer"
