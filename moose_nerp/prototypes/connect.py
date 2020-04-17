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
from moose_nerp.prototypes import plasticity
from moose_nerp.prototypes.util import NamedList

log = logutil.Logger()
CONNECT_SEPARATOR='_to_'

####################### Connections
#for improved NetPyne correspondance: change synapse to synMech, change pre to source
#Two types of probabilities controlling the connections
#A. probability of connecting two different neurons.  NamedList('connect') Parameters include
#A1. constant probability
#A2. space_const: allows distance dependent connection, where distance is measured between pre- and post-synaptic neuron's cell bodies
#A3. num_conns allows a single pre-synaptic cell to make more than one connection on the post-synaptic cell
#B. dend_loc, which controls the dendritic location of post-synaptic target as follows
#mindist, maxdist, half_dist, steep  are alternatives to postsyn_fraction 
#connect_prob=0 if dist<mindist
#connect_prob=0 if dist>maxdist
#connect_prob = probability if dist between mindist and maxdist, or
#if half_dist is defined:
#for steep>0: connect_prob=1 if dist>maxdist and 0 if dist<mindist 
#connect_prob=(dist-mindist)^steep/((dist-mindist)^steep+half_dist^steep)
#make steep<0 to switch slope and have connect_prob=1 if dist<mindist and 0 if dist>maxdist
#do not use steep (or set to zero) to have constant connection probability between min and maxdist

#Intrinsic (within network) connections specified using NamedList('connect')
#Extrinsic (external time table) connections specified using NamedList('ext_connect')
#post syn fraction: what fraction of synapse is contacted by time tables specified in pre
#NOTE:, if multiple pre-synaptic populations, then the sum of those post syn fractions should be <= 1.0

dend_location=NamedList('dend_location','mindist=0 maxdist=1 maxprob=None half_dist=None steep=0 postsyn_fraction=None')

#probability for intrinsic is the probability of connecting pre and post.
connect=NamedList('connect','synapse pre post num_conns=2 space_const=None probability=None dend_loc=None stp=None weight=1')
ext_connect=NamedList('ext_connect','synapse pre post dend_loc=None stp=None weight=1')

def plain_synconn(syn,presyn,syn_delay,weight,simdt=None,stp_params=None):
    sh=moose.element(syn.path)
    jj=sh.synapse.num
    sh.synapse.num = sh.synapse.num+1
    sh.synapse[jj].delay=syn_delay
    sh.synapse[jj].weight=weight
    if weight!=1:
        log.info('SYNAPSE: {} index {} num {} delay {} weight {} tt {}', syn.path, jj, sh.synapse.num, sh.synapse[jj].delay, sh.synapse[jj].weight,presyn.path)
    #It is possible to set the synaptic weight here.
    if presyn.className=='TimeTable':
        msg='eventOut'
    else:
        msg='spikeOut'
    moose.connect(presyn, msg, sh.synapse[jj], 'addSpike')
    if stp_params is not None:
        plasticity.ShortTermPlas(sh.synapse[jj],jj,stp_params,simdt,presyn,msg)

def synconn(synpath,dist,presyn, syn_params ,mindel=1e-3,cond_vel=0.8,simdt=None,stp=None,weight=1):
    if dist:
        syn_delay = max(mindel,np.random.normal(mindel+dist/cond_vel,mindel))
    else:
        syn_delay=mindel
    syn=moose.element(synpath)
    plain_synconn(syn,presyn,syn_delay,weight,simdt=simdt,stp_params=stp)
                
    if syn.parent.name==syn_params.NAME_AMPA:
       nmda_synpath=syn.parent.parent.path+'/'+syn_params.NAME_NMDA+'/'+syn.name
       if moose.exists(nmda_synpath):
           nmda_syn=moose.element(nmda_synpath)
           #probably should add stp for NMDA.  When including desensitization, will be different
           plain_synconn(nmda_syn,presyn,syn_delay,weight)

def select_entry(table):
    row=np.random.random_integers(0,len(table)-1)
    element=table[row][0]
    table[row][1]=int(table[row][1])-1
    if table[row][1]==0: 
        table.pop(row)
    return element

