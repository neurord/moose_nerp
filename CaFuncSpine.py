def CaProto(thick,basal,ctau,poolname):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')
    #if the proto as been created already, this will not create a duplicate
    poolproto=moose.CaConc('/library/'+poolname)
    poolproto.CaBasal=basal
    poolproto.ceiling=1
    poolproto.floor=0.0
    poolproto.thick=thick
    poolproto.tau=ctau
    return poolproto

def addCaPool(comp,poolname):
    length=moose.Compartment(comp).length
    diam=moose.Compartment(comp).diameter
    SA=pi*length*diam
        #create the calcium pools in each compartment
    caproto=moose.element('/library/'+poolname)
    capool = moose.copy(caproto, comp, poolname)[0]
    vol=SA*capool.thick
    capool.B = 1/(Faraday*vol*2)/BufCapacity
    #print "CALCIUM", capool.path, length,diam,capool.thick,vol
    return capool

def connectVDCC_KCa(ghkYN,comp,capool):
    if ghkYN:
        ghk=moose.element('%s/ghk' %(comp.path))
        moose.connect(capool,'concOut',ghk,'set_Cin')
        moose.connect(ghk,'IkOut',capool,'current')
        #print "CONNECT ghk to ca",ghk.path,capool.path
        #connect them to the channels
    for chan in moose.wildcardFind('%s/#[TYPE=HHChannel]' %(comp.path)):
        channame=chan.path[rfind(chan.path,'/')+1:]
        if isCaChannel(channame):
            if (ghkYN==0):
                    #do nothing if ghkYesNo==1, since already connected the single GHK object 
                moose.connect(chan, 'IkOut', capool, 'current')
        elif isKCaChannel(channame):
            moose.connect(capool, 'concOut', chan, 'concen')

def connectNMDA(nmdachans,poolname,caFrac):
    #Note that ghk must receive input from SynChan and send output to MgBlock
    for chan in nmdachans:
        if ghkYesNo:
            nmdaCurr=moose.GHK(chan.path+'/CaCurr/ghk')
        else:
            nmdaCurr=moose.MgBlock(chan.path+'/CaCurr/mgblock')
        caname=chan.path[0:rfind(chan.path,'/')+1]+poolname
        capool=moose.CaConc(caname)
        #print "CONNECT", nmdaCurr.path,'to',capool.path
        n=moose.connect(nmdaCurr, 'IkOut', capool, 'current')


