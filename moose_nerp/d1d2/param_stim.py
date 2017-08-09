from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.util import NamedDict

#definitions -- description of a paradigm
#Prestim = 0 -- no presynaptic stimulation
#Prestim = 1 -- random choice of spines
#Prestim = 2 -- chosen spine sequence

ParadigmParams = NamedList('ParadigmParams','''
PreStim
f_pulse
n_pulse
A_inject
f_burst
n_burst
f_train
n_train
width_AP
AP_interval
n_AP
ISI''')

'''
which_spines -- which spines get stimulated.
If 'all' -- spines are randomly chosen with a probability of spine_density
if a sequencea list -- stimulated spines are randomly chosen from the list
stim_delay -- delay of the stimulation onset
pulse_sequence -- which spine gets which pulses
'''

StimParams = NamedList('PresynapticStimulation','''
Paradigm
which_spines
spine_density
pulse_sequence
stim_dendrites
phasic_GABA
phasic_GABA_delay
stim_delay
injection_compartment''')
                           
Fino_Pre = ParadigmParams(PreStim=2, f_pulse=50., n_pulse=1, A_inject=0.38e-9, f_burst=1, n_burst=1, f_train=1, n_train=10, width_AP=0.030, AP_interval=0.01, n_AP=1, ISI=-0.010)
Fino_Post = ParadigmParams(PreStim=2, f_pulse=50., n_pulse=1, A_inject=0.38e-9, f_burst=1, n_burst=1, f_train=1, n_train=100, width_AP=0.030, AP_interval=0.01, n_AP=1, ISI=-0.040)
AP_1 =  ParadigmParams(PreStim=0, f_pulse=50., n_pulse=1, A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=1, ISI=-0.040)
PSP_1 = ParadigmParams(PreStim=2,f_pulse = 1., n_pulse=1,A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0)

PSP_20_Hz = ParadigmParams(PreStim=2,f_pulse = 20., n_pulse = 20,A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0)

PSP_20_Hz = ParadigmParams(PreStim=2,f_pulse = 100., n_pulse = 100,A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0)

Kerr_and_Plenz = ParadigmParams(PreStim=0,f_pulse = 100, n_pulse = 0,A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.1, n_AP=5, ISI=0)

Pawlak_and_Kerr_Pre = ParadigmParams(PreStim=2,f_pulse = 50, n_pulse = 1,A_inject=1e-9, f_burst=1, n_burst=1, f_train=0.1, n_train=60, width_AP=0.005, AP_interval=1./50., n_AP=3, ISI=0.01)

Pawlak_and_Kerr_Post = ParadigmParams(PreStim=2,f_pulse = 50, n_pulse = 1,A_inject=1e-9, f_burst=1, n_burst=1, f_train=0.1, n_train=60, width_AP=0.005, AP_interval=1./50., n_AP=3, ISI=-0.03)

Pawlak_and_Kerr_1_AP_Pre = ParadigmParams(PreStim=2,f_pulse = 50, n_pulse = 1.,A_inject=1e-9, f_burst=1, n_burst=1, f_train=0.1, n_train=60, width_AP=0.005, AP_interval=1./50., n_AP=1, ISI=0.01)

Pawlak_and_Kerr_1_AP_Post = ParadigmParams(PreStim=2,f_pulse = 50, n_pulse = 1.,A_inject=1e-9, f_burst=1, n_burst=1, f_train=0.1, n_train=60, width_AP=0.005, AP_interval=1./50., n_AP=1, ISI=-0.03)

Shen_Pre = ParadigmParams(PreStim=2,f_pulse = 50., n_pulse = 3,A_inject=1e-9, f_burst=5, n_burst=5, f_train=0.1, n_train=10, width_AP=0.005, AP_interval=1./50., n_AP=3, ISI=0.005)

Shen_Post = ParadigmParams(PreStim=2,f_pulse = 50., n_pulse = 1,A_inject=1e-9, f_burst=5, n_burst=5, f_train=0.1, n_train=10, width_AP=0.005, AP_interval=1./50., n_AP=3, ISI=-0.01)

TBS =  ParadigmParams(PreStim=2,f_pulse = 50., n_pulse = 4,A_inject=.1e-9, f_burst=8, n_burst=10, f_train=0.1, n_train=1, width_AP=1.1, AP_interval=2., n_AP=1, ISI=0)


Stimulation = StimParams(Paradigm = Shen_Pre,which_spines='all',spine_density = 0.2,stim_delay = 0.2,pulse_sequence=None,
                         stim_dendrites=['tertdend1_1'],phasic_GABA=0,phasic_GABA_delay=0.02,injection_compartment="soma")
