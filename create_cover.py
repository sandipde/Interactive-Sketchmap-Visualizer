# -*- coding: utf-8 -*-
import pandas as pd
import os
#import argparse
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
from bokeh.events import ButtonClick
from bokeh.models.widgets import RadioGroup,RadioButtonGroup,CheckboxGroup
from bokeh.models.widgets import DataTable,TableColumn
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.plotting import figure
libfolder=os.path.join(os.path.abspath(os.path.dirname(__file__)),'app-base')
sys.path.insert(0, libfolder)
from smaplib import *

def main(dfile,pcol,app_name,title='Sketch-map',pointsize=10,jmol_settings=""):
    global cv,controls,selectsrc,columns,button,slider,n,xcol,ycol,ccol,rcol,plt_name,indx,ps,jmolsettings,appname
    appname=app_name
    ps=pointsize
    jmolsettings=jmol_settings
#initialise data
    datafile=join(appname, 'data', dfile)
    cv=smap(name=title)
    cv.read(datafile) 
    n=len(cv.data)
    columns=[i for i in cv.columns]

# set up selection options

    xcol = Select(title='X-Axis', value=columns[pcol[0]-1], options=columns,width=50)
    ycol = Select(title='Y-Axis', value=columns[pcol[1]-1], options=columns, width=50)
    roptions=['None']
    for option in columns: roptions.append(option)
    rcol = Select(title='Size', value='None', options=roptions,width=50)
    ccol = Select(title='Color', value=columns[pcol[2]-1], options=roptions,width=50)
    plt_name = Select(title='Palette',width=50, value='Inferno256', options=["Magma256","Plasma256","Spectral6","Inferno256","Viridis256","Greys256"])
    xm=widgetbox(xcol,width=210,sizing_mode='fixed')
    ym=widgetbox(ycol,width=210,sizing_mode='fixed')
    cm=widgetbox(ccol,width=210,sizing_mode='fixed')
    rm=widgetbox(rcol,width=210,sizing_mode='fixed')
    pm=widgetbox(plt_name,width=210,sizing_mode='fixed')
    controls = Row(xm, ym, cm,rm, pm, width=1050, sizing_mode='scale_width')

# create plot and slider

    p1,p2=cv.bkplot(xcol.value,ycol.value,ccol.value,radii=rcol.value,palette=plt_name.value,ps=10,minps=4,alpha=0.6,pw=700,ph=600,Hover=False,toolbar_location=None,table=False,table_width=550, table_height=400,title='',add_colorbar=False)
    create_cover_image(appname,p1)

    
def create_cover_image(appname,plot):
   from bokeh.io import export_png
   # in standalone app mode there are now static folder inside the app-folder. We check that to determine which mode we are in.
   server_static_root=''
   if os.path.exists(os.path.join(appname,'static')):server_static_root=appname
   filename=os.path.join(server_static_root,'static',appname+'-cover.png')
   export_png(plot, filename=filename)  
   print ("Success: wrote: "+ filename)   
   return

#if __name__ == '__main__':

def cover(appname):
#   appname=os.path.basename(dirname(__file__))
#   parser = argparse.ArgumentParser(description="A python script to generate interactive web graphics using bokeh")
#   parser.add_argument("-smapdata", default='COLVAR',help="The name of the data file to use in data directory")
#   parser.add_argument("-u",  type=str, default='1:2:3',help="columns of the data file to plot eg. -u 1:2:3:4 to plot 1st column vs 2nd column. color the data using 3rd coloumn and 4th column to varry the point size (optional)")
#   parser.add_argument("-ps",  type=float, default='10',help="point size")
#   parser.add_argument("-jmol",  type=str, default=" ",help="optional: parameters to be used for jmol")
#   #parser.add_argument("-t",  type=str, default='',help="Title of the plot")
#   args,unknown = parser.parse_known_args()
#   pcol = list(map(int,args.u.split(':')))
#   libfolder=os.path.join(__file__,appname)
#   print libfolder
#   sys.path.insert(0, libfolder) 
   pcol=[1,2,3]
   ps=10
   main(dfile='COLVAR',pcol=pcol,app_name=appname,pointsize=ps,jmol_settings='')
   return

if __name__=='__main__' :
     import sys
     cover(sys.argv[1])
