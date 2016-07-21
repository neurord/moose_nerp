from __future__ import print_function, division

import moose 
import numpy as np

from spspine import param_chan, param_cond, param_sim

def graphtables(neuron,pltcurr,curmsg, capools=[],plas=[],syn=[]):
    print("GRAPH TABLES, ca=", len(capools),"plas=",len(plas),"curr=",pltcurr)
    #Vm and Calcium
    vmtab=[]
    catab=[]
    #
    for neurtype in param_cond.neurontypes():
        ncomps = len(neuron[neurtype]['comps'])
        vmtab.append([moose.Table('/data/Vm%s_%d' % (neurtype,ii))  for ii in range(ncomps)])
        if len(capools[neurtype]):
            catab.append([moose.Table('/data/Ca%s_%d' % (neurtype,ii)) for ii in range(ncomps)])
    for num,neurtype in enumerate(param_cond.neurontypes()):
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
        for num,neurtype in enumerate(param_cond.neurontypes()):
            plastab.append(moose.Table('/data/plas%s' %neurtype))
            plasCumtab.append(moose.Table('/data/plasCum%s' %neurtype))
            syntab.append(moose.Table('/data/synwt%s' %neurtype))
            moose.connect(plastab[num], 'requestOut', plas[neurtype]['plas'], 'getValue')
            moose.connect(plasCumtab[num], 'requestOut', plas[neurtype]['cum'], 'getValue')
            shname=syn[neurtype].path+'/SH'
            sh=moose.element(shname)
            moose.connect(syntab[num], 'requestOut',sh.synapse[0],'getWeight')
    #
    #CHANNEL CURRENTS
    currtab={}
    for neurtype in param_cond.neurontypes():
        currtab[neurtype]={}
        for channame in param_chan.ChanDict:
            currtab[neurtype][channame]=[moose.Table('/data/chan%s%s_%d' %(channame,neurtype,ii)) for ii in range(len(neuron[neurtype]['comps']))]
    for neurtype in param_cond.neurontypes():
        for channame in param_chan.ChanDict:
            for tab, comp in zip(currtab[neurtype][channame], neuron[neurtype]['comps']):
                try:
                    chan=moose.element(comp.path+'/'+channame)
                    moose.connect(tab, 'requestOut', chan, curmsg)
                except:
                    if param_sim.printMoreInfo:
                        print('no channel', comp.path+'/'+channame)
    return vmtab,catab,{'syn':syntab,'plas':plastab,'cum':plasCumtab},currtab

