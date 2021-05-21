# -*- coding:utf-8 -*-

########  ############
## Code to create entopeduncular neuron
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional

from __future__ import print_function, division
import moose
import numpy as np
from moose_nerp.prototypes import create_model_sim, inject_func
from moose_nerp import ep as model
'''Imports functions for setting up and simulating model. These take the `model`
namespace as argument, and append variables to this namespace. Thus, after
running a simulation, the output tables would be accessible as model.vmtab,
model.catab, etc.'''
plot_facil=False
model.synYN = False
model.stpYN = False
presyn='none' #choose from 'str', 'GPe', 'none'
stimfreq=0 #choose from 1,5,10,20,40
stimtype='AP_'#choose from AP and PSP
if stimfreq>0:
    model.param_sim.stim_paradigm=stimtype+str(stimfreq)+'Hz'
    model.param_stim.Stimulation.StimLoc=model.param_stim.location[presyn]
else:
    model.param_sim.stim_paradigm='inject'

# This function sets up the options specified in param_sim or passed from
# command line:
create_model_sim.setupOptions(model)
# Parameter overrides can be specified:
param_sim = model.param_sim
param_sim.injection_current = [-100e-12,-200e-12,0e-12,25e-12, 50e-12]#,75e-12,100e-12,150e-12,200e-12]
param_sim.injection_delay = 0.2
param_sim.injection_width=0.3
param_sim.simtime=0.7

param_sim.save_txt=False
#param_sim.plot_synapse=True
param_sim.plot_calcium=False
#param_sim.plotcomps = list(set(param_sim.plotcomps+['p0b1','p0b1b1','p0b1b1a','p0b1b1c','p0b1b1_1']))
#soma:13 um diam
#p0b1:16 um away
#p0b1b1:60 um 
#p0b1b1a:36 um 

# this is only needed if adding short term plasticity to synapse
from moose_nerp import ep_net as net
if presyn=='str' and model.stpYN:
    stp_params=net.param_net.str_plas
elif presyn=='GPe' and model.stpYN:
    stp_params=net.param_net.GPe_plas
else:
    print('########### unknown synapse type:', presyn)

param_sim.fname='ep'+stimtype+presyn+'_freq'+str(stimfreq)+'_plas'+str(1 if model.stpYN else 0)
if model.param_sim.stim_paradigm != 'inject':
    param_sim.fname=param_sim.fname+'_inj'+str(param_sim.injection_current[0])
print('>>>>>>>>>> moose_main, protocol {} presyn {} stpYN {} plot comps {}'.format(model.param_sim.stim_paradigm,presyn,model.stpYN,param_sim.plotcomps))

# This function creates the neuron(s) in Moose:
create_model_sim.setupNeurons(model)

# This function sets up the Output options, e.g. saving, graph tables, etc.
create_model_sim.setupOutput(model)

# This function sets up the stimulation in Moose, e.g. pulsegen for current
# injection or synaptic stimulation:
create_model_sim.setupStim(model)

#add short term plasticity to synapse as appropriate
param_dict={'syn':presyn,'freq':stimfreq,'plas':model.stpYN,'inj':param_sim.injection_current,'simtime':param_sim.simtime,'dt':param_sim.plotdt}
if model.param_stim.Stimulation.Paradigm.name.startswith('PSP'):
    from moose_nerp.prototypes import plasticity_test as plas_test
    syntab={ntype:[] for ntype in  model.neurons.keys()}
    plastabset={ntype:[] for ntype in  model.neurons.keys()}
    for ntype in model.neurons.keys():
        for tt_syn_tuple in model.tuples[ntype].values():
            if model.stpYN:
                syntab[ntype],plastabset[ntype]=plas_test.short_term_plasticity_test(tt_syn_tuple,syn_delay=0,
                                                                       simdt=model.param_sim.simdt,stp_params=stp_params)
            else:
                syntab[ntype]=plas_test.short_term_plasticity_test(tt_syn_tuple,syn_delay=0)
        param_dict[ntype]={'syn_tt': [(k,tt[0].vector) for k,tt in model.tuples[ntype].items()]}

        #additional current injection, e.g. if an offset current is desired
