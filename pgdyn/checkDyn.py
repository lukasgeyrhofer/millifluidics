#!/usr/bin/env python3


import numpy as np
import argparse
import sys,math


class TimeIntegrator:
    # General forward integration of dynamics with Runge-Kutta method of 4th order
    def __init__(self,step = 1e-3,requiredpositive = True,initialconditions = None,dynamics = None,globaltime = 0,**kwargs):
        self.__step = step
        self.__requiredpositive = requiredpositive

        self.params = kwargs.get('params',None)
        
        if initialconditions is None:   raise ValueError
        else:                           self.x   = np.array(initialconditions)
        if dynamics is None:            raise NotImplementedError
        else:                           self.dyn = dynamics
        
        assert len(self.x) == len(self.dyn(0,self.x,self.params)), "Initial conditions and dynamics do not have identical dimensions"
            
        self.globaltime = globaltime
        
    def RungeKutta4(self,xx,tt):
        # 4th order Runge-Kutta integration scheme
        k1 = self.__step * self.dyn( tt               , xx      , self.params )
        k2 = self.__step * self.dyn( tt+self.__step/2., xx+k1/2., self.params )
        k3 = self.__step * self.dyn( tt+self.__step/2., xx+k2/2., self.params )
        k4 = self.__step * self.dyn( tt+self.__step   , xx+k3   , self.params )
        return xx + (k1+2*k2+2*k3+k4)/6.

    def IntegrationStep(self,time):
        t = 0
        while t <= time:
            self.x = self.RungeKutta4(self.x,self.globaltime + t)
            if self.__requiredpositive:
                self.x[self.x<=0]=0
            t += self.__step
        self.globaltime += time
    
    def IntegrateToZero(self,index):
        t = 0
        while self.x[index] > 0:
            self.x = self.RungeKutta4(self.x,self.globaltime + t)
            if self.__requiredpositive:
                self.x[self.x<=0]=0
            t += self.__step
        self.globaltime += t
            

    def __str__(self):
        return (" ".join(["{:14.6e}"]*len(self.x))).format(*self.x)


def notneg(a):
    if a < 0:
        return 0
    else:
        return a


def DynWithPG(time,x,params):
    # dependence on concentration of public good
    a = notneg(1+params['eps']*x[2])
    y = notneg(1+params['delta']*x[2])
    if x[1]==0:
        a = 0
        
    return np.array( [
        a * x[0],
        -a/y * x[0],
        params['kappa']*x[0]
        ])

def DynDirect(time,x,params):
    # dependence directly on population size
    a = notneg(1+params['eps']*x[0])
    y = notneg(1+params['delta']*x[0])
    if x[1]==0:
        a = 0
        
    return np.array([
        a*x[0],
        -a/y*x[0]
        ])

def DynTwoStrainWithPG(time,x,params):
    a1 = notneg(1 + params['eps']   * x[3])
    y1 = notneg(1 + params['delta'] * x[3])
    a2 = notneg(1                         )
    y2 = notneg(1 + params['delta'] * x[3])
    if x[2] == 0:
        a1 = a2 = 0
        
    return np.array([
        a1 * x[0],
        a2 * x[1],
        -a1/y1*x[0] - a2/y2*x[1],
        params['kappa'] * x[0]
        ])

def DynTwoStrainDirect(time,x,params):
    a1 = notneg(1 + params['eps']   * x[0])
    y1 = notneg(1 + params['delta'] * x[0])
    a2 = notneg(1                         )
    y2 = notneg(1 + params['delta'] * x[0])
    if x[2] == 0:
        a1 = a2 = 0
        
    return np.array([
        a1 * x[0],
        a2 * x[1],
        -a1/y1*x[0] - a2/y2*x[1]
        ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e","--epsilon",type=float,default=1e-6)
    parser.add_argument("-d","--delta",type=float,default=1e-6)
    parser.add_argument("-k","--kappa",type=float,default=1e0)
    
    parser.add_argument("-T","--maxtime",type=float,default=20)
    parser.add_argument("-t","--timestep",type=float,default=.1)
    parser.add_argument("-i","--integratetimestep",type=float,default=1e-3)
    
    args = parser.parse_args()
    
    params = {"eps":args.epsilon,"delta":args.delta,"kappa":args.kappa}

    d1 = TimeIntegrator(dynamics = DynWithPG,          step = args.integratetimestep, initialconditions = np.array([2,1e4,0]),   params = params)
    d2 = TimeIntegrator(dynamics = DynDirect,          step = args.integratetimestep, initialconditions = np.array([2,1e4]),     params = params)
    d3 = TimeIntegrator(dynamics = DynTwoStrainWithPG, step = args.integratetimestep, initialconditions = np.array([1,1,1e4,0]), params = params)
    d4 = TimeIntegrator(dynamics = DynTwoStrainDirect, step = args.integratetimestep, initialconditions = np.array([1,1,1e4]),   params = params)
    
    t = 0
    while t < args.maxtime:
        d1.IntegrationStep(args.timestep)
        d2.IntegrationStep(args.timestep)
        d3.IntegrationStep(args.timestep)
        d4.IntegrationStep(args.timestep)
        t += args.timestep
        print("{:6.2f}".format(t),d1,d2,d3,d4)
    
    
if __name__ == "__main__":
    main()


    






