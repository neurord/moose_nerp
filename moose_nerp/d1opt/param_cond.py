

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
morph_file = {'D1':'MScelltaperspines.p', 'D2': 'MScelltaperspines.p'} # old_version.

#CONDUCTANCES - UNITS of Siemens/meter squared
_D1 = _util.NamedDict(
    'D1',
    Krp = {prox:0.03153098536573899, med:0.11798139588840685, dist:0.04323845451253293},
    KaF = {prox:1200.5548368381437, med:697.4519737095645, dist:73.05445633059472},
    KaS = {prox:40.404877003444774, med: 603.2880958230676, dist: 47.47895158472515},
    Kir = {prox:4.588682375508999, med: 4.588682375508999, dist: 4.588682375508999},
    CaL13 = {prox:13.54950268345995*ghKluge, med: 0.026889208914742325*ghKluge, dist: 0.15944551166340565*ghKluge},
    CaL12 = {prox:8.285376322179289*ghKluge, med: 4.832450810847347*ghKluge, dist: 1.3974048064445423*ghKluge},
    CaR = {prox:2.1818627864028284*ghKluge, med: 42.21307696914031*ghKluge, dist: 78.36808727998259*ghKluge},
    CaN = {prox:4.656952174944405*ghKluge, med: 0.0*ghKluge, dist: 0.0*ghKluge},
    CaT = {prox:0.0*ghKluge, med: 0.0679269038806246*ghKluge, dist: 0.008854229505179834*ghKluge},
    NaF = {prox:284658.39584274805, med:3223.160493124536 , dist: 1485.214919735172},
    SKCa = {prox:4.089264671148438, med: 4.089264671148438, dist:4.089264671148438 },
    BKCa = {prox:5.70792868048078, med: 5.70792868048078, dist:5.70792868048078},
    CaCC = {prox:0.29517102580362675, med: 0.29517102580362675, dist:0.29517102580362675 },
)
_D2 = _util.NamedDict(
    'D2',
    Krp = {prox:177.25, med:177.25, dist:27.25},
    KaF = {prox:641, med:300, dist:100},
    KaS = {prox:372, med: 32.9, dist: 0},
    Kir = {prox:6.2, med: 6.2, dist: 6.2},
    CaL13 = {prox:10*ghKluge, med: 4*ghKluge, dist: 4*ghKluge},
    CaL12 = {prox:4*ghKluge, med: 2.2*ghKluge, dist: 2.2*ghKluge},
    CaR = {prox:20*ghKluge, med: 45*ghKluge, dist: 45*ghKluge},
    CaN = {prox:1.5*ghKluge, med: 0.0*ghKluge, dist: 0.0*ghKluge},
    CaT = {prox:0.0*ghKluge, med: 1.9*ghKluge, dist: 1.9*ghKluge},
    NaF = {prox:150.0e3, med: 2503, dist: 1073},
    SKCa = {prox:0.5, med: 0.5, dist: 0.5},
    BKCa = {prox:10, med: 10, dist: 10},
    CaCC = {prox:5, med: 2, dist:2 },
)

Condset  = _util.NamedDict(
    'Condset',
    D1 = _D1,
    D2 = _D2,
)
