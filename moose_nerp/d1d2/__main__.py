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

from moose_nerp.prototypes import (cell_proto,
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

#two examples of calling option_parser - one overrides the defaults and is useful when running from python window
option_parser = standard_options.standard_options()
option_parser = standard_options.standard_options(default_calcium=True, default_synapse=True,default_spines=True,default_injection_current=[0.2e-9],default_simulation_time=0.2,default_stim='inject',default_stim_loc='soma')
#,default_simulation_time=0.01)
param_sim = option_parser.parse_args()

param_sim.save=1
param_sim.plot_channels=0
plotcomps=[model.param_cond.NAME_SOMA]

######## adjust the model settings if specified by command-line options and retain model defaults otherwise
model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

syn,neuron= cell_proto.neuronclasses(model)

plas = {}

####### Set up stimulation 
pg,param_sim=inject_func.setup_stim(model,param_sim,neuron)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
#Need to debug this since eliminated param_sim.stimtimes
#See what else needs to be changed in plasticity_test. 
if model.plasYN:
      plas,stimtab=plasticity_test.plasticity_test(model, param_sim.syncomp, syn, param_sim.stimtimes)
    
###############--------------output elements
if param_sim.plot_channels:
    for chan in model.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      model.VMIN, model.VMAX, model.CAMIN, model.CAMAX)

vmtab, catab, plastab, currtab = tables.graphtables(model, neuron,
                              param_sim.plot_current,
                              param_sim.plot_current_message,
                              plas,plotcomps)
if param_sim.save:
    fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]
    tables.setup_hdf5_output(model, neuron, filename=fname+'.npz')

if model.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(model,neuron,plotcomps)
else:
    spinevmtab=[]

########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in util.neurontypes(model.param_cond)]
clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve, model.param_cond.NAME_SOMA)
print("simdt", param_sim.simdt, "hsolve", param_sim.hsolve)

if param_sim.hsolve and model.calYN:
    calcium.fix_calcium(util.neurontypes(model.param_cond), model)

########### plot xgate
xtab=moose.Table('data/xgate')
kirchan=moose.element('/D1/soma/Kir')
moose.connect(xtab,'requestOut', kirchan,'getX')
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
'''plt.figure()
ts = np.linspace(0, param_sim.simtime, len(xtab.vector))
plt.plot(ts,xtab.vector,label='Kir, X value')
plt.legend()
plt.show()
'''
# block in non-interactive mode
util.block_if_noninteractive()
