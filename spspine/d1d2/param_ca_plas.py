from spspine.calcium import cabuf_params,NAME_CALCIUM

#example of how to specify calcium buffers.
#new def in calcium.py will loop over items in cabuf dictionary and create buffers
#add lines,items for calbindin, fixed buffer, and calcium indicators
#exclude or include buffers by changing cabuf dictionary, not params
#alternative is to have separate dictionary specifying total and bound
#need method to estimate/calculate bound from total and CaBasal
CaMN_params=cabuf_params(bufname='CaMN',kf=0.1e6,kb=1e3,diffconst=66e-12,total=15e-3,bound=3e-3)
CaMC_params=cabuf_params(bufname='CaMC',kf=0.006e6,kb=9.1,diffconst=66e-12,total=15e-3,bound=3e-3)
cabuf={'CaMN':CaMN_params,'CaMC':CaMC_params}

#if calcium=0, then calcium pools not implemented
#if calcium=2, then diffusion,buffers and pumps implemented (eventually)
calcium=1

#These params are for single time constant of decay calcium
BufCapacity=2
CaThick=0.1e-6
CaBasal=0.05e-3
CaTau=20e-3

plasYesNo=1
syntype='ampa'
#These thresholds are applied to calcium concentration
##Note that these must be much larger if there are spines
highThresh=0.3e-3
lowThresh=0.15e-3
#Thresholds need to be adjusted together with these factors for plasticity
#Both the timeStep Factor - applied to both, and the Arbitrary constant
timeStepFactor=100.0
lowfactor='/'+str(lowThresh-highThresh)+'/'+str(timeStepFactor)
#Arbitrary constant
highfactor='(0.5/'+str(timeStepFactor)+')*'
