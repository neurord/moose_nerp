# -*- coding:utf-8 -*-
'''
Main script to create and simulate two SP neuron classes from the package
moose_nerp.d1d2 when run as module (python -m moose_nerp.d1d2)

  -using dictionaries for channels and synapses
  -calcium based learning rule/plasticity function, optional
  -spines, optionally with ion channels and synpases
  -Synapses to test the plasticity function, optional
  -used to tune parameters and channel kinetics (but using larger morphology)

Any of the parameters in param_sim, param_model_defaults, param_chan,
param_cond, etc. can be overriden here. For example, to override simtime (set
in parm_sim), do: model.param_sim.simtime = NEW_VALUE. Or to override spinesYN,
do: model.spinesYN = True (Default is set in param_model_defaults).
'''

from __future__ import print_function, division

from moose_nerp import d1opt as model
'''Evaluates moose_nerp/d1d2/__init__.py to load all the parameters, e.g.
param_sim.py, param_ca_plas.py, param_chan.py, param_cond.py, param_sim.py, etc.
into the model namespace. These parameters are then accessible by, e.g.,
`model.param_sim.fname`.
'''

from moose_nerp.prototypes import create_model_sim
'''Imports functions for setting up and simulating model. These take the `model`
namespace as argument, and append variables to this namespace. Thus, after
running a simulation, the output tables would be accessible as model.vmtab,
model.catab, etc.'''

# Parameter overrides can be specified:
model.spineYN=True
model.calYN=True
model.plasYN = False#True
model.synYN = True
#for k,v in model.param_ca_plas.CaShellModeDensity.items():
#    model.param_ca_plas.CaShellModeDensity[k] = model.param_ca_plas.SHELL

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
