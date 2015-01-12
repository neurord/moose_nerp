#param_ca_plas.py
#if calcium=0, then calcium pools not implemented
#if calcium=2, then diffusion,buffers and pumps implemented (eventually)
calcium=1

#These params are for single time constant of decay calcium
BufCapacity=2
CaThick=0.1e-6
CaBasal=0.05e-3
CaTau=20e-3
caName='CaPool'

plasYesNo=1
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
