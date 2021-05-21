# Generated from npzfile: fitgp-proto-cmaes_proto154_84362_24.npz of fit number: 6398
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
morph_file = {'proto':'GP1_41comp_24_proto_6398.p'}
             ## 'arky': 'GP_arky_41comp.p'}
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
    KDr={prox: 721.147926041521, dist: 106.12827790455063, axon: 283.0391515056384},
    Kv3={prox: 669.51355396041, dist: 1599.626497905752, axon: 1.074194666621207},  # , med:669.51355396041},
    KvF={prox: 30.440004302674488, dist: 5.088755788537158, axon: 31.38076081404364},  # , med: 30.440004302674488},
    KvS={prox: 0.9969466673760452, dist: 4.388134249072175, axon: 20.528228893571885},  # , med: 0.9969466673760452
    KCNQ={prox: 0.578505374045909, dist: 0.578505374045909, axon: 0.578505374045909},  # , med: 0.578505374045909
    NaF={prox: 21701.342895373706, dist: 22.884978164846288, axon: 11355.584838282499},  # , med: 21701.342895373706
    NaS={prox: 4.295277888200458, dist: 7.304542445654162, axon: 2.6116343600220033},  # med: 4.295277888200458,
    Ca={prox: 0.19835338541633807, dist: 0.14784381009216302, axon: 0},  # med: 0.19835338541633807,
    HCN1={prox: 3.523693437964114, dist: 2.1308516762770964, axon: 0},  # , med: 3.523693437964114
    HCN2={prox: 2.718195087299697, dist: 0.2638958442012078, axon: 0},  # med: 2.718195087299697,
    SKCa={prox: 1.3668728877412653, dist: 5.162280847044437, axon: 0},  # med: 1.3668728877412653,
    BKCa={prox: 468.9349300269476, dist: 145.97717240371728, axon: 0},  # med: 468.9349300269476,
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
    #arky=_arky,
)
