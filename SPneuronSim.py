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

from spspine import (cell_proto,
                     inject_func,
                     neuron_graph,
                     util as _util)
import param_sim as sim
import param_cond
import clocks
import test_plas

try:
    from ParamOverrides import *
except ImportError:
    pass

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron,capools,synarray,spineHeads = cell_proto.neuronclasses(sim.plotchan,sim.plotpow,sim.calcium,sim.synYesNo,sim.spineYesNo,sim.ghkYesNo)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
if sim.synYesNo:
    syn,plas,stimtab=test_plas.test_plas(sim.syncomp,sim.calcium,sim.plasYesNo,sim.inpath,MSNsyn)
else:
    syn,plas = {}, {}

####---------------Current Injection
currents = _util.inclusive_range(sim.current1,sim.current2,sim.currinc)
pg=inject_func.setupinj(sim.delay,sim.width,neuron)

###############--------------output elements
data = moose.Neutral('/data')

vmtab,catab,plastab,currtab = neuron_graph.graphtables(neuron,sim.plotcurr,sim.currmsg,capools,plas,syn)
#if sim.spineYesNo:
#    spinecatab,spinevmtab=spinetabs()

########## clocks are critical
simpaths=['/'+neurotype for neurotype in param_cond.neurontypes]
clocks.assign_clocks(simpaths, '/data', sim.simdt, sim.plotdt, sim.hsolve)

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
        neuron_graph.graphs(vmtab,sim.plotcurr,currtab,sim.currlabel,catab,plastab)
        Alltraces.append(vmtab[0][0].vector)
        #if sim.spineYesNo:
        #    spineFig(spinecatab,spinevmtab)
    neuron_graph.SingleGraphSet(Alltraces,currents)

    # block in non-interactive mode
    _util.block_if_noninteractive()

    #End of inject loop
