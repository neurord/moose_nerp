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


for ii in 1 2 3 4 5 6 7 8 9 10 11 12 
do
    echo $(date '+%Y-%m-%d %H:%M:%S') >> testfile
    echo "$ii" >> testfile
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_clust24_spc2_4_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_clust24_spc2_4_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_clust24_spc2_4_NaFexp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 4 -spc_subset 2 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_clust24_spc2_4_NaFexp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc_subset 3 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_clust24_spc3_6_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc_subset 3 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_clust24_spc3_6_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc_subset 3 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_clust24_spc3_6_NaFexp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc_subset 3 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_clust24_spc3_6_NaFexp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 18 -spc_subset 3 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_clust18_spc3_6_NaFexp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 18 -spc_subset 3 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_clust18_spc3_6_NaFexp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS -num_clustered 24 -spc 7 -spc_subset 3 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DLS_clust24_spc2_4_exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS -num_clustered 24 -spc 7 -spc_subset 3 -num_dispersed 0 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -block_naf True -start_cluster 0.1 -end_cluster 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_clust24_spc2_4_exp50.txt &
    pids="$pids $!"
    echo "$pids" >> testfile
    #wait  #wait for all of above to finish, then start the next batch
done

    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS num_clustered 4 -num_dispersed 30 -min_disp 50e-6 -max_disp 300e-6 -start_cluster 0.1 -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp300u_30_4_NaF_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS num_clustered 8 -num_dispersed 30 -min_disp 50e-6 -max_disp 300e-6 -start_cluster 0.1 -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp300u_30_8_NaF_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS num_clustered 0 -num_dispersed 30 -min_disp 50e-6 -max_disp 300e-6 -start_cluster 0.1 -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp300u_30_0_NaF_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS num_clustered 4 -num_dispersed 30 -min_disp 50e-6 -max_disp 300e-6 -start_cluster 0.1 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_30_4_NaF_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS num_clustered 8 -num_dispersed 30 -min_disp 50e-6 -max_disp 300e-6 -start_cluster 0.1 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_30_8_NaF_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS num_clustered 0 -num_dispersed 30 -min_disp 50e-6 -max_disp 300e-6 -start_cluster 0.1 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_30_0_NaF_0.3exp50.txt &

    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS num_clustered 4 -num_dispersed 20 -min_disp 100e-6 -max_disp 150e-6 -start_cluster 0.1 -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp150u_20_4_NaF_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS num_clustered 0 -num_dispersed 20 -min_disp 100e-6 -max_disp 150e-6 -start_cluster 0.1 -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp150u_20_0_NaF_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS num_clustered 4 -num_dispersed 20 -min_disp 100e-6 -max_disp 150e-6 -start_cluster 0.1 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_20_4_NaF_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS num_clustered 0 -num_dispersed 20 -min_disp 100e-6 -max_disp 150e-6 -start_cluster 0.1 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_20_0_NaF_0.3exp50.txt &

    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS num_clustered 0 -num_dispersed 24 -min_disp 150e-6 -max_disp 200e-6 -start_cluster 0.1 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp200u_24_0_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS num_clustered 0 -num_dispersed 24 -min_disp 150e-6 -max_disp 200e-6 -start_cluster 0.1 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_24_0_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS num_clustered 0 -num_dispersed 30 -min_disp 150e-6 -max_disp 200e-6 -start_cluster 0.1 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp200u_30_0_0.3exp50.txt &
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS num_clustered 0 -num_dispersed 30 -min_disp 150e-6 -max_disp 200e-6 -start_cluster 0.1 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_30_0_0.3exp50.txt &
