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
param_sim.simtime=0.05

#################################-----------create the model: neurons, and synaptic inputs
#### Do not setup hsolve yet, since there may be additional neuron_modules
model=create_model_sim.setupNeurons(model,network=True)

#create dictionary of BufferCapacityDensity - only needed if hsolve, simple calcium dynamics
if param_sim.hsolve and model.calYN:
    buf_cap={neur:model.param_ca_plas.BufferCapacityDensity for neur in model.neurons.keys()}

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
        model.param_syn.NumSyn[new_neur]=neur_mod.param_syn.NumSyn[new_neur]
        
########### Create Network. For multiple populations, send in net_modules ###########
population,connections,plas=create_network.create_network(model, net, model.neurons,network_list=net_modules)
print(net.connect_dict)
print(population['location'],population['pop'])
'''
connections={}
all_networks={}
locations={}
print(net.connect_dict)
for network in net_modules:
    net_params=importlib.import_module(network)
    one_network_pop = pop_funcs.create_population(moose.Neutral(net_params.netname), net_params, model.param_cond.NAME_SOMA)
    all_networks.update(one_network_pop['pop'])
    locations[network]=one_network_pop['location']
    net.connect_dict=create_network.dict_of_dicts_merge(net.connect_dict,net_params.connect_dict)
network_pop={'location':locations,'pop':all_networks}
print(net.connect_dict)
print(network_pop['location'])
for ntype in network_pop['pop'].keys():
    connections[ntype]=connect.connect_neurons(network_pop['pop'], net, ntype, model)
'''
''' 
debugging:
4. deal with time tables - import ttables in netparam?  no need to specify ttables?
which time tables are being created? gp, ep or bg_net?  
3. commit and push

remaining issues
1. model.param_cond.NAME_SOMA needs to be dictionary, to allow different soma names for different neurons
2. all ion channels are created in same library.  That means that channels with same name are overwriting existing channels - could be problem
3. network['location'] is now a dictionary of lists, instead of just a list; BUT, this is not used, so OK

'''
    
