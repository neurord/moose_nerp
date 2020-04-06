# Generated from npzfile: fitgp-proto-cmaes_proto047_84362_24.npz of fit number: 6217

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
Na_m_params = AlphaBetaChannelParams(A_rate=18701.745382475252,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.043880558912688265,
 A_vslope=-0.005,
 B_rate=18701.745382475252,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.043880558912688265,
 B_vslope=0.005)

Na_h_params = AlphaBetaChannelParams(A_rate=4857.585684134198,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.07626550356491181,
 A_vslope=0.009,
 B_rate=4857.585684134198,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.036265503564911816,
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
NaS_m_params = AlphaBetaChannelParams(A_rate=41197.37931250061,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.06405823835209269,
 A_vslope=-0.027,
 B_rate=41197.37931250061,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.1263417616479073,
 B_vslope=0.0262)

NaS_h_params = AlphaBetaChannelParams(A_rate=30.876717655802608,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.05668068837819083,
 A_vslope=0.0045,
 B_rate=28.946922802314944,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.05568068837819083,
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

Kv3_X_params = AlphaBetaChannelParams(A_rate=2625.150335847398,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.023241061330191666,
 A_vslope=-0.015,
 B_rate=3570.2044567524613,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.08775893866980834,
 B_vslope=0.015)

Kv3_Y_params = TauInfMinChannelParams(T_min=0.005880416985412505,
 T_vdep=0.021841548802960735,
 T_vhalf=-0.0011705863826189256,
 T_vslope=0.01,
 SS_min=0.6,
 SS_vdep=0.4,
 SS_vhalf=-0.021170586382618928,
 SS_vslope=0.01,
 T_power=1)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate=5067.713481174843,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.04015056051148264,
 A_vslope=-0.026,
 B_rate=5067.713481174843,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12184943948851737,
 B_vslope=0.027)

KvF_Y_params = AlphaBetaChannelParams(A_rate=124.55318766873071,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.10257800412733314,
 A_vslope=0.012,
 B_rate=117.91035099306508,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07757800412733315,
 B_vslope=-0.012)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate=4875.405390203058,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.03810081527067605,
 A_vslope=-0.022,
 B_rate=1924.5021277117332,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.09189918472932396,
 B_vslope=0.02)

KvS_Y_params = AlphaBetaChannelParams(A_rate=13.522239153405499,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.08533436461188804,
 A_vslope=0.01,
 B_rate=14.233935950953157,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07033436461188804,
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

HCN1_X_params = AlphaBetaChannelParams(A_rate=147.73518604835527,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.14003954848149266,
 A_vslope=0.01,
 B_rate=64.01858062095395,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.02003954848149267,
 B_vslope=-0.012)
HCN1_Y_params=[]

HCN2param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN2')

HCN2_X_params = AlphaBetaChannelParams(A_rate=16.30776822533482,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.13017657728096807,
 A_vslope=0.01,
 B_rate=10.871845483556546,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.01017657728096806,
 B_vslope=-0.012)
HCN2_Y_params=[]

#Caparam - D.James Surmeier, ( tau and ss)
Caparam=ChannelSettings(Xpow=1 , Ypow=0 , Zpow=0, Erev=carev , name='Ca')
Ca_X_params = AlphaBetaChannelParams(A_rate=372209.48742746585,
 A_B=-5176033.354641075,
 A_C=-1,
 A_vhalf=-0.07191017946082695,
 A_vslope=-0.011,
 B_rate=854.0455026617319,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.007089820539173047,
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
