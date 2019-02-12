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
                                   standard_options,
                                   create_model_sim)
from moose_nerp import ep as model
from moose_nerp import ep_net as net
from moose_nerp.graph import net_graph, neuron_graph, spine_graph


#additional, optional parameter overrides specified from with python terminal
model.synYN = True
model.plasYN = False
net.single=True

create_model_sim.setupOptions(model)
param_sim = model.param_sim

###alcohol injection--> Bk channel constant multiplier
alcohol = 1
if alcohol > 1:
    for neurtype in model.param_cond.Condset:
        for key in model.param_cond.Condset[neurtype]['BKCa']:
            model.param_cond.Condset[neurtype]['BKCa'][key]=alcohol*model.param_cond.Condset[neurtype]['BKCa'][key]
    net.outfile = 'alcohol'+str(alcohol)
else:
    net.outfile='Ctrl'
#list of size >=1 is required for plotcomps
plotcomps=[model.param_cond.NAME_SOMA]

#################################-----------create the model: neurons, and synaptic inputs
model=create_model_sim.setupNeurons(model,network=True)
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

if net.single:
    #fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]+'.npz'
    #simpath used to set-up simulation dt and hsolver
    simpath=['/'+neurotype for neurotype in all_neur_types]
    ##############--------------output elements
    #create_model_sim.setupOutput(model)
    vmtab, catab, plastab, currtab=tables.graphtables(model, model.neurons,
                                   model.param_sim.plot_current,
                                   model.param_sim.plot_current_message,
                                   model.plas,
                                   model.param_sim.plotcomps)
    if model.synYN:
        #overwrite plastab above, since it is empty
        syntab, plastab=tables.syn_plastabs(connections,plas)
    if model.spineYN:
        spinecatab,spinevmtab=tables.spinetabs(model,neuron)
else:   #population of neurons
    ##############--------------output elements
    spiketab,vmtab,plastab,catab=net_output.SpikeTables(model, population['pop'], net.plot_netvm, plas, net.plots_per_neur)
    #simpath used to set-up simulation dt and hsolver
    simpath=[net.netname]

########## clocks are critical
## these function needs to be tailored for each simulation
## if things are not working, you've probably messed up here.
#possibly need to setup an hsolver separately for each cell in the network
clocks.assign_clocks(simpath, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)

################### Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

traces, names = [], []
for inj in param_sim.injection_current:
    run_simulation(injection_current=inj, simtime=param_sim.simtime)
    if net.single and len(vmtab):
        for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
            traces.append(vmtab[neurtype][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
        if model.synYN:
            net_graph.syn_graph(connections, model.syntab, param_sim.simtime)
        if model.spineYN:
            spine_graph.spineFig(model,model.spinecatab,model.spinevmtab, param_sim.simtime)
    else:
        if net.plot_netvm:
            net_graph.graphs(population['pop'], param_sim.simtime, vmtab,catab,plastab)
        net_output.writeOutput(model, net.outfile+str(inj),spiketab,vmtab,population)

if net.single:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    # block in non-interactive mode
util.block_if_noninteractive()
