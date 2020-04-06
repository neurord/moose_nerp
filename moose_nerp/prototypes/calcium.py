from __future__ import print_function, division
import os
import numpy as np
import moose

from moose_nerp.prototypes import constants, logutil
from moose_nerp.prototypes.util import distance_mapping, NamedList
from moose_nerp.prototypes.spines import NAME_NECK, NAME_HEAD

CalciumConfig = NamedList('CalciumConfig','''
shellMode
increase_mode
outershell_thickness
thickness_increase
min_thickness''')

SingleBufferParams = NamedList('SingleBufferParams','''
Name
kf
kb
D''')

SinglePumpParams = NamedList('SinglePumpParams','''
Name
Kd
''')



CellCalcium = NamedList('CellCalcium','''
CaName
Ceq
DCa
tau
''')

ShapeParams = NamedList('ShapeParams','''
OutershellThickness
ThicknessIncreaseFactor
ThicknessIncreaseMode
MinThickness
''')


log = logutil.Logger()

def shell_surface(dShell,head=False,prevd=0):

    if dShell.shapeMode:
        if not dShell.length:
            cos_alpha = (dShell.diameter/2-prevd)/(dShell.diameter/2)
            cos_alpha_beta = (dShell.diameter/2-prevd-dShell.thickness)/(dShell.diameter/2)
            surfaceArea = np.pi*(dShell.diameter)*(cos_alpha-cos_alpha_beta)
        else:
            surfaceArea = np.pi*dShell.diameter*dShell.thickness
    else:
        surfaceArea = dShell.outerArea
    if head and dShell.shapeMode:
        if dShell.length:
            surfaceArea += dShell.outerArea


    return surfaceArea

def shell_volume(dShell):
    if dShell.shapeMode: #SLAB
        return np.pi*(dShell.diameter/2)**2*dShell.thickness
    else:
        if dShell.length: #ONION Cylinder
            return np.pi*dShell.length*((dShell.diameter/2)**2-(dShell.diameter/2-dShell.thickness)**2)
        else:
            return 4./3.*np.pi*((dShell.diameter/2)**3-(dShell.diameter/2-dShell.thickness)**3)

def get_path(s):
    l = len(s.split('/')[-1])
    return s[:-l]

def difshell_geometry(comp, shell_params):
    res = []

    if shell_params.shellMode == 0:
        multiplier = 2.
        new_rad = comp.diameter/2.
    else:
        multiplier = 1.
        if comp.length:
            new_rad = comp.length
        else:
            new_rad = comp.diameter

    i = 1

    new_thick = shell_params.outershell_thickness

    if shell_params.increase_mode:
        while new_rad > shell_params.min_thickness + new_thick:

            res.append([new_rad*multiplier,new_thick])
            new_rad = new_rad - new_thick
            new_thick = shell_params.outershell_thickness*shell_params.thickness_increase**i
            i = i+1

        res.append([new_rad*multiplier,new_rad])
        return res

    while new_rad >shell_params.min_thickness+ new_thick:

        res.append([new_rad*multiplier,new_thick])
        new_rad = new_rad - new_thick
        new_thick = shell_params.outershell_thickness + i*shell_params.thickness_increase*shell_params.outershell_thickness
        i = i+1

    res.append([new_rad*multiplier,new_rad])

    return res

def strip_brackets(comp):
    shellName = ''
    for s in comp.path.split('[0]'):
        shellName += s
    return shellName


def addCaDifShell(comp,shellMode,shellDiameter,shellThickness,name,capar):
    name = strip_brackets(comp)+'/'+capar.CaName+'_'+name

    dif = moose.DifShell(name)
    dif.Ceq =  capar.Ceq
    dif.D = capar.DCa
    dif.valence = 2
    dif.leak = 0
    dif.shapeMode = shellMode
    dif.thickness = shellThickness
    if shellMode:
        dif.diameter = comp.diameter
        dif.length = shellThickness
    else:
        dif.length = comp.length
        dif.diameter = shellDiameter

    return dif

def addDifBuffer(comp,dShell,bufparams,bTotal):

    name = strip_brackets(dShell)+ '_' + bufparams.Name

    dbuf = moose.DifBuffer(name)
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

def addMMPump(dShell,pumpparams,Vmax,surface):

    shellName = ''
    for s in dShell.path.split('[0]'):
        shellName += s
    pump = moose.MMPump(shellName+'_'+pumpparams.Name)

    pump.Vmax = Vmax*surface
    pump.Kd = pumpparams.Kd

    moose.connect(pump,"PumpOut",dShell,"mmPump")
    return pump


def CaProto(model):
    if not model.calYN:
        return

    capar = model.CaPlasticityParams.CalciumParams


    if not moose.exists('/library'):
        lib = moose.Neutral('/library')

    if not moose.exists('/library/'+capar.CaName):

        concproto = moose.CaConc('/library/'+capar.CaName)
        concproto.tau = capar.tau
        concproto.CaBasal = capar.Ceq
        concproto.ceiling = 1.
        concproto.floor = 0.0
        concproto.tick=-1

    return moose.element('/library/'+capar.CaName)



