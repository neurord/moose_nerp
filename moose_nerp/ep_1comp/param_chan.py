# Generated from npzfile: pchan_032717_162938.npz of fit number: 17929

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
Na_m_params = AlphaBetaChannelParams(A_rate=8929.205626365298,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.029425351443600374,
 A_vslope=-0.005,
 B_rate=8929.205626365298,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.029425351443600374,
 B_vslope=0.005)

Na_h_params = AlphaBetaChannelParams(A_rate=2668.1033154895335,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.06443186709257158,
 A_vslope=0.009,
 B_rate=2668.1033154895335,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.02443186709257159,
 B_vslope=-0.005)

NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')

#KDrparam -Kv2
KDrparam = ChannelSettings(Xpow=4, Ypow=0, Zpow=0, Erev=krev, name='KDr')

KDr_X_params = AlphaBetaChannelParams(A_rate=9292.376229755133,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.045109323980938115,
 A_vslope=-0.015,
 B_rate=3957.8639497105196,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12389067601906188,
 B_vslope=0.022)

KDr_Y_params = AlphaBetaChannelParams(A_rate=0.4879010965648323,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.007525309468427759,
 A_vslope=0.015,
 B_rate=0.4879010965648323,
 B_B=0.0,
 B_C=1,
 B_vhalf=-0.007525309468427759,
 B_vslope=-0.015)

Kv3param = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='Kv3')


#qfactKrp=1

Kv3_X_params = AlphaBetaChannelParams(A_rate=3655.2926665441573,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.03394932911992257,
 A_vslope=-0.015,
 B_rate=4971.198026500054,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07705067088007743,
 B_vslope=0.015)

Kv3_Y_params = TauInfMinChannelParams(T_min=0.008715508556105754,
 T_vdep=0.03237188892267851,
 T_vhalf=0.001386908029635936,
 T_vslope=0.01,
 SS_min=0.6,
 SS_vdep=0.4,
 SS_vhalf=-0.018613091970364065,
 SS_vslope=0.01,
 T_power=1)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate=2258.3842471378803,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.022364946423545806,
 A_vslope=-0.026,
 B_rate=2258.3842471378803,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.1396350535764542,
 B_vslope=0.027)

KvF_Y_params = AlphaBetaChannelParams(A_rate=248.47418621427934,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.08500274775572314,
 A_vslope=0.012,
 B_rate=235.22222961618445,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.060002747755723146,
 B_vslope=-0.012)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate=6742.786637193274,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.03579439118561917,
 A_vslope=-0.022,
 B_rate=2661.6263041552397,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.09420560881438084,
 B_vslope=0.02)

KvS_Y_params = AlphaBetaChannelParams(A_rate=25.05565580426304,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.09905901209189559,
 A_vslope=0.01,
 B_rate=26.374374530803202,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.08405901209189559,
 B_vslope=-0.012)

HCN2param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN2')

HCN2_X_params = AlphaBetaChannelParams(A_rate=20.202189212087497,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.12604427441917815,
 A_vslope=0.01,
 B_rate=13.468126141391664,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.006044274419178137,
 B_vslope=-0.012)
HCN2_Y_params=[]

Channels = NamedDict(
    'Channels',
    KDr =   TypicalOneD(KDrparam, KDr_X_params, KDr_Y_params),
    Kv3 =   TypicalOneD(Kv3param, Kv3_X_params, Kv3_Y_params),
    KvF =   TypicalOneD(KvFparam, KvF_X_params, KvF_Y_params),
    KvS =   TypicalOneD(KvSparam, KvS_X_params, KvS_Y_params),
    HCN2 =  TypicalOneD(HCN2param,HCN2_X_params, []),
    NaF =   TypicalOneD(NaFparam, Na_m_params, Na_h_params),
)

