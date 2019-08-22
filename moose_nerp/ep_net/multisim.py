# -*- coding:utf-8 -*-

######## ep_net/multisim.py ############

from __future__ import print_function, division

def moose_main(p):
    stimfreq,presyn,stpYN,trialnum,prefix,ttGPe,ttstr=p

    import numpy as np
    import os
    import moose

    from moose_nerp.prototypes import (calcium,
                                       create_model_sim,
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
    stimtype='PSP_'
    outdir="ep_net/output/"
    if stimfreq>0:
        model.param_sim.stim_paradigm=stimtype+str(stimfreq)+'Hz'
        model.param_stim.Stimulation.StimLoc=model.param_stim.location[presyn]
    else:
        model.param_sim.stim_paradigm='inject'
    create_model_sim.setupOptions(model)
    param_sim = model.param_sim
    param_sim.injection_current = [0e-12]
    param_sim.injection_delay = 0.0
    param_sim.plot_synapse=False
       
    if prefix.startswith('POST-HFS'):
        net.connect_dict['ep']['ampa']['extern1'].weight=0.6 #STN - weaker
        net.connect_dict['ep']['gaba']['extern2'].weight=0.8 #GPe - weaker
        net.connect_dict['ep']['gaba']['extern3'].weight=1.4 #str - stronger
    if prefix.startswith('POST-NoDa'):
        net.connect_dict['ep']['ampa']['extern1'].weight=1.0 #STN - no change
        net.connect_dict['ep']['gaba']['extern2'].weight=2.8 #GPe - stronger
        net.connect_dict['ep']['gaba']['extern3'].weight=1.0 #str - no change

    #override time tables here - before creating model, e.g.
    fname_part=''
    if ttGPe is not None:
        net.param_net.tt_GPe.filename=ttGPe
        print ('!!!!!!! new tt file for GPe:',net.param_net.tt_GPe.filename)
        fname_part=fname_part+'_tg_'+os.path.basename(ttGPe)
    if ttstr is not None:
        net.param_net.tt_str.filename=ttstr
        print ('!!!!!!! new tt file for str:',net.param_net.tt_str.filename)
        fname_part=fname_part+'_ts_'+os.path.basename(ttstr)
    #################################-----------create the model: neurons, and synaptic inputs
    
    model=create_model_sim.setupNeurons(model,network=not net.single)
    population,connections,plas=create_network.create_network(model, net, model.neurons)

    ####### Set up stimulation - could be current injection or plasticity protocol
    # set num_inject=0 to avoid current injection
    if net.num_inject<np.inf :
        model.inject_pop=inject_func.inject_pop(population['pop'],net.num_inject)
        if net.num_inject==0:
            param_sim.injection_current=[0]
    else:
        model.inject_pop=population['pop']

    ############## Set-up test of synaptic plasticity at single synapse ####################
    if presyn=='str':
        stp_params=net.param_net.str_plas
    elif presyn=='GPe':
        stp_params=net.param_net.GPe_plas
    else:
        print('########### unknown synapse type')

    param_sim.fname='ep'+prefix+'_syn'+presyn+'_freq'+str(stimfreq)+'_plas'+str(1 if model.stpYN else 0)+fname_part+'t'+str(trialnum)
    print('>>>>>>>>>> moose_main, presyn {} stpYN {} stimfreq {} simtime {} trial {} plotcomps {} tt {} {}'.format(presyn,model.stpYN,stimfreq, param_sim.simtime,trialnum, param_sim.plotcomps,ttGPe,ttstr))

    create_model_sim.setupStim(model)

    ##############--------------output elements
    if net.single:
        create_model_sim.setupOutput(model)
    else:   #population of neurons
        spiketab,vmtab,plastab,catab=net_output.SpikeTables(model, population['pop'], net.plot_netvm, plas, net.plots_per_neur)
        #simpath used to set-up simulation dt and hsolver
        simpath=[net.netname]
        clocks.assign_clocks(simpath, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)
        # Fix calculation of B parameter in CaConc if using hsolve
        if model.param_sim.hsolve and model.calYN:
            calcium.fix_calcium(util.neurontypes(model.param_cond), model)
    #
    if model.synYN and (param_sim.plot_synapse or net.single):
        #overwrite plastab above, since it is empty
        syntab, plastab, stp_tab=tables.syn_plastabs(connections,model)
    #
    #add short term plasticity to synapse as appropriate
    param_dict={'syn':presyn,'freq':stimfreq,'plas':model.stpYN,'inj':param_sim.injection_current,'simtime':param_sim.simtime, 'trial': trialnum,'dt':param_sim.plotdt}
    if stimfreq>0:
        from moose_nerp.prototypes import plasticity_test as plas_test
        extra_syntab={ntype:[] for ntype in  model.neurons.keys()}
        extra_plastabset={ntype:[] for ntype in  model.neurons.keys()}
        for ntype in model.neurons.keys():
            for tt_syn_tuple in model.tuples[ntype].values():
                if model.stpYN:
                    extra_syntab[ntype],extra_plastabset[ntype]=plas_test.short_term_plasticity_test(tt_syn_tuple,syn_delay=0,
                                                                            simdt=model.param_sim.simdt,stp_params=stp_params)
                else:
                    extra_syntab[ntype]=plas_test.short_term_plasticity_test(tt_syn_tuple,syn_delay=0)
            param_dict[ntype]={'syn_tt': [(k,tt[0].vector) for k,tt in model.tuples[ntype].items()]}
    #
    #################### Actually run the simulation
    param_sim.simtime=20.0
    print('$$$$$$$$$$$$$$ paradigm=', model.param_stim.Stimulation.Paradigm.name,' inj=0? ',np.all([inj==0 for inj in param_sim.injection_current]),'simtime:', param_sim.simtime)
    if model.param_stim.Stimulation.Paradigm.name is not 'inject' and not np.all([inj==0 for inj in param_sim.injection_current]):
        pg=inject_func.setupinj(model, param_sim.injection_delay,model.param_sim.simtime,model.inject_pop)
        inj=[i for i in param_sim.injection_current if i !=0]
        pg.firstLevel = param_sim.injection_current[0]
        create_model_sim.runOneSim(model, simtime=model.param_sim.simtime)
    else:
        for inj in model.param_sim.injection_current:
            create_model_sim.runOneSim(model, simtime=model.param_sim.simtime, injection_current=inj)

    #net_output.writeOutput(model, param_sim.fname+'vm',spiketab,vmtab,population)
    #
    #Save results: spike time, Vm, parameters, input time tables
    vmtab={ntype:[tab.vector for tab in tabset] for ntype,tabset in model.vmtab.items()}
    import ISI_anal
    spike_time,isis=ISI_anal.spike_isi_from_vm(model.vmtab,param_sim.simtime,soma=model.param_cond.NAME_SOMA)
    if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
        np.savez(outdir+param_sim.fname,spike_time=spike_time,isi=isis,params=param_dict,vm=vmtab)
    else:
        print('no spikes for',param_sim.fname, 'saving vm and parameters')
        np.savez(outdir+param_sim.fname,params=param_dict,vm=vmtab)
    if net.single:
        #save spiketime of all input time tables
        timtabs={}
        for neurtype,neurtype_dict in connections.items():
            for neur,neur_dict in neurtype_dict.items():
                for syn,syn_dict in neur_dict.items():
                    timtabs[syn]={}
                    for pretype,pre_dict in syn_dict.items():
                        timtabs[syn][pretype]={}
                        for branch,presyns in pre_dict.items():
                            if 'TimTab' in presyns:
                                timtabs[syn][pretype][branch]=moose.element(presyns).vector
        np.save(outdir+'tt'+param_sim.fname,timtabs)

    #create dictionary with the output (vectors) from test plasticity
    tab_dict={}
    if stimfreq>0:
        for ntype,tabset in extra_syntab.items():
            tab_dict[ntype]={'syn':tabset.vector,'syndt':tabset.dt, 
            'tt': {ntype+'_'+pt:tab.vector for pt,tab in model.tt[ntype].items()}}
            if model.stpYN:
                tab_dict[ntype]['plas']={tab.name:tab.vector for tab in extra_plastabset[ntype]}
    return param_dict,tab_dict,vmtab,spike_time,isis

def multi_main(p):
    from multiprocessing.pool import Pool
    import os
    
    max_pools=os.cpu_count()
    #to use different ttstr for each trial, create 15 different files in "synth_trains\spike_trains.py" with suffix t1-t15
    #p.ttstr+'t'+str(trial)
    sim_params=[(p.freq,p.syn,p.stpYN,trial,p.cond,p.ttGPe,p.ttstr) for trial in range(p.trials)]
    num_pools=min(len(sim_params),max_pools)
    print('************* number of processors',max_pools,' num params',len(sim_params), 'pools', num_pools,'syn', p.syn,'freq', p.freq)
    p = Pool(num_pools,maxtasksperchild=1)
    #
    results = p.map(moose_main,sim_params)

from moose_nerp.prototypes import standard_options 
def parse_args(commandline,do_exit):
    parser, _ = standard_options.standard_options()
    parser.add_argument("--cond",'-c', type=str, help = 'give exper name, for example: GABAosc')
    #these control synaptic strength and should start with GABA for ctrl, POST-HFS or POST-NoDa
    parser.add_argument("--syn",'-syn', type=str, default='non', help = 'optional: synapse type of special input, omit or non for none')
    parser.add_argument("--freq",'-f', type=int, default=0, help="optional: frequency of special input, omit or 0 for non")
    #could  change this to type list to provide a range of frequencies
    parser.add_argument("--trials",'-n', type=int, help="number of trials")
    parser.add_argument("--stpYN",'-stp', type=str, choices=["1", "0"],help="1 for yes, 0 for no short term plas")
    parser.add_argument("--ttGPe",'-tg', type=str, help="name of tt files for GPe")
    parser.add_argument("--ttstr",'-ts', type=str, help="name of tt files for Str")
    try:
        args = parser.parse_args(commandline) # maps arguments (commandline) to choices, and checks for validity of choices.
    except SystemExit:
        if do_exit:
            raise # raise the exception above (SystemExit)
        else:
            raise ValueError('invalid ARGS')
    return args

if __name__ == "__main__":
    #from within python: ARGS="--cond GABAosc --trials 15 --syn non --stp 1 --freq 0"
    #or ARGS="-c GABA -n 15 -syn non -stp 1 -f 0"
    #execfile ('multisim.py')
    #from outside python, see multi-sim.bat for examples
    import sys
    print('running main')
    try:
        args = ARGS.split(" ")
        print("ARGS =", ARGS, "commandline=", args)
        do_exit = False
    except NameError: #NameError refers to an undefined variable (in this case ARGS)
        args = sys.argv[1:]
        print("commandline =", args)
        do_exit = True
    params=parse_args(args,do_exit)
    print('params',params)
    results = multi_main(params)

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
