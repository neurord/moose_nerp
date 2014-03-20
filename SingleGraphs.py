from matplotlib import pyplot
from iso_scaling import iso_scaling

def graphtables(neuron,pltplas,pltcurr,calyesno,capools,curmsg):
    print "GRAPH TABLES, plas=",pltplas,"curr=",pltcurr
    #Vm and Calcium
    vmtab=[]
    catab=[]
    for neurtype in neurontypes:
        vmtab.append([moose.Table('/data/comp%s_%d' % (neurtype,ii)) for ii in range(len(neuron[neurtype]['comps']))])
        if calyesno:
            catab.append([moose.Table('/data/ca%s_%d' % (neurtype,ii)) for ii in range(len(neuron[neurtype]['comps']))])
    for neurnum,neurtype in zip(range(len(neurontypes)),neurontypes):
        for tab, comp in zip(vmtab[neurnum], neuron[neurtype]['comps']):
            moose.connect(tab, 'requestData', comp, 'get_Vm')
        if calyesno:
            for ctab, cal in zip(catab[neurnum], capools[neurtype]):
                moose.connect(ctab, 'requestData', cal, 'get_Ca')
    #
    # synaptic weight and plasticity
    syntab=[]
    plastab=[]
    plasCumtab=[]
    synlegend=[]
    if pltplas:
        for ii,neurtype in zip(range(len(neurontypes)),neurontypes):
            plastab.append(moose.Table('/data/plas'+neurtype))
            plasCumtab.append(moose.Table('/data/plasCum'+neurtype))
            moose.connect(plastab[ii], 'requestData', plas[neurtype]['plas'], 'get_value')
            moose.connect(plasCumtab[ii], 'requestData', plas[neurtype]['cum'], 'get_value')
        for ii,neurtype in zip(range(len(neurontypes)),neurontypes):
            syntab.append(moose.Table('/data/%ssynwt' %neurtype))
            moose.connect(syntab[ii], 'requestData',syn[neurtype].synapse[0],'get_weight')
            synlegend.append(neurtype)
    #
    #
    currtab={}
    for neurtype in neurontypes:
        currtab[neurtype]={}
        for channame in ChanDict:
            currtab[neurtype][channame]=[moose.Table('/data/chan%s%s_%d' %(channame,neurtype,ii)) for ii in range(len(neuron[neurtype]['comps']))]
    for neurtype in neurontypes:
        for channame in ChanDict:
            for tab, comp in zip(currtab[neurtype][channame], neuron[neurtype]['comps']):
                try:
                    chan=moose.element(comp.path+'/'+channame)
                    moose.connect(tab, 'requestData', chan, curmsg)
                except:
                    if printinfo:
                        print 'no channel', comp.path+'/'+channame
    return vmtab,catab,{'syn':syntab,'plas':plastab,'cum':plasCumtab},currtab,synlegend

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

def graphs(vmtab,catab,syntab,currtab,grphsyn,grphcurr,legend,calyesno,curlabl):
    t = np.linspace(0, simtime, len(vmtab[0][0].vec))

    for ii in range(len(neurontypes)):
        f = _get_graph('{} voltage'.format(neurontypes[ii]), figsize=(6,6))
        t = np.linspace(0, simtime, len(vmtab[ii][0].vec))
        axes = f.add_subplot(211) if calyesno else f.gca()
        for oid in vmtab[ii]:
            axes.plot(t, oid.vec, label=oid.path[-5:])
        axes.set_ylabel('Vm {}'.format(neurontypes[ii]))
        axes.legend(fontsize=8, loc='best')
        axes.set_title('voltage vs. time')
        if calyesno:
            axes = f.add_subplot(212)
            for oid in catab[ii]:
                axes.plot(t, oid.vec*1e3, label=oid.path[-5:])
            axes.set_ylabel('calcium, uM')
            axes.legend(fontsize=8, loc='best')
            axes.set_title('calcium vs. time')
        f.tight_layout()
        f.canvas.draw()

        if plotplas:
            f = _get_graph('{} plasticity'.format(neurontypes[ii]), figsize=(6,8))
            for i, a, b in zip((1,2,3),
                               ('plas', 'syn', 'cum'),
                               ('plas', 'wt', 'cum')):
                axes = f.add_subplot(3, 1, i)
                axes.plot(t,syntab[a][ii].vec, label=b+legend[ii])
                axes.legend(loc='upper left', fontsize=10)
                axes.set_title('something vs. time')
        f.tight_layout()
        f.canvas.draw()

        if grphcurr:
            f = _get_graph('{} currents'.format(neurontypes[ii]), figsize=(6,12))
            numplots=len(ChanDict)
            for plotnum, channame in enumerate(sorted(ChanDict)):
                try:
                    axes = f.add_subplot(numplots,1,plotnum)
                    toplot = [tab.vec / (
                        ghKluge if rfind(tab.path,'Ca')==10 else 1)
                            for tab in currtab[neurontypes[ii]][channame]]
                    scaling = iso_scaling(*toplot)
                    for vec in toplot:
                        axes.plot(t, vec / scaling.divisor)
                        labelstring=u'{}, {}{}'.format(channame, scaling.unit, curlabl)
                    axes.set_ylabel(labelstring)
                    if plotnum == 1:
                        axes.set_title('current vs. time')
                except:
                    print "no channel", channame        
        f.subplots_adjust(left=0.16, bottom=0.05, right=0.95, top=0.95, hspace=0.26)
        f.canvas.draw()
