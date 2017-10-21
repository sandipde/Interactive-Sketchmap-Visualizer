from  __future__ import print_function
import sys
import argparse
from setup_class import isv
import os

def main(appnames,datafiles,structure_files,extserver=False):
    if extserver: 
       apptype='server'
    else:
       apptype='stand_alone'
    libfolder=os.path.join(os.path.abspath(os.path.dirname(__file__)),'app-base')
#    print (libfolder)
    sys.path.insert(0, libfolder)
#    print (sys.path)
    print ("Number of apps to build: ", len(datafiles))
    for i in range(len(datafiles)):
       print("Building: ", appnames[i] )
       print("Datafile: ", datafiles[i] )
       print("Structure File: ", structure_files[i] )
       app=isv(appname=appnames[i],apptype=apptype)
       app.setup(datafiles[i],structure_files[i])
       print ("___________ Success !!_____________")
    if extserver : 
        print (" run: python server.py  --app ", appnames )
        print ("_______________________________________" )
    else:
        print (" run: bokeh serve ", appnames , "--show" )
        print ("_______________________________________" )

    

if __name__=='__main__':
   parser = argparse.ArgumentParser(description=""" Python Script to setup Interactive Sketchmap Visualizer  """)
   parser.add_argument("--data", nargs='+',type=str, help="Name of the files containing Sketchmap data and properties")
   parser.add_argument("--traj", nargs='+',type=str, help="Name of the trajectory files containing structures. All formats supported by ase can be used")
   parser.add_argument("--extserver",action="store_true", help="Optional argument: The setup will be done consistent to run with external server. Useful when you want to run multiple apps") 
   parser.add_argument("--app",nargs='+', type=str, help="Name of the apps you are creating")
   args = parser.parse_args()
#   try:appnames=args.app
#   except:appnames=[]
   nd=len(args.data)
   nf=len(args.traj)
   if (nd != nf): sys.exit("number of trajectory and data file mismatch")
#   try: nn=len(args.app)
#   except:
#        nn=0
   appnames=[]
   for i in range(nd):
      try: appnames.append(args.app[i])
      except: appnames.append(os.path.basename(args.data[i])[:-4])
   
   main(appnames,args.data,args.traj,args.extserver)