def connectVDCC_KCa(model,comp,capool,CurrentMessage,CaOutMessage,check_list=[]):

    if model.ghkYN:
        ghk = moose.element(comp.path + '/ghk')
        moose.connect(capool,CaOutMessage,ghk,'set_Cin')
        moose.connect(ghk,'IkOut',capool,CurrentMessage)
        log.debug('CONNECT GHK {.path} to Ca {.path}', ghk, capool)
        #connect them to the channels

    chan_list = [c for c in comp.neighbors['VmOut'] if c.className == 'HHChannel' or c.className == 'HHChannel2D']

    if not check_list:
        check_list=chan_list

    for chan in chan_list:
        if model.Channels[chan.name].calciumPermeable:
            if not model.ghkYN:
                # do nothing if ghkYesNo==1, since already connected the single GHK object
                if chan in check_list or chan.name in check_list:
                    m = moose.connect(chan, 'IkOut', capool, CurrentMessage)
                    log.debug('channel {.path} to Ca {.path}',chan, capool)

        if model.Channels[chan.name].calciumDependent:
            if chan in check_list or chan.name in check_list:
                m = moose.connect(capool,CaOutMessage, chan, 'concen')
                log.debug('channel message {} {} {}', chan.path, comp.path, m)

def connectNMDA(comp,capool,CurrentMessage,CaOutMessage):
    #nmdachans!!!
    for chan in moose.element(comp).neighbors['VmOut']:
        if chan.className == 'NMDAChan':
            moose.connect(chan, 'ICaOut', capool, CurrentMessage)
            moose.connect(capool,CaOutMessage,chan,'assignIntCa')


def addDifMachineryToComp(model,comp,Buffers,Pumps,sgh,spine):

    diam_thick = difshell_geometry(comp, sgh)

    BufferParams = model.CaPlasticityParams.BufferParams

    PumpParams = model.CaPlasticityParams.PumpParams

    difshell = []
    buffers = []
    prevd = 0 #important only for spherical compartments with SLABS, we might have them one day, right!?

    #print('Adding DifShells to '+comp.path)

    for i,(diameter,thickness) in enumerate(diam_thick): #adding shells


        dShell = addCaDifShell(comp,sgh.shellMode,diameter,thickness,str(i),model.CaPlasticityParams.CalciumParams)

        difshell.append(dShell)

        b = []
        for j,buf in enumerate(Buffers): #add buffers to shell
            b.append(addDifBuffer(comp,dShell,BufferParams[buf],Buffers[buf]))
        buffers.append(b)
        if i: #diffusion between neighboring shells
            #connect shells
            moose.connect(difshell[i-1],"outerDifSourceOut",difshell[i],"fluxFromOut")
            moose.connect(difshell[i],"innerDifSourceOut",difshell[i-1],"fluxFromIn")
            #connect buffers
            for j,b in enumerate(buffers[i]): #diffusion between buffers
                moose.connect(buffers[i-1][j],"outerDifSourceOut",buffers[i][j],"fluxFromOut")
                moose.connect(buffers[i][j],"innerDifSourceOut",buffers[i-1][j],"fluxFromIn")


        #pumps
        #There is a surface correction for the pumps for the PSD
        if not i:
            connectNMDA(comp,dShell,'influx','concentrationOut')

        if comp.name.endswith(NAME_HEAD) and i == 0:
            head = True
        else:
            head = False

        surface = shell_surface(dShell,head=head,prevd=prevd)

        if spine and comp.name.endswith(NAME_HEAD):
            try:
                check_list = model.SpineParams.spineChanList[i]
                connectVDCC_KCa(model,comp,dShell,'influx','concentrationOut',check_list)
            except IndexError:
                pass
        else:
            if not i:
                connectVDCC_KCa(model,comp,dShell,'influx','concentrationOut')


        if dShell.shapeMode == 1:
            addPumps(dShell,PumpParams,Pumps,surface)
        else:
            if i == 0:
                addPumps(dShell,PumpParams,Pumps,surface)

        prevd += dShell.thickness


    return difshell

def addPumps(dShell,PumpParams,Pumps,surface):
    leak = 0

    for pump in Pumps:
        Km = PumpParams[pump]
        p = addMMPump(dShell,PumpParams[pump],Pumps[pump],surface)

        leak += p.Vmax*dShell.Ceq/shell_volume(dShell)/(dShell.Ceq+p.Kd)

    dShell.leak = leak

