from __future__ import print_function, division
import os
import numpy as np
import moose

from spspine import constants, logutil
log = logutil.Logger()
def get_path(s):
    l = len(s.split('/')[-1])
    return s[:-l]
    

def addCaDifShell(comp,difparams):
    difproto = moose.element('/library/'+CaName)
    dif = moose.copy(difproto, comp, difparams.name)[0]
    dif.D = difparams.DCa
    dif.valence = 2
    dif.leak = 0
    dif.shapeMode = difparams.shellMode
    dif.length = difparams.shellLength
    dif.diameter = difparams.shellDiameter
    dif.thickness = difparams.Thickness
    return dif

def addDifBuffer(comp,dShell,bufparams):
    shellName = dShell.path.split('/')[-1]
    bufferName = shellName+'_' + bufparams.name
    dbufproto = moose.element('/library/'+CaName)
    dbuf = moose.copy(dbufproto,comp,bufferName)[0]
    dbuf.bTot = bufparams.bTotal
    dbuf.kf = bufparams.kf
    dbuf.kb = bufparams.kb
    dbuf.D = bufparams.DBuf
    dbuf.shapeMode = dShell.shellMode
    dbuf.length = dShell.shellLength
    dbuf.diameter = dShell.diameter
    dbuf.thickness = dShell.thickness
    
    moose.connect(dShell,"concentrationOut",dbuf,"concentration")
    moose.connect(dbuf,"reactionOut",dShell,"reaction")

    return dbuf

def addMMPump(dShell,pumpName,params):
    
    shellName = dShell.path
    pump = moose.MMPump(shellName+'_'+bufferName)
    pump.Vmax = params.Vmax
    pump.Kd = params.Kd

    moose.connect(pump,"pumpOut",dShell,"mmPump")

    return pump
    
    
def CaProto(parameters):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')
    if parameters.caltype = 0:
        return
    if parameters.caltype == 1:
    #if the proto as been created already, this will not create a duplicate
        params = parameters.CaPoolParams
        poolproto = moose.CaConc('/library/'+params.CaName)
        poolproto.CaBasal = params.CaBasal
        poolproto.ceiling = 1.
        poolproto.floor = 0.0
        poolproto.thick = params.CaThick
        poolproto.tau = params.CaTau
        poolproto.B = params.BufCapacity
        return poolproto, None

    
    shellproto = moose.DifShell('/library/'+params.CaName)
    shellproto.Ceq = params.CaBasal
    bufferproto = []
    for buf in  params.ModelBuffers:
        one_buffer = moose.DifBuffer('/library/'+buf.Name)
        bufferproto.append(one_buffer)
    else:
        bufferproto = None
    return shellproto, bufferproto
    

def addCaPool(comp, caproto):
    el = moose.Compartment(comp)

    SA = np.pi*el.length*el.diameter
    #create the calcium pools in each compartment

    capool = moose.copy(caproto, comp, 'CaPool')[0]
    vol = SA * capool.thick
    capool.B = 1 / (constants.Faraday*vol*2) / capool.B #volume correction
    log.debug('CALCIUM {} {} {} {} {}', capool.path, length,diam,capool.thick,vol)
    return capool

def connectVDCC_KCa(model,comp,capool):
    if model.ghkYN:
        ghk = moose.element(comp.path + '/ghk')
        moose.connect(capool,model.CaPlasticityParams.CaOutMessage,ghk,'set_Cin')
        moose.connect(ghk,'IkOut',capool,model.CaPlasticityParams.CurrentMessage)
        log.debug('CONNECT GHK {.path} to Ca {.path}', ghk, capool)
        #connect them to the channels
    chan_list = (moose.wildcardFind(comp.path + '/#[TYPE=HHChannel]') +
                 moose.wildcardFind(comp.path + '/#[TYPE=HHChannel2D]'))

    for chan in chan_list:
        if model.Channels[chan.name].calciumPermeable:
            if not ghkYN:
                # do nothing if ghkYesNo==1, since already connected the single GHK object
                m = moose.connect(chan, 'IkOut', capool, model.CaPlasticityParams.CurrentMessage)
                    
        if model.Channels[chan.name].calciumDependent:
            m = moose.connect(capool, model.CaPlasticityParams.CaOutMessage, chan, 'concen')
            log.debug('channel message {} {} {}', chan.path, comp.path, m)
                

 
def connectNMDA(nmdachans,capool,CurrentMessage,path):
    #nmdachans!!!
    for chan in nmdachans:
        if get_path(chan) == path:
            log.debug('CONNECT {.path} to {.path}', chan, capool)
            moose.connect(chan, 'ICaOut', capool, CurrentMessage)

def addCalcium(model,synArray,headArray,ntype):
    if model.caltype == 0:
        return
    
    pools = CaProto(model.CaPlasticityParams)
    if (model.caltype == 1):
        #put all these calcium parameters into a dictionary
        protopool = pools[0]
        caPools = []
        for comp in moose.wildcardFind(ntype + '/#[TYPE=Compartment]'):
            capool = calcium.addCaPool(comp, protopool)
            caPools.append(capool)
            calcium.connectVDCC_KCa(model,comp,capool)
            #if there are spines, calcium will be added to the spine head
            if model.spineYN:
                
                for spcomp in headArray:

                    capool = calcium.addCaPool(spcomp, protopool)
                    
                    if model.SpineParams.spineChanList:
                        calcium.connectVDCC_KCa(model, spcomp,capool)
                    #if there are synapses, NMDA will be connected to set of calcium pools
                    if model.synYN:
                        calcium.connectNMDA(synArray['nmda'],capool,model.CaPlasticityParams.CurrentMessage,get_path(spcomp.path))
            else:
                
                calcium.connectNMDA(synArray['nmda'],capool,model.CaPlasticityParams.CurrentMessage,get_path(comp.path))
        return caPools  
