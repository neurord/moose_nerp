#refine select_branch to make use of location dependence and allow multiple connections per neuron
#alternative to extern_input, used in addinput:
# a. create list of all post-syn neurons
# b. loop over all timetables, select conn_per_tt out of the post-syn neurons without replacement
# c. for each neuron selected, randomly select a compartment
# disadvantage: can't create table of compartments for one neuron at a time, and different than other connection types.  

from __future__ import print_function, division
import numpy as np
import moose

from spspine import logutil, extern_conn
log = logutil.Logger()


#somewhere need to calculate conn_per_tt from fraction duplicate (or correlation), number of neurons, number of syn/neuron - probably after population is created and before connections.  Use destexhe formula
# in param_net.py: want to add mean number of connections / synapses between each pre-post pair - within neuron corr

    #c. each tt in list is associated with number of times it can be used: conn_per_tt,
    #       calculated from number of neurons, number of synapses per neuron, and percent duplicates
    #d. randomly select a time table, decrement number of times, when zero is reached, remove from list
    #e. then randomly select a branch to connect to (same as in connect_neurons)
    # disadvantage: toward the end, may be connecting a neuron to same tt numerous times

def count_total_tt(netparams):
    organize dictionary into ordered multi-dict to do the following:
    1. post_syn type, e.g. glu or gaba varies least                       glu     ctx_tt      D1post  fraction_duplicate
    2. ttname in second column                                            glu     ctx_tt      D2post  fraction_duplicate
    3. post-syn neuron class in third column                              glu     thal_tt     D1post  fraction_duplicate
    4. ttname varies less than post-syn                                   glu     thal_tt     D2post  fraction_duplicate
    5. Sum number of post-syn comps for each ttname and compare with size of ttname file
    Issue: ensure that ctx_tt + thal_tt is sufficient for D1post popoulation
    Also ensure that ctx_tt is sufficient for both D1post and D2post
    To deal with this, need to specify what proportion of inputs are ctx vs thal, OR give range of compartments for ctx vs thal and syn per comp
    Or probability of connect.
    
    num_postsyn,num_postcells=count_postsyn(netparams,numneurons) 
    extern_dict=OrderedDict()
    #reg_voxel_vol=omdict(( zip(model['grid'][:]['region'],model['grid'][:]['volume'] ) ))
     for ntype in netparams.connect_dict.keys():
         for syntype in netparams.connect_dict[ntype].keys():
            if netparams.connect_dict[ntype][syntype].pre='timetable':
                temp=(netparams.connect_dict[ntype][syntype].fname, ntype, netparams.connect_dict[syntype].fraction_duplicate)
                extern_dict[syntype].append(temp)
    for syntype in extern_dict.keys():
                unique = num_input*(1-netparams.connect_dict[syntype].fraction_duplicate)
                dup=num_input*netparams.connect_dict[syntype].fraction_duplicate/num_neurons
                total_tt=unique+dup

        total_tt = num_input*SQRT(1-netparams.connect_dict[syntype].corr)
    return total_tt

#expand external connections to include post-syn location and percent  
def create_network():
    if not model.single:
        striatum_pop = pop_funcs.create_population(moose.Neutral(param_net.netname), param_net)
        count_total_tt(striatum_pop)
    else:
        count_total_tt(protypes)
    #do this by each ntype?
    check_netparms(netparams)
    for ntype in striatum_pop['pop'].keys():
        connect.fill_time_tables()
        connect=connect.connect_neurons(striatum_pop['pop'], param_net, ntype, synarray)

