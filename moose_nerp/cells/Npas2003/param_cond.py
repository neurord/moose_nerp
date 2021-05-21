# Generated from npzfile: fitgp-Npas-cmaes_Npas2003_84362_24.npz of fit number: 7270
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
morph_file = {'proto': 'GP1_41comp.p', 'arky': 'GP_arky_41comp.p', 'Npas':'GP1_41comp_24_Npas_7270.p'}
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

_Npas = _util.NamedDict(
    'Npas',
    KDr={prox: 250.2932218695007, dist: 268.7354804866685, axon: 280.5723806463007},
    Kv3={prox: 679.2357136114708, dist: 1269.9521615663984, axon: 1538.9903008253873},
    KvF={prox: 0.979330814412403, dist: 35.97721515233846, axon: 0.6154527480113761},
    KvS={prox: 26.879254315083443, dist: 49.763320327853464, axon: 8.490785340728625},
    KCNQ={prox: 0.7913264883782645, dist: 0.7913264883782645, axon: 0.7913264883782645},
    NaF={prox: 436.7965461761581, dist: 1996.5135708819403, axon: 13140.431967720644},
    NaS={prox: 9.878384876529607, dist: 5.234100631140883, axon: 5.470414237005418},
    Ca={prox: 0.024619805684643656, dist: 4.418685849048501e-05, axon: 0},
    HCN1={prox: 3.0613035571340976, dist: 2.4066362883932586e-05, axon: 0},
    HCN2={prox: 4.664483613498876, dist: 0.003303387635864018, axon: 0},
    SKCa={prox: 0.37251169994908934, dist: 0.809342394792432, axon: 0},
    BKCa={prox: 179.30400453044177, dist: 771.8038218702118, axon: 0},
    #BKCa={prox: 400, dist: 1600, axon: 0},
)
Condset  = _util.NamedDict(
    'Condset',
    Npas=_Npas
)
