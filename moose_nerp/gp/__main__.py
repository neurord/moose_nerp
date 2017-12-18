# -*- coding:utf-8 -*-

######## SPneuronSim.py ############
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
from moose_nerp import gp
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph

option_parser = standard_options.standard_options(
    default_injection_current=[25e-12],#[-100e-12, -50e-12, 25e-12,75e-12],
    default_simulation_time=0.6,
    default_injection_width=0.4,
    default_plotdt=0.0001)
#,default_stim='PSP_1')
# Issue with stimulation needs fixing:
#Line 83: st, spines, pg = inject_func.ConnectPreSynapticPostSynapticStimulation(gp,ntype)
#File "moose_nerp/prototypes/inject_func.py", line 227, in ConnectPreSynapticPostSynapticStimulation
#stim_spines.update(new_spines)
#TypeError: 'NoneType' object is not iterable
#same error with or without spines

param_sim = option_parser.parse_args()

plotcomps=[gp.param_cond.NAME_SOMA]

######## adjust the model settings if specified by command-line options and retain model defaults otherwise
#These assignment statements are required because they are not part of param_sim namespace.
if param_sim.calcium is not None:
    gp.calYN = param_sim.calcium
if param_sim.spines is not None:
    gp.spineYN = param_sim.spines
if param_sim.stim_paradigm is not None:
    gp.param_stim.Stimulation.Paradigm=gp.param_stim.paradigm_dict[param_sim.stim_paradigm]
if param_sim.stim_loc is not None:
    gp.param_stim.Stimulation.StimLoc.stim_dendrites=param_sim.stim_loc

#These assignments make assumptions about which parameters should be changed together   
if gp.calYN and param_sim.plot_calcium is None:
    param_sim.plot_calcium = True
if gp.param_stim.Stimulation.Paradigm.name is not 'inject':
    #override defaults if synaptic stimulation is planned
    gp.synYN=1
    #this will need enhancement in future, e.g. in option_parser, to plot additional locations
    plotcomps=plotcomps+gp.param_stim.location.stim_dendrites

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

#gp.neurontypes(['arky'])
MSNsyn,neuron = cell_proto.neuronclasses(gp)
print('MSNsyn:', MSNsyn)
print('neuron:', neuron)

plas = {}

####### Set up stimulation
if gp.param_stim.Stimulation.Paradigm.name is not 'inject':
    ### plasticity paradigms combining synaptic stimulation with optional current injection
    sim_time = []
    for ntype in gp.neurontypes():
        #update how ConnectPreSynapticPostSynapticStimulation deals with param_stim
        st, spines, pg = inject_func.ConnectPreSynapticPostSynapticStimulation(gp,ntype)
        sim_time.append( st)
        plas[ntype] = spines
    param_sim.simtime = max(sim_time)
    param_sim.injection_current = [0]
else:
    ### Current Injection alone, either use values from Paradigm or from command-line options
    if not np.any(param_sim.injection_current):
        param_sim.injection_current = [gp.param_stim.Stimulation.Paradigm.A_inject]
        param_sim.injection_delay = gp.param_stim.Stimulation.stim_delay
        param_sim.injection_width = gp.param_stim.Stimulation.Paradigm.width_AP
    all_neurons={}
    for ntype in neuron.keys():
        all_neurons[ntype]=list([neuron[ntype].path])
    pg=inject_func.setupinj(gp, param_sim.injection_delay, param_sim.injection_width,all_neurons)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
#Need to debug this since eliminated param_sim.stimtimes
#See what else needs to be changed in plasticity_test. 
if gp.plasYN:
      plas,stimtab=plasticity_test.plasticity_test(gp, param_sim.syncomp, MSNsyn, param_sim.stimtimes)
    
###############--------------output elements
param_sim.plot_channels=1
if param_sim.plot_channels:
    for chan in ['NaF', 'NaS']:#gp.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      gp.VMIN, gp.VMAX, gp.CAMIN, gp.CAMAX)


vmtab, catab, plastab, currtab = tables.graphtables(gp, neuron, 
                              param_sim.plot_current,
                              param_sim.plot_current_message,
                              plas,plotcomps)

if param_sim.save:
    tables.setup_hdf5_output(d1d2, neuron, param_sim.save)

if gp.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(gp,neuron,plotcomps)
else:
    spinevmtab=[]
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in gp.neurontypes()]
clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,gp.param_cond.NAME_SOMA)

if param_sim.hsolve and gp.calYN:
    calcium.fix_calcium(gp.neurontypes(), gp)

##print soma conductances
moose.reinit()
if param_sim.hsolve:
    chantype='ZombieHHChannel'
else:
    chantype='HHChannel'
for neur in gp.neurontypes():
  for chan in moose.wildcardFind('{}/soma/#[TYPE={}]'.format(neur, chantype)):
    print (neur, chan.name,chan.Ik*1e9, chan.Gk*1e9)
  for chan in moose.wildcardFind('/'+neur+'/soma/#[TYPE=HHChannel2D]'):
    print (neur, chan.name,chan.Ik*1e9, chan.Gk*1e9)

spikegen=moose.SpikeGen('/data/spikegen')
spikegen.threshold=0.0
spikegen.refractT=1.0e-3
msg=moose.connect(moose.element(neur+'/'+gp.param_cond.NAME_SOMA),'VmOut',spikegen,'Vm')

####
spiketab=moose.Table('/data/spike')
moose.connect(spikegen,'spikeOut',spiketab,'spike')

###########Actually run the simulation
def run_simulation( simtime,injection_current=None):
    if gp.param_stim.Stimulation.Paradigm.name == 'inject':
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
        neuron_graph.graphs(gp, vmtab, param_sim.plot_current, param_sim.simtime,
                        currtab,param_sim.plot_current_label, catab, plastab)
    for neurnum,neurtype in enumerate(gp.neurontypes()):
        #
        if param_sim.plot_current:
            for channame in gp.Channels.keys():
                key =  neurtype+'_'+channame
                print(channame,key)
                value[key] = currtab[neurtype][channame][0].vector
                label[key] = '{} @ {}'.format(neurtype, channame)
        traces.append(vmtab[neurnum][0].vector)
        #traces.append(vmtab[neurnum][2].vector)
        if gp.calYN and param_sim.plot_calcium:
            calcium_traces.append(catab[neurnum][0].vector)
            #calcium_traces.append(catab[neurnum][2].vector)
        names.append('c0{} @ {}'.format(neurtype, inj))
        #names.append('c1{} @ {}'.format(neurtype, inj))

    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(gp,spinecatab,spinevmtab, param_sim.simtime)
#
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
    if gp.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(calcium_traces,names,param_sim.simtime, title='Ca')

# block in non-interactive mode
util.block_if_noninteractive()

print("number of spikes", len(spiketab.vector))
