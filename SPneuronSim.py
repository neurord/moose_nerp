# -*- coding:utf-8 -*-

######## SPneuronSim.py ############
## Code to create two SP neuron classes 
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional
##      used to tune parameters and channel kinetics (but using larger morphology)

from __future__ import print_function, division

import os
os.environ['NUMPTHREADS'] = '1'
import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from pprint import pprint
import moose 

import util
import param_sim as sim
from param_cond import neurontypes
import cell_proto as cell
import clocks as clock
import inject_func as inj
import test_plas as test
import neuron_graph as graph

try:
    from ParamOverrides import *
except ImportError:
    pass

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron,capools,synarray,spineHeads = cell.neuronclasses(sim.plotchan,sim.plotpow,sim.calcium,sim.synYesNo,sim.spineYesNo,sim.ghkYesNo)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
syn,plas,stimtab=test.test_plas(sim.syncomp,sim.calcium,sim.plasYesNo,sim.inpath,MSNsyn)

####---------------Current Injection
currents = util.inclusive_range(sim.current1,sim.current2,sim.currinc)
pg=inj.setupinj(sim.delay,sim.width,neuron)

###############--------------output elements
data = moose.Neutral('/data')

vmtab,catab,plastab,currtab = graph.graphtables(neuron,sim.plotcurr,sim.currmsg,capools,plas,syn)
#if sim.spineYesNo:
#    spinecatab,spinevmtab=spinetabs()

########## clocks are critical
simpaths=['/'+neurotype for neurotype in neurontypes]
clock.assign_clocks(simpaths, '/data', sim.simdt, sim.plotdt, sim.hsolve)

###########Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    Alltraces=[]
    for inj in currents:
        run_simulation(injection_current=inj, simtime=sim.simtime)
        graph.graphs(vmtab,sim.plotcurr,currtab,sim.currlabel,catab,plastab)
        Alltraces.append(vmtab[0][0].vector)
        #if sim.spineYesNo:
        #    spineFig(spinecatab,spinevmtab)
    graph.SingleGraphSet(Alltraces,currents)

    # block in non-interactive mode
    util.block_if_noninteractive()

    #End of inject loop
