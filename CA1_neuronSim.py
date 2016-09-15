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
                     plastic_synapse,
                     logutil,
                     util as _util)
from spspine import param_sim_CA1, CA1#change to CA1
from spspine.graph import plot_channel, neuron_graph

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron,capools,synarray,spineHeads = cell_proto.neuronclasses(CA1)#change all CA1 to ca1

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
if CA1.synYN:
    syn,plas,stimtab=plastic_synapse.plastic_synapse(CA1, param_sim_CA1.syncomp, MSNsyn)
else:
    syn,plas = {}, {}

####---------------Current Injection
currents = _util.inclusive_range(param_sim_CA1.current1,param_sim_CA1.current2,param_sim_CA1.currinc)
pg=inject_func.setupinj(CA1, param_sim_CA1.delay,param_sim_CA1.width,neuron)

###############--------------output elements
if param_sim_CA1.plotchan:
    for chan in CA1.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim_CA1.plotpow, CA1.VMIN, CA1.VMAX, CA1.CAMIN, CA1.CAMAX)

data = moose.Neutral('/data')

vmtab,catab,plastab,currtab = tables.graphtables(CA1, neuron,param_sim_CA1.plotcurr,param_sim_CA1.currmsg,capools,plas,syn)
#if sim.spineYesNo:
#    spinecatab,spinevmtab=spinetabs()
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in CA1.neurontypes()]
clocks.assign_clocks(simpaths, '/data', param_sim_CA1.simdt, param_sim_CA1.plotdt, param_sim_CA1.hsolve)

###########Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    traces, names = [], []
    for inj in currents:
        run_simulation(injection_current=inj, simtime=param_sim_CA1.simtime)
        neuron_graph.graphs(CA1, vmtab,param_sim_CA1.plotcurr,currtab,param_sim_CA1.currlabel,catab,plastab)
        traces.append(vmtab[0][0].vector)
        names.append('CA1 @ {}'.format(inj))
        #if CA1.spineYN:
        #    spineFig(spinecatab,spinevmtab)
    neuron_graph.SingleGraphSet(traces, names)

    # block in non-interactive mode
    _util.block_if_noninteractive()

    #End of inject loop
