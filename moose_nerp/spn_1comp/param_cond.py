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

NAME_SOMA='soma'

# helper variables to index the Conductance and synapses with distance
# UNITS: meters
prox = (0, 50.1e-6)
med =  (50.1e-6, 50e-6)
dist = (50e-6, 1000e-6)
#If using swc files for morphology, can add with morphology specific helper variables
#e.g. med=(26.1e-6, 50e-6,'_2')
#_1 as soma, _2 as apical dend, _3 as basal dend and _4 as axon
#Parameters used by optimization from here down
morph_file = {'D1':'MScell-soma.p', 'D2': 'MScell-soma.p'} # old_version.

#CONDUCTANCES - UNITS of Siemens/meter squared
_D1 = _util.NamedDict(
    'D1',
    KaF = {prox:1530.85},
    KaS = {prox:113.95},
    Kir = {prox:12.7875},
    CaL12 = {prox:29.868*ghKluge},
    CaR = {prox:10.63412*ghKluge},
    NaF = {prox:140e3},
)
_D2 = _util.NamedDict(
    'D2',
    KaF = {prox:1441},
    KaS = {prox:672},
    Kir = {prox:8.2},
    CaL12 = {prox:4*ghKluge},
    CaR = {prox:10*ghKluge},
    NaF = {prox:150.0e3},
)

Condset  = _util.NamedDict(
    'Condset',
    D1 = _D1,
    D2 = _D2,
)
