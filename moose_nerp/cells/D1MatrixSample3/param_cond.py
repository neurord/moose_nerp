# Generated from npzfile: fitd1patchsample2-D1-D1_Matrix_Sample_3_NSG_full_tmp_93239.npz of fit number: 47
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
morph_file = {'D1':'D1_long_matrix_93239_D1_47.p'}
#morph_file = {'D1':'D1_patch_sample_3.p'} # old_version.

#CONDUCTANCES - UNITS of Siemens/meter squared
_D1 = _util.NamedDict(
    'D1',
    Krp = {prox:27.767443350753148, med:27.767443350753148, dist:27.767443350753148},
    KaF = {prox:9990.316145155499, med:51.021230046643566, dist:17.950391396925582},
    KaS = {prox:296.0546687545436, med: 914.2790578800586, dist: 58.338418299878825},
    Kir = {prox:18.390275553838112, med: 2.0512463300307124, dist: 7.344834087616996},
    CaL13 = {prox:0.0015763798000977824*ghKluge, med: 0.193842425864601*ghKluge, dist: 0.036762528340846666*ghKluge},
    CaL12 = {prox:0.40492759387689903*ghKluge, med: 1.0446915852096967*ghKluge, dist: 0.12823229258956642*ghKluge},
    CaR = {prox:40.566408172536896*ghKluge, med: 2.348224788460588*ghKluge, dist: 45.212330536333404*ghKluge},
    CaN = {prox:0.0602618405226481*ghKluge, med: 0.0*ghKluge, dist: 0.0*ghKluge},
    CaT33 = {prox:0.0*ghKluge, med: 0.005469950290092841*ghKluge, dist: 0.0016004341109531273*ghKluge},
    CaT32 = {prox:0.0*ghKluge, med: 1.442968477744508*ghKluge, dist: 0.008008817487438223*ghKluge},
    NaF = {prox:13340.715427885596, med:2281.092661584591 , dist: 1.9729185669763},
    SKCa = {prox:0.12382025853097961, med: 0.12382025853097961, dist:0.12382025853097961 },
    BKCa = {prox:20.74111361100438, med: 20.74111361100438, dist:20.74111361100438},
    CaCC = {prox:96.03874603487895, med: 96.03874603487895, dist:96.03874603487895 },
)

Condset  = _util.NamedDict(
    'Condset',
    D1 = _D1,
)
