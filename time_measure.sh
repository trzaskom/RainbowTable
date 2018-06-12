#!/bin/bash
for i in {1..16}
do
   mpiexec -n $i python main.py -length 7
done
