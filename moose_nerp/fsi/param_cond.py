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

NAME_SOMA='soma'

# helper variables to index the Conductance and synapses with distance
# UNITS: meters
prox = (0, 26.1e-6)
med =  (26.1e-6, 50e-6)
dist = (50e-6, 1000e-6)
#If using swc files for morphology, can add with morphology specific helper variables
#e.g. med=(26.1e-6, 50e-6,'_2')
#_1 as soma, _2 as apical dend, _3 as basal dend and _4 as axon
#Parameters used by optimization from here down

morph_file = {'FSI':'fs_morph.p'} # old_version.

#CONDUCTANCES - UNITS of Siemens/meter squared
_FSI = _util.NamedDict(
    'FSI',
    Ka = {prox:500, med:90, dist:0},
    Kv13 = {prox:1460,  med: 0, dist: 0},
    Kv3132 = {prox:582, med: 0, dist: 0},
    NaF = {prox:1149, med:0, dist: 0},
)
Condset  = _util.NamedDict(
    'Condset',
    FSI = _FSI,
)
#NEXT: edit __init__.py and/or param_model_defaults: no calcium, no spines
#  possibly edit __main__.py
#test that ion channels are within range
