#Cellproto.py
#Other than the special NaF channel, this can be used to create any neuron type
def create_neuron(p_file,container,GnaCond,Cond,ghkYN):
    cellproto=moose.loadModel(p_file, container)
    comps=[]
    #######channels
    for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(container)):
        comps.append(comp)
        length=moose.Compartment(comp).length
        diam=moose.Compartment(comp).diameter
        xloc=moose.Compartment(comp).x
        yloc=moose.Compartment(comp).y
        dist=sqrt(xloc*xloc+yloc*yloc)
        SA=pi*length*diam
        #print "comp,dist,SA",comp.path,dist,SA
        #na channel - not in normal channel dictionary
        chanpath=NaFparam['name']
        proto = moose.HHChannel('/library/'+chanpath)
        nachan = moose.copy(proto, comp, chanpath)[0]
        moose.connect(nachan, 'channel', comp, 'channel')
        nachan.Gbar =GnaCond[dist_num(distTable, dist)] * SA

        #other Channels
        #If we are using GHK, just create one GHK per compartment, connect it to comp
        if ghkYN:
            ghkproto=moose.element('/library/ghk')
            ghk=moose.copy(ghkproto,comp,'ghk')[0]
            moose.connect(ghk,'channel',comp,'channel')
        for key in ChanDict.keys():
            chanpath=key
            proto = moose.HHChannel('/library/'+key)
            chan = moose.copy(proto, comp, chanpath)[0]
            channame=chan.path[rfind(chan.path,'/')+1:]
            #If we are using GHK AND it is a calcium channel, connect it to GHK
            if (ghkYN and isCaChannel(channame)):
                moose.connect(chan,'permeability',ghk,'addPermeability')
                moose.connect(comp,'VmOut',chan,'Vm')
            else:
                moose.connect(chan, 'channel', comp, 'channel')
            #
            #Distance dependent conductances, change distTable[0] to distTable[prox]?
            #Then, just use some look up table function and probably don't need if statement
            chan.Gbar = Cond[key][dist_num(distTable, dist)] * SA

    return {'comps': comps, 'cell': cellproto}

def neuronclasses(pltchan,pltpow,calyesno,synYesNo,spYesNo,ghkYN):
    ##create channels in the library
    chanlib(pltchan,pltpow)
    synchanlib()
    ##now create the neuron prototypes
    neuron={}
    syn={}
    synarray={}
    pathlist=[]
    caPools={}
    headarray={}
    for ntype in neurontypes:
        protoname='/library/'+ntype
        #use pfile[ntype] for cell-type specific morphology
        #create_neuron creates morphology and ion channels only
        neuron[ntype]=create_neuron(pfile,ntype,GnaCondset[ntype],Condset[ntype],ghkYN)
        #optionally add spines
        if spYesNo:
            headarray[ntype]=addSpines(ntype)
        print "headarray", headarray
        pathlist=pathlist+['/'+ntype]
        #optionally add synapses, to dendrites, and possibly to spines
        if synYesNo:
            [synarray[ntype],syn[ntype]]=add_synchans(ntype,calyesno,ghkYN)
            print "in neuronclasses, prin syn", syn
    #Calcium concentration - also optional
    #possibly when FS are added will change this to avoid calcium in the FSI
    if (calyesno==1):
        CaProto(CaThick,CaBasal,CaTau,caName)
        for ntype in neurontypes:
            tempCaPools=[]
            for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(ntype)):
                capool=addCaPool(comp,caName)
                tempCaPools.append(capool)
                connectVDCC_KCa(ghkYesNo,comp,capool)
                #if there are spines, calcium will be added to the spine head
                for spcomp in moose.wildcardFind('%s/#[ISA=Compartment]'%(comp.path)):
                    if (find(spcomp.path,'head')>-1):
                        capool=addCaPool(spcomp,caName)
                        if (len(spineChanList)>0):
                            connectVDCC_KCa(ghkYesNo,spcomp,capool)
            caPools[ntype]=tempCaPools
            #if there are synapses, NMDA will be connected to the appropriate calcium pool
            if synYesNo:
                connectNMDA(syn[ntype]['nmda'],caName,nmdaCaFrac)
    #
    return syn,neuron,pathlist,caPools,synarray
#
