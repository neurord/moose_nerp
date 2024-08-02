#!/usr/bin/env python3
"""
Simulate upstate conditions for Patch Samples 4-5 and Matrix Samples 2-3 models.

Modify local channel conductances at site of clustered input for each neuron 
to achieve upstate duration and amplitude consistent with experimental averages.

Do current injection with modified conductances to confirm modifying them does 
not greatly alter the fit to current injection data.

Simulate without blocking sodium channels.

Simulate with additional dispersed inputs.

Simulation steps:

For each neuron:
    - Randomly select parameters from within a range to vary
        - parameters to vary:
        - Random seed necessary for selecting parameters?
    For each set of parameters:
        - Use same random seeds to control synapse selection
        - [done] simulate upstate only: Need an upstate seed (same every sim/param set)
        - [done] Simulate dispersed only: Need a Dispersed seed (same every sim/param set for now)
        - [done] Simulate upstate and dispersed together: Use same upstate seed and same dispersed seed
        - [ ] range over dispersion frequency params
        
        - [later] Should we simulate "spatially disperse" the clustered inputs but at the same time as a control? Not for now
        - [done] Simulate single EPSP (EPSP seed?-same every sim)
        - [done] Simulate IV traces to compare to original model IV to see how much the optimization fit is messed up
        - [ ] simulate upstate plus current injection at increasing steps...

TO DO:

Save voltage at soma from each simulation

File name scheme:
param_set_X_sim_name_sim_variable_name_value_neuron-name_vm.txt
e.g.
param_set_1__upstate_plus_dispersed__dispersed_freq_375__D1PatchSample5_vm.txt



Make plotting optional argument

Save parameter variation values (and any necessary random seeds?) for each simulation

param_set_list.csv

set_ID (corresponds to param_set_X in filenames), var1name, var2name...
e.g.
0,      2, 3,...



"""

import importlib
import numpy as np


def rand_mod_dict():
    mod_dict = {"D1MatrixSample2": {},"D1MatrixSample3": {}, "D1PatchSample5": {}}

    var_range = {
        "KaS": [0, 4],
        "NMDA": [0, 4],
        "CaR": [0, 20],
        "AMPA": [0.1, 1],
        "CaL12": [0, 4],
        "CaL13": [0, 4],
        "CaT32": [0, 4],
        "CaT33": [0, 4],
        "Kir": [0, 4],
        "KaF": [0, 4],
    }
    for mod in mod_dict:
        for var in var_range:
            mod_dict[mod][var] = np.random.uniform(*var_range[var])

    return mod_dict


def make_mod_dict():

    mod_dict = {
        "D1MatrixSample2": {},
        "D1MatrixSample3": {},
        # "D1PatchSample4": {},
        "D1PatchSample5": {},
    }

    mod_dict["D1MatrixSample2"] = {
        "KaS": 0.5,  # 0.2,
        "NMDA": 2.25,
        "CaR": 10,  # 1,
        "AMPA": 0.4,  # 2,
        "CaL12": 1,  # 0.01,
        "CaL13": 1,  # 0.25,
        "CaT32": 0.5,  # 0.001,
        "CaT33": 1,  # 0.05,
        "Kir": 1,
    }
    mod_dict["D1MatrixSample3"] = {
        "KaS": 0.5,  # 0.2,
        "NMDA": 2.25,
        "CaR": 10,  # 1,
        "AMPA": 0.4,  # 2,
        "CaL12": 1,  # 0.01,
        "CaL13": 1,  # 0.25,
        "CaT32": 0.5,  # 0.001,
        "CaT33": 1,  # 0.05,
        "Kir": 1,
    }
    # mod_dict["D1MatrixSample3"] = {
    #     "KaS": 1,
    #     "NMDA": 1,
    #     "CaR": 1,
    #     "AMPA": .25,#1,
    #     "CaL12": 1,
    #     "CaL13": 1,
    #     "CaT32": 1,
    #     "CaT33": 1,
    #     "Kir": 1,
    #     "KaF": 1,
    #     "CaCC": 0,
    # }
    # mod_dict["D1PatchSample4"] = {
    #     "KaS": 1,
    #     "NMDA": 2,
    #     "CaR": 100,
    #     "AMPA": .19,#1,
    #     "CaL12": 1,
    #     "CaL13": 1,
    #     "CaT32": 1,
    #     "CaT33": 1,
    #     "Kir": 1,
    #     "KaF": 1,
    # }
    mod_dict["D1PatchSample5"] = {
        "KaS": 1,
        "NMDA": 2.25,
        "CaR": 2,
        "AMPA": 0.4,  # .3,#1,
        "CaL12": 1,
        "CaL13": 1,
        "CaT32": 1,
        "CaT33": 1,
        "Kir": 1,
        "KaF": 1,  # 1,
    }

    return mod_dict


