# Generated from npzfile: fitd1patchsample2-D1-D1_Patch_Sample_5_NSG_full_tmp_8753287.npz of fit number: 17

from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes.chan_proto import (
    AlphaBetaChannelParams,
    StandardMooseTauInfChannelParams,
    TauInfMinChannelParams,
    ZChannelParams,
    BKChannelParams,
    ChannelSettings,
    TypicalOneD,
    TwoD,
    )

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
#

#units for membrane potential: volts
clrev=-60e-3
krev=-90e-3
narev=50e-3
carev=140e-3 #assumes CaExt=2 mM and CaIn=50e-3
ZpowCDI=2

VMIN = -140e-3
VMAX = 80e-3
VDIVS = 3401 #0.5 mV steps

#units for calcium concentration: mM
CAMIN = 0.001e-3   #10 nM
CAMAX = 150e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS = 4001 #10 nM steps

#mtau: Ogata fig 5, no qfactor accounted in mtau, 1.2 will improve spike shape
#activation minf fits Ogata 1990 figure 3C (which is cubed root)
#inactivation hinf fits Ogata 1990 figure 6B
#htau fits the main -50 through -10 slope of Ogata figure 9 (log tau), but a qfact of 2 is already taken into account.

qfactNaF = 2.5

Na_m_params = TauInfMinChannelParams(T_min=0.0003527656466065767,
 T_vdep=0.007416897719903275,
 T_vhalf=-0.06439497144622046,
 T_vslope=0.008,
 SS_min=0.0,
 SS_vdep=1.0,
 SS_vhalf=-0.02739497144622046,
 SS_vslope=-0.01,
 T_power=2)

Na_h_params = TauInfMinChannelParams(T_min=0.0005797713601397877,
 T_vdep=0.002526236863354194,
 T_vhalf=-0.02582494684815666,
 T_vslope=0.003,
 SS_min=0.0,
 SS_vdep=1.0,
 SS_vhalf=-0.04382494684815666,
 SS_vslope=0.006,
 T_power=1)

NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')

#This is from Migliore.
# KDrparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='KDr')

# KDr_X_params = AlphaBetaChannelParams(A_rate = 28.2,
#                                       A_B = 0,
#                                       A_C = 0.0,
#                                       A_vhalf = 0,
#                                       A_vslope = -12.5e-3,
#                                       B_rate = 6.78,
#                                       B_B = 0.0,
#                                       B_C = 0.0,
#                                       B_vhalf = 0.0,
#                                       B_vslope = 33.5e-3)
# KDr_Y_params = []

Krpparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='Krp')

#Act tuned to fit Nisenbaum 1996 fig6C (minf^2) and fig 8C (mtau)
qfactKrp=3  #Used by RE

Krp_X_params = AlphaBetaChannelParams(A_rate=48,
 A_B=0,
 A_C=0.0,
 A_vhalf=0,
 A_vslope=-0.02,
 B_rate=7.199999999999999,
 B_B=0.0,
 B_C=0.0,
 B_vhalf=0.0,
 B_vslope=0.04)

# tuned to fit Nisenbaum 1996 fig 9D (hinf, 87% inactivating) and 9B (htau)
Krp_Y_params = TauInfMinChannelParams(T_min=0.8639999999999999,
 T_vdep=12.48,
 T_vhalf=-0.042,
 T_vslope=0.013000000000000001,
 SS_min=0.13,
 SS_vdep=0.87,
 SS_vhalf=-0.056,
 SS_vslope=0.015,
 T_power=1)

Kirparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='Kir')
qfactKir = 1

Kir_X_params = AlphaBetaChannelParams(A_rate=0.017739434064030172,
 A_B=0.0,
 A_C=0.0,
 A_vhalf=0.019781231406896534,
 A_vslope=0.011,
 B_rate=2217.4292580037713,
 B_B=0.0,
 B_C=1.0,
 B_vhalf=-0.02021876859310347,
 B_vslope=-0.04)

KaFparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KaF')

# activation constants for alphas and betas (obtained by
# matching m2 to Tkatch et al., 2000 Figs 2c, and mtau to fig 2b)