def dendritic_distance_dep_connect_prob(prob,dist):
    #Two possibilites:
    #1. sigmoid increase (if steep>0) or decrease (if steep<0) in probability of synapse with distance from soma
    # sigmoid increases to maximum of maxprob (default=1) between mindist and maxdist
    #dist_prob=maxprob*(distance)**steep/(distance**steepp+half_dist**steep)
    #2. constant probability between mindist and maxdist
    if prob.postsyn_fraction:
        maxprob=prob.postsyn_fraction
    else:
        maxprob=1
    #if prob.steep:
    steep=prob.steep
    #print('maxprob',maxprob,'steep',steep)
    if steep>0:
        if dist<prob.mindist:
            dist_prob=0
        elif dist>prob.maxdist:
            dist_prob=1
        else:
            dist_prob=maxprob*(dist-prob.mindist)**steep/((dist-prob.mindist)**steep+prob.half_dist**steep)
    elif steep<0:
        if dist<prob.mindist:
            dist_prob=1
        elif dist>prob.maxdist:
            dist_prob=0
        else:
            dist_prob=maxprob*prob.half_dist**(-steep)/((dist-prob.mindist)**(-steep)+prob.half_dist**(-steep))
    else:
        if dist<prob.mindist or dist>prob.maxdist:
            dist_prob=0
        else:
            dist_prob=maxprob
        #print('steep==0, dist=', dist,'p=',dist_prob)
    return dist_prob

def create_synpath_array(allsyncomp_list,syntype,NumSyn,prob=None,soma_loc=[0,0,0]):
    #list of possible synapses with connection probability, which takes into account prior creation of synapses
    syncomps=[]
    totalsyns=0
    #print('    CREATE_SYNPATH_ARRAY: syntype:', syntype, 'prob',prob,'soma_loc',soma_loc)
    for syncomp in allsyncomp_list:
        dist,nm=util.get_dist_name(syncomp.parent,soma_loc)
        if prob: #calculate dendritic distance dependent connection probability to store with table
            dist_prob=dendritic_distance_dep_connect_prob(prob,dist)
        else:
            dist_prob=1
        #print('    syncomp',syncomp,'dist',dist,'prob',dist_prob)
        #length of syncomps is the number of synapses available for connections
        #this is the number of synchans * number of synapses per synchan
        #optionally multiply by probably of connecting to that synchan, e.g. based on distance dependence
        #since there may be multiple types of pre-synaptic neurons, reduce length of syncomps if synapses already made
        #
        if dist_prob>0: #only add synchan to list if connection probability is non-zero
            sh=moose.element(syncomp.path+'/SH')
            # TODO: Fix for synapses on spines; there should only be 1 per spine
            if NAME_HEAD in nm:
                SynPerComp = 1 #- sh.numSynapses
            else:
                SynPerComp = util.distance_mapping(NumSyn[syntype], dist)#-sh.numSynapses
            #print('   sh',sh.path,'numSynapses',sh.numSynapses,'synpercomp',SynPerComp,'NumSyn',NumSyn[syntype])
            for i in range(SynPerComp):
                totalsyns+=dist_prob #totalsyns=total synapses to connect
                if i < SynPerComp - sh.numSynapses:
                    syncomps.append([syncomp.path+'/SH',dist_prob])
                    #print('{} synapses already connected of {} total synapses, adding 1 synapse with {} dist_prob to list'.format(sh.numSynapses,SynPerComp,dist_prob))
                else:
                    syncomps.append([syncomp.path+'/SH',0])
                    #print('   {} synapses already connected of {} total, adding 1 syn with 0 prob to list'.format(sh.numSynapses,SynPerComp))

    #normalize probability to pdf
    syncomp_sum = sum([p[1] for p in syncomps])
    #print('CONNECT: totsyns:',totalsyns,'syncomp_sum',syncomp_sum)
    if syncomp_sum >0:
        for syn in syncomps:
            syn[1]=float(syn[1])/syncomp_sum
    else:
        log.info('&&&&&&&&& Un Oh, no synapes remaining on post-synaptic neurons, syncom_sum='.format(syncomp_sum))
    avail_syns=np.int(np.round(syncomp_sum))
    return syncomps,totalsyns,avail_syns

