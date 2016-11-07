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
#allneurons=[]
#allneurons.append(neuron)  #make neuron the list of neurons (not compartments)

######################### elements of new create_network.py ###############################
def create_network(d1d2, netparams):
    #where should time tables be created? if all created at once, no need to know the name of the table
    param_net.TableSet.create_all()

    if d1d2.single:
        #fix this kluge with the allneurons array above
        for ntype in d1d2.neurontypes():
            striatum_pop['pop'][ntype]="/"+ntype
        #subset of check_netparams
        num_postsyn,num_postcells=count_postsyn(netparams,d1d2.param_syn.NumSyn,striatum_pop['pop'])
        tt_per_syn,tt_per_ttfile=connect.count_total_tt(param_net,num_postsyn,num_postcells)
        #
        for ntype in striatum_pop['pop'].keys():
            connect=connect.connect_neurons(striatum_pop['pop'], param_net, ntype, d1d2.param_syn.NumSyn )
    else:
        #check_connect prior to creating population
        check_connect.check_netparams(param_net,d1d2.param_syn.NumSyn)
        #
        #May not need to return both cells and pop from create_population - just pop is fine?
        striatum_pop = pop_funcs.create_population(moose.Neutral(param_net.netname), param_net)
        #
        #check_connect syntax after creating population
        check_connect.check_netparams(param_net,d1d2.param_syn.NumSyn,striatum_pop['pop'])
        #
        #loop over all post-synaptic neuron types and create connections:
        for ntype in striatum_pop['pop'].keys():
            connections=connect.connect_neurons(striatum_pop['pop'], param_net, ntype, d1d2.param_syn.NumSyn)

        #Last, save/write out the list of connections and location of each neuron
        savez(param_net.confile,conn=connections,loc=striatum_pop['location'])
        return striatum_pop

#Types of spike train correlations
#1. number of synaptic terminals between single axon and single neuron
#       parameter specifying range or mean number.  Randomly select how many and repeat calls to
#           synpath,syncomps=select_entry(syncomps)
#           synconn(synpath,dist,presyn_tt,netparams.mindelay)
#2. with and between neuron correlation due to correlation of the cortical region projecting to striatum
#      account for both of these (same source) with correlated spike trains
#3.  between neuron correlations because a single axon can contact multiple neurons
#       implement using parameter syn_per_tt - associated with table object
#       this will also allow multiple synapses within single neuron, but unlikely if large neuron population

#1A: fix synconn for time table object
#Then  update create_network.py
#2: plasticity
#population,SynPlas=create_network.CreateNetwork(d1d2, moose.Neutral('/input'), striatum_pop['pop'], synarray)
# then delete extern_conn.py,
# then eliminate return of capools, neuron[comps], SynPerComp and MSNsyn - only need list of neurons, possibly synarray
# e.g. neuron,synarray = cell_proto.neuronclasses(d1d2)

#3: tackle tables and graphs for both single and network
#4: Think about how to connect two different networks, e.g. striatum and GP

#5. Refinements
#A. refine NamedLists for connections to specify post-syn location dependence (optional)
#B. refine select_branch to make use of location dependence 
#C. refine count_presyn to account for a. non-dist dependence, and multiple connections per neuron with location dependence
#                                      b. 3D arrays of elements
#D. debug case where neurons to have both intrinsic (pre-cell) and extern (timetable) inputs of same syntype

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
