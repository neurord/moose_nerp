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

def dict_delete(a, delete, path=[]):
    "deletes dictionary with key b from a"
    for ntype in delete:
        if ntype in a:
            for syntype in delete[ntype]:
                if syntype in a[ntype]:
                    print('dict delete',ntype,syntype,delete[ntype][syntype])
                    if isinstance (delete[ntype][syntype],str):
                        del a[ntype][syntype][delete[ntype][syntype]]
                    elif isinstance (delete[ntype][syntype],list):
                        for pre in delete[ntype][syntype]:
                            del a[ntype][syntype][pre]
                    else:
                        print('>>>>>>>> dict_delete,', delete[ntype][syntype], 'is neither string nor list. Write more code to handle this')
                else:
                    pass
        else:
            pass
    return a

def change_connect(connect_dict,change_dict):
    for neurtype in change_dict.keys():
        for syntype in change_dict[neurtype].keys():
            for presyn,change_tuple in change_dict[neurtype][syntype].items():
                #print('>>>>>> old connect ',connect_dict[neurtype][syntype][presyn])
                if presyn in connect_dict[neurtype][syntype]:
                    if change_tuple[0]=='space_const' or change_tuple[0]=='weight':
                        oldvalue=connect_dict[neurtype][syntype][presyn].__getattribute__(change_tuple[0])
                        connect_dict[neurtype][syntype][presyn].__setattr__(change_tuple[0],change_tuple[1]*oldvalue)
                    else:
                        connect_dict[neurtype][syntype][presyn].__setattr__(change_tuple[0],change_tuple[1])
                    print('>>>>>> change connect, type= ', change_dict[neurtype][syntype][presyn][0],' :::',connect_dict[neurtype][syntype][presyn])
                else:
                    print('***** connection not found for ', neurtype,syntype,presyn,' other connections=',connect_dict[neurtype][syntype])
                    
    return connect_dict

def change_extern_files(connect_dict,ttables):
    for neurtype in ttables:
        for syntype in ttables[neurtype]:
            for presyn in ttables[neurtype][syntype]:
                connect_dict[neurtype][syntype][presyn].pre=ttables[neurtype][syntype][presyn]
                print('>>>>>>      new connect          ', connect_dict[neurtype][syntype][presyn])
    return connect_dict

def print_connect_dict(connect_dict):
    for key1,item1 in connect_dict.items():
        for key2,item2 in item1.items():
            for key3,item3 in item2.items():
                print('***connect_dict after merge and delete:',key1,key2,key3,item3)
    return

def create_network(model, param_net,neur_protos={},network_list=None):
    connections={}
    #
    conn_summary={}
    if param_net.single:
        #create all timetables
        ttables.TableSet.create_all()
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
            net_names=[]
            for network in network_list:
                other_net=importlib.import_module(network)
                net_names.append(other_net.netname)
                one_network_pop = pop_funcs.create_population(moose.Neutral(other_net.netname), other_net, model.param_cond.NAME_SOMA)
                all_networks.update(one_network_pop['pop'])
                locations[network]=one_network_pop['location']
                if param_net.merge_connect:
                    #create one dictionary of all connections from other networks param_net
                    #print_connect_dict(other_net.connect_dict)
                    param_net.connect_dict=merge(param_net.connect_dict,other_net.connect_dict)
                #FIXME - only using mindelay and cond_vel from last network
                # recommendation - make mindelay and cond_vel dictionaries - one value for each neuron type
                param_net.mindelay=merge(param_net.mindelay,other_net.mindelay)
                param_net.cond_vel=merge(param_net.cond_vel,other_net.cond_vel)
            if param_net.merge_connect:
                #change weight of connections
                param_net.connect_dict=change_connect(param_net.connect_dict, param_net.change_weight)
                #change connection probabilities for intrinsic connectins
                param_net.connect_dict=change_connect(param_net.connect_dict,param_net.change_prob)
                #delete connections, e.g. extrinsic, no longer needed since connecting to other networks
                param_net.connect_dict=dict_delete(param_net.connect_dict,param_net.connect_delete)
                #print_connect_dict(param_net.connect_dict)
                param_net.connect_dict=change_extern_files(param_net.connect_dict,param_net.ttable_replace)
            network_pop={'location':locations,'pop':all_networks,'netnames':net_names}
            #identify needed timtables and only create unique ones (no duplicates)
            needed_ttabs=list(set([it3.pre for it1 in param_net.connect_dict.values() for it2 in it1.values() for it3 in it2.values() if isinstance(it3,connect.ext_connect)]))
            ttables.TableSet.ALL=needed_ttabs
        #Regardles of whether one or multiple populations, create needed timetables
        ttables.TableSet.create_all()
        #loop over all post-synaptic neuron types and create connections:
        for ntype in network_pop['pop'].keys():
            connections[ntype],conn_summary[ntype]=connect.connect_neurons(network_pop['pop'], param_net, ntype, model)
        for ntype in conn_summary.keys():
            print('@@@@@@@@@@@@@@@@@@ neuron',ntype)
            for syn in conn_summary[ntype]['intra'].keys():
                print('      syn=', syn, ', mean shortage=',np.mean([short for short in conn_summary[ntype]['shortage'][syn].values()]),', has inputs:')
                print(conn_summary[ntype]['intra'][syn])
                if len(conn_summary[ntype]['intra'][syn])>1: #if more than one type of input to each cell
                    allconns=np.zeros(len(network_pop['pop'][ntype]))
                    for v in conn_summary[ntype]['intra'][syn].values():
                        allconns+=np.array(v)
                    print('         mean number of inputs for ',syn,' = ',np.mean(allconns))
        if network_list is not None:
            print('TTABLES',[tt.filename for tt in ttables.TableSet.ALL])
            print ('>>>> original ttabs',len(ttables.TableSet.ALL),'needed_ttabs',len(needed_ttabs), [tt.filename for tt in needed_ttabs])
    #
    ##### add Synaptic Plasticity if specified, requires calcium
    plascum={}
    if model.calYN and model.plasYN:
        for ntype in network_pop['pop'].keys():
            plascum[ntype]=plasticity.addPlasticity(network_pop['pop'][ntype],model.CaPlasticityParams)
    return network_pop, [connections, conn_summary],plascum