if model.param_stim.Stimulation.Paradigm.name is not 'inject' and not np.all([inj==0 for inj in param_sim.injection_current]):
    print('$$$$$$$$$$$$$$ stim paradigm',model.param_stim.Stimulation.Paradigm.name, 'inject', param_sim.injection_current)
    neuron_pop = {ntype:[neur.path] for ntype, neur in model.neurons.items()}
    #set injection width to simulation time
    pg=inject_func.setupinj(model, param_sim.injection_delay,param_sim.simtime,neuron_pop)
    pg.firstLevel = param_sim.injection_current[0]

##################### for debugging: shows that some spikes elicit 2x increase in weight
if plot_facil:
    fac=moose.element('/ep/p2b2b1/gaba/fac0')
    x0=fac.x[0]
    x1=fac.x[1]
    x0tab=moose.Table('x0tab')
    x1tab=moose.Table('x1tab') #better captures presyn than ttstate
    moose.connect(x0tab,'requestOut',x0,'getValue')
    moose.connect(x1tab,'requestOut',x1,'getValue')

#param_sim.simtime=0.01

##################### 
create_model_sim.runAll(model,printParams=True)
print('<<<<<<<<<<< moose_main, sim {} finished'.format(param_sim.fname))

# Alternative function to create_model_sim.runAll, that runs a simulation a few
# steps at a time and then updates a plot, to show the live simulation results.
# This is an example of modifying, expanding, or customizing code:
#   `create_model_sim.stepRunPlot(model)`

###################### Analysis ##############################
#Extract spike times and calculate ISI if spikes occur
import numpy as np
from moose_nerp import ISI_anal

#stim_spikes are spikes that occur during stimulation - they prevent correct psp_amp calculation
spike_time,isis=ISI_anal.spike_isi_from_vm(model.vmtab,param_sim.simtime,soma=model.param_cond.NAME_SOMA)
if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
    if model.param_sim.save_txt:
        np.savez(param_sim.fname,spike_time=spike_time,isi=isis,params=param_dict)

if model.param_stim.Stimulation.Paradigm.name.startswith('PSP'):
    stim_spikes=ISI_anal.stim_spikes(spike_time,model.tt,soma=model.param_cond.NAME_SOMA)
    if not np.all([len(st) for tabset in stim_spikes.values() for st in tabset]):
        #Extract amplitude of PSPs based on knowledge of spike time if no spikes during stimulation
        psp_amp,psp_norm=ISI_anal.psp_amp(model.vmtab,model.tt,soma=model.param_cond.NAME_SOMA)
        if model.param_sim.save_txt:
            np.savez(param_sim.fname,amp=psp_amp,norm=psp_norm,params=param_dict)
else:
    psp_norm=None

########################## Plotting results ##############################
#plot plasticity and synaptic response
from matplotlib import pyplot as plt
plt.ion()
if model.param_stim.Stimulation.Paradigm.name.startswith('PSP'):
    plt.figure()
    plt.title('synapse')
    for ntype in model.neurons.keys():
        numpts=len(syntab[ntype].vector)
        time=np.arange(0,syntab[ntype].dt*numpts,syntab[ntype].dt)
        if model.stpYN:
            for i,tab in enumerate(plastabset[ntype]):
                offset=i*0.02
                labl=tab.name[-4:-1]+'+'+str(offset)
                plt.plot(time[0:numpts],tab.vector+offset,label=labl)
    plt.plot(time[0:numpts],syntab[ntype].vector*1e9,label='Gk*1e9')
    plt.legend()

##################### for debugging: shows that some spikes elicit 2x increase in weight
if plot_facil:
    plt.figure()
    plt.title(fac.expr)
    plt.plot(time[0:numpts],x0tab.vector,label='x0tab')
    plt.plot(time[0:numpts],x1tab.vector,label='x1tab')
    plt.legend()
#####################

#plot spikes or PSP amplitude if no spikes during stimulation
if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
    plt.figure()
    plt.title('ISI vs time for '+presyn+' at '+str(stimfreq)+'hz')
    plt.xlabel('Time (msec)')
    plt.ylabel('ISI (sec)')
    for neurtype, tabset in isis.items():
        for i,tab in enumerate(tabset):
            plt.plot(spike_time[neurtype][i][0:len(tab)],tab,'o')
if psp_norm:
    plt.figure()
    plt.title('normalized PSP amp vs time for '+presyn+' at '+str(stimfreq)+'hz')
    plt.ylabel('Normalized PSP amp')
    plt.xlabel('stim number')
    for neurtype, tabset in psp_norm.items():
        for i,tab in enumerate(tabset):
            plt.plot(range(len(tab)),tab,'o')


