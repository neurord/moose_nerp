# -*- coding:utf-8 -*-
from __future__ import print_function, division


def moose_main(corticalinput,LTP_amp_thresh_mod=1.158, LTD_amp_thresh_mod=1.656, LTP_dur_thresh_mod=1.653, LTD_dur_thresh_mod=0.867,LTP_gain_mod=0.704, LTD_gain_mod=1.671,nmda_mod=1):
    import logging

    import numpy as np
    np.random.seed(42)
    import os

    from pprint import pprint
    import moose

    from moose_nerp.prototypes import (
        create_model_sim,
        cell_proto,
        clocks,
        inject_func,
        create_network,
        tables,
        net_output,
        logutil,
        util,
        standard_options,
    )
    #from moose_nerp import d1opt as model
    #from moose_nerp import D1MatrixSample2 as model
    from moose_nerp import D1PatchSample5 as model
    from moose_nerp import str_net as net
    from moose_nerp.graph import net_graph, neuron_graph, spine_graph

    # additional, optional parameter overrides specified from with python terminal
    # model.Condset.D1.NaF[model.param_cond.prox] /= 3
    # model.Condset.D1.KaS[model.param_cond.prox] *= 3

    model.param_syn._SynAMPA.Gbar = .25e-9
    model.param_syn._SynNMDA.Gbar = .25e-9
    model.param_syn._SynGaba.Gbar = 1e-9

    net.connect_dict["D1"]["ampa"]["extern1"].dend_loc.postsyn_fraction = 0.8
    net.param_net.tt_Ctx_SPN.filename = corticalinput
    print(
        "cortical_fraction = {}".format(
            net.connect_dict["D1"]["ampa"]["extern1"].dend_loc.postsyn_fraction
        )
    )
    model.synYN = True
    model.plasYN = True
    model.calYN = True
    model.spineYN = True

    # vary plasticity params
    model.CaPlasticityParams.Plas2_syn.LTP_amp_thresh*=LTP_amp_thresh_mod
    model.CaPlasticityParams.Plas2_syn.LTD_amp_thresh*=LTD_amp_thresh_mod
    model.CaPlasticityParams.Plas2_syn.LTP_dur_thresh*=LTP_dur_thresh_mod
    model.CaPlasticityParams.Plas2_syn.LTD_dur_thresh*=LTD_dur_thresh_mod
    model.CaPlasticityParams.Plas2_syn.LTP_gain*=LTP_gain_mod
    model.CaPlasticityParams.Plas2_syn.LTD_gain*=LTD_gain_mod
    
    # new changes: Universal function to modify variables. Needs to extract any attribute based (e.g. model.CaParams...) or dict/list based (e.g. model.dict['key']) parameter name as a string, parse the variable, and apply the modification. Additionally, need to specify a multiplicative change, additive change, or direct replacement.
    #model.CaPlasticityParams.BufferCapacityDensity*=buffer_capacity_density_gain_mod
    
    #


    net.single = True
    model.ConcOut = model.param_cond.ConcOut = 1.2
    create_model_sim.setupOptions(model)
    param_sim = model.param_sim
    param_sim.useStreamer = True
    param_sim.plotdt = 0.1e-3
    param_sim.stim_loc = model.NAME_SOMA
    param_sim.stim_paradigm = "inject"
    param_sim.injection_current = [0]  # [-0.2e-9, 0.26e-9]
    param_sim.injection_delay = 0.2
    param_sim.injection_width = 0.4
    param_sim.simtime = 21.5#3.5  # 21
    net.num_inject = 0
    model.name = model.__name__.split('.')[-1]
    net.confile = "str_connect_plas_sim{}_{}_corticalfraction_{}".format(
        model.name, os.path.basename(net.param_net.tt_Ctx_SPN.filename), 0.8
    )

    if net.num_inject == 0:
        param_sim.injection_current = [0]
    #################################-----------create the model: neurons, and synaptic inputs
    model = create_model_sim.setupNeurons(model, network=not net.single)
    all_neur_types = model.neurons
    # FSIsyn,neuron = cell_proto.neuronclasses(FSI)
    # all_neur_types.update(neuron)
    population, [connections,conn_summary], plas = create_network.create_network(
        model, net, all_neur_types)

    ###### Set up stimulation - could be current injection or plasticity protocol
    # set num_inject=0 to avoid current injection
    if net.num_inject < np.inf:
        inject_pop = inject_func.inject_pop(population["pop"], net.num_inject)
    else:
        inject_pop = population["pop"]
    # Does setupStim work for network?
    # create_model_sim.setupStim(model)
    pg = inject_func.setupinj(
        model, param_sim.injection_delay, param_sim.injection_width, inject_pop
    )
    moose.showmsg(pg)

    ##############--------------output elements
    if net.single:
        # fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]+'.npz'
        # simpath used to set-up simulation dt and hsolver
        simpath = ["/" + neurotype for neurotype in all_neur_types]
        create_model_sim.setupOutput(model)
    else:  # population of neurons
        spiketab, vmtab, plastab, catab = net_output.SpikeTables(
            model, population["pop"], net.plot_netvm, plas, net.plots_per_neur
        )
        # simpath used to set-up simulation dt and hsolver
        simpath = [net.netname]
        clocks.assign_clocks(
            simpath,
            param_sim.simdt,
            param_sim.plotdt,
            param_sim.hsolve,
            model.param_cond.NAME_SOMA,
        )
    if model.synYN and (param_sim.plot_synapse or net.single):
        # overwrite plastab above, since it is empty
        syntab, plastab, stp_tab = tables.syn_plastabs(connections, model)
        nonstim_plastab = tables.nonstimplastabs(plas)

    # Streamer to prevent Tables filling up memory on disk
    # This is a hack, should be better implemented
    if param_sim.useStreamer == True:
        allTables = moose.wildcardFind("/##[ISA=Table]")
        streamer = moose.Streamer("/streamer")
        streamer.outfile = "plas_sim{}_{}_corticalfraction_{}_LTP_amp_thresh_mod_{}_LTD_amp_thresh_mod_{}_LTP_dur_thresh_mod_{}_LTD_dur_thresh_mod_{}_LTP_gain_mod_{}_LTD_gain_mod_{}.npy".format(model.name,
            os.path.basename(net.param_net.tt_Ctx_SPN.filename), 0.8, LTP_amp_thresh_mod, LTD_amp_thresh_mod, LTP_dur_thresh_mod, LTD_dur_thresh_mod, LTP_gain_mod, LTD_gain_mod,
        )
        moose.setClock(streamer.tick, 0.1)
        for t in allTables:
            if any(s in t.path for s in ["plas", "VmD1_0", "extern", "Shell_0"]):
                streamer.addTable(t)
            else:
                t.tick = -2

    spinedistdict = {}
    for sp in moose.wildcardFind('D1/##/#head#[ISA=CompartmentBase]'):
        dist,_ = util.get_dist_name(sp)
        path = sp.path
        spinedistdict[path]=dist
    np.save(os.path.basename(net.param_net.tt_Ctx_SPN.filename)+'_spine_dist_dict.npy',spinedistdict)

    ################### Actually run the simulation
    def run_simulation(injection_current, simtime):
        print(u"◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤".format(injection_current))
        pg.firstLevel = injection_current
        moose.reinit()
        moose.start(simtime, True)

    traces, names = [], []
    for inj in param_sim.injection_current:
        run_simulation(injection_current=inj, simtime=param_sim.simtime)

    weights = [w.value for w in moose.wildcardFind("/##/plas##[TYPE=Function]")]
    if param_sim.useStreamer == True:
        import atexit
        atexit.register(moose.quit)
    return weights


