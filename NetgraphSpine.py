#NetgraphSpine.py

def connectTables(vcomp,vtab,ctab,stab,tabnum,calyn):
    if printinfo:
        print "VTABLES", vtab[tabnum].path,vcomp.path
    m=moose.connect(vtab[tabnum], 'requestData', vcomp, 'get_Vm')
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
        assert chan in stab[syntabnum].path
        moose.connect(stab[syntabnum], 'requestData', syn, Synmsg)
    return vtab,ctab,stab

def spineTables(spineHeads,catab,syntab,calyn):
    for typenum, neurtype in enumerate(sorted(neurontypes)):
        for headnum,head in enumerate(spineHeads[neurtype]):
            if calyn:
                spcal=head.path+'/'+caName
                moose.connect(catab[typenum][headnum], 'requestData', moose.element(spcal), 'get_Ca')
            for synnum,chan in enumerate(SpineSynChans):
                syn=moose.element(head.path+'/'+chan)
                if chan=='nmda':
                    syn=moose.element(syn.path+'/mgblock')
                syntabnum=len(SpineSynChans)*headnum+synnum
                if printinfo:
                    print syn.path,syntab[typenum][syntabnum].path, chan
                assert chan in syntab[typenum][syntabnum].path
                moose.connect(syntab[typenum][syntabnum], 'requestData', syn, Synmsg)
    return catab,syntab

def graphtables(singl,pltnet,pltplas,calyesno,spinesYN):
    print "GRAPHS","single=",singl,"plotnet=",pltnet,"plotPlas=",pltplas, "cal=", calyesno, "spines=", spinesYN
    message=["ONE FROM NETWORK","SINGLE"]
    syntab=[]
    vmtab=[]
    catab=[]
    spcatab=[]
    spsyntab=[]
    plastab=[]
    plasCumtab=[]
    for typenum,neurtype in enumerate(sorted(neurontypes)):
        vmtab.append([])
        catab.append([])
        syntab.append([])
        if spinesYN:
            spcatab.append([])
            spsyntab.append([])
        if pltplas:
            plastab.append([])
            plasCumtab.append([])
    #
    if singl or not pltnet:
        #create tables, one per neuron compartment
        for typenum, neurtype in enumerate(sorted(neurontypes)):
            for comp in neuron[neurtype]['comps']:
                compname = comp.path.split('/')[compNameNum]
                #print "Single",comp.path,neurtype,split(comp.path,'/')[compNameNum],'/data/Vm%s_%s' % (neurtype,split(comp.path,'/')[compNameNum])
                vmtab[typenum].append(moose.Table('/data/Vm%s_%s' % (neurtype, compname)))
                if calyesno:
                    catab[typenum].append(moose.Table('/data/Ca%s_%s' % (neurtype,compname)))
                for chan in DendSynChans:
                    syntab[typenum].append(moose.Table('/data/Gk%s_%s_%s' % (chan,neurtype,compname)))
            if spinesYN:
                for head in spineHeads[neurtype]:
                    if calcium:
                        p = head.path.split('/')
                        spinename = p[compNameNum] + p[spineNameNum][spineNumLoc]
                        spcatab[typenum].append(moose.Table('/data/SpCa%s_%s' % (neurtype,spinename)))
                    for chan in SpineSynChans:
                         spsyntab[typenum].append(moose.Table('/data/SpGk%s_%s_%s' % (chan,neurtype,spinename)))
            if pltplas:
                for plas in SynPlas[neurtype]: 
                    p = plas['plas'].path.split('/')
                    plasname = p[compNameNum] + p[spineNameNum][spineNumLoc]
                    plastab[typenum].append(moose.Table('/data/plas%s_%s' % (neurtype,plasname))) 
                    plasCumtab[typenum].append(moose.Table('/data/plasCum%s_%s' % (neurtype,plasname))) 
        #Connect tables
        print "***********PLOTTING",message[singl],"********************"
        for typenum, neurtype in enumerate(sorted(neurontypes)):
            for tabnum,comp in enumerate(neuron[neurtype]['comps']):
                if singl:
                    plotcomp=comp
                else:
                    comppath= comp.path.split('/')[compNameNum]
                    plotcomp=moose.element(MSNpop['pop'][typenum][0]+'/'+comppath)
                vmtab[typenum],catab[typenum],syntab[typenum]=connectTables(plotcomp,vmtab[typenum],catab[typenum],syntab[typenum],tabnum, calyesno)
            #tables for spines, or plasticity
            if pltplas:
                for tabnum,plasObject in enumerate(SynPlas[neurtype]):
                    print plasObject
                    moose.connect(plastab[typenum][tabnum], 'requestData', plasObject['plas'], 'get_value')
                    moose.connect(plasCumtab[typenum][tabnum], 'requestData', plasObject['cum'], 'get_value')
        if spinesYN:
            spcatab,spsyntab=spineTables(spineHeads,spcatab,spsyntab,calyesno)
    else:
        #create and connect tables, one per cell soma.  
        print "***********PLOTTING NETWORK SOMATA***************"
        for typenum,neurtype in enumerate(sorted(neurontypes)):
            for neurpath in MSNpop['pop'][typenum]:
                neurnum = neurpath.partition('_')[2]
                vmtab[typenum].append(moose.Table('/data/soma%s_%s' % (neurtype,neurnum)))
                if calyesno:
                    catab[typenum].append(moose.Table('/data/Ca%s_%s' % (neurtype,neurnum)))
                for chan in DendSynChans:
                    syntab[typenum].append(moose.Table('/data/Gk%s%s_%s' % (chan,neurtype,neurnum)))
            for tabnum,neurpath in enumerate(MSNpop['pop'][typenum]):
                plotcomp=moose.element(neurpath+'/soma')
                vmtab[typenum],catab[typenum],syntab[typenum]=connectTables(plotcomp,vmtab[typenum],catab[typenum],syntab[typenum],tabnum,calyesno)
    return vmtab,syntab,catab,plastab,plasCumtab,spcatab,spsyntab

