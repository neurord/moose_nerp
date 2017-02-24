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

PumpParams = NamedList('PumpParams','''
Name
Kd
''')

#shellMode: CaPool = -1, Shell = 0, SLICE/SLAB = 1, userdef = 3. If shellMode=-1 caconc thickness is outershell_thickness, and BuferCapacityDensity is used
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

calbindin = BufferParams('Calbindin',  kf=0.028e6, kb=19.6, D=66e-12)
camc = BufferParams('CaMC', kf=0.006e6, kb=9.1, D=66.0e-12) 
camn = BufferParams('CaMN',  kf=0.1e6, kb=1000., D=66.0e-12)
fixed_buffer = BufferParams('Fixed_Buffer',  kf=0.4e6, kb=20e3, D=0) 
Fura2 = BufferParams('Fura-2',  kf=1000e3, kb=185, D=6e-11) 
Fluo5F = BufferParams('Fluo5f_Wickens',  kf=2.36e5, kb=82.6, D=6e-11)
Fluo4 = BufferParams('Fluo4',  kf=2.36e5, kb=82.6, D=6e-11)
Fluo4FF = BufferParams('Fluo4FF', kf=.8e5, kb=776, D=6e-11) 

which_dye = 0
soma = (0,14e-6)
dend = (14.000000000000000001e-6,1000e-6)
everything = (0.,1.)
MMPump = PumpParams('MMpump',Kd=0.3e-3)
NCX = PumpParams("NCX",Kd=1e-3)

PumpKm = NamedDict('PumpKM',MMPump=MMPump,NCX=NCX)

BufferParams = NamedDict('BufferParams',Calbindin=calbindin,CaMN=camn,CaMC=camc,FixedBuffer=fixed_buffer,Fura2=Fura2,Fluo5F=Fluo5F,Fluo4=Fluo4,Flou4FF=Fluo4FF)

BufferTotals ={0:{'Calbindin':80e-3,'CaMC':15e-3,'CaMN':15e-3,'FixedBuffer':1},
               1:{'Fura2':100e-3,'FixedBuffer':1},
               2:{'Fluo5F':300.0e-3,'FixedBuffer':1},
               3:{'Fluo4':100.e-3,'FixedBuffer':1},
               4:{'Fluo4FF':500e-3,'FixedBuffer':1},
               5:{'Fluo5F':100e-3,'FixedBuffer':1},
    }

PumpVmaxDend = NamedDict('PumpVmax', NCX = 0,MMPump=8e-8)
PumpVmaxSoma = NamedDict('PumpVmax', MMPump=85e-8)
spines = (0.,1.,'sp')

BufferDensity = {everything:BufferTotals[0]}
BufferCapacityDensity = {soma:2.,dend:2.}
PumpDensity = {soma:PumpVmaxSoma,dend:PumpVmaxDend,spines:PumpVmaxDend}
CaShellModeDensity = {soma:0, dend:0, spines:1}
OutershellThicknessDensity = {soma : .1e-6,dend:.1e-6,spines:.07e-6}
ThicknessIncreaseDensity = {soma : 2,dend : 2,spines: 0.}
ThicknessModeDensity= {soma:1,dend:1,spines:0.}
CalciumParams = CellCalcium(CaName='Shells',CaPoolName='Calc',Ceq=50e-6,DCa=200.,tau=20e-3)
