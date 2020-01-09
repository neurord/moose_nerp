# -*- coding:utf-8 -*-

######## GPnetSim.py ############
"""\
Create a network of GP neurons using dictionaries for channels, synapses, and network parameters

Can use ghk for calcium permeable channels if ghkYesNo=1
Optional calcium concentration in compartments (calcium=1)
Optional synaptic plasticity based on calcium (plasyesno=1)
Spines are optional (spineYesNo=1), but not allowed for network
The graphs won't work for multiple spines per compartment
"""
from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt
plt.ion()

import moose
import importlib
from moose_nerp.prototypes import (create_model_sim,
                                   cell_proto,
                                   calcium,
                                   clocks,
                                   inject_func,
                                   create_network,
                                   tables,
                                   net_output,
                                   logutil,
                                   util,
                                   multi_module,
                                   net_sim_graph)
from moose_nerp import proto154_1compNoCal as model
from moose_nerp import gp_net as net

#names of additional neuron modules to import
neuron_modules=['arky140_1compNoCal','Npas2005_1compNoCal']

#additional, optional parameter overrides specified from with python terminal
model.synYN = True
model.stpYN = True
model.calYN = False
model.spinYN = False
net.single=False

###alcohol injection--> Bk channel constant multiplier
'''alcohol = 1#2.5
ampa_wt=1.0#0.7
gaba_wt=1.0#0.8
for neurtype in model.param_cond.Condset:
    for key in model.param_cond.Condset[neurtype]['BKCa']:
        model.param_cond.Condset[neurtype]['BKCa'][key]=alcohol*model.param_cond.Condset[neurtype]['BKCa'][key]
    #AMPA PART
    net.connect_dict[neurtype]['ampa']['extern'].weight=ampa_wt
    ampa_fname='all'+str(net.connect_dict[neurtype]['ampa']['extern'].weight)
    #GABA: change all:
    for presyn in net.connect_dict[neurtype]['gaba'].keys():
        net.connect_dict[neurtype]['gaba'][presyn].weight=gaba_wt
        gaba_fname='all'+str(net.connect_dict[neurtype]['gaba'][presyn].weight)
#GABA; change proto only

neurtype='proto';presyn='proto'
net.connect_dict[neurtype]['gaba'][presyn].weight=gaba_wt
gaba_fname='gabaproto'+str(net.connect_dict[neurtype]['gaba'][presyn].weight)

#gaba_fname='0'
net.outfile = 'alcohol'+str(alcohol)+'_gaba'+gaba_fname+'_ampa'+ampa_fname
outdir="gp_net/output/"
print('************ Output file name ***************', net.outfile)
'''
create_model_sim.setupOptions(model)
param_sim = model.param_sim
param_sim.injection_current = [0e-12]
param_sim.save_txt = False
param_sim.simtime=0.5
net.num_inject = 0
if net.num_inject==0:
    param_sim.injection_current=[0]

#################################-----------create the model: neurons, and synaptic inputs
#### Do not setup hsolve yet, since there may be additional neuron_modules
model=create_model_sim.setupNeurons(model,network=True)
#create dictionary of BufferCapacityDensity - only needed if hsolve, simple calcium dynamics
buf_cap={neur:model.param_ca_plas.BufferCapacityDensity for neur in model.neurons.keys()}

#import additional neuron modules, add them to neurons and synapses
######## this is skipped if neuron_modules is empty
if len(neuron_modules):
    buf_cap=multi_module.multi_modules(neuron_modules,model,buf_cap)
population,connections,plas=create_network.create_network(model, net, model.neurons)

####### Set up stimulation - could be current injection or plasticity protocol
# set num_inject=0 to avoid current injection
if net.num_inject<np.inf :
    model.inject_pop=inject_func.inject_pop(population['pop'],net.num_inject)
    if net.num_inject==0:
        param_sim.injection_current=[0]
else:
    model.inject_pop=population['pop']

create_model_sim.setupStim(model)

##############--------------output elements and simulation method----------########
if net.single:
    #fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]+'.npz'
    #simpath used to set-up simulation dt and hsolver
    simpath=['/'+neurotype for neurotype in model.neurons.keys()]
    create_model_sim.setupOutput(model)
else:   #population of neurons
    model.spiketab,model.vmtab,model.plastab,model.catab=net_output.SpikeTables(model, population['pop'], net.plot_netvm, plas, net.plots_per_neur)
    #simpath used to set-up simulation dt and hsolver
    simpath=[net.netname]

#### Set up hsolve and fix calcium
clocks.assign_clocks(simpath, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)
# Fix calculation of B parameter in CaConc if using hsolve
######### Need to use CaPlasticityParams.BufferCapacityDensity from EACH neuron_module
if model.param_sim.hsolve and model.calYN:
    calcium.fix_calcium(model.neurons.keys(), model,buf_cap)

if model.synYN and (param_sim.plot_synapse or net.single):
    #overwrite plastab above, since it is empty
    model.syntab, model.plastab, model.stp_tab=tables.syn_plastabs(connections,model)

################### Actually run the simulation and produce graphs
net_sim_graph.sim_plot(model,net,connections,population)

import ISI_anal
spike_time,isis=ISI_anal.spike_isi_from_vm(model.vmtab,param_sim.simtime,soma=model.param_cond.NAME_SOMA)

if model.param_sim.save_txt:
    vmout={ntype:[tab.vector for tab in tabset] for ntype,tabset in model.vmtab.items()}
    if np.any([len(st) for tabset in spike_time.values() for st in tabset]):
        np.savez(outdir+net.outfile,spike_time=spike_time,isi=isis,vm=vmout)
    else:
        print('no spikes for',param_sim.fname, 'saving vm and parameters')
        np.savez(outdir+net.outfile,vm=vmout)
#spikes=[st.vector for tabset in model.spiketab for st in tabset]    


'''
Fix netgraph to use dictionaries - similar to neuron graph
check on ep synaptic strength - do simulations
commit everything
send summary to Alon

#plot data
import numpy as np
import matplotlib.pyplot as plt
plt.ion()
alldata=np.load('gp_out0.0.npz','r')
vmdata=alldata['vm'][()] OR alldata['vm'].item()
plt.figure()
simtime=0.2
numpoints=len(vmdata['proto']['0'])
ts=np.linspace(0,simtime,numpoints)
for cell,data in vmdata['proto'].items():
  plt.plot(ts,data,label=cell)

plt.legend()

#examine connections
import numpy as np
data=np.load('gp_connect.npz')
conns=data['conn'].item()
for neurtype,neurdict in conns.items():
  for cell in neurdict.keys():
     for pre,post in neurdict[cell]['gaba'].items():
        print(cell,pre,post)
'''
