#process using neur_anal
python3 ep/multisim.py -15e-12 0
python3 ep/multisim.py 0 0
python3 ep/multisim.py 0 1
python3 ep/__main__.py
python3 ep/multisim.py -15e-12 1

################################################################################################
## 1. Test multiplexing transmission, using two different striatal trains
#python3 ep_net/multisim.py -c GABA_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > GABA_non_0_stp1_GPe18_str_DM_DL.log
#python3 ep_net/multisim.py -c POST-HFS_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > POST-HFS_non_0_stp1_GPe18_str_DM_DL.log

#python3 ep_net/multisim.py -c GABA_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > GABA_non_0_stp1_GPe29_str_DM_DL.log
#python3 ep_net/multisim.py -c POST-HFS_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > POST-HFS_non_0_stp1_GPe29_str_DM_DL.log

################################################################################################
## 2. simulations to evaluate effect of input correlation on Str-EP cross correlation
#condition -n num_trials -syn syntype -stp stpYN -f stimfreq -ttGPe GPe_stim_file_root --ttstr str_stim_file_root
#if stimfreq is 0 and syntype is non, that means no single synapse periodic stimulation
#>>>outputs: /home/avrama/moose/mn_output/ep_net/epGABAPSP_non_freq0_plas1_tg_GPe_lognorm_freq*_ts_str_exp_corr0.*_t*t*.npz
#>>>outputs: /home/avrama/moose/mn_output/ep_net/epGABAPOST_HFS_non_freq0_plas1_tg_GPe_lognorm_freq*_ts_str_exp_corr0.*_t*t*.npz

#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.49_t > GABA_non_0_stp1_GPe18_str_0.49.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.49_t > POST-HFS_non_0_stp1_GPe18_str_0.49.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.64_t_t > GABA_non_0_stp1_GPe18_str_0.64.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.64_t > POST-HFS_non_0_stp1_GPe18_str_0.64.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.81_t > GABA_non_0_stp1_GPe18_str_0.81.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.81_t > POST-HFS_non_0_stp1_GPe18_str_0.81.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.90_t > GABA_non_0_stp1_GPe18_str_0.90.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.90_t > POST-HFS_non_0_stp1_GPe18_str_0.90.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.95_t > GABA_non_0_stp1_GPe18_str_0.95.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr0.95_t > POST-HFS_non_0_stp1_GPe18_str_0.95.log

#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.49_t > GABA_non_0_stp1_GPe29_str_0.49.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.49_t > POST-HFS_non_0_stp1_GPe29_str_0.49.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.64_t > GABA_non_0_stp1_GPe29_str_0.64.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.64_t > POST-HFS_non_0_stp1_GPe29_str_0.64.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.81_t > GABA_non_0_stp1_GPe29_str_0.81.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.81_t > POST-HFS_non_0_stp1_GPe29_str_0.81.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.90_t > GABA_non_0_stp1_GPe29_str_0.90.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.90_t > POST-HFS_non_0_stp1_GPe29_str_0.90.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.95_t > GABA_non_0_stp1_GPe29_str_0.95.log
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr0.95_t > POST-HFS_non_0_stp1_GPe29_str_0.95.log

q################################################################################################
# 3. Test ability to transmit oscillations based on condition, and with only one nucleus oscillating
#oscillations in GPe, STN is lognorm
#python3 ep_net/multisim.py -c POST-HFS_GPeOsc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_InhomPoisson.npz --ttSTN ep_net/STN_lognorm.npz > POST-HFS_GPeOsc_STNlognorm.log
#python3 ep_net/multisim.py -c GABA_GPeOsc -n 15 -syn non -stp 1 -f 0  --ttGPe ep_net/GPe_InhomPoisson.npz --ttSTN ep_net/STN_lognorm.npz > GABA_GPeOsc_STNlognorm.log
#outputs: /home/avrama/moose/mn_output/ep_net/epGABA_GPeOscPSP_non_freq0_plas1_tg_GPe_InhomPoisson_ts_STN_lognormt*.npz
#python3 ep_net/multisim.py -c POST-NoDa_GPeOsc -n 15 -syn non -stp 1 -f 0  --ttGPe ep_net/GPe_InhomPoisson.npz --ttSTN ep_net/STN_lognorm.npz > GABA_GPeOsc_STNlognorm.log

#oscillations in STN, GPe is lognorm
#python3 ep_net/multisim.py -c POST-HFS_STNosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm.npz --ttSTN ep_net/STN_InhomPoisson.npz > POST-HFS_STNosc_GPeLognorm.log
#python3 ep_net/multisim.py -c GABA_STNosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm.npz --ttSTN ep_net/STN_InhomPoisson.npz > GABA_STNosc_GPeLognorm.log
#outputs: /home/avrama/moose/mn_output/ep_net/epGABA_STNoscPSP_non_freq0_plas1_tg_GPe_lognorm_ts_STN_InhomPoissont*.npz
#python3 ep_net/multisim.py -c POST-NoDa_STNosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm.npz --ttSTN ep_net/STN_InhomPoisson.npz > GABA_STNosc_GPeLognorm.log

