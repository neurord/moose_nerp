# -*- coding:utf-8 -*-

####################
## Code to create two globus pallidus neurons
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
from moose_nerp import gp as model
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph

option_parser = standard_options.standard_options(
    default_injection_current=[-100e-12],
    default_simulation_time=0.1,
    default_injection_width=1.0,
    default_injection_delay=0.047,
    default_plotdt=0.0001)
#,default_stim='PSP_1')
# Issue with stimulation needs fixing:
#Line 83: st, spines, pg = inject_func.ConnectPreSynapticPostSynapticStimulation(model,ntype)
#File "moose_nerp/prototypes/inject_func.py", line 227, in ConnectPreSynapticPostSynapticStimulation
#stim_spines.update(new_spines)
#TypeError: 'NoneType' object is not iterable
#same error with or without spines

param_sim = option_parser.parse_args()
param_sim.save=1
param_sim.plot_channels=0

plotcomps=[model.param_cond.NAME_SOMA]

######## adjust the model settings if specified by command-line options and retain model defaults otherwise
model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

syn,neuron = cell_proto.neuronclasses(model)
print('syn:', syn)
print('neuron:', neuron)

plas = {}

####### Set up stimulation
pg,param_sim=inject_func.setup_stim(model,param_sim,neuron)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
#Need to debug this since eliminated param_sim.stimtimes
#See what else needs to be changed in plasticity_test. 
if model.plasYN:
      plas,stimtab=plasticity_test.plasticity_test(model, param_sim.syncomp, syn, param_sim.stimtimes)
    
###############--------------output elements
if param_sim.plot_channels:
    for chan in model.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      model.VMIN, model.VMAX, model.CAMIN, model.CAMAX)

vmtab, catab, plastab, currtab = tables.graphtables(model, neuron, 
                              param_sim.plot_current,
                              param_sim.plot_current_message,
                              plas,plotcomps)

# create spikegens to detect and spike tables to count spikes
spiketab=tables.spiketables(neuron,model.param_cond)

if param_sim.save:
    fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]
    tables.setup_hdf5_output(model, neuron, filename=fname+'.npz')

if model.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(model,neuron,plotcomps)
else:
    spinevmtab=[]
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in util.neurontypes(model.param_cond)]
clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)

if param_sim.hsolve and model.calYN:
    calcium.fix_calcium(util.neurontypes(model.param_cond), model)

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
        #traces.append(vmtab[neurnum][2].vector)
        if model.calYN and param_sim.plot_calcium:
            calcium_traces.append(catab[neurnum][0].vector)
            #calcium_traces.append(catab[neurnum][2].vector)
        names.append('c0{} @ {}'.format(neurtype, inj))
        #names.append('c1{} @ {}'.format(neurtype, inj))

    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(model,spinecatab,spinevmtab, param_sim.simtime)

#
#subset1=['proto_HCN1','proto_HCN2' ]
#subset2=['proto_NaS']
#subset3=['proto_Ca']
#subset4=['proto_BKCa']
#subset5=['proto_NaS']
#subset6 = ['proto_KvS']
#subsetin=['proto_HCN1','proto_HCN2','proto_NaS', 'proto_Ca' ,'proto_NaF']
#subsetout=['proto_KCNQ','proto_KvS', 'proto_KvF', 'proto_Kv3', 'proto_SKCa','proto_KDr' ]
#neuron_graph.CurrentGraphSet(value,label,subsetin, param_sim.simtime)
#neuron_graph.CurrentGraphSet(value, label, subsetout, param_sim.simtime)
#neuron_graph.CurrentGraphSet(value, label, subset3, param_sim.simtime)
#neuron_graph.CurrentGraphSet(value, label, subset4, param_sim.simtime)
#neuron_graph.CurrentGraphSet(value, label, subset5, param_sim.simtime)
#neuron_graph.CurrentGraphSet(value, label, subset6, param_sim.simtime)

if param_sim.plot_vm:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    if model.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(calcium_traces,names,param_sim.simtime, title='Ca')

# block in non-interactive mode
util.block_if_noninteractive()

for st in spiketab:
      print("number of spikes", st.path, ' = ',len(st.vector))

