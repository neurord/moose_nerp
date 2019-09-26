#non-oscillatory input is firing too fast, ~50 Hz.  Need to decrease STN input or increase Str input
#a. reduce firing frequency of STN - DONE Now mean_ISI is 1/18.  Reduced from 50 Hz to 30 Hz - still too high
#b. reduce number of tt inputs per synapse: from 3 to 2 GOOD
#c. reduce conductance of tt inputs, e.g. from 0.25e-9 to 0.2e-9 NOT NEEDED

################################################################################################
## 1. Test multiplexing transmission, using two different striatal trains
## SPECIFYING THE TWO STRIATAL TRAINS IN PARAM_NET - DIFFERENT THAN ABOVE - Repeat?
#python3 ep_net/multisim.py -c GABA_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > GABA_non_0_stp1_GPe18_str_DM_DL.log
#python3 ep_net/multisim.py -c POST-HFS_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > POST-HFS_non_0_stp1_GPe18_str_DM_DL.log

#python3 ep_net/multisim.py -c GABA_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > GABA_non_0_stp1_GPe29_str_DM_DL.log
#python3 ep_net/multisim.py -c POST-HFS_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > POST-HFS_non_0_stp1_GPe29_str_DM_DL.log

################################################################################################
## 2. 16 sets of simulations to evaluate effect of input correlation on Str-EP cross correlation
#RE DO ALL THESE WITH ONLY SINGLE STR INPUT - eliminate str2 before running, set ttSTN
#~6 hours each. 4/day, 4 days
#condition -n num_trials -syn syntype -stp stpYN -f stimfreq -ttGPe GPe_stim_file_root --ttstr str_stim_file_root
#if stimfreq is 0 and syntype is non, that means no single synapse periodic stimulation
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.49_t > GABA_non_0_stp1_GPe18_str_0.49.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.49_t > POST-HFS_non_0_stp1_GPe18_str_0.49.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.64_t_t > GABA_non_0_stp1_GPe18_str_0.64.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.64_t > POST-HFS_non_0_stp1_GPe18_str_0.64.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.81_t > GABA_non_0_stp1_GPe18_str_0.81.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.81_t > POST-HFS_non_0_stp1_GPe18_str_0.81.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.90_t > GABA_non_0_stp1_GPe18_str_0.90.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.90_t > POST-HFS_non_0_stp1_GPe18_str_0.90.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.95_t > GABA_non_0_stp1_GPe18_str_0.95.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.95_t > POST-HFS_non_0_stp1_GPe18_str_0.95.log

python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.49_t > GABA_non_0_stp1_GPe29_str_0.49.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.49_t > POST-HFS_non_0_stp1_GPe29_str_0.49.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.64_t > GABA_non_0_stp1_GPe29_str_0.64.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.64_t > POST-HFS_non_0_stp1_GPe29_str_0.64.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.81_t > GABA_non_0_stp1_GPe29_str_0.81.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.81_t > POST-HFS_non_0_stp1_GPe29_str_0.81.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.90_t > GABA_non_0_stp1_GPe29_str_0.90.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.90_t > POST-HFS_non_0_stp1_GPe29_str_0.90.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.95_t > GABA_non_0_stp1_GPe29_str_0.95.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.95_t > POST-HFS_non_0_stp1_GPe29_str_0.95.log

################################################################################################
# 3. Test ability to transmit oscillations based on condition, and with only one nucleus oscillating
### Better to do this with oscillation frequency adjusted according to measurements during Parkinson's, e.g. beta freq?  But less strong modulation
#SINGLE STRIATAL INPUT - eliminate str2 before running
#oscillations in GPe, STN is lognorm
python3 ep_net/multisim.py -c POST-HFS_GPeOsc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_InhomPoisson.npz --ttSTN ep_net/STN_lognorm.npz > POST-HFS_GPeOsc_STNlognorm.log
python3 ep_net/multisim.py -c GABA_GPeOsc -n 15 -syn non -stp 1 -f 0  --ttGPe ep_net/GPe_InhomPoisson.npz --ttSTN ep_net/STN_lognorm.npz > GABA_GPeOsc_STNlognorm.log
python3 ep_net/multisim.py -c POST-NoDa_GPeOsc -n 15 -syn non -stp 1 -f 0  --ttGPe ep_net/GPe_InhomPoisson.npz --ttSTN ep_net/STN_lognorm.npz > GABA_GPeOsc_STNlognorm.log

#oscillations in STN, GPe is lognorm
python3 ep_net/multisim.py -c POST-HFS_STNosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm.npz --ttSTN ep_net/STN_InhomPoisson.npz > POST-HFS_STNosc_GPeLognorm.log
python3 ep_net/multisim.py -c GABA_STNosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm.npz --ttSTN ep_net/STN_InhomPoisson.npz > GABA_STNosc_GPeLognorm.log
python3 ep_net/multisim.py -c POST-NoDa_STNosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm.npz --ttSTN ep_net/STN_InhomPoisson.npz > GABA_STNosc_GPeLognorm.log

################################################################################################
#Test information processing with two striatal frequencies
#RE DO ALL THESE SPECIFYING THE TWO STRIATAL FREQUENCIES IN PARAM_NET
#python3 ep_net/multisim.py -c GABA_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > GABA_DMDLosc_non_0_stp1_GPe18_strf1.8_f5.0.log
#python3 ep_net/multisim.py -c POST-HFS_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > POST-HFS_DMDLosc_non_0_stp1_GPe18_strf1.8_f5.0.log

#python3 ep_net/multisim.py -c GABA_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > GABA_DMDLosc_non_0_stp1_GPe29_strf1.8_f5.0.log
#python3 ep_net/multisim.py -c POST-HFS_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > POST-HFS_DMDLosc_non_0_stp1_GPe29_strf1.8_f5.0.log

################
#3. calculate correlation between str input and EP output
#consider an additional GPe correlation depending on results

