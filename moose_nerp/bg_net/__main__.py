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

import numpy as np
import matplotlib.pyplot as plt
plt.ion()

import moose
import importlib
from moose_nerp.prototypes import (calcium,
                                   cell_proto,
                                   create_model_sim,
                                   clocks,
                                   inject_func,
                                   create_network,
                                   pop_funcs,
                                   tables,
                                   net_output,
                                   util)
from moose_nerp import proto144 as model
from moose_nerp import bg_net as net
from moose_nerp.graph import net_graph, neuron_graph, spine_graph

#names of additional neuron modules to import
neuron_modules=['Npas2006','ep']
### By importing other modules, do not need to repeat all the information in param_net.py
net_modules=['gp_net','ep_net']

#additional, optional parameter overrides specified from with python terminal
model.synYN = True
model.stpYN = True
net.single=False

create_model_sim.setupOptions(model)
param_sim = model.param_sim
param_sim.injection_current = [-50e-12]
param_sim.save_txt = False
param_sim.simtime=0.5

#################################-----------create the model: neurons, and synaptic inputs
#### Do not setup hsolve yet, since there may be additional neuron_modules
model=create_model_sim.setupNeurons(model,network=True)

#create dictionary of BufferCapacityDensity - only needed if hsolve, simple calcium dynamics
if param_sim.hsolve and model.calYN:
    buf_cap={neur:model.param_ca_plas.BufferCapacityDensity for neur in model.neurons.keys()}
    model.param_syn.NumSyn={neur:model.param_syn.NumSyn for neur in model.neurons.keys()} #NOT NEEDED if change NumSyn

#import additional neuron modules, add them to neurons and synapses
for neur_module in neuron_modules:
    neur_mod=importlib.import_module(neur_module)
    #probably a good idea to give synapses to all neurons (or no neurons)
    neur_mod.synYN = model.synYN
    neur_mod.param_cond.neurontypes = util.neurontypes(neur_mod.param_cond)
    syn,neur=cell_proto.neuronclasses(neur_mod)
    for new_neur in neur.keys():
        model.syn[new_neur]=syn[new_neur]
        model.neurons[new_neur]=neur[new_neur]
        buf_cap[new_neur]=neur_mod.param_ca_plas.BufferCapacityDensity
        model.param_syn.NumSyn[new_neur]=neur_mod.param_syn.NumSyn #NOT NEEDED if change NumSyn
        
########### Set up multiple populations
network_pop={}
for network in net_modules:
    net_params=importlib.import_module(network)
    #Issue 1: create_network uses model.param_syn.NumSyn - this needs to be matched to network
    #only used in check_connect
    #Issue 2: don't break it for creating single network, BUT, single network could still have different NumSyn for different neurons!
    # BEST SOLUTION: Change param_syn to make NumSyn a dictionary of dictionaries - one for each neuron
    #population,connections,plas=create_network.create_network(model, net_mod, model.neurons)
    network_pop[network] = pop_funcs.create_population(moose.Neutral(net_params.netname), net_params, model.param_cond.NAME_SOMA)
    #Issue 3: connections - how to specify between network connections
    # a. same way as for within, but probably don't use distance dependent connections
    # b, need to re-define some named lists if specify in param_net: test:from moose_nerp.gp_net import dend_location, connect 
    # c. could even use plasticitiy - create new ones or re-use those specified in individual networks?
    # problem - they are specified in param_net.  How to read those in? see b. above
    #Issue 4: connections -how to resolve within versus between network connections
    # unclear how to deal with not using up all potential synapses.
    # currently, assign ALL connections going through once.  Single connect_dict for each neurons
    # Solution is obvious! add to connect_dict, e.g.
    #connect_dict['proto']['gaba']['D2']=net3_net1_A
    #suggests need to specify these connections afer reading in module?
    #e.g. ep.connect_dict['ep']['gaba']['proto']=bg_net.proto_to_ep_gaba
    #need to call connect AFTER creating each population - rewrite create_network - loop over create_pop, and only then call connect
