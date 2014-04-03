from __future__ import print_function, division

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
    if printMoreInfo:
        print("CALCIUM", capool.path, length,diam,capool.thick,vol)
    return capool

def connectVDCC_KCa(ghkYN,comp,capool):
    if ghkYN:
        ghk=moose.element('%s/ghk' %(comp.path))
        moose.connect(capool,'concOut',ghk,'set_Cin')
        moose.connect(ghk,'IkOut',capool,'current')
        if printMoreInfo:
            print("CONNECT ghk to ca",ghk.path,capool.path)
        #connect them to the channels
    chan_list = []
    chan_list.extend(moose.wildcardFind('%s/#[TYPE=HHChannel]' %(comp.path)))
    chan_list.extend(moose.wildcardFind('%s/#[TYPE=HHChannel2D]' %(comp.path)))
    for chan in chan_list:
        channame = chan.path.split('/')[chanNameNum]
        if isCaChannel(channame):
            if (ghkYN==0):
                    #do nothing if ghkYesNo==1, since already connected the single GHK object 
                m=moose.connect(chan, 'IkOut', capool, 'current')
        elif isKCaChannel(channame):
            m=moose.connect(capool, 'concOut', chan, 'concen')
            if printMoreInfo:
                print("channel message", chan.path,comp.path, m)
    return
 
def connectNMDA(nmdachans,poolname):
    #Note that ghk must receive input from SynChan and send output to MgBlock
    for chan in nmdachans:
        if ghkYesNo:
            nmdaCurr=moose.element(chan.path+'/CaCurr/ghk')
        else:
            nmdaCurr=moose.element(chan.path+'/CaCurr/mgblock')
        caname = os.path.join(os.path.dirname(chan.path), poolname)
        capool=moose.element(caname)
        if printMoreInfo:
            print("CONNECT", nmdaCurr.path,'to',capool.path)
        n=moose.connect(nmdaCurr, 'IkOut', capool, 'current')
    return
