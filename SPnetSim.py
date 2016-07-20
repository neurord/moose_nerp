# -*- coding:utf-8 -*-

######## SPnetSim.py ############
"""\
Create a SP neuron using dictionaries for channels and synapses

This allows multiple channels to be added with minimal change to the code
Can use ghk for calcium permeable channels if ghkYesNo=1
Optional calcium concentration in compartments (calcium=1)
Optional synaptic plasticity based on calcium (plasyesno=1)
Spines are optional (spineYesNo=1), but not allowed for network
The graphs won't work for multiple spines per compartment
Assumes spine head has name 'head', cell body called 'soma',
Also assumes that single neuron element tree is '/neurtype/compartment', and
network element tree is '/network/neurtype/compartment'
"""
from __future__ import print_function, division

import os
os.environ['NUMPTHREADS'] = '1'
import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from pprint import pprint
import moose 

from spspine import (cell_proto,
                     create_network,
                     inject_func,
                     util as _util)
import param_sim as sim
from param_cond import neurontypes
import clocks as clock
import param_net
import net_graph
import net_output
#################################-----------create the model

##create 2 neuron prototypes with synapses and calcium
MSNsyn,neuron,capools,synarray,spineHeads = cell_proto.neuronclasses(sim.plotchan,sim.plotpow,sim.calcium,sim.synYesNo,sim.spineYesNo,sim.ghkYesNo)

MSNpop,SynPlas=create_network.CreateNetwork(sim.inpath,sim.calcium,sim.plasYesNo,sim.single,spineHeads,synarray,MSNsyn,neuron)

###------------------Current Injection
currents = _util.inclusive_range(sim.current1)
pg=inject_func.setupinj(sim.delay,sim.width,neuron)

##############--------------output elements
data = moose.Neutral('/data')
if sim.showgraphs:
    vmtab,syntab,catab,plastab,sptab = net_graph.graphtables(neuron,sim.single,sim.plotnet,MSNpop,capools,SynPlas,spineHeads)
else:
    vmtab=[]

spiketab, vmtab = net_output.SpikeTables(sim.single,MSNpop,sim.showgraphs,vmtab)

########## clocks are critical
## these function needs to be tailored for each simulation
## if things are not working, you've probably messed up here.
if sim.single:
    simpath=['/'+neurotype for neurotype in neurontypes]
else:
    #possibly need to setup an hsolver separately for each cell in the network
    simpath=[netpar.netname]
clock.assign_clocks(simpath, '/data', sim.simdt, sim.plotdt, sim.hsolve)

################### Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    for inj in currents:
        run_simulation(injection_current=inj, simtime=sim.simtime)
        if sim.showgraphs:
            net_graph.graphs(vmtab,syntab,graphsyn,catab,plastab,sptab)
            plt.show()
        if not sim.single:
            writeOutput(param_net.outfile+str(inj),spiketab,vmtab,MSNpop)

    # block in non-interactive mode
    _util.block_if_noninteractive()
