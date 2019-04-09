from __future__ import print_function, division
def moose_main(p):
    stimfreq,presyn,stpYN=p
    import moose
    from moose_nerp.prototypes import create_model_sim
    from moose_nerp.prototypes import plasticity_test as plas_test
    from moose_nerp import ep as model
    from moose_nerp import ep_net as net

    model.synYN = True
    model.stpYN = stpYN
    model.param_sim.stim_paradigm='PSP_'+str(stimfreq)+'Hz'
    create_model_sim.setupOptions(model)
    # Parameter overrides can be specified:
    #stim_protocol='PSP_'+str(stimfreq)+'Hz'
    #model.param_stim.Stimulation=model.param_stim.paradigm_dict[stim_protocol]

    param_sim = model.param_sim
    param_sim.injection_current= [-25e-12] 
    param_sim.save_txt=False
    param_sim.plot_synapse=True
    param_sim.plot_calcium=False

    if presyn=='str':
        stp_params=net.param_net.str_plas
    elif presyn=='GPe':
        stp_params=net.param_net.GPe_plas
    else:
        print('########### unknown synapse type')

    param_sim.fname='ep_syn'+presyn+'_freq'+str(stimfreq)+'_plas'+str(1 if model.stpYN else 0)+'_inj'+str(param_sim.injection_current[0])
    print('>>>>>>>>>> moose_main, stimfreq {} presyn {} stpYN {}'.format(stimfreq,presyn,stpYN))
    param_dict={'syn':presyn,'freq':stimfreq,'plas':model.stpYN,'inj':param_sim.injection_current}

    # This function creates the neuron(s) in Moose:
    create_model_sim.setupNeurons(model)

    # This function sets up the Output options, e.g. saving, graph tables, etc.
    create_model_sim.setupOutput(model)

    # This function sets up the stimulation in Moose, e.g. pulsegen for current
    # injection or synaptic stimulation:
    create_model_sim.setupStim(model)

    #add short term plasticity to synapse as appropriate - need to modify this to NOT create or hook up tt, just create plas and output tables
    syntab={ntype:[] for ntype in  model.neurons.keys()}
    plastabset={ntype:[] for ntype in  model.neurons.keys()}
    for ntype in model.neurons.keys():
        for tt_syn_pair in model.pairs[ntype].values():
            tt=tt_syn_pair[0]
            synchan=tt_syn_pair[1]
            if model.stpYN:
                syntab[ntype],plastabset[ntype]=plas_test.short_term_plasticity_test(synchan,tt,syn_delay=0,
                                                                                     simdt=model.param_sim.simdt,stp_params=stp_params)
            else:
                syntab[ntype]=plas_test.short_term_plasticity_test(synchan,tt,syn_delay=0)

    #simulate the model
    create_model_sim.runAll(model,printParams=False)
    print('<<<<<<<<<<< moose_main, sim {} finished'.format(param_sim.fname))

    #create dictionary with the output (vectors) from tables
    tab_dict={}
    for ntype,tabset in syntab.items():
        tab_dict[ntype]={'syn':tabset.vector,'syndt':tabset.dt,
        'tt': {ntype+'_'+pt:tab.vector for pt,tab in model.tt[ntype].items()}}#,'tt_dt':tabset.dt}
        if model.stpYN:
            tab_dict[ntype]['plas']={tab.name:tab.vector for tab in plastabset[ntype]}
    return tab_dict

def multi_main(syntype,stpYN):
    from multiprocessing.pool import Pool
    p = Pool(12,maxtasksperchild=1)
    # Apply main simulation varying cortical fractions:
    stimfreqs=[5,10,20,40]
    params=[(freq,syntype,stpYN) for freq in stimfreqs]
    results = p.map(moose_main,params)
    return dict(zip(stimfreqs,results))

if __name__ == "__main__":
    print('running main')
    syn='GPe'
    stpYN=1
    results = multi_main(syn,stpYN)

    #plot plasticity and synaptic response
    from matplotlib import pyplot as plt
    import numpy as np
    plt.ion()
    if stpYN:
        numplots=3
    else:
        numplots=1
    fig,axes =plt.subplots(numplots, 1,sharex=True)
    fig.canvas.set_window_title(syn)
    axis=fig.axes
    axis[-1].set_xlabel('time, sec')
    for stimfreq,tabset in results.items():
        for ntype,tabs in tabset.items():
            dt=tabs['syndt'] 
            print('*********** freq',stimfreq,'tt',tabs['tt'])
            numpts=len(tabs['syn'])
            time=np.arange(0,dt*numpts,dt)
            if stpYN:
                for tabname,tab in tabs['plas'].items():
                    if 'stp' in tabname:
                        axisnum=1
                    else:
                        axisnum=0
                    labl=ntype+'_'+tabname[-4:-1]+str(stimfreq)
                    axis[axisnum].plot(time[0:numpts],tab,label=labl)
                axis[0].set_ylabel('dep or fac')
                axis[1].set_ylabel('plas')
                axis[0].legend()
        axis[2].plot(time[0:numpts],tabset[ntype]['syn']*1e9,label=ntype+' freq='+str(stimfreq))
        axis[2].set_ylabel('Gk*1e9')
    axis[2].legend()

'''
ToDo:
add these functions to network simulation - possibly "reserve" the synapse from random time tables
write tables to disk, move spike time and ISI calculation into function
add trial number as parameter in network simulations
calculate ISI across trials
'''   
