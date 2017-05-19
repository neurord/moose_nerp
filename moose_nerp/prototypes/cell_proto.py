"""\
Other than the special NaF channel, this can be used to create any neuron type.
"""
from __future__ import print_function, division
import os as _os
import moose 
import numpy as np

from moose_nerp.prototypes import (calcium,
                     chan_proto,
                     spines,
                     syn_proto,
                     add_channel,
                     util as _util,
                     logutil
                     )

log = logutil.Logger()

def find_morph_file(model, ntype):
    return _util.find_model_file(model, model.morph_file[ntype])

def create_neuron(model, ntype, ghkYN):
    p_file = find_morph_file(model,ntype)
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
            c = _util.distance_mapping(Cond[channame], comp)
            if c > 0:
                log.debug('Testing Cond If {} {}', channame, c)
                calciumPermeable = chanparams.calciumPermeable
                add_channel.addOneChan(channame, c, comp, ghkYN, ghk, calciumPermeable=calciumPermeable)
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
            headArray[ntype]=spines.addSpines(model, ntype, model.ghkYN, model.param_cond.NAME_SOMA)
        #optionally add synapses to dendrites, and possibly to spines
        if model.synYN:
            synArray[ntype] = syn_proto.add_synchans(model, ntype)
        #Calcium concentration - also optional
        #   0: none
        #   1: single tau
        #   2: diffusion, buffering, pumps
        #      this will require many additional function definitions
        if model.calYN:
            caPools[ntype] = calcium.addCalcium(model,ntype)

    return synArray,neuron
