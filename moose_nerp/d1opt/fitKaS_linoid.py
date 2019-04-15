#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 16:01:33 2018

@author: dandorman
"""

import numpy as np
from matplotlib import pyplot as plt
import scipy.optimize


## Fit KAs parameters to Wolf et al 2005
## Original experiment is Shen 2004, but Wolf model states that via personal
## correspondance with author on Shen 2004, parameters in Shen 2004 were 
## published incorrectly, and gives corrected parameters.

# voltage iterations (mV)
v = np.linspace(-140,60,1000)


##### Wolf Parameters ######:
vmh = -27.0
vmc = -16.
vhh = -33.5	
vhc = 21.5
hshift = 0.0

xInfWolf = 1./(1.+(np.exp((v - vmh)/vmc)))
yInfWolf = 0.996*1./(1.+(np.exp((v - vhh - hshift)/vhc)))+(1.-0.996)

plt.figure()
plt.plot(v,xInfWolf,label='xInf-Wolf')
plt.plot(v,yInfWolf,label='yInf-Wolf')
plt.legend()

plt.figure()
xTauWolf = 3.4  +  89.2 * np.exp( -1.* ((v - -34.3)/30.1)**2 )
xTauWolf = xTauWolf/3.

left = 1. * np.exp( -(v - -0.96 - -90)/29.01 )
right = 1. * np.exp( (v- -0.96 - -90)/100 )
yTauWolf = 9876.6 / ( left + right ) / 3.

plt.plot(v,xTauWolf,label='xTauWolf')
plt.plot(v,yTauWolf,label='yTauWolf')

### Function used by fit to fit Linoid form of alpha/beta equations to 
### steady statey/tau
def alphabetafunction(X):
    #Linoid form only:
    arate,avhalf,avslope,brate,bvhalf,bvslope,=X
    aB = -arate/avhalf
    aC=-1
    bB=-brate/bvhalf
    bC=-1
    taumin=0
    ## General Form:
    alpha = (arate + aB * v) / (aC + np.exp((v + avhalf) / avslope))
    beta = (brate + bB * v) / (bC + np.exp((v + bvhalf) / bvslope))
    tau = taumin + (1.0/(alpha+beta))
    ss = alpha/(alpha+beta)
    return alpha, beta, tau,ss
### Fitting function to optimize alpha/beta parameters given in X:
def fit(X,*args):
    ssfit,taufit = args
    alpha, beta, tau, ss = alphabetafunction(X)
    tauerror = (tau-taufit)/np.max(taufit)
    sserror=(ss-ssfit)/np.max(ssfit)
    taurms = np.sqrt(np.mean(tauerror**2))
    ssrms = np.sqrt(np.mean(sserror**2))
    error=taurms+4.0*ssrms
    return error

### Parameter boundaries for fitting function:
ratebound=(-20000000,200000000.)
bbound=(-20000000000,20000000000)
vhalfbound=(-30000,30000)
vslopebound=(-20000,20000)
bounds=[ratebound,vhalfbound,vslopebound]*2

#### Fitting Function, passing yInf/yTau equations to fit yGate:
#resY=scipy.optimize.differential_evolution(fit,bounds,args=(yInfWolf,yTauWolf),tol=1e-15,maxiter=20000)#,mutation=1.9,seed=12,popsize=60,recombination=0.2)
#
## Get best alpha,beta,tau,and ss values using the outcome of fitting procedure:
#alpha,beta,tau,ss = alphabetafunction(resY.x)
#
## Compare the fit
#plt.figure()
#ax = plt.subplot(1,2,1)
#plt.plot(v,yInfWolf,label='YinfWolf')
#plt.plot(v,ss,label='ssfit')
#plt.legend()
#ax = plt.subplot(1,2,2)
#plt.plot(v,yTauWolf,label='YTauWolf',marker='.')
#plt.plot(v,tau,label='taufit')
#plt.legend()


### Fitting Function, passing xInf/xTau equations to fit xGate:
resX=scipy.optimize.differential_evolution(fit,bounds,args=(xInfWolf,xTauWolf),tol=1e-15,maxiter=20000)#,mutation=1.9,seed=12,popsize=60,recombination=0.2)

# Get best alpha,beta,tau,and ss values using the outcome of fitting procedure:
alphaX,betaX,tauX,ssX = alphabetafunction(resX.x)

#Compare the fit
plt.figure()
ax = plt.subplot(1,2,1)
plt.plot(v,xInfWolf,label='XinfWolf')
plt.plot(v,ssX,label='ssfit')
plt.legend()
ax = plt.subplot(1,2,2)
plt.plot(v,xTauWolf,label='XTauWolf',marker='.')
plt.plot(v,tauX,label='taufit')
plt.legend()
