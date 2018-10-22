# -*- coding:utf-8 -*-

######## Squid.py ############
## Code to create squid neurons with 2 compartments (SOMA and Dendrite).
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
from moose_nerp import squid as model
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph
from moose_nerp.prototypes.tables import write_textfile
from ajustador.helpers.loggingsystem import getlogger
from moose_nerp.prototypes import print_params
logger = getlogger(__name__)
logger.setLevel(logging.DEBUG)
#handle = logging.StreamHandler()
#handle.setLevel(logging.DEBUG)
#logger.addHandler(handle)
logging.basicConfig(level=logging.DEBUG)
log = logutil.Logger()

#import engineering_notation as eng

option_parser = standard_options.standard_options(
    default_injection_current=[1e-9], #units (Amperes)
    default_simulation_time=200e-3, #units (Seconds) #2 second simulations
    default_injection_width=60e-3, #units (Seconds)  #1 second injection spacing
    default_injection_delay=30e-3, #units (Seconds)  #0.5 second injection start
    default_plotdt=20e-5 #units (Seconds)
    )

param_sim = option_parser.parse_args()
param_sim.hsolve=1
#param_sim.save_vm='/home/Sriramsagar/neural_prj/waves/squid-experimental/squid_trace.npy'
#param_sim.save_vm='/home/Sriramsagar/neural_prj/waves/squid-experimental/squid_trace_tau.npy'
#param_sim.save_vm='/home/Sriramsagar/neural_prj/waves/squid-experimental/squid_trace_tau_z.npy'
param_sim.save='../squid.npz'
param_sim.plot_channels = 0
plotcomps=[model.param_cond.NAME_SOMA]

model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)

fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0] + '.npz'
######## adjust the model settings if specified by command-line options and retain model defaults otherwise
print(fname)
syn, neuron, writer, outtables= create_model_sim.create_model_sim(model,fname,param_sim,plotcomps)
vmtab, catab, plastab, currtab = outtables
neuron_paths = {ntype:[neur.path] for ntype, neur in neuron.items()}
pg,param_sim=inject_func.setup_stim(model,param_sim,neuron_paths)
print('syn:', syn)
print('neuron:', neuron)

if log.logger.level==logging.DEBUG:
    for neur in neuron.keys():
        print_params.print_elem_params(model,neur,param_sim)

#################################-----------create the model
##create neuron prototype, optionally with synapses, calcium, and spines

###############--------------output elements
 #Set 1 to plot_channels else 0.
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

if param_sim.hsolve and model.calYN:
    calcium.fix_calcium(util.neurontypes(model.param_cond), model)

########### Actually run the simulation
def run_simulation( simtime,injection_current=None):
    if model.param_stim.Stimulation.Paradigm.name == 'inject':
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

traces, names, calcium_traces = [], [], []
value = {}
label = {}
for inj in param_sim.injection_current:
    run_simulation(simtime=param_sim.simtime, injection_current=inj)
    if param_sim.plot_vm:
        neuron_graph.graphs(model, vmtab, param_sim.plot_current, param_sim.simtime,
                        currtab,param_sim.plot_current_label, catab, plastab)
    for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
        if param_sim.plot_current:
            for channame in model.Channels.keys():
                key =  neurtype+'_'+channame
                print(channame,key)
                value[key] = currtab[neurtype][channame][0].vector
                label[key] = '{} @ {}'.format(neurtype, channame)
        traces.append(vmtab[neurnum][0].vector)
        if model.calYN and param_sim.plot_calcium:
            calcium_traces.append(catab[neurnum][0].vector)
        names.append('{} @ {}'.format(neurtype, inj))

    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(ep,spinecatab,spinevmtab, param_sim.simtime)

if param_sim.plot_vm:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    if model.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(calcium_traces,names,param_sim.simtime, title='Ca')

import numpy as np
opt_data_seed = np.load('/tmp/Sriramsagarsquid-squid-squid_experimentaltau_z/tmpuc_n6nhc/ivdata-1e-09.npy') #with seed
opt_data_without_seed =np.load('/tmp/Sriramsagarsquid-squid-squid_experimentaltau_z_ns/tmpidjzl3x2/ivdata-1e-09.npy') #without seed

f_dt = 20E-5
#x = np.arange(0+30E-6, 200E-3+30E-6, f_dt) #proto
x_seed = np.linspace(param_sim.plotdt, param_sim.simtime + param_sim.plotdt, len(opt_data_seed))
x_no_seed = np.linspace(param_sim.plotdt, param_sim.simtime + param_sim.plotdt, len(opt_data_seed))

plt.plot(x_seed, opt_data_seed, x_no_seed, opt_data_without_seed)
plt.legend(['sim', 'seed', 'no_seed'])
plt.grid(True)
plt.show()

# Write simulation output to a numpy file.

#np_file_name = write_textfile(tabset=vmtab, tabname='squid', fname= 'squid_trace', inj=1e-9, simtime=param_sim.simtime)
#import pandas as pd
#pd.DataFrame(np.loadtxt(np_file_name)).to_csv(np_file_name.replace('.txt', '.csv'), index=False, header=['Time', *param_sim.injection_current])

# block in non-interactive mode
util.block_if_noninteractive()
