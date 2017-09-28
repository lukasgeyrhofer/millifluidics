#!/usr/bin/env python

import argparse
import numpy as np
import sys,math
import pickle

sys.path.append(sys.path[0] + '/../mixingcycles')
import growthclasses as gc
import itertools


parser = argparse.ArgumentParser()
parser_io = parser.add_argument_group(description = "Input/Output [required]")
parser_io.add_argument("-i","--infile",required = True)
parser_io.add_argument("-o","--outfile",required = True)
parser_io.add_argument("-v","--verbose",default=False,action="store_true")

parser_dilution = parser.add_argument_group(description = "Parameters for dilution values")
parser_dilution.add_argument("-D","--dilution",default=1e-5,type=float)

parser_flowmap = parser.add_argument_group(description = "Parameters for Flowmap between mixing cycles")
parser_flowmap.add_argument("-I","--initialconditions",type=float,nargs=2,default=[1,1])
parser_flowmap.add_argument("-L","--trajectorylength",type=int,default=20)

args = parser.parse_args()

try:
    g = pickle.load(open(args.infile))
except:
    raise IOError,"Could not open and load from pickle file"

if not g.hasGrowthMatrix():
    raise ValueError,"Loaded pickle instance does not contain growthmatrix"

mx,my = g.growthmatrixgrid

gm1 = g.growthmatrix[:,:,0]
gm2 = g.growthmatrix[:,:,1]

if args.verbose:
    print g.ParameterString()

x,y = args.initialconditions
for i in range(args.trajectorylength):
    px = gc.PoissonSeedingVectors(mx,x)
    py = gc.PoissonSeedingVectors(my,y)
    x = np.dot(py,np.dot(px,gm1))*dilution
    y = np.dot(py,np.dot(px,gm2))*dilution
    print >> fp,x,y
    if (x==0) and (y==0):
        break
print >> fp
fp.close()
            
