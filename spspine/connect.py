"""\
Function definitions for connecting populations of neurons
1. single synaptic connection
2. creating an array of post-synaptic channels, to randomly select without replacement
3. connect each post-syn channel type of each neuron to either a pre-synaptic neuron or a timetable
4. functions to load time tables

"""

from __future__ import print_function, division
import numpy as np
import moose

from spspine import logutil, util
log = logutil.Logger()

AMPAname='ampa'
NMDAname='nmda'

def plain_synconn(synchan,presyn,syn_delay):
    shname=synchan.path+'/SH'
    sh=moose.SimpleSynHandler(shname)
    if sh.synapse.num==1:
        moose.connect(sh, 'activationOut', synchan, 'activation')
    jj=sh.synapse.num
    sh.synapse.num = sh.synapse.num+1
    sh.synapse[jj].delay=syn_delay
    log.debug('SYNAPSE: {} {} {} {}', synchan.path, jj, sh.synapse.num, sh.synapse[jj].delay)
    #It is possible to set the synaptic weight here.
    m = moose.connect(presyn, 'spikeOut', sh.synapse[jj], 'addSpike')
    return

def synconn(synpath,dist,presyn_path,mindel=1e-3,cond_vel=0.8):
    presyn=moose.element(presyn_path)
    if dist:
        syn_delay = max(mindel,np.random.normal(mindel+dist/cond_vel,mindel))
    else:
        syn_delay=mindel
    synchan=moose.element(synpath)
    plain_synconn(synchan,presyn,syn_delay)
                
    if synchan.name==AMPAname:
       nmda_synpath=synchan.parent+NMDAname
       nmda_synchan=moose.element(nmda_synpath)# - check for existance
       plain_synconn(nmda_synchan,presyn,syn_delay)
    return

def select_entry(table):
    row=np.random.random_integers(0,len(table)-1)
    element=table[row][0]
    table[row][1]=int(table[row][1])-1
    if table[row][1]==0: 
        table[row]=table[len(table)-1]
        table=np.resize(table,(len(table)-1,2))
    return element,table

def select_tt(table,fraction):
    row=np.random.random_integers(0,len(table)-1)
    element=table[row]
    #only remove a fraction of time tables, allow re-use of the duplicate fraction
    if np.random.uniform()>fraction:
        table[row]=table[len(table)-1]
        table=np.resize(table,(len(table)-1))
    return element,table

def create_synpath_array(allsyncomp_list,syntype,NumSyn):
    syncomps=[]
    totalsyn=0
    for syncomp in allsyncomp_list:
        if syncomp.name==syntype:
            xloc=syncomp.parent.x
            yloc=syncomp.parent.y
            dist=np.sqrt(xloc*xloc+yloc*yloc)
            SynPerComp = util.distance_mapping(NumSyn[syntype], dist)
            syncomps.append([syncomp.path,SynPerComp])
            totalsyn+=SynPerComp
    return syncomps,totalsyn

def connect_neurons(cells, netparams, postype, NumSyn):
    log.info('CONNECT set: {} {} {}', postype, cells[postype],netparams.connect_dict[postype])
    post_connections=netparams.connect_dict[postype]
    log.debug('CONNECT set: {} {}', postype, cells[postype])
    prelist=list()
    postlist=list()
    distloclist=[]
    #loop over post-synaptic neurons
    for postcell in cells[postype]:
        postsoma=postcell+'/soma'
        xpost=moose.element(postsoma).x
        ypost=moose.element(postsoma).y
        zpost=moose.element(postsoma).z
        #set-up array of post-synapse compartments/synchans
        allsyncomp_list=moose.wildcardFind(postcell+'/##[ISA=SynChan]')
        for syntype in post_connections.keys():
            #make a table of possible post-synaptic connections
            syncomps,totalsyn=create_synpath_array(allsyncomp_list,syntype,NumSyn)
            log.info('SYN TABLE for {} {} has {} compartments and {} synapses', postsoma, syntype, len(syncomps),totalsyn)
            for pretype in post_connections[syntype].keys():
                if pretype=='timetable' or pretype=='extern':  #not sure which to use.  Could be two types: both thal and ctx
                    ####### connect to time tables instead of other neurons in network
                    tt_list=post_connections[syntype][pretype].pre.stimtab
                    fraction_duplicate=post_connections[syntype][pretype].fraction_duplicat
                    dist=0
                    num_tt=len(tt_list)    #possibly only assign a fraction of totalsyn to each tt_list
                    for i in range(totalsyn):
                        presyn_tt,tt_list=select_tt(tt_list,fraction_duplicate)
                        synpath,syncomps=select_entry(syncomps)
                        log.info('CONNECT: TT {} POST {} DIST {}', presyn_tt,synpath,dist)
                        #connect the time table with mindelay (dist=0)
                        synconn(synpath,dist,presyn_tt,netparams.mindelay)
                else:
                    ###### connect to other neurons in network: loop over pre-synaptic neurons
                    for precell in cells[pretype]:
                        presoma=precell+'/soma'
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
                            synpath,syncomps=select_entry(syncomps)
                            log.info('CONNECT: PRE {} POST {} DIST {}', spikegen,synpath,dist)
                            #make this one list? of dictionaries (to know what each value means)
                            postlist.append((synpath,xpost,ypost,zpost))
                            prelist.append((presoma,xpre,ypre,zpre))
                            distloclist.append((dist,prob))
                            #connect the synapse
                            synconn(synpath,dist,spikegen,netparams.mindelay,netparams.cond_vel)
    return {'post': postlist, 'pre': prelist, 'dist': distloclist}

