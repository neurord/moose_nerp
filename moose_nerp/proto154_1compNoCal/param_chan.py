# Generated from npzfile: fitgp_1comp-proto-cmaes_proto154_84362_8noCal.npz of fit number: 8151
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
Na_m_params = AlphaBetaChannelParams(A_rate=74805.13121562618,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.03185275093333961,
 A_vslope=-0.005,
 B_rate=74805.13121562618,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.03185275093333961,
 B_vslope=0.005)

Na_h_params = AlphaBetaChannelParams(A_rate=8892.34887056553,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.07005373487255172,
 A_vslope=0.009,
 B_rate=8892.34887056553,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.030053734872551714,
 B_vslope=-0.005)


NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')


#KDrparam -Kv2
KDrparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KDr')

KDr_X_params = AlphaBetaChannelParams(A_rate=3833.132552015514,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.049,
 A_vslope=-0.015,
 B_rate=1632.6305314140154,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12,
 B_vslope=0.022)

KDr_Y_params = AlphaBetaChannelParams(A_rate=0.5480082299209672,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.0,
 A_vslope=0.015,
 B_rate=0.5480082299209672,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0,
 B_vslope=-0.015)

Kv3param = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='Kv3')


#qfactKrp=1

Kv3_X_params = AlphaBetaChannelParams(A_rate=6562.550002507868,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.026020030073901267,
 A_vslope=-0.015,
 B_rate=8925.0680034107,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.08497996992609873,
 B_vslope=0.015)

Kv3_Y_params = TauInfMinChannelParams(T_min=0.005508571871081583,
 T_vdep=0.020460409806874448,
 T_vhalf=-0.01282016812665924,
 T_vslope=0.01,
 SS_min=0.6,
 SS_vdep=0.4,
 SS_vhalf=-0.032820168126659235,
 SS_vslope=0.01,
 T_power=1)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate=2929.086037975104,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.03862764078731916,
 A_vslope=-0.026,
 B_rate=2929.086037975104,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12337235921268083,
 B_vslope=0.027)

KvF_Y_params = AlphaBetaChannelParams(A_rate=301.39952903992446,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.10821215831723578,
 A_vslope=0.012,
 B_rate=285.32488749112844,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.08321215831723579,
 B_vslope=-0.012)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate=9618.035146074442,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.013842103592046014,
 A_vslope=-0.022,
 B_rate=3796.5928208188584,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.11615789640795399,
 B_vslope=0.02)

KvS_Y_params = AlphaBetaChannelParams(A_rate=23.896341554302662,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.09492956187793512,
 A_vslope=0.01,
 B_rate=25.154043741371225,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07992956187793512,
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

HCN2_X_params = AlphaBetaChannelParams(A_rate=10.872436855994172,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.0775131813908781,
 A_vslope=0.01,
 B_rate=7.248291237329447,
 B_B=0.0,
 B_C=1,
 B_vhalf=-0.0424868186091219,
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