def mod_local_gbar(complist, mod_dict):
    # input_parent_dends = set([i.parent.parent for i in inputs])
    for comp in complist:
        for chan in mod_dict:
            for child in comp.children:
                if chan == child[0].name and "HHChannel" in str(child[0].__class__):
                    # print(child[0].Gbar)
                    child[0].Gbar *= mod_dict[chan]
                    # print(child[0].Gbar)
                    # print(child.path)


def mod_dist_gbar(model, mod_dict):
    for chan in mod_dict:
        if chan in model.Condset.D1.keys():
            #print("{} before: {}".format(chan, model.Condset.D1[chan]))
            model.Condset.D1[chan][model.param_cond.dist] *= mod_dict[chan]
            #print("modifying {} ".format(chan))
            #print("{} after: {}".format(chan, model.Condset.D1[chan]))


def setup_model(model, mod_dict, block_naf=False, Mg_conc=1, filename=None): #spine_parrent
    model = importlib.import_module("moose_nerp.{}".format(model))
    # from IPython import embed; embed()
    from moose_nerp.prototypes import create_model_sim
    from moose_nerp.prototypes import spatiotemporalInputMapping as stim
    import moose

    if filename is not None:
        model.param_sim.fname = filename
    #override parameters in param_sim
    model.param_sim.save_txt = True
    model.param_sim.plot_vm = False
    model.param_sim.plot_current = False #True
    model.param_sim.plot_current_message = "getIk"
    model.param_sim.simtime=0.8
    model.spineYN = True
    model.calYN = True
    model.synYN = True
    #model.SpineParams.explicitSpineDensity = 1e6
    if any("patch" in v for v in model.morph_file.values()):
        # model.SpineParams.spineParent = "570_3"
        model.clusteredparent = "570_3"
    if any("matrix" in v for v in model.morph_file.values()):
        # model.SpineParams.spineParent = "1157_3"
        model.clusteredparent = "1157_3" #4th order, terminal branch; distance is 119 um from soma
        model.clusteredparent = "785_3" #1st order, tert is either 889_3 or 1483, with >= 4 branches and correct length for both DMS and DLS
    #if spine_parent='branch':  #or possibly specified clusteredparent?
        #model.SpineParams.spineParent = model.clusteredparent
    #else:
    model.SpineParams.spineParent = "soma" #model.clusteredparent  # # clusteredparent will create all spines in one compartment only
    if model.SpineParams.spineParent != 'soma':
        model.SpineParams.explicitSpineDensity =0.5e6 #increase spine density if only putting spines on one branch
    modelname = model.__name__.split(".")[-1]
    model.param_syn._SynNMDA.Gbar = 10e-09 * mod_dict[modelname]["NMDA"]
    model.param_syn._SynNMDA.tau2 *= 2
    model.param_syn._SynNMDA.tau1 *= 2
    model.param_syn._SynAMPA.Gbar = 1e-9 * mod_dict[modelname]["AMPA"]
    model.param_syn._SynAMPA.spinic=True #allow synapses on dendrites even if there are spines
    model.param_syn._SynNMDA.spinic=True
    mod_dist_gbar(model, mod_dict[modelname])
    print('NaF vals', model.param_cond.Condset['D1']['NaF'], 'block_naf=', block_naf)
    if block_naf:
        for k, v in model.Condset.D1.NaF.items():
            model.Condset.D1.NaF[k] = 0.0

    if Mg_conc!=model.param_syn.SYNAPSE_TYPES.nmda.MgBlock.C:
        model.param_syn.SYNAPSE_TYPES.nmda.MgBlock.C = Mg_conc
    # create_model_sim.setupOptions(model)

    # create_model_sim.setupNeurons(model)

    # create_model_sim.setupOutput(model)

    return model


