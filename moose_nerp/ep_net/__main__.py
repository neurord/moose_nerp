# -*- coding:utf-8 -*-

######## GPnetSim.py ############
"""
Create a network of EP neurons using dictionaries for channels, synapses, and network parameters
net.single=True creates single neuron with timetable (spike train) inputs
net.single=False creates network of neurons with timetable (spike train) inputs
Optional long term synaptic plasticity based on calcium (plasYN=1)
optional pre-synaptic spike-based short term plasticity (stpYN=1)
Spines are optional (spineYesNo=1), but not allowed for net.single=False
The graphs won't work for multiple spines per compartment
"""

from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt
plt.ion()

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
model.stpYN = True
net.single=True

#these parameters passed are passed into function in multisim.py
stimtype='PSP_' #choose from AP and PSP
presyn='non' #choose from 'str', 'GPe', or 'non' to provide no additional input
stimfreq=0 #choose from 1,5,10,20,40
outdir="ep_net/output/"
prefix='GABAoscStr'
############## if stim_freq>0, stim_paradigm adds regular input and synaptic plasticity at specified synapse ####################
if stimfreq>0:
    model.param_sim.stim_paradigm=stimtype+str(stimfreq)+'Hz'
    model.param_stim.Stimulation.StimLoc=model.param_stim.location[presyn]
else:
    model.param_sim.stim_paradigm='inject'

create_model_sim.setupOptions(model)
param_sim = model.param_sim
param_sim.injection_current = [-0e-12]
param_sim.injection_delay = 0.0
param_sim.injection_width = param_sim.simtime
param_sim.plot_synapse=True
param_sim.save_txt = False

if prefix.startswith('POST-HFS'):
    net.connect_dict['ep']['ampa']['extern1'].weight=0.6 #STN - weaker
    net.connect_dict['ep']['gaba']['extern2'].weight=0.8 #GPe - weaker
    net.connect_dict['ep']['gaba']['extern3'].weight=1.4 #str - stronger
if prefix.startswith('POST-NoDa'):
    net.connect_dict['ep']['ampa']['extern1'].weight=1.0 #STN - no change
    net.connect_dict['ep']['gaba']['extern2'].weight=2.8 #GPe - stronger
    net.connect_dict['ep']['gaba']['extern3'].weight=1.0 #str - no change

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

param_sim.fname='ep'+prefix+stimtype+presyn+'_freq'+str(stimfreq)+'_plas'+str(1 if model.stpYN else 0)+'_inj'+str(param_sim.injection_current[0])
print('>>>>>>>>>> moose_main, protocol {} presyn {} stpYN {} stimfreq {} simtime {} plotcomps {} '.format(model.param_sim.stim_paradigm,presyn,model.stpYN,stimfreq, param_sim.simtime, param_sim.plotcomps))

create_model_sim.setupStim(model)
print('>>>> After setupStim, simtime:', param_sim.simtime) 
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

if model.synYN and (param_sim.plot_synapse or net.single):
    #overwrite plastab above, since it is empty
    syntab, plastab, stp_tab=tables.syn_plastabs(connections,model)

#add short term plasticity to synapse as appropriate
param_dict={'syn':presyn,'freq':stimfreq,'plas':model.stpYN,'inj':param_sim.injection_current,'simtime':param_sim.simtime,'dt':param_sim.plotdt}
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

#################### Actually run the simulation
param_sim.simtime=1
print('$$$$$$$$$$$$$$ paradigm=', model.param_stim.Stimulation.Paradigm.name,' inj=0? ',np.all([inj==0 for inj in param_sim.injection_current]),', simtime:', param_sim.simtime)
#in case simtime was changed by setupStim, make sure injection width is long enough
#param_sim.injection_width = param_sim.simtime-param_sim.injection_delay

traces, names = [], []
pg=False
if model.param_stim.Stimulation.Paradigm.name is not 'inject' and not np.all([inj==0 for inj in param_sim.injection_current]):
    pg=inject_func.setupinj(model, param_sim.injection_delay,param_sim.injection_width,model.inject_pop)
for inj in param_sim.injection_current:
    if pg:
        pg.firstLevel = inj
        create_model_sim.runOneSim(model, simtime=model.param_sim.simtime)
    else:
        create_model_sim.runOneSim(model, simtime=model.param_sim.simtime, injection_current=inj)
    if net.single and len(model.vmtab):
        for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
            traces.append(model.vmtab[neurtype][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
        if model.synYN:
            net_graph.syn_graph(connections, syntab, param_sim,graph_title="Syn Chans, plasticity="+str(model.stpYN))
            if model.stpYN:
                net_graph.syn_graph(connections, stp_tab,param_sim,graph_title='short term plasticity')
        if model.spineYN:
            spine_graph.spineFig(model,model.spinecatab,model.spinevmtab, param_sim.simtime)
    else:
        if net.plot_netvm:
            net_graph.graphs(population['pop'], param_sim.simtime, vmtab,catab,plastab)
        if model.synYN and param_sim.plot_synapse:
            net_graph.syn_graph(connections, syntab, param_sim)
            if model.stpYN:
                net_graph.syn_graph(connections, stp_tab,param_sim,graph_title='short term plasticity',factor=1)
        net_output.writeOutput(model, net.outfile+str(inj),spiketab,vmtab,population)

#Save results: spike time, Vm, parameters, input time tables
vmtab={ntype:[tab.vector for tab in tabset] for ntype,tabset in model.vmtab.items()}
import ISI_anal
spike_time,isis=ISI_anal.spike_isi_from_vm(model.vmtab,param_sim.simtime,soma=model.param_cond.NAME_SOMA)

if model.param_sim.save_txt:
    if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
        np.savez(outdir+param_sim.fname,spike_time=spike_time,isi=isis,params=param_dict,vm=vmtab)
    else:
        print('no spikes for',param_sim.fname, 'saving vm and parameters')
        np.savez(outdir+param_sim.fname,params=param_dict,vm=vmtab)
#spikes=[st.vector for tabset in spiketab for st in tabset]

if net.single:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    #save spiketime of all input time tables
    timtabs={}
    for neurtype,neurtype_dict in connections.items():
        for neur,neur_dict in neurtype_dict.items():
            for syn,syn_dict in neur_dict.items():
                timtabs[syn]={}
                for pretype,pre_dict in syn_dict.items():
                    timtabs[syn][pretype]={}
                    for branch,presyn in pre_dict.items():
                        if 'TimTab' in presyn:
                            timtabs[syn][pretype][branch]=moose.element(presyn).vector
    np.save(outdir+'tt'+param_sim.fname,timtabs)
    # block in non-interactive mode
util.block_if_noninteractive()

if stimfreq>0:
    plt.figure()
    plt.title('synapse')
    for ntype in extra_syntab.keys():
        numpts=len(extra_syntab[ntype].vector)
        time=np.arange(0,extra_syntab[ntype].dt*numpts,extra_syntab[ntype].dt)
        if model.stpYN:
            for i,tab in enumerate(extra_plastabset[ntype]):
                offset=i*0.02
                labl=tab.name[-4:-1]+'+'+str(offset)
                plt.plot(time[0:numpts],tab.vector+offset,label=labl)
    plt.plot(time[0:numpts],extra_syntab[ntype].vector*1e9,label='Gk*1e9')
    plt.legend()


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
