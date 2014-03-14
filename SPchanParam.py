from collections import namedtuple

#chanDictSP.py
#contains all gating parameters and reversal potentials
# Gate equations have the form:
#
# y(x) = (rate + B * x) / (C + exp((x + vhalf) / vslope))
#
# OR
# y(x) = tau_min + tau_vdep / (1 + exp((x + vhalf) / vslope))
#
# where x is membrane voltage and y is the rate constant
#KDr params used by Sriram, RE paper1, Krp params used by RE paper 2
krev=-87e-3
narev=50e-3
carev=48e-3 #assumes CaExt=2 mM and CaIn=50e-3
ZpowCDI=2

#mtau: Ogata fig 5, no qfactor accounted in mtau, 1.2 will improve spike shape
#activation minf fits Ogata 1990 figure 3C (which is cubed root)
#inactivation hinf fits Ogata 1990 figure 6B
#htau fits the main -50 through -10 slope of Ogata figure 9 (log tau), but a qfact of 2 is already taken into account.

qfactNaF = 1.3
SSTauChannelParams = namedtuple('SSTauChannelParams', '''
                                Arate
                                A_B
                                A_C
                                Avhalf
                                Avslope
                                taumin
                                tauVdep
                                tauPow
                                tauVhalf
                                tauVslope''')

Na_m_params = SSTauChannelParams(Arate = 1.0,
                                 A_B = 0.0,
                                 A_C = 1.0,
                                 Avhalf = 25e-3,
                                 Avslope = -10e-3,
                                 taumin = 0.1e-3,
                                 tauVdep = 1.45e-3,
                                 tauPow = 2,
                                 tauVhalf = 62e-3,
                                 tauVslope = 8e-3)
Na_h_params = SSTauChannelParams(Arate = 1.0,
                                 A_B = 0.0,
                                 A_C = 1.0,
                                 Avhalf = 60e-3,
                                 Avslope = 6e-3,
                                 taumin = 0.2754e-3,
                                 tauVdep = 1.2e-3,
                                 tauPow = 1,
                                 tauVhalf = 42e-3,
                                 tauVslope = 3e-3)

ChannelSettings = namedtuple('ChannelSettings', 'Xpow Ypow Zpow Erev name')
NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')

#This is from Migliore.
KDrparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='KDr')

AlphaBetaChannelParams = namedtuple('AlphaBetaChannelParams', '''
                              A_rate
                              A_B
                              A_C
                              Avhalf
                              A_vslope
                              B_rate
                              B_B
                              B_C
                              Bvhalf
                              B_vslope''')

KDr_X_params = AlphaBetaChannelParams(A_rate = 28.2,
                                      A_B = 0,
                                      A_C = 0.0,
                                      Avhalf = 0,
                                      A_vslope = -12.5e-3,
                                      B_rate = 6.78,
                                      B_B = 0.0,
                                      B_C = 0.0,
                                      Bvhalf = 0.0,
                                      B_vslope = 33.5e-3)
KDr_Y_params = []

Krpparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='Krp')

#Act tuned to fit Nisenbaum 1996 fig6C (minf^2) and fig 8C (mtau)
qfactKrp=3  #Used by RE

Krp_X_params = AlphaBetaChannelParams(A_rate = 16*qfactKrp,
                                      A_B = 0,
                                      A_C = 0.0,
                                      Avhalf = 0,
                                      A_vslope = -24e-3,
                                      B_rate = 2.4*qfactKrp,
                                      B_B = 0.0,
                                      B_C = 0.0,
                                      Bvhalf = 0.0,
                                      B_vslope = 45e-3)

# tuned to fit Nisenbaum 1996 fig 9D (hinf, 87% inactivating) and 9B (htau)
Krp_Y_params = AlphaBetaChannelParams(A_rate = 0.01*qfactKrp,
                                      A_B = 0,
                                      A_C = 0.0,
                                      Avhalf = 0,
                                      A_vslope = 100e-3,
                                      B_rate = 0.4*qfactKrp,
                                      B_B = 0.0,
                                      B_C = 0.0,
                                      Bvhalf = 0.0,
                                      B_vslope = -18e-3)

Kirparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='Kir')
qfactKir = 0.5

Kir_X_params = AlphaBetaChannelParams(A_rate = 0.01*qfactKir,
                                      A_B = 0,
                                      A_C = 0.0,
                                      Avhalf = 0,
                                      A_vslope = 11e-3,
                                      B_rate = 1.2e3*qfactKir,
                                      B_B = 0.0,
                                      B_C = 1.0,
                                      Bvhalf = -30e-3,
                                      B_vslope = -50e-3)

KaFparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KaF')

# activation constants for alphas and betas (obtained by
# matching m2 to Tkatch et al., 2000 Figs 2c, and mtau to fig 2b)

