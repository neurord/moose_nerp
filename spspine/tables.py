from __future__ import print_function, division

import moose
import numpy as np

from collections import defaultdict
from spspine.calcium import NAME_CALCIUM
from . import logutil
log = logutil.Logger()

def graphtables(model, neuron,pltcurr,curmsg, plas=[],syn=[]):
    print("GRAPH TABLES, of ", neuron.keys(), "plas=",len(plas),"curr=",pltcurr)
    #Vm and Calcium
    vmtab=[]
    catab=[]
    currtab=defaultdict(list)
    # Make sure /data exists
    moose.Neutral('/data')
    
    for typenum,neur_type in enumerate(neuron.keys()):
        neur_comps = moose.wildcardFind(neur_type + '/#[TYPE=Compartment]')
        vmtab.append([moose.Table('/data/Vm%s_%d' % (neur_type,ii)) for ii in range(len(neur_comps))])
        for ii,comp in enumerate(neur_comps):
            moose.connect(vmtab[typenum][ii], 'requestOut', comp, 'getVm')
        if model.calYN:
            catab.append([moose.Table('/data/Ca%s_%d' % (neur_type,ii)) for ii in range(len(neur_comps))])
            for ii,comp in enumerate(neur_comps):
                cal=moose.element(comp.path+'/'+NAME_CALCIUM)
                moose.connect(catab[typenum][ii], 'requestOut', cal, 'getCa')
        if pltcurr:
            #CHANNEL CURRENTS (Optional)
            for channame in model.Channels:
                currtab[neur_type][channame]=[moose.Table('/data/chan%s%s_%d' %(channame,neur_type,ii)) for ii in range(len(neur_comps))]
                for tab, comp in zip(currtab[neur_type][channame], neur_comps):
                    path = comp.path+'/'+channame
                    try:
                        chan=moose.element(path)
                        moose.connect(tab, 'requestOut', chan, curmsg)
                    except Exception:
                        log.debug('no channel {}', path)
    #
    # synaptic weight and plasticity (Optional)
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

def spinetabs(model,neuron):
    spcatab = defaultdict(list)
    spvmtab = defaultdict(list)
    for typenum,neurtype in enumerate(neuron.keys()):
        spineHeads=moose.wildcardFind(neurtype+'/##/#head#[ISA=Compartment]')
        for headnum,head in enumerate(spineHeads):
            headname = head.parent.name
            spvmtab[typenum].append(moose.Table('/data/SpVm%s_%s' % (neurtype,headname)))
            log.debug('{} {} {}', headnum,head, spvmtab[typenum][headnum])
            moose.connect(spvmtab[typenum][headnum], 'requestOut', head, 'getVm')
            if model.calYN:
                spcatab[typenum].append(moose.Table('/data/SpCa%s_%s' % (neurtype,headname)))
                spcal=moose.element(head.path+'/'+NAME_CALCIUM)
                moose.connect(spcatab[typenum][headnum], 'requestOut', spcal, 'getCa')
    return spcatab,spvmtab

