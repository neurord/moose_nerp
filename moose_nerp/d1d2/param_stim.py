from moose_nerp.prototypes.inject_func import ParadigmParams, StimParams


example_pulse_seqeunce = {1:[0,1],2:[2,3],3:[0,1]}

Fino_Pre = ParadigmParams( f_pulse=50., n_pulse=1, A_inject=0.38e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.030, AP_interval=0.01, n_AP=1, ISI=-0.010, name="Fino_Pre")
Fino_Post = ParadigmParams( f_pulse=50., n_pulse=1, A_inject=0.38e-9, f_burst=1, n_burst=1, f_train=1, n_train=100, width_AP=0.030, AP_interval=0.01, n_AP=1, ISI=-0.040, name="Fino_Pre")

AP_1 =  ParadigmParams(f_pulse=50., n_pulse=1, A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=1, ISI=-0.040, name="1_AP")
PSP_1 = ParadigmParams(f_pulse = 1., n_pulse=1,A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="1_PSP")

PSP_20_Hz = ParadigmParams(f_pulse = 20., n_pulse = 20,A_inject=0, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="20_Hz")

PSP_100_Hz = ParadigmParams(f_pulse = 100., n_pulse = 100,A_inject=0, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="100_Hz")

Kerr_and_Plenz = ParadigmParams(f_pulse = 100, n_pulse = 0,A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.1, n_AP=5, ISI=0, name="Kerr_and_Plenz")

Pawlak_and_Kerr_Pre = ParadigmParams(f_pulse = 50, n_pulse = 1,A_inject=1e-9, f_burst=1, n_burst=1, f_train=0.1, n_train=60, width_AP=0.005, AP_interval=1./50., n_AP=3, ISI=0.01, name="Pawlak_and_Kerr_Pre")

Pawlak_and_Kerr_Post = ParadigmParams(f_pulse = 50, n_pulse = 1,A_inject=1e-9, f_burst=1, n_burst=1, f_train=0.1, n_train=60, width_AP=0.005, AP_interval=1./50., n_AP=3, ISI=-0.03, name="Pawlak and_Kerr_Post")

Pawlak_and_Kerr_1_AP_Pre = ParadigmParams(f_pulse = 50, n_pulse = 1.,A_inject=1e-9, f_burst=1, n_burst=1, f_train=0.1, n_train=60, width_AP=0.005, AP_interval=1./50., n_AP=1, ISI=0.01, name="Pawlak_and_Kerr_1_AP_Pre")

Pawlak_and_Kerr_1_AP_Post = ParadigmParams(f_pulse = 50, n_pulse = 1.,A_inject=1e-9, f_burst=1, n_burst=1, f_train=0.1, n_train=60, width_AP=0.005, AP_interval=1./50., n_AP=1, ISI=-0.03, name="Pawlak_and_Kerr_1_AP_Post")

Shen_Pre = ParadigmParams(f_pulse = 50., n_pulse = 3,A_inject=1e-9, f_burst=5, n_burst=5, f_train=0.1, n_train=10, width_AP=0.005, AP_interval=1./50., n_AP=3, ISI=0.005, name="Shen_Pre")

Shen_Post = ParadigmParams(f_pulse = 50., n_pulse = 1,A_inject=1e-9, f_burst=5, n_burst=5, f_train=0.1, n_train=10, width_AP=0.005, AP_interval=1./50., n_AP=3, ISI=-0.01, name="Shen_Post")

TBS =  ParadigmParams(f_pulse = 50., n_pulse = 4,A_inject=0, f_burst=8, n_burst=10, f_train=0.1, n_train=1, width_AP=1.1, AP_interval=2., n_AP=1, ISI=0, name="TBS")


Stimulation = StimParams(Paradigm = TBS,which_spines='all',spine_density = 0.2,stim_delay = 0.02,pulse_sequence=None,
                         stim_dendrites=['tertdend1_1'])


#pulse sequence should be of the form:
#{1:[0,1],2:[2,3],3:[0,1]} -- for each pulse specify a list of spines to stimulate
