# do not put !/bin/bash if you want to run this through the atq
### evaluate effect of distance on upstate amplitude versus spikes
### possibly consider using more inputs for DMS, but given in the same time frame/time window
### Try advancing the BLA inputs to start at same time as upstate inputs, or 100 ms later
### JUST increase NMDA conductance to reflect higher NMDA: AMPA ratio - 2 fold for DMS, 3 fold for DLS
### Then, do the striosome model, using the higher NMDA to AMPA ratio, and then LOWER the NMDA:AMPA ratio

### simulation variations - simulate for 1 sec
### a. time of BLA inputs = 0 or 100 ms (relative to upstate) -> 0.1 or 0.2 sec - 100 ms works better
### b. location of BLA inputs - distal or proximal - distal of 100 um is probably not distal enough
### c. use one branch - fewer inputs needed; block NaF - plateau will be more apparent
### d. NMDA:AMPA ratio - 0.4 (control) vs 3x higher - change line 95 and rerun
### repeat above using striosome neuron
### evaluate both upstate amplitude and number of spikes
### d. possibly give 20 inputs (over same 60 ms) for DMS

#dispersed over small region of dendrite - optimal for upstate

#python3 sim_upstate.py iv -sim_type rheobase_only -SPN cells.D1PatchSample4 
#python3 sim_upstate.py iv -sim_type rheobase_only -SPN D1PatchSample5 

#evaluate number of spines available using different dist_dispers and d2c - may need to change the d2c values
#Possibly existing dispersed, constrain2 sims - were not always excluding existing compartments - currently just excluding those from calcium analysis. rerun
for ii in 1 2 3 4 5 6 7 8 9 10 11 12 
do
    echo $(date '+%Y-%m-%d %H:%M:%S') >> testfile
    echo "$ii" >> testfile
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 4 -dist_dispers 100e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 0 50e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1patch_clust10_disp4_spc2_4_d2c0_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 4 -dist_dispers 100e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 50e-6 120e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1patch_clust10_disp4_spc2_4_d2c50_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 4 -dist_dispers 100e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 120e-6 165e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1patch_clust10_disp4_spc2_4_d2c120_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 4 -dist_dispers 100e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 165e-6 250e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1patch_clust10_disp4_spc2_4_d2c165_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 4 -dist_dispers 50e-6 100e-6 -dist_cluster 50e-6 350e-6 -d2c 0 50e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1patch_clust10_disp4_spc2_4_d2c0_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 4 -dist_dispers 50e-6 100e-6 -dist_cluster 50e-6 350e-6 -d2c 50e-6 120e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1patch_clust10_disp4_spc2_4_d2c50_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 4 -dist_dispers 50e-6 100e-6 -dist_cluster 50e-6 350e-6 -d2c 120e-6 150e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1patch_clust10_disp4_spc2_4_d2c120_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 4 -dist_dispers 50e-6 100e-6 -dist_cluster 50e-6 350e-6 -d2c 150e-6 200e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1patch_clust10_disp4_spc2_4_d2c150_exp50.txt &

    python3 sim_upstate_BLA.py single -sim_type BLA_DLS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 0 -dist_cluster 50e-6 400e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1patch4_clust10_disp0_spc2_4_exp50_set2.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS -SPN cells.D1PatchSample4 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 0 -dist_cluster 50e-6 400e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1patch4_clust10_disp0_spc2_4_exp50_set2.txt &

    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -SPN D1PatchSample5 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 0 -dist_cluster 50e-6 350e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1patch5_clust10_disp0_spc2_4_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -SPN D1PatchSample5 -num_clustered 10 -spc 4 -spc_subset 2 -num_dispersed 0 -dist_cluster 50e-6 350e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1patch5_clust10_disp0_spc2_4_exp50.txt &

    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 0 50e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1matrix_clust24_disp8_spc2_4_d2c0_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 50e-6 120e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1matrix_clust24_disp8_spc2_4_d2c50_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 120e-6 150e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1matrix_clust24_disp8_spc2_4_d2c120_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 150e-6 300e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1matrix_clust24_disp8_spc2_4_d2c150_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 50e-6 100e-6 -dist_cluster 50e-6 350e-6 -d2c 0 40e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1matrix_clust24_disp8_spc2_4_d2c0_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 50e-6 100e-6 -dist_cluster 50e-6 350e-6 -d2c 40e-6 80e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1matrix_clust24_disp8_spc2_4_d2c40_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 50e-6 100e-6 -dist_cluster 50e-6 350e-6 -d2c 80e-6 120e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1matrix_clust24_disp8_spc2_4_d2c80_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 50e-6 100e-6 -dist_cluster 50e-6 350e-6 -d2c 120e-6 170e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1matrix_clust24_disp8_spc2_4_d2c120_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 50e-6 100e-6 -dist_cluster 50e-6 350e-6 -d2c 170e-6 300e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1matrix_clust24_disp8_spc2_4_d2c150_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 0 -dist_cluster 50e-6 400e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_clust24_disp0_spc2_4_exp50_set2.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 0 -dist_cluster 50e-6 400e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_clust24_disp0_spc2_4_exp50_set2.txt &

    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 0 50e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1matrix_clust24_disp8_spc2_4_d2c0_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 0 50e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1matrix_clust24_disp8_spc2_4_d2c0_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 50e-6 120e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1matrix_clust24_disp8_spc2_4_d2c50_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 50e-6 120e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1matrix_clust24_disp8_spc2_4_d2c50_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 120e-6 150e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1matrix_clust24_disp8_spc2_4_d2c120_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 120e-6 150e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1matrix_clust24_disp8_spc2_4_d2c120_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 150e-6 200e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1matrix_clust24_disp8_spc2_4_d2c150_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 150e-6 200e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1matrix_clust24_disp8_spc2_4_d2c150_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 200e-6 300e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_D1matrix_clust24_disp8_spc2_4_d2c200_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 8 -dist_dispers 150e-6 350e-6 -dist_cluster 50e-6 350e-6 -d2c 200e-6 300e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_D1matrix_clust24_disp8_spc2_4_d2c200_exp50.txt &
    pids="$pids $!"
    echo "$pids" >> testfile
    #sleep 5m  #wait 5 min - then start next batch, only when doing small number of sims
    wait  #wait for all of above to finish, then start the next batch
done

