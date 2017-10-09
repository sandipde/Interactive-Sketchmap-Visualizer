# Interactive Sketchmap Visualizer

The code to generate Interactive Sketchmap visualizer using bokeh. 
To see an demo version try : https://sketchmap.herokuapp.com/
To know about sketchmap go to http://sketchmap.org/

# Getting Started

cd Interactive Sketchmap Visualizer

./util/prepare_app.sh app-base app-name data-to-plot xyz-trajectory-file

See build-app-example folder for a working example 
 
# Usage

 bokeh serve example-app --show --args -u 1:2:3 -ps 10 
 
 It means start bokeh server to plot using the first two columns in the COLVAR file present in example-app/data/ folder. Use 3rd column as color and pointsize set to 10.  


SMAP-DATA-FILE format

Column-Name-1 Coulumn-Name-2  ... ... ...

data11         data12         ... ... ...

  :              : 
  
  :              :
  
  :              :


you can also add uderdefined jmol settings by adding -jmol "jmol settings"
 eg.
bokeh  serve MAPbI --show  --args -u 1:2:4 -ps 10 -jmol "connect 1.0 1.2 (carbon) (hydrogen) SINGLE CREATE ; connect 1.0 1.2 (nitrogen) (hydrogen) SINGLE CREATE ; connect 1.0 4.2 (carbon) (nitrogen) SINGLE CREATE ; connect 3.0 6 (phosphorus) (iodine) SINGLE CREATE ; set perspectiveDepth OFF " 

# Known Issues
You need python 2.7 Python 3 is not supported yet 

The data file coloumn names should not contain wild characters. For safety only use "_" as separator eg . atomic_energy

# Dependencies

argparse

tornado==4.4.3

numpy

bokeh==0.12.5

pandas
