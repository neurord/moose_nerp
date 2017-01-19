from __future__ import print_function, division
import os
import numpy as np
import moose

from spspine import constants, logutil
log = logutil.Logger()

def createCaDifShell(shellName,params):
    dif = moose.DifShell(shellName)
    dif.Ceq = params.CaBasal
    dif.D = params.DCa
    dif.valence = 2
    dif.leak = 0
    dif.shapeMode = params.shellMode
    dif.length = params.shellLength
    dif.diameter = params.shellDiameter
    dif.thickness = params.shellThickness
    return dif

def addDifBuffer(dShell,bufferName,params):
    shellName = dShell.path
    dbuf = moose.DifBuffer(shellName+'_'+bufferName)
    dbuf.bTot = params.bTotal
    dbuf.kf = params.kf
    dbuf.kb = params.kb
    dbuf.D = params.DBuf
    dbuf.shapeMode = dShell.shellMode
    dbuf.length = dShell.shellLength
    dbuf.diameter = dShell.diameter
    dbuf.thickness = dShell.thickness
    
    moose.connect(dShell,"concentrationOut",buf,"concentration")
    moose.connect(buf,"reactionOut",dShell,"reaction")

    return dbuf

def addMMPump(dShell,pumpName,params):
    
    shellName = dShell.path
    pump = moose.MMPump(shellName+'_'+bufferName)
    pump.Vmax = params.Vmax
    pump.Kd = params.Kd

    moose.connect(pump,"pumpOut",dShell,"mmPump")

    return pump
    
 

    
def CaProto(params):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')
    #if the proto as been created already, this will not create a duplicate
    poolproto = moose.CaConc('/library/CaPool')
    poolproto.CaBasal = params.CaBasal
    poolproto.ceiling = 1
    poolproto.floor = 0.0
    poolproto.thick = params.CaThick
    poolproto.tau = params.CaTau
    return poolproto

def addCaPool(model, comp):
    length=moose.Compartment(comp).length
    diam=moose.Compartment(comp).diameter
    SA=np.pi*length*diam
        #create the calcium pools in each compartment
    caproto = moose.element('/library/CaPool')
    capool = moose.copy(caproto, comp, 'CaPool')[0]
    vol = SA * capool.thick
    capool.B = 1 / (constants.Faraday*vol*2) / model.CaPlasticityParams.BufCapacity
    log.debug('CALCIUM {} {} {} {} {}', capool.path, length,diam,capool.thick,vol)
    return capool

def connectVDCC_KCa_pools(model, ghkYN,comp,capool,CaOutMessage,CurrentMessage):
    if ghkYN:
        ghk = moose.element(comp.path + '/ghk')
        moose.connect(capool,CaOutMessage,ghk,'set_Cin')
        moose.connect(ghk,'IkOut',capool,CurrentMessage)
        log.debug('CONNECT GHK {.path} to Ca {.path}', ghk, capool)
        #connect them to the channels
    chan_list = (moose.wildcardFind(comp.path + '/#[TYPE=HHChannel]') +
                 moose.wildcardFind(comp.path + '/#[TYPE=HHChannel2D]'))
    for chan in chan_list:
        if model.Channels[chan.name].calciumPermeable:
            if not ghkYN:
                # do nothing if ghkYesNo==1, since already connected the single GHK object
                m = moose.connect(chan, 'IkOut', capool, CurrentMessage)
                    
        if model.Channels[chan.name].calciumDependent:
            m = moose.connect(capool, CaOutMessage, chan, 'concen')
            log.debug('channel message {} {} {}', chan.path, comp.path, m)
                
def connectVDCC_KCa(model, ghkYN,comp,capool):
    if model.caltype == 1:
        CaOutMessage = 'concOut'
        CurrentMessgae = 'current'
    elif model.caltype == 1:
        CaOutMessage = 'concentrationOut'
        CurrentMessgae = 'influx'
                
    connectVDCC_KCa_pools(model, ghkYN,comp,capool,CaOutMessage,CurrentMessage)
 
def connectNMDA(nmdachans, ghkYesNo):
    for chan in nmdachans:
        caname = os.path.dirname(chan.path) + '/CaPool'
        capool = moose.element(caname)
        log.debug('CONNECT {.path} to {.path}', chan, capool)
        moose.connect(chan, 'ICaOut', capool, 'current')
