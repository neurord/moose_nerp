"""\
Function definitions for making and connecting populations

1. Creating the population
2. Interconnecting the population
"""
from __future__ import print_function, division
import numpy as np
import moose

from spspine import logutil, extern_conn
log = logutil.Logger()

def create_population(container, netparams):
    netpath = container.path
    proto=[]
    neurXclass={}
    neurons=[]
    #determine total number of neurons
    size=np.ones(len(netparams.grid),dtype=np.int)
    numneurons=1
    for i in range(len(netparams.grid)):
	if netparams.grid[i]['inc']>0:
	    size[i]=np.int((netparams.grid[i]['xyzmax']-netparams.grid[i]['xyzmin'])/netparams.grid[i]['inc'])
        else:
            size[i]=1
	numneurons*=size[i]
    #array of random numbers that will be used to select neuron type
    rannum = np.random.uniform(0,1,numneurons)
    pop_percent=[]
    for neurtype in netparams.pop_dict.keys():
        proto.append(moose.element(neurtype))
        neurXclass[neurtype]=[]
        pop_percent.append(netparams.pop_dict[neurtype].percent)
        #create cumulative array of probabilities for selecting neuron type
    choicearray=np.cumsum(pop_percent)
    #Error check for last element in choicearray equal to 1.0
    log.info("numneurons= {} {} choicarray={} rannum={}", size, numneurons, choicearray, rannum)
    for i,xloc in enumerate(np.linspace(netparams.grid[0]['xyzmin'], netparams.grid[0]['xyzmax'], size[0])):
        for j,yloc in enumerate(np.linspace(netparams.grid[1]['xyzmin'], netparams.grid[1]['xyzmax'], size[1])):
	    for k,zloc in enumerate(np.linspace(netparams.grid[2]['xyzmin'], netparams.grid[2]['xyzmax'], size[2])):
                #for each location in grid, assign neuron type, update soma location, add in spike generator
		neurnumber=i*size[2]*size[1]+j*size[2]+k
		neurtypenum=np.min(np.where(rannum[neurnumber]<choicearray))
                log.info("i,j,k {} {} {} neurnumber {} type {}", i,j,k, neurnumber, neurtypenum)
		typename = proto[neurtypenum].name
		tag = '{}_{}'.format(typename, neurnumber)
		neurons.append(moose.copy(proto[neurtypenum],netpath, tag))
		neurXclass[typename].append(container.path + '/' + tag)
		comp=moose.Compartment(neurons[neurnumber].path + '/soma')
		comp.x=i*xloc
		comp.y=j*yloc
		comp.z=k*zloc
		log.debug("x,ymz={},{},{} {}", comp.x, comp.y, comp.z, neurons[neurnumber].path)
		#spike generator - can this be done to the neuron prototype?
		spikegen = moose.SpikeGen(comp.path + '/spikegen')
                #should these be parameters in netparams?
		spikegen.threshold = 0.0
		spikegen.refractT=1e-3
		m = moose.connect(comp, 'VmOut', spikegen, 'Vm')
    return {'cells': neurons,
            'pop':neurXclass}

def select_entry(table):
    row=np.random.random_integers(0,len(table)-1)
    element=table[row][0]
    table[row][1]-=1
    if table[row][1]==0:
        table[row]=table[len(table)-1]
        table=np.resize(table,len(table)-1)
    return element,table

def connect_neurons(cells, netparams, postype, NumSyn, tt_list=[]):
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
        #set-up array of post-synapse compartments/synchans
        allsyncomp_list=moose.wildcardFind(postcell+'/##[ISA=SynChan]')
        for syntype in post_connections.keys():
            #make a table of possible post-synaptic connections
            #replace with call to create_synpath_array in connection.py
            syncomps=[]
            for syncomp in allsyncomp_list:
                if syncomp.name==syntype:
                    xloc=syncomp.parent.x
                    yloc=syncomp.parent.y
                    dist=np.sqrt(xloc*xloc+yloc*yloc)
                    SynPerComp = distance_mapping(model.NumSyn[syntype], dist)
                    syncomps.append((syncomp.path,SynPerComp))
                    totalsyn+=SynPerComp
            log.debug('SYN TABLE for {} has {} entries and {} synapses', postsoma, len(syncomps),totalsyn)
            for pretype in post_connections[syntype].keys():
                #########if syntype is glu -  need to deal with ampa and nmda (not glu)
                if pretype=='timetable' or pretype=='extern':  #not sure which to use.  Could be two types: both thal and ctx
                    dist=0
                    num_tt=len(tt_list)    #possibly only assign a fraction of totalsyn to each tt_list
                    for i in range(totalsyn):
                        presyn_tt,tt_list=select_entry(tt_list)
                        synpath,syncomps=select_entry(syncomps)
                        log.info('CONNECT: TT {} POST {} DIST {}', presyn_tt,synpath,dist)
                        #connect the time table with mindelay (dist=0)
                    extern_conn.synconn(synpath,dist,presyn_tt,netparams.mindelay)
                else:
                    #loop over pre-synaptic neurons - all types
                    for precell in cells[pretype]:
                        presoma=precell+'/soma'
                        fact=post_connections[syntype][pretype].space_const
                        xpre=moose.element(presoma).x
                        ypre=moose.element(presoma).y
                        #calculate distance between pre- and post-soma
                        dist=np.sqrt((xpre-xpost)**2+(ypre-ypost)**2)
                        prob=np.exp(-(dist/fact))
                        connect=np.random.uniform()
                        log.debug('{} {} {} {} {} {}', presoma,postsoma,dist,fact,prob,connect)
                        #select a random number to determine whether a connection should occur
                        if connect < prob and dist > 0 and len(syncomps)>0:
                            spikegen=moose.wildcardFind(presoma+'/#[TYPE=SpikeGen]')[0]
                            #if so, randomly select a branch, and then eliminate that branch from the table.
                        #presently only a single synapse established.  Need to expand this to allow multiple conns
                        synpath,syncomps=select_entry(syncomps)
                        log.info('CONNECT: PRE {} POST {} DIST {}', spikegen,synpath,dist)
                        postlist.append((synpath,xpost,ypost))
                        prelist.append((presoma,xpre,xpost))
                        distloclist.append((dist,prob))
                        #connect the synapse
                        extern_conn.synconn(synpath,dist,spikegen,netparams.mindelay,netparams.cond_vel)
    return {'post': postlist, 'pre': prelist, 'dist': distloclist}
