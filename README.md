# Interactive Sketchmap Visualizer

The code to generate Interactive Sketchmap visualizer using bokeh. 
To see an demo version try : https://sketchmap.herokuapp.com/
To know about sketchmap go to http://sketchmap.org/



# Usage

 bokeh serve example-app --show --args -u 1:2:3 -ps 10 
 
 It means start bokeh server to plot using the first two columns in the COLVAR file present in example-app/data/ folder. Use 3rd column as color and pointsize set to 10.  

To use your own data you have to do the following 

```
cp -r example-app  <your-app>
cp <SMAP-DATA-FILE> <your-app>/data/COLVAR
rm -f <your-app>/static/xyz/*
cp <your-xyz-files> <your-app>/static/xyz/
```

SMAP-DATA-FILE should be formatted according to the following schema

```
Column-Name-1 Coulumn-Name-2  ... ... ...
data11         data12         ... ... ...
  :              : 
  :              :
  :              :
```

The xyz files need to follow the name convention: set.0000.xyz set.0001.xyz .....


you can also add user-defined jmol settings by adding -jmol "<jmol settings>"
 eg.

```
bokeh  serve MAPbI --show  --args -u 1:2:4 -ps 10 -jmol "connect 1.0 1.2 (carbon) (hydrogen) SINGLE CREATE ; connect 1.0 1.2 (nitrogen) (hydrogen) SINGLE CREATE ; connect 1.0 4.2 (carbon) (nitrogen) SINGLE CREATE ; connect 3.0 6 (phosphorus) (iodine) SINGLE CREATE ; set perspectiveDepth OFF " 
```

# Dependencies

argparse

tornado==4.4.3

numpy

bokeh==0.12.5

pandas