qfactKaF = 1.5
KaF_X_params = AlphaBetaChannelParams(A_rate = 1.8e3*qfactKaF,
                                      A_B = 0,
                                      A_C = 1.0,
                                      Avhalf = 18e-3,
                                      A_vslope = -13.0e-3,
                                      B_rate = 0.45e3*qfactKaF,
                                      B_B = 0.0,
                                      B_C = 1.0,
                                      Bvhalf = -2.0e-3,
                                      B_vslope = 11.0e-3)

#inactivation consts for alphas and betas obtained by matching Tkatch et al., 2000 Fig 3b,
#and tau voltage dependence consistent with their value for V=0 in fig 3c.
#slowing down inact improves spike shape tremendously
KaF_Y_params = AlphaBetaChannelParams(A_rate = 0.105e3/qfactKaF,
                                      A_B = 0,
                                      A_C = 1.0,
                                      Avhalf = 121e-3,
                                      A_vslope = 22.0e-3,
                                      B_rate = 0.065e3/qfactKaF,
                                      B_B = 0.0,
                                      B_C = 1.0,
                                      Bvhalf = 55.0e-3,
                                      B_vslope = -11.0e-3)

KaSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KaS')
qfactKaS = 2
KaS_X_params = AlphaBetaChannelParams(A_rate = 250*qfactKaS,
                                      A_B = 0,
                                      A_C = 1.0,
                                      Avhalf = -54e-3,
                                      A_vslope = -22.0e-3,
                                      B_rate = 50*qfactKaS,
                                      B_B = 0.0,
                                      B_C = 1.0,
                                      Bvhalf = 100e-3,
                                      B_vslope = 35e-3)

KaS_Y_params = AlphaBetaChannelParams(A_rate = 2.5*qfactKaS,
                                      A_B = 0,
                                      A_C = 1.0,
                                      Avhalf = 95e-3,
                                      A_vslope = 16.0e-3,
                                      B_rate = 2.0*qfactKaS,
                                      B_B = 0.0,
                                      B_C = 1.0,
                                      Bvhalf = -50.0e-3,
                                      B_vslope = -70.0e-3)

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
CaL12param = ChannelSettings(Xpow=1, Ypow=0, Zpow=ZpowCDI, Erev=carev, name='CaL12')
qfactCaL = 1
CaL12_X_params = AlphaBetaChannelParams(A_rate = -880*qfactCaL,
                                        A_B = -220e3*qfactCaL,
                                        A_C = -1.0,
                                        Avhalf = 4.00003e-3,
                                        A_vslope = -7.5e-3,
                                        B_rate = -284*qfactCaL,
                                        B_B = 71e3*qfactCaL,
                                        B_C = -1.0,
                                        Bvhalf = -4.00003e-3,
                                        B_vslope = 5e-3)

# Using Xpow=1 produced too high a basal calcium,
# so used Xpow=2 and retuned params - much better basal calcium
CaL13param = ChannelSettings(Xpow=2, Ypow=0, Zpow=ZpowCDI, Erev=carev, name='CaL13')
CaL13_X_params = AlphaBetaChannelParams(A_rate = 1500*qfactCaL,
                                        A_B = 0,
                                        A_C = 1.0,
                                        Avhalf = -5.0e-3,
                                        A_vslope = -25.0e-3,
                                        B_rate =  2000*qfactCaL,
                                        B_B = 0,
                                        B_C = 1.0,
                                        Bvhalf = 52e-3,
                                        B_vslope = 6.5e-3)

#Params from McRory J Biol Chem, alpha1I subunit
CaTparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=ZpowCDI, Erev=carev, name='CaT')
qfactCaT = 2
CaT_X_params = AlphaBetaChannelParams(A_rate = 1000*qfactCaT,
                                      A_B = 0.0,
                                      A_C = 0.0,
                                      Avhalf = 0.0,
                                      A_vslope = -19e-3,
                                      B_rate = 1340*qfactCaT,
                                      B_B = 16500*qfactCaT,
                                      B_C = -1.0,
                                      Bvhalf = 81e-3,
                                      B_vslope = 7.12e-3)

#Original inactivation ws too slow compared to activation, made closder the alpha1G
CaT_Y_params = AlphaBetaChannelParams(A_rate = 3840*qfactCaT,
                                      A_B = 34000*qfactCaT,
                                      A_C = -1.0,
                                      Avhalf = 113.0e-3,
                                      A_vslope = 5.12e-3,
                                      B_rate = 320*qfactCaT,
                                      B_B = 0,
                                      B_C = 0.0,
                                      Bvhalf = 0.0,
                                      B_vslope = -17e-3)

