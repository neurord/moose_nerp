# -*- coding:utf-8 -*-

######## SPnetSim.py ############
"""\
Create a network of SP neurons using dictionaries for channels, synapses, and network parameters

Can use ghk for calcium permeable channels if ghkYesNo=1
Optional calcium concentration in compartments (calcium=1)
Optional synaptic plasticity based on calcium (plasyesno=1)
Spines are optional (spineYesNo=1), but not allowed for network
The graphs won't work for multiple spines per compartment
"""
from __future__ import print_function, division
import logging

import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from pprint import pprint
import moose 

from moose_nerp.prototypes import (cell_proto,
                     clocks,
                     inject_func,
                     create_network,
                     tables,
                     net_output,
                     logutil,
                     util,
                     standard_options)
from moose_nerp import (d1d2,str_net)
from moose_nerp.graph import net_graph, neuron_graph, spine_graph

option_parser = standard_options.standard_options(default_injection_current=[100e-12])
param_sim = option_parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
#overrides:
d1d2.synYN = True
d1d2.plasYN = False

##create neuron prototypes with synapses and calcium
MSNsyn,neuron = cell_proto.neuronclasses(d1d2)

all_neur_types=neuron
#FSIsyn,neuron = cell_proto.neuronclasses(FSI)
#all_neur_types.update(neuron)

#create network and plasticity
population,connections,plas=create_network.create_network(d1d2, str_net, all_neur_types)

###------------------Current Injection
if str_net.num_inject<np.inf and not str_net.single :
    inject_pop=inject_func.inject_pop(population['pop'],str_net.num_inject)
else:
    inject_pop=population['pop']
pg=inject_func.setupinj(d1d2, param_sim.injection_delay,param_sim.injection_width,inject_pop)
moose.showmsg(pg)
##############--------------output elements
if str_net.single:
    vmtab, catab, plastab, currtab =tables.graphtables(d1d2, all_neur_types,
                                                       param_sim.plot_current,
                                                       param_sim.plot_current_message,
                                                       [])
    if d1d2.synYN:
        #overwrite plastab above, since it is empty
        syntab, plastab=tables.syn_plastabs(connections,plas)
    if d1d2.spineYN:
        spinecatab,spinevmtab=tables.spinetabs(d1d2,neuron)
else:
    spiketab, vmtab, plastab, catab = net_output.SpikeTables(d1d2, population['pop'], str_net.plot_netvm, plas, str_net.plots_per_neur)

########## clocks are critical
## these function needs to be tailored for each simulation
## if things are not working, you've probably messed up here.
if str_net.single:
    simpath=['/'+neurotype for neurotype in all_neur_types]
else:
    #possibly need to setup an hsolver separately for each cell in the network
    simpath=[str_net.netname]
clocks.assign_clocks(simpath, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,d1d2.param_cond.NAME_SOMA)

################### Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

traces, names = [], []
for inj in param_sim.injection_current:
    run_simulation(injection_current=inj, simtime=param_sim.simtime)
    if str_net.single:
        for neurnum,neurtype in enumerate(d1d2.neurontypes()):
            traces.append(vmtab[neurnum][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
        if d1d2.synYN:
            net_graph.syn_graph(connections, syntab, param_sim.simtime)
        if d1d2.spineYN:
            spine_graph.spineFig(d1d2,spinecatab,spinevmtab, param_sim.simtime)
    else: 
        if str_net.plot_netvm:
            net_graph.graphs(population['pop'], param_sim.simtime, vmtab,catab,plastab)
        net_output.writeOutput(d1d2, str_net.outfile+str(inj),spiketab,vmtab,population)

if str_net.single:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    # block in non-interactive mode
util.block_if_noninteractive()
