# -*- coding:utf-8 -*-

######## SPspineNeuronSim.py ############
## Code to create two SP neuron classes 
##          using dictionaries for channels and synapses
##          calcium based learning rule/plasticity function
##          spines, optionally with ion channels and synpases
## Synapses implemented to test the plasticity function
##This one should be used to tune parameters and channel kinetics (but using larger morphology)
##Presently, AHPs too deep, I don't know about spike width
##Also, fires too early with slightly higher current injection

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
from CaPlasParam import *
from SimParams import *
try:
    from ParamOverrides import *
except ImportError:
    pass
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

#################################-----------create the model
##create 2 neuron prototypes with synapses and calcium
##only create synapses to create plasticity, hence pass plasYesNo to function
MSNsyn,neuron,pathlist,capools,synarray = neuronclasses(plotchan,plotpow,calcium,synYesNo,spineYesNo,ghkYesNo)

[syn,plas,stimtab]=TestSynPlas(syncomp,calcium,plasYesNo,inputpath)

#------------------Current Injection
currents = util.inclusive_range(current1)
pg=setupinj(delay,width)

###############--------------output elements
data = moose.Neutral('/data')

execfile('SingleGraphs.py')
vmtab,catab,plastab,currtab,plaslegend = graphtables(neuron,plotplas,plotcurr,calcium,capools,currmsg)
if spineYesNo:
    spinecatab=[]
    spinevmtab=[]
    for neurtype,neurnum in zip(neurontypes,range(len(neurontypes))):
        spinecatab.append(moose.Table('/data/SpCa%s' % (neurtype)))
        spinevmtab.append(moose.Table('/data/SpVm%s' % (neurtype)))
        spname=MSNsyn[neurtype]['ampa'][1].path[0:rfind(MSNsyn[neurtype]['ampa'][1].path,'/')+1]
        spine=moose.element(spname)
        moose.connect(spinevmtab[neurnum], 'requestData', spine, 'get_Vm')
        if calcium:
            cal=moose.element(spname+caName)
            moose.connect(spinecatab[neurnum], 'requestData', cal, 'get_Ca')
#
########## clocks are critical
## these function needs to be tailored for each simulation
## if things are not working, you've probably messed up here.
assign_clocks(pathlist, inputpath, '/data', simdt, plotdt,hsolve)

#Make sure elements have been assigned clocks
if (showclocks):
    printclocks(clocka,clockb)

###########Actually run the simulation
def run_simulation(injection_current, simtime):
    print u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current)
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    for inj in currents:
        run_simulation(injection_current=inj, simtime=simtime)
        graphs(vmtab,catab,plastab,currtab,plotplas,plotcurr,plaslegend,calcium,currlabel)

    if spineYesNo:
        figure()
        t = np.linspace(0, simtime, len(spinevmtab[0].vec))
        if calcium:
            subplot(211)
        for neurnum in range(len(neurontypes)):
            plt.plot(t,spinevmtab[neurnum].vec,label=neurontypes[neurnum])
        if calcium:
            subplot(212)
            for neurnum in range(len(neurontypes)):
                plt.plot(t,spinecatab[neurnum].vec,label=neurontypes[neurnum])
        plt.legend()
        plt.show()
    #End of inject loop

    #Replace graphs with table output to files to inspection later
    #Add in comparison of results with a standard to further automate the parameter turning