def multi_main():
    from multiprocessing.pool import Pool

    p = Pool(4, maxtasksperchild=1)
    # Apply main simulation varying cortical fractions:
    # cfs = ['FullTrialLowVariability', 'FullTrialHighVariability','FullTrialHigherVariability']
    #remove str_net/ from filenames if running from within str_net directory
    cfs = [
        "str_net/FullTrialLowVariabilitySimilarTrialsTruncatedNormal",
        "str_net/FullTrialMediumVariabilitySimilarTrialsTruncatedNormal",
        "str_net/FullTrialHighVariabilitySimilarTrialsTruncatedNormal",
        "str_net/FullTrialHigherVariabilitySimilarTrialsTruncatedNormal",
    ]
    results = p.map(moose_main, cfs)
    return dict(zip(cfs, results))

def multi_plas_rule_main():
    from multiprocessing.pool import Pool

    p = Pool(16, maxtasksperchild=1)
    # Apply main simulation varying cortical fractions:
    # cfs = ['FullTrialLowVariability', 'FullTrialHighVariability','FullTrialHigherVariability']
    #remove str_net/ from filenames if running from within str_net directory
    cfs = [
        "str_net/FullTrialLowVariabilitySimilarTrialsTruncatedNormal",
        "str_net/FullTrialMediumVariabilitySimilarTrialsTruncatedNormal",
        "str_net/FullTrialHighVariabilitySimilarTrialsTruncatedNormal",
        "str_net/FullTrialHigherVariabilitySimilarTrialsTruncatedNormal",
    ]

    plas_mod_values = [.5,2]
    plas_mod_keys = ['LTP_amp_thresh_mod', 'LTD_amp_thresh_mod','LTP_dur_thresh_mod', 'LTD_dur_thresh_mod','LTP_gain_mod', 'LTD_gain_mod']
    simlist = []
    from itertools import product
    simlist = list(product(cfs,*[plas_mod_values]*6))

    results = p.starmap(moose_main, simlist)
    return dict(zip(simlist, results))

def multi_main_moved_spikes():
    from multiprocessing.pool import Pool

    p = Pool(11, maxtasksperchild=1)
    # Apply main simulation varying cortical fractions:
    # cfs = ['FullTrialLowVariability', 'FullTrialHighVariability','FullTrialHigherVariability']
    cfs = [
        "MovedSpikesToOtherTrains_Prob_10_Percent",
        "MovedSpikesToOtherTrains_Prob_20_Percent",
        "MovedSpikesToOtherTrains_Prob_30_Percent",
        "MovedSpikesToOtherTrains_Prob_40_Percent",
        "MovedSpikesToOtherTrains_Prob_50_Percent",
        "MovedSpikesToOtherTrains_Prob_60_Percent",
        "MovedSpikesToOtherTrains_Prob_70_Percent",
        "MovedSpikesToOtherTrains_Prob_80_Percent",
        "MovedSpikesToOtherTrains_Prob_90_Percent",
        "MovedSpikesToOtherTrains_Prob_100_Percent",
    ]
    results = p.map(moose_main, cfs)
    return dict(zip(cfs, results))



if __name__ == "__main__":
    print("running main")
    results = multi_main()
    #results = multi_main_moved_spikes()
    #######################  one plot of ending synaptic weights for each simulation ###################
    import os
    import matplotlib.pyplot as plt
    for key, weights in results.items():
        plt.figure()
        plt.hist(weights, bins=100)
        if isinstance(key,str):
            title=os.path.basename(key)
        elif isinstance(k,tuple):
            title=os.path.basename(key[0])+'_'.join([str(s) for s in key[1:]])
        else:
            print('new type of multi-sim, unsure how to construct figure filename')
            title=''
        plt.title("plas_sim_{}".format(title))
        plt.savefig("plas_sim_{}.png".format(title))
