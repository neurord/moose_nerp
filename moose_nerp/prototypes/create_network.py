"""\
Sets up time tables, creates population
connects time tables to neurons
connects neurons to each other
"""
from __future__ import print_function, division
import numpy as np
import importlib
from copy import deepcopy
import moose

from moose_nerp.prototypes import (pop_funcs,
                                   connect,
                                   check_connect,
                                   plasticity,
                                   ttables,
                                   logutil)
log = logutil.Logger()

def merge(a, b, path=[]):
    "merges b into a"
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def create_network(model, param_net,neur_protos={},network_list=None):
    #create all timetables
    ttables.TableSet.create_all()
    #print(ttables.TableSet.ALL)
    for tt in ttables.TableSet.ALL:
        print('>>>>TIME TABLE', tt.filename)
    connections={}
    #
    if param_net.single:
        network_pop={'pop':{},'location':{}}
        #network is equal to the list of neuron prototypes:
        for ntype in neur_protos.keys():
            network_pop['pop'][ntype]=list([neur_protos[ntype].path])
        #subset of check_param_net
        #FIXME - update to work with NumSyn as cell type specific (dictionary of dictionaries)
        #num_postsyn,num_postcells,allsyncomp_list=check_connect.count_postsyn(param_net,model.param_syn.NumSyn,network_pop['pop'])
        #print("num synapses {} cells {}".format(num_postsyn, num_postcells))
        #tt_per_syn,tt_per_ttfile=check_connect.count_total_tt(param_net,num_postsyn,num_postcells,allsyncomp_list,model.param_syn.NumSyn)
        #print("num time tables needed: per synapse type {} per ttfile {}".format(tt_per_syn, tt_per_ttfile))
        #
        for ntype in network_pop['pop'].keys():
            connections[ntype]=connect.timetable_input(network_pop['pop'], param_net, ntype, model )
        #
    else:
        if network_list is None:
            #check_connect.check_netparams(param_net,model.param_syn.NumSyn)
            #
            #create population of neurons according to grid spacing and size using neuron prototypes
            network_pop = pop_funcs.create_population(moose.Neutral(param_net.netname), param_net, model.param_cond.NAME_SOMA)
            #
            #check_connect syntax after creating population
            #check_connect.check_netparams(param_net,model.param_syn.NumSyn,network_pop['pop'])
            #
        else:
            all_networks={}
            locations={}
            for network in network_list:
                net_params=importlib.import_module(network)
                one_network_pop = pop_funcs.create_population(moose.Neutral(net_params.netname), net_params, model.param_cond.NAME_SOMA)
                all_networks.update(one_network_pop['pop'])
                locations[network]=one_network_pop['location']
                param_net.connect_dict=merge(param_net.connect_dict,net_params.connect_dict)
                #FIXME - only using mindelay and cond_vel from last network
                # recommendation - make mindelay and cond_vel dictionaries - one value for each neuron type
                param_net.mindelay=merge(param_net.mindelay,net_params.mindelay)
                param_net.cond_vel=merge(param_net.cond_vel,net_params.cond_vel)
            network_pop={'location':locations,'pop':all_networks}
        #Regardles of whether one or multiple populations,
        #loop over all post-synaptic neuron types and create connections:
        for ntype in network_pop['pop'].keys():
            connections[ntype]=connect.connect_neurons(network_pop['pop'], param_net, ntype, model)
        #
    #save/write out the list of connections and location of each neuron
    np.savez(param_net.confile,conn=connections,loc=network_pop['location'])
    #
    ##### add Synaptic Plasticity if specified, requires calcium
    plascum={}
    if model.calYN and model.plasYN:
        for ntype in network_pop['pop'].keys():
            plascum[ntype]=plasticity.addPlasticity(network_pop['pop'][ntype],model.CaPlasticityParams)
    return network_pop, connections, plascum

