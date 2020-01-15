# Generated from npzfile: fitgp_1comp-proto-cmaes_FSI01Aug2014_SLH002_84362_8noCal.npz of fit number: 2908
# Generated from npzfile: fitgp-Npas-cmaes_Npas2003_84362_24.npz of fit number: 7270

from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes.chan_proto import (
    AlphaBetaChannelParams,
    StandardMooseTauInfChannelParams,
    TauInfMinChannelParams,
    ZChannelParams,
    BKChannelParams,
    ChannelSettings,
    TypicalOneD,
    TwoD)

#units for membrane potential: volts
krev=-90e-3
narev=50e-3
carev=130e-3
hcnrev=-30e-3
ZpowCDI=2

VMIN = -120e-3
VMAX = 50e-3
VDIVS = 3401 #0.5 mV steps

#units for calcium concentration: mM
CAMIN = 0.01e-3   #10 nM
CAMAX = 60e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS = 5999 #10 nM steps

#contains all gating parameters and reversal potentials
# Gate equations have the form:
# AlphaBetaChannelParams (specify forward and backward transition rates):
# alpha(v) or beta(v) = (rate + B * v) / (C + exp((v + vhalf) / vslope))
# OR
# StandardMooseTauInfChannelParams (specify steady state and time constants):
# tau(v) or inf(v) = (rate + B * v) / (C + exp((v + vhalf) / vslope))
# OR
# TauInfMinChannelParams (specify steady state and time constants with non-zero minimum - useful for tau):
# inf(v) = min + max / (1 + exp((v + vhalf) / vslope))
# tau(v) = taumin + tauVdep / (1 + exp((v + tauVhalf) / tauVslope))
# or if tau_power=2: tau(v) = taumin + tauVdep / (1 + exp((v + tauVhalf) / tauVslope))* 1 / (1 + exp((v + tauVhalf) / -tauVslope))
#
# where v is membrane potential in volts, vhalf and vslope have units of volts
# C, min and max are dimensionless; and C should be either +1, 0 or -1
# Rate has units of per sec, and B has units of per sec per volt
# taumin and tauVdep have units of per sec

qfactNaF = 2.0

NaF_X_params = AlphaBetaChannelParams(A_rate = -120.0e6*-71.5e-3*qfactNaF,
                                      A_B = -120.0e6*qfactNaF,
                                      A_C = -1,
                                      A_vhalf = -52.5e-3,
                                      A_vslope = -9.5e-3,
                                      B_rate = .36786e3*qfactNaF,
                                      B_B = 0.0,
                                      B_C = 0.0,
                                      B_vhalf = 0.0,
                                      B_vslope = 32.248e-3)

NaF_Y_params = AlphaBetaChannelParams(A_rate=2000,
                                      A_B=0.0,
                                      A_C=1,
                                      A_vhalf=0.067,
                                      A_vslope=0.009,
                                      B_rate=2000,
                                      B_B=0.0,
                                      B_C=1,
                                      B_vhalf=0.027,
                                      B_vslope=-0.015)

NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')

#KDrparam -Kv2
KDrparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KDr')

KDr_X_params = AlphaBetaChannelParams(A_rate=3240.5222892101206,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.049,
 A_vslope=-0.015,
 B_rate=1380.2224565154218,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12,
 B_vslope=0.022)

KDr_Y_params = AlphaBetaChannelParams(A_rate=0.36293714164529783,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.0,
 A_vslope=0.015,
 B_rate=0.36293714164529783,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0,
 B_vslope=-0.015)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')

KvF_X_params = AlphaBetaChannelParams(A_rate=4384.6356204737285,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.022008821162802922,
 A_vslope=-0.026,
 B_rate=4384.6356204737285,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.13999117883719708,
 B_vslope=0.027)

KvF_Y_params = AlphaBetaChannelParams(A_rate=172.36563170867834,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.08500099601792117,
 A_vslope=0.012,
 B_rate=163.1727980175488,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.06000099601792118,
 B_vslope=-0.012)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate=3224.994112398424,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.02035004570131537,
 A_vslope=-0.022,
 B_rate=1273.02399173622,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.10964995429868463,
 B_vslope=0.02)

KvS_Y_params = AlphaBetaChannelParams(A_rate=44.61801775568367,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.08212102001359652,
 A_vslope=0.01,
 B_rate=46.96633447966702,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.06712102001359652,
 B_vslope=-0.012)


qfactKv3132 = 1
Kv3132_X_params = AlphaBetaChannelParams(A_rate = 95e3,
                                         A_B = -1e6,
                                         A_C = -1,
                                         A_vhalf = -75e-3,
                                         A_vslope = -11.8e-3,
                                         B_rate = 0.025e3,
                                         B_B = 0.0,
                                         B_C = 0.0,
                                         B_vhalf = 0.0e-3,
                                         B_vslope = 22.222e-3)


Kv3132param = ChannelSettings(Xpow=2, Ypow=0, Zpow=0, Erev=krev, name='Kv3132')

Ka_X_params = TauInfMinChannelParams(T_min = 1e-3,
                                        T_vdep = 1e-3,
                                        T_vhalf = 0.07,
                                        T_vslope = -0.013,
                                        SS_min = 0,
                                        SS_vdep = 1,
                                        SS_vhalf = -0.045,
                                        SS_vslope = -0.013)

Ka_Y_params = TauInfMinChannelParams(T_min = 0.014,
                                        T_vdep = 0,
                                        T_vhalf = 37.0e-3,
                                        T_vslope = 5.0e-3,
                                        SS_min =  0,
                                        SS_vdep = 1,
                                        SS_vhalf = -0.077,
                                        SS_vslope = 0.008)
Kaparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=carev, name='Ka')

Channels = NamedDict(
    'Channels',
    KvF =   TypicalOneD(KvFparam, KvF_X_params, KvF_Y_params),
    KvS =   TypicalOneD(KvSparam, KvS_X_params, KvS_Y_params),
    NaF =   TypicalOneD(NaFparam, NaF_X_params, NaF_Y_params),
    Kv3132 =   TypicalOneD(Kv3132param, Kv3132_X_params, []),
)
