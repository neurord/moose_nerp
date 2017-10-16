# -*- coding: utf-8 -*-

from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes.chan_proto import (
    AlphaBetaChannelParams,
    ZChannelParams,
    BKChannelParams,
    ChannelSettings,
    TypicalOneD,
    TwoD)

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
krev=-87e-3
narev=50e-3
carev=48e-3 #assumes CaExt=2 mM and CaIn=50e-3
ZpowCDI=2

VMIN = -120e-3
VMAX = 50e-3
VDIVS = 3401 #0.5 mV steps
CAMIN = 0.01e-3   #10 nM
CAMAX = 40e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS = 4001 #10 nM steps

kDr_X_params= AlphaBetaChannelParams (
    A_rate=6.5,
    A_B=0,
    A_C=0,
    A_vhalf=0,
    A_vslope=-12.5e-3,
    B_rate=24,
    B_B=0,
    B_C=0,
    B_vhalf=0,
    B_vslope=33.5e-3)

kDr_Y_params=[]

kDrparams=ChannelSettings(Xpow=1,Ypow=0,Zpow=0,Erev=-0.09,name='kDr')

KAdist_m_params= AlphaBetaChannelParams (
    A_rate=0.7,
    A_B=0,
    A_C=0,
    A_vhalf=0,
    A_vslope=-50e-3,
    B_rate=0.15,
    B_B=0,
    B_C=0,
    B_vhalf=-30.1001e-3,
    B_vslope=9e-3)

KAdist_h_params= AlphaBetaChannelParams (
    A_rate=17,
    A_B=0,
    A_C=0,
    A_vhalf=-95.1001e-3,
    A_vslope=14e-3,
    B_rate=10,
    B_B=0,
    B_C=0,
    B_vhalf=0,
    B_vslope=25e-3)

KAdistparams=ChannelSettings(Xpow=2,Ypow=1,Zpow=0,Erev=-0.09,name='KAdist')

KAprox_m_params= AlphaBetaChannelParams (
    A_rate=0.375,
    A_B=0,
    A_C=0,
    A_vhalf=0,
    A_vslope=40e-3,
    B_rate=0.025,
    B_B=0,
    B_C=0,
    B_vhalf=-18.1001e-3,
    B_vslope=18e-3)

KAprox_h_params= AlphaBetaChannelParams (
    A_rate=17,
    A_B=0,
    A_C=0,
    A_vhalf=-95.1001e-3,
    A_vslope=14e-3,
    B_rate=10,
    B_B=0,
    B_C=0,
    B_vhalf=0,
    B_vslope=25e-3)

KAproxparams=ChannelSettings(Xpow=2,Ypow=1,Zpow=0,Erev=-0.09,name='KAprox')
# KD_x_params= AlphaBetaChannelParams (
#     A_rate=1,
#     A_B=0,
#     A_C=0,
#     A_vhalf=-63e-3,
#     A_vslope=3*0.0376583676871,
#     B_rate=1,
#     B_B=0,
#     B_C=0,
#     B_vhalf=-63e-3,
#     B_vslope=-3*0.0376583676871)

# KD_y_params= AlphaBetaChannelParams (
#     A_rate=17,
#     A_B=0,
#     A_C=0,
#     A_vhalf=-95.1001e-3,
#     A_vslope=14e-3,
#     B_rate=10,
#     B_B=0,
#     B_C=0,
#     B_vhalf=0, 
#     B_vslope=25e-3)


# KDparams=ChannelSettings(Xpow=2,Ypow=1,Zpow=0,Erev=-90e-3,name='KAdist',xparams=KD_x_params,yparams=KD_y_params,zparams=[])

qfactNaF = 1

Na_m_params= AlphaBetaChannelParams (
    A_rate=-12.0052e-3*2.14e6,
    A_B=-0.4*2.14e6,
    A_C=-1,
    A_vhalf=30.013e-3,
    A_vslope=-7.2e-3,
    B_rate=3.722e-3*2.14e6,
    B_B=0.124*2.14e6,
    B_C=-1,
    B_vhalf=30.013e-3,
    B_vslope=7.2e-3)



Na_h_params= AlphaBetaChannelParams (
    A_rate=(45.013e-3+15.0e-3)*0.03*2.14e6,
    A_B=0.03*2.14e6,
    A_C=-1,
    A_vhalf=45.013e-3+15e-3,
    A_vslope=3.5e-3,
    B_rate=-(45.013e-3+15e-3)*0.01*2.14e6,
    B_B=-0.01*2.14e6,
    B_C=-1,
    B_vhalf=45.013e-3+15e-3,
    B_vslope=-3.5e-3)


naFparams=ChannelSettings(Xpow=3,Ypow=1,Zpow=0,Erev=55.0e-3,name='NaF')


Channels = NamedDict(
    'Channels',
    Kdr =   TypicalOneD(kDrparams, kDr_X_params, kDr_Y_params),
    Kadist = TypicalOneD(KAdistparams, KAdist_m_params, KAdist_h_params),
    Kaprox = TypicalOneD(KAproxparams, KAprox_m_params, KAdist_h_params),
    Na = TypicalOneD(naFparams, Na_m_params, Na_h_params),




)
