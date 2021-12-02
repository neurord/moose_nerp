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
np.random.seed(2020)
import os
import matplotlib.pyplot as plt
plt.ion()

from pprint import pprint
import moose
import importlib

from moose_nerp.prototypes import (create_model_sim,
                                   calcium,
                                   clocks,
                                   inject_func,
                                   create_network,
                                   tables,
                                   net_output,
                                   logutil,
                                   util,
                                   multi_module,
                                   net_sim_graph)
#from moose_nerp import d1opt as model
from moose_nerp import D1MatrixSample2 as model
from moose_nerp.networks import matrix_net as net
from moose_nerp.graph import net_graph, neuron_graph, spine_graph

#names of additional neuron modules to import
neuron_modules=['cells.d1d2'] #d1d2 has the matrix d2 neuron
#neuron_modules=[]

#additional, optional parameter overrides specified from with python terminal
net.connect_dict['D1']['ampa']['extern1'].dend_loc.postsyn_fraction = 0.7
net.connect_dict['D2']['ampa']['extern1'].dend_loc.postsyn_fraction = 0.8
model.param_syn._SynAMPA.Gbar = .25e-9
model.param_syn._SynNMDA.Gbar = .25e-9
model.param_syn._SynGaba.Gbar = 0.75e-9

model.synYN = True
model.plasYN = False
model.calYN = True
model.spineYN = False
net.single=False#True#
#for k,v in model.param_ca_plas.CaShellModeDensity.items():
#    model.param_ca_plas.CaShellModeDensity[k] = model.param_ca_plas.SHELL
create_model_sim.setupOptions(model)
param_sim = model.param_sim
param_sim.useStreamer = False
param_sim.plotdt = .1e-3
param_sim.stim_loc = model.NAME_SOMA
param_sim.stim_paradigm = 'inject'
param_sim.injection_current = [0] #[-0.2e-9, 0.26e-9]
param_sim.injection_delay = 0.2
param_sim.injection_width = 0.4
param_sim.simtime = 1.0 #2.5 #2.5#.003#.#21
net.num_inject = 0
if net.num_inject==0:
    param_sim.injection_current=[0]
#################################-----------create the model: neurons, and synaptic inputs
model=create_model_sim.setupNeurons(model,network=True) # Do not setup hsolve yet, since there may be additional neuron_modules
#create dictionary of BufferCapacityDensity - only needed if hsolve & simple calcium dynamics
buf_cap={neur:model.param_ca_plas.BufferCapacityDensity for neur in model.neurons.keys()}

#import additional neuron modules, add them to neurons and synapses
######## this is skipped if neuron_modules is empty
if len(neuron_modules):
    buf_cap=multi_module.multi_modules(neuron_modules,model,buf_cap)

########### Create Network. For multiple populations, send in net_modules ###########
population,[connections,conn_summary],plas=create_network.create_network(model, net, model.neurons)

###### Set up stimulation - could be current injection or plasticity protocol
# set num_inject=0 to avoid current injection
if net.num_inject<np.inf :
    model.inject_pop=inject_func.inject_pop(population['pop'],net.num_inject)
else:
    model.inject_pop=population['pop']

create_model_sim.setupStim(model)

##############--------------output elements
if net.single:
    #fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]+'.npz'
    #simpath used to set-up simulation dt and hsolver
    simpath=['/'+neurotype for neurotype in model.neurons.keys()]
    create_model_sim.setupOutput(model)
else:   #population of neurons
    model.spiketab,model.vmtab,model.plastab,model.catab=net_output.SpikeTables(model, population['pop'], net.plot_netvm, plas, net.plots_per_neur)
    #simpath used to set-up simulation dt and hsolver
    simpath=[net.netname]

clocks.assign_clocks(simpath, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)
# Fix calculation of B parameter in CaConc if using hsolve and simple calcium dynamics
######### Need to use CaPlasticityParams.BufferCapacityDensity from EACH neuron_module
if model.param_sim.hsolve and model.calYN:
    calcium.fix_calcium(model.neurons.keys(), model, buf_cap)

if model.synYN and (param_sim.plot_synapse or net.single):
    #overwrite plastab above, since it is empty
    model.syntab, model.plastab, model.stp_tab=tables.syn_plastabs(connections,model)
    nonstim_plastab = tables.nonstimplastabs(plas)

# Streamer to prevent Tables filling up memory on disk
# This is a hack, should be better implemented
if param_sim.useStreamer==True:
    allTables = moose.wildcardFind('/##[ISA=Table]')
    streamer = moose.Streamer('/streamer')
    streamer.outfile = 'main_plas_sim_{}.npy'.format(os.path.basename(net.param_net.tt_Ctx_SPN.filename))
    moose.setClock(streamer.tick,0.1)
    for t in allTables:
        if any (s in t.path for s in ['plas','VmD1_0','extern','Shell_0']):
            streamer.addTable(t)
        else:
            t.tick=-2

spinedistdict = {}
for sp in moose.wildcardFind('D1/##/#head#[ISA=CompartmentBase]'):
    dist,_ = util.get_dist_name(sp)
    path = sp.path
    spinedistdict[path]=dist
np.save('main_spine_dist_dict.npy',spinedistdict)
    
################### Actually run the simulation
def run_simulation(injection_current, simtime, pg,continue_sim = False):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    if not continue_sim:
        moose.reinit()
    moose.start(simtime)

continue_sim = False
traces, names = [], []
for inj in param_sim.injection_current:
    run_simulation(injection_current=inj, simtime=param_sim.simtime,pg=model.pg,continue_sim=continue_sim)
    if net.single and len(model.vmtab):
        for neurnum,neurtype in enumerate(model.neurons):
            traces.append(model.vmtab[neurtype][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
        if model.synYN and not param_sim.useStreamer:
            net_graph.syn_graph(connections, model.syntab, param_sim)
        if model.plasYN and not param_sim.useStreamer:
            net_graph.syn_graph(connections, model.plastab, param_sim, graph_title='Plas Weight')
            net_graph.syn_graph(connections, nonstim_plastab, param_sim, graph_title='NonStim Plas Weight')

        if model.spineYN and not param_sim.useStreamer:
            spine_graph.spineFig(model,model.spinecatab,model.spinevmtab, param_sim.simtime)
    else:
        if net.plot_netvm and not param_sim.useStreamer:
            net_graph.graphs(population['pop'], param_sim.simtime, model.vmtab,model.catab,model.plastab)
        if model.synYN and param_sim.plot_synapse and not param_sim.useStreamer:
            net_graph.syn_graph(connections, model.syntab, param_sim)
        net_output.writeOutput(model, net.outfile+str(inj),model.spiketab,model.vmtab,population)

if net.single:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime,title=net.netname)
    # block in non-interactive mode

if model.plasYN: 
    weights = [w.value for w in moose.wildcardFind('/##/plas##[TYPE=Function]')]
    plt.figure()
    plt.hist(weights,bins=100)
    util.block_if_noninteractive()

if param_sim.useStreamer==True:
    import atexit
    atexit.register(moose.quit)

