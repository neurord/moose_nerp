# Generated from npzfile: fitgp-proto-cmaes_proto079_84362_24.npz of fit number: 7390
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
ConcOut=2     # mM, default for GHK is 2
Temp=30         # Celsius, needed for GHK objects, some channels

neurontypes = None
morph_file = {'proto':'GP1_41comp_24_proto_7390.p', 'arky': 'GP_arky_41comp.p', 'Npas': 'GP1_41comp.p'}
NAME_SOMA='soma'

#CONDUCTANCES
#Kdr is Kv2
# helper variables to index the Conductance and synapses with distance
# UNITS: meters
#soma spherical so x,y=0,0, 1e-6 means prox=soma
prox = (0,1e-6)
#med =  (0,50e-6)
dist = (1e-6, 1000e-6)
axon = (0.,1., 'axon')
#If using swc files for morphology, specify structure using: _1 as soma, _2 as apical dend, _3 as basal dend and _4 as axon

#CONDUCTANCE VALUES - UNITS of Siemens/meter squared
# _proto for prototypical GP neuron
_proto = _util.NamedDict(
    'proto',
    KDr={prox: 120.28641636043633, dist: 217.4671784427647, axon: 123.4209927468946},
    Kv3={prox: 980.9410727372475, dist: 1470.0569350913831, axon: 593.2857411864359},  # , med:980.9410727372475},
    KvF={prox: 3.5077413883315858, dist: 8.917201955317227, axon: 51.13716852661817},  # , med: 3.5077413883315858},
    KvS={prox: 25.931803240646417, dist: 8.765185432093238, axon: 7.348477077767936},  # , med: 25.931803240646417
    KCNQ={prox: 0.32195918431707254, dist: 0.32195918431707254, axon: 0.32195918431707254},  # , med: 0.32195918431707254
    NaF={prox: 52703.402310716614, dist: 717.9438437086594, axon: 58372.401244892186},  # , med: 52703.402310716614
    NaS={prox: 9.934460578454809, dist: 1.2174113326879807, axon: 3.6987372255827835},  # med: 9.934460578454809,
    Ca={prox: 6.443327418109966e-07, dist: 0.0024293073342097453, axon: 0},  # med: 6.443327418109966e-07,
    HCN1={prox: 4.044184442432762, dist: 4.996262614689237, axon: 0},  # , med: 4.044184442432762
    HCN2={prox: 4.989052298706778, dist: 0.008547083542867123, axon: 0},  # med: 4.989052298706778,
    SKCa={prox: 0.6151817209006618, dist: 11.248832158332352, axon: 0},  # med: 0.6151817209006618,
    #BKCa={prox: 30.841324345463068, dist: 383.98052274629447, axon: 0},  # med: 30.841324345463068,
    BKCa={prox: 62, dist: 768, axon: 0},  # med: 30.841324345463068,
)

_arky = _util.NamedDict(
    'arky',
    KDr={prox: 300, dist: 58.2, axon: 580},
    Kv3={prox: 266, dist: 46.6, axon: 466},
    KvF={prox: 2.5, dist: 2.5, axon: 25},
    KvS={prox: 0.75, dist: 0.75, axon: 7.5},
    KCNQ={prox: 0.04, dist: 0.04, axon: 0.04},
    NaF={prox: 40000, dist: 400, axon: 40000},
    NaS={prox: 0.15, dist: 0.15, axon: 0.5},
    Ca={prox: 0.1, dist: 0.06, axon: 0},
    HCN1={prox: 0.2, dist: 0.2, axon: 0},
    HCN2={prox: 0.25, dist: 0.25, axon: 0},
    SKCa={prox: 35, dist: 3.5, axon: 0},
    BKCa={prox: 200, dist: 200, axon: 0},
)

_Npas = _util.NamedDict(
    'Npas',
    KDr={prox: 300, dist: 58.2, axon: 580},
    Kv3={prox: 266, dist: 46.6, axon: 466},
    KvF={prox: 2.5, dist: 2.5, axon: 25},
    KvS={prox: 0.75, dist: 0.75, axon: 7.5},
    KCNQ={prox: 0.04, dist: 0.04, axon: 0.04},
    NaF={prox: 40000, dist: 400, axon: 40000},
    NaS={prox: 0.15, dist: 0.15, axon: 0.5},
    Ca={prox: 0.1, dist: 0.06, axon: 0},
    HCN1={prox: 0.2, dist: 0.2, axon: 0},
    HCN2={prox: 0.25, dist: 0.25, axon: 0},
    SKCa={prox: 35, dist: 3.5, axon: 0},
    BKCa={prox: 200, dist: 200, axon: 0},
)
Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
)
