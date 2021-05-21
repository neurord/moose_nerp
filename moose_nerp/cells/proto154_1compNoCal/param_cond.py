# Generated from npzfile: fitgp_1comp-proto-cmaes_proto154_84362_8noCal.npz of fit number: 8151
#Do not define EREST_ACT or ELEAK here - they are in the .p file
# Contains maximal conductances, name of .p file, and some other parameters
# such as whether to use GHK, or whether to have real spines

import numpy as np

from moose_nerp.prototypes import util as _util

#if ghkYesNo=0 then ghk not implemented
#Note that you can use GHK without a calcium pool, it uses a default of 5e-5 Cin
if False: # param_sim.Config['ghkYN']:
    ghKluge=0.35e-6
else:
    ghKluge=1

#using 0.035e-9 makes NMDA calcium way too small, using single Tau calcium
ConcOut=2e-3     # mM, default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

neurontypes = None
morph_file = {'proto':'GP_soma_8noCal_proto_8151.p', 'arky': 'GP_soma.p', 'Npas': 'GP_soma.p'}
NAME_SOMA='soma'

#CONDUCTANCES
#Kdr is Kv2
# helper variables to index the Conductance and synapses with distance
# UNITS: meters
#soma spherical so x,y=0,0, 1e-6 means prox=soma
prox = (0,20e-6)
#med =  (0,50e-6)
dist = (1e-6, 1000e-6)
axon = (0.,1., 'axon')
#If using swc files for morphology, specify structure using: _1 as soma, _2 as apical dend, _3 as basal dend and _4 as axon

#CONDUCTANCE VALUES - UNITS of Siemens/meter squared
# _proto for prototypical GP neuron
_proto = _util.NamedDict(
    'proto',
    KDr={prox: 27.343138967696184},
    Kv3={prox: 977.0650830330653},
    KvF={prox: 228.49240134488954},
    KvS={prox: 87.48247275990892},
    NaF={prox: 3285.69063083201},
    HCN2={prox: 4.130672163441272},
)

_arky = _util.NamedDict(
    'arky',
    KDr={prox: 708.11742766709327},
    Kv3={prox: 536.5656407446413},
    KvF={prox: 1.74023152805182},
    KvS={prox: 48.004268194532763626},
    NaF={prox: 4321.968478081542},
    HCN2={prox: 3.5734741500058576},
)

_Npas = _util.NamedDict(
    'Npas',
    KDr={prox: 335.11742766709327},
    Kv3={prox: 386.5656407446413},
    KvF={prox: 147.74023152805182},
    KvS={prox: 27.004268194532763626},
    NaF={prox: 20556.968478081542},
    HCN2={prox: 2.5734741500058576},
)
Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
    #arky = _arky,
    #Npas=_Npas
)
