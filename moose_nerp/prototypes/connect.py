"""\
Function definitions for connecting populations of neurons
1. single synaptic connection
2. creating an array of post-synaptic channels, to randomly select without replacement
3. connect each post-syn channel type of each neuron to either a pre-synaptic neuron or a timetable

"""

from __future__ import print_function, division
import numpy as np
import moose

from moose_nerp.prototypes import logutil, util
from moose_nerp.prototypes.spines import NAME_HEAD
log = logutil.Logger()

def plain_synconn(synchan,presyn,syn_delay):
    shname=synchan.path+'/SH'
    sh=moose.SimpleSynHandler(shname)
    if sh.synapse.num==0:
        moose.connect(sh, 'activationOut', synchan, 'activation')
    jj=sh.synapse.num
    sh.synapse.num = sh.synapse.num+1
    sh.synapse[jj].delay=syn_delay
    log.debug('SYNAPSE: {} index {} num {} delay {}', synchan.path, jj, sh.synapse.num, sh.synapse[jj].delay)
    #It is possible to set the synaptic weight here.
    if presyn.className=='TimeTable':
        moose.connect(presyn, 'eventOut', sh.synapse[jj], 'addSpike')
    else:
        moose.connect(presyn, 'spikeOut', sh.synapse[jj], 'addSpike')

def synconn(synpath,dist,presyn_path, syn_params ,mindel=1e-3,cond_vel=0.8):
    presyn=moose.element(presyn_path)
    if dist:
        syn_delay = max(mindel,np.random.normal(mindel+dist/cond_vel,mindel))
    else:
        syn_delay=mindel
    synchan=moose.element(synpath)
    plain_synconn(synchan,presyn,syn_delay)
                
    if synchan.name==syn_params.NAME_AMPA:
       nmda_synpath=synchan.parent.path+'/'+syn_params.NAME_NMDA
       if moose.exists(nmda_synpath):
           nmda_synchan=moose.element(nmda_synpath)
           plain_synconn(nmda_synchan,presyn,syn_delay)

def select_entry(table):
    row=np.random.random_integers(0,len(table)-1)
    element=table[row][0]
    table[row][1]=int(table[row][1])-1
    if table[row][1]==0: 
        table[row]=table[len(table)-1]
        table=np.resize(table,(len(table)-1,2))
    return element

def create_synpath_array(allsyncomp_list,syntype,NumSyn):
    syncomps=[]
    totalsyn=0
    for syncomp in allsyncomp_list:
        xloc=syncomp.parent.x
        yloc=syncomp.parent.y
        dist=np.sqrt(xloc*xloc+yloc*yloc)
        SynPerComp = util.distance_mapping(NumSyn[syntype], dist)
        syncomps.append([syncomp.path,SynPerComp])
        totalsyn+=SynPerComp
    return syncomps,totalsyn

def connect_timetable(post_connection,syncomps,totalsyn,netparams, syn_params):
    dist=0
    tt_list=post_connection.pre.stimtab
    postsyn_fraction=post_connection.postsyn_fraction
    num_tt=len(tt_list)
    connections={}
    #calculate how many of these timetables should be connected to this synapse type
    #randomly select a timetable (presyn_tt), and post-synaptic branch (synpath) for each connection
    for i in range(np.int(np.round(totalsyn*postsyn_fraction))):
        presyn_tt=select_entry(tt_list)
        synpath=select_entry(syncomps)
        log.debug('CONNECT: TT {} POST {} ', presyn_tt.path,synpath)
        #connect the time table with mindelay (dist=0)
        synconn(synpath,dist,presyn_tt,syn_params,netparams.mindelay)
        postbranch=util.syn_name(synpath,NAME_HEAD)
        connections[postbranch]=presyn_tt.path
    return connections

