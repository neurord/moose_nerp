"""\
Create table for spike generators of network, and Vm when not graphing.
"""
from __future__ import print_function, division
import numpy as np
import moose
#from moose_nerp.prototypes.calcium import NAME_CALCIUM
from moose_nerp.prototypes.tables import DATA_NAME, add_one_table
from moose_nerp.prototypes import logutil
log = logutil.Logger()

def SpikeTables(model, pop,plot_netvm, plas=[], plots_per_neur=[]):
    if not moose.exists(DATA_NAME):
        moose.Neutral(DATA_NAME)
    spiketab=[]
    vmtab=[]
    plastabs=[]
    catab=[]
    for typenum,neur_type in enumerate(pop.keys()):
        if plot_netvm:
            vmtab.append([moose.Table(DATA_NAME+'/Vm_%s' % (moose.element(neurname).name)) for neurname in pop[neur_type]])
        spiketab.append([moose.Table(DATA_NAME+'/outspike_%s' % (moose.element(neurname).name)) for neurname in pop[neur_type]])
        for tabnum,neur in enumerate(pop[neur_type]):
            soma_name=neur+'/'+model.param_cond.NAME_SOMA
            sg=moose.element(soma_name+'/spikegen')
            log.debug('{} '*3, neur_type, sg.path, spiketab[typenum][tabnum])
            m=moose.connect(sg, 'spikeOut', spiketab[typenum][tabnum],'spike')
            if plot_netvm:
                moose.connect(vmtab[typenum][tabnum], 'requestOut', moose.element(soma_name), 'getVm')
    #now plot calcium and plasticity, if created, but only from a few compartments for each neuron
    if model.plasYN:
        tabrow=0
        for neur_type in plas.keys():
            for cellnum,cellpath in enumerate(plas[neur_type].keys()):
                cellname=moose.element(cellpath).name
                choice_comps=plas[neur_type][cellpath].keys()
                syncomp_names=np.random.choice(choice_comps,plots_per_neur,replace=False)
                log.debug('{} {} {}', cellpath, cellname, syncomp_names)
                catab.append([moose.Table(DATA_NAME+'/Ca%s_%s' % (cellname, syncomp)) for syncomp in syncomp_names])
                for compnum,syncomp_name in enumerate(syncomp_names):
                    plas_entry = plas[neur_type][cellpath][syncomp_name]
                    plastabs.append(add_one_table(DATA_NAME,plas_entry, cellname+syncomp_name))
                    # cal_name=plas_entry['syn'].parent.path+'/'+NAME_CALCIUM
                    # moose.connect(catab[tabrow][compnum], 'requestOut', moose.element(cal_name), 'getCa')
                tabrow=tabrow+1
    elif model.calYN:
        #if no plasticity, just plot calcium and (synaptic input?) for some compartments
        #add synaptic channels for the calcium compartments?  Or randomly select synchans with synapses and then plot those calcium comps
        # tabrow=0
        # for typenum,neur_type in enumerate(pop.keys()):
        #     for neurnum,neurname in enumerate(pop[neur_type]):
        #         allcomps = moose.wildcardFind(neurname+ '/#[TYPE=Compartment]')
        #         plotcomps=np.random.choice(allcomps,plots_per_neur,replace=False)
        #         catab.append([moose.Table(DATA_NAME+'/Ca%s_%s' % (moose.element(neurname).name,comp.name)) for comp in plotcomps])
        #         for compnum,comp in enumerate(plotcomps):
        #             cal_name=comp.path+'/'+NAME_CALCIUM
        #             print(catab[tabrow][compnum].path,moose.element(cal_name).path)
        #             moose.connect(catab[tabrows][compnum], 'requestOut', moose.element(cal_name), 'getCa')
        #         tabrow=tabrow+1
        pass
    return spiketab, vmtab, plastabs, catab

def writeOutput(model, outfilename,spiketab,vmtab,network_pop):
    outspiketab={}
    outVmtab={}
    for typenum,neurtype in enumerate(model.neurontypes()):
        tmpspiketab={}
        tmpVmtab={}
        print(outspiketab.keys())
        for tabnum,neurname in enumerate(network_pop['pop'][neurtype]):
            neurnum=int(neurname.split('_')[-1])
            log.info('{} is type {} num={} paths: {.path}',
                     neurname, neurtype, neurnum,spiketab[typenum][tabnum])
            tmpspiketab[neurname.split('_')[-1]]=spiketab[typenum][tabnum].vector
            if len(vmtab):
                tmpVmtab[neurname.split('_')[-1]]=vmtab[typenum][tabnum].vector
        outspiketab[neurtype]=tmpspiketab
        outVmtab[neurtype]=tmpVmtab
    np.savez(outfilename,spk=outspiketab,vm=outVmtab)
    #to read in data: f=np.load('gp_out5e-11.npz') spk_dat=f['spk'].item() or vm_dat=f['vm'].item()