qfactKaF = 2
KaF_X_params = AlphaBetaChannelParams(A_rate=1522.7237068370623,
 A_B=0.0,
 A_C=1.0,
 A_vhalf=0.02234093839962657,
 A_vslope=-0.013,
 B_rate=380.6809267092656,
 B_B=0.0,
 B_C=1.0,
 B_vhalf=0.002340938399626571,
 B_vslope=0.011)

#inactivation consts for alphas and betas obtained by matching Tkatch et al., 2000 Fig 3b,
#and tau voltage dependence consistent with their value for V=0 in fig 3c.
#slowing down inact improves spike shape tremendously
KaF_Y_params = AlphaBetaChannelParams(A_rate=291.9506848318663,
 A_B=0.0,
 A_C=1.0,
 A_vhalf=0.1278458167887299,
 A_vslope=0.022,
 B_rate=180.73137632448868,
 B_B=0.0,
 B_C=1.0,
 B_vhalf=0.061845816788729906,
 B_vslope=-0.011)

#KaS based on Shen 2004 data and Wolf 2005 model code. Note that the Wolf model
#code on ModelDB notes that, via personal correspondance with Shen 2004 author,
#parameters in Shen 2004 were misreported, and are subsequently corrected in
#the Wolf 2005 code. Alpha/Beta channel params were fit to be similar to the
#Wolf steady state and tau equations--see fitKaS.py for fitting script.
#Note: Fit looks ok with these parameters but could stand to be improved.
KaSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KaS')
qfactKaS = 3 # Shen 2004/Wolf 2005
KaS_X_params = AlphaBetaChannelParams(A_rate=108110.51895580215,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.09358987070353847,
 A_vslope=-0.0162951634,
 B_rate=1705794648.3562324,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.3925286630964615,
 B_vslope=0.0218235302)

KaS_Y_params = AlphaBetaChannelParams(A_rate=62977434.43001568,
 A_B=0.0,
 A_C=1.0,
 A_vhalf=1.2195571881862548,
 A_vslope=0.0645391447,
 B_rate=3.166722744924064,
 B_B=0.0,
 B_C=1.0,
 B_vhalf=-0.0018072090117451892,
 B_vslope=-0.0262013787)

#SS values from Churchill and MacVicar, assuming Xpow = 1
##time constants extrapolated from scarce measurements - Song & Surmeier
#SS values measured by Kasai and Neher are quite similar, except
#they use Xpow=2 to fit, thus params would be different
#they have nice time constant measurements which are ~2x slower than above
#but they measured at room temp, so qfact=1 on S&S and qfact=2 on K&N would equate them
#Vdep inact by Kasai ~10% and very slow (>50 ms). For now, have no Vdep inact.
# CDI measured by Kasai
#Note that CaL13 for D1 has mvhalf 10 mV more negative than for D2
#CaL12 does not differ between D1 and D2.
CaL12param = ChannelSettings(Xpow=1, Ypow=1, Zpow=ZpowCDI, Erev=carev, name='CaL12')
qfactCaL = 2

CaL12_X_params = AlphaBetaChannelParams(A_rate=-1760.132,
 A_B=-440000.0,
 A_C=-1.0,
 A_vhalf=0.0040003,
 A_vslope=-0.008,
 B_rate=-568.0426,
 B_B=142000.0,
 B_C=-1.0,
 B_vhalf=-0.0040003,
 B_vslope=0.005)


CaL12_Y_params = TauInfMinChannelParams(T_min=0.02215,
 T_vdep=0,
 T_vhalf=0.0040003,
 T_vslope=-0.0075,
 SS_min=0.83,
 SS_vdep=0.17,
 SS_vhalf=-0.055,
 SS_vslope=0.008,
 T_power=1)

# Using Xpow=1 produced too high a basal calcium,
# so used Xpow=2 and retuned params - much better basal calcium
CaL13param = ChannelSettings(Xpow=1, Ypow=1, Zpow=ZpowCDI, Erev=carev, name='CaL13')

CaL13_X_params = AlphaBetaChannelParams(A_rate=3000,
 A_B=0,
 A_C=1,
 A_vhalf=-0.005,
 A_vslope=-0.018,
 B_rate=4000,
 B_B=0,
 B_C=1.0,
 B_vhalf=0.052,
 B_vslope=0.008)
