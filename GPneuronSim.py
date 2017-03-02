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

import os
os.environ['NUMPTHREADS'] = '1'
import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from pprint import pprint
import moose 

from spspine import (cell_proto,
                     clocks,
                     inject_func,
                     tables,
                     plastic_synapse,
                     logutil,
                     util,
                     standard_options)
from spspine import gp
from spspine.graph import plot_channel, neuron_graph, spine_graph

option_parser = standard_options.standard_options(default_injection_current=[1.6e-9])#0.5e-9, 1.0e-9, 1.4e-9, 1.8e-9, 2.2e-9
param_sim = option_parser.parse_args()
param_sim.simtime=0.35
param_sim.injection_width=0.4
param_sim.plot_current=1

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron = cell_proto.neuronclasses(gp)

#axon conductance(Gbar) assigned directly until
ax_cond= moose.element('/proto/axon/NaF')
ax_cond.Gbar=1.413715381e-6
ax_cond= moose.element('/proto/axon/NaS')
ax_cond.Gbar= 1.130972382e-08
ax_cond= moose.element('/proto/axon/KDr')
ax_cond.Gbar= 1.809555812e-07
ax_cond= moose.element('/proto/axon/KvF')
ax_cond.Gbar= 4.523889174e-07
ax_cond= moose.element('/proto/axon/KvS')
ax_cond.Gbar= 6.785833762e-07
ax_cond= moose.element('/proto/axon/Kv3')
ax_cond.Gbar= 3.619111624e-07
ax_cond= moose.element('/proto/axon/KCNQ')
ax_cond.Gbar= 1.13097233e-10
ax_cond= moose.element('/proto/axon/HCN1')
ax_cond.Gbar= 0
ax_cond= moose.element('/proto/axon/HCN2')
ax_cond.Gbar= 0
ax_cond= moose.element('/proto/axon/SKCa')
ax_cond.Gbar= 0
ax_cond= moose.element('/proto/axon/Ca')
ax_cond.Gbar= 0
ax_cond=moose.element('/proto/axon/BKCa')
ax_cond.Gbar=0
##
#soma_R=moose.element('/proto/soma')
#soma_R.Ra=557992.5 *2
##
##
Bval=moose.element('/proto/soma/CaPool')
Bval.B=4.586150298e+10

##axon conductance for arky
ax_cond= moose.element('/arky/axon/NaF')
ax_cond.Gbar=1.413715381e-6
ax_cond= moose.element('/arky/axon/NaS')
ax_cond.Gbar= 1.130972382e-08
ax_cond= moose.element('/arky/axon/KDr')
ax_cond.Gbar= 1.809555812e-07
ax_cond= moose.element('/arky/axon/KvF')
ax_cond.Gbar= 4.523889174e-07
ax_cond= moose.element('/arky/axon/KvS')
ax_cond.Gbar= 6.785833762e-07*0.8
ax_cond= moose.element('/arky/axon/Kv3')
ax_cond.Gbar= 3.619111624e-07
ax_cond= moose.element('/arky/axon/KCNQ')
ax_cond.Gbar= 1.13097233e-10
ax_cond= moose.element('/arky/axon/HCN1')
ax_cond.Gbar= 0
ax_cond= moose.element('/arky/axon/HCN2')
ax_cond.Gbar= 0
ax_cond= moose.element('/arky/axon/SKCa')
ax_cond.Gbar= 0
ax_cond= moose.element('/arky/axon/Ca')
ax_cond.Gbar= 0
ax_cond=moose.element('/arky/axon/BKCa')
ax_cond.Gbar=0
#
#soma_R=moose.element('/arky/soma')
#soma_R.Ra=557992.5
#
Bval=moose.element('/arky/soma/CaPool')
Bval.B=4.586150298e+10



#If calcium and synapses created, could test plasticity at a single synapse in syncomp
if gp.synYN:
    plas,stimtab=plastic_synapse.plastic_synapse(gp, param_sim.syncomp, MSNsyn, param_sim.stimtimes)
else:
    plas = {}

####---------------Current Injection
all_neurons={}
for ntype in neuron.keys():
    all_neurons[ntype]=list([neuron[ntype].path])
pg=inject_func.setupinj(gp, param_sim.injection_delay, param_sim.injection_width, all_neurons)


###-------Voltage clamp
#neu=moose.element('/proto')
#tab= inject_func.Vclam(2.0,50.0,0.0,1.0,0.03,0.0,1e10,0.5,0.02,0.005,1e10)


###############--------------output elements
param_sim.plot_channels
if param_sim.plot_channels:
    for chan in gp.Channels.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plot_activation,
                                      gp.VMIN, gp.VMAX, gp.CAMIN, gp.CAMAX)


vmtab,catab,plastab,currtab = tables.graphtables(gp, neuron, param_sim.plot_current,  param_sim.plot_current_message, plas)

if gp.spineYN:
    spinecatab,spinevmtab=tables.spinetabs(gp,neuron)
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in gp.neurontypes()]
clocks.assign_clocks(simpaths, param_sim.simdt, param_sim.plotdt, param_sim.hsolve)

##print soma conductances
moose.reinit()
for neur in gp.neurontypes():
  for chan in moose.wildcardFind('/'+neur+'/soma/#[TYPE=HHChannel]'):
    print (neur, chan.name,chan.Ik*1e9, chan.Gk*1e9)
  for chan in moose.wildcardFind('/'+neur+'/soma/#[TYPE=HHChannel2D]'):
    print (neur, chan.name,chan.Ik*1e9, chan.Gk*1e9)
###########Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)


if __name__ == '__main__':
    traces, names = [], []
    value= []
    label=[]
    for inj in param_sim.injection_current:
        run_simulation(injection_current=inj, simtime=param_sim.simtime)
        #neuron_graph.graphs(gp, vmtab, param_sim.plot_current, param_sim.simtime,
        #                    currtab,param_sim.plot_current_label, catab, plastab)
        for neurnum,neurtype in enumerate(gp.neurontypes()):
            traces.append(vmtab[neurnum][0].vector)
            names.append('{} @ {}'.format(neurtype, inj))
        if gp.spineYN:
            spine_graph.spineFig(gp,spinecatab,spinevmtab, param_sim.simtime)
        if param_sim.plot_current==1:
            for channum,channame in enumerate (gp.Channels):
                print(channum,channame)
                value.append(currtab [neurtype][channame][0].vector)
                label.append('{} @ {}'.format(neurtype,channame))
                neuron_graph.CurrentGraphSet(value,label,param_sim.simtime)
    neuron_graph.SingleGraphSet(traces, names, param_sim.simtime)

    # block in non-interactive mode
    util.block_if_noninteractive()

    #End of inject loop
