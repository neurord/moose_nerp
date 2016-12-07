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

    for typenum,neur_type in enumerate(neuron.keys()):
        neur_comps = moose.wildcardFind(neur_type + '/##[TYPE=Compartment]')
        vmtab.append([moose.Table('/data/Vm%s_%d' % (neur_type,ii)) for ii in range(len(neur_comps))])
        for ii,comp in enumerate(neur_comps):
            moose.connect(vmtab[typenum][ii], 'requestOut', comp, 'getVm')
        if model.calYN:
            catab.append([moose.Table('/data/Ca%s_%d' % (neur_type,ii)) for ii in range(len(neur_comps))])
            for ii,cal in enumerate(moose.wildcardFind(neur_type + '/##[ISA=CaConc]')):
                moose.connect(catab[typenum][ii], 'requestOut', cal, 'getCa')
        if pltcurr:
            for channame in model.Channels:
                for tab, comp in zip(currtab[neur_type][channame], neur_comps):
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
        for num,neur_type in enumerate(model.neuroneur_types()):
            plastab.append(moose.Table('/data/plas' + neur_type))
            plasCumtab.append(moose.Table('/data/plasCum' + neur_type))
            syntab.append(moose.Table('/data/synwt' + neur_type))
            moose.connect(plastab[num], 'requestOut', plas[neur_type]['plas'], 'getValue')
            moose.connect(plasCumtab[num], 'requestOut', plas[neur_type]['cum'], 'getValue')
            shname=syn[neur_type].path+'/SH'
            sh=moose.element(shname)
            moose.connect(syntab[num], 'requestOut',sh.synapse[0],'getWeight')
    #
    return vmtab,catab,{'syn':syntab,'plas':plastab,'cum':plasCumtab},currtab
