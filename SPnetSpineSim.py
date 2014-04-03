# -*- coding:utf-8 -*-

######## SPnetSpineSim.py ############
"""\
Code to create SP neuron using dictionaries for channels and synapses

This allows multiple channels to be added with minimal change to the code
Can use ghk for calcium permeable channels if ghkYesNo=1
Optional calcium concentration in compartments (calcium=1)
Optional synaptic plasticity based on calcium (plasyesno=1)
Spines are optional (spineYesNo=1), but not allowed for network
The graphs won't work for multiple spines per compartment
Assumes spine head has name 'head', cell body called 'soma',
Also assumes that single neuron element tree is '/neurtype/compartment', and
network element tree is '/network/neurtype/compartment'
"""
from __future__ import print_function, division

import os
os.environ['NUMPTHREADS'] = '1'
from pylab import *
import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from pprint import pprint

import moose 

import util
from util import execfile
from SPcondParamSpine import *
from SPchanParam import *
from SynParamSpine import *
from SpineParams import *
from CaPlasParam import *
from NetParams import *
from SimParams import *
execfile('ChanGhkProtoLib.py')
execfile('CaFuncSpine.py')
execfile('SynProtoSpine.py')
execfile('makeSpine.py')
execfile('CellProtoSpine.py')
execfile('CaPlasFunc.py')
execfile('injectfunc.py')
execfile('CreateNetwork.py')
execfile('PopFuncsSpine.py')
execfile('ExtConnSpine.py')
execfile('AssignClocks.py')
execfile('PlotChannel2.py')
execfile('NetgraphSpine.py')
execfile('NetOutput.py')
#################################-----------create the model

##create 2 neuron prototypes with synapses and calcium
MSNsyn,neuron,capools,synarray,spineHeads=neuronclasses(plotchan,plotpow,calcium,synYesNo,spineYesNo,ghkYesNo)

MSNpop,SynPlas=CreateNetwork(inputpath,networkname,infile+'.npz',calcium,plasYesNo,single,confile,spineYesNo)

###------------------Current Injection
currents = util.inclusive_range(current1)
pg=setupinj(delay,width)

##############--------------output elements
data = moose.Neutral('/data')
if showgraphs:
    vmtab,syntab,catab,plastab,plasCumtab,spcatab,spsyntab = graphtables(single,plotnet,plotplas,calcium,spineYesNo)
else:
    vmtab=[]
#
spiketab, vmtab=SpikeTables(single,MSNpop,showgraphs,vmtab)
#
########## clocks are critical
## these function needs to be tailored for each simulation
## if things are not working, you've probably messed up here.
if single:
    simpath=['/'+neurotype for neurotype in neurontypes]
else:
    #possibly need to setup an hsolver separately for each cell in the network
    simpath=[networkname]
assign_clocks(simpath,inputpath, '/data', simdt, plotdt,hsolve)

#Make sure elements have been assigned clocks
if (showclocks):
    printclocks(clocka,clockb)

################### Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    for inj in currents:
        run_simulation(injection_current=inj, simtime=simtime)
        if showgraphs:
            graphs(vmtab,syntab,catab,plastab,plasCumtab,spcatab,graphsyn,plotplas,calcium,spineYesNo)
            plt.show()
        if not single:
            writeOutput(outfile+str(inj),spiketab,vmtab)
