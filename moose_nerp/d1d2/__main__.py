# -*- coding:utf-8 -*-
'''
Main script to create and simulate two SP neuron classes from the package
moose_nerp.d1d2 when run as module (python -m moose_nerp.d1d2)

  -using dictionaries for channels and synapses
  -calcium based learning rule/plasticity function, optional
  -spines, optionally with ion channels and synpases
  -Synapses to test the plasticity function, optional
  -used to tune parameters and channel kinetics (but using larger morphology)

Any of the following parameters can be overridden below; otherwise defaults to
the listed values (which correspond to moose_nerp.prototypes.standard_options).

    (Note that any change/update to standard_options will automatically be
    detected when parsing options, so this static list may not represent the
    full current state of possible valid options).

        simtime = 0.35
        simdt = 1e-05
        plotdt = 0.0002
        hsolve = True
        save = None
        calcium = None
        spines = None
        synapse = None
        modelParamOverrides = None
        injection_current = None
        injection_delay = 0.1
        injection_width = 0.4
        stim_paradigm = None
        stim_loc = None
        plot_vm = True
        plot_current = None
        plot_calcium = None
        plot_current_message = 'getGk'
        plot_current_label = 'Cond, S'
        plot_synapse = None
        plot_synapse_message = 'getGk'
        plot_synapse_label = 'Cond, nS'
        plot_channels = None
        plot_activation = None
        plot_network = None
        plot_netvm = None

    Additional defaults that can be overriden by kwargs:
        logging_level = model.logging.INFO
        fname = (model.param_stim.Stimulation.Paradigm.name + '_' +
                 model.param_stim.location.stim_dendrites[0])
         plotcomps = model.NAME_SOMA
'''

from __future__ import print_function, division

from moose_nerp import d1d2 as model
from moose_nerp.prototypes import create_model_sim

# Options dictionary to be passed as **kwargs for main simulation function.
# Any parameter name listed above can be optionally overriden by including in
# this dictionary
#options = {}

# Optionally set logging level; default is INFO
#options['logging_level'] = model.logging.WARNING #DEBUG

#options['injection_current'] = [-0.2e-9, 0.26e-9]
#options['stim_paradigm'] = 'inject'
#options['stim_loc'] = model.NAME_SOMA

#options['save'] = 0
#options['plot_channels'] = 0

# Other possible options:
# options['plot_comps'] # Defaults to model.NAME_SOMA;
# options['fname'] # Set by default from model.param_stim

# Main
model.spineYN=True
model.calYN=True
create_model_sim.setupAll(model)
create_model_sim.runAll(model)
#create_model_sim.stepRunPlot(model)
'''
Note: create_model_sim.setupAll is a simple wrapper function that sequentially calls
4 other functions in create_model_sim:
    1. setupOptions(model,**kwargs) where all the **kwargs to main get passed
    2. setupNeurons(model)
    3. setupOutput(model)
    4. setupStim(model)
These functions can be called individually if desired to inspect and or modify
their outcome. E.g. to just inspect the moose model without simulating,
model.create_model_sim.setupNeurons(model) could be called.

Also note: model is passed to all these functions as a reference to the module,
and rather than having to return multiple variables, the functions simply add
variables to the model namespace. For instance, rather than having to return
param_sim, the function setupOptions adds param_sim to model namespace as
model.param_sim. After calling setupOptions, model.param_sim is available and
does not require a return.

'''
