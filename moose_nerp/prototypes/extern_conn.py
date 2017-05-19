"""\
Function definitions for connecting timetables to neurons

"""
from __future__ import print_function, division
import numpy as np
import moose

from moose_nerp.prototypes import logutil
log = logutil.Logger()

def connect_timetable(post_connection,syncomps,totalsyn,netparams):
    tt_list=post_connection.pre.stimtab
    postsyn_fraction=post_connection.postsyn_fraction
    num_tt=len(tt_list)    
    for i in range(totalsyn*postsyn_fraction):
        presyn_tt,tt_list=select_entry(tt_list)
        synpath,syncomps=select_entry(syncomps)
        log.info('CONNECT: TT {} POST {} DIST {}', presyn_tt,synpath,dist)
        #connect the time table with mindelay (dist=0)
        synconn(synpath,dist,presyn_tt,netparams.mindelay)
    return syncomps

def addinput(cells, netparams, postype, NumSyn):
    #connect post-synaptic synapses to time tables
    #used for single neuron models, since populations are connected in connect_neurons
    log.debug('CONNECT set: {} {} {}', postype, cells[postype],netparams.connect_dict[postype])
    post_connections=netparams.connect_dict[postype]
    for postcell in cells[postype]:
        postsoma=postcell+'/soma'
        allsyncomp_list=moose.wildcardFind(postcell+'/##[ISA=SynChan]')
        for syntype in post_connections.keys():
            syncomps,totalsyn=create_synpath_array(allsyncomp_list,syntype,NumSyn)
            log.info('SYN TABLE for {} {} has {} compartments and {} synapses', postsoma, syntype, len(syncomps),totalsyn)
            for pretype in post_connections[syntype].keys():
                if pretype=='timetable' or pretype=='extern':
                    
        #all synpases in synlist must in same compartment (e.g. both on spines or both on dendrites)
    log.info('cells {} {} syn/Comp {}', len(cells), cells, SynPerComp)
    #create table of synapse compartments for each neuron
    comps=[]
    Duptt=ttab['Dup']
    Uniqtt=ttab['Uniq']
    delay=0   #no need for delay for time table inputs

    for kk in range(len(synchans[synlist[0]])):
        p = synchans[synlist[0]][kk].path.split('/')
        compname = '/' + p[model.compNameNum]
        log.debug('{} {}', kk, SynPerComp[kk])
        if param_sim.spineYesNo:
            comps.append(compname + '/' + p[model.SpineParams.spineNameNum])
        else:
            for qq in range(SynPerComp[kk]):
                comps.append(compname)
        log.debug('comps: {}', comps)
    allcomps=np.tile(comps,(len(cells),1))
    remainingcomps=[len(comps) for ii in range(len(cells))]
    log.info('Remaing comps to connect {} {}', remainingcomps, np.shape(allcomps))
    #
    #loop through duplicates and connect them to a compartment in each neuron
    for train in range(len(Duptt)):
        tt=moose.TimeTable(Duptt[train])
        for cell in range(len(cells)):
            postneur=cells[cell]
            branch=np.random.random_integers(0,remainingcomps[cell]-1)
            synpath=postneur+allcomps[cell][branch]
            remainingcomps[cell]=remainingcomps[cell]-1
            allcomps[cell][branch]=allcomps[cell][remainingcomps[cell]]
            allcomps[cell][remainingcomps[cell]]=''
            log.debug('CONNECT: {} {} {} {} {}',
                      branch, tt.path, cells[cell].path, remainingcomps, synpath)
            log.debug(allcomps)
            for chan in synlist:
                synconn(synpath+'/'+chan,dist,tt,param_sim.calcium,delay)
    #loop through unique trains and connect them to one comp in one neuron
    TotalTrains=0
    for train in range(startt,len(Uniqtt)):
        if sum(remainingcomps)>0:
            TotalTrains+=1
            tt=moose.TimeTable(Uniqtt[train])
            br=np.random.random_integers(0,sum(remainingcomps)-1)
            cumcomps=np.array([int(sum(remainingcomps[0:x])) for x in np.arange(1,len(remainingcomps)+1)])
            cell=int(np.min(np.where(cumcomps>br)))
            postneur=cells[cell]
            if cell > 0:
                branch=br-cumcomps[cell-1]
            else:
                branch=br
            log.debug('{}'*7, br, sum(remainingcomps), cumcomps, np.where(cumcomps>br), cell, branch,allcomps[cell][branch])
            synpath=postneur+allcomps[cell][branch]
            remainingcomps[cell]=remainingcomps[cell]-1
            allcomps[cell][branch]=allcomps[cell][remainingcomps[cell]]
            allcomps[cell][remainingcomps[cell]]=''
            log.debug('CONNECT: {} {} {} {} {} {}',
                      br, branch, cumcomps, remainingcomps, tt.path, synpath)
            for chan in synlist:
                synconn(synpath+'/'+chan,0,tt,param_sim.calcium,delay)
        else:
            #print "out of synpases"
            break
            #don't do anything. I don't think this break is exiting the loop
    return len(Uniqtt)
