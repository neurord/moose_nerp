# Generated from npzfile: fitgp_1comp-proto-cmaes_FSI01Aug2014_SLH002_84362_8noCal.npz of fit number: 2908
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
morph_file = {'FSI':'fs_morph.p'} 
NAME_SOMA='soma'

#CONDUCTANCES
#Kdr is Kv2
# helper variables to index the Conductance and synapses with distance
# UNITS: meters
#soma spherical so x,y=0,0, 1e-6 means prox=soma
prox = (0,50e-6)
#med =  (0,50e-6)
dist = (50e-6, 1000e-6)
axon = (0.,1., 'axon')
#If using swc files for morphology, specify structure using: _1 as soma, _2 as apical dend, _3 as basal dend and _4 as axon

#CONDUCTANCE VALUES - UNITS of Siemens/meter squared
# _proto for prototypical GP neuron
_FSI = _util.NamedDict(
    'FSI',
    Kv3132={prox: 751.24040393667866},
    KvF={prox: 194.8582758385129},
    KvS={prox: 99.97317204766406},
    NaF={prox: 18591.3722159805},
)

Condset  = _util.NamedDict(
    'Condset',
    FSI = _FSI,
)
