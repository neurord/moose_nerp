from __future__ import print_function, division
import numpy as np
from matplotlib import pyplot
import moose

from moose_nerp.prototypes import syn_proto, logutil
log = logutil.Logger()

def graphs(neurons, simtime, vmtab,catab=[],plastab=[]):
    t = np.linspace(0, simtime, len(vmtab[0][0].vector))
    fig,axes =pyplot.subplots(len(vmtab), 1,sharex=True)
    fig.canvas.set_window_title('Population Vm')
    for typenum,neur in enumerate(neurons.keys()):
        for vmoid in vmtab[typenum]:
            neur_name=vmoid.msgOut[0].e2.path.split('/')[-2][0:-3]
            axes[typenum].plot(t, vmoid.vector, label=neur_name)
        axes[typenum].set_ylabel(neur+' Vm, volts')
        axes[typenum].legend(fontsize=8,loc='upper left')
    axes[typenum].set_xlabel('Time, sec')
    #
    if len(catab):
        fig,axes =pyplot.subplots(len(vmtab), 1,sharex=True)
        fig.canvas.set_window_title('Population Calcium')
        for tabset in catab:
            if len(tabset)==1:
                caoid=tabset
                typenum=neurons.keys().index(caoid.name.partition('_')[0][2:])
                axes[typenum].plot(t, caoid.vector*1e3, label=caoid.name.partition('_')[2])
            else:
                for caoid in tabset:
                    typenum=neurons.keys().index(caoid.name.partition('_')[0][2:])
                    axes[typenum].plot(t, caoid.vector*1e3, label=caoid.name.partition('_')[2])
        for typenum,neur in enumerate(neurons.keys()):
            axes[typenum].set_ylabel(neur+' Calcium, uM')
            axes[typenum].legend(fontsize=8,loc='upper left')
        axes[typenum].set_xlabel('Time, sec')
    #
    if len(plastab):
        fig,axes =pyplot.subplots(len(vmtab), len(plastab[0].keys()), sharex=True)
        fig.canvas.set_window_title('Population Plasticity')
        for neurnum,tabset in enumerate(plastab):
            for plasnum, plastype in enumerate(tabset.keys()):
                if plastype=='plas':
                    scaling=1000
                else:
                    scaling=1
                plasoid=tabset[plastype]
                typenum=neurons.keys().index(plasoid.name.split(plastype)[1].split('_')[0])
                t=np.linspace(0, simtime, len(plasoid.vector))
                axes[typenum][plasnum].plot(t,plasoid.vector*scaling, label=plasoid.path.partition('_')[2])
            axes[typenum][plasnum].legend(fontsize=8,loc='best')
        for typenum,neur in enumerate(neurons.keys()):
            for plasnum, plastype in enumerate(tabset.keys()):
                axes[typenum][plasnum].set_ylabel(neur+''+plastype)
                axes[typenum][plasnum].set_xlabel('Time, sec')
        fig.tight_layout()
        fig.canvas.draw()

def syn_graph(connections, syntabs, simtime):
    numrows=int(np.size(syntabs)/np.shape(syntabs)[0])
    fig,axes =pyplot.subplots(numrows, 1,sharex=True)
    fig.canvas.set_window_title('Syn Chans')
    for oid in syntabs:
        typenum=connections.keys().index(oid.name.partition('_')[0])
        t = np.linspace(0, simtime, len(oid.vector))
        axes.plot(t, oid.vector*1e9, label=oid.path.partition('_')[2])
    axes.set_ylabel('I (nA), {}'.format(oid.path.rpartition('_')[2]))
    axes.legend(fontsize=8,loc='upper left')
