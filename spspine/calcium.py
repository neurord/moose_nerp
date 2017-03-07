from __future__ import print_function, division
import os
import numpy as np
import moose

from spspine import constants, logutil
import util
from spspine.spines import NAME_NECK, NAME_HEAD

CalciumConfig = util.NamedList('CalciumConfig','''
shellMode
increase_mode
outershell_thickness
thickness_increase
min_thickness
''')


log = logutil.Logger()

def get_path(s):
    l = len(s.split('/')[-1])
    return s[:-l]

def difshell_geometry(diameter, shell_params):
    res = []

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
            new_thick = shell_params.outershell_thickness+shell_params.outershell_thickness*shell_params.thickness_increase**i
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
    #Old versions of moose don't have difshells. This should be removed.
    try:
        shellproto = moose.DifShell('/library/'+capar.CaName)
        shellproto.Ceq = capar.Ceq
        shellproto.D = capar.DCa
        bufferproto = moose.DifBuffer('/library/'+capar.CaName+'_Buffer')
    
        return concproto, shellproto, bufferproto
    except:
        return concproto,
    
    
    
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
                log.debug('channel {.path} to Ca {.path}',chan, capool)

        if model.Channels[chan.name].calciumDependent:

            m = moose.connect(capool,CaOutMessage, chan, 'concen')
            log.debug('channel message {} {} {}', chan.path, comp.path, m)

def connectNMDA(comp,capool,CurrentMessage):
    #nmdachans!!!
    for chan in moose.element(comp).neighbors['VmOut']:
        if chan.className == 'NMDAChan':
            moose.connect(chan, 'ICaOut', capool, CurrentMessage)

            
def addDifMachineryToComp(model,comp,capools,Buffers,Pumps,sgh):
    protodif, protobuf = capools
    if sgh.shellMode:
        diam_thick = difshell_geometry(comp.diameter,sgh)
    else:
        diam_thick = difshell_geometry(comp.length, sgh)

    BufferParams = model.CaPlasticityParams.BufferParams
    PumpKm = model.CaPlasticityParams.PumpKm 

    difshell = []
    buffers = []
    print('Adding DifShells to '+comp.path)
    for i,(diameter,thickness) in enumerate(diam_thick):
        
        name = protodif.name+'_'+str(i)
        dShell = addCaDifShell(comp,protodif,sgh.shellMode,diameter,thickness,name)
        
        difshell.append(dShell)

        b = []
        for j,buf in enumerate(Buffers):
            b.append(addDifBuffer(comp,dShell,protobuf,BufferParams[buf],Buffers[buf]))
        buffers.append(b)

        if i:
            #connect shells
            moose.connect(difshell[i-1],"outerDifSourceOut",difshell[i],"fluxFromOut")
            moose.connect(difshell[i],"innerDifSourceOut",difshell[i-1],"fluxFromIn")
            #connect buffers
            for j,b in enumerate(buffers[i]):
                moose.connect(buffers[i-1][j],"outerDifSourceOut",buffers[i][j],"fluxFromOut")
                moose.connect(buffers[i][j],"innerDifSourceOut",buffers[i-1][j],"fluxFromIn")
        else:
            #Add pumps
            for pump in Pumps:
               Km = PumpKm[pump]
                
               p = addMMPump(dShell,PumpKm[pump],Pumps[pump])
               #connect channels

            connectVDCC_KCa(model,comp,dShell,'influx','concentrationOut')
            connectNMDA(comp,dShell,'influx')
       

    return difshell
    
def addCaPool(model,OutershellThickness,BufCapacity,comp,caproto,spine):
    #create the calcium pools in each compartment
    capool = moose.copy(caproto, comp, caproto.name)[0]
    
    capool.thick = OutershellThickness
    capool.diameter = comp.diameter
    capool.length = comp.length
    radius = comp.diameter/2.

    if spine:
        vol = np.pi*radius**2*capool.thick
    else:
        if capool.length:
            vol = np.pi*capool.length*(radius**2-(radius-capool.thick)**2)
        else:
            vol = 4./3.*np.pi*(radius**3-(radius-capool.thick)**3)


    capool.B = 1. / (constants.Faraday*vol*2) / BufCapacity #volume correction

    connectVDCC_KCa(model,comp,capool,'current','concOut')
    
    connectNMDA(comp,capool,'current')
    print('Adding CaConc to '+capool.path)
    return capool

