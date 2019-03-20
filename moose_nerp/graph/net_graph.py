from __future__ import print_function, division
import numpy as np
from matplotlib import pyplot
import moose

from moose_nerp.prototypes import syn_proto, logutil
log = logutil.Logger()

def graphs(neurons, simtime, vmtab,catab={},plastab={}):
    length_time=np.max([len(tab.vector) for tabset in vmtab.values() for tab in tabset])
    t = np.linspace(0, simtime, length_time)
    fig,axes =pyplot.subplots(len(vmtab), 1,sharex=True)
    axis=fig.axes
    fig.canvas.set_window_title('Population Vm')
    for typenum,neur_type in enumerate(vmtab.keys()):
        for vmoid in vmtab[neur_type]:
            neur_name=vmoid.msgOut[0].e2.path.split('/')[-2][0:-3]
            axis[typenum].plot(t, vmoid.vector, label=neur_name)
        axis[typenum].set_ylabel(neur_type+' Vm, volts')
        axis[typenum].legend(fontsize=8,loc='upper left')
    axis[typenum].set_xlabel('Time, sec')
    #
    if len(catab.keys()):
        fig,axes =pyplot.subplots(len(catab), 1,sharex=True)
        axis=fig.axes
        fig.canvas.set_window_title('Population Calcium')
        for typenum,neur_type in enumerate(catab.keys()):
            for caoid in catab[neur_type]:
                typenum=neurons.keys().index(caoid.name.partition('_')[0][2:])
                axis[typenum].plot(t, caoid.vector*1e3, label=caoid.name.partition('_')[2])
            axis[typenum].set_ylabel(neur_type+' Calcium, uM')
            axis[typenum].legend(fontsize=8,loc='upper left')
        axis[typenum].set_xlabel('Time, sec')
    #
    #if len(plastab):
    #    fig,axes =pyplot.subplots(len(vmtab), len(plastab[0].keys()), sharex=True)
    #    axis=fig.axes
    #    fig.canvas.set_window_title('Population Plasticity')
    #    for neurnum,tabset in enumerate(plastab):
    #        for plasnum, plastype in enumerate(tabset.keys()):
    #            if plastype=='plas':
    #                scaling=1000
    #            else:
    #                scaling=1
    #            plasoid=tabset[plastype]
    #            typenum=neurons.keys().index(plasoid.name.split(plastype)[1].split('_')[0])
    #            t=np.linspace(0, simtime, len(plasoid.vector))
    #            axis[typenum][plasnum].plot(t,plasoid.vector*scaling, label=plasoid.path.partition('_')[2])
    #        axis[typenum][plasnum].legend(fontsize=8,loc='best')
    #    for typenum,neur in enumerate(neurons.keys()):
    #        for plasnum, plastype in enumerate(tabset.keys()):
    #            axis[typenum][plasnum].set_ylabel(neur+''+plastype)
    #            axis[typenum][plasnum].set_xlabel('Time, sec')
    #    fig.tight_layout()
    #    fig.canvas.draw()

def syn_graph(connections, syntabs, param_sim,factor=1e9):
    numrows=len(syntabs.keys()) #how many neuron types
    max_index=np.argmax([len(syntabs[k].keys()) for k in syntabs.keys()])
    syntypes=[list(syntabs[k].keys()) for k in syntabs.keys()][max_index] #how many synapse types
    numcols=len(syntypes)
    fig,axes =pyplot.subplots(numrows, numcols,sharex=True)
    axis=fig.axes #convert to 1D list in case numrows or numcols=1
    if factor==1:
        fig.canvas.set_window_title('desensitization')
    else:
        fig.canvas.set_window_title('Syn Chans')
    for typenum,neurtype in enumerate(syntabs.keys()):
        for synnum,syntype in enumerate(syntabs[neurtype].keys()):
            axisnum=typenum*len(syntypes)+synnum
            for oid in syntabs[neurtype][syntype]:
                #synnum=syntypes.index(oid.path.rpartition('_')[2].split('[')[0]) #extract synapse type from table name
                t = np.linspace(0, param_sim.simtime, len(oid.vector))
                axis[axisnum].plot(t, oid.vector*factor, label=oid.name)
            axis[axisnum].set_ylabel('{} {} {}'.format(param_sim.plot_synapse_label,syntype,neurtype))
    for ax in range(len(axis)):
        axis[ax].legend(fontsize=6,loc='upper left') #add legend
