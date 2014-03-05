def graphtables(singl,pltnet,pltplas,calyesno,spinesYN):
    print "GRAPHS","single=",singl,"plotnet=",pltnet,"plotPlas=",pltplas, "cal=", calyesno, "spines=", spinesYN
    syntab=[]
    vmtab=[]
    catab=[]
    plastab=[]
    plasCumtab=[]
    spcatab=[]
    if ((singl == 1) or (pltnet==0)):
        for neurtype in neurontypes:
            for ii in range(len(neuron[neurtype]['comps'])):
                vmtab.append(moose.Table('/data/comp%d_%s' % (ii,neurtype)))
                if calyesno:
                    catab.append(moose.Table('/data/cal%d_%s' % (ii,neurtype)))
                for chan in SynChanDict:
                    syntab.append(moose.Table('/data/Gk%s%d_%s' % (chan,ii,neurtype)))
        if (pltplas):
            for ii,ntype in zip(range(len(neurontypes)),neurontypes):
                plastab.append([])
                plasCumtab.append([])
                spcatab.append([])
                for numtab in range(min(len(SynPlas[ntype]),len(neuron[neurtype]['comps']))):
                    plastab[ii].append(moose.Table('/data/plas%d_%s' % (numtab,ntype)))
                    plasCumtab[ii].append(moose.Table('/data/plasCum%d_%s' % (numtab,ntype)))
                    spcatab[ii].append(moose.Table('/data/spcal%d_%s' % (numtab,ntype)))
        #
        if (singl==1): 
            print "***********PLOTTING SINGLE: 1 spine per compartment"
            tabnum=0
            for neurtype in neurontypes:
                for comp in neuron[neurtype]['comps']:
                    moose.connect(vmtab[tabnum], 'requestData', comp, 'get_Vm')
                    if calyesno:
                        cal=comp.path+'/'+caName
                        moose.connect(catab[tabnum], 'requestData', cal, 'get_Ca')
                    for synnum, chan in enumerate(sorted(DendSynChans)):
                        syn=moose.element(comp.path+'/'+chan)
                        if chan=='nmda':
                            syn=moose.element(comp.path+'/'+chan+'/mgblock')
                        syntabnum=len(SynChanDict)*tabnum+synnum
                        moose.connect(syntab[syntabnum], 'requestData', syn, Synmsg)
                    for chan in SpineSynChans:
                        for spcomp in moose.wildcardFind('%s/#[ISA=Compartment]' %(comp.path)):
                            if (find(spcomp.path,'head')>-1):
                                syn=moose.element(spcomp.path+'/'+chan)
                                if chan=='nmda':
                                    syn=moose.element(spcomp.path+'/'+chan+'/mgblock')
                                synnum=sorted(SynChanDict).index(chan)
                                syntabnum=len(SynChanDict)*tabnum+synnum
                                moose.connect(syntab[syntabnum], 'requestData', syn, Synmsg)
                    tabnum=tabnum+1
            if (pltplas):
                for ii,ntype in zip(range(len(neurontypes)),neurontypes):
                    for neur in range(len(SynPlas[ntype])):
                        moose.connect(plastab[ii][neur], 'requestData', SynPlas[ntype][neur]['plas'], 'get_value')
                        moose.connect(plasCumtab[ii][neur], 'requestData', SynPlas[ntype][neur]['cum'], 'get_value')
                        spcal=SynPlas[ntype][neur]['plas'].path[0:rfind(SynPlas[ntype][neur]['plas'].path,'/')+1]+caName
                        moose.connect(spcatab[ii][neur], 'requestData', moose.element(spcal), 'get_Ca')
        else:
            print "***********PLOTTING ONE FROM NETWORK: no spines allowed"
            tabnum=0
            for neurnum,neurtype in zip(range(len(neurontypes)),neurontypes):
                for ii in range(len(neuron[neurtype]['comps'])):
                    comppath=neuron[neurtype]['comps'][ii].path[rfind(neuron[neurtype]['comps'][ii].path,'/')+1:]
                    plotcomp=moose.element(MSNpop['pop'][neurnum][0]+'/'+comppath)
                    moose.connect(vmtab[tabnum], 'requestData', plotcomp, 'get_Vm')
                    if calyesno:
                        cacomp=moose.element(MSNpop['pop'][neurnum][0]+'/'+comppath+'/'+caName)
                        moose.connect(catab[tabnum], 'requestData', cacomp, 'get_Ca')
                    #print "TABLES", vmtab[tabnum].path,plotcomp.path,catab[tabnum].path,cacomp.path
                    for synnum,chan in enumerate(sorted(SynChanDict)):
                        syn=moose.element(plotcomp.path+'/'+chan)
                        if chan=='nmda':
                            syn=moose.element(plotcomp.path+'/'+chan+'/mgblock')
                        syntabnum=len(SynChanDict)*tabnum+synnum
                        if (find(syntab[syntabnum].path,chan)==-1):
                            print "HOOKING UP SYN TABLES WRONG!"
                        else:
                            moose.connect(syntab[syntabnum], 'requestData', syn, Synmsg)
                    tabnum=tabnum+1
            if (pltplas):
                for ii,ntype in zip(range(len(neurontypes)),neurontypes):
                    for neur in range(len(neuron[neurtype]['comps'])):
                        moose.connect(plastab[ii][neur], 'requestData', SynPlas[ntype][neur]['plas'], 'get_value')
                        moose.connect(plasCumtab[ii][neur], 'requestData', SynPlas[ntype][neur]['cum'], 'get_value')
    else:
        print "***********PLOTTING NETWORK SOMATA"
        for ii in range(len(MSNpop['cells'])):
            typeloc=find(MSNpop['cells'][ii].path,'_')
            neurtype=MSNpop['cells'][ii].path[typeloc-2:typeloc]
            vmtab.append(moose.Table('/data/soma%d_%s'%(ii,neurtype)))
            if calyesno:
                catab.append(moose.Table('/data/cal%d_%s' % (ii,neurtype)))
            for chan in SynChanDict:
                syntab.append(moose.Table('/data/Gk%s%d_%s' % (chan,ii,neurtype)))
        for ii in range(len(MSNpop['cells'])):
            plotcomp=moose.element(MSNpop['cells'][ii].path+'/soma')
            moose.connect(vmtab[ii], 'requestData', plotcomp, 'get_Vm')
            if calyesno:
                cacomp=moose.element(MSNpop['cells'][ii].path+'/soma/'+caName)
                moose.connect(catab[ii], 'requestData', cacomp, 'get_Ca')
            #print "TABLES", vmtab[ii].path,plotcomp.path,catab[ii].path,cacomp.path
            for synnum,chan in enumerate(sorted(SynChanDict)):
                plotsyn=moose.element(plotcomp.path+'/'+chan)
                if chan=='nmda':
                    syn=moose.element(plotcomp.path+'/'+chan+'/mgblock')
                tabnum=len(SynChanDict)*ii+synnum
                if (find(syntab[tabnum].path,chan)==-1):
                    print "HOOKING UP SYN TABLES WRONG!"
                else:
                    moose.connect(syntab[tabnum], 'requestData', plotsyn, Synmsg)
    return vmtab,syntab,catab,plastab,plasCumtab,spcatab

