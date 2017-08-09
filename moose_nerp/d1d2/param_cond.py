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
ConcOut=2e-3     # default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

_neurontypes = None
def neurontypes(override=None):
    "Query or set names of neurontypes of each neuron created"
    global _neurontypes
    if override is None:
        return _neurontypes if _neurontypes is not None else sorted(Condset.keys())
    else:
        if any(key not in Condset.keys() for key in override):
            raise ValueError('unknown neuron types requested')
        _neurontypes = override

morph_file = {'D1':'MScell-Entire.p', 'D2': 'MScell-Entire.p'}
NAME_SOMA='soma'
#CONDUCTANCES
#RE has lower soma (50000) and higher prox (6000) and dist (2000) GNa
# GnaCondD1=[60.5e3, 1894, 927]
# GnaCondD2=[69.0e3, 2503, 1073]
# GnaCondset={'D1':GnaCondD1,'D2':GnaCondD2}
# GbkCondD1=[10, 10, 10]
# GbkCondD2=[10, 10, 10]
# GbkCondset={'D1':GbkCondD1,'D2':GbkCondD2}
#CaL values are taken from GHK model, with arbitrary 1e-6 incr conduct
#
#RE has much lower KaF prox: 300; sl lower KaS prox: 200
#RE has Kir=11, Krp=14 (double), gSK=1.0
#RE uses dist dep Ca currents, esp CaT=0 in soma
#CaL13=0.3e-6 soma,0.005e-6 dend
#CaL12=0.6e-6 soma, 0.1e-6 dend
#CaR=0.8e-6 soma, 1.0e-6 dend; CaN=1.2e-6 soma only

# helper variables to index the Conductance and synapses with distance
prox = (0, 26.1e-6)
med =  (26.1e-6, 50e-6)
dist = (50e-6, 1000e-6)

_D1 = _util.NamedDict(
    'D1',
    #Krp = {prox:77.963, med:77.25, dist:7.25},
    Krp = {prox:150.963, med:70.25, dist:77.25},
    #KaF = {prox:3214, med: 571, dist: 314},
    #KaF = {prox:1157, med:500, dist:200},
    KaF = {prox:600, med:500, dist:100},
    KaS = {prox:404.7, med: 35.2, dist: 0},
    Kir = {prox:9.4644, med: 9.4644, dist: 9.4644},
    CaL13 = {prox:12*ghKluge, med: 5.6*ghKluge, dist: 5.6*ghKluge},
    CaL12 = {prox:8*ghKluge, med: 4*ghKluge, dist: 4*ghKluge},
    CaR = {prox:20*ghKluge, med: 45*ghKluge, dist: 44*ghKluge},
    CaN = {prox:4.0*ghKluge, med: 0.0*ghKluge, dist: 0.0*ghKluge},
    CaT = {prox:0.0*ghKluge, med: 1.9*ghKluge, dist: 1.9*ghKluge},
    NaF = {prox:130e3, med: 1894, dist: 927},
    SKCa = {prox:0.5, med: 0.5, dist: 0.5},
    BKCa = {prox:10.32, med: 10, dist: 10},
)
_D2 = _util.NamedDict(
    'D2',
    Krp = {prox:177.25, med:177.25, dist:27.25},
    #KaF = {prox:3214, med: 471, dist: 234},
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
)

Condset  = _util.NamedDict(
    'Condset',
    D1 = _D1,
    D2 = _D2,
)
