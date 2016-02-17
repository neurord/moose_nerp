"""\
Function definitions for making and connecting populations

1. Creating the population
2. Interconnecting the population
"""
from __future__ import print_function, division
from param_sim import printinfo,calcium
import param_cond
import param_chan
import numpy as np
import moose

def create_population(container, neurontypes, sizeX, sizeY, spacing):
    netpath = container.path
    spikegens = []
    proto=[]
    neurXclass=[]
    neurons=[]
    for neur in neurontypes:
        proto.append(moose.element(neur))
        neurXclass.append([])
    #Decide whether to implement a D1 or D2 neuron
    #count how many of each is implemented
    choices=ceil(np.random.uniform(0,1,sizeX*sizeY)-fractionD1)
    for i in range(sizeX):
        for j in range(sizeY):
            number=i*sizeY+j
            neurnum=int(choices[number])
            neurons.append(moose.copy(proto[neurnum],netpath,neurontypes[neurnum]+'_%s' %(number)))
            neurXclass[neurnum].append(container.path+'/'+neurontypes[neurnum]+'_%s' %(number))
            comp=moose.Compartment(neurons[number].path+'/soma')
            comp.x=i*spacing
            comp.y=j*spacing
            if printMoreInfo:
                print("x,y", comp.x, comp.y, neurons[number].path)
            #This new assignment of x and y prevents dist_num from working anymore
            #Must consider this if creating function for variability of all compartments
            #Channel Variance in soma only, for channels with non-zero conductance
            for chan in param_chan.ChanDict:
                if (param_cond.Condset[neurontypes[neurnum]][chan][0] > 0
                    and param_cond.chanvar[chan] > 0):
                    chancomp=moose.element(comp.path+'/'+chan)
                    chancomp.Gbar=chancomp.Gbar*abs(np.random.normal(1.0, chanvar[chan]))
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
    if printinfo:
        print('CONNECT:', postype, spaceConst)
    numSpikeGen = len(spikegen)
    prelist=list()
    postlist=list()
    distloclist=[]
    if printinfo:
        print("SYNAPSES:", numSpikeGen, cells, spikegen)
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
        if printMoreInfo:
            print("SYN TABLE:", len(comps), comps, postsoma)
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
            if printMoreInfo:
                print(precomp,postsoma,dist,fact,prob,connect)
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
                synconn(synpath,dist,spikegen[ii],calcium,mindelay,cond_vel)
    return {'post': postlist, 'pre': prelist, 'dist': distloclist}
