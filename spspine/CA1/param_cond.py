#Do not define EREST_ACT or ELEAK here - they are in the .p file
# Contains maximal conductances, name of .p file, and some other parameters
# such as whether to use GHK, or whether to have real spines

import numpy as np

from spspine import param_sim, util as _util

#if ghkYesNo=0 then ghk not implemented
#Note that you can use GHK without a calcium pool, it uses a default of 5e-5 Cin
if False: # param_sim.Config['ghkYN']:
    ghKluge=0.35e-6
else:
    ghKluge=1

#using 0.035e-9 makes NMDA calcium way too small, using single Tau calcium
ConcOut=2e-3     # default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

def neurontypes():
    "Names of neurontypes of each neuron created"
    return sorted(Condset.keys())

####These numbers are used with split to extract channel and compartment names
compNameNum=2

#will eventually use different morphologies also
morph_file = 'MScell-Entire.p'

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
inclu = (0, 1000e-6)

_CA1 = _util.NamedDict(
    'CA1',
    Kdr =  {inclu: 70.0}
    Kadist = {inclu: 200.0}
    Kaprox = {inclu: 200.0}
    Na = {inclu: 140.0}
)


chanvar = _util.NamedDict(
    'chanvar',
    Krp = 0.04,
    KaF = 0.04,
    KaS = 0.04,
    Kir = 0.04,
    CaL13 = 0.04,
    CaL12 = 0.04,
    CaR = 0.04,
    CaN = 0.04,
    CaT = 0.04,
    NaF = 0.0,
    BKCa = 0.04,
    SKCa = 0.04,
)

Condset  = _util.NamedDict(
    'Condset',
    CA1 = _CA1,

)
