"""\
Function definitions for making channels.
"""

from __future__ import print_function, division
import moose
import numpy as np

from moose_nerp.prototypes import constants, logutil
from moose_nerp.prototypes.util import NamedList, distance_mapping
from moose_nerp.prototypes.spines import NAME_HEAD
log = logutil.Logger()

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

DesensitizationParams =  NamedList('DesensitizationParams',
                                   ''' dep_per_spike
                                   dep_tau''')

def SpineSynChans(model):
    return sorted(key for key,val in model.SYNAPSE_TYPES.items()
                  if val.spinic and model.spineYN)

def DendSynChans(model):
    # If spines are disabled, put all synaptic channels in the dendrite
    return sorted(key for key,val in model.SYNAPSE_TYPES.items()
                  if not (val.spinic and model.spineYN))

def make_synchan(model, chanpath, synparams):
    # for AMPA or GABA - just make the channel, no connections/messages
    log.info('synparams: {} {}', chanpath, synparams)
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
        if (model.calYN):
            synchan.condFraction = synparams.nmdaCaFrac
            synchan.temperature = constants.celsius_to_kelvin(model.Temp)
            synchan.extCa = model.ConcOut
    return synchan

def synchanlib(model):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')

    for name, params in model.SYNAPSE_TYPES.items():
        synchan = make_synchan(model,
                               '/library/' + name,
                               params)
        print(synchan)


        
def addoneSynChan(chanpath,syncomp,gbar,calYN,GbarVar):
     
    proto = moose.element('/library/' +chanpath)
        
    log.debug('adding channel {} to {.path} from {.path}', chanpath, syncomp, proto)
    synchan=moose.copy(proto,syncomp,chanpath)[0]
    synchan.Gbar = np.random.normal(gbar,gbar*GbarVar)
    #bidirectional connection from synchan to compartment when not NMDA:
    m = moose.connect(syncomp, 'channel', synchan, 'channel')
    return synchan

def add_synchans(model, container):
    #synchans is 2D array, where each row has a single channel type
    #at the end they are concatenated into a dictionary
    synchans=[]
    comp_list = moose.wildcardFind(container + '/#[TYPE=Compartment]')
    SynPerCompList=np.zeros((len(comp_list),len(model.NumSyn)),dtype=int)
    #Create 2D array to store all the synapses.  Rows=num synapse types, columns=num comps
    for key in model.SYNAPSE_TYPES:
        synchans.append([])
    allkeys = sorted(model.SYNAPSE_TYPES)

    # i indexes compartment for array that stores number of synapses
    for i, comp in enumerate(comp_list):
                
        #create each type of synchan in each compartment.  Add to 2D array
        for key in DendSynChans(model):
            keynum = allkeys.index(key)
            Gbar = model.SYNAPSE_TYPES[key].Gbar
            Gbarvar=model.SYNAPSE_TYPES[key].var
            synchans[keynum].append(addoneSynChan(key,comp,Gbar, model.calYN, Gbarvar))
        
            
        for key in SpineSynChans(model):
            keynum = allkeys.index(key)
            Gbar = model.SYNAPSE_TYPES[key].Gbar
            Gbarvar=model.SYNAPSE_TYPES[key].var
            for spcomp in moose.wildcardFind(comp.path + '/#[ISA=Compartment]'):
                if NAME_HEAD in spcomp.path:
                    synchans[keynum].append(addoneSynChan(key,spcomp,Gbar, model.calYN, Gbarvar))
                   
        ########### delete from here to allsynchans= once pop_funcs debugged ################

        #calculate distance from soma
        xloc=moose.Compartment(comp).x
        yloc=moose.Compartment(comp).y
        dist=np.sqrt(xloc*xloc+yloc*yloc)
        #create array of number of synapses per compartment based on distance
        #possibly replace NumGlu[] with number of spines, or eliminate this if using real morph
        #Check in ExtConn - how is SynPerComp used
    #end of iterating over compartments
    #now, transform the synchans into a dictionary
    
    allsynchans={key:synchans[keynum]
                 for keynum, key in enumerate(sorted(model.SYNAPSE_TYPES))}

    return allsynchans
