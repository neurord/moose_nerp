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

model.synYN = False#True
model.stpYN = False#True
presyn='str' #choose from 'str', 'GPe', 'none'
stimfreq=10 #choose from 1,5,10,20,40
stimtype='PSP_' #choose from AP and PSP
model.param_sim.stim_paradigm=stimtype+str(stimfreq)+'Hz'
model.param_stim.Stimulation.StimLoc=model.param_stim.location[presyn]
model.param_sim.stim_paradigm='inject'
# This function sets up the options specified in param_sim or passed from
# command line:
create_model_sim.setupOptions(model)
# Parameter overrides can be specified:
param_sim = model.param_sim
param_sim.injection_current = [0e-12]
param_sim.injection_delay = 0.0
param_sim.injection_width = 1.0
param_sim.save_txt=True
#param_sim.plot_synapse=True
#param_sim.plot_calcium=False
param_sim.plotcomps = param_sim.plotcomps#+['p0b1','p0b1b1','p0b1b1_a']
#soma:13 um diam
#p0b1:16 um away
#p0b1b1:46 um (additional 30 um)
#p0b1b1_x:76 um (additional 30 um)


# this is only needed if adding short term plasticity to synapse
from moose_nerp import ep_net as net
if presyn=='str' and model.stpYN:
    stp_params=net.param_net.str_plas
elif presyn=='GPe' and model.stpYN:
    stp_params=net.param_net.GPe_plas
else:
    print('########### unknown synapse type:', presyn)

param_sim.fname='ep'+stimtype+presyn+'_freq'+str(stimfreq)+'_plas'+str(1 if model.stpYN else 0)+'_inj'+str(param_sim.injection_current[0])
print('>>>>>>>>>> moose_main, protocol {} presyn {} stpYN {}'.format(model.param_sim.stim_paradigm,presyn,model.stpYN))

# This function creates the neuron(s) in Moose:
create_model_sim.setupNeurons(model)

# This function sets up the Output options, e.g. saving, graph tables, etc.
create_model_sim.setupOutput(model)

# This function sets up the stimulation in Moose, e.g. pulsegen for current
# injection or synaptic stimulation:
create_model_sim.setupStim(model)
#additional current injection, e.g. if an offset current is desired
if not np.all([inj==0 for inj in param_sim.injection_current]):
    neuron_pop = {ntype:[neur.path] for ntype, neur in model.neurons.items()}
    pg=inject_func.setupinj(model, param_sim.injection_delay,param_sim.injection_width,neuron_pop)
    pg.firstLevel = param_sim.injection_current[0]
    
#add short term plasticity to synapse as appropriate
if model.param_stim.Stimulation.Paradigm.name.startswith('PSP'):
    from moose_nerp.prototypes import plasticity_test as plas_test
    syntab={ntype:[] for ntype in  model.neurons.keys()}
    plastabset={ntype:[] for ntype in  model.neurons.keys()}
    param_dict={'syn':presyn,'freq':stimfreq,'plas':model.stpYN,'inj':param_sim.injection_current,'simtime':param_sim.simtime}
    for ntype in model.neurons.keys():
        for tt_syn_tuple in model.tuples[ntype].values():
            if model.stpYN:
                syntab[ntype],plastabset[ntype]=plas_test.short_term_plasticity_test(tt_syn_tuple,syn_delay=0,
                                                                       simdt=model.param_sim.simdt,stp_params=stp_params)
            else:
                syntab[ntype]=plas_test.short_term_plasticity_test(tt_syn_tuple,syn_delay=0)
        param_dict[ntype]={'syn_tt': [(k,tt[0].vector) for k,tt in model.tuples[ntype].items()]}

# This function runs all the specified simulations, plotting and saving them
# as specified:
create_model_sim.runAll(model,printParams=True)

# Alternative function to create_model_sim.runAll, that runs a simulation a few
# steps at a time and then updates a plot, to show the live simulation results.
# This is an example of modifying, expanding, or customizing code:
#   `create_model_sim.stepRunPlot(model)`

# Note that customizations should be added to 'create_model_sim' to make them
# available to any model, by adding new functions or expanding existing functions
# with new options that do not alter the current state of the functions unless
# the new options are explicitly called.

# There is also a convenience function, `create_model_sim.setupAll(model)` that
# would sequentially call the above four functions: setupOptions, setupNeurons,
# setupOutput, and setupStim
#That function does not include adding short term plasticity

###################### Analysis ##############################
#Extract spike times and calculate ISI if spikes occur
import numpy as np
import ISI_anal
#stim_spikes are spikes that occur during stimulation - they prevent correct psp_amp calculation
spike_time,isis=ISI_anal.spike_isi_from_vm(model.vmtab,param_sim.simtime)
if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
    if model.param_sim.save_txt:
        np.savez(param_sim.fname,spike_time=spike_time,isi=isis,params=param_dict)
psp_norm=None
if model.param_stim.Stimulation.Paradigm.name.startswith('PSP'):
    stim_spikes=ISI_anal.stim_spikes(spike_time,model.tt)
    if not np.all([len(st) for tabset in stim_spikes.values() for st in tabset]):
        #Extract amplitude of PSPs based on knowledge of spike time if no spikes during stimulation
        psp_amp,psp_norm=ISI_anal.psp_amp(model.vmtab,model.tt)
        if model.param_sim.save_txt:
            np.savez(param_sim.fname,amp=psp_amp,norm=psp_norm,params=param_dict)

########################## Plotting results ##############################
#plot plasticity and synaptic response
from matplotlib import pyplot as plt
plt.ion()
if psp_norm:
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
 
''' 
ToDo:
1. update this chart
2. fix inject protocol and handling of overrides

          tau decay = 20ms               Lavian       tau decay = 10 ms
              str      GPe,tau=1s  tau=0.6s  GPe    Str    str   GPe (tau=0.6s)
initial PSP   0.4 mV   1.5 mV       1.5       3     1.5   
1 Hz                                          0.9   1.0
5Hz           1.6      0.75         0.83      0.75  2.6    1.6    0.83
10Hz          2.0      0.65         0.72      0.65  3.5    2.1    0.72
20Hz          1.2      0.3          0.43      0.55  2.5    2.2    0.49
40Hz          0.2                   0.14      0.3   1.5    0.41   0.2

Str depression with higher freq due to membrane time constant
GABA inputs should have fast and slow decay components

Traces in Lavian reveal that str decay gets _faster_ with higher frequencies, 
so decay between pulses does not decrease drastically
Lower membrane time constant with higher tau decay may work better

Assessment during firing:
a. STN input to produce firing (using lognormal time tables
add in regular GPe or STR input and measure change in ISI

b. STN, GPe and str log normal inputs
compare with and without plasticity
'''
