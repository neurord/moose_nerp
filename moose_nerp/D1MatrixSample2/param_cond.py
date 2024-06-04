# Generated from npzfile: fitd1patchsample2-D1-D1_Matrix_Sample_2_NSG_full_tmp_84362.npz of fit number: 15
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
ConcOut=1.2 #2     # mM, default for GHK is 2e-3
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
morph_file = {'D1':'D1_long_matrix_84362_D1_15_ab.p'}
#morph_file = {'D1':'D1_patch_sample_3.p'} # old_version.

#CONDUCTANCES - UNITS of Siemens/meter squared
_D1 = _util.NamedDict(
    'D1',
    Krp = {prox:5.496179063008175, med:5.496179063008175, dist:5.496179063008175},
    KaF = {prox:29.226600275340836, med:.1*504.23087774531007, dist:5.230428327475811},
    KaS = {prox:264.3503622943717, med: 1.3309193685837277, dist: 39.50680776325384},
    Kir = {prox:5.0158030095879385, med: 1.4993272317591255, dist: 2.180459063459886},
    CaL13 = {prox:0.0078101135569365425*ghKluge, med: 0.0017310717845631434*ghKluge, dist: 0.00725602323771053*ghKluge},
    CaL12 = {prox:0.21426003661615273*ghKluge, med: 0.007050444150763455*ghKluge, dist: 2.3657715885940402*ghKluge},
    CaR = {prox:29.309232705562795*ghKluge, med: 0.07091374426838025*ghKluge, dist: 0.0030125013350808323*ghKluge},
    CaN = {prox:0.020334112974543864*ghKluge, med: 0.0*ghKluge, dist: 0.0*ghKluge},
    CaT33 = {prox:0.0*ghKluge, med: 0.09134861727050925*ghKluge, dist: 0.001034232317817416*ghKluge},
    CaT32 = {prox:0.0*ghKluge, med: 0.012640331616789933*ghKluge, dist: 2.094610044420062*ghKluge}, #using 4.095 is more likely to have strange plateaus at -20 mV
    NaF = {prox:10584.983320327856, med:156.27678897869188 , dist: 260.7915404184741},
    SKCa = {prox:0.23814023377939955, med: 0.23814023377939955, dist:0.23814023377939955 },
    BKCa = {prox:97.99657283280274, med: 97.99657283280274, dist:97.99657283280274},
    CaCC = {prox:0.12397593297975379, med: 0.12397593297975379, dist:0.12397593297975379 },
)

Condset  = _util.NamedDict(
    'Condset',
    D1 = _D1,
)
