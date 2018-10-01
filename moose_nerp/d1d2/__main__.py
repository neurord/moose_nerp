# -*- coding:utf-8 -*-

######## SPneuronSim.py ############
## Code to create two SP neuron classes 
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
from moose_nerp import d1d2 as model
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#two examples of calling option_parser - one overrides the defaults and is useful when running from python window
#option_parser = standard_options.standard_options()
option_parser = standard_options.standard_options(
      default_injection_current=[-0.2e-9,0.26e-9],
      default_stim='inject',
      default_stim_loc='soma')
param_sim = option_parser.parse_args()

#additional, optional parameter overrides specified from with python terminal
param_sim.save=0
param_sim.plot_channels=0

#list of size >=1 is required for plotcomps
plotcomps=[model.param_cond.NAME_SOMA]

######## required for all simulations: adjust the model settings if specified by command-line options and retain model defaults otherwise
model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)

#default file name is obtained from stimulation parameters
fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]


############# required for all simulations: create the model, set up stimulation and basic output

syn,neuron,pg,param_sim,writer,vmtab, catab, plastab, currtab=create_model_sim.create_model_sim(model,fname,param_sim,plotcomps)

############# Optionally, some additional output ##############

if param_sim.plot_channels:
    for chan in model.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      model.VMIN, model.VMAX, model.CAMIN, model.CAMAX)

if model.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(model,neuron,plotcomps)
else:
    spinevmtab=[]

###########Actually run the simulation
def run_simulation( simtime,injection_current=None):
    if model.param_stim.Stimulation.Paradigm.name == 'inject':
        print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

traces, names, catraces = [], [], []
for inj in param_sim.injection_current:
    run_simulation(simtime=param_sim.simtime,injection_current=inj)
    if param_sim.plot_vm:
        neuron_graph.graphs(model, vmtab, param_sim.plot_current, param_sim.simtime,
                        currtab, param_sim.plot_current_label,
                        catab, plastab)
    #set up tables that accumulate soma traces for multiple simulations
    for neurnum,neurtype in enumerate(util.neurontypes(model.param_cond)):
        traces.append(vmtab[neurnum][0].vector)
        if model.calYN and param_sim.plot_calcium:
            catraces.append(catab[neurnum][0].vector)
        names.append('{} @ {}'.format(neurtype, inj))
        # In Python3.6, the following syntax works:
        #names.append(f'{neurtype} @ {inj}')
    #plot spines
    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(model,spinecatab,spinevmtab, param_sim.simtime)
    #save output - expand this to optionally save current data
    if param_sim.save:
        inj_nA=inj*1e9
        tables.write_textfile(vmtab,'Vm', fname,inj_nA,param_sim.simtime)
        if model.calYN:
            tables.write_textfile(catab,'Ca', fname,inj_nA,param_sim.simtime)
        if model.spineYN and len(spinevmtab):
            tables.write_textfile(list(spinevmtab.values()),'SpVm', fname,inj_nA,param_sim.simtime)
            if model.spineYN and len(spinecatab):
                tables.write_textfile(list(spinecatab.values()),'SpCa', fname,inj_nA,param_sim.simtime)
if param_sim.plot_vm:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    if model.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(catraces, names, param_sim.simtime)

'''dat=np.load('/tmp/fitd1d2-D1-tmp_non05Jan2015_SLH00462938/tmpu3y709a8/ivdata-2.6e-10.npy','r')
ts=np.arange(0,0.8,0.0002)
plt.plot(ts[0:3500],dat[500:4000])
'''
# block in non-interactive mode
util.block_if_noninteractive()

#may need to eliminate parameter_overrides for Cal, Syn, etc - to prevent ajustador - moose_nerp differences