def connect_timetable(post_connection,syncomps,totalsyn,model,mindelay=0):
    dist=0
    syn_params=model.param_syn
    simdt=model.param_sim.simdt
    #tt_list is list of time tables stored with number of times the time table can be used in the network
    tt_list=post_connection.pre.stimtab
    dend_loc=post_connection.dend_loc
    if getattr(model,'stpYN',False):
        stp=post_connection.stp
    else:
        stp=None
    connections={}
    num_choices=np.int(np.round(totalsyn))
    if num_choices>0:
        #if len([sc[0] for sc in syncomps if sc[1]==0.0])<num_choices:
        #    print('@@@@@@@@@@@ connect tt - NEED TO ADJUST POST-SYNAPTIC CONNECTION DISTRIBUTION', len([sc[0] for sc in syncomps if sc[1]==0.0]), 'synapses have 0 connect probability')
        #EDIT: use [sc[0] for sc in syncomps if sc[1]>0.0] if num_choices > those syncomps?
        #randomly select num_choices of synapses without replacement from the entire set
        syn_choices=np.random.choice([sc[0] for sc in syncomps],size=num_choices,replace=False,p=[sc[1] for sc in syncomps])
        #randomly select subset of time-tables for spike train input
        #could do this in one line, but then meaningless error message
        log.info('>>>>>>>>> num_choices {} for {} {} tt remaining {} from',num_choices, post_connection.post,post_connection.synapse,  len(tt_list), post_connection.pre.tablename)
        if len(tt_list)<1000:#2*num_choices:
            print('>>>>>>>>> num_choices {} for {} {} tt remaining {} from'.format(num_choices, post_connection.post,post_connection.synapse,  len(tt_list), post_connection.pre.tablename))
        presyn_tt=[]
        for i,syn in enumerate(syn_choices):
            if len(tt_list)>0:
                presyn_tt.append(select_entry(tt_list))
            else:
                print('table empty',i,syn,tt_list)
        #presyn_tt=[select_entry(tt_list) for syn in syn_choices]
    else:
        syn_choices=[];presyn_tt=[]
        log.info('&&&&&&&&&&&&&& no connectons from time tables'.format(post_connection.pre.tablename))
    #connect the time-table to the synapse with mindelay (set dist=0)
    for tt,syn in zip(presyn_tt,syn_choices):
        postbranch=util.syn_name(moose.element(syn).parent.path,NAME_HEAD)
        log.debug('CONNECT: TT {} POST {}', tt.path,syn)
        synconn(syn,dist,tt,syn_params,mindelay,simdt=simdt,stp=stp,weight=post_connection.weight)
        #save the connection in a dictionary for inspection later.
        if postbranch in connections.keys():
            connections[postbranch].append(tt.path)
        else:
            connections[postbranch]=[tt.path]
    return connections

def timetable_input(cells, netparams, postype, model,soma_loc=[0,0,0]):
    #connect post-synaptic synapses to time tables
    #used for single neuron models only, since populations are connected in connect_neurons
    log.info('CONNECT set: {} {} {}', postype, cells[postype],netparams.connect_dict[postype])
    post_connections=netparams.connect_dict[postype]
    connect_list = {pc:{} for pc in cells[postype]}
    postcell = cells[postype][0]
    for syntype in post_connections.keys():
        connect_list[postcell][syntype]={}
        for pretype in post_connections[syntype].keys():
            if 'extern' in pretype:
                dend_prob=post_connections[syntype][pretype].dend_loc
                print('####### timetable input ######### to',postcell,'from', pretype, ', synchan=', syntype)
                allsyncomp_list=moose.wildcardFind(postcell+'/##/'+syntype+'[ISA=SynChan]')
                syncomps,totalsyn,availsyn=create_synpath_array(allsyncomp_list,syntype,model.param_syn.NumSyn[postype],prob=dend_prob,soma_loc=soma_loc)
                log.info('  SYN TABLE for {} {} has {} slots to make {} synapses from {} ', postcell,syntype, len(syncomps),totalsyn,pretype)
                connect_list[postcell][syntype][pretype]=connect_timetable(post_connections[syntype][pretype],syncomps,availsyn,model)
    return connect_list
                    
