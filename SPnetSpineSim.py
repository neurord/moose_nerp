# -*- coding:utf-8 -*-

######## SPnetSpineSim.py ############
## Code to create SP neuron using dictionaries for channels and synapses
## This allows multiple channels to be added with minimal change to the code
## Can use ghk for calcium permeable channels if ghkYesNo=1
## Optional calcium concentration in compartments (calcium=1)
## Optional synaptic plasticity based on calcium (plasyesno=1)
## Spines are optional (spineYesNo=1), but not allowed for network
## The graphs won't work for multiple spines per compartment
## Assumes spine head has name 'head', cell body called 'soma',
## Also assumes that single neuron element tree is '/neurtype/compartment', and
## network element tree is '/network/neurtype/compartment'

import os
os.environ['NUMPTHREADS'] = '1'
from pylab import *
import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from string import *
from pprint import pprint

import moose 

import util
from SPcondParamSpine import *
from SPchanParam import *
from SynParamSpine import *
from SpineParams import *
from CaPlasParam import *
from NetParams import *
from SimParams import *
execfile('ChanGhkProtoLib.py')
execfile('PlotChannel2.py')
execfile('CaFuncSpine.py')
execfile('makeSpine.py')
execfile('CellProtoSpine.py')
execfile('SynProtoSpine.py')
execfile('ExtConnSpine.py')
execfile('CaPlasFunc.py')
execfile('injectfunc.py')
execfile('PopFuncsSpine.py')
execfile('AssignClocks.py')
execfile('CreateNetwork.py')

#################################-----------create the model

##create 2 neuron prototypes with synapses and calcium
[MSNsyn,neuron,pathlist,capools,synarray]=neuronclasses(plotchan,plotpow,calcium,1,spineYesNo,ghkYesNo)

###------------------Current Injection
currents = util.inclusive_range(current1)
pg=setupinj(delay,width)

##############--------------output elements
data = moose.Neutral('/data')
spiketab=[]
##spike generators created automatically for network, but not for single
if not single:
    for neur in MSNpop['cells']:
        underscore=find(neur.path,'_')
        spikenum=int(neur.path[underscore+1:])
        ntype=neur.path[underscore-2:underscore]
        sg=moose.element(neur.path+'/soma/spikegen')
        spiketab.append(moose.Table('/data/outspike%d_%s' % (spikenum,ntype)))
        print ntype,spikenum,neur.path,sg.path,spiketab[spikenum].path
        m=moose.connect(sg, 'event', spiketab[spikenum],'spike')
#
if showgraphs:
    execfile('NetgraphSpine.py')
    vmtab,syntab,catab,plastab,plasCumtab,spcatab = graphtables(single,plotnet,plotplas,calcium,spineYesNo)
#
########## clocks are critical
## these function needs to be tailored for each simulation
## if things are not working, you've probably messed up here.
if single:
    simpath=['/'+neurotype for neurotype in neurontypes]
else:
    simpath=[networkname]
assign_clocks(simpath,'/data', inputpath, simdt, plotdt,hsolve)

#Make sure elements have been assigned clocks
if (showclocks):
    printclocks(clocka,clockb)

################### Actually run the simulation
def run_simulation(injection_current, simtime):
    print u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current)
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    for inj in currents:
        run_simulation(injection_current=inj, simtime=simtime)
        if showgraphs:
            graphs(vmtab,syntab,catab,plastab,plasCumtab,spcatab,graphsyn,plotplas,calcium,spineYesNo)
            plt.show()

###################### Write the spiketable (only for the final sim) to a file
if not single:
    outvmfile='Vm'+outspikefile
    print "SPIKE FILE", outspikefile, "VM FILE", outvmfile
    outspiketab=list()
    outVmtab=list()
    for tabindex in range(len(neurontypes)):
        outspiketab.append([])
        outVmtab.append([])
        for neurname in MSNpop['pop'][tabindex]:
            underscore=find(neurname,'_')
            neurnum=int(neurname[underscore+1:])
            ntype=neurname[underscore-2:underscore]
            print neurname,"is", neurontypes[tabindex],"=",ntype,"num=",neurnum,spiketab[neurnum].path,vmtab[neurnum].path
            outspiketab[tabindex].append(insert(spiketab[neurnum].vec,0, neurnum))
            outVmtab[tabindex].append(insert(vmtab[neurnum].vec,0, neurnum))
    savez(outspikefile,D1=outspiketab[0],D2=outspiketab[1])
    savez(outvmfile,D1=outVmtab[0],D2=outVmtab[1])
