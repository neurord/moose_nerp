from __future__ import print_function, division

import moose
import numpy as np
import glob

from collections import defaultdict, namedtuple
#from moose_nerp.prototypes.calcium import NAME_CALCIUM
from moose_nerp.prototypes.spines import NAME_HEAD
DATA_NAME='/data'
HDF5WRITER_NAME='/hdf5'

from . import logutil, calcium, util
log = logutil.Logger()

def vm_table_path(neuron, spine=None, comp=0):
    return '{}/Vm{}_{}{}'.format(DATA_NAME, neuron, '' if spine is None else spine, comp)

@util.listize
def find_compartments(neuron, *compartments):
    if not compartments:
        compartments = '',
    for comp_name in compartments:
        for comp in moose.wildcardFind('{}/{}#[TYPE=Compartment]'.format(neuron, comp_name)):
            yield comp

@util.listize
def glob_compartments(neuron, *patterns):
    """List compartments with paths matching one of the glob patterns

    [0] are removed from the path, and should not be specified in the
    pattern.

    >>> glob_compartments('D1', '*dend1')
    [<moose.Compartment: id=..., dataIndex=0, path=/D1[0]/primdend1[0]>]
    """
    for comp in find_compartments(neuron):
        path = comp.name.replace('[0]', '')
        if any(glob.fnmatch.fnmatch(path, pattern) for pattern in patterns):
            yield comp

def find_vm_tables(neuron):
    return moose.wildcardFind('{}/Vm{}_#[TYPE=Table]'.format(DATA_NAME, neuron))

DEFAULT_HDF5_COMPARTMENTS = 'soma',

def setup_volume_average(path, compartments):
    total_volume = 0
    print('AVERAGE:', path, compartments)
    average = moose.DiffAmp(path)

    for comp in compartments:
        for child in comp.children:
            if child.className in {"CaConc", "ZombieCaConc"}:
                cal = moose.element(comp.path+'/'+child.name)
                da = moose.DiffAmp(cal.path + '/diffamp')
                volume = calcium.shell_volume(cal)
                da.gain = volume
                total_volume += volume
                moose.connect(cal, 'concOut', da, 'plusIn')
                moose.connect(da, 'output', average, 'plusIn')
            # FIXME: add support for DifShells

    average.gain = 1/total_volume
    return average

@util.listize
def children_groups(neuron, *patterns):
    """Find groups of children with the same prefix before '_'

    Returns a list of path prefixes.

    >>> from pprint import pprint
    >>> pprint(moose_nerp.prototypes.tables.children_groups('D1', 'soma', '*tertdend[12]_*'))
    [(<moose.Compartment: id=534, dataIndex=0, path=/D1[0]/soma[0]>,),
     (<moose.Compartment: id=558, dataIndex=0, path=/D1[0]/tertdend2_1[0]>,
      <moose.Compartment: id=559, dataIndex=0, path=/D1[0]/tertdend2_2[0]>,
      <moose.Compartment: id=560, dataIndex=0, path=/D1[0]/tertdend2_3[0]>,
      <moose.Compartment: id=561, dataIndex=0, path=/D1[0]/tertdend2_4[0]>,
      <moose.Compartment: id=562, dataIndex=0, path=/D1[0]/tertdend2_5[0]>,
      <moose.Compartment: id=563, dataIndex=0, path=/D1[0]/tertdend2_6[0]>,
      <moose.Compartment: id=564, dataIndex=0, path=/D1[0]/tertdend2_7[0]>,
      <moose.Compartment: id=565, dataIndex=0, path=/D1[0]/tertdend2_8[0]>,
      <moose.Compartment: id=566, dataIndex=0, path=/D1[0]/tertdend2_9[0]>,
      <moose.Compartment: id=567, dataIndex=0, path=/D1[0]/tertdend2_10[0]>,
      <moose.Compartment: id=568, dataIndex=0, path=/D1[0]/tertdend2_11[0]>),
     (<moose.Compartment: id=547, dataIndex=0, path=/D1[0]/tertdend1_1[0]>,
      <moose.Compartment: id=548, dataIndex=0, path=/D1[0]/tertdend1_2[0]>,
      <moose.Compartment: id=549, dataIndex=0, path=/D1[0]/tertdend1_3[0]>,
      <moose.Compartment: id=550, dataIndex=0, path=/D1[0]/tertdend1_4[0]>,
      <moose.Compartment: id=551, dataIndex=0, path=/D1[0]/tertdend1_5[0]>,
      <moose.Compartment: id=552, dataIndex=0, path=/D1[0]/tertdend1_6[0]>,
      <moose.Compartment: id=553, dataIndex=0, path=/D1[0]/tertdend1_7[0]>,
      <moose.Compartment: id=554, dataIndex=0, path=/D1[0]/tertdend1_8[0]>,
      <moose.Compartment: id=555, dataIndex=0, path=/D1[0]/tertdend1_9[0]>,
      <moose.Compartment: id=556, dataIndex=0, path=/D1[0]/tertdend1_10[0]>,
      <moose.Compartment: id=557, dataIndex=0, path=/D1[0]/tertdend1_11[0]>)]
    """
    comps = glob_compartments(neuron, *patterns)
    with_under = [c for c in comps if '_' in c.name]
    without_under = [c for c in comps if '_' not in c.name]

    for c in without_under:
        yield c,

    prefixes = set(c.path.replace('[0]', '').rsplit('_', 1)[0] for c in with_under)
    for prefix in prefixes:
        group = moose.wildcardFind(prefix + '_#[TYPE=Compartment]')
        if group:
            yield group

