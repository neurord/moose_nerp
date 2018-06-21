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
from moose_nerp import squid as model
from moose_nerp.graph import plot_channel, neuron_graph, spine_graph
from ajustador.helpers.loggingsystem import getlogger
logger = getlogger(__name__)
logger.setLevel(logging.DEBUG)
handle = logging.StreamHandler()
handle.setLevel(logging.DEBUG)
logger.addHandler(handle)
logger.debug("@@@@@@@")

#import engineering_notation as eng

option_parser = standard_options.standard_options(
    default_injection_current=[1e-9], #units (Amperes)
    default_simulation_time=0.1, #units (Seconds)
    default_injection_width=40e-3, #units (Seconds)
    default_injection_delay=20e-3, #units (Seconds)
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

plotcomps=[model.param_cond.NAME_SOMA]

model,plotcomps,param_sim=standard_options.overrides(param_sim,model,plotcomps)

logging.basicConfig(level=logging.DEBUG)
log = logutil.Logger()

######## adjust the model settings if specified by command-line options and retain model defaults otherwise
#These assignment statements are required because they are not part of param_sim namespace.
if param_sim.calcium is not None:
    model.calYN = param_sim.calcium
if param_sim.spines is not None:
    model.spineYN = param_sim.spines
if param_sim.stim_paradigm is not None:
    model.param_stim.Stimulation.Paradigm=ep.param_stim.paradigm_dict[param_sim.stim_paradigm]
if param_sim.stim_loc is not None:
    model.param_stim.Stimulation.StimLoc.stim_dendrites=param_sim.stim_loc

#These assignments make assumptions about which parameters should be changed together
if model.calYN and param_sim.plot_calcium is None:
    param_sim.plot_calcium = True
if model.param_stim.Stimulation.Paradigm.name is not 'inject':
    #override defaults if synaptic stimulation is planned
    model.synYN=1
    #this will need enhancement in future, e.g. in option_parser, to plot additional locations
    plotcomps=plotcomps+model.param_stim.location.stim_dendrites

#################################-----------create the model
##create neuron prototype, optionally with synapses, calcium, and spines

logger.debug("{} ?????".format(model.param_cond))
MSNsyn,neuron = cell_proto.neuronclasses(model)
print('MSNsyn:', MSNsyn)
print('neuron:', neuron)

plas = {}

####### Set up stimulation
if model.param_stim.Stimulation.Paradigm.name is not 'inject':
    ### plasticity paradigms combining synaptic stimulation with optional current injection
    sim_time = []
    for ntype in model.neurontypes():
        #update how ConnectPreSynapticPostSynapticStimulation deals with param_stim
        st, spines, pg = inject_func.ConnectPreSynapticPostSynapticStimulation(ep,ntype)
        sim_time.append( st)
        plas[ntype] = spines
    param_sim.simtime = max(sim_time)
    param_sim.injection_current = [0]
else:
    ### Current Injection alone, either use values from Paradigm or from command-line options
    if not np.any(param_sim.injection_current):
        param_sim.injection_current = [model.param_stim.Stimulation.Paradigm.A_inject]
        param_sim.injection_delay = model.param_stim.Stimulation.stim_delay
        param_sim.injection_width = model.param_stim.Stimulation.Paradigm.width_AP
    all_neurons={}
    for ntype in neuron.keys():
        all_neurons[ntype]=list([neuron[ntype].path])
    pg=inject_func.setupinj(model, param_sim.injection_delay, param_sim.injection_width,all_neurons)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
#Need to debug this since eliminated param_sim.stimtimes
#See what else needs to be changed in plasticity_test.
if model.plasYN:
      plas,stimtab=plasticity_test.plasticity_test(model, param_sim.syncomp, MSNsyn, param_sim.stimtimes)

###############--------------output elements
param_sim.plot_channels=1 #Set 1 to plot_channels else 0.
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
    tables.setup_hdf5_output(d1d2, neuron, param_sim.save)

if model.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(model,neuron,plotcomps)
else:
    spinevmtab=[]
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in util.neurontypes(model.param_cond)]
clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve,model.param_cond.NAME_SOMA)

if param_sim.hsolve and model.calYN:
    calcium.fix_calcium(util.neurontypes(model.param_cond), model)

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

