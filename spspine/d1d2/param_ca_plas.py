#example of how to specify calcium buffers.
#new def in calcium.py will loop over items in cabuf dictionary and create buffers
#add lines,items for calbindin, fixed buffer, and calcium indicators
#exclude or include buffers by changing cabuf dictionary, not params
#alternative is to have separate dictionary specifying total and bound
#need method to estimate/calculate bound from total and CaBasal
#if calcium=0, then calcium pools not implemented
#if calcium=2, then diffusion,buffers and pumps implemented (eventually)
#This is an attempt to transfer Ca_constants.g
from spspine.util import NamedList
from spspine.util import NamedDict

BufferParams = NamedList('BufferParams','''
Name
kf
kb
D''')
#bTotal

PumpParams = NamedList('PumpParams','''
Name
Kd
''')
#Vmax

CalciumConfig = NamedList('CalciumConfig','''
Buffers
BufCapacity
Pumps
shellMode
increase_mode
outershell_thickness
thickness_increase
min_thickness
''')

#shellMode: CaPool = -1, Shell = 0, SLICE/SLAB = 1, userdef = 3
#increase_mode linear = 0, geometric = 1

CDIYesNo = 0
plasYesNo = 1
CaBasal = 50e-6
CellCalcium = NamedList('CellCalcium','''
CaPoolName
CaName
Ceq
DCa
tau
''')
syntype='ampa'

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

calbindin = BufferParams('Calbindin',  kf=0.028e6, kb=19.6, D=66e-12)#bTotal=80e-3,
camc = BufferParams('CaMC', kf=0.006e6, kb=9.1, D=66.0e-12) #bTotal=15e-3,
camn = BufferParams('CaMN',  kf=0.1e6, kb=1000., D=66.0e-12) #bTotal=15e-3,
fixed_buffer = BufferParams('Fixed_Buffer',  kf=0.4e6, kb=20e3, D=0) #bTotal=1,
Fura2 = BufferParams('Fura-2',  kf=1000e3, kb=185, D=6e-11) #bTotal=100e-3, #Kerrs
Fluo5F = BufferParams('Fluo5f_Wickens',  kf=2.36e5, kb=82.6, D=6e-11)#bTotal=300.0e-3, #Wickens, #bTotal = 100.e-3 #Lovinger
Fluo4 = BufferParams('Fluo4',  kf=2.36e5, kb=82.6, D=6e-11)#bTotal=100.0e-3,
Fluo4FF = BufferParams('Fluo4FF', kf=.8e5, kb=776, D=6e-11) #bTotal=500.0e-3,

which_dye = 0
soma = (0,14e-6)
dend = (14.000000000000000001e-6,1000e-6)

MMPump = PumpParams('MMpump',Kd=0.3e-3)
NCX = PumpParams("NCX",Kd=1e-3)

PumpKm = NamedDict('PumpKM',MMPump=MMPump,NCX=NCX)

BufferParams = NamedDict('BufferParams',Calbindin=calbindin,CaMN=camn,CaMC=camc,FixedBuffer=fixed_buffer,Fura2=Fura2,Fluo5F=Fluo5F,Fluo4=Fluo4,Flou4FF=Fluo4FF)

BufferTotals ={0:NamedDict('BufferTotals', Calbindin=80e-3,CaMC=15e-3,CaMN=15e-3,FixedBuffer=1),
               1:NamedDict('BufferTotals',Fura2=100e-3,FixedBuffer=1),
               2:NamedDict('BufferTotals',Fluo5F=300.0e-3,FixedBuffer=1),
               3:NamedDict('BufferTotals', Fluo4=100.e-3,FixedBuffer=1),
               4:NamedDict('BufferTotals',Fluo4FF=500e-3,FixedBuffer=1),
               5:NamedDict('BufferTotals',Fluo5F=100e-3,FixedBuffer=1),
    }

PumpVmaxDend = NamedDict('PumpVmax', NCX = 0,MMPump=8e-8)
PumpVmaxSoma = NamedDict('PumpVmax', MMPump=85e-8)

DifShellGeometryDend = CalciumConfig(shellMode=0,outershell_thickness=.1e-6,thickness_increase = 2.,min_thickness = .11e-6,increase_mode=1,Buffers=BufferTotals[which_dye],Pumps=PumpVmaxDend,BufCapacity=0)
DifShellGeometrySoma = CalciumConfig(shellMode=0,outershell_thickness=.1e-6,thickness_increase = 2.,min_thickness = .11e-6,increase_mode=1,Buffers=BufferTotals[which_dye],Pumps=PumpVmaxSoma,BufCapacity=0)
DifShellGeometrySpine = CalciumConfig(shellMode=1,outershell_thickness=0.02e-6,thickness_increase = 2.,min_thickness = .11e-6,increase_mode=0,Buffers=BufferTotals[which_dye],Pumps=PumpVmaxDend,BufCapacity=0)

CaPoolGeometryDend = CalciumConfig(shellMode=-1,outershell_thickness=.1e-6,thickness_increase = 2.,min_thickness = .11e-6,increase_mode=1,Buffers=BufferTotals[which_dye],Pumps=PumpVmaxDend,BufCapacity=2)
CaPoolGeometrySoma = CalciumConfig(shellMode=-1,outershell_thickness=.1e-6,thickness_increase = 2.,min_thickness = .11e-6,increase_mode=1,Buffers=BufferTotals[which_dye],Pumps=PumpVmaxSoma,BufCapacity=3)
CaPoolGeometrySpine = CalciumConfig(shellMode=-1,outershell_thickness=0.07e-6,thickness_increase = 2.,min_thickness = .11e-6,increase_mode=0,Buffers=BufferTotals[which_dye],Pumps=PumpVmaxDend,BufCapacity=1)

CalciumParams = CellCalcium(CaName='Shells',CaPoolName='Calc',Ceq=50e-6,DCa=200.,tau=20e-3)


#Calcium = NamedDict('CalciumConfig',dendrite={soma:DifShellGeometrySoma,dend:DifShellGeometryDend},spine={soma:DifShellGeometrySpine,dend:DifShellGeometrySpine})

#Calcium = NamedDict('CalciumConfig',dendrite={soma:CaPoolGeometrySoma,dend:CaPoolGeometryDend},spine={soma:DifShellGeometrySpine,dend:DifShellGeometrySpine})
#Calcium = NamedDict('CalciumConfig',dendrite={soma:DifShellGeometrySoma,dend:DifShellGeometryDend},spine={soma:CaPoolGeometryDend,dend:CaPoolGeometryDend})
Calcium = NamedDict('CalciumConfig',dendrite={soma:CaPoolGeometrySoma,dend:CaPoolGeometryDend},spine={soma:CaPoolGeometryDend,dend:CaPoolGeometryDend})