def extract_and_add_capool(model,comp,pools,spine):
    params = model.CaPlasticityParams
    shape = util.distance_mapping(params.ShapeConfig,comp)
    OuterShellThick = shape.OutershellThickness
    BufCapacity = util.distance_mapping(params.BufferCapacityDensity,comp)

    pool = addCaPool(model,OuterShellThick,BufCapacity,comp, pools,spine)

    return pool

def extract_and_add_difshell(model, shellMode, comp, pools):
    params = model.CaPlasticityParams

    
    Pumps = util.distance_mapping(params.PumpDensity,comp)
    Buffers = util.distance_mapping(params.BufferDensity,comp)
    shape = util.distance_mapping(params.ShapeConfig,comp)
    
    
    shellsparams = CalciumConfig(shellMode=shellMode,increase_mode=shape.ThicknessIncreaseMode,outershell_thickness=shape.OutershellThickness,thickness_increase=shape.ThicknessIncreaseFactor, min_thickness=shape.OutershellThickness*1.1)

    dshells_dend = addDifMachineryToComp(model,comp,pools,Buffers,Pumps,shellsparams)
    
    return dshells_dend        

def add_calcium_to_compartment(model, shellMode, comp, pools,capool,spine=False):
    if shellMode == -1:
        capool.append(extract_and_add_capool(model,comp,pools[0],spine))
        dshells_dend = None
        return dshells_dend
    if shellMode == 0 or shellMode == 1 or shellMode == 3:
        dshells_dend = extract_and_add_difshell(model, shellMode, comp, pools[1:])
        capool.extend(dshells_dend)
        return dshells_dend
    
    print('Unknown shellMode. Leaving')
    return -1

def addCalcium(model,ntype):
    
    pools = CaProto(model)
    capool = []
    params = model.CaPlasticityParams
    for comp in moose.wildcardFind(ntype + '/#[TYPE=Compartment]'):
        if NAME_NECK not in comp.name and NAME_HEAD not in comp.name: #Look for spines connected to the dendrite
            shellMode = util.distance_mapping(params.CaShellModeDensity,comp)
            dshells_dend = add_calcium_to_compartment(model, shellMode, comp, pools,capool)
            if dshells_dend == -1:
                return

            if model.spineYN:
                spines = []
                neighbors = list(comp.neighbors['raxial'])
                neighbors.extend(list(comp.neighbors['axial']))
                for neighbor in neighbors:
                    if NAME_NECK in neighbor.name:
                        spines.append(neighbor)
                else:
                    'Could not find spines!!!'
                for sp in spines:
             
                    shellMode = util.distance_mapping(params.CaShellModeDensity,moose.element(sp))
                    dshells_neck = add_calcium_to_compartment(model,shellMode,moose.element(sp),pools,capool,spine=True)
                    if dshells_neck == -1:
                        return
                    if dshells_dend and dshells_neck: #diffusion between neck and dendrite
                        moose.connect(dshells_neck[-1],"outerDifSourceOut",dshells_dend[0],"fluxFromOut")
                        moose.connect(dshells_dend[0],"innerDifSourceOut",dshells_neck[-1],"fluxFromIn")
                    heads = []
                    neighbors = list(moose.element(sp).neighbors['raxial'])
                    neighbors.extend(list(moose.element(sp).neighbors['axial']))
                    for neighbor in neighbors:
                        if NAME_HEAD in neighbor.name:
                            heads.append(neighbor)
                    if not heads:
                        'Could not find heads!!!'
                    for head in heads:
                        shellMode =  util.distance_mapping(params.CaShellModeDensity,head)
                        dshells_head = add_calcium_to_compartment(model,shellMode,moose.element(head),pools,capool,spine=True)
                        if dshells_head == -1:
                            return
                        if dshells_head and dshells_neck: #diffusion between neck and dendrite
                            moose.connect(dshells_head[-1],"outerDifSourceOut",dshells_neck[0],"fluxFromOut")
                            moose.connect(dshells_neck[0],"innerDifSourceOut",dshells_head[-1],"fluxFromIn")

    return capool
