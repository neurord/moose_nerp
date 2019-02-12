# Generated from npzfile: fitep-ep-pchan_032717_162938.npz of fit number: 5722

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
Na_m_params = AlphaBetaChannelParams(A_rate=8140.361657046223,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.026248242342406997,
 A_vslope=-0.005,
 B_rate=8140.361657046223,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.026248242342406997,
 B_vslope=0.005)

Na_h_params = AlphaBetaChannelParams(A_rate=2035.0904142615557,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.062248242342406994,
 A_vslope=0.009,
 B_rate=2035.0904142615557,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.022248242342407,
 B_vslope=-0.005)
'''
Na_s_params= AlphaBetaChannelParams(A_rate = 100,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = 84e-3,
                                      A_vslope = 10.0e-3,
                                      B_rate = 80,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = -26e-3,
                                      B_vslope = -14e-3)
'''
Na_s_params = TauInfMinChannelParams(T_min=0.25438630178269445,
 T_vdep=1.1192997278438557,
 T_vhalf=-0.041751757657593,
 T_vslope=0.012,
 SS_min=0.15,
 SS_vdep=0.85,
 SS_vhalf=-0.054751757657593,
 SS_vslope=0.0054,
 T_power=1)

NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')


#persistent Na_channel.  Slow down from Dieter Jaeger
'''
NaS_m_params = AlphaBetaChannelParams(A_rate=76e3,
                                     A_B=0,
                                     A_C=1,
                                     A_vhalf=-55.4e-3,
                                     A_vslope=-13.6e-3,
                                    B_rate=70e3,
                                     B_B=0.0,
                                     B_C=1,
                                     B_vhalf=135e-3,
                                     B_vslope=13.5e-3)
'''
NaS_m_params = AlphaBetaChannelParams(A_rate=15208.162754202816,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.06461130189662245,
 A_vslope=-0.027,
 B_rate=15208.162754202816,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12578869810337756,
 B_vslope=0.0262)

NaS_h_params = AlphaBetaChannelParams(A_rate=19.466448325379606,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.048788698103377555,
 A_vslope=0.0045,
 B_rate=18.24979530504338,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.047788698103377554,
 B_vslope=-0.004)

NaS_s_params = AlphaBetaChannelParams(A_rate=-0.08942399699471255,
 A_B=-5.2559410478524935,
 A_C=1,
 A_vhalf=0.007788698103377553,
 A_vslope=0.00463,
 B_rate=0.8157658501354391,
 B_B=12.665357941700107,
 B_C=1,
 B_vhalf=0.05518869810337755,
 B_vslope=-0.00263)
'''
NaS_s_params = TauInfMinChannelParams(SS_min = 0,
                                         SS_vdep = 1,
                                         SS_vhalf = -0.010,
                                         SS_vslope = 0.0049,
                                         T_min = 0.5,
                                         T_vdep = 8,
                                         T_vhalf = -0.066,
                                         T_vslope = -0.016,
                                         T_power=2)
'''
NaSparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaP')

#KDrparam -Kv2
KDrparam = ChannelSettings(Xpow=4, Ypow=0, Zpow=0, Erev=krev, name='KDr')

KDr_X_params = AlphaBetaChannelParams(A_rate=5400.0,
 A_B=0,
 A_C=1,
 A_vhalf=-0.049,
 A_vslope=-0.015,
 B_rate=2300.0,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12,
 B_vslope=0.022)

KDr_Y_params = AlphaBetaChannelParams(A_rate=0.292,
 A_B=0,
 A_C=1,
 A_vhalf=0.0,
 A_vslope=0.015,
 B_rate=0.292,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0,
 B_vslope=-0.015)

Kv3param = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='Kv3')


#qfactKrp=1

Kv3_X_params = AlphaBetaChannelParams(A_rate=2147.69613336688,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.039463554920227496,
 A_vslope=-0.015,
 B_rate=2920.8667413789567,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0715364450797725,
 B_vslope=0.015)