def connect_neurons(cells, netparams, postype, model):
    print_cells=3
    print('CONNECT_NEURONS, num cells',len(cells[postype]), ', a few cells', [cl for cl in cells[postype][0:print_cells]])
    log.info('CONNECT set: {} {} {}', postype, cells[postype],netparams.connect_dict[postype])
    post_connections=netparams.connect_dict[postype]
    connect_list = {pc:{} for pc in cells[postype]}
    intra_conns={key:{k:[] for k in post_connections[key].keys()} for key in post_connections.keys()} #accumulate number of connections of each type to calculate mean
    #loop over post-synaptic neurons - convert to list if only singe instance of any type
    if not isinstance(cells[postype],list):
        temp=cells[postype]
        cells[postype]=list([temp])
    synchan_shortage={k:{} for k in post_connections.keys()}
    for ix,postcell in enumerate(cells[postype]):
        postsoma=postcell+'/'+model.param_cond.NAME_SOMA
        xpost=moose.element(postsoma).x
        ypost=moose.element(postsoma).y
        zpost=moose.element(postsoma).z
        connect_list[postcell]['postsoma_loc']=(xpost,ypost,zpost)
        #set-up array of post-synapse compartments/synchans
        for syntype in post_connections.keys():
            synchan_shortage[syntype][postcell]=0
            connect_list[postcell][syntype]={}
            #make a table of possible post-synaptic connections
            for pretype in post_connections[syntype].keys():
                dend_prob=post_connections[syntype][pretype].dend_loc
                allsyncomp_list=moose.wildcardFind(postcell+'/##/'+syntype+'[ISA=SynChan]')
                syncomps,totalsyn,availsyns=create_synpath_array(allsyncomp_list,syntype,model.param_syn.NumSyn[postype],prob=dend_prob,soma_loc=[xpost,ypost,zpost])
                if ix<print_cells:
                    print('    SYN TABLE for {} {} from {} has {} slots and {} synapses avail'.format( postsoma, syntype, pretype,len(syncomps),availsyns))
                if 'extern' in pretype:
                    if ix<print_cells:
                        print('## connect to tt',postcell,syntype,pretype,'from',post_connections[syntype][pretype].pre.filename)
                    ####### connect to time tables instead of other neurons in network
                    connect_list[postcell][syntype][pretype]=connect_timetable(post_connections[syntype][pretype],syncomps,availsyns,model)
                    intra_conns[syntype][pretype].append(np.sum([len(item) for item in connect_list[postcell][syntype][pretype].values()]))
                else:
                    if getattr(model,'stpYN',False):
                        stp=post_connections[syntype][pretype].stp
                    else:
                        stp=None
                    spikegen_conns=[]
                    fact=1;prob=0
                    ###### connect to other neurons in network: loop over pre-synaptic neurons
                    for precell in cells[pretype]:
                        presoma=precell+'/'+model.param_cond.NAME_SOMA
                        xpre=moose.element(presoma).x
                        ypre=moose.element(presoma).y
                        zpre=moose.element(presoma).z
                        dist=np.sqrt((xpre-xpost)**2+(ypre-ypost)**2+(zpre-zpost)**2)
                        if post_connections[syntype][pretype].space_const:
                            fact=post_connections[syntype][pretype].space_const
                            #calculate distance between pre- and post-soma
                            prob=np.exp(-(dist/fact))
                        elif post_connections[syntype][pretype].probability:
                            prob=post_connections[syntype][pretype].probability
                        else:
                            print('need to specify either probability or space constant in param_net for', syntype,pretype)
                        connect=np.random.uniform()
                        log.debug('{} {} {} {} {} {}', presoma,postsoma,dist,fact,prob,connect)
                        #select a random number to determine whether a connection should occur
                        if connect<prob and dist>0:
                            spikegen_conns.append([moose.wildcardFind(presoma+'/#[TYPE=SpikeGen]')[0],(xpre,ypre,zpre),dist])
                    if len(spikegen_conns):
                        num_conn=[max(np.random.poisson(post_connections[syntype][pretype].num_conns),1) for n in spikegen_conns]
                        if ix<print_cells:
                            print('&& connect to neuron', postcell,syntype,'from',pretype,'num conns',num_conn)
                        intra_conns[syntype][pretype].append(np.sum(num_conn))
                        #duplicate spikegens in list to match the length of the list syn_choices to be generated
                        for i in range(len(num_conn)-1,-1,-1):
                            for n in range(num_conn[i]-1):
                                spikegen_conns.insert(i,spikegen_conns[i])
                        num_choices=min(len(spikegen_conns),availsyns)
                        if len(spikegen_conns)>availsyns:
                            if ix<print_cells:
                                print('$$$$$$ uh oh, too few synapses on post-synaptic cell, need',len(spikegen_conns),', avail',availsyns)
                            synchan_shortage[syntype][postcell]=synchan_shortage[syntype][postcell]+len(spikegen_conns)-availsyns
                        #randomly select num_choices of synapses
                        if availsyns==0:
                            if ix<print_cells:
                                print('$$$$$$$$$$$$$$$$ even worse, no available synapses on post-synaptic cell')
                            syn_choices=[]
                        else:
                            syn_choices=np.random.choice([sc[0] for sc in syncomps],size=num_choices,replace=False,p=[sc[1] for sc in syncomps])
                        log.debug('CONNECT: PRE {} POST {} ', spikegen_conns,syn_choices)
                        #connect the pre-synaptic spikegens to randomly chosen synapses
                        #print('** intrinsic synconns',pretype, 'one mindelay',netparams.mindelay[pretype],'all cond',netparams.cond_vel, 'num cons:',len(syn_choices))
                        for i,syn in enumerate(syn_choices):
                                postbranch=util.syn_name(moose.element(syn).parent.path,NAME_HEAD)
                                precell=spikegen_conns[i][0].parent.path.split('/')[2].split('[')[0]
                                connect_list[postcell][syntype][precell+CONNECT_SEPARATOR+postbranch]={'presoma_loc':spikegen_conns[i][1],'dist':np.round(spikegen_conns[i][2],6)}
                                log.debug('{}',connect_list[postcell][syntype])
                                #connect the synapse
                                #print('** intrinsic synconn',i,syn,spikegen_conns[i][2],spikegen_conns[i][0].path)
                                synconn(syn,spikegen_conns[i][2], spikegen_conns[i][0],model.param_syn,netparams.mindelay[pretype],netparams.cond_vel[pretype],stp=stp,weight=post_connections[syntype][pretype].weight)
                    else:
                        intra_conns[syntype][pretype].append(0)
                        if len(cells[pretype]):
                            print('   !!! no pre-synaptic cells selected for',postcell, 'from',pretype, 'connect=',connect,'>? prob=',prob,'or dist=0?',dist)
                        else:
                            print('   !!! no pre-synaptic cells selected for',postcell,' because no', pretype, 'in population')
    for syn in intra_conns.keys():
        tmp=[(pre,np.sum(intra_conns[syn][pre])/float(len(cells[postype]))) for pre in intra_conns[syn].keys()]
        print('*************** number of intra-network connections to',postype, syn,'from\n',intra_conns[syn],'\nmean',tmp)
    print('@@@@@@@@@@@@@@@@@@ summary of synchan shortage for', postype)
    for syn,syn_short in synchan_shortage.items():
        if np.sum(list(syn_short.values()))>0: 
            print(syn,':::',[short for short in syn_short.values()],'mean',np.mean([short for short in syn_short.values()]))
        else:
            print(syn,'::: shortage=0')
    return connect_list,{'intra':intra_conns,'shortage':synchan_shortage}

