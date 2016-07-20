from __future__ import print_function, division
import numpy as np
import moose

import param_cond as parcond
import param_sim as parsim
from param_spine import SpineParams

def connectTables(vcomp,vtab,ctab,stab,tabnum,calyn):
    if printinfo:
        print("VTABLES", vtab[tabnum].path,vcomp.path)
    m=moose.connect(vtab[tabnum], 'requestOut', vcomp, 'getVm')
    if calyn:
        cacomp=moose.element(vcomp.path+'/'+caName)
        if printinfo:
            print("CTABLES", ctab[tabnum].path,cacomp.path)
        moose.connect(ctab[tabnum], 'requestOut', cacomp, 'getCa')
    for synnum,chan in enumerate(parsim.DendSynChans):
        syn=moose.element(vcomp.path+'/'+chan)
        if chan=='nmda':
            syn=moose.element(syn.path+'/mgblock')
        syntabnum=len(parsim.DendSynChans)*tabnum+synnum
        if printinfo:
            print(stab[syntabnum].path, chan)
        assert chan in stab[syntabnum].path
        moose.connect(stab[syntabnum], 'requestOut', syn, Synmsg)
    return vtab,ctab,stab

def spineTables(spineHeads,catab,syntab,calyn):
    for typenum, neurtype in enumerate(sorted(parcond.neurontypes)):
        for headnum,head in enumerate(spineHeads[neurtype]):
            if calyn:
                spcal=head.path+'/'+caName
                moose.connect(catab[typenum][headnum], 'requestOut', moose.element(spcal), 'getCa')
            for synnum,chan in enumerate(parsim.SpineSynChans):
                syn=moose.element(head.path+'/'+chan)
                if chan=='nmda':
                    syn=moose.element(syn.path+'/mgblock')
                syntabnum=len(parsim.SpineSynChans)*headnum+synnum
                if printinfo:
                    print(syn.path,syntab[typenum][syntabnum].path, chan)
                assert chan in syntab[typenum][syntabnum].path
                moose.connect(syntab[typenum][syntabnum], 'requestOut', syn, Synmsg)
    return catab,syntab

def graphtables(neuron,singl,pltnet,msn_pop,capools=[],SynPlas=[],spineheads=[]):
    print("GRAPHS","single=",singl,"plotnet=",pltnet, "ca=", len(capools),"plas=",len(SynPlas), "spines=", len(spineheads))
    message=["ONE FROM NETWORK","SINGLE"]
    syntab=[]
    vmtab=[]
    catab=[]
    spcatab=[]
    spsyntab=[]
    plastab=[]
    plasCumtab=[]
    for typenum,neurtype in enumerate(sorted(parcond.neurontypes)):
        vmtab.append([])
        catab.append([])
        syntab.append([])
        if len(spineheads[neurtype]):
            spcatab.append([])
            spsyntab.append([])
        if len(SynPlas[neurtype]):
            plastab.append([])
            plasCumtab.append([])
    #
    if singl or not pltnet:
        #create tables, one per neuron compartment
        for typenum, neurtype in enumerate(sorted(parcond.neurontypes)):
            for comp in neuron[neurtype]['comps']:
                compname = comp.path.split('/')[parcond.compNameNum]
                #print "Single",comp.path,neurtype,split(comp.path,'/')[compNameNum],'/data/Vm%s_%s' % (neurtype,split(comp.path,'/')[compNameNum])
                vmtab[typenum].append(moose.Table('/data/Vm%s_%s' % (neurtype, compname)))
                if len(capools[neurtype]):
                    catab[typenum].append(moose.Table('/data/Ca%s_%s' % (neurtype,compname)))
                for chan in parsim.DendSynChans:
                    syntab[typenum].append(moose.Table('/data/Gk%s_%s_%s' % (chan,neurtype,compname)))
            if len(spineheads[neurtype]):
                for head in spineheads[neurtype]:
                    if len(capools[neurtype]):
                        p = head.path.split('/')
                        spinename = p[parcond.compNameNum] + p[SpineParams.spineNameNum][SpineParams.spineNumLoc]
                        spcatab[typenum].append(moose.Table('/data/SpCa%s_%s' % (neurtype,spinename)))
                    for chan in parsim.SpineSynChans:
                         spsyntab[typenum].append(moose.Table('/data/SpGk%s_%s_%s' % (chan,neurtype,spinename)))
            if SynPlas[neurtype]:
                for plas in SynPlas[neurtype]: 
                    p = plas['plas'].path.split('/')
                    plasname = p[parcond.compNameNum] + p[SpineParams.spineNameNum][SpineParams.spineNumLoc]
                    plastab[typenum].append(moose.Table('/data/plas%s_%s' % (neurtype,plasname))) 
                    plasCumtab[typenum].append(moose.Table('/data/plasCum%s_%s' % (neurtype,plasname))) 
        #Connect tables
        print("***********PLOTTING",message[singl],"********************")
        for typenum, neurtype in enumerate(sorted(parcond.neurontypes)):
            for tabnum,comp in enumerate(neuron[neurtype]['comps']):
                if singl:
                    plotcomp=comp
                else:
                    comppath= comp.path.split('/')[parcond.compNameNum]
                    plotcomp=moose.element(msn_pop['pop'][typenum][0]+'/'+comppath)
                vmtab[typenum],catab[typenum],syntab[typenum]=connectTables(plotcomp,vmtab[typenum],catab[typenum],syntab[typenum],tabnum, calyesno)
            #tables for spines, or plasticity
            if SynPlas[neurtype]:
                for tabnum,plasObject in enumerate(SynPlas[neurtype]):
                    print(plasObject)
                    moose.connect(plastab[typenum][tabnum], 'requestOut', plasObject['plas'], 'getValue')
                    moose.connect(plasCumtab[typenum][tabnum], 'requestOut', plasObject['cum'], 'getValue')
        if len(spineheads[neurtype]):
            spcatab,spsyntab=spineTables(spineheads,spcatab,spsyntab,calyesno)
    else:
        #create and connect tables, one per cell soma.  
        print("***********PLOTTING NETWORK SOMATA***************")
        for typenum,neurtype in enumerate(sorted(parcond.neurontypes)):
            for neurpath in msn_pop['pop'][typenum]:
                neurnum = neurpath.partition('_')[2]
                vmtab[typenum].append(moose.Table('/data/soma%s_%s' % (neurtype,neurnum)))
                if len(capools[neurtype]):
                    catab[typenum].append(moose.Table('/data/Ca%s_%s' % (neurtype,neurnum)))
                for chan in parsim.DendSynChans:
                    syntab[typenum].append(moose.Table('/data/Gk%s%s_%s' % (chan,neurtype,neurnum)))
            for tabnum,neurpath in enumerate(msn_pop['pop'][typenum]):
                plotcomp=moose.element(neurpath+'/soma')
                vmtab[typenum],catab[typenum],syntab[typenum]=connectTables(plotcomp,vmtab[typenum],catab[typenum],syntab[typenum],tabnum,calyesno)
    return vmtab,syntab,catab,{'plas':plastab,'cum':plasCumtab},{'cal':spcatab,'syn':spsyntab}

