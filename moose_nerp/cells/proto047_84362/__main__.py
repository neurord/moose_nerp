# -*- coding:utf-8 -*-
#1. repeat optimizations with fixed Buffer Capacity.
#2. use helpers to copy parameters into param_cond
#3. run single neuron simulations to verify
#4. run network simulations (single = True, then False) with and without ethanol - prelim
####################
## Code to create two globus pallidus neurons
##      using dictionaries for channels and synapses
##      calcium based learning rule/plasticity function, optional
##      spines, optionally with ion channels and synpases
##      Synapses to test the plasticity function, optional
##      used to tune parameters and channel kinetics (but using larger morphology)

from __future__ import print_function, division
from moose_nerp.cells import proto047 as model
'''Evaluates moose_nerp/gp/__init__.py to load all the parameters, e.g.
param_sim.py, param_ca_plas.py, param_chan.py, param_cond.py, param_sim.py, etc.
into the model namespace. These parameters are then accessible by, e.g.,
`model.param_sim.fname`.
'''
from moose_nerp.prototypes import create_model_sim
'''Imports functions for setting up and simulating model. These take the `model`
namespace as argument, and append variables to this namespace. Thus, after
running a simulation, the output tables would be accessible as model.vmtab,
model.catab, etc.'''

# Parameter overrides can be specified below:


# This function sets up the options specified in param_sim or passed from
# command line:
create_model_sim.setupOptions(model)

# This function creates the neuron(s) in Moose:
create_model_sim.setupNeurons(model)

# This function sets up the Output options, e.g. saving, graph tables, etc.
create_model_sim.setupOutput(model)

# This function sets up the stimulation in Moose, e.g. pulsegen for current
# injection or synaptic stimulation:
create_model_sim.setupStim(model)

# There is also a convenience function, `create_model_sim.setupAll(model)` that
# would sequentially call the above four functions: setupOptions, setupNeurons,
# setupOutput, and setupStim

# This function runs all the specified simulations, plotting and saving them
# as specified:
create_model_sim.runAll(model)

# Alternative function to create_model_sim.runAll, that runs a simulation a few
# steps at a time and then updates a plot, to show the live simulation results.
# This is an example of modifying, expanding, or customizing code:
#   `create_model_sim.stepRunPlot(model)`

# Note that customizations should be added to 'create_model_sim' to make them
# available to any model, by adding new functions or expanding existing functions
# with new options that do not alter the current state of the functions unless
# the new options are explicitly called.

#dat=pickle.load(open('params.pickle','rb'))
'''
import numpy as np
from matplotlib import pyplot as plt
fildir='pfc_arky120_3297_8/tmpwbtsanb3'
dat=np.load('/home/avrama/moose/opt_scripts/gp_opt/'+fildir+'/ivdata-0.0.npy','r')
simtime=1.25
ts=np.linspace(0,simtime,len(dat))
plt.plot(ts[0:3000],dat[0:3000])
'''
