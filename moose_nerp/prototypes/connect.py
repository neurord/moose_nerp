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

log = logutil.Logger()
CONNECT_SEPARATOR='_to_'

def plain_synconn(syn,presyn,syn_delay,weight,simdt=None,stp_params=None):
    sh=moose.element(syn.path)
    jj=sh.synapse.num
    sh.synapse.num = sh.synapse.num+1
    sh.synapse[jj].delay=syn_delay
    sh.synapse[jj].weight=weight
    if weight!=1:
        print('SYNAPSE: {} index {} num {} delay {} weight {} tt {}'.format( syn.path, jj, sh.synapse.num, sh.synapse[jj].delay, sh.synapse[jj].weight,presyn.path))
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
    return dist_prob

def create_synpath_array(allsyncomp_list,syntype,NumSyn,prob=None):
    #list of possible synapses with connection probability, which takes into account prior creation of synapses
    syncomps=[]
    totalsyns=0
    print('CONNECT: syntype:', syntype, 'prob',prob)
    for syncomp in allsyncomp_list:
        dist,nm=util.get_dist_name(syncomp.parent)
        if prob: #calculate dendritic distance dependent connection probability to store with table
            dist_prob=dendritic_distance_dep_connect_prob(prob,dist)
        else:
            dist_prob=1
        #print('syncomp',syncomp,'dist',dist,'prob',dist_prob)
        if dist_prob>0: #only add synchan to list if connection probability is non-zero
            sh=moose.element(syncomp.path+'/SH')
            # TODO: Fix for synapses on spines; there should only be 1 per spine
            if NAME_HEAD in nm:
                SynPerComp = 1 #- sh.numSynapses
            else:
                SynPerComp = util.distance_mapping(NumSyn[syntype], dist)#-sh.numSynapses
            for i in range(SynPerComp):
                totalsyns+=dist_prob #totalsyns=total synapses to connect
                if i < SynPerComp - sh.numSynapses:
                    syncomps.append([syncomp.path+'/SH',dist_prob])
                    #print('{} synapses already connected of {} total synapses, adding 1 synapse with {} dist_prob to list'.format(sh.numSynapses,SynPerComp,dist_prob))
                else:
                    syncomps.append([syncomp.path+'/SH',0])
                    #print('{} synapses already connected of {} total synapses, adding 1 synapse with 0 dist_prob to list'.format(sh.numSynapses,SynPerComp))

    #normalize probability to pdf
    syncomp_sum = sum([p[1] for p in syncomps])
    print('CONNECT: totsyns:',totalsyns,'syncomp_sum',syncomp_sum)
    for syn in syncomps:
        syn[1]=float(syn[1])/syncomp_sum
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
        #randomly select num_choices of synapses without replacement from the entire set
        syn_choices=np.random.choice([sc[0] for sc in syncomps],size=num_choices,replace=False,p=[sc[1] for sc in syncomps])
        #randomly select subset of time-tables for spike train input
        #could do this in one line, but then meaningless error message
        presyn_tt=[]
        for i,syn in enumerate(syn_choices):
            if len(tt_list)>0:
                presyn_tt.append(select_entry(tt_list))
            else:
                print('table empty',i,syn,tt_list)
        #presyn_tt=[select_entry(tt_list) for syn in syn_choices]
        print('## connect from tt',post_connection.pre.tablename,', number of connections',len(presyn_tt))
    else:
        syn_choices=[];presyn_tt=[]
        print('&& no connectons from time tables',post_connection.pre.tablename)
    #connect the time-table to the synapse with mindelay (set dist=0)
    for tt,syn in zip(presyn_tt,syn_choices):
        postbranch=util.syn_name(moose.element(syn).parent.path,NAME_HEAD)
        log.debug('CONNECT: TT {} POST {}', tt.path,syn)
        synconn(syn,dist,tt,syn_params,mindelay,simdt=simdt,stp=stp,weight=post_connection.weight)
        #save the connection in a dictionary for inspection later
        connections[postbranch]=tt.path
    return connections

def timetable_input(cells, netparams, postype, model):
    #connect post-synaptic synapses to time tables
    #used for single neuron models only, since populations are connected in connect_neurons
    log.info('CONNECT set: {} {} {}', postype, cells[postype],netparams.connect_dict[postype])
    post_connections=netparams.connect_dict[postype]
    connect_list = {pc:{} for pc in cells[postype]}
    postcell = cells[postype][0]
    for syntype in post_connections.keys():
        connect_list[postcell][syntype]={}
        for pretype in post_connections[syntype].keys():
            dend_prob=post_connections[syntype][pretype].dend_loc
            print('################',postcell, 'synchan:',syntype,'pretype:',pretype)
            allsyncomp_list=moose.wildcardFind(postcell+'/##/'+syntype+'[ISA=SynChan]')
            print('CREATE_SYNPATH_ARRAY from timetable_input, pre=', pretype)
            syncomps,totalsyn,availsyn=create_synpath_array(allsyncomp_list,syntype,model.param_syn.NumSyn[postype],prob=dend_prob)
            log.info('SYN TABLE for {} {} has {} compartments to make {} synapses', postcell,syntype, len(syncomps),totalsyn)
            if 'extern' in pretype:
                print('## connect to tt',postcell,syntype,pretype)
                connect_list[postcell][syntype][pretype]=connect_timetable(post_connections[syntype][pretype],syncomps,totalsyn,model)
    return connect_list
                    
