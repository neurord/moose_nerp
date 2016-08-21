from __future__ import print_function, division
import numpy as np
import moose

from spspine import param_cond, syn_proto
from spspine.param_spine import SpineParams

def connectTables(vcomp,vtab,ctab,stab,tabnum,calyn):
    if printinfo:
        print("VTABLES", vtab[tabnum].path,vcomp.path)
    m=moose.connect(vtab[tabnum], 'requestOut', vcomp, 'getVm')
    if calyn:
        cacomp=moose.element(vcomp.path+'/CaPool')
        if printinfo:
            print("CTABLES", ctab[tabnum].path,cacomp.path)
        moose.connect(ctab[tabnum], 'requestOut', cacomp, 'getCa')
    for synnum,chan in enumerate(syn_proto.DendSynChans()):
        syn=moose.element(vcomp.path+'/'+chan)
        if chan=='nmda':
            syn=moose.element(syn.path+'/mgblock')
        syntabnum=len(syn_proto.DendSynChans())*tabnum+synnum
        if printinfo:
            print(stab[syntabnum].path, chan)
        assert chan in stab[syntabnum].path
        moose.connect(stab[syntabnum], 'requestOut', syn, Synmsg)
    return vtab,ctab,stab

def spineTables(spineHeads,catab,syntab,calyn):
    for typenum, neurtype in enumerate(param_cond.neurontypes()):
        for headnum,head in enumerate(spineHeads[neurtype]):
            if calyn:
                spcal=head.path+'/CaPool'
                moose.connect(catab[typenum][headnum], 'requestOut', moose.element(spcal), 'getCa')
            for synnum,chan in enumerate(syn_proto.SpineSynChans()):
                syn=moose.element(head.path+'/'+chan)
                if chan=='nmda':
                    syn=moose.element(syn.path+'/mgblock')
                syntabnum = len(syn_proto.SpineSynChans()) * headnum + synnum
                if printinfo:
                    print(syn.path,syntab[typenum][syntabnum].path, chan)
                assert chan in syntab[typenum][syntabnum].path
                moose.connect(syntab[typenum][syntabnum], 'requestOut', syn, Synmsg)
    return catab,syntab

def graphs(vmtab,syntab,grphsyn,catab=[],plastab=[],plasCumtab=[],sptab=[]):
    t = np.linspace(0, sim.simtime, len(vmtab[0][0].vector))
    for typenum,neur in enumerate(param_cond.neurontypes()):
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
        for typenum,neur in enumerate(param_cond.neurontypes()):
            f=figure()
            f.canvas.set_window_title(neur+' Dend SynChans')
            for i,chan in enumerate(syn_proto.DendSynChans()):
                axes=f.add_subplot(len(syn_proto.DendSynChans()),1,i+1)
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
                f.canvas.set_window_title(param_cond.neurontypes()[typenum]+plastype)
                axes=f.add_subplot(numplots,1,plasnum+1)
                for oid in plastab[plastype][typenum]:
                    axes.plot(t,oid.vector*scaling, label=oid.path.rpartition('_')[2])
                axes.legend(fontsize=8,loc='best')
    if len(sptab['cal']):
        for typenum,neur in enumerate(param_cond.neurontypes()):
            f = plt.figure()
            f.canvas.set_window_title("Spines {}".format(neur))
            numplots = len(syn_proto.SpineSynChans())+1
            for i,chan in enumerate(syn_proto.SpineSynChans()):
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
