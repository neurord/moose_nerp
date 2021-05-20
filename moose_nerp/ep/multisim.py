from __future__ import print_function, division

def moose_main(p):
    stimfreq,presyn,stpYN,inj=p
    import numpy as np
    import moose
    from moose_nerp.prototypes import create_model_sim,inject_func
    from moose_nerp import ep as model

    model.synYN = True
    model.stpYN = stpYN
    outdir="ep/output/"
    if presyn=='none':
        stimtype='AP_' #choose from AP and PSP
    else:
        stimtype='PSP_'
    if stimfreq>0:
        model.param_sim.stim_paradigm=stimtype+str(stimfreq)+'Hz'
        print(model.param_sim.stim_paradigm,presyn)
        if presyn != 'none':
            model.param_stim.Stimulation.StimLoc=model.param_stim.location[presyn]
    else:
        model.param_sim.stim_paradigm='inject'
    
    create_model_sim.setupOptions(model)
    # Parameter overrides can be specified:

    param_sim = model.param_sim
    param_sim.injection_current= [inj] 
    #param_sim.injection_delay = 1.0
    param_sim.save_txt=True
    param_sim.plot_synapse=False
    param_sim.plot_calcium=False
    param_sim.plotcomps = list(set(param_sim.plotcomps+['p0b1','p0b1b1','p0b1b1a','p0b1b1c','p0b1b1_1']))

    # this is only needed if adding short term plasticity to synapse
    from moose_nerp import ep_net as net
    if presyn=='str' and model.stpYN:
        stp_params=net.param_net.str_plas
    elif presyn=='GPe' and model.stpYN:
        stp_params=net.param_net.GPe_plas
    else:
        print('########### unknown synapse type', presyn, 'or no STP')

    param_sim.fname='ep'+stimtype+presyn+'_freq'+str(stimfreq)+'_plas'+str(1 if model.stpYN else 0)+'_inj'+str(param_sim.injection_current[0])
    print('>>>>>>>>>> moose_main, stimfreq {} presyn {} stpYN {} plot comps {}'.format(stimfreq,presyn,stpYN,param_sim.plotcomps))

    # This function creates the neuron(s) in Moose:
    create_model_sim.setupNeurons(model)

    # This function sets up the Output options, e.g. saving, graph tables, etc.

    create_model_sim.setupOutput(model)

    # This function sets up the stimulation in Moose, e.g. pulsegen for current
    # injection or synaptic stimulation:
    create_model_sim.setupStim(model)
    param_sim.simtime=4.0

    #add short term plasticity to synapse as appropriate
    param_dict={'syn':presyn,'freq':stimfreq,'plas':model.stpYN,'inj':param_sim.injection_current,'simtime':param_sim.simtime,'dt':param_sim.plotdt}
    if model.param_stim.Stimulation.Paradigm.name.startswith('PSP'):
        from moose_nerp.prototypes import plasticity_test as plas_test
        syntab={ntype:[] for ntype in  model.neurons.keys()}
        plastabset={ntype:[] for ntype in  model.neurons.keys()}
        param_dict['syn_tt']={}
        for ntype in model.neurons.keys():
            for tt_syn_tuple in model.tuples[ntype].values():
                if model.stpYN:
                    syntab[ntype],plastabset[ntype]=plas_test.short_term_plasticity_test(tt_syn_tuple,syn_delay=0,
                                                                                         simdt=model.param_sim.simdt,stp_params=stp_params)
                else:
                    syntab[ntype]=plas_test.short_term_plasticity_test(tt_syn_tuple,syn_delay=0)
            param_dict['syn_tt'][ntype]=[(k,tt[0].vector) for k,tt in model.tuples[ntype].items()]

    #simulate the model
    if model.param_stim.Stimulation.Paradigm.name is not 'inject' and not np.all([ij==0 for ij in param_sim.injection_current]):
        print('$$$$$$$$$$$$$$ stim paradigm' ,model.param_stim.Stimulation.Paradigm.name, 'inject', param_sim.injection_current)
        neuron_pop = {ntype:[neur.path] for ntype, neur in model.neurons.items()}
        #set injection width to simulation time
        pg=inject_func.setupinj(model, param_sim.injection_delay,model.param_sim.simtime,neuron_pop)
        #for ij in model.param_sim.injection_current:
        pg.firstLevel=param_sim.injection_current[0]
    '''
            create_model_sim.runOneSim(model, simtime=model.param_sim.simtime)
    else:
    '''
    create_model_sim.runAll(model,printParams=True)
    print('<<<<<<<<<<< moose_main, sim {} finished'.format(param_sim.fname))

    #Extract spike times and calculate ISI if spikes occur
    vmtab={ntype:[tab.vector for tab in tabset] for ntype,tabset in model.vmtab.items()}
    import numpy as np
    from moose_nerp import ISI_anal
    #stim_spikes are spikes that occur during stimulation - they prevent correct psp_amp calculation
    spike_time,isis=ISI_anal.spike_isi_from_vm(model.vmtab,param_sim.simtime,soma=model.param_cond.NAME_SOMA)
    if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
        np.savez(outdir+param_sim.fname,spike_time=spike_time,isi=isis,params=param_dict,vm=vmtab)
        print('&&&&&&&&&&&&&&&&& Saving spike times &&&&&&&&&&&&&&&&&&&', param_sim.fname)
    if model.param_stim.Stimulation.Paradigm.name.startswith('PSP'):
        stim_spikes=ISI_anal.stim_spikes(spike_time,model.tt,soma=model.param_cond.NAME_SOMA)
        if not np.all([len(st) for tabset in stim_spikes.values() for st in tabset]):
            psp_amp,psp_norm=ISI_anal.psp_amp(model.vmtab,model.tt,soma=model.param_cond.NAME_SOMA)
            np.savez(outdir+param_sim.fname,amp=psp_amp,norm=psp_norm,params=param_dict,vm=vmtab)
            print('&&&&&&&&&&&&&&&&& Saving PSP amplitude &&&&&&&&&&&&&&&&&&&', param_sim.fname)
    #
    #create dictionary with the output (vectors) from tables 
    tab_dict={}
    if model.param_stim.Stimulation.Paradigm.name.startswith('PSP'):
        for ntype,tabset in syntab.items():
            tab_dict[ntype]={'syn':tabset.vector,'syndt':tabset.dt, 
                             'tt': {ntype+'_'+pt:tab.vector for pt,tab in model.tt[ntype].items()}}#,'tt_dt':tabset.dt}
            if model.stpYN:
                tab_dict[ntype]['plas']={tab.name:tab.vector for tab in plastabset[ntype]}

    return param_dict,tab_dict,vmtab,spike_time,isis

