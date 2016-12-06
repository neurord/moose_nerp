from __future__ import print_function, division

import moose
import numpy as np

from . import logutil
log = logutil.Logger()

def graphtables(model, neuron,pltcurr,curmsg, plas=[],syn=[]):
    print("GRAPH TABLES, ", "plas=",len(plas),"curr=",pltcurr)
    #Vm and Calcium
    vmtab=[]
    catab=[]
    currtab={}
        
    # Make sure /data exists
    moose.Neutral('/data')

    #CHANNEL CURRENTS (Optional)
    if pltcurr:
        for ntype in neuron.keys():
            currtab[ntype]={}
            for channame in model.Channels:
                currtab[ntype][channame]=[moose.Table('/data/chan%s%s_%d' %(channame,ntype,ii)) for ii in range(len(neur_comps))]

    for ntype in neuron.keys():
        neur_comps = moose.wildcardFind(ntype + '/#[TYPE=Compartment]')
        for ii,comp in enumerate(neur_comps):
            vmtab.append(moose.Table('/data/Vm%s_%d' % (ntype,ii)))
            moose.connect(vmtab[ii], 'requestOut', comp, 'getVm')
        if model.calYN:
            for ii,cal in enumerate(moose.wildcardFind(ntype + '/##[ISA=CaConc]')):
                catab.append(moose.Table('/data/Ca%s_%d' % (ntype,ii)))
                moose.connect(catab[ii], 'requestOut', cal, 'getCa')
        if pltcurr:
            for channame in model.Channels:
                for tab, comp in zip(currtab[ntype][channame], neur_comps):
                    path = comp.path+'/'+channame
                    try:
                        chan=moose.element(path)
                        moose.connect(tab, 'requestOut', chan, curmsg)
                    except Exception:
                        log.debug('no channel {}', path)
    #
    # synaptic weight and plasticity
    syntab=[]
    plastab=[]
    plasCumtab=[]
    if len(plas):
        for num,ntype in enumerate(model.neurontypes()):
            plastab.append(moose.Table('/data/plas' + ntype))
            plasCumtab.append(moose.Table('/data/plasCum' + ntype))
            syntab.append(moose.Table('/data/synwt' + ntype))
            moose.connect(plastab[num], 'requestOut', plas[ntype]['plas'], 'getValue')
            moose.connect(plasCumtab[num], 'requestOut', plas[ntype]['cum'], 'getValue')
            shname=syn[ntype].path+'/SH'
            sh=moose.element(shname)
            moose.connect(syntab[num], 'requestOut',sh.synapse[0],'getWeight')
    #
    return vmtab,catab,{'syn':syntab,'plas':plastab,'cum':plasCumtab},currtab
