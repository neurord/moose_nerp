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

from moose_nerp.prototypes import (create_model_sim,
                                   cell_proto,
                                   clocks,
                                   inject_func,
                                   create_network,
                                   tables,
                                   net_output,
                                   logutil,
                                   util,
                                   standard_options)
from moose_nerp import d1d2 as model
from moose_nerp import str_net as net
from moose_nerp.graph import net_graph, neuron_graph, spine_graph

#additional, optional parameter overrides specified from with python terminal
model.synYN = True
model.plasYN = True
model.calYN = True
model.spineYN = True
net.single=True
for k,v in model.param_ca_plas.CaShellModeDensity.items():
    model.param_ca_plas.CaShellModeDensity[k] = model.param_ca_plas.SHELL
create_model_sim.setupOptions(model)
param_sim = model.param_sim
param_sim.simtime = .1
net.num_inject = 0
if net.num_inject==0:
    param_sim.injection_current=[0]
#################################-----------create the model: neurons, and synaptic inputs
model=create_model_sim.setupNeurons(model,network=not net.single)
all_neur_types=model.neurons
#FSIsyn,neuron = cell_proto.neuronclasses(FSI)
#all_neur_types.update(neuron)
population,connections,plas=create_network.create_network(model, net, all_neur_types)

###### Set up stimulation - could be current injection or plasticity protocol
# set num_inject=0 to avoid current injection
if net.num_inject<np.inf :
    inject_pop=inject_func.inject_pop(population['pop'],net.num_inject)
else:
    inject_pop=population['pop']
#Does setupStim work for network?
#create_model_sim.setupStim(model)
pg=inject_func.setupinj(model, param_sim.injection_delay,param_sim.injection_width,inject_pop)
moose.showmsg(pg)

##############--------------output elements
if net.single:
    #fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]+'.npz'
    #simpath used to set-up simulation dt and hsolver
    simpath=['/'+neurotype for neurotype in all_neur_types]
    create_model_sim.setupOutput(model)
else:   #population of neurons
    spiketab,vmtab,plastab,catab=net_output.SpikeTables(model, population['pop'], net.plot_netvm, plas, net.plots_per_neur)
    #simpath used to set-up simulation dt and hsolver
    simpath=[net.netname]
    clocks.assign_clocks(simpath, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)
if model.synYN and (param_sim.plot_synapse or net.single):
    #overwrite plastab above, since it is empty
    syntab, plastab, stp_tab=tables.syn_plastabs(connections,model)

################### Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

traces, names = [], []
for inj in param_sim.injection_current:
    run_simulation(injection_current=inj, simtime=param_sim.simtime)
    if net.single and len(model.vmtab):
        for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
            traces.append(model.vmtab[neurtype][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
        if model.synYN:
            net_graph.syn_graph(connections, syntab, param_sim)
        if model.plasYN:
            net_graph.syn_graph(connections, plastab, param_sim, graph_title='Plas Weight')
        if model.spineYN:
            spine_graph.spineFig(model,model.spinecatab,model.spinevmtab, param_sim.simtime)
    else:
        if net.plot_netvm:
            net_graph.graphs(population['pop'], param_sim.simtime, vmtab,catab,plastab)
        if model.synYN and param_sim.plot_synapse:
            net_graph.syn_graph(connections, syntab, param_sim)
        net_output.writeOutput(model, net.outfile+str(inj),spiketab,vmtab,population)

if net.single:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    # block in non-interactive mode
util.block_if_noninteractive()

'''
import detect
if net.single:
    vmtab=model.vmtab
spike_time={key:[] for key in population['pop'].keys()}
numspikes={key:[] for key in population['pop'].keys()}
for neurtype, tabset in vmtab.items():
    for tab in tabset:
       spike_time[neurtype].append(detect.detect_peaks(tab.vector)*param_sim.plotdt)
    numspikes[neurtype]=[len(st) for st in spike_time[neurtype]]
    print(neurtype,'mean:',np.mean(numspikes[neurtype]),'rate',np.mean(numspikes[neurtype])/param_sim.simtime,'from',numspikes[neurtype], 'spikes')
#spikes=[st.vector for tabset in spiketab for st in tabset]
'''
