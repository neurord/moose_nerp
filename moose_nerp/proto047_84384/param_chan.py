# Generated from npzfile: fitgp-proto-cmaes_proto047_84384_24.npz of fit number: 7821
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
Na_m_params = AlphaBetaChannelParams(A_rate=23834.784066557146,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.041877113490140526,
 A_vslope=-0.005,
 B_rate=23834.784066557146,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.041877113490140526,
 B_vslope=0.005)

Na_h_params = AlphaBetaChannelParams(A_rate=9826.778941304572,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.08580752968000901,
 A_vslope=0.009,
 B_rate=9826.778941304572,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.045807529680009014,
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
 SS_vhalf=-0.038349999999999995,
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
NaS_m_params = AlphaBetaChannelParams(A_rate=17619.505803396736,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.05313191902146385,
 A_vslope=-0.027,
 B_rate=17619.505803396736,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.13726808097853616,
 B_vslope=0.0262)

NaS_h_params = AlphaBetaChannelParams(A_rate=48.46995490834114,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.0673899251431188,
 A_vslope=0.0045,
 B_rate=45.440582726569815,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0663899251431188,
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

Kv3_X_params = AlphaBetaChannelParams(A_rate=6572.116411926462,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.02451850141718452,
 A_vslope=-0.015,
 B_rate=8938.07832021999,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.08648149858281548,
 B_vslope=0.015)

Kv3_Y_params = TauInfMinChannelParams(T_min=0.008454224735315752,
 T_vdep=0.031401406159744225,
 T_vhalf=-0.0017956519933174393,
 T_vslope=0.01,
 SS_min=0.6,
 SS_vdep=0.4,
 SS_vhalf=-0.02179565199331744,
 SS_vslope=0.01,
 T_power=1)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate=4358.338536308002,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.04140247519307409,
 A_vslope=-0.026,
 B_rate=4358.338536308002,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12059752480692591,
 B_vslope=0.027)

KvF_Y_params = AlphaBetaChannelParams(A_rate=269.16212397680323,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.08732935195248714,
 A_vslope=0.012,
 B_rate=254.8068106980404,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.06232935195248716,
 B_vslope=-0.012)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate=5960.418899661727,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.034008036898163695,
 A_vslope=-0.022,
 B_rate=2352.7969340769973,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0959919631018363,
 B_vslope=0.02)

KvS_Y_params = AlphaBetaChannelParams(A_rate=32.66439402525449,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.09827182394146124,
 A_vslope=0.01,
 B_rate=34.38357265816262,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.08327182394146124,
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

HCN1_X_params = AlphaBetaChannelParams(A_rate=70.225402855513,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.13885315583812616,
 A_vslope=0.01,
 B_rate=30.431007904055633,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.01885315583812615,
 B_vslope=-0.012)
HCN1_Y_params=[]

HCN2param = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=hcnrev, name='HCN2')

HCN2_X_params = AlphaBetaChannelParams(A_rate=8.478900598386513,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.1382670991351183,
 A_vslope=0.01,
 B_rate=5.652600398924342,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.018267099135118304,
 B_vslope=-0.012)
HCN2_Y_params=[]

#Caparam - D.James Surmeier, ( tau and ss)
Caparam=ChannelSettings(Xpow=1 , Ypow=0 , Zpow=0, Erev=carev , name='Ca')
Ca_X_params = AlphaBetaChannelParams(A_rate=282157.7966843071,
 A_B=-3829065.3572715926,
 A_C=-1,
 A_vhalf=-0.07368842533556522,
 A_vslope=-0.011,
 B_rate=631.795783318017,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.005311574664434791,
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
''' value of channel parameters after 1 set of proto and Npas fits
1st three are Npas, 2nd three are proto
 Chan_HCN1_taumul [0.75247 0.99662 1.5855  0.87686 1.5789  0.87148] mean: 1.1103 stdev: 0.34105
 Chan_HCN2_taumul [1.9513  0.58199 1.5997  1.1972  1.0126  1.9645 ] mean: 1.3845 stdev: 0.50355
 Chan_HCN1_vshift [ 0.011049  -0.0049125  0.014316  -0.013645  -0.019864   0.010886 ] mean: -0.00036175 stdev: 0.013227
 Chan_HCN2_vshift [ 0.012432  -0.0047285  0.015686   0.0059645 -0.013647  -0.016169 ] mean: -7.7e-05 stdev: 0.012289
*** Chan_NaF_vshift [0.0049162  0.0054647  0.0028813  0.0037995  0.00020927 0.0074307 ] mean: 0.0041169 stdev: 0.0022485
*** Chan_NaF_taumul [1.5573  0.54307 1.8079  1.8231  1.9615  1.3606 ] mean: 1.5089 stdev: 0.47436
*** Chan_NaS_vshift [ 0.008924   0.0099036  0.0099299 -0.0046971  0.0072152  0.0086504] mean: 0.0066543 stdev: 0.0051574
 Chan_NaS_taumul [0.65767 1.0104  0.97767 1.231   1.5465  1.132  ] mean: 1.0925 stdev: 0.26952
 Chan_Kv3_vshift [ 0.0092292  0.002342  -0.0081308 -0.0025044  0.008635   0.0096172] mean: 0.003198 stdev: 0.0066925
*** Chan_Kv3_taumul [1.834  1.245  1.0253 1.895  1.7331 1.5499] mean: 1.547 stdev: 0.31662
 Chan_KvS_vshift [ 0.007601  -0.0013709 -0.0071367  0.0050459 -0.0088977  0.0023334] mean: -0.00040417 stdev: 0.0060509
*** Chan_KvS_taumul [0.85621 1.7998  1.5479  1.3451  1.4659  1.3459 ] mean: 1.3935 stdev: 0.28503
 Chan_KvF_vshift [ 0.0012018  0.008845   0.003316  -0.0084184  0.0079531 -0.0074532] mean: 0.00090738 stdev: 0.006775
 Chan_KvF_taumul [1.3766  0.68123 1.2083  1.6584  1.4367  1.0324 ] mean: 1.2323 stdev: 0.31315
'''
