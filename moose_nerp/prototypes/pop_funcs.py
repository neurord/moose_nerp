"""\
Function definitions for making populations of neurons

"""
from __future__ import print_function, division
import numpy as np
import moose

from moose_nerp.prototypes import logutil, util
log = logutil.Logger()

def count_neurons(netparams):
    size=np.ones(len(netparams.grid),dtype=np.int)
    length=np.ones(len(netparams.grid),dtype=np.float)
    numneurons=1
    volume=1
    for i in range(len(netparams.grid)):
        if netparams.grid[i]['inc']>0:
            length[i]=netparams.grid[i]['xyzmax']-netparams.grid[i]['xyzmin']
            size[i]=np.int(np.ceil(length[i]/netparams.grid[i]['inc']))
        numneurons*=size[i]
        volume*=length[i]
    return size, numneurons, volume

def create_population(container, netparams, name_soma):
    netpath = container.path
    proto=[]
    neurXclass={}
    locationlist=[]
    #determine total number of neurons
    size,numneurons,vol=count_neurons(netparams)
    pop_percent=[]
    for neurtype in netparams.pop_dict.keys():
        if moose.exists(neurtype):
            proto.append(moose.element(neurtype))
            neurXclass[neurtype]=[]
            pop_percent.append(netparams.pop_dict[neurtype].percent)
    #create cumulative array of probabilities for selecting neuron type
    choicearray=np.cumsum(pop_percent)
    if choicearray[-1]<1.0:
        log.info("Warning!!!! fractional populations sum to {}",choicearray[-1])
    #array of random numbers that will be used to select neuron type
    rannum = np.random.uniform(0,choicearray[-1],numneurons)
    #Error check for last element in choicearray equal to 1.0
    log.info("numneurons= {} {} choicarray={}", size, numneurons, choicearray)
    log.debug("rannum={}", rannum)
    for i,xloc in enumerate(np.linspace(netparams.grid[0]['xyzmin'], netparams.grid[0]['xyzmax'], size[0])):
        for j,yloc in enumerate(np.linspace(netparams.grid[1]['xyzmin'], netparams.grid[1]['xyzmax'], size[1])):
            for k,zloc in enumerate(np.linspace(netparams.grid[2]['xyzmin'], netparams.grid[2]['xyzmax'], size[2])):
                #for each location in grid, assign neuron type, update soma location, add in spike generator
                neurnumber=i*size[2]*size[1]+j*size[2]+k
                neurtypenum=np.min(np.where(rannum[neurnumber]<choicearray))
                log.debug("i,j,k {} {} {} neurnumber {} type {}", i,j,k, neurnumber, neurtypenum)
                typename = proto[neurtypenum].name
                tag = '{}_{}'.format(typename, neurnumber)
                new_neuron=moose.copy(proto[neurtypenum],netpath, tag)
                neurXclass[typename].append(container.path + '/' + tag)
                #update all coordinates of the neuron - add same value to x,y,z,x0,y0,z0 of all compartments
                util.move_neuron(xloc,yloc,zloc,new_neuron.path)
                comp=moose.element(new_neuron.path + '/'+name_soma)
                log.debug("x,y,z={},{},{} for {}", comp.x, comp.y, comp.z, new_neuron.path)
                locationlist.append([new_neuron.name,comp.x,comp.y,comp.z])
                #spike generator - can this be done to the neuron prototype?
                spikegen = moose.SpikeGen(comp.path + '/spikegen')
                #should these be parameters in netparams?
                spikegen.threshold = 0.0
                spikegen.refractT=1e-3
                m = moose.connect(comp, 'VmOut', spikegen, 'Vm')
    #Create variability in neurons of network
    for neurtype in netparams.chanvar.keys():
        for chan,var in netparams.chanvar[neurtype].items():
            #single multiplier for Gbar for all the channels compartments
            if var>0 and len(neurXclass[neurtype]):
                log.info('adding variability to {} soma {}, variance: {}', neurtype,chan, var)
                GbarArray=abs(np.random.normal(1.0, var, len(neurXclass[neurtype])))
                for ii,neurname in enumerate(neurXclass[neurtype]):
                    soma_chan_path=neurname+'/'+name_soma+'/'+chan
                    if moose.exists(soma_chan_path):
                        chancomp=moose.element(soma_chan_path)
                        chancomp.Gbar=chancomp.Gbar*GbarArray[ii]
    #
    return {'location': locationlist,
            'pop':neurXclass}
