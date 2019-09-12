#non-oscillatory input is firing too fast, ~50 Hz.  Need to decrease STN input or increase Str input
#a. reduce firing frequency of STN - DONE Now mean_ISI is 1/18.  Reduced from 50 Hz to 30 Hz - still too high
#b. reduce number of tt inputs per synapse: from 3 to 2 GOOD
#c. reduce conductance of tt inputs, e.g. from 0.25e-9 to 0.2e-9 NOT NEEDED

############## 16 sets of simulations to evaluate effect of input correlation on Str-EP cross correlation
#~6 hours each. 4/day, 4 days
#condition -n num_trials -syn syntype -stp stpYN -f stimfreq -ttGPe GPe_stim_file_root --ttstr str_stim_file_root
#if stimfreq is 0 and syntype is non, that means no single synapse regular stimulation
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.49 > GABA_non_0_stp1_GPe18_str_0.49.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.49 > POST-HFS_non_0_stp1_GPe18_str_0.49.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.64 > GABA_non_0_stp1_GPe18_str_0.64.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.64 > POST-HFS_non_0_stp1_GPe18_str_0.64.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.81 > GABA_non_0_stp1_GPe18_str_0.81.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.81 > POST-HFS_non_0_stp1_GPe18_str_0.81.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.90 > GABA_non_0_stp1_GPe18_str_0.90.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.90 > POST-HFS_non_0_stp1_GPe18_str_0.90.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.95 > GABA_non_0_stp1_GPe18_str_0.95.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.95 > POST-HFS_non_0_stp1_GPe18_str_0.95.log

#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.49 > GABA_non_0_stp1_GPe29_str_0.49.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.49 > POST-HFS_non_0_stp1_GPe29_str_0.49.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.64 > GABA_non_0_stp1_GPe29_str_0.64.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.64 > POST-HFS_non_0_stp1_GPe29_str_0.64.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.81 > GABA_non_0_stp1_GPe29_str_0.81.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.81 > POST-HFS_non_0_stp1_GPe29_str_0.81.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.90 > GABA_non_0_stp1_GPe29_str_0.90.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.90 > POST-HFS_non_0_stp1_GPe29_str_0.90.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.95 > GABA_non_0_stp1_GPe29_str_0.95.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.95 > POST-HFS_non_0_stp1_GPe29_str_0.95.log

#Test information processing with two striatal frequencies
#python3 ep_net/multisim.py -c GABAosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > GABAosc_non_0_stp1_GPe18_strf1.8_f5.0.log
#python3 ep_net/multisim.py -c POST-HFSosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > POST-HFSosc_non_0_stp1_GPe18_strf1.8_f5.0.log

#python3 ep_net/multisim.py -c GABAosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > GABAosc_non_0_stp1_GPe29_strf1.8_f5.0.log
#python3 ep_net/multisim.py -c POST-HFSosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > POST-HFSosc_non_0_stp1_GPe29_strf1.8_f5.0.log

#Test ability to transmit oscillations based on condition, and with only one nucleus oscillating
python3 ep_net/multisim.py -c POST-HFS_GPeOsc -n 15 -syn non -stp 1 -f 0  > POST-HFS_GPeOsc_STNlognorm.log
python3 ep_net/multisim.py -c GABA_GPeOsc -n 15 -syn non -stp 1 -f 0  > GABA_GPeOsc_STNlognorm.log
python3 ep_net/multisim.py -c POST-NoDa_GPeOsc -n 15 -syn non -stp 1 -f 0  > GABA_GPeOsc_STNlognorm.log

#python3 ep_net/multisim.py -c POST-HFS_STNosc -n 15 -syn non -stp 1 -f 0  > POST-HFS_STNosc_GPeLognorm.log
#python3 ep_net/multisim.py -c GABA_STNosc -n 15 -syn non -stp 1 -f 0  > GABA_STNosc_GPeLognorm.log
#python3 ep_net/multisim.py -c POST-NoDa_STNosc -n 15 -syn non -stp 1 -f 0  > GABA_STNosc_GPeLognorm.log

################
#3. calculate correlation between str input and EP output
#consider an additional GPe correlation depending on results

