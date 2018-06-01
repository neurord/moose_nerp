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
from moose_nerp import ep
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph

option_parser = standard_options.standard_options(
    default_injection_current=[-200e-12],
    default_simulation_time=0.2,
    default_injection_width=0.3,
    default_injection_delay=0.1,
    default_plotdt=0.0001)

param_sim = option_parser.parse_args()
param_sim.hsolve=1

plotcomps=[ep.param_cond.NAME_SOMA]

######## adjust the model settings if specified by command-line options and retain model defaults otherwise
ep,plotcomps=standard_options.overrides(param_sim,ep,plotcomps)

logging.basicConfig(level=logging.INFO) log = logutil.Logger()

#################################-----------create the model
##create neuron prototype, optionally with synapses, calcium, and spines

syn,neuron = cell_proto.neuronclasses(ep)

plas = {}

####### Set up stimulation
pg,param_sim=inject_func.setup_stim(d1d2,param_sim,neuron)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
#Need to debug this since eliminated param_sim.stimtimes
#See what else needs to be changed in plasticity_test. 
if ep.plasYN:
      plas,stimtab=plasticity_test.plasticity_test(ep, param_sim.syncomp, syn, param_sim.stimtimes)
    
###############--------------output elements
param_sim.plot_channels=0
if param_sim.plot_channels:
    for chan in ep.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      ep.VMIN, ep.VMAX, ep.CAMIN, ep.CAMAX)


vmtab, catab, plastab, currtab = tables.graphtables(ep, neuron, 
                              param_sim.plot_current,
                              param_sim.plot_current_message,
                              plas,plotcomps)

if param_sim.save:
    fname=ep.param_stim.Stimulation.Paradigm.name+'_'+ep.param_stim.location.stim_dendrites[0]
    tables.setup_hdf5_output(ep, neuron, filename=fname+'.npz')

if ep.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(ep,neuron,plotcomps)
else:
    spinevmtab=[]
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in ep.neurontypes()]
clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,ep.param_cond.NAME_SOMA)

if param_sim.hsolve and ep.calYN:
    calcium.fix_calcium(ep.neurontypes(), ep)

#### create spikegen to count spikes
spikegen=moose.SpikeGen('/data/spikegen')
spikegen.threshold=0.0
spikegen.refractT=1.0e-3
msg=moose.connect(moose.element(neur+'/'+ep.param_cond.NAME_SOMA),'VmOut',spikegen,'Vm')

spiketab=moose.Table('/data/spike')
moose.connect(spikegen,'spikeOut',spiketab,'spike')

###########Actually run the simulation
def run_simulation( simtime,injection_current=None):
    if ep.param_stim.Stimulation.Paradigm.name == 'inject':
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
        neuron_graph.graphs(ep, vmtab, param_sim.plot_current, param_sim.simtime,
                        currtab,param_sim.plot_current_label, catab, plastab)
    for neurnum,neurtype in enumerate(ep.neurontypes()):
        #
        if param_sim.plot_current:
            for channame in ep.Channels.keys():
                key =  neurtype+'_'+channame
                print(channame,key)
                value[key] = currtab[neurtype][channame][0].vector
                label[key] = '{} @ {}'.format(neurtype, channame)
        traces.append(vmtab[neurnum][0].vector)
        if ep.calYN and param_sim.plot_calcium:
            calcium_traces.append(catab[neurnum][0].vector)
        names.append('{} @ {}'.format(neurtype, inj))

    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(ep,spinecatab,spinevmtab, param_sim.simtime)

if param_sim.plot_vm:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    if ep.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(calcium_traces,names,param_sim.simtime, title='Ca')

# block in non-interactive mode
util.block_if_noninteractive()

print("number of spikes", len(spiketab.vector))
