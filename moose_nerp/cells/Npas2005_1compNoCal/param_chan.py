# Generated from npzfile: fitgp_1comp-Npas-cmaes_Npas2005_84362_8noCal.npz of fit number: 7669
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
Na_m_params = AlphaBetaChannelParams(A_rate=48869.52576705926,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.03256589042652369,
 A_vslope=-0.005,
 B_rate=48869.52576705926,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.03256589042652369,
 B_vslope=0.005)

Na_h_params = AlphaBetaChannelParams(A_rate=6810.764574104278,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.07745302320358723,
 A_vslope=0.009,
 B_rate=6810.764574104278,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.037453023203587225,
 B_vslope=-0.005)


NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')


#KDrparam -Kv2
KDrparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KDr')

KDr_X_params = AlphaBetaChannelParams(A_rate=6094.508110357232,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.049,
 A_vslope=-0.015,
 B_rate=2595.8090099669694,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.12,
 B_vslope=0.022)

KDr_Y_params = AlphaBetaChannelParams(A_rate=0.456818021968593,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.0,
 A_vslope=0.015,
 B_rate=0.456818021968593,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.0,
 B_vslope=-0.015)

Kv3param = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='Kv3')


#qfactKrp=1

Kv3_X_params = AlphaBetaChannelParams(A_rate=3794.01343804835,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.035602703223899766,
 A_vslope=-0.015,
 B_rate=5159.858275745756,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07539729677610023,
 B_vslope=0.015)

Kv3_Y_params = TauInfMinChannelParams(T_min=0.005472828692040172,
 T_vdep=0.02032764942757778,
 T_vhalf=-0.010800038578430718,
 T_vslope=0.01,
 SS_min=0.6,
 SS_vdep=0.4,
 SS_vhalf=-0.030800038578430715,
 SS_vslope=0.01,
 T_power=1)

KvFparam = ChannelSettings(Xpow=4, Ypow=1, Zpow=0, Erev=krev, name='KvF')


KvF_X_params = AlphaBetaChannelParams(A_rate=3597.6784536945975,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.029645387917126724,
 A_vslope=-0.026,
 B_rate=3597.6784536945975,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.13235461208287327,
 B_vslope=0.027)

KvF_Y_params = AlphaBetaChannelParams(A_rate=167.79745197842635,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.103629856377904,
 A_vslope=0.012,
 B_rate=158.84825453957694,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07862985637790401,
 B_vslope=-0.012)


KvSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KvS')


KvS_X_params = AlphaBetaChannelParams(A_rate=11676.815250062044,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.013063384479154559,
 A_vslope=-0.022,
 B_rate=4609.26917765607,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.11693661552084544,
 B_vslope=0.02)

KvS_Y_params = AlphaBetaChannelParams(A_rate=37.41933483585848,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.08698818638315453,
 A_vslope=0.01,
 B_rate=39.38877351142998,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.07198818638315453,
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

HCN2_X_params = AlphaBetaChannelParams(A_rate=4.051659010859005,
 A_B=0.0,
 A_C=1,
 A_vhalf=0.09511840967666049,
 A_vslope=0.01,
 B_rate=2.7011060072393365,
 B_B=0.0,
 B_C=1,
 B_vhalf=-0.02488159032333951,
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
