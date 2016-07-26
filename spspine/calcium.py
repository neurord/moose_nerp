from __future__ import print_function, division
import os
import numpy as np
import moose

from spspine import param_cond, param_chan, param_sim, param_ca_plas

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
    SA=np.pi*length*diam
        #create the calcium pools in each compartment
    caproto=moose.element('/library/'+poolname)
    capool = moose.copy(caproto, comp, poolname)[0]
    vol = SA * capool.thick
    capool.B = 1 / (param_cond.Faraday*vol*2) / param_ca_plas.BufCapacity
    if param_sim.printMoreInfo:
        print("CALCIUM", capool.path, length,diam,capool.thick,vol)
    return capool

def connectVDCC_KCa(ghkYN,comp,capool):
    if ghkYN:
        ghk=moose.element('%s/ghk' %(comp.path))
        moose.connect(capool,'concOut',ghk,'set_Cin')
        moose.connect(ghk,'IkOut',capool,'current')
        if param_sim.printMoreInfo:
            print("CONNECT ghk to ca",ghk.path,capool.path)
        #connect them to the channels
    chan_list = (moose.wildcardFind('{}/#[TYPE=HHChannel]'.format(comp.path)) +
                 moose.wildcardFind('{}/#[TYPE=HHChannel2D]'.format(comp.path)))
    for chan in chan_list:
        channame = chan.path.split('/')[param_cond.chanNameNum]
        if channame.endswith('[0]'):
            channame = channame[:-3]
        if param_chan.ChanDict[channame].calciumPermeable:
            if ghkYN == 0:
                # do nothing if ghkYesNo==1, since already connected the single GHK object
                m = moose.connect(chan, 'IkOut', capool, 'current')
        elif param_cond.isKCaChannel(channame):
            m = moose.connect(capool, 'concOut', chan, 'concen')
            if param_sim.printMoreInfo:
                print("channel message", chan.path, comp.path, m)
 
def connectNMDA(nmdachans,poolname,ghkYesNo):
    #Note that ghk must receive input from SynChan and send output to MgBlock
    for chan in nmdachans:
        if ghkYesNo:
            nmdaCurr=moose.element(chan.path+'/CaCurr/ghk')
        else:
            nmdaCurr=moose.element(chan.path+'/CaCurr/mgblock')
        caname = os.path.join(os.path.dirname(chan.path), poolname)
        capool=moose.element(caname)
        if param_sim.printMoreInfo:
            print("CONNECT", nmdaCurr.path,'to',capool.path)
        n=moose.connect(nmdaCurr, 'IkOut', capool, 'current')
