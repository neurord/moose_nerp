#if calcium=0, then calcium pools not implemented
#if calcium=2, then diffusion,buffers and pumps implemented (eventually)
caltype = 1

BufferParams = NamedList('BufferParams','''
Name
bTotal
kf
kb
D''')
PumpParams = NamedList('BufferParams','''
Name
Km
Kcat
''')
#These params are for single time constant of decay calcium

BufCapacity = 2
CaThick = 0.1e-6
CaBasal = 0.05e-3
CaTau = 20e-3

plasYesNo = 1
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
fura2 = BufferParams('Fura-2', bTotal=100e-3, kf=1000e3, kb=185, D=6e-11) #Kerrs
Fluo5f_Wickens = BufferParams('Fluo5f_Wickens', bTotal=300.0e-3, kf=2.36e5, kb=82.6, D=6e-11)
Fluo5f_Lovinger = BufferParams('Fluo5f_Lovinger', bTotal=300.0e-3, kf=2.36e5, kb=82.6, D=6e-11)
Fluo4 = BufferParams('Fluo4', bTotal=100.0e-3, kf=2.36e5, kb=82.6, D=6e-11)
Fluo4FF = BufferParams('Fluo4FF', bTotal=500.0e-3, kf=.8e5, kb=776, D=6e-11)

MMpump_soma = PumpParams('MMpump_soma',Km=0.3e-3,Kcat=85e-8)
MMpump_dend = PumpParams('MMpump_dend',Km=0.3e-3,Kcat=8e-8)
NCX = PumpParams("NCX",Km=1e-3,Kcat=0)


