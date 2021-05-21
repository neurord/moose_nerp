# Generated from npzfile: fitgp-proto-cmaes_proto144_84362_24.npz of fit number: 6398

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
Na_m_params = AlphaBetaChannelParams(A_rate=31948.819333513035,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.04093678397741053,
 A_vslope=-0.005,
 B_rate=31948.819333513035,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.04093678397741053,
 B_vslope=0.005)

Na_h_params = AlphaBetaChannelParams(A_rate=7802.64405700474,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.07985022729172757,
 A_vslope=0.009,
 B_rate=7802.64405700474,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.03985022729172758,
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
Na_s_params = TauInfMinChannelParams(T_min=0.01,
 T_vdep=2.2,
 T_vhalf=-0.032,
 T_vslope=0.012,
 SS_min=0.15,
 SS_vdep=0.85,
 SS_vhalf=-0.045,
 SS_vslope=0.0054,
 T_power=2)

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
NaS_m_params = AlphaBetaChannelParams(A_rate=31601.715060988732,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.052146656803080046,
 A_vslope=-0.027,
 B_rate=31601.715060988732,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.13825334319691995,
 B_vslope=0.0262)

NaS_h_params = AlphaBetaChannelParams(A_rate=32.54223258177678,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.0631629717353271,
 A_vslope=0.0045,
 B_rate=30.50834304541573,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0621629717353271,
 B_vslope=-0.004)

NaS_s_params = AlphaBetaChannelParams(A_rate=-0.147,
 A_B=-8.64,
 A_C=1,
 A_vhalf=0.017,
 A_vslope=0.00463,
 B_rate=1.341,
 B_B=20.82,
 B_C=1,
 B_vhalf=0.0644,
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
KDrparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KDr')

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

Kv3_X_params = AlphaBetaChannelParams(A_rate=7750.6538515492575,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.023509079685596013,
 A_vslope=-0.015,
 B_rate=10540.88923810699,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.08749092031440399,
 B_vslope=0.015)

Kv3_Y_params = TauInfMinChannelParams(T_min=0.008468330722169971,
 T_vdep=0.031453799825202744,
 T_vhalf=0.004954664861122766,
 T_vslope=0.01,
 SS_min=0.6,
 SS_vdep=0.4,
 SS_vhalf=-0.015045335138877234,
 SS_vslope=0.01,
 T_power=1)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate=1987.473114677305,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.023098281620822204,
 A_vslope=-0.026,
 B_rate=1987.473114677305,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.1389017183791778,
 B_vslope=0.027)

KvF_Y_params = AlphaBetaChannelParams(A_rate=155.0707887644478,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.09635551277668221,
 A_vslope=0.012,
 B_rate=146.80034669701058,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07135551277668221,
 B_vslope=-0.012)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate=3367.673776159523,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.03946827653641401,
 A_vslope=-0.022,
 B_rate=1329.3449116419172,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.090531723463586,
 B_vslope=0.02)

KvS_Y_params = AlphaBetaChannelParams(A_rate=16.884216266285712,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.08429372843832385,
 A_vslope=0.01,
 B_rate=17.772859227669173,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.06929372843832385,
 B_vslope=-0.012)


KCNQparam =  ChannelSettings(Xpow=4, Ypow=0, Zpow=0, Erev=krev, name='KCNQ')

KCNQ_X_params = AlphaBetaChannelParams(A_rate=195,
 A_B=0,
 A_C=1,
 A_vhalf=-0.039,
 A_vslope=-0.0295,
 B_rate=120,
 B_B=0,
 B_C=1,
 B_vhalf=0.128,
 B_vslope=0.032)

KCNQ_Y_params = []



HCN1param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN1')

HCN1_X_params = AlphaBetaChannelParams(A_rate=118.45847831517291,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.1475322548760142,
 A_vslope=0.01,
 B_rate=51.33200726990826,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.027532254876014208,
 B_vslope=-0.012)
HCN1_Y_params=[]

HCN2param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN2')

HCN2_X_params = AlphaBetaChannelParams(A_rate=16.723217843530193,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.14257308786463516,
 A_vslope=0.01,
 B_rate=11.148811895686794,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.022573087864635154,
 B_vslope=-0.012)
HCN2_Y_params=[]

#Caparam - D.James Surmeier, ( tau and ss)
Caparam=ChannelSettings(Xpow=1 , Ypow=0 , Zpow=0, Erev=carev , name='Ca')
Ca_X_params = AlphaBetaChannelParams(A_rate=383222.88539317786,
 A_B=-5282904.210855806,
 A_C=-1,
 A_vhalf=-0.07254019192808675,
 A_vslope=-0.011,
 B_rate=871.6791939195289,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.006459808071913251,
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
    KCNQ =  TypicalOneD(KCNQparam,KCNQ_X_params, []),
    NaF =   TypicalOneD(NaFparam, Na_m_params, Na_h_params,Na_s_params),
    NaS= TypicalOneD(NaSparam,NaS_m_params,NaS_h_params,NaS_s_params),
    Ca =   TypicalOneD(Caparam,Ca_X_params, [],[], calciumPermeable=True),
    SKCa=  TypicalOneD(SKparam, [], [], SK_Z_params , calciumDependent=True),
    BKCa=TwoD(BKparam, BK_X_params, calciumDependent=True),
)
# have to add NaP and calcium channels
