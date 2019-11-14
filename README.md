# Citation 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3541831.svg)](https://doi.org/10.5281/zenodo.3541831)

# Interactive Sketchmap Visualizer

    The code to generate Interactive Sketchmap visualizer using bokeh. 
    To see an demo version try : https://interactive.sketchmap.org/
    To know about sketchmap go to http://sketchmap.org/

# Getting Started

    git clone https://github.com/sandipde/Interactive-Sketchmap-Visualizer.git
    cd Interactive Sketchmap Visualizer/example
    sudo pip install jinja2 pyyaml argparse tornado==4.5.3 numpy bokeh==0.12.14 pandas selenium pillow ase
    python ../build.py  --data Arginine-Dipeptide.dat  Qm7b.dat Pyrole.dat --traj traj-Arginine-Dipeptide.xyz traj-qm7b.xyz traj-Pyrole.xyz
    bokeh serve Arginine-Dipeptide Qm7b Pyrole --show
 
# Usage Scenario 1: Build independent apps 

Independent apps are portable and contain all resources in one folder. SO if you just need to make one or two apps this is the option you want. SRCPATH= is the directory when you have cloned the repository 
                                        
        python SRCPATH/build.py --data mydatafile1.dat mydatafile2.dat mydatafile3.dat --traj my-trajectory-file1 my-trajectory-file-2 my-trajectory-file-3 

 This will set up three apps with folder name mydatafile1, mydatafile2 and mydatafile3. If you want to specify the name of the apps by yourself you can add following option to the above script.
                
         --app MYapp1 Myapp2 Myapp3 
 
 At the end of the build it will tell you how to view the apps. To view a specific app you can run 
 
        bokeh serve myapp1 --show --args -u 1:2:3 -ps 10 --jmol "Spin ON" 
 
 It means start bokeh server to plot using the first two columns in the COLVAR file present in example-app/data/ folder. Use 3rd column as color and pointsize set to 10. You are also supplying an additional jmol option. jmol options can be as complex as you want and allows for customzing the display, eg.
 
        bokeh  serve myapp --show  --args -u 1:2:4 -ps 10 -jmol "connect 1.0 1.2 (carbon) (hydrogen) SINGLE CREATE ;            connect 1.0 1.2 (nitrogen) (hydrogen) SINGLE CREATE ; connect 1.0 4.2 (carbon) (nitrogen) SINGLE CREATE ; connect 3.0 6 (phosphorus) (iodine) SINGLE CREATE ; set perspectiveDepth OFF " 
 
 
# Usage Scenario 2: Build Custom app server

The problem with independent apps are that they all need their own static resources. If you have multiple apps, this means that you end of having same javascript libraries multiple times and waste the server disk space. To tell the build.py script that you intend to make a server, you just need to supply one additional flag '--extserver'

             python SRCPATH/build.py --data mydatafile1.dat mydatafile2.dat mydatafile3.dat --traj my-trajectory-file1 my-trajectory-file-2 my-trajectory-file-3 --extserver
             
  At the end of the build it will tell you how to view the apps. In this case you will run the server with
  
            python server.py --app myapp1 myapp2 myapp3
  
  To get additional options run 
  
            python server.py -h


# DATA FORMATS

Datafile format containing the sketchmap and property data

     ColumnName_1 CoulumnName_2  ... ... ...

     data11         data12         ... ... ...

     :              : 
  
     :              :
  
     :              :

We support both neumerical and Categorical data. See example/Pyrole.dat for example.
The trajectory files are read through ase interface. All the formats supported by ase are naturally supported from now on.
Get the full list of supported input from https://wiki.fysik.dtu.dk/ase/ase/io/io.html
you can also add userdefined jmol settings by adding -jmol "jmol settings"
 eg.
 ```
     bokeh  serve MAPbI --show  --args -u 1:2:4 -ps 10 -jmol "connect 1.0 1.2 (carbon) (hydrogen) SINGLE CREATE ;            connect 1.0 1.2 (nitrogen) (hydrogen) SINGLE CREATE ; connect 1.0 4.2 (carbon) (nitrogen) SINGLE CREATE ; connect 3.0 6 (phosphorus) (iodine) SINGLE CREATE ; set perspectiveDepth OFF " 
```


# Known Issues
    The data file coloumn names should not contain wild characters. 
    For safety only use "_" as separator eg . atomic_energy

# Dependencies

Work with both Python 2.7 and 3.3  
Building dependency 

        argparse
        pyyaml
        tornado==4.5.3
        numpy
        bokeh==0.12.14
        pandas
        jinja2
        selenium
        pillow
        ase

  Runtime Dependency 
  
        argparse
        tornado==4.5.3
        numpy
        bokeh==0.12.14
        pandas
        jinja2

  
