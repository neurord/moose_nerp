# -*- coding: utf-8 -*-

from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes.chan_proto import (
    AlphaBetaChannelParams,
    StandardMooseTauInfChannelParams,
    TauInfMinChannelParams,
    ZChannelParams,
    BKChannelParams,
    ChannelSettings,
    TypicalOneD,
    TwoD,
    )

#contains all gating parameters and reversal potentials
# Gate equations have the form:
# AlphaBetaChannelParams (specify forward and backward transition rates):
# alpha(v) or beta(v) = (rate + B * v) / (C + exp((v + vhalf) / vslope))
# OR
# StandardMooseTauInfChannelParams (specify steady state and time constants):
# tau(v) or inf(v) = (rate + B * v) / (C + exp((v + vhalf) / vslope))
# OR
# TauInfMinChannelParams (specify steady state and time constants with non-zero minimum - useful for tau):
# inf(v) = min + max / (1 + exp((v - vhalf) / vslope))
# tau(v) = taumin + tauVdep / (1 + exp((v - tauVhalf) / tauVslope))
# or if tau_power=2: tau(v) = taumin + tauVdep / (1 + exp((v - tauVhalf) / tauVslope))* 1 / (1 + exp((v - tauVhalf) / -tauVslope))
#
# where v is membrane potential in volts, vhalf and vslope have units of volts
# C, min and max are dimensionless; and C should be either +1, 0 or -1
# Rate has units of per sec, and B has units of per sec per volt
# taumin and tauVdep have units of per sec
#

#units for membrane potential: volts
krev=-90e-3
narev=50e-3
carev=140e-3 #assumes CaExt=2 mM and CaIn=50e-3
ZpowCDI=2

VMIN = -120e-3
VMAX = 50e-3
VDIVS = 3401 #0.5 mV steps

#units for calcium concentration: mM
CAMIN = 0.01e-3   #10 nM
CAMAX = 40e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS = 4001 #10 nM steps

###### All channels from Kotaleski & Blackwell FSI model

qfactNaF = 1
NaF_X_params = AlphaBetaChannelParams(A_rate = 3020e3,
                                      A_B = -40.0e6,
                                      A_C = -1,
                                      A_vhalf = -75.5e-3,
                                      A_vslope = -13.5e-3,
                                      B_rate = 1.2262e3,
                                      B_B = 0.0,
                                      B_C = 0.0,
                                      B_vhalf = 0.0,
                                      B_vslope = 42.248e-3)

NaF_Y_params = AlphaBetaChannelParams(A_rate = 0.0035e3,
                                      A_B = 0.0,
                                      A_C = 0.0,
                                      A_vhalf = 0.0,
                                      A_vslope = 24.186e-3,
                                      B_rate = -0.017e6*51.25e-3,
                                      B_B = -0.017e6,
                                      B_C = -1.0,
                                      B_vhalf = 51.25e-3, 
                                      B_vslope = -5.2e-3)

NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')


qfactKv3132 = 1
Kv3132_X_params = AlphaBetaChannelParams(A_rate = 95e3,
                                         A_B = -1e6,
                                         A_C = -1,
                                         A_vhalf = -95e-3,
                                         A_vslope = -11.8e-3,
                                         B_rate = 0.025e3,
                                         B_B = 0.0,
                                         B_C = 0.0,
                                         B_vhalf = 0.0e-3,
                                         B_vslope = 22.222e-3)


Kv3132param = ChannelSettings(Xpow=2, Ypow=0, Zpow=0, Erev=krev, name='Kv3132')

qfactKv13 = 1 
Kv13_X_params = AlphaBetaChannelParams(A_rate = -0.616e3, #per msec, e3 converts to per sec
                                       A_B = -0.014e6,  #per msec/mV e3 converts to per sec,e3 converts to per V
                                       A_C = -1,
                                       A_vhalf = 44e-3,
                                       A_vslope = -2.3e-3,
                                       B_rate = 0.0043e3,
                                       B_B = 0,
                                       B_C = 0,
                                       B_vhalf = 44e-3,
                                       B_vslope = 34e-3)

Kv13param = ChannelSettings(Xpow=4, Ypow=0, Zpow=0, Erev=krev, name='Kv13')

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

#Dictionary of "standard" channels, to create channels using a loop
#NaF doesn't fit since it uses different prototype form
#will need separate dictionary for BK

Channels = NamedDict(
    'Channels',
    Ka =   TypicalOneD(Kaparam, Ka_X_params, Ka_Y_params),
    Kv13 =   TypicalOneD(Kv13param, Kv13_X_params, []),
    Kv3132 =   TypicalOneD(Kv3132param, Kv3132_X_params, []),
    NaF =   TypicalOneD(NaFparam, NaF_X_params, NaF_Y_params),
)
