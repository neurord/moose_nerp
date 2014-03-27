#CellprotoSPine.py
#Other than the special NaF channel, this can be used to create any neuron type

from util import dist_num

def addOneChan(chanpath,gbar,comp,ghkYN,ghk=None):
    length=moose.Compartment(comp).length
    diam=moose.Compartment(comp).diameter
    SA=pi*length*diam
    proto = moose.element('/library/'+chanpath)
    chan = moose.copy(proto, comp, chanpath)[0]
    chan.Gbar = gbar * SA
    #If we are using GHK AND it is a calcium channel, connect it to GHK
    if (ghkYN and isCaChannel(chanpath)):
        ghk=moose.element(comp.path+'/ghk')
        moose.connect(chan,'permeability',ghk,'addPermeability')
        m=moose.connect(comp,'VmOut',chan,'Vm')
    else:
        m=moose.connect(chan, 'channel', comp, 'channel')
    if printMoreInfo:
        print "channel message", chan.path,comp.path, m
    return

def create_neuron(p_file,container,Cond,ghkYN):
    cellproto=moose.loadModel(p_file, container)
    comps=[]
    #######channels
    for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(container)):
        comps.append(comp)
        xloc=moose.Compartment(comp).x
        yloc=moose.Compartment(comp).y
        #Possibly this should be replaced by pathlength
        dist=sqrt(xloc*xloc+yloc*yloc)
        if printMoreInfo:
            print "comp,dist",comp.path,dist
        #
        #If we are using GHK, just create one GHK per compartment, connect it to comp
        #calcium concentration is connected in a different function
        if ghkYN:
            ghkproto=moose.element('/library/ghk')
            ghk=moose.copy(ghkproto,comp,'ghk')[0]
            moose.connect(ghk,'channel',comp,'channel')
        else:
            ghk=[]
        for chanpath in ChanDict:
            if Cond[chanpath][dist_num(distTable, dist)]:
                if printMoreInfo:
                    print "Testing Cond If", chanpath, Cond[chanpath][dist_num(distTable, dist)]
                addOneChan(chanpath,Cond[chanpath][dist_num(distTable, dist)],comp, ghkYN, ghk)
    return {'comps': comps, 'cell': cellproto}

def neuronclasses(plotchan,plotpow,calyesno,synYesNo,spYesNo,ghkYN):
    ##create channels in the library
    chanlib(plotchan,plotpow)
    synchanlib()
    ##now create the neuron prototypes
    neuron={}
    synArray={}
    numSynArray={}
    caPools={}
    headArray={}
    for ntype in neurontypes:
        protoname='/library/'+ntype
        #use p_file[ntype] for cell-type specific morphology
        #create_neuron creates morphology and ion channels only
        neuron[ntype]=create_neuron(p_file,ntype,Condset[ntype],ghkYN)
        #optionally add spines
        if spYesNo:
            headArray[ntype]=addSpines(ntype)
        #optionally add synapses to dendrites, and possibly to spines
        if synYesNo:
            numSynArray[ntype], synArray[ntype] = add_synchans(ntype, calyesno, ghkYN)
        caPools[ntype]=[]
    #Calcium concentration - also optional
    #possibly when FS are added will change this to avoid calcium in the FSI
    if calyesno:
        CaProto(CaThick,CaBasal,CaTau,caName)
        for ntype in neurontypes:
            for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(ntype)):
                capool=addCaPool(comp,caName)
                caPools[ntype].append(capool)
                connectVDCC_KCa(ghkYesNo,comp,capool)
            #if there are spines, calcium will be added to the spine head
            if spYesNo:
                for spcomp in headArray[ntype]:
                    capool=addCaPool(spcomp,caName)
                    if spineChanList:
                        connectVDCC_KCa(ghkYesNo,spcomp,capool)
            #if there are synapses, NMDA will be connected to set of calcium pools
            if synYesNo:
                connectNMDA(synArray[ntype]['nmda'],caName)
    return synArray,neuron,caPools,numSynArray,headArray
