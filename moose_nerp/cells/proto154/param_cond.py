# Generated from npzfile: fitgp-proto-cmaes_proto154_84362_24.npz of fit number: 7159
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
ConcOut=2     # mM, default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

neurontypes = None
morph_file = {'proto':'GP1_41comp_24_proto_7159.p', 'arky': 'GP_arky_41comp.p', 'Npas': 'GP1_41comp.p'}
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
    KDr={prox: 75.01363349328577, dist: 224.06912023325566, axon: 109.56316209786557},
    Kv3={prox: 965.4436696785973, dist: 1674.7951029329881, axon: 1961.9753334738714},  # , med:965.4436696785973},
    KvF={prox: 12.050810977125028, dist: 7.15200476201949, axon: 16.6971417587557},  # , med: 12.050810977125028},
    KvS={prox: 6.175768415247292, dist: 2.2785049468184875, axon: 13.29912038469051},  # , med: 6.175768415247292
    KCNQ={prox: 0.9930868108323331, dist: 0.9930868108323331, axon: 0.9930868108323331},  # , med: 0.9930868108323331
    NaF={prox: 4814.914854740478, dist: 29.16065498828257, axon: 25598.56000840923},  # , med: 4814.914854740478
    NaS={prox: 8.559194111123773, dist: 4.6462878860713746, axon: 9.195718490942578},  # med: 8.559194111123773,
    Ca={prox: 0.37948191860801617, dist: 0.0023287227667423416, axon: 0},  # med: 0.37948191860801617,
    HCN1={prox: 1.9547940097366836, dist: 4.352309883359046, axon: 0},  # , med: 1.9547940097366836
    HCN2={prox: 0.9249843399523716, dist: 1.3533594906934736, axon: 0},  # med: 0.9249843399523716,
    SKCa={prox: 0.0011040117025098398, dist: 11.210093511859728, axon: 0},  # med: 0.0011040117025098398,
    BKCa=BKCa={prox: 162.4365599930099, dist: 486.2380974239053, axon: 0},
    #BKCa={prox: 324, dist: 972, axon: 0},  # med: 162.4365599930099,
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
