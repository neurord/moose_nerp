# -*- coding:utf-8 -*-
from __future__ import print_function, division
def moose_main(corticalinput):
    import logging

    import numpy as np
    import matplotlib.pyplot as plt
    #plt.ion()

    from pprint import pprint
    import moose

    from moose_nerp.prototypes import (create_model_sim,
                                    cell_proto,
                                    clocks,
                                    inject_func,
                                    create_network,
                                    tables,
                                    net_output,
                                    logutil,
                                    util,
                                    standard_options)
    from moose_nerp import d1opt as model
    from moose_nerp import str_net as net
    from moose_nerp.graph import net_graph, neuron_graph, spine_graph

    #additional, optional parameter overrides specified from with python terminal
    #model.Condset.D1.NaF[model.param_cond.prox] /= 3
    #model.Condset.D1.KaS[model.param_cond.prox] *= 3

    net.connect_dict['D1']['ampa']['extern1'].dend_loc.postsyn_fraction = 0.8
    net.param_net.tt_Ctx_SPN.filename = corticalinput
    print('cortical_fraction = {}'.format(net.connect_dict['D1']['ampa']['extern1'].dend_loc.postsyn_fraction))
    model.synYN = True
    model.plasYN = True
    model.calYN = True
    model.spineYN = True
    net.single=True
    create_model_sim.setupOptions(model)
    param_sim = model.param_sim
    param_sim.useStreamer = True
    param_sim.plotdt = .1e-3
    param_sim.stim_loc = model.NAME_SOMA
    param_sim.stim_paradigm = 'inject'
    param_sim.injection_current = [0] #[-0.2e-9, 0.26e-9]
    param_sim.injection_delay = 0.2
    param_sim.injection_width = 0.4
    param_sim.simtime = 21
    net.num_inject = 0
    net.confile = 'str_connect_plas_simd1opt_{}_corticalfraction_{}'.format(net.param_net.tt_Ctx_SPN.filename,0.8)

    if net.num_inject==0:
        param_sim.injection_current=[0]
    #################################-----------create the model: neurons, and synaptic inputs
    model=create_model_sim.setupNeurons(model,network=not net.single)
    all_neur_types=model.neurons
    #FSIsyn,neuron = cell_proto.neuronclasses(FSI)
    #all_neur_types.update(neuron)
    population,connections,plas=create_network.create_network(model, net, all_neur_types)

    ###### Set up stimulation - could be current injection or plasticity protocol
    # set num_inject=0 to avoid current injection
    if net.num_inject<np.inf :
        inject_pop=inject_func.inject_pop(population['pop'],net.num_inject)
    else:
        inject_pop=population['pop']
    #Does setupStim work for network?
    #create_model_sim.setupStim(model)
    pg=inject_func.setupinj(model, param_sim.injection_delay,param_sim.injection_width,inject_pop)
    moose.showmsg(pg)

    ##############--------------output elements
    if net.single:
        #fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]+'.npz'
        #simpath used to set-up simulation dt and hsolver
        simpath=['/'+neurotype for neurotype in all_neur_types]
        create_model_sim.setupOutput(model)
    else:   #population of neurons
        spiketab,vmtab,plastab,catab=net_output.SpikeTables(model, population['pop'], net.plot_netvm, plas, net.plots_per_neur)
        #simpath used to set-up simulation dt and hsolver
        simpath=[net.netname]
        clocks.assign_clocks(simpath, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)
    if model.synYN and (param_sim.plot_synapse or net.single):
        #overwrite plastab above, since it is empty
        syntab, plastab, stp_tab=tables.syn_plastabs(connections,model)
        nonstim_plastab = tables.nonstimplastabs(plas)


    # Streamer to prevent Tables filling up memory on disk
    # This is a hack, should be better implemented
    if param_sim.useStreamer==True:
        allTables = moose.wildcardFind('/##[ISA=Table]')
        streamer = moose.Streamer('/streamer')
        streamer.outfile = 'plas_simd1opt_{}_corticalfraction_{}.npy'.format(net.param_net.tt_Ctx_SPN.filename,0.8)
        moose.setClock(streamer.tick,0.1)
        for t in allTables:
            if any (s in t.path for s in ['plas','VmD1_0','extern','Shell_0']):
                streamer.addTable(t)
            else:
                t.tick=-2

    
    ################### Actually run the simulation
    def run_simulation(injection_current, simtime):
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        pg.firstLevel = injection_current
        moose.reinit()
        moose.start(simtime,True)

    traces, names = [], []
    for inj in param_sim.injection_current:
        run_simulation(injection_current=inj, simtime=param_sim.simtime)
    
    weights = [w.value for w in moose.wildcardFind('/##/plas##[TYPE=Function]')]
    plt.figure()
    plt.hist(weights,bins=100)
    plt.title('plas_sim_{}_corticalfraction_{}'.format(net.param_net.tt_Ctx_SPN.filename,cortical_fraction))
    plt.savefig('plas_simd1opt_{}_corticalfraction_{}.png'.format(net.param_net.tt_Ctx_SPN.filename,0.8))
    if param_sim.useStreamer==True:
        import atexit
        atexit.register(moose.quit)
    return weights

def multi_main():
    from multiprocessing.pool import Pool
    p = Pool(4,maxtasksperchild=1)
    # Apply main simulation varying cortical fractions:
    cfs = ['FullTrialLowVariability', 'FullTrialHighVariability','FullTrialHigherVariability']
    results = p.map(moose_main,cfs)
    return dict(zip(cfs,results))

if __name__ == "__main__":
    print('runningmain')
    results = multi_main()
