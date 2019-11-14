# -*- coding: utf-8 -*-
from __future__ import print_function
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
from bokeh.models.widgets import Select,TextInput,CheckboxButtonGroup,RangeSlider
#from cosmo import create_plot
from os.path import dirname, join
from smaplib import *
from bokeh.events import ButtonClick
from bokeh.models.widgets import RadioGroup,RadioButtonGroup,CheckboxGroup
from bokeh.models.widgets import DataTable,TableColumn
from bokeh.embed import components
from bokeh.resources import CDN, INLINE
from bokeh.plotting import figure


def bkapp(dfile,pcol,app_name,server_static_root,title='Sketch-map',pointsize=10,jmol_settings=""):
    global cv,controls,selectsrc,columns,button,slider,n,xcol,ycol,ccol,rcol,plt_name,indx,ps,jmolsettings,appname,lay,server_prefix,periodic_checkbox,pss,frac,alphas,grid,marker
    appname=app_name
    server_prefix=server_static_root
    ps=pointsize
    jmolsettings=jmol_settings
#initialise data
    datafile=join(appname, 'data', dfile)
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

    marker_options=['circle','diamond','triangle','square','asterisk','cross','inverted_triangle','variable']
    marker = Select(title='Marker', value='circle', options=marker_options,width=50)
    marker.on_change('value',update)

    periodic_checkbox=CheckboxGroup(labels=["Periodic Palette"], active=[])
    periodic_checkbox.on_change('active',update)
    
    grid=CheckboxGroup(labels=["Show Axis"], active=[0])
    grid.on_change('active',update)

    plt_name = Select(title='Palette',width=50, value='Inferno256', options=["Magma256","Plasma256","Spectral6","Inferno256","Viridis256","Greys256","cosmo"])
    plt_name.on_change('value', update)

    pss= Slider(start=0, end=50, value=ps, step=1,callback_policy='mouseup', title="Point Size", width=150)
    pss.on_change('value',update)

    frac= Slider(start=0, end=1, value=1.0, step=0.1,callback_policy='mouseup', title="Fraction Of Data Loaded", width=200)
    frac.on_change('value',update)

    alphas= Slider(start=0, end=1, value=0.75, step=0.1,callback_policy='mouseup', title="Point Alpha", width=150)
    alphas.on_change('value',update)

    xm=widgetbox(xcol,width=170,sizing_mode='fixed')
    ym=widgetbox(ycol,width=170,sizing_mode='fixed')
    cm=widgetbox(ccol,width=170,sizing_mode='fixed')
    mm=widgetbox(marker,width=170,sizing_mode='fixed')
    cp=widgetbox(periodic_checkbox,width=100,sizing_mode='fixed')
    gc=widgetbox(grid,width=100,sizing_mode='fixed')
    rm=widgetbox(rcol,width=170,sizing_mode='fixed')
    pm=widgetbox(plt_name,width=170,sizing_mode='fixed')
    psw=widgetbox(pss,width=210,height=50,sizing_mode='fixed')
    asl=widgetbox(alphas,width=210,height=50,sizing_mode='fixed')
    fw=widgetbox(frac,width=270,height=50,sizing_mode='fixed')
    controls = Column(Row(xm, ym, cm,rm, pm,mm, width=1050, sizing_mode='scale_width'),Row(gc,fw,psw,asl,cp, width=1050,sizing_mode='fixed'))

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
    global cv,selectsrc,columns,button,slider,n,xcol,ycol,ccol,rcol,plt_name,indx,controls,ps,jmolsettings,Periodic_color,pss,frac
# Set up main plot
    Periodic_color=False
    if len(periodic_checkbox.active)>0: Periodic_color=True
    style='smapstyle'
    if len(grid.active)>0: style=None
    p1,p2,table,plotdatasrc=cv.bkplot(xcol.value,ycol.value,ccol.value,radii=rcol.value,palette=plt_name.value,ps=pss.value,minps=pss.value/2.0,alpha=alphas.value,pw=700,ph=600,Hover=True,toolbar_location="above",table=True,table_height=170,Periodic_color=Periodic_color,return_datasrc=True,frac_load=frac.value,style=style,marker=[marker.value])

# Set up mouse selection callbacks


