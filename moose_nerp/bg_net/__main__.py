# -*- coding:utf-8 -*-

######## bg_net/__main__.py ############
"""
Model of entire basal ganglia
Loads in all neuron modules and all network modules
1. Test/Fix connections from external spike trains - bg_net
2. Investigate why running out of connections - with gp_net or spn1comp_net only
3. Verify that single compartment neurons are behaving same in network as single
4. Investigate why synaptic inputs not visible - with gp_net or spn1comp_net only
5. Adjust synaptic strength to match data (use smal number of neurons)
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
from moose_nerp import spn_1comp as model
from moose_nerp import bg_net as net
from moose_nerp.graph import net_graph, neuron_graph, spine_graph

#names of additional neuron modules to import
neuron_modules=['ep_1comp','proto154_1compNoCal','Npas2005_1compNoCal','arky140_1compNoCal','fsi']
### By importing other modules, do not need to repeat all the information in param_net.py
net_modules=['moose_nerp.gp_net','moose_nerp.ep_net', 'moose_nerp.spn1_net']

#additional, optional parameter overrides specified from with python terminal
model.synYN = True
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
buf_cap={neur:model.param_ca_plas.BufferCapacityDensity for neur in model.neurons.keys()}

#import additional neuron modules, add them to neurons and synapses
for neur_module in neuron_modules:
    neur_mod=importlib.import_module('moose_nerp.'+neur_module)
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
debugging:
4. deal with time tables - import ttables in netparam?  no need to specify ttables?
which time tables are being created? gp, ep or bg_net?  
1. test with tt specified in param_net (better comments in create_network)
if works:
2. figure out whether could read in (and accumulate?) from importlib - would need to call TableSet.create_all again


remaining issues
1. model.param_cond.NAME_SOMA needs to be dictionary, to allow different soma names for different neurons
2. all ion channels are created in same library.  That means that channels with same name are overwriting existing channels - could be problem
3. network['location'] is now a dictionary of lists, instead of just a list; BUT, this is not used, so OK

'''
    
