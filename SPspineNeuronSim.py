# -*- coding:utf-8 -*-

######## SPspineNeuronSim.py ############
## Code to create two SP neuron classes 
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional
##      used to tune parameters and channel kinetics (but using larger morphology)

import os
os.environ['NUMPTHREADS'] = '1'
from pylab import *
import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from pprint import pprint

import moose 

import util
from SPcondParamSpine import *
from SPchanParam import *
from SynParamSpine import *
from SpineParams import *
from CaPlasParam import *
from SimParams import *
execfile('ChanGhkProtoLib.py')
execfile('PlotChannel2.py')
execfile('CaFuncSpine.py')
execfile('makeSpine.py')
execfile('CellProtoSpine.py')
execfile('SynProtoSpine.py')
execfile('CaPlasFunc.py')
execfile('injectfunc.py')
execfile('AssignClocks.py')
execfile('TestSynPlas.py')
execfile('SingleGraphs.py')
execfile('SpineGraphs.py')
try:
    from ParamOverrides import *
except ImportError:
    pass

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron,capools,synarray,spineHeads = neuronclasses(plotchan,plotpow,calcium,synYesNo,spineYesNo,ghkYesNo)
#If calcium and synapses created, could test plasticity at a single synapse in syncomp
syn,plas,stimtab=TestSynPlas(syncomp,calcium,plasYesNo,inputpath)

####---------------Current Injection
currents = util.inclusive_range(current1,current2,currinc)
pg=setupinj(delay,width)

###############--------------output elements
data = moose.Neutral('/data')

vmtab,catab,plastab,currtab = graphtables(neuron,plotplas,plotcurr,calcium,capools,currmsg)
if spineYesNo:
    spinecatab,spinevmtab=spinetabs()

########## clocks are critical
## these function needs to be tailored for each simulation
## if things are not working, you've probably messed up here.
simpaths=['/'+neurotype for neurotype in neurontypes]
assign_clocks(simpaths, inputpath, '/data', simdt, plotdt,hsolve)

#Make sure elements have been assigned clocks
if (showclocks):
    printclocks(clocka,clockb)

###########Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    Alltraces=[]
    for inj in currents:
        run_simulation(injection_current=inj, simtime=simtime)
        graphs(vmtab,catab,plastab,currtab,plotplas,plotcurr,calcium,currlabel)
        Alltraces.append(vmtab[0][0].vec)
        if spineYesNo:
            spineFig(spinecatab,spinevmtab)
    SingleGraphSet(Alltraces,currents)
    
    #End of inject loop
