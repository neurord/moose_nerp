from __future__ import print_function, division
import numpy as np
import moose
import logging

from spspine import logutil,pop_funcs,connect

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

mismatch_critera=0.1
#evaluate number of pre-synaptic cells between min_dist*space_constant and max_dist*space_const
#in increments of dist_incr*space_const
dist_incr = 1.0
min_dist=0.01
max_dist=5.0

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

def count_presyn(netparams,num_cells,volume):
    pre_syn_cells={}
    for postype in netparams.connect_dict.keys():
        for syntype in netparams.connect_dict[postype].keys():
            pre_syn_cells[postype]={}
            pre_syn_cells[postype][syntype]=0
            for presyn_type in netparams.connect_dict[postype][syntype].keys():
                if presyn_type != 'extern':
                    predict_cells=0
                    space_const=netparams.connect_dict[postype][syntype][presyn_type].space_const
                    density=num_cells[presyn_type]/volume
                    max_cells=num_cells[presyn_type]
                    inner_area=0
                    for dist in np.arange(min_dist*space_const,max_dist*space_const,dist_incr*space_const):
                        outer_area=np.pi*dist*dist
                        predict_cells+=np.int(density*(outer_area-inner_area)*np.exp(-dist/space_const))
                        log.debug("dist {} outer_area {} predict_cells {} ",  dist, outer_area, predict_cells)
                        inner_area=outer_area
                    pre_syn_cells[postype][syntype]+=min(max_cells,predict_cells)
                    log.debug ("vol {} max_cells {} num_presyn {}",volume, max_cells, pre_syn_cells[postype][syntype])
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
    size,num_neurons,volume=pop_funcs.count_neurons(netparams)
    log.info("net size: {} {} vol {}", size,num_neurons,volume)
    #if population net yet created, calculate predicted population
    if not len(population):
        population={}
        for ntype in netparams.connect_dict.keys():
            population[ntype]=np.arange(np.round(num_neurons*netparams.pop_dict[ntype].percent))
    log.debug("pop {}",population)
    num_postsyn,num_postcells=count_postsyn(netparams,synapse_density,population)
    log.info("num synapses {} cells {}", num_postsyn, num_postcells)
    num_tt=count_total_tt(netparams,num_postsyn,num_postcells)
    log.debug("num time tables {}", num_tt)
    pre_syn_cells=count_presyn(netparams,num_postcells,volume)
    log.info("num presyn_cells {}", pre_syn_cells)
    for ntype in netparams.connect_dict.keys():
        for syntype in netparams.connect_dict[ntype].keys():
            if 'extern' in netparams.connect_dict[ntype][syntype].keys():
                log.info("Neuron {} Synapse {} Post {} needed tt {}", ntype, syntype, num_postsyn[ntype][syntype], num_tt[ntype][syntype])
            else:
                log.info("Neuron {} Synapse {} Post {} available Pre {}", ntype, syntype, num_postsyn[ntype][syntype]/num_postcells[ntype], pre_syn_cells[ntype][syntype])
    return num_neurons,num_postsyn,num_postcells,num_tt,pre_syn_cells
        
