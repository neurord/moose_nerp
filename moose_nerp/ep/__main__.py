# -*- coding:utf-8 -*-

########  ############
## Code to create entopeduncular neuron
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional
##      used to tune parameters and channel kinetics (but using larger morphology)

from __future__ import print_function, division
import logging

import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from pprint import pprint
import moose 

from moose_nerp.prototypes import (create_model_sim,
                                   cell_proto,
                                   calcium,
                                   clocks,
                                   inject_func,
                                   tables,
                                   plasticity_test,
                                   logutil,
                                   util,
                                   standard_options,
                                   constants)
from moose_nerp import ep as model
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

option_parser = standard_options.standard_options(
    default_injection_current=[-200e-12],
    default_simulation_time=0.2,
    default_injection_width=0.3,
    default_injection_delay=0.1,
    default_plotdt=0.0001)

param_sim = option_parser.parse_args()
param_sim.hsolve=1
param_sim.plot_channels=0

plotcomps=[model.param_cond.NAME_SOMA]

####### required for all simulations: adjust the model settings if specified by command-line options and retain model defaults otherwise
model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)

#default file name is obtained from stimulation parameters
fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]

############## required for all simulations: create the model, set up stimulation and basic output

syn,neuron,pg,param_sim,writer,vmtab, catab, plastab, currtab=create_model_sim.create_model_sim(model,fname,param_sim,plotcomps)

############# Optionally, some additional output ##############

if param_sim.plot_channels:
    for chan in model.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      model.VMIN, model.VMAX, model.CAMIN, model.CAMAX)

# create spikegens to detect and spike tables to count spikes
spiketab=tables.spiketables(neuron,model.param_cond)

if model.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(model,neuron,plotcomps)
else:
    spinevmtab=[]

###########Actually run the simulation
def run_simulation( simtime,injection_current=None):
    if model.param_stim.Stimulation.Paradigm.name == 'inject':
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

traces, names = [], []
value = {}
label = {}
calcium_traces=[]
for inj in param_sim.injection_current:
    run_simulation(injection_current=inj, simtime=param_sim.simtime)
    if param_sim.plot_vm:
        neuron_graph.graphs(model, vmtab, param_sim.plot_current, param_sim.simtime,
                        currtab,param_sim.plot_current_label, catab, plastab)
    for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
        #
        if param_sim.plot_current:
            for channame in model.Channels.keys():
                key =  neurtype+'_'+channame
                print(channame,key)
                value[key] = currtab[neurtype][channame][0].vector
                label[key] = '{} @ {}'.format(neurtype, channame)
        traces.append(vmtab[neurnum][0].vector)
        if model.calYN and param_sim.plot_calcium:
            calcium_traces.append(catab[neurnum][0].vector)
        names.append('{} @ {}'.format(neurtype, inj))

    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(model,spinecatab,spinevmtab, param_sim.simtime)

if param_sim.plot_vm:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    if model.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(calcium_traces,names,param_sim.simtime, title='Ca')

# block in non-interactive mode
util.block_if_noninteractive()

for st in spiketab:
      print("number of spikes", st.path, ' = ',len(st.vector))

