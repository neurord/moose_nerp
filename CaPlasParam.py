#CaPlasParam.py
#if calcium=0, then calcium pools not implemented
calcium=1

Faraday = 96485.3415 
#These params are for single time constant of decay calcium
BufCapacity=2
CaThick=0.1e-6
CaBasal=0.05e-3
CaTau=20e-3
caName='CaPool'

#fraction of nmda current carried by calcium
#Note that since Ca reversal produces ~2x driving potential,
#need to make this half of typical value
nmdaCaFrac=0.05

plasyesno=1
#These thresholds are applied to calcium concentration
##Note that these must be much larger if there are spines
highThresh=0.3e-3
lowThresh=0.15e-3
#Thresholds need to be adjusted together with these factors for plasticity
#Both the timeStep Factor - applied to both, and the Arbitrary constant
timeStepFactor=100.0
lowfactor='/'+str(lowThresh-highThresh)+'/'+str(timeStepFactor)
#Arbitraty constant 
highfactor='(0.5/'+str(timeStepFactor)+')*'
