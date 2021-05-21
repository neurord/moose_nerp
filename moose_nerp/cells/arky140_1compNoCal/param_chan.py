# Generated from npzfile: fitgp_1comp-arky-cmaes_arky140_84362_8noCal.npz of fit number: 4986
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

qfactNaF = 1.0

#These values were too fast - change rate from 35e3 to 16e3
Na_m_params = AlphaBetaChannelParams(A_rate=37792.709096491206,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.03533635901010369,
 A_vslope=-0.005,
 B_rate=37792.709096491206,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.03533635901010369,
 B_vslope=0.005)

Na_h_params = AlphaBetaChannelParams(A_rate=5654.606181605965,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.07689738878303974,
 A_vslope=0.009,
 B_rate=5654.606181605965,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.03689738878303973,
 B_vslope=-0.005)


NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')


#KDrparam -Kv2
KDrparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KDr')

KDr_X_params = AlphaBetaChannelParams(A_rate=9195.853786397276,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.049,
 A_vslope=-0.015,
 B_rate=3916.752538650692,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12,
 B_vslope=0.022)

KDr_Y_params = AlphaBetaChannelParams(A_rate=0.336638662429464,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.0,
 A_vslope=0.015,
 B_rate=0.336638662429464,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0,
 B_vslope=-0.015)

Kv3param = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='Kv3')


#qfactKrp=1

Kv3_X_params = AlphaBetaChannelParams(A_rate=3189.410941127774,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.03776099637932748,
 A_vslope=-0.015,
 B_rate=4337.598879933773,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07323900362067252,
 B_vslope=0.015)

Kv3_Y_params = TauInfMinChannelParams(T_min=0.008738675971393061,
 T_vdep=0.03245793932231708,
 T_vhalf=-0.005683681756781953,
 T_vslope=0.01,
 SS_min=0.6,
 SS_vdep=0.4,
 SS_vhalf=-0.025683681756781953,
 SS_vslope=0.01,
 T_power=1)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate=3261.161091702947,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.022018415451993303,
 A_vslope=-0.026,
 B_rate=3261.161091702947,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.1399815845480067,
 B_vslope=0.027)

KvF_Y_params = AlphaBetaChannelParams(A_rate=93.78840235406865,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.10448225544431078,
 A_vslope=0.012,
 B_rate=88.78635422851832,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07948225544431078,
 B_vslope=-0.012)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate=6843.080620992109,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.022558106128296576,
 A_vslope=-0.022,
 B_rate=2701.2160346021483,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.10744189387170343,
 B_vslope=0.02)

KvS_Y_params = AlphaBetaChannelParams(A_rate=24.177663548465556,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.09660703334718929,
 A_vslope=0.01,
 B_rate=25.450172156279535,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.08160703334718929,
 B_vslope=-0.012)


HCN1param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN1')

HCN1_X_params = AlphaBetaChannelParams(A_rate=120,
 A_B=0,
 A_C=1,
 A_vhalf=0.15,
 A_vslope=0.01,
 B_rate=52,
 B_B=0,
 B_C=1,
 B_vhalf=0.03,
 B_vslope=-0.012)
HCN1_Y_params=[]

HCN2param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN2')

HCN2_X_params = AlphaBetaChannelParams(A_rate=15.999743754866419,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.11511403364190007,
 A_vslope=0.01,
 B_rate=10.666495836577612,
 B_B=0.0,
 B_C=1,
 B_vhalf=-0.004885966358099944,
 B_vslope=-0.012)
HCN2_Y_params=[]

Channels = NamedDict(
    'Channels',
    KDr =   TypicalOneD(KDrparam, KDr_X_params, KDr_Y_params),
    Kv3 =   TypicalOneD(Kv3param, Kv3_X_params, Kv3_Y_params),
    KvF =   TypicalOneD(KvFparam, KvF_X_params, KvF_Y_params),
    KvS =   TypicalOneD(KvSparam, KvS_X_params, KvS_Y_params),
    HCN1 =  TypicalOneD(HCN1param,HCN1_X_params, []),
    HCN2 =  TypicalOneD(HCN2param,HCN2_X_params, []),
    NaF =   TypicalOneD(NaFparam, Na_m_params, Na_h_params),
)
