# -*- coding:utf-8 -*-

######## SPnetSim.py ############
"""\
Create a network of SP neurons using dictionaries for channels, synapses, and network parameters

Can use ghk for calcium permeable channels if ghkYesNo=1
Optional calcium concentration in compartments (calcium=1)
Optional synaptic plasticity based on calcium (plasyesno=1)
Spines are optional (spineYesNo=1), but not allowed for network
The graphs won't work for multiple spines per compartment
"""
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
                     check_connect,
                     connect,
                     pop_funcs,
                     #net_output,
                     tables,
                     logutil,
                     util,
                     standard_options)
from spspine import (param_net, d1d2)
#from spspine.graph import net_graph

option_parser = standard_options.standard_options(default_injection_current=[50e-12, 100e-12])
param_sim = option_parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logutil.Logger()

#################################-----------create the model
#overrides:
d1d2.synYN=True

##create 2 neuron prototypes with synapses and calcium
MSNsyn,neuron,capools,synarray,spineHeads = cell_proto.neuronclasses(d1d2)
#FSIsyn,neuron,capools,synarray,spineHeads = cell_proto.neuronclasses(FSI)
#neurons=[]
#neurons.append(cell_proto.neuronclasses(FSI)

#check_connect prior to creating population, or after:
num_neurons,num_postsyn,num_postcells,num_tt,presyn_cells=check_connect.check_netparams(param_net,d1d2.param_syn.NumSyn)

### once debugged, the following lines will be incorporated in create_network
striatum_pop = pop_funcs.create_population(moose.Neutral(param_net.netname), param_net)
#May not need to return both cells and pop from create_population - just pop is fine?

#This will create the time tables for tt_gluSPN
#where should time tables be created?
#should all be created at once?
#does a tt_list need to be passed to connect_neurons?
param_net.tt_gluSPN.create()

#check_connect syntax after creating population
#possibly don't need to return any values except num_tt
num_neurons,num_postsyn,num_postcells,num_tt,presyn_cells=check_connect.check_netparams(param_net,d1d2.param_syn.NumSyn,striatum_pop['pop'])

#loop over all post-synaptic neuron types:
for ntype in striatum_pop['pop'].keys():
    connections=connect.connect_neurons(striatum_pop['pop'], param_net, ntype, d1d2.param_syn.NumSyn)

#  fix alltables (create sample timetables to test) and test tt connections
#  eliminate extern_conn.py 
#  fix create_network - eliminate use of spineheads if possible
#  delete connection.py? - currently holding notes
# also eliminate return of capools, neuron[comps], SynPerComp and MSNsyn - only need list of neurons
# plasticity

#LAST: tackle tables and graphs for both single and network
#Think about how to connect two different networks, e.g. striatum and GP
#May not need some of the create_network code depending on how external conn implemented

#population,SynPlas=create_network.CreateNetwork(d1d2, moose.Neutral('/input'), spineheads, synarray, MSNsyn, param_sim.simtime)

###------------------Current Injection
pg=inject_func.setupinj(d1d2, param_sim.injection_delay,param_sim.injection_width,neuron)

##############--------------output elements
data = moose.Neutral('/data')
if param_sim.show_xxx:
    vmtab,syntab,catab,plastab,sptab = tables.graphtables(d1d2, neuron, param_sim.plot_network,MSNpop,capools,SynPlas,spineHeads)
else:
    vmtab=[]

spiketab, vmtab = net_output.SpikeTables(d1d2, MSNpop,param_sim.show_xxx,vmtab)

########## clocks are critical
## these function needs to be tailored for each simulation
## if things are not working, you've probably messed up here.
if d1d2.single:
    simpath=['/'+neurotype for neurotype in d1d2.neurontypes()]
else:
    #possibly need to setup an hsolver separately for each cell in the network
    simpath=[netpar.netname]
clocks.assign_clocks(simpath, '/data', param_sim.simdt, param_sim.plotdt, param_sim.hsolve)

################### Actually run the simulation
def run_simulation(injection_current, simtime):
    print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
    pg.firstLevel = injection_current
    moose.reinit()
    moose.start(simtime)

if __name__ == '__main__':
    for inj in currents:
        run_simulation(injection_current=inj, simtime=param_sim.simtime)
        if param_sim.show_xxx:
            #net_graph.graphs(d1d2, vmtab,syntab,graphsyn,catab,plastab,sptab)
            plt.show()
        if not d1d2.single:
            writeOutput(d1d2, param_net.outfile+str(inj),spiketab,vmtab,MSNpop)

    # block in non-interactive mode
    _util.block_if_noninteractive()
