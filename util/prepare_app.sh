#!/bin/bash
app=$1
data=$2
xyz=$3

cp -r example-app $1 
rm -rf $1/static/xyz/*
cd $1/static/xyz/
gfortran ../../../util/split_xyz.f90 ; ./a.out < ../../../$3 ;rm a.out ;cd ../../../
mv $2 $1/data/COLVAR 


