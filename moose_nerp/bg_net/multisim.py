from __future__ import print_function, division

def moose_main(p):
    stop_signal,freqCtx,freqStn,pulsedur,rampdur,fb_npas,fb_lhx,FSI_input,simtime,trial=p
    import numpy as np
    import moose
    import importlib
    from moose_nerp.prototypes import (calcium,
                                       cell_proto,
                                       create_model_sim,
                                       clocks,
                                       inject_func,
                                       create_network,
                                       pop_funcs,
                                       tables,
                                       net_output,
                                       util,
                                       multi_module,
                                       net_sim_graph)
    from moose_nerp import spn_1comp as model
    from moose_nerp import bg_net as net

    #output file names and time table inputs depend on input parameters
    net.confile,net.outfile=net.fname(stop_signal,freqCtx,freqStn,pulsedur,rampdur,fb_npas,fb_lhx,FSI_input)
    net.outfile=net.outfile+'t'+str(trial)
    if stop_signal: #regardless, STN2000_lognorm_freq28.0.npz is used
        print('if stop signal',stop_signal,'param_net',net.param_net.tt_Ctx.filename,'fname',net.outfile)
        net.param_net.tt_Ctx.filename='bg_net/Ctx10000_ramp_freq7.0_'+freqCtx+'dur'+str(rampdur)
        net.param_net.tt_STNp.filename='bg_net/STN500_pulse_freq1.0_'+freqStn+'dur'+str(pulsedur)
    else:
        net.param_net.tt_Ctx.filename='bg_net/Ctx10000_osc_freq'+freqCtx+'_osc0.7'
   
    if stop_signal: #add in second "pulse" time table, change postyn fraction for the log normal inpput
        net.connect_dict,net.change_prob=net.add_connect(net.connect_dict,net.change_prob,freqStn) 
    
    net.connect_dict=net.feedback(net.connect_dict,fb_npas,fb_lhx)
    net.connect_delete=net.change_FSI(net.connect_delete,net.p['FSI_input'])

    np.random.seed()
    #names of additional neuron modules to import
    neuron_modules=['ep_1comp','proto154_1compNoCal','Npas2005_1compNoCal','arky140_1compNoCal','FSI01Aug2014']

    ### By importing network modules, no need to repeat all the information in param_net.py
    net_modules=['moose_nerp.ep_net','moose_nerp.gp_net', 'moose_nerp.spn1_net']

    #only save vm trace from save_num neurons of each type if there are more than too_many_neurons
    #consider putting this stuff into param_net
    too_many_neurons=30
    save_num=2
    savett=True
    save_conn=False

    #additional, optional parameter overrides specified from with python terminal
    model.synYN = True
    net.single=False
    outdir="bg_net/output/"
    create_model_sim.setupOptions(model)
    param_sim = model.param_sim
    param_sim.injection_current = [0e-12]
    net.num_inject=0
    param_sim.injection_width=0.3
    param_sim.injection_delay=0.2
    param_sim.save_txt = True
    param_sim.simtime=simtime
    
    #################################-----------create the model: neurons, and synaptic inputs
    #### Do not setup hsolve yet, since there may be additional neuron_modules
    model=create_model_sim.setupNeurons(model,network=True)

    #create dictionary of BufferCapacityDensity - only needed if hsolve, simple calcium dynamics
    buf_cap={neur:model.param_ca_plas.BufferCapacityDensity for neur in model.neurons.keys()}

    #import additional neuron modules, add them to neurons and synapses
    ######## this is skipped if neuron_modules is empty
    if len(neuron_modules):
        buf_cap=multi_module.multi_modules(neuron_modules,model,buf_cap,net.change_syn)

    ########### Create Network. For multiple populations, send in net_modules ###########
    population,[connections,conn_summary],plas=create_network.create_network(model, net, model.neurons,network_list=net_modules)
    #print(net.connect_dict)
    total_neurons=np.sum([len(pop) for pop in population['pop'].values()])
    if total_neurons<too_many_neurons:
        print('populations created and connected!!!',population['pop'],'\n',population['netnames'])
    else:
        print('populations created and connected!!!',[(key,len(pop)) for key,pop in population['pop'].items()])
    ###### Set up stimulation - could be current injection or plasticity protocol
    # set num_inject=0 to avoid current injection
    if net.num_inject<np.inf :
        model.inject_pop=inject_func.inject_pop(population['pop'],net.num_inject)
        if net.num_inject==0:
            param_sim.injection_current=[0]
    else:
        model.inject_pop=population['pop']

    create_model_sim.setupStim(model)

