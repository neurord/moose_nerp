from __future__ import print_function, division

import moose 
from matplotlib import pyplot
from iso_scaling import iso_scaling
import numpy as np
import param_cond as parcond
from param_chan import ChanDict
from param_sim import printMoreInfo, simtime

def graphtables(neuron,pltplas,pltcurr,calyesno,capools,curmsg):
    print("GRAPH TABLES, plas=",pltplas,"curr=",pltcurr)
    #Vm and Calcium
    vmtab=[]
    catab=[]
    #
    for neurtype in parcond.neurontypes:
        vmtab.append([moose.Table('/data/Vm%s_%d' % (neurtype,ii))  for ii in range(len(neuron[neurtype]['comps']))])
        if calyesno:
            catab.append([moose.Table('/data/Ca%s_%d' % (neurtype,ii)) for ii in range(len(neuron[neurtype]['comps']))])
    for num,neurtype in enumerate(parcond.neurontypes):
        for tab, comp in zip(vmtab[num], neuron[neurtype]['comps']):
            moose.connect(tab, 'requestOut', comp, 'getVm')
        if calyesno:
            for ctab, cal in zip(catab[num], capools[neurtype]):
                moose.connect(ctab, 'requestOut', cal, 'getCa')
    #
    # synaptic weight and plasticity
    syntab=[]
    plastab=[]
    plasCumtab=[]
    if pltplas:
        for num,neurtype in enumerate(parcond.neurontypes):
            plastab.append(moose.Table('/data/plas%s' %neurtype))
            plasCumtab.append(moose.Table('/data/plasCum%s' %neurtype))
            syntab.append(moose.Table('/data/synwt%s' %neurtype))
            moose.connect(plastab[num], 'requestOut', plas[neurtype]['plas'], 'get_value')
            moose.connect(plasCumtab[num], 'requestOut', plas[neurtype]['cum'], 'get_value')
            moose.connect(syntab[num], 'requestOut',syn[neurtype].synapse[0],'getWeight')
    #
    #CHANNEL CURRENTS
    currtab={}
    for neurtype in parcond.neurontypes:
        currtab[neurtype]={}
        for channame in ChanDict:
            currtab[neurtype][channame]=[moose.Table('/data/chan%s%s_%d' %(channame,neurtype,ii)) for ii in range(len(neuron[neurtype]['comps']))]
    for neurtype in parcond.neurontypes:
        for channame in ChanDict:
            for tab, comp in zip(currtab[neurtype][channame], neuron[neurtype]['comps']):
                try:
                    chan=moose.element(comp.path+'/'+channame)
                    moose.connect(tab, 'requestOut', chan, curmsg)
                except:
                    if printMoreInfo:
                        print('no channel', comp.path+'/'+channame)
    return vmtab,catab,{'syn':syntab,'plas':plastab,'cum':plasCumtab},currtab

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

def graphs(vmtab,catab,plastab,currtab,plotplas,grphcurr,calyesno,curlabl):
    t = np.linspace(0, simtime, len(vmtab[0][0].vec))

    for typenum,neurtype in enumerate(parcond.neurontypes):
        f = _get_graph('{} voltage'.format(neurtype), figsize=(6,6))
        t = np.linspace(0, simtime, len(vmtab[typenum][0].vec))
        axes = f.add_subplot(211) if calyesno else f.gca()
        for oid in vmtab[typenum]:
            axes.plot(t, oid.vec, label=oid.path[-2:])
        axes.set_ylabel('Vm {}'.format(neurtype))
        axes.legend(fontsize=8, loc='best')
        axes.set_title('voltage vs. time')
        if calyesno:
            axes = f.add_subplot(212)
            for oid in catab[typenum]:
                axes.plot(t, oid.vec*1e3, label=oid.path[-2:])
            axes.set_ylabel('calcium, uM')
            axes.legend(fontsize=8, loc='best')
            axes.set_title('calcium vs. time')
        f.tight_layout()
        f.canvas.draw()

        if plotplas:
            f = _get_graph('{} plasticity'.format(neurtype), figsize=(6,8))
            for plasnum,plastype in enumerate(['plas','cum','syn']):
                if plastype=='plas':
                    title='wt change'
                    scaling=1000
                else:
                    title=plastype
                    scaling=1
                axes = f.add_subplot(3, 1, plasnum)
                for oid in plastab[plastype]:
                    axes.plot(t,scaling*oid.vec, label=oid.path[-2:])
                axes.set_ylabel(str(scaling)+'*'+title)
                axes.set_title(title +' vs. time')
                axes.legend(loc='best', fontsize=8)
        f.tight_layout()
        f.canvas.draw()

        if grphcurr:
            f = _get_graph('{} currents'.format(neurtype), figsize=(6,12))
            numplots=len(ChanDict)
            for plotnum, channame in enumerate(sorted(ChanDict)):
                try:
                    axes = f.add_subplot(numplots,1,plotnum)
                    toplot = [tab.vec / (parcond.ghKluge if 'chanCa' in tab.path else 1)
                              for tab in currtab[neurtype][channame]]
                    scaling = iso_scaling(*toplot)
                    for vec in toplot:
                        axes.plot(t, vec / scaling.divisor)
                        labelstring=u'{}, {}{}'.format(channame, scaling.unit, curlabl)
                    axes.set_ylabel(labelstring)
                    if plotnum == 1:
                        axes.set_title('current vs. time')
                except:
                    print("no channel", channame)
        f.subplots_adjust(left=0.16, bottom=0.05, right=0.95, top=0.95, hspace=0.26)
        f.canvas.draw()

def SingleGraphSet(traces,currents):
    t = np.linspace(0, simtime, len(traces[0]))
    f=pyplot.figure()
    f.canvas.set_window_title('Voltage')
    axes=f.add_subplot(1,1,1)
    for i in range(len(traces)):
        axes.plot(t,traces[i],label=currents[i])
    axes.set_ylabel('Vm, volts')
    axes.set_xlabel('Time, sec')
    axes.legend(fontsize=8,loc='best')
    f.canvas.draw()
