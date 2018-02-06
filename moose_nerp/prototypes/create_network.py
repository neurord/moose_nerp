"""\
Sets up time tables, creates population
connects time tables to neurons
connects neurons to each other
"""
from __future__ import print_function, division
import numpy as np
import moose

from moose_nerp.prototypes import (pop_funcs,
                                   connect,
                                   check_connect,
                                   plasticity,
                                   ttables,
                                   logutil)
log = logutil.Logger()

def create_network(model, param_net,neur_protos={}):
    #create all timetables
    ttables.TableSet.create_all()
    connections={}
    #
    if param_net.single:
        network_pop={'pop':{},'location':{}}
        #network is equal to the list of neuron prototypes:
        for ntype in neur_protos.keys():
            network_pop['pop'][ntype]=list([neur_protos[ntype].path])
        #subset of check_param_net
        num_postsyn,num_postcells=check_connect.count_postsyn(param_net,model.param_syn.NumSyn,network_pop['pop'])
        tt_per_syn,tt_per_ttfile=check_connect.count_total_tt(param_net,num_postsyn,num_postcells)
        #
        for ntype in network_pop['pop'].keys():
            connections[ntype]=connect.timetable_input(network_pop['pop'], param_net, ntype, model )
        #
    else:
        #check_connect.check_netparams(param_net,model.param_syn.NumSyn)
        #
        #May not need to return both cells and pop from create_population - just pop is fine?
        network_pop = pop_funcs.create_population(moose.Neutral(param_net.netname), param_net, model.param_cond.NAME_SOMA)
        #
        #check_connect syntax after creating population
        check_connect.check_netparams(param_net,model.param_syn.NumSyn,network_pop['pop'])
        #
        #loop over all post-synaptic neuron types and create connections:
        for ntype in network_pop['pop'].keys():
            connections[ntype]=connect.connect_neurons(network_pop['pop'], param_net, ntype, model)

        #save/write out the list of connections and location of each neuron
        np.savez(param_net.confile,conn=connections,loc=network_pop['location'])


        ##### add Synaptic Plasticity if specified, requires calcium
    plascum={}
    if model.calYN and model.plasYN:
        
        for ntype in network_pop['pop'].keys():
            plascum[ntype]=plasticity.addPlasticity(network_pop['pop'][ntype],model.CaPlasticityParams)
    return network_pop, connections, plascum

