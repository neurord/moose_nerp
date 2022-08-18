# Generated from npzfile: fitd1patchsample2-D1-D1_Patch_Sample_4_NSG_full_tmp_187463.npz of fit number: 108
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
morph_file = {'D1':'D1_short_patch_187463_D1_108.p'}
#morph_file = {'D1':'D1_patch_sample_3.p'} # old_version.

#CONDUCTANCES - UNITS of Siemens/meter squared
_D1 = _util.NamedDict(
    'D1',
    Krp = {prox:10.33465268842297, med:10.33465268842297, dist:10.33465268842297},
    KaF = {prox:98.90238629239887, med:0*159.18186127663472, dist:0*73.57552460659961},
    KaS = {prox:17.496935981241535, med:0*942.4482443009879, dist: 0*96.5333599202463},
    Kir = {prox:0*45.19068596402698, med: 7.098796065419932, dist: 14.42982220560428},
    CaL13 = {prox:0*0.8236658954732146*ghKluge, med: 0*0.4555045300143664*ghKluge, dist: 0*0.004707362683183888*ghKluge},
    CaL12 = {prox:0*0.04395293917091653*ghKluge, med: 0*0.7064562560370982*ghKluge, dist: 0*0.0010605158405644045*ghKluge},
    CaR = {prox:0*14.304858524613376*ghKluge, med: 0*1.0408723026107292*ghKluge, dist: 0*0.0032824781600049157*ghKluge},
    CaN = {prox:0*1.4476069309427722*ghKluge, med: 0.0*ghKluge, dist: 0.0*ghKluge},
    CaT33 = {prox:0.0*ghKluge, med: 0*0.006943937428105069*ghKluge, dist: 0*0.0018148531523959196*ghKluge},
    CaT32 = {prox:0.0*ghKluge, med: 0*0.03449152974902706*ghKluge, dist: 0*0.003415574130224261*ghKluge},
    NaF = {prox:0*10375.910075122561, med:0*2.013140758754235 , dist: 0*1.7392010153513813},
    SKCa = {prox:0.39816548166768595, med: 0.39816548166768595, dist:0.39816548166768595 },
    BKCa = {prox:30.111797607805894, med: 30.111797607805894, dist:30.111797607805894},
    CaCC = {prox:0.9949457821410473, med: 0.9949457821410473, dist:0.9949457821410473 },
)

Condset  = _util.NamedDict(
    'Condset',
    D1 = _D1,
)
