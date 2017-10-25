#check whether network parameters are reasonable for making appropriate connections
#if population not yet created, predicted population is calculated in function
#i.e., this function can be used to determine how many timetables to create

from __future__ import print_function, division
import numpy as np
import moose
import logging

from moose_nerp.prototypes import (pop_funcs,
                                   connect,
                                   ttables,
                                   logutil)

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
        #convert to list if only singe instance of any cell type
        if not isinstance(population[ntype],list):
            temp=population[ntype]
            population[ntype]=list([temp])
        num_postcells[ntype]=len(population[ntype])
        num_postsyn[ntype]={}
        neur_proto=moose.element(ntype).path
        #allsyncomp_list = moose.wildcardFind(neur_proto + '/##[ISA=SynChan]')
        for syntype in netparams.connect_dict[ntype].keys():  #next level is synaptic receptor
            allsyncomp_list = moose.wildcardFind(neur_proto + '/##/'+syntype+'[ISA=SynChan]')
            syncomps,totalsyn=connect.create_synpath_array(allsyncomp_list,syntype,synapse_density)
            num_postsyn[ntype][syntype]=num_postcells[ntype]*totalsyn
    return num_postsyn,num_postcells

def count_presyn(netparams,num_cells,volume):
    presyn_cells={}
    for postype in netparams.connect_dict.keys():
        for syntype in netparams.connect_dict[postype].keys():
            presyn_cells[postype]={}
            presyn_cells[postype][syntype]=0
            for presyn_type in netparams.connect_dict[postype][syntype].keys():
                if 'extern' not in presyn_type:
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
                    presyn_cells[postype][syntype]+=min(max_cells,predict_cells)
                    log.debug ("vol {} max_cells {} num_presyn {}",volume, max_cells, presyn_cells[postype][syntype])
    return presyn_cells

def count_total_tt(netparams,num_postsyn,num_postcells):
    tt_needed_per_syntype={}
    tt_per_ttfile={}
    for each in ttables.TableSet.ALL:
        tt_per_ttfile[each.tablename]={}
        each.needed=0
    #Determine how many trains of synaptic input are needed needed.
    for ntype in netparams.connect_dict.keys():
        tt_needed_per_syntype[ntype]={}
        if num_postcells[ntype]:
            for syntype in netparams.connect_dict[ntype].keys():
                needed_trains=0
                for key in netparams.connect_dict[ntype][syntype].keys():
                  if 'extern' in key:
                      ttname=netparams.connect_dict[ntype][syntype][key].pre
                      dups=netparams.connect_dict[ntype][syntype][key].pre.syn_per_tt
                      postsyn_fraction=netparams.connect_dict[ntype][syntype][key].postsyn_fraction
                      needed_trains+=np.int(np.ceil(num_postsyn[ntype][syntype]*postsyn_fraction/dups))
                      tt_per_ttfile[ttname.tablename][ntype]={'num': np.int(np.ceil(num_postsyn[ntype][syntype]*postsyn_fraction/dups)), 'syn_per_tt': dups}
                      log.debug('tt {} syn_per_tt {} postsyn_fraction {} needed_trains {}',key, dups,postsyn_fraction,needed_trains)
                tt_needed_per_syntype[ntype][syntype]=needed_trains
    for each in ttables.TableSet.ALL:
        for ntype in tt_per_ttfile[each.tablename].keys():
            each.needed+=tt_per_ttfile[ttname.tablename][ntype]['num']
            log.info('ttname {}, {} needed for neuron {}', each.tablename, tt_per_ttfile[ttname.tablename][ntype],ntype )
        log.info("{} tt needed for file {}", each.needed, each.filename)
    return tt_needed_per_syntype,tt_per_ttfile
                     
def check_netparams(netparams,NumSyn,population=[]):
    size,num_neurons,volume=pop_funcs.count_neurons(netparams)
    log.info("net size: {} {} tissue volume {}", size,num_neurons,volume)
    #if population net yet created, calculate predicted population
    if not len(population):
        population={}
        for ntype in netparams.connect_dict.keys():
            population[ntype]=np.arange(np.round(num_neurons*netparams.pop_dict[ntype].percent))
    log.debug("pop {}",population)
    num_postsyn,num_postcells=count_postsyn(netparams,NumSyn,population)
    log.info("num synapses {} cells {}", num_postsyn, num_postcells)
    tt_per_syn,tt_per_ttfile=count_total_tt(netparams,num_postsyn,num_postcells)
    log.debug("num time tables needed: per synapse {} per ttfile {}", tt_per_syn, tt_per_ttfile)
    presyn_cells=count_presyn(netparams,num_postcells,volume)
    log.info("num presyn_cells {}", presyn_cells)
    for ntype in netparams.connect_dict.keys():
        if num_postcells[ntype]:
            for syntype in netparams.connect_dict[ntype].keys():
                log.info("POST: Neuron {} {} num_syn={}", ntype, syntype, num_postsyn[ntype][syntype])
                if syntype in presyn_cells[ntype].keys():
                    avail=presyn_cells[ntype][syntype]
                else:
                    avail=0
                log.info("PRE: neurons available={} expected tt={}", avail, tt_per_syn[ntype][syntype])
    return 
        
