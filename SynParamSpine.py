#Parameters for inhibitory synpases:
#Erev, tau1, tau2  (SI units)

DendSynChans=['gaba']
SpineSynChans=['ampa', 'nmda']

#Sriram uses 0.109e-9 for AMPA and  0.9e-9 for Gaba
SynGaba={'Erev': -60e-3, 'tau1': 0.25e-3, 'tau2': 3.75e-3, 'name': 'gaba', 'Gbar': 0.2e-9}
SynAMPA={'Erev': 5e-3, 'tau1': 1.1e-3, 'tau2': 5.75e-3, 'name': 'ampa','Gbar': 2e-9}
SynNMDA={'Erev': 5e-3, 'tau1': 1.1e-3, 'tau2': 37.5e-3, 'name': 'nmda','Gbar': 2e-9}
SynChanDict={'ampa': SynAMPA,
             'gaba': SynGaba,
             'nmda': SynNMDA}


#C is concentration of Mg, A is 1/eta and B is 1/gamma, 
#Rebekah's:
#These params are too insensitive to voltage
#mgparams={'A':(1/18.0), 'B':(1/99.0), 'C': 1.4} 
#Classic (allows significant calcium at resting potential):
#mgparams={'A':(1/3.57), 'B':(1/62.0), 'C': 1.4} 
#Intermediate
mgparams={'A':(1/6.0), 'B':(1/80.0), 'C': 1.4} 

GbarVar=0.05

#dictionary of synapses at each distance
#distances defined in configSPdict.py

NumGaba=[3, 2, 1]
NumGlu=[1, 2, 3]

#number of synapse classes such as Gaba and Glutamate
NumSynClass = 2
#indices to use in arrays of dimension NumSynClass
GABA=0
GLU=1