Kv3_Y_params = TauInfMinChannelParams(T_min=0.00375846823339204,
 T_vdep=0.01396002486688472,
 T_vhalf=-0.006463554920227495,
 T_vslope=0.01,
 SS_min=0.6,
 SS_vdep=0.4,
 SS_vhalf=-0.026463554920227495,
 SS_vslope=0.01,
 T_power=1)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate=4196.416547477543,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.0237961937262095,
 A_vslope=-0.026,
 B_rate=4196.416547477543,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.1382038062737905,
 B_vslope=0.027)

KvF_Y_params = AlphaBetaChannelParams(A_rate=209.8208273738771,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.1032038062737905,
 A_vslope=0.012,
 B_rate=198.63038324727034,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0782038062737905,
 B_vslope=-0.012)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate=5221.191942369082,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.033867001054492044,
 A_vslope=-0.022,
 B_rate=2060.9968193562167,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.09613299894550796,
 B_vslope=0.02)

KvS_Y_params = AlphaBetaChannelParams(A_rate=26.10595971184541,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.08813299894550795,
 A_vslope=0.01,
 B_rate=27.479957591416223,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07313299894550795,
 B_vslope=-0.012)



HCN1param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN1')

HCN1_X_params = AlphaBetaChannelParams(A_rate=65.79336205346931,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.15182309819939113,
 A_vslope=0.01,
 B_rate=28.5104568898367,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.031823098199391144,
 B_vslope=-0.012)
HCN1_Y_params=[]

HCN2param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN2')

HCN2_X_params = AlphaBetaChannelParams(A_rate=9.841639179079088,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.12904595813026373,
 A_vslope=0.01,
 B_rate=6.5610927860527255,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.009045958130263711,
 B_vslope=-0.012)
HCN2_Y_params=[]

#Caparam - D.James Surmeier, ( tau and ss)
Caparam=ChannelSettings(Xpow=1 , Ypow=0 , Zpow=0, Erev=carev , name='Ca')
Ca_X_params = AlphaBetaChannelParams(A_rate=147272.72742,
 A_B=-2727272.73,
 A_C=-1,
 A_vhalf=-0.054,
 A_vslope=-0.011,
 B_rate=450,
 B_B=0,
 B_C=1,
 B_vhalf=0.025,
 B_vslope=0.013)
Ca_Y_params=[]

SKparam= ChannelSettings(Xpow=0, Ypow=0, Zpow=1, Erev=krev, name='SKCa')

SK_Z_params = ZChannelParams(Kd=0.00035,
 power=4.6,
 tau=0.002,
 taumax=0.0037928,
 tau_power=4.3,
 cahalf=0.002703)
#BK channel
BKparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='BKCa')

BK_X_params=[BKChannelParams(alphabeta=480, K=0.18, delta=-0.84),
BKChannelParams(alphabeta=280, K=0.011, delta=-1.0)]

Channels = NamedDict(
    'Channels',
    KDr =   TypicalOneD(KDrparam, KDr_X_params, KDr_Y_params),
    Kv3 =   TypicalOneD(Kv3param, Kv3_X_params, Kv3_Y_params),
    KvF =   TypicalOneD(KvFparam, KvF_X_params, KvF_Y_params),
    KvS =   TypicalOneD(KvSparam, KvS_X_params, KvS_Y_params),
    HCN1 =  TypicalOneD(HCN1param,HCN1_X_params, []),
    HCN2 =  TypicalOneD(HCN2param,HCN2_X_params, []),
    NaF =   TypicalOneD(NaFparam, Na_m_params, Na_h_params,Na_s_params),
    NaS= TypicalOneD(NaSparam,NaS_m_params,NaS_h_params,NaS_s_params),
    Ca =   TypicalOneD(Caparam,Ca_X_params, [],[], calciumPermeable=True),
    SKCa=  TypicalOneD(SKparam, [], [], SK_Z_params , calciumDependent=True),
    BKCa=TwoD(BKparam, BK_X_params, calciumDependent=True),
)