CaL13_Y_params = TauInfMinChannelParams(T_min=0.02215,
 T_vdep=0,
 T_vhalf=0.037,
 T_vslope=0.005,
 SS_min=0,
 SS_vdep=1,
 SS_vhalf=-0.037,
 SS_vslope=0.005,
 T_power=1)
#Params from McRory J Biol Chem, alpha1I subunit
CaTparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=carev, name='CaT')
qfactCaT = 2
CaT_X_params = AlphaBetaChannelParams(A_rate=2000,
 A_B=0.0,
 A_C=0.0,
 A_vhalf=0.0,
 A_vslope=-0.019,
 B_rate=2673.0099,
 B_B=33000,
 B_C=-1.0,
 B_vhalf=0.0810003,
 B_vslope=0.00712)

#Original inactivation ws too slow compared to activation, made closder the alpha1G
CaT_Y_params = AlphaBetaChannelParams(A_rate=7684.020399999999,
 A_B=68000,
 A_C=-1.0,
 A_vhalf=0.1130003,
 A_vslope=0.00512,
 B_rate=640,
 B_B=0,
 B_C=0.0,
 B_vhalf=0.0,
 B_vslope=-0.017)

CaT32param = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=carev, name='CaT32')
qfactCaT32 = 2
CaT32_X_params = TauInfMinChannelParams(T_min=0.000458,
 T_vdep=0.00665,
 T_vhalf=-0.0536,
 T_vslope=0.0104,
 SS_min=0.0,
 SS_vdep=1.0,
 SS_vhalf=-0.0523,
 SS_vslope=-0.0068,
 T_power=1)
CaT32_Y_params = TauInfMinChannelParams(T_min=0.0102,
 T_vdep=0.0228,
 T_vhalf=-0.0455,
 T_vslope=0.003,
 SS_min=0.0,
 SS_vdep=1.0,
 SS_vhalf=-0.0738,
 SS_vslope=0.0028,
 T_power=1)

CaT33param = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=carev, name='CaT33')
qfactCaT33 = 2
CaT33_X_params = TauInfMinChannelParams(T_min=0.0016,
 T_vdep=0.1005,
 T_vhalf=-0.0814,
 T_vslope=0.0089,
 SS_min=0.003,
 SS_vdep=1.0,
 SS_vhalf=-0.0727,
 SS_vslope=-0.0087,
 T_power=1)
CaT33_Y_params = TauInfMinChannelParams(T_min=0.05705,
 T_vdep=0.5,
 T_vhalf=-0.0699,
 T_vslope=0.0044,
 SS_min=0.005,
 SS_vdep=1.0,
 SS_vhalf=-0.0932,
 SS_vslope=0.0049,
 T_power=1)


# CaN SS parameters tuned so m2 fits Bargas and Surmeier 1994 boltzmann curve
# CaN tau from kasai 1992.
# Kasai measures calcium dependent inactivation
#McNaughton has act and inact, tau and ss for human CaN
CaNparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=ZpowCDI, Erev=carev, name='CaN')
qfactCaN = 2
CaN_X_params = AlphaBetaChannelParams(A_rate=608,
 A_B=0,
 A_C=0.0,
 A_vhalf=0.0,
 A_vslope=-0.014,
 B_rate=1499.5231680000002,
 B_B=105600,
 B_C=-1.0,
 B_vhalf=0.01420003,
 B_vslope=0.01)

CaN_Y_params = TauInfMinChannelParams(T_min=0.035,
 T_vdep=0,
 T_vhalf=0.0,
 T_vslope=-0.014,
 SS_min=0.79,
 SS_vdep=0.21,
 SS_vhalf=-0.0748,
 SS_vslope=0.0065,
 T_power=1)
# CaR SS (Act and Inact) parameters from Foerhing et al., 2000
# Was Xpow=3 taken into account during fit?
# CaR tau from a few measurements from pyramidal neurons by Foerhing
# CaR inact tau from Brevi 2001
#Inact params are a bit too steep for ss, and not steep enough for tau
CaRparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=carev, name='CaR')
qfactCaR = 2
CaR_X_params = AlphaBetaChannelParams(A_rate=120.0,
 A_B=0,
 A_C=0.0,
 A_vhalf=-0.01,
 A_vslope=-0.028,
 B_rate=592000.0,
 B_B=4000000.0,
 B_C=-1.0,
 B_vhalf=0.148,
 B_vslope=0.0136)