def iv_main(model, mod_dict, block_naf=False, filename=None):
    print("filename: {}".format(filename))
    import numpy as np
    from moose_nerp.prototypes import create_model_sim
    from moose_nerp.prototypes import spatiotemporalInputMapping as stim
    import moose

    model = setup_model(model, mod_dict, block_naf=block_naf, filename=filename)
    model.param_sim.plot_current = False

    create_model_sim.setupOptions(model)
    create_model_sim.setupNeurons(model)
    create_model_sim.setupOutput(model)
    create_model_sim.setupStim(model)

    create_model_sim.runAll(model)

def upstate_main(
    model,
    mod_dict,
    block_naf=False,
    num_clustered=14,
    n_per_clustered=2,
    num_dispersed=100,
    freq_dispersed=375,
    n_per_dispersed=10,
    clustered_seed=None,
    dispersed_seed=None,
    filename=None,
    do_plots=False,
    injection_current = None,
    time_tables=None,
    start_cluster=0.3,
    end_cluster=None, #if defined, this will override frequency specified
    start_dispersed=0.05,
    end_dispersed=0.6,
    Mg_conc=1,
    min_dist_disp=None, 
    max_dist_disp=None, 
    min_dist_clust=100e-6, 
    max_dist_clust=150e-6, 
    spc=6,
    spc_subset=6, #add spine_parent
    ):
    import numpy as np
    from moose_nerp.prototypes import create_model_sim, tables
    from moose_nerp.prototypes import spatiotemporalInputMapping as stim
    from moose_nerp.prototypes import util as _util
    from moose_nerp.graph import plot_channel,spine_graph
    import moose

    model = setup_model(model, mod_dict, block_naf=block_naf, Mg_conc=Mg_conc,filename=filename) #send in spine_parent
    create_model_sim.setupOptions(model)

    create_model_sim.setupNeurons(model)

    modelname = model.__name__.split(".")[-1]
    neuron=_util.select_neuron(model.neurons['D1'])
    bd = stim.getBranchDict(neuron)
    branch_list=_util.select_branch(model.clusteredparent)
    model.param_sim.plotcomps = [s.split("/")[-1] for s in bd[branch_list[0]]["BranchPath"]] #add in parent_dend for plotting
    inputs=[]; far=[]
    ############# Identify a cluster of synapses for stimulation ########################
    ### updated to make specified number of inputs per branch/compartment
    ### update to ensure each set of inputs has unique parent branch?
    if num_clustered > 0:
        if model.SpineParams.spineParent != 'soma': #clustered BLA is distributed, 2 per comp on multile branches
            possibleBranches, branch_len = stim.getBranchesOfOrder(neuron, -1, n=1,  #select one terminal branch; n='all' will select multiple terminal on specified primary; None will include all order branches, 3 will use only tertiary 
                                          commonParentOrder=1, commonParentBranch=branch_list[0]) #, min_length = 120e-6#select with parent=specified primary, with 120 um length - but not for exampleClustered
        if 'DLS' in filename or 'DMS' in filename:
            print('simulating',num_clustered,'  BLA inputs beween', min_dist_clust, max_dist_clust, 'um')
            if model.SpineParams.spineParent == 'soma': #inputs dispersed over entire tree.  maybe 4 spine_per_comp to get more inputs on each branch?
                inputs, groups=stim.n_inputs_per_comp(model, nInputs = int((spc/spc_subset)*num_clustered),spine_per_comp=spc,seed=clustered_seed, minDistance=min_dist_clust, maxDistance=max_dist_clust)
            else:
                tries=0
                success=0
                while tries<8 and success==0: #if elist is not big enough, try a few more times
                    elist = stim.generateElementList(neuron, wildcardStrings=['ampa,nmda'], elementType='SynChan',
                                            minDistance=min_dist_clust, maxDistance=max_dist_clust, commonParentOrder=0,  #
                                            numBranches=1, min_length=10e-6, branch_list=possibleBranches
                                            ) 
                    tries+=1
                    if len(elist)>=num_clustered:
                        success=1
                    else:
                        print('only', len(elist), 'possible inputs on try', tries)
                inputs = stim.selectRandom(elist,n=num_clustered,func='elist_DLS',seed=clustered_seed)
        else:
            inputs = stim.exampleClusteredDistal(
                model,
                nInputs=num_clustered,
                branch_list=branch_list,
                seed=clustered_seed,  # 6,
            )
        parent_dend = [i.parent.parent for i in inputs]
        parent_spine = [i.parent for i in inputs]
        parents = parent_dend + parent_spine
        input_parent_dends = set(parents)
        # mod_local_gbar(input_parent_dends, mod_dict[modelname])
        print('clustered stim for seed', clustered_seed) #if want to exclude these branches from dispersed input, need to put into branch_list
        far.append(stim.report_element_distance(inputs))
        cluster_comps=list(np.unique([pd.path for pd in parent_dend]))
    comps = [moose.element(comp) for comp in bd[branch_list[0]]["BranchPath"]] #plot compartments for 1st branch
    spines = [sp[0] for comp in comps for sp in comp.children if "head" in sp.name] #

    # mod_local_gbar(set(comps+spines), mod_dict[modelname])
    # from IPython import embed; embed()

    ############# Identify a set of synapses for dispersed stimulation ########################
    #dispersed inputs go to all branches except those stimulated (if specified in branch_list). 
    if num_dispersed>0:
        if model.SpineParams.spineParent=='soma': #i.e., if dispersing inputs everywhere
            print(filename,'has excluded synapses:', [i.path for i in inputs], 'dispersed',n_per_dispersed, freq_dispersed) 
            if max_dist_disp:
                dispersed_inputs = stim.dispersed(model,nInputs=num_dispersed,
                    seed=dispersed_seed, minDistance=min_dist_disp, maxDistance=max_dist_disp, exclude_syn=inputs) #using seed - always same. exclude synapses with clustered inputs, but not branch
            else:
                dispersed_inputs = stim.dispersed(model,nInputs=num_dispersed,
                    exclude_branch_list=branch_list, seed=dispersed_seed) # exclude entire branch with clustered inputs.  do not specify min and max distances
        else:
            possibleBranches, _ = stim.getBranchesOfOrder(neuron, None, n='all', min_path_length=min_dist_disp, max_path_length=max_dist_disp, #select multiple branches on specified primary 
                                          commonParentOrder=1, commonParentBranch=branch_list[0]) #select with parent=specified primary, with 120 um length
            print(filename,'dispersing inputs on:', possibleBranches, 'dispersed',n_per_dispersed, freq_dispersed)
            dispersed_inputs = stim.dispersed(model,nInputs=num_dispersed, exclude_syn=inputs,
                branch_list=possibleBranches,seed=dispersed_seed, minDistance=min_dist_disp, maxDistance=max_dist_disp) #using seed - always same; min_disp and max_disp needed here, too
        far.append(stim.report_element_distance(dispersed_inputs))
        disp_comps=list(np.unique([i.parent.parent.path for i in dispersed_inputs]))
        model.param_sim.plotcomps+=[dc.split('/')[-1] for dc in disp_comps]
    print('num dispersed stim for seed',dispersed_seed,'=',num_dispersed)
    print('FURTHEST ELEMENTS', [f.path for f in far])

    create_model_sim.setupOutput(model)
    # import pdb;pdb.set_trace()
     ############## Identify set of synaptic inputs, one set dispersed, the other a cluster ###################
    if model.param_sim.plot_current:
        plotgates = []#["CaR", "CaT32", "CaT33", "CaL12", "CaL13"]
        plotchan=plotgates+["SKCa", "ampa", "nmda","CaL12", "CaT32"]
        msg='getGk'
        spine_cur_tab=plot_channel.plot_gates(model,plotgates,plotchan,far,msg)
    ############## create time table inputs, either specific frequency or from external spike trains ###################
    from moose_nerp.prototypes import ttables #move up
    tt_Ctx_SPN = ttables.TableSet('CtxSPN', time_tables['fname'],syn_per_tt=time_tables['syn_per_tt']) #move up
    ttables.TableSet.create_all() #move up
    if num_clustered > 0:
        input_subset=[list(a['inputs'])[0:spc_subset] for a in groups.values()]  
        inputs=[i for inp in input_subset for i in inp]
        if spc_subset<spc:
            remaining={c:{'dist':g['dist'],'inputs':g['inputs'][spc_subset:spc]} for c,g in groups.items()}
            BLA_inputs={k: v for k, v in sorted(remaining.items(), key=lambda item: item[1]['dist'])}
        input_times,tt = stim.createTimeTables(
            inputs, model, n_per_syn=n_per_clustered, start_time=start_cluster,end_time=end_cluster, input_spikes=tt_Ctx_SPN)#, freq=80) #FIXME.  make syn_per_comp parameter, divide by n_per_cluster?
        #n_per_syn is how many times each synapse in the cluster receives an input, default freq for all synapses =500 Hz, unused if using time tables
    if num_dispersed>0:
        inputs_disp,tt = stim.createTimeTables(dispersed_inputs, model, n_per_syn=n_per_dispersed, start_time=start_dispersed,  #n_per_syn is unused if using time tables
            freq=freq_dispersed, end_time=end_dispersed, input_spikes=tt_Ctx_SPN)# freq_dispersed is unused if using time tables #=time_tables
        print('dispersed inputs:', time_tables, 'num stimuli=', len(inputs_disp), '\n   begin=', inputs_disp[0:5], '\n   end=', inputs_disp[-5:])
    else:
        end_dispersed=round(input_times[-1],3) #use time of last clustered stim for filename if no dispersed

    # c.Rm = c.Rm*100
    if injection_current is not None:
        model.param_sim.injection_current = [injection_current]
        model.param_sim.injection_delay = 0.3
        model.param_sim.injection_width = 0.1
        create_model_sim.setupStim(model)
        #print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        model.pg.firstLevel = injection_current
        
        #from IPython import embed; embed()
    if spc_subset<spc:
        iterations=2
    else:
        iterations=1
    for ii in range(iterations):
        model.param_sim.fname=filename+'_'+str(num_dispersed)+'_'+str(num_clustered)
        print('ready to simulate, simtime=', model.param_sim.simtime)
        moose.reinit()
        moose.start(model.param_sim.simtime)

        if do_plots:
            create_model_sim.neuron_graph.graphs(model, model.vmtab, False, model.param_sim.simtime)
            from matplotlib import pyplot as plt
            ######## Add time of clustered stim to figure #########3
            ax = plt.gca()
            ax.set_title(modelname+' '+model.param_sim.fname)
            if num_clustered > 0:
                ax.axvspan(
                    input_times[0], input_times[-1], facecolor="gray", alpha=0.5, zorder=-10
                )
            elif num_dispersed > 0:
                ax.axvspan(
                    inputs_disp[0], inputs_disp[-1], facecolor="gray", alpha=0.5, zorder=-10
                )            
            import pprint
            # ax.text(.5,.5,pprint.pformat(mod_dict[modelname]), transform = ax.transAxes)
            plt.ion()
            plt.show()
            if len(model.spinevmtab[0]):
                spine_graph.spineFig(model,model.param_sim.simtime,model.spinevmtab)

            #create_model_sim.neuron_graph.dist_vs_diam(model,modelname,model.param_sim.fname,num_dispersed)

            if model.param_sim.plot_current:
                plt.figure()
                plt.suptitle(modelname+' '+model.param_sim.fname)
                for cur in spine_cur_tab:
                    t=np.linspace(0,model.param_sim.simtime,cur.size,endpoint=False)
                    plt.plot(t,cur.vector, label=cur.name.strip("_"))

                plt.legend()
                plt.ylabel(msg)
                plt.xlabel('Time (sec)')
                plt.show()

        if max_dist_disp:
            max_dist=max_dist_disp
        elif max_dist_clust:
            max_dist=max_dist_clust
        else:
            max_dist=1000e-6
        if block_naf:
            model.param_sim.fname='_'.join([model.param_sim.fname,str(end_dispersed),str(end_cluster),str(round(max_dist*1e6)),str(spc),str(dispersed_seed)])
        else:
            model.param_sim.fname='_'.join([model.param_sim.fname,str(end_dispersed),str(end_cluster),str(mod_dict[modelname]['NMDA']),str(round(max_dist*1e6)),'NaF',str(dispersed_seed)])

        tables.write_textfiles(model, 0, ca=False, spines=False, spineca=False)
        print("upstate filename: {}".format(model.param_sim.fname))

        #though additional inputs provided, nothing will happen if iterations is 1
        num_BLA_comps=3 # make this param?
        if 'DMS' in filename:
            new=[x['inputs'] for x in list(BLA_inputs.values())[:num_BLA_comps]] #closest n comps
            new_dist=[x['dist'] for x in list(BLA_inputs.values())[:num_BLA_comps]]
        elif 'DLS' in filename:
            new=[x['inputs'] for x in list(BLA_inputs.values())[len(BLA_inputs)-num_BLA_comps:]] #furthest n comps,  May need to make sure they are > 150 um
            new_dist=[x['dist'] for x in list(BLA_inputs.values())[len(BLA_inputs)-num_BLA_comps:]]
        new_inputs=[x for y in new for x in y]
        print('Adding additional inputs from BLA to existing clusters at these distances:', new_dist)
        input_times,tt = stim.createTimeTables(
            new_inputs, model, n_per_syn=n_per_clustered, start_time=start_cluster,end_time=end_cluster, input_spikes=tt_Ctx_SPN)
        num_clustered+=len(new_inputs)
    # return model.vmtab['D1'][0].vector
    # return plt.gcf()
    #from IPython import embed
    #embed()
    return model


