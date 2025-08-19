# Generated from npzfile: fitd1patchsample2-D1-D1_Patch_Sample_5_NSG_full_tmp_8753287.npz of fit number: 17
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
morph_file = {'D1':'D1_short_patch_8753287_D1_17_ab.p'}
#morph_file = {'D1':'D1_patch_sample_3.p'} # old_version.

#CONDUCTANCES - UNITS of Siemens/meter squared
_D1 = _util.NamedDict(
    'D1',
    Krp = {prox:27.253262624176354, med:27.253262624176354, dist:27.253262624176354},
    KaF = {prox:592.7521268226621, med:198.78063409553224, dist:70.22343767992629},
    KaS = {prox:918.2211609049533, med: 121.13919403439475, dist: 1.7040694119594348},
    Kir = {prox:3.183099590525866, med: 28.96120166160575, dist: 12.2637277782406},
    CaL13 = {prox:0.07040591669598627*ghKluge, med: 0.0021446494071807078*ghKluge, dist: 0.0010326983086313465*ghKluge},
    CaL12 = {prox:0.0031200041239918272*ghKluge, med: 1.085169779042406*ghKluge, dist: 0.020315495396126627*ghKluge},
    CaR = {prox:2.5389480709872543*ghKluge, med: 2.982031424081204*ghKluge, dist: 1.1607354020370952*ghKluge},
    CaN = {prox:0.003701979697629981*ghKluge, med: 0.0*ghKluge, dist: 0.0*ghKluge},
    CaT33 = {prox:0.0*ghKluge, med: 0.07055441665882141*ghKluge, dist: 0.01498484770743048*ghKluge},
    CaT32 = {prox:0.0*ghKluge, med: 0.44676845433261203*ghKluge, dist: 0.2448470865403426*ghKluge},
    NaF = {prox:17611.462693764395, med:2.2847566839893 , dist: 1.04798697068298},
    SKCa = {prox:0.41703631559185905, med: 0.41703631559185905, dist:0.41703631559185905 },
    BKCa = {prox:46.39459672141241, med: 46.39459672141241, dist:46.39459672141241},
    CaCC = {prox:0.7940528531979776, med: 0.7940528531979776, dist:0.7940528531979776 },
)

Condset  = _util.NamedDict(
    'Condset',
    D1 = _D1,
)
