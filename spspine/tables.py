from __future__ import print_function, division

import moose
import numpy as np

from collections import defaultdict
from spspine.calcium import NAME_CALCIUM
from spspine.spines import NAME_HEAD
DATA_NAME='/data'

from . import logutil
log = logutil.Logger()

def graphtables(model, neuron,pltcurr,curmsg, plas=[]):
    print("GRAPH TABLES, of ", neuron.keys(), "plas=",len(plas),"curr=",pltcurr)
    #Vm and Calcium
    vmtab=[]
    catab=[]
    currtab=defaultdict(list)
    # Make sure /data exists
    if not moose.exists(DATA_NAME):
        moose.Neutral(DATA_NAME)
    
    for typenum,neur_type in enumerate(neuron.keys()):
        neur_comps = moose.wildcardFind(neur_type + '/#[TYPE=Compartment]')
        vmtab.append([moose.Table(DATA_NAME+'/Vm%s_%d' % (neur_type,ii)) for ii in range(len(neur_comps))])
        for ii,comp in enumerate(neur_comps):
            moose.connect(vmtab[typenum][ii], 'requestOut', comp, 'getVm')
        if model.calYN:
            catab.append([moose.Table(DATA_NAME+'/Ca%s_%d' % (neur_type,ii)) for ii in range(len(neur_comps))])
            for ii,comp in enumerate(neur_comps):
                cal=moose.element(comp.path+'/'+NAME_CALCIUM)
                moose.connect(catab[typenum][ii], 'requestOut', cal, 'getCa')
        if pltcurr:
            #CHANNEL CURRENTS (Optional)
            for channame in model.Channels:
                currtab[neur_type][channame]=[moose.Table(DATA_NAME+'/chan%s%s_%d' %(channame,neur_type,ii)) for ii in range(len(neur_comps))]
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
        for num,neur_type in enumerate(plas.keys()):
            plastab.append(moose.Table(DATA_NAME+'/plas' + neur_type))
            plasCumtab.append(moose.Table(DATA_NAME+'/plasCum' + neur_type))
            syntab.append(moose.Table(DATA_NAME+'/synwt' + neur_type))
            moose.connect(plastab[num], 'requestOut', plas[neur_type]['plas'], 'getValue')
            moose.connect(plasCumtab[num], 'requestOut', plas[neur_type]['cum'], 'getValue')
            shname=plas[neur_type]['syn'].path+'/SH'
            sh=moose.element(shname)
            moose.connect(syntab[num], 'requestOut',sh.synapse[0],'getWeight')
    #
    return vmtab,catab,{'syn':syntab,'plas':plastab,'cum':plasCumtab},currtab

def spinetabs(model,neuron):
    spcatab = defaultdict(list)
    spvmtab = defaultdict(list)
    for typenum,neurtype in enumerate(neuron.keys()):
        spineHeads=moose.wildcardFind(neurtype+'/##/#head#[ISA=Compartment]')
        for spinenum,spine in enumerate(spineHeads):
            compname = spine.parent.name
            sp_num=spine.name.split(NAME_HEAD)[0]
            spvmtab[typenum].append(moose.Table(DATA_NAME+'/Vm%s_%s%s' % (neurtype,sp_num,compname)))
            log.debug('{} {} {}', spinenum,spine, spvmtab[typenum][spinenum])
            moose.connect(spvmtab[typenum][spinenum], 'requestOut', spine, 'getVm')
            if model.calYN:
                spcatab[typenum].append(moose.Table(DATA_NAME+'/Ca%s_%s%s' % (neurtype,sp_num,compname)))
                spcal=moose.element(spine.path+'/'+NAME_CALCIUM)
                moose.connect(spcatab[typenum][spinenum], 'requestOut', spcal, 'getCa')
    return spcatab,spvmtab

