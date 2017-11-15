#!/usr/bin/python
from __future__ import print_function
from jinja2 import Environment, FileSystemLoader
from tornado.web import RequestHandler,StaticFileHandler
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler, DirectoryHandler
from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
import argparse
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
import os,sys

def main(appnames,applist_file,port,allow_origin):
     env = Environment(loader=FileSystemLoader('templates'))
          
     class IndexHandler(RequestHandler):
         def get(self):
             template = env.get_template('index.html')
             #script = server_document('http://localhost:5006/app-base')
             self.write(template.render(applist=apps))
     if appnames==None:  
        print ("No appname provided on command line \n Trying to read app names from: ",applist_file) 
        try: 
           with open(applist_file) as file:
               apps = [line.strip() for line in file]
           print ("found ", len(apps)) #,sep=":")
           print (apps)
        except: sys.exit("Not found ! You need to provide appnames")
     else:
        apps=appnames
     serverlist={}
     bokeh_app=[]
     for i in range(len(apps)):
#        libfolder=os.path.join(os.path.abspath(os.path.dirname(__file__)),apps[0])
       # print (libfolder)
#        sys.path.insert(0, libfolder)
        print ("adding ",apps[i])# ,sep=":" )
        bokeh_app.append(Application(DirectoryHandler(filename=apps[i])))
        rpath='/' +str(apps[i])
        serverlist[rpath]=bokeh_app[i]
     #server = Server({'/Qm7b': bokeh_app, '/Arginine-Dipeptide':bokeh_app2 }, num_procs=1,port=5001, extra_patterns=[('/', IndexHandler),("/static", StaticFileHandler, {'path':'static/'})])
     server = Server(serverlist, num_procs=1,use_xheaders=False,port=port,allow_websocket_origin=allow_origin, extra_patterns=[('/', IndexHandler), (r"/static/(.*)", StaticFileHandler, {"path": "./static"})])
     #server = Server({'/app-base': bokeh_app }, num_procs=1, port=5001)
     server.start()
     return server
if __name__ == '__main__':
    from bokeh.util.browser import view
    parser = argparse.ArgumentParser(description="A python script to generate website containing  bokeh apps")
    parser.add_argument("--applist", default='Applist.dat',help="The name of the file containing names of apps")
    parser.add_argument("--app", nargs='+',type=str,help="The name of the apps (support multiple apps)")
    parser.add_argument("--port",type=int, default=5006,help="Port number to use")
    parser.add_argument("--allow-websocket-origin",nargs='+',type=str, default=["localhost:5006"],help="allow address pattern")
    args = parser.parse_args()
    server=main(args.app,args.applist,args.port,args.allow_websocket_origin)
    print ("Opening Tornado app with embedded Bokeh application on http://localhost:",args.port) #,sep="")
    address="http://localhost:"+str(args.port)
    server.io_loop.add_callback(view, address)
    server.io_loop.start()