def setup_hdf5_output(model, neurons, *patterns, filename=None):
    if not patterns:
        patterns = DEFAULT_HDF5_COMPARTMENTS

    # Make sure /hdf5 exists
    if not moose.exists(HDF5WRITER_NAME):
        print('creating', HDF5WRITER_NAME)
        writer = moose.HDF5DataWriter(HDF5WRITER_NAME)
        writer.mode = 2 # Truncate existing file
        if filename is not None:
            writer.filename = filename
        moose.useClock(8, HDF5WRITER_NAME, 'process')
    else:
        print('using', HDF5WRITER_NAME)
        writer = moose.element(HDF5WRITER_NAME)

    for typenum,neur_type in enumerate(neurons.keys()):
        groups = children_groups(neur_type, *patterns)

        # Connect the first in each group for voltage,
        # and set up volume averaging of the rest for calcium.
        for group in groups:
            moose.connect(writer, 'requestOut', group[0], 'getVm')

            if model.calYN:
                avpath = group[0].path.replace('[0]', '').rsplit('_', 1)[0] + '_ca'
                average = setup_volume_average(avpath, group)
                moose.connect(writer, 'requestOut', average, 'getOutputValue')
    return writer

GraphTables = namedtuple('GraphTables', 'vmtab catab plastab currtab')

def graphtables(model, neurons,pltcurr,curmsg, plas=[]):
    print("GRAPH TABLES, of ", neurons.keys(), "plas=",len(plas),"curr=",pltcurr)
    #tables for Vm and calcium in each compartment
    vmtab=[]
    catab=[]
    for typenum, neur_type in enumerate(neurons.keys()):
        catab.append([])
    currtab={}

    # Make sure /data exists
    if not moose.exists(DATA_NAME):
        moose.Neutral(DATA_NAME)

    for typenum,neur_type in enumerate(neurons.keys()):
        neur_comps = find_compartments(neur_type)
        vmtab.append([moose.Table(vm_table_path(neur_type, comp=ii)) for ii in range(len(neur_comps))])

        for ii,comp in enumerate(neur_comps):
            moose.connect(vmtab[typenum][ii], 'requestOut', comp, 'getVm')

        if model.calYN:
            for ii,comp in enumerate(neur_comps):
                for child in comp.children:
                    if child.className in {"CaConc", "ZombieCaConc"}:
                        catab[typenum].append(moose.Table(DATA_NAME+'/%s_%d_' % (neur_type,ii)+child.name))

                        cal = moose.element(comp.path+'/'+child.name)
                        moose.connect(catab[typenum][-1], 'requestOut', cal, 'getCa')
                    elif  child.className == 'DifShell':
                        catab[typenum].append(moose.Table(DATA_NAME+'/%s_%d_'% (neur_type,ii)+child.name))

                        cal = moose.element(comp.path+'/'+child.name)
                        moose.connect(catab[typenum][-1], 'requestOut', cal, 'getC')

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
                    except Exception:
                        log.debug('no channel {}', path)
    #
    # synaptic weight and plasticity (Optional) for one synapse per neuron
    plastab=[]
    if len(plas):
        for num,neur_type in enumerate(plas.keys()):
            plastab.append(add_one_table(DATA_NAME,plas[neur_type],neur_type))
    return GraphTables(vmtab, catab, plastab, currtab)


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
                        spcatab[typenum].append(moose.Table(DATA_NAME+'/%s_%s%s'% (neurtype,sp_num,compname)+child.name))
                        spcal = moose.element(spine.path+'/'+child.name)
                        moose.connect(spcatab[typenum][-1], 'requestOut', spcal, 'getCa')
                    elif child.className == 'DifShell':
                        spcatab[typenum].append(moose.Table(DATA_NAME+'/%s_%s%s'% (neurtype,sp_num,compname)+child.name))
                        spcal = moose.element(spine.path+'/'+child.name)
                        moose.connect(spcatab[typenum][-1], 'requestOut', spcal, 'getC')
    return spcatab,spvmtab
