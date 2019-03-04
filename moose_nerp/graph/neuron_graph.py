from __future__ import print_function, division

import moose
from matplotlib import pyplot
import numpy as np

from moose_nerp.prototypes.iso_scaling import iso_scaling
from moose_nerp.prototypes import tables
from moose_nerp.prototypes.util import neurontypes
try:
    _GRAPHS
except NameError:
    _GRAPHS = {}
def _get_graph(name, figsize=None):
    try:
        f = _GRAPHS[name]
    except KeyError:
        f = _GRAPHS[name] = pyplot.figure(figsize=figsize)
        f.canvas.set_window_title(name)
    else:
        f.clear()
        f.canvas.draw() # this is here to make it easier to see what changed
    return f

def graphs(model, vmtab, plotcurr, simtime, currtab=[],curlabl="",catab={},plastab={}, compartments=None):
    for neurtype in vmtab.keys():
        f = _get_graph('{} voltage&calcium'.format(neurtype), figsize=(6,6))
        axes = f.add_subplot(211) if len(catab.keys()) else f.gca()
        for oid in vmtab[neurtype]:#tables.find_tables(neurtype,'Vm'):
            compnum = oid.msgOut[0].e2.name
            print('in graphs', compnum)
            if compartments is None or int(compnum) in compartments:
                t = np.linspace(0, simtime, len(oid.vector))
                axes.plot(t, oid.vector, label=compnum)
        axes.set_ylabel('Vm {}'.format(neurtype))
        axes.legend(fontsize=8, loc='best')
        axes.set_title('voltage vs. time')
        if len(catab.keys()):
            axes = f.add_subplot(212)
            for oid in catab[neurtype]:
                neurnum=oid.name.split('_')[-1].split('[')[0]
                t = np.linspace(0, simtime, len(oid.vector))
                axes.plot(t, oid.vector*1e3, label=neurnum)
            axes.set_ylabel('calcium, uM')
            axes.set_xlabel('Time (sec)')
            axes.legend(fontsize=8, loc='best')
            axes.set_title('calcium vs. time')
        f.tight_layout()
        f.canvas.draw()

    if model.plasYN:
        fig,axes =pyplot.subplots(len(plastab)+1, 1,sharex=True)
        fig.suptitle('Plasticity')
        for neurtype in plastab.keys():
          item = plastab[neurtype][0]
          for plasnum,plastype in enumerate(['plas','syn']):
            if plastype=='plas':
                title='wt change'
                scaling=1000
            else:
                title=plastype
                scaling=1
            neurnum=item[plastype].name.split(plastype)[-1]
            t = np.linspace(0, simtime, len(item[plastype].vector))
            axes[plasnum].plot(t, scaling*item[plastype].vector, label=neurnum)
            axes[plasnum].set_ylabel(str(scaling)+'*'+title)
            axes[plasnum].legend(loc='best', fontsize=8)
        axes[plasnum].set_xlabel('time')
        fig.tight_layout()
        fig.canvas.draw()

    if plotcurr:
        f = _get_graph('D1/D2 currents', figsize=(6,12))
        numplots=len(model.Channels)
        for plotnum, channame in enumerate(sorted(model.Channels)):
            try:
                axes = f.add_subplot(numplots, 1, plotnum + 1)
                toplot = [tab.vector / (model.ghKluge if 'chanCa' in tab.path else 1)
                          for tab in currtab[neurtype][channame]]
                scaling = iso_scaling(*toplot)
                for vec in toplot:
                    t = np.linspace(0, simtime, len(vec))
                    axes.plot(t, vec / scaling.divisor)
                    labelstring=u'{}, {}{}'.format(channame, scaling.unit, curlabl)
                axes.set_ylabel(labelstring)
                if plotnum == 1:
                    axes.set_title('current vs. time')
            except:
                print("no channel", channame)
        f.subplots_adjust(left=0.16, bottom=0.05, right=0.95, top=0.95, hspace=0.26)
        f.canvas.draw()

def SingleGraphSet(traces, currents, simtime, title='Voltage'):
    t = np.linspace(0, simtime, len(traces[0]))
    f=pyplot.figure()
    f.canvas.set_window_title(title)
    axes=f.add_subplot(1,1,1)
    for i in range(len(traces)):
        axes.plot(t,traces[i],label=currents[i])
    if title == 'Voltage':
        yaxis='Vm, volts'
    else:
        yaxis='Ca, mM'
    axes.set_ylabel(yaxis)
    axes.set_xlabel('Time, sec')
    axes.legend(fontsize=8,loc='best')
    f.canvas.draw()
##

def CurrentGraphSet(value,g, keys, simtime):
    #
    f = pyplot.figure()
    f.canvas.set_window_title('Conductance')
    axes = f.add_subplot(1, 1, 1)
    #
    if isinstance(value,dict):
        for key in keys:
            t = np.linspace(0, simtime, len(value[key]))
            axes.plot(t, value[key], label=g[key])
    else:
        for i in range(len(value)):
            axes.plot(t,value[i],label=g[i])
    axes.set_ylabel('gk, volts')
    axes.set_xlabel('Time, sec')
    axes.legend(fontsize=10,loc='best')
    f.canvas.draw()
