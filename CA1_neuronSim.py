# -*- coding:utf-8 -*-

######## SPneuronSim.py ############
## Code to create two SP neuron classes 
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional
##      used to tune parameters and channel kinetics (but using larger morphology)

from __future__ import print_function, division
import logging

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
                     tables,
                     test_plas,
                     logutil,
                     util as _util)
from spspine import param_sim, CA1#change to CA1
from spspine.graph import plot_channel, neuron_graph

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron,capools,synarray,spineHeads = cell_proto.neuronclasses(CA1)#change all CA1 to ca1

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
if CA1.synYN:
    syn,plas,stimtab=test_plas.test_plas(CA1, param_sim.syncomp, param_sim.inpath, MSNsyn)
else:
    syn,plas = {}, {}

####---------------Current Injection
currents = _util.inclusive_range(param_sim.current1,param_sim.current2,param_sim.currinc)
pg=inject_func.setupinj(CA1, param_sim.delay,param_sim.width,neuron)

###############--------------output elements
if param_sim.plotchan:
    for chan in CA1.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plotpow, CA1.VMIN, CA1.VMAX, CA1.CAMIN, CA1.CAMAX)

data = moose.Neutral('/data')

vmtab,catab,plastab,currtab = tables.graphtables(CA1, neuron,param_sim.plotcurr,param_sim.currmsg,capools,plas,syn)
#if sim.spineYesNo:
#    spinecatab,spinevmtab=spinetabs()
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in CA1.neurontypes()]
clocks.assign_clocks(simpaths, '/data', param_sim.simdt, param_sim.plotdt, param_sim.hsolve)

###########Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    traces, names = [], []
    for inj in currents:
        run_simulation(injection_current=inj, simtime=param_sim.simtime)
        neuron_graph.graphs(CA1, vmtab,param_sim.plotcurr,currtab,param_sim.currlabel,catab,plastab)
        traces.append(vmtab[0][0].vector)
        names.append('CA1 @ {}'.format(inj))
        #if CA1.spineYN:
        #    spineFig(spinecatab,spinevmtab)
    neuron_graph.SingleGraphSet(traces, names)

    # block in non-interactive mode
    _util.block_if_noninteractive()

    #End of inject loop
