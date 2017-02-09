"""\
Other than the special NaF channel, this can be used to create any neuron type.
"""
from __future__ import print_function, division
import os as _os
import moose 
import numpy as np

from spspine import (calcium,
                     chan_proto,
                     spines,
                     syn_proto,
                     util as _util,
                     logutil)
log = logutil.Logger()
NAME_SOMA='soma'

def addOneChan(chanpath,gbar,comp,ghkYN, ghk=None, calciumPermeable=False):
    length=moose.Compartment(comp).length
    diam=moose.Compartment(comp).diameter
    SA=np.pi*length*diam
    if length==0:
        SA=np.pi*diam**2
    proto = moose.element('/library/'+chanpath)
    chan = moose.copy(proto, comp, chanpath)[0]
    chan.Gbar = gbar * SA
    #If we are using GHK AND it is a calcium channel, connect it to GHK
    if ghkYN and calciumPermeable:
        ghk=moose.element(comp.path+'/ghk')
        moose.connect(chan,'permeability',ghk,'addPermeability')
        m=moose.connect(comp,'VmOut',chan,'Vm')
    else:
        m=moose.connect(chan, 'channel', comp, 'channel')
    log.debug('channel message {.path} {.path} {}', chan, comp, m)

def find_morph_file(model):
    return _util.maybe_find_file(model.morph_file,
                                 _os.path.dirname(model.__file__))

def create_neuron(model, ntype, ghkYN):
    p_file = find_morph_file(model)
    try:
        cellproto=moose.loadModel(p_file, ntype)
    except IOError:
        print('could not load model from {!r}'.format(p_file))
        raise
    #######channels
    Cond = model.Condset[ntype]
    for comp in moose.wildcardFind('{}/#[TYPE=Compartment]'.format(ntype)):
        xloc=moose.Compartment(comp).x
        yloc=moose.Compartment(comp).y
        #Possibly this should be replaced by pathlength
        dist=np.sqrt(xloc*xloc+yloc*yloc)
        log.debug('comp {.path} dist {}', comp, dist)
        #
        #If we are using GHK, just create one GHK per compartment, connect it to comp
        #calcium concentration is connected in a different function
        if ghkYN:
            ghkproto=moose.element('/library/ghk')
            ghk=moose.copy(ghkproto,comp,'ghk')[0]
            moose.connect(ghk,'channel',comp,'channel')
        else:
            ghk=[]
        for channame, chanparams in model.Channels.items():
            c = _util.distance_mapping(Cond[channame], dist)
            if c > 0:
                log.debug('Testing Cond If {} {}', channame, c)
                calciumPermeable = chanparams.calciumPermeable
                addOneChan(channame, c, comp, ghkYN, ghk, calciumPermeable=calciumPermeable)
    return cellproto

def neuronclasses(model):
    ##create channels in the library
    chan_proto.chanlib(model)
    syn_proto.synchanlib(model)
    ##now create the neuron prototypes
    neuron={}
    synArray={}
    headArray={}
    caPools = {}
    for ntype in model.neurontypes():
        protoname='/library/'+ntype
        #use morph_file[ntype] for cell-type specific morphology
        #create_neuron creates morphology and ion channels only
        neuron[ntype]=create_neuron(model, ntype, model.ghkYN)
        #optionally add spines
        if model.spineYN:
            headArray[ntype]=spines.addSpines(model, ntype, model.ghkYN,NAME_SOMA)
        #optionally add synapses to dendrites, and possibly to spines
        if model.synYN:
            synArray[ntype] = syn_proto.add_synchans(model, ntype)
        #Calcium concentration - also optional
        #possibly when FS are added will change this to avoid calcium in the FSI
        #This is single tau calcium. 
        #Next step: change model.calYN to caltype, allowing
        #   0: none
        #   1: single tau
        #   2: diffusion, buffering, pumps
        #      this will require many additional function definitions
        caPools[ntype] = calcium.addCalcium(model,ntype)

                
    return synArray,neuron

