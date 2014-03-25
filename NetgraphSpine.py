#1. Verify the plasticity stuff
#2. Add graphs for spines, and spine synapses.

def connectTables(vcomp,vtab,ctab,stab,tabnum,calyn):
    if printinfo:
        print "VTABLES", vtab[tabnum].path,vcomp.path
    m=moose.connect(vtab[tabnum], 'requestData', vcomp, 'get_Vm')
    print m
    if calyn:
        cacomp=moose.element(vcomp.path+'/'+caName)
        if printinfo:
            print "CTABLES", ctab[tabnum].path,cacomp.path
        moose.connect(ctab[tabnum], 'requestData', cacomp, 'get_Ca')
    for synnum,chan in enumerate(DendSynChans):
        syn=moose.element(vcomp.path+'/'+chan)
        if chan=='nmda':
            syn=moose.element(syn.path+'/mgblock')
        syntabnum=len(DendSynChans)*tabnum+synnum
        if printinfo:
            print stab[syntabnum].path, chan
        #assert chan in stab[syntabnum].path
        if (find(stab[syntabnum].path,chan)==-1):
            print "HOOKING UP SYN TABLES WRONG!"
        else:
            moose.connect(stab[syntabnum], 'requestData', syn, Synmsg)
    return vtab,ctab,stab

def graphtables(singl,pltnet,pltplas,calyesno,spinesYN):
    print "GRAPHS","single=",singl,"plotnet=",pltnet,"plotPlas=",pltplas, "cal=", calyesno, "spines=", spinesYN
    syntab=[]
    vmtab=[]
    catab=[]
    plastab=[]
    plasCumtab=[]
    spcatab=[]
    for typenum,neurtype in enumerate(sorted(neurontypes)):
        vmtab.append([])
        catab.append([])
        syntab.append([])
    #
    if singl or not pltnet:
        #create tables, one per neuron compartment
        for typenum, neurtype in enumerate(sorted(neurontypes)):
            for comp in neuron[neurtype]['comps']:
                print "Single",comp.path,neurtype,split(comp.path,'/')[compNameNum],'/data/VM%s_%s' % (neurtype,split(comp.path,'/')[compNameNum])
                vmtab[typenum].append(moose.Table('/data/VM%s_%s' % (neurtype,split(comp.path,'/')[compNameNum])))
                if calyesno:
                    catab[typenum].append(moose.Table('/data/CA%s_%s' % (neurtype,split(comp.path,'/')[compNameNum])))
                for chan in DendSynChans:
                    syntab[typenum].append(moose.Table('/data/GK%s_%s_%s' % (chan,neurtype,split(comp.path,'/')[compNameNum])))
        if pltplas:
            for typenum, neurtype in enumerate(sorted(neurontypes)):
                plastab.append([])
                plasCumtab.append([])
                spcatab.append([])
                for numtab in range(min(len(SynPlas[ntype]),len(neuron[neurtype]['comps']))): #??
                    plastab[typenum].append(moose.Table('/data/plas%d_%s' % (neurtype,numtab)))
                    plasCumtab[typenum].append(moose.Table('/data/plasCum%d_%s' % (neurtype,numtab)))
                    spcatab[typenum].append(moose.Table('/data/spcal%d_%s' % (neurtype,numtab)))
        #Connect tables
        if singl:
            print "***********PLOTTING SINGLE********************"
            for typenum, neurtype in enumerate(sorted(neurontypes)):
                for compnum,comp in enumerate(neuron[neurtype]['comps']):
                    vmtab[typenum],catab[typenum],syntab[typenum]=connectTables(comp,vmtab[typenum],catab[typenum],syntab[typenum],compnum, calyesno)
            if pltplas:
                for ii, ntype in enumerate(sorted(neurontypes)):
                    for neur in range(len(SynPlas[ntype])):
                        moose.connect(plastab[ii][neur], 'requestData', SynPlas[ntype][neur]['plas'], 'get_value')
                        moose.connect(plasCumtab[ii][neur], 'requestData', SynPlas[ntype][neur]['cum'], 'get_value')
                        spcal=SynPlas[ntype][neur]['plas'].path[0:rfind(SynPlas[ntype][neur]['plas'].path,'/')+1]+caName
                        moose.connect(spcatab[ii][neur], 'requestData', moose.element(spcal), 'get_Ca')
        else:
            print "***********PLOTTING ONE FROM NETWORK**************"
            for typenum, neurtype in enumerate(sorted(neurontypes)):
                for tabnum,comp in enumerate(neuron[neurtype]['comps']):
                    comppath=split(comp.path,'/')[compNameNum]
                    plotcomp=moose.element(MSNpop['pop'][typenum][0]+'/'+comppath)
                    vmtab[typenum],catab[typenum],syntab[typenum]=connectTables(plotcomp,vmtab[typenum],catab[typenum],syntab[typenum],tabnum, calyesno)
            if pltplas:
                for ii,ntype in enumerate(sorted(neurontypes)):
                    for neur in range(len(neuron[neurtype]['comps'])):
                        moose.connect(plastab[ii][neur], 'requestData', SynPlas[ntype][neur]['plas'], 'get_value')
                        moose.connect(plasCumtab[ii][neur], 'requestData', SynPlas[ntype][neur]['cum'], 'get_value')
    else:
        #create and connect tables, one per cell soma
        print "***********PLOTTING NETWORK SOMATA***************"
        for typenum,neurtype in enumerate(sorted(neurontypes)):
            for neurpath in MSNpop['pop'][typenum]:
                neurnum=neurpath[find(neurpath,'_')+1:]
                vmtab[typenum].append(moose.Table('/data/soma%s_%s' % (neurtype,neurnum)))
                if calyesno:
                    catab[typenum].append(moose.Table('/data/cal%s_%s' % (neurtype,neurnum)))
                for chan in DendSynChans:
                    syntab[typenum].append(moose.Table('/data/Gk%s%s_%s' % (chan,neurtype,neurnum)))
            for tabnum,neurpath in enumerate(MSNpop['pop'][typenum]):
                plotcomp=moose.element(neurpath+'/soma')
                vmtab[typenum],catab[typenum],syntab[typenum]=connectTables(plotcomp,vmtab[typenum],catab[typenum],syntab[typenum],tabnum,calyesno)
    return vmtab,syntab,catab,plastab,plasCumtab,spcatab

