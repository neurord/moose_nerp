#cell_proto.py
"""\
Other than the special NaF channel, this can be used to create any neuron type.
"""
from __future__ import print_function, division
import os as _os
from spspine import util as _util
import moose 
import numpy as np
from param_sim import printMoreInfo
import param_cond
import param_chan
import param_ca_plas
from param_spine import SpineParams
import chan_proto
import syn_proto
import spines
import calcium

def addOneChan(chanpath,gbar,comp,ghkYN,ghk=None):
    length=moose.Compartment(comp).length
    diam=moose.Compartment(comp).diameter
    SA=np.pi*length*diam
    proto = moose.element('/library/'+chanpath)
    chan = moose.copy(proto, comp, chanpath)[0]
    chan.Gbar = gbar * SA
    #If we are using GHK AND it is a calcium channel, connect it to GHK
    if ghkYN and param_cond.isCaChannel(chanpath):
        ghk=moose.element(comp.path+'/ghk')
        moose.connect(chan,'permeability',ghk,'addPermeability')
        m=moose.connect(comp,'VmOut',chan,'Vm')
    else:
        m=moose.connect(chan, 'channel', comp, 'channel')
    if printMoreInfo:
        print("channel message", chan.path,comp.path, m)
    return

def create_neuron(p_file,container,Cond,ghkYN):
    p_file = _util.maybe_find_file(p_file, '.', _os.path.dirname(__file__))
    try:
        cellproto=moose.loadModel(p_file, container)
    except IOError:
        print('could not load model from {!r}'.format(p_file))
        raise
    comps=[]
    #######channels
    for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(container)):
        comps.append(comp)
        xloc=moose.Compartment(comp).x
        yloc=moose.Compartment(comp).y
        #Possibly this should be replaced by pathlength
        dist=np.sqrt(xloc*xloc+yloc*yloc)
        if printMoreInfo:
            print("comp,dist",comp.path,dist)
        #
        #If we are using GHK, just create one GHK per compartment, connect it to comp
        #calcium concentration is connected in a different function
        if ghkYN:
            ghkproto=moose.element('/library/ghk')
            ghk=moose.copy(ghkproto,comp,'ghk')[0]
            moose.connect(ghk,'channel',comp,'channel')
        else:
            ghk=[]
        for chanpath in param_chan.ChanDict:
            if Cond[chanpath][_util.dist_num(param_cond.distTable, dist)]:
                if printMoreInfo:
                    print("Testing Cond If", chanpath, Cond[chanpath][_util.dist_num(param_cond.distTable, dist)])
                addOneChan(chanpath,Cond[chanpath][_util.dist_num(param_cond.distTable, dist)],comp, ghkYN, ghk)
    return {'comps': comps, 'cell': cellproto}

def neuronclasses(plotchan,plotpow,calyesno,synYesNo,spYesNo,ghkYN):
    ##create channels in the library
    chan_proto.chanlib(plotchan,plotpow)
    syn_proto.synchanlib(ghkYN,calyesno)
    ##now create the neuron prototypes
    neuron={}
    synArray={}
    numSynArray={}
    caPools={}
    headArray={}
    for ntype in param_cond.neurontypes:
        protoname='/library/'+ntype
        #use morph_file[ntype] for cell-type specific morphology
        #create_neuron creates morphology and ion channels only
        neuron[ntype]=create_neuron(param_cond.morph_file,ntype,param_cond.Condset[ntype],ghkYN)
        #optionally add spines
        if spYesNo:
            headArray[ntype]=spines.addSpines(ntype,ghkYN)
        #optionally add synapses to dendrites, and possibly to spines
        if synYesNo:
            numSynArray[ntype], synArray[ntype] = syn_proto.add_synchans(ntype, calyesno, ghkYN)
        caPools[ntype]=[]
    #Calcium concentration - also optional
    #possibly when FS are added will change this to avoid calcium in the FSI
    #This is single tau calcium. 
    #Next step: change calyesno to caltype, allowing
    #   0: none
    #   1: single tau
    #   2: diffusion, buffering, pumps
    #      this will require many additional function definitions
    if calyesno:
        calcium.CaProto(param_ca_plas.CaThick,param_ca_plas.CaBasal,param_ca_plas.CaTau,param_ca_plas.caName)
        for ntype in param_cond.neurontypes:
            for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(ntype)):
                capool=calcium.addCaPool(comp,param_ca_plas.caName)
                caPools[ntype].append(capool)
                calcium.connectVDCC_KCa(ghkYN,comp,capool)
            #if there are spines, calcium will be added to the spine head
            if spYesNo:
                for spcomp in headArray[ntype]:
                    capool=calcium.addCaPool(spcomp,param_ca_plas.caName)
                    if SpineParams.spineChanList:
                        calcium.connectVDCC_KCa(ghkYN,spcomp,capool)
            #if there are synapses, NMDA will be connected to set of calcium pools
            if synYesNo:
                calcium.connectNMDA(synArray[ntype]['nmda'],param_ca_plas.caName,ghkYN)
    return synArray,neuron,caPools,numSynArray,headArray
