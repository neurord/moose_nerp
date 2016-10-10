from __future__ import print_function, division
import numpy as np
import moose

from spspine import pop_funcs,connect

dist_incr = 0.2
min_dist=0.1
max_dist=4.0
mismatch_critera=0.1

def count_postsyn(netparams,synapse_density,population):
    num_postcells={}  #dictionary of number of cells by type
    num_postsyn={}   #dictionary of post-synaptic receptors by cell type and synaptic receptor
    for ntype in netparams.connect_dict.keys():   #top level key is post-synaptic type
        num_postcells[ntype]=len(population[ntype])
        num_postsyn[ntype]={}
        neur_proto=moose.element(ntype).path
        allsyncomp_list = moose.wildcardFind(neur_proto + '/##[ISA=SynChan]')
        for syntype in netparams.connect_dict[ntype].keys():  #next level is synaptic receptor
            syncomps,totalsyn=connect.create_synpath_array(allsyncomp_list,syntype,synapse_density)
            num_postsyn[ntype][syntype]=num_postcells[ntype]*totalsyn
    return num_postsyn,num_postcells

def count_presyn(netparams,num_cells):
    pre_syn_cells={}
    for ntype in netparams.connect_dict.keys():
        for syntype in netparams.connect_dict[ntype].keys():
            pre_syn_cells[ntype]={}
            pre_syn_cells[ntype][syntype]=0
            for presyn_type in netparams.connect_dict[ntype][syntype].keys():
                space_const=netparams.connect_dict[ntype][syntype][presyn_type].space_const
                print(space_const,pre_syn_cells[ntype][syntype],num_cells[presyn_type])
                #for dist in range(min_dist*space_const,max_dist*space_const,dist_incr):
                    #cell density * probability:replace num_cells with cell density*area
                pre_syn_cells[ntype][syntype]+=num_cells[presyn_type]#*np.exp(-(dist/space_const))
    return pre_syn_cells

def count_total_tt(netparams,num_postsyn,num_postcells):
    total_trains={}
    #Now determine how many unique and shared trains needed.
    #The following assumes unique timetable files for each ntype/syntype
    for ntype in netparams.connect_dict.keys():
        total_trains[ntype]={}
        for syntype in netparams.connect_dict[ntype].keys():
            num_input=num_postsyn[ntype][syntype]
            if 'extern' in netparams.connect_dict[ntype][syntype].keys():
                #may need to loop over multiple instances of extern if multiple tt
                dups=netparams.connect_dict[ntype][syntype]['extern'].fraction_duplicate
                unique=num_input*(1-dups)
                shared=num_input*dups/num_postcells[ntype]
                total_trains[ntype][syntype]=unique+shared
    return total_trains
                     
def check_netparams(netparams,synapse_density,population=[]):
    size,num_neurons=pop_funcs.count_neurons(netparams)
    #if population net yet created, calculate predicted population
    if not len(population):
        population={}
        for ntype in netparams.connect_dict.keys():
            population[ntype]=np.arange(np.round(num_neurons*netparams.pop_dict[ntype].percent))
    num_postsyn,num_postcells=count_postsyn(netparams,synapse_density,population)
    num_tt=count_total_tt(netparams,num_postsyn,num_postcells)
    pre_syn_cells=count_presyn(netparams,num_neurons)
    #for ntype in netparams.connect_dict.keys():
    #    for syntype in netparams.connect_dict[ntype].keys():
    #        if np.abs(pre_syn_cells[ntype][syntype] - num_postsyn[ntype][syntype])/ ((pre_syn_cells[ntype][syntype]+num_postsyn[ntype][syntype])/2)>mistmatch_criteria:
    #             print ("oops, mismatch")
    #need to count external connections for some synapse types - in count_total_tt
    return num_neurons,num_postsyn,num_postcells,num_tt
        
