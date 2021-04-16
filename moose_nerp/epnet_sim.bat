#run ep vs freq for str & GPe, stp or not, two different inj
#process using new neur_anal
python3 ep/multisim.py -15e-12 0
python3 ep/multisim.py 0 0
python3 ep/multisim.py 0 1
python3 ep/__main__.py
python3 ep/multisim.py -15e-12 1


################################################################################################
## 1. Test multiplexing transmission, using two different striatal trains
## SPECIFYING THE TWO STRIATAL TRAINS IN PARAM_NET - DIFFERENT THAN ABOVE - Repeat?
#python3 ep_net/multisim.py -c GABA_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > GABA_non_0_stp1_GPe18_str_DM_DL.log
#python3 ep_net/multisim.py -c POST-HFS_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > POST-HFS_non_0_stp1_GPe18_str_DM_DL.log

#python3 ep_net/multisim.py -c GABA_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > GABA_non_0_stp1_GPe29_str_DM_DL.log
#python3 ep_net/multisim.py -c POST-HFS_DMDL -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > POST-HFS_non_0_stp1_GPe29_str_DM_DL.log

################################################################################################
# 3. Test ability to transmit oscillations based on condition, and with only one nucleus oscillating
#SINGLE STRIATAL INPUT - eliminate str2 before running
#oscillations in GPe, STN is lognorm
#python3 ep_net/multisim.py -c POST-HFS_GPeOsc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_InhomPoisson.npz --ttSTN ep_net/STN_lognorm.npz > POST-HFS_GPeOsc_STNlognorm.log
#python3 ep_net/multisim.py -c GABA_GPeOsc -n 15 -syn non -stp 1 -f 0  --ttGPe ep_net/GPe_InhomPoisson.npz --ttSTN ep_net/STN_lognorm.npz > GABA_GPeOsc_STNlognorm.log
#python3 ep_net/multisim.py -c POST-NoDa_GPeOsc -n 15 -syn non -stp 1 -f 0  --ttGPe ep_net/GPe_InhomPoisson.npz --ttSTN ep_net/STN_lognorm.npz > GABA_GPeOsc_STNlognorm.log

#oscillations in STN, GPe is lognorm
#python3 ep_net/multisim.py -c POST-HFS_STNosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm.npz --ttSTN ep_net/STN_InhomPoisson.npz > POST-HFS_STNosc_GPeLognorm.log
#python3 ep_net/multisim.py -c GABA_STNosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm.npz --ttSTN ep_net/STN_InhomPoisson.npz > GABA_STNosc_GPeLognorm.log
#python3 ep_net/multisim.py -c POST-NoDa_STNosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm.npz --ttSTN ep_net/STN_InhomPoisson.npz > GABA_STNosc_GPeLognorm.log

################################################################################################
#Test information processing with two striatal frequencies
#python3 ep_net/multisim.py -c GABA_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > GABA_DMDLosc_non_0_stp1_GPe18_strf1.8_f5.0.log
#python3 ep_net/multisim.py -c POST-HFS_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq18  > POST-HFS_DMDLosc_non_0_stp1_GPe18_strf1.8_f5.0.log

#python3 ep_net/multisim.py -c GABA_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > GABA_DMDLosc_non_0_stp1_GPe29_strf1.8_f5.0.log
#python3 ep_net/multisim.py -c POST-HFS_DMDLosc -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29  > POST-HFS_DMDLosc_non_0_stp1_GPe29_strf1.8_f5.0.log

################ All log norm inputs
#python3 ep_net/multisim.py -c POST-HFS -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm> POST-HFS_alllognorm.log
#python3 ep_net/multisim.py -c GABA -n 15 -syn non -stp 1 -f 0 --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm > POST-HFS_alllognorm.log
#python3 ep_net/multisim.py -c POST-NoDa -n 15 -syn non -stp 1 -f 0  --ttGPe ep_net/GPe_lognorm_freq29 --ttSTN ep_net/STN_lognorm --ttstr ep_net/SPN_lognorm> GABA_alllognorm.log

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