def addCaPool(model,OutershellThickness,BufCapacity,comp,caproto,tau=None,tauScale=None):
    #create the calcium pools in each compartment
    capool = moose.copy(caproto, comp, caproto.name)[0]
    capool.thick = OutershellThickness
    capool.diameter = comp.diameter
    capool.length = comp.length
    radius = comp.diameter/2.
    if capool.thick > radius:
        capool.thick = radius
    if capool.length:
        vol = np.pi * comp.length * (radius**2 - (radius-capool.thick)**2)
    else:
        vol = 4./3.*np.pi*(radius**3-(radius-capool.thick)**3)
    if tau is not None:
        capool.tau = tau#*np.pi*comp.diameter*comp.length *0.125e10 #/(np.pi*comp.length*(comp.diameter/2)**2) #
        if tauScale is not None:
            if tauScale == 'SurfaceArea':
                capool.tau = tau * (np.pi * comp.diameter * comp.length) / 8.478e-11 # normalize to primdend surface area
            elif tauScale == 'Volume':
                capool.tau = tau / vol
            elif tauScale == 'SVR': #surface to volume ratio
                capool.tau = tau / (np.pi * comp.diameter * comp.length)/vol


    capool.B = 1. / (constants.Faraday*vol*2) / BufCapacity #volume correction

    connectVDCC_KCa(model,comp,capool,'current','concOut')
    connectNMDA(comp,capool,'current','concOut')
    #print('Adding CaConc to '+capool.path)
    return capool

def extract_and_add_capool(model,comp,pools):
    params = model.CaPlasticityParams
    shape = distance_mapping(params.ShapeConfig,comp)
    OuterShellThick = shape.OutershellThickness
    BufCapacity = distance_mapping(params.BufferCapacityDensity,comp)
    if hasattr(params,'Taus'):
        tau = distance_mapping(params.Taus,comp)
        tauScale = params.tauScale
    else:
        tau = params.CalciumParams.tau
        tauScale = None
    pool = addCaPool(model,OuterShellThick,BufCapacity,comp, pools,tau=tau,tauScale=tauScale)

    return pool

def extract_and_add_difshell(model, shellMode, comp,spine):
    params = model.CaPlasticityParams

    Pumps = {}
    for pump in params.PumpVmaxDensities.keys():
        Pumps[pump] = distance_mapping(params.PumpVmaxDensities[pump], comp)

    Buffers = distance_mapping(params.BufferDensity,comp)
    shape = distance_mapping(params.ShapeConfig,comp)
    shellsparams = CalciumConfig(shellMode=shellMode,increase_mode=shape.ThicknessIncreaseMode,outershell_thickness=shape.OutershellThickness,thickness_increase=shape.ThicknessIncreaseFactor, min_thickness=shape.MinThickness)

    dshells_dend = addDifMachineryToComp(model,comp,Buffers,Pumps,shellsparams,spine)

    return dshells_dend

def add_calcium_to_compartment(model, shellMode, comp, pools,capool,spine):
    if shellMode == -1:
        capool.append(extract_and_add_capool(model,comp,pools))
        dshells_dend = None
        return dshells_dend
    if shellMode == 0 or shellMode == 1 or shellMode == 3:
        dshells_dend = extract_and_add_difshell(model, shellMode, comp,spine)
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
            shellMode = distance_mapping(params.CaShellModeDensity,comp)
            dshells_dend = add_calcium_to_compartment(model, shellMode, comp, pools,capool,spine=False)
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

                    shellMode = distance_mapping(params.CaShellModeDensity,moose.element(sp))
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
                        shellMode =  distance_mapping(params.CaShellModeDensity,moose.element(head))
                        dshells_head = add_calcium_to_compartment(model,shellMode,moose.element(head),pools,capool,spine=True)
                        if dshells_head == -1:
                            return
                        if dshells_head and dshells_neck: #diffusion between neck and dendrite
                            moose.connect(dshells_head[-1],"outerDifSourceOut",dshells_neck[0],"fluxFromOut")
                            moose.connect(dshells_neck[0],"innerDifSourceOut",dshells_head[-1],"fluxFromIn")

    return capool

def fix_calcium(neurontypes, model,buf_cap=None):
    """kluge to fix buffer capacity in CaPool

    Initiating hsolve calculates CaConc.B from thickness, length,
    diameter; ignores buffer capacity.
    """

    comptype = 'ZombieCompartment'
    cacomptype = 'ZombieCaConc'
         
    for ntype in neurontypes:
        ### if neurons come from different packages, they may have different buffer_capacity_densities
        ### if so, use the dictionary of those values in this function
        if buf_cap:
            buffer_density=buf_cap[ntype]
            log.info('Fixing calcium buffer capacity for {} elements, using {}'.format(comptype,list(buffer_density.values())))
        else:
            buffer_density=model.CaPlasticityParams.BufferCapacityDensity
            log.info('Fixing calcium buffer capacity for {} elements'.format(comptype))
            
        for comp in moose.wildcardFind('{}/#[TYPE={}]'.format(ntype, comptype)):
            cacomps = [m for m in moose.element(comp).children if m.className==cacomptype]
            for cacomp in cacomps:

                buf_capacity = distance_mapping(buffer_density, comp)
                radius = cacomp.diameter/2.
                if cacomp.thick > radius:
                    cacomp.thick = radius
                if cacomp.length:
                    vol = np.pi * cacomp.length * (radius**2 - (radius-cacomp.thick)**2)

                else:
                    vol = 4. / 3. * np.pi * ((cacomp.diameter / 2) ** 3 - (cacomp.diameter / 2 - cacomp.thick) ** 3)
                cacomp.B = 1. / (constants.Faraday * vol * 2) / buf_capacity # volume correction
              # print(cacomp.path, cacomp.B, cacomp.className)
