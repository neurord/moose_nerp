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

dist_incr = 0.2
min_dist=0.1
max_dist=4.0
mismatch_critera=0.1
#modify connection to add nmda
def nmdaconn():
    #fix if mindel:  should be if dist: ?
    ##if AMPA channel, create name of NMDA channel
    #if synchan.name=='ampa':
    #   nmdasynpath=synchan.parent+NMDAname
    #   nmdasynchan=moose.element(nmdasynpath) - check for existance
    #   nmdashname=nmdasynchan.path+'/SH'
    #   nmdash=moose.SimpleSynHandler(nmdashname)
    #   if nmdash.synapse.num==1:
    #       moose.connect(nmdash, 'activationOut', nmdasynchan, 'activation')
    #   nmdash.synapse.num = nmdash.synapse.num+1
    #   kk=nmdash.synapse.num
    #   nmdash.synapse[kk].delay=sh.synapse[jj].delay
    #   m = moose.connect(presyn, 'spikeOut', nmdash.synapse[kk], 'addSpike')


def alltables(fname,inpath,presyn_name,simtime):
    #Read in file with spike times.  At most one set of time tables per post-syn type
    ######################Add some code to allow entering fname if not found by system
    Spikes=np.load(fname+'.npz')
    log.info('AVAILBLE trains: {} ', len(Spikes))
    #create Time tables
    spike_tt=filltimtable(Spikes,simtime,presyn_name,inpath)
    return spike_tt

#somewhere need to calculate conn_per_tt from fraction duplicate (or correlation), number of neurons, number of syn/neuron - probably after population is created and before connections.  Use destexhe formula
# in param_net.py: want to add mean number of connections / synapses between each pre-post pair - within neuron corr

    #c. each tt in list is associated with number of times it can be used: conn_per_tt,
    #       calculated from number of neurons, number of synapses per neuron, and percent duplicates
    #d. randomly select a time table, decrement number of times, when zero is reached, remove from list
    #e. then randomly select a branch to connect to (same as in connect_neurons)
    # disadvantage: toward the end, may be connecting a neuron to same tt numerous times

def count_neurons(netparams):
    #don't repeat this in pop_funcs.  Either pass in size & numneurons, or call this function
    size=np.ones(len(netparams.grid),dtype=np.int)
    numneurons=1
    for i in range(len(netparams.grid)):
	if netparams.grid[i]['inc']>0:
	    size[i]=np.int((netparams.grid[i]['xyzmax']-netparams.grid[i]['xyzmin'])/netparams.grid[i]['inc'])
        else:
            size[i]=1
	numneurons*=size[i]
    return size, numneurons

def count_postsyn(netparams,numneurons):
    num_postcells={}  #dictionary of number of cells by type
    num_postsyn={}   #dictionary of post-synaptic receptors by cell type and synaptic receptor
    for ntype in connect_dict.keys():   #top level key is post-synaptic type
        num_postcells[ntype]=numneurons*netparams.pop_dict[ntype].percent
        num_postsyn[ntype]={}
        neur_proto=moose.element(ntype)
        allsyncomp_list = moose.wildcardFind(neur_proto + '/##[ISA=SynChan]')
        for syntype in netparams.connect_dict[ntype].keys():  #next level is synaptic receptor
            syncomps,totalsyn=create_synpath_array(allsyncomp_list,syntype,NumSyn[syntype])
            num_postsyn[ntype][syntype]=num_postcells[ntype]*totalsyn
    return num_postsyn,num_postcells

#don't repeat this in connect_neurons; call this function
def create_synpath_array(allsyncomp_list,syntype,NumSyn):
    syncomps=[]
    totalsyn=0
    for syncomp in allsyncomp_list:
        if syncomp.name==syntype:
            xloc=syncomp.parent.x
            yloc=syncomp.parent.y
            dist=np.sqrt(xloc*xloc+yloc*yloc)
            SynPerComp = distance_mapping(model.NumSyn, dist)
            syncomps.append((syncomp.path,SynPerComp))
            totalsyn+=SynPerComp
    return syncomps,totalsyn

def count_presyn(netparams,num_cells):
    pre_syn_cells={}
    for ntype in netparams.connect_dict.keys():
        for syntype in netparams.connect_dict[ntype].keys():
            pre_syn_cells[ntype]={}
            pre_syn_cells[ntype][syntype]=0
            for presyn_type in netparams.connect_dict[ntype][syntype].keys():
                space_const=netparams.connect_dict[ntype][syntype][presyn_type].space_const
                for dist in range(min_dist*space_const,max_dist*space_const,dist_incr):
                    #cell density * probability:replace num_cells with cell density*area
                    pre_syn_cells[ntype][syntype]+=num_cells[presyn_type]*np.exp(-(dist/space_const))
    return pre_syn_cells

def check_netparams(netparams):
    num_neurons=count_neurons(netparams):
    num_postsyn,num_postcells=count_postsyn(netparams,num_neurons)
    pre_syn_cells=count_presyn(netparams,num_neurons)
    for ntype in netparams.connect_dict.keys():
        for syntype in netparams.connect_dict[ntype].keys():
            if np.abs(pre_syn_cells[ntype][syntype] - num_postsyn[ntype][syntype])/
            ((pre_syn_cells[ntype][syntype]+num_postsyn[ntype][syntype])/2)>mistmatch_criteria:
                 print ("oops, mismatch")
    #need to count external connections for some synapse types - in count_total_tt
        
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
        fill_time_tables()
        connect=pop_funcs.connect_neurons(striatum_pop['pop'], param_net, ntype, synarray)

