from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes.chan_proto import AlphaBetaChannelParams
from moose_nerp.prototypes.chan_proto import ChannelSettings
from moose_nerp.prototypes.chan_proto import TypicalOneD
from moose_nerp.prototypes.chan_proto import TauInfMinChannelParams
from moose_nerp.prototypes.chan_proto import ZChannelParams

EREST_ACT = -70e-3 # units(Volts) # Neuron resting potential.

# Measures are in SI units.
krev=-12e-3  + EREST_ACT # units(Volts) # E_k Nernst reversal potential for Potassium.
narev=115e-3 + EREST_ACT # units(Volts) # E_Na Nernst reversal potential for Sodium.

# Below are not used in simulaton of squid
CAMIN = 0.01e-3   #10 nM
CAMAX = 60e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS = 5999 #10 nM steps
qfactNaF = 1.0
# End of not used variables

VMIN = -100e-3 # units(Volts) # Minimun allowed membrane potential.
VMAX = 50e-3 # units(Volts) # Maximum allowed membrane potential.
VDIVS = 3000 # No units # Range of VMIN to VMAX is equally split in VDIVS sections. # 0.5 mV steps

# contains all gating parameters and reversal potentials
# Gate equations have the form:
# AlphaBetaChannelParams (specify forward and backward transition rates):
# alpha(v) or beta(v) = (rate + B * v) / (C + exp((v + vhalf) / vslope))
# descrition: alpha(v)/beta(v) are the implicit Action potential driving equations.
#             alpha(v)/beta(v) equations adjustes the steady states[SS](alpha(v)/(alpha(v) + beta(v))
#             and time constants (1/(alpha(v) + beta(v))).
# m,h,n are HH-channel gating variables
Na_m_params = AlphaBetaChannelParams(A_rate = -1e5 *(-25e-3 - EREST_ACT),
                                      A_B = -1e5,
                                      A_C = -1.0,
                                      A_vhalf = -25e-3 - EREST_ACT,
                                      A_vslope = -10e-3,
                                      B_rate = 4e3,
                                      B_B = 0.0,
                                      B_C = 0.0,
                                      B_vhalf = 0.0 - EREST_ACT,
                                      B_vslope = 18e-3)

Na_h_params = AlphaBetaChannelParams(A_rate = 70,
                                      A_B = 0.0,
                                      A_C = 0.0,
                                      A_vhalf = 0.0 - EREST_ACT,
                                      A_vslope = 0.02,
                                      B_rate = 1000.0,
                                      B_B = 0.0,
                                      B_C = 1.0,
                                      B_vhalf = -30e-3 - EREST_ACT,
                                      B_vslope = -0.01)

NaSparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='Na')

K_n_params = AlphaBetaChannelParams(A_rate = -1e4*(-10e-3 - EREST_ACT),
                                      A_B = -1e4,
                                      A_C = -1.0,
                                      A_vhalf = -10e-3 - EREST_ACT,
                                      A_vslope = -10e-3,
                                      B_rate = 0.125e3,
                                      B_B = 0.0,
                                      B_C = 0.0,
                                      B_vhalf = 0.0 - EREST_ACT,
                                      B_vslope = 80e-3)

KSparam = ChannelSettings(Xpow=4, Ypow=0, Zpow=0, Erev=krev, name='K')

Krp_X_params = AlphaBetaChannelParams(A_rate = 16,
                                      A_B = 0,
                                      A_C = 0.0,
                                      A_vhalf = 0,
                                      A_vslope = -20e-3,
                                      B_rate = 2.4,
                                      B_B = 0.0,
                                      B_C = 0.0,
                                      B_vhalf = 0.0,
                                      B_vslope = 40e-3)

Krp_Y_params = TauInfMinChannelParams(T_min = 0.287,
                                    T_vdep = 4.16,
                                    T_vhalf = -0.042,
                                    T_vslope = 0.013,
                                    SS_min = 0.13,
                                    SS_vdep = 0.87,
                                    SS_vhalf = -0.056,
                                    SS_vslope = 0.014)

Krpparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='Krp')


SK_Z_params = ZChannelParams(Kd=0.00035,
                             power=4.6,
                             tau=0.002,
                             taumax=0.0037928,
                             tau_power=4.3,
                             cahalf=0.002703
                             )

SKparam = ChannelSettings(Xpow=0, Ypow=0, Zpow=1, Erev=krev, name='SKCa')

Channels = NamedDict(
    'Channels',
    Na = TypicalOneD(NaSparam, Na_m_params, Na_h_params),
    K =  TypicalOneD(KSparam, K_n_params, None),
    Krp = TypicalOneD(Krpparam, Krp_X_params,Krp_Y_params),
    SKCa =TypicalOneD(SKparam, [], [], SK_Z_params, calciumDependent=True)
)
