#Do not define EREST_ACT or ELEAK here - they are in the .p file
# Contains maximal conductances, name of .p file, and some other parameters
# such as whether to use GHK, or whether to have real spines

import numpy as np

from spspine import util as _util

#if ghkYesNo=0 then ghk not implemented
#Note that you can use GHK without a calcium pool, it uses a default of 5e-5 Cin
if False: # param_sim.Config['ghkYN']:
    ghKluge=0.35e-6
else:
    ghKluge=1

#using 0.035e-9 makes NMDA calcium way too small, using single Tau calcium
ConcOut=2e-3     # default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

def neurontypes():
    "Names of neurontypes of each neuron created"
    return sorted(Condset.keys())

####These numbers are used with split to extract channel and compartment names
compNameNum=2

#will eventually use different morphologies also
morph_file = 'GP1_41comp.p'

#CONDUCTANCES
#Kdr is Kv2
# helper variables to index the Conductance and synapses with distance
prox = (0,0)
med =  (0,50e-6)
dist = (50e-6, 1000e-6)

_proto = _util.NamedDict(
    'proto',
    KDr = {prox:20.8, med:40.2, dist:20.8},
    Kv3 = {prox:09.6, med:38.4, dist:09.6},
    KvF = {prox:22.4, med: 48, dist: 22.4},
    KvS = {prox:53.6, med: 100, dist: 53.6},
    NaF = {prox:50, med: 100, dist: 50},
    HCN1 = {prox:0.628, med: 0, dist: 0.628},
    HCN2 = {prox:1.57, med: 0, dist: 1.57},
    KCNQ = {prox:1.256, med: 2.512, dist:1.256},
    #NaS = {prox: 3.14, med: 251.2, dist: 3.14},
    #Hva = {prox: 6.28, med: 0, dist: 0.471},
    #Sk = {prox: 157, med: 0, dist: 927},
    #Ca = {prox: 5.73, med: 0, dist: 5.73},
)

chanvar = _util.NamedDict(
    'chanvar',
    KDr=0.04,
    Kv3=0.04,
    KvF=0.04,
    Kvs=0.04,
    NaF=0.0,
    HCN1=0.04,
    HCN2=0.04,
    KCNQ=0.04,
    # NaS = 0.04,
    # Hva = 0.04,
    # Sk = 0.04,
    # Ca = 0.04,
)

Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
)
