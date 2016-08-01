"""\
Function definitions for making channels.
"""

from __future__ import print_function, division
import moose
import numpy as np

from spspine import param_cond, param_sim, constants
from spspine.util import NamedList, distance_mapping

SynChannelParams = NamedList('SynChannelParams',
                              '''Erev
                                 tau1
                                 tau2
                                 Gbar
                                 var
                                 MgBlock=None
                                 spinic=False
                                 NMDA=False
                                 nmdaCaFrac=None
                              ''')
MgParams = NamedList('MgParams',
                      '''A
                         B
                         C
                      ''')

def SpineSynChans(synapse_types):
    return sorted(key for key,val in synapse_types.items()
                  if val.spinic and param_sim.Config['spineYN'])

def DendSynChans(synapse_types):
    # If synapses are disabled, put all synaptic channels in the dendrite
    return sorted(key for key,val in synapse_types.items()
                  if not (val.spinic and param_sim.Config['spineYN']))

def make_synchan(chanpath,synparams,calYN):
    # for AMPA or GABA - just make the channel, no connections/messages
    if param_sim.printinfo:
        print('synparams:', chanpath, synparams)
    if synparams.NMDA:
        synchan=moose.NMDAChan(chanpath)
    else:
        synchan = moose.SynChan(chanpath)
    synchan.tau1 = synparams.tau1
    synchan.tau2 = synparams.tau2
    synchan.Ek = synparams.Erev
    #for NMDA, assign MgBlock parameters, and then parameters for calcium current using GHK
    if synparams.NMDA and synparams.MgBlock:
        synchan.KMg_A = synparams.MgBlock.A
        synchan.KMg_B = synparams.MgBlock.B
        synchan.CMg = synparams.MgBlock.C
        if calYN:
            synchan.condFraction = synparams.nmdaCaFrac
            synchan.temperature = constants.celsius_to_kelvin(param_cond.Temp)
            synchan.extCa = param_cond.ConcOut
    return synchan

def synchanlib(calYN,synapse_types):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')

    for name, params in synapse_types.items():
        synchan = make_synchan('/library/' + name,
                               params, calYN)
        print(synchan)

def addoneSynChan(chanpath,syncomp,gbar,calYN,GbarVar):
    proto=moose.SynChan('/library/' +chanpath)
    if param_sim.printMoreInfo:
        print("adding channel",chanpath,"to",syncomp.path,"from",proto.path)
    synchan=moose.copy(proto,syncomp,chanpath)[0]
    synchan.Gbar = np.random.normal(gbar,gbar*GbarVar)
    #bidirectional connection from synchan to compartment when not NMDA:
    m = moose.connect(syncomp, 'channel', synchan, 'channel')
    return synchan

def add_synchans(container,calYN,synapse_types,NumSyn):
    #synchans is 2D array, where each row has a single channel type
    #at the end they are concatenated into a dictionary
    synchans=[]
    comp_list = moose.wildcardFind(container + '/#[TYPE=Compartment]')
    SynPerCompList=np.zeros((len(comp_list),len(NumSyn)),dtype=int)
    #Create 2D array to store all the synapses.  Rows=num synapse types, columns=num comps
    for key in synapse_types:
        synchans.append([])
    allkeys = sorted(synapse_types)

    # i indexes compartment for array that stores number of synapses
    SynPerComp={}
    for i, comp in enumerate(comp_list):
                
        #create each type of synchan in each compartment.  Add to 2D array
        for key in DendSynChans(synapse_types):
            keynum = allkeys.index(key)
            Gbar = synapse_types[key].Gbar
            Gbarvar=synapse_types[key].var
            synchans[keynum].append(addoneSynChan(key,comp,Gbar,calYN,Gbarvar))
        for key in SpineSynChans(synapse_types):
            keynum = allkeys.index(key)
            Gbar = synapse_types[key].Gbar
            Gbarvar=synapse_types[key].var
            for spcomp in moose.wildcardFind(comp.path + '/#[ISA=Compartment]'):
                if 'head' in spcomp.path:
                    synchans[keynum].append(addoneSynChan(key,spcomp,Gbar,calYN,Gbarvar))
        #
        #calculate distance from soma
        xloc=moose.Compartment(comp).x
        yloc=moose.Compartment(comp).y
        dist=np.sqrt(xloc*xloc+yloc*yloc)
        #create array of number of synapses per compartment based on distance
        #possibly replace NumGlu[] with number of spines, or eliminate this if using real morph
        #Check in ExtConn - how is SynPerComp used
        for j,syntype in enumerate(NumSyn.keys()):
            SynPerCompList[i,j] = distance_mapping(NumSyn[syntype], dist)
    for j,syntype in enumerate(NumSyn.keys()):
        SynPerComp[syntype]=SynPerCompList[:,j]
    #end of iterating over compartments
    #now, transform the synchans into a dictionary
    allsynchans={key:synchans[keynum]
                 for keynum, key in enumerate(sorted(synapse_types))}

    return SynPerComp,allsynchans
