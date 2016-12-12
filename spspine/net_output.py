"""\
Create table for spike generators of network, and Vm when not graphing.
"""
from __future__ import print_function, division
import numpy as np
import moose
from spspine.cell_proto import NAME_SOMA
from spspine.tables import DATA_NAME

from spspine import logutil
log = logutil.Logger()

def SpikeTables(model, pop,plot_netvm):
    if not moose.exists(DATA_NAME):
        moose.Neutral(DATA_NAME)
    spiketab=[]
    vmtab=[]
    for typenum,neur_type in enumerate(pop.keys()):
        if plot_netvm:
            vmtab.append([moose.Table(DATA_NAME+'/Vm_%s' % (moose.element(neurname).name)) for neurname in pop[neur_type]])
        spiketab.append([moose.Table(DATA_NAME+'/outspike_%s' % (moose.element(neurname).name)) for neurname in pop[neur_type]])
        for tabnum,neur in enumerate(pop[neur_type]):
            soma_name=neur+'/'+NAME_SOMA
            sg=moose.element(soma_name+'/spikegen')
            log.debug('{} '*3, neur_type, sg.path, spiketab[typenum][tabnum])
            m=moose.connect(sg, 'spikeOut', spiketab[typenum][tabnum],'spike')
            if plot_netvm:
                moose.connect(vmtab[typenum][tabnum], 'requestOut', moose.element(soma_name), 'getVm')
    return spiketab, vmtab

#also create function to store calcium and the change in synaptic weight for synapses in the network
#modify graphtables to plot subset of synapses when fully connected?
#        if model.calYN:
#            catab.append([moose.Table(DATA_NAME+'/Ca%s_%d' % (moose.element(neurname).name)) for neurname in pop[neur_type]])
#            for ii,neur in enumerate(pop[neur_type]):
#                cal=moose.element(neur+'/'+NAME_SOMA+'/'+NAME_CALCIUM)
#                moose.connect(catab[typenum][ii], 'requestOut', cal, 'getCa')

def writeOutput(model, outfilename,spiketab,vmtab,MSNpop):
    outvmfile='Vm'+outfilename
    outspikefile='Spike'+outfilename
    log.info('SPIKE FILE {} VM FILE {}', outspikefile, outvmfile)
    outspiketab=list()
    outVmtab=list()
    for typenum,neurtype in enumerate(model.neurontypes()):
        outspiketab.append([])
        outVmtab.append([])
        for tabnum,neurname in enumerate(MSNpop['pop'][typenum]):
            underscore=find(neurname,'_')
            neurnum=int(neurname[underscore+1:])
            print(neurname.split('_')[1])
            log.info('{} is {} num={} {.path} {}',
                     neurname, neurtype, neurnum,spiketab[typenum][tabnum], vmtab[typenum][tabnum])
            outspiketab[typenum].append(insert(spiketab[typenum][tabnum].vector,0, neurnum))
            outVmtab[typenum].append(insert(vmtab[typenum][tabnum].vector,0, neurnum))
    savez(outspikefile,D1=outspiketab[0],D2=outspiketab[1])
    savez(outvmfile,D1=outVmtab[0],D2=outVmtab[1])
