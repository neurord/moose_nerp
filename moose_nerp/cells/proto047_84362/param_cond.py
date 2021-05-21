# Generated from npzfile: fitgp-proto-cmaes_proto047_84362_24.npz of fit number: 6217
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
morph_file = {'proto':'GP1_41comp_24_proto_6217.p'}
              #'arky': 'GP_arky_41comp.p'}
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
    KDr={prox: 434.9394132102496, dist: 64.96410150958411, axon: 129.24314862037647},
    Kv3={prox: 679.8527381812426, dist: 422.63439531490405, axon: 414.2445010709591},  # , med:679.8527381812426},
    KvF={prox: 3.1396938488774238, dist: 2.32572685495933, axon: 45.90079196744677},  # , med: 3.1396938488774238},
    KvS={prox: 18.11863873318851, dist: 19.165688147878583, axon: 17.649518548724288},  # , med: 18.11863873318851
    KCNQ={prox: 0.04472386632776082, dist: 0.04472386632776082, axon: 0.04472386632776082},  # , med: 0.04472386632776082
    NaF={prox: 469.5422174970995, dist: 22.792993140107917, axon: 3958.1814559693853},  # , med: 469.5422174970995
    NaS={prox: 6.837771623044803, dist: 2.119455610664537, axon: 1.1402373753318071},  # med: 6.837771623044803,
    Ca={prox: 0.2977718858939978, dist: 0.2611610257146589, axon: 0},  # med: 0.2977718858939978,
    HCN1={prox: 0.9036850209030474, dist: 1.1867191085101634, axon: 0},  # , med: 0.9036850209030474
    HCN2={prox: 0.8337083259141735, dist: 3.555653675137907, axon: 0},  # med: 0.8337083259141735,
    SKCa={prox: 1.1337603847076458, dist: 7.074674047097322, axon: 0},  # med: 1.1337603847076458,
    BKCa={prox: 11.429724379510244, dist: 194.4667178059927, axon: 0},  # med: 11.429724379510244,
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
)'''

Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
    arky=_arky,
)