def multi_main(synset,stpYN,inj,stimfreqs):
    from multiprocessing.pool import Pool
    import os
    # Apply main simulation varying cortical fractions:
    params=[(freq,syntype,stpYN,inj) for freq in stimfreqs for syntype in synset]
    key=[(p[0],p[1]) for p in params]
    max_pools=os.cpu_count()
    num_pools=min(len(params),max_pools)
    print('************* number of processors',num_pools,' params',len(params),params, 'syn', synset)
    p = Pool(num_pools,maxtasksperchild=1)
    results = p.map(moose_main,params)
    return dict(zip(key,results))

if __name__ == "__main__":
    import sys
    print('running main')
    try:
        args = ARGS.split(" ")
        print("ARGS =", ARGS, "commandline=", args)
        plot_stuff=1
        do_exit = False
    except NameError: #NameError refers to an undefined variable (in this case ARGS)
        args = sys.argv[1:]
        plot_stuff=0
        print("commandline =", args)
        do_exit = True
    inj=float(args[0]) #choose from 0 or -15e-12 (15 pA)
    stpYN=int(args[1]) #either 0 or 1
    synset=args[2].split() 
    stimfreqs=[5,10,20,40,50]
    results = multi_main(synset,stpYN,inj,stimfreqs)

    if plot_stuff:
        #plot plasticity and synaptic response
        from matplotlib import pyplot as plt
        import numpy as np
        plt.ion()
        if stpYN:
            numplots=3
        else:
            numplots=1
        fig,axes =plt.subplots(numplots, len(synset),sharex=True)
        fig.canvas.set_window_title(synset)
        axis=fig.axes
        for (stimfreq,syntype),tabset in results.items():
            synindex=synset.index(syntype)#0 or 1
            param_dict,syntab_dict,vmtab,spike_time,isis=tabset
            for ntype,syntabs in syntab_dict.items():
                dt=syntabs['syndt'] 
                #print('*********** freq',stimfreq,'tt',syntabs['tt'])
                numpts=len(syntabs['syn'])
                time=np.arange(0,dt*numpts,dt)
                if stpYN:
                    for tabname,tab in syntabs['plas'].items():
                        if 'stp' in tabname:
                            axisnum=2*len(synset)
                            ylabel=syntype+' plas'
                        else:
                            axisnum=1*len(synset)
                            ylabel=syntype+' dep or fac'
                        labl=ntype+'_'+tabname[-4:-1]+str(stimfreq)
                        axis[synindex+axisnum].plot(time[0:numpts],tab,label=labl)
                        axis[synindex+axisnum].set_ylabel(ylabel)
            axis[synindex].plot(time[0:numpts],syntabs['syn']*1e9,label=ntype+' freq='+str(stimfreq))
            axis[synindex+(numplots-1)*len(synset)].set_xlabel('time, sec')
            axis[synindex].set_ylabel(syntype+' Gk*1e9')
            axis[synindex].legend()