def timetable_input(cells, netparams, postype, model):
    #connect post-synaptic synapses to time tables
    #used for single neuron models only, since populations are connected in connect_neurons
    log.debug('CONNECT set: {} {} {}', postype, cells[postype],netparams.connect_dict[postype])
    post_connections=netparams.connect_dict[postype]
    connect_list = {}
    postcell = cells[postype][0]
    for syntype in post_connections.keys():
        connect_list[syntype]={}
        allsyncomp_list=moose.wildcardFind(postcell+'/##/'+syntype+'[ISA=SynChan]')
        syncomps,totalsyn=create_synpath_array(allsyncomp_list,syntype,model.param_syn.NumSyn)
        log.info('SYN TABLE for {} has {} compartments and {} synapses', syntype, len(syncomps),totalsyn)
        for pretype in post_connections[syntype].keys():
            if 'extern' in pretype:
                #This is going to overwrite pretype1 dictionary with pretype2 dictionary
                connect_list[syntype]=connect_timetable(post_connections[syntype][pretype],syncomps,totalsyn,netparams,model.param_syn)
    return connect_list
                    
def connect_neurons(cells, netparams, postype, model):
    log.debug('CONNECT set: {} {} {}', postype, cells[postype],netparams.connect_dict[postype])
    post_connections=netparams.connect_dict[postype]
    connect_list = {}
    #loop over post-synaptic neurons - convert to list if only singe instance of any type
    if not isinstance(cells[postype],list):
        temp=cells[postype]
        cells[postype]=list([temp])
    for postcell in cells[postype]:
        connect_list[postcell]={}
        postsoma=postcell+'/'+model.param_cond.NAME_SOMA
        xpost=moose.element(postsoma).x
        ypost=moose.element(postsoma).y
        zpost=moose.element(postsoma).z
        #set-up array of post-synapse compartments/synchans
        for syntype in post_connections.keys():
            allsyncomp_list=moose.wildcardFind(postcell+'/##/'+syntype+'[ISA=SynChan]')
            connect_list[postcell][syntype]={}
            #make a table of possible post-synaptic connections
            syncomps,totalsyn=create_synpath_array(allsyncomp_list,syntype,model.param_syn.NumSyn)
            log.debug('SYN TABLE for {} {} has {} compartments and {} synapses', postsoma, syntype, len(syncomps),totalsyn)
            for pretype in post_connections[syntype].keys():
                if 'extern' in pretype:
                    ####### connect to time tables instead of other neurons in network
                    connect_list[postcell][syntype]=connect_timetable(post_connections[syntype][pretype],syncomps,totalsyn,netparams,model.param_syn)
                else:
                    ###### connect to other neurons in network: loop over pre-synaptic neurons
                    for precell in cells[pretype]:
                        presoma=precell+'/'+model.param_cond.NAME_SOMA
                        fact=post_connections[syntype][pretype].space_const
                        xpre=moose.element(presoma).x
                        ypre=moose.element(presoma).y
                        zpre=moose.element(presoma).z
                        #calculate distance between pre- and post-soma
                        dist=np.sqrt((xpre-xpost)**2+(ypre-ypost)**2+(zpre-zpost)**2)
                        prob=np.exp(-(dist/fact))
                        connect=np.random.uniform()
                        log.debug('{} {} {} {} {} {}', presoma,postsoma,dist,fact,prob,connect)
                        #select a random number to determine whether a connection should occurmore c
                        if connect < prob and dist > 0 and len(syncomps)>0:
                            spikegen=moose.wildcardFind(presoma+'/#[TYPE=SpikeGen]')[0]
                            #if so, randomly select a branch, and then eliminate that branch from the table.
                            #presently only a single synapse established.  Need to expand this to allow multiple conns
                            synpath=select_entry(syncomps)
                            log.debug('CONNECT: PRE {} POST {} DIST {}', spikegen,synpath,dist)
                            #list of connections for further processing if desired.  Assumes one conn per synpath (which might be a problem)
                            postbranch=util.syn_name(synpath,NAME_HEAD)
                            connect_list[postcell][syntype][postbranch]={'postloc':(xpost,ypost,zpost),'pre':precell,'preloc':(xpre,ypre,zpre),'dist':dist, 'prob':prob}
                            log.debug('{}',connect_list[postcell][syntype])
                            #connect the synapse
                            synconn(synpath,dist,spikegen, model.param_syn,netparams.mindelay,netparams.cond_vel)
    return connect_list

