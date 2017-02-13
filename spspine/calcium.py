from __future__ import print_function, division
import os
import numpy as np
import moose

from spspine import constants, logutil
import util

log = logutil.Logger()

def get_path(s):
    l = len(s.split('/')[-1])
    return s[:-l]

def difshell_geometry(diameter, shell_params):
    res = [] #[[diameter,shell_params.outershell_thickness]]
    
    if shell_params.shellMode == 0:
        multiplier = 2.
        new_rad = diameter/2.
    else:
        multiplier = 1.
        new_rad = diameter

    i = 1
    new_thick = shell_params.outershell_thickness
    if shell_params.increase_mode:
        while new_rad > shell_params.min_thickness + new_thick:
            res.append([new_rad*multiplier,new_thick])
            new_rad = new_rad - new_thick
            new_thick = shell_params.outershell_thickness*shell_params.thickness_increase**i
            i = i+1
        res.append([new_rad,new_rad])
        return res
    
    while new_rad >shell_params.min_thickness+ new_thick:

       
        res.append([new_rad*multiplier,new_thick])
        new_rad = new_rad - new_thick
        new_thick = shell_params.outershell_thickness + i*shell_params.thickness_increase*shell_params.outershell_thickness
        i = i+1
        
    res.append([new_rad,new_rad])    
    return res


        
def addCaDifShell(comp,difproto,shellMode,shellDiameter,shellThickness,name):

    dif = moose.copy(difproto, comp, name)[0]
    dif.valence = 2
    dif.leak = 0
    dif.shapeMode = shellMode
    dif.length = moose.element(comp).length
    dif.diameter = shellDiameter
    dif.thickness = shellThickness
    return dif

def addDifBuffer(comp,dShell,dbufproto,bufparams):
    
    name = dShell.name + '_' + bufparams.Name

    dbuf = moose.copy(dbufproto,comp,name)[0]
    dbuf.bTot = bufparams.bTotal
    dbuf.kf = bufparams.kf
    dbuf.kb = bufparams.kb
    dbuf.D = bufparams.D
    dbuf.shapeMode = dShell.shapeMode
    dbuf.length = dShell.length
    dbuf.diameter = dShell.diameter
    dbuf.thickness = dShell.thickness
    
    moose.connect(dShell,"concentrationOut",dbuf,"concentration")
    moose.connect(dbuf,"reactionOut",dShell,"reaction")

    return dbuf

def addMMPump(dShell,params):
    
    shellName = ''
    for s in dShell.path.split('[0]'):
        shellName += s
    pump = moose.MMPump(shellName+'_'+params.Name)
    pump.Vmax = params.Vmax
    pump.Kd = params.Kd
    print(pump)
    print(dShell)
    moose.connect(pump,"PumpOut",dShell,"mmPump")
    
    return pump
    
    
def CaProto(params):
    
    capar = params.CaParams

    if not capar:
        return

    if not moose.exists('/library'):
        lib = moose.Neutral('/library')


    if capar.DCa == 0 and capar.CaTau >0 and capar.BufCapacity>0:
        #if the proto as been created already, this will not create a duplicate
        poolproto = moose.CaConc('/library/'+capar.Name)
        poolproto.CaBasal = capar.CaBasal
        poolproto.tau = capar.CaTau
        poolproto.B = capar.BufCapacity
        poolproto.ceiling = 1.
        poolproto.floor = 0.0
        return poolproto, None

    
    shellproto = moose.DifShell('/library/'+capar.Name)
    shellproto.Ceq = capar.CaBasal
    
    bufferproto = []
    
    for buf in  params.ModelBuffers:
        one_buffer = moose.DifBuffer('/library/'+buf.Name)
        bufferproto.append(one_buffer)
        print(one_buffer)
    
    return shellproto, bufferproto
    
def connectVDCC_KCa(model,comp,capool):
    if model.ghkYN:
        ghk = moose.element(comp.path + '/ghk')
        moose.connect(capool,model.CaPlasticityParams.CaOutMessage,ghk,'set_Cin')
        moose.connect(ghk,'IkOut',capool,model.CaPlasticityParams.CurrentMessage)
        log.debug('CONNECT GHK {.path} to Ca {.path}', ghk, capool)
        #connect them to the channels
        
    chan_list = [c for c in comp.neighbors['VmOut'] if c.className == 'HHChannel' or c.className == 'HHChannel2D']
  
    for chan in chan_list:
        if model.Channels[chan.name].calciumPermeable:
            if not model.ghkYN:
                # do nothing if ghkYesNo==1, since already connected the single GHK object
                m = moose.connect(chan, 'IkOut', capool, model.CaPlasticityParams.CurrentMessage)
                    
        if model.Channels[chan.name].calciumDependent:
            m = moose.connect(capool, model.CaPlasticityParams.CaOutMessage, chan, 'concen')
            log.debug('channel message {} {} {}', chan.path, comp.path, m)

