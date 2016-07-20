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
                     clocks,
                     inject_func,
                     neuron_graph,
                     test_plas,
                     util as _util)
from spspine import param_cond, param_sim

try:
    from ParamOverrides import *
except ImportError:
    pass

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron,capools,synarray,spineHeads = cell_proto.neuronclasses(param_sim.plotchan,param_sim.plotpow,param_sim.calcium,param_sim.synYesNo,param_sim.spineYesNo,param_sim.ghkYesNo)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
if param_sim.synYesNo:
    syn,plas,stimtab=test_plas.test_plas(param_sim.syncomp,param_sim.calcium,param_sim.plasYesNo,param_sim.inpath,MSNsyn)
else:
    syn,plas = {}, {}

####---------------Current Injection
currents = _util.inclusive_range(param_sim.current1,param_sim.current2,param_sim.currinc)
pg=inject_func.setupinj(param_sim.delay,param_sim.width,neuron)

###############--------------output elements
data = moose.Neutral('/data')

vmtab,catab,plastab,currtab = neuron_graph.graphtables(neuron,param_sim.plotcurr,param_sim.currmsg,capools,plas,syn)
#if sim.spineYesNo:
#    spinecatab,spinevmtab=spinetabs()

########## clocks are critical
simpaths=['/'+neurotype for neurotype in param_cond.neurontypes()]
clocks.assign_clocks(simpaths, '/data', param_sim.simdt, param_sim.plotdt, param_sim.hsolve)

###########Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    Alltraces=[]
    for inj in currents:
        run_simulation(injection_current=inj, simtime=param_sim.simtime)
        neuron_graph.graphs(vmtab,param_sim.plotcurr,currtab,param_sim.currlabel,catab,plastab)
        Alltraces.append(vmtab[0][0].vector)
        #if param_sim.spineYesNo:
        #    spineFig(spinecatab,spinevmtab)
    neuron_graph.SingleGraphSet(Alltraces,currents)

    # block in non-interactive mode
    _util.block_if_noninteractive()

    #End of inject loop
