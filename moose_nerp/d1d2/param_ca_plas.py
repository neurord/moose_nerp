from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes.calcium import CalciumConfig, SingleBufferParams, SinglePumpParams, CellCalcium, ShapeParams

#to change the type of calcium model, change CaShellModeDensity
#if using CAPOOL, may want to adjust CalciumParams.tau (decay time constant) or BufferCapacityDensity
#if using SHELL or POOL, optionally change:
#which_dye to specify one of a set of buffer parameters
#BufferTotals to change buffer quantitites (or add additional lines)
#PumpDensity or PumpVmax to change those parameters
#parameters in tree_shape, etc to change size of subcompartments

#definitions, 1. shellMode
#CAPOOL implements caconc object with single time constant of Ca decay
#   thickness is outershell_thickness, and BuferCapacityDensity is used
CAPOOL = -1
#difshell types
#SHELL subdivides dendrite in cylinderical sheels, with diffusion between outer/submembrane shell and central core
SHELL = 0
#SLAB subdivides spines (or dendrite) into slices, with diffusion in the axial dimension
SLAB = 1
CUSTOM = 3

#region/distance definitions
soma = (0,14.1e-6)
dend = (14.100000000000000001e-6,1000e-6)
everything = (0.,1.)
spines = (0.,1.,'sp')
heads = (0.,1.,'head')
necks = (0.,1.,'neck')

#difshell increase mode
#  allows submembrane shells or slaps to be smaller than deeper shells/slabs
GEOMETRIC = 1
LINEAR = 0

#SPECIFY TYPE OF CALCIUM DYNAMICS HERE
CaShellModeDensity = {soma:SHELL, dend:SHELL, spines:SLAB}
#CaShellModeDensity = {soma:CAPOOL, dend:CAPOOL, spines:CAPOOL}

############################################
#intrinsic calcium params
#diffusion constant from Allbritton et al.1992.
#    Tau is used only if using single time constant of decay instead of pumps and buffers
CaBasal = 50e-6
CalciumParams = CellCalcium(CaName='Shell',Ceq=CaBasal,DCa=200e-12,tau=20e-3)

#################################
BufferParams = NamedDict('BufferParams') # Buffer params dictionary
#kinetic parameters of various calcium Buffers / indicators
#Calbindin binding rates from Schmidt et al. 2007 J Physiol
BufferParams.Calbindin = SingleBufferParams('Calbindin',  kf=0.028e6, kb=19.6, D=66e-12)
#Calmodulin binding rates from Brown SE, Martin SR, Bayley PM (1997) J Biol Chem and Putkey JA, Kleerekoper Q, Gaertner TR, Waxham MN (2003) J Biol Chem
BufferParams.CaMC = SingleBufferParams('CaMC', kf=0.006e6, kb=9.1, D=66.0e-12)
BufferParams.CaMN = SingleBufferParams('CaMN',  kf=0.1e6, kb=1000., D=66.0e-12)
BufferParams.FixedBuffer = SingleBufferParams('Fixed_Buffer',  kf=0.4e6, kb=20e3, D=0)
BufferParams.Fura2 = SingleBufferParams('Fura-2',  kf=1000e3, kb=185, D=6e-11)
BufferParams.Fluo5F = SingleBufferParams('Fluo5f_Wickens',  kf=2.36e5, kb=82.6, D=6e-11)
BufferParams.Fluo4 = SingleBufferParams('Fluo4',  kf=2.36e5, kb=82.6, D=6e-11)
BufferParams.Fluo4FF = SingleBufferParams('Fluo4FF', kf=.8e5, kb=776, D=6e-11)

####################################################
#Kinetic parameters for calcium extrusion (pump) mechanisms
PumpParams = NamedDict('PumpParams') # Buffer params dictionary
#PMCA (mmpump) Km from sedova, Blatter 1999 cell calcium, Km=150-320
PumpParams.MMPump = SinglePumpParams('MMpump',Kd=0.3e-3)
#NCX affinity from Gall et al. 1999 Biophys J, Km=1.5 uM
PumpParams.NCX = SinglePumpParams("NCX",Kd=1e-3)

##################### VARY THESE PARAMETERS TO CONTROL CALCIUM DYNAMICS #############
#dye used in simulations
which_dye = "no_dye"

#Quantity of calcium buffers.  "no_dye" is specifies the exogenous buffer quantity.
#Other possible dye sets are for replicating calcium imaging experiments, and assume the diffusible buffers are dialyzed
#Quantities of calcium indicators taken directly from experimental papers

#possible dye sets used in experiments
BufferTotals ={"no_dye":{'Calbindin':80e-3,'CaMC':15e-3,'CaMN':15e-3,'FixedBuffer':1}, #endogenous immobile low affinity buffer (e.g. see Matthews, Scoch, & Dietrich, J. Neuro, 2013 (hippocampus))
               "Fura_2":{'Fura2':100e-3,'FixedBuffer':1}, #Kerr
               "Fluo5F Shindou":{'Fluo5F':300.0e-3,'FixedBuffer':1},
               "Fluo4":{'Fluo4':100.e-3,'FixedBuffer':1}, #Plotkin use 100uM or 200
               "Fluo4FF":{'Fluo4FF':500e-3,'FixedBuffer':1}, #500 uM used by Plotkin
               "Fluo5F Lovinger and Sabatini":{'Fluo5F':100e-3,'FixedBuffer':1},
               "no_buffers":{}
    }

#Pump Vmax, NCX distribution from Lorincz et al. 2007 PNAS
PumpVmaxDensities = NamedDict('PumpVmaxDensities')
PumpVmaxDensities.MMPump = {soma:85e-8, dend:8.e-8, spines:1.e-8}
PumpVmaxDensities.NCX = {soma:0, dend:0, spines:8.e-8}
##########################################################
#Buffer density specification -- this is used with difshells
BufferDensity = {everything:BufferTotals[which_dye]}
#Buffer capacity specification -- this is used with CaConc (single time constant of Ca decay)
BufferCapacityDensity = {soma:20.,dend:20.}

#Specificy the size of the smaller calcium compartments
#When subdividing dendrite or spine, can have the PSD or submembrane shell thinner than inner shells with a thickness increase.
tree_shape = ShapeParams(OutershellThickness=.1e-6,ThicknessIncreaseFactor=2,ThicknessIncreaseMode=GEOMETRIC,MinThickness=.11e-6)
head_shape = ShapeParams(OutershellThickness=.07e-6,ThicknessIncreaseFactor=2.,ThicknessIncreaseMode=LINEAR,MinThickness=.06e-6)
neck_shape = ShapeParams(OutershellThickness=.1667e-6,ThicknessIncreaseFactor=1.,ThicknessIncreaseMode=LINEAR,MinThickness=.13e-6)

ShapeConfig = {everything:tree_shape,heads:head_shape,necks:neck_shape}

#################### Plasticity ##########################
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
