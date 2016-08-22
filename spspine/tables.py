from __future__ import print_function, division

import moose 
import numpy as np

from . import logutil
log = logutil.Logger()

def graphtables(model, neuron,pltcurr,curmsg, capools=[],plas=[],syn=[]):
    print("GRAPH TABLES, ca=", len(capools),"plas=",len(plas),"curr=",pltcurr)
    #Vm and Calcium
    vmtab=[]
    catab=[]
    #
    for neurtype in model.neurontypes():
        ncomps = len(neuron[neurtype]['comps'])
        vmtab.append([moose.Table('/data/Vm%s_%d' % (neurtype,ii))  for ii in range(ncomps)])
        if len(capools[neurtype]):
            catab.append([moose.Table('/data/Ca%s_%d' % (neurtype,ii)) for ii in range(ncomps)])
    for num,neurtype in enumerate(model.neurontypes()):
        for tab, comp in zip(vmtab[num], neuron[neurtype]['comps']):
            moose.connect(tab, 'requestOut', comp, 'getVm')
        if len(capools[neurtype]):
            for ctab, cal in zip(catab[num], capools[neurtype]):
                moose.connect(ctab, 'requestOut', cal, 'getCa')
    #
    # synaptic weight and plasticity
    syntab=[]
    plastab=[]
    plasCumtab=[]
    if len(plas):
        for num,neurtype in enumerate(model.neurontypes()):
            plastab.append(moose.Table('/data/plas' + neurtype))
            plasCumtab.append(moose.Table('/data/plasCum' + neurtype))
            syntab.append(moose.Table('/data/synwt' + neurtype))
            moose.connect(plastab[num], 'requestOut', plas[neurtype]['plas'], 'getValue')
            moose.connect(plasCumtab[num], 'requestOut', plas[neurtype]['cum'], 'getValue')
            shname=syn[neurtype].path+'/SH'
            sh=moose.element(shname)
            moose.connect(syntab[num], 'requestOut',sh.synapse[0],'getWeight')
    #
    #CHANNEL CURRENTS
    currtab={}
    for neurtype in model.neurontypes():
        currtab[neurtype]={}
        for channame in model.Channels:
            currtab[neurtype][channame]=[moose.Table('/data/chan%s%s_%d' %(channame,neurtype,ii)) for ii in range(len(neuron[neurtype]['comps']))]
    for neurtype in model.neurontypes():
        for channame in model.Channels:
            for tab, comp in zip(currtab[neurtype][channame], neuron[neurtype]['comps']):
                path = comp.path+'/'+channame
                try:
                    chan=moose.element(path)
                    moose.connect(tab, 'requestOut', chan, curmsg)
                except Exception:
                    log.debug('no channel {}', path)
    return vmtab,catab,{'syn':syntab,'plas':plastab,'cum':plasCumtab},currtab