def subprocess_main(function, model, mod_dict, kwds,time_limit):
    from multiprocessing import Process, Queue
    import time
    # q = Queue()
    p = Process(target=function, args=(model, mod_dict), kwargs=kwds)
    p.start()
    # result = q.get()
    # print(result)
    remaining = time_limit - time.time()
    if remaining <=0:
        p.terminate()
        return
    p.join(timeout=remaining-10)
    p.terminate()

    # return result


def mpi_main(mod_dict, sims):
    if __name__ == "__main__":
        from mpi4py import MPI
        from mpi4py.futures import MPICommExecutor
        import time
        import pickle

        with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
            time_limit = time.time() + 60 * 60 * 8#3.75  # 3.75 hours
            
            if executor is not None:
                results = []
                make_new_params = False
                if make_new_params:
                    param_set_list = [rand_mod_dict() for i in range(2)]#10000)]
                    with open("params.pickle", "wb") as f:
                        pickle.dump(param_set_list, f)
                else:
                    with open("params.pickle",'rb') as f:
                        param_set_list = pickle.load(f)
                # print(param_set_list)
                for i, param_set in enumerate(param_set_list[:1020]):#1020
                    for key in mod_dict:
                        for sim in sims:
                            #                    param_set_1__upstate_plus_dispersed__dispersed_freq_375__D1PatchSample5_vm.txt
                            filename = (
                                "param_set_"
                                + str(i)
                                + "__"
                                + sim["name"]
                                + "__dispersed_freq_"
                                + str(sim["kwds"].get("freq_dispersed"))
                                + "__injection_current_"
                                + str(sim["kwds"].get("injection_current"))
                                + "__"
                                + key
                            )
                            kwds = {k: v for k, v in sim["kwds"].items()}
                            kwds["filename"] = filename
                            # r = p.apply_async(upstate_main, args=(key, mod_dict),kwds={'num_dispersed':0})
                            # r = p.apply_async(sim["f"], args=(key, param_set), kwds=kwds)
                            r = executor.submit(
                                subprocess_main, *(sim["f"], key, param_set, kwds, time_limit)
                            )
                            results.append(r)

                while True:
                    if all([res.done() for res in results]):
                        print('all results returned done; breaking')
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

