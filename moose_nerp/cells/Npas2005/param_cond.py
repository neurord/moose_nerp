# Generated from npzfile: fitgp-Npas-cmaes_Npas2005_84362_24.npz of fit number: 7328
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
morph_file = {'proto': 'GP1_41comp.p', 'arky': 'GP_arky_41comp.p', 'Npas':'GP1_41comp_24_Npas_7328.p'}
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
    KDr={prox: 75.65660399636157, dist: 199.63794857362865, axon: 8.02491280223606},
    Kv3={prox: 855.926045811648, dist: 1170.1454546670852, axon: 1864.4380717636457},
    KvF={prox: 11.632016532900819, dist: 30.95521501793393, axon: 29.02968077822384},
    KvS={prox: 22.36067336386422, dist: 48.1973285475009, axon: 25.59739089017718},
    KCNQ={prox: 0.9295322722487949, dist: 0.9295322722487949, axon: 0.9295322722487949},
    NaF={prox: 2900.965428795479, dist: 1947.0696665636287, axon: 1153.8914559584239},
    NaS={prox: 3.7269009191409452, dist: 5.719282369101743, axon: 7.248417584738833},
    Ca={prox: 0.05046306576852568, dist: 0.49144746190184635, axon: 0},
    HCN1={prox: 1.2507833852434733, dist: 0.6546289438821045, axon: 0},
    HCN2={prox: 4.553527872255706, dist: 0.2652407940199485, axon: 0},
    SKCa={prox: 1.348333966009967, dist: 0.5897724027620707, axon: 0},
    #BKCa={prox: 41.46049284310749, dist: 760.8717731078918, axon: 0},
    BKCa={prox: 83, dist: 1522, axon: 0},
)
Condset  = _util.NamedDict(
    'Condset',
    Npas=_Npas
)
