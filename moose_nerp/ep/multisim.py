from __future__ import print_function, division
def moose_main(p):
    stimfreq,syntype,stpYN=p
    import moose
    from moose_nerp.prototypes import create_model_sim
    from moose_nerp.prototypes import plasticity
    from moose_nerp import ep as model
    from moose_nerp import ep_net as net

    syn_delay=1.0
    minpulses=10
    model.synYN = True
    model.stpYN = stpYN

    create_model_sim.setupOptions(model)
    # Parameter overrides can be specified:
    param_sim = model.param_sim
    param_sim.injection_delay = 0.0
    param_sim.save_txt=False
    param_sim.injection_current = [-1e-12] 
    param_sim.plot_synapse=True
    param_sim.plot_calcium=False
    param_sim.fname='ep_syn'+syntype+'_freq'+str(stimfreq)+'_plas'+str(1 if model.stpYN else 0)
    print('>>>>>>>>>> moose_main, stimfreq {} syntype {} stpYN {}'.format(stimfreq,syntype,stpYN))

    tt=moose.TimeTable('tt'+str(stimfreq)+'hz')
    if stimfreq<minpulses:
        param_sim.simtime = syn_delay+minpulses/float(stimfreq)
        tt.vector=[syn_delay+n/float(stimfreq) for n in range(minpulses)]
    else:
        param_sim.simtime = syn_delay+1.1
        tt.vector=[syn_delay+n/float(stimfreq) for n in range(stimfreq)]
    param_sim.injection_width = param_sim.simtime-param_sim.injection_delay

    param_dict={'syn':syntype,'freq':stimfreq,'plas':model.stpYN,'inj':param_sim.injection_current}
    outfile=param_sim.fname+'_inj'+str(param_sim.injection_current[0])

    # This function creates the neuron(s) in Moose:
    create_model_sim.setupNeurons(model)

    # This function sets up the Output options, e.g. saving, graph tables, etc.
    create_model_sim.setupOutput(model)

    # This function sets up the stimulation in Moose, e.g. pulsegen for current
    # injection or synaptic stimulation:
    create_model_sim.setupStim(model)

    if syntype=='str':
        synchan=moose.element('/ep[0]/p0b1b1b2[0]/gaba[0]/')#str synchan
        stp_params=net.param_net.str_plas
    elif syntype=='GPe':
        synchan=moose.element('/ep[0]/p0b1[0]/gaba[0]/') #gp synchan
        stp_params=net.param_net.GPe_plas
    else:
        print('########### unknown synapse type')

    #Connect time table of synaptic inputs to synapse
    sh=moose.element(synchan.path+'/SH')
    sh.numSynapses=1
    moose.connect(tt,'eventOut', sh.synapse[0], 'addSpike')
    #create output table for the synaptic response
    syn_tab=moose.Table('/syntab')
    moose.connect(syn_tab,'requestOut',synchan,'getGk')

    #add short term plasticity to synapse as appropriate
    if model.stpYN:
        simdt =  model.param_sim.simdt
        plasticity.ShortTermPlas(sh.synapse[0],0,stp_params,simdt,tt,'eventOut')
        #Add output tables for plasticity
        if stp_params.depress is not None:
            deptab = moose.Table('/deptab')
            dep=moose.element(synchan.path+'/dep0')
            moose.connect(deptab, 'requestOut', dep, 'getValue')
        if stp_params.facil is not None:
            factab = moose.Table('/factab')
            fac=moose.element(synchan.path+'/fac0')
            moose.connect(factab, 'requestOut', fac, 'getValue')
        plas_tab = moose.Table('/plastab')
        plas=moose.element(synchan.path+'/stp0')
        moose.connect(plas_tab, 'requestOut', plas, 'getValue')

    #simulate the model
    create_model_sim.runAll(model,printParams=False)
    print('<<<<<<<<<<< moose_main, sim {} finished'.format(param_sim.fname))
    tab_dict={'syn':syn_tab.vector, 'tt': tt.vector,'dt':{'tabdt':syn_tab.dt,'ttdt':tt.dt}}
    if model.stpYN:
        tab_dict['plas']=plas_tab.vector
        if stp_params.depress is not None:
            tab_dict['dep']=deptab.vector
        if stp_params.facil is not None:
            tab_dict['fac']=factab.vector
    return tab_dict

def multi_main(syntype,stpYN):
    from multiprocessing.pool import Pool
    p = Pool(12,maxtasksperchild=1)
    # Apply main simulation varying cortical fractions:
    stimfreqs=[10,20,40]
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
        dt=tabset['dt']['tabdt']
        print('*********** freq',stimfreq,'tt',tabset['tt'])
        numpts=len(tabset['plas'])
        time=np.arange(0,dt*numpts,dt)
        if stpYN:
            if 'dep' in tabset.keys():
                axis[0].plot(time[0:numpts],tabset['dep'],label='dep '+str(stimfreq))
            if 'fac' in tabset.keys():
                axis[0].plot(time[0:numpts],tabset['fac'],label='fac '+str(stimfreq))
            axis[0].set_ylabel('dep or fac')
            axis[1].plot(time[0:numpts],tabset['plas'],label='freq='+str(stimfreq))
            axis[1].set_ylabel('plas')
        axis[2].plot(time[0:numpts],tabset['syn']*1e9,label='freq='+str(stimfreq))
        axis[2].set_ylabel('Gk*1e9')
    axis[2].legend()

'''
ToDo:
make synchan a parameter/option
Put the single tt connected to synchan and output tables into function for testing plasticity
add those functions to network simulation
write tables to disk, move spike time and ISI calculation into function
add trial number as parameter in network simulations
calculate ISI across trials
'''   
