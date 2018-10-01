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
from ajustador.helpers.loggingsystem import getlogger
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
    #default_simulation_time=100e-3, #units (Seconds)
    #default_injection_width=40e-3, #units (Seconds)
    #default_injection_delay=20e-3, #units (Seconds)
    default_simulation_time=200e-3, #units (Seconds) #2 second simulations
    default_injection_width=130e-3, #units (Seconds)  #1 second injection spacing
    default_injection_delay=30e-3, #units (Seconds)  #0.5 second injection start
    default_plotdt=25e-6 #units (Seconds)

    #default_injection_current=[float(eng.EngUnit('1nA'))], #units (Amperes)
    #default_simulation_time=float(eng.EngUnit('0.1S')), #units (Seconds)
    #default_injection_width=float(eng.EngUnit('40mS')), #units (Seconds)
    #default_injection_delay=float(eng.EngUnit('20mS')), #units (Seconds)
    #default_plotdt=float(eng.EngUnit('25uS')) #units (Seconds)
    )

param_sim = option_parser.parse_args()
param_sim.hsolve=1
param_sim.save_vm='/home/Sriramsagar/neural_prj/waves/squid-experimental/squid_trace.npy'
param_sim.plot_channels=1
#param_sim.save_vm='/home/Sriramsagar/neural_prj/waves/squid-experimental/squid_trace_tau.npy'
#param_sim.save_vm='/home/Sriramsagar/neural_prj/waves/squid-experimental/squid_trace_tau_z.npy'

plotcomps=[model.param_cond.NAME_SOMA]

model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)


######## required for all simulations: adjust the model settings if specified by command-line options and retain model defaults otherwise
model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)

#default file name is obtained from stimulation parameters
fname=model.param_stim.Stimulation.Paradigm.name+'_'+model.param_stim.location.stim_dendrites[0]

############## required for all simulations: create the model, set up stimulation and basic output

syn,neuron,pg,param_sim,writer,vmtab, catab, plastab, currtab=create_model_sim.create_model_sim(model,fname,param_sim,plotcomps)


logger.debug("{} ?????".format(model.param_cond))
logger.debug("Check for simtime: {}".format(param_sim))

print('syn:', syn)
print('neuron:', neuron)

############# Optionally, some additional output ##############

if param_sim.plot_channels:
    for chan in model.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      model.VMIN, model.VMAX, model.CAMIN, model.CAMAX)

###############--------------output elements
 #Set 1 to plot_channels else 0.
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
        if model.calYN and param_sim.plot_calcium:
            calcium_traces.append(catab[neurnum][0].vector)
        names.append('{} @ {}'.format(neurtype, inj))

    if len(spinevmtab) and param_sim.plot_vm:
        spine_graph.spineFig(ep,spinecatab,spinevmtab, param_sim.simtime)

###############plot zgate
# plt.figure()
# ts = np.linspace(0, param_sim.simtime, len(ztab.vector))
# plt.plot(ts,ztab.vector,label='NaF, Z value')
# plt.legend()
# plt.show()

if param_sim.plot_vm:
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)
    if model.calYN and param_sim.plot_calcium:
        neuron_graph.SingleGraphSet(calcium_traces,names,param_sim.simtime, title='Ca')

if param_sim.save_vm:
        logger.debug("Saveing Trace to file {}!!!".format(param_sim.save_vm))
        logger.debug('{}'.format(util.neurontypes(model.param_cond)))
        neuron_type = util.neurontypes(model.param_cond)[0]
        elemname = '/data/Vm{}_0'.format(neuron_type)
        persist_data = {"simtime": param_sim.simtime,
                        "injection_current":param_sim.injection_current,
                        "voltage_data_points": moose.element(elemname).vector,
                        "data_points_count": len(moose.element(elemname).vector)}
        logger.debug(persist_data)
        np.save(param_sim.save_vm, persist_data)

# block in non-interactive mode
util.block_if_noninteractive()

