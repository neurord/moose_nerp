#condition num_trials syntype stpYN stimfreq
python3 ep_net/multisim.py GABA 15 non 0 0 > Ctrlnon_0_stp0.log
python3 ep_net/multisim.py GABA 15 GPe 0 40 > Ctrlgpe_40_stp0.log
python3 ep_net/multisim.py GABA 15 str 0 20 > Ctrlstr_20_stp0.log
python3 ep_net/multisim.py GABA 15 non 1 0 > Ctrlnon_0.log
python3 ep_net/multisim.py GABA 15 GPe 1 40 > Ctrlgpe_40.log
python3 ep_net/multisim.py GABA 15 str 1 20 > Ctrlstr_20.log
python3 ep_net/multisim.py POST-HFS 15 non 1 0 > POST-HFS_non_0.log
python3 ep_net/multisim.py POST-HFS 15 GPe 1 40 > POST-HFS_gpe_40.log
python3 ep_net/multisim.py POST-HFS str 1 20 > POST-HFS_str_20.log
python3 ep_net/multisim.py POST-NoDa 15 non 1 0 > POST-NoDa_non_0.log
python3 ep_net/multisim.py POST-NoDa 15 GPe 1 40 >> POST-NoDa_gpe_40.log
python3 ep_net/multisim.py POST-NoDa str 1 20 > POST-NoDa_str_20.log
python3 ep/multisim.py 0.0 1 > epfreq_inj0_stp1.log
python3 ep/multisim.py -15e-12 1 > epfreq_inj-15e-12_stp1.log
python3 ep/multisim.py 0.0 0 > epfreq_inj0_stp0.log
python3 ep/multisim.py -15e-12 0 > epfreq_inj-15e-12_stp0.log

