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
ConcOut=2e-3     # default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

_neurontypes = None
def neurontypes(override=None):
    "Query or set names of neurontypes of each neuron created"
    global _neurontypes
    if override is None:
        return _neurontypes if _neurontypes is not None else sorted(Condset.keys())
    else:
        if any(key not in Condset.keys() for key in override):
            raise ValueError('unknown neuron types requested')
        _neurontypes = override

morph_file = {'proto':'GP1_41comp.p','arky':'GP_arky_41comp.p'}
NAME_SOMA='soma'

#CONDUCTANCES
#Kdr is Kv2
# helper variables to index the Conductance and synapses with distance
#soma spherical so x,y=0,0, 1e-6 means prox=soma
prox = (0,1e-6)
#med =  (0,50e-6)
dist = (1e-6, 1000e-6)
axon = (0.,1., 'axon')
# check Gbar vlues for NaS,Hva,SK and Ca
# _proto for prototypical GP neuron
_proto = _util.NamedDict(
    'proto',
    KDr={prox: 40, dist: 7.75, axon: 77.5},
    Kv3={prox: 800, dist: 140, axon: 1400},  # , med:38.4},
    KvF={prox: 10, dist: 10, axon: 100},  # , med: 48},
    KvS={prox: 3, dist: 3, axon: 30},  # , med: 100
    KCNQ={prox: 0.04, dist: 0.04, axon: 0.04},  # , med: 2.512
    NaF={prox: 40000, dist: 400, axon: 40000},  # , med: 100
    NaS={prox: 0.5, dist: 0.5, axon: 0.5},  # med: 251.2,
    Ca={prox: 0.1, dist: 0.06, axon: 0},  # med: 0,
    HCN1={prox: 0.2, dist: 0.2, axon: 0},  # , med: 0
    HCN2={prox: 0.5, dist: 0.5, axon: 0},  # med: 0,
    SKCa={prox: 2, dist: 0.15, axon: 0},  # med: 0,
    BKCa={prox: 0.1, dist: 0.1, axon: 0},  # med: 10,
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

Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
    arky=_arky,
)
