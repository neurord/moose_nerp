import sys
import numpy as np
import argparse
import sim_upstate as su

def parsarg(commandline):
    small_parser=argparse.ArgumentParser()
    small_parser.add_argument('-BLA', type=str, help='clustered stim from BLA to DMS or DLS')
    small_parser.add_argument('-tt',type=str,default='networks/FullTrialMediumVariabilitySimilarTrialsTruncatedNormal', help='spike train file')
    small_parser.add_argument('-SPN', type=str, default="D1MatrixSample2", help='neuron module')
    small_parser.add_argument('-seed', type=int, default=172,help='dispersed spine seed')

    args=small_parser.parse_args(commandline)
    return args

mod_dict = su.make_mod_dict()
clustered_seed = 135
single_epsp_seed = 314

args='-BLA DMS -seed 123'.split()
#args = sys.argv[1:]
params=parsarg(args)
sim_type='BLA'+params.BLA+'dispersed'
dispersed_seed=params.seed
sims=su.specify_sims(sim_type,clustered_seed,dispersed_seed,single_epsp_seed)
tt_Ctx_SPN = {'fname': params.tt,'syn_per_tt':2} 
model=su.upstate_main(params.SPN, mod_dict, **sims[0]['kwds'],do_plots=True,filename=sims[0]['name']+str(), time_tables=tt_Ctx_SPN)
print(sims[0])

