import sys
import numpy as np
import sim_upstate as su

mod_dict = su.make_mod_dict()
single_epsp_seed = 314

#args='single -sim_type BLA_DLS -num_clustered 24 -num_dispersed 8 -d2c 50e-6 120e-6 -dist_dispers 50e-6 350e-6 -spc_subset 2 -spc 4 -dist_cluster 50e-6 350e-6 -start_cluster 0.1 -end_cluster 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0'.split() #for debugging
#args='-BLA DMS'.split()# -seed 123'.split()
args = sys.argv[1:]
params=su.parsarg(args)

####### randomly select seed and call upstate_main ############Ad
if not params.seed:
    dispersed_seed=np.random.randint(0,32000)
    clustered_seed=dispersed_seed#np.random.randint(0,32000)
else:
    dispersed_seed=params.seed
    clustered_seed=params.seed
sims=su.specify_sims(params.sim_type,clustered_seed,dispersed_seed,single_epsp_seed, params)
tt_Ctx_SPN = {'fname': params.spkfile,'syn_per_tt':2} 
spn_name=params.SPN.split('.')[-1][0:5]+params.SPN.split('.')[-1][-1]
print(sims[0],'clustered seed=', clustered_seed, ', dispersed_seed=', dispersed_seed, 'spn_name=',spn_name)
model=su.upstate_main(params.SPN, mod_dict, **sims[0]['kwds'],do_plots=False, filename=spn_name+sims[0]['name'], time_tables=tt_Ctx_SPN)