def specify_sims(sim_type,clustered_seed,dispersed_seed,single_epsp_seed,params=None):
    if sim_type=='rheobase_only':
        sims = [
            {
                "name": "rheobase_only",
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": 0,
                    "block_naf": False,
                    "num_clustered": 0,
                    "clustered_seed": clustered_seed,
                    "injection_current": inj,
                },
            } for inj in np.arange(0,226e-12,25e-12)]
    elif sim_type=='upstate_plus_rheobase':
        sims = [
         {
                 "name": "upstate_plus_rheobase",
                 "f": upstate_main,
                 "kwds": {
                     "num_dispersed": 0,
                     "block_naf": False,
                     "num_clustered": 14,
                     "clustered_seed": clustered_seed,
                     "injection_current": 25e-12,
                 },
             } for inj in np.arange(0,226e-12,25e-12)]
    elif sim_type=='upstate_plus_new_dispersed_300ms':
        sims = [
             {
                 "name": "upstate_plus_new_dispersed_300ms",
                 "f": upstate_main,
                 "kwds": {
                     "num_dispersed": 100,
                     "freq_dispersed": 200,
                     "dispersed_seed": dispersed_seed,
                     "clustered_seed": clustered_seed,
                 },
             }]# for freq in np.arange(200,501,50)]
    elif sim_type=='new_dispersed_300ms_only':
        sims = [
            {
                "name": "new_dispersed_300ms_only",
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": 100,
                    "num_clustered": 0,
                    "freq_dispersed": 250,
                    "dispersed_seed": dispersed_seed,
                    "clustered_seed": clustered_seed,
                },
            } ] #for freq in np.arange(200,501,50)]
    elif sim_type=='upstate_only':
        sims = [
            {
                "name": "upstate_only",
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": 0,
                    "block_naf": True,
                    "num_clustered": 14,
                    "clustered_seed": clustered_seed,
                },
            }]
    elif sim_type=='BLA_DMS' or sim_type=='BLA_DLS':
        sims = [
            {
                "name": sim_type,
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": params.num_dispersed, 
                    "num_clustered": params.num_clustered,
                    "freq_dispersed": 50,
                    "dispersed_seed": dispersed_seed,
                    "clustered_seed": clustered_seed,
                    "n_per_clustered": params.n_per_clustered,
                   "block_naf": params.block_naf,
                 },
            } ]
    elif sim_type=='single_epsp':
        sims = [
            {
                "name": "single_epsp",
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": 0,
                    "block_naf": True,
                    "num_clustered": 1,
                    "n_per_clustered": 1,
                    "clustered_seed": single_epsp_seed,
                    "Mg_conc": 0.05, #cannot assign zero
                },
            }]
    else:
        sims=[ {"name": "iv_curves", "f": iv_main, "kwds": {}}]
    for sim in sims:
        sim['kwds']['min_dist_disp']=params.min_dist_disp
        sim['kwds']['max_dist_disp']=params.max_dist_disp
        sim['kwds']['min_dist_clust']=params.min_dist_clust
        sim['kwds']['max_dist_clust']=params.max_dist_clust
        sim['kwds']["start_dispersed"]=params.start_dispersed
        sim['kwds']["end_dispersed"]=params.end_dispersed
        sim['kwds']["start_cluster"]=params.start_cluster
        sim['kwds']["end_cluster"]=params.end_cluster
        sim['kwds']["spc"]=params.spc
        if params.spc_subset==None or params.spc_subset>params.spc:
            sim['kwds']["spc_subset"]=params.spc
        else:
            sim['kwds']["spc_subset"]=params.spc_subset
        if not params.spkfile and sim_type.startswith('BLA'):
            sim['kwds']['n_per_dispersed']=round((params.end_dispersed-params.start_dispersed)*sim['kwds']['freq_dispersed'])
            sim['kwds']['freq_dispersed']*=sim['kwds']['num_dispersed'] #redefine frequency for BLA dispersed to achieve original freq at EACH synapse, instead of collectively
     
    return sims
    
