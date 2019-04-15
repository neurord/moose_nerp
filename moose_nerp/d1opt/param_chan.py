

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

VMIN = -120e-3
VMAX = 50e-3
VDIVS = 3401 #0.5 mV steps

#units for calcium concentration: mM
CAMIN = 0.01e-3   #10 nM
CAMAX = 40e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS = 4001 #10 nM steps

#mtau: Ogata fig 5, no qfactor accounted in mtau, 1.2 will improve spike shape
#activation minf fits Ogata 1990 figure 3C (which is cubed root)
#inactivation hinf fits Ogata 1990 figure 6B
#htau fits the main -50 through -10 slope of Ogata figure 9 (log tau), but a qfact of 2 is already taken into account.

qfactNaF = 2.5

Na_m_params = TauInfMinChannelParams(T_min=0.000319999856631733,
 T_vdep=0.006727996985682187,
 T_vhalf=-0.03485224384186281,
 T_vslope=0.008,
 SS_min=0.0,
 SS_vdep=1.0,
 SS_vhalf=0.002147756158137188,
 SS_vslope=-0.01,
 T_power=2)

Na_h_params = TauInfMinChannelParams(T_min=0.000548472713377449,
 T_vdep=0.002389859317548796,
 T_vhalf=-0.020221280082147595,
 T_vslope=0.003,
 SS_min=0.0,
 SS_vdep=1.0,
 SS_vhalf=-0.038221280082147605,
 SS_vslope=0.006,
 T_power=1)

NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')

#This is from Migliore.
'''
KDrparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='KDr')

KDr_X_params = AlphaBetaChannelParams(A_rate = 28.2,
                                      A_B = 0,
                                      A_C = 0.0,
                                      A_vhalf = 0,
                                      A_vslope = -12.5e-3,
                                      B_rate = 6.78,
                                      B_B = 0.0,
                                      B_C = 0.0,
                                      B_vhalf = 0.0,
                                      B_vslope = 33.5e-3)
KDr_Y_params = []
'''
Krpparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='Krp')

#Act tuned to fit Nisenbaum 1996 fig6C (minf^2) and fig 8C (mtau)
qfactKrp=3  #Used by RE

Krp_X_params = AlphaBetaChannelParams(A_rate=352.83971247681075,
 A_B=0.0,
 A_C=0.0,
 A_vhalf=-0.007031818920258446,
 A_vslope=-0.02,
 B_rate=52.925956871521606,
 B_B=0.0,
 B_C=0.0,
 B_vhalf=-0.007031818920258446,
 B_vslope=0.04)

# tuned to fit Nisenbaum 1996 fig 9D (hinf, 87% inactivating) and 9B (htau)
Krp_Y_params = TauInfMinChannelParams(T_min=6.351114824582592,
 T_vdep=91.73832524397079,
 T_vhalf=-0.049031818920258444,
 T_vslope=0.013000000000000001,
 SS_min=0.13,
 SS_vdep=0.87,
 SS_vhalf=-0.06303181892025844,
 SS_vslope=0.015,
 T_power=1)

Kirparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='Kir')
qfactKir = 1

Kir_X_params = AlphaBetaChannelParams(A_rate=0.008,
 A_B=0,
 A_C=0.0,
 A_vhalf=0,
 A_vslope=0.011,
 B_rate=1000,
 B_B=0.0,
 B_C=1.0,
 B_vhalf=-0.04,
 B_vslope=-0.04)

KaFparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KaF')

# activation constants for alphas and betas (obtained by
# matching m2 to Tkatch et al., 2000 Figs 2c, and mtau to fig 2b)

qfactKaF = 2
KaF_X_params = AlphaBetaChannelParams(A_rate=26836.413071168372,
 A_B=0.0,
 A_C=1.0,
 A_vhalf=0.021534774810745536,
 A_vslope=-0.013,
 B_rate=6709.103267792093,
 B_B=0.0,
 B_C=1.0,
 B_vhalf=0.0015347748107455402,
 B_vslope=0.011)