def connect_neurons(cells, netparams, postype, model):
    log.info('CONNECT set: {} {} {}', postype, cells[postype],netparams.connect_dict[postype])
    post_connections=netparams.connect_dict[postype]
    connect_list = {pc:{} for pc in cells[postype]}
    intra_conns={key:[] for key in post_connections.keys()} #accumulate number of connections of each type to calculate mean
    #loop over post-synaptic neurons - convert to list if only singe instance of any type
    if not isinstance(cells[postype],list):
        temp=cells[postype]
        cells[postype]=list([temp])
    for postcell in cells[postype]:
        postsoma=postcell+'/'+model.param_cond.NAME_SOMA
        xpost=moose.element(postsoma).x
        ypost=moose.element(postsoma).y
        zpost=moose.element(postsoma).z
        connect_list[postcell]['postsoma_loc']=(xpost,ypost,zpost)
        #set-up array of post-synapse compartments/synchans
        for syntype in post_connections.keys():
            connect_list[postcell][syntype]={}
            #make a table of possible post-synaptic connections
            for pretype in post_connections[syntype].keys():
                dend_prob=post_connections[syntype][pretype].dend_loc
                allsyncomp_list=moose.wildcardFind(postcell+'/##/'+syntype+'[ISA=SynChan]')
                print('CREATE_SYNPATH_ARRAY from connect_neurons, pre=', pretype)
                syncomps,totalsyn,availsyns=create_synpath_array(allsyncomp_list,syntype,model.param_syn.NumSyn[postype],prob=dend_prob)
                log.info('SYN TABLE for {} {} {} has {} compartments and {} synapses', postsoma, syntype, pretype,len(syncomps),totalsyn)
                if 'extern' in pretype:
                    print('## connect to tt',postcell,syntype,pretype)
                    ####### connect to time tables instead of other neurons in network
                    connect_list[postcell][syntype][pretype]=connect_timetable(post_connections[syntype][pretype],syncomps,totalsyn,model)
                    intra_conns[syntype].append(len(connect_list[postcell][syntype][pretype]))
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
                        print('&& connect to neuron', postcell,syntype,'from',pretype,'num conns',num_conn)
                        intra_conns[syntype].append(np.sum(num_conn))
                        #duplicate spikegens in list to match the length of the list syn_choices to be generated
                        for i in range(len(num_conn)-1,-1,-1):
                            for n in range(num_conn[i]-1):
                                spikegen_conns.insert(i,spikegen_conns[i])
                        num_choices=min(len(spikegen_conns),availsyns)
                        if len(spikegen_conns)>availsyns:
                            print('>>>> uh oh, too few synapses on post-synaptic cell')
                        #randomly select num_choices of synapses
                        if availsyns==0:
                            print('>>>>>>>>>>> uh oh, no available synapses on post-synaptic cell')
                            syn_choices=[]
                        else:
                            syn_choices=np.random.choice([sc[0] for sc in syncomps],size=num_choices,replace=False,p=[sc[1] for sc in syncomps])
                        log.debug('CONNECT: PRE {} POST {} ', spikegen_conns,syn_choices)
                        #connect the pre-synaptic spikegens to randomly chosen synapses
                        print('** intrinsic synconn',pretype, 'one mindelay',netparams.mindelay[pretype],'all cond',netparams.cond_vel)
                        for i,syn in enumerate(syn_choices):
                                postbranch=util.syn_name(moose.element(syn).parent.path,NAME_HEAD)
                                precell=spikegen_conns[i][0].parent.path.split('/')[2].split('[')[0]
                                connect_list[postcell][syntype][precell+CONNECT_SEPARATOR+postbranch]={'presoma_loc':spikegen_conns[i][1],'dist':np.round(spikegen_conns[i][2],6)}
                                log.debug('{}',connect_list[postcell][syntype])
                                #connect the synapse
                                #print('** intrinsic synconn',i,syn,spikegen_conns[i][2],spikegen_conns[i][0].path)
                                synconn(syn,spikegen_conns[i][2], spikegen_conns[i][0],model.param_syn,netparams.mindelay[pretype],netparams.cond_vel[pretype],stp=stp,weight=post_connections[syntype][pretype].weight)
                    else:
                        print('   no pre-synaptic cells selected for',postcell, 'from',pretype)
    tmp=[np.mean(intra_conns[syn])/len(cells[postype]) for syn in intra_conns.keys()]                                     
    print('mean number of intra-network connections', intra_conns,tmp)
    return connect_list