# The following code is very tricky to understand properly. 
# the %s are the function or variable to pass from python depending on the slider callback or mouse callback. 
# One could write 3 seperate callbacks to connect slider,jmol and mouse selection but this way it is more compact ! 
 

    code="""
       var refdata = ref.data;
       var data = source.data;
       var plotdata=plotsrc.data;
       var ind = %s ;
       Array.prototype.min = function() {
          return Math.min.apply(null, this);
          };
       var inds =ind%s;
       var idx = %s; //plotdata['id'][inds];
       console.log(inds);
       var xs = refdata['x'][inds];
       var ys = refdata['y'][inds];
       data['xs'] = [xs];
       data['ys'] = [ys];
       data=refdata[inds];
       source.change.emit();
       %s;
       var str = "" + idx;
       var pad = "000000";
       var indx = pad.substring(0, pad.length - str.length) + str;
       var settings= "%s" ; 
       var file= "javascript:Jmol.script(jmolApplet0," + "'set frank off; load  %s/static/%s-structures/set."+ indx+ ".xyz ;" + settings + "')" ;
       location.href=file;
       localStorage.setItem("indexref",indx);
       document.getElementById("p1").innerHTML = " Selected frame:"+ indx ;
       //document.getElementById("info").innerHTML = "Complete Selection: " + plotdata['id'][ind]  ;
       """ 

# Set up Slider
   # print (jmolsettings)
    iold=0  
    selectsrc=ColumnDataSource({'xs': [cv.pd[xcol.value][iold]], 'ys': [cv.pd[ycol.value][iold]]})
    refsrc=ColumnDataSource({'x':cv.pd[xcol.value], 'y':cv.pd[ycol.value]})
    slider = Slider(start=0, end=n-1, value=0, step=1, title="Structure id", width=400)
    slider_callback=CustomJS(args=dict(source=selectsrc, ref=refsrc,slider=slider,plotsrc=plotdatasrc), code=code%("cb_obj.value",".toFixed(0)","inds","",jmolsettings,server_prefix,appname))
    slider.js_on_change('value', slider_callback)
    slider.on_change('value', slider_update)

#set up mouse
    callback=CustomJS(
         args=dict(source=selectsrc, ref=refsrc,slider=slider,plotsrc=plotdatasrc), code=code%("plotsrc.selected['1d'].indices",".min()","plotdata['id'][inds]","slider.value=idx",jmolsettings,server_prefix,appname))
    taptool = p1.select(type=TapTool)
    taptool.callback = callback
  #  p1.add_tools(HoverTool(tooltips=None, callback=callback)) #test
    p1.circle('xs', 'ys', source=selectsrc, fill_alpha=0.9, fill_color="blue",line_color='black',line_width=1, size=15,name="selectcircle")

# Draw Selection on Overview Plot
 
    p2.circle('xs', 'ys', source=selectsrc, fill_alpha=0.9, fill_color="blue",line_color='black',line_width=1, size=8,name="mycircle")
    


# layout stuffs 
    spacer1 = Spacer(width=200, height=0)
    spacer2 = Spacer(width=200, height=190)
    indx=0
    xval=cv.pd[xcol.value][indx]
    yval=cv.pd[ycol.value][indx]

#slider
    slider_widget=widgetbox(slider,width=400,height=50,sizing_mode='fixed')
    spacer = Spacer(width=300, height=50)

# create buttons 
    play_widget,download_widget=create_buttons()
    playpanel=Row(Spacer(width=30),play_widget,Spacer(width=30),slider_widget)
    plotpanel=Row(Column(p1,Spacer(height=40),Row(Spacer(width=10,height=40),
                                                     download_widget)),Column(spacer1,p2,spacer2,playpanel,Spacer(height=10),table))
    
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
    
    global cv,indx,controls,selectsrc,xval,yval,plt_name,xcol,ycol,ccol,rcol,jmolsettings,appname,server_prefix,Periodic_color
    title='Sketchmap for '+appname+ ': Colored with '+ ccol.value + ' Point Size Variation: '+rcol.value 
    Periodic_color=False
    style='smapstyle'
    if len(grid.active)>0: style=None
    if len(periodic_checkbox.active)>0: Periodic_color=True 
    p1,p2,table,plotdatasrc=cv.bkplot(xcol.value,ycol.value,ccol.value,radii=rcol.value,palette=plt_name.value,ps=pss.value,minps=pss.value/2.,alpha=alphas.value,pw=700,ph=600,Hover=True,toolbar_location="above",table=True,table_width=550, table_height=400,title='',Periodic_color=Periodic_color,return_datasrc=True,frac_load=frac.value,style=style,marker=[marker.value])
    # Set up mouse selection callbacks


