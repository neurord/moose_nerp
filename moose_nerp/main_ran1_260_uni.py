################# To run on the Neuroscience Gateway############
# this file, and possibly NSG_plasticity_moosemain.py and sim_upstate.py
# need to be one directory upward
###############################################################
import NSG_plasticity_moosemain as nsgpm
import sim_upstate as su

#260 spines * 0.8 prob of connect = 208 spines
def mpi_main(num_sims=100,randomize=1,global_test=False,spines=260,distr='norm'):
    if __name__ == "__main__":
        print('running mpi main')
        
        from mpi4py import MPI
        from mpi4py.futures import MPICommExecutor
        import time
        import pickle

        with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
            time_limit = time.time() + 60 * 60 * 8 if not global_test else time.time() + 60*60*.1#3.75  # 3.75 hours
            
            if executor is not None:
                print(executor)
                results = []
                make_new_params = True
                if make_new_params:
                    n = num_sims if not global_test else 52
                    param_set_list = nsgpm.make_rand_mod_dict(n=n,spines=spines,distr=distr)
                    with open("testparams.pickle", "wb") as f:
                        pickle.dump(param_set_list, f)
                else:
                    with open("testparams.pickle",'rb') as f:
                        param_set_list = pickle.load(f)
                #print(param_set_list)
                for i, param_set in enumerate(param_set_list):#1020
                    param_set['randomize']=randomize
                    print(i, param_set)
                    r = executor.submit(
                                nsgpm.subprocess_main, *(nsgpm.moose_main,"str_net/FullTrialLowVariabilitySimilarTrialsTruncatedNormal", param_set,  time_limit)
                            )
                    results.append(r)

                while True:
                    if all([res.done() for res in results]):
                        print('all results returned done; breaking')
                        #import pdb;pdb.set_trace()
                        break

                    if time.time() >= time_limit:
                        print("****************** TIME LIMIT EXCEEDED***********")
                        for res in results:
                            res.cancel()
                            #print('canceling', res)
                            
                        #executor.shutdown(wait=False)
                        print('shutting down')
                        MPI.COMM_WORLD.Abort()
                        print('aborting')
                        break
                print('done')
                return
            #while True:
            #    if time.time() >= time_limit:
            #        break
            #MPI.COMM_WORLD.Abort()


if __name__ == "__main__":

    import sys

    args = sys.argv
    # args.append('--single')
    if "--test" in args:
        global_test = True
    else:
        global_test = False
    print('global test = {}'.format(global_test))
    if len(args) > 1 and args[1] == "--single":
        # upstate_main(list(mod_dict.keys())[0],mod_dict)
        ClusteringParams = {'n_clusters':20, 'cluster_length':20e-6, 'n_spines_per_cluster':10}
        nsgpm.moose_main("str_net/FullTrialLowVariabilitySimilarTrialsTruncatedNormal", seed=42,ClusteringParams=ClusteringParams,global_test=global_test)

    elif len(args) > 1 and args[1] == "--iv":
        mod_dict=su.make_mod_dict()
        # upstate_main(list(mod_dict.keys())[0],mod_dict)
        su.iv_main("D1PatchSample5", mod_dict, filename="test")  ######## Probably better to use sim_upstate.py for these sims

    elif len(args) > 1 and args[1] == "--mp":                   ######## Probably better to use sim_upstate.py for these sims
        results = []
        from multiprocessing import Pool

        with Pool(16, maxtasksperchild=1) as p:
            param_set_list = [su.rand_mod_dict() for i in range(10000)] #use 2-3 for testing
            clustered_seed = 135
            dispersed_seed = 172
            single_epsp_seed = 314
            sim_type='rheobase_only'
            sims=su.specify_sims(sim_type,clustered_seed,dispersed_seed,single_epsp_seed)

            import pickle

            with open("params.pickle", "wb") as f:
                pickle.dump(param_set_list, f)

            #print(param_set_list)
            for i, param_set in enumerate(param_set_list): 
                for key in param_set.keys():
                    for sim in sims:
                        # param_set_1__upstate_plus_dispersed__dispersed_freq_375__D1PatchSample5_vm.txt

                        filename = (
                            "param_set_"
                            + str(i)
                            + "__"
                            + sim["name"]
                            + "__dispersed_freq_"
                            + str(sim["kwds"].get("freq_dispersed"))
                            + "__"
                            + key
                        )
                        kwds = {k: v for k, v in sim["kwds"].items()}
                        kwds["filename"] = filename
                        # r = p.apply_async(upstate_main, args=(key, mod_dict),kwds={'num_dispersed':0})
                        r = p.apply_async(sim["f"], args=(key, param_set), kwds=kwds)
                        results.append(r)
            for res in results:
                res.wait()
    else:  #when running on NSG
        mpi_main(num_sims=200,spines=208,distr='uni')
        print('done?')