#inactivation consts for alphas and betas obtained by matching Tkatch et al., 2000 Fig 3b,
#and tau voltage dependence consistent with their value for V=0 in fig 3c.
#slowing down inact improves spike shape tremendously
KaF_Y_params = AlphaBetaChannelParams(A_rate=1144.9233729041205,
 A_B=0.0,
 A_C=1.0,
 A_vhalf=0.15934201776336743,
 A_vslope=0.022,
 B_rate=708.7620879882651,
 B_B=0.0,
 B_C=1.0,
 B_vhalf=0.09334201776336742,
 B_vslope=-0.011)

#KaS based on Shen 2004 data and Wolf 2005 model code. Note that the Wolf model
#code on ModelDB notes that, via personal correspondance with Shen 2004 author,
#parameters in Shen 2004 were misreported, and are subsequently corrected in
#the Wolf 2005 code. Alpha/Beta channel params were fit to be similar to the
#Wolf steady state and tau equations--see fitKaS.py for fitting script.
#Note: Fit looks ok with these parameters but could stand to be improved.
KaSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KaS')
qfactKaS = 3 # Shen 2004/Wolf 2005
KaS_X_params = AlphaBetaChannelParams(A_rate=484839.2175890564,
 A_B=0.0,
 A_C=1,
 A_vhalf=-0.13266144249786604,
 A_vslope=-0.0162951634,
 B_rate=7649913724.07291,
 B_B=0.0,
 B_C=1,
 B_vhalf=0.3534570913021339,
 B_vslope=0.0218235302)

KaS_Y_params = AlphaBetaChannelParams(A_rate=254395877.14473855,
 A_B=0.0,
 A_C=1.0,
 A_vhalf=1.2333113968478355,
 A_vslope=0.0645391447,
 B_rate=12.79190264989889,
 B_B=0.0,
 B_C=1.0,
 B_vhalf=0.011946999649835387,
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
CaRparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=ZpowCDI, Erev=carev, name='CaR')
qfactCaR = 2
CaR_X_params = AlphaBetaChannelParams(A_rate=480,
 A_B=0,
 A_C=0.0,
 A_vhalf=0.0,
 A_vslope=-0.028,
 B_rate=2528000.0,
 B_B=16000000.0,
 B_C=-1.0,
 B_vhalf=0.158,
 B_vslope=0.0136)

CaR_Y_params = AlphaBetaChannelParams(A_rate=1100.0,
 A_B=10000,
 A_C=-1.0,
 A_vhalf=0.11,
 A_vslope=0.017,
 B_rate=20,
 B_B=0,
 B_C=0.0,
 B_vhalf=0.0,
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
 tau=0.013,
 taumax=0,
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
    CaL12 = TypicalOneD(CaL12param,CaL12_X_params, CaL12_Y_params, CDI_Z_params, calciumPermeable=True),
    CaL13 = TypicalOneD(CaL13param, CaL13_X_params,CaL13_Y_params, CDI_Z_params, calciumPermeable=True),
    CaN =   TypicalOneD(CaNparam, CaN_X_params, CaN_Y_params, CDI_Z_params, calciumPermeable=True),
    CaR =   TypicalOneD(CaRparam, CaR_X_params, CaR_Y_params, CDI_Z_params, calciumPermeable=True),
    CaT =   TypicalOneD(CaTparam,CaT_X_params, CaT_Y_params, [], calciumPermeable=True),
    SKCa =  TypicalOneD(SKparam, [], [], SK_Z_params, calciumDependent=True),
    NaF =   TypicalOneD(NaFparam, Na_m_params, Na_h_params),
    BKCa =  TwoD(BKparam, BK_X_params, calciumDependent=True),
    CaCC =  TypicalOneD(CaCCparam, [], [], CaCC_Z_params, calciumDependent=True),
)
