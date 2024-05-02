# do not put !/bin/bash if you want to run this through the atq
#find bug - using dispersed time table inputs, observe spike and strange inputs around 0.6-0.7 sec
#   a. run cluster alone - decide on how many stim per compartment
#   b. Start sim expers below
### one other comparison - just model the DLS, change location of inputs (i.e., use same number of inputs to each)
### evaluate effect of distance on upstate amplitude versus spikes
### possibly consider using more inputs for DMS, but given in the same time frame/time window
### Try advancing the BLA inputs to start at same time as upstate inputs, or 100 ms later
### JUST increase NMDA conductance to reflect higher NMDA: AMPA ratio - 2 fold for DMS, 3 fold for DLS
### Then, do the striosome model, using the higher NMDA to AMPA ratio, and then LOWER the NMDA:AMPA ratio

### simulation variations - 8 variations in each neuron, using 75 dispersed inputs (subthreshold) simulate for 0.6 sec
### a. time of BLA inputs = 0 or 100 ms (relative to upstate) -> 0.1 or 0.2 sec - IP
### b. location of BLA inputs - distal or proximal - IP
### c. NMDA:AMPA ratio - 0.4 (control) vs 3x higher - change line 95 and rerun
### repeat above using striosome neuron
### evaluate both upstate amplitude and number of spikes
### d. possibly give 24 inputs (over same 60 ms) for DMS

for ii in 1 2 3 4
do
    echo "$ii" >> testfile
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 70 -start_stim 0.1 >> DMS_70_16_100ms.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 16 -num_dispersed 70 -start_stim 0.1 >> DLS_70_16_100ms.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 70 -start_stim 0.2 >> DMS_70_16_200ms.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 16 -num_dispersed 70 -start_stim 0.2 >> DLS_70_16_200ms.txt
    ##test different matrix neuron, updated with CaR=5.2, not 45.2 to see if this one has better response to dispersed
    python3 sim_upstate_BLA.py single -SPN cells.D1MatrixSample3 -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 70 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0 >> DLS_mat3_exp5_70_0.txt
    python3 sim_upstate_BLA.py single -SPN cells.D1MatrixSample3 -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 70 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0 >> DMS_mat3_exp5_70_0.txt
    python3 sim_upstate_BLA.py single -SPN cells.D1MatrixSample3 -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 65 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0 >> DLS_mat3_exp5_65_0.txt
    python3 sim_upstate_BLA.py single -SPN cells.D1MatrixSample3 -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 65 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0 >> DMS_mat3_exp5_65_0.txt
    #python3 sim_upstate_BLA.py single -SPN cells.D1MatrixSample3 -sim_type BLA_DLS_dispersed -num_clustered 16 -num_dispersed 70 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0 >> DLS_mat3_exp5_70_16_100ms.txt
    #python3 sim_upstate_BLA.py single -SPN cells.D1MatrixSample3 -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 70 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0 >> DMS_mat3_exp5_70_16_100ms.txt
    #python3 sim_upstate_BLA.py single -SPN cells.D1MatrixSample3 -sim_type BLA_DLS_dispersed -num_clustered 16 -num_dispersed 70 -start_stim 0.2 -spkfile spn1_net/Ctx1000_exp_freq5.0 >> DLS_mat3_exp5_70_16_200ms.txt
    #python3 sim_upstate_BLA.py single -SPN cells.D1MatrixSample3 -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 70 -start_stim 0.2 -spkfile spn1_net/Ctx1000_exp_freq5.0 >> DMS_mat3_exp5_70_16_200ms.txt
    #python3 sim_upstate_BLA.py single -SPN cells.D1MatrixSample3 -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 65 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0 >> DLS_mat3_exp5_65_0_100ms.txt
    #python3 sim_upstate_BLA.py single -SPN cells.D1MatrixSample3 -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 65 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0 >> DMS_mat3_exp5_65_0_100ms.txt
    ##test more patch to determine subthreshold
    #python3 sim_upstate_BLA.py single -SPN D1PatchSample5 -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 80 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DMS_patch_exp5_80_16_100ms.txt
    #python3 sim_upstate_BLA.py single -SPN D1PatchSample5 -sim_type BLA_DLS_dispersed -num_clustered 16 -num_dispersed 80 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DLS_patch_exp5_80_16_100ms.txt
    #python3 sim_upstate_BLA.py single -SPN D1PatchSample5 -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 80 -start_stim 0.2 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DMS_patch_exp5_70_16_200ms.txt
    #python3 sim_upstate_BLA.py single -SPN D1PatchSample5 -sim_type BLA_DLS_dispersed -num_clustered 16 -num_dispersed 80 -start_stim 0.2 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DLS_patch_exp5_70_16_200ms.txt
    #python3 sim_upstate_BLA.py single -SPN D1PatchSample5 -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 80 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DMS_patch_exp5_80_0.txt
    #python3 sim_upstate_BLA.py single -SPN D1PatchSample5 -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 80 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DLS_patch_exp5_80_0.txt
    #python3 sim_upstate_BLA.py single -SPN D1PatchSample5 -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 90 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DMS_patch_exp5_65_0.txt
    #python3 sim_upstate_BLA.py single -SPN D1PatchSample5 -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 90 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DLS_patch_exp5_65_0.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 0 -start_stim 0.1 >> DMS_mat_0_16_100ms.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 16 -num_dispersed 0 -start_stim 0.1 >> DLS_mat_0_16_100ms.txt
    #python3 sim_upstate_BLA.py single -SPN D1PatchSample5 -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 0 -start_stim 0.1 >> DMS_patch_0_16_100ms.txt
    #python3 sim_upstate_BLA.py single -SPN D1PatchSample5 -sim_type BLA_DLS_dispersed -num_clustered 16 -num_dispersed 0 -start_stim 0.1 >> DLS_patch_0_16_100ms.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 70 -start_stim 0.1 >> DMS_70_0_100ms.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 70 -start_stim 0.1 >> DLS_70_0_100ms.txt
    ## change param_cond in Matrix2, CaT32=1.09 not 8.09, and see if this has better response to dispersed. 
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 70 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DMS_exp5_70_0.txt
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 70 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DLS_exp5_70_0.txt
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 75 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DMS_exp5_75_0.txt
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 75 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DLS_exp5_75_0.txt
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 70 -start_stim 0.1 >> DMS_70_0.txt
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 70 -start_stim 0.1 >> DLS_70_0.txt
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 75 -start_stim 0.1 >> DMS_75_0.txt
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 75 -start_stim 0.1 >> DLS_75_0.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 65 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DMS_65_16_100ms.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 16 -num_dispersed 65 -start_stim 0.1 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DLS_65_16_100ms.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 65 -start_stim 0.2 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DMS_65_16_200ms.txt
    #python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 16 -num_dispersed 65 -start_stim 0.2 -spkfile spn1_net/Ctx1000_exp_freq5.0>> DLS_65_16_200ms.txt
    ## test NMDAR conductance
    ## possibly use real spike trains if D1MatrixSample3 works better

done
