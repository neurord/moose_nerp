from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes.chan_proto import AlphaBetaChannelParams
from moose_nerp.prototypes.chan_proto import ChannelSettings
from moose_nerp.prototypes.chan_proto import TypicalOneD

#import engineering_notation as eng

#EREST_ACT = float(eng.EngUnit('-70mV')) #Neuron resting potential
EREST_ACT = -70e-3

# Measures are in SI units.
#krev=float(eng.EngUnit('-12mV'))  + EREST_ACT # units(Volts) # E_k Nernst reversal potential for Potassium.
krev=-12e-3  + EREST_ACT
#narev=float(eng.EngUnit('115mV')) + EREST_ACT # units(Volts) # E_Na Nernst reversal potential for Sodium.
narev=115e-3 + EREST_ACT

# Below are not used in simulaton of squid
CAMIN = 0.01e-3   #10 nM
CAMAX = 60e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS = 5999 #10 nM steps
qfactNaF = 1.0
# End of not used variables

#VMIN = float(eng.EngUnit('-100mV')) # Minimun allowed membrane potential.
VMIN = -100e-3
#VMAX = float(eng.EngUnit('50mV')) # Maximum allowed membrane potential.
VMAX = 50e-3
VDIVS = 3000 #0.5 mV steps

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

Channels = NamedDict(
    'Channels',
    Na = TypicalOneD(NaSparam, Na_m_params, Na_h_params),
    K =  TypicalOneD(KSparam, K_n_params, None)
)

# 29th MAY 2018 meeting points.
# current optimazation does conductances
# Future and my part channel parameter optimization.
# read a 2 manuscripts a week. !!!!! VERY IMPORTANT.

#READ paper
# Hourglass method. (broaden - focus - broad summary)
# First Read just introduction first.
# Second
# Third summary.
# Rule of thumb is 3 refereces to discussion.

# Presentations focus on the big picture.( main message)
# How do the figures support the main results
# Has the author left any details regarding paper.