# The following code is very tricky to understand properly. 
# the %s are the function or variable to pass from python depending on the slider callback or mouse callback. 
# One could write 3 seperate callbacks to connect slider,jmol and mouse selection but this way it is more compact ! 
    code="""
       var refdata = ref.data;
       var data = source.data;
       var plotdata=plotsrc.data;
       var ind = %s ;
       Array.prototype.min = function() {
          return Math.min.apply(null, this);
          };
       var inds =ind%s;
       var idx=plotdata['id'][inds];
       var xs = refdata['x'][inds];
       var ys = refdata['y'][inds];
       data['xs'] = [xs];
       data['ys'] = [ys];
       data=refdata[inds];
       source.change.emit();
       %s;
       var str = "" + idx;
       var pad = "000000";
       var indx = pad.substring(0, pad.length - str.length) + str;
       var settings= "%s" ; 
       var file= "javascript:Jmol.script(jmolApplet0," + "'set frank off; load  %s/static/%s-structures/set."+ indx+ ".xyz ;" + settings + "')" ;
       location.href=file;
       localStorage.setItem("indexref",indx);
       document.getElementById("p1").innerHTML = " Selected frame:"+ indx ;
       
       """ 

# Set up Slider
    #print (jmolsettings)
    iold=0  
    selectsrc=ColumnDataSource({'xs': [cv.pd[xcol.value][iold]], 'ys': [cv.pd[ycol.value][iold]]})
    refsrc=ColumnDataSource({'x':cv.pd[xcol.value], 'y':cv.pd[ycol.value]})
    slider = Slider(start=0, end=n-1, value=0, step=1, title="Primary Selection", width=400)
    slider_callback=CustomJS(args=dict(source=selectsrc, ref=refsrc,slider=slider,plotsrc=plotdatasrc), code=code%("cb_obj.value",".toFixed(0)","",jmolsettings,'.',appname))
    slider.js_on_change('value', slider_callback)
    slider.on_change('value', slider_update)

#set up mouse
    callback=CustomJS(
         args=dict(source=selectsrc, ref=refsrc,slider=slider,plotsrc=plotdatasrc), code=code%("plotsrc.selected['1d'].indices",".min()","slider.value=idx",jmolsettings,'.',appname))
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
    if (sys.version_info[0] <3):js=js.decode("utf-8") #need this for python 2.7 but not python 3.3  
#    print "jS",js 
#    print "TAG",tag
#    return 
    css=[]
    for f in ["w3"]:
        css.append("./static/css/"+f+'.css')
    templateLoader = jinja2.FileSystemLoader( searchpath="./")
    templateEnv = jinja2.Environment( loader=templateLoader )
    TEMPLATE_FILE = appname+"/templates/offline-template.html"
    #print TEMPLATE_FILE
    template = templateEnv.get_template( TEMPLATE_FILE )
    html = template.render(js_resources=js,div=tag,jmolsettings=jmolsettings,appname=appname,server_prefix='.',css_files=css,title=title)
    fbase=appname+'-sketchmap_'+xcol.value+'-'+ycol.value+'-'+ccol.value+'-'+rcol.value+'-'+plt_name.value+'-f'+str(frac.value)+'-ps'+str(pss.value)+'a'+str(alphas.value)
    if Periodic_color: fbase=fbase+'_Periodic'
    fname=os.path.join(server_prefix,'static',fbase+'.html')
    zname=os.path.join(server_prefix,'static',fbase+'.zip')
 #   fname=fbase+'.html'
    if (sys.version_info[0] <3):
             f=open(fname,'w')   #python 2.7
    else:
             f=open(fname,'wb')  #python 3.3
    f.write(html.encode("utf-8"))
    f.close()
    
# prepare zip file from template
    if (os.path.isfile(zname)): os.remove(zname)
    copyfile(os.path.join(server_prefix,'static',appname+'-static-offline.zip'),zname)
    zip = zipfile.ZipFile(zname,'a')
    zip.write(fname,fbase+'.html')
#    zip.write(os.path.join(server_prefix,'static','README'),'README')
    zip.close()
        
    return CustomJS(code="""
           alert('Extended offline html file might fail to load on your browser. Refer to README file in download for solution. ');
           window.open("%s",title="%s");
           """ % (zname,fbase))
 
def create_download_simple():
    from bokeh.io import output_file,show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.embed import autoload_static
    from bokeh.resources import INLINE
    from bokeh.resources import Resources
