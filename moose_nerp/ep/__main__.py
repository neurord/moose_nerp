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

# This function sets up the options specified in param_sim or passed from
# command line:
create_model_sim.setupOptions(model)
# Parameter overrides can be specified:
param_sim = model.param_sim
param_sim.injection_delay = 0.0
model.synYN = True
model.stpYN = True
param_sim.save_txt=True
param_sim.plot_synapse=True
param_sim.plot_calcium=False

############ Vary the next three parameters to evaluate response to regular synaptic stimulation
param_sim.injection_current = [-1e-12] #choose from [50e012,-50e-12]
syntype='GPe' #choose from 'str', 'GPe'
stimfreq=10 #choose from 1,5,10,20,40

syn_delay=1.0
minpulses=10
import moose
tt=moose.TimeTable('tt'+str(stimfreq)+'hz')
if stimfreq<minpulses:
    param_sim.simtime = syn_delay+minpulses/float(stimfreq)
    tt.vector=[syn_delay+n/float(stimfreq) for n in range(minpulses)]
else:
    param_sim.simtime = syn_delay+1.1
    tt.vector=[syn_delay+n/float(stimfreq) for n in range(stimfreq)]
param_sim.injection_width = param_sim.simtime-param_sim.injection_delay

param_sim.fname='ep_syn'+syntype+'_freq'+str(stimfreq)+'_plas'+str(1 if model.stpYN else 0)
param_dict={'syn':syntype,'freq':stimfreq,'plas':model.stpYN,'inj':param_sim.injection_current}
outfile=param_sim.fname+'_inj'+str(param_sim.injection_current[0])

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

#specify presyn as tt explicitly and test
#This code should be moved to plasticity_test

from moose_nerp.prototypes import plasticity_test as plas_test
from moose_nerp import ep_net as net

if syntype=='str':
    synchan=moose.element('/ep[0]/p0b1b1b2[0]/gaba[0]/')#str synchan
    stp_params=net.param_net.str_plas
elif syntype=='GPe':
    synchan=moose.element('/ep[0]/p0b1[0]/gaba[0]/') #gp synchan
    stp_params=net.param_net.GPe_plas
else:
    print('########### unknown synapse type')

#add short term plasticity to synapse as appropriate
if model.stpYN:
    syntab,plastabset=plas_test.short_term_plasticity_test(synchan,tt,syn_delay=0,
                                                        simdt=model.param_sim.simdt,stp_params=stp_params)
else:
    syntab=plas_test.short_term_plasticity_test(synchan,tt,syn_delay=0)

#simulate the model
create_model_sim.runAll(model,printParams=False)

#plot plasticity and synaptic response
print('*********** freq',stimfreq,'simtime',param_sim.simtime,'tt',tt.vector)
from matplotlib import pyplot as plt
import numpy as np
plt.ion()
plt.figure()
plt.title('synapse')
numpts=len(syntab.vector)
time=np.arange(0,syntab.dt*numpts,syntab.dt)
if model.stpYN:
    if 'dep' in plastabset.keys():
        plt.plot(time[0:numpts],plastabset['dep'].vector,label='dep')
    if 'fac' in plastabset.keys():
        plt.plot(time[0:numpts],plastabset['fac'].vector,label='fac')
    plt.plot(time[0:numpts],plastabset['plas'].vector+0.1,label='plas+0.1')
plt.plot(time[0:numpts],syntab.vector*1e9,label='Gk*1e9')
plt.legend()

#Extract spike times and calculate ISI if not hyperpolarized
import detect
vmtab=model.vmtab
spike_time={key:[] for key in vmtab.keys()}
numspikes={key:[] for key in vmtab.keys()}
isis={key:[] for key in vmtab.keys()}
plt.figure()
plt.title('ISI vs time for '+syntype+' at '+str(stimfreq)+'hz')
plt.xlabel('Time (msec)')
plt.ylabel('ISI (sec)')
for neurtype, tabset in vmtab.items():
    for tab in tabset:
        spike_time[neurtype].append(detect.detect_peaks(tab.vector)*tab.dt)
        isis[neurtype].append(np.diff(spike_time[neurtype][-1]))
        plt.plot(spike_time[neurtype][-1][0:len(isis[neurtype][-1])],isis[neurtype][-1],'o')
    numspikes[neurtype]=[len(st) for st in spike_time[neurtype]]
    print(neurtype,'mean:',np.mean(numspikes[neurtype]),'rate',np.mean(numspikes[neurtype])/param_sim.simtime,'from',numspikes[neurtype], 'spikes, ISI mean&STD: ',[np.mean(isi) for isi in isis[neurtype]], [np.std(isi) for isi in isis[neurtype]] )

spike1=np.min(tt.vector)
spikeN=np.max(tt.vector)
stim_spikes=[st for st in spike_time['ep'][0] if st>spike1 and st<spikeN ]
if len(spike_time['ep'][0]):
    if model.param_sim.save_txt:
        np.savez(outfile,spike_time=spike_time,isi=isis,params=param_dict)
elif not len(stim_spikes):
    #Extract amplitude of PSPs based on knowledge of spike time if no spikes during stimulation
    vmtab=model.vmtab['ep'][0].vector
    vm_init=[vmtab[int(t/vmtab.dt)] for t in tt.vector]
    #use np.min for IPSPs and np.max for EPSPs
    vm_peak=[np.min(vmtab[int(tt.vector[i]/vmtab.dt):int(tt.vector[i+1]/vmtab.dt)]) for i in range(len(tt.vector)-1)]
    psp_amp=[(vm_init[i]-vm_peak[i]) for i in range(len(vm_peak))]
    psp_norm=[amp/psp_amp[0] for amp in psp_amp]
    pulse=range(len(psp_norm))
    plt.figure()
    plt.title('Normalized PSP amp for '+syntype+' at '+str(stimfreq)+'hz')
    plt.plot(pulse,psp_norm,'o')
    plt.xlabel('stim number')
    ##save vmtab, psp_amp, psp_norm, spike_time, isi so can plot the entire set of frequencies
    if model.param_sim.save_txt:
        np.savez(outfile,amp=psp_amp,norm=psp_norm,params=param_dict)
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

Perhaps get Dan's help in adding frequency parameters to command line changes

#Analyze set of files
import glob
import numpy as np

syntype='GPe'
plasYN=1
inj='-1e-10'
pattern='ep_syn'+syntype+'*_plas'+str(plasYN)+'_inj'+inj+'*.npz'
files=glob.glob(pattern)
results={}
time={}
for fname in files:
    dat=np.load(fname,'r')
    params=dat['params'].item()
    if float(inj)<0:
        results[params['freq']]=dat['norm']#.item()['ep'][0]
        time[params['freq']]=range(len(dat['norm']))
        ylabel='normalized PSP amp'
        xlabel='pulse'
    if float(inj)>=0:
        results[params['freq']]=dat['isi'].item()['ep'][0]
        time[params['freq']]=dat['spike_time'].item()['ep'][0]
        ylabel='isi (msec)'
        xlabel='time (msec)'

#plot the set of results:
from matplotlib import pyplot as plt
plt.ion()
plt.figure()
for freq in sorted(results.keys()):
    plt.plot(time[freq][0:len(results[freq])],results[freq],label=str(freq))

plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.legend()
'''
'''
Assessment during firing:
a. STN input to produce firing (using lognormal time tables
add in regular GPe or STR input and measure change in ISI

b. STN, GPe and str log normal inputs
compare with and without plasticity
'''