CaR_Y_params = AlphaBetaChannelParams(A_rate=250.0,
 A_B=2500.0,
 A_C=-1.0,
 A_vhalf=0.1,
 A_vslope=0.017,
 B_rate=5.0,
 B_B=0,
 B_C=0.0,
 B_vhalf=-0.01,
 B_vslope=-0.03)

#Reference: Maylie Bond Herson Lee Adelman 2004, Fig 2 steady state
#Fast component has tau~4 ms; not used: slow tau = 70 ms
#Fast component, tau=4.9ms from Hirschberg et al., 1998 figure 13.
SKparam = ChannelSettings(Xpow=0, Ypow=0, Zpow=1, Erev=krev, name='SKCa')

SK_Z_params = ZChannelParams(Kd=0.00057,
 power=5.2,
 tau=0.0049,
 taumax=0,
 tau_power=0,
 cahalf=0)

#Reference: Berkefeld et al. Science 2006 314(5799):615-20. Moczydlowski and Latorre 1983, J. Gen. Physiol. 82:511-542.

BKparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='BKCa')

BK_X_params=[BKChannelParams(alphabeta=480, K=0.18, delta=-0.84),
             BKChannelParams(alphabeta=280, K=0.011, delta=-1.0)]
#These CDI params can be used with every channel, make ZpowCDI=2
#If ZpowCDI=0 the CDI will not be used, power=-4 is to transform
#(Ca/Kd)^pow/(1+(Ca/Kd)^pow) to 1/(1+(ca/Kd)^-pow)
CDI_Z_params = ZChannelParams(Kd=0.00012,
 power=-4,
 tau=0.142,
 taumax=0,
 tau_power=0,
 cahalf=0)


# Calcium-activated chloride channel params
# Reference: Pifferi, S., Dibattista, M., & Menini, A. (2009). TMEM16B induces chloride
#            currents activated by calcium in mammalian cells. Pflügers Archiv-European
#            Journal of Physiology, 458(6), 1023-1038.
CaCCparam = ChannelSettings(Xpow=0, Ypow=0, Zpow=1, Erev=clrev, name='CaCC')

CaCC_Z_params = ZChannelParams(Kd=0.00183,
 power=2.3,
 tau=0.01386312014608369,
 taumax=0.0,
 tau_power=0,
 cahalf=0)


#Dictionary of "standard" channels, to create channels using a loop
#NaF doesn't fit since it uses different prototype form
#will need separate dictionary for BK

Channels = NamedDict(
    'Channels',
    Krp =   TypicalOneD(Krpparam, Krp_X_params,Krp_Y_params),
    KaF =   TypicalOneD(KaFparam, KaF_X_params, KaF_Y_params),
    KaS =   TypicalOneD(KaSparam, KaS_X_params, KaS_Y_params),
    Kir =   TypicalOneD(Kirparam,  Kir_X_params, []),
    CaL12 = TypicalOneD(CaL12param,CaL12_X_params, CaL12_Y_params, CDI_Z_params, calciumPermeable=True, calciumDependent=True),
    CaL13 = TypicalOneD(CaL13param, CaL13_X_params,CaL13_Y_params, CDI_Z_params, calciumPermeable=True, calciumDependent=True),
    CaN =   TypicalOneD(CaNparam, CaN_X_params, CaN_Y_params, CDI_Z_params, calciumPermeable=True, calciumDependent=True),
    CaR =   TypicalOneD(CaRparam, CaR_X_params, CaR_Y_params, [], calciumPermeable=True),
    CaT =   TypicalOneD(CaTparam,CaT_X_params, CaT_Y_params, [], calciumPermeable=True),
    CaT32 =   TypicalOneD(CaT32param,CaT32_X_params, CaT32_Y_params, [], calciumPermeable=True),
    CaT33 =   TypicalOneD(CaT33param,CaT33_X_params, CaT33_Y_params, [], calciumPermeable=True),
    SKCa =  TypicalOneD(SKparam, [], [], SK_Z_params, calciumDependent=True),
    NaF =   TypicalOneD(NaFparam, Na_m_params, Na_h_params),
    BKCa =  TwoD(BKparam, BK_X_params, calciumDependent=True),
    CaCC =  TypicalOneD(CaCCparam, [], [], CaCC_Z_params, calciumDependent=True),
)
