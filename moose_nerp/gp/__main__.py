# -*- coding:utf-8 -*-
#1. repeat optimizations with fixed Buffer Capacity.  
#2. use helpers to copy parameters into param_cond
#3. run single neuron simulations to verify
#4. run network simulations (single = True, then False) with and without ethanol - prelim
####################
## Code to create two globus pallidus neurons
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional
##      used to tune parameters and channel kinetics (but using larger morphology)

from __future__ import print_function, division
import logging

import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from pprint import pprint
import moose 

from moose_nerp.prototypes import (create_model_sim,
                                   cell_proto,
                                   calcium,
                                   clocks,
                                   inject_func,
                                   tables,
                                   plasticity_test,
                                   logutil,
                                   util,
                                   standard_options,
                                   constants)
from moose_nerp import gp as model
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph
from moose_nerp.prototypes import print_params

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#set-up option parser with overrides specified from with python terminal
#no default_x specs are needed if running from unix terminal
option_parser = standard_options.standard_options(
      default_injection_current=[0e-12,-200e-12],
      default_simulation_time=1.01,
      default_injection_width=1.0,
      default_injection_delay=0.047,
      default_plotdt=0.0001)
param_sim = option_parser.parse_args()

#additional, optional parameter overrides specified from with python terminal
param_sim.save=0
param_sim.plot_channels=0

#list of size >=1 is required for plotcomps
plotcomps=[model.param_cond.NAME_SOMA]

######## required for all simulations: adjust the model settings if specified by command-line options and retain model defaults otherwise
model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)

#default file name is obtained from stimulation parameters
fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]+'.npz'

############## required for all simulations: create the model, set up stimulation and basic output

syn,neuron,writer,outtables=create_model_sim.create_model_sim(model,fname,param_sim,plotcomps)

####### Set up stimulation - could be current injection or synaptic
neuron_paths = {ntype:[neur.path] for ntype, neur in neuron.items()}

pg,param_sim=inject_func.setup_stim(model,param_sim,neuron_paths)

############# Optionally, some additional output ##############
if log.logger.level==logging.DEBUG:
    for neur in neuron.keys():
        print_params.print_elem_params(model,neur,param_sim)

if param_sim.plot_channels:
    for chan in model.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      model.VMIN, model.VMAX, model.CAMIN, model.CAMAX)

# create spikegens to detect and spike tables to count spikes
spiketab=tables.spiketables(neuron,model.param_cond)

if model.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(model,neuron,plotcomps)
else:
    spinevmtab=[]

########### Actually run the simulation: customize as desired
def run_simulation( simtime,injection_current=None):
    if model.param_stim.Stimulation.Paradigm.name == 'inject':
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

vmtab, catab, plastab, currtab=outtables
traces, names = [], []
value = {}
label = {}
calcium_traces=[]
for inj in param_sim.injection_current:
    run_simulation(injection_current=inj, simtime=param_sim.simtime)
    if param_sim.plot_vm:
        neuron_graph.graphs(model, vmtab, param_sim.plot_current, param_sim.simtime,
                        currtab,param_sim.plot_current_label, catab, plastab)
    for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
        #
        if param_sim.plot_current:
            for channame in model.Channels.keys():
                key =  neurtype+'_'+channame
                print(channame,key)
                value[key] = currtab[neurtype][channame][0].vector
                label[key] = '{} @ {}'.format(neurtype, channame)
        traces.append(vmtab[neurnum][0].vector)
        #traces.append(vmtab[neurnum][2].vector)
        if model.calYN and param_sim.plot_calcium:
            calcium_traces.append(catab[neurnum][0].vector)
            #calcium_traces.append(catab[neurnum][2].vector)
        names.append('c0{} @ {}'.format(neurtype, inj))
        #names.append('c1{} @ {}'.format(neurtype, inj))

    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(model,spinecatab,spinevmtab, param_sim.simtime)

if param_sim.plot_vm:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    if model.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(calcium_traces,names,param_sim.simtime, title='Ca')

# block in non-interactive mode
util.block_if_noninteractive()

for st in spiketab:
      print("number of spikes", st.path, ' = ',len(st.vector))

#dat=pickle.load(open('params.pickle','rb'))
'''dat=np.load('/tmp/fitgp-arky-tmp_arky1202938/tmpwp_8zpqg/ivdata--2e-10.npy','r')
simtime=2.0
ts=np.arange(0,simtime,simtime/(len(dat)-1))
plt.plot(ts[0:6000],dat[0:6000])
'''
