
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
ConcOut=1.2#2#e-3     # mM, default for GHK is 2e-3
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
    Krp = {prox:0.030412982511354256, med:0.1187764150066657, dist:0.04371546368456764},
    KaF = {prox:1198.6106336137718, med:694.7565410220733, dist:73.63781307916403},
    KaS = {prox:42.301506989682956, med: 598.1981044394101, dist: 48.109060863002135},
    Kir = {prox:4.593346732504891, med: 4.593346732504891, dist: 4.593346732504891},
    CaL13 = {prox:13.497468485634915*ghKluge, med: 0.0003742350945052135*ghKluge, dist: 0.14313485017720698*ghKluge},
    CaL12 = {prox:8.224130813140018*ghKluge, med: 4.755641803836486*ghKluge, dist: 1.359189909219976*ghKluge},
    CaR = {prox:2.0319640194309367*ghKluge, med: 42.098081446111564*ghKluge, dist: 77.87435524955357*ghKluge},
    CaN = {prox:4.8225437615192845*ghKluge, med: 0.0*ghKluge, dist: 0.0*ghKluge},
    CaT = {prox:0.0*ghKluge, med: 0.06754073749968142*ghKluge, dist: 0.003149595759888971*ghKluge},
    NaF = {prox:278913.52391468134, med:3191.508903477709 , dist: 1469.6950316113168},
    SKCa = {prox:4.098903673534784, med: 4.098903673534784, dist:4.098903673534784 },
    BKCa = {prox:5.7478346619307406, med: 5.7478346619307406, dist:5.7478346619307406},
    CaCC = {prox:0.31307249403534215, med: 0.31307249403534215, dist:0.31307249403534215 },
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
