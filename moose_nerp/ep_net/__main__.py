# -*- coding:utf-8 -*-

######## GPnetSim.py ############
"""\
Create a network of GP neurons using dictionaries for channels, synapses, and network parameters

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
from moose_nerp import ep as model
from moose_nerp import ep_net as net
from moose_nerp.graph import net_graph, neuron_graph, spine_graph


#additional, optional parameter overrides specified from with python terminal
model.synYN = True
model.stpYN = False
net.single=True

create_model_sim.setupOptions(model)
param_sim = model.param_sim
param_sim.injection_current = [0e-12]
param_sim.plot_synapse=True
param_sim.injection_delay = 0.1
param_sim.simtime = 1.0
param_sim.plot_synapse=True

param_sim.injection_width = param_sim.simtime-param_sim.injection_delay
if net.num_inject==0:
    param_sim.injection_current=[0]

#################################-----------create the model: neurons, and synaptic inputs
model=create_model_sim.setupNeurons(model,network=not net.single)
all_neur_types = model.neurons
population,connections,plas=create_network.create_network(model, net, all_neur_types)

####### Set up stimulation - could be current injection or plasticity protocol
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
    # Fix calculation of B parameter in CaConc if using hsolve
    if model.param_sim.hsolve and model.calYN:
        calcium.fix_calcium(util.neurontypes(model.param_cond), model)

if model.synYN and (param_sim.plot_synapse or net.single):
    #overwrite plastab above, since it is empty
    syntab, plastab, stp_tab=tables.syn_plastabs(connections,model)

#################### Actually run the simulation
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
            net_graph.syn_graph(connections, syntab, param_sim,graph_title="Syn Chans, no plasticity")
            if model.stpYN:
                net_graph.syn_graph(connections, stp_tab,param_sim,graph_title='short term plasticity')
        if model.spineYN:
            spine_graph.spineFig(model,model.spinecatab,model.spinevmtab, param_sim.simtime)
    else:
        if net.plot_netvm:
            net_graph.graphs(population['pop'], param_sim.simtime, vmtab,catab,plastab)
        if model.synYN and param_sim.plot_synapse:
            net_graph.syn_graph(connections, syntab, param_sim)
            if model.stpYN:
                net_graph.syn_graph(connections, stp_tab,param_sim,graph_title='short term plasticity',factor=1)
        net_output.writeOutput(model, net.outfile+str(inj),spiketab,vmtab,population)

if net.single:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    # block in non-interactive mode
util.block_if_noninteractive()

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
ToDo:
1. short term plasticity
a. SpikeTables in net_output needs work to plot calcium, and also debug plastabs - possible to use tables.syn_plastabs?
Also, perhaps eliminate the default (empty?) plastab created in graphtables

b. Debug calcium !!!! adding calcium produces strange oscillations.

c. Verify frequency dependent change in GPe and Str inputs using single timetable inputs and 
 i. no firing (hyperpol slightly)
 ii. firing (no hyperpol or slight depol) - prolonged ISI (Str) or stop firing (GPe)

d. evaluate (network) response to time table input with and without stp

2. long term plasticity: how much to change synaptic weights?

3. How to analyze results

for neurtype,neurtype_dict in connections.items():
    for neur,neur_dict in neurtype_dict.items():
        for syn,syn_dict in neur_dict.items():
            for pretype,pre_dict in syn_dict.items():
                for branch,presyn in pre_dict.items():
                    if 'TimTab' not in presyn:
                        preflag='** Intrinsic **'
                    else:
                        preflag='ext'
                    print(preflag,neurtype,neur,syn,pretype,branch,presyn)

import numpy as np
data=np.load('gp_connect.npz')
conns=data['conn'].item()
for neurtype,neurdict in conns.items():
  for cell in neurdict.keys():
     for pre,post in neurdict[cell]['gaba'].items():
        print(cell,pre,post)
'''
