#!/usr/bin/env python3

import argparse
import numpy as np
import sys,math

import growthclasses as gc

parser = argparse.ArgumentParser()
parser = gc.AddGrowthParameters(parser,dilution=True)
parser.add_argument("-m","--maxN",type=int,default=10)
args   = parser.parse_args()

g                         = gc.GrowthDynamics(**vars(args))
m                         = np.arange(args.maxN)
fp                        = g.getSingleStrainFixedPointsPoissonSeeding(size = args.maxN)
px,dpx                    = gc.PoissonSeedingVectors(m,fp,diff=True)

growth1_ICm1,growth2_ICm1 = g.getGrowthMatrix(size=(m,np.array([0,1])))
growth1_IC1m,growth2_IC1m = g.getGrowthMatrix(size=(np.array([0,1]),m))
invasiongrowth1           = g.Growth([fp[0],1])
invasiongrowth2           = g.Growth([1,fp[1]])

Egrowth1_ICm1             = np.dot(growth1_ICm1[:,1],px[0])
Egrowth1_IC1m             = np.dot(growth1_IC1m[1,:],px[0])
Egrowth2_ICm1             = np.dot(growth2_ICm1[:,1],px[1])
Egrowth2_IC1m             = np.dot(growth2_IC1m[1,:],px[1])
                          
gamma1inv1                = invasiongrowth1[0]/fp[0]
gamma2inv1                = invasiongrowth1[1]/fp[1]
gamma1inv2                = invasiongrowth2[0]/fp[0]
gamma2inv2                = invasiongrowth2[1]/fp[1]

print("{:f} {:f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f}".format(g.growthrates[1]/g.growthrates[0],g.yieldfactors[1]/g.yieldfactors[0],fp[0],fp[1],Egrowth1_ICm1,Egrowth2_ICm1,Egrowth1_IC1m,Egrowth2_IC1m,invasiongrowth1[0],invasiongrowth1[1],invasiongrowth2[0],invasiongrowth2[1],gamma1inv1,gamma2inv1,gamma1inv2,gamma2inv2))
