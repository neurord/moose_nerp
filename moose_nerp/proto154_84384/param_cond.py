# Generated from npzfile: fitgp-proto-cmaes_proto154_84384_24.npz of fit number: 7983
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
morph_file = {'proto':'GP1_41comp_24_proto_7395_24_proto_7983.p'}
              ##'arky': 'GP_arky_41comp.p', 'Npas': 'GP1_41comp_24_Npas_7270.p'}
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
    KDr={prox: 911.7178766440811, dist: 41.49763695550516, axon: 59.90952962932371},
    Kv3={prox: 999.215064234903, dist: 745.4924093570389, axon: 1284.5568368323927},  # , med:999.215064234903},
    KvF={prox: 40.726933191849625, dist: 23.583599045178143, axon: 77.23111351963732},  # , med: 40.726933191849625},
    KvS={prox: 6.013316833338406, dist: 48.930143555784554, axon: 2.5031208206248037},  # , med: 6.013316833338406
    KCNQ={prox: 0.41578283061285354, dist: 0.41578283061285354, axon: 0.41578283061285354},  # , med: 0.41578283061285354
    NaF={prox: 7701.282853062054, dist: 14.420063967350105, axon: 92037.73404081738},  # , med: 7701.282853062054
    NaS={prox: 6.079394710937423, dist: 9.585424628034213, axon: 5.334826519106627},  # med: 6.079394710937423,
    Ca={prox: 0.05191738185898093, dist: 0.04579475773579736, axon: 0},  # med: 0.05191738185898093,
    HCN1={prox: 2.5136849882801515, dist: 4.425151508142181, axon: 0},  # , med: 2.5136849882801515
    HCN2={prox: 1.4597559839946261, dist: 2.3386225077223086, axon: 0},  # med: 1.4597559839946261,
    SKCa={prox: 0.005904276462949703, dist: 20.291893608820587, axon: 0},  # med: 0.005904276462949703,
    BKCa={prox: 248.89394398231212, dist: 755.5682517693289, axon: 0},
    #BKCa={prox: 248.89394398231212, dist: 755.5682517693289, axon: 0},  # med: 248.89394398231212,
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

_Npas = _util.NamedDict(
    'Npas',
    KDr={prox: 250.2932218695007, dist: 268.7354804866685, axon: 280.5723806463007},
    Kv3={prox: 679.2357136114708, dist: 1269.9521615663984, axon: 1538.9903008253873},
    KvF={prox: 0.979330814412403, dist: 35.97721515233846, axon: 0.6154527480113761},
    KvS={prox: 26.879254315083443, dist: 49.763320327853464, axon: 8.490785340728625},
    KCNQ={prox: 0.7913264883782645, dist: 0.7913264883782645, axon: 0.7913264883782645},
    NaF={prox: 436.7965461761581, dist: 1996.5135708819403, axon: 13140.431967720644},
    NaS={prox: 9.878384876529607, dist: 5.234100631140883, axon: 5.470414237005418},
    Ca={prox: 0.024619805684643656, dist: .00004418685849048501, axon: 0},
    HCN1={prox: 3.0613035571340976, dist: .000024066362883932586, axon: 0},
    HCN2={prox: 4.664483613498876, dist: 0.003303387635864018, axon: 0},
    SKCa={prox: 0.37251169994908934, dist: 0.809342394792432, axon: 0},
    BKCa={prox: 179.30400453044177, dist: 771.8038218702118, axon: 0},
    #BKCa={prox: 400, dist: 1600, axon: 0}, ethanol
)'''
Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
    #Npas=_Npas
)