#    from jinja2 import Template
    import jinja2

    global cv,indx,controls,selectsrc,xval,yval,plt_name,xcol,ycol,ccol,rcol,server_prefix,Periodic_color,frac,alphas,pss
    title='Sketchmap for '+appname+ ': Colored with '+ ccol.value + ' Point Size Variation: '+rcol.value
    Periodic_color=False
    style='smapstyle'
    if len(grid.active)>0: style=None
    if len(periodic_checkbox.active)>0: Periodic_color=True 
    p1,p2,table=cv.bkplot(xcol.value,ycol.value,ccol.value,radii=rcol.value,palette=plt_name.value,ps=pss.value,
                              minps=pss.value/2.,alpha=alphas.value,pw=700,ph=600,Hover=True,toolbar_location="above",table=True,table_width=550, table_height=300,title='',Periodic_color=Periodic_color,frac_load=frac.value,style=style,marker=[marker.value])
    spacer1 = Spacer(width=200, height=10)
    spacer2 = Spacer(width=200, height=20)
    plotpanel_static=Row(p1,Column(spacer1,Row(Spacer(width=200),p2),spacer2,table))
    js, tag = autoload_static(plotpanel_static, Resources(mode='inline'), "")
    if (sys.version_info[0] <3):js=js.decode("utf-8") #need this for python 2.7 but not python 3.3  
    templateLoader = jinja2.FileSystemLoader( searchpath="./")
    templateEnv = jinja2.Environment( loader=templateLoader )
    TEMPLATE_FILE = appname+"/templates/offline-template-minimal.html"
    #print TEMPLATE_FILE
    template = templateEnv.get_template( TEMPLATE_FILE )
    html = template.render(js_resources=js,div=tag,appname=appname,title=title,server_prefix=server_prefix)
#    html = file_html(plotpanel_static, CDN, "my plot")
    fbase=appname+'-sketchmap_'+xcol.value+'-'+ycol.value+'-'+ccol.value+'-'+rcol.value+'-'+plt_name.value+'-f'+str(frac.value)+'-ps'+str(pss.value)+'a'+str(alphas.value)
    if Periodic_color: fbase=fbase+'_Periodic'
    fname=os.path.join(server_prefix,'static',fbase+'-minimal.html')
#    if (os.path.isfile(fname)): os.remove(fname)
    if (sys.version_info[0] <3):
             f=open(fname,'w')   #python 2.7
    else:
             f=open(fname,'wb')  #python 3.3

    f.write(html.encode("utf-8"))
    f.close()
    return fname,fbase

def download_simple():
    return CustomJS(code="""        
           window.open("%s",title="%s");
           """ % (create_download_simple()))   

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
    global cv,indx,selectsrc,xval,yval,plt_name,xcol,ycol,ccol,rcol,extended,lay,Periodic_color
    plotpanel=create_plot()
    slider_widget=widgetbox(slider,width=800,sizing_mode='fixed')
    lay.children[1] = plotpanel


appname=os.path.basename(dirname(__file__))
parser = argparse.ArgumentParser(description="A python script to generate interactive web graphics using bokeh")
parser.add_argument("-smapdata", default='COLVAR',help="The name of the data file to use in data directory")
parser.add_argument("-u",  type=str, default='1:2:3',help="columns of the data file to plot eg. -u 1:2:3:4 to plot 1st column vs 2nd column. color the data using 3rd coloumn and 4th column to varry the point size (optional)")
parser.add_argument("-ps",  type=float, default='10',help="point size")
parser.add_argument("-jmol",  type=str, default=" ",help="optional: parameters to be used for jmol")
parser.add_argument("--extserver", action="store_true",help="need to use it if you want to generate configuration to run with externel server")
#parser.add_argument("-t",  type=str, default='',help="Title of the plot")
args = parser.parse_args()
pcol = list(map(int,args.u.split(':')))

# in standalone app mode there are now static folder inside the app-folder. We check that to determine which mode we are in.
server_static_root='.'
if os.path.exists(os.path.join(appname,'static')):server_static_root=appname

# main calling of the plot
lay=bkapp(dfile='COLVAR',pcol=pcol,app_name=appname,pointsize=args.ps,jmol_settings=args.jmol,server_static_root=server_static_root)
curdoc().add_root(lay)
curdoc().template_variables["js_files"] = [server_static_root+"/static/jmol/JSmol.min.js"]
css=[]
for f in ["w3","introjs"]:
  css.append(server_static_root+"/static/css/"+f+'.css')
curdoc().template_variables["css_files"] = css
curdoc().template_variables["appname"] = appname
curdoc().template_variables["jmolsettings"] = args.jmol
curdoc().template_variables["server_prefix"] = server_static_root
curdoc().title = "Interactive Sketchmap Visualizer"