def parsarg(commandline):
    import argparse
    small_parser=argparse.ArgumentParser()
    small_parser.add_argument('base_sim', type=str, default='mpi_main', help='single, iv, mp, or mpi_main')
    small_parser.add_argument('-sim_type', type=str, default='rheobase_only', help='one of the choices from specify_sims')
    small_parser.add_argument('-spkfile',type=str, help='spike train file')
    small_parser.add_argument('-SPN', type=str, default="D1MatrixSample2", help='neuron module')
    small_parser.add_argument('-seed', type=int, help='dispersed spine seed')
    small_parser.add_argument('-start_cluster', type=float, default=0.3, help='time to start clustered, BLA stim, in sec')
    small_parser.add_argument('-end_cluster', type=float, help='time to end clustered, BLA stim, in sec')
    small_parser.add_argument('-num_dispersed', type=int, default=75, help='number of dispersed inputs')
    small_parser.add_argument('-num_clustered', type=int, default=16, help='number of BLA inputs')
    small_parser.add_argument('-start_dispersed', type=float, default=0.1, help='time to start dispersed stim')
    small_parser.add_argument('-end_dispersed', type=float, default=0.6, help='time to end dispersed stim')
    small_parser.add_argument('-block_naf', type=bool, default=False)
    small_parser.add_argument('-min_dist_disp', type=float, default=None, help='minimum distance for dispersed inputs') 
    small_parser.add_argument('-max_dist_disp', type=float, default=None, help='maximum distance for dispersed inputs') 
    small_parser.add_argument('-min_dist_clust', type=float, default=50e-6, help='minimum distance for clustered inputs') #Plotkin: 80-130 um, alter1 = 100 to 180 um, alter2: 150 to 220 or more
    small_parser.add_argument('-max_dist_clust', type=float, default=350e-6, help='maximum distance for clustered inputs')
    small_parser.add_argument('-n_per_clustered', type=int, default=8, help='number of stim per clustered synapse, unused if specify spike train file') 
    small_parser.add_argument('-spc', type=int, default=6, help='spines per compartment for each cluster')
    small_parser.add_argument('-spc_subset', type=int, default=None, help='spines per compartment for each cluster WITHOUT BLA input')

    args=small_parser.parse_args(commandline)
    return args

