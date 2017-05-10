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
                     calcium,
                     clocks,
                     inject_func,
                     tables,
                     plastic_synapse,
                     logutil,
                     util,
                     standard_options,
                     constants)
from spspine import d1d2
from spspine.graph import plot_channel, neuron_graph, spine_graph

option_parser = standard_options.standard_options()
param_sim = option_parser.parse_args()
d1d2.calYN=1
logging.basicConfig(level=logging.INFO)
log = logutil.Logger()
param_sim.hsolve=True
#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines
MSNsyn,neuron= cell_proto.neuronclasses(d1d2)
#If calcium and synapses created, could test plasticity at a single synapse in syncomp
if d1d2.synYN:
    plas,stimtab=plastic_synapse.plastic_synapse(d1d2, param_sim.syncomp, MSNsyn, param_sim.stimtimes)
else:
    plas = {}

####---------------Current Injection
all_neurons={}
for ntype in neuron.keys():
    all_neurons[ntype]=list([neuron[ntype].path])
pg=inject_func.setupinj(d1d2, param_sim.injection_delay, param_sim.injection_width, all_neurons)

###############--------------output elements
if param_sim.plot_channels:
    for chan in d1d2.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      d1d2.VMIN, d1d2.VMAX, d1d2.CAMIN, d1d2.CAMAX)

vmtab,catab,plastab,currtab = tables.graphtables(d1d2, neuron,
                                                 param_sim.plot_current,
                                                 param_sim.plot_current_message,
                                                 plas)
if d1d2.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(d1d2,neuron)
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in d1d2.neurontypes()]
clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve, d1d2.param_cond.NAME_SOMA)
print("simdt", param_sim.simdt, "hsolve", param_sim.hsolve)

if param_sim.hsolve and d1d2.calYN:
    calcium.fix_calcium(d1d2.neurontypes(), d1d2)

###########Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    traces, names, catraces = [], [], []
    for inj in param_sim.injection_current:
        run_simulation(injection_current=inj, simtime=param_sim.simtime)
        neuron_graph.graphs(d1d2, param_sim.plot_current, param_sim.simtime,
                            currtab,param_sim.plot_current_label, catab, plastab)
        for neurnum,neurtype in enumerate(d1d2.neurontypes()):
            traces.append(vmtab[neurnum][0].vector)
            catraces.append(catab[neurnum][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
            # In Python3.6, the following syntax works:
            #names.append(f'{neurtype} @ {inj}')
        if d1d2.spineYN:
            spine_graph.spineFig(d1d2,spinecatab,spinevmtab, param_sim.simtime)
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    neuron_graph.SingleGraphSet(catraces, names, param_sim.simtime)

    # block in non-interactive mode
    util.block_if_noninteractive()

    #End of inject loop