def graphs(vmtab,syntab,catab,plastab,plasCumtab,spcaltab,grphsyn,pltplas,calyesno,spinesYN):
    t = np.linspace(0, simtime, len(vmtab[0][0].vec))
    for typenum,neur in enumerate(sorted(neurontypes)):
        f=figure()
        f.canvas.set_window_title(neur+' Vm')
        if calyesno:
            subplot(211)
        for vmoid in vmtab[typenum]:
            if neur in vmoid.path:
                plt.plot(t, vmoid.vec, label=vmoid.path.partition('_')[2])
        plt.ylabel('Vm, volts')
        plt.legend(fontsize=8,loc='upper left')
        if calyesno:
            subplot(212)
            for caoid in catab[typenum]:
                if neur in caoid.path:
                    plt.plot(t, caoid.vec*1e3, label=caoid.path.partition('_')[2])
            plt.ylabel('calcium, uM')
    #
    if grphsyn:
        for typenum,neur in enumerate(sorted(neurontypes)):
            f=figure()
            f.canvas.set_window_title(neur+' Dend SynChans')
            for i,chan in enumerate(DendSynChans):
                axes=f.add_subplot(len(DendSynChans),1,i+1)
                axes.set_title(neur+chan)
                for oid in syntab[typenum]:
                    if chan in oid.path and len(oid.vec) > 0:
                        t = np.linspace(0, simtime, len(oid.vec))
                        axes.plot(t, oid.vec*1e9, label=oid.path.rpartition('_')[2])
                axes.set_ylabel('I (nA), {}'.format(chan))
                axes.legend(fontsize=8,loc='upper left')
    if pltplas:
        numplots = 2
        for typenum in range(len(SynPlas)):
            t=np.linspace(0, simtime, len(plastab[typenum][0].vec))
            f = plt.figure(figsize=(6,6))
            f.canvas.set_window_title(neurontypes[typenum]+'plas')
            axes=f.add_subplot(numplots,1,1)
            for oid in plastab[typenum]:
                axes.plot(t,oid.vec*1000, label=oid.path.rpartition('_')[2])
            axes=f.add_subplot(numplots,1,2)
            for oid in plasCumtab[typenum]:
                axes.plot(t,oid.vec, label=oid.path.rpartition('_')[2])
            axes.legend(fontsize=8,loc='best')
    if spinesYN:
        for typenum,neur in enumerate(sorted(neurontypes)):
            f = plt.figure()
            f.canvas.set_window_title("Spines {}".format(neur))
            numplots = len(SpineSynChans)+1
            for i,chan in enumerate(SpineSynChans):
                axes=f.add_subplot(numplots,1,i+1)
                axes.set_ylabel('I (nA) {}'.format(chan))
                for oid in spsyntab[typenum]:
                    if (chan in oid.path) and (len(oid.vec)>0):
                        t = np.linspace(0, simtime, len(oid.vec))
                        axes.plot(t, oid.vec*1e9, label=oid.path.rpartition('_')[2])
                axes.legend(fontsize=8,loc='best')
                axes.set_title('current vs. time')
            axes=f.add_subplot(numplots,1,numplots)
            axes.set_ylabel('calcium, uM')
            for oid in spcaltab[typenum]:
                axes.plot(t,oid.vec, label=oid.path.rpartition('_')[2])
            axes.legend(fontsize=8,loc='best')
            axes.set_title('Spine Ca vs. time')
            f.tight_layout()
            f.canvas.draw()