def connectNMDA(comp,capool,CurrentMessage):
    #nmdachans!!!
    for chan in moose.element(comp).neighbors['VmOut']:
        if chan.className == 'NMDAChan':
            moose.connect(chan, 'ICaOut', capool, CurrentMessage)

            
def addDifMachineryToComp(model,comp,sgh,capools):
    
    protodif = capools[0]
    protobufs = capools[1]
    diam_thick = difshell_geometry(comp.diameter, sgh)
    print(protobufs)
    difshell = []
    buffers = []
    for i,(diameter,thickness) in enumerate(diam_thick):
        name = model.CaPlasticityParams.CaParams.Name+'_'+str(i)
        dShell = addCaDifShell(comp,protodif,sgh.shellMode,diameter,thickness,name)
        difshell.append(dShell)
        
        b = []
        for j,bufparams in enumerate(model.CaPlasticityParams.ModelBuffers):
            b.append(addDifBuffer(comp,dShell,protobufs[j],bufparams))
        buffers.append(b)
        print(buffers)
        if i>0:
            #connect shells
            moose.connect(difshell[i-1],"outerDifSourceOut",difshell[i],"fluxFromOut")
            moose.connect(difshell[i],"innerDifSourceOut",difshell[i-1],"fluxFromIn")
            #connect buffers
            for j,b in enumerate(buffers[i]):
                moose.connect(buffers[i-1][j],"outerDifSourceOut",buffers[i][j],"fluxFromOut")
                moose.connect(buffers[i][j],"innerDifSourceOut",buffers[i-1][j],"fluxFromIn")
        else:
            #Add pumps
            xloc = moose.Compartment(comp).x
            yloc = moose.Compartment(comp).y
            dist = np.sqrt(xloc*xloc+yloc*yloc)
            log.debug('comp {.path} dist {}', comp, dist)
            for pump in model.CaPlasticityParams.Pumps:
                pparams = util.distance_mapping(model.CaPlasticityParams.Pumps[pump], dist)
                if pparams:
                    p = addMMPump(dShell,pparams)
                #connect channels        
            connectVDCC_KCa(model,comp,dShell)
            connectNMDA(comp,dShell,'influx')
            
    return difshell
    
def addCaPool(model,comp, caproto):
    #create the calcium pools in each compartment
    capool = moose.copy(caproto, comp, caproto.name)[0]
    capool.thick = comp.diameter/2.
    SA = comp.diameter*comp.length*np.pi
    vol = SA*capool.thick/2.
    bc = capool.B
    capool.B = 1. / (constants.Faraday*vol*2) / bc #volume correction
    log.debug('CALCIUM {} {} {} {} {}', capool.path, comp.length,comp.diameter,capool.thick,vol)
    connectVDCC_KCa(model,comp,capool)
    connectNMDA(comp,capool,'current')
    return capool


def addCalcium(model,ntype):

    if model.CaPlasticityParams.caltype == 0:
        return
    
    pools = CaProto(model.CaPlasticityParams)
    shell_geometry_dendrite =  model.CaPlasticityParams.CaMorphologyShellDendrite
    shell_geometry_spine = model.CaPlasticityParams.CaMorphologyShellSpine
  
    params = model.CaPlasticityParams
    dparam = model.CaPlasticityParams.ShellParams
    buffers = model.CaPlasticityParams.ModelBuffers
    capool = []
    for comp in moose.wildcardFind(ntype + '/#[TYPE=Compartment]'):
        xloc = moose.Compartment(comp).x
        yloc = moose.Compartment(comp).y
        dist = np.sqrt(xloc*xloc+yloc*yloc)

        if model.CaPlasticityParams.caltype == 1:
            capool.append( addCaPool(model,comp, pools[0]))
            #if there are spines, calcium will be added to the spine head
        else:

            sgh = util.distance_mapping(shell_geometry_dendrite, dist)
            capool.append(addDifMachineryToComp(model,comp,sgh,pools))
        if model.spineYN:
            spines = list(set(comp.children)&set(comp.neighbors['raxial']))
            for sp in spines:
                if model.CaPlasticityParams.caltype == 1:
                    capool.append(addCaPool(model,sp, pools[0]))
                else:
                    sgh = util.distance_mapping(shell_geometry_spine, dist)
                    capool.append(addDifMachineryToComp(model,sp,sgh,params))
                    
                heads = moose.element(sp).neighbors['raxial']
                for head in heads:
                    if model.CaPlasticityParams.caltype == 1:
                        capool.append(addCaPool(model,head, pools[0]))
                    else:
                        sgh = util.distance_mapping(shell_geometry_spine, dist)
                        capool.append(AddDifMachineryToComp(model,comp,sgh,params,pools))


    return capool
