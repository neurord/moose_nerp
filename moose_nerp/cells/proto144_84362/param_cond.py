# Generated from npzfile: fitgp-proto-cmaes_proto144_84362_24.npz of fit number: 6398
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
morph_file = {'proto':'GP1_41comp_24_proto_6398.p'} #'arky': 'GP_arky_41comp.p'}
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
    KDr={prox: 834.0245832547635, dist: 56.99125055627413, axon: 153.4255924456234},
    Kv3={prox: 739.8340486311502, dist: 536.9099574626429, axon: 1192.0699294645933},  # , med:739.8340486311502},
    KvF={prox: 5.8553871571009175, dist: 49.85888884381543, axon: 74.77192696439074},  # , med: 5.8553871571009175},
    KvS={prox: 13.378336061486289, dist: 32.38834007838196, axon: 10.584395880560809},  # , med: 13.378336061486289
    KCNQ={prox: 0.5237116554481058, dist: 0.5237116554481058, axon: 0.5237116554481058},  # , med: 0.5237116554481058
    NaF={prox: 19621.35680324152, dist: 10.153445802115677, axon: 591.7219581641156},  # , med: 19621.35680324152
    NaS={prox: 3.7665330917032547, dist: 2.659782020161396, axon: 0.34027721945979134},  # med: 3.7665330917032547,
    Ca={prox: 0.99949946342345, dist: 0.33088360700342057, axon: 0},  # med: 0.99949946342345,
    HCN1={prox: 4.614307706690431, dist: 3.646874622578351, axon: 0},  # , med: 4.614307706690431
    HCN2={prox: 4.999863404886508, dist: 3.9671073811201802, axon: 0},  # med: 4.999863404886508,
    SKCa={prox: 2.760649967062625, dist: 8.658400828060975, axon: 0},  # med: 2.760649967062625,
    BKCa={prox: 0.6120566621609183, dist: 784.6765349296644, axon: 0},  # med: 0.6120566621609183,
)
'''
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
'''
Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
    arky=_arky,
)
