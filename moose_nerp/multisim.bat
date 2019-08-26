#condition num_trials syntype stpYN stimfreq
#python3 ep/multisim.py 0.0 1 > epfreq_inj0_stp1.log
#python3 ep/multisim.py -15e-12 1 > epfreq_inj-15e-12_stp1.log
#python3 ep/multisim.py 0.0 0 > epfreq_inj0_stp0.log
#python3 ep/multisim.py -15e-12 0 > epfreq_inj-15e-12_stp0.log
#python3 ep_net/multisim.py GABAosc 15 non 0 0 > Ctrlosc_non_0_stp0.log
#python3 ep_net/multisim.py GABA 15 GPe 0 40 > Ctrlgpe_40_stp0.log
#python3 ep_net/multisim.py GABA 15 str 0 20 > Ctrlstr_20_stp0.log
####python3 ep_net/multisim.py GABA 15 non 1 0 > Ctrlosc_non_0_stp1.log
#python3 ep_net/multisim.py GABAosc 15 non 1 0 > Ctrlnon_0.log
#python3 ep_net/multisim.py GABA 15 GPe 1 40 > Ctrlgpe_40.log
#python3 ep_net/multisim.py GABA 15 str 1 20 > Ctrlstr_20.log
#python3 ep_net/multisim.py POST-HFSosc 15 non 1 0 > POST-HFSosc_non_0.log
#python3 ep_net/multisim.py POST-HFS 15 GPe 1 40 > POST-HFS_gpe_40.log
#python3 ep_net/multisim.py POST-HFS str 1 20 > POST-HFS_str_20.log
#python3 ep_net/multisim.py POST-NoDaosc 15 non 1 0 > POST-NoDaosc_non_0.log
#python3 ep_net/multisim.py POST-NoDa 15 GPe 1 40 > POST-NoDa_gpe_40.log
#python3 ep_net/multisim.py POST-NoDa str 1 20 > POST-NoDa_str_20.log

#non-oscillatory input is firing too fast, ~50 Hz.  Need to decrease STN input or increase Str input
#a. reduce firing frequency of STN - DONE Now mean_ISI is 1/18.  Reduced from 50 Hz to 30 Hz - still too high
#b. reduce number of tt inputs per synapse: from 3 to 2 GOOD
#c. reduce conductance of tt inputs, e.g. from 0.25e-9 to 0.2e-9 NOT NEEDED

############## 16 sets of simulations to evaluate effect of input correlation on Str-EP cross correlation
#~6 hours each. 4/day, 4 days
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr010 > GABA_non_0_stp1_GPe18_str_010.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr010 > POST-HFS_non_0_stp1_GPe18_str_010.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr030 > GABA_non_0_stp1_GPe18_str_030.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr030 > POST-HFS_non_0_stp1_GPe18_str_030.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr100 > GABA_non_0_stp1_GPe18_str_100.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr100 > POST-HFS_non_0_stp1_GPe18_str_100.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr300 > GABA_non_0_stp1_GPe18_str_300.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18 --ttstr ep_net/str_exp_corr300 > POST-HFS_non_0_stp1_GPe18_str_300.log

python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr010 > GABA_non_0_stp1_GPe29_str_010.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr010 > POST-HFS_non_0_stp1_GPe29_str_010.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr030 > GABA_non_0_stp1_GPe29_str_030.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr030 > POST-HFS_non_0_stp1_GPe29_str_030.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr100 > GABA_non_0_stp1_GPe29_str_100.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr100 > POST-HFS_non_0_stp1_GPe29_str_100.log
python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr300 > GABA_non_0_stp1_GPe29_str_300.log
python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttstr ep_net/str_exp_corr300 > POST-HFS_non_0_stp1_GPe29_str_300.log

################
#3. calculate correlation between str input and EP output
#consider an additional GPe correlation depending on results

