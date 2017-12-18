

from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes.chan_proto import (
    SSTauQuadraticChannelParams,
    AlphaBetaChannelParams,
    StandardMooseTauInfChannelParams,
    TauInfMinChannelParams,
    ZChannelParams,
    BKChannelParams,
    ChannelSettings,
    TypicalOneD,
    TwoD)


krev=-90e-3
narev=50e-3
carev=130e-3
hcnrev=-30e-3
ZpowCDI=2

VMIN = -120e-3
VMAX = 50e-3
VDIVS = 3401 #0.5 mV steps

CAMIN = 0.01e-3   #10 nM
CAMAX = 60e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS = 5999 #10 nM steps

#contains all gating parameters and reversal potentials
# Gate equations have the form:
# AlphaBetaChannelParams (specify forward and backward transition rates):
# alpha(v) or beta(v) = (rate + B * v) / (C + exp((v + vhalf) / vslope))

#Fast sodium - same as GP, but no slow gating
qfactNaF = 1.0

#These values were too fast - change rate from 35e3 to 12e3
Na_m_params = AlphaBetaChannelParams(A_rate = 8e3,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = 36e-3,
                                      A_vslope = -5e-3,
                                      B_rate = 8e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 36e-3,
                                      B_vslope = 5e-3)

Na_h_params = AlphaBetaChannelParams(A_rate = 4500,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = 70e-3,
                                      A_vslope = 9e-3,
                                      B_rate = 3000,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 32e-3,
                                      B_vslope = -5e-3)

#Zgate not working
Na_s_params= AlphaBetaChannelParams(A_rate = 100,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = 84e-3,
                                      A_vslope = 10.0e-3,
                                      B_rate = 0.0080,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = -26e-3,
                                      B_vslope = -14e-3)

Na_s_params= SSTauQuadraticChannelParams(SS_min=0.99,  
                                         SS_vdep=0.01,  
                                         SS_vhalf=-0.045,
                                         SS_vslope=0.0054,
                                         taumin = 0.01,
                                         tauVdep = 2.2,
                                         tauVhalf = -0.032,
                                         tauVslope = 0.012)
                                        
NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')


#persistent Na_channel- same as GP, but no slow gating
#Two changes made recently: slow down activation (still < 1 ms), less steep vdep of inactivation
NaS_m_params = AlphaBetaChannelParams(A_rate=25e3,
                                     A_B=0,
                                     A_C=1,
                                     A_vhalf=-55.4e-3,
                                     A_vslope=-27e-3,
                                     B_rate=25e3,
                                     B_B=0.0,
                                     B_C=1,
                                     B_vhalf=135e-3,
                                     B_vslope=26.2e-3)

NaS_h_params = SSTauQuadraticChannelParams(SS_min = 0.154,
                                           SS_vdep = 0.846,
                                           SS_vhalf = -0.057,
                                           SS_vslope = 0.004,
                                           taumin = 0.03,
                                           tauVdep = 0.015,
                                           tauVhalf = -0.03,
                                           tauVslope = 0.022)

NaS_h_params = AlphaBetaChannelParams(A_rate=32,
                                      A_B=0,
                                      A_C=1,
                                      A_vhalf=58e-3,
                                      A_vslope=10e-3,
                                      B_rate=30,
                                      B_B=0.0,
                                      B_C=1,
                                      B_vhalf=57e-3,
                                      B_vslope=-10e-3)

NaSparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaP')

#KDrparam -Kv2
KDrparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KDr')

KDr_X_params = AlphaBetaChannelParams(A_rate = 5.4e3,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = -49e-3,
                                      A_vslope = -15e-3,
                                      B_rate = 2.3e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 120e-3,
                                      B_vslope = 22e-3)

KDr_Y_params = AlphaBetaChannelParams(A_rate = 0.292,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = 0e-3,
                                      A_vslope = 15e-3,
                                      B_rate = 0.292,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 0e-3,
                                      B_vslope = -15e-3)

Kv3param = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='Kv3')


#qfactKrp=1
#Slightly faster to match DJ tau at hyperpol potentials
Kv3_X_params = AlphaBetaChannelParams(A_rate = 4000,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = -33e-3,
                                      A_vslope =-15e-3,
                                      B_rate = 5440,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 78e-3,
                                      B_vslope = 15e-3)

