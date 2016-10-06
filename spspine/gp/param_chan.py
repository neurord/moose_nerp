

from spspine.util import NamedDict
from spspine.chan_proto import (
    SSTauChannelParams,
    AlphaBetaChannelParams,
    ZChannelParams,
    BKChannelParams,
    ChannelSettings,
    TypicalOneDalpha,
    AtypicalOneD,
    TwoD)


krev=-87e-3
narev=50e-3
carev=48e-3
ZpowCDI=2

VMIN = -120e-3
VMAX = 50e-3
VDIVS = 3401 #0.5 mV steps
CAMIN = 0.01e-3   #10 nM
CAMAX = 40e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS = 4001 #10 nM steps


#qfactNaF = 1.0

Na_m_params = AlphaBetaChannelParams(A_rate = 35.7e3,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf = -32.4e-3,
                                      A_vslope = 6e-3,
                                      B_rate = 35.7e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      Bvhalf = -32.4e-3,
                                      B_vslope = -6e-3)

Na_h_params = AlphaBetaChannelParams(A_rate = 3.9e3,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf = -70e-3,
                                      A_vslope = -10.0e-3,
                                      B_rate = 3.9e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      Bvhalf = -30e-3,
                                      B_vslope = 6e-3)

Na_s_param= AlphaBetaChannelParams(A_rate = 98.73,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf = -85e-3,
                                      A_vslope = -10.0e-3,
                                      B_rate = 69,
                                      B_B = 0.0,
                                      B_C = 1,
                                      Bvhalf = 29e-3,
                                      B_vslope = 13e-3)


NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=1, Erev=narev, name='NaF')


#KDrparam -Kv2
KDrparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KDr')

KDr_X_params = AlphaBetaChannelParams(A_rate = 8.2e3,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf = 48e-3,
                                      A_vslope = 13e-3,
                                      B_rate = 5.71e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      Bvhalf = -130e-3,
                                      B_vslope = -18e-3)

KDr_Y_params = AlphaBetaChannelParams(A_rate = 0.3,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf = -10e-3,
                                      A_vslope = -10e-3,
                                      B_rate = 0.3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      Bvhalf = -10e-3,
                                      B_vslope = 10e-3)



Kv3param = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='Kv3')


#qfactKrp=1

Kv3_X_params = AlphaBetaChannelParams(A_rate = 10e3,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf = 40e-3,
                                      A_vslope = 12e-3,
                                      B_rate = 10e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      Bvhalf = -85e-3,
                                      B_vslope = -12e-3)


Kv3_Y_params = AlphaBetaChannelParams(A_rate = 30.5,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf = -15e-3,
                                      A_vslope = -13e-3,
                                      B_rate = 145,
                                      B_B = 0.0,
                                      B_C = 1,
                                      Bvhalf = 10e-3,
                                      B_vslope = 13e-3)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate = 3.8e3,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf = 30e-3,
                                      A_vslope = 22.0e-3,
                                      B_rate = 1.5e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      Bvhalf = -100e-3,
                                      B_vslope = -20e-3)

KvF_Y_params= AlphaBetaChannelParams(A_rate = 160,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf = -100e-3,
                                      A_vslope = -15e-3,
                                      B_rate = 142,
                                      B_B = 0.0,
                                      B_C = 1,
                                      Bvhalf = -73e-3,
                                      B_vslope = -10e-3)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KaF')


KvS_X_params = AlphaBetaChannelParams(A_rate =3.8e3,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf = 30e-3,
                                      A_vslope = 22.0e-3,
                                      B_rate = 1.5e3,
                                      B_B = 0,
                                      B_C = 1,
                                      Bvhalf = -100e-3,
                                      B_vslope = -20e-3)

KvS_Y_params = AlphaBetaChannelParams(A_rate =20 ,
                                      A_B = 0,
                                      A_C = 1,
                                      Avhalf =-90e-3 ,
                                      A_vslope = -12e-3,
                                      B_rate = 20,
                                      B_B = 0,
                                      B_C = 1,
                                      Bvhalf =-77e-3 ,
                                      B_vslope = 10e-3)


KCNQparam =  ChannelSettings(Xpow=4, Ypow=0, Zpow=0, Erev=krev, name='KCNQ')

KCNQ_X_params = AlphaBetaChannelParams(A_rate=145,
                                      A_B=0,
                                      A_C=1,
                                      Avhalf=20e-3,
                                      A_vslope=25e-3,
                                      B_rate=80,
                                      B_B=0,
                                      B_C=1,
                                      Bvhalf=-100e-3,
                                      B_vslope=-25e-3)

KCNQ_Y_params = []



HCN1param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=carev, name='HCN1')

HCN1_X_params = AlphaBetaChannelParams(A_rate = 17.5e3,
                                        A_B = 0,
                                        A_C = 1,
                                        Avhalf = -150e-3,
                                        A_vslope = -6.3e-3,
                                        B_rate = 6700e3,
                                        B_B = 0,
                                        B_C = 1,
                                        Bvhalf = -40e-3,
                                        B_vslope = 6.9e-3)
HCN1_Y_params=[]

HCN2param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=carev, name='HCN2')

HCN2_X_params = AlphaBetaChannelParams(A_rate = 20.5e3,
                                        A_B = 0,
                                        A_C = 1,
                                        Avhalf = -185e-3,
                                        A_vslope = -8e-3,
                                        B_rate = 55000e3,
                                        B_B = 0,
                                        B_C = 1,
                                        Bvhalf = 80e-3,
                                        B_vslope = 8.5e-3)
HCN2_Y_params=[]






Channels = NamedDict(
    'Channels',
    KDr =   TypicalOneDalpha(KDrparam, KDr_X_params, KDr_Y_params),
    Kv3 =   TypicalOneDalpha(Kv3param, Kv3_X_params, Kv3_Y_params),
    KvF =   TypicalOneDalpha(KvFparam, KvF_X_params, KvF_Y_params),
    KvS =   TypicalOneDalpha(KvSparam, KvS_X_params, KvS_Y_params),
    HCN1 =  TypicalOneDalpha(HCN1param,HCN1_X_params, []),
    HCN2 =  TypicalOneDalpha(HCN2param,HCN2_X_params, []),
    KCNQ =  TypicalOneDalpha(KCNQparam,KCNQ_X_params, []),
    NaF =   TypicalOneDalpha(NaFparam, Na_m_params, Na_h_params,Na_s_param),
)
# have to add NaP and calcium channels