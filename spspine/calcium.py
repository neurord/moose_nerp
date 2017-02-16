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

def addDifBuffer(comp,dShell,dbufproto,bufparams,bTotal):
    
    name = dShell.name + '_' + bufparams.Name

    dbuf = moose.copy(dbufproto,comp,name)[0]
    dbuf.bTot = bTotal
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

def addMMPump(dShell,pumpparams,Vmax):
    
    shellName = ''
    for s in dShell.path.split('[0]'):
        shellName += s
    pump = moose.MMPump(shellName+'_'+pumpparams.Name)
    pump.Vmax = Vmax
    pump.Kd = pumpparams.Kd
    moose.connect(pump,"PumpOut",dShell,"mmPump")
    
    return pump
    
    
def CaProto(model):
    if not model.calYN:
        return
    
    capar = model.CaPlasticityParams.CalciumParams


    if not moose.exists('/library'):
        lib = moose.Neutral('/library')

    concproto = moose.CaConc('/library/'+capar.CaPoolName)
    concproto.tau = capar.tau
    concproto.CaBasal = capar.Ceq
    concproto.ceiling = 1.
    concproto.floor = 0.0
     
    shellproto = moose.DifShell('/library/'+capar.CaName)
    shellproto.Ceq = capar.Ceq
    shellproto.D = capar.DCa
    bufferproto = moose.DifBuffer('/library/'+capar.CaName+'_Buffer')
    
    return concproto, shellproto, bufferproto
    
def connectVDCC_KCa(model,comp,capool,CurrentMessage,CaOutMessage):
  
    if model.ghkYN:
        ghk = moose.element(comp.path + '/ghk')
        moose.connect(capool,CaOutMessage,ghk,'set_Cin')
        moose.connect(ghk,'IkOut',capool,CurrentMessage)
        log.debug('CONNECT GHK {.path} to Ca {.path}', ghk, capool)
        #connect them to the channels
        
    chan_list = [c for c in comp.neighbors['VmOut'] if c.className == 'HHChannel' or c.className == 'HHChannel2D']
  
    for chan in chan_list:
        if model.Channels[chan.name].calciumPermeable:
            if not model.ghkYN:
                # do nothing if ghkYesNo==1, since already connected the single GHK object
                m = moose.connect(chan, 'IkOut', capool, CurrentMessage)
            
        if model.Channels[chan.name].calciumDependent:
            m = moose.connect(capool,CaOutMessage, chan, 'concen')
            log.debug('channel message {} {} {}', chan.path, comp.path, m)
            
def connectNMDA(comp,capool,CurrentMessage):
    #nmdachans!!!
    for chan in moose.element(comp).neighbors['VmOut']:
        if chan.className == 'NMDAChan':
            moose.connect(chan, 'ICaOut', capool, CurrentMessage)

            
def addDifMachineryToComp(model,comp,sgh,capools):
    protodif = capools[0]
    protobuf = capools[1]
    diam_thick = difshell_geometry(comp.diameter, sgh)
    BufferParams = model.CaPlasticityParams.BufferParams
    PumpKm = model.CaPlasticityParams.PumpKm 

    difshell = []
    buffers = []

    for i,(diameter,thickness) in enumerate(diam_thick):
        
        name = protodif.name+'_'+str(i)
        dShell = addCaDifShell(comp,protodif,sgh.shellMode,diameter,thickness,name)
        
        difshell.append(dShell)
        
        b = []
        for j,buf in enumerate(sgh.Buffers):
            b.append(addDifBuffer(comp,dShell,protobuf,BufferParams[buf],sgh.Buffers[buf]))
        buffers.append(b)

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
            for pump in sgh.Pumps:
                Km = PumpKm[pump]
                
                p = addMMPump(dShell,PumpKm[pump],sgh.Pumps[pump])
                #connect channels        
            connectVDCC_KCa(model,comp,dShell,'influx','concentrationOut')
            connectNMDA(comp,dShell,'influx')
       
            
    return difshell
    
def addCaPool(model,params,comp, caproto):
    #create the calcium pools in each compartment
    capool = moose.copy(caproto, comp, caproto.name)[0]
    
    capool.thick = params.outershell_thickness
    SA = comp.diameter*comp.length*np.pi
    vol = SA*capool.thick/2.
    bc = params.BufCapacity
    capool.B = 1. / (constants.Faraday*vol*2) / bc #volume correction
    connectVDCC_KCa(model,comp,capool,'current','concOut')
    
    connectNMDA(comp,capool,'current')
    return capool


def addCalcium(model,ntype):
    
    if model.calYN == 0:
        return
    
    pools = CaProto(model)
    capool = []
    paramsdend = model.CaPlasticityParams.Calcium.dendrite
    paramsspine = model.CaPlasticityParams.Calcium.spine
    for comp in moose.wildcardFind(ntype + '/#[TYPE=Compartment]'):
        xloc = moose.Compartment(comp).x
        yloc = moose.Compartment(comp).y
        dist = np.sqrt(xloc*xloc+yloc*yloc)
        params = util.distance_mapping(paramsdend, dist)
        
        if params.shellMode == -1:
            pool = addCaPool(model,params,comp, pools[0])
            capool.append(pool)
           
            dshells_dend = None
            #if there are spines, calcium will be added to the spine head
        elif params.shellMode == 0 or params.shellMode == 1 or params.shellMode == 3:
            dshells_dend = addDifMachineryToComp(model,comp,params,pools[1:]) 
            capool.append(dshells_dend)
        else:
            print('Unknown shellMode. Leaving')
            return
        if model.spineYN:
            spines = list(set(comp.children)&set(comp.neighbors['raxial']))
            params = util.distance_mapping(paramsspine, dist)
            for sp in spines:
                if params.shellMode == -1:
                    pool = addCaPool(model,params,moose.element(sp), pools[0])
                    capool.append(pool)
                elif params.shellMode == 0 or params.shellMode == 1 or params.shellMode == 3:
                    dshells_neck = addDifMachineryToComp(model,moose.element(sp),params,pools[1:])
                    if dshells_dend: #diffusion between neck and dendrite
                        moose.connect(dshells_neck[-1],"outerDifSourceOut",dshells_dend[0],"fluxFromOut")
                        moose.connect(dshells_dend[0],"innerDifSourceOut",dshells_neck[-1],"fluxFromIn")
                    capool.append(dshells_neck)
                else:
                    print('Unknown shellMode. Leaving')
                    return  
                heads = moose.element(sp).neighbors['raxial']

                for head in heads:
                    if params.shellMode == -1:
                        pool = addCaPool(model,params,moose.element(head), pools[0])
                        
                        capool.append(pool)
                    elif params.shellMode == 0 or params.shellMode == 1 or params.shellMode == 3:
                        dshells_head = addDifMachineryToComp(model,moose.element(head),params,pools[1:])
                        moose.connect(dshells_neck[0],"outerDifSourceOut",dshells_head[-1],"fluxFromOut")
                        moose.connect(dshells_head[-1],"innerDifSourceOut",dshells_neck[0],"fluxFromIn")
                        capool.append(dshells_head)
                    
                    else:
                        print('Unknown shellMode. Leaving')
                        return
   
    return capool
