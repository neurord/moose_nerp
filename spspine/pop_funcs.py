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

def connect_neurons(cells, netparams, postype, SynPerComp):
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
        #set-up array of post-synapse compartments
        comp_list = moose.wildcardFind(postcell + '/##[TYPE=Compartment]')
        for syntype in post_connections.keys():
            #make a table of possible post-synaptic connections
            #########if syntype is extern - skip, connect time tables in different funciton
            #########if syntype is glu -  need to deal with ampa and nmda (not glu)
            syncomps=[]
            for comp in comp_list:
              for i in range(len(comp.children)):
                  if syntype in comp.children[i].path:
                      #for qq in range(SynPerComp[kk]):  this line incorporates number of synapses per compartment
                      syncomps.append(comp.children[i].path)
            log.debug('SYN TABLE: {} {} {}', len(syncomps), len(comp_list), postsoma)
            for pretype in post_connections[syntype].keys():
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
                        branch=np.random.random_integers(0,len(syncomps)-1)
                        synpath=syncomps[branch]
                        log.info('CONNECT: PRE {} POST {} DIST {}', spikegen,synpath,dist)
                        syncomps[branch]=syncomps[len(syncomps)-1]
                        syncomps=np.resize(syncomps,len(syncomps)-1)
                        postlist.append((synpath,xpost,ypost))
                        prelist.append((presoma,xpre,xpost))
                        distloclist.append((dist,prob))
                        #connect the synapse
                        extern_conn.synconn(synpath,dist,spikegen,netparams.mindelay,netparams.cond_vel)
    return {'post': postlist, 'pre': prelist, 'dist': distloclist}
