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
    if (pltplas):
        keys=plas.keys()
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
        for channame in ChanDict.keys():
            currtab[neurtype][channame]=[moose.Table('/data/chan%s%s_%d' %(channame,neurtype,ii)) for ii in range(len(neuron[neurtype]['comps']))]
    for neurtype in neurontypes:
        for channame in ChanDict.keys():
            for tab, comp in zip(currtab[neurtype][channame], neuron[neurtype]['comps']):
                chan=moose.element(comp.path+'/'+channame)
                moose.connect(tab, 'requestData', chan, curmsg)
    return vmtab,catab,{'syn':syntab,'plas':plastab,'cum':plasCumtab},currtab,synlegend

def graphs(vmtab,catab,syntab,currtab,grphsyn,grphcurr,legend,calyesno,curlabl):
    t = np.linspace(0, simtime, len(vmtab[0][0].vec))

    for ii in range(len(neurontypes)):
        figure(figsize=(6,6))
        title=neurontypes[ii]
        plt.title(title)
        t = np.linspace(0, simtime, len(vmtab[ii][0].vec))
        if calyesno:
            subplot(211)
        for oid in vmtab[ii]:
            plt.plot(t, oid.vec, label=oid.path[-5:])
        plt.ylabel('Vm %s' %(neurontypes[ii]))
        if calyesno:
            subplot(212)
            for oid in catab[ii]:
                plt.plot(t, oid.vec*1e3, label=oid.path[-5:])
            plt.ylabel('calcium, uM')
        #plt.legend()
        if (plotplas):
            figure(figsize=(6,8))
            plt.title(neurontypes[ii]+'plas')
            subplot(311)
            plt.plot(t,syntab['plas'][ii].vec,label='plas'+legend[ii])
            plt.legend(loc='upper left')
            subplot(312)
            plt.plot(t,syntab['syn'][ii].vec,label='wt'+legend[ii])
            plt.legend(loc='upper left')
            subplot(313)
            plt.plot(t,syntab['cum'][ii].vec,label='cum '+legend[ii])
            plt.legend(loc='upper left')
        if (grphcurr):
            print neurontypes[ii]
            figure(figsize=(6,12))
            plt.title('%s currents' %(neurontypes[ii]))
            numplots=len(ChanDict.keys())
            for channame,plotnum in zip(ChanDict.keys(),range(len(ChanDict.keys()))):
                subplot(numplots,1,plotnum)
                for tab in currtab[neurontypes[ii]][channame]:
                    if (rfind(tab.path,'Ca')==10):
                        fact=ghKluge
                    else:
                        fact=1
                    if np.max(abs(tab.vec*1e12/fact))>1000:
                        plt.plot(t,tab.vec*1e9/fact)
                        labelstring='%s,n%s'%(channame,curlabl)
                    else:
                        plt.plot(t,tab.vec*1e12/fact)
                        labelstring='%s,p%s'%(channame,curlabl)
                plt.ylabel(labelstring)
        #
        #end of for neurtype loop
    plt.show()