def graphs(vmtab,syntab,grphsyn,catab=[],plastab=[],plasCumtab=[],sptab=[]):
    t = np.linspace(0, sim.simtime, len(vmtab[0][0].vector))
    for typenum,neur in enumerate(sorted(parcond.neurontypes)):
        f=figure()
        f.canvas.set_window_title(neur+' Vm')
        if len(catab):
            subplot(211)
        for vmoid in vmtab[typenum]:
            if neur in vmoid.path:
                plt.plot(t, vmoid.vector, label=vmoid.path.partition('_')[2])
        plt.ylabel('Vm, volts')
        plt.legend(fontsize=8,loc='upper left')
        if len(catab):
            subplot(212)
            for caoid in catab[typenum]:
                if neur in caoid.path:
                    plt.plot(t, caoid.vector*1e3, label=caoid.path.partition('_')[2])
            plt.ylabel('calcium, uM')
    #
    if grphsyn:
        for typenum,neur in enumerate(sorted(parcond.neurontypes)):
            f=figure()
            f.canvas.set_window_title(neur+' Dend SynChans')
            for i,chan in enumerate(parsim.DendSynChans):
                axes=f.add_subplot(len(parsim.DendSynChans),1,i+1)
                axes.set_title(neur+chan)
                for oid in syntab[typenum]:
                    if chan in oid.path and len(oid.vector) > 0:
                        t = np.linspace(0, simtime, len(oid.vector))
                        axes.plot(t, oid.vector*1e9, label=oid.path.rpartition('_')[2])
                axes.set_ylabel('I (nA), {}'.format(chan))
                axes.legend(fontsize=8,loc='upper left')
    if len(plastab['plas']):
        numplots = len(plastab)
        for plasnum,plastype in enumerate(['plas','cum']):
            if plastype=='plas':
                scaling=1000
            else:
                scaling=1
            for typenum in range(len(plastab[plastype])):
                t=np.linspace(0, simtime, len(plastab[typenum][0].vector))
                f = plt.figure(figsize=(6,6))
                f.canvas.set_window_title(parcond.neurontypes[typenum]+plastype)
                axes=f.add_subplot(numplots,1,plasnum+1)
                for oid in plastab[plastype][typenum]:
                    axes.plot(t,oid.vector*scaling, label=oid.path.rpartition('_')[2])
                axes.legend(fontsize=8,loc='best')
    if len(sptab['cal']):
        for typenum,neur in enumerate(sorted(parcond.neurontypes)):
            f = plt.figure()
            f.canvas.set_window_title("Spines {}".format(neur))
            numplots = len(parsim.SpineSynChans)+1
            for i,chan in enumerate(parsim.SpineSynChans):
                axes=f.add_subplot(numplots,1,i+1)
                axes.set_ylabel('I (nA) {}'.format(chan))
                for oid in sptab['syn'][typenum]:
                    if (chan in oid.path) and (len(oid.vector)>0):
                        t = np.linspace(0, simtime, len(oid.vector))
                        axes.plot(t, oid.vector*1e9, label=oid.path.rpartition('_')[2])
                axes.legend(fontsize=8,loc='best')
                axes.set_title('current vs. time')
            axes=f.add_subplot(numplots,1,numplots)
            axes.set_ylabel('calcium, uM')
            for oid in sptab['cal'][typenum]:
                axes.plot(t,oid.vector, label=oid.path.rpartition('_')[2])
            axes.legend(fontsize=8,loc='best')
            axes.set_title('Spine Ca vs. time')
            f.tight_layout()
            f.canvas.draw()
