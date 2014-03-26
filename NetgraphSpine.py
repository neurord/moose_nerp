#1. Verify the plasticity tables
#2. Fix graphs for spines Ca and synapses.
#3. plasticity not working, possibly because totaltt needs to be modified for when synapses in spines and more than one per comp
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
        #assert chan in stab[syntabnum].path
        if (find(stab[syntabnum].path,chan)==-1):
            print "HOOKING UP SYN TABLES WRONG!"
        else:
            moose.connect(stab[syntabnum], 'requestData', syn, Synmsg)
    return vtab,ctab,stab

def spineTables(spineHeads,catab,syntab,calyn):
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
                print syntab[typenum][syntabnum].path, chan
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
        if spineYesNo:
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
                print "Single",comp.path,neurtype,split(comp.path,'/')[compNameNum],'/data/Vm%s_%s' % (neurtype,split(comp.path,'/')[compNameNum])
                vmtab[typenum].append(moose.Table('/data/Vm%s_%s' % (neurtype,split(comp.path,'/')[compNameNum])))
                if calyesno:
                    catab[typenum].append(moose.Table('/data/Ca%s_%s' % (neurtype,split(comp.path,'/')[compNameNum])))
                for chan in DendSynChans:
                    syntab[typenum].append(moose.Table('/data/Gk%s_%s_%s' % (chan,neurtype,split(comp.path,'/')[compNameNum])))
        if spineYesNo:
            for typenum, neurtype in enumerate(sorted(neurontypes)):
                for head in spineHeads[neurtype]:
                    if calcium:
                        print head.path
                        spcatab[typenum].append(moose.Table('/data/SpCa%s_%s' % (neurtype,split(head.path,'/')[compNameNum])))
                    for chan in SpineSynChans:
                         spsyntab[typenum].append(moose.Table('/data/SpGk%s_%s_%s' % (chan,neurtype,split(head.path,'/')[compNameNum])))
        if pltplas:
            for typenum, neurtype in enumerate(sorted(neurontypes)):
                for numtab in range(min(len(SynPlas[ntype]),len(neuron[neurtype]['comps']))): #??
                    plastab[typenum].append(moose.Table('/data/plas%s_%s' % (neurtype,numtab))) #change numtab to comp?
                    plasCumtab[typenum].append(moose.Table('/data/plasCum%s_%s' % (neurtype,numtab)))
        #Connect tables
        print "***********PLOTTING",message[singl],"********************"
        for typenum, neurtype in enumerate(sorted(neurontypes)):
            for tabnum,comp in enumerate(neuron[neurtype]['comps']):
                if singl:
                    plotcomp=comp
                else:
                    comppath=split(comp.path,'/')[compNameNum]
                    plotcomp=moose.element(MSNpop['pop'][typenum][0]+'/'+comppath)
                vmtab[typenum],catab[typenum],syntab[typenum]=connectTables(comp,vmtab[typenum],catab[typenum],syntab[typenum],tabnum, calyesno)
            #tables for spines, or plasticity
            if spineYesNo:
                spcatab[typenum],spsyntab[typenum]=spineTables(spineHeads[typenum],spcatab[typenum],spsyntab[typenum],calyn)
            if pltplas:
                if singl:
                    for neur in range(len(SynPlas[neurtype])): #?? Do we really need to loop over something different?
                        moose.connect(plastab[typenum][neur], 'requestData', SynPlas[neurtype][neur]['plas'], 'get_value')
                        moose.connect(plasCumtab[typenum][neur], 'requestData', SynPlas[neurtype][neur]['cum'], 'get_value')
                else:
                    for neur in range(len(neuron[neurtype]['comps'])):
                        moose.connect(plastab[typenum][neur], 'requestData', SynPlas[neurtype][neur]['plas'], 'get_value')
                        moose.connect(plasCumtab[typenum][neur], 'requestData', SynPlas[neurtype][neur]['cum'], 'get_value')
   else:
        #create and connect tables, one per cell soma
        print "***********PLOTTING NETWORK SOMATA***************"
        for typenum,neurtype in enumerate(sorted(neurontypes)):
            for neurpath in MSNpop['pop'][typenum]:
                neurnum=neurpath[find(neurpath,'_')+1:]
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
