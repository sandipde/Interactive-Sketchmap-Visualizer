# -*- coding: utf-8 -*-
from bokeh.io import curdoc
import argparse
import os
from app import bkapp
from os.path import dirname, join
global lay
appname=os.path.basename(dirname(__file__))
parser = argparse.ArgumentParser(description="A python script to generate interactive web graphics using bokeh")
parser.add_argument("-smapdata", default='COLVAR',help="The name of the data file to use in data directory")
parser.add_argument("-u",  type=str, default='1:2:3',help="columns of the data file to plot eg. -u 1:2:3:4 to plot 1st column vs 2nd column. color the data using 3rd coloumn and 4th column to varry the point size (optional)")
parser.add_argument("-ps",  type=float, default='10',help="point size")
parser.add_argument("-jmol",  type=str, default=" ",help="optional: parameters to be used for jmol")
#parser.add_argument("-t",  type=str, default='',help="Title of the plot")
args = parser.parse_args()
pcol = list(map(int,args.u.split(':')))
server_static_root=appname
lay=bkapp(dfile='COLVAR',pcol=pcol,app_name=appname,pointsize=args.ps,jmol_settings=args.jmol,server_static_root=appname)
curdoc().add_root(lay)
curdoc().template_variables["js_files"] = [server_static_root+"/static/jmol/JSmol.min.js"]
css=[]
for f in ["w3","introjs"]:
  css.append(server_static_root+"/static/css/"+f+'.css')
curdoc().template_variables["css_files"] = css
curdoc().template_variables["appname"] = [appname]
curdoc().template_variables["jmolsettings"] = args.jmol
curdoc().title = "Interactive Sketchmap Visualizer"
