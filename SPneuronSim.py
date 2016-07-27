# -*- coding:utf-8 -*-

######## SPneuronSim.py ############
## Code to create two SP neuron classes 
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional
##      used to tune parameters and channel kinetics (but using larger morphology)

from __future__ import print_function, division

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
                     neuron_graph,
                     test_plas,
                     util as _util)
from spspine import param_chan,param_cond, param_sim, param_syn
from spspine.graph import plot_channel

try:
    from ParamOverrides import *
except ImportError:
    pass

#################################-----------create the model
##create 2 neuron prototypes, optionally with synapses, calcium, and spines

MSNsyn,neuron,capools,synarray,spineHeads = cell_proto.neuronclasses(param_sim.Config,param_sim.printMoreInfo,param_syn.SynChanParams, param_syn.NumSyn)

#If calcium and synapses created, could test plasticity at a single synapse in syncomp
if param_sim.Config['synYN']:
    syn,plas,stimtab=test_plas.test_plas(param_sim.syncomp,param_sim.Config['calYN'],param_sim.Config['plasYN'],param_sim.inpath,MSNsyn)
else:
    syn,plas = {}, {}

####---------------Current Injection
currents = _util.inclusive_range(param_sim.current1,param_sim.current2,param_sim.currinc)
pg=inject_func.setupinj(param_sim.delay,param_sim.width,neuron)

###############--------------output elements
if param_sim.plotchan:
    for chan in param_chan.ChanDict.keys():
        libchan=moose.element('/library/'+chan)
        plot_channel.plot_gate_params(libchan,param_sim.plotpow, param_chan.VMIN, param_chan.VMAX, param_chan.CAMIN, param_chan.CAMAX)

data = moose.Neutral('/data')

vmtab,catab,plastab,currtab = tables.graphtables(neuron,param_sim.plotcurr,param_sim.currmsg,capools,plas,syn)
#if sim.spineYesNo:
#    spinecatab,spinevmtab=spinetabs()
########## clocks are critical. assign_clocks also sets up the hsolver
simpaths=['/'+neurotype for neurotype in param_cond.neurontypes()]
clocks.assign_clocks(simpaths, '/data', param_sim.simdt, param_sim.plotdt, param_sim.hsolve, param_sim.printinfo)

###########Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    Alltraces=[]
    for inj in currents:
        run_simulation(injection_current=inj, simtime=param_sim.simtime)
        neuron_graph.graphs(vmtab,param_sim.plotcurr,currtab,param_sim.currlabel,catab,plastab)
        Alltraces.append(vmtab[0][0].vector)
        #if param_sim.Config['spineYN']:
        #    spineFig(spinecatab,spinevmtab)
    neuron_graph.SingleGraphSet(Alltraces,currents)

    # block in non-interactive mode
    _util.block_if_noninteractive()

    #End of inject loop
