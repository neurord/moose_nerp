# Generated from npzfile: fitgp-Npas-cmaes_Npas2006_84362_24.npz of fit number: 6186
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
morph_file = {'proto': 'GP1_41comp.p', 'arky': 'GP_arky_41comp.p', 'Npas':'GP1_41comp_24_Npas_6186.p'}
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
    KDr={prox: 625.8592518272382, dist: 215.60062816798296, axon: 58.2980404900246},
    Kv3={prox: 732.7894235949365, dist: 606.5755404530711, axon: 1149.8695938160624},
    KvF={prox: 13.633988447641922, dist: 23.793601845153546, axon: 79.52483066479697},
    KvS={prox: 5.447516744486231, dist: 25.491200082359683, axon: 6.700197250108917},
    KCNQ={prox: 0.36494874933365706, dist: 0.36494874933365706, axon: 0.36494874933365706},
    NaF={prox: 592.8651020395013, dist: 1337.22800942151, axon: 19470.295180886533},
    NaS={prox: 0.047790363068377466, dist: 2.469690124264712, axon: 0.8767090717102308},
    Ca={prox: 0.29748381330642754, dist: 0.04457231301278166, axon: 0},
    HCN1={prox: 2.3120932774216927, dist: 2.5398717167943268, axon: 0},
    HCN2={prox: 0.008551688413615605, dist: 4.991834702565233, axon: 0},
    SKCa={prox: 0.21889487090651727, dist: 0.01362275430489544, axon: 0},
    #BKCa={prox: 297.99245306761316, dist: 588.2828708693687, axon: 0},
    BKCa={prox: 588, dist: 1176, axon: 0},
)
Condset  = _util.NamedDict(
    'Condset',
    Npas=_Npas
)
