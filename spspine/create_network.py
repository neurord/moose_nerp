"""\
Sets up time tables, creates population
connects time tables to neurons
connects neurons to each other
"""
from __future__ import print_function, division
import numpy as np
import moose

from spspine import (pop_funcs,
                     connect,
                     check_connect,
                     plasticity,
                     logutil)
log = logutil.Logger()

def create_network(model, param_net,neur_protos=[]):
    #create all timetables
    param_net.TableSet.create_all()
    #
    if model.single:
        striatum_pop={'pop':{},'location':{}}
        for ntype in neur_protos.keys():
            striatum_pop['pop'][ntype]=list([neur_protos[ntype].path])
        #subset of check_param_net
        num_postsyn,num_postcells=check_connect.count_postsyn(param_net,model.param_syn.NumSyn,striatum_pop['pop'])
        tt_per_syn,tt_per_ttfile=check_connect.count_total_tt(param_net,num_postsyn,num_postcells)
        #
        for ntype in striatum_pop['pop'].keys():
            connections=connect.timetable_input(striatum_pop['pop'], param_net, ntype, model.param_syn.NumSyn )
        #
    else:
        #check_connect.check_netparams(param_net,model.param_syn.NumSyn)
        #
        #May not need to return both cells and pop from create_population - just pop is fine?
        striatum_pop = pop_funcs.create_population(moose.Neutral(param_net.netname), param_net)
        #
        #check_connect syntax after creating population
        check_connect.check_netparams(param_net,model.param_syn.NumSyn,striatum_pop['pop'])
        #
        #loop over all post-synaptic neuron types and create connections:
        for ntype in striatum_pop['pop'].keys():
            connections=connect.connect_neurons(striatum_pop['pop'], param_net, ntype, model.param_syn.NumSyn)

        #save/write out the list of connections and location of each neuron
        np.savez(param_net.confile,conn=connections,loc=striatum_pop['location'])

        ##### add Synaptic Plasticity if specified, requires calcium
    plascum=[]
    if model.calYN and model.plasYN:
        for ntype in striatum_pop['pop'].keys():
                plascum[ntype]=plasticity.addPlasticity(striatium_pop['pop'][ntype],model.CaPlasticityParams)
    return striatum_pop, connections, plascum
