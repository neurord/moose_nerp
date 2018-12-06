# -*- coding:utf-8 -*-

########  ############
## Code to create entopeduncular neuron
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
from moose_nerp import ep as model
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

option_parser = standard_options.standard_options(
    default_injection_current=[100e-12],
    default_simulation_time=0.55,
    default_injection_width=0.3,
    default_injection_delay=0.15,
    default_plotdt=0.0001)

param_sim = option_parser.parse_args()
param_sim.hsolve=1
param_sim.plot_channels=1
param_sim.plot_current=1
plotgate='NaS' #plot X, Y, Z values vs time for this channel
plotcomps=[model.param_cond.NAME_SOMA]

####### required for all simulations: adjust the model settings if specified by command-line options and retain model defaults otherwise
model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)

#default file name is obtained from stimulation parameters
fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]

############## required for all simulations: create the model, set up stimulation and basic output

syn,neuron,writer,outtables=create_model_sim.create_model_sim(model,fname,param_sim,plotcomps)
vmtab, catab, plastab, currtab = outtables

####### Set up stimulation - could be current injection or synaptic
neuron_paths = {ntype:[neur.path] for ntype, neur in neuron.items()}

pg,param_sim=inject_func.setup_stim(model,param_sim,neuron_paths)

############# Optionally, some additional output ##############

if param_sim.plot_channels:
    for chan in ['NaS','NaF']:#model.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      model.VMIN, model.VMAX, model.CAMIN, model.CAMAX)

# create spikegens to detect and spike tables to count spikes
spiketab=tables.spiketables(neuron,model.param_cond)

if model.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(model,neuron,plotcomps)
else:
    spinevmtab=[]

gatextab=moose.Table('/data/gatex')
moose.connect(gatextab, 'requestOut', moose.element('/ep/soma/'+plotgate), 'getX')
gateytab=moose.Table('/data/gatey')
moose.connect(gateytab, 'requestOut', moose.element('/ep/soma/'+plotgate), 'getY')
if model.Channels[plotgate][0][2]==1:
    gateztab=moose.Table('/data/gatez')
    moose.connect(gateztab, 'requestOut', moose.element('/ep/soma/'+plotgate), 'getZ')

###########Actually run the simulation
def run_simulation( simtime,injection_current=None):
    if model.param_stim.Stimulation.Paradigm.name == 'inject':
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

traces, names = [], []
calcium_traces=[]
current_traces,curr_names=[],[]

for inj in param_sim.injection_current:
    run_simulation(injection_current=inj, simtime=param_sim.simtime)
    for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
        if param_sim.plot_current:
            for channame in model.Channels.keys():
                current_traces.append(currtab[neurtype][channame][0].vector)
                curr_names.append('{}: {} @ {}'.format(neurtype, channame,inj))
        traces.append(vmtab[neurnum][0].vector)
        if model.calYN and param_sim.plot_calcium:
            calcium_traces.append(catab[neurnum][0].vector)
        names.append('{} @ {}'.format(neurtype, inj))

    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(model,spinecatab,spinevmtab, param_sim.simtime)

if param_sim.plot_vm:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    if model.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(calcium_traces,names,param_sim.simtime, title='Ca')
        
    if param_sim.plot_current:
        num_currents=np.shape(current_traces)[0]//len(param_sim.injection_current)
        neuron_graph.SingleGraphSet(current_traces[-num_currents:], curr_names,param_sim.simtime)
        plt.figure()
        ts = np.linspace(0, param_sim.simtime, len(gatextab.vector))
        plt.suptitle('X,Y,Z gates; hsolve='+str(param_sim.hsolve)+' calYN='+str(model.calYN)+' Zgate='+str(model.Channels[plotgate][0][2]))
        plt.plot(ts,gatextab.vector,label='X')
        plt.plot(ts,gateytab.vector,label='Y')
        if model.Channels[plotgate][0][2]==1:
            plt.plot(ts,gateztab.vector,label='Z')
        plt.legend()

# block in non-interactive mode
util.block_if_noninteractive()

for st in spiketab:
      print("number of spikes", st.path, ' = ',len(st.vector))

from moose_nerp.prototypes import print_params
#print_params.print_elem_params(model,'ep',param_sim)