# CaN SS parameters tuned so m2 fits Bargas and Surmeier 1994 boltzmann curve
# CaN tau from kasai 1992.
# Kasai measures calcium dependent inactivation
#McNaughton has act and inact, tau and ss for human CaN
CaNparam = ChannelSettings(Xpow=2, Ypow=0, Zpow=ZpowCDI, Erev=carev, name='CaN')
qfactCaN = 2
CaN_X_params = AlphaBetaChannelParams(A_rate = 304.2*qfactCaN,
                                      A_B = 0,
                                      A_C = 0.0,
                                      Avhalf = 0.0,
                                      A_vslope = -14.0e-3,
                                      B_rate = 749*qfactCaN,
                                      B_B = 52800*qfactCaN,
                                      B_C = -1.0,
                                      Bvhalf = 14.2e-3,
                                      B_vslope = 10e-3)

# CaR SS (Act and Inact) parameters from Foerhing et al., 2000
# Was Xpow=3 taken into account during fit?
# CaR tau from a few measurements from pyramidal neurons by Foerhing
# CaR inact tau from Brevi 2001
#Inact params are a bit too steep for ss, and not steep enough for tau
CaRparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=ZpowCDI, Erev=carev, name='CaN')
qfactCaR = 2
CaR_X_params = AlphaBetaChannelParams(A_rate = 240*qfactCaR,
                                      A_B =    0,
                                      A_C =  0.0,
                                      Avhalf =  0.0,
                                      A_vslope = -28.0e-3,
                                      B_rate = 1.26e6*qfactCaR,
                                      B_B = 8e6*qfactCaR,
                                      B_C = -1.0,
                                      Bvhalf = 158e-3,
                                      B_vslope = 13.6e-3)

CaR_Y_params = AlphaBetaChannelParams(A_rate = 1100*qfactCaR,
                                      A_B = 10000*qfactCaR,
                                      A_C = -1.0,
                                      Avhalf = 0.11,
                                      A_vslope = 17e-3,
                                      B_rate = 20*qfactCaR,
                                      B_B = 0,
                                      B_C = 0.0,
                                      Bvhalf = 0.0,
                                      B_vslope = -30.0e-3)

#Reference: Maylie Bond Herson Lee Adelman 2004, Fig 2 steady state
#Fast component has tau~4 ms; not used: slow tau = 70 ms
#Fast component, tau=4.9ms from Hirschberg et al., 1998 figure 13.
SKparam = ChannelSettings(Xpow=0, Ypow=0, Zpow=1, Erev=krev, name='SKCa')

ZChannelParams = namedtuple('ZChannelParams', 'Kd power tau')

SK_Z_params = ZChannelParams(Kd = 0.57e-3,
                             power = 5.2,
                             tau = 4.9e-3)

BKparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='BKCa')
BKChannelParams=namedtuple('BKChannelParams', 'alphabeta K delta')

BK_X_params=[BKChannelParams(alphabeta=480, K=0.18,delta=-0.84),
             BKChannelParams(alphabeta=280,K=0.011,delta=-1.0)]
#These CDI params can be used with every channel, make ZpowCDI=2
#If ZpowCDI=0 the CDI will not be used, power=-4 is to transform
#(Ca/Kd)^pow/(1+(Ca/Kd)^pow) to 1/(1+(ca/Kd)^-pow)
CDI_Z_params = ZChannelParams(Kd = 0.12e-3,
                              power = -4,
                              tau = 142e-3)
#
#Dictionary of "standard" channels, to create channels using a loop
#NaF doesn't fit since it uses different prototype form
#will need separate dictionary for BK
XChanDict={'Krp':Krp_X_params,
           'KaF':KaF_X_params,
           'KaS':KaS_X_params,
           'Kir': Kir_X_params,
           'CaL12': CaL12_X_params,
           'CaL13': CaL13_X_params,
           'CaN': CaN_X_params,
           'CaR': CaR_X_params,
           'CaT': CaT_X_params,
           'SKCa': []}
#
YChanDict={'Krp':Krp_Y_params,
           'KaF':KaF_Y_params,
           'KaS':KaS_Y_params,
           'Kir': [],
           'CaL12': [],
           'CaL13': [],
           'CaN': [],
           'CaR': CaR_Y_params,
           'CaT': CaT_Y_params,
           'SKCa': []}
#
ZChanDict={'SKCa':SK_Z_params,
           'CaL12': CDI_Z_params,
           'CaL13': CDI_Z_params,
           'CaN': CDI_Z_params,
           'CaR': CDI_Z_params,
           'CaT': CDI_Z_params
}
#
ChanDict={'Krp':Krpparam,
          'KaF':KaFparam,
          'KaS':KaSparam,
          'Kir': Kirparam,
          'CaL12': CaL12param,
          'CaL13': CaL13param,
          'CaN': CaNparam,
          'CaR': CaRparam,
          'CaT': CaTparam,
          'SKCa': SKparam
}
