# -*- coding: utf-8 -*-

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
#Parameters for Ca channels may need to be shifted - see Dorman model
krev=-9e-3
narev=50e-3
carev=0.14 #assumes CaExt=2 mM and CaIn=50e-3
ZpowCDI = 1

VMIN = -120e-3
VMAX = 50e-3
VDIVS = 3401 #0.5 mV steps
CAMIN=0.01e-3   #10 nM
CAMAX=40e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS=4001 #10 nM steps

#mtau: Ogata fig 5, no qfactor accounted in mtau, 1.2 will improve spike shape
#activation minf fits Ogata 1990 figure 3C (which is cubed root)
#inactivation hinf fits Ogata 1990 figure 6B
#htau fits the main -50 through -10 slope of Ogata figure 9 (log tau), but a qfact of 2 is already taken into account.

qfactNaF = 1.3

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

NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')

#This is from Migliore.
KDrparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='KDr')

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
                                      A_vslope = -20e-3,
                                      B_rate = 2.4*qfactKrp,
                                      B_B = 0.0,
                                      B_C = 0.0,
                                      Bvhalf = 0.0,
                                      B_vslope = 40e-3)

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
qfactKir = 1

Kir_X_params = AlphaBetaChannelParams(A_rate = 0.008*qfactKir,
                                      A_B = 0,
                                      A_C = 0.0,
                                      Avhalf = 0,
                                      A_vslope = 11.0e-3,
                                      B_rate = 1000*qfactKir,
                                      B_B = 0.0,
                                      B_C = 1.0,
                                      Bvhalf = -40e-3,
                                      B_vslope = -40e-3)

KaFparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KaF')

# activation constants for alphas and betas (obtained by
# matching m2 to Tkatch et al., 2000 Figs 2c, and mtau to fig 2b)

qfactKaF = 2
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
CaL12param = ChannelSettings(Xpow=1, Ypow=1, Zpow=ZpowCDI, Erev=carev, name='CaL12')
qfactCaL = 2
CaL12_X_params = AlphaBetaChannelParams(A_rate = -110000.0*.00399*qfactCaL,#Checked JJS
                                        A_B = -110000.0*qfactCaL,
                                        A_C = -1.0,
                                        Avhalf = 3.99e-3,
                                        A_vslope = -7.5e-3,
                                        B_rate = -35500.0*.00399*qfactCaL,
                                        B_B = 35500.0*qfactCaL,
                                        B_C = -1.0,
                                        Bvhalf = -3.99e-3,
                                        B_vslope = 5e-3)

CaL12_X_params = AlphaBetaChannelParams(A_rate = -219.45*qfactCaL,#TODO
                                        A_B = -55000*qfactCaL,
                                        A_C = -1.0,
                                        Avhalf = 3.99e-3,
                                        A_vslope = -7.5e-3,
                                        B_rate = 70.82*qfactCaL,
                                        B_B = 17750*qfactCaL,
                                        B_C = -1.0,
                                        Bvhalf = -3.99e-3,
                                        B_vslope = 5e-3)

# Using Xpow=1 produced too high a basal calcium,
# so used Xpow=2 and retuned params - much better basal calcium 
CaL13param = ChannelSettings(Xpow=1, Ypow=1, Zpow=ZpowCDI, Erev=carev, name='CaL13')
CaL13_X_params = AlphaBetaChannelParams(A_rate = 1500*qfactCaL, #Checked JJS
                                        A_B = 0,
                                        A_C = 1.0,
                                        Avhalf = -5.0e-3,
                                        A_vslope = -25.0e-3,
                                        B_rate =  2000*qfactCaL,
                                        B_B = 0,
                                        B_C = 1.0,
                                        Bvhalf = 52e-3,
                                        B_vslope = 7e-3)
CaL13_Y_params = AlphaBetaChannelParams(A_rate = 42.2*qfactCaL, #Checked JJS
                                        A_B = -8.1,
                                        A_C = 1.9,
                                        Avhalf = 40e-3,
                                        A_vslope = 5.0e-3,
                                        B_rate =  45*qfactCaL,
                                        B_B = 8.0,
                                        B_C = 2.0,
                                        Bvhalf = 34e-3,
                                        B_vslope = -5.0e-3)
