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


def setup_model(model, mod_dict, block_naf=False, Mg_conc=1, filename=None):
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
    model.param_sim.simtime=1.0
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

    model.SpineParams.spineParent = model.clusteredparent  #"soma" # clusteredparent will create all spines in one compartment only
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
    min_disp=100e-6, #change to 20e-6
    max_disp=150e-6, #change to 300e-6
    ):
    import numpy as np
    from moose_nerp.prototypes import create_model_sim, tables
    from moose_nerp.prototypes import spatiotemporalInputMapping as stim
    from moose_nerp.prototypes import util as _util
    from moose_nerp.graph import plot_channel,spine_graph
    import moose

    model = setup_model(model, mod_dict, block_naf=block_naf, Mg_conc=Mg_conc,filename=filename)
    create_model_sim.setupOptions(model)

    create_model_sim.setupNeurons(model)

    modelname = model.__name__.split(".")[-1]
    neuron=_util.select_neuron(model.neurons['D1'])
    bd = stim.getBranchDict(neuron)
    branch_list=_util.select_branch(model.clusteredparent)
 
    ############# Identify a cluster of synapses for stimulation ########################
    ### updated to make specified number of inputs per branch/compartment
    ### update to ensure each set of inputs has unique parent branch?
    if num_clustered > 0:
        if model.SpineParams.spineParent != 'soma': #clustered BLA is distributed, 2 per comp on multile branches
            possibleBranches, branch_len = stim.getBranchesOfOrder(neuron, -1, n=1,  #select one terminal branch; n='all' will select multiple terminal on specified primary; None will include all order branches, 3 will use only tertiary 
                                          commonParentOrder=1, commonParentBranch=branch_list[0]) #, min_length = 120e-6#select with parent=specified primary, with 120 um length - but not for exampleClustered
        if 'DMS' in filename:
            print('simulating ',num_clustered,' BLA inputs to DMS') #
            if model.SpineParams.spineParent == 'soma': #inputs dispersed over entire tree
                inputs=stim.n_inputs_per_comp(model, nInputs = num_clustered,spine_per_comp=2,seed=clustered_seed, minDistance=40e-6, maxDistance=60e-6) #FIXME. spine_per_comp should be 3 for DMS only if num_clustered=24
            else:
                tries=0
                success=0
                while tries<8 and success==0: #if elist is not big enough, try a few more times
                    elist = stim.generateElementList(neuron, wildcardStrings=['ampa,nmda'], elementType='SynChan',
                                            minDistance=40e-6, maxDistance=70e-6, commonParentOrder=0,
                                            numBranches=1, min_length=10e-6, branch_list=possibleBranches
                                            ) #could try minDistance=120e-6'''
                    tries+=1
                    if len(elist)>=num_clustered:
                        success=1
                    else:
                        print('only', len(elist), 'possible inputs on try', tries)
                inputs = stim.selectRandom(elist,n=num_clustered,func='elist_DMS')
        elif 'DLS' in filename:
            print('simulating',num_clustered,'  BLA inputs to DLS')
            if model.SpineParams.spineParent == 'soma': #inputs dispersed over entire tree
                inputs=stim.n_inputs_per_comp(model, nInputs = num_clustered,spine_per_comp=2,seed=clustered_seed, minDistance=100e-6, maxDistance=120e-6)
            else:
                tries=0
                success=0
                while tries<8 and success==0: #if elist is not big enough, try a few more times
                    elist = stim.generateElementList(neuron, wildcardStrings=['ampa,nmda'], elementType='SynChan',
                                            minDistance=100e-6, maxDistance=150e-6, commonParentOrder=0,
                                            numBranches=1, min_length=10e-6, branch_list=possibleBranches
                                            ) #could try minDistance=120e-6'''
                    tries+=1
                    if len(elist)>=num_clustered:
                        success=1
                    else:
                        print('only', len(elist), 'possible inputs on try', tries)
                inputs = stim.selectRandom(elist,n=num_clustered,func='elist_DLS')
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
        print('clustered stim for seed', clustered_seed,'=')#,inputs) #if want to exclude these branches from dispersed input, need to put into branch_list
        stim.report_element_distance(inputs)
        cluster_comps=list(np.unique([pd.path for pd in parent_dend]))
        branch_list=[c for c in cluster_comps if c in bd.keys()] #new branch_list based on clustered inputs
    
    #new branch list - one of the clustered inputs
    if len(branch_list)==0:
        for path in cluster_comps:
            bl=[br for br in bd.keys() if path in bd[br]['CompList']]
            branch_list.append(bl[0])
    branch_list=list(np.unique(branch_list))
    comps = [moose.element(comp) for comp in bd[branch_list[0]]["BranchPath"]] #plot compartments for 1st branch
    spines = [sp[0] for comp in comps for sp in comp.children if "head" in sp.name] #
    model.param_sim.plotcomps = [s.split("/")[-1] for s in bd[branch_list[0]]["BranchPath"]] #add in parent_dend for plotting

    # mod_local_gbar(set(comps+spines), mod_dict[modelname])
    # from IPython import embed; embed()

    # import pdb;pdb.set_trace()
     ############## Identify set of synaptic inputs, one set dispersed, the other a cluster ###################
    if num_clustered > 0 and model.param_sim.plot_current:
        plotgates = ["CaR", "CaT32", "CaT33", "CaL12", "CaL13"]
        plotchan=plotgates+["SKCa", "ampa", "nmda"]
        msg='getIk'
        spine_cur_tab=plot_channel.plot_gates(model,plotgates,plotchan,inputs,msg)

    ############# Identify a set of synapses for dispersed stimulation ########################
    #dispersed inputs go to all branches except those stimulated (if specified in branch_list). 
    if num_dispersed>0:
        if model.SpineParams.spineParent=='soma': #i.e., if dispersing inputs everywhere
            print(filename,'has excluded branches:', branch_list, 'dispersed',n_per_dispersed, freq_dispersed) 
            dispersed_inputs = stim.dispersed(model,nInputs=num_dispersed,
                exclude_branch_list=branch_list, seed=dispersed_seed) #using seed - always same.  excludes branches with clustered inputs
        else:
            possibleBranches, _ = stim.getBranchesOfOrder(neuron, None, n='all', min_path_length=min_disp, max_path_length=max_disp, #select multiple branches on specified primary 
                                          commonParentOrder=1, commonParentBranch=branch_list[0]) #select with parent=specified primary, with 120 um length
            print(filename,'dispersing inputs on:', possibleBranches, 'dispersed',n_per_dispersed, freq_dispersed)
            dispersed_inputs = stim.dispersed(model,nInputs=num_dispersed,
                branch_list=possibleBranches,seed=dispersed_seed, minDistance=min_disp, maxDistance=max_disp) #using seed - always same; min_disp and max_disp needed here, too
        stim.report_element_distance(dispersed_inputs)
        disp_comps=list(np.unique([i.parent.parent.path for i in dispersed_inputs]))
    print('dispersed stim=',num_dispersed)

    create_model_sim.setupOutput(model)
    ############## create time table inputs, either specific frequency or from external spike trains ###################
    if num_clustered > 0:
        model.param_sim.plotcomps +=[s.split("/")[-1] for s in cluster_comps]
        input_times = stim.createTimeTables(
            inputs, model, n_per_syn=n_per_clustered, start_time=start_cluster,end_time=end_cluster)#, freq=80) #FIXME.  make syn_per_comp parameter, divide by n_per_cluster?
        #n_per_syn is how many times each synapse in the cluster receives an input, default freq for all synapses =500 Hz
    if num_dispersed>0:
        model.param_sim.plotcomps += [s.split("/")[-1] for s in disp_comps]
        inputs_disp = stim.createTimeTables(dispersed_inputs, model, n_per_syn=n_per_dispersed, start_time=start_dispersed,  #n_per_syn is unused if using time tables
            freq=freq_dispersed, end_time=end_dispersed, input_spikes=time_tables)
        print('dispersed inputs:', time_tables, 'num stimuli=', len(inputs_disp), '\n   begin=', inputs_disp[0:5], '\n   end=', inputs_disp[-5:])
    else:
        end_dispersed=round(input_times[-1],3) #use time of last clustered stim for filename if no dispersed
    model.param_sim.fname=model.param_sim.fname+'_'+str(num_dispersed)+'_'+str(num_clustered)
    # c.Rm = c.Rm*100
    if injection_current is not None:
        model.param_sim.injection_current = [injection_current]
        model.param_sim.injection_delay = 0.3
        model.param_sim.injection_width = 0.1
        create_model_sim.setupStim(model)
        #print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        model.pg.firstLevel = injection_current
        
        #from IPython import embed; embed()
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

        spine_graph.spineFig(model,model.param_sim.simtime,model.spinevmtab)

        #create_model_sim.neuron_graph.dist_vs_diam(model,modelname,model.param_sim.fname,num_dispersed)

        if num_clustered > 0 and model.param_sim.plot_current:
            plt.figure()
            plt.suptitle(modelname+' '+model.param_sim.fname)
            for cur in spine_cur_tab:
                t=np.linspace(0,model.param_sim.simtime,len(cur),endpoint=False)
                plt.plot(t,cur.vector, label=cur.name.strip("_"))

            plt.legend()
            plt.ylabel(msg)
            plt.xlabel('Time (sec)')
            # create_model_sim.plot_channel.plot_gate_params(moose.element('/library/CaT32'),3)
            ######## Test this, may be redundanat with plot_channel #########
            # for c,d in model.gatetables.items():
            #     plt.figure()
            #     plt.title(c)
            #     for g,t in d.items():
            #         plt.plot(t.vector,label=g)
            #     plt.legend()

            plt.show(block=True)
    if block_naf:
        model.param_sim.fname='_'.join([model.param_sim.fname,str(end_dispersed),str(mod_dict[modelname]['NMDA']),str(round(max_disp*1e6)),str(dispersed_seed)])
    else:
        model.param_sim.fname='_'.join([model.param_sim.fname,str(end_dispersed),str(mod_dict[modelname]['NMDA']),str(round(max_disp*1e6)),'NaF',str(dispersed_seed)])
    # c = moose.element('D1/634_3')
    tables.write_textfiles(model, 0, ca=False, spines=False, spineca=False)
    print("upstate filename: {}".format(model.param_sim.fname))

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
    elif sim_type=='BLA_DMS_dispersed':
        sims = [
            {
                "name": "BLA_DMS",
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": params.num_dispersed, 
                    "num_clustered": params.num_clustered,
                    "freq_dispersed": 250,
                    "dispersed_seed": dispersed_seed,
                    "clustered_seed": clustered_seed,
                    "n_per_clustered": params.n_per_clustered,
                   "block_naf": params.block_naf,
                 },
            } ]
    elif sim_type=='BLA_DLS_dispersed':
        sims = [
            {
                "name": "BLA_DLS",
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": params.num_dispersed, 
                    "num_clustered": params.num_clustered,
                    "freq_dispersed":250,
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
        sim['kwds']['min_disp']=params.min_disp
        sim['kwds']['max_disp']=params.max_disp
        sim['kwds']["start_dispersed"]=params.start_dispersed
        sim['kwds']["end_dispersed"]=params.end_dispersed
        sim['kwds']["start_cluster"]=params.start_cluster
        sim['kwds']["end_cluster"]=params.end_cluster
     
    return sims
    
def parsarg(commandline):
    import argparse
    small_parser=argparse.ArgumentParser()
    small_parser.add_argument('base_sim', type=str, default='mpi_main', help='single, iv, mp, or mpi_main')
    small_parser.add_argument('-sim_type', type=str, default='rheobase_only', help='one of the choices from specify_sims')
    small_parser.add_argument('-spkfile',type=str,default='networks/FullTrialMediumVariabilitySimilarTrialsTruncatedNormal', help='spike train file')
    small_parser.add_argument('-SPN', type=str, default="D1MatrixSample2", help='neuron module')
    small_parser.add_argument('-seed', type=int, help='dispersed spine seed')
    small_parser.add_argument('-start_cluster', type=float, default=0.3, help='time to start clustered, BLA stim, in sec')
    small_parser.add_argument('-end_cluster', type=float, help='time to end clustered, BLA stim, in sec')
    small_parser.add_argument('-num_dispersed', type=int, default=75, help='number of dispersed inputs')
    small_parser.add_argument('-num_clustered', type=int, default=16, help='number of BLA inputs')
    small_parser.add_argument('-start_dispersed', type=float, default=0.1, help='time to start dispersed stim')
    small_parser.add_argument('-end_dispersed', type=float, default=0.6, help='time to end dispersed stim')
    small_parser.add_argument('-block_naf', type=bool, default=False)
    small_parser.add_argument('-min_disp', type=float, default=20e-6, help='minimum distance for dispersed inputs')
    small_parser.add_argument('-max_disp', type=float, default=300e-6, help='maximum distance for dispersed inputs')
    small_parser.add_argument('-n_per_clustered', type=int, default=2, help='number of stim per clustered synapse')

    args=small_parser.parse_args(commandline)
    return args

if __name__ == "__main__":
    mod_dict = make_mod_dict()
    clustered_seed = 135
    dispersed_seed = 172
    single_epsp_seed = 314
    #sim_type='rheobase_only' #'new_dispersed_300ms_only'#  or 'upstate_only'?

    import sys

    #args = sys.argv[1:]
    args='single -sim_type BLA_DMS_dispersed -num_clustered 0 -num_dispersed 20'.split() #for debugging
    params=parsarg(args)
    sims=specify_sims(params.sim_type,clustered_seed,dispersed_seed,single_epsp_seed,params)
 
    if params.base_sim == "single":
        if params.spkfile:
            tt_Ctx_SPN={'fname':params.spkfile,'syn_per_tt':2}
            spn_name=params.SPN.split('.')[-1][0:5]+params.SPN.split('.')[-1][-1]
            model=upstate_main(params.SPN, mod_dict, **sims[0]['kwds'],do_plots=True,filename=spn_name+sims[0]['name'], time_tables=tt_Ctx_SPN)
            print(sims[0])
        else:
            # upstate_main(list(mod_dict.keys())[0],mod_dict)
            upstate_main("D1PatchSample5", mod_dict, do_plots=True)

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

