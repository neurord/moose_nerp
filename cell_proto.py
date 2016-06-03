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
import param_cond as parcond
import param_chan as parchan
import param_ca_plas as parcal
import param_spine as parsp
import chan_proto as chan
import syn_proto as syn
import spines as sp
import calcium as cal

def addOneChan(chanpath,gbar,comp,ghkYN,ghk=None):
    length=moose.Compartment(comp).length
    diam=moose.Compartment(comp).diameter
    SA=np.pi*length*diam
    proto = moose.element('/library/'+chanpath)
    chan = moose.copy(proto, comp, chanpath)[0]
    chan.Gbar = gbar * SA
    #If we are using GHK AND it is a calcium channel, connect it to GHK
    if (ghkYN and parcond.isCaChannel(chanpath)):
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
        for chanpath in parchan.ChanDict:
            if Cond[chanpath][_util.dist_num(parcond.distTable, dist)]:
                if printMoreInfo:
                    print("Testing Cond If", chanpath, Cond[chanpath][_util.dist_num(parcond.distTable, dist)])
                addOneChan(chanpath,Cond[chanpath][_util.dist_num(parcond.distTable, dist)],comp, ghkYN, ghk)
    return {'comps': comps, 'cell': cellproto}

def neuronclasses(plotchan,plotpow,calyesno,synYesNo,spYesNo,ghkYN):
    ##create channels in the library
    chan.chanlib(plotchan,plotpow)
    syn.synchanlib(ghkYN,calyesno)
    ##now create the neuron prototypes
    neuron={}
    synArray={}
    numSynArray={}
    caPools={}
    headArray={}
    for ntype in parcond.neurontypes:
        protoname='/library/'+ntype
        #use morph_file[ntype] for cell-type specific morphology
        #create_neuron creates morphology and ion channels only
        neuron[ntype]=create_neuron(parcond.morph_file,ntype,parcond.Condset[ntype],ghkYN)
        #optionally add spines
        if spYesNo:
            headArray[ntype]=sp.addSpines(ntype,ghkYN)
        #optionally add synapses to dendrites, and possibly to spines
        if synYesNo:
            numSynArray[ntype], synArray[ntype] = syn.add_synchans(ntype, calyesno, ghkYN)
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
        cal.CaProto(parcal.CaThick,parcal.CaBasal,parcal.CaTau,parcal.caName)
        for ntype in parcond.neurontypes:
            for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(ntype)):
                capool=cal.addCaPool(comp,parcal.caName)
                caPools[ntype].append(capool)
                cal.connectVDCC_KCa(ghkYN,comp,capool)
            #if there are spines, calcium will be added to the spine head
            if spYesNo:
                for spcomp in headArray[ntype]:
                    capool=cal.addCaPool(spcomp,parcal.caName)
                    if parsp.spineChanList:
                        cal.connectVDCC_KCa(ghkYN,spcomp,capool)
            #if there are synapses, NMDA will be connected to set of calcium pools
            if synYesNo:
                cal.connectNMDA(synArray[ntype]['nmda'],parcal.caName,ghkYN)
    return synArray,neuron,caPools,numSynArray,headArray
