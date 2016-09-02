"""\
Function definitions for making and connecting populations

1. Creating the population
2. Interconnecting the population
"""
from __future__ import print_function, division
import numpy as np
import moose

from spspine import param_sim, logutil
log = logutil.Logger()

def create_population(container, netparams):
    netpath = container.path
    spikegens = []
    proto=[]
    neurXclass=[]
    neurons=[]
    #number of neurons
    size=np.ones(len(netparams.grid))
    numneurons=1
    for i in range(len(netparams.grid)):
	if netparams.grid[i]['inc']>0:
	    size[i]=np.int((netparams.grid[i]['xyzmax']-netparams.grid[i]['xyzmin'])/netparams.grid[i]['inc'])
	numneurons*=size[i]
    rannum = np.random.uniform(0,1,numneurons)
    choicearray=[0]
    for neurtype in netparams.pop_dict.keys():
        proto.append(moose.element(neurtype))
        neurXclass.append([])
        #create cumulative array for selecting neuron type - maybe one of Zbyszek's utilities?
	choicearray.append(choicearray[len(choicearray)-1]+netparams.pop_dict[neurtype].percent)
    print(choicearray)
    #probably need to eliminate the 0 element in choice array
    #replace range with something for floats
    for i,xloc in enumerate(range(netparams.grid[0]['xyzmin'], netparams.grid[0]['xyzmax'], netparams.grid[0]['inc'])):
        for j,yloc in enumerate(range(netparams.grid[1]['xyzmin'], netparams.grid[1]['xyzmax'], netparams.grid[1]['inc'])):
	    for k,zloc in enumerate(range(netparams.grid[2]['xyzmin'], netparams.grid[2]['xyzmax'], netparams.grid[2]['inc'])):
		neurnumber=k*num[2]*num[1]+j*num[1]+i
		neurtypenum=np.max(np.where(rannum[neurnumber]<choicearray))
		typename = proto[neurtypenum].name#neurontypes[neurnum]
		tag = '{}_{}'.format(typename, neurnumber)
		neurons.append(moose.copy(proto[neurtypenum],netpath, tag))
		neurXclass[neurnum].append(container.path + '/' + tag)
		comp=moose.Compartment(neurons[number].path + '/soma')
		comp.x=i*xloc
		comp.y=j*yloc
		comp.z=k.zloc
		log.debug("x,ymz={},{},{} {}", comp.x, comp.y, comp.z, neurons[number].path)
		#spike generator
		spikegen = moose.SpikeGen(comp.path + '/spikegen')
		spikegen.threshold = 0.0
		spikegen.refractT=1e-3
		m = moose.connect(comp, 'VmOut', spikegen, 'Vm')
		spikegens.append(spikegen)
    return {'cells': neurons,
            'pop':neurXclass,
            'spikegen': spikegens}

def connect_neurons(spikegen, cells, synchans, spaceConst, SynPerComp,postype):
    log.info('CONNECT: {} {}', postype, spaceConst)
    numSpikeGen = len(spikegen)
    prelist=list()
    postlist=list()
    distloclist=[]
    log.info('SYNAPSES: {} {} {}', numSpikeGen, cells, spikegen)
    #loop over post-synaptic neurons
    for jj in range(len(cells)):
        postsoma=cells[jj]+'/soma'
        xpost=moose.element(postsoma).x
        ypost=moose.element(postsoma).y
        #set-up array of post-synapse compartments
        comps=[]
        for kk in range(len(synchans)):
            p = synchans[kk].path.split('/')
            compname = '/' + p[-2] + '/' + p[-1]
            for qq in range(SynPerComp[kk]):
                comps.append(compname)
        log.debug('SYN TABLE: {} {} {}', len(comps), comps, postsoma)
        #loop over pre-synaptic neurons - all types
        for ii in range(numSpikeGen):
            precomp = os.path.dirname(spikegen[ii].path)
            #################Can be expanded to determine whether an FS neuron also
            fact=spaceConst['same' if postype in precomp else 'diff']
            xpre=moose.element(precomp).x
            ypre=moose.element(precomp).y
            #calculate distance between pre- and post-soma
            dist=np.sqrt((xpre-xpost)**2+(ypre-ypost)**2)
            prob=np.exp(-(dist/fact))
            connect=np.random.uniform()
            log.debug('{} {} {} {} {} {}', precomp,postsoma,dist,fact,prob,connect)
            #select a random number to determine whether a connection should occur
            if connect < prob and dist > 0 and len(comps)>0:
                #if so, randomly select a branch, and then eliminate that branch from the table.
                #presently only a single synapse established.  Need to expand this to allow mutliple conns
                branch=np.random.random_integers(0,len(comps)-1)
                synpath=cells[jj]+comps[branch]
                comps[branch]=comps[len(comps)-1]
                comps=resize(comps,len(comps)-1)
                #print "    POST:", synpath, xpost,ypost,"PRE:", precomp, xpre, ypre
                postlist.append((synpath,xpost,ypost))
                prelist.append((precomp,xpre,xpost))
                distloclist.append((dist,prob))
                #connect the synapse
                synconn(synpath,dist,spikegen[ii],param_sim.calcium,mindelay,cond_vel)
    return {'post': postlist, 'pre': prelist, 'dist': distloclist}
