# Generated from npzfile: fitd1d2-D1-D1_Patch_Sample_2_post_injection_curve_tau_and_full_charging_curve_tmp_358.npz of fit number: 10253
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
ConcOut=2     # mM, default for GHK is 2e-3
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
morph_file = {'D1':'D1_short_patch.p'} # old_version.
#morph_file = {'D1':'D1_patch_sample_3.p'} # old_version.

#CONDUCTANCES - UNITS of Siemens/meter squared
_D1 = _util.NamedDict(
    'D1',
    Krp = {prox:0.05006551249741205, med:0.05006551249741205, dist:0.05006551249741205},
    KaF = {prox:4389.470290538669, med:749.8955695196053, dist:28.14751553099997},
    KaS = {prox:475.0972939473723, med: 597.1440354876032, dist: 76.32524179163596},
    Kir = {prox:5.933189483909874, med: 5.933189483909874, dist: 5.933189483909874},
    CaL13 = {prox:9.231777352086931*ghKluge, med: 2.4013133071400934*ghKluge, dist: 0.6803723796672949*ghKluge},
    CaL12 = {prox:0.3670566089203581*ghKluge, med: 3.9112224494974255*ghKluge, dist: 2.3162095058181715*ghKluge},
    CaR = {prox:6.020952615897578*ghKluge, med: 9.738386461210768*ghKluge, dist: 17.31893386016392*ghKluge},
    CaN = {prox:9.033232913044772*ghKluge, med: 0.0*ghKluge, dist: 0.0*ghKluge},
    CaT33 = {prox:0.0*ghKluge, med: 0.0007721704132985384*ghKluge, dist: 0.04371369995209336*ghKluge},
    CaT32 = {prox:0.0*ghKluge, med: 0.007721704132985384*ghKluge, dist: 0.4371369995209336*ghKluge},
    NaF = {prox:20264.011048395758, med:35054.87847330811 , dist: 2795.7343482062784},
    SKCa = {prox:0.6810806557420438, med: 0.6810806557420438, dist:0.6810806557420438 },
    BKCa = {prox:12.648119595394444, med: 12.648119595394444, dist:12.648119595394444},
    CaCC = {prox:1.0887331920472634, med: 1.0887331920472634, dist:1.0887331920472634 },
)

Condset  = _util.NamedDict(
    'Condset',
    D1 = _D1,
)
