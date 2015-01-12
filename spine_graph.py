#spine_graph.py
from __future__ import print_function, division

import os

def spinetabs():
    spcatab=[]
    spvmtab=[]
    for typenum, neurtype in enumerate(sorted(neurontypes)):
        spcatab.append([])
        spvmtab.append([])
    for typenum, neurtype in enumerate(sorted(neurontypes)):
        for headnum,head in enumerate(spineHeads[neurtype]):
            p = head.path.split('/')
            spinename = p[compNameNum] + p[spineNameNum][spineNumLoc]
            spvmtab[typenum].append(moose.Table('/data/SpVm%s_%s' % (neurtype,spinename)))
            if printinfo:
                print(headnum,head, spvmtab[typenum][headnum])
            moose.connect(spvmtab[typenum][headnum], 'requestOut', head, 'getVm')
            if calcium:
                spcatab[typenum].append(moose.Table('/data/SpCa%s_%s' % (neurtype,spinename)))
                spcal=moose.element(head.path+'/'+caName)
                moose.connect(spcatab[typenum][headnum], 'requestOut', spcal, 'getCa')
    return spcatab,spvmtab

def spineFig(spinecatab,spinevmtab):
    figure()
    t = np.linspace(0, simtime, len(spinevmtab[0][0].vector))
    if calcium:
        subplot(211)
    for neurnum in range(len(neurontypes)):
        for oid in spinevmtab[neurnum]:
            plt.plot(t,oid.vector,label=oid.path[oid.path.rfind('_')-2:])
        plt.ylabel('Vm')
    if calcium:
        subplot(212)
        for neurnum in range(len(neurontypes)):
            for oid in spinecatab[neurnum]:
                plt.plot(t,1000*oid.vector,label=oid.path[oid.path.rfind('_')-2:])
            plt.ylabel('calcium, uM')
    plt.legend()
    plt.show()
