#Function definitions for making channels.

def make_synchan(chanpath,synparams):
    print 'synparams:', chanpath, synparams['tau1'], synparams['tau2'], synparams['Erev']
    synchan=moose.SynChan(chanpath)
    synchan.tau1 = synparams['tau1']
    synchan.tau2 = synparams['tau2']
    synchan.Ek = synparams['Erev']
    if synparams['name']=='nmda':
        blockname=chanpath+'/mgblock'
        mgblock=moose.MgBlock(blockname)
        mgblock.KMg_A=mgparams['A']
        mgblock.KMg_B=mgparams['B']
        mgblock.CMg=mgparams['C']
        mgblock.Ek=synparams['Erev']
        mgblock.Zk=2
        print 'nmda',blockname,mgblock,mgparams
        moose.connect(synchan,'channelOut', mgblock,'origChannel')
        if calcium:
        #This duplicate nmda current prevents reversal of calcium current
        #It needs its own Mg Block, since the output will only go to the calcium pool
        #If necessary, can make the decay time faster for the calcium part of NMDA
            synchan2=moose.SynChan(chanpath+'CaCurr')
            synchan2.tau1 = synparams['tau1']
            synchan2.tau2 = synparams['tau2']
            synchan2.Ek = carev
            blockname=chanpath+'CaCurr/mgblock'
            mgblock2=moose.MgBlock(blockname)
            mgblock2.KMg_A=mgparams['A']
            mgblock2.KMg_B=mgparams['B']
            mgblock2.CMg=mgparams['C']
            mgblock2.Ek=carev
            mgblock2.Zk=2
            moose.connect(synchan2,'channelOut', mgblock2,'origChannel')
            if ghkYesNo:
                #Note that ghk must receive input from SynChan and send output to MgBlock
                ghkproto=moose.element('/library/ghk')
                ghk=moose.copy(ghkproto,synchan2.path,'ghk')[0]
                print "CONNECT nmdaCa", synchan2.path, "TO", mgblock2.path, "TO", ghk.path
                moose.connect(mgblock2,'ghk',ghk, 'ghk')
    return synchan

def synchanlib():
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')
    synchan=list()
    for key in SynChanDict.keys():
        chanpath='/library/'+key
        synchan.append(make_synchan(chanpath,SynChanDict[key]))
    print synchan

def addoneSynChan(chanpath,syncomp,gbar,calYN,ghkYN):
    proto=moose.SynChan('/library/' +chanpath)
    if printinfo:
        print "adding channel",chanpath,"to",syncomp.path,"from",proto.path
    synchan=moose.copy(proto,syncomp,chanpath)[0]
    synchan.Gbar = np.random.normal(gbar,gbar*GbarVar)
    if (chanpath=='nmda'):
        #does the mgblock also need to be copied?  No, deep copy.
        mgblock=moose.element(synchan.path+'/mgblock')
        moose.connect(mgblock, 'channel', syncomp, 'channel')
        if calYN:   #create separate nmda channel to keep track of calcium
            proto=moose.SynChan('/library/nmdaCaCurr')
            synchan2=moose.copy(proto,syncomp,chanpath+'CaCurr')[0]
            mgblock2=moose.element(synchan2.path+'/mgblock')
            moose.connect(syncomp,'VmOut',mgblock2,'Vm')
            if ghkYN:
                synchan2.Gbar=synchan.Gbar*nmdaCaFrac*ghKluge
            else:
                synchan2.Gbar=synchan.Gbar*nmdaCaFrac
        else:
            m = moose.connect(syncomp, 'channel', synchan, 'channel')
    return synchan

def add_synchans(container,calYN,ghkYN):
    #synchans is 2D array, where each row has a single channel type
    #at the end they are concatenated into a dictionary
    synchans=[]
    SynPerComp=[]
    numspines=0
    for keynum in range(len(SynChanDict.keys())):
        synchans.append([])
    allkeys=SynChanDict.keys()
    i=0     #i indexes compartment for array that stores number of synapses
    for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(container)):
        SynPerComp.append([0,0])
        #create each type of synchan in each compartment.  Add to 2D array
        for key in DendSynChans:
            keynum=allkeys.index(key)
            Gbar=SynChanDict[key]['Gbar']
            synchans[keynum].append(addoneSynChan(key,comp,Gbar,calYN,ghkYN))
        for key in SpineSynChans:
            keynum=allkeys.index(key)
            Gbar=SynChanDict[key]['Gbar']
            numspines=0   #count number of spines in each compartment
            for spcomp in moose.wildcardFind('%s/#[ISA=Compartment]'%(comp.path)):
                if (find(spcomp.path,'head')>-1):
                    synchans[keynum].append(addoneSynChan(key,spcomp,Gbar,calYN,ghkYN))
                    numspines=numspines+1
        #
        #calculate distance from soma
        xloc=moose.Compartment(comp).x
        yloc=moose.Compartment(comp).y
        dist=sqrt(xloc*xloc+yloc*yloc)
        #create array of number of synapses per compartment based on distance
        #possibly replace NumGlu[] with number of spines, or eliminate this if using real morph
#Check in ExtConn - how is SynPerComp used
        if (dist<distTable['prox']):
            SynPerComp[i][GABA]=NumGaba['prox']
            SynPerComp[i][GLU]=NumGlu['prox']
        else:
            if (dist<distTable['mid']):
                SynPerComp[i][GABA]=NumGaba['mid']
                SynPerComp[i][GLU]=NumGlu['mid']
            else:
                SynPerComp[i][GABA]=NumGaba['dist']
                SynPerComp[i][GLU]=NumGlu['dist']
        i=i+1
    #end of iterating over compartments
    #now, transform the synchans into a dictionary
    allsynchans={}
    for key,keynum in zip(SynChanDict.keys(), range(len(SynChanDict.keys()))):
        allsynchans.__setitem__(key,synchans[keynum])
        
    return SynPerComp,allsynchans

