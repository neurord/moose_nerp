from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.util import NamedDict

#definitions
CAPOOL = -1 #single time constant of decay
#difshell types
SHELL = 0
SLAB = 1
CUSTOM = 3

#region/distance definitions
soma = (0,141e-6)
dend = (14.100000000000000001e-6,1000e-6)
everything = (0.,1.)
spines = (0.,1.,'sp')

#difshell increase mode
GEOMETRIC = 1
LINEAR = 0

BufferParams = NamedList('BufferParams','''
Name
kf
kb
D''')

PumpParams = NamedList('PumpParams','''
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

#intrinsic calcium params
CalciumParams = CellCalcium(CaName='Shells',Ceq=50e-6,DCa=200.e-12,tau=20e-3)

#shellMode: CaPool = -1, Shell = 0, SLICE/SLAB = 1, userdef = 3. If shellMode=-1 caconc thickness is outershell_thickness, and BuferCapacityDensity is used
#increase_mode linear = 0, geometric = 1

#Buffer params
calbindin = BufferParams('Calbindin',  kf=0.028e6, kb=19.6, D=66e-12)
camc = BufferParams('CaMC', kf=0.006e6, kb=9.1, D=66.0e-12) 
camn = BufferParams('CaMN',  kf=0.1e6, kb=1000., D=66.0e-12)
fixed_buffer = BufferParams('Fixed_Buffer',  kf=0.4e6, kb=20e3, D=0) 
Fura2 = BufferParams('Fura-2',  kf=1000e3, kb=185, D=6e-11) 
Fluo5F = BufferParams('Fluo5f_Wickens',  kf=2.36e5, kb=82.6, D=6e-11)
Fluo4 = BufferParams('Fluo4',  kf=2.36e5, kb=82.6, D=6e-11)
Fluo4FF = BufferParams('Fluo4FF', kf=.8e5, kb=776, D=6e-11) 

#Buffer params dictionary
BufferParams = NamedDict('BufferParams',Calbindin=calbindin,CaMN=camn,CaMC=camc,FixedBuffer=fixed_buffer,Fura2=Fura2,Fluo5F=Fluo5F,Fluo4=Fluo4,Flou4FF=Fluo4FF)

#Pump params
MMPump = PumpParams('MMpump',Kd=0.3e-3)
NCX = PumpParams("NCX",Kd=1e-3)

#Pump params dictionary
PumpKm = {'MMPump':MMPump,'NCX':NCX}

#dye used in simulations
which_dye = "no_dye"
CaBasal = 50e-6

#possible dye sets used in experiments
BufferTotals ={"no_dye":{'Calbindin':80e-3,'CaMC':15e-3,'CaMN':15e-3,'FixedBuffer':1},
               "Fura_2":{'Fura2':100e-3,'FixedBuffer':1},
               "Fluo5F Shindou":{'Fluo5F':300.0e-3,'FixedBuffer':1},
               "Fluo4":{'Fluo4':100.e-3,'FixedBuffer':1},
               "Fluo4FF":{'Fluo4FF':500e-3,'FixedBuffer':1},
               "Fluo5F Lovinger and Sabatini":{'Fluo5F':100e-3,'FixedBuffer':1},
    }
#Pump Vmax
PumpVmaxDend = {'NCX':0.,'MMPump':8e-8}
PumpVmaxSoma = {'MMPump':85e-8}

#Buffer density specification -- this is used with difshells
BufferDensity = {everything:BufferTotals[which_dye]}
#Pump density specification -- used with diffshells
PumpDensity = {soma:PumpVmaxSoma,dend:PumpVmaxDend,spines:PumpVmaxDend}
#Buffer capacity specification -- this is used with CaConc (single time constant of Ca decay)
BufferCapacityDensity = {soma:20.,dend:20.}

#Ca dynamics specification
CaShellModeDensity = {soma:SHELL, dend:SHELL, spines:SLAB}

tree_shape = ShapeParams(OutershellThickness=.1e-6,ThicknessIncreaseFactor=2,ThicknessIncreaseMode=GEOMETRIC,MinThickness=.11e-6)
spines_shape = ShapeParams(OutershellThickness=.07e-6,ThicknessIncreaseFactor=2.,ThicknessIncreaseMode=LINEAR,MinThickness=.03e-6)

ShapeConfig = {everything:tree_shape,spines:spines_shape}


#These thresholds are applied to calcium concentration
##Note that these must be much larger if there are spines
PlasParams = NamedList('PlasParams','''
Name
highThreshold
lowThreshold
highDurationThreshold
lowDurationThreshold
highFactor
lowFactor
''')
timeStepFactor = 100.0
lowThreshold = 0.15e-3
highThreshold = 0.3e-3
Plas_syn = PlasParams(Name='ampa',highThreshold=highThreshold,lowThreshold=lowThreshold, highDurationThreshold = 0.005,lowDurationThreshold=0.025,highFactor='(0.5/'+str(timeStepFactor)+')*',lowFactor =  '/'+str(lowThreshold-highThreshold)+'/'+str(timeStepFactor))
