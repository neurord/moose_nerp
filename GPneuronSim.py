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
                     util,
                     standard_options)
from spspine import gp
from spspine.graph import plot_channel, neuron_graph, spine_graph

option_parser = standard_options.standard_options(default_injection_current=[0.1e-9])
param_sim = option_parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron = cell_proto.neuronclasses(gp)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
if gp.synYN:
    syn,plas,stimtab=plastic_synapse.plastic_synapse(gp, param_sim.syncomp, MSNsyn, param_sim.stimtimes)
else:
    syn,plas = {}, {}

####---------------Current Injection

pg=inject_func.setupinj(gp, param_sim.injection_delay, param_sim.injection_width, neuron)

###############--------------output elements
param_sim.plot_channels=1
if param_sim.plot_channels:
    for chan in gp.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      gp.VMIN, gp.VMAX, gp.CAMIN, gp.CAMAX)

vmtab,catab,plastab,currtab = tables.graphtables(gp, neuron,
                                                 param_sim.plot_current,
                                                 param_sim.plot_current_message,
                                                 plas,syn)
if gp.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(gp,neuron)
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in gp.neurontypes()]
clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve)

###########Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    traces, names = [], []
    for inj in param_sim.injection_current:
        run_simulation(injection_current=inj, simtime=param_sim.simtime)
        neuron_graph.graphs(gp, vmtab, param_sim.plot_current, param_sim.simtime,
                            currtab,param_sim.plot_current_label, catab, plastab)
        for neurnum,neurtype in enumerate(gp.neurontypes()):
            traces.append(vmtab[neurnum][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
        if gp.spineYN:
            spine_graph.spineFig(gp,spinecatab,spinevmtab, param_sim.simtime)
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)

    # block in non-interactive mode
    util.block_if_noninteractive()

    #End of inject loop
