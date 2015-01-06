# SPcondParam.py
#Do not define EREST_ACT or ELEAK here - they are in the .p file
# Contains maximal conductances, name of .p file, and some other parameters
# such as whether to use GHK, or whether to have real spines

import numpy as np

def isCaChannel(channame):
    return channame.startswith('Ca')

def isKCaChannel(channame):
    return channame.endswith('KCa')

#if ghkYesNo=0 then ghk not implemented
#Note that you can use GHK without a calcium pool, it uses a default of 5e-5 Cin
ghkYesNo=1
ghKluge=0.35e-6        #set this = 1 if ghkYesNo=0, ~0.35e-6 for ghkYesNo=1
#using 0.035e-9 makes NMDA calcium way too small, using single Tau calcium
ConcOut=2e-3     # default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK object
Farady=96485
R=8.31

#dictionary to index the Conductance and synapses with distance
distTable=[26.1e-6,   # "prox"
           50e-6,     # "mid"
           1000e-6]   # "dist"

#neurontype of each neuron created, with set of conductances
neurontypes=['D1', 'D2']

#will eventually use different morphologies also
p_file = 'MScell-Entire.p'

#CONDUCTANCES
#RE has lower soma (50000) and higher prox (6000) and dist (2000) GNa
# GnaCondD1=[60.5e3, 1894, 927]
# GnaCondD2=[69.0e3, 2503, 1073]
# GnaCondset={'D1':GnaCondD1,'D2':GnaCondD2}
# GbkCondD1=[10, 10, 10]
# GbkCondD2=[10, 10, 10]
# GbkCondset={'D1':GbkCondD1,'D2':GbkCondD2}
#CaL values are taken from GHK model, with arbitrary 1e-6 incr conduct
#
#RE has much lower KaF prox: 300; sl lower KaS prox: 200
#RE has Kir=11, Krp=14 (double), gSK=1.0
#RE uses dist dep Ca currents, esp CaT=0 in soma
#CaL13=0.3e-6 soma,0.005e-6 dend
#CaL12=0.6e-6 soma, 0.1e-6 dend
#CaR=0.8e-6 soma, 1.0e-6 dend; CaN=1.2e-6 soma only
CondD1={#'Krp': [77.963,77.25,7.25],
        'Krp': [150.963,70.25,77.25],
        #'KaF': [3214, 571, 314],
        #'KaF':[1157,500,200],
        'KaF':[600,500,100],
        'KaS': [404.7, 35.2, 0],
        'Kir': [9.4644, 9.4644, 9.4644],
        'CaL13': [12*ghKluge, 5.6*ghKluge, 5.6*ghKluge],
        'CaL12': [8*ghKluge, 4*ghKluge, 4*ghKluge],
        'CaR': [20*ghKluge, 45*ghKluge, 44*ghKluge],
        'CaN': [4.0*ghKluge, 0.0*ghKluge, 0.0*ghKluge],
        'CaT': [0.0*ghKluge, 1.9*ghKluge, 1.9*ghKluge],
        'NaF':[130e3, 1894, 927],
        'SKCa':[0.5, 0.5, 0.5],
        'BKCa':[10.32, 10, 10]
        }
CondD2={'Krp': [177.25,177.25,27.25],
        #'KaF': [3214, 471, 234],
        'KaF':[641,300,100],
        'KaS': [372, 32.9, 0],
        'Kir': [6.2, 6.2, 6.2],
        'CaL13': [10*ghKluge, 4*ghKluge, 4*ghKluge],
        'CaL12': [4*ghKluge, 2.2*ghKluge, 2.2*ghKluge],
        'CaR': [20*ghKluge, 45*ghKluge, 45*ghKluge],
        'CaN': [1.5*ghKluge, 0.0*ghKluge, 0.0*ghKluge],
        'CaT': [0.0*ghKluge, 1.9*ghKluge, 1.9*ghKluge],
        'NaF':[150.0e3, 2503, 1073],
        'SKCa':[0.5, 0.5, 0.5],
        'BKCa':[10, 10, 10]
        }
chanvar={'Krp': 0.04,
         'KaF': 0.04,
         'KaS': 0.04,
         'Kir': 0.04,
         'CaL13': 0.04,
         'CaL12': 0.04,
         'CaR': 0.04,
         'CaN': 0.04,
         'CaT': 0.04,
         'NaF': 0.0,
         'BKCa': 0.04,
         'SKCa': 0.04}

Condset={'D1':CondD1,'D2':CondD2}


