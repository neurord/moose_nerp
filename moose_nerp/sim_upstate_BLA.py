import sys
import numpy as np
import sim_upstate as su

mod_dict = su.make_mod_dict()
clustered_seed = 135
single_epsp_seed = 314
num_sims=4

#args='-BLA DMS'.split()# -seed 123'.split()
args='single -sim_type BLA_DMS_dispersed -num_clustered 16 -num_dispersed 75 -start_stim 0.1'.split()
#args = sys.argv[1:]
params=su.parsarg(args)

for ii in range(num_sims):
    ####### randomly select seed and call upstate_main ############Ad
    if not params.seed:
        dispersed_seed=np.random.randint(0,32000) 
    else:
        dispersed_seed=params.seed
    sims=su.specify_sims(params.sim_type,clustered_seed,dispersed_seed,single_epsp_seed, params)
    tt_Ctx_SPN = {'fname': params.tt,'syn_per_tt':2} 
    model=su.upstate_main(params.SPN, mod_dict, **sims[0]['kwds'],do_plots=False,filename=sims[0]['name'], time_tables=tt_Ctx_SPN)
    print(sims[0])

