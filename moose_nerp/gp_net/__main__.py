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

from moose_nerp.prototypes import (calcium,
                                   create_model_sim,
                                   clocks,
                                   inject_func,
                                   create_network,
                                   tables,
                                   net_output,
                                   util)
from moose_nerp import gp as model
from moose_nerp import gp_net as net
from moose_nerp.graph import net_graph, neuron_graph, spine_graph

#additional, optional parameter overrides specified from with python terminal
model.synYN = True
model.stpYN = True
net.single=False

###alcohol injection--> Bk channel constant multiplier
alcohol = 1#2.5
for neurtype in model.param_cond.Condset:
    for key in model.param_cond.Condset[neurtype]['BKCa']:
        model.param_cond.Condset[neurtype]['BKCa'][key]=alcohol*model.param_cond.Condset[neurtype]['BKCa'][key]
if alcohol > 1:
    model.net.outfile = 'alcohol'+str(alcohol)

create_model_sim.setupOptions(model)
param_sim = model.param_sim
param_sim.injection_current = [-0e-12]
param_sim.save_txt = True
#param_sim.simtime=0.001

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

create_model_sim.setupStim(model)

##############--------------output elements
if net.single:
    #fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]+'.npz'
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

################### Actually run the simulation
traces, names = [], []
for inj in param_sim.injection_current:
    create_model_sim.runOneSim(model, simtime=model.param_sim.simtime, injection_current=inj)
    if net.single and len(model.vmtab):
        for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
            traces.append(model.vmtab[neurtype][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
        if model.synYN:
            net_graph.syn_graph(connections, syntab, param_sim)
        if model.spineYN:
            spine_graph.spineFig(model,model.spinecatab,model.spinevmtab, param_sim.simtime)
    else:
        if net.plot_netvm:
            net_graph.graphs(population['pop'], param_sim.simtime, vmtab,catab,plastab)
        if model.synYN and param_sim.plot_synapse:
            net_graph.syn_graph(connections, syntab, param_sim)
            if model.stpYN:
                net_graph.syn_graph(connections, stp_tab,param_sim,graph_title='stp',factor=1)
        outfname=net.outfile+str(inj)+'gaba'+str(model.param_syn.SYNAPSE_TYPES.gaba.Gbar)    
        net_output.writeOutput(model, outfname,spiketab,vmtab,population)

if net.single:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    # block in non-interactive mode
util.block_if_noninteractive()

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
