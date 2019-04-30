# Generated from npzfile: pchan_032117_162938.npz of fit number: 8080

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
Na_m_params = AlphaBetaChannelParams(A_rate=17191.515248231462,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.032543629783614365,
 A_vslope=-0.005,
 B_rate=17191.515248231462,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.032543629783614365,
 B_vslope=0.005)

Na_h_params = AlphaBetaChannelParams(A_rate=2000.0011080946113,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.06964827061745116,
 A_vslope=0.009,
 B_rate=2000.0011080946113,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.029648270617451164,
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
Na_s_params = TauInfMinChannelParams(T_min=0.5,
 T_vdep=2.2,
 T_vhalf=-0.032,
 T_vslope=0.012,
 SS_min=0.15,
 SS_vdep=0.85,
 SS_vhalf=-0.045,
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
NaS_m_params = AlphaBetaChannelParams(A_rate=30874.92399256788,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.0636836971406017,
 A_vslope=-0.027,
 B_rate=30874.92399256788,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.1267163028593983,
 B_vslope=0.0262)

NaS_h_params = AlphaBetaChannelParams(A_rate=62.54774162319001,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.06741148846466145,
 A_vslope=0.0045,
 B_rate=58.638507771740635,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.06641148846466145,
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
KDrparam = ChannelSettings(Xpow=4, Ypow=0, Zpow=0, Erev=krev, name='KDr')

KDr_X_params = AlphaBetaChannelParams(A_rate=3371.1851278864888,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.04024381829372494,
 A_vslope=-0.015,
 B_rate=1435.8751470627637,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12875618170627506,
 B_vslope=0.022)

KDr_Y_params = AlphaBetaChannelParams(A_rate=0.35922698129532715,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.00044955649988733806,
 A_vslope=0.015,
 B_rate=0.35922698129532715,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.00044955649988733806,
 B_vslope=-0.015)

Kv3param = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='Kv3')


#qfactKrp=1

Kv3_X_params = AlphaBetaChannelParams(A_rate=2669.274113926997,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.027871377217813725,
 A_vslope=-0.015,
 B_rate=3630.212794940716,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.08312862278218627,
 B_vslope=0.015)

Kv3_Y_params = TauInfMinChannelParams(T_min=0.010460284049302515,
 T_vdep=0.03885248361169505,
 T_vhalf=-0.0099862376569078,
 T_vslope=0.01,
 SS_min=0.6,
 SS_vdep=0.4,
 SS_vhalf=-0.029986237656907798,
 SS_vslope=0.01,
 T_power=1)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate=1977.5074215666145,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.029094483674203194,
 A_vslope=-0.026,
 B_rate=1977.5074215666145,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.1329055163257968,
 B_vslope=0.027)

KvF_Y_params = AlphaBetaChannelParams(A_rate=178.59771511203988,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.10342198212722103,
 A_vslope=0.012,
 B_rate=169.07250363939775,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07842198212722104,
 B_vslope=-0.012)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate=4457.958167964498,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.03928285483746839,
 A_vslope=-0.022,
 B_rate=1759.7203294596704,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.09071714516253161,
 B_vslope=0.02)

KvS_Y_params = AlphaBetaChannelParams(A_rate=34.19309467144274,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.09640163479923668,
 A_vslope=0.01,
 B_rate=35.99273123309762,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.08140163479923668,
 B_vslope=-0.012)



HCN1param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN1')

HCN1_X_params = AlphaBetaChannelParams(A_rate=120.6949524564979,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.1431017070158994,
 A_vslope=0.01,
 B_rate=52.301146064482424,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0231017070158994,
 B_vslope=-0.012)
HCN1_Y_params=[]

HCN2param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN2')

HCN2_X_params = AlphaBetaChannelParams(A_rate=6.634849628827391,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.14496255806298924,
 A_vslope=0.01,
 B_rate=4.423233085884927,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.02496255806298924,
 B_vslope=-0.012)
HCN2_Y_params=[]

#Caparam - D.James Surmeier, ( tau and ss)
#decreases the Ca rates to help prevent instability
Caparam=ChannelSettings(Xpow=1 , Ypow=0 , Zpow=0, Erev=carev , name='Ca')
Ca_X_params = AlphaBetaChannelParams(A_rate= 45000,
                                     A_B=45000/-54e-3,#2727272.73,
 A_C=-1,
 A_vhalf=-0.054,
 A_vslope=-0.012,
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

