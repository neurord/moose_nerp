import sys
import numpy as np
import sim_upstate as su

mod_dict = su.make_mod_dict()
clustered_seed = 135
single_epsp_seed = 314

#args='single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 75 -start_stim 0.1'.split()
#args='-BLA DMS'.split()# -seed 123'.split()
args = sys.argv[1:]
params=su.parsarg(args)

####### randomly select seed and call upstate_main ############Ad
if not params.seed:
    dispersed_seed=np.random.randint(0,32000) 
else:
    dispersed_seed=params.seed
sims=su.specify_sims(params.sim_type,clustered_seed,dispersed_seed,single_epsp_seed, params)
tt_Ctx_SPN = {'fname': params.spkfile,'syn_per_tt':2} 
spn_name=params.SPN.split('.')[-1][0:5]+params.SPN.split('.')[-1][-1]
model=su.upstate_main(params.SPN, mod_dict, **sims[0]['kwds'],do_plots=False,filename=spn_name+sims[0]['name'], time_tables=tt_Ctx_SPN)
print(sims[0])

