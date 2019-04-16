# -*- coding:utf-8 -*-

######## ep_net/multisim.py ############

from __future__ import print_function, division

def moose_main(p):
    stimfreq,presyn,stpYN,trialnum=p

    import numpy as np
    import moose

    from moose_nerp.prototypes import (create_model_sim,
                                       clocks,
                                       inject_func,
                                       create_network,
                                       tables,
                                       net_output,
                                       util)
    from moose_nerp import ep as model
    from moose_nerp import ep_net as net
    from moose_nerp.graph import net_graph, neuron_graph, spine_graph


    #additional, optional parameter overrides specified from with python terminal
    model.synYN = True
    model.stpYN = stpYN
    net.single=True
    model.param_sim.stim_paradigm='PSP_'+str(stimfreq)+'Hz'

    create_model_sim.setupOptions(model)
    param_sim = model.param_sim
    param_sim.injection_current = [0e-12]
    param_sim.injection_delay = 0.0
    param_sim.plot_synapse=False

    #################################-----------create the model: neurons, and synaptic inputs
    model=create_model_sim.setupNeurons(model,network=not net.single)
    population,connections,plas=create_network.create_network(model, net, model.neurons)

    ####### Set up stimulation - could be current injection or plasticity protocol
    # set num_inject=0 to avoid current injection
    if net.num_inject<np.inf :
        model.inject_pop=inject_func.inject_pop(population['pop'],net.num_inject)
    else:
        model.inject_pop=population['pop']
        if net.num_inject==0:
            param_sim.injection_current=[0]

    ############## Set-up test of synaptic plasticity at single synapse ####################
    if presyn=='str':
        stp_params=net.param_net.str_plas
    elif presyn=='GPe':
        stp_params=net.param_net.GPe_plas
    else:
        print('########### unknown synapse type')

    param_sim.fname='epnet_syn'+presyn+'_freq'+str(stimfreq)+'_plas'+str(1 if model.stpYN else 0)+'_inj'+str(param_sim.injection_current[0])+'t'+str(trialnum)
    print('>>>>>>>>>> moose_main, presyn {} stpYN {} stimfreq {} trial {}'.format(stimfreq,presyn,model.stpYN,trialnum))

    create_model_sim.setupStim(model)

    ##############--------------output elements
    if net.single:
        #fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]+'.npz'
        create_model_sim.setupOutput(model)
    else:   #population of neurons
        spiketab,vmtab,plastab,catab=net_output.SpikeTables(model, population['pop'], net.plot_netvm, plas, net.plots_per_neur)
        #simpath used to set-up simulation dt and hsolver
        simpath=[net.netname]
        clocks.assign_clocks(simpath, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)
        # Fix calculation of B parameter in CaConc if using hsolve
        if model.param_sim.hsolve and model.calYN:
            calcium.fix_calcium(util.neurontypes(model.param_cond), model)

    if model.synYN and (param_sim.plot_synapse or net.single):
        #overwrite plastab above, since it is empty
        syntab, plastab, stp_tab=tables.syn_plastabs(connections,model)

    from moose_nerp.prototypes import plasticity_test as plas_test
    extra_syntab={ntype:[] for ntype in  model.neurons.keys()}
    extra_plastabset={ntype:[] for ntype in  model.neurons.keys()}
    param_dict={'syn':presyn,'freq':stimfreq,'plas':model.stpYN,'inj':param_sim.injection_current,'simtime':param_sim.simtime, 'trial': trialnum}
    for ntype in model.neurons.keys():
        for tt_syn_tuple in model.tuples[ntype].values():
            if model.stpYN:
                extra_syntab[ntype],extra_plastabset[ntype]=plas_test.short_term_plasticity_test(tt_syn_tuple,syn_delay=0,
                                                                        simdt=model.param_sim.simdt,stp_params=stp_params)
            else:
                extra_syntab[ntype]=plas_test.short_term_plasticity_test(tt_syn_tuple,syn_delay=0)
        param_dict[ntype]={'syn_tt': [(k,tt[0].vector) for k,tt in model.tuples[ntype].items()]}

    #################### Actually run the simulation
    create_model_sim.runOneSim(model)
    #net_output.writeOutput(model, param_sim.fname+'vm',spiketab,vmtab,population)

    import ISI_anal
    #stim_spikes are spikes that occur during stimulation - they prevent correct psp_amp calculation
    spike_time,isis=ISI_anal.spike_isi_from_vm(model.vmtab,param_sim.simtime)
    stim_spikes=ISI_anal.stim_spikes(spike_time,model.tt)
    if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
        np.savez(param_sim.fname,spike_time=spike_time,isi=isis,params=param_dict)
    else:
        print('no spikes for',param_sim.fname)
    #create dictionary with the output (vectors) from tables 
    tab_dict={}
    for ntype,tabset in extra_syntab.items():
        tab_dict[ntype]={'syn':tabset.vector,'syndt':tabset.dt, 
        'tt': {ntype+'_'+pt:tab.vector for pt,tab in model.tt[ntype].items()}}#,'tt_dt':tabset.dt}
        if model.stpYN:
            tab_dict[ntype]['plas']={tab.name:tab.vector for tab in extra_plastabset[ntype]}
    vmtab={ntype:[tab.vector for tab in tabset] for ntype,tabset in model.vmtab.items()}
    return param_dict,tab_dict,vmtab,spike_time,isis

def multi_main(syntype,stpYN,stimfreqs,num_trials):
    from multiprocessing.pool import Pool
    p = Pool(12,maxtasksperchild=1)
    # Apply main simulation varying cortical fractions:
    all_results={}
    #for trial in range(num_trials):
    #    params=[(freq,syntype,stpYN,trial) for freq in stimfreqs]
    for freq in stimfreqs:
        params=[(freq,syntype,stpYN,trial) for trial in range(num_trials)]
        results = p.map(moose_main,params)
        all_results[freq]=dict(zip(range(num_trials),results))
    #all_results.append(dict(zip(stimfreqs,results)))
    return all_results

if __name__ == "__main__":
    print('running main')
    syn='str'
    stpYN=1
    num_trials=10
    stimfreqs=[20]
    all_results = multi_main(syn,stpYN,stimfreqs,num_trials)


'''
ToDo:
a. possibly "reserve" the synapse from random time tables 
   e.g. call create_model_sim.setupStim(model) after creating pop but before connecting time_tables
b. repeat stp effect with dopamine blocked conditions
'''

'''
for neurtype,neurtype_dict in connections.items():
    for neur,neur_dict in neurtype_dict.items():
        for syn,syn_dict in neur_dict.items():
            for pretype,pre_dict in syn_dict.items():
                for branch,presyn in pre_dict.items():
                    if 'TimTab' not in presyn:
                        preflag='** Intrinsic **'
                    else:
                        preflag='ext'
                    print(preflag,neurtype,neur,syn,pretype,branch,presyn)

import numpy as np
data=np.load('gp_connect.npz')
conns=data['conn'].item()
for neurtype,neurdict in conns.items():
  for cell in neurdict.keys():
     for pre,post in neurdict[cell]['gaba'].items():
        print(cell,pre,post)
'''