##############--------------output elements
    if net.single:
        #simpath used to set-up simulation dt and hsolver
        simpath=['/'+neurotype for neurotype in model.neurons.keys()]
        create_model_sim.setupOutput(model)
    else:   #population of neurons
        model.spiketab,model.vmtab,model.plastab,model.catab=net_output.SpikeTables(model, population['pop'], net.plot_netvm, plas, net.plots_per_neur)
        #simpath used to set-up simulation dt and hsolver
        simpath=[netname for netname in population['netnames']]
        print('simpath',simpath)

    #### Set up hsolve and fix calcium
    clocks.assign_clocks(simpath, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)
    # Fix calculation of B parameter in CaConc if using hsolve and calcium
    ######### Need to use CaPlasticityParams.BufferCapacityDensity from EACH neuron_module
    if model.param_sim.hsolve and model.calYN:
        calcium.fix_calcium(model.neurons.keys(), model, buf_cap)

    if model.synYN and (param_sim.plot_synapse or net.single):
        #overwrite plastab above, since it is empty
        model.syntab, model.plastab, model.stp_tab=tables.syn_plastabs(connections,model)

    ################### Actually run the simulation
    #net_sim_graph.sim_plot(model,net,connections,population)
    for inj in model.param_sim.injection_current:
        print('ready to simulation with', inj)
        create_model_sim.runOneSim(model, simtime=model.param_sim.simtime, injection_current=inj)
    
    ##### extract spikes and save information
    from moose_nerp import ISI_anal
    spike_time,isis=ISI_anal.spike_isi_from_vm(model.vmtab,model.param_sim.simtime,soma=model.param_cond.NAME_SOMA,print_comp=False)

    for neurtype in isis:
        if len(isis):
            print(neurtype,': mean rate of ',np.round(np.nanmean([len(st) for st in spike_time[neurtype]])/param_sim.simtime,3),'from', len(spike_time[neurtype]),'neurons')
        else:
            print(neurtype,': no neurons')

    ####### conn_dict is summary of number of connection properties
    from moose_nerp.prototypes.ttables import TableSet
    conn_dict=[]
    for ntype in net.connect_dict.keys():
        for syntype in net.connect_dict[ntype].keys():
            for pretype,info in net.connect_dict[ntype][syntype].items():
                if isinstance(info.pre,TableSet):
                    conn_dict.append({'neur':ntype,'syn':syntype,'pre':pretype,'params':{'infil':info.pre.filename,'wt':info.weight}})
                else:
                    conn_dict.append({'neur':ntype,'syn':syntype,'pre':pretype,'params':{'nc':info.num_conns,'prob':info.probability,'sc':info.space_const,'wt':info.weight}})

    params={'simtime':model.param_sim.simtime,,'plotdt':model.param_sim.plotdt,'numSyn':model.NumSyn,'connect_dict':conn_dict}

    ######### Actually save data - just spikes if they occur.  also conn_dict
    print('************ output file name',net.outfile)
    if model.param_sim.save_txt:
        if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
            np.savez(outdir+net.outfile,spike_time=spike_time,isi=isis,params=params)
        elif total_neurons<too_many_neurons:
            print('no spikes for',param_sim.fname, 'saving vm and parameters')
            vmout={ntype:[tab.vector for tab in tabset] for ntype,tabset in model.vmtab.items()}
            np.savez(outdir+net.outfile,vm=vmout)
        else:
            print('no spikes for',param_sim.fname,'and too many neurons. Saving vm for',save_num,' neurons of each population')
            vmout={ntype:[tab.vector for tab in tabset[0:save_num]] for ntype,tabset in model.vmtab.items()}
            np.savez(outdir+net.outfile,vm=vmout)

        #save/write out the list of connections and location of each neuron

        if save_conn:
            np.savez(net.confile,conn=connections,loc=population['location'],summary=conn_summary)
        else:
            np.savez(net.confile,summary=conn_summary)
        #
    return spike_time,isis,params,conn_summary

def multi_main(p):
    from multiprocessing.pool import Pool
    import os
    # Apply main simulation varying cortical fractions:
    params=[(p.stoptask,p.ctxfreq,p.stnfreq,p.pulsedur,p.rampdur,p.fb_npas,p.fb_lhx,p.FSI,p.simtime,i) for i in range(p.trials)]
    max_pools=os.cpu_count()
    num_pools=min(len(params),max_pools)
    print('************* number of processors',num_pools,' params',len(params),params)
    pp = Pool(num_pools,maxtasksperchild=1)
    results = pp.map(moose_main,params)
    return dict(zip(range(p.trials),results))
    
from moose_nerp.prototypes import standard_options
def parse_args(commandline,do_exit):
    parser, _ = standard_options.standard_options()
    parser.add_argument("--stoptask", type=standard_options.parse_boolean, default=False, help="True to provide stop signal input")
    parser.add_argument("--fb_npas", type=int, default=3, help = "weight for npas feedback to SPNs")
    parser.add_argument("--fb_lhx",type=int, default=4, help="weight for lhx6 feedback to FSIs")
    parser.add_argument("--trials",type=int, help="number of trials")
    parser.add_argument("--pulsedur",'-dur', type=float, default=0,help="duration of stn pulse inputs during stop task") 
    parser.add_argument("--stnfreq",'-stn', type=str, help="frequency of stn inputs to GPe")
    parser.add_argument("--rampdur",'-ramp', type=float, default=0,help="duration of ctx ramp inputs to striatum")
    parser.add_argument("--ctxfreq",'-ctx', type=str, help="frequency of ctx inputs to striatum")
    parser.add_argument("--FSI",'-FSI', type=str, default='11', help="2 bit string controlling FSI inputs, first bit=0 deletes inputs to FSI, 2nd bit=0 deletes inputs to SPNs")
    try:
        args = parser.parse_args(commandline) # maps arguments (commandline) to choices, and checks for validity of choices.
    except SystemExit:
        if do_exit:
            raise # raise the exception above (SystemExit)
        else:
            raise ValueError('invalid ARGS')
    return args

if __name__ == "__main__":
    #from within python: ARGS="--cond stopsig --trials 15 "
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
    print('main: params',params)
    results = multi_main(params)


