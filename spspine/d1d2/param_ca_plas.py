#if calcium=0, then calcium pools not implemented
#if calcium=2, then diffusion,buffers and pumps implemented (eventually)
#This is an attempt to transfer Ca_constants.g


BufferParams = NamedList('BufferParams','''
Name
bTotal
kf
kb
D''')

PumpParams = NamedList('PumpParams','''
Name
Km
Kcat
''')

CalciumParams = NamedList('CalciumParams','''
CaName
CaBasal
DCa
CaTau
BufCapacity
''')

CalciumConfig = NamedList('CalciumConfig','''
shellMode
increase_mode
outershell_thickness
thickness_increase
min_thickness
''')



#shellMode: CaPool = -1, Shell = 0, SLICE/SLAB = 1, userdef = 3
#increase_mode linear = 0, geometric = 1
#These params are for single time constant of decay calcium

caltype = 1
CDIYesNo = 1
which_dye = 0 #just regular buffers
plasYesNo = 1
CaOutMessages = ['','concOut','concentrationOut']
CurrentMessages = ['', 'current','influx']

CurrentMessage = CurrentMessages[caltype]
CaOutMessage = CaOutMessages[caltype]
CaBasal = 50e-6
CaPoolParams = CalciumParams('CaPool',CaBasal=CaBasal,DCa=0,CaTau=20e-3,BufCapacity = 2)
ShellParams =  CalciumParams('DifShell',CaBasal=CaBasal,DCa=200.0e-12,CaTau=0,BufCapacity=0)

CalciumParamsList = [None,CaPoolParams,ShellParams]
CaParams = CalciumParamsList[caltype]

soma = (0,14e-6)
dend = (14.1e-6,1000e-6)

#These thresholds are applied to calcium concentration
##Note that these must be much larger if there are spines
highThresh = 0.3e-3
lowThresh = 0.15e-3
#Thresholds need to be adjusted together with these factors for plasticity
#Both the timeStep Factor - applied to both, and the Arbitrary constant
timeStepFactor = 100.0
lowfactor='/'+str(lowThresh-highThresh)+'/'+str(timeStepFactor)
#Arbitrary constant
highfactor='(0.5/'+str(timeStepFactor)+')*'

calbindin = BufferParams('Calbindin', bTotal=80e-3, kf=0.028e6, kb=19.6, D=66e-12)
camc = BufferParams('CaMC', bTotal=15e-3, kf=0.006e6, kb=9.1, D=66.0e-12)
camn = BufferParams('CaMN', bTotal=15e-3, kf=0.1e6, kb=1000., D=66.0e-12)
fixed_buffer = BufferParams('Fixed_Buffer', bTotal=1, kf=0.4e6, kb=20e3, D=0)
Fura2 = BufferParams('Fura-2', bTotal=100e-3, kf=1000e3, kb=185, D=6e-11) #Kerrs
Fluo5f_Wickens = BufferParams('Fluo5f_Wickens', bTotal=300.0e-3, kf=2.36e5, kb=82.6, D=6e-11)
Fluo5f_Lovinger = BufferParams('Fluo5f_Lovinger', bTotal=100.0e-3, kf=2.36e5, kb=82.6, D=6e-11)
Fluo4 = BufferParams('Fluo4', bTotal=100.0e-3, kf=2.36e5, kb=82.6, D=6e-11)
Fluo4FF = BufferParams('Fluo4FF', bTotal=500.0e-3, kf=.8e5, kb=776, D=6e-11)

MMpump_soma = PumpParams('MMpump_soma',Km=0.3e-3,Kcat=85e-8)
MMpump_dend = PumpParams('MMpump_dend',Km=0.3e-3,Kcat=8e-8)

NCX = PumpParams("NCX",Km=1e-3,Kcat=0)

Pumps = NamedDict('Pumps',MMPump = {soma:MMpump_soma,dend:MMpump_dend}, NCXPump = {soma:None,dend:NCX})

cadyes = { #aka buffer combinations
    0: [calbindin,camn,camc,fixed_buffer],
    1: [Fura2,fixed_buffer],
    2: [Fluo5f_Wickens,fixed_buffer],
    3: [Fluo4,fixed_buffer],
    4: [Fluo4FF,fixed_buffer],
    5: [Fluo5f_Lovinger,fixed_buffer]
 }
    
ModelBuffers =  BufferCombinations[cadye]                    
DifShellGeometryDend = CalciumConfig(shellMode=0,outershell_thickness=.1e-6,thickness_increase = 2.,min_thickness = .11e-6,increase_mode=1)
DifShellGeometrySpine = CalciumConfig(shellMode=1,outershell_thickness=0.07e-6,thickness_increase = 2.,min_thickness = .11e-6,increase_mode=0)

CaMorphologyShell = NamedDict('CaMorphConf',dendrite = {soma:DifShellGeometryDend,dendrite:DifShellGeometryDend},spine=DifShellGeometrySpine)
