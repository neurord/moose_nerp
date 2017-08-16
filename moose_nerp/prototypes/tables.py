from __future__ import print_function, division

import moose
import numpy as np

from collections import defaultdict, namedtuple
#from moose_nerp.prototypes.calcium import NAME_CALCIUM
from moose_nerp.prototypes.spines import NAME_HEAD
DATA_NAME='/data'
HDF5WRITER_NAME='/hdf5'

from . import logutil
log = logutil.Logger()

def vm_table_path(neuron, spine=None, comp=0):
    return '{}/Vm{}_{}{}'.format(DATA_NAME, neuron, '' if spine is None else spine, comp)

def find_compartments(neuron):
    return moose.wildcardFind('{}/#[TYPE=Compartment]'.format(neuron))

def find_vm_tables(neuron):
    return moose.wildcardFind('{}/Vm{}_#[TYPE=Table]'.format(DATA_NAME, neuron))

GraphTables = namedtuple('GraphTables', 'vmtab catab plastab currtab hdf5writer')

def graphtables(model, neuron,pltcurr,curmsg, plas=[]):
    print("GRAPH TABLES, of ", neuron.keys(), "plas=",len(plas),"curr=",pltcurr)
    #tables for Vm and calcium in each compartment
    vmtab=[]
    catab=[]
    for typenum, neur_type in enumerate(neuron.keys()):
        catab.append([])
    currtab={}

    # Make sure /hdf5 exists
    if not moose.exists(HDF5WRITER_NAME):
        print('creating', HDF5WRITER_NAME)
        writer = moose.HDF5DataWriter(HDF5WRITER_NAME)
        writer.mode = 2 # Truncate existing file
        moose.useClock(7, HDF5WRITER_NAME, 'process')
    else:
        print('using', HDF5WRITER_NAME)
        writer = moose.element(HDF5WRITER_NAME)

    # Make sure /data exists
    if not moose.exists(DATA_NAME):
        moose.Neutral(DATA_NAME)

    for typenum,neur_type in enumerate(neuron.keys()):
        neur_comps = find_compartments(neur_type)
        vmtab.append([moose.Table(vm_table_path(neur_type, comp=ii)) for ii in range(len(neur_comps))])

        for ii,comp in enumerate(neur_comps):
            moose.connect(vmtab[typenum][ii], 'requestOut', comp, 'getVm')
            moose.connect(writer, 'requestOut', comp, 'getVm')

        if model.calYN:
            for ii,comp in enumerate(neur_comps):
                for child in comp.children:
                    if child.className == "CaConc" or  child.className == "ZombieCaConc":

                        NAME_CALCIUM = child.name

                        catab[typenum].append(moose.Table(DATA_NAME+'/%s_%d_' % (neur_type,ii)+NAME_CALCIUM) )

                        cal = moose.element(comp.path+'/'+NAME_CALCIUM)
                        moose.connect(catab[typenum][-1], 'requestOut', cal, 'getCa')
                        moose.connect(writer, 'requestOut', cal, 'getCa')
                    elif  child.className == 'DifShell':
                        NAME_CALCIUM = child.name
                        catab[typenum].append(moose.Table(DATA_NAME+'/%s_%d_'% (neur_type,ii)+NAME_CALCIUM ) )

                        cal = moose.element(comp.path+'/'+NAME_CALCIUM)
                        moose.connect(catab[typenum][-1], 'requestOut', cal, 'getC')
                        moose.connect(writer, 'requestOut', cal, 'getC')

        if pltcurr:
            currtab[neur_type]={}
            #CHANNEL CURRENTS (Optional)
            for channame in model.Channels:
                tabs = [moose.Table(DATA_NAME+'/chan%s%s_%d' %(channame,neur_type,ii))
                        for ii in range(len(neur_comps))]
                currtab[neur_type][channame] = tabs
                for tab, comp in zip(tabs, neur_comps):
                    path = comp.path+'/'+channame
                    try:
                        chan=moose.element(path)
                        moose.connect(tab, 'requestOut', chan, curmsg)
                        moose.connect(writer, 'requestOut', cal, curmsg)
                    except Exception:
                        log.debug('no channel {}', path)
    #
    # synaptic weight and plasticity (Optional) for one synapse per neuron
    plastab=[]
    if len(plas):
        for num,neur_type in enumerate(plas.keys()):
            plastab.append(add_one_table(DATA_NAME,plas[neur_type],neur_type))
    return GraphTables(vmtab, catab, plastab, currtab, writer)


