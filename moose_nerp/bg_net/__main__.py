# -*- coding:utf-8 -*-

######## bg_net/__main__.py ############
"""
Model of entire basal ganglia
Loads in all neuron modules and all network modules
Adds in connections between network modules
"""
from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt
plt.ion()

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

#names of additional neuron modules to import
neuron_modules=['ep_1comp','proto154_1compNoCal','Npas2005_1compNoCal','arky140_1compNoCal','FSI01Aug2014']
### By importing network modules, no need to repeat all the information in param_net.py
net_modules=['moose_nerp.ep_net','moose_nerp.gp_net', 'moose_nerp.spn1_net']

#only save vm trace from save_num neurons of each type if there are more than too_many_neurons
too_many_neurons=30
save_num=2

#additional, optional parameter overrides specified from with python terminal
model.synYN = True
net.single=False
outdir="bg_net/"
create_model_sim.setupOptions(model)
param_sim = model.param_sim
param_sim.injection_current = [-20e-12]
net.num_inject=0
param_sim.injection_width=0.3
param_sim.injection_delay=0.2
param_sim.save_txt = True
param_sim.simtime=0.5

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
population,connections,plas=create_network.create_network(model, net, model.neurons,network_list=net_modules)
#print(net.connect_dict)
print('populations created and connected!!!',population['pop'],'\n',population['netnames'])
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
net_sim_graph.sim_plot(model,net,connections,population)

##### extract spikes and save information
from moose_nerp import ISI_anal
spike_time,isis=ISI_anal.spike_isi_from_vm(model.vmtab,model.param_sim.simtime,soma=model.param_cond.NAME_SOMA)
for neurtype in isis:
    if len(isis):
        print(neurtype,': mean rate of ',np.nanmean([len(st) for st in spike_time[neurtype]])/param_sim.simtime,'from', len(spike_time[neurtype]),'neurons')
    else:
        print(neurtype,': no neurons')

if model.param_sim.save_txt:
    total_neurons=np.sum([len(pop) for pop in population['pop'].values()])
    if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
        np.savez(outdir+net.outfile,spike_time=spike_time,isi=isis)
    elif total_neurons<too_many_neurons:
        print('no spikes for',param_sim.fname, 'saving vm and parameters')
        vmout={ntype:[tab.vector for tab in tabset] for ntype,tabset in model.vmtab.items()}
        np.savez(outdir+net.outfile,vm=vmout)
    else:
        print('no spikes for',param_sim.fname,'and too many neurons. Saving vm for',save_num,' neurons of each population')
        vmout={ntype:[tab.vector for tab in tabset[0:save_num]] for ntype,tabset in model.vmtab.items()}

''' 
1. adjust connection strength to achieve in vivo like firing rates.  

2. Use oscillatory or ramp inputs (inhomogeneous Poisson) READY
      Ctx to STN, go: 2 Hz background, 30 Hz for 50 ms (e.g. starting at 1 sec)
                stop: 2 hz background, 50 Hz for 50 ms starting 200 ms after go signal
      Ctx to Str: fast and slow ramps.  16hz for ramp, 14 hz for ramp plateau
                  oscillations (for upstates): 6 hz for peak rate

3. simulate larger network - with and without GPe feedback - change grid size in param net?
      str: 2790 - 48% D1,D2, 4% FSI  - 300um2 gives 144 neurons; 500um2 gives 400 neurons; 1000um2 gives 1600 neurons
      GPi: 46 - 6% proto, 25% Npas, 15% lhx6 - 300 um2 gives 49 neurons
      EP: 29 - 300um2 gives 25 neurons 

NEXT:
4. adjust connections and train frequency for reasonable firing rates (using oscillatory trains or exp)
5. Then, try countermanding task!!! using ramps and pulses
6. Test effect of GPe feedback to striatum on EP response with fast or slow Ctx ramps
Talk to Karina about 

remaining issues
1. model.param_cond.NAME_SOMA needs to be dictionary, to allow different soma names for different neurons
2. possibly injection current could be different for different networks
3. network['location'] is now a dictionary of lists, instead of just a list; BUT, this is not used, so OK
4. cond_delay and min_delay are the same for all networks
5. change grid size (i.e., population size) from bg_net/param_net, instead of network modules
'''
    
