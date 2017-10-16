

from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes.chan_proto import (
    SSTauQuadraticChannelParams,
    AlphaBetaChannelParams,
    StandardMooseTauSSChannelParams,
    TauSSMinChannelParams,
    ZChannelParams,
    BKChannelParams,
    ChannelSettings,
    TypicalOneDalpha,
    AtypicalOneD,
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

qfactNaF = 1.0

Na_m_params = AlphaBetaChannelParams(A_rate = 35e3,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = 36e-3,
                                      A_vslope = -5e-3,
                                      B_rate = 35e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 36e-3,
                                      B_vslope = 5e-3)

Na_h_params = AlphaBetaChannelParams(A_rate = 4.5e3,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = 70e-3,
                                      A_vslope = 9e-3,
                                      B_rate = 3e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 32e-3,
                                      B_vslope = -5e-3)

Na_s_param= AlphaBetaChannelParams(A_rate = 100,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = 84e-3,
                                      A_vslope = 10.0e-3,
                                      B_rate = 80,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = -26e-3,
                                      B_vslope = -14e-3)


NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=1, Erev=narev, name='NaF')


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
                                      A_vhalf = 20e-3,
                                      A_vslope = 10e-3,
                                      B_rate = 0.292,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 20e-3,
                                      B_vslope = -10e-3)



Kv3param = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='Kv3')


#qfactKrp=1

Kv3_X_params = AlphaBetaChannelParams(A_rate = 7e3,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = -32e-3,
                                      A_vslope =-12e-3,
                                      B_rate = 11e3,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = 82e-3,
                                      B_vslope = 12e-3)


Kv3_Y_params = AlphaBetaChannelParams(A_rate = 30.5,
                                      A_B = 0,
                                      A_C = 1,
                                      A_vhalf = 22e-3,
                                      A_vslope = 13e-3,
                                      B_rate = 145,
                                      B_B = 0.0,
                                      B_C = 1,
                                      B_vhalf = -10e-3,
                                      B_vslope = -15e-3)

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


KCNQparam =  ChannelSettings(Xpow=4, Ypow=0, Zpow=0, Erev=krev, name='KCNQ')

KCNQ_X_params = AlphaBetaChannelParams(A_rate=195,
                                      A_B=0,
                                      A_C=1,
                                      A_vhalf=-39e-3,
                                      A_vslope=-29.5e-3,
                                      B_rate=120,
                                      B_B=0,
                                      B_C=1,
                                      B_vhalf=128e-3,
                                      B_vslope=32e-3)

KCNQ_Y_params = []



HCN1param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN1')

HCN1_X_params = AlphaBetaChannelParams(A_rate = 10e3,
                                        A_B = 0,
                                        A_C = 1,
                                        A_vhalf = 140e-3,
                                        A_vslope = 6e-3,
                                        B_rate = 18000e3,
                                        B_B = 0,
                                        B_C = 1,
                                        B_vhalf = -56.5e-3,
                                        B_vslope = -7.4e-3)
HCN1_Y_params=[]

HCN2param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN2')

HCN2_X_params = AlphaBetaChannelParams(A_rate = 450,
                                        A_B = 0,
                                        A_C = 1,
                                        A_vhalf = 150e-3,
                                        A_vslope = 7.8e-3,
                                        B_rate = 13000e3,
                                        B_B = 0,
                                        B_C = 1,
                                        B_vhalf = -58e-3,
                                        B_vslope = -8e-3)
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
                            kdtau=4.3,
                            cahalf=0.002703
                             )
#persistnet Na_channel

NaS_m_params = AlphaBetaChannelParams(A_rate=7600e3,
                                     A_B=0,
                                     A_C=1,
                                     A_vhalf=-55.4e-3,
                                     A_vslope=-13.6e-3,
                                    B_rate=7000e3,
                                     B_B=0.0,
                                     B_C=1,
                                     B_vhalf=135e-3,
                                     B_vslope=13.5e-3)

NaS_h_params = AlphaBetaChannelParams(A_rate=32,
                                     A_B=0,
                                     A_C=1,
                                     A_vhalf=58e-3,
                                     A_vslope=4.5e-3,
                                     B_rate=32,
                                     B_B=0.0,
                                     B_C=1,
                                    B_vhalf=50e-3,
                                     B_vslope=-4e-3)

NaS_s_params = AlphaBetaChannelParams(A_rate=-0.147,
                                     A_B=-8.64,
                                     A_C=1,
                                     A_vhalf=0.017,
                                     A_vslope=4.63e-3,
                                     B_rate=1.341,
                                     B_B=20.82,
                                     B_C=1,
                                     B_vhalf=64.4e-3,
                                    B_vslope=-2.63e-3)
NaSparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=1, Erev=narev, name='NaP')

#BK channel
BKparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='BKCa')

BK_X_params=[BKChannelParams(alphabeta=480, K=0.18, delta=-0.84),
BKChannelParams(alphabeta=280, K=0.011, delta=-1.0)]
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
    Ca =   TypicalOneDalpha(Caparam,Ca_X_params, [],[], calciumPermeable=True),
    SKCa=  TypicalOneDalpha(SKparam, [], [], SK_Z_params , calciumDependent=True),
    NaS= TypicalOneDalpha(NaSparam,NaS_m_params,NaS_h_params,NaS_s_params),
    BKCa=TwoD(BKparam, BK_X_params, calciumDependent=True),
)
# have to add NaP and calcium channels
