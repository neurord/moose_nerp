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
### d. possibly give 24 inputs (over same 60 ms) for DMS

#dispersed over small region of dendrite - optimal for upstate

for ii in 1 2 3 4 5 6 7 8 9 10 11 12 
do
    echo "$ii" >> testfile
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 36 -min_disp 150e-6 -max_disp 200e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp200u_36_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 36 -min_disp 150e-6 -max_disp 200e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_36_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 48 -min_disp 150e-6 -max_disp 200e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp200u_48_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 48 -min_disp 150e-6 -max_disp 200e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_48_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 60 -min_disp 150e-6 -max_disp 200e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp200u_60_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 60 -min_disp 150e-6 -max_disp 200e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_60_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 72 -min_disp 150e-6 -max_disp 200e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp200u_72_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 72 -min_disp 150e-6 -max_disp 200e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_72_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 84 -min_disp 150e-6 -max_disp 200e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp200u_84_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 84 -min_disp 150e-6 -max_disp 200e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_84_0_exp50.txt &

    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 48 -min_disp 100e-6 -max_disp 300e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp300u_48_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 48 -min_disp 100e-6 -max_disp 300e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_48_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 60 -min_disp 100e-6 -max_disp 300e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp300u_60_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 60 -min_disp 100e-6 -max_disp 300e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_60_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 72 -min_disp 100e-6 -max_disp 300e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp300u_72_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 72 -min_disp 100e-6 -max_disp 300e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_72_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 84 -min_disp 100e-6 -max_disp 300e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp300u_84_0_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 84 -min_disp 100e-6 -max_disp 300e-6 -end_dispersed 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_84_0_exp50.txt &

    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 24 -min_disp 50e-6 -max_disp 300e-6 -end_dispersed 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp300u_24_0_NaF_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 24 -min_disp 50e-6 -max_disp 300e-6 -end_dispersed 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_24_0_NaF_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 20 -min_disp 50e-6 -max_disp 300e-6 -end_dispersed 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp300u_20_0_NaF_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 20 -min_disp 50e-6 -max_disp 300e-6 -end_dispersed 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_20_0_NaF_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DLS_dispersed -num_clustered 0 -num_dispersed 16 -min_disp 50e-6 -max_disp 300e-6 -end_dispersed 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> Disp300u_28_0_NaF_exp50.txt &
    python3 sim_upstate_BLA.py single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 16 -min_disp 50e-6 -max_disp 300e-6 -end_dispersed 0.3 -spkfile spn1_net/Ctx1000_exp_freq50.0>> DMS_28_0_NaF_exp50.txt &

    pids="$pids $!"
    echo "$pids" >> testfile
    wait  #wait for all of above to finish, then start the next batch
done

