# Generated from npzfile: fitgp-proto-cmaes_proto047_84384_24.npz of fit number: 7821
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
morph_file = {'proto':'GP1_41comp_24_proto_7395_24_proto_7821.p'}
              #'arky': 'GP_arky_41comp.p', 'Npas': 'GP1_41comp_24_Npas_7270.p'}
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
    KDr={prox: 151.60069472315223, dist: 113.76737930046734, axon: 234.4582441435215},
    Kv3={prox: 876.4865140852901, dist: 502.43076782704895, axon: 1470.627157248897},  # , med:876.4865140852901},
    KvF={prox: 6.23637658369084, dist: 24.327410047616215, axon: 92.46871372458511},  # , med: 6.23637658369084},
    KvS={prox: 8.442601211533391, dist: 28.943554447059693, axon: 25.486247186362974},  # , med: 8.442601211533391
    KCNQ={prox: 0.08983706648179858, dist: 0.08983706648179858, axon: 0.08983706648179858},  # , med: 0.08983706648179858
    NaF={prox: 100.04787643859751, dist: 19.841034362668815, axon: 97074.2356875824},  # , med: 100.04787643859751
    NaS={prox: 6.9074351045412055, dist: 6.636151679951692, axon: 3.092252945646026},  # med: 6.9074351045412055,
    Ca={prox: 0.0050378472906975795, dist: 0.20041810983933112, axon: 0},  # med: 0.0050378472906975795,
    HCN1={prox: 4.701757097754434, dist: 4.252376410749097, axon: 0},  # , med: 4.701757097754434
    HCN2={prox: 1.1123267630768898, dist: 2.554635572187788, axon: 0},  # med: 1.1123267630768898,
    SKCa={prox: 32.70712162505971, dist: 12.682577867602735, axon: 0},  # med: 32.70712162505971,
    BKCa={prox: 171.96302130781493, dist: 611.1513876135258, axon: 0},
    #BKCa={prox: 171.96302130781493, dist: 611.1513876135258, axon: 0},  # med: 171.96302130781493,
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
)
Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
    Npas=_Npas
)'''