#Use SSTau Quadratic to better match minimal inactivation of this channel
Kv3_Y_params =  TauInfMinChannelParams(SS_min = 0.6,
                                 SS_vdep = 0.4,
                                 SS_vhalf = -20e-3,
                                 SS_vslope = 10e-3,
                                 T_min = 0.007,
                                 T_vdep = 0.026,
                                 T_vhalf = 0e-3,
                                 T_vslope = 10e-3)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate = 3e3,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = -32e-3,
                                      A_vslope = -26.0e-3,
                                      B_rate = 3e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 130e-3,
                                      B_vslope = 27e-3)

KvF_Y_params= AlphaBetaChannelParams(A_rate = 150,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = 95e-3,
                                      A_vslope = 12e-3,
                                      B_rate = 142,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 70e-3,
                                      B_vslope = -12e-3)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate =3.8e3,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = -30e-3,
                                      A_vslope = -22.0e-3,
                                      B_rate = 1.5e3,
                                      B_B = 0,
                                      B_C = 1,
                                      B_vhalf = 100e-3,
                                      B_vslope = 20e-3)

KvS_Y_params = AlphaBetaChannelParams(A_rate =19 ,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf =92e-3 ,
                                      A_vslope =10e-3,
                                      B_rate = 20,
                                      B_B = 0,
                                      B_C = 1,
                                      B_vhalf =77e-3 ,
                                      B_vslope = -12e-3)

#less steep voltage dependence than than GP channel
HCN1param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN1')

#previous values were too fast
HCN1_X_params = AlphaBetaChannelParams(A_rate = 120,
                                        A_B = 0,
                                        A_C = 1,
                                        A_vhalf = 0.15,
                                        A_vslope = 0.01,
                                        B_rate = 52,
                                        B_B = 0,
                                        B_C = 1,
                                        B_vhalf = 0.03,
                                        B_vslope = -0.012)
HCN1_Y_params=[]

HCN2param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN2')

HCN2_X_params = AlphaBetaChannelParams(A_rate = 12,
                                        A_B = 0,
                                        A_C = 1,
                                        A_vhalf = 0.15,
                                        A_vslope = 0.01,
                                        B_rate = 8,
                                        B_B = 0,
                                        B_C = 1,
                                        B_vhalf = 0.03,
                                        B_vslope = -0.012)
HCN2_Y_params=[]

#Caparam - D.James Surmeier, ( tau and ss)
Caparam=ChannelSettings(Xpow=1 , Ypow=0 , Zpow=0, Erev=carev , name='Ca')
Ca_X_params=AlphaBetaChannelParams(A_rate = 147272.7273,
                                        A_B = -2727272.73,
                                        A_C = -1,
                                        A_vhalf = -54e-3,
                                        A_vslope = -11e-3,
                                        B_rate = 450,
                                        B_B = 0,
                                        B_C = 1,
                                        B_vhalf = 25e-3,
                                        B_vslope = 13e-3)
Ca_Y_params=[]

SKparam= ChannelSettings(Xpow=0, Ypow=0, Zpow=1, Erev=krev, name='SKCa')

SK_Z_params= ZChannelParams(Kd=0.00035,
                            power=4.6,
                            tau=0.002,
                            taumax=0.0037928,
                            tau_power=4.3,
                            cahalf=0.002703
                             )
#BK channel
BKparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='BKCa')

BK_X_params=[BKChannelParams(alphabeta=480, K=0.18, delta=-0.84),
BKChannelParams(alphabeta=280, K=0.011, delta=-1.0)]
Channels = NamedDict(
    'Channels',
    KDr =   TypicalOneD(KDrparam, KDr_X_params, KDr_Y_params),
    Kv3 =   TypicalOneD(Kv3param, Kv3_X_params, Kv3_Y_params),
    #KvF =   TypicalOneD(KvFparam, KvF_X_params, KvF_Y_params),
    KvS =   TypicalOneD(KvSparam, KvS_X_params, KvS_Y_params),
    HCN1 =  TypicalOneD(HCN1param,HCN1_X_params, []),
    HCN2 =  TypicalOneD(HCN2param,HCN2_X_params, []),
    NaF =   TypicalOneD(NaFparam, Na_m_params, Na_h_params, Na_s_params),
    NaS= TypicalOneD(NaSparam,NaS_m_params,NaS_h_params),
    Ca =   TypicalOneD(Caparam,Ca_X_params, [],[], calciumPermeable=True),
    SKCa=  TypicalOneD(SKparam, [], [], SK_Z_params , calciumDependent=True),
    BKCa=TwoD(BKparam, BK_X_params, calciumDependent=True),
)
# have to add NaP and calcium channels