if __name__ == "__main__":
    mod_dict = make_mod_dict()
    clustered_seed = 135
    dispersed_seed = 172
    single_epsp_seed = 314
    #sim_type='rheobase_only' #'new_dispersed_300ms_only'#  or 'upstate_only'?

    import sys

    args = sys.argv[1:]
    args='single -sim_type BLA_DLS -num_clustered 24 -num_dispersed 0 -spc_subset 3 -min_dist_clust 50e-6 -max_dist_clust 350e-6 -start_cluster 0.1 -end_cluster 0.3 -block_naf True -spkfile spn1_net/Ctx1000_exp_freq50.0'.split() #for debugging
    params=parsarg(args)
    sims=specify_sims(params.sim_type,clustered_seed,dispersed_seed,single_epsp_seed,params)
 
    if params.base_sim == "single":
        spn_name=params.SPN.split('.')[-1][0:5]+params.SPN.split('.')[-1][-1]
        if params.spkfile:
            tt_Ctx_SPN={'fname':params.spkfile,'syn_per_tt':1} #must be 1 if you use the tables for both clustered and dispersed
        else:
            tt_Ctx_SPN=None
        model=upstate_main(params.SPN, mod_dict, **sims[0]['kwds'],do_plots=True,filename=spn_name+sims[0]['name'], time_tables=tt_Ctx_SPN)
        print(sims[0])
        #else: #original code
            # upstate_main(list(mod_dict.keys())[0],mod_dict)
            #upstate_main("D1PatchSample5", mod_dict, do_plots=True)

    elif params.base_sim == "iv":
        # upstate_main(list(mod_dict.keys())[0],mod_dict)
        iv_main("D1PatchSample5", mod_dict, filename="test")

    elif params.base_sim == "mp":
        results = []
        from multiprocessing import Pool

        with Pool(16, maxtasksperchild=1) as p:
            param_set_list = [rand_mod_dict() for i in range(10000)]

            import pickle

            with open("params.pickle", "wb") as f:
                pickle.dump(param_set_list, f)

            #print(param_set_list)
            for i, param_set in enumerate(param_set_list):
                for key in mod_dict:
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
    else:
        mpi_main(mod_dict, sims)
        print('done?')

