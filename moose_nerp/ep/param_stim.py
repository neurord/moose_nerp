from moose_nerp.prototypes.inject_func import ParadigmParams, StimParams, StimLocParams


example_pulse_seqeunce = {1:[0,1],2:[2,3],3:[0,1]}

#UNITS: frequency (f_pulse,f_burst,f_train) in Hz; width_AP, AP_interval, and ISI : sec; A_inject: Amps, n (n_pulse,n_burst,n_train,n_AP) dimensionless
AP_1 =  ParadigmParams(f_pulse=50., n_pulse=1, A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=1, ISI=-0.040, name="1_AP")
PSP_1 = ParadigmParams(f_pulse = 1., n_pulse=1,A_inject=0e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="1_PSP")

TestPlas = ParadigmParams(f_pulse = 5, n_pulse = 3,A_inject=0, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="TestPlas")

inject = ParadigmParams(f_pulse = 5, n_pulse = 0,A_inject=0.25e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.5, AP_interval=0.01, n_AP=0, ISI=0, name="inject")

PSP_1Hz=ParadigmParams(f_pulse = 1., n_pulse=10,A_inject=0e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="PSP_1Hz")
PSP_5Hz=ParadigmParams(f_pulse = 5., n_pulse=10,A_inject=0e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="PSP_5Hz")
PSP_10Hz=ParadigmParams(f_pulse = 10., n_pulse=10,A_inject=0e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="PSP_10Hz")
PSP_20Hz=ParadigmParams(f_pulse = 20., n_pulse=20,A_inject=0e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="PSP_20Hz")
PSP_40Hz=ParadigmParams(f_pulse = 40., n_pulse=40,A_inject=0e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="PSP_40Hz")
PSP_100Hz=ParadigmParams(f_pulse = 100., n_pulse=100,A_inject=0e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.005, AP_interval=0.01, n_AP=0, ISI=0, name="PSP_100Hz")

#n_AP is number of AP per PSP input pulse, AP_interval dicates frequency of AP when n_AP>1
#set ISI to large negative number to avoid observing any PSPs
AP_10Hz =  ParadigmParams(f_pulse=1., n_pulse=0, A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.001, AP_interval=0.1, n_AP=20, ISI=0, name="AP_10Hz")
AP_20Hz =  ParadigmParams(f_pulse=1., n_pulse=0, A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.001, AP_interval=0.05, n_AP=40, ISI=0, name="AP_10Hz")
AP_40Hz =  ParadigmParams(f_pulse=1., n_pulse=0, A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.001, AP_interval=0.025, n_AP=80, ISI=0, name="AP_10Hz")
AP_50Hz =  ParadigmParams(f_pulse=1., n_pulse=0, A_inject=1e-9, f_burst=1, n_burst=1, f_train=1, n_train=1, width_AP=0.001, AP_interval=0.02, n_AP=100, ISI=0, name="AP_10Hz")


#This list is required to assign different stim paradigms if specified by the arg_parser
paradigm_dict={'inject':inject,
               'TestPlas':TestPlas,
               'AP_1': AP_1,
               'AP_10Hz': AP_10Hz,
               'AP_20Hz': AP_20Hz,
               'AP_40Hz': AP_40Hz,
               'AP_50Hz': AP_50Hz,
               'PSP_1': PSP_1,
               'PSP_1Hz': PSP_1Hz,
               'PSP_5Hz': PSP_5Hz,
               'PSP_10Hz': PSP_10Hz,
               'PSP_20Hz': PSP_20Hz,
               'PSP_40Hz': PSP_40Hz,
               'PSP_100Hz': PSP_100Hz}

#stim_dendrite list must correspond to dendrites in morphology.p
#spine_density units: fraction of spines connected in specified compartments
#if zero, will connect directly to dendrite, but must specify syntype
location={}
#['p0b1b1b2','p1_2a','p2b2b2','p2b2b1']
location['str']=StimLocParams(which_spines='all',spine_density = 0.0, pulse_sequence=None,  stim_dendrites=['p2b2b1'],syntype='gaba')
location['GPe']=StimLocParams(which_spines='all',spine_density = 0.0, pulse_sequence=None,  stim_dendrites=['p0b1','p1_1a','p2b2a'],syntype='gaba',weight=2)

#stim_delay units: sec
Stimulation = StimParams(Paradigm = PSP_100Hz,stim_delay = 2,StimLoc=location['GPe'])

#pulse sequence should be of the form:
#{1:[0,1],2:[2,3],3:[0,1]} -- for each pulse specify a list of spines to stimulate
