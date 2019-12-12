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
from moose_nerp.prototypes import (calcium,
                                   cell_proto,
                                   create_model_sim,
                                   clocks,
                                   inject_func,
                                   create_network,
                                   tables,
                                   net_output,
                                   util)
from moose_nerp import proto144 as model
from moose_nerp import gp_net as net
from moose_nerp.graph import net_graph, neuron_graph, spine_graph

#names of additional neuron modules to import
neuron_modules=['Npas2006']

#additional, optional parameter overrides specified from with python terminal
model.synYN = True
model.stpYN = True
net.single=False

###alcohol injection--> Bk channel constant multiplier
alcohol = 1#2.5
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
'''
neurtype='proto';presyn='proto'
net.connect_dict[neurtype]['gaba'][presyn].weight=gaba_wt
gaba_fname='gabaproto'+str(net.connect_dict[neurtype]['gaba'][presyn].weight)
'''
#gaba_fname='0'
net.outfile = 'alcohol'+str(alcohol)+'_gaba'+gaba_fname+'_ampa'+ampa_fname
outdir="gp_net/output/"
print('************ Output file name ***************', net.outfile)

create_model_sim.setupOptions(model)
param_sim = model.param_sim
param_sim.injection_current = [-50e-12]
param_sim.save_txt = False
param_sim.simtime=0.5

#################################-----------create the model: neurons, and synaptic inputs
#### Do not setup hsolve yet, since there may be additional neuron_modules
model=create_model_sim.setupNeurons(model,network=True)
#create dictionary of BufferCapacityDensity - only needed if hsolve, simple calcium dynamics
if param_sim.hsolve and model.calYN:
    buf_cap={neur:model.param_ca_plas.BufferCapacityDensity for neur in model.neurons.keys()}

#import additional neuron modules, add them to neurons and synapses
for neur_module in neuron_modules:
    nm=importlib.import_module(neur_module)
    #probably a good idea to give synapses to all neurons (or no neurons)
    nm.synYN = model.synYN
    nm.param_cond.neurontypes = util.neurontypes(nm.param_cond)
    syn,neur=cell_proto.neuronclasses(nm)
    for new_neur in neur.keys():
        model.syn[new_neur]=syn[new_neur]
        model.neurons[new_neur]=neur[new_neur]
        buf_cap[new_neur]=nm.param_ca_plas.BufferCapacityDensity
        model.param_syn.NumSyn[new_neur]=nm.param_syn.NumSyn[new_neur]
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
    simpath=['/'+neurotype for neurotype in model.neurons.keys()]
    #fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]+'.npz'
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

################### Actually run the simulation
traces, names = [], []
for inj in param_sim.injection_current:
    create_model_sim.runOneSim(model, simtime=model.param_sim.simtime, injection_current=inj)
    if net.single and len(model.vmtab):
        for neurnum,neurtype in enumerate(model.neurons.keys()):
            traces.append(model.vmtab[neurtype][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
        if model.synYN:
            net_graph.syn_graph(connections, model.syntab, param_sim)
        if model.spineYN:
            spine_graph.spineFig(model,model.spinecatab,model.spinevmtab, param_sim.simtime)
    else:
        if net.plot_netvm:
            net_graph.graphs(population['pop'], param_sim.simtime, model.vmtab,model.catab,model.plastab)
        if model.synYN and param_sim.plot_synapse:
            net_graph.syn_graph(connections, model.syntab, param_sim)
            if model.stpYN:
                net_graph.syn_graph(connections, model.stp_tab,param_sim,graph_title='stp',factor=1)
        #net_output.writeOutput(model, net.outfile,model.spiketab,model.vmtab,population)

if net.single:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    # block in non-interactive mode
util.block_if_noninteractive()

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
