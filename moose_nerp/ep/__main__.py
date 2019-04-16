# -*- coding:utf-8 -*-

########  ############
## Code to create entopeduncular neuron
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional
##      used to tune parameters and channel kinetics (but using larger morphology)

from __future__ import print_function, division
from moose_nerp import ep as model
'''Evaluates moose_nerp/ca1/__init__.py to load all the parameters, e.g.
param_sim.py, param_ca_plas.py, param_chan.py, param_cond.py, param_sim.py, etc.
into the model namespace. These parameters are then accessible by, e.g.,
`model.param_sim.fname`.
'''

from moose_nerp.prototypes import create_model_sim
'''Imports functions for setting up and simulating model. These take the `model`
namespace as argument, and append variables to this namespace. Thus, after
running a simulation, the output tables would be accessible as model.vmtab,
model.catab, etc.'''

model.synYN = True
model.stpYN = True
presyn='GPe' #choose from 'str', 'GPe'
stimfreq=20 #choose from 1,5,10,20,40
model.param_sim.stim_paradigm='PSP_'+str(stimfreq)+'Hz'

# This function sets up the options specified in param_sim or passed from
# command line:
create_model_sim.setupOptions(model)

# Parameter overrides can be specified:
param_sim = model.param_sim
param_sim.injection_current = [0e-12] #offset to prevent or enhance firing
param_sim.injection_delay = 0.0
param_sim.save_txt=False
param_sim.plot_synapse=True
param_sim.plot_calcium=False

#
from moose_nerp import ep_net as net
if presyn=='str':
    stp_params=net.param_net.str_plas
elif presyn=='GPe':
    stp_params=net.param_net.GPe_plas
else:
    print('########### unknown synapse type')

param_sim.fname='ep_syn'+presyn+'_freq'+str(stimfreq)+'_plas'+str(1 if model.stpYN else 0)+'_inj'+str(param_sim.injection_current[0])
print('>>>>>>>>>> moose_main, stimfreq {} presyn {} stpYN {}'.format(stimfreq,presyn,model.stpYN))

# This function creates the neuron(s) in Moose:
create_model_sim.setupNeurons(model)

# This function sets up the Output options, e.g. saving, graph tables, etc.
create_model_sim.setupOutput(model)

# This function sets up the stimulation in Moose, e.g. pulsegen for current
# injection or synaptic stimulation:
create_model_sim.setupStim(model)

# There is also a convenience function, `create_model_sim.setupAll(model)` that
# would sequentially call the above four functions: setupOptions, setupNeurons,
# setupOutput, and setupStim

# This function runs all the specified simulations, plotting and saving them
# as specified:
#create_model_sim.runAll(model,printParams=False)
# Alternative function to create_model_sim.runAll, that runs a simulation a few
# steps at a time and then updates a plot, to show the live simulation results.
# This is an example of modifying, expanding, or customizing code:
#   `create_model_sim.stepRunPlot(model)`

# Note that customizations should be added to 'create_model_sim' to make them
# available to any model, by adding new functions or expanding existing functions
# with new options that do not alter the current state of the functions unless
# the new options are explicitly called.

#add short term plasticity to synapse as appropriate
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

#simulate the model
create_model_sim.runAll(model,printParams=True)
print('<<<<<<<<<<< sim finished: freq',stimfreq,'simtime',param_sim.simtime,'tt',tt_syn_tuple[0].vector)

#Extract spike times and calculate ISI if spikes occur
import numpy as np
import ISI_anal
#stim_spikes are spikes that occur during stimulation - they prevent correct psp_amp calculation
spike_time,isis=ISI_anal.spike_isi_from_vm(model.vmtab,param_sim.simtime)
stim_spikes=ISI_anal.stim_spikes(spike_time,model.tt)

if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
    if model.param_sim.save_txt:
        np.savez(param_sim.fname,spike_time=spike_time,isi=isis,params=param_dict)
if not np.all([len(st) for tabset in stim_spikes.values() for st in tabset]):
    #Extract amplitude of PSPs based on knowledge of spike time if no spikes during stimulation
    psp_amp,psp_norm=ISI_anal.psp_amp(model.vmtab,model.tt)
    if model.param_sim.save_txt:
        np.savez(param_sim.fname,amp=psp_amp,norm=psp_norm,params=param_dict)
else:
    psp_norm=None

########################## Plotting results ##############################
#plot plasticity and synaptic response
from matplotlib import pyplot as plt
plt.ion()
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
 
'''           tau decay = 20ms               Lavian       tau decay = 10 ms
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