def add_one_table(DATA_NAME, plas_entry, comp_name):
    if comp_name.find('/')==0:
       comp_name=comp_name[1:]
    plastab=moose.Table(DATA_NAME+'/plas' + comp_name)
    plasCumtab=moose.Table(DATA_NAME+'/cum' + comp_name)
    syntab=moose.Table(DATA_NAME+'/syn' + comp_name)
    moose.connect(plastab, 'requestOut', plas_entry['plas'], 'getValue')
    moose.connect(plasCumtab, 'requestOut', plas_entry['cum'], 'getValue')
    shname=plas_entry['syn'].path+'/SH'
    sh=moose.element(shname)
    moose.connect(syntab, 'requestOut',sh.synapse[0],'getWeight')
    return {'plas':plastab,'cum':plasCumtab,'syn':syntab}

def syn_plastabs(connections, plas=[]):
    if not moose.exists(DATA_NAME):
        moose.Neutral(DATA_NAME)
    #tables with synaptic conductance for all synapses that receive input
    syn_tabs=[]
    plas_tabs=[]
    for neur_type in connections.keys():
        for syntype in connections[neur_type].keys():
            for compname in connections[neur_type][syntype].keys():
                tt = moose.element(connections[neur_type][syntype][compname])
                synapse=tt.msgOut[0].e2[0]  #msgOut[1] is the NMDA synapse if [0] is AMPA; tt could go to multiple synapses
                log.debug('{} {} {} {}', neur_type,compname,tt.msgOut, synapse)
                synchan=synapse.parent.parent
                syn_tabs.append(moose.Table(DATA_NAME+'/'+neur_type+'_'+compname+synchan.name))
                log.debug('{} {} ', syn_tabs[-1], synchan)
                moose.connect(syn_tabs[-1], 'requestOut', synchan, 'getGk')
    #tables of dictionaries with instantaneous plasticity (plas), cumulative plasticity (plasCum) and synaptic weight (syn)
    if len(plas):
        for neur_type in plas.keys():
            for cell in plas[neur_type].keys():
                for syncomp in plas[neur_type][cell].keys():
                    plas_tabs.append(add_one_table(DATA_NAME, plas[neur_type][cell][syncomp], cell+syncomp))
    return syn_tabs, plas_tabs

def spinetabs(model,neuron):
    if not moose.exists(DATA_NAME):
        moose.Neutral(DATA_NAME)
    #creates tables of calcium and vm for spines
    spcatab = defaultdict(list)
    spvmtab = defaultdict(list)
    for typenum,neurtype in enumerate(neuron.keys()):
        spineHeads=moose.wildcardFind(neurtype+'/##/#head#[ISA=Compartment]')
        for spinenum,spine in enumerate(spineHeads):
            compname = spine.parent.name
            sp_num=spine.name.split(NAME_HEAD)[0]
            spvmtab[typenum].append(moose.Table(vm_table_path(neurtype, spine=sp_num, comp=compname)))
            log.debug('{} {} {}', spinenum,spine, spvmtab[typenum][spinenum])
            moose.connect(spvmtab[typenum][spinenum], 'requestOut', spine, 'getVm')
            if model.calYN:
                for child in spine.children:
                    if child.className == "CaConc" or  child.className == "ZombieCaConc" :
                        NAME_CALCIUM = child.name
                        spcatab[typenum].append(moose.Table(DATA_NAME+'/%s_%s%s'% (neurtype,sp_num,compname)+NAME_CALCIUM))
                        spcal = moose.element(spine.path+'/'+NAME_CALCIUM)
                        moose.connect(spcatab[typenum][-1], 'requestOut', spcal, 'getCa')
                    elif child.className == 'DifShell':
                        NAME_CALCIUM = child.name
                        spcatab[typenum].append(moose.Table(DATA_NAME+'/%s_%s%s'% (neurtype,sp_num,compname)+NAME_CALCIUM))
                        spcal = moose.element(spine.path+'/'+NAME_CALCIUM)
                        moose.connect(spcatab[typenum][-1], 'requestOut', spcal, 'getC')
    return spcatab,spvmtab