def graphs(vmtab,syntab,catab,plastab,plasCumtab,spcaltab,grphsyn,pltplas,calyesno,spinesYN):
    t = np.linspace(0, simtime, len(vmtab[0][0].vec))
    for typenum,neur in enumerate(sorted(neurontypes)):
        figure()
        title=title1+neur
        plt.title(title)
        if calyesno:
            subplot(211)
        for vmoid in vmtab[typenum]:
            if (find(vmoid.path,neur)>-1):
                plt.plot(t, vmoid.vec, label=vmoid.path[find(vmoid.path,'_')+1:])
        plt.ylabel('Vm')
        plt.legend(loc='upper left')
        if calyesno:
            subplot(212)
            for caoid in catab[typenum]:
                if (find(caoid.path,neur)>-1):
                    plt.plot(t, caoid.vec*1e3, label=caoid.path[find(caoid.path,'_')+1:])
            plt.ylabel('calcium, uM')
    #
    if grphsyn:
        for typenum,neur in enumerate(sorted(neurontypes)):
            f=figure()
            for i,chan in enumerate(DendSynChans):
                axes=f.add_subplot(len(DendSynChans),1,i)
                axes.set_title(neur+chan)
                for oid in syntab[typenum]:
                    if (chan in oid.path) and (len(oid.vec)>0):
                        print "graphSyn", oid.path, chan
                        t = np.linspace(0, simtime, len(oid.vec))
                        plt.plot(t, oid.vec*1e9, label=oid.path[rfind(oid.path,'_')+1:])
                plt.ylabel(SynLabel)
                plt.legend(loc='upper left')
    if pltplas:
        numplots = 3 if spinesYN else 2
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
            if spinesYN:
                subplot(numplots,1,3)
                for oid in spcaltab[ii]:
                    plt.plot(t,oid.vec)
    #
    plt.show()
