#!/usr/bin/env python3

import numpy as np
import argparse
import sys,math
import pickle

sys.path.append(sys.path[0] + '/..')
import growthclasses as gc


def main():
    parser = argparse.ArgumentParser()
    parser_io = parser.add_argument_group(description = "==== I/O ====")
    parser_io.add_argument("-i","--infile",required=True)
    parser_io.add_argument("-o","--baseoutfilename",default=None)
    parser_io.add_argument("-v","--verbose",action="store_true",default=False)
    parser_io.add_argument("-X","--write_xi_file",action="store_true",default=False)

    parser = gc.AddLatticeParameters(parser)
    
    args = parser.parse_args()

    g = gc.LoadGM(**vars(args))

    a1_list,a2_list = gc.getInoculumAxes(**vars(args))

    # extract data from pickle object
    m1,m2 = g.growthmatrixgrid
    gm1   = g.growthmatrix[:,:,0]
    gm2   = g.growthmatrix[:,:,1]

    mm1   = np.repeat([m1],len(m2),axis=0).T
    mm2   = np.repeat([m2],len(m1),axis=0)

    alpha = np.mean(g.growthrates)
    da    = g.growthrates[0]/alpha - 1.


    # wd = within-deme
    # compute quantities at first for each deme separately
    wd_N_fin             = np.zeros(gm1.shape,dtype=np.float)
    wd_N_ini             = np.zeros(gm1.shape,dtype=np.float)
    wd_X_fin             = np.zeros(gm1.shape,dtype=np.float)
    wd_X_ini             = np.zeros(gm1.shape,dtype=np.float)

    wd_N_fin             = gm1 + gm2
    wd_N_ini             = mm1 + mm2

    wd_X_fin[wd_N_fin>0] = (1.*gm1[wd_N_fin>0])/(1.*wd_N_fin[wd_N_fin>0])
    wd_X_ini[wd_N_ini>0] = (1.*mm1[wd_N_ini>0])/(1.*wd_N_ini[wd_N_ini>0])

    wd_dX                = wd_X_fin - wd_X_ini

    wd_Xi                = g.GetXiMatrix()
    mask                 = np.array(wd_Xi == 0)
    wd_logXi             = np.zeros(np.shape(wd_Xi))
    wd_logXi[wd_Xi > 0]  = np.log(wd_Xi[wd_Xi > 0])

    if args.write_xi_file:
        fp = open('xi.txt','w')
        for i,n1 in enumerate(m1):
            for j,n2 in enumerate(m2):
                fp.write("{} {} {}\n".format(n1,n2,wd_Xi[i,j]))
            fp.write("\n")
        fp.close()

    if not args.baseoutfilename is None:
        fp = open(args.baseoutfilename,'w')
    else:
        fp = sys.stdout

    # compute averages for all inocula given by the two axes
    for i,a1 in enumerate(a1_list):
        for j,a2 in enumerate(a2_list):
            
            inoc      = gc.TransformInoculum([a1,a2],inabs = args.AbsoluteCoordinates, outabs = True)
            
            avg_N1    = gc.SeedingAverage(gm1,       inoc)
            avg_N2    = gc.SeedingAverage(gm2,       inoc)
            avg_N1N1  = gc.SeedingAverage(gm1 * gm1, inoc)
            avg_N1N2  = gc.SeedingAverage(gm1 * gm2, inoc)

            avg_dX    = gc.SeedingAverage(wd_dX,     inoc)
            avg_X     = gc.SeedingAverage(wd_X_fin,  inoc)
            
            
            avg_nXi   = gc.SeedingAverage(wd_N_ini * wd_Xi, inoc)
            if avg_nXi > 0: omega = wd_N_ini * wd_Xi / avg_nXi
            else:           omega = 0
            
            var_N1    = avg_N1N1 - avg_N1 * avg_N1
            cov_N1N2  = avg_N1N2 - avg_N1 * avg_N2
                    
            if avg_N1 + avg_N2 > 0:
                cov_XrelN = avg_N1/(avg_N1 + avg_N2) - avg_X
            else:
                cov_XrelN = 0
            
            avg_Xi    = gc.SeedingAverage(wd_Xi,    inoc)
            avg_LogXi = gc.SeedingAverage(wd_logXi, inoc)
            
            # individual 4 terms for 2 strains in the expansion of Cov[X,N/<N>] up to O(da), weak selection limit
            avg_exp1   =      gc.SeedingAverage(wd_X_ini * (omega - 1),               inoc)
            avg_exp2   = da * gc.SeedingAverage(wd_X_ini * (omega - 1) * wd_logXi,    inoc)
            avg_exp3A  = da * gc.SeedingAverage(wd_X_ini * (2*wd_X_ini-1) * wd_logXi, inoc)
            avg_exp3B1 =      gc.SeedingAverage(wd_X_ini * omega,                     inoc)
            avg_exp3B2 =      gc.SeedingAverage((2*wd_X_ini-1) * omega * wd_logXi,    inoc)
            avg_exp3B  = da * avg_exp3B1 * avg_exp3B2
            
            # output                                                                                             1   2   3       4          5         6         7                      8       9      
            fp.write("{:14.6e} {:14.6e} {:14.6e} {:14.6e} {:14.6e} {:14.6e} {:14.6e} {:14.6e} {:14.6e}\n".format(a1, a2, avg_dX, cov_XrelN, avg_exp1, avg_exp2, avg_exp3A - avg_exp3B, avg_Xi, avg_LogXi))
        fp.write("\n")

    if not args.baseoutfilename is None:
        fp.close()


if __name__ == "__main__":
    main()
