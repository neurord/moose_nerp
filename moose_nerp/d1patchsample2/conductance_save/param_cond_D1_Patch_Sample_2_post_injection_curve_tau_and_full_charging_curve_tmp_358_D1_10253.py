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
#morph_file = {'D1':'MScell-primDend.p', 'D2': 'MScell-primDend.p'} # test_version.
morph_file = {'D1':'D1_short_patch_358_D1_10253.p'} # old_version.

#CONDUCTANCES - UNITS of Siemens/meter squared
_D1 = _util.NamedDict(
    'D1',
    Krp = {prox:0.0266, med:0.0740, dist:0.02746},
    KaF = {prox:1430.85, med:406.796, dist:91.140},
    KaS = {prox:13.95, med: 1419.54, dist: 62.524},
    Kir = {prox:12.7875, med: 12.7875, dist: 12.7875},
    CaL13 = {prox:16.8551*ghKluge, med: 4.01164*ghKluge, dist: 2.0984*ghKluge},
    CaL12 = {prox:99.868*ghKluge, med: 7.40227*ghKluge, dist: 5.9285*ghKluge},
    CaR = {prox:10.63412*ghKluge, med: 5.010147*ghKluge, dist: 46.54782*ghKluge},
    CaN = {prox:7.2082*ghKluge, med: 0.0*ghKluge, dist: 0.0*ghKluge},
    CaT = {prox:0.0*ghKluge, med: 8.1514*ghKluge, dist: 4.09788*ghKluge},
    NaF = {prox:229400, med:4080.6 , dist: 705.49},
    SKCa = {prox:1.4664, med: 1.4664, dist:1.4664 },
    BKCa = {prox:12.96, med: 12.96, dist:12.96},
    CaCC = {prox:5, med: 2, dist:2 },
)

Condset  = _util.NamedDict(
    'Condset',
    D1 = _D1,
)
