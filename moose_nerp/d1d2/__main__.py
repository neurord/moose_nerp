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

import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from pprint import pprint
import moose 

from moose_nerp.prototypes import (cell_proto,
                     calcium,
                     clocks,
                     inject_func,
                     tables,
                     plasticity_test,
                     logutil,
                     util,
                     standard_options,
                     constants)
from moose_nerp import d1d2
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph

#two examples of calling option_parser - one overrides the defaults and is useful when running from python window
option_parser = standard_options.standard_options()
#option_parser = standard_options.standard_options(default_calcium=True, default_spines=False,default_injection_current=[0.25e-9,0.35e-9],default_stim='inject')
param_sim = option_parser.parse_args()

plotcomps=[d1d2.param_cond.NAME_SOMA]

######## adjust the model settings if specified by command-line options and retain model defaults otherwise
#These assignment statements are required because they are not part of param_sim namespace.
if param_sim.calcium is not None:
    d1d2.calYN = param_sim.calcium
if d1d2.calYN and param_sim.plot_calcium is None:
    param_sim.plot_calcium = True
if param_sim.spines is not None:
    d1d2.spineYN = param_sim.spines
if param_sim.stim_paradigm is not None:
    d1d2.param_stim.Stimulation.Paradigm=d1d2.param_stim.paradigm_dict[param_sim.stim_paradigm]
if param_sim.stim_loc is not None:
    d1d2.param_stim.Stimulation.StimLoc.stim_dendrites=param_sim.stim_loc
if d1d2.param_stim.Stimulation.Paradigm.name is not 'inject':
    #override defaults if synaptic stimulation is planned
    d1d2.calYN=1
    d1d2.spineYN=1
    d1d2.synYN=1
    #this will need enhancement in future, e.g. in option_parser, to plot additional locations
    plotcomps=plotcomps+d1d2.param_stim.location.stim_dendrites

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron= cell_proto.neuronclasses(d1d2)

plas = {}

####### Set up stimulation
if d1d2.param_stim.Stimulation.Paradigm.name is not 'inject':
    ### plasticity paradigms combining synaptic stimulation with optional current injection
    sim_time = []
    for ntype in d1d2.neurontypes():
        #update how ConnectPreSynapticPostSynapticStimulation deals with param_stim
        st, spines, pg = inject_func.ConnectPreSynapticPostSynapticStimulation(d1d2,ntype)
        sim_time.append( st)
        plas[ntype] = spines
    param_sim.simtime = max(sim_time)
    param_sim.injection_current = [0]
else:
    ### Current Injection alone, either use values from Paradigm or from command-line options
    if not np.any(param_sim.injection_current):
        param_sim.injection_current = [d1d2.param_stim.Stimulation.Paradigm.A_inject]
        param_sim.injection_delay = d1d2.param_stim.Stimulation.stim_delay
        param_sim.injection_width = d1d2.param_stim.Stimulation.Paradigm.width_AP
    all_neurons={}
    for ntype in neuron.keys():
        all_neurons[ntype]=list([neuron[ntype].path])
    pg=inject_func.setupinj(d1d2, param_sim.injection_delay, param_sim.injection_width,all_neurons)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
#Need to debug this since eliminated param_sim.stimtimes
#See what else needs to be changed in plasticity_test. 
if d1d2.plasYN:
      plas,stimtab=plasticity_test.plasticity_test(d1d2, param_sim.syncomp, MSNsyn, param_sim.stimtimes)
    
###############--------------output elements
if param_sim.plot_channels:
    for chan in d1d2.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      d1d2.VMIN, d1d2.VMAX, d1d2.CAMIN, d1d2.CAMAX)

vmtab, catab, plastab, currtab = tables.graphtables(d1d2, neuron,
                              param_sim.plot_current,
                              param_sim.plot_current_message,
                              plas,plotcomps)
if param_sim.save:
    tables.setup_hdf5_output(d1d2, neuron, param_sim.save)

if d1d2.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(d1d2,neuron,plotcomps)

########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in d1d2.neurontypes()]
clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve, d1d2.param_cond.NAME_SOMA)
print("simdt", param_sim.simdt, "hsolve", param_sim.hsolve)

if param_sim.hsolve and d1d2.calYN:
    calcium.fix_calcium(d1d2.neurontypes(), d1d2)

###########Actually run the simulation
def run_simulation( simtime,injection_current=None):
    if d1d2.param_stim.Stimulation.Paradigm.name == 'inject':
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

traces, names, catraces = [], [], []
for inj in param_sim.injection_current:
    run_simulation(simtime=param_sim.simtime,injection_current=inj)
    if param_sim.plot_vm:
        neuron_graph.graphs(d1d2, param_sim.plot_current, param_sim.simtime,
                        currtab, param_sim.plot_current_label,
                        catab, plastab)
    #set up tables that accumulate soma traces for multiple simulations
    for neurnum,neurtype in enumerate(d1d2.neurontypes()):
        traces.append(vmtab[neurnum][0].vector)
        if d1d2.calYN and param_sim.plot_calcium:
            catraces.append(catab[neurnum][0].vector)
        names.append('{} @ {}'.format(neurtype, inj))
        # In Python3.6, the following syntax works:
        #names.append(f'{neurtype} @ {inj}')
    #plot spines
    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(d1d2,spinecatab,spinevmtab, param_sim.simtime)
if param_sim.plot_vm:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    if d1d2.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(catraces, names, param_sim.simtime)

# block in non-interactive mode
util.block_if_noninteractive()
