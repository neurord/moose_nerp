"""\
Sets up time tables, creates population
connects time tables to neurons
connects neurons to each other
"""
from __future__ import print_function, division
import moose

from spspine import (pop_funcs,
                     connect,
                     check_connect,
                     plasticity,
                     logutil)
log = logutil.Logger()

def create_network(model, param_net):
    #create all timetables
    param_net.TableSet.create_all()
    #
    if model.single:
        #fix this kluge? Potentially may need to know neurontypes/names of multiple neurons 
        striatum_pop={'pop':{},'location':{}}
        for ntype in model.neurontypes():
            striatum_pop['pop'][ntype]=["/"+ntype]
        #subset of check_param_net
        num_postsyn,num_postcells=check_connect.count_postsyn(param_net,model.param_syn.NumSyn,striatum_pop['pop'])
        tt_per_syn,tt_per_ttfile=check_connect.count_total_tt(param_net,num_postsyn,num_postcells)
        #
        for ntype in striatum_pop['pop'].keys():
            connections=connect.connect_neurons(striatum_pop['pop'], param_net, ntype, model.param_syn.NumSyn )
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

        #Last, save/write out the list of connections and location of each neuron
        savez(param_net.confile,conn=connect,loc=striatum_pop['location'])

    ##### Synaptic Plasticity, requires calcium
    #### Array of SynPlas has ALL neurons of a single type in one big array.  Might want to change this
    if model.calYN and model.plasYN:
        #rolled back code because didn't know how to add loop over nnum (synchronized to ntype) in single line
        SynPlas={}
        if model.single:
            for ntype in _types:
                SynPlas[ntype]=plasticity.addPlasticity(MSNsyn[ntype]['ampa'],
                                                        model.CaPlasticityParams.highThresh,
                                                        model.CaPlasticityParams.lowThresh,
                                                        model.CaPlasticityParams.highfactor,
                                                        model.CaPlasticityParams.lowfactor,
                                                        [])
#        else:
#            for nnum,ntype in _enumerate(_types):
#                SynPlas[ntype]=plasticity.addPlasticity(MSNsyn[ntype]['ampa'],
#                                                        model.CaPlasticityParams.highThresh,
#                                                        model.CaPlasticityParams.lowThresh,
#                                                        model.CaPlasticityParams.highfactor,
#                                                        model.CaPlasticityParams.lowfactor,
#                                                        population['pop'][nnum])
    else:
        SynPlas=[]
    return striatum_pop, SynPlas