def graphs(vmtab,syntab,catab,plastab,plasCumtab,spcaltab,grphsyn,pltplas,calyesno,spinesYN):
    t = np.linspace(0, simtime, len(vmtab[0].vec))
    for neur in neurontypes:
        figure()
        title=title1+neur
        plt.title(title)
        if calyesno:
            subplot(211)
        for vmoid in vmtab:
            if (find(vmoid.path,neur)>-1):
                plt.plot(t, vmoid.vec, label=vmoid.path[-5:])
        plt.ylabel('Vm')
        plt.legend(loc='upper left')
        if calyesno:
            subplot(212)
            for caoid in catab:
                if (find(caoid.path,neur)>-1):
                    plt.plot(t, caoid.vec*1e3, label=caoid.path[-5:])
            plt.ylabel('calcium, uM')
    #
    if (grphsyn):
        for neur in neurontypes:
            for chan in SynChanDict:
                figure()
                title=title1+neur+chan
                plt.title(title)
                for oid in syntab:
                    if ((find(oid.path,neur)>-1) and (find(oid.path,chan)>-1) and (len(oid.vec)>0)):
                        t = np.linspace(0, simtime, len(oid.vec))
                        plt.plot(t, oid.vec*1e9, label=oid.path[-5:])
                plt.ylabel(SynLabel)
                plt.legend(loc='upper left')
    if (pltplas):
        if (spinesYN==1):
            numplots=3
        else:
            numplots=2
        for ii in range(len(SynPlas)):
            t=np.linspace(0, simtime, len(plastab[ii][0].vec))
            figure(figsize=(6,6))
            plt.title(neurontypes[ii]+'plas')
            subplot(numplots,1,1)
            for oid in plastab[ii]:
                plt.plot(t,oid.vec, label=oid.path[-5:])
            plt.legend(loc='upper left')
            subplot(numplots,1,2)
            for oid in plasCumtab[ii]:
                plt.plot(t,oid.vec, label=oid.path[-5:])
            if (spinesYN==1):
                subplot(numplots,1,3)
                for oid in spcaltab[ii]:
                    plt.plot(t,oid.vec)
    #
    plt.show()

