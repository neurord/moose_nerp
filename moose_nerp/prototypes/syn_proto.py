"""\
Function definitions for making channels.
"""

from __future__ import print_function, division
import moose
import numpy as np

from moose_nerp.prototypes import constants, logutil
from moose_nerp.prototypes.util import NamedList
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

DesensitizationParams  =  NamedList('DesensitizationParams',
                                   ''' dep_per_spike
                                   dep_tau''')

#can be used for facilitation or depression
#change_operator is either multiply or add - specify * or +
#to depress with additive, give negative change_per_spike
#both desens and facil allowed in same synapse

SpikePlasParams =  NamedList('SpikePlasParams',
                             ''' change_per_spike
                             change_tau
                             change_operator''')

ShortTermPlasParams=NamedList('ShortTermPlasParams','''depress=None facil=None''')

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

def synchanlib(model,module=None):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')
    else:
        lib=moose.element('/library')

    if module is not None:
        if moose.exists('/library/'+module):
            lib=moose.element('/library/'+module)
            print('using existing module library for synchans',lib.path)
        else:
            lib=moose.Neutral('/library/'+module)
            print('new synchan library for',module, lib.path)
    
    for name, params in model.SYNAPSE_TYPES.items():
        synchan = make_synchan(model,
                               lib.path + '/'+ name,
                               params)
        print(synchan)

       
def addoneSynChan(chanpath,syncomp,gbar,calYN,GbarVar,module=None):
    if module is None:
        proto = moose.element('/library/' +chanpath)
    else:
        proto = moose.element('/library/'+module+'/'+chanpath)
    log.debug('adding channel {} to {.path} from {.path}'.format( chanpath, syncomp, proto))
    synchan=moose.copy(proto,syncomp,chanpath)[0]
    synchan.Gbar = np.random.normal(gbar,gbar*GbarVar)
    #bidirectional connection from synchan to compartment when not NMDA:
    m = moose.connect(syncomp, 'channel', synchan, 'channel')
    #create and connect synhandler
    shname=synchan.path+'/SH'
    sh=moose.SimpleSynHandler(shname)
    moose.connect(sh, 'activationOut', synchan, 'activation')
    return synchan

def add_synchans(model, container,module=None):
    synchans=[]
    #2D array to store all the synapses.  Rows=num synapse types, columns=num comps
    #at the end they are concatenated into a dictionary
    for key in model.SYNAPSE_TYPES:
        synchans.append([])
    allkeys = sorted(model.SYNAPSE_TYPES)

    comp_list = moose.wildcardFind(container + '/#[TYPE=Compartment]')
    for comp in comp_list:
        #create each type of synchan in each compartment.  Add to 2D array
        for key in DendSynChans(model):
            keynum = allkeys.index(key)
            Gbar = model.SYNAPSE_TYPES[key].Gbar
            Gbarvar=model.SYNAPSE_TYPES[key].var
            synchans[keynum].append(addoneSynChan(key,comp,Gbar, model.calYN, Gbarvar,module))
        
        for key in SpineSynChans(model):
            keynum = allkeys.index(key)
            Gbar = model.SYNAPSE_TYPES[key].Gbar
            Gbarvar=model.SYNAPSE_TYPES[key].var
            for spcomp in moose.wildcardFind(comp.path + '/#[ISA=Compartment]'):
                if NAME_HEAD in spcomp.path:
                    synchans[keynum].append(addoneSynChan(key,spcomp,Gbar, model.calYN, Gbarvar,module))
                   
    allsynchans={key:synchans[keynum]
                 for keynum, key in enumerate(sorted(model.SYNAPSE_TYPES))}

    return allsynchans