####### All three nuclei oscillating #########
python3 ep_net/multisim.py -c GABAosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_InhomPoisson_freq29.3_osc2.0.npz --ttSTN ep_net/STN_InhomPoisson_freq18_osc0.6.npz -ttstr ep_net/str_InhomPoisson_freq4.0_osc0.2.npz > GABAosc_STNlognorm.log
python3 ep_net/multisim.py -c POST-HFSosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_InhomPoisson_freq29.3_osc2.0.npz --ttSTN ep_net/STN_InhomPoisson_freq18_osc0.6.npz -ttstr ep_net/str_InhomPoisson_freq4.0_osc0.2.npz > POST-HFSosc_STNlognorm.log
python3 ep_net/multisim.py -c POST-NoDaosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_InhomPoisson_freq29.3_osc2.0.npz --ttSTN ep_net/STN_InhomPoisson_freq18_osc0.6.npz -ttstr ep_net/str_InhomPoisson_freq4.0_osc0.2.npz > POST-NoDaosc_STNlognorm.log

################################################################################################
#Test information processing with two striatal frequencies
#python3 ep_net/multisim.py -c GABA_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > GABA_DMDLosc_non_0_stp1_GPe18_strf1.8_f5.0.log
#>>>outputs:/home/avrama/moose/mn_output/ep_net/epGABA_DMDLoscPSP_non_freq0_plas1_tg_GPe_lognorm_freq18t*.npz
#python3 ep_net/multisim.py -c POST-HFS_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > POST-HFS_DMDLosc_non_0_stp1_GPe18_strf1.8_f5.0.log
#>>>outputs:/home/avrama/moose/mn_output/ep_net/epPOST-HFS_DMDLoscPSP_non_freq0_plas1_tg_GPe_lognorm_freq18t*.npz

#python3 ep_net/multisim.py -c GABA_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > GABA_DMDLosc_non_0_stp1_GPe29_strf1.8_f5.0.log
#>>>outputs:/home/avrama/moose/mn_output/ep_net/epGABA_DMDLoscPSP_non_freq0_plas1_tg_GPe_lognorm_freq29t*.npz
#python3 ep_net/multisim.py -c POST-HFS_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > POST-HFS_DMDLosc_non_0_stp1_GPe29_strf1.8_f5.0.log
#>>>outputs:/home/avrama/moose/mn_output/ep_net/epPOST-HFS_DMDLoscPSP_non_freq0_plas1_tg_GPe_lognorm_freq29t*.npz

################
#3. calculate correlation between str input and EP output
#consider an additional GPe correlation depending on results

################ All log norm inputs
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm> POST-HFS_alllognorm.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm > POST-HFS_alllognorm.log
#python3 ep_net/multisim.py -c POST-NoDa -n 15 -syn non -stp 1 -f 0  --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm> GABA_alllognorm.log

#log norm inputs with addition 20 Hz stimulation
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn str -stp 1 -f 20 --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm> POST-HFS_str20_alllognorm.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn str -stp 1 -f 20 --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm > POST-HFS_str20_alllognorm.log
#python3 ep_net/multisim.py -c POST-NoDa -n 15 -syn str -stp 1 -f 20  --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm> GABA_str20_alllognorm.log

#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn GPe -stp 1 -f 20 --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm> POST-HFS_GPe20_alllognorm.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn GPe -stp 1 -f 20 --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm > POST-HFS_GPe20_alllognorm.log
#python3 ep_net/multisim.py -c POST-NoDa -n 15 -syn GPe -stp 1 -f 20  --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm> GABA_GPe20_alllognorm.log

#python3 ep_net/multisim.py -c GABA -n 15 -syn str -stp 1 -f 20 --ttGPe ep_net/GPe_lognorm_freq18 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm > GABA_str20_stp1_alllognorm.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn GPe -stp 1 -f 20 --ttGPe ep_net/GPe_lognorm_freq18 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm > GABA_gpe20_stp1_alllognorm.log

#python3 ep_net/multisim.py -c GABA -n 15 -syn str -stp 0 -f 20 --ttGPe ep_net/GPe_lognorm_freq18 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm > GABA_str20_stp0_alllognorm.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn GPe -stp 0 -f 20 --ttGPe ep_net/GPe_lognorm_freq18 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm > GABA_gpe20_stp0_alllognorm.log


 