#Params from McRory J Biol Chem, alpha1I subunit
CaTparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=ZpowCDI, Erev=carev, name='CaT')
qfactCaT = 2
CaT_X_params = AlphaBetaChannelParams(A_rate = 5342.5*qfactCaT,
                                      A_B = 2100*qfactCaT,
                                      A_C = 11.9,
                                      Avhalf = 1e-3,
                                      A_vslope = -12e-3,
                                      B_rate = 289.7*qfactCaT,
                                      B_B = 0.,
                                      B_C = 1.,
                                      Bvhalf = 0.0969,
                                      B_vslope = 0.0141)

#Original inactivation ws too slow compared to activation, made closder the alpha1G

CaT_Y_params = AlphaBetaChannelParams(A_rate = 0*qfactCaT,
                                      A_B = -74.,
                                      A_C = 1,
                                      Avhalf = 0.09,
                                      A_vslope = 5e-3,
                                      B_rate = 15*qfactCaT,
                                      B_B = -1.5*qfactCaT,
                                      B_C = 1.5,
                                      Bvhalf = 50e-3,
                                      B_vslope = -15e-3)
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
                                      Bvhalf = 14.20003e-3,
                                      B_vslope = 10e-3)

# CaR SS (Act and Inact) parameters from Foerhing et al., 2000
# Was Xpow=3 taken into account during fit?
# CaR tau from a few measurements from pyramidal neurons by Foerhing
# CaR inact tau from Brevi 2001
#Inact params are a bit too steep for ss, and not steep enough for tau
CaRparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=ZpowCDI, Erev=carev, name='CaR')
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

SK_Z_params = ZChannelParams(Kd = 0.57e-3,
                             power = 5.2,
                             tau = 4.9e-3)

BKparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='BKCa')

BK_X_params=[BKChannelParams(alphabeta=480, K=0.18, delta=-0.84),
             BKChannelParams(alphabeta=280, K=0.011, delta=-1.0)]
#These CDI params can be used with every channel, make ZpowCDI=2
#If ZpowCDI=0 the CDI will not be used, power=-4 is to transform
#(Ca/Kd)^pow/(1+(Ca/Kd)^pow) to 1/(1+(ca/Kd)^-pow) Why 2? JJS
CDI_Z_params = ZChannelParams(Kd = 0.12e-3,
                              power = -4,
                              tau = 142e-3)

#Dictionary of "standard" channels, to create channels using a loop
#NaF doesn't fit since it uses different prototype form
#will need separate dictionary for BK

ChanDict = NamedDict(
    'ChannelParams',
    Krp =   TypicalOneDalpha(Krpparam, Krp_X_params, Krp_Y_params),
    KaF =   TypicalOneDalpha(KaFparam, KaF_X_params, KaF_Y_params),
    KaS =   TypicalOneDalpha(KaSparam, KaS_X_params, KaS_Y_params),
    Kir =   TypicalOneDalpha(Kirparam,  Kir_X_params, []),
    CaL12 = TypicalOneDalpha(CaL12param, CaL12_X_params, CaL12_Y_params, CDI_Z_params, calciumPermeable=True),
    CaL13 = TypicalOneDalpha(CaL13param, CaL13_X_params, CaL12_Y_params, CDI_Z_params, calciumPermeable=True),
    CaN =   TypicalOneDalpha(CaNparam, CaN_X_params, [], CDI_Z_params, calciumPermeable=True),
    CaR =   TypicalOneDalpha(CaRparam, CaR_X_params, CaR_Y_params, CDI_Z_params, calciumPermeable=True),
    CaT =   TypicalOneDalpha(CaTparam, CaT_X_params, CaT_Y_params, CDI_Z_params, calciumPermeable=True),
    SKCa =  TypicalOneDalpha(SKparam, [], [], SK_Z_params, calciumDependent=True),
    NaF =   AtypicalOneD(NaFparam, Na_m_params, Na_h_params),
    BKCa =  TwoD(BKparam, BK_X_params, calciumDependent=True),
)
