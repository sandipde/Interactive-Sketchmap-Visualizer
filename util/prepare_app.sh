#!/bin/bash
# USAGE: ./util/prepare_app.sh app-base newapp mydata-for-plot my-traj.xyz 
appbase=$1
app=$2
data=$3
xyz=$4

cp -r ${appbase} ${app} 
gfortran ${appbase}/../util/split_xyz.f90 -o split 
cd ${app}/static/xyz/
../../../split < ../../../${xyz}  ;cd ../../../
rm -f split
cp ${data} ${app}/data/COLVAR 
zip -r static-offline.zip ${app}/static/
mv static-offline.zip ${app}/static/ 
bokeh serve ${app} --show


