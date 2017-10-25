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
from moose_nerp import ca1

from moose_nerp.graph import plot_channel, neuron_graph, spine_graph

option_parser = standard_options.standard_options(default_injection_current=[200e-12])
param_sim = option_parser.parse_args()
param_sim.save=0

plotcomps=[ca1.param_cond.NAME_SOMA]

######## adjust the model settings if specified by command-line options and retain model defaults otherwise
#These assignment statements are required because they are not part of param_sim namespace.
if param_sim.calcium is not None:
    ca1.calYN = param_sim.calcium
if param_sim.spines is not None:
    ca1.spineYN = param_sim.spines
if param_sim.stim_paradigm is not None:
    ca1.param_stim.Stimulation.Paradigm=ca1.param_stim.paradigm_dict[param_sim.stim_paradigm]
if param_sim.stim_loc is not None:
    ca1.param_stim.Stimulation.StimLoc.stim_dendrites=param_sim.stim_loc

#These assignments make assumptions about which parameters should be changed together   
if ca1.calYN and param_sim.plot_calcium is None:
    param_sim.plot_calcium = True
if ca1.param_stim.Stimulation.Paradigm.name is not 'inject':
    #override defaults if synaptic stimulation is planned
    ca1.calYN=1
    #Perhaps these should be removed
    ca1.spineYN=1
    ca1.synYN=1
#update in future: currently cannot deal with more than one stim_dendrite in option parser (OK in param_stim.location)
if ca1.param_stim.Stimulation.Paradigm.name is not 'inject' or param_sim.stim_loc is not None:
    plotcomps=np.unique(plotcomps+ca1.param_stim.location.stim_dendrites)

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron = cell_proto.neuronclasses(ca1)

plas = {}

####### Set up stimulation
if ca1.param_stim.Stimulation.Paradigm.name is not 'inject':
    ### plasticity paradigms combining synaptic stimulation with optional current injection
    sim_time = []
    for ntype in ca1.neurontypes():
        #update how ConnectPreSynapticPostSynapticStimulation deals with param_stim
        st, spines, pg = inject_func.ConnectPreSynapticPostSynapticStimulation(ca1,ntype)
        sim_time.append( st)
        plas[ntype] = spines
    param_sim.simtime = max(sim_time)
    param_sim.injection_current = [0]
else:
    ### Current Injection alone, either use values from Paradigm or from command-line options
    if not np.any(param_sim.injection_current):
        param_sim.injection_current = [ca1.param_stim.Stimulation.Paradigm.A_inject]
        param_sim.injection_delay = ca1.param_stim.Stimulation.stim_delay
        param_sim.injection_width = ca1.param_stim.Stimulation.Paradigm.width_AP
    all_neurons={}
    for ntype in neuron.keys():
        all_neurons[ntype]=list([neuron[ntype].path])
    pg=inject_func.setupinj(ca1, param_sim.injection_delay, param_sim.injection_width,all_neurons)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
#Need to debug this since eliminated param_sim.stimtimes
#See what else needs to be changed in plasticity_test. 
if ca1.plasYN:
      plas,stimtab=plasticity_test.plasticity_test(ca1, param_sim.syncomp, MSNsyn, param_sim.stimtimes)

###############--------------output elements
if param_sim.plot_channels:
    for chan in ca1.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      ca1.VMIN, ca1.VMAX, ca1.CAMIN, ca1.CAMAX)

vmtab, catab, plastab, currtab = tables.graphtables(ca1, neuron,
                              param_sim.plot_current,
                              param_sim.plot_current_message,
                              plas,plotcomps)
if param_sim.save:
    fname=ca1.param_stim.Stimulation.Paradigm.name+'_'+ca1.param_stim.location.stim_dendrites[0]
#    tables.setup_hdf5_output(ca1, neuron, param_sim.save)

if ca1.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(ca1,neuron,plotcomps)
else:
    spinevmtab=[]
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in ca1.neurontypes()]
clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,ca1.param_cond.NAME_SOMA)

if param_sim.hsolve and ca1.calYN:
    calcium.fix_calcium(ca1.neurontypes(), ca1)

###########Actually run the simulation
def run_simulation( simtime,injection_current=None):
    if ca1.param_stim.Stimulation.Paradigm.name == 'inject':
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

traces, names, catraces = [], [], []
for inj in param_sim.injection_current:
    run_simulation(simtime=param_sim.simtime,injection_current=inj)
    if param_sim.plot_vm:
        neuron_graph.graphs(ca1, vmtab,param_sim.plot_current, param_sim.simtime,
                        currtab, param_sim.plot_current_label, catab, plastab)
    #set up tables that accumulate soma traces for multiple simulations
    for neurnum,neurtype in enumerate(ca1.neurontypes()):
        traces.append(vmtab[neurnum][0].vector)
        if ca1.calYN and param_sim.plot_calcium:
            catraces.append(catab[neurnum][0].vector)
        names.append('{} @ {}'.format(neurtype, inj))
        # In Python3.6, the following syntax works:
        #names.append(f'{neurtype} @ {inj}')
    #plot spines
    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(ca1,spinecatab,spinevmtab, param_sim.simtime)
    #save output - expand this to optionally save current data
    if param_sim.save:
        inj_nA=inj*1e9
        tables.write_textfile(vmtab,'Vm', fname,inj_nA,param_sim.simtime)
        if ca1.calYN:
            tables.write_textfile(catab,'Ca', fname,inj_nA,param_sim.simtime)
        if ca1.spineYN and len(spinevmtab):
            tables.write_textfile(list(spinevmtab.values()),'SpVm', fname,inj_nA,param_sim.simtime)
            if ca1.spineYN and len(spinecatab):
                tables.write_textfile(list(spinecatab.values()),'SpCa', fname,inj_nA,param_sim.simtime)
if param_sim.plot_vm:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    if ca1.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(catraces, names, param_sim.simtime)

# block in non-interactive mode
util.block_if_noninteractive()
