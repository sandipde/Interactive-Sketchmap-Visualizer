from __future__ import print_function
import os 
import shutil
from os.path import dirname,join
from ase.io import read,write
import argparse
import sys
from ase.io import read,write

class isv():
    def __init__(self,appname='myapp',apptype='stand_alone'):
        import os
        import sys
        currentdir=os.getcwd()        
        self.appname=appname
        self.apptype=apptype
        self.approot=os.path.dirname(__file__)
        if (currentdir==self.approot) and (apptype=='server'):
            print ("It seems you are running the code from source code directory.")
            sys.exit("Please run it from another directory.")
        print("Initializing: ", appname)
        if apptype=='stand_alone':
            rmdir_list=[appname]
      #      destdir={'static':os.path.join(appname,'static'),}
            static_path=os.path.join(appname,'static')
        else:
            rmdir_list=[appname,'templates']
            static_path='static'
        self.rmdir_list=rmdir_list
        self.static=static_path
        
        print("The following Directory will be overwritten if you continue:")
        print (self.rmdir_list)
#        if self.confirm_overwrite() :
        for dir in self.rmdir_list :
                if os.path.exists(dir): shutil.rmtree(dir,ignore_errors=True)
#                os.makedirs(dir)
    def setup(self,datafile,structure_file):
       try:
         self.setup_base()
         self.setup_static()
         self.setup_templates()            
         self.add_data(datafile)
       except:
         sys.exit("There was a problem in setting up directory structure.\nTry Running from a clean directory.")
       try:
         self.add_structures(structure_file)
       except:
         print("There was problem handling the Trajectory file. You will not have atomic structures in server")
         pass
       try:self.setup_offline_arxiv()
       except:
         print("There was a problem setting up the static archive. You will not be able to use static html download option") 
         pass
           
       if self.apptype =="server" : 
             try: self.setup_cover()
             except:print("Problem creating cover image. Your website will not look good but it will work !" )
             shutil.copy2(os.path.join(self.approot,'server.py'),'server.py')
    
    def setup_cover(self):
       from create_cover import cover
       print ("Creating Cover")
       cover(self.appname)       

    def setup_offline_arxiv(self): 
       zname=self.appname+'-static-offline'
       print("Setting up archive template:",zname)
       if not os.path.exists('.isv'):os.mkdir('.isv')
       rmpath=os.path.join('.isv','static')
       if os.path.exists(rmpath): 
          shutil.rmtree(rmpath)
       os.mkdir(rmpath)
       os.mkdir(os.path.join('.isv','static','css'))
       shutil.copy2(os.path.join(self.static,'css','w3.css'),os.path.join('.isv','static','css'))
       shutil.copytree(os.path.join(self.static,self.appname+'-structures'),os.path.join('.isv','static',self.appname+'-structures'))
       shutil.copytree(os.path.join(self.static,'jmol'),os.path.join('.isv','static','jmol'))
       shutil.copy2(os.path.join(self.static,'pop.html'),os.path.join('.isv','static'))
       shutil.copy2(os.path.join(self.static,'compare.html'),os.path.join('.isv','static'))
       shutil.copy2(os.path.join(self.static,'loading.gif'),os.path.join('.isv','static'))
  #     rmpath=os.path.join('.isv','static','js')
  #     if os.path.exists(rmpath): shutil.rmtree(rmpath)
       shutil.copy2(os.path.join(self.approot,'static','README'),os.path.join('.isv','README'))
       shutil.make_archive(os.path.join(self.static,zname),'zip','.isv')
       try: shutil.rmtree('.isv')
       except: pass


    def add_data(self,datafile):
       appname=self.appname
       os.mkdir(os.path.join(appname,'data'))
       shutil.copy2(datafile,os.path.join(appname,'data','COLVAR'))

    def add_structures(self,structure_file):
         from ase.atoms import Atoms
        # Split trajectory file separate xyz files
         static_path=self.static
         appname=self.appname
         frames = read(structure_file,index=':')
         dest=os.path.join(static_path,appname+'-structures')
         if  os.path.exists(dest): shutil.rmtree(dest)
         os.mkdir(dest)
         print ("Read ",len(frames)," frames from ", structure_file)
         print ("Splitting frames into xyz files...")
         for it,frame in enumerate(frames):
             sys.stderr.write("Writing frame no %d    \r: " %(it))
             fn = open(os.path.join(dest,'set.{:06d}.xyz'.format(it)),'w')
             symbols = Atoms(frame).get_chemical_symbols()
             natoms = len(symbols)
             comment=appname+' frame: '+str(it)
             fn.write('%d\n%s\n' % (natoms, comment))
             for s, (x, y, z) in zip(symbols, frame.positions):
                 fn.write('%-2s %12.2f %12.2f %12.2f\n' % (s, x, y, z))
         print("\nDone !")
   

    def setup_base(self):
        print("Setting up app-base: ", self.appname)
        approot=self.approot
        appname=self.appname
        os.makedirs(appname)
        for file in ['main.py','smaplib.py','theme.yaml']:
            src=os.path.join(approot,'app-base',file)
            dest=os.path.join(appname,file)
            if not os.path.exists(dest):
                shutil.copy2(src,dest)
    
    
    def setup_static(self):
        print("Setting up static:", self.static)
        # copy folder and file from app-base/static folder to static folder
        ref_static_path=os.path.join(self.approot,'static')
        static_path=self.static
        if not os.path.exists(static_path):os.mkdir(static_path)
        for dir in ['css','jmol']:
            src=os.path.join(ref_static_path,dir)
            dest=os.path.join(static_path,dir)
            if not os.path.exists(dest):      
                shutil.copytree(src,dest)

        for file in ['loading.gif','pop.html','compare.html']:
            src=os.path.join(ref_static_path,file)
            dest=os.path.join(static_path,file)
            if not os.path.exists(dest):
                shutil.copy2(src,dest)
        
        if self.apptype=='server':
            for dir in ['js']:
                src=os.path.join(self.approot,'static',dir)
                dest=os.path.join(static_path,dir)
                if not os.path.exists(dest):
                    shutil.copytree(src,dest)
       #     src=os.path.join(self.approot,'static','css')
       #     src_files = os.listdir(src)
       #     for file_name in src_files:
       #          full_file_name = os.path.join(src, file_name)
       #          dest=os.path.join(static_path,'css')
       #          if (os.path.isfile(full_file_name)):
       #             shutil.copy2(full_file_name, dest)
    
    
    def setup_templates(self):
        print("Setting up templates")
        approot=self.approot
        appname=self.appname
        src=os.path.join(approot,'app-base','templates')
        dest=os.path.join(appname,'templates')
        if not os.path.exists(dest):
                shutil.copytree(src,dest)

        if self.apptype=='server':
            src=os.path.join(approot,'templates')
            dest='templates'
            if not os.path.exists(dest):
                    shutil.copytree(src,dest)

    
    def confirm_overwrite(self):
        yes = {'yes','y', 'ye', ''}
        no = {'no','n'}
        while True:
            try:
               choice = raw_input("Continue ? [y/n]").lower()
            except: 
               choice = input().lower()
            if choice in yes:
               return True
            elif choice in no:
               return False
            else:
               sys.stdout.write("Please respond with 'yes' or 'no'")
