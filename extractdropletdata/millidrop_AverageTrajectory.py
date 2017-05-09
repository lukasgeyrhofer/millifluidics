#!/usr/bin/env python

import argparse
import numpy as np
import sys,math

import millidrop_dataclass as mdc

parser = argparse.ArgumentParser()
ioparser = parser.add_argument_group(description = "==== I/O parameters ====")
ioparser.add_argument("-i","--infiles",nargs="*")
ioparser.add_argument("-t","--templatefile",default=None)
ioparser.add_argument("-r","--restrictionfile",default=None)
ioparser.add_argument("-o","--outbasename",default=None)
ioparser.add_argument("-B","--splitBackForthTrajectories",default=False,action="store_true")

tparser = parser.add_argument_group(description = "==== New grid parameters ====")
tparser.add_argument("-M","--maxtime",default=None,type=float)
tparser.add_argument("-m","--mintime",default=0,type=float)
tparser.add_argument("-n","--datapoints",default=50,type=int)

aparser = parser.add_argument_group(description = "==== Algorithm parameters ====")
aparser.add_argument("-d","--stddev",default=False,action="store_true")

args = parser.parse_args()


data = mdc.DropletData(infiles = args.infiles,templatefile = args.templatefile, splitBackForthTrajectories = True)
if not args.restrictionfile is None:
    data.load_restrictions_from_file(args.restrictionfile)

for label,trajectories in data:
    n = len(trajectories)
    if n >= 1:
        if args.maxtime is None:
            maxtime = np.max([t[-1,0] for t in trajectories if len(t) >= 1])
        else:
            maxtime = args.maxtime
        timegrid        = np.linspace(start = args.mintime,stop = maxtime,num = args.datapoints)
        sumtrajectories = np.zeros((np.shape(trajectories[0])[1]-1,args.datapoints))
        if args.stddev:
            sum2trajectories = np.zeros((np.shape(trajectories[0])[1]-1,args.datapoints))
        for t in trajectories:
            if len(t) > 0:
                for i in range(1,np.shape(trajectories[0])[1]):
                    values = np.interp(timegrid,t[:,0],t[:,i])
                    sumtrajectories[i-1] += values
                    if args.stddev:
                        sum2trajectories[i-1] += values*values
            else:
                n -= 1
    if n >= 1:
        sumtrajectories /= n
        if not args.outbasename is None:
            outbasename = args.outbasename
        else:
            outbasename = ""
        outfilename = outbasename + label + ".average"
        print "{:12s}: saving average from {:d} trajectories to file '{:s}'".format(label,n,outfilename)
        np.savetxt(outfilename,np.transpose(np.concatenate([[np.array(timegrid)],sumtrajectories],axis=0)),fmt = '%.6e')
        if args.stddev:
            outfilename = outbasename + label + ".stddev"
            sum2trajectories /= n
            np.savetxt(outfilename,np.transpose(np.concatenate([[np.array(timegrid)],np.sqrt(sum2trajectories - sumtrajectories**2)],axis=0)),fmt = '%.6e')
            
        
